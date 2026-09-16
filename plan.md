# Plan: Hotel Management System - Full Enhancement

## TL;DR
Transform the Django backend into a production-ready system with:
1. **Improved internal pages** (booking & customer management with modern UI)
2. **Customer portal** (login → view/manage bookings, make new bookings)
3. **Check-in time slots** (morning/afternoon/evening with customizable times)
4. **Email notifications** (confirmation, reminders, cancellations)
5. **Room management** (photo/gallery support, better availability display)
6. **Refund system** (cancellation with partial/full refunds)
7. **Enhanced REST API** (ready for external website integration)

Target: Single-hotel system, Django templates + API approach.

---

## Steps

### Phase 1: Data Model Enhancements
1. **Add CheckInTimeSlot model** to `resultapp/models.py`
   - Fields: name (Morning/Afternoon/Evening), start_time, end_time, description
   - Link to HotelSettings for hotel-specific slots
   - Create default slots via migration

2. **Extend Room model** with photo/gallery support
   - Add `featured_image` (ImageField) for main room photo
   - Create `RoomPhoto` model (room, image, caption, display_order)
   - Add `is_featured` flag for front-page display

3. **Extend Booking model** with time slot reference
   - Add `check_in_slot` (ForeignKey to CheckInTimeSlot, nullable)
   - Add `check_out_slot` (ForeignKey to CheckInTimeSlot, nullable)
   - Add `special_requests` (TextField)

4. **Create Refund model** for cancellation management
   - Fields: booking (OneToOne), refund_amount (Decimal), refund_method, status (Pending/Approved/Rejected/Processed), reason, processed_at
   - Link to Payment for audit trail

5. **Create EmailNotification model** for tracking sent emails
   - Fields: booking, notification_type (Confirmation/Reminder/Cancellation), sent_at, recipient, status
   - Prevents duplicate sends

6. **Extend Payment model** with refund fields
   - Add `refund_amount`, `refund_status`, `refunded_at`

7. **Create Customer User link**
   - Extend Guest model: add `user` (OneToOneField to User, nullable) for login capability
   - Create signal to auto-link User ↔ Guest on registration

### Phase 2: Backend Features
1. **Check-in Slot Time Management**
   - Add management command to seed default slots
   - Update HotelSettings API to include slots
   - Modify booking creation to accept slot selection
   - Add slot availability logic (max bookings per slot per day)

2. **Email System Setup**
   - Install `django-anymail` or use `smtplib` for email backend
   - Create `email_service.py` with functions:
     - `send_booking_confirmation(booking)`
     - `send_reminder(booking)` (48h before check-in)
     - `send_cancellation(booking, refund)`
   - Create email templates (HTML/text)
   - Add celery task (async) or background signals for sending

3. **Room Photo Management**
   - Update Room admin to support inline RoomPhoto creation
   - Create API endpoint `GET /api/rooms/<id>/photos/` for gallery
   - Add photo upload endpoint `POST /api/rooms/<id>/photos/`
   - Implement image resizing/optimization

4. **Refund Management System**
   - Create refund request endpoint `POST /api/bookings/<id>/request-refund/` with reason
   - Create refund approval endpoint (manager only) `POST /api/refunds/<id>/approve/`
   - Calculate refund amount: 100% if cancelled >7 days before, 50% if 1-7 days, 0% if <1 day
   - Update Payment and Booking status on refund approval

5. **Improve Booking Logic**
   - Add validation: check_in_slot + check_out_slot required
   - Add special_requests field to booking
   - Auto-calculate minimum stay requirements
   - Add group booking support (multiple rooms, same dates)

### Phase 3: Customer Portal Pages (New Templates)
1. **Customer Registration Page** (`templates/auth/register.html`)
   - Form: first_name, last_name, email, password, confirm_password, phone, address
   - Create User + Guest automatically
   - Redirect to login

2. **Customer Login Page** (already exists at `/accounts/login/`, improve UI)
   - Make it match booking page design
   - Add "forgot password" link
   - Remember me option

3. **Customer Dashboard** (`templates/customers/customer_dashboard.html`)
   - Header: Welcome message, customer info
   - Stat cards: Total Bookings, Active Bookings, Total Spent, Loyalty Tier
   - **My Bookings** section showing:
     - Booking cards (checkout-in date, room type, status, actions)
     - Status badges (Pending/Confirmed/Checked-In/Checked-Out/Cancelled)
     - Action buttons: View Details, Cancel, Write Review, Request Refund (if eligible)

4. **Booking Details Modal/Page** (`templates/customers/booking_detail.html`)
   - Full booking info: booking ID, room, dates, check-in slot
   - Guest info, special requests
   - Payment status & amount
   - Review form (if checked out)
   - Cancellation request form
   - Refund status display

5. **Make New Booking Page** (`templates/customers/make_booking.html`)
   - Similar to admin booking form but simplified for customer
   - Pre-filled with logged-in customer info
   - Hotel/room selection, date picker, check-in slot dropdown
   - Special requests textarea
   - Preview total cost before confirmation

6. **Refund Management Page** (`templates/customers/my_refunds.html`)
   - List all refund requests with status
   - Show refund amount, reason, date requested

### Phase 4: Improve Internal Management Pages

1. **Improve Booking Page** (`templates/booking/booking.html`)
   - Redesign with better layout:
     - Add check-in slot selection dropdown
     - Add special requests field
     - Add cancellation/refund request tracking column
     - Add filter by status, date range
     - Add export to CSV
   - Improve table responsiveness
   - Add bulk actions (confirm, cancel, mark checked-in)

