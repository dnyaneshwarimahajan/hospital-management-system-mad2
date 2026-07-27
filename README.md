# 🏥 Hospital Management System (HMS)

A full-stack Hospital Management System with a **Vue 3 single-page frontend** and a **Flask REST API** backend. It provides three role-based dashboards — **Admin**, **Doctor**, and **Patient** — with token-based authentication, appointment scheduling, treatment records, and automated email jobs powered by Celery and Redis.

---

## ✨ Features

### 👤 Patient
- Register and log in with secure, token-based authentication
- Browse departments and doctors, and check doctor availability by slot
- Book, view, and manage appointments
- View personal treatment history and export it as a CSV (emailed on request)

### 🩺 Doctor
- Manage availability across daily slots (morning / evening)
- View upcoming and past appointments
- Record diagnosis, treatment, and prescription against each appointment
- Receive an automated monthly activity report by email

### 🛠️ Admin
- Manage users, doctors, and departments
- Assign roles and control account access (activate / blacklist)
- Oversee appointments and system-wide records

---

## 🧰 Tech Stack

**Frontend**
- Vue 3 (Composition API) + Vite
- Vue Router for routing, Pinia for state management

**Backend**
- Flask + Flask-RESTful (REST API, all routes under `/api`)
- Flask-Security for authentication and role-based access control
- Flask-SQLAlchemy (ORM) with SQLite
- Flask-Caching (Redis) and Flask-CORS

**Async & Scheduling**
- Celery for background tasks
- Redis as message broker, result backend, and cache

---

## 🔐 Authentication & Security
- Token-based authentication via Flask-Security (`Authentication-Token` header)
- Passwords hashed with **pbkdf2-SHA512**
- Role-based access control across **Admin / Doctor / Patient**
- CORS restricted to the frontend origin

---

## 🗃️ Data Model

The relational schema spans 7 entities:

| Table | Purpose |
|-------|---------|
| `users` | Accounts for patients, doctors, and admins (with doctor profile fields) |
| `roles` | Role definitions |
| `user_roles` | Many-to-many mapping of users to roles |
| `departments` | Hospital departments |
| `appointment` | Bookings linking patients, doctors, date, time slot, and treatment |
| `treatment` | Diagnosis, treatment, and prescription details |
| `doctor_availability` | Per-doctor daily slot availability |

---

## ⏰ Background Jobs (Celery + Redis)

| Task | Trigger | Description |
|------|---------|-------------|
| Daily appointment reminders | Every day, 8:00 AM | Emails patients who have an appointment that day |
| Monthly doctor reports | 1st of every month, 6:00 AM | Emails each doctor a monthly activity summary |
| Treatment history export | On demand (`/api/export-csv`) | Generates a patient's treatment history as CSV and emails it |

---

## 📁 Project Structure

```
MAD2_Project/
├── backend/
│   ├── app.py                 # App factory, config, API + Security setup
│   ├── model.py               # SQLAlchemy models
│   ├── config.py              # App configuration
│   ├── database.py            # DB instance
│   ├── extensions.py          # Cache and shared extensions
│   ├── celery_config.py       # Celery app + beat schedule
│   ├── task.py                # Background tasks (reminders, reports, export)
│   ├── mail.py                # Email helper
│   ├── auth_apis.py           # Auth / registration endpoints
│   ├── *_route.py / *_resources.py   # Admin, doctor, patient APIs
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── views/             # Page views (dashboards, login, register, etc.)
    │   ├── components/        # Reusable components
    │   ├── router/            # Vue Router config
    │   └── stores/            # Pinia stores
    ├── package.json
    └── vite.config.js
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 20.19+ (or 22.12+)
- Redis running locally on port `6379`

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start the Flask API
python app.py
```

### 2. Redis & Celery

Make sure Redis is running, then in separate terminals from `backend/`:

```bash
# Celery worker
celery -A celery_config.celery worker --loglevel=info --pool=solo

# Celery beat (scheduled jobs)
celery -A celery_config.celery beat --loglevel=info
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

The app runs at **http://localhost:5173** and talks to the API at **http://localhost:5000/api**.

---

## 🔗 Selected API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/register` | Register a new user |
| `POST` | `/api/check-email` | Check if an email is already registered |
| `POST` | `/api/check-username` | Check if a username is available |
| `POST` | `/api/export-csv` | Trigger treatment-history CSV export |
| `GET`  | `/api/trigger-reminders` | Manually trigger daily reminders |
| `GET`  | `/api/trigger-monthly-report` | Manually trigger monthly reports |

Authentication and login endpoints are provided by Flask-Security. Admin, doctor, and patient resources are exposed under the `/api` prefix.

---

## 👩‍💻 Author

**Dnyaneshwari Mahajan**
BS in Data Science & Applications, IIT Madras
GitHub: [@your-username](https://github.com/your-username)

---

> Built as part of the Modern Application Development II (MAD II) course project.
