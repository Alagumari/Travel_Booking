# ✈️ TravelX Pro
### Advanced Tours & Travel Management System

> A production-level full-stack travel booking platform built with Django, Bootstrap 5, and MySQL.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- MySQL 8.0+
- pip

### 2. Clone / Extract Project
```bash
cd travelx_pro
```

### 3. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure MySQL Database
Open MySQL and run:
```sql
CREATE DATABASE travelx_pro_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'travelx_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON travelx_pro_db.* TO 'travelx_user'@'localhost';
FLUSH PRIVILEGES;
```

### 6. Configure Settings
Edit `travelx_pro/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'travelx_pro_db',
        'USER': 'travelx_user',       # ← your MySQL user
        'PASSWORD': 'your_password',   # ← your MySQL password
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# Razorpay
RAZORPAY_KEY_ID = 'rzp_test_XXXXXXXXXX'
RAZORPAY_KEY_SECRET = 'XXXXXXXXXXXXXXXXXX'

# Google Maps
GOOGLE_MAPS_API_KEY = 'AIzaXXXXXXXXXXXXXXXXXXXX'

# Email (Gmail SMTP)
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password'
```

### 7. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 8. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 9. Collect Static Files
```bash
python manage.py collectstatic
```

### 10. Seed Sample Data (Optional)
```bash
python manage.py shell
```
```python
from tours.models import Destination, TravelCategory, TourPackage

# Create a category
cat = TravelCategory.objects.create(name='Beach', icon='bi-umbrella-fill')

# Create a destination
dest = Destination.objects.create(
    name='Maldives', country='Maldives',
    description='Paradise on Earth',
    latitude=3.2028, longitude=73.2207,
    is_popular=True
)

# Create a package
TourPackage.objects.create(
    title='Maldives Luxury Escape',
    destination=dest, category=cat,
    description='7-day luxury water villa experience.',
    short_description='Luxury water villas, snorkeling, and sunsets.',
    highlights='Water villa\nSnorkeling\nSunset cruise\nAll-inclusive meals',
    price_per_person=89999,
    discount_percentage=10,
    duration_days=7, duration_nights=6,
    hotel_type='luxury', transport_type='flight',
    total_seats=20, available_seats=20,
    inclusions='Flights\nHotel\nMeals\nSnorkeling gear',
    exclusions='Visa\nPersonal expenses',
    is_active=True, is_featured=True, is_bestseller=True
)
print('Sample data created!')
```

### 11. Start Development Server
```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

---

## 📁 Project Structure

```
travelx_pro/
├── travelx_pro/          # Project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/             # User auth & profiles
│   ├── models.py         # UserProfile, Notification
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── tours/                # Tour packages & destinations
│   ├── models.py         # TourPackage, Destination, Review, Wishlist
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── bookings/             # Booking management
│   ├── models.py         # Booking, TravelerDetail
│   ├── views.py
│   └── urls.py
├── payments/             # Razorpay + PDF + QR
│   ├── models.py         # Payment
│   ├── views.py
│   └── urls.py
├── dashboard/            # User & admin dashboards
│   ├── views.py
│   └── urls.py
├── templates/            # All HTML templates
│   ├── base.html         # Master layout
│   ├── accounts/
│   ├── tours/
│   ├── bookings/
│   ├── payments/
│   └── dashboard/
├── static/
│   ├── css/main.css      # Custom styles
│   └── js/main.js        # Custom JS
├── media/                # User uploaded files
├── manage.py
└── requirements.txt
```

---

## 🔑 API Keys Setup

### Razorpay
1. Sign up at https://razorpay.com
2. Go to Settings → API Keys
3. Generate Key ID and Key Secret
4. Add to `settings.py`

### Google Maps
1. Go to https://console.cloud.google.com
2. Enable Maps Embed API and Maps JavaScript API
3. Create credentials → API Key
4. Add to `settings.py`

### Gmail SMTP (App Password)
1. Enable 2-Step Verification on Gmail
2. Go to Account → Security → App Passwords
3. Generate password for "Mail"
4. Add to `settings.py`

---

## 👤 User Roles

| Role | Access |
|------|--------|
| User | Browse, book, wishlist, dashboard |
| Staff/Admin | Full admin panel, manage all data |
| Travel Agent | Add packages, manage own bookings |

---

## 💳 Payment Flow

```
User selects package
      ↓
Fill booking form
      ↓
Razorpay payment popup
      ↓
Payment verified (signature check)
      ↓
Booking confirmed → Notification sent
      ↓
PDF ticket + QR code generated
```

---

## 📄 PDF Ticket

After payment, users can download a PDF ticket containing:
- Booking reference number
- Package & destination details
- Travel date & traveler count
- QR code for check-in
- Payment confirmation

---

## 🎨 UI Features

- ✅ Dark glassmorphism design
- ✅ Hero with particle animations
- ✅ Advanced search & filtering
- ✅ Interactive image gallery
- ✅ Star rating widget
- ✅ Confetti on booking success
- ✅ Animated counters
- ✅ Scroll reveal animations
- ✅ Toast notifications
- ✅ Wishlist toggle with AJAX
- ✅ Mobile-first responsive
- ✅ Chart.js analytics dashboard
- ✅ Marquee destination ticker

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Bootstrap 5, JavaScript |
| Backend | Python Django 4.2 |
| Database | MySQL 8.0 |
| Auth | Django Authentication |
| Payments | Razorpay |
| Maps | Google Maps Embed API |
| PDF | ReportLab |
| QR Code | qrcode[pil] |
| Charts | Chart.js |
| Fonts | Google Fonts (Playfair Display + DM Sans) |
| Icons | Bootstrap Icons |

---

## 📧 Support

For issues or customization help:
- Email: support@travelxpro.com
- GitHub: github.com/travelxpro

---

**Made with ❤️ for travelers | TravelX Pro © 2025**
