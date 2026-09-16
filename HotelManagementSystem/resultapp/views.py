from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

# ─── Role permission helpers ─────────────────────────────────
def require_auth(fn):
    """Ensure DRF api_view is authenticated."""
    def wrapper(request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        return fn(request, *args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

def admin_only(view_func):
    """Only admin can access."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Not authenticated'}, status=401)
        if get_role(request.user) != 'admin':
            return JsonResponse({'error': 'Admin access required'}, status=403)
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

def manager_or_above(view_func):
    """Admin and Manager can access."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Not authenticated'}, status=401)
        if get_role(request.user) not in ('admin', 'manager'):
            return JsonResponse({'error': 'Manager access required'}, status=403)
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper
from django.utils import timezone
from django.db.models import Avg, Sum, Q
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from accounts.views import get_role
from datetime import date, datetime
from decimal import Decimal

from .models import (
    Hotel, RoomType, Room, Guest, Booking, Payment,
    Staff, Service, BookingService, Review, MaintenanceRequest, Complaint,
    RoomCleaning, HotelSettings
)
from .serializers import (
    HotelSerializer, RoomTypeSerializer, RoomListSerializer, RoomDetailSerializer,
    GuestListSerializer, GuestDetailSerializer,
    BookingListSerializer, BookingDetailSerializer, BookingCreateSerializer,
    PaymentSerializer, StaffListSerializer, StaffDetailSerializer,
    ServiceSerializer, BookingServiceSerializer, ReviewSerializer,
    MaintenanceRequestSerializer, ComplaintSerializer
)

# ─── Page Views ───────────────────────────────────────────────
def home(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    return redirect('/accounts/login/')

@login_required
def dashboard(request):
    return render(request, 'dashboard/dashboard.html', {'role': get_role(request.user), 'username': request.user.get_full_name() or request.user.username})

@login_required
def bookings(request):
    return render(request, 'booking/booking.html', {'role': get_role(request.user), 'username': request.user.get_full_name() or request.user.username})

@login_required
def rooms(request):
    return render(request, 'rooms/rooms.html', {'role': get_role(request.user), 'username': request.user.get_full_name() or request.user.username})

@login_required
def customers(request):
    return render(request, 'customers/customers.html', {'role': get_role(request.user), 'username': request.user.get_full_name() or request.user.username})

@login_required
def payments(request):
    return render(request, 'payments/payments.html', {'role': get_role(request.user), 'username': request.user.get_full_name() or request.user.username})

@login_required
def users_view(request):
    if get_role(request.user) != 'admin':
        return redirect('/dashboard/')
    return render(request, 'users/users.html', {'role': get_role(request.user), 'username': request.user.get_full_name() or request.user.username})

@login_required
def settings_view(request):
    if get_role(request.user) not in ('admin', 'manager'):
        return redirect('/dashboard/')
    return render(request, 'settings/settings.html', {'role': get_role(request.user), 'username': request.user.get_full_name() or request.user.username})

@login_required
def housekeeping_view(request):
    return render(request, 'housekeeping/housekeeping.html', {'role': get_role(request.user), 'username': request.user.get_full_name() or request.user.username})

@login_required
def complaints_view(request):
    return render(request, 'complaints/complaints.html', {'role': get_role(request.user), 'username': request.user.get_full_name() or request.user.username})

@login_required
def maintenance_view(request):
    return render(request, 'maintenance/maintenance.html', {'role': get_role(request.user), 'username': request.user.get_full_name() or request.user.username})

@login_required
def staff_view(request):
    if get_role(request.user) not in ('admin', 'manager'):
        return redirect('/dashboard/')
    return render(request, 'staff/staff.html', {'role': get_role(request.user), 'username': request.user.get_full_name() or request.user.username})

@login_required
def services_view(request):
    return render(request, 'services/services.html', {'role': get_role(request.user), 'username': request.user.get_full_name() or request.user.username})

@login_required
def reviews_view(request):
    return render(request, 'reviews/reviews.html', {'role': get_role(request.user), 'username': request.user.get_full_name() or request.user.username})


# ─── PUBLIC endpoint: hotel name for login page ──────────────
@api_view(['GET'])
def public_hotel_name(request):
    hotel = Hotel.objects.first()
    return Response({'hotelName': hotel.name if hotel else 'Hotel Management System'})


# ─── API Views ────────────────────────────────────────────────
@api_view(['GET'])
@require_auth
def dashboard_data(request):
    today = date.today()
    total_rooms    = Room.objects.count()
    total_bookings = Booking.objects.count()
    total_guests   = Guest.objects.count()
    total_revenue  = Payment.objects.filter(status='Completed').aggregate(total=Sum('amount'))['total'] or 0

    room_status = {
        'available':   Room.objects.filter(status='Available').count(),
        'occupied':    Room.objects.filter(status='Occupied').count(),
        'maintenance': Room.objects.filter(status='Maintenance').count(),
        'cleaning':    Room.objects.filter(status='Cleaning').count(),
    }
    occupied_total = room_status['occupied']
    occupancy_rate = round((occupied_total / total_rooms * 100) if total_rooms > 0 else 0, 1)

    # Today's workflow
    arrivals_today   = Booking.objects.filter(check_in_date=today,  status='Confirmed').count()
    departures_today = Booking.objects.filter(check_out_date=today,  status='Checked In').count()
    pending_payments = Payment.objects.filter(status='Pending').count()
    open_complaints  = Complaint.objects.filter(status__in=['Open', 'In Progress']).count()
    pending_cleaning = RoomCleaning.objects.filter(status__in=['Pending', 'In Progress']).count()

    recent_bookings = Booking.objects.order_by('-created_at')[:5]
    serializer = BookingListSerializer(recent_bookings, many=True)

    return Response({
        'totalRooms':       total_rooms,
        'totalBookings':    total_bookings,
        'totalGuests':      total_guests,
        'totalRevenue':     float(total_revenue),
        'occupancyRate':    occupancy_rate,
        'arrivalsToday':    arrivals_today,
        'departuresToday':  departures_today,
        'pendingPayments':  pending_payments,
        'openComplaints':   open_complaints,
        'pendingCleaning':  pending_cleaning,
        'roomStatus':       room_status,
        'bookings':         serializer.data,
    })

@api_view(['POST'])
@require_auth
def create_booking(request):
    data = request.data
    guest_name     = data.get('guestName') or data.get('name')
    email          = data.get('email') or data.get('guestEmail')
    phone          = data.get('phone') or data.get('guestPhone')
    room_type_name = data.get('roomType')
    room_number    = data.get('roomNumber')
    guests         = int(data.get('guests') or data.get('numberOfGuests') or 1)
    check_in       = data.get('checkIn') or data.get('check_in')
    check_out      = data.get('checkOut') or data.get('check_out')
    notes          = data.get('notes', '')

    check_in_time_str  = data.get('checkInTime')  or data.get('check_in_time')
    check_out_time_str = data.get('checkOutTime') or data.get('check_out_time')

    if not guest_name or not email or not room_type_name or not check_in or not check_out:
        return Response({'error': 'Missing booking information'}, status=400)

    try:
        check_in_date  = datetime.strptime(check_in,  '%Y-%m-%d').date()
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
    except ValueError:
        return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

    if check_in_date < date.today():
        return Response({'error': 'Check-in date cannot be in the past.'}, status=400)
    if check_in_date >= check_out_date:
        return Response({'error': 'Check-out date must be after check-in date.'}, status=400)

    # Parse optional times
    check_in_time = check_out_time = None
    for time_str, attr in [(check_in_time_str, 'check_in_time'), (check_out_time_str, 'check_out_time')]:
        if time_str:
            for fmt in ('%H:%M:%S', '%H:%M'):
                try:
                    parsed = datetime.strptime(time_str, fmt).time()
                    if attr == 'check_in_time':
                        check_in_time = parsed
                    else:
                        check_out_time = parsed
                    break
                except ValueError:
                    continue

    hotel = Hotel.objects.first()
    if not hotel:
        return Response({'error': 'No hotel configured'}, status=500)

    # Get or create guest — also update phone if it changed
    guest, created = Guest.objects.get_or_create(
        email=email,
        defaults={
            'first_name': guest_name.split()[0],
            'last_name':  ' '.join(guest_name.split()[1:]) if len(guest_name.split()) > 1 else '',
            'phone':      phone or ''
        }
    )
    if not created and phone and guest.phone != phone:
        guest.phone = phone
        guest.save(update_fields=['phone'])

    # Find room
    room = None
    if room_number:
        room = Room.objects.filter(hotel=hotel, room_number=room_number).first()
    if not room:
        room = Room.objects.filter(
            hotel=hotel,
            room_type__name__iexact=room_type_name,
            status='Available',
            is_available=True
        ).first()
    if not room:
        return Response({'error': 'No available room found.'}, status=400)

    # Validate guest count vs room capacity
    if room.room_type and guests > room.room_type.capacity:
        return Response({'error': f'Room capacity is {room.room_type.capacity} guests max.'}, status=400)

    # Double-booking check — include ALL active statuses including Reserved
    overlapping = Booking.objects.filter(
        room=room,
        status__in=['Confirmed', 'Checked In', 'Pending', 'Reserved'],
        check_in_date__lt=check_out_date,
        check_out_date__gt=check_in_date
    )
    if overlapping.exists():
        return Response({'error': 'Room already booked for these dates.'}, status=400)

    nights      = (check_out_date - check_in_date).days
    total_price = room.price_per_night * Decimal(nights)
    booking = Booking.objects.create(
        hotel=hotel, guest=guest, room=room,
        check_in_date=check_in_date, check_in_time=check_in_time,
        check_out_date=check_out_date, check_out_time=check_out_time,
        number_of_guests=guests, status='Pending',
        total_price=total_price, notes=notes
    )
    room.status = 'Reserved'
    room.is_available = False
    room.save()
    Payment.objects.create(booking=booking, amount=total_price, status='Pending')
    return Response(BookingDetailSerializer(booking).data, status=201)

@api_view(['POST'])
@manager_or_above
def bulk_add_rooms(request):
    data = request.data
    start_room = data.get('startRoom')
    end_room = data.get('endRoom')
    room_type_name = data.get('roomType')
    price = data.get('price')
    floor = int(data.get('floor') or 1)

    if not all([start_room, end_room, room_type_name, price]):
        return Response({'error': 'startRoom, endRoom, roomType and price are required'}, status=400)

    try:
        start_room = int(start_room)
        end_room = int(end_room)
    except (ValueError, TypeError):
        return Response({'error': 'startRoom and endRoom must be integers'}, status=400)

    if end_room < start_room:
        return Response({'error': 'endRoom must be >= startRoom'}, status=400)

    if (end_room - start_room + 1) > 200:
        return Response({'error': 'Maximum 200 rooms per batch'}, status=400)

    hotel = Hotel.objects.first()
    if not hotel:
        return Response({'error': 'No hotel configured'}, status=500)

    room_type, _ = RoomType.objects.get_or_create(
        name=room_type_name,
        defaults={'base_price': Decimal(str(price)), 'capacity': 1, 'amenities': ''}
    )

    created = []
    skipped = []
    for num in range(start_room, end_room + 1):
        room_number = str(num)
        if Room.objects.filter(hotel=hotel, room_number=room_number).exists():
            skipped.append(room_number)
            continue
        room = Room.objects.create(
            hotel=hotel,
            room_number=room_number,
            room_type=room_type,
            floor=floor,
            status='Available',
            price_per_night=Decimal(str(price)),
            is_available=True,
        )
        created.append(room_number)

    return Response({
        'created': len(created),
        'skipped': len(skipped),
        'rooms': created,
        'skippedRooms': skipped,
        'message': f'{len(created)} room(s) created, {len(skipped)} skipped (already exist).'
    }, status=201)


@api_view(['POST'])
@manager_or_above
def add_room(request):
    data = request.data
    room_number = data.get('roomNumber')
    room_type_name = data.get('roomType')
    price = data.get('price')
    floor = int(data.get('floor') or 1)

    if not room_number or not room_type_name or not price:
        return Response({'error': 'Missing room information'}, status=400)

    hotel = Hotel.objects.first()
    if not hotel:
        return Response({'error': 'No hotel configured'}, status=500)

    room_type, _ = RoomType.objects.get_or_create(
        name=room_type_name,
        defaults={'base_price': Decimal(price), 'capacity': 1, 'amenities': ''}
    )

    if Room.objects.filter(hotel=hotel, room_number=room_number).exists():
        return Response({'error': 'Room number already exists'}, status=400)

    room = Room.objects.create(
        hotel=hotel, room_number=room_number, room_type=room_type,
        floor=floor, status='Available', price_per_night=Decimal(price), is_available=True
    )
    return Response({
        'id': room.id, 'room_number': room.room_number,
        'room_type': room_type.name, 'status': room.status,
        'price_per_night': float(room.price_per_night)
    }, status=201)

@api_view(['GET'])
@require_auth
def customers_data(request):
    search = request.query_params.get('search', '').strip()
    guests = Guest.objects.all()
    if search:
        guests = guests.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    customers = [{
        'id': g.id,
        'name': str(g),
        'email': g.email,
        'phone': g.phone,
        'country': g.country or 'N/A',
        'bookings': g.bookings.count(),
        'total_spent': float(g.bookings.filter(status='Checked Out').aggregate(total=Sum('total_price'))['total'] or 0)
    } for g in guests]
    avg_rating = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0
    active_bookings = Booking.objects.filter(status='Confirmed').count()
    total_revenue = Payment.objects.filter(status='Completed').aggregate(total=Sum('amount'))['total'] or 0
    return Response({
        'totalCustomers': Guest.objects.count(),
        'activeBookings': active_bookings,
        'totalRevenue': float(total_revenue),
        'avgRating': round(avg_rating, 1),
        'customers': customers
    })

@api_view(['GET'])
@require_auth
def payments_data(request):
    payments_qs = Payment.objects.select_related('booking', 'booking__guest').all().order_by('-created_at')
    total_all   = payments_qs.count()
    payments    = payments_qs[:50]   # show last 50, count separately
    payment_list = [{
        'id': p.id,
        'guestName': str(p.booking.guest),
        'bookingId': p.booking.booking_id,
        'amount': float(p.amount),
        'method': p.payment_method,
        'date': p.paid_at.strftime('%Y-%m-%d') if p.paid_at else p.created_at.strftime('%Y-%m-%d'),
        'status': p.status
    } for p in payments]
    total_revenue = Payment.objects.filter(status='Completed').aggregate(total=Sum('amount'))['total'] or 0
    return Response({
        'totalPayments': total_all,
        'completed': Payment.objects.filter(status='Completed').count(),
        'pending':   Payment.objects.filter(status='Pending').count(),
        'failed':    Payment.objects.filter(status='Failed').count(),
        'refunded':  Payment.objects.filter(status='Refunded').count(),
        'totalRevenue': float(total_revenue),
        'payments': payment_list
    })

@api_view(['GET', 'POST'])
@require_auth
def settings_data(request):
    if request.method == 'POST' and get_role(request.user) not in ('admin', 'manager'):
        return Response({'error': 'Permission denied'}, status=403)
    hotel = Hotel.objects.first()
    sys_settings = HotelSettings.get()  # singleton row, auto-created if missing

    if request.method == 'POST':
        data = request.data

        # --- Save hotel info ---
        if hotel:
            hotel.name    = data.get('hotelName',    hotel.name)
            hotel.email   = data.get('hotelEmail',   hotel.email)
            hotel.phone   = data.get('hotelPhone',   hotel.phone)
            hotel.address = data.get('hotelAddress', hotel.address)
            hotel.city    = data.get('hotelCity',    hotel.city)
            hotel.save()

        # --- Save system settings ---
        sys_settings.currency        = data.get('currency',        sys_settings.currency)
        sys_settings.payment_gateway = data.get('paymentGateway',  sys_settings.payment_gateway)
        sys_settings.tax_rate        = data.get('taxRate',         sys_settings.tax_rate)
        sys_settings.date_format     = data.get('dateFormat',      sys_settings.date_format)
        sys_settings.time_zone       = data.get('timeZone',        sys_settings.time_zone)
        sys_settings.language        = data.get('language',        sys_settings.language)
        sys_settings.check_in_time   = data.get('checkInTime',     sys_settings.check_in_time)
        sys_settings.check_out_time  = data.get('checkOutTime',    sys_settings.check_out_time)
        sys_settings.cleaning_time   = data.get('cleaningTime',    sys_settings.cleaning_time)
        sys_settings.payment_timeout = data.get('paymentTimeout',  sys_settings.payment_timeout)
        sys_settings.currency_code   = data.get('currencyCode',    sys_settings.currency_code)
        sys_settings.base_rate       = data.get('baseRate',        sys_settings.base_rate)
        sys_settings.save()

        return Response({'status': True, 'message': 'Settings saved'})

    # --- GET: return all settings ---
    return Response({
        'hotelName':      hotel.name    if hotel else 'Grand Hotel',
        'hotelEmail':     hotel.email   if hotel else 'info@grandhotel.com',
        'hotelPhone':     hotel.phone   if hotel else '1-800-HOTEL',
        'hotelAddress':   hotel.address if hotel else '123 Main Street',
        'hotelCity':      hotel.city    if hotel else 'New York',
        'currency':       sys_settings.currency,
        'paymentGateway': sys_settings.payment_gateway,
        'taxRate':        sys_settings.tax_rate,
        'dateFormat':     sys_settings.date_format,
        'timeZone':       sys_settings.time_zone,
        'language':       sys_settings.language,
        'checkInTime':    sys_settings.check_in_time,
        'checkOutTime':   sys_settings.check_out_time,
        'cleaningTime':   sys_settings.cleaning_time,
        'paymentTimeout': sys_settings.payment_timeout,
        'currencyCode':   sys_settings.currency_code,
        'baseRate':       sys_settings.base_rate,
    })

# ─── NEW CUSTOMER-BOOKING ANALYTICS ENDPOINTS ─────────────────
@api_view(['GET'])
@require_auth
def customer_booking_history(request, customer_id):
    """Get complete booking history for a customer"""
    try:
        guest = Guest.objects.get(id=customer_id)
        bookings = guest.bookings.select_related('room', 'payment').order_by('-created_at')
        
        booking_data = []
        for booking in bookings:
            data = {
                'booking_id':      booking.booking_id,
                'room_number':     booking.room.room_number,
                'room_type':       booking.room.room_type.name if booking.room.room_type else 'N/A',
                'check_in':        booking.check_in_date.strftime('%Y-%m-%d'),
                'check_in_time':   booking.check_in_time.strftime('%H:%M') if booking.check_in_time else None,
                'check_out':       booking.check_out_date.strftime('%Y-%m-%d'),
                'check_out_time':  booking.check_out_time.strftime('%H:%M') if booking.check_out_time else None,
                # Actual timestamps recorded when staff clicked Check In / Check Out
                'actual_check_in':  booking.actual_check_in.strftime('%Y-%m-%d %H:%M') if booking.actual_check_in else None,
                'actual_check_out': booking.actual_check_out.strftime('%Y-%m-%d %H:%M') if booking.actual_check_out else None,
                'nights':          booking.number_of_nights,
                'total_price':     float(booking.total_price),
                'status':          booking.status,
                'payment_status':  booking.payment.status if hasattr(booking, 'payment') else 'N/A',
                'created_at':      booking.created_at.strftime('%Y-%m-%d')
            }
            booking_data.append(data)
        
        # Calculate stats
        total_spent = guest.bookings.filter(status='Checked Out').aggregate(
            total=Sum('total_price')
        )['total'] or 0
        completed_bookings = guest.bookings.filter(status='Checked Out').count()
        
        return Response({
            'customer': {
                'id': guest.id,
                'name': f"{guest.first_name} {guest.last_name}",
                'email': guest.email,
                'phone': guest.phone,
                'country': guest.country,
                'total_bookings': guest.total_bookings
            },
            'statistics': {
                'completed_bookings': completed_bookings,
                'total_spent': float(total_spent),
                'avg_per_booking': float(total_spent / completed_bookings) if completed_bookings > 0 else 0,
                'loyalty_tier': 'Gold' if completed_bookings >= 5 else 'Silver' if completed_bookings >= 2 else 'Bronze'
            },
            'bookings': booking_data
        })
    except Guest.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=404)

@api_view(['GET'])
@require_auth
def customer_analytics(request):
    """Get overall customer analytics"""
    total_customers = Guest.objects.count()
    repeat_customers = Guest.objects.filter(total_bookings__gte=2).count()
    total_revenue = Payment.objects.filter(status='Completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Top customers by spending
    top_customers = Guest.objects.annotate(
        total_spent=Sum('bookings__total_price')
    ).order_by('-total_spent')[:5]
    
    top_customer_data = [{
        'id': c.id,
        'name': f"{c.first_name} {c.last_name}",
        'email': c.email,
        'bookings': c.total_bookings,
        'total_spent': float(c.total_spent or 0)
    } for c in top_customers]
    
    return Response({
        'total_customers': total_customers,
        'repeat_customers': repeat_customers,
        'repeat_customer_percentage': round((repeat_customers / total_customers * 100) if total_customers > 0 else 0, 1),
        'total_revenue': float(total_revenue),
        'avg_revenue_per_customer': float(total_revenue / total_customers) if total_customers > 0 else 0,
        'top_customers': top_customer_data
    })

@api_view(['POST'])
@require_auth
def create_guest_review(request, booking_id):
    """Create review after checkout"""
    try:
        booking = Booking.objects.get(id=booking_id, status='Checked Out')
        data = request.data
        
        review, created = Review.objects.update_or_create(
            booking=booking,
            defaults={
                'guest': booking.guest,
                'rating': data.get('rating', 5),
                'cleanliness': data.get('cleanliness', 5),
                'service': data.get('service', 5),
                'food': data.get('food', 5),
                'comment': data.get('comment', ''),
                'would_recommend': data.get('would_recommend', True)
            }
        )
        
        return Response({
            'status': 'Review created' if created else 'Review updated',
            'booking_id': booking.booking_id
        }, status=201 if created else 200)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found or not checked out'}, status=404)

@api_view(['GET'])
@require_auth
def room_occupancy_forecast(request):
    """Get room occupancy forecast for next 30 days"""
    from datetime import timedelta
    
    today = date.today()
    forecast_days = 30
    occupancy_data = []
    
    for i in range(forecast_days):
        current_date = today + timedelta(days=i)
        occupied = Booking.objects.filter(
            check_in_date__lte=current_date,
            check_out_date__gt=current_date,
            status__in=['Confirmed', 'Checked In']
        ).count()
        
        total_rooms = Room.objects.count()
        occupancy_rate = (occupied / total_rooms * 100) if total_rooms > 0 else 0
        
        occupancy_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'occupied_rooms': occupied,
            'available_rooms': total_rooms - occupied,
            'occupancy_rate': round(occupancy_rate, 1)
        })
    
    return Response({
        'forecast': occupancy_data,
        'average_occupancy': round(
            sum(d['occupancy_rate'] for d in occupancy_data) / len(occupancy_data), 1
        )
    })

# ─── HOUSEKEEPING / CLEANING API ─────────────────────────────

@api_view(['GET'])
@require_auth
def cleaning_list(request):
    """
    Return all cleaning tasks, optionally filtered by status.
    Query params: ?status=Pending | In Progress | Completed
    """
    status_filter = request.query_params.get('status', '')
    qs = RoomCleaning.objects.select_related('room', 'room__room_type', 'booking', 'booking__guest', 'assigned_to', 'assigned_to__user')
    if status_filter:
        qs = qs.filter(status=status_filter)

    data = []
    for c in qs:
        guest_name = ''
        if c.booking and c.booking.guest:
            guest_name = str(c.booking.guest)
        data.append({
            'id': c.id,
            'room_number': c.room.room_number,
            'room_type': c.room.room_type.name if c.room.room_type else 'N/A',
            'floor': c.room.floor,
            'status': c.status,
            'notes': c.notes or '',
            'guest_name': guest_name,
            'booking_id': c.booking.booking_id if c.booking else '',
            'assigned_to': c.assigned_to.user.get_full_name() if c.assigned_to else '',
            'started_at': c.started_at.strftime('%Y-%m-%d %H:%M') if c.started_at else None,
            'completed_at': c.completed_at.strftime('%Y-%m-%d %H:%M') if c.completed_at else None,
            'created_at': c.created_at.strftime('%Y-%m-%d %H:%M'),
        })

    # Summary counts
    all_qs = RoomCleaning.objects.all()
    return Response({
        'cleaning_tasks': data,
        'summary': {
            'pending': all_qs.filter(status='Pending').count(),
            'in_progress': all_qs.filter(status='In Progress').count(),
            'completed_today': all_qs.filter(
                status='Completed',
                completed_at__date=date.today()
            ).count(),
        }
    })


@api_view(['POST'])
@require_auth
def cleaning_update_status(request, cleaning_id):
    """
    Update a cleaning task status.
    Body: { "status": "In Progress" | "Completed", "notes": "..." }
    When Completed → room is set back to Available automatically.
    """
    try:
        task = RoomCleaning.objects.select_related('room').get(id=cleaning_id)
    except RoomCleaning.DoesNotExist:
        return Response({'error': 'Cleaning task not found'}, status=404)

    new_status = request.data.get('status')
    notes = request.data.get('notes', task.notes)

    if new_status not in ('In Progress', 'Completed'):
        return Response({'error': 'Status must be "In Progress" or "Completed"'}, status=400)

    task.notes = notes

    if new_status == 'In Progress':
        if task.status != 'Pending':
            return Response({'error': 'Task must be Pending to start'}, status=400)
        task.status = 'In Progress'
        task.started_at = timezone.now()

    elif new_status == 'Completed':
        if task.status not in ('Pending', 'In Progress'):
            return Response({'error': 'Task is already completed'}, status=400)
        task.status = 'Completed'
        task.completed_at = timezone.now()
        if not task.started_at:
            task.started_at = task.completed_at
        # Room is now clean — make it available again
        task.room.status = 'Available'
        task.room.is_available = True
        task.room.save()

    task.save()
    return Response({
        'status': 'ok',
        'cleaning_status': task.status,
        'room_status': task.room.status,
    })


# ─── COMPLAINTS API ──────────────────────────────────────────

@api_view(['GET'])
@require_auth
def complaints_data(request):
    qs = Complaint.objects.select_related('guest', 'booking').order_by('-created_at')
    status_filter = request.query_params.get('status', '')
    if status_filter:
        qs = qs.filter(status=status_filter)
    data = [{
        'id': c.id,
        'guest_name': str(c.guest),
        'guest_id': c.guest.id,
        'booking_id': c.booking.booking_id,
        'complaint_type': c.complaint_type,
        'description': c.description,
        'status': c.status,
        'resolution': c.resolution or '',
        'resolved_at': c.resolved_at.strftime('%Y-%m-%d %H:%M') if c.resolved_at else None,
        'created_at': c.created_at.strftime('%Y-%m-%d %H:%M'),
    } for c in qs]
    return Response({
        'total':       Complaint.objects.count(),
        'open':        Complaint.objects.filter(status='Open').count(),
        'in_progress': Complaint.objects.filter(status='In Progress').count(),
        'resolved':    Complaint.objects.filter(status='Resolved').count(),
        'closed':      Complaint.objects.filter(status='Closed').count(),
        'complaints':  data,
    })

@api_view(['POST'])
@require_auth
def create_complaint(request):
    data = request.data
    try:
        booking = Booking.objects.get(booking_id=data.get('booking_id'))
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=404)
    complaint = Complaint.objects.create(
        booking=booking,
        guest=booking.guest,
        complaint_type=data.get('complaint_type', 'Other'),
        description=data.get('description', ''),
        status='Open',
    )
    return Response({'id': complaint.id, 'status': 'Complaint created'}, status=201)

