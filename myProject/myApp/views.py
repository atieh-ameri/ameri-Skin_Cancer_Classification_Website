from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
import os
import numpy as np
import tensorflow as tf
from keras import preprocessing
import base64
import uuid
import logging


from .forms import RegisterForm, LoginForm, ImageUploadForm
# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Load the trained model globally (so it doesn't reload every request)
MODEL_PATH = os.path.join(settings.BASE_DIR, "xception_isic2024_final.h5")
model = tf.keras.models.load_model(MODEL_PATH)




def preprocess_image(img_path, target_size=(299, 299)):
    try:
        logger.info(f"Preprocessing image: {img_path}")
        img = preprocessing.image.load_img(img_path, target_size=target_size)  # Load image
        img_array = preprocessing.image.img_to_array(img)  # Convert to NumPy array
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
        img_array = img_array / 255.0  # Normalize

    
        return img_array
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        raise


# Home page view
def home(request):
    return render(request, "home.html")


# Image cropping page
def imagecropper(request):
    return render(request, "imagecropper.html")


# User registration view
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect("dashboard")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


# User login view
def login_user(request):
    if request.method == "POST":
        form = LoginForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("dashboard")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


# User logout view
def logout_user(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("login")




from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from .forms import ContactForm


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Construct email message
            email_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            
            try:
                # Send email
                send_mail(
                    subject=f"Contact Form: {subject}",
                    message=email_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_EMAIL],  # Define this in settings.py
                )
                messages.success(request, "Your message has been sent! We'll get back to you soon.")
                return redirect('contact')  # Redirect to same page
            except BadHeaderError:
                messages.error(request, "Invalid header found. Please try again.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})




@login_required
def dashboard(request):
    logger.info(f"Dashboard view accessed, method: {request.method}")
    
    if request.method == "POST":
        logger.info("Processing POST request in dashboard")
        form = ImageUploadForm(request.POST, request.FILES)
        result = []
        
        if form.is_valid():
            logger.info("Form is valid")
            # Get Form Data
            sex = form.cleaned_data["sex"]
            dob = form.cleaned_data["dob"]
            location = form.cleaned_data["location"]
            
            # Get the uploaded image
            image = form.cleaned_data.get("image")
            
            if not image:
                logger.warning("No image was uploaded")
                messages.error(request, "No image was uploaded.")
                return render(request, "dashboard.html", {"form": form})
            
            logger.info(f"Form data: sex={sex}, dob={dob}, location={location}, image_name={image.name}")
       
            try:
                # Save the image
                img_path = default_storage.save(f"uploads/{image.name}", image)
                logger.info(f"Image saved at: {img_path}")
                
                # Get the full filesystem path
                full_img_path = os.path.join(settings.MEDIA_ROOT, img_path)
                logger.info(f"Full image path: {full_img_path}")
                
                # Get the URL path for display
                image_url = os.path.join(settings.MEDIA_URL, img_path)
                
                # Create a basic result without model prediction
                classification_result = {
                    "sex": sex,
                    "dob": str(dob),
                    "location": location,
                    "image_url": image_url,
                    "prediction": {"status": "processing"}
                }
                
                # Try to load the model and make a prediction
                try:
                    if model:
                        # Preprocess and predict
                        processed_img = preprocess_image(full_img_path)
                        prediction = model.predict(processed_img)
                        
                        # Format the prediction result
                        prediction_result = {
                            "status": "success",
                            "raw_prediction": round(float(prediction[0][0])*100, 2) 

                        }
                        
                        # Update the classification result with prediction
                        classification_result["prediction"] = prediction_result
                    else:
                        logger.warning("Model could not be loaded")
                        classification_result["prediction"] = {
                            "status": "error",
                            "message": "Model could not be loaded"
                        } 
                        
                except Exception as e:
                    logger.error(f"Error during prediction: {e}")
                    classification_result["prediction"] = {
                        "status": "error",
                        "message": f"Error during prediction: {str(e)}"
                    }
                
                # Return results on the same page
                return render(request, "dashboard.html", {
                    "form": form,
                    "classification_result": classification_result,
                    "show_results": True
                })
                
            except Exception as e:
                logger.error(f"Error processing image: {e}")
                messages.error(request, f"Error processing image: {str(e)}")
                return render(request, "dashboard.html", {"form": form})
        
        else:
            logger.warning(f"Form validation errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return render(request, "dashboard.html", {"form": form})
    
    else:
        form = ImageUploadForm()
        return render(request, "dashboard.html", {
            "form": form,
            "show_results": False
        })


@login_required
def result(request):
    
    logger.info("Result view accessed")
    
    # Debug information
    logger.info(f"Available session data keys: {request.session.keys()}")
    
    classification_result = request.session.get("classification_result", {})
    logger.info(f"Retrieved classification result: {classification_result}")
    
    # if not classification_result:
    #     logger.warning("No classification data found in session")
    #     messages.error(request, "No classification data found. Please submit an image first.")
    #     return redirect("dashboard")
    
    return render(request, "result.html", {"classification_result": classification_result})

