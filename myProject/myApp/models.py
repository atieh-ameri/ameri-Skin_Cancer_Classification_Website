# models.py
from django.db import models

class ImageUpload(models.Model):
    # Gender Dropdown Choices
    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("", ""),
    ]
    sex = models.CharField(max_length=10, choices=GENDER_CHOICES, default=None, blank=True, null=True)

    # Age Dropdown Choices (10-100)
    DOB_CHOICES = [(str(age), str(age)) for age in range(2025, 1900, -1)]
    dob = models.CharField(max_length=4, choices=DOB_CHOICES, default="2000", blank=True, null=True)

    # Location Input
    LOCATION_CHOICES = [
        ('lower extremity', 'lower extremity'),
        ('head/neck', 'head/neck'),
        ('posterior torso', 'posterior torso'),
        ('anterior torso', 'anterior torso'),
        ('upper extremity', 'upper extremity'),
        ("", ""),
    ]
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES, default=None, blank=True, null=True)

    # Image Upload Field
    image = models.ImageField(upload_to="uploads/", blank=False, null=False)

    def __str__(self):
        return f"{self.sex} - {self.dob}"