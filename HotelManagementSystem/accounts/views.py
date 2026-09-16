"""
ACCOUNTS APP - AUTHENTICATION & USER MANAGEMENT VIEWS

This module handles:
1. User login/logout functionality
2. User role and permission management
3. Admin APIs for managing system users
4. Helper functions to check user roles and permissions
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Profile
import json


# ═══════════════════════════════════════════════════════════════
# PAGE VIEWS (Return HTML pages)
# ═══════════════════════════════════════════════════════════════

def login_view(request):
    """
    Login Page & Process User Credentials
    
    If user is already logged in → redirect to dashboard
    If POST request → verify username/password and log them in
    If GET request → show login form
    """
    # If user is already logged in, redirect them to dashboard
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    
    # Handle login form submission
    if request.method == 'POST':
        # Get username and password from the login form
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check if credentials are correct
        user = authenticate(request, username=username, password=password)
        
        if user is not None:  # Credentials are valid
            login(request, user)  # Log the user in
            return redirect('/dashboard/')  # Send them to dashboard
        else:  # Credentials are invalid
            messages.error(request, 'Invalid username or password.')
    
    # Show the login form (GET request or failed login)
    return render(request, 'accounts/login.html')


def logout_view(request):
    """
    Logout User & Redirect to Login Page
    
    This clears the user's session and logs them out of the system.
    """
    logout(request)  # Log the user out
    return redirect('/accounts/login/')  # Redirect to login page


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS (Used by decorators and views)
# ═══════════════════════════════════════════════════════════════

def get_role(user):
    """
    Get the role of a user (admin, manager, or staff)
    
    Args:
        user: The User object
    
    Returns:
        String: 'admin', 'manager', 'staff', or 'staff' (default if error)
    """
    try:
        return user.profile.role
    except Exception:
        # If something goes wrong, default to 'staff' (lowest permissions)
        return 'staff'


# ═══════════════════════════════════════════════════════════════
# PERMISSION DECORATORS (Control who can access each function)
# ═══════════════════════════════════════════════════════════════

def admin_required(view_func):
    """
    Permission Decorator - Only admins can access this function
    
    Usage: Add @admin_required above a view function to restrict access to admins only
    
    Returns:
    - Error 401: User is not logged in
    - Error 403: User is logged in but doesn't have admin role
    """
    def wrapper(request, *args, **kwargs):
        # Check if user is logged in
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Not authenticated'}, status=401)
        
        # Check if user is an admin
        if get_role(request.user) != 'admin':
            return JsonResponse({'error': 'Admin access required'}, status=403)
        
        # User is an admin, allow them to proceed
        return view_func(request, *args, **kwargs)
    
    wrapper.__name__ = view_func.__name__
    return wrapper


# ═══════════════════════════════════════════════════════════════
# API ENDPOINTS (Return JSON data)
# ═══════════════════════════════════════════════════════════════

@login_required  # User must be logged in to use this
def current_user(request):
    """
    API Endpoint - Get Current Logged-In User Info
    
    Returns JSON with:
    - User ID, username, name, email
    - User role (admin/manager/staff)
    - Flags for admin/manager status (easier for frontend to check)
    """
    user = request.user
    return JsonResponse({
        'id':         user.id,
        'username':   user.username,
        'first_name': user.first_name,
        'last_name':  user.last_name,
        'email':      user.email,
        'role':       get_role(user),
        'is_admin':   get_role(user) == 'admin',  # Is this user an admin?
        'is_manager': get_role(user) in ('admin', 'manager'),  # Is this user a manager or admin?
    })


@login_required
@admin_required  # Only admins can use this
def list_users(request):
    """
    API Endpoint - Get List of All System Users (Admin Only)
    
    Returns JSON array with info about each user:
    - ID, username, name, email, role
    - Whether account is active
    - When they joined the system
    """
    # Get all users, including their profile info
    users = User.objects.select_related('profile').all().order_by('id')
    
    # Build a list of user info
    data = []
    for u in users:
        data.append({
            'id':         u.id,
            'username':   u.username,
            'first_name': u.first_name,
            'last_name':  u.last_name,
            'email':      u.email,
            'role':       get_role(u),
            'is_active':  u.is_active,
            'date_joined': u.date_joined.strftime('%Y-%m-%d'),  # Format date as YYYY-MM-DD
        })
    
    return JsonResponse({'users': data})


@login_required
@admin_required  # Only admins can create users
def create_user(request):
    """
    API Endpoint - Create a New User Account (Admin Only)
    
    Expects POST request with JSON data:
    {
        "username": "john_doe",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password": "secure_password",
        "role": "manager"  // or "staff" or "admin"
    }
    
    Returns:
    - Success: JSON with user ID
    - Error: JSON error message + status code
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    # Parse the JSON data from request
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # Extract data from request
    username   = data.get('username', '').strip()
    first_name = data.get('first_name', '').strip()
    last_name  = data.get('last_name', '').strip()
    email      = data.get('email', '').strip()
    password   = data.get('password', '')
    role       = data.get('role', 'staff')

    # Validate that all required fields are provided
    if not all([username, first_name, email, password]):
        return JsonResponse({'error': 'All fields are required.'}, status=400)
    
    # Validate password strength
    if len(password) < 6:
        return JsonResponse({'error': 'Password must be at least 6 characters.'}, status=400)
    
    # Check if username already exists
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Username already taken.'}, status=400)
    
    # Check if email already exists
    if User.objects.filter(email=email).exists():
        return JsonResponse({'error': 'Email already registered.'}, status=400)
    
    # Validate role
    if role not in ('admin', 'manager', 'staff'):
        return JsonResponse({'error': 'Invalid role.'}, status=400)

    # Create the new user
    user = User.objects.create_user(
        username=username, 
        email=email, 
        password=password,
        first_name=first_name, 
        last_name=last_name
    )
    
    # Set the user's role
    user.profile.role = role
    user.profile.save()

    return JsonResponse({'success': True, 'id': user.id})


@login_required
@admin_required  # Only admins can update users
def update_user(request, user_id):
    """
    API Endpoint - Update User Info (Admin Only)
    
    Accepts POST or PATCH request with JSON data:
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "newemail@example.com",
        "role": "manager",  // Can change user's role
        "is_active": true   // Can deactivate/activate account
    }
    
    Args:
        user_id: ID of the user to update
    """
    if request.method not in ('POST', 'PATCH'):
        return JsonResponse({'error': 'POST required'}, status=405)
    
    # Parse JSON data
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # Find the user
    try:
        user = User.objects.select_related('profile').get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    # Safety check: admins can't demote themselves
    if user == request.user and data.get('role') and data['role'] != 'admin':
        return JsonResponse({'error': 'You cannot change your own role.'}, status=400)

    # Update user's basic information
    if 'first_name' in data: 
        user.first_name = data['first_name']
    if 'last_name'  in data: 
        user.last_name  = data['last_name']
    if 'email'      in data: 
        user.email      = data['email']
    if 'is_active'  in data: 
        user.is_active  = data['is_active']
    
    user.save()

    # Update user's role if provided
    if 'role' in data:
        # Validate the role
        if data['role'] not in ('admin', 'manager', 'staff'):
            return JsonResponse({'error': 'Invalid role.'}, status=400)
        user.profile.role = data['role']
        user.profile.save()

    return JsonResponse({'success': True})


@login_required
@admin_required  # Only admins can delete users
def delete_user(request, user_id):
    """
    API Endpoint - Delete a User Account (Admin Only)
    
    Args:
        user_id: ID of the user to delete
    
    Returns:
    - Success: JSON success message
    - Error: If user not found or trying to delete themselves
    """
    if request.method != 'DELETE':
        return JsonResponse({'error': 'DELETE required'}, status=405)
    
    # Find the user
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    # Safety check: can't delete your own account
    if user == request.user:
        return JsonResponse({'error': 'You cannot delete your own account.'}, status=400)
    
    # Delete the user
    user.delete()
    return JsonResponse({'success': True})