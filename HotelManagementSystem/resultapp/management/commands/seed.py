"""
MANAGEMENT COMMAND: Seed Database

This management command creates sample data for testing and development.
It's an alternative/complement to init_hotel.py.

Usage:
python manage.py seed

This creates:
- Hotel details
- Room types (Single, Double, Suite, Deluxe)
- Sample rooms in different states (Available, Occupied, Maintenance)
- Sample guests
- Sample bookings with payments
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from resultapp.models import Hotel, RoomType, Room, Guest, Booking, Payment
from decimal import Decimal
from datetime import date


class Command(BaseCommand):
    """
    Django Management Command - Seeds database with test data
    
    Run with: python manage.py seed
    """
    
    # Description shown in: python manage.py help seed
    help = 'Seed database with sample data'

    def handle(self, *args, **kwargs):
        """
        Main function - runs when command is executed
        
        Creates all sample data for testing
        """
        
        self.stdout.write('Seeding data...')

        # ──────────────────────────────────────────────────
        # STEP 1: Create Hotel
        # ──────────────────────────────────────────────────
        
        hotel, _ = Hotel.objects.get_or_create(
            name='Grand Hotel',
            defaults={
                'address': '123 Main Street',
                'city': 'New York',
                'state': 'NY',
                'postal_code': '10001',
                'phone': '1-800-HOTEL',
                'email': 'info@grandhotel.com',
                'total_rooms': 8
            }
        )

        # ──────────────────────────────────────────────────
        # STEP 2: Create Room Types
        # ──────────────────────────────────────────────────
        
        # Single room - sleeps 1 person
        single, _ = RoomType.objects.get_or_create(
            name='Single', 
            defaults={'base_price': Decimal('99.99'), 'capacity': 1}
        )
        
        # Double room - sleeps 2 people
        double, _ = RoomType.objects.get_or_create(
            name='Double', 
            defaults={'base_price': Decimal('149.99'), 'capacity': 2}
        )
        
        # Suite - sleeps 4 people
        suite, _ = RoomType.objects.get_or_create(
            name='Suite', 
            defaults={'base_price': Decimal('299.99'), 'capacity': 4}
        )
        
        # Deluxe - sleeps 3 people
        deluxe, _ = RoomType.objects.get_or_create(
            name='Deluxe', 
            defaults={'base_price': Decimal('199.99'), 'capacity': 3}
        )

        # ──────────────────────────────────────────────────
        # STEP 3: Create Sample Rooms
        # ──────────────────────────────────────────────────
        
        # Room data: (number, type, floor, price, status)
        # Shows rooms in different statuses for testing
        rooms_data = [
            ('101', single, 1, Decimal('99.99'), 'Available'),     # Available for booking
            ('102', single, 1, Decimal('99.99'), 'Available'),     # Available for booking
            ('201', double, 2, Decimal('149.99'), 'Available'),    # Available for booking
            ('202', double, 2, Decimal('149.99'), 'Occupied'),     # Currently occupied
            ('301', suite, 3, Decimal('299.99'), 'Available'),     # Available for booking
            ('302', deluxe, 3, Decimal('199.99'), 'Available'),    # Available for booking
            ('401', suite, 4, Decimal('349.99'), 'Maintenance'),   # Under maintenance
            ('402', deluxe, 4, Decimal('219.99'), 'Available'),    # Available for booking
        ]
        
        # Create each room
        for number, rtype, floor, price, status in rooms_data:
            Room.objects.get_or_create(
                hotel=hotel, 
                room_number=number,
                defaults={
                    'room_type': rtype,
                    'floor': floor,
                    'price_per_night': price,
                    'status': status,
                    # Mark as available if status is "Available"
                    'is_available': status == 'Available'
                }
            )

        # ──────────────────────────────────────────────────
        # STEP 4: Create Sample Guests
        # ──────────────────────────────────────────────────
        
        # Guest 1 - John Doe
        guest1, _ = Guest.objects.get_or_create(
            email='john.doe@email.com',
            defaults={
                'first_name': 'John', 
                'last_name': 'Doe', 
                'phone': '555-0101'
            }
        )
        
        # Guest 2 - Jane Smith
        guest2, _ = Guest.objects.get_or_create(
            email='jane.smith@email.com',
            defaults={
                'first_name': 'Jane', 
                'last_name': 'Smith', 
                'phone': '555-0102'
            }
        )
        
        # Guest 3 - Bob Wilson
        guest3, _ = Guest.objects.get_or_create(
            email='bob.wilson@email.com',
            defaults={
                'first_name': 'Bob', 
                'last_name': 'Wilson', 
                'phone': '555-0103'
            }
        )

        # ──────────────────────────────────────────────────
        # STEP 5: Create Sample Bookings
        # ──────────────────────────────────────────────────
        
        # Get rooms for bookings
        room202 = Room.objects.get(hotel=hotel, room_number='202')
        room201 = Room.objects.get(hotel=hotel, room_number='201')

        # Booking 1: John Doe in Double Room
        # Check-in: May 1, Check-out: May 5 (4 nights)
        # Status: Confirmed (payment received)
        if not Booking.objects.filter(guest=guest1, room=room202).exists():
            b1 = Booking.objects.create(
                hotel=hotel, 
                guest=guest1, 
                room=room202,
                check_in_date=date(2025, 5, 1),
                check_out_date=date(2025, 5, 5),
                number_of_guests=2,
                status='Confirmed',
                total_price=Decimal('599.96')  # 4 nights * 149.99
            )
            
            # Create payment for this booking (already completed)
            Payment.objects.get_or_create(
                booking=b1,
                defaults={
                    'amount': Decimal('599.96'), 
                    'status': 'Completed'
                }
            )

        # Booking 2: Jane Smith in Double Room
        # Check-in: May 10, Check-out: May 12 (2 nights)
        # Status: Pending (waiting for payment)
        if not Booking.objects.filter(guest=guest2, room=room201).exists():
            b2 = Booking.objects.create(
                hotel=hotel, 
                guest=guest2, 
                room=room201,
                check_in_date=date(2025, 5, 10),
                check_out_date=date(2025, 5, 12),
                number_of_guests=1,
                status='Pending',
                total_price=Decimal('299.98')  # 2 nights * 149.99
            )
            
            # Create payment for this booking (still pending)
            Payment.objects.get_or_create(
                booking=b2,
                defaults={
                    'amount': Decimal('299.98'), 
                    'status': 'Pending'
                }
            )

        # ──────────────────────────────────────────────────
        # SUCCESS!
        # ──────────────────────────────────────────────────
        
        self.stdout.write(self.style.SUCCESS('✅ Database seeded successfully!'))