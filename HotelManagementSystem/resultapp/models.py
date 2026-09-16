"""
HOTEL MANAGEMENT SYSTEM - DATABASE MODELS

This module defines all the database tables (models) for the hotel system.
Each model represents a different entity in the hotel business:
- Hotel: The main hotel property
- Room, RoomType: Room inventory management
- Guest, Booking: Guest and reservation management
- Payment: Payment tracking
- Staff: Employee management
- Services: Hotel services offered
- Review: Guest feedback
- MaintenanceRequest, Complaint: Maintenance and complaint tracking
- HotelSettings: System configuration

Models in Django are like database tables. Each field becomes a column.
"""

from django.db import models
from django.contrib.auth.models import User
import random
import string


class Hotel(models.Model):
    """
    Hotel - Stores information about the hotel property
    
    This is the main hotel entity. One hotel can have many rooms, bookings, etc.
    
    Fields:
    - name: Hotel's display name
    - address: Full street address
    - city: City where hotel is located
    - state: State/province
    - postal_code: Zip/postal code
    - phone: Main contact phone number
    - email: Main contact email
    - website: Hotel's website URL (optional)
    - total_rooms: How many rooms the hotel has
    - created_at: When this record was created
    - updated_at: When this record was last updated
    """
    # Hotel basic information
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    total_rooms = models.IntegerField(default=0)
    
    # Timestamps for tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Display the hotel name when this object is shown"""
        return self.name


class RoomType(models.Model):
    """
    Room Type - Categories of rooms (Single, Double, Suite, etc.)
    
    Defines different types of rooms available in the hotel.
    Examples: Single Room, Double Room, Deluxe Suite, etc.
    
    Fields:
    - name: Room type name (e.g., "Single", "Double")
    - description: Details about this room type
    - base_price: Default price per night for this type
    - capacity: Maximum number of guests this room can fit
    - amenities: List of amenities included (WiFi, TV, AC, etc.)
    """
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField(default=1)
    amenities = models.TextField(blank=True, null=True)

    def __str__(self):
        """Display the room type name"""
        return self.name


class Room(models.Model):
    """
    Room - Individual room in the hotel
    
    Each Room is a specific, physical room with a unique room number.
    A room has a status (Available, Occupied, Maintenance, or Reserved).
    
    Fields:
    - hotel: Which hotel this room belongs to
    - room_number: Room identifier (e.g., "101", "202")
    - room_type: What type of room is this? (links to RoomType)
    - floor: Which floor is this room on?
    - status: Current status of the room
    - price_per_night: How much this room costs per night
    - is_available: Is room available for booking?
    - description: Additional details about this specific room
    - created_at, updated_at: Tracking timestamps
    
    Room Status Flow:
    Available → Reserved (when booking) → Occupied (check-in) → Available (check-out)
    Or: Available → Maintenance → Available (after repairs)
    """
    
    # Define the possible room statuses
    STATUS_CHOICES = (
        ('Available', 'Available'),      # Room is ready and can be booked
        ('Occupied', 'Occupied'),        # Guest is currently in the room
        ('Cleaning', 'Cleaning'),        # Room is being cleaned after checkout
        ('Maintenance', 'Maintenance'),  # Room is under maintenance
        ('Reserved', 'Reserved'),        # Room is booked but guest hasn't checked in yet
    )
    
    # Link this room to a hotel
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    
    # Room identification - like "101", "202", "Suite 5", etc.
    room_number = models.CharField(max_length=10)
    
    # What type of room is this? (links to RoomType model)
    room_type = models.ForeignKey(RoomType, on_delete=models.SET_NULL, null=True, related_name='rooms')
    
    # Floor number where this room is located
    floor = models.IntegerField(default=1)
    
    # Current status of this room
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    
    # Nightly rate for this room
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Is this room available for booking? (Alternative to status)
    is_available = models.BooleanField(default=True)
    
    # Extra details about this room (e.g., "Corner room with great view")
    description = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Each hotel can only have one room with a given room number
        unique_together = ('hotel', 'room_number')

    def __str__(self):
        """Display room info: 'Room 101 - Grand Hotel'"""
        return f"Room {self.room_number} - {self.hotel.name}"


