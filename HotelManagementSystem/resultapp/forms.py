"""
DJANGO FORMS - Input validation and data collection

Forms handle data validation from user input.
They check if data is valid before saving to the database.

For beginners: Forms are like templates for collecting data from users.
They validate that the input makes sense (e.g., number is actually a number).
"""

from django import forms
from .models import Hotel, RoomType


class BulkRoomForm(forms.Form):
    """
    Form for creating multiple rooms at once
    
    This form collects information needed to create a batch of rooms:
    - Which hotel?
    - Room number range (e.g., 101-110)
    - What type of rooms?
    - What floor?
    - Price per night?
    
    Example Usage:
    If you want to create rooms 101-110, all Double rooms, 
    floor 1, at $90 per night, use this form.
    """

    # Which hotel to create rooms for?
    # This dropdown shows all hotels in the system
    hotel = forms.ModelChoiceField(
        queryset=Hotel.objects.all(),
        help_text="Select the hotel where rooms will be created"
    )

    # Starting room number (e.g., "101")
    start_room = forms.IntegerField(
        help_text="First room number to create (e.g., 101)",
        min_value=1,
        max_value=9999
    )

    # Ending room number (e.g., "110")
    end_room = forms.IntegerField(
        help_text="Last room number to create (e.g., 110)",
        min_value=1,
        max_value=9999
    )

    # What type of rooms? (Single, Double, Suite, etc.)
    # This dropdown shows all room types in the system
    room_type = forms.ModelChoiceField(
        queryset=RoomType.objects.all(),
        help_text="Select the type of rooms"
    )

    # Which floor are these rooms on?
    floor = forms.IntegerField(
        help_text="Floor number (e.g., 1 for first floor)",
        min_value=1,
        max_value=100
    )

    # How much per night for these rooms?
    price_per_night = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per night in dollars (e.g., 99.99)",
        min_value=0
    )