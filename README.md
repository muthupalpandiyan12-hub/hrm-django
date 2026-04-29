# 🏢 HRM System — Human Resource Management

A full-featured **HR Management System** built with Django 5.2, deployed on **AWS EC2 + RDS PostgreSQL**.

🌐 **Live Demo:** [http://65.2.31.152](http://65.2.31.152)

---

## 🔐 Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `Admin@1234` |
| Employee | `Emp124` | *(employee password)* |

---

## ✅ Features

### 👨‍💼 Admin Panel
| Module | Description |
|--------|-------------|
| 👥 Employee Management | Add, edit, view employees with department & salary |
| 🗓️ Attendance Tracking | Mark present / absent / late / half-day |
| 🌿 Leave Management | Approve or reject employee leave requests |
| 💰 Payroll & Payslips | Generate monthly payslips |
| 🏖️ Holidays | Manage public & company holidays |
| 📢 Announcements | Post announcements to all employees |
| ⭐ Performance Reviews | Quarterly / annual employee ratings |
| 📊 Reports & Analytics | Charts — attendance, salary, performance |
| 👤 User Management | Create admin / employee user accounts |

### 🧑‍💻 Employee Self-Service Portal
| Feature | Description |
|---------|-------------|
| 📋 My Dashboard | Personal stats — attendance, leaves, payslip |
| 🕐 Punch In / Out | Clock in and clock out with timestamp |
| 📅 My Attendance | View personal attendance history |
| 🌿 My Leaves | Apply for leave, track status |
| 💵 My Payslips | Download monthly payslips |
| ⭐ My Reviews | View performance reviews |
| 👤 My Profile | View personal profile |

### 🎨 UI / UX
- 🌙 **Dark Mode** toggle
- 📱 **Mobile Responsive** design
- 📊 **Chart.js** charts for analytics
- 🎨 **Bootstrap 5.3** modern UI

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 5.2 |
| **Language** | Python 3.14 |
| **Database** | PostgreSQL (AWS RDS) |
| **Web Server** | Nginx + Gunicorn |
| **Cloud** | AWS EC2 (Ubuntu 26.04) |
| **Frontend** | Bootstrap 5.3 + Chart.js 4.4 |
| **Icons** | Bootstrap Icons |
| **Fonts** | Google Fonts — Poppins |

---

## ☁️ AWS Architecture

```
User Browser
     │
     ▼
  Nginx (Port 80)
     │
     ▼
  Gunicorn (Port 8000)
     │
     ▼
  Django App (EC2)
     │
     ▼
  PostgreSQL (RDS)
```

- **EC2:** Ubuntu 26.04 LTS — t3.micro
- **RDS:** PostgreSQL — ap-south-1
- **Static files:** served via Nginx

---

## 🚀 Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/muthupalpandiyan12-hub/hrm-django.git
cd hrm-django

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Edit .env with your database credentials

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Run server
python manage.py runserver
```

---

## 📁 Project Structure

```
hrm-django/
├── accounts/          # Authentication
├── attendance/        # Attendance management
├── core/              # Holidays, Announcements, Reports
├── employees/         # Employee & Department models
├── hrm_django/        # Project settings & URLs
├── leave/             # Leave requests & approval
├── payroll/           # Payslip generation
├── performance/       # Performance reviews
├── punch/             # Punch in/out
├── userroles/         # User roles & permissions
├── templates/
│   ├── base.html      # Admin base template
│   └── portal/        # Employee portal templates
├── static/            # CSS, JS, images
├── manage.py
└── requirements.txt
```

---

## 📊 Reports & Analytics

The Reports page (`/core/reports/`) shows:
- 📅 **Monthly Attendance Chart** — Present / Absent / Late / Half-Day per month
- 🏢 **Department-wise Salary** — Total salary payout per department
- ⭐ **Employee Performance** — Top 10 employees by average rating

---

## 📸 Screenshots

| Dashboard | Reports |
|-----------|---------|
| Admin dashboard with stats | Charts & analytics |

---

## 👨‍💻 Developer

**Muthu Palpandiyan**
- GitHub: [@muthupalpandiyan12-hub](https://github.com/muthupalpandiyan12-hub)

---

## 📄 License

This project is for educational / portfolio purposes.