class Guest(models.Model):
    """
    Guest - Customer information for the hotel
    
    Stores all information about guests (visitors/customers).
    Each guest can make multiple bookings.
    Staff manage guest records on behalf of guests — no guest login.
    """
    
    # Gender choices
    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'), ('O', 'Other'))
    
    # Guest's name
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    # Contact information
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    
    # Address information
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    
    # Personal details
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    id_type = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Passport"
    id_number = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Statistics
    total_bookings = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Display guest's full name"""
        return f"{self.first_name} {self.last_name}"


class Booking(models.Model):
    """
    Booking - A reservation made by a guest for a room
    
    Represents a guest's reservation for a specific room during specific dates.
    Each booking has a status tracking its progress through the booking lifecycle.
    
    Key Features:
    - Auto-generates booking_id in format: BK-XXXXXXXX
    - Auto-calculates number_of_nights
    - Auto-calculates total_price
    - Creates a Payment record automatically
    - Validates rooms aren't double-booked
    
    Booking Status Flow:
    Pending → Confirmed → Checked In → Checked Out
    (Can be Cancelled at any point)
    
    Fields:
    - booking_id: Unique booking reference (auto-generated)
    - hotel, guest, room: References to hotel, guest, and room being booked
    - check_in_date, check_out_date: Reservation dates
    - number_of_guests: How many people are staying
    - number_of_nights: How many nights (auto-calculated)
    - total_price: Total cost (auto-calculated)
    - status: Current booking status
    - notes: Special requests or notes
    """
    
    # Define booking statuses
    STATUS_CHOICES = (
        ('Pending', 'Pending'),              # Waiting for payment
        ('Confirmed', 'Confirmed'),          # Payment received, waiting for check-in
        ('Checked In', 'Checked In'),        # Guest is in the room
        ('Checked Out', 'Checked Out'),      # Guest has left
        ('Cancelled', 'Cancelled'),          # Booking was cancelled
    )
    
    # Auto-generated booking reference ID
    booking_id = models.CharField(max_length=20, unique=True, blank=True)
    
    # Which hotel, guest, and room?
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookings')
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    
    # Reservation dates and times (planned)
    check_in_date  = models.DateField()
    check_in_time  = models.TimeField(blank=True, null=True)   # planned check-in time
    check_out_date = models.DateField()
    check_out_time = models.TimeField(blank=True, null=True)   # planned check-out time

    # Actual check-in / check-out timestamps (recorded when action happens)
    actual_check_in  = models.DateTimeField(blank=True, null=True)  # set when guest checks in
    actual_check_out = models.DateTimeField(blank=True, null=True)  # set when guest checks out
    
    # Guest count
    number_of_guests = models.IntegerField(default=1)
    
    # Booking status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # Automatically calculated fields
    number_of_nights = models.IntegerField(default=0)  # Auto-filled: checkout - checkin
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Auto-filled: nightly_rate * nights
    
    # Extra information
    notes = models.TextField(blank=True, null=True)  # Special requests, notes
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        Custom save method - runs automatically when booking is saved
        
        This does important calculations:
        1. Generate booking_id if it doesn't exist
        2. Calculate number_of_nights
        """
        # Generate booking_id if not already created
        if not self.booking_id:
            # Format: BK- followed by 8 random characters
            self.booking_id = 'BK-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # Calculate number of nights
        if self.check_in_date and self.check_out_date:
            self.number_of_nights = (self.check_out_date - self.check_in_date).days
        
        # Call parent save method to actually save to database
        super().save(*args, **kwargs)

    def __str__(self):
        """Display booking info: 'BK-XXXXXXXX - Guest Name'"""
        return f"{self.booking_id} - {self.guest}"


class Payment(models.Model):
    """
    Payment - Tracks payment information for each booking
    
    Each booking has one payment record.
    Tracks what payment method was used, current status, and amount paid.
    
    Payment Methods: Cash, Online (eSewa, Khalti, etc.), Bank Transfer
    Payment Status: Pending, Completed, Failed, or Refunded
    
    Fields:
    - booking: Which booking is this payment for?
    - amount: How much was paid
    - payment_method: Cash, card, digital wallet, etc.
    - status: Has payment been completed?
    - transaction_id: Reference number from payment gateway
    - paid_at: When was payment received
    """
    
    # Available payment methods the hotel accepts
    METHOD_CHOICES = (
        ('Cash', 'Cash'),
        ('eSewa', 'eSewa'),
        ('Khalti', 'Khalti'),
        ('IME Pay', 'IME Pay'),
        ('Fonepay', 'Fonepay'),
        ('ConnectIPS', 'ConnectIPS'),
        ('nPay', 'nPay'),
        ('NIC Asia Bank', 'NIC Asia Bank'),
        ('Nabil Bank', 'Nabil Bank'),
        ('Global IME Bank', 'Global IME Bank'),
        ('Everest Bank', 'Everest Bank'),
        ('Kumari Bank', 'Kumari Bank'),
        ('Sanima Bank', 'Sanima Bank'),
    )
    
    # Possible payment statuses
    STATUS_CHOICES = (
        ('Pending', 'Pending'),        # Waiting for payment
        ('Completed', 'Completed'),    # Payment received
        ('Failed', 'Failed'),          # Payment attempt failed
        ('Refunded', 'Refunded'),      # Payment was refunded to guest
    )
    
    # Which booking is this payment for? (one-to-one relationship)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=METHOD_CHOICES, default='Cash')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # Reference from payment gateway (for tracking transactions)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Optional notes
    notes = models.TextField(blank=True, null=True)
    
    # When was this payment actually received?
    paid_at = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Display payment info: 'Payment for BK-XXXXXXXX'"""
        return f"Payment for {self.booking.booking_id}"


