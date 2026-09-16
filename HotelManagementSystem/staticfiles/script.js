/**
 * â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
 * HOTEL MANAGEMENT SYSTEM - MAIN JAVASCRIPT FILE
 * 
 * This file contains all frontend JavaScript for the hotel system:
 * - Dashboard, Bookings, Rooms, Customers, Payments management
 * - Authentication and user interface controls
 * - API communication with Django backend
 * - Modal dialogs and form handling
 * - Payment processing and receipts
 * 
 * For beginners: This is the "brain" of the web interface.
 * It talks to the backend API and updates the website based on user actions.
 * â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
 */

// Global currency settings - used to format all prices displayed on screen
let appCurrency = 'USD';
let appCurrencySymbol = '$';

/**
 * Update Global Currency Settings
 * 
 * This function extracts currency info from API settings and stores it globally.
 * It's called whenever settings are loaded so all prices display with correct symbol.
 * 
 * Example currency format: "USD ($)" â†’ extracts "USD" and "$"
 * 
 * @param {Object} data - Settings object from API (contains currency field)
 */
function applyCurrencyFromSettings(data) {
    if (data && data.currency) {
        // Extract currency code and symbol from format "CODE (SYMBOL)"
        // Example: "USD ($)" matches and extracts "USD" and "$"
        const match = data.currency.match(/^(\w+)\s*\((.+)\)$/);
        if (match) {
            appCurrency       = match[1];   // e.g. "USD"
            appCurrencySymbol = match[2];   // e.g. "$"
        }
    }
}


/**
 * Load Currency Settings from Backend
 * 
 * Fetches currency settings from API once and applies them globally.
 * This is run on all pages except login so prices always display correctly.
 * 
 * Why? We need to know the currency symbol before loading data,
 * otherwise prices might show "$" when currency is EUR or Â£.
 */
function loadCurrencyGlobal() {
    // Skip on login/accounts pages â€” user is not authenticated yet
    if (window.location.pathname.includes('/accounts/')) return;
    
    // Fetch settings from backend
    fetch('/api/settings/', { headers: getAuthHeaders(false) })
        .then(r => r.json())
        .then(data => applyCurrencyFromSettings(data))
        .catch(() => {});  // Silently fail - use default currency
}

/* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
 * UTILITY FUNCTIONS - Common helpers used throughout the app
 * â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */

/**
 * Toggle User Profile Popup Menu
 * Shows/hides the dropdown menu when you click your username
 */
function toggle(){
    document.getElementById("userPopup").classList.toggle("active");
}

/**
 * Toggle Sidebar (Mobile Menu)
 * Opens/closes the side navigation on mobile devices
 */
function toggleSidebar(){
    document.getElementById("sidebar").classList.toggle("active");
    document.getElementById("overlay").classList.toggle("show");
    document.getElementById("mainContent").classList.toggle("shift");
}

/**
 * Create Toast Container (One Time)
 * Creates a container at the top of the page where notifications appear
 * Toast messages are those little notifications that pop up (success, error, etc)
 */
function createToastContainer() {
    if (document.getElementById('toastContainer')) return;  // Already exists
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
}

/**
 * Show Notification Toast (Success, Error, Info)
 * 
 * Displays a temporary popup notification at the top of the page.
 * It automatically disappears after a few seconds.
 * 
 * Examples:
 * - showToast('Booking created!', 'success')
 * - showToast('Failed to load data', 'error')
 * - showToast('Processing...', 'info')
 * 
 * @param {string} message - Text to show in notification
 * @param {string} type - 'success', 'error', 'info', 'warning'
 * @param {number} duration - How long to show (milliseconds, default 3500)
 */
function showToast(message, type = 'info', duration = 3500) {
    createToastContainer();
    
    // Create the toast element
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;  // CSS styles based on type
    toast.textContent = message;
    document.getElementById('toastContainer').appendChild(toast);
    
    // Animate in
    requestAnimationFrame(() => toast.classList.add('visible'));
    
    // Auto-remove after duration
    setTimeout(() => {
        toast.classList.remove('visible');
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 350);
    }, duration);
}

/**
 * Get Cookie Value by Name
 * 
 * Reads a cookie from the browser's storage.
 * Mostly used to get the CSRF security token.
 * 
 * @param {string} name - Cookie name to find
 * @returns {string|null} Cookie value or null if not found
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        document.cookie.split(';').forEach(cookie => {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            }
        });
    }
    return cookieValue;
}

/**
 * Get HTTP Headers for API Requests
 * 
 * Returns headers needed for secure API communication:
 * - CSRF token (security)
 * - Content-Type (what format we're sending)
 * 
 * @param {boolean} hasJson - Include JSON content-type header?
 * @returns {Object} Headers object for fetch requests
 */
function getAuthHeaders(hasJson = true) {
    const headers = { 'X-CSRFToken': getCookie('csrftoken') };
    if (hasJson) headers['Content-Type'] = 'application/json';
    return headers;
}

/**
 * Format Number as Currency
 * 
 * Takes a number and formats it with currency symbol.
 * Uses the global appCurrency and appCurrencySymbol set from settings.
 * 
 * Examples:
 * - 99.5 â†’ "$ 99.50"
 * - 1500 â†’ "$ 1,500.00"
 * 
 * @param {number|string} value - Amount to format
 * @returns {string} Formatted currency string
 */
function formatCurrency(value) {
    // Convert to number if it's a string
    const amount = typeof value === 'number'
        ? value
        : parseFloat(value) || 0;

    // Format: symbol + space + number with commas and 2 decimals
    return `${appCurrencySymbol} ${amount.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })}`;
}

/**
 * Format Date for Display
 * 
 * Takes a date string and formats it nicely.
 * Input: "2025-05-15" â†’ Output: "May 15, 2025"
 * 
 * @param {string|Date} value - Date to format
 * @returns {string} Formatted date like "May 15, 2025" or "-" if invalid
 */
function formatDate(value) {
    if (!value) return '-';
    
    const date = new Date(value);
    if (isNaN(date)) return value;  // Invalid date, return original
    
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
}



/**
 * Guest Email Lookup - Auto-fill Guest Form
 * 
 * When a staff member enters a guest's email, this function:
 * 1. Searches for existing guest records in database
 * 2. If found, pre-fills name and phone fields
 * 3. Shows a message confirming guest was found
 * 
 * This saves time when creating bookings for returning customers.
 */
function lookupGuestByEmail() {
    const emailInput = document.getElementById('guestEmail');
    const statusEl = document.getElementById('guestLookupStatus');
    const email = emailInput?.value?.trim();
    
    if (!email) {
        if (statusEl) statusEl.textContent = '';
        return;
    }

    // Search backend for guest with this email
    fetch(`/api/guests/?search=${encodeURIComponent(email)}`, { headers: getAuthHeaders(false) })
        .then(response => response.json())
        .then(data => {
            const guests = Array.isArray(data) ? data : data.results || [];
            
            if (!guests.length) {
                if (statusEl) statusEl.textContent = 'No existing customer found';
                return;
            }

            // Find exact match or use first result
            const exact = guests.find(g => g.email?.toLowerCase() === email.toLowerCase());
            const guest = exact || guests[0];
            
            if (guest) {
                // Auto-fill the form with found guest info
                const guestName = guest.name || `${guest.first_name || ''} ${guest.last_name || ''}`.trim();
                document.getElementById('guestName').value = guestName;
                document.getElementById('guestPhone').value = guest.phone || '';
                if (statusEl) statusEl.textContent = 'Existing customer found and prefilled';
            }
        })
        .catch(error => {
            console.error('Guest lookup error:', error);
            if (statusEl) statusEl.textContent = 'Unable to lookup customer';
        });
}

/**
 * Highlight Active Sidebar Menu Item
 * 
 * When a page loads, this function marks the current page's menu item as "active"
 * so users know which page they're on.
 * 
 * Example: On /booking/ page, the "Booking" sidebar button gets highlighted.
 */
function highlightActiveSidebar() {
    const currentPage = window.location.pathname;
    document.querySelectorAll('.sidebar a').forEach(link => {
        link.classList.toggle('active', link.getAttribute('href') === currentPage);
    });
}

/* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
 * AUTHENTICATION FUNCTIONS - Login, Logout, Password Toggle
 * â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */

/**
 * Redirect User to Different Page
 * 
 * Only allows redirecting to approved pages for security.
 * Prevents accidental/malicious redirects to random pages.
 * 
 * @param {string} page - Page name like "booking", "rooms", "customers"
 */
function redirectTo(page){
    const validPages = ["booking", "rooms", "customers", "payments", "settings"];
    if(!validPages.includes(page)){
        alert("Invalid page");
        return;
    }
    window.location.href = "/" + page + "/";
}

/**
 * Logout User
 * 
 * Sends user to logout page which clears their session.
 * After logout, they'll be redirected to login page.
 */
function logout(){
    window.location.href = "/accounts/logout/";
}

/**
 * Toggle Password Visibility in Login Form
 * 
 * Switches between showing/hiding password as user types.
 * Click the eye icon to toggle between "password" and "text" input types.
 */
function togglePassword(){
    const passwordInput = document.getElementById("password");
    const icon = document.querySelector(".toggle-password i");
    
    if(passwordInput.type === "password"){
        passwordInput.type = "text";  // Show password
        icon.className = "bx bx-hide";
    } else {
        passwordInput.type = "password";  // Hide password
        icon.className = "bx bx-show";
    }
}



/* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
 * DASHBOARD FUNCTIONS - Display summary statistics and recent bookings
 * â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */

/**
 * Load and Display Dashboard
 * 
 * Fetches overview data from backend:
 * - Total rooms, bookings, guests
 * - Total revenue (completed payments)
 * - Room availability status (Available vs Occupied)
 * - Recent bookings list
 * 
 * Updates all dashboard cards and charts.
 */
function loadDashboard() {
    loadCurrencyGlobal();

    fetch('/api/dashboard/', { headers: getAuthHeaders(false) })
        .then(response => response.json())
        .then(data => {
            const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };

            set('totalRoomsCount',    data.totalRooms);
            set('totalBookingsCount', data.totalBookings);
            set('totalGuestsCount',   data.totalGuests);
            set('totalRevenueCount',  formatCurrency(data.totalRevenue));
            set('arrivalsToday',      data.arrivalsToday   || 0);
            set('departuresToday',    data.departuresToday  || 0);
            set('occupancyRate',      (data.occupancyRate  || 0) + '%');

            populateBookingsTable(data.bookings);

            const rs          = data.roomStatus || {};
            const available   = rs.available    || 0;
            const occupied    = rs.occupied     || 0;
            const cleaning    = rs.cleaning     || 0;
            const maintenance = rs.maintenance  || 0;
            const totalRooms  = data.totalRooms || 1;

            set('availableRoomsCount',   available);
            set('occupiedRoomsCount',    occupied);
            set('cleaningRoomsCount',    cleaning);
            set('cleaningRoomsBarCount', cleaning);
            set('maintenanceRoomsCount', maintenance);

            const bar = (id, v) => { const el = document.getElementById(id); if (el) el.style.width = ((v/totalRooms)*100).toFixed(1)+'%'; };
            bar('availableRoomsBar',   available);
            bar('occupiedRoomsBar',    occupied);
            bar('cleaningRoomsBar',    cleaning);
            bar('maintenanceRoomsBar', maintenance);

            const rateEl   = document.getElementById('occupancyRateBar');
            const rateFill = document.getElementById('occupancyBarFill');
            if (rateEl)   rateEl.textContent   = (data.occupancyRate || 0) + '%';
            if (rateFill) rateFill.style.width  = (data.occupancyRate || 0) + '%';

            // Smart notifications
            const notifEl = document.getElementById('dashboardNotifications');
            if (notifEl) {
                const msgs = [];
                if (data.arrivalsToday   > 0) msgs.push("Arrivals today: " + data.arrivalsToday);
                if (data.departuresToday > 0) msgs.push("Departures today: " + data.departuresToday);
                if (data.pendingPayments > 0) msgs.push("Payments pending: " + data.pendingPayments);
                if (data.openComplaints  > 0) msgs.push("Open complaints: " + data.openComplaints);
                if (cleaning > 0)              msgs.push("Rooms need cleaning: " + cleaning);
                if (maintenance > 0)           msgs.push("Under maintenance: " + maintenance);
                if (msgs.length === 0)         msgs.push("Everything looks good");
                notifEl.innerHTML = msgs.map(m => `<p>${m}</p>`).join('');
            }
        })
        .catch(err => {
            console.error('Dashboard load error:', err);
            showToast('Failed to load dashboard data', 'error');
        });
}

