"""
ACCOUNTS APP - URL ROUTING

This file defines all the URLs (web addresses) for the accounts app.
Each URL maps to a view function that handles requests.

For beginners:
- Each path() defines one URL that users can visit
- The name parameter makes it easy to reference the URL in code
"""

from django.urls import path
from . import views

urlpatterns = [
    # ═══════════════════════════════════════════════════════════════
    # PAGE ROUTES (Return HTML pages)
    # ═══════════════════════════════════════════════════════════════
    
    # User login page
    path('login/',         views.login_view,    name='login'),
    
    # User logout (clears session)
    path('logout/',        views.logout_view,   name='logout'),

    # ═══════════════════════════════════════════════════════════════
    # API ROUTES (Return JSON data)
    # Admin Only - User Management
    # ═══════════════════════════════════════════════════════════════
    
    # Get current logged-in user info
    path('api/me/',                   views.current_user,  name='current_user'),
    
    # Get list of all users (admin only)
    path('api/users/',                views.list_users,    name='list_users'),
    
    # Create a new user account (admin only)
    path('api/users/create/',         views.create_user,   name='create_user'),
    
    # Update a user's info or role (admin only)
    # Example: /accounts/api/users/5/ to update user with ID 5
    path('api/users/<int:user_id>/',  views.update_user,   name='update_user'),
    
    # Delete a user account (admin only)
    # Example: /accounts/api/users/5/delete/ to delete user with ID 5
    path('api/users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
]