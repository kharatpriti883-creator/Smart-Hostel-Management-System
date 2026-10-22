-- PostgreSQL Schema for Smart Hostel Management & Resource Optimization System
-- Database: smart_hostel

-- Clean existing tables if needed (order respects FK constraints)
DROP TABLE IF EXISTS fee_receipts CASCADE;
DROP TABLE IF EXISTS fees CASCADE;
DROP TABLE IF EXISTS complaints CASCADE;
DROP TABLE IF EXISTS leave_requests CASCADE;
DROP TABLE IF EXISTS attendance CASCADE;
DROP TABLE IF EXISTS notices CASCADE;
DROP TABLE IF EXISTS resources CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS wardens CASCADE;
DROP TABLE IF EXISTS rooms CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- 1. Users Table (Authentication)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('warden', 'student')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Rooms Table
CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    room_number VARCHAR(20) UNIQUE NOT NULL,
    block VARCHAR(10) NOT NULL,
    floor INTEGER NOT NULL,
    room_type VARCHAR(30) DEFAULT 'Standard',
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    occupied_beds INTEGER DEFAULT 0 CHECK (occupied_beds >= 0 AND occupied_beds <= capacity),
    status VARCHAR(20) DEFAULT 'Available' CHECK (status IN ('Available', 'Full', 'Maintenance'))
);

-- 3. Students Table
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    roll_number VARCHAR(30) UNIQUE NOT NULL,
    branch VARCHAR(50) NOT NULL,
    year INTEGER NOT NULL CHECK (year BETWEEN 1 AND 5),
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(100) NOT NULL,
    parent_name VARCHAR(100) NOT NULL,
    parent_email VARCHAR(100) NOT NULL,
    parent_phone VARCHAR(15) NOT NULL,
    room_id INTEGER REFERENCES rooms(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Wardens Table
CREATE TABLE wardens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    employee_id VARCHAR(30) UNIQUE NOT NULL,
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Fees Table
CREATE TABLE fees (
    id SERIAL PRIMARY KEY,
    student_id INTEGER UNIQUE REFERENCES students(id) ON DELETE CASCADE,
    total_amount NUMERIC(10, 2) NOT NULL DEFAULT 85000.00,
    paid_amount NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    pending_amount NUMERIC(10, 2) GENERATED ALWAYS AS (total_amount - paid_amount) STORED,
    payment_status VARCHAR(20) DEFAULT 'Pending' CHECK (payment_status IN ('Paid', 'Partial', 'Pending')),
    payment_date DATE,
    due_date DATE DEFAULT (CURRENT_DATE + INTERVAL '30 days')
);

-- 6. Fee Receipts Table
CREATE TABLE fee_receipts (
    id SERIAL PRIMARY KEY,
    fee_id INTEGER REFERENCES fees(id) ON DELETE CASCADE,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    receipt_number VARCHAR(50) UNIQUE NOT NULL,
    amount_paid NUMERIC(10, 2) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_mode VARCHAR(30) DEFAULT 'Online UPI / NetBanking',
    remarks TEXT DEFAULT 'Hostel Term Fee Payment'
);

-- 7. Complaints Table
CREATE TABLE complaints (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    category VARCHAR(30) NOT NULL CHECK (category IN ('Electrical', 'Water', 'Room', 'Maintenance', 'Other')),
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending', 'In Progress', 'Resolved')),
    warden_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Leave Requests Table
CREATE TABLE leave_requests (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Approved', 'Rejected')),
    warden_remark TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. Attendance Table
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    check_in_time TIME DEFAULT CURRENT_TIME,
    status VARCHAR(10) NOT NULL CHECK (status IN ('Present', 'Absent')),
    verification_method VARCHAR(30) DEFAULT 'Biometric' CHECK (verification_method IN ('Biometric', 'QR_Hostel_WiFi', 'Manual')),
    marked_by VARCHAR(50) DEFAULT 'System',
    UNIQUE (student_id, date)
);

-- 10. Notices Table
CREATE TABLE notices (
    id SERIAL PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    date DATE DEFAULT CURRENT_DATE,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. Resources Table (Resource Monitoring)
CREATE TABLE resources (
    id SERIAL PRIMARY KEY,
    resource_type VARCHAR(30) NOT NULL CHECK (resource_type IN ('Electricity', 'Water', 'Maintenance')),
    metric_name VARCHAR(100) NOT NULL,
    usage_value NUMERIC(10, 2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    status VARCHAR(30) DEFAULT 'Normal' CHECK (status IN ('Normal', 'High Usage', 'Warning', 'Maintenance Needed')),
    recorded_date DATE DEFAULT CURRENT_DATE,
    remarks TEXT
);

-- INDEXES for Optimized Performance
CREATE INDEX idx_students_roll ON students(roll_number);
CREATE INDEX idx_students_room ON students(room_id);
CREATE INDEX idx_complaints_student ON complaints(student_id);
CREATE INDEX idx_leave_student ON leave_requests(student_id);
CREATE INDEX idx_attendance_student_date ON attendance(student_id, date);
CREATE INDEX idx_resources_date ON resources(recorded_date);
