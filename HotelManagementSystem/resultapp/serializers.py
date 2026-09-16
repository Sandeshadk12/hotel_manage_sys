"""
SERIALIZERS - Convert Django Models to/from JSON

Serializers are tools that convert:
- Django Model instances → JSON (for API responses)
- JSON input → Django Model instances (for API requests)

This makes it easy to send data to the frontend as JSON.

For beginners: Think of serializers as "translators" between Python objects and JSON.
When a user requests hotel data via API, the serializer converts the Python
object to JSON so the browser can understand it.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Hotel, RoomType, Room, Guest, Booking, Payment,
    Staff, Service, BookingService, Review, MaintenanceRequest, Complaint
)


# ═══════════════════════════════════════════════════════════════
# BASIC SERIALIZERS (for simple models)
# ═══════════════════════════════════════════════════════════════

class UserSerializer(serializers.ModelSerializer):
    """
    Convert Django User model to JSON
    
    Shows: ID, username, name, email
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class HotelSerializer(serializers.ModelSerializer):
    """
    Convert Hotel model to JSON
    
    Shows all hotel fields
    """
    class Meta:
        model = Hotel
        fields = '__all__'


class RoomTypeSerializer(serializers.ModelSerializer):
    """
    Convert RoomType model to JSON
    
    Shows all room type fields
    """
    class Meta:
        model = RoomType
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    """
    Convert Service model to JSON
    
    Shows all service fields
    """
    class Meta:
        model = Service
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    """
    Convert Review model to JSON
    
    Shows all review fields including ratings
    """
    class Meta:
        model = Review
        fields = '__all__'


# ═══════════════════════════════════════════════════════════════
# ROOM SERIALIZERS (different views for list vs detail)
# ═══════════════════════════════════════════════════════════════

class RoomListSerializer(serializers.ModelSerializer):
    """
    Room List View - Shows abbreviated room info
    
    Includes: room_type name as a readable field
    This is used when showing a list of rooms (doesn't need all details)
    """
    # Show room type name instead of just ID
    room_type_name = serializers.CharField(source='room_type.name', read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'room_number', 'room_type', 'room_type_name', 'floor', 'status', 'price_per_night', 'is_available']


class RoomDetailSerializer(serializers.ModelSerializer):
    """
    Room Detail View - Shows complete room info
    
    Includes: Full RoomType details + all room fields
    This is used when viewing a single room's complete details
    """
    # Show full room type details
    room_type = RoomTypeSerializer(read_only=True)
    
    # Also allow setting room_type by ID when creating/updating
    room_type_id = serializers.PrimaryKeyRelatedField(
        queryset=RoomType.objects.all(), source='room_type', write_only=True, required=False
    )

    class Meta:
        model = Room
        fields = '__all__'


# ═══════════════════════════════════════════════════════════════
# GUEST SERIALIZERS
# ═══════════════════════════════════════════════════════════════

class GuestListSerializer(serializers.ModelSerializer):
    """
    Guest List View - Shows basic guest info
    
    Used when listing all guests (summary view)
    """
    class Meta:
        model = Guest
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'country', 'total_bookings']


class GuestDetailSerializer(serializers.ModelSerializer):
    """
    Guest Detail View - Shows complete guest info
    
    Used when viewing a single guest's full profile
    """
    class Meta:
        model = Guest
        fields = '__all__'


# ═══════════════════════════════════════════════════════════════
# PAYMENT SERIALIZER
# ═══════════════════════════════════════════════════════════════

class PaymentSerializer(serializers.ModelSerializer):
    """
    Convert Payment model to JSON
    
    Shows payment details including method and status
    """
    class Meta:
        model = Payment
        fields = '__all__'


# ═══════════════════════════════════════════════════════════════
# BOOKING SERIALIZERS
# ═══════════════════════════════════════════════════════════════

class BookingListSerializer(serializers.ModelSerializer):
    """
    Booking List View - Shows key booking info
    
    Used when listing bookings
    Includes: guest name, room number, dates, price
    """
    # Show guest name instead of just ID
    guest_name = serializers.SerializerMethodField()
    
    # Show room number instead of just ID
    room_number = serializers.CharField(source='room.room_number', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'booking_id', 'guest_name', 'room_number', 'check_in_date',
                  'check_in_time', 'check_out_date', 'check_out_time',
                  'actual_check_in', 'actual_check_out',
                  'status', 'total_price', 'number_of_nights']

    def get_guest_name(self, obj):
        """Custom method to get guest's full name"""
        return str(obj.guest)