class Staff(models.Model):
    """
    Staff - Employee records
    
    Tracks information about hotel staff members (employees).
    Each staff member is linked to a Django User account.
    
    Fields:
    - user: Link to Django User account
    - employee_id: Unique employee ID
    - position: Job title (Manager, Receptionist, etc.)
    - department: Which department they work in
    - shift: Work shift (Morning, Evening, Night)
    - phone: Contact number
    - hire_date: When they started working
    - salary: Monthly/yearly salary
    - is_active: Are they currently employed?
    """
    
    # Job positions available
    POSITION_CHOICES = (
        ('Manager', 'Manager'),
        ('Receptionist', 'Receptionist'),
        ('Housekeeper', 'Housekeeper'),
        ('Chef', 'Chef'),
        ('Waiter', 'Waiter'),
        ('Security', 'Security'),
        ('Maintenance', 'Maintenance'),
    )
    
    # Work shifts
    SHIFT_CHOICES = (
        ('Morning', 'Morning'),
        ('Evening', 'Evening'),
        ('Night', 'Night'),
    )
    
    # Link to Django User account
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff')
    
    # Employee identification
    employee_id = models.CharField(max_length=20, unique=True)
    
    # Job information
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)
    department = models.CharField(max_length=100, blank=True, null=True)
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES, default='Morning')
    
    # Contact
    phone = models.CharField(max_length=15)
    
    # Employment details
    hire_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Display staff info: 'Full Name - Position'"""
        return f"{self.user.get_full_name()} - {self.position}"


class Service(models.Model):
    """
    Service - Hotel services that guests can purchase
    
    Examples: Room Service, Laundry, Spa, Gym access, Airport Transfer, etc.
    Guests can add these services to their bookings for an additional fee.
    
    Fields:
    - name: Service name
    - service_type: Category of service
    - description: What does this service include?
    - price: Cost of this service
    - is_available: Is the service currently available?
    """
    
    # Service categories
    TYPE_CHOICES = (
        ('Room Service', 'Room Service'),
        ('Laundry', 'Laundry'),
        ('Spa', 'Spa'),
        ('Gym', 'Gym'),
        ('Restaurant', 'Restaurant'),
        ('Parking', 'Parking'),
        ('Tours', 'Tours'),
        ('Other', 'Other'),
    )
    
    # Service information
    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Other')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Is this service available?
    is_available = models.BooleanField(default=True)
    
    # When was this service added?
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Display the service name"""
        return self.name


