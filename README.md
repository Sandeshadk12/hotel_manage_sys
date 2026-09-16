# Hotel Management System

A Django-based hotel management system with a REST API backend and HTML/CSS/JS frontend.

## Project Structure

```
Hotel_clean/
├── HotelManagementSystem/       # Django project root
│   ├── manage.py
│   ├── db.sqlite3
│   ├── HotelManagementSystem/   # Django settings package
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── resultapp/               # Main app (models, views, API)
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── forms.py
│   │   ├── migrations/
│   │   └── management/commands/
│   │       ├── init_hotel.py    # Seed initial hotel data
│   │       └── seed.py          # Seed sample data
│   └── accounts/                # Authentication app
│       ├── models.py
│       ├── views.py
│       └── urls.py
├── templates/                   # HTML templates
│   ├── accounts/
│   ├── dashboard/
│   ├── booking/
│   ├── rooms/
│   ├── customers/
│   ├── payments/
│   └── settings/
├── static/                      # CSS, JS, images
├── requirements.txt
└── .gitignore
```

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy and configure environment variables
cp HotelManagementSystem/.env.example HotelManagementSystem/.env
# Edit .env and set a strong SECRET_KEY

# 4. Apply migrations
cd HotelManagementSystem
python manage.py migrate

# 5. Seed initial hotel data
python manage.py init_hotel

# 6. Create a superuser
python manage.py createsuperuser

# 7. Run the development server
python manage.py runserver
```

Visit http://127.0.0.1:8000 — you will be redirected to the login page.

## Key URLs

| URL | Description |
|-----|-------------|
| `/` | Redirects to dashboard or login |
| `/accounts/login/` | Login page |
| `/accounts/register/` | Registration (JSON POST) |
| `/dashboard/` | Dashboard |
| `/booking/` | Bookings |
| `/rooms/` | Rooms |
| `/customers/` | Customers |
| `/payments/` | Payments |
| `/settings/` | Hotel settings |
| `/admin/` | Django admin |

## API Endpoints

All API endpoints require session authentication.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/dashboard/` | GET | Dashboard stats |
| `/api/bookings/add/` | POST | Create booking |
| `/api/rooms/add/` | POST | Add room |
| `/api/rooms/bulk-add/` | POST | Bulk add rooms |
| `/api/customers/` | GET | Customer list |
| `/api/payments-summary/` | GET | Payment summary |
| `/api/settings/` | GET/POST | Hotel settings |
| `/api/` | — | DRF browsable API (ViewSets) |