class BookingDetailSerializer(serializers.ModelSerializer):
    """
    Booking Detail View - Shows complete booking info
    
    Used when viewing a single booking's details
    Includes: Full guest details, room details, payment info, and services
    """
    # Show complete guest information
    guest = GuestListSerializer(read_only=True)
    
    # Show complete room information
    room = RoomListSerializer(read_only=True)
    
    # Show payment information
    payment = PaymentSerializer(read_only=True)
    
    # Show all services added to this booking
    services = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = '__all__'
    
    def get_services(self, obj):
        """Get all services linked to this booking"""
        booking_services = obj.services.all()
        return BookingServiceSerializer(booking_services, many=True).data


# ═══════════════════════════════════════════════════════════════
# BOOKING SERVICE SERIALIZER
# ═══════════════════════════════════════════════════════════════

class BookingServiceSerializer(serializers.ModelSerializer):
    """
    Convert BookingService model to JSON
    
    Shows which service was added to a booking
    Includes: Service name for readability
    """
    # Show service name instead of just ID
    service_name = serializers.CharField(source='service.name', read_only=True)

    class Meta:
        model = BookingService
        fields = '__all__'


# ═══════════════════════════════════════════════════════════════
# STAFF SERIALIZERS
# ═══════════════════════════════════════════════════════════════

class StaffListSerializer(serializers.ModelSerializer):
    """
    Staff List View - Shows key staff info
    
    Used when listing all staff members
    Includes: User details, position, shift
    """
    # Show full user information
    user = UserSerializer(read_only=True)

    class Meta:
        model = Staff
        fields = ['id', 'user', 'employee_id', 'position', 'department', 'shift', 'is_active']


class StaffDetailSerializer(serializers.ModelSerializer):
    """
    Staff Detail View - Shows complete staff info
    
    Used when viewing a single staff member's details
    Includes: Full user details, salary, hire date, etc.
    """
    # Show full user information
    user = UserSerializer(read_only=True)
    
    # Allow setting user by ID when creating/updating
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )

    class Meta:
        model = Staff
        fields = '__all__'


# ═══════════════════════════════════════════════════════════════
# MAINTENANCE REQUEST SERIALIZER
# ═══════════════════════════════════════════════════════════════

class MaintenanceRequestSerializer(serializers.ModelSerializer):
    """
    Convert MaintenanceRequest model to JSON
    
    Shows maintenance request details
    Includes: Room number and assigned staff member name for readability
    """
    # Show room number instead of just ID
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    
    # Show assigned staff member's name
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = MaintenanceRequest
        fields = '__all__'

    def get_assigned_to_name(self, obj):
        """Get the name of the staff member assigned to this maintenance request"""
        if obj.assigned_to:
            return obj.assigned_to.user.get_full_name()
        return None


# ═══════════════════════════════════════════════════════════════
# COMPLAINT SERIALIZER
# ═══════════════════════════════════════════════════════════════

class ComplaintSerializer(serializers.ModelSerializer):
    """
    Convert Complaint model to JSON
    
    Shows complaint details
    Includes: Guest name for readability
    """
    # Show guest name instead of just ID
    guest_name = serializers.SerializerMethodField()

    class Meta:
        model = Complaint
        fields = '__all__'

    def get_guest_name(self, obj):
        """Get the guest's full name"""
        return str(obj.guest)


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['hotel', 'guest', 'room', 'check_in_date', 'check_in_time',
                  'check_out_date', 'check_out_time', 'number_of_guests', 'notes']

    def validate(self, data):
        if data['check_in_date'] >= data['check_out_date']:
            raise serializers.ValidationError("Check-out date must be after check-in date.")
        room = data['room']
        if not room.is_available:
            raise serializers.ValidationError("This room is not available.")
        # Check for overlapping bookings
        overlapping = Booking.objects.filter(
            room=room,
            status__in=['Confirmed', 'Checked In', 'Pending'],
            check_in_date__lt=data['check_out_date'],
            check_out_date__gt=data['check_in_date']
        )
        if overlapping.exists():
            raise serializers.ValidationError("Room is already booked for these dates.")
        return data

    def create(self, validated_data):
        room = validated_data['room']
        nights = (validated_data['check_out_date'] - validated_data['check_in_date']).days
        total_price = room.price_per_night * nights
        booking = Booking.objects.create(total_price=total_price, **validated_data)
        # Auto-create payment record
        Payment.objects.create(
            booking=booking,
            amount=total_price,
            status='Pending'
        )
        return booking