class BookingService(models.Model):
    """
    BookingService - Links services to bookings
    
    This is a "join table" that connects bookings with services.
    If a guest orders room service, a BookingService record is created.
    
    Fields:
    - booking: Which booking added this service?
    - service: Which service was added?
    - quantity: How many times (e.g., room service ordered 3 times)
    - price: How much was charged for this service (at time of order)
    - added_on: When was this service added to the booking?
    """
    
    # Which booking?
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='services')
    
    # Which service?
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    
    # How many units of this service?
    quantity = models.IntegerField(default=1)
    
    # Price of this service (stored to preserve price history)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # When was it added?
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Display service info: 'Service Name for BK-XXXXXXXX'"""
        return f"{self.service.name} for {self.booking.booking_id}"


class Review(models.Model):
    """
    Review - Guest feedback after checkout
    
    After a guest checks out, they can leave a review rating:
    - Overall rating
    - Cleanliness rating
    - Service rating
    - Food rating
    - Written comment
    - Would they recommend this hotel?
    
    Ratings are 1-5 stars.
    """
    
    # Define rating choices: 1 to 5 stars
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    
    # Link to booking and guest
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='reviews')
    
    # Ratings (1-5 stars)
    rating = models.IntegerField(choices=RATING_CHOICES)  # Overall rating
    cleanliness = models.IntegerField(choices=RATING_CHOICES)
    service = models.IntegerField(choices=RATING_CHOICES)
    food = models.IntegerField(choices=RATING_CHOICES)
    
    # Comments and recommendation
    comment = models.TextField()
    would_recommend = models.BooleanField(default=True)
    
    # When was this review written?
    reviewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Display review info: 'Review by Name - Rating/5'"""
        return f"Review by {self.guest} - {self.rating}/5"


class MaintenanceRequest(models.Model):
    """
    MaintenanceRequest - Track room maintenance tasks
    
    When something needs to be fixed in a room, a maintenance request is created.
    Tracks:
    - What needs to be fixed
    - Priority level (Low/Medium/High/Urgent)
    - Who it's assigned to
    - Current status
    - When it was completed
    
    Fields:
    - room: Which room needs maintenance?
    - priority: How urgent is it?
    - description: What needs to be fixed?
    - status: Is it Open/In Progress/Completed/Cancelled?
    - assigned_to: Which staff member is handling it?
    - completed_at: When was it finished?
    """
    
    # Priority levels
    PRIORITY_CHOICES = (
        ('Low', 'Low'),              # Can wait
        ('Medium', 'Medium'),        # Should be done soon
        ('High', 'High'),            # Urgent
        ('Urgent', 'Urgent'),        # Emergency - fix immediately
    )
    
    # Status tracking
    STATUS_CHOICES = (
        ('Open', 'Open'),                    # Just created, not started
        ('In Progress', 'In Progress'),      # Someone is working on it
        ('Completed', 'Completed'),          # Fixed!
        ('Cancelled', 'Cancelled'),          # Not needed
    )
    
    # Which room?
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='maintenance_requests')
    
    # How urgent?
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    
    # What's wrong?
    description = models.TextField()
    
    # Current status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    
    # Who's assigned to fix it?
    assigned_to = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_requests')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        """Display: 'Maintenance HIGH - Room 101'"""
        return f"Maintenance {self.priority} - Room {self.room.room_number}"