@api_view(['POST'])
@require_auth
def update_complaint(request, complaint_id):
    try:
        complaint = Complaint.objects.get(id=complaint_id)
    except Complaint.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)
    new_status   = request.data.get('status', complaint.status)
    resolution   = request.data.get('resolution', complaint.resolution)
    complaint.status     = new_status
    complaint.resolution = resolution
    if new_status in ('Resolved', 'Closed') and not complaint.resolved_at:
        complaint.resolved_at = timezone.now()
    complaint.save()
    return Response({'status': 'ok', 'complaint_status': complaint.status})


# ─── MAINTENANCE API ─────────────────────────────────────────

@api_view(['GET'])
@require_auth
def maintenance_data(request):
    qs = MaintenanceRequest.objects.select_related('room', 'assigned_to', 'assigned_to__user').order_by('-created_at')
    status_filter = request.query_params.get('status', '')
    priority_filter = request.query_params.get('priority', '')
    if status_filter:
        qs = qs.filter(status=status_filter)
    if priority_filter:
        qs = qs.filter(priority=priority_filter)
    data = [{
        'id': m.id,
        'room_number': m.room.room_number,
        'room_type':   m.room.room_type.name if m.room.room_type else 'N/A',
        'floor':       m.room.floor,
        'priority':    m.priority,
        'description': m.description,
        'status':      m.status,
        'assigned_to': m.assigned_to.user.get_full_name() if m.assigned_to else '',
        'assigned_to_id': m.assigned_to.id if m.assigned_to else None,
        'created_at':  m.created_at.strftime('%Y-%m-%d %H:%M'),
        'completed_at': m.completed_at.strftime('%Y-%m-%d %H:%M') if m.completed_at else None,
    } for m in qs]
    return Response({
        'total':       MaintenanceRequest.objects.count(),
        'open':        MaintenanceRequest.objects.filter(status='Open').count(),
        'in_progress': MaintenanceRequest.objects.filter(status='In Progress').count(),
        'completed':   MaintenanceRequest.objects.filter(status='Completed').count(),
        'urgent':      MaintenanceRequest.objects.filter(priority='Urgent', status__in=['Open','In Progress']).count(),
        'requests':    data,
    })