/**
 * Display Recent Bookings in Dashboard Table
 * 
 * Creates table rows showing recent bookings with guest name, room, check-in date, status.
 * 
 * @param {Array} bookings - Array of booking objects from API
 */
function populateBookingsTable(bookings) {
    const table = document.getElementById("bookingsTable");
    if (!table) return;
    
    let html = "<tr><th>Guest Name</th><th>Room</th><th>Check-in</th><th>Status</th></tr>";
    
    bookings.forEach(booking => {
        html += `<tr>
            <td>${booking.guest_name || booking.guestName || ''}</td>
            <td>${booking.room_number || booking.roomNumber || ''}</td>
            <td>${formatDate(booking.check_in_date || booking.checkIn)}</td>
            <td class="${(booking.status || '').toLowerCase()}">${booking.status || 'Pending'}</td>
        </tr>`;
    });
    
    table.innerHTML = html;
}

/* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
 * BOOKINGS FUNCTIONS - Create, view, manage room reservations
 * â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */

/**
 * Create New Booking
 * 
 * Takes form data from "New Booking" form and sends to backend to create a reservation.
 * 
 * Validations:
 * - All required fields (name, email, check-in, check-out) must be filled
 * - Check-out date must be after check-in date
 * 
 * @param {Event} event - Form submission event (for preventing default behavior)
 */

/**
 * Update price preview when room and dates are both selected
 */
function updatePricePreview() {
    const roomSelect = document.getElementById('roomNumber');
    const checkIn    = document.getElementById('checkIn')?.value;
    const checkOut   = document.getElementById('checkOut')?.value;
    const previewCard= document.getElementById('pricePreviewCard');
    const previewEl  = document.getElementById('pricePreview');
    if (!roomSelect || !checkIn || !checkOut || !previewCard || !previewEl) return;

    const selectedOpt = roomSelect.options[roomSelect.selectedIndex];
    if (!selectedOpt || !selectedOpt.value) { previewCard.style.display = 'none'; return; }

    const d1 = new Date(checkIn), d2 = new Date(checkOut);
    const nights = Math.round((d2 - d1) / (1000*60*60*24));
    if (nights <= 0) { previewCard.style.display = 'none'; return; }

    // Look up price from cached rooms
    fetch('/api/rooms/', { headers: getAuthHeaders(false) })
    .then(r => r.json())
    .then(rooms => {
        const room = rooms.find(r => r.room_number === selectedOpt.value);
        if (!room) { previewCard.style.display = 'none'; return; }
        const total = (parseFloat(room.price_per_night) || 0) * nights;
        previewEl.textContent = `${formatCurrency(total)} — ${nights} night${nights>1?'s':''}`;
        previewCard.style.display = '';
    })
    .catch(() => { previewCard.style.display = 'none'; });
}

function createBooking(event) {
    if (event) event.preventDefault();

    const bookingData = {
        guestName:    document.getElementById("guestName")?.value,
        guestEmail:   document.getElementById("guestEmail")?.value,
        guestPhone:   document.getElementById("guestPhone")?.value,
        roomType:     document.getElementById("roomType")?.value,
        roomNumber:   document.getElementById("roomNumber")?.value,
        guests:       parseInt(document.getElementById("guests")?.value) || 1,
        checkIn:      document.getElementById("checkIn")?.value,
        checkOut:     document.getElementById("checkOut")?.value,
        checkInTime:  document.getElementById("checkInTime")?.value || null,
        checkOutTime: document.getElementById("checkOutTime")?.value || null,
        notes:        document.getElementById("bookingNotes")?.value || '',
    };

    if (!bookingData.guestName || !bookingData.guestEmail || !bookingData.checkIn || !bookingData.checkOut) {
        showToast("Please fill all required fields", 'error');
        return;
    }
    if (new Date(bookingData.checkOut) <= new Date(bookingData.checkIn)) {
        showToast("Check-out date must be after check-in date", 'error');
        return;
    }

    fetch('/api/bookings/add/', {
        method: 'POST',
        headers: getAuthHeaders(true),
        body: JSON.stringify(bookingData)
    })
    .then(response => response.json().then(body => ({ status: response.status, body })))
    .then(({ status, body }) => {
        if (status >= 200 && status < 300) {
            showToast("âœ… Booking created successfully!", 'success');
            if (event?.target) event.target.reset();
            loadBookings();
        } else {
            showToast(body.error || "Failed to create booking", 'error');
        }
    })
    .catch(error => {
        console.error('Create booking error:', error);
        showToast("Failed to create booking", 'error');
    });
}

/**
 * Load All Bookings and Display in Table
 * 
 * Fetches all bookings from database and calls functions to:
 * - Display them in a table with guest names, dates, status
 * - Load available room options for the booking form
 */
function loadBookings() {
    loadCurrencyGlobal();   // Ensure currency symbol is up-to-date
    const bookingTableBody = document.querySelector('#bookingListTable tbody');
    if (bookingTableBody) {
        bookingTableBody.innerHTML = '<tr><td colspan="7" style="text-align:center;">Loading bookings...</td></tr>';
    }

    fetch('/api/bookings/', { headers: getAuthHeaders(false) })
    .then(response => response.json())
    .then(data => {
        window._allBookings = data;
        populateBookingList(data);
        loadRoomOptions();
    })
    .catch(error => {
        console.error('Load bookings error:', error);
        if (bookingTableBody) {
            bookingTableBody.innerHTML = '<tr><td colspan="7" style="text-align:center;">Failed to load bookings</td></tr>';
        }
    });
}

/**
 * Display Bookings in Table
 * 
 * Creates HTML table rows for all bookings, with action buttons based on booking status:
 * - Pending: Show "Confirm" and "Cancel" buttons
 * - Confirmed: Show "Check In" and "Cancel" buttons
 * - Checked In: Show "Check Out" button
 * - Checked Out / Cancelled: Show "View" button only
 */
function populateBookingList(bookings) {
    const tbody = document.querySelector('#bookingListTable tbody');
    if (!tbody) return;
    if (!bookings || bookings.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;">No bookings found</td></tr>';
        return;
    }

    let html = '';
    bookings.forEach(booking => {
        const bookingId = booking.id;
        const status    = booking.status || 'Pending';
        let actions     = '';

        // Show different buttons based on current booking status
        if (status === 'Pending') {
            actions = `
                <button type="button" class="secondary" onclick="confirmBooking(${bookingId})">Confirm</button>
                <button type="button" class="danger"    onclick="cancelBooking(${bookingId})">Cancel</button>`;
        } else if (status === 'Confirmed') {
            actions = `
                <button type="button" class="secondary" onclick="checkInGuest(${bookingId})">Check In</button>
                <button type="button" class="danger"    onclick="cancelBooking(${bookingId})">Cancel</button>`;
        } else if (status === 'Checked In') {
            actions = `
                <button type="button" class="secondary" onclick="checkOutGuest(${bookingId})">Check Out</button>`;
        } else {
            actions = `
                <button type="button" class="secondary" onclick="viewBookingDetails(${bookingId})">View</button>`;
        }

        html += `<tr>
            <td>${booking.booking_id || ''}</td>
            <td>${booking.guest_name || ''}</td>
            <td>${booking.room_number || ''}</td>
            <td>${formatDate(booking.check_in_date)}${booking.check_in_time ? '<br><small style="color:var(--muted)">' + booking.check_in_time.slice(0,5) + '</small>' : ''}</td>
            <td>${formatDate(booking.check_out_date)}${booking.check_out_time ? '<br><small style="color:var(--muted)">' + booking.check_out_time.slice(0,5) + '</small>' : ''}</td>
            <td>${formatCurrency(booking.total_price || 0)}</td>
            <td class="${status.toLowerCase().replace(/ /g, '-')}">${status}</td>
            <td>${actions}</td>
        </tr>`;
    });
    tbody.innerHTML = html;
}

/**
 * View Booking Details Modal
 * 
 * Opens a detailed modal showing all information about a booking:
 * - Guest name and contact info
 * - Room number
 * - Check-in and check-out dates
 * - Number of nights
 * - Total price
 * - Booking status
 */
