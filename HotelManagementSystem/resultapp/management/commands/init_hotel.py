"""
MANAGEMENT COMMAND: Initialize Hotel

This is a Django management command that sets up sample data for the hotel system.
It's run once to prepare the database with initial data.

For beginners: Management commands are special Django commands you run from terminal
using: python manage.py init_hotel [options]

This command:
1. Creates an admin user
2. Creates a hotel
3. Creates room types (Single, Double, Suite)
4. Creates sample rooms
5. Creates sample guests
6. Creates hotel services

Usage:
python manage.py init_hotel
python manage.py init_hotel --hotel-name "My Hotel" --admin-username "myapp_admin"
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from resultapp.models import Hotel, RoomType, Room, Guest, Staff, Service
from decimal import Decimal
from datetime import date


class Command(BaseCommand):
    """
    Django Management Command Class
    
    All management commands inherit from BaseCommand.
    The handle() method is called when user runs the command.
    """
    
    # Description shown when user runs: python manage.py help init_hotel
    help = 'Initialize hotel with sample data'

    def add_arguments(self, parser):
        """
        Define command-line arguments that users can pass
        
        For beginners: This allows users to customize the command:
        python manage.py init_hotel --hotel-name "Custom Hotel"
        """
        
        # --hotel-name: What should the hotel be called?
        parser.add_argument(
            '--hotel-name', 
            type=str, 
            default='Grand Hotel', 
            help='Hotel name'
        )
        
        # --admin-username: What username for the admin account?
        parser.add_argument(
            '--admin-username', 
            type=str, 
            default='admin', 
            help='Admin username'
        )

    def handle(self, *args, **options):
        """
        Main function - runs when the command is executed
        
        Args:
            args: Positional arguments (if any)
            options: Named arguments from add_arguments()
        
        This function does all the initialization work.
        """
        
        # Get the arguments passed by the user
        hotel_name = options['hotel_name']
        admin_username = options['admin_username']

        # ─────────────────────────────────────────────────────
        # STEP 1: Create Admin User
        # ─────────────────────────────────────────────────────
        
        # Check if admin user already exists
        if not User.objects.filter(username=admin_username).exists():
            # Create a superuser (has all permissions)
            User.objects.create_superuser(
                username=admin_username,
                email=f'{admin_username}@hotel.com',
                password='admin123',
                first_name='Hotel',
                last_name='Admin'
            )
            # Tell the user that admin was created
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created admin user: {admin_username} / admin123'
                )
            )

        # ─────────────────────────────────────────────────────
        # STEP 2: Create Hotel
        # ─────────────────────────────────────────────────────
        
        # Create hotel or use existing one
        hotel, created = Hotel.objects.get_or_create(
            name=hotel_name,
            # If hotel doesn't exist, create with these details
            defaults={
                'address': '123 Main Street',
                'city': 'Kathmandu',
                'state': 'Bagmati',
                'postal_code': '44600',
                'phone': '+977-1-4000000',
                'email': 'info@grandhotel.com',
                'website': 'https://grandhotel.com',
                'total_rooms': 20
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created hotel: {hotel_name}')
            )

        # ─────────────────────────────────────────────────────
        # STEP 3: Create Room Types
        # ─────────────────────────────────────────────────────
        
        # Define the room types the hotel offers
        room_types = [
            {
                'name': 'Single', 
                'base_price': Decimal('50.00'), 
                'capacity': 1, 
                'amenities': 'WiFi, TV, AC'
            },
            {
                'name': 'Double', 
                'base_price': Decimal('90.00'), 
                'capacity': 2, 
                'amenities': 'WiFi, TV, AC, Mini Fridge'
            },
            {
                'name': 'Suite', 
                'base_price': Decimal('200.00'), 
                'capacity': 4, 
                'amenities': 'WiFi, TV, AC, Mini Bar, Jacuzzi'
            },
        ]
        
        # Create each room type
        rt_objects = {}
        for rt in room_types:
            obj, _ = RoomType.objects.get_or_create(
                name=rt['name'], 
                defaults=rt
            )
            # Store for later use
            rt_objects[rt['name']] = obj

        # ─────────────────────────────────────────────────────
        # STEP 4: Create Sample Rooms
        # ─────────────────────────────────────────────────────
        
        # List of rooms to create (room_number, room_type_name, floor)
        rooms_data = [
            ('101', 'Single', 1), ('102', 'Single', 1), ('103', 'Single', 1),
            ('201', 'Double', 2), ('202', 'Double', 2), ('203', 'Double', 2),
            ('301', 'Suite', 3), ('302', 'Suite', 3),
        ]
        
        # Create each room
        for room_number, rt_name, floor in rooms_data:
            rt = rt_objects[rt_name]  # Get the room type
            Room.objects.get_or_create(
                hotel=hotel, 
                room_number=room_number,
                # If room doesn't exist, create with these details
                defaults={
                    'room_type': rt,
                    'floor': floor,
                    'status': 'Available',
                    'price_per_night': rt.base_price,
                    'is_available': True
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Created sample rooms'))

        # ─────────────────────────────────────────────────────
        # STEP 5: Create Sample Guests
        # ─────────────────────────────────────────────────────
        
        # Sample guest data
        guests_data = [
            {
                'first_name': 'John', 
                'last_name': 'Doe', 
                'email': 'john@example.com', 
                'phone': '+1-555-0101', 
                'country': 'USA'
            },
            {
                'first_name': 'Jane', 
                'last_name': 'Smith', 
                'email': 'jane@example.com', 
                'phone': '+44-7700-900001', 
                'country': 'UK'
            },
        ]
        
        # Create each guest
        for g in guests_data:
            Guest.objects.get_or_create(
                email=g['email'], 
                defaults=g
            )
        
        self.stdout.write(self.style.SUCCESS('Created sample guests'))

        # ─────────────────────────────────────────────────────
        # STEP 6: Create Hotel Services
        # ─────────────────────────────────────────────────────
        
        # Services the hotel offers (that guests can purchase)
        services_data = [
            {
                'name': 'Room Service', 
                'service_type': 'Room Service', 
                'description': 'Food delivery to room', 
                'price': Decimal('20.00')
            },
            {
                'name': 'Laundry', 
                'service_type': 'Laundry', 
                'description': 'Clothes washing service', 
                'price': Decimal('15.00')
            },
            {
                'name': 'Spa', 
                'service_type': 'Spa', 
                'description': 'Full body spa treatment', 
                'price': Decimal('100.00')
            },
            {
                'name': 'Gym Access', 
                'service_type': 'Gym', 
                'description': 'Access to fitness center', 
                'price': Decimal('0.00')
            },
            {
                'name': 'Airport Transfer', 
                'service_type': 'Tours', 
                'description': 'Airport pickup/drop', 
                'price': Decimal('30.00')
            },
        ]
        
        # Create each service
        for s in services_data:
            Service.objects.get_or_create(
                name=s['name'], 
                defaults=s
            )
        
        self.stdout.write(self.style.SUCCESS('Created sample services'))

        # ─────────────────────────────────────────────────────
        # DONE! Print success message
        # ─────────────────────────────────────────────────────
        
        self.stdout.write(self.style.SUCCESS('\n✅ Hotel system initialized successfully!'))
        self.stdout.write(self.style.SUCCESS(f'   Admin: http://localhost:8000/admin/'))
        self.stdout.write(self.style.SUCCESS(f'   API:   http://localhost:8000/api/'))
        self.stdout.write(self.style.SUCCESS(f'   Login: {admin_username} / admin123'))