@api_view(['POST'])
@manager_or_above
def create_maintenance(request):
    data = request.data
    try:
        room = Room.objects.get(room_number=data.get('room_number'))
    except Room.DoesNotExist:
        return Response({'error': 'Room not found'}, status=404)
    req = MaintenanceRequest.objects.create(
        room=room,
        priority=data.get('priority', 'Medium'),
        description=data.get('description', ''),
        status='Open',
    )
    # Optionally mark room as Maintenance
    if data.get('mark_room', False):
        room.status = 'Maintenance'
        room.is_available = False
        room.save()
    return Response({'id': req.id, 'status': 'Request created'}, status=201)

@api_view(['POST'])
@manager_or_above
def update_maintenance(request, req_id):
    try:
        req = MaintenanceRequest.objects.select_related('room').get(id=req_id)
    except MaintenanceRequest.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)
    new_status = request.data.get('status', req.status)
    req.status = new_status
    if new_status == 'Completed':
        req.completed_at = timezone.now()
        req.room.status = 'Available'
        req.room.is_available = True
        req.room.save()
    req.save()
    return Response({'status': 'ok', 'request_status': req.status})


# ─── STAFF API ────────────────────────────────────────────────

@api_view(['GET'])
@require_auth
def staff_data(request):
    qs = Staff.objects.select_related('user').order_by('user__first_name')
    data = [{
        'id':          s.id,
        'name':        s.user.get_full_name() or s.user.username,
        'email':       s.user.email,
        'employee_id': s.employee_id,
        'position':    s.position,
        'department':  s.department or '',
        'shift':       s.shift,
        'phone':       s.phone,
        'hire_date':   s.hire_date.strftime('%Y-%m-%d'),
        'salary':      float(s.salary),
        'is_active':   s.is_active,
    } for s in qs]
    return Response({
        'total':    Staff.objects.count(),
        'active':   Staff.objects.filter(is_active=True).count(),
        'inactive': Staff.objects.filter(is_active=False).count(),
        'staff':    data,
    })


# ─── SERVICES API ─────────────────────────────────────────────

@api_view(['GET'])
@require_auth
def services_data(request):
    qs = Service.objects.all().order_by('service_type', 'name')
    data = [{
        'id':           s.id,
        'name':         s.name,
        'service_type': s.service_type,
        'description':  s.description,
        'price':        float(s.price),
        'is_available': s.is_available,
        'created_at':   s.created_at.strftime('%Y-%m-%d'),
    } for s in qs]
    return Response({
        'total':     Service.objects.count(),
        'available': Service.objects.filter(is_available=True).count(),
        'services':  data,
    })

@api_view(['POST'])
@manager_or_above
def create_service(request):
    d = request.data
    svc = Service.objects.create(
        name=d.get('name',''),
        service_type=d.get('service_type','Other'),
        description=d.get('description',''),
        price=Decimal(str(d.get('price', 0))),
        is_available=d.get('is_available', True),
    )
    return Response({'id': svc.id, 'status': 'Service created'}, status=201)

@api_view(['PATCH','POST'])
@manager_or_above
def update_service(request, service_id):
    try:
        svc = Service.objects.get(id=service_id)
    except Service.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)
    d = request.data
    svc.name         = d.get('name', svc.name)
    svc.service_type = d.get('service_type', svc.service_type)
    svc.description  = d.get('description', svc.description)
    svc.is_available = d.get('is_available', svc.is_available)
    if 'price' in d:
        svc.price = Decimal(str(d['price']))
    svc.save()
    return Response({'status': 'ok'})


# ─── REVIEWS API ──────────────────────────────────────────────

@api_view(['GET'])
@require_auth
def reviews_data(request):
    qs = Review.objects.select_related('guest', 'booking').order_by('-reviewed_at')
    data = [{
        'id':               r.id,
        'guest_name':       str(r.guest),
        'booking_id':       r.booking.booking_id,
        'rating':           r.rating,
        'cleanliness':      r.cleanliness,
        'service':          r.service,
        'food':             r.food,
        'comment':          r.comment,
        'would_recommend':  r.would_recommend,
        'reviewed_at':      r.reviewed_at.strftime('%Y-%m-%d %H:%M'),
    } for r in qs]
    avg = Review.objects.aggregate(
        avg_rating=Avg('rating'),
        avg_cleanliness=Avg('cleanliness'),
        avg_service=Avg('service'),
        avg_food=Avg('food'),
    )
    return Response({
        'total':   Review.objects.count(),
        'avg_rating':      round(avg['avg_rating'] or 0, 1),
        'avg_cleanliness': round(avg['avg_cleanliness'] or 0, 1),
        'avg_service':     round(avg['avg_service'] or 0, 1),
        'avg_food':        round(avg['avg_food'] or 0, 1),
        'recommend_pct':   round(Review.objects.filter(would_recommend=True).count() / max(Review.objects.count(),1) * 100, 1),
        'reviews':         data,
    })


# ─── ViewSets ─────────────────────────────────────────────────
class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        hotel = self.get_object()
        total_revenue = hotel.bookings.filter(
            payment__status='Completed'
        ).aggregate(total=Sum('total_price'))['total'] or 0
        return Response({
            'total_rooms': hotel.rooms.count(),
            'available_rooms': hotel.rooms.filter(status='Available').count(),
            'total_bookings': hotel.bookings.count(),
            'total_revenue': float(total_revenue)
        })

class RoomTypeViewSet(viewsets.ModelViewSet):
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeSerializer

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.select_related('hotel', 'room_type').all()

    def get_serializer_class(self):
        if self.action in ['list', 'available']:
            return RoomListSerializer
        return RoomDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search')
        ordering = self.request.query_params.get('ordering')
        if search:
            qs = qs.filter(room_number__icontains=search)
        if ordering:
            qs = qs.order_by(ordering)
        return qs

    @action(detail=False, methods=['get'])
    def available(self, request):
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')
        rooms = Room.objects.filter(is_available=True, status='Available')
        if check_in and check_out:
            booked = Booking.objects.filter(
                status__in=['Confirmed', 'Checked In', 'Pending'],
                check_in_date__lt=check_out, check_out_date__gt=check_in
            ).values_list('room_id', flat=True)
            rooms = rooms.exclude(id__in=booked)
        return Response(RoomListSerializer(rooms, many=True).data)

    @action(detail=True, methods=['post'])
    def mark_maintenance(self, request, pk=None):
        room = self.get_object()
        room.status = 'Maintenance'
        room.is_available = False
        room.save()
        return Response({'status': 'Room marked for maintenance'})

class GuestViewSet(viewsets.ModelViewSet):
    queryset = Guest.objects.all()

    def get_serializer_class(self):
        return GuestListSerializer if self.action == 'list' else GuestDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(first_name__icontains=search) | \
                 qs.filter(last_name__icontains=search) | \
                 qs.filter(email__icontains=search)
        return qs

    @action(detail=True, methods=['get'])
    def bookings(self, request, pk=None):
        return Response(BookingListSerializer(self.get_object().bookings.all(), many=True).data)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.select_related('guest', 'room', 'hotel').all()

    def get_serializer_class(self):
        if self.action == 'create': return BookingCreateSerializer
        if self.action == 'list': return BookingListSerializer
        return BookingDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search')
        status_filter = self.request.query_params.get('status')
        guest_id = self.request.query_params.get('guest')
        if search: qs = qs.filter(booking_id__icontains=search)
        if status_filter: qs = qs.filter(status=status_filter)
        if guest_id: qs = qs.filter(guest_id=guest_id)
        return qs

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        bookings = Booking.objects.filter(
            check_in_date__gte=date.today(), status__in=['Confirmed', 'Pending']
        ).order_by('check_in_date')
        return Response(BookingListSerializer(bookings, many=True).data)

    @action(detail=False, methods=['get'])
    def occupancy_stats(self, request):
        """Get occupancy analytics"""
        total_bookings = Booking.objects.count()
        occupied_rooms = Room.objects.filter(status='Occupied').count()
        available_rooms = Room.objects.filter(status='Available').count()
        reserved_rooms = Room.objects.filter(status='Reserved').count()
        maintenance_rooms = Room.objects.filter(status='Maintenance').count()
        
        total_revenue = Payment.objects.filter(status='Completed').aggregate(total=Sum('amount'))['total'] or 0
        
        return Response({
            'total_bookings': total_bookings,
            'rooms': {
                'occupied': occupied_rooms,
                'available': available_rooms,
                'reserved': reserved_rooms,
                'maintenance': maintenance_rooms,
                'total': occupied_rooms + available_rooms + reserved_rooms + maintenance_rooms
            },
            'revenue': float(total_revenue)
        })

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        booking = self.get_object()
        if booking.status != 'Pending':
            return Response({'error': 'Only pending bookings can be confirmed'}, status=400)
        
        # Check payment status
        if hasattr(booking, 'payment') and booking.payment.status == 'Failed':
            return Response({'error': 'Payment failed. Please process payment first.'}, status=400)
        
        booking.status = 'Confirmed'
        booking.save()
        return Response({'status': 'Booking confirmed', 'booking_id': booking.booking_id}, status=200)

    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        booking = self.get_object()
        if booking.status != 'Confirmed':
            return Response({'error': 'Booking must be confirmed before check-in'}, status=400)
        
        payment_ok = True
        if hasattr(booking, 'payment'):
            if booking.payment.status != 'Completed':
                payment_ok = False
        
        now = timezone.now()
        booking.status          = 'Checked In'
        booking.actual_check_in = now          # ← record real check-in time
        booking.room.status     = 'Occupied'
        booking.room.is_available = False
        booking.room.save()
        booking.save()
        
        return Response({
            'status': 'Guest checked in',
            'booking_id': booking.booking_id,
            'room': booking.room.room_number,
            'actual_check_in': now.strftime('%Y-%m-%d %H:%M'),
            'payment_warning': 'Payment not completed' if not payment_ok else None
        }, status=200)

    @action(detail=True, methods=['post'])
    def check_out(self, request, pk=None):
        booking = self.get_object()
        if booking.status != 'Checked In':
            return Response({'error': 'Guest must be checked in first'}, status=400)
        
        now = timezone.now()
        booking.status           = 'Checked Out'
        booking.actual_check_out = now           # ← record real check-out time
        booking.room.status      = 'Cleaning'
        booking.room.is_available = False
        booking.room.save()
        booking.save()
        
        RoomCleaning.objects.create(
            room=booking.room,
            booking=booking,
            status='Pending',
        )
        
        guest = booking.guest
        guest.total_bookings = guest.bookings.filter(status='Checked Out').count()
        guest.save()
        
        return Response({
            'status': 'Guest checked out — room queued for cleaning',
            'booking_id': booking.booking_id,
            'actual_check_out': now.strftime('%Y-%m-%d %H:%M'),
            'guest_total_bookings': guest.total_bookings
        }, status=200)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status in ['Checked Out', 'Cancelled']:
            return Response({'error': f'Cannot cancel {booking.status} booking'}, status=400)
        
        booking.status = 'Cancelled'
        booking.room.is_available = True
        if booking.room.status == 'Reserved':
            booking.room.status = 'Available'
        booking.room.save()
        booking.save()
        
        # Handle refund
        if hasattr(booking, 'payment'):
            payment = booking.payment
            if payment.status != 'Refunded':
                payment.status = 'Refunded'
                payment.save()
        
        return Response({
            'status': 'Booking cancelled',
            'booking_id': booking.booking_id,
            'refund_status': 'Refunded'
        }, status=200)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        if status_filter: qs = qs.filter(status=status_filter)
        return qs

    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        payment = self.get_object()
        method         = request.data.get('method', 'Cash')
        transaction_id = request.data.get('transaction_id', None)

        payment.status         = 'Completed'
        payment.payment_method = method
        payment.transaction_id = transaction_id
        payment.paid_at        = timezone.now()
        payment.save()

        # Only advance to Confirmed if booking is still Pending
        if payment.booking.status == 'Pending':
            payment.booking.status = 'Confirmed'
            payment.booking.save()

        return Response({
            'status':           'Payment processed',
            'booking_status':   payment.booking.status,
            'method':           method,
            'transaction_id':   transaction_id
        })

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.filter(is_available=True)
    serializer_class = ServiceSerializer

class BookingServiceViewSet(viewsets.ModelViewSet):
    queryset = BookingService.objects.all()
    serializer_class = BookingServiceSerializer

class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.select_related('user').all()

    def get_serializer_class(self):
        return StaffListSerializer if self.action == 'list' else StaffDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        position = self.request.query_params.get('position')
        if position: qs = qs.filter(position=position)
        return qs

    @action(detail=False, methods=['get'])
    def active(self, request):
        return Response(StaffListSerializer(Staff.objects.filter(is_active=True).select_related('user'), many=True).data)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    @action(detail=False, methods=['get'])
    def average_rating(self, request):
        avg = Review.objects.aggregate(
            avg_rating=Avg('rating'), avg_cleanliness=Avg('cleanliness'),
            avg_service=Avg('service'), avg_food=Avg('food')
        )
        return Response({k: round(v, 2) if v else 0 for k, v in avg.items()})

class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceRequest.objects.all()
    serializer_class = MaintenanceRequestSerializer

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        maintenance = self.get_object()
        try:
            staff = Staff.objects.get(id=request.data.get('staff_id'))
            maintenance.assigned_to = staff
            maintenance.status = 'In Progress'
            maintenance.save()
            return Response({'status': 'Maintenance assigned'})
        except Staff.DoesNotExist:
            return Response({'error': 'Staff not found'}, status=400)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        maintenance = self.get_object()
        maintenance.status = 'Completed'
        maintenance.completed_at = timezone.now()
        maintenance.save()
        maintenance.room.status = 'Available'
        maintenance.room.is_available = True
        maintenance.room.save()
        return Response({'status': 'Maintenance completed'})

class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        complaint = self.get_object()
        complaint.status = 'Resolved'
        complaint.resolution = request.data.get('resolution', '')
        complaint.resolved_at = timezone.now()
        complaint.save()
        return Response({'status': 'Complaint resolved'})