2. **Improve Customers Page** (`templates/customers/customers.html`)
   - Add customer segmentation (by loyalty tier)
   - Add customer search with filters (by country, bookings, spend)
   - Add "View Customer Portal" button (preview their dashboard)
   - Add customer lifecycle stats (acquisition date, LTV, churn risk)
   - Improve customer detail modal:
     - Show booking history with status
     - Show total revenue from customer
     - Show refund requests
     - Add note-taking feature for staff

3. **New Rooms Management Page** (enhance existing `templates/rooms/rooms.html`)
   - Add photo gallery section per room
   - Add photo upload button
   - Add featured image selector
   - Add room availability calendar view
   - Add maintenance scheduling UI

4. **Payments Page Enhancement** (`templates/payments/payments.html`)
   - Add refund column showing pending/approved refunds
   - Add refund approval workflow
   - Add payment reconciliation report

### Phase 5: REST API Enhancements

1. **Expand Public APIs** (for external website to call)
   - `GET /api/hotels/` - Hotel info, check-in slots
   - `GET /api/rooms/?hotel_id=X&check_in=YYYY-MM-DD&check_out=YYYY-MM-DD&guests=N` - Room availability search
   - `GET /api/rooms/<id>/photos/` - Room gallery
   - `GET /api/room-types/` - Room type list
   - `POST /api/bookings/` - Create booking (requires guest email/phone or user auth)
   - `GET /api/bookings/<booking_id>/` - Booking details (public access with booking_id)
   - `POST /api/bookings/<booking_id>/review/` - Submit review
   - `POST /api/bookings/<booking_id>/request-refund/` - Request refund
   - `POST /api/auth/register/` - Customer registration
   - `POST /api/auth/login/` - Customer login (returns token)

2. **Add API Serializers for new fields**
   - BookingSerializer: include check_in_slot, check_out_slot, special_requests, status
   - RoomSerializer: include photos, featured_image
   - RefundSerializer: full refund details

3. **Add pagination/filtering**
   - Bookings: filter by status, date range, customer
   - Customers: search, filter by loyalty tier
   - Payments: filter by status, date range

### Phase 6: Email & Notifications

1. **Email Templates** (`templates/emails/`)
   - `booking_confirmation.html` - Booking details, QR code for check-in
   - `booking_reminder.html` - Reminder 48h before check-in
   - `cancellation_confirmation.html` - Cancellation + refund info
   - `refund_approved.html` - Refund processed notification

2. **Celery Tasks** (or use Django signals for sync)
   - Task: send_confirmation_email (on booking creation)
   - Task: send_reminder_emails (daily cron - check bookings for next 48h)
   - Task: send_cancellation_email (on cancellation)

---

## Relevant Files
- `resultapp/models.py` — Add CheckInTimeSlot, RoomPhoto, Refund models; extend Room, Booking, Payment, Guest
- `resultapp/views.py` — Add refund endpoints, improve booking creation, add email triggers
- `resultapp/serializers.py` — Add/update serializers for new models and fields
- `resultapp/admin.py` — Update admin UI for new models (inline photos, refund management)
- `resultapp/forms.py` — Add CheckInTimeSlot form, update BulkRoomForm
- `templates/booking/booking.html` — Redesign with slots, special requests, refund tracking
- `templates/customers/customers.html` — Add loyalty tier view, improve modal
- `templates/auth/register.html` — NEW - Customer registration
- `templates/customers/customer_dashboard.html` — NEW - Customer portal homepage
- `templates/customers/booking_detail.html` — NEW - Booking detail + cancellation/refund
- `templates/customers/make_booking.html` — NEW - Simplified booking form for customers
- `templates/rooms/rooms.html` — Add photo gallery management
- `templates/payments/payments.html` — Add refund workflow
- `HotelManagementSystem/settings.py` — Add email config, celery (optional)
- `resultapp/email_service.py` — NEW - Email sending functions
- `resultapp/management/commands/init_checkin_slots.py` — NEW - Seed default slots

---

## Verification
1. **Database migrations**: Run migrations for new models (CheckInTimeSlot, RoomPhoto, Refund, EmailNotification)
2. **API testing**: Use Postman/curl to test new endpoints:
   - Create booking with check-in slot
   - Request refund on booking
   - Upload room photos
   - Customer registration & login
3. **Email testing**: Verify booking confirmation email sent on booking creation
4. **UI testing**:
   - Admin can manage time slots in settings
   - Admin can approve/reject refunds
   - Customer can register, login, view bookings, request refund
   - Customer can see room photos on booking form
5. **Integration**: Verify external website can:
   - Fetch available rooms for date range
   - Create booking via API
   - Track booking status
   - Submit review

---

## Decisions
- **Single hotel system**: Simplified schema; if multi-hotel needed later, refactor Room/Booking filtering
- **Customer authentication**: Guest model linked to User for login (enable customer portal)
- **Check-in slots**: 3 default slots (Morning 8am-12pm, Afternoon 1pm-5pm, Evening 6pm-10pm) - configurable via HotelSettings
- **Refund policy**: 100% refund if cancelled 7+ days before, 50% if 1-7 days, 0% if <1 day (configurable per booking)
- **Email delivery**: Use async task queue (Celery) if available; otherwise use Django signals + threading (simpler)
- **Image storage**: Use Django's FileSystemStorage or S3 (if deployed to cloud)
- **REST API**: Session + JWT support (for external frontend)
- **UI framework**: Keep existing HTML/CSS with Bootstrap improvements (avoid heavy re-framework)

---

## Further Considerations
1. **Payment Gateway Integration**: Currently Payment model exists but no actual processing. Should we integrate Stripe, PayPal, or local Nepal payment gateways (eSewa, Khalti)?
2. **Multi-language Support**: Hotel in Nepal - should we add Nepali language translations?
3. **Seasonal Pricing**: Should we support dynamic pricing based on season/occupancy?