class Complaint(models.Model):
    """
    Complaint - Track guest complaints and resolutions
    
    When a guest has an issue (cleanliness, noise, service, etc.),
    a complaint record is created to track it.
    
    Fields:
    - booking, guest: Who complained?
    - complaint_type: What's the complaint about?
    - description: Details of the problem
    - status: Is it Open/In Progress/Resolved/Closed?
    - resolution: How was it resolved?
    - resolved_at: When was it fixed?
    """
    
    # Types of complaints
    TYPE_CHOICES = (
        ('Cleanliness', 'Cleanliness'),
        ('Noise', 'Noise'),
        ('Service', 'Service'),
        ('Facilities', 'Facilities'),
        ('Other', 'Other'),
    )
    
    # Complaint resolution status
    STATUS_CHOICES = (
        ('Open', 'Open'),                  # Just reported
        ('In Progress', 'In Progress'),    # Being worked on
        ('Resolved', 'Resolved'),          # Fixed
        ('Closed', 'Closed'),              # Case closed
    )
    
    # Link to booking and guest
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='complaints')
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='complaints')
    
    # What's the complaint?
    complaint_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField()
    
    # Resolution tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    resolution = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        """Display: 'Complaint - Type by GuestName'"""
        return f"Complaint - {self.complaint_type} by {self.guest}"


class RoomCleaning(models.Model):
    """
    RoomCleaning - Tracks cleaning sessions for rooms after checkout

    Every time a guest checks out, a RoomCleaning record is created automatically.
    Housekeeping staff can update the status from Pending → In Progress → Completed.
    When marked Completed, the room is automatically set back to Available.

    Status Flow:
    Pending → In Progress → Completed

    Fields:
    - room: Which room needs cleaning
    - booking: The checkout booking that triggered this (optional link)
    - status: Pending / In Progress / Completed
    - notes: Any special instructions (e.g., deep clean, stain on carpet)
    - assigned_to: Which staff member is handling it (optional)
    - started_at: When cleaning started
    - completed_at: When cleaning was finished
    - created_at: When the cleaning task was created (at checkout)
    """

    STATUS_CHOICES = (
        ('Pending', 'Pending'),          # Waiting to be cleaned
        ('In Progress', 'In Progress'),  # Currently being cleaned
        ('Completed', 'Completed'),      # Cleaning done, room is available
    )

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='cleaning_sessions')
    booking = models.ForeignKey(
        'Booking', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='cleaning_session'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    notes = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='cleaning_tasks'
    )
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Cleaning Room {self.room.room_number} - {self.status}"


class HotelSettings(models.Model):
    """
    HotelSettings - System-wide configuration (Singleton)
    
    This model stores all system-wide settings in a single database row.
    It's a "singleton" pattern - there should only ever be ONE row.
    
    Stores:
    - Currency and payment settings
    - Check-in/check-out times
    - Tax rates
    - Timezone and language
    - Other system-wide configurations
    
    How to use:
    settings = HotelSettings.get()  # Always returns the one row (creates if needed)
    settings.currency  # Access any setting
    """
    
    # Payment settings
    currency        = models.CharField(max_length=20,  default='USD ($)')
    payment_gateway = models.CharField(max_length=50,  default='Stripe')
    tax_rate        = models.CharField(max_length=10,  default='10')
    currency_code   = models.CharField(max_length=5,   default='USD')
    base_rate       = models.CharField(max_length=20,  default='150')
    
    # Format settings
    date_format     = models.CharField(max_length=20,  default='MM/DD/YYYY')
    time_zone       = models.CharField(max_length=30,  default='UTC-5')
    language        = models.CharField(max_length=30,  default='English')
    
    # Hotel operations
    check_in_time   = models.CharField(max_length=10,  default='15:00')  # Default: 3 PM
    check_out_time  = models.CharField(max_length=10,  default='11:00') # Default: 11 AM
    cleaning_time   = models.CharField(max_length=10,  default='30')    # Minutes between checkouts
    payment_timeout = models.CharField(max_length=10,  default='3600')  # Seconds before payment expires
    
    # When was this updated?
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Hotel Settings'
        verbose_name_plural = 'Hotel Settings'

    def __str__(self):
        """Display: 'Hotel Settings (currency: USD ($))'"""
        return f'Hotel Settings (currency: {self.currency})'

    @classmethod
    def get(cls):
        """
        Get or Create the singleton settings object
        
        This is a special method that ensures there's always exactly one
        HotelSettings row in the database.
        
        Usage:
        settings = HotelSettings.get()
        
        Returns:
        HotelSettings object (creates it if it doesn't exist)
        """
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj