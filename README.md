# Sushrusa Healthcare Platform — Backend

A Django REST Framework backend for the Sushrusa Healthcare Platform, supporting teleconsultation, prescriptions, payments, patient/doctor management, real-time WebSocket communication, and more.

---

## Tech Stack

- Python 3.10+
- Django 5.2 + Django REST Framework
- PostgreSQL
- Redis (Celery broker + Django Channels)
- Celery (async tasks)
- Django Channels + Daphne (WebSockets)
- JWT Authentication (SimpleJWT)
- DigitalOcean Spaces (S3-compatible media/static storage)
- Gunicorn (WSGI production server)
- Razorpay / PhonePe / Stripe (payment gateways)
- MSG91 / Twilio (OTP/SMS)
- ReportLab (PDF prescription generation)

---

## Project Structure

```
SushrusaBackEnd/
├── myproject/          # Django project config (settings, urls, asgi, wsgi)
├── authentication/     # Custom user model, OTP login, JWT auth
├── patients/           # Patient profiles and records
├── doctors/            # Doctor profiles, availability, specializations
├── consultations/      # Consultation booking and management
├── prescriptions/      # Prescription creation and PDF generation
├── payments/           # Razorpay, PhonePe, Stripe integrations
├── eclinic/            # E-clinic / clinic management
├── analytics/          # Usage analytics
├── notifications/      # Push/SMS/email notifications
├── websockets/         # Real-time WebSocket consumers
├── utils/              # Shared utilities
├── medical_records/    # Patient medical history
├── requirements.txt
├── manage.py
├── gunicorn.conf.py
├── deploy.sh
└── .env.example
```

---

## Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Redis 6+
- pip / virtualenv

---

## Local Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/ss-sahoo/SushrusaBackEnd.git
cd SushrusaBackEnd
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in the required values (see [Environment Variables](#environment-variables) below).

### 5. Set up PostgreSQL

```bash
psql -U postgres
CREATE DATABASE sushrusa_db;
CREATE USER sushrusa_user WITH PASSWORD 'sushrusa_pass';
GRANT ALL PRIVILEGES ON DATABASE sushrusa_db TO sushrusa_user;
\q
```

### 6. Run migrations

```bash
python manage.py migrate
```

### 7. Create a superuser

```bash
python manage.py createsuperuser
```

### 8. Start Redis (required for Celery and WebSockets)

```bash
redis-server
```

### 9. Start the development server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`.

---

## Running WebSocket Support (Daphne)

For WebSocket support in development, use Daphne instead of the default runserver:

```bash
daphne -b 0.0.0.0 -p 8000 myproject.asgi:application
```

---

## Running Celery (Background Tasks)

In a separate terminal:

```bash
celery -A myproject worker --loglevel=info
```

---

## API Documentation

Once the server is running, interactive API docs are available at:

- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`
- OpenAPI Schema: `http://localhost:8000/api/schema/`

---

## API Endpoints Overview

| Prefix | App | Description |
|---|---|---|
| `/api/auth/` | authentication | Register, OTP login, JWT token management |
| `/api/patients/` | patients | Patient profile CRUD |
| `/api/doctors/` | doctors | Doctor profiles, availability |
| `/api/consultations/` | consultations | Book and manage consultations |
| `/api/prescriptions/` | prescriptions | Create prescriptions, generate PDFs |
| `/api/payments/` | payments | Razorpay, PhonePe, Stripe payment flows |
| `/api/eclinic/` | eclinic | Clinic management |
| `/api/analytics/` | analytics | Platform analytics |
| `/api/notifications/` | notifications | Notification management |
| `/api/utils/` | utils | Utility endpoints |
| `/admin/` | Django Admin | Admin panel |

---

## Environment Variables

Key variables from `.env.example`:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for development, `False` for production |
| `ALLOWED_HOSTS` | Comma-separated allowed hostnames |
| `POSTGRES_DB` | PostgreSQL database name |
| `POSTGRES_USER` | PostgreSQL username |
| `POSTGRES_PASSWORD` | PostgreSQL password |
| `POSTGRES_HOST` | PostgreSQL host (default: `localhost`) |
| `POSTGRES_PORT` | PostgreSQL port (default: `5432`) |
| `REDIS_URL` | Redis connection URL |
| `MSG91_AUTHKEY` | MSG91 API key for OTP SMS |
| `MSG91_TEMPLATE_ID` | MSG91 OTP template ID |
| `TWILIO_ACCOUNT_SID` | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | Twilio auth token |
| `TWILIO_PHONE_NUMBER` | Twilio sender phone number |
| `RAZORPAY_KEY_ID` | Razorpay key ID |
| `RAZORPAY_KEY_SECRET` | Razorpay secret key |
| `PHONEPE_ENVIRONMENT` | `sandbox` or `production` |
| `STRIPE_SECRET_KEY` | Stripe secret key |
| `AWS_ACCESS_KEY_ID` | DigitalOcean Spaces / AWS access key |
| `AWS_SECRET_ACCESS_KEY` | DigitalOcean Spaces / AWS secret key |
| `AWS_STORAGE_BUCKET_NAME` | Spaces bucket name |
| `AWS_S3_ENDPOINT_URL` | Spaces endpoint URL |
| `EMAIL_HOST_USER` | SMTP email address |
| `EMAIL_HOST_PASSWORD` | SMTP email password |

Copy `.env.example` to `.env` and fill in your values. Never commit `.env` to version control.

---

## Production Deployment

### Using the deploy script

```bash
source venv/bin/activate
bash deploy.sh
```

This will:
1. Pull latest changes from git
2. Install/update dependencies
3. Run migrations
4. Collect static files
5. Start Gunicorn with the config in `gunicorn.conf.py`

### Gunicorn

Gunicorn is configured in `gunicorn.conf.py`:
- Binds to `0.0.0.0:8000`
- Workers: `(CPU count * 2) + 1`
- Max requests: 1000 (with jitter to prevent thundering herd)

### WebSocket Deployment

For production WebSocket support, use Daphne behind Nginx:

```bash
bash deploy_websocket.sh
```

### Nginx (recommended reverse proxy)

Point Nginx to Gunicorn on port 8000 and Daphne on port 8001 (or use a single Daphne process for both HTTP and WebSocket).

---

## OTP Test Mode

In development, OTP verification is bypassed. Any OTP code `999999` will be accepted.

To disable test mode, set in `settings.py`:

```python
OTP_TEST_MODE = False
```

---

## WebSocket Channels

| Channel | URL Pattern |
|---|---|
| Doctor status | `ws/doctor-status/` |
| Notifications | `ws/notifications/` |
| Consultations | `ws/consultations/` |
| Chat | `ws/chat/` |

---

## Running Tests

```bash
pytest
# or
python manage.py test
```

---

## License

Private — Sushrusa Healthcare Platform. All rights reserved.
