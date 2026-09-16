"""
HOTEL MANAGEMENT SYSTEM - URL ROUTING

This file defines all the URLs (web addresses) for the hotel app.
URLs are organized into:
1. API Routes (return JSON data)
2. Frontend Pages (return HTML)
3. REST API ViewSets (automatic CRUD endpoints)

For beginners:
- path() defines a URL that users can visit
- The view function handles what happens at that URL
- name parameter makes it easy to reference URLs in code
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# ═══════════════════════════════════════════════════════════════
# REST API ViewSets - Auto-generate CRUD endpoints
# These create endpoints like:
# /api/hotels/ (list all)
# /api/hotels/<id>/ (get one)
# /api/hotels/ (create new)
# /api/hotels/<id>/ (update)
# /api/hotels/<id>/ (delete)
# ═══════════════════════════════════════════════════════════════

router = DefaultRouter()

# Hotel management
router.register(r'hotels', views.HotelViewSet)

# Room type management
router.register(r'room-types', views.RoomTypeViewSet)

# Room management
router.register(r'rooms', views.RoomViewSet)

# Guest management
router.register(r'guests', views.GuestViewSet)

# Booking management
router.register(r'bookings', views.BookingViewSet)

# Payment management
router.register(r'payments', views.PaymentViewSet)

# Staff management
router.register(r'staff', views.StaffViewSet)

# Hotel services management
router.register(r'services', views.ServiceViewSet)

# Service additions to bookings
router.register(r'booking-services', views.BookingServiceViewSet)

# Guest reviews
router.register(r'reviews', views.ReviewViewSet)

# Maintenance requests
router.register(r'maintenance-requests', views.MaintenanceRequestViewSet)

# Guest complaints
router.register(r'complaints', views.ComplaintViewSet)


urlpatterns = [

    # =========================
    # DASHBOARD & ANALYTICS APIs
    # =========================
    # Main dashboard - overview stats
    # Returns: total rooms, bookings, guests, revenue, room status
    path('api/dashboard/', views.dashboard_data, name='api_dashboard'),
    
    # =========================
    # BOOKING APIs
    # =========================
    # Create a new booking
    # POST with: guest name, email, check-in, check-out, room type
    path('api/bookings/add/', views.create_booking, name='api_booking_add'),
    
    # =========================
    # ROOM MANAGEMENT APIs
    # =========================
    # Add a single room
    # POST with: room number, type, price, floor
    path('api/rooms/add/', views.add_room, name='api_room_add'),
    
    # Add multiple rooms at once (bulk add)
    # POST with: start room, end room, type, price, floor
    path('api/rooms/bulk-add/', views.bulk_add_rooms, name='api_room_bulk_add'),
    
    # Get room occupancy forecast for next 30 days
    path('api/rooms/occupancy/forecast/', views.room_occupancy_forecast, name='occupancy_forecast'),
    
    # =========================
    # CUSTOMER/GUEST APIs
    # =========================
    # Get list of all customers with search
    # Query params: ?search=keyword
    path('api/customers/', views.customers_data, name='api_customers'),
    
    # Get booking history for a specific customer
    path('api/customer/<int:customer_id>/bookings/', views.customer_booking_history, name='customer_booking_history'),
    
    # Get overall customer analytics
    path('api/customers/analytics/', views.customer_analytics, name='customer_analytics'),
    
    # =========================
    # PAYMENT APIs
    # =========================
    # Get payment summary and list
    path('api/payments-summary/', views.payments_data, name='api_payments'),
    
    # =========================
    # REVIEW APIs
    # =========================
    # Create a guest review after checkout
    path('api/bookings/<int:booking_id>/review/', views.create_guest_review, name='create_guest_review'),
    
    # =========================
    # SETTINGS APIs
    # =========================
    # Get or update system settings (admin/manager only for POST)
    path('api/settings/', views.settings_data, name='api_settings'),
    path('api/hotel-name/', views.public_hotel_name, name='api_hotel_name'),

    # =========================
    # HOUSEKEEPING APIs
    # =========================
    path('api/cleaning/', views.cleaning_list, name='api_cleaning_list'),
    path('api/cleaning/<int:cleaning_id>/update/', views.cleaning_update_status, name='api_cleaning_update'),

    # =========================
    # COMPLAINTS APIs
    # =========================
    path('api/complaints-data/', views.complaints_data,            name='api_complaints_data'),
    path('api/complaints/create/', views.create_complaint,         name='api_complaint_create'),
    path('api/complaints/<int:complaint_id>/update/', views.update_complaint, name='api_complaint_update'),

    # =========================
    # MAINTENANCE APIs
    # =========================
    path('api/maintenance-data/', views.maintenance_data,           name='api_maintenance_data'),
    path('api/maintenance/create/', views.create_maintenance,       name='api_maintenance_create'),
    path('api/maintenance/<int:req_id>/update/', views.update_maintenance, name='api_maintenance_update'),

    # =========================
    # STAFF APIs
    # =========================
    path('api/staff-data/', views.staff_data, name='api_staff_data'),

    # =========================
    # SERVICES APIs
    # =========================
    path('api/services-data/', views.services_data,                name='api_services_data'),
    path('api/services/create/', views.create_service,             name='api_service_create'),
    path('api/services/<int:service_id>/update/', views.update_service, name='api_service_update'),

    # =========================
    # REVIEWS APIs
    # =========================
    path('api/reviews-data/', views.reviews_data, name='api_reviews_data'),

    # =========================
    # REST API ViewSets
    # Auto-generated CRUD endpoints
    # =========================
    path('api/', include(router.urls)),

    # =========================
    # FRONTEND PAGES
    # =========================
    path('', views.home, name='home'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('booking/', views.bookings, name='booking'),
    path('rooms/', views.rooms, name='rooms'),
    path('customers/', views.customers, name='customers'),
    path('payments/', views.payments, name='payments'),
    path('settings/', views.settings_view,      name='settings'),
    path('users/',    views.users_view,          name='users'),
    path('housekeeping/', views.housekeeping_view, name='housekeeping'),
    path('complaints/',   views.complaints_view,   name='complaints'),
    path('maintenance/',  views.maintenance_view,  name='maintenance'),
    path('staff/',        views.staff_view,         name='staff'),
    path('services/',     views.services_view,      name='services'),
    path('reviews/',      views.reviews_view,       name='reviews'),
]