# Smart Hostel Management & Resource Optimization System
> **College Final Year & Hackathon Competition-Ready Full-Stack Web Application**

A complete, production-grade full-stack web application designed for college hostel administration and resident student services. Built with Python Flask, PostgreSQL, HTML5, Vanilla CSS3, and JavaScript Fetch API.

---

## 🌟 Key Features

1. **Authentication & Role Authorization**:
   - Separate login portals for **Students** and **Warden Administration**.
   - Werkzeug secure password hashing (`pbkdf2:sha256`) and Flask session management.
   - Guarded page routes and API protection preventing unauthorized cross-role access.

2. **Smart Room & Capacity Management**:
   - Automatic room bed capacity enforcement (`capacity - occupied_beds`).
   - Dynamic block allocations (Block A, Block B) preventing room overbooking.

3. **Digital Fee Billing & Printable Receipts**:
   - Tracks total, paid, and pending fee balances across student accounts.
   - Printable / PDF-exportable official fee receipt modal (`window.print()`).

4. **Student Grievance & Maintenance Desk**:
   - Category-based maintenance complaints (Electrical, Plumbing/Water, Room Locks, General).
   - Real-time status updates (Pending -> In Progress -> Resolved) with Warden responses.

5. **Outstation Leave Pass & Parent Email Alerts**:
   - Outstation leave pass applications with start date, end date, and reason.
   - Automatic SMTP parent email notification dispatched upon Warden approval or rejection (with fallback console logging).

6. **Biometric & QR Attendance Architecture**:
   - Hardware integration architecture for biometric thumbprint roll-call logging.
   - Location-verified QR attendance simulation for students connected to hostel Wi-Fi.

7. **Utility Resource Optimization Desk**:
   - Real-time monitoring of Electricity sub-meters (kWh), Overhead Water Storage (Liters), and Facility Maintenance logs.
   - Status alerts (Normal, High Usage, Leak Warning, Maintenance Needed).

---

## 🚀 Quick Setup & Installation Guide

### Step 1: Prerequisites
- **Python** (version 3.9 or higher)
- **PostgreSQL** installed and running on your system.

---

### Step 2: Create PostgreSQL Database
Open PostgreSQL `psql` shell or pgAdmin and create a new database named `smart_hostel`:

```sql
CREATE DATABASE smart_hostel;
```

---

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Open `.env` and edit your PostgreSQL credentials:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smart_hostel
DB_USER=postgres
DB_PASSWORD=YOUR_POSTGRES_PASSWORD
SECRET_KEY=super_secret_hostel_management_key_2026

# Optional SMTP Settings (Logs cleanly to terminal if unconfigured)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM=noreply@smarthostel.edu
```

---

### Step 4: Install Dependencies
Open VS Code terminal inside the project directory and run:

```bash
pip install -r requirements.txt
```

---

### Step 5: Initialize Database & Seed Demo Data
Run the automated initialization script to create all PostgreSQL tables, foreign key constraints, indexes, and seed realistic demo records:

```bash
python init_db.py
```

*Note: Running `python init_db.py` is safe and idempotent. It creates tables cleanly and populates demo records.*

---

### Step 6: Start Flask Server
Run the Flask application:

```bash
python app.py
```

---

### Step 7: Open Application in Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔑 Demo Credentials for Viva / Presentation

### 👨‍💼 Warden Demo Account
- **Username**: `warden1`
- **Password**: `warden123`

### 👨‍🎓 Student Demo Accounts
- **Student 1**: Username `student1` | Password `student123` (Rahul Sharma - Computer Science, Room A-101)
- **Student 2**: Username `student2` | Password `student123` (Priya Patel - Electronics, Room A-101)
- **Student 3**: Username `student3` | Password `student123` (Amit Verma - Mechanical, Room A-101)
- **Student 4**: Username `student4` | Password `student123` (Sneha Reddy - Electrical, Room A-102)
- **Student 5**: Username `student5` | Password `student123` (Vikram Singh - IT, Room A-102)

---

## 📁 Project Structure

```
Smart_Hostel_Management/
├── app.py                      # Flask Application Server & REST APIs
├── init_db.py                  # Automated Database Initializer & Demo Data Seed
├── requirements.txt            # Python Dependencies (Flask, psycopg2-binary, python-dotenv, Werkzeug)
├── README.md                   # Comprehensive Setup Documentation
├── .env.example                # Sample Environment Variables
├── .env                        # Live Environment Configuration
├── .gitignore
├── database/
│   └── database.sql            # Complete PostgreSQL DDL Schema & Indexes
├── templates/
│   ├── index.html              # Public Home Page with Student & Warden Login Options
│   ├── student_login.html      # Student Login Page
│   ├── warden_login.html       # Warden Login Page
│   ├── student_dashboard.html  # Student Dashboard & Overview
│   ├── student_profile.html    # Student Profile Management
│   ├── student_room.html       # Allocated Room & Roommates Details
│   ├── student_fees.html       # Student Fee Summary & Printable Receipt
│   ├── student_complaints.html # Student Grievance Complaint Submission & History
│   ├── student_leave.html      # Outstation Leave Application Desk
│   ├── student_attendance.html # Attendance Log & QR Wi-Fi Simulation
│   ├── student_notices.html    # Published Hostel Announcements
│   ├── warden_dashboard.html   # Warden Admin Dashboard with Charts
│   ├── warden_students.html    # Student Directory (Add, Search, Allocate Room, Delete)
│   ├── warden_rooms.html       # Room Capacity & Bed Occupancy Manager
│   ├── warden_fees.html       # Fee Billing & Payment Acknowledgment
│   ├── warden_complaints.html # Grievance Response Desk
│   ├── warden_leave.html      # Leave Approval Desk with Parent Email Dispatch
│   ├── warden_attendance.html # Daily Attendance Roster & Manual Override
│   ├── warden_notices.html    # Notice Board Manager
│   └── warden_resources.html  # Utility Resource Optimization Desk (Electricity, Water, Maint.)
└── static/
    ├── css/
    │   └── style.css          # Design System & Responsive Layouts
    └── js/
        └── script.js          # REST Client, Fetch API Handlers & UI Interactivity
