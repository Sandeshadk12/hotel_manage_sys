web: cd HotelManagementSystem && python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn HotelManagementSystem.wsgi:application --bind 0.0.0.0:$PORT --workers 2