function viewBookingDetails(bookingId) {
    fetch(`/api/bookings/${bookingId}/`, { headers: getAuthHeaders(false) })
    .then(r => r.json())
    .then(booking => {
        const modal = document.getElementById('viewBookingModal');
        if (!modal) return;
        
        document.getElementById('modalBookingId').textContent = `Booking #${booking.booking_id}`;
        document.getElementById('modalBookingStatus').textContent = booking.status || 'Pending';
        
        const body = document.getElementById('modalBookingBody');
        body.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                <div>
                    <label style="font-weight: bold; color: #666;">Guest Name</label>
                    <p>${booking.guest?.first_name || ''} ${booking.guest?.last_name || ''}</p>
                </div>
                <div>
                    <label style="font-weight: bold; color: #666;">Email</label>
                    <p>${booking.guest?.email || 'N/A'}</p>
                </div>
                <div>
                    <label style="font-weight: bold; color: #666;">Phone</label>
                    <p>${booking.guest?.phone || 'N/A'}</p>
                </div>
                <div>
                    <label style="font-weight: bold; color: #666;">Room</label>
                    <p>${booking.room?.room_number || 'N/A'}</p>
                </div>
                <div>
                    <label style="font-weight: bold; color: #666;">Planned Check-in</label>
                    <p>${formatDate(booking.check_in_date)}${booking.check_in_time ? ' at ' + booking.check_in_time.slice(0,5) : ''}</p>
                </div>
                <div>
                    <label style="font-weight: bold; color: #666;">Planned Check-out</label>
                    <p>${formatDate(booking.check_out_date)}${booking.check_out_time ? ' at ' + booking.check_out_time.slice(0,5) : ''}</p>
                </div>
                <div>
                    <label style="font-weight: bold; color: #666;">Actual Check-in</label>
                    <p>${booking.actual_check_in ? '<span style="color:var(--green)">🟢 ' + booking.actual_check_in + '</span>' : '<span style="opacity:.5;">—</span>'}</p>
                </div>
                <div>
                    <label style="font-weight: bold; color: #666;">Actual Check-out</label>
                    <p>${booking.actual_check_out ? '<span style="color:var(--purple)">🔴 ' + booking.actual_check_out + '</span>' : '<span style="opacity:.5;">—</span>'}</p>
                </div>
                <div>
                    <label style="font-weight: bold; color: #666;">Number of Nights</label>
                    <p>${booking.number_of_nights || 'N/A'}</p>
                </div>
                <div>
                    <label style="font-weight: bold; color: #666;">Total Price</label>
                    <p>${formatCurrency(booking.total_price)}</p>
                </div>
            </div>
        `;
        
        modal.classList.add('active');
    })
    .catch(() => showToast('Failed to load booking details', 'error'));
}

function closeBookingModal() {
    const modal = document.getElementById('viewBookingModal');
    if (!modal) return;
    modal.classList.remove('active');
}

/**
 * Filter bookings by search text and/or status
 */
function filterBookings() {
    const search = (document.getElementById('bookingSearch')?.value || '').toLowerCase();
    const status = document.getElementById('bookingStatusFilter')?.value || '';
    const all    = window._allBookings || [];
    const filtered = all.filter(b => {
        const matchSearch = !search ||
            (b.booking_id  || '').toLowerCase().includes(search) ||
            (b.guest_name  || '').toLowerCase().includes(search) ||
            (b.room_number || '').toLowerCase().includes(search);
        const matchStatus = !status || b.status === status;
        return matchSearch && matchStatus;
    });
    populateBookingList(filtered);
}


/**
 * Confirm Booking
 * 
 * Changes booking status from "Pending" to "Confirmed".
 * Used when booking is verified and ready.
 */
function confirmBooking(bookingId) {
    showConfirm({
        icon: 'âœ…',
        title: 'Confirm Booking',
        message: 'Are you sure you want to confirm this booking?',
        btnText: 'Yes, Confirm',
        btnClass: 'confirm-btn-success',
        onConfirm: () => {
            fetch(`/api/bookings/${bookingId}/confirm/`, {
                method: 'POST', 
                headers: getAuthHeaders(true)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status || data.booking_id) {
                    showToast('âœ… Booking confirmed', 'success');
                    loadBookings();
                } else {
                    showToast(data.error || 'Failed to confirm', 'error');
                }
            })
            .catch(() => showToast('Server error', 'error'));
        }
    });
}


function checkInGuest(bookingId) {
    showConfirm({
        icon: 'ðŸ¨',
        title: 'Check In Guest',
        message: 'Confirm guest check-in? The room will be marked as Occupied.',
        btnText: 'Check In',
        btnClass: 'confirm-btn-success',
        onConfirm: () => {
            fetch(`/api/bookings/${bookingId}/check_in/`, {
                method: 'POST', headers: getAuthHeaders(true)
            })
            .then(r => r.json())
            .then(data => {
                if (data.status) { showToast('Guest checked in', 'success'); loadBookings(); }
                else showToast(data.error || 'Failed to check in', 'error');
            })
            .catch(() => showToast('Server error', 'error'));
        }
    });
}

function checkOutGuest(bookingId) {
    // First fetch booking to check payment status
    fetch(`/api/bookings/${bookingId}/`, { headers: getAuthHeaders(false) })
    .then(r => r.json())
    .then(booking => {
        const paymentStatus = booking.payment?.status || 'Pending';
        
        // Check if payment is completed
        if (paymentStatus !== 'Completed') {
            showToast(`âš ï¸ Payment is ${paymentStatus}. Please process payment first before checkout.`, 'error');
            return;
        }
        
        // Payment is complete, proceed with check-out
        showConfirm({
            icon: 'ðŸšª',
            title: 'Check Out Guest',
            message: 'Confirm guest check-out? The room will be marked as Available.',
            btnText: 'Check Out',
            btnClass: 'confirm-btn-warning',
            onConfirm: () => {
                fetch(`/api/bookings/${bookingId}/check_out/`, {
                    method: 'POST', headers: getAuthHeaders(true)
                })
                .then(r => r.json())
                .then(data => {
                    if (data.status) { 
                        showToast('âœ… Guest checked out', 'success'); 
                        loadBookings(); 
                    }
                    else showToast(data.error || 'Failed to check out', 'error');
                })
                .catch(() => showToast('Server error', 'error'));
            }
        });
    })
    .catch(() => showToast('Failed to load booking details', 'error'));
}

function cancelBooking(bookingId) {
    showConfirm({
        icon: 'âŒ',
        title: 'Cancel Booking',
        message: 'Are you sure you want to cancel this booking? This will refund the payment.',
        btnText: 'Yes, Cancel',
        btnClass: 'confirm-btn-danger',
        onConfirm: () => {
            fetch(`/api/bookings/${bookingId}/cancel/`, {
                method: 'POST', headers: getAuthHeaders(true)
            })
            .then(r => r.json())
            .then(data => {
                if (data.status) { showToast('Booking cancelled', 'success'); loadBookings(); }
                else showToast(data.error || 'Failed to cancel', 'error');
            })
            .catch(() => showToast('Server error', 'error'));
        }
    });
}




function loadRoomOptions() {
    const selectedType     = document.getElementById("roomType")?.value;
    const roomNumberSelect = document.getElementById("roomNumber");
    if (!roomNumberSelect) return;

    const checkIn  = document.getElementById('checkIn')?.value;
    const checkOut = document.getElementById('checkOut')?.value;
    let roomsUrl = '/api/rooms/';
    if (checkIn && checkOut) {
        roomsUrl = `/api/rooms/available/?check_in=${checkIn}&check_out=${checkOut}`;
    }

    fetch(roomsUrl, { headers: getAuthHeaders(false) })
    .then(response => response.json())
    .then(roomData => {
        const rooms = Array.isArray(roomData) ? roomData : (roomData.results || roomData);
        const availableRooms = rooms.filter(room => room.status === 'Available' || roomsUrl.includes('available'));
        let options = '<option value="">Select available room</option>';
        availableRooms
            .filter(room => !selectedType || room.room_type_name === selectedType || room.room_type === selectedType)
            .forEach(room => {
                const roomNumber = room.room_number || '';
                const roomType   = room.room_type_name || room.room_type || '';
                options += `<option value="${roomNumber}">${roomNumber} - ${roomType}</option>`;
            });
        if (options === '<option value="">Select available room</option>') {
            options = '<option value="">No rooms available</option>';
        }
        roomNumberSelect.innerHTML = options;
    })
    .catch(() => {
        roomNumberSelect.innerHTML = '<option value="">Unable to load rooms</option>';
    });
}

/* ================= ROOMS FUNCTIONS ================= */
function loadRooms() {
    loadCurrencyGlobal();   // ensure currency symbol is up-to-date
    fetch('/api/rooms/', { headers: getAuthHeaders(false) })
    .then(response => response.json())
    .then(rooms => {
        const available   = rooms.filter(r => r.status === 'Available').length;
        const occupied    = rooms.filter(r => r.status === 'Occupied').length;
        const maintenance = rooms.filter(r => r.status === 'Maintenance').length;

        document.getElementById("totalRooms").textContent       = rooms.length;
        document.getElementById("availableRooms").textContent   = available;
        document.getElementById("occupiedRooms").textContent    = occupied;
        document.getElementById("maintenanceRooms").textContent = maintenance;

        populateRoomsTable(rooms);
    })
    .catch(error => {
        console.error('Load rooms error:', error);
        showToast('Failed to load rooms', 'error');
    });
}

function populateRoomsTable(rooms) {
    const tbody = document.getElementById("roomTable");
    if (!tbody) return;
    if (!rooms || rooms.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;">No rooms available</td></tr>';
        return;
    }
    let html = "";
    // Also update cleaning count if card exists
    const cleanEl = document.getElementById('cleaningRooms');
    if (cleanEl) cleanEl.textContent = rooms.filter(r => r.status === 'Cleaning').length;

    rooms.forEach(room => {
        const sc = (room.status || '').toLowerCase().replace(/ /g, '-');
        html += `<tr>
            <td><strong>${room.room_number || '-'}</strong></td>
            <td>${room.room_type_name || room.room_type || 'Standard'}</td>
            <td>Floor ${room.floor || 1}</td>
            <td><span class="status-badge ${sc}">${room.status || 'Available'}</span></td>
            <td>${formatCurrency(room.price_per_night || 0)}</td>
            <td>
                <button type="button" class="secondary" style="width:auto;padding:6px 10px;"
                    onclick="editRoom(${room.id}, '${room.room_number}', '${room.status}', ${room.price_per_night || 0}, ${room.floor || 1})">Edit</button>
            </td>
        </tr>`;
    });
    tbody.innerHTML = html;
}

function addRoom(event) {
    if (event) event.preventDefault();

    const roomData = {
        roomNumber: document.getElementById("newRoomNumber")?.value,
        roomType:   document.getElementById("newRoomType")?.value,
        price:      parseFloat(document.getElementById("newRoomPrice")?.value),
        floor:      parseInt(document.getElementById('newRoomFloor')?.value) || 1
    };

    if (!roomData.roomNumber || !roomData.roomType || !roomData.price) {
        showToast("Please fill all room details", 'error');
        return;
    }

    fetch('/api/rooms/add/', {
        method: 'POST',
        headers: getAuthHeaders(true),
        body: JSON.stringify(roomData)
    })
    .then(response => response.json().then(body => ({ status: response.status, body })))
    .then(({ status, body }) => {
        if (status >= 200 && status < 300) {
            showToast("âœ… Room added successfully!", 'success');
            if (event?.target) event.target.reset();
            loadRooms();
        } else {
            showToast(body.error || "Failed to add room", 'error');
        }
    })
    .catch(() => showToast("Failed to add room", 'error'));
}

function bulkAddRooms(event) {
    if (event) event.preventDefault();

    const start = parseInt(document.getElementById('bulkStart')?.value);
    const end   = parseInt(document.getElementById('bulkEnd')?.value);
    const type  = document.getElementById('bulkRoomType')?.value;
    const price = parseFloat(document.getElementById('bulkPrice')?.value);
    const floor = parseInt(document.getElementById('bulkFloor')?.value) || 1;

    if (!start || !end || !type || !price) {
        showToast('Please fill all bulk room fields', 'error');
        return;
    }
    if (end < start) {
        showToast('End room must be greater than or equal to start room', 'error');
        return;
    }
    if ((end - start + 1) > 200) {
        showToast('Maximum 200 rooms per batch', 'error');
        return;
    }

    const btn = document.getElementById('bulkSubmitBtn');
    if (btn) { btn.disabled = true; btn.textContent = 'Adding...'; }

    fetch('/api/rooms/bulk-add/', {
        method: 'POST',
        headers: getAuthHeaders(true),
        body: JSON.stringify({ startRoom: start, endRoom: end, roomType: type, price, floor })
    })
    .then(r => r.json().then(body => ({ status: r.status, body })))
    .then(({ status, body }) => {
        if (status >= 200 && status < 300) {
            showToast(body.message || (body.created + ' room(s) added!'), 'success');
            if (event?.target) event.target.reset();
            loadRooms();
        } else {
            showToast(body.error || 'Failed to add rooms', 'error');
        }
    })
    .catch(() => showToast('Failed to add rooms', 'error'))
    .finally(() => {
        if (btn) { btn.disabled = false; btn.textContent = 'Add Rooms'; }
    });
}

function editRoom(roomId, roomNumber, currentStatus, price, floor) {
    const modal = document.getElementById('editRoomModal');
    if (!modal) return;
    
    document.getElementById('editRoomId').value          = roomId;
    document.getElementById('editRoomSubtitle').textContent = `Update Room ${roomNumber}`;
    document.getElementById('editRoomStatus').value      = currentStatus;
    document.getElementById('editRoomPrice').value       = price || '';
    document.getElementById('editRoomFloor').value       = floor || 1;
    document.getElementById('editRoomDescription').value = '';
    
    modal.classList.add('active');
}

function closeRoomModal() {
    const modal = document.getElementById('editRoomModal');
    if (!modal) return;
    modal.classList.remove('active');
}

function saveRoomEdit() {
    const roomId = document.getElementById('editRoomId').value;
    const newStatus = document.getElementById('editRoomStatus').value;
    
    if (!roomId || !newStatus) {
        showToast('Please select a status', 'error');
        return;
    }
    
    const price = document.getElementById('editRoomPrice').value;
    const floor = document.getElementById('editRoomFloor').value;
    const desc  = document.getElementById('editRoomDescription').value;
    const payload = { status: newStatus, is_available: newStatus === 'Available' };
    if (price) payload.price_per_night = parseFloat(price);
    if (floor) payload.floor = parseInt(floor);
    if (desc)  payload.description = desc;

    fetch(`/api/rooms/${roomId}/`, {
        method: 'PATCH',
        headers: getAuthHeaders(true),
        body: JSON.stringify(payload)
    })
    .then(r => r.json())
    .then(data => {
        if (data.id) {
            showToast(`Room updated to ${newStatus}`, 'success');
            closeRoomModal();
            loadRooms();
        } else {
            showToast(data.error || 'Failed to update room', 'error');
        }
    })
    .catch(() => showToast('Failed to update room', 'error'));
}

/* ================= CUSTOMERS FUNCTIONS ================= */
function loadCustomers() {
    loadCurrencyGlobal();   // ensure currency symbol is up-to-date
    fetch('/api/customers/', { headers: getAuthHeaders(false) })
    .then(response => response.json())
    .then(data => {
        document.getElementById("totalCustomers").textContent = data.totalCustomers;
        document.getElementById("activeBookings").textContent = data.activeBookings;
        document.getElementById("totalRevenue").textContent   = formatCurrency(data.totalRevenue);
        document.getElementById("avgRating").textContent      = data.avgRating;
        populateCustomersTable(data.customers);
    })
    .catch(error => {
        console.error('Load customers error:', error);
        showToast('Failed to load customers', 'error');
    });
}

function populateCustomersTable(customers) {
    const tbody = document.querySelector('#customersTable tbody');
    if (!tbody) return;
    if (!customers || customers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No customers found</td></tr>';
        return;
    }
    let html = "";
    customers.forEach(customer => {
        html += `<tr>
            <td>${customer.name || ''}</td>
            <td>${customer.email}</td>
            <td>${customer.phone}</td>
            <td>${customer.country || 'N/A'}</td>
            <td>${customer.bookings || 0}</td>
            <td>${formatCurrency(customer.total_spent || 0)}</td>
            <td>
                <button type="button" class="secondary" onclick="viewCustomer(${customer.id})">View</button>
                <button type="button" class="secondary" onclick="editCustomer(${customer.id})">Edit</button>
            </td>
        </tr>`;
    });
    tbody.innerHTML = html;
}

function viewCustomer(customerId) {
    fetch(`/api/customer/${customerId}/bookings/`, { headers: getAuthHeaders(false) })
    .then(r => r.json())
    .then(data => {
        const modal = document.getElementById('customerModal');
        if (!modal) return;

        document.getElementById('modalCustomerName').textContent = data.customer.name || 'Customer';
        document.getElementById('modalCustomerEmail').textContent = data.customer.email || 'N/A';

        const body = document.getElementById('modalCustomerBody');
        const stats = data.statistics || {};
        const bookings = data.bookings || [];

        let bookingRows = '';
        if (bookings.length === 0) {
            bookingRows = '<tr><td colspan="7" style="text-align:center;">No booking history</td></tr>';
        } else {
            bookings.forEach(booking => {
                const actualIn  = booking.actual_check_in
                    ? '<br><small style="color:var(--green);">✓ ' + booking.actual_check_in + '</small>'
                    : '';
                const actualOut = booking.actual_check_out
                    ? '<br><small style="color:var(--purple);">✓ ' + booking.actual_check_out + '</small>'
                    : '';
                const payBadge = booking.payment_status === 'Completed'
                    ? '<span style="color:var(--green);font-weight:600;">' + booking.payment_status + '</span>'
                    : '<span style="color:var(--orange);font-weight:600;">' + (booking.payment_status || 'N/A') + '</span>';
                bookingRows += `<tr>
                    <td>${booking.booking_id}</td>
                    <td>${booking.room_number}<br><small style="opacity:.6;">${booking.room_type}</small></td>
                    <td>${formatDate(booking.check_in)}${booking.check_in_time ? '<br><small style="opacity:.6;">' + booking.check_in_time + '</small>' : ''}${actualIn}</td>
                    <td>${formatDate(booking.check_out)}${booking.check_out_time ? '<br><small style="opacity:.6;">' + booking.check_out_time + '</small>' : ''}${actualOut}</td>
                    <td>${booking.nights || booking.number_of_nights || 0} night${(booking.nights || booking.number_of_nights || 0) !== 1 ? 's' : ''}</td>
                    <td>${formatCurrency(booking.total_price)}<br>${payBadge}</td>
                    <td>${booking.status}</td>
                </tr>`;
            });
        }

        body.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 18px;">
                <div>
                    <label style="font-weight: bold; color: #666;">Phone</label>
                    <p>${data.customer.phone || 'N/A'}</p>
                </div>
                <div>
                    <label style="font-weight: bold; color: #666;">Country</label>
                    <p>${data.customer.country || 'N/A'}</p>
                </div>
                <div>
                    <label style="font-weight: bold; color: #666;">Total Bookings</label>
                    <p>${data.customer.total_bookings || 0}</p>
                </div>
                <div>
                    <label style="font-weight: bold; color: #666;">Loyalty Tier</label>
                    <p>${stats.loyalty_tier || 'Bronze'}</p>
                </div>
                <div>
                    <label style="font-weight: bold; color: #666;">Completed Bookings</label>
                    <p>${stats.completed_bookings || 0}</p>
                </div>
                <div>
                    <label style="font-weight: bold; color: #666;">Total Spent</label>
                    <p>${formatCurrency(stats.total_spent || 0)}</p>
                </div>
            </div>
            <div>
                <h3 style="margin-bottom: 10px;">Booking History</h3>
                <table style="width:100%; border-collapse: collapse;">
                    <thead>
                        <tr style="text-align:left; color: var(--text); opacity: 0.8;">
                            <th>Booking</th><th>Room</th><th>Check-in</th><th>Check-out</th><th>Nights</th><th>Amount</th><th>Status</th>
                        </tr>
                    </thead>
                    <tbody>${bookingRows}</tbody>
                </table>
            </div>
        `;

        modal.classList.add('active');
    })
    .catch(() => showToast('Failed to load customer booking history', 'error'));
}

function closeCustomerModal() {
    const modal = document.getElementById('customerModal');
    if (!modal) return;
    modal.classList.remove('active');
}

function addCustomer() {
    const firstName = document.getElementById("newFirstName")?.value?.trim();
    const lastName = document.getElementById("newLastName")?.value?.trim();
    const email = document.getElementById("newEmail")?.value?.trim();
    const phone = document.getElementById("newPhone")?.value?.trim();
    const country = document.getElementById("newCountry")?.value?.trim();
    const address = document.getElementById("newAddress")?.value?.trim();

    if (!firstName || !lastName || !email || !phone) {
        showToast("Please fill all required fields (First Name, Last Name, Email, Phone)", 'error');
        return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showToast("Please enter a valid email address", 'error');
        return;
    }

    fetch('/api/guests/', {
        method: 'POST',
        headers: getAuthHeaders(true),
        body: JSON.stringify({
            first_name: firstName,
            last_name: lastName,
            email: email,
            phone: phone,
            country: country || '',
            address: address || ''
        })
    })
    .then(response => response.json().then(body => ({ status: response.status, body })))
    .then(({ status, body }) => {
        if (status >= 200 && status < 300) {
            showToast("âœ… Customer added successfully!", 'success');
            document.getElementById("newFirstName").value = '';
            document.getElementById("newLastName").value = '';
            document.getElementById("newEmail").value = '';
            document.getElementById("newPhone").value = '';
            document.getElementById("newCountry").value = '';
            document.getElementById("newAddress").value = '';
            loadCustomers();
        } else {
            showToast(body.error || "Failed to add customer", 'error');
        }
    })
    .catch(error => {
        console.error('Add customer error:', error);
        showToast("Failed to add customer", 'error');
    });
}

function searchCustomers() {
    const searchInput = document.getElementById("customerSearch")?.value?.trim() || '';
    if (!searchInput) {
        loadCustomers();
        return;
    }

    fetch(`/api/customers/?search=${encodeURIComponent(searchInput)}`, { headers: getAuthHeaders(false) })
    .then(response => response.json())
    .then(data => {
        populateCustomersTable(data.customers);
    })
    .catch(error => {
        console.error('Search customers error:', error);
        showToast('Failed to search customers', 'error');
    });
}

function editCustomer(customerId) {
    fetch(`/api/guests/${customerId}/`, { headers: getAuthHeaders(false) })
    .then(r => r.json())
    .then(guest => {
        const modal = document.getElementById('editCustomerModal');
        if (!modal) return;
        
        document.getElementById('editCustomerId').value = customerId;
        document.getElementById('editFirstName').value = guest.first_name || '';
        document.getElementById('editLastName').value = guest.last_name || '';
        document.getElementById('editEmail').value = guest.email || '';
        document.getElementById('editPhone').value = guest.phone || '';
        document.getElementById('editCountry').value = guest.country || '';
        document.getElementById('editCity').value = guest.city || '';
        document.getElementById('editAddress').value = guest.address || '';
        
        modal.classList.add('active');
    })
    .catch(() => showToast('Failed to load customer details', 'error'));
}

function closeEditCustomerModal() {
    const modal = document.getElementById('editCustomerModal');
    if (!modal) return;
    modal.classList.remove('active');
}

function saveCustomerEdit() {
    const customerId = document.getElementById('editCustomerId').value;
    const firstName = document.getElementById('editFirstName')?.value?.trim();
    const lastName = document.getElementById('editLastName')?.value?.trim();
    const email = document.getElementById('editEmail')?.value?.trim();
    const phone = document.getElementById('editPhone')?.value?.trim();
    const country = document.getElementById('editCountry')?.value?.trim();
    const city = document.getElementById('editCity')?.value?.trim();
    const address = document.getElementById('editAddress')?.value?.trim();

    if (!firstName || !lastName || !email || !phone) {
        showToast("Please fill all required fields", 'error');
        return;
    }

    fetch(`/api/guests/${customerId}/`, {
        method: 'PATCH',
        headers: getAuthHeaders(true),
        body: JSON.stringify({
            first_name: firstName,
            last_name: lastName,
            email: email,
            phone: phone,
            country: country,
            city: city,
            address: address
        })
    })
    .then(response => response.json().then(body => ({ status: response.status, body })))
    .then(({ status, body }) => {
        if (status >= 200 && status < 300) {
            showToast("âœ… Customer updated successfully!", 'success');
            closeEditCustomerModal();
            loadCustomers();
        } else {
            showToast(body.error || "Failed to update customer", 'error');
        }
    })
    .catch(error => {
        console.error('Update customer error:', error);
        showToast("Failed to update customer", 'error');
    });
}

/* ================= PAYMENTS FUNCTIONS ================= */



function loadPayments() {
    loadCurrencyGlobal();  // ensure currency symbol is up-to-date before formatting amounts
    fetch('/api/payments-summary/', { headers: getAuthHeaders(false) })
    .then(response => response.json())
    .then(data => {
        document.getElementById("totalPaymentsCount").textContent   = data.totalPayments;
        document.getElementById("completedPaymentsCount").textContent = data.completed;
        document.getElementById("pendingPaymentsCount").textContent  = data.pending;
        document.getElementById("totalRevenueCount").textContent     = formatCurrency(data.totalRevenue);

        populatePaymentsTable(data.payments);

        const total = data.completed + data.pending + data.failed;
        if (total > 0) {
            document.getElementById("completedPaymentsPercent").textContent = Math.round((data.completed / total) * 100);
            document.getElementById("pendingPaymentsPercent").textContent   = Math.round((data.pending   / total) * 100);
            document.getElementById("failedPaymentsPercent").textContent    = Math.round((data.failed    / total) * 100);
            document.getElementById("completedPaymentsBar").style.width = ((data.completed / total) * 100) + "%";
            document.getElementById("pendingPaymentsBar").style.width   = ((data.pending   / total) * 100) + "%";
            document.getElementById("failedPaymentsBar").style.width    = ((data.failed    / total) * 100) + "%";
        }
    })
    .catch(error => {
        console.error('Load payments error:', error);
        showToast('Failed to load payments', 'error');
    });
}

function populatePaymentsTable(payments) {
    const table = document.getElementById("paymentsTable");
    let html = `<tr>
        <th>Guest Name</th>
        <th>Booking</th>
        <th>Amount</th>
        <th>Method</th>
        <th>Date</th>
        <th>Status</th>
        <th>Action</th>
    </tr>`;
    if (!payments || payments.length === 0) {
        html += '<tr><td colspan="5" style="text-align:center;">No payments found</td></tr>';
        table.innerHTML = html;
        return;
    }
    payments.forEach(payment => {
        const isPending = (payment.status || '').toLowerCase() === 'pending';
        const actionBtn = isPending
            ? `<button type="button" onclick="openPaymentModal(${payment.id}, ${payment.amount}, '${(payment.guestName || payment.name || '').replace(/'/g, "\\'")}')"
                style="width:auto;padding:6px 12px;background:linear-gradient(135deg,#059669,#047857);">
                ðŸ’³ Pay
               </button>`
            : `<span class="status-badge confirmed">âœ“ Paid</span>`;

        html += `<tr>
            <td>${payment.guestName || payment.name || '-'}</td>
            <td style="font-size:11px;">${payment.bookingId || '-'}</td>
            <td>${formatCurrency(payment.amount)}</td>
            <td style="font-size:11px;">${payment.method || '-'}</td>
            <td>${formatDate(payment.date)}</td>
            <td class="${(payment.status || '').toLowerCase()}">${payment.status || 'Pending'}</td>
            <td>${actionBtn}</td>
        </tr>`;
    });
    table.innerHTML = html;
}

/* ================= SETTINGS FUNCTIONS ================= */
function loadSettings() {
    fetch('/api/settings/', { headers: getAuthHeaders(false) })
    .then(response => response.json())
    .then(data => {

        Object.keys(data).forEach(key => {
            const element = document.getElementById(key);
            if (!element) return;

            if (element.tagName === 'SELECT') {
                // Find the option whose value OR text matches (case-insensitive)
                const target = String(data[key]).trim().toLowerCase();
                let matched = false;
                for (const opt of element.options) {
                    if (opt.value.trim().toLowerCase() === target ||
                        opt.text.trim().toLowerCase()  === target) {
                        element.value = opt.value;
                        matched = true;
                        break;
                    }
                }
                // Fallback: try setting directly (works when values match exactly)
                if (!matched) element.value = data[key];
            } else {
                element.value = data[key];
            }
        });

        // Update global currency symbol so formatCurrency() is correct
        applyCurrencyFromSettings(data);
    })
    .catch(error => {
        console.error('Load settings error:', error);
        showToast('Failed to load settings', 'error');
    });
}

function saveSettings(event) {
    if (event) event.preventDefault();

    const settingsData = {
        hotelName:      document.getElementById("hotelName")?.value      || "",
        hotelEmail:     document.getElementById("hotelEmail")?.value     || "",
        hotelPhone:     document.getElementById("hotelPhone")?.value     || "",
        hotelAddress:   document.getElementById("hotelAddress")?.value   || "",
        hotelCity:      document.getElementById("hotelCity")?.value      || "",
        currency:       document.getElementById("currency")?.value       || "USD ($)",
        paymentGateway: document.getElementById("paymentGateway")?.value || "Stripe",
        taxRate:        document.getElementById("taxRate")?.value        || "10",
        dateFormat:     document.getElementById("dateFormat")?.value     || "MM/DD/YYYY",
        timeZone:       document.getElementById("timeZone")?.value       || "UTC-5",
        language:       document.getElementById("language")?.value       || "English",
        checkInTime:    document.getElementById("checkInTime")?.value    || "15:00",
        checkOutTime:   document.getElementById("checkOutTime")?.value   || "11:00",
        cleaningTime:   document.getElementById("cleaningTime")?.value   || "30",
        paymentTimeout: document.getElementById("paymentTimeout")?.value || "3600",
        currencyCode:   document.getElementById("currencyCode")?.value   || "USD",
        baseRate:       document.getElementById("baseRate")?.value       || "150"
    };

    fetch('/api/settings/', {
        method: 'POST',
        headers: getAuthHeaders(true),
        body: JSON.stringify(settingsData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status) {
            // Immediately apply the new currency so formatCurrency() is up-to-date
            applyCurrencyFromSettings(settingsData);
            showToast('âœ… Settings saved successfully', 'success');
        } else {
            showToast(data.error || 'Failed to save settings', 'error');
        }
    })
    .catch(() => showToast('Failed to save settings', 'error'));
}

function resetSettings(){
    showConfirm({
        icon: '⚠️', title: 'Reset Settings',
        message: 'Reset all settings to defaults? This cannot be undone.',
        btnText: 'Yes, Reset', btnClass: 'confirm-btn-danger',
        onConfirm: function() {
            const defaults = {
                    currency: 'USD ($)', paymentGateway: 'Stripe', taxRate: '10',
                    dateFormat: 'MM/DD/YYYY', timeZone: 'UTC-5', language: 'English',
                    checkInTime: '15:00', checkOutTime: '11:00',
                    cleaningTime: '30', paymentTimeout: '3600', baseRate: '150'
                };
                fetch('/api/settings/', {
                    method: 'POST',
                    headers: getAuthHeaders(true),
                    body: JSON.stringify(defaults)
                })
                .then(r => r.json())
                .then(data => {
                    if (data.status) {
                        applyCurrencyFromSettings(defaults);
                        showToast('Settings reset to defaults', 'success');
                        setTimeout(() => location.reload(), 800);
                    } else {
                        showToast('Failed to reset settings', 'error');
                    }
                })
                .catch(() => showToast('Failed to reset settings', 'error'));
        }
    });
}


/* ================= USER MANAGEMENT (Admin only) ================= */
let currentUserRole = null;

function loadCurrentUser() {
    fetch('/accounts/api/me/', { headers: getAuthHeaders(false) })
    .then(r => r.json())
    .then(data => {
        currentUserRole = data.role;
        // Show/hide admin-only UI elements
        document.querySelectorAll('.admin-only').forEach(el => {
            el.style.display = data.is_admin ? '' : 'none';
        });
        document.querySelectorAll('.manager-only').forEach(el => {
            el.style.display = data.is_manager ? '' : 'none';
        });
        // Show username in header
        const userDisplay = document.getElementById('userDisplay');
        if (userDisplay) {
            userDisplay.textContent = data.first_name || data.username;
        }
        const userRoleDisplay = document.getElementById('userRoleDisplay');
        if (userRoleDisplay) {
            userRoleDisplay.textContent = data.role.charAt(0).toUpperCase() + data.role.slice(1);
        }
    })
    .catch(() => {});
}

function loadUsers() {
    fetch('/accounts/api/users/', { headers: getAuthHeaders(false) })
    .then(r => r.json())
    .then(data => {
        populateUsersTable(data.users || []);
    })
    .catch(() => showToast('Failed to load users', 'error'));
}

function populateUsersTable(users) {
    const tbody = document.getElementById('usersTableBody');
    if (!tbody) return;

    // Update stat cards if present
    const totalEl = document.getElementById('totalUsersCount');
    const adminEl = document.getElementById('adminCount');
    const staffEl = document.getElementById('staffCount');
    if (totalEl) totalEl.textContent = users.length;
    if (adminEl) adminEl.textContent = users.filter(u => u.role === 'admin').length;
    if (staffEl) staffEl.textContent = users.filter(u => u.role === 'staff' || u.role === 'manager').length;

    if (!users.length) {
        tbody.innerHTML = '<tr><td colspan="6" class="table-empty">No users found</td></tr>';
        return;
    }
    const roleBadge = { admin: 'var(--blue)', manager: 'var(--green)', staff: 'var(--muted)' };
    let html = '';
    users.forEach(u => {
        const color = roleBadge[u.role] || 'var(--muted)';
        html += `<tr>
            <td>${u.first_name} ${u.last_name}</td>
            <td>${u.username}</td>
            <td>${u.email}</td>
            <td><span style="color:${color};font-weight:600;text-transform:capitalize;">${u.role}</span></td>
            <td><span class="${u.is_active ? 'confirmed' : 'cancelled'}">${u.is_active ? 'Active' : 'Inactive'}</span></td>
            <td>
                <button type="button" class="secondary" onclick="openEditUser(${u.id},'${u.first_name}','${u.last_name}','${u.email}','${u.role}',${u.is_active})">Edit</button>
                <button type="button" class="danger"    onclick="deleteUser(${u.id},'${u.username}')">Delete</button>
            </td>
        </tr>`;
    });
    tbody.innerHTML = html;
}

function openAddUser() {
    document.getElementById('addUserForm')?.reset();
    document.getElementById('addUserMsg').innerHTML = '';
    document.getElementById('addUserModal').classList.add('active');
}

function closeAddUser() {
    document.getElementById('addUserModal').classList.remove('active');
}

function submitAddUser() {
    const first_name = document.getElementById('au_first_name').value.trim();
    const last_name  = document.getElementById('au_last_name').value.trim(); // optional
    const username   = document.getElementById('au_username').value.trim();
    const email      = document.getElementById('au_email').value.trim();
    const password   = document.getElementById('au_password').value.trim();
    const role       = document.getElementById('au_role').value.trim();

    const msgDiv = document.getElementById('addUserMsg');

    // only required fields
    const requiredFields = [first_name, username, email, password, role];

    if (requiredFields.some(field => field === '')) {
        msgDiv.innerHTML = '<div class="msg-error">Please fill in all required fields.</div>';
        return;
    }

    fetch('/accounts/api/users/create/', {
        method: 'POST',
        headers: getAuthHeaders(true),
        body: JSON.stringify({
            first_name,
            last_name, // can be empty
            username,
            email,
            password,
            role
        })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            showToast('âœ… User created successfully', 'success');
            closeAddUser();
            loadUsers();
        } else {
            msgDiv.innerHTML = `<div class="msg-error">${data.error}</div>`;
        }
    })
    .catch(() => {
        msgDiv.innerHTML = '<div class="msg-error">Server error. Please try again.</div>';
    });
}

function openEditUser(id, firstName, lastName, email, role, isActive) {
    document.getElementById('eu_id').value         = id;
    document.getElementById('eu_first_name').value = firstName;
    document.getElementById('eu_last_name').value  = lastName;
    document.getElementById('eu_email').value      = email;
    document.getElementById('eu_role').value       = role;
    document.getElementById('eu_is_active').value  = isActive ? 'true' : 'false';
    document.getElementById('editUserMsg').innerHTML = '';
    document.getElementById('editUserModal').classList.add('active');
}

function closeEditUser() {
    document.getElementById('editUserModal').classList.remove('active');
}

function submitEditUser() {
    const id         = document.getElementById('eu_id').value;
    const first_name = document.getElementById('eu_first_name').value.trim();
    const last_name  = document.getElementById('eu_last_name').value.trim();
    const email      = document.getElementById('eu_email').value.trim();
    const role       = document.getElementById('eu_role').value;
    const is_active  = document.getElementById('eu_is_active').value === 'true';
    const msgDiv     = document.getElementById('editUserMsg');

    fetch(`/accounts/api/users/${id}/`, {
        method: 'POST',
        headers: getAuthHeaders(true),
        body: JSON.stringify({ first_name, last_name, email, role, is_active })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            showToast('âœ… User updated successfully', 'success');
            closeEditUser();
            loadUsers();
        } else {
            msgDiv.innerHTML = `<div class="msg-error">${data.error}</div>`;
        }
    })
    .catch(() => {
        msgDiv.innerHTML = '<div class="msg-error">Server error. Please try again.</div>';
    });
}

function deleteUser(userId, username) {
    showConfirm({
        icon: 'ðŸ—‘ï¸',
        title: 'Delete User',
        message: `Delete user "${username}"? This cannot be undone.`,
        btnText: 'Delete',
        btnClass: 'confirm-btn-danger',
        onConfirm: () => {
            fetch(`/accounts/api/users/${userId}/delete/`, {
                method: 'DELETE', headers: getAuthHeaders(false)
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) { showToast('User deleted', 'success'); loadUsers(); }
                else showToast(data.error || 'Failed to delete user', 'error');
            })
            .catch(() => showToast('Failed to delete user', 'error'));
        }
    });
}       


/* ================= CUSTOM CONFIRM MODAL ================= */
let _confirmCallback = null;

function showConfirm(options) {
    document.getElementById('confirmIcon').textContent    = options.icon    || 'âš ï¸';
    document.getElementById('confirmTitle').textContent   = options.title   || 'Are you sure?';
    document.getElementById('confirmMessage').textContent = options.message || '';

    const btn = document.getElementById('confirmOkBtn');
    btn.textContent  = options.btnText  || 'Confirm';
    btn.className    = options.btnClass || 'confirm-btn-danger';

    _confirmCallback = options.onConfirm || null;

    const modal = document.getElementById('confirmModal');
    if (!modal) return;
    modal.classList.add('active');
}

function closeConfirm() {
    const modal = document.getElementById('confirmModal');
    if (modal) modal.classList.remove('active');
    _confirmCallback = null;
}

function executeConfirm() {
    if (typeof _confirmCallback === 'function') _confirmCallback();
    closeConfirm();
}   

/* ================= PAGE LOAD HANDLERS ================= */
document.addEventListener("DOMContentLoaded", function() {
    createToastContainer();
    highlightActiveSidebar();
    if (!window.location.pathname.includes('/accounts/')) loadCurrentUser();

    document.addEventListener('click', event => {
        const popup = document.getElementById('userPopup');
        if (popup && !event.target.closest('.user-popup') && !event.target.closest('#userDisplay')) {
            popup.classList.remove('active');
        }
    });



    const currentPath = window.location.pathname;
    const currentPage = currentPath.split("/").filter(Boolean).pop();

    if (!currentPage || currentPath === '/') return;

    // Skip API calls on login page
    if (currentPath.includes('/accounts/')) return;

    // Fetch currency from DB first, then load page â€” avoids symbol flicker
    fetch('/api/settings/', { headers: getAuthHeaders(false) })
        .then(r => r.json())
        .then(data => applyCurrencyFromSettings(data))
        .catch(() => {})
        .finally(() => {
            if      (currentPage.includes("dashboard"))    loadDashboard();
            else if (currentPage.includes("booking"))      loadBookings();
            else if (currentPage.includes("rooms"))        loadRooms();
            else if (currentPage.includes("customers"))    loadCustomers();
            else if (currentPage.includes("payments"))     loadPayments();
            else if (currentPage.includes("settings"))     loadSettings();
            else if (currentPage.includes("users"))        loadUsers();
            else if (currentPage.includes("housekeeping")) loadHousekeeping();
            else if (currentPage.includes("complaints"))   loadComplaints();
            else if (currentPage.includes("maintenance"))  loadMaintenance();
            else if (currentPage.includes("staff"))        loadStaff();
            else if (currentPage.includes("services"))     loadServices();
            else if (currentPage.includes("reviews"))      loadReviews();
        });
});


/* ================= PAYMENT MODAL ================= */
let currentPaymentId = null;
let currentPaymentAmount = 0;
let currentPaymentGuest = '';
let selectedGateway = '';

function openPaymentModal(paymentId, amount, guestName) {
    currentPaymentId = paymentId;
    currentPaymentAmount = parseFloat(amount);
    currentPaymentGuest = guestName;
    selectedGateway = '';

    document.getElementById('payStep1').style.display = 'block';
    document.getElementById('payStep2Cash').style.display = 'none';
    document.getElementById('payStep2Online').style.display = 'none';
    document.getElementById('payStep3Receipt').style.display = 'none';

    const infoHtml = `<strong>${guestName}</strong> &nbsp;|&nbsp; Amount: <strong>${formatCurrency(amount)}</strong>`;
    document.getElementById('payInfoBar').innerHTML = infoHtml;

    document.getElementById('paymentModal').classList.add('active');
}

function closePaymentModal() {
    document.getElementById('paymentModal').classList.remove('active');
    loadPayments();
}

function selectMethod(method) {
    document.getElementById('payStep1').style.display = 'none';
    if (method === 'cash') {
        document.getElementById('payStep2Cash').style.display = 'block';
        document.getElementById('cashAmountDue').textContent = formatCurrency(currentPaymentAmount);
        document.getElementById('payInfoBarCash').innerHTML =
            `<strong>${currentPaymentGuest}</strong> &nbsp;|&nbsp; Amount Due: <strong>${formatCurrency(currentPaymentAmount)}</strong>`;
        document.getElementById('cashReceived').value = '';
        document.getElementById('changeDisplay').style.display = 'none';
        document.getElementById('confirmCashBtn').disabled = true;
    } else {
        document.getElementById('payStep2Online').style.display = 'block';
        document.getElementById('payInfoBarOnline').innerHTML =
            `<strong>${currentPaymentGuest}</strong> &nbsp;|&nbsp; Amount: <strong>${formatCurrency(currentPaymentAmount)}</strong>`;
        document.querySelectorAll('.gateway-card').forEach(c => c.classList.remove('selected'));
        document.getElementById('transactionSection').style.display = 'none';
        document.getElementById('confirmOnlineBtn').disabled = true;
        selectedGateway = '';
    }
}

function goBackToStep1() {
    document.getElementById('payStep2Cash').style.display = 'none';
    document.getElementById('payStep2Online').style.display = 'none';
    document.getElementById('payStep1').style.display = 'block';
}



function calculateChange() {
    const received = parseFloat(document.getElementById('cashReceived').value) || 0;
    const due = currentPaymentAmount;
    const change = received - due;

    document.getElementById('changeDisplay').style.display = 'block';
    document.getElementById('changeDue').textContent = formatCurrency(due);
    document.getElementById('changeReceived').textContent = formatCurrency(received);

    if (change >= 0) {
        document.getElementById('changeReturn').textContent = formatCurrency(change);
        document.getElementById('changeReturn').style.color = 'var(--green)';
        document.getElementById('confirmCashBtn').disabled = false;
    } else {
        document.getElementById('changeReturn').textContent = `${formatCurrency(Math.abs(change))} short`;
        document.getElementById('changeReturn').style.color = 'var(--red)';
        document.getElementById('confirmCashBtn').disabled = true;
    }
}

function selectGateway(name) {
    selectedGateway = name;
    document.querySelectorAll('.gateway-card').forEach(c => {
        c.classList.toggle('selected', c.dataset.gw === name);
    });
    document.getElementById('transactionSection').style.display = 'block';
    document.getElementById('transactionId').value = '';
    document.getElementById('confirmOnlineBtn').disabled = true;

    // Hint per gateway
    const hints = {
        'eSewa': 'e.g. ESW-XXXXXXXXXX (from eSewa app transaction history)',
        'Khalti': 'e.g. KHL-XXXXXXXXXX (from Khalti transaction details)',
        'IME Pay': 'e.g. IME-XXXXXXXXXX (from IME Pay receipt)',
        'Fonepay': 'e.g. FPY-XXXXXXXXXX (from Fonepay confirmation SMS)',
        'ConnectIPS': 'e.g. CPS-XXXXXXXXXX (from ConnectIPS reference)',
        'nPay': 'e.g. NPY-XXXXXXXXXX (from nPay transaction ID)',
        'NIC Asia Bank': 'Enter bank reference / UTR number',
        'Nabil Bank': 'Enter bank reference / UTR number',
        'Global IME Bank': 'Enter bank reference / UTR number',
        'Everest Bank': 'Enter bank reference / UTR number',
        'Kumari Bank': 'Enter bank reference / UTR number',
        'Sanima Bank': 'Enter bank reference / UTR number',
    };
    document.getElementById('txnHint').textContent = hints[name] || 'Enter transaction reference number';
}

function validateTransactionId() {
    const val = document.getElementById('transactionId').value.trim();
    document.getElementById('confirmOnlineBtn').disabled = val.length < 5;
}

function confirmCashPayment() {
    processPayment('Cash', null);
}

function confirmOnlinePayment() {
    const txnId = document.getElementById('transactionId').value.trim();
    if (!txnId) { showToast('Please enter transaction ID', 'error'); return; }
    processPayment(selectedGateway, txnId);
}

function processPayment(method, txnId) {
    const btn = method === 'Cash'
        ? document.getElementById('confirmCashBtn')
        : document.getElementById('confirmOnlineBtn');
    btn.disabled = true;
    btn.textContent = 'Processing...';

    fetch(`/api/payments/${currentPaymentId}/process_payment/`, {
        method: 'POST',
        headers: getAuthHeaders(true),
        body: JSON.stringify({ method, transaction_id: txnId })
    })
    .then(r => r.json())
    .then(data => {
        if (data.status || data.booking_status) {
            showReceipt(method, txnId);
            loadPayments();
        } else {
            showToast(data.error || 'Payment failed', 'error');
            btn.disabled = false;
            btn.textContent = 'âœ“ Confirm Payment';
        }
    })
    .catch(() => {
        showToast('Server error. Please try again.', 'error');
        btn.disabled = false;
        btn.textContent = 'âœ“ Confirm Payment';
    });
}

function showReceipt(method, txnId) {
    document.getElementById('payStep2Cash').style.display = 'none';
    document.getElementById('payStep2Online').style.display = 'none';
    document.getElementById('payStep3Receipt').style.display = 'block';

    const now = new Date();
    document.getElementById('receiptDate').textContent =
        now.toLocaleDateString('en-NP', { year: 'numeric', month: 'long', day: 'numeric' }) +
        ' ' + now.toLocaleTimeString('en-NP', { hour: '2-digit', minute: '2-digit' });

    document.getElementById('rGuestName').textContent = currentPaymentGuest;
    document.getElementById('rPaymentId').textContent = '#' + currentPaymentId;
    document.getElementById('rMethod').textContent = method;
    document.getElementById('rAmount').textContent = formatCurrency(currentPaymentAmount);

    if (txnId) {
        document.getElementById('rTxnRow').style.display = 'flex';
        document.getElementById('rTxnId').textContent = txnId;
    } else {
        document.getElementById('rTxnRow').style.display = 'none';
    }
}

function printReceipt() {
    const receiptHtml = document.getElementById('receiptContent').outerHTML;
    const win = window.open('', '_blank', 'width=400,height=600');
    win.document.write(`
        <!DOCTYPE html><html><head>
        <title>Payment Receipt</title>
        <style>
            body { font-family: Inter, sans-serif; padding: 20px; background: #fff; color: #1a1a1a; }
            .receipt-box { max-width: 340px; margin: 0 auto; }
            .receipt-header { text-align: center; margin-bottom: 12px; }
            .receipt-logo { font-size: 20px; font-weight: 700; }
            .receipt-title { font-size: 13px; font-weight: 600; margin-top: 4px; }
            .receipt-subtitle { font-size: 11px; color: #888; }
            .receipt-divider { border-top: 1px dashed #ccc; margin: 10px 0; }
            .receipt-row { display: flex; justify-content: space-between; font-size: 13px; padding: 3px 0; }
            .receipt-row span:first-child { color: #666; }
            .receipt-total { font-size: 15px; font-weight: 700; }
            .receipt-status { text-align: center; font-weight: 700; color: #059669; margin: 10px 0 4px; }
            .receipt-footer { text-align: center; font-size: 11px; color: #888; }
        </style></head><body>
        ${receiptHtml}
        </body></html>
    `);
    win.document.close();
    win.focus();
    setTimeout(() => { win.print(); win.close(); }, 400);
}

// Only fetch hotel name when logged in (not on login page)
if (!window.location.pathname.includes('/accounts/')) {
    fetch('/api/settings/', { headers: getAuthHeaders(false) })
        .then(response => response.json())
        .then(data => {
            const logo = document.getElementsByClassName('logo')[0];
            const header = document.getElementsByClassName('header')[0];
            if (logo)   logo.innerText   = data.hotelName || 'Hotel Admin';
            if (header) header.innerText = (data.hotelName || 'Hotel Admin') + ' ' + (document.title || '');
        })
        .catch(() => {});
}




/* ═══════════════════════════════════════════════════════════════
 * HOUSEKEEPING FUNCTIONS
 * ═══════════════════════════════════════════════════════════════ */

var _currentHousekeepingFilter = '';

function loadHousekeeping() {
    loadCurrencyGlobal();
    const url = _currentHousekeepingFilter
        ? '/api/cleaning/?status=' + encodeURIComponent(_currentHousekeepingFilter)
        : '/api/cleaning/';

    const tbody = document.getElementById('cleaningTableBody');
    if (tbody) tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;">Loading...</td></tr>';

    fetch(url, { headers: getAuthHeaders(false) })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            const s = data.summary || {};
            const pendingEl        = document.getElementById('pendingCount');
            const inProgressEl     = document.getElementById('inProgressCount');
            const completedTodayEl = document.getElementById('completedTodayCount');
            if (pendingEl)        pendingEl.textContent        = s.pending         || 0;
            if (inProgressEl)     inProgressEl.textContent     = s.in_progress     || 0;
            if (completedTodayEl) completedTodayEl.textContent = s.completed_today || 0;
            populateCleaningTable(data.cleaning_tasks || []);
        })
        .catch(function() {
            if (tbody) tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:var(--red);">Failed to load cleaning tasks</td></tr>';
            showToast('Failed to load housekeeping data', 'error');
        });
}

function filterHousekeeping(status) {
    _currentHousekeepingFilter = status;
    ['filterAll','filterPending','filterProgress','filterCompleted'].forEach(function(id) {
        const el = document.getElementById(id);
        if (el) el.style.opacity = '0.55';
    });
    const activeMap = {
        '':            'filterAll',
        'Pending':     'filterPending',
        'In Progress': 'filterProgress',
        'Completed':   'filterCompleted'
    };
    const activeEl = document.getElementById(activeMap[status]);
    if (activeEl) activeEl.style.opacity = '1';
    loadHousekeeping();
}

function populateCleaningTable(tasks) {
    const tbody = document.getElementById('cleaningTableBody');
    if (!tbody) return;

    if (!tasks.length) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;opacity:.6;">No cleaning tasks found</td></tr>';
        return;
    }

    let html = '';
    tasks.forEach(function(task) {
        const statusClass = task.status === 'Completed'   ? 'completed'
                          : task.status === 'In Progress' ? 'in-progress'
                          : 'pending';

        const statusBadge = '<span class="status-badge ' + statusClass + '">' + task.status + '</span>';

        let actions = '';
        if (task.status === 'Pending') {
            actions  = '<button type="button" style="width:auto;padding:6px 10px;background:linear-gradient(135deg,#2563eb,#1d4ed8);" onclick="openNotesModal(' + task.id + ',\'In Progress\',\'Room ' + task.room_number + '\')">🔄 Start</button>';
            actions += '<button type="button" style="width:auto;padding:6px 10px;background:linear-gradient(135deg,#059669,#047857);margin-left:4px;" onclick="openNotesModal(' + task.id + ',\'Completed\',\'Room ' + task.room_number + '\')">✅ Done</button>';
        } else if (task.status === 'In Progress') {
            actions = '<button type="button" style="width:auto;padding:6px 10px;background:linear-gradient(135deg,#059669,#047857);" onclick="openNotesModal(' + task.id + ',\'Completed\',\'Room ' + task.room_number + '\')">✅ Mark Done</button>';
        } else {
            actions = '<span style="opacity:.5;font-size:12px;">—</span>';
        }

        const startedTime   = task.started_at   ? '<br><small style="color:var(--blue);">Started: '  + task.started_at   + '</small>' : '';
        const completedTime = task.completed_at  ? '<br><small style="color:var(--green);">Done: '    + task.completed_at + '</small>' : '';

        html += '<tr>'
            + '<td><strong>' + task.room_number + '</strong></td>'
            + '<td>' + task.room_type + '</td>'
            + '<td>Floor ' + task.floor + '</td>'
            + '<td>' + (task.guest_name || '—') + '</td>'
            + '<td style="font-size:12px;">' + task.created_at + startedTime + completedTime + '</td>'
            + '<td>' + statusBadge + '</td>'
            + '<td style="font-size:12px;max-width:160px;word-wrap:break-word;">' + (task.notes || '<span style="opacity:.4;">—</span>') + '</td>'
            + '<td>' + actions + '</td>'
            + '</tr>';
    });

    tbody.innerHTML = html;
}

function openNotesModal(cleaningId, targetStatus, roomLabel) {
    document.getElementById('notesCleaningId').value   = cleaningId;
    document.getElementById('notesTargetStatus').value = targetStatus;
    document.getElementById('notesModalSubtitle').textContent =
        targetStatus === 'In Progress'
            ? 'Start cleaning for ' + roomLabel
            : 'Mark ' + roomLabel + ' as Done';
    document.getElementById('cleaningNotes').value = '';

    const confirmBtn = document.getElementById('notesConfirmBtn');
    if (confirmBtn) {
        confirmBtn.style.background = targetStatus === 'Completed'
            ? 'linear-gradient(135deg,#059669,#047857)'
            : 'linear-gradient(135deg,#2563eb,#1d4ed8)';
        confirmBtn.textContent = targetStatus === 'Completed' ? '✅ Mark Done' : '🔄 Start Cleaning';
    }

    const modal = document.getElementById('notesModal');
    requestAnimationFrame(function() { modal.classList.add('active'); });
}

function closeNotesModal() {
    const modal = document.getElementById('notesModal');
    if (!modal) return;
    modal.classList.remove('active');
}

function confirmStatusUpdate() {
    const cleaningId   = document.getElementById('notesCleaningId').value;
    const targetStatus = document.getElementById('notesTargetStatus').value;
    const notes        = document.getElementById('cleaningNotes').value.trim();

    if (!cleaningId || !targetStatus) return;

    fetch('/api/cleaning/' + cleaningId + '/update/', {
        method: 'POST',
        headers: getAuthHeaders(true),
        body: JSON.stringify({ status: targetStatus, notes: notes })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.status === 'ok') {
            closeNotesModal();
            showToast(targetStatus === 'Completed' ? '✅ Room marked clean — now Available' : '🔄 Cleaning started', 'success');
            loadHousekeeping();
        } else {
            showToast(data.error || 'Failed to update status', 'error');
        }
    })
    .catch(function() { showToast('Server error', 'error'); });
}


/* ═══════════════════════════════════════════════════════════════
 * COMPLAINTS PAGE
 * ═══════════════════════════════════════════════════════════════ */

function loadComplaints(statusFilter) {
    var url = '/api/complaints-data/';
    if (statusFilter) url += '?status=' + encodeURIComponent(statusFilter);
    var tbody = document.getElementById('complaintsTableBody');
    if (tbody) tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;">Loading...</td></tr>';

    fetch(url, { headers: getAuthHeaders(false) })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var e = function(id, val) { var el = document.getElementById(id); if (el) el.textContent = val; };
            e('cntOpen',       data.open       || 0);
            e('cntInProgress', data.in_progress || 0);
            e('cntResolved',   data.resolved    || 0);
            e('cntTotal',      data.total       || 0);
            populateComplaintsTable(data.complaints || []);
        })
        .catch(function() { showToast('Failed to load complaints', 'error'); });
}

function populateComplaintsTable(list) {
    var tbody = document.getElementById('complaintsTableBody');
    if (!tbody) return;
    if (!list.length) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;opacity:.6;">No complaints found</td></tr>';
        return;
    }
    var statusColors = { 'Open': 'var(--orange)', 'In Progress': 'var(--blue)', 'Resolved': 'var(--green)', 'Closed': 'var(--muted)' };
    var html = '';
    list.forEach(function(c) {
        var color = statusColors[c.status] || 'var(--muted)';
        var badge = '<span style="color:' + color + ';font-weight:600;">' + c.status + '</span>';
        html += '<tr>'
            + '<td>' + (c.booking_id || '—') + '</td>'
            + '<td>' + (c.guest_name || '—') + '</td>'
            + '<td>' + c.complaint_type + '</td>'
            + '<td style="max-width:200px;word-wrap:break-word;font-size:12px;">' + (c.description || '') + '</td>'
            + '<td>' + badge + '</td>'
            + '<td style="font-size:12px;">' + (c.created_at || '') + '</td>'
            + '<td><button type="button" class="secondary" style="width:auto;padding:6px 10px;" onclick="openResolveModal(' + c.id + ',\'' + c.status + '\',\'' + (c.resolution || '').replace(/'/g, '') + '\')">Update</button></td>'
            + '</tr>';
    });
    tbody.innerHTML = html;
}

function submitComplaint() {
    var bookingId = (document.getElementById('newBookingId') || {}).value || '';
    var type      = (document.getElementById('newComplaintType') || {}).value || '';
    var desc      = (document.getElementById('newComplaintDesc') || {}).value || '';
    if (!bookingId || !desc) { showToast('Booking ID and description are required', 'error'); return; }
    fetch('/api/complaints/create/', {
        method: 'POST', headers: getAuthHeaders(true),
        body: JSON.stringify({ booking_id: bookingId, complaint_type: type, description: desc })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.id) {
            showToast('✅ Complaint logged', 'success');
            document.getElementById('newBookingId').value = '';
            document.getElementById('newComplaintDesc').value = '';
            loadComplaints();
        } else { showToast(data.error || 'Failed to create', 'error'); }
    })
    .catch(function() { showToast('Server error', 'error'); });
}

function openResolveModal(id, currentStatus, currentResolution) {
    document.getElementById('resolveComplaintId').value = id;
    document.getElementById('resolveStatus').value = currentStatus;
    document.getElementById('resolveText').value = currentResolution || '';
    document.getElementById('resolveModalSubtitle').textContent = 'Complaint #' + id;
    document.getElementById('resolveModal').classList.add('active');
}

function closeResolveModal() {
    document.getElementById('resolveModal').classList.remove('active');
}

function saveComplaintUpdate() {
    var id         = document.getElementById('resolveComplaintId').value;
    var newStatus  = document.getElementById('resolveStatus').value;
    var resolution = document.getElementById('resolveText').value;
    fetch('/api/complaints/' + id + '/update/', {
        method: 'POST', headers: getAuthHeaders(true),
        body: JSON.stringify({ status: newStatus, resolution: resolution })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.status === 'ok') {
            closeResolveModal();
            showToast('✅ Complaint updated', 'success');
            loadComplaints();
        } else { showToast(data.error || 'Failed', 'error'); }
    })
    .catch(function() { showToast('Server error', 'error'); });
}


/* ═══════════════════════════════════════════════════════════════
 * MAINTENANCE PAGE
 * ═══════════════════════════════════════════════════════════════ */

function loadMaintenance(statusFilter) {
    var url = '/api/maintenance-data/';
    if (statusFilter) url += '?status=' + encodeURIComponent(statusFilter);
    var tbody = document.getElementById('maintenanceTableBody');
    if (tbody) tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;">Loading...</td></tr>';

    fetch(url, { headers: getAuthHeaders(false) })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var e = function(id, val) { var el = document.getElementById(id); if (el) el.textContent = val; };
            e('mntOpen',       data.open        || 0);
            e('mntInProgress', data.in_progress || 0);
            e('mntCompleted',  data.completed   || 0);
            e('mntUrgent',     data.urgent      || 0);
            populateMaintenanceTable(data.requests || []);
        })
        .catch(function() { showToast('Failed to load maintenance data', 'error'); });
}

function populateMaintenanceTable(list) {
    var tbody = document.getElementById('maintenanceTableBody');
    if (!tbody) return;
    if (!list.length) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;opacity:.6;">No maintenance requests</td></tr>';
        return;
    }
    var priorityColors = { 'Low': 'var(--muted)', 'Medium': 'var(--blue)', 'High': 'var(--orange)', 'Urgent': 'var(--red)' };
    var statusColors   = { 'Open': 'var(--orange)', 'In Progress': 'var(--blue)', 'Completed': 'var(--green)', 'Cancelled': 'var(--muted)' };
    var html = '';
    list.forEach(function(m) {
        var pColor = priorityColors[m.priority] || 'var(--muted)';
        var sColor = statusColors[m.status]   || 'var(--muted)';
        var actions = (m.status !== 'Completed' && m.status !== 'Cancelled')
            ? '<button type="button" class="secondary" style="width:auto;padding:6px 10px;" onclick="openMntModal(' + m.id + ',\'' + m.status + '\',\'Room ' + m.room_number + '\')">Update</button>'
            : '<span style="opacity:.4;font-size:12px;">—</span>';
        html += '<tr>'
            + '<td><strong>' + m.room_number + '</strong></td>'
            + '<td style="font-size:12px;">' + (m.room_type || '') + '<br>Floor ' + m.floor + '</td>'
            + '<td><span style="color:' + pColor + ';font-weight:600;">' + m.priority + '</span></td>'
            + '<td style="max-width:180px;word-wrap:break-word;font-size:12px;">' + (m.description || '') + '</td>'
            + '<td><span style="color:' + sColor + ';font-weight:600;">' + m.status + '</span></td>'
            + '<td style="font-size:12px;">' + (m.created_at || '') + (m.completed_at ? '<br><small style="color:var(--green);">Done: ' + m.completed_at + '</small>' : '') + '</td>'
            + '<td>' + actions + '</td>'
            + '</tr>';
    });
    tbody.innerHTML = html;
}

function submitMaintenance() {
    var roomNum = (document.getElementById('mntRoomNumber') || {}).value || '';
    var priority = (document.getElementById('mntPriority') || {}).value || 'Medium';
    var desc = (document.getElementById('mntDescription') || {}).value || '';
    var markRoom = document.getElementById('mntMarkRoom') ? document.getElementById('mntMarkRoom').checked : false;
    if (!roomNum || !desc) { showToast('Room number and description are required', 'error'); return; }
    fetch('/api/maintenance/create/', {
        method: 'POST', headers: getAuthHeaders(true),
        body: JSON.stringify({ room_number: roomNum, priority: priority, description: desc, mark_room: markRoom })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.id) {
            showToast('✅ Maintenance request created', 'success');
            document.getElementById('mntRoomNumber').value = '';
            document.getElementById('mntDescription').value = '';
            loadMaintenance();
        } else { showToast(data.error || 'Failed', 'error'); }
    })
    .catch(function() { showToast('Server error', 'error'); });
}

function openMntModal(id, currentStatus, label) {
    document.getElementById('mntReqId').value = id;
    document.getElementById('mntNewStatus').value = currentStatus;
    document.getElementById('mntModalSubtitle').textContent = label + ' — Request #' + id;
    document.getElementById('mntModal').classList.add('active');
}

function closeMntModal() {
    document.getElementById('mntModal').classList.remove('active');
}

function saveMntUpdate() {
    var id = document.getElementById('mntReqId').value;
    var newStatus = document.getElementById('mntNewStatus').value;
    fetch('/api/maintenance/' + id + '/update/', {
        method: 'POST', headers: getAuthHeaders(true),
        body: JSON.stringify({ status: newStatus })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.status === 'ok') {
            closeMntModal();
            showToast('✅ Request updated to ' + data.request_status, 'success');
            loadMaintenance();
        } else { showToast(data.error || 'Failed', 'error'); }
    })
    .catch(function() { showToast('Server error', 'error'); });
}


/* ═══════════════════════════════════════════════════════════════
 * STAFF PAGE
 * ═══════════════════════════════════════════════════════════════ */

var _allStaff = [];

function loadStaff() {
    fetch('/api/staff-data/', { headers: getAuthHeaders(false) })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var e = function(id, val) { var el = document.getElementById(id); if (el) el.textContent = val; };
            e('staffTotal',    data.total    || 0);
            e('staffActive',   data.active   || 0);
            e('staffInactive', data.inactive || 0);
            _allStaff = data.staff || [];
            populateStaffTable(_allStaff);
        })
        .catch(function() { showToast('Failed to load staff', 'error'); });
}

function populateStaffTable(list) {
    var tbody = document.getElementById('staffTableBody');
    if (!tbody) return;
    if (!list.length) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;opacity:.6;">No staff found</td></tr>';
        return;
    }
    var html = '';
    list.forEach(function(s) {
        var statusBadge = s.is_active
            ? '<span style="color:var(--green);font-weight:600;">Active</span>'
            : '<span style="color:var(--muted);font-weight:600;">Inactive</span>';
        html += '<tr>'
            + '<td>' + (s.name || '') + '<br><small style="opacity:.6;">' + s.email + '</small></td>'
            + '<td>' + s.employee_id + '</td>'
            + '<td>' + s.position + '</td>'
            + '<td>' + (s.department || '—') + '</td>'
            + '<td>' + s.shift + '</td>'
            + '<td>' + s.phone + '</td>'
            + '<td style="font-size:12px;">' + s.hire_date + '</td>'
            + '<td>' + statusBadge + '</td>'
            + '</tr>';
    });
    tbody.innerHTML = html;
}

function filterStaffTable() {
    var q = (document.getElementById('staffSearch') || {}).value || '';
    q = q.toLowerCase();
    if (!q) { populateStaffTable(_allStaff); return; }
    var filtered = _allStaff.filter(function(s) {
        return (s.name || '').toLowerCase().includes(q)
            || (s.position || '').toLowerCase().includes(q)
            || (s.department || '').toLowerCase().includes(q);
    });
    populateStaffTable(filtered);
}


/* ═══════════════════════════════════════════════════════════════
 * SERVICES PAGE
 * ═══════════════════════════════════════════════════════════════ */

function loadServices() {
    loadCurrencyGlobal();
    fetch('/api/services-data/', { headers: getAuthHeaders(false) })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var e = function(id, val) { var el = document.getElementById(id); if (el) el.textContent = val; };
            e('svcTotal',     data.total     || 0);
            e('svcAvailable', data.available || 0);
            populateServicesTable(data.services || []);
        })
        .catch(function() { showToast('Failed to load services', 'error'); });
}

function populateServicesTable(list) {
    var tbody = document.getElementById('servicesTableBody');
    if (!tbody) return;
    if (!list.length) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;opacity:.6;">No services found</td></tr>';
        return;
    }
    // detect if edit column should show (check DOM for an edit button header)
    var html = '';
    list.forEach(function(s) {
        var avail = s.is_available
            ? '<span style="color:var(--green);font-weight:600;">Available</span>'
            : '<span style="color:var(--red);font-weight:600;">Unavailable</span>';
        var editBtn = '<button type="button" class="secondary" style="width:auto;padding:6px 10px;" onclick="openEditSvcModal(' + s.id + ')">Edit</button>';
        html += '<tr>'
            + '<td><strong>' + s.name + '</strong></td>'
            + '<td>' + s.service_type + '</td>'
            + '<td style="font-size:12px;max-width:160px;word-wrap:break-word;">' + (s.description || '') + '</td>'
            + '<td>' + formatCurrency(s.price) + '</td>'
            + '<td>' + avail + '</td>'
            + '<td>' + editBtn + '</td>'
            + '</tr>';
    });
    tbody.innerHTML = html;
}

function submitService() {
    var name  = (document.getElementById('svcName')  || {}).value || '';
    var type  = (document.getElementById('svcType')  || {}).value || 'Other';
    var price = (document.getElementById('svcPrice') || {}).value || '0';
    var desc  = (document.getElementById('svcDescription') || {}).value || '';
    var avail = document.getElementById('svcAvailableCheck') ? document.getElementById('svcAvailableCheck').checked : true;
    if (!name || !price) { showToast('Name and price are required', 'error'); return; }
    fetch('/api/services/create/', {
        method: 'POST', headers: getAuthHeaders(true),
        body: JSON.stringify({ name: name, service_type: type, price: parseFloat(price), description: desc, is_available: avail })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.id) {
            showToast('✅ Service added', 'success');
            document.getElementById('svcName').value = '';
            document.getElementById('svcPrice').value = '';
            document.getElementById('svcDescription').value = '';
            loadServices();
        } else { showToast(data.error || 'Failed', 'error'); }
    })
    .catch(function() { showToast('Server error', 'error'); });
}

function openEditSvcModal(serviceId) {
    fetch('/api/services/' + serviceId + '/', { headers: getAuthHeaders(false) })
        .then(function(r) { return r.json(); })
        .then(function(s) {
            document.getElementById('editSvcId').value    = s.id;
            document.getElementById('editSvcName').value  = s.name;
            document.getElementById('editSvcType').value  = s.service_type;
            document.getElementById('editSvcPrice').value = s.price;
            document.getElementById('editSvcDesc').value  = s.description || '';
            document.getElementById('editSvcAvailable').checked = s.is_available;
            document.getElementById('editSvcModal').classList.add('active');
        })
        .catch(function() { showToast('Failed to load service', 'error'); });
}

function closeEditSvcModal() {
    document.getElementById('editSvcModal').classList.remove('active');
}

function saveServiceEdit() {
    var id    = document.getElementById('editSvcId').value;
    var name  = document.getElementById('editSvcName').value;
    var type  = document.getElementById('editSvcType').value;
    var price = document.getElementById('editSvcPrice').value;
    var desc  = document.getElementById('editSvcDesc').value;
    var avail = document.getElementById('editSvcAvailable').checked;
    fetch('/api/services/' + id + '/update/', {
        method: 'POST', headers: getAuthHeaders(true),
        body: JSON.stringify({ name: name, service_type: type, price: parseFloat(price), description: desc, is_available: avail })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.status === 'ok') {
            closeEditSvcModal();
            showToast('✅ Service updated', 'success');
            loadServices();
        } else { showToast(data.error || 'Failed', 'error'); }
    })
    .catch(function() { showToast('Server error', 'error'); });
}


/* ═══════════════════════════════════════════════════════════════
 * REVIEWS PAGE
 * ═══════════════════════════════════════════════════════════════ */

function loadReviews() {
    fetch('/api/reviews-data/', { headers: getAuthHeaders(false) })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var e = function(id, val) { var el = document.getElementById(id); if (el) el.textContent = val; };
            e('revTotal',        data.total          || 0);
            e('revAvgRating',    data.avg_rating      || '—');
            e('revRecommendPct', (data.recommend_pct || 0) + '%');
            e('avgOverall',      data.avg_rating      || '—');
            e('avgCleanliness',  data.avg_cleanliness || '—');
            e('avgService',      data.avg_service     || '—');
            e('avgFood',         data.avg_food        || '—');
            populateReviewsTable(data.reviews || []);
        })
        .catch(function() { showToast('Failed to load reviews', 'error'); });
}

function populateReviewsTable(list) {
    var tbody = document.getElementById('reviewsTableBody');
    if (!tbody) return;
    if (!list.length) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;opacity:.6;">No reviews yet</td></tr>';
        return;
    }
    function stars(n) {
        var s = '';
        for (var i = 1; i <= 5; i++) s += (i <= n ? '★' : '☆');
        return '<span style="color:var(--yellow);">' + s + '</span> ' + n;
    }
    var html = '';
    list.forEach(function(r) {
        var rec = r.would_recommend
            ? '<span style="color:var(--green);">✓ Yes</span>'
            : '<span style="color:var(--red);">✗ No</span>';
        html += '<tr>'
            + '<td>' + (r.guest_name || '—') + '</td>'
            + '<td style="font-size:12px;">' + r.booking_id + '</td>'
            + '<td>' + stars(r.rating) + '</td>'
            + '<td>' + stars(r.cleanliness) + '</td>'
            + '<td>' + stars(r.service) + '</td>'
            + '<td>' + stars(r.food) + '</td>'
            + '<td>' + rec + '</td>'
            + '<td style="font-size:12px;max-width:160px;word-wrap:break-word;">' + (r.comment || '—') + '</td>'
            + '<td style="font-size:12px;">' + (r.reviewed_at || '') + '</td>'
            + '</tr>';
    });
    tbody.innerHTML = html;
}