```

---

## 🛠️ Full REST API Endpoint Reference

| Method | Endpoint | Access Role | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/login/student` | Public | Authenticate student credentials |
| `POST` | `/api/login/warden` | Public | Authenticate warden credentials |
| `POST` | `/api/logout` | Session | Clear session & log out |
| `GET` | `/api/dashboard/stats` | Protected | Fetch summary statistics & chart data |
| `GET` | `/api/students` | Warden | Fetch all enrolled students |
| `POST` | `/api/students` | Warden | Register a new student to database |
| `PUT` | `/api/students/<id>` | Protected | Update student contact records |
| `DELETE`| `/api/students/<id>` | Warden | Remove student & release room bed |
| `GET` | `/api/rooms` | Protected | Fetch rooms & occupant lists |
| `POST` | `/api/rooms` | Warden | Add new hostel room |
| `POST` | `/api/rooms/<id>/allocate` | Warden | Allocate student to room with capacity check |
| `GET` | `/api/fees` | Protected | View fee billing records |
| `PUT` | `/api/fees/<id>` | Warden | Record fee payment & update status |
| `GET` | `/api/fees/receipt/<id>` | Protected | Get printable fee receipt data |
| `GET` | `/api/complaints` | Protected | View complaints list |
| `POST` | `/api/complaints` | Student | Submit maintenance complaint |
| `PUT` | `/api/complaints/<id>` | Warden | Update complaint status & warden response |
| `GET` | `/api/leaves` | Protected | View outstation leave passes |
| `POST` | `/api/leaves` | Student | Submit outstation leave request |
| `PUT` | `/api/leaves/<id>` | Warden | Approve/Reject leave & notify parent email |
| `GET` | `/api/attendance` | Protected | View daily attendance logs |
| `POST` | `/api/attendance` | Protected | Record attendance (Biometric/QR/Manual) |
| `GET` | `/api/notices` | Public/Protected| Fetch active notice board announcements |
| `POST` | `/api/notices` | Warden | Publish new hostel notice |
| `PUT` | `/api/notices/<id>` | Warden | Update or activate/deactivate notice |
| `DELETE`| `/api/notices/<id>` | Warden | Remove notice from database |
| `GET` | `/api/resources` | Protected | Fetch electricity/water/maintenance readings |
| `POST` | `/api/resources` | Warden | Add utility meter log |
| `PUT` | `/api/resources/<id>` | Warden | Update resource reading & status alert |

---

## 🧪 Comprehensive Viva & Demonstration Checklist

- [x] **Home Page**: Rendered with Hostel branding, rules, facilities, and TWO distinct login options.
- [x] **Student Login**: Authenticate `student1` / `student123` -> Redirect to Student Dashboard.
- [x] **Student Dashboard**: Live cards for Room A-101, Fee Status, Attendance Rate (86.67%), Complaints, and Recent Notices.
- [x] **Student Complaints**: Submit new complaint -> Appears instantly in database and Warden desk.
- [x] **Warden Login**: Authenticate `warden1` / `warden123` -> Redirect to Warden Dashboard.
- [x] **Warden Dashboard**: Display real-time stats (Total Students, Free Beds, Pending Complaints, Attendance Doughnut Chart).
- [x] **Student Directory**: Click "Add New Student" -> Save form -> Inserts into PostgreSQL -> Appears in table without manual SQL.
- [x] **Room Allocation & Capacity Enforcement**: Assign student to full room -> Rejected with error message.
- [x] **Fee Payment & Receipt**: Update fee payment -> View Receipt modal -> Download/Print PDF view.
- [x] **Leave Pass Approval & Email Dispatch**: Warden approves leave -> Parent notification email dispatched (or logged to console).
- [x] **Resource Monitoring**: Update electricity/water log -> Status badge updates on dashboard.

---

## 📜 License & Project Rights
Created for College Final Project / Competition demonstration. Feel free to customize and extend!
