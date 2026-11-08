# BarberLink

A booking app for home-visit barbers. Barbers manage their week and prices; customers find a barber nearby, book a time, and the barber comes to their home.

## Features

**Barber**
- Weekly slot view with prices set by the barber
- Approve or decline booking requests, mark visits as completed
- Customer details and one-tap directions to their home (Google Maps)
- 1-year free trial, then renewal through Razorpay

**Customer**
- Find barbers within ~5-6 km using browser location
- See live availability and book a time
- Cancel a booking while it is waiting or approved

**General**
- Double-booking protection: only one booking can win a slot
- JWT login (phone number + password)
- Automatic cleanup of old slots
- English and Kannada interface

## Tech Stack

Django, Django REST Framework, SimpleJWT, SQLite, Razorpay

## Installation

**Prerequisites:** Python 3.11+, Git

```bash
# 1. Clone the repository
git clone https://github.com/sristiacharya13/BarberLink.git
cd barberlink

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create a .env file in the project root (see below)

# 5. Apply migrations
python manage.py migrate

# 6. (Optional) Create an admin user
python manage.py createsuperuser

# 7. Run the server
python manage.py runserver
```

Open http://127.0.0.1:8000/

### Environment variables (`.env`)

```
SECRET_KEY=your-django-secret-key
DEBUG=True
RAZORPAY_KEY_ID=rzp_test_xxxxxxxx
RAZORPAY_KEY_SECRET=your-razorpay-secret
```

Use Razorpay **test** keys while developing. Never commit `.env`.

## API Documentation

Full API docs are in a separate repository: **[BarberLink API Docs](https://github.com/sristiacharya13/barberlink-api-docs)**

## Authors

Built by [Sristi Acharya](https://github.com/sristiacharya13) and [Pranav Nayak](https://github.com/pranav-archi)
