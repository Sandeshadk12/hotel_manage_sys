"""
ACCOUNTS APP - USER AUTHENTICATION & ROLES

This module handles user authentication and user profile management.
It extends Django's built-in User model with additional profile information
like user role (admin, manager, staff) and phone number.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """
    User Profile - Stores additional information about each system user
    
    This model extends Django's built-in User model with extra fields.
    Each user in the system automatically gets a Profile when they're created.
    
    Fields:
    - user: Reference to the Django User object (one-to-one relationship)
    - role: User's role in the system (admin, manager, or staff)
    - phone: Contact phone number
    - created_at: When the profile was created
    """
    
    # Define the three roles available in the system
    ROLE_CHOICES = (
        ('admin', 'Admin'),        # Admin - Full system access
        ('manager', 'Manager'),    # Manager - Can manage settings and staff
        ('staff', 'Staff'),        # Staff - Limited read-only access
    )
    
    # Link to Django's User model - each user has one profile
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # What role does this user have?
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    
    # User's contact phone number
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    # When was this profile created?
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Show the username and role when this object is displayed"""
        return f"{self.user.username} - {self.role}"


# Automatically create a Profile when a new User is created
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Signal handler - Automatically creates a Profile when a new User is created
    
    This function runs automatically whenever a new User is saved to the database.
    - sender: The model that triggered this signal (User)
    - instance: The actual User object being saved
    - created: True if this is a new User, False if updating existing
    - kwargs: Other parameters passed by Django
    """
    if created:  # Only create profile if this is a new user
        Profile.objects.create(user=instance)


# Make sure Profile changes are saved when User is updated
@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """
    Signal handler - Ensures Profile is saved when User is saved
    
    This keeps the Profile synchronized with the User model.
    """
    instance.profile.save()