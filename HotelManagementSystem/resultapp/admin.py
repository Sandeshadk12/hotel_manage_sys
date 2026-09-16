from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    Hotel, RoomType, Room, Guest, Booking, Payment,
    Staff, Service, BookingService, Review, MaintenanceRequest, Complaint,
    RoomCleaning, HotelSettings
)
from .forms import BulkRoomForm

# ─── Admin site branding ──────────────────────────────────────
admin.site.site_header  = "HotelMS Administration"
admin.site.site_title   = "HotelMS Admin"
admin.site.index_title  = "Hotel Management — Control Panel"


# ─── Hotel ────────────────────────────────────────────────────
@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display  = ['name', 'city', 'state', 'phone', 'email', 'total_rooms', 'created_at']
    search_fields = ['name', 'city', 'email']
    list_filter   = ['city', 'state']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {'fields': ('name', 'email', 'phone', 'website')}),
        ('Location',          {'fields': ('address', 'city', 'state', 'postal_code')}),
        ('Stats',             {'fields': ('total_rooms',)}),
        ('Timestamps',        {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


# ─── Room Type ────────────────────────────────────────────────
@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display  = ['name', 'base_price', 'capacity', 'amenities']
    search_fields = ['name']


# ─── Room ─────────────────────────────────────────────────────
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display       = ['room_number', 'hotel', 'room_type', 'floor', 'status_badge', 'price_per_night', 'is_available']
    list_filter        = ['status', 'is_available', 'hotel', 'room_type', 'floor']
    search_fields      = ['room_number']
    list_editable      = ['is_available']
    readonly_fields    = ['created_at', 'updated_at']
    change_list_template = 'admin/resultapp/room/change_list.html'

    def status_badge(self, obj):
        colors = {
            'Available':   '#10b981',
            'Occupied':    '#ef4444',
            'Cleaning':    '#f59e0b',
            'Maintenance': '#fb923c',
            'Reserved':    '#a78bfa',
        }
        color = colors.get(obj.status, '#94a3b8')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            color, obj.status
        )
    status_badge.short_description = 'Status'

    def get_urls(self):
        custom = [
            path('bulk-add/', self.admin_site.admin_view(self.bulk_add_view),
                 name='resultapp_room_bulk_add'),
        ]
        return custom + super().get_urls()

    def bulk_add_view(self, request):
        if request.method == 'POST':
            form = BulkRoomForm(request.POST)
            if form.is_valid():
                hotel      = form.cleaned_data['hotel']
                start_room = form.cleaned_data['start_room']
                end_room   = form.cleaned_data['end_room']
                room_type  = form.cleaned_data['room_type']
                floor      = form.cleaned_data['floor']
                price      = form.cleaned_data['price_per_night']
                if end_room < start_room:
                    form.add_error('end_room', 'End room must be >= start room.')
                elif (end_room - start_room + 1) > 200:
                    form.add_error('end_room', 'Maximum 200 rooms per batch.')
                else:
                    created = skipped = 0
                    for num in range(start_room, end_room + 1):
                        _, was_created = Room.objects.get_or_create(
                            hotel=hotel, room_number=str(num),
                            defaults={'room_type': room_type, 'floor': floor,
                                      'price_per_night': price, 'status': 'Available', 'is_available': True}
                        )
                        if was_created: created += 1
                        else: skipped += 1
                    if created: messages.success(request, f'{created} room(s) created.')
                    if skipped: messages.warning(request, f'{skipped} skipped (already exist).')
                    return redirect('../')
        else:
            form = BulkRoomForm()
        return render(request, 'admin/resultapp/bulk_add_rooms.html', {
            **self.admin_site.each_context(request),
            'form': form, 'title': 'Bulk Add Rooms', 'opts': self.model._meta,
        })


# ─── Guest ────────────────────────────────────────────────────
@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display   = ['full_name', 'email', 'phone', 'country', 'total_bookings', 'created_at']
    search_fields  = ['first_name', 'last_name', 'email', 'phone', 'id_number']
    list_filter    = ['country', 'gender']
    readonly_fields= ['total_bookings', 'created_at', 'updated_at']
    fieldsets = (
        ('Personal Information', {'fields': ('first_name', 'last_name', 'gender', 'date_of_birth')}),
        ('Contact',              {'fields': ('email', 'phone', 'address', 'city', 'country', 'postal_code')}),
        ('Identity Document',    {'fields': ('id_type', 'id_number')}),
        ('Stats',                {'fields': ('total_bookings',)}),
        ('Timestamps',           {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Guest Name'


# ─── Booking ──────────────────────────────────────────────────
class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['amount', 'payment_method', 'status', 'transaction_id', 'paid_at']
    can_delete = False
    show_change_link = True

class ComplaintInline(admin.TabularInline):
    model = Complaint
    extra = 0
    readonly_fields = ['guest', 'complaint_type', 'status', 'created_at']
    can_delete = False
    show_change_link = True


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display    = ['booking_id', 'guest', 'room', 'check_in_date', 'check_out_date',
                       'nights', 'status_badge', 'total_price', 'actual_check_in', 'actual_check_out']
    list_filter     = ['status', 'hotel', 'check_in_date', 'check_out_date']
    search_fields   = ['booking_id', 'guest__first_name', 'guest__last_name', 'room__room_number']
    readonly_fields = ['booking_id', 'number_of_nights', 'total_price', 'actual_check_in', 'actual_check_out', 'created_at', 'updated_at']
    date_hierarchy  = 'check_in_date'
    inlines         = [PaymentInline, ComplaintInline]
    fieldsets = (
        ('Booking Reference',  {'fields': ('booking_id', 'hotel', 'status')}),
        ('Guest & Room',       {'fields': ('guest', 'room', 'number_of_guests')}),
        ('Planned Dates',      {'fields': ('check_in_date', 'check_in_time', 'check_out_date', 'check_out_time')}),
        ('Actual Times',       {'fields': ('actual_check_in', 'actual_check_out')}),
        ('Financials',         {'fields': ('number_of_nights', 'total_price')}),
        ('Notes',              {'fields': ('notes',)}),
        ('Timestamps',         {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def status_badge(self, obj):
        colors = {
            'Pending':     '#fb923c',
            'Confirmed':   '#10b981',
            'Checked In':  '#60a5fa',
            'Checked Out': '#a78bfa',
            'Cancelled':   '#ef4444',
        }
        color = colors.get(obj.status, '#94a3b8')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            color, obj.status
        )
    status_badge.short_description = 'Status'

    def nights(self, obj):
        return f"{obj.number_of_nights}n"
    nights.short_description = 'Nights'


# ─── Payment ──────────────────────────────────────────────────
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display   = ['booking', 'guest_name', 'amount', 'payment_method', 'status_badge', 'transaction_id', 'paid_at']
    list_filter    = ['status', 'payment_method']
    search_fields  = ['booking__booking_id', 'transaction_id', 'booking__guest__first_name']
    readonly_fields= ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

    def guest_name(self, obj):
        return str(obj.booking.guest)
    guest_name.short_description = 'Guest'

    def status_badge(self, obj):
        colors = {'Pending': '#fb923c', 'Completed': '#10b981', 'Failed': '#ef4444', 'Refunded': '#a78bfa'}
        color = colors.get(obj.status, '#94a3b8')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            color, obj.status
        )
    status_badge.short_description = 'Status'


# ─── Staff ────────────────────────────────────────────────────
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display   = ['employee_id', 'full_name', 'position', 'department', 'shift', 'phone', 'hire_date', 'is_active']
    list_filter    = ['position', 'shift', 'is_active', 'department']
    search_fields  = ['employee_id', 'user__first_name', 'user__last_name', 'user__email']
    list_editable  = ['is_active']
    readonly_fields= ['created_at', 'updated_at']
    fieldsets = (
        ('User Account',    {'fields': ('user',)}),
        ('Employment',      {'fields': ('employee_id', 'position', 'department', 'shift', 'hire_date', 'salary', 'is_active')}),
        ('Contact',         {'fields': ('phone',)}),
        ('Timestamps',      {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    full_name.short_description = 'Name'


# ─── Service ──────────────────────────────────────────────────
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display  = ['name', 'service_type', 'price', 'is_available', 'created_at']
    list_filter   = ['service_type', 'is_available']
    search_fields = ['name']
    list_editable = ['is_available']


# ─── Booking Service ──────────────────────────────────────────
@admin.register(BookingService)
class BookingServiceAdmin(admin.ModelAdmin):
    list_display  = ['booking', 'service', 'quantity', 'price', 'added_on']
    search_fields = ['booking__booking_id', 'service__name']
    list_filter   = ['service']


# ─── Review ───────────────────────────────────────────────────
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display   = ['guest', 'booking', 'rating_stars', 'cleanliness', 'service', 'food', 'would_recommend', 'reviewed_at']
    list_filter    = ['rating', 'would_recommend']
    search_fields  = ['guest__first_name', 'guest__last_name', 'comment']
    readonly_fields= ['reviewed_at']

    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color:#f59e0b;font-size:14px;">{}</span>', stars)
    rating_stars.short_description = 'Rating'


# ─── Maintenance ──────────────────────────────────────────────
@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display   = ['room', 'priority_badge', 'status_badge', 'assigned_to', 'created_at', 'completed_at']
    list_filter    = ['priority', 'status']
    search_fields  = ['room__room_number', 'description']
    list_editable  = []
    readonly_fields= ['created_at', 'completed_at']
    date_hierarchy = 'created_at'

    def priority_badge(self, obj):
        colors = {'Low': '#10b981', 'Medium': '#f59e0b', 'High': '#fb923c', 'Urgent': '#ef4444'}
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            colors.get(obj.priority, '#94a3b8'), obj.priority
        )
    priority_badge.short_description = 'Priority'

    def status_badge(self, obj):
        colors = {'Open': '#fb923c', 'In Progress': '#60a5fa', 'Completed': '#10b981', 'Cancelled': '#94a3b8'}
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            colors.get(obj.status, '#94a3b8'), obj.status
        )
    status_badge.short_description = 'Status'


# ─── Complaint ────────────────────────────────────────────────
@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display   = ['guest', 'booking', 'complaint_type', 'status_badge', 'created_at', 'resolved_at']
    list_filter    = ['complaint_type', 'status']
    search_fields  = ['guest__first_name', 'guest__last_name', 'description']
    readonly_fields= ['created_at', 'resolved_at']
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Complaint',   {'fields': ('booking', 'guest', 'complaint_type', 'description')}),
        ('Resolution',  {'fields': ('status', 'resolution', 'resolved_at')}),
        ('Timestamps',  {'fields': ('created_at',), 'classes': ('collapse',)}),
    )

    def status_badge(self, obj):
        colors = {'Open': '#fb923c', 'In Progress': '#60a5fa', 'Resolved': '#10b981', 'Closed': '#94a3b8'}
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            colors.get(obj.status, '#94a3b8'), obj.status
        )
    status_badge.short_description = 'Status'


# ─── Room Cleaning ────────────────────────────────────────────
@admin.register(RoomCleaning)
class RoomCleaningAdmin(admin.ModelAdmin):
    list_display   = ['room', 'status_badge', 'booking', 'assigned_to', 'created_at', 'started_at', 'completed_at']
    list_filter    = ['status']
    search_fields  = ['room__room_number']
    readonly_fields= ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

    def status_badge(self, obj):
        colors = {'Pending': '#fb923c', 'In Progress': '#60a5fa', 'Completed': '#10b981'}
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            colors.get(obj.status, '#94a3b8'), obj.status
        )
    status_badge.short_description = 'Status'


# ─── Hotel Settings ───────────────────────────────────────────
@admin.register(HotelSettings)
class HotelSettingsAdmin(admin.ModelAdmin):
    list_display = ['currency', 'check_in_time', 'check_out_time', 'tax_rate', 'payment_gateway', 'updated_at']
    readonly_fields = ['updated_at']
    fieldsets = (
        ('Currency & Payment',    {'fields': ('currency', 'currency_code', 'payment_gateway', 'tax_rate', 'base_rate')}),
        ('Check-in / Check-out',  {'fields': ('check_in_time', 'check_out_time', 'cleaning_time', 'payment_timeout')}),
        ('Regional Settings',     {'fields': ('date_format', 'time_zone', 'language')}),
        ('Timestamps',            {'fields': ('updated_at',), 'classes': ('collapse',)}),
    )

    def has_add_permission(self, request):
        return not HotelSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
