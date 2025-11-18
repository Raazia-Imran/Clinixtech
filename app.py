# Importing Required Libraries
import os
from datetime import datetime

import os
from flask import Flask, render_template, request, redirect, url_for, flash, session

from datetime import datetime, timedelta
from functools import wraps
from io import BytesIO
import heapq

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# PDF generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
except ImportError:
    print("Warning: reportlab not installed. PDF features will not work.")

# # ==================== FLASK APP SETUP ====================

# app = Flask(__name__)
# app.secret_key = "supersecretkey"

# # Database setup
# basedir = os.path.abspath(os.path.dirname(__file__))
# instance_path = os.path.join(basedir, 'instance')
# os.makedirs(instance_path, exist_ok=True)

# # Upload folder setup
# UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
# PATIENT_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'patients')
# os.makedirs(PATIENT_UPLOAD_FOLDER, exist_ok=True)

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# db_path = os.path.join(instance_path, 'clinic.db')
# app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)

# ==================== FLASK APP SETUP ====================

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database setup
basedir = os.path.abspath(os.path.dirname(__file__))

# Upload folder setup
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
PATIENT_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'patients')
os.makedirs(PATIENT_UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# 🔹 IMPORTANT: Point directly to the edited DB file
db_path = os.path.join(basedir, 'clinic.db')  # changed from instance_path
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ==================== DATABASE MODELS ====================

#Doctor Table

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    cnic = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(100))
    contact = db.Column(db.String(20))
    specialization = db.Column(db.String(100))
    qualification = db.Column(db.String(100))
    experience_years = db.Column(db.Integer)
    license_number = db.Column(db.String(50))
    current_hospital = db.Column(db.String(100))
    availability = db.Column(db.String(50))

    consultation_fee = db.Column(db.Float, default=2000.0)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)
    medical_records = db.relationship('MedicalRecord', backref='doctor', lazy=True)
    prescriptions = db.relationship('Prescription', backref='doctor', lazy=True)

# Prescription Table - Stores prescription data
# class Prescription(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
#     patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
#     medication = db.Column(db.String(200))
#     dosage = db.Column(db.String(100))
#     duration = db.Column(db.String(50))
#     instructions = db.Column(db.Text)
#     date = db.Column(db.String(50))


class DoctorAvailability(db.Model):
    __tablename__ = 'doctor_availability'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)  
    day_of_week = db.Column(db.String(20), nullable=False)
    time_slot = db.Column(db.String(20), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    doctor = db.relationship('Doctor', backref='availabilities')

# Appointment Table - Stores appointment data
# class Appointment(db.Model):
#     __tablename__ = 'appointment'
    
#     id = db.Column(db.Integer, primary_key=True)
#     patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
#     doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
#     appointment_date = db.Column(db.Date, nullable=False)
#     time_slot = db.Column(db.String(20), nullable=False)
#     reason = db.Column(db.Text, nullable=False)
#     priority = db.Column(db.String(20), default='normal')  # critical, high, normal
#     status = db.Column(db.String(20), default='pending')   # pending, completed, cancelled
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     completed_at = db.Column(db.DateTime, nullable=True)
    
#     patient = db.relationship('Patient', backref='appointments')
#     doctor = db.relationship('Doctor', backref='appointments')

# Patient Table (ENHANCED)
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    cnic = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    
    # NEW FIELDS for patient portal
    address = db.Column(db.String(200))
    blood_group = db.Column(db.String(5))
    profile_picture = db.Column(db.String(200))
    emergency_contact = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='patient', lazy=True, cascade='all, delete-orphan')
    medical_records = db.relationship('MedicalRecord', backref='patient', lazy=True, cascade='all, delete-orphan')
    vitals = db.relationship('Vitals', backref='patient', lazy=True, cascade='all, delete-orphan')
    prescriptions = db.relationship('Prescription', backref='patient', lazy=True, cascade='all, delete-orphan')

# Doctor Table (ENHANCED)
# class Doctor(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     age = db.Column(db.Integer, nullable=False)
#     gender = db.Column(db.String(10), nullable=False)
#     cnic = db.Column(db.String(20), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(100), nullable=False)
#     contact = db.Column(db.String(20), nullable=False)
#     specialization = db.Column(db.String(100), nullable=False)
#     qualification = db.Column(db.String(100), nullable=False)
#     experience_years = db.Column(db.Integer, nullable=False)
#     license_number = db.Column(db.String(50), unique=True, nullable=False)
#     current_hospital = db.Column(db.String(100))
#     availability = db.Column(db.String(50))
    
#     # NEW FIELD
#     consultation_fee = db.Column(db.Float, default=2000.0)
    
#     # Relationships
#     appointments = db.relationship('Appointment', backref='doctor', lazy=True)
#     medical_records = db.relationship('MedicalRecord', backref='doctor', lazy=True)
#     prescriptions = db.relationship('Prescription', backref='doctor', lazy=True)

# Admin Table (Keep as is)
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    cnic = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(50))

# NEW MODELS FOR PATIENT PORTAL

class Appointment(db.Model):
    __tablename__ = 'appointment'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(10), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    #symptoms = db.Column(db.Text)#
    completed_at = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(20), default='normal')  # emergency, urgent, normal
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MedicalRecord(db.Model):
    __tablename__ = 'medical_record'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    visit_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    diagnosis = db.Column(db.Text, nullable=False)
    treatment = db.Column(db.Text)
    prescription = db.Column(db.Text)
    vitals = db.Column(db.Text)  # JSON string
    notes = db.Column(db.Text)
    follow_up_date = db.Column(db.Date)

class Vitals(db.Model):
    __tablename__ = 'vitals'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    heart_rate = db.Column(db.Integer)  # bpm
    blood_pressure_systolic = db.Column(db.Integer)  # mmHg
    blood_pressure_diastolic = db.Column(db.Integer)  # mmHg
    temperature = db.Column(db.Float)  # °F
    oxygen_saturation = db.Column(db.Integer)  # %
    weight = db.Column(db.Float)  # kg
    height = db.Column(db.Float)  # cm
    bmi = db.Column(db.Float)
    notes = db.Column(db.Text)

class Prescription(db.Model):
    __tablename__ = 'prescription'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    medication = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.Text)
    refills = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)

# ==================== HELPER FUNCTIONS ====================

def clear_sessions():
    """Clear all login sessions"""
    session.pop('admin', None)
    session.pop('doctor', None)
    session.pop('patient', None)
    session.pop('patient_id', None)
    session.pop('user_type', None)

def patient_login_required(f):
    """Decorator to require patient login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'patient' not in session:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('login_patient'))
        return f(*args, **kwargs)
    return decorated_function

def calculate_bmi(weight, height):
    """Calculate BMI from weight (kg) and height (cm)"""
    if weight and height and height > 0:
        height_m = height / 100
        return round(weight / (height_m ** 2), 2)
    return None

def check_vital_alerts(vitals):
    """Check if any vitals are in abnormal range"""
    alerts = []
    
    if vitals.heart_rate:
        if vitals.heart_rate < 60:
            alerts.append(('Heart Rate', 'Low', vitals.heart_rate))
        elif vitals.heart_rate > 100:
            alerts.append(('Heart Rate', 'High', vitals.heart_rate))
    
    if vitals.blood_pressure_systolic and vitals.blood_pressure_diastolic:
        if vitals.blood_pressure_systolic > 140 or vitals.blood_pressure_diastolic > 90:
            alerts.append(('Blood Pressure', 'High', f"{vitals.blood_pressure_systolic}/{vitals.blood_pressure_diastolic}"))
        elif vitals.blood_pressure_systolic < 90 or vitals.blood_pressure_diastolic < 60:
            alerts.append(('Blood Pressure', 'Low', f"{vitals.blood_pressure_systolic}/{vitals.blood_pressure_diastolic}"))
    
    if vitals.temperature:
        if vitals.temperature > 100.4:
            alerts.append(('Temperature', 'Fever', vitals.temperature))
        elif vitals.temperature < 97:
            alerts.append(('Temperature', 'Low', vitals.temperature))
    
    if vitals.oxygen_saturation:
        if vitals.oxygen_saturation < 95:
            alerts.append(('Oxygen Saturation', 'Low', vitals.oxygen_saturation))
    
    return alerts

# ==================== EXISTING ROUTES (Keep as is) ====================

@app.route('/')
def home():
    return render_template('index.html')

# Patient Signup (KEEP ORIGINAL)
@app.route('/signup/patient', methods=['GET', 'POST'])
def signup_patient():
    clear_sessions()
    if request.method == 'POST':
        try:
            patient = Patient(
                name=request.form['name'],
                age=request.form['age'],
                gender=request.form['gender'],
                cnic=request.form['cnic'],
                email=request.form['email'],
                password=request.form['password'],  # In production, use hashing
                contact=request.form['contact']
            )
            db.session.add(patient)
            db.session.commit()
            flash("Patient account created successfully!", "success")
            return redirect(url_for('login_patient'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating account: {str(e)}", "error")
    return render_template('PatientSignIn.html')

# Doctor Signup (KEEP ORIGINAL)
@app.route('/signup/doctor', methods=['GET', 'POST'])
def signup_doctor():
    clear_sessions()
    if request.method == 'POST':
        try:
            doctor = Doctor(
                name=request.form['name'],
                age=request.form['age'],
                gender=request.form['gender'],
                cnic=request.form['cnic'],
                email=request.form['email'],
                password=request.form['password'],
                contact=request.form['contact'],
                specialization=request.form['specialization'],
                qualification=request.form['qualification'],
                experience_years=request.form['experience_years'],
                license_number=request.form['license_number'],
                current_hospital=request.form['current_hospital'],
                availability=request.form['availability']
            )
            db.session.add(doctor)
            db.session.commit()
            flash("Doctor account created successfully!", "success")
            return redirect(url_for('login_doctor'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating account: {str(e)}", "error")
    return render_template('DoctorSignIn.html')

# Admin Signup (KEEP ORIGINAL)
@app.route('/signup/admin', methods=['GET', 'POST'])
def signup_admin():
    clear_sessions()
    if request.method == 'POST':
        try:
            admin = Admin(
                name=request.form['name'],
                age=request.form['age'],
                gender=request.form['gender'],
                cnic=request.form['cnic'],
                email=request.form['email'],
                password=request.form['password'],
                contact=request.form['contact'],
                position=request.form['position'],
                title=request.form.get('title', '')
            )
            db.session.add(admin)
            db.session.commit()
            flash("Admin account created successfully!", "success")
            return redirect(url_for('login_admin'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating account: {str(e)}", "error")
    return render_template('AdminSignIn.html')

# Patient Login (ENHANCED)
@app.route('/login/patient', methods=['GET','POST'])
def login_patient():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        patient = Patient.query.filter_by(email=email, password=password).first()
        
        if patient:
            session.pop('doctor', None)
            session.pop('admin', None)
            session['patient'] = patient.name
            session['patient_id'] = patient.id
            session['user_type'] = 'patient'
            
            flash(f"Welcome, {patient.name}!", "success")
            return redirect(url_for('patient_dashboard'))
        else:
            flash("Invalid email or password", "error")
    
    return render_template('PatientLogin.html')

# Doctor Login (KEEP ORIGINAL)
@app.route('/login/doctor', methods=['GET', 'POST'])
def login_doctor():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        doctor = Doctor.query.filter_by(email=email, password=password).first()
        
        if doctor:
            # Clear other roles
            session.pop('patient', None)
            session.pop('admin', None)
            
            # Store doctor's name in session
            session['doctor'] = doctor.name
            
            # Welcome message
            flash(f"Welcome, Dr. {doctor.name}!", "doctor")
            
            # Redirect to doctor dashboard
            return redirect(url_for('dashboard_doctor'))
        else:
            flash("Invalid email or password", "doctor")
    
    return render_template('DoctorLogin.html')

# Admin Login (KEEP ORIGINAL)
@app.route('/login/admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        admin = Admin.query.filter_by(email=email, password=password).first()
        
        if admin:
            session.pop('patient', None)
            session.pop('doctor', None)
            session['admin'] = admin.name
            session['admin_id'] = admin.id
            session['user_type'] = 'admin'
            
            flash(f"Welcome, Admin {admin.name}!", "success")
            return redirect(url_for('dashboard_admin'))
        else:
            flash("Invalid email or password", "error")
    
    return render_template('AdminLogin.html')

# Old Dashboards (KEEP for backward compatibility)
@app.route('/dashboard/patient')
def dashboard_patient_old():
    if 'patient' not in session:
        return redirect(url_for('login_patient'))
    return redirect(url_for('patient_dashboard'))

@app.route('/dashboard/doctor')
def dashboard_doctor():
    if 'doctor' not in session:
        return redirect(url_for('login_doctor'))
    
    doctor = Doctor.query.filter_by(name=session['doctor']).first()
    
    if not doctor:
        flash("Session expired. Please login again.", "danger")
        return redirect(url_for('login_doctor'))
    
    return render_template('DoctorDashboard.html', doctor=doctor)

@app.route('/dashboard/admin')
def dashboard_admin():
    if 'admin' not in session:
        return redirect(url_for('login_admin'))
    return render_template('AdminDashboard.html')

@app.route('/logout')
def logout():
    clear_sessions()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('home'))

# ==================== NEW PATIENT PORTAL ROUTES ====================

# UPDATED PATIENT ROUTES WITH PROPER DATABASE INTEGRATION
# Add these routes to your app.py, replacing the existing patient routes

# ==================== PATIENT PORTAL ROUTES (FIXED) ====================

@app.route('/patient/dashboard')
@patient_login_required
def patient_dashboard():
    patient_id = session.get('patient_id')
    patient = Patient.query.get_or_404(patient_id)
    
    # Get upcoming appointments
    today = datetime.now().date()
    upcoming_appointments = Appointment.query.filter(
        Appointment.patient_id == patient_id,
        Appointment.appointment_date >= today,
        Appointment.status == 'scheduled'
    ).order_by(Appointment.appointment_date, Appointment.time_slot).limit(5).all()
    
    # Get recent medical records
    recent_records = MedicalRecord.query.filter_by(
        patient_id=patient_id
    ).order_by(MedicalRecord.visit_date.desc()).limit(5).all()
    
    # Get latest vitals
    latest_vitals = Vitals.query.filter_by(
        patient_id=patient_id
    ).order_by(Vitals.date.desc()).first()
    
    # Get active prescriptions
    active_prescriptions = Prescription.query.filter_by(
        patient_id=patient_id,
        active=True
    ).order_by(Prescription.date.desc()).limit(5).all()
    
    # Check for vital alerts
    vital_alerts = []
    if latest_vitals:
        vital_alerts = check_vital_alerts(latest_vitals)
    
    return render_template('patient/dashboard.html',
                         patient=patient,
                         upcoming_appointments=upcoming_appointments,
                         recent_records=recent_records,
                         latest_vitals=latest_vitals,
                         active_prescriptions=active_prescriptions,
                         vital_alerts=vital_alerts,
                         now=datetime.now())

@app.route('/patient/book-appointment', methods=['GET', 'POST'])
@patient_login_required
def book_appointment():
    patient_id = session.get('patient_id')
    
    if request.method == 'POST':
        try:
            doctor_id = request.form.get('doctor_id')
            date_str = request.form.get('date')
            time = request.form.get('time')
            reason = request.form.get('reason')
            priority = request.form.get('priority', 'normal')
            
            # Validate inputs
            if not all([doctor_id, date_str, time, reason]):
                flash('Please fill in all required fields.', 'error')
                return redirect(url_for('book_appointment'))
            
            # Convert date string to date object
            appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Check if doctor exists
            doctor = Doctor.query.get(doctor_id)
            if not doctor:
                flash('Selected doctor not found.', 'error')
                return redirect(url_for('book_appointment'))
            
            # Check if slot is already booked
            existing = Appointment.query.filter_by(
                doctor_id=doctor_id,
                appointment_date=appointment_date,
                time_slot=time,
                status='scheduled'
            ).first()
            
            if existing:
                flash('This time slot is already booked. Please choose another time.', 'error')
                return redirect(url_for('book_appointment'))
            
            # Create new appointment
            appointment = Appointment(
                patient_id=patient_id,
                doctor_id=doctor_id,
                appointment_date=appointment_date,
                time_slot=time,
                reason=reason,
                priority=priority,
                status='scheduled',
                created_at=datetime.utcnow()
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            flash('Appointment booked successfully!', 'success')
            return redirect(url_for('view_appointments'))
            
        except ValueError as e:
            db.session.rollback()
            flash(f'Invalid date format: {str(e)}', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Error booking appointment: {str(e)}', 'error')
            print(f"Appointment booking error: {str(e)}")  # Debug logging
    
    # GET request - show booking form
    doctors = Doctor.query.all()
    specializations = db.session.query(Doctor.specialization).distinct().all()
    specializations = [s[0] for s in specializations if s[0]]
    
    return render_template('patient/book-appointment.html',
                         doctors=doctors,
                         specializations=specializations,
                         today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/patient/appointments')
@patient_login_required
def view_appointments():
    patient_id = session.get('patient_id')
    
    # Get all appointments for this patient
    all_appointments = Appointment.query.filter_by(
        patient_id=patient_id
    ).order_by(Appointment.appointment_date.desc(), Appointment.time_slot.desc()).all()
    
    today = datetime.now().date()
    
    # Separate upcoming and past appointments
    upcoming = [a for a in all_appointments if a.appointment_date >= today and a.status == 'scheduled']
    past = [a for a in all_appointments if a.appointment_date < today or a.status in ['completed', 'cancelled']]
    
    return render_template('patient/view-appointments.html',
                         upcoming_appointments=upcoming,
                         past_appointments=past)

@app.route('/patient/appointment/<int:appointment_id>/cancel', methods=['POST'])
@patient_login_required
def cancel_appointment(appointment_id):
    patient_id = session.get('patient_id')
    
    try:
        appointment = Appointment.query.filter_by(
            id=appointment_id,
            patient_id=patient_id
        ).first_or_404()
        
        # Only allow cancellation of scheduled appointments
        if appointment.status != 'scheduled':
            flash('Only scheduled appointments can be cancelled.', 'error')
            return redirect(url_for('view_appointments'))
        
        appointment.status = 'cancelled'
        db.session.commit()
        
        flash('Appointment cancelled successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error cancelling appointment: {str(e)}', 'error')
    
    return redirect(url_for('view_appointments'))

@app.route('/patient/medical-records')
@patient_login_required
def medical_records():
    patient_id = session.get('patient_id')
    
    # Get all medical records for this patient
    records = MedicalRecord.query.filter_by(
        patient_id=patient_id
    ).order_by(MedicalRecord.visit_date.desc()).all()
    
    return render_template('patient/medical-records.html', records=records)

@app.route('/patient/prescriptions')
@patient_login_required
def prescriptions():
    patient_id = session.get('patient_id')
    
    # Get active prescriptions
    active = Prescription.query.filter_by(
        patient_id=patient_id,
        active=True
    ).order_by(Prescription.date.desc()).all()
    
    # Get past prescriptions
    past = Prescription.query.filter_by(
        patient_id=patient_id,
        active=False
    ).order_by(Prescription.date.desc()).all()
    
    return render_template('patient/prescriptions.html',
                         active_prescriptions=active,
                         past_prescriptions=past)

@app.route('/patient/vitals', methods=['GET', 'POST'])
@patient_login_required
def patient_vitals():
    patient_id = session.get('patient_id')
    
    if request.method == 'POST':
        try:
            # Get form data
            weight = float(request.form.get('weight')) if request.form.get('weight') else None
            height = float(request.form.get('height')) if request.form.get('height') else None
            
            # Calculate BMI if both weight and height are provided
            bmi = calculate_bmi(weight, height) if weight and height else None
            
            # Create new vitals record
            vitals = Vitals(
                patient_id=patient_id,
                date=datetime.utcnow(),
                heart_rate=int(request.form.get('heart_rate')) if request.form.get('heart_rate') else None,
                blood_pressure_systolic=int(request.form.get('bp_systolic')) if request.form.get('bp_systolic') else None,
                blood_pressure_diastolic=int(request.form.get('bp_diastolic')) if request.form.get('bp_diastolic') else None,
                temperature=float(request.form.get('temperature')) if request.form.get('temperature') else None,
                oxygen_saturation=int(request.form.get('oxygen_saturation')) if request.form.get('oxygen_saturation') else None,
                weight=weight,
                height=height,
                bmi=bmi,
                notes=request.form.get('notes')
            )
            
            db.session.add(vitals)
            db.session.commit()
            
            # Check for alerts
            alerts = check_vital_alerts(vitals)
            if alerts:
                alert_msg = "Warning: " + ", ".join([f"{a[0]} is {a[1]}" for a in alerts])
                flash(alert_msg, 'warning')
            else:
                flash('Vitals recorded successfully!', 'success')
            
            return redirect(url_for('patient_vitals'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error recording vitals: {str(e)}', 'error')
            print(f"Vitals recording error: {str(e)}")  # Debug logging
    
    # GET request - show vitals form and history
    all_vitals = Vitals.query.filter_by(
        patient_id=patient_id
    ).order_by(Vitals.date.desc()).all()
    
    return render_template('patient/vitals.html', vitals_list=all_vitals)

@app.route('/patient/profile', methods=['GET', 'POST'])
@patient_login_required
def patient_profile():
    patient_id = session.get('patient_id')
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        try:
            # Update basic information
            patient.name = request.form.get('name')
            patient.age = int(request.form.get('age'))
            patient.gender = request.form.get('gender')
            patient.contact = request.form.get('contact')
            patient.address = request.form.get('address')
            patient.blood_group = request.form.get('blood_group')
            patient.emergency_contact = request.form.get('emergency_contact')
            
            # Handle profile picture upload
            if 'profile_picture' in request.files:
                file = request.files['profile_picture']
                if file and file.filename:
                    filename = secure_filename(f"patient_{patient_id}_{file.filename}")
                    filepath = os.path.join(PATIENT_UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    patient.profile_picture = filename
            
            # Change password if provided
            if request.form.get('new_password'):
                patient.password = request.form.get('new_password')
            
            # Update session name if changed
            if patient.name != session['patient']:
                session['patient'] = patient.name
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('patient_profile'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'error')
            print(f"Profile update error: {str(e)}")  # Debug logging
    
    return render_template('patient/profile.html', patient=patient)

# ==================== API ROUTES ====================

# ==================== PATIENT API ROUTES ====================
# Add these API routes to your app.py

@app.route('/api/doctors/available')
@patient_login_required
def available_doctors():
    date_str = request.args.get('date')
    specialization = request.args.get('specialization')
    
    query = Doctor.query
    
    if specialization:
        query = query.filter_by(specialization=specialization)
    
    doctors = query.all()
    
    result = []
    for doctor in doctors:
        booked_slots = []
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                appointments = Appointment.query.filter_by(
                    doctor_id=doctor.id,
                    appointment_date=date,
                    status='scheduled'
                ).all()
                booked_slots = [a.time_slot for a in appointments]  # Use time_slot here
            except ValueError:
                pass
        
        result.append({
            'id': doctor.id,
            'name': doctor.name,
            'specialization': doctor.specialization,
            'qualification': doctor.qualification,
            'experience_years': doctor.experience_years,
            'consultation_fee': doctor.consultation_fee,
            'booked_slots': booked_slots
        })
    
    return jsonify(result)

def check_appointment_fields():
    """Check what fields exist in the Appointment model"""
    with app.app_context():
        try:
            # Try to access appointments
            appointments = Appointment.query.limit(1).all()
            if appointments:
                apt = appointments[0]
                print(f"✅ Appointment fields:")
                print(f"   - appointment_date: {hasattr(apt, 'appointment_date')}")
                print(f"   - time_slot: {hasattr(apt, 'time_slot')}")
                print(f"   - date: {hasattr(apt, 'date')}")
                print(f"   - time: {hasattr(apt, 'time')}")
            else:
                print("ℹ️ No appointments found in database")
        except Exception as e:
            print(f"❌ Error checking appointments: {e}")

# # Call this in your main block
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#         check_appointment_fields()
#         init_sample_data()
#     app.run(debug=True)

@app.route('/api/patient/vitals')
@patient_login_required
def vitals_api():
    """Get patient vitals data for charts"""
    patient_id = session.get('patient_id')
    days = request.args.get('days', 30, type=int)
    
    start_date = datetime.now() - timedelta(days=days)
    vitals = Vitals.query.filter(
        Vitals.patient_id == patient_id,
        Vitals.date >= start_date
    ).order_by(Vitals.date).all()
    
    data = {
        'dates': [],
        'heart_rate': [],
        'bp_systolic': [],
        'bp_diastolic': [],
        'temperature': [],
        'oxygen_saturation': [],
        'weight': [],
        'bmi': []
    }
    
    for v in vitals:
        data['dates'].append(v.date.strftime('%Y-%m-%d'))
        data['heart_rate'].append(v.heart_rate)
        data['bp_systolic'].append(v.blood_pressure_systolic)
        data['bp_diastolic'].append(v.blood_pressure_diastolic)
        data['temperature'].append(v.temperature)
        data['oxygen_saturation'].append(v.oxygen_saturation)
        data['weight'].append(v.weight)
        data['bmi'].append(v.bmi)
    
    return jsonify(data)

@app.route('/api/patient/appointments')
@patient_login_required
def appointments_api():
    """Get patient appointments for priority queue display"""
    patient_id = session.get('patient_id')
    
    appointments = Appointment.query.filter_by(
        patient_id=patient_id,
        status='scheduled'
    ).order_by(Appointment.appointment_date, Appointment.time_slot).all()
    
    data = []
    priority_order = {'emergency': 1, 'urgent': 2, 'normal': 3}
    
    for a in appointments:
        data.append({
            'id': a.id,
            'doctor': a.doctor.name,
            'date': a.appointment_date.strftime('%Y-%m-%d'),
            'time': a.time_slot,
            'priority': a.priority,
            'priority_value': priority_order.get(a.priority, 3),
            'reason': a.reason
        })
    
    # Sort by date first, then by priority
    data.sort(key=lambda x: (x['date'], x['priority_value'], x['time']))
    
    return jsonify(data)

# ==================== PDF GENERATION ROUTES ====================

@app.route('/patient/download-medical-summary')
@patient_login_required
def download_medical_summary():
    """Generate and download a PDF summary of medical records"""
    try:
        patient_id = session.get('patient_id')
        patient = Patient.query.get_or_404(patient_id)
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Header
        p.setFont("Helvetica-Bold", 20)
        p.drawString(1*inch, height - 1*inch, "Medical Summary Report")
        
        # Patient Info
        p.setFont("Helvetica-Bold", 12)
        p.drawString(1*inch, height - 1.5*inch, "Patient Information")
        p.setFont("Helvetica", 10)
        y = height - 1.8*inch
        p.drawString(1*inch, y, f"Name: {patient.name}")
        y -= 0.2*inch
        p.drawString(1*inch, y, f"Age: {patient.age} | Gender: {patient.gender}")
        y -= 0.2*inch
        p.drawString(1*inch, y, f"Blood Group: {patient.blood_group or 'N/A'}")
        y -= 0.2*inch
        p.drawString(1*inch, y, f"Contact: {patient.contact}")
        
        # Recent Records
        y -= 0.5*inch
        p.setFont("Helvetica-Bold", 12)
        p.drawString(1*inch, y, "Recent Medical Records")
        p.setFont("Helvetica", 9)
        
        records = MedicalRecord.query.filter_by(patient_id=patient_id).order_by(
            MedicalRecord.visit_date.desc()
        ).limit(10).all()
        
        y -= 0.3*inch
        for record in records:
            if y < 2*inch:  # Start new page if running out of space
                p.showPage()
                y = height - 1*inch
            
            p.drawString(1*inch, y, f"Date: {record.visit_date.strftime('%Y-%m-%d')}")
            y -= 0.15*inch
            p.drawString(1*inch, y, f"Diagnosis: {record.diagnosis[:60]}")
            y -= 0.15*inch
            p.drawString(1*inch, y, f"Doctor: Dr. {record.doctor.name}")
            y -= 0.3*inch
        
        p.save()
        buffer.seek(0)
        
        return send_file(buffer, as_attachment=True, download_name='medical_summary.pdf',
                        mimetype='application/pdf')
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'error')
        return redirect(url_for('patient_dashboard'))

@app.route('/patient/download-prescription/<int:prescription_id>')
@patient_login_required
def download_prescription(prescription_id):
    """Generate and download a PDF prescription"""
    try:
        patient_id = session.get('patient_id')
        prescription = Prescription.query.filter_by(
            id=prescription_id,
            patient_id=patient_id
        ).first_or_404()
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Header
        p.setFont("Helvetica-Bold", 18)
        p.drawString(1*inch, height - 1*inch, "Prescription")
        
        # Doctor Info
        p.setFont("Helvetica-Bold", 11)
        p.drawString(1*inch, height - 1.5*inch, f"Dr. {prescription.doctor.name}")
        p.setFont("Helvetica", 9)
        p.drawString(1*inch, height - 1.7*inch, f"{prescription.doctor.specialization}")
        p.drawString(1*inch, height - 1.9*inch, f"License: {prescription.doctor.license_number}")
        
        # Patient Info
        p.setFont("Helvetica-Bold", 11)
        p.drawString(1*inch, height - 2.3*inch, "Patient Information")
        p.setFont("Helvetica", 9)
        p.drawString(1*inch, height - 2.5*inch, f"Name: {prescription.patient.name}")
        p.drawString(1*inch, height - 2.7*inch, f"Age: {prescription.patient.age}")
        p.drawString(1*inch, height - 2.9*inch, f"Date: {prescription.date.strftime('%Y-%m-%d')}")
        
        # Prescription Details
        p.setFont("Helvetica-Bold", 12)
        p.drawString(1*inch, height - 3.4*inch, "Medication")
        p.setFont("Helvetica", 10)
        y = height - 3.7*inch
        p.drawString(1*inch, y, f"Medication: {prescription.medication}")
        y -= 0.2*inch
        p.drawString(1*inch, y, f"Dosage: {prescription.dosage}")
        y -= 0.2*inch
        p.drawString(1*inch, y, f"Frequency: {prescription.frequency}")
        y -= 0.2*inch
        p.drawString(1*inch, y, f"Duration: {prescription.duration}")
        
        if prescription.instructions:
            y -= 0.3*inch
            p.setFont("Helvetica-Bold", 10)
            p.drawString(1*inch, y, "Instructions:")
            p.setFont("Helvetica", 9)
            y -= 0.2*inch
            # Word wrap instructions
            instructions = prescription.instructions[:200]
            p.drawString(1*inch, y, instructions)
        
        p.save()
        buffer.seek(0)
        
        return send_file(buffer, as_attachment=True, 
                        download_name=f'prescription_{prescription_id}.pdf',
                        mimetype='application/pdf')
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'error')
        return redirect(url_for('prescriptions'))

# ==================== DATABASE INITIALIZATION ====================

def init_sample_data():
    """Initialize sample data for testing"""
    with app.app_context():
        # Create sample doctors if none exist
        if Doctor.query.count() == 0:
            doctors_data = [
                {
                    'name': 'Dr. Sarah Ahmed',
                    'age': 42,
                    'gender': 'Female',
                    'cnic': '42301-1234567-8',
                    'email': 'sarah.ahmed@clinic.com',
                    'password': 'doctor123',
                    'contact': '0300-1234567',
                    'specialization': 'Cardiology',
                    'qualification': 'MBBS, FCPS (Cardiology)',
                    'experience_years': 15,
                    'license_number': 'PMC-12345',
                    'current_hospital': 'City General Hospital',
                    'availability': 'Mon-Fri: 9AM-5PM',
                    'consultation_fee': 2500.0
                },
                {
                    'name': 'Dr. Ali Hassan',
                    'age': 38,
                    'gender': 'Male',
                    'cnic': '42301-7654321-9',
                    'email': 'ali.hassan@clinic.com',
                    'password': 'doctor123',
                    'contact': '0300-7654321',
                    'specialization': 'Neurology',
                    'qualification': 'MBBS, FCPS (Neurology)',
                    'experience_years': 12,
                    'license_number': 'PMC-12346',
                    'current_hospital': 'City General Hospital',
                    'availability': 'Mon-Fri: 10AM-6PM',
                    'consultation_fee': 3000.0
                },
                {
                    'name': 'Dr. Fatima Khan',
                    'age': 35,
                    'gender': 'Female',
                    'cnic': '42301-1111111-1',
                    'email': 'fatima.khan@clinic.com',
                    'password': 'doctor123',
                    'contact': '0300-1111111',
                    'specialization': 'Pediatrics',
                    'qualification': 'MBBS, DCH, FCPS (Pediatrics)',
                    'experience_years': 10,
                    'license_number': 'PMC-12347',
                    'current_hospital': 'Children Hospital',
                    'availability': 'Mon-Sat: 8AM-4PM',
                    'consultation_fee': 2000.0
                },
                {
                    'name': 'Dr. Ahmed Raza',
                    'age': 45,
                    'gender': 'Male',
                    'cnic': '42301-2222222-2',
                    'email': 'ahmed.raza@clinic.com',
                    'password': 'doctor123',
                    'contact': '0300-2222222',
                    'specialization': 'Orthopedics',
                    'qualification': 'MBBS, MS (Orthopedics)',
                    'experience_years': 18,
                    'license_number': 'PMC-12348',
                    'current_hospital': 'Orthopedic Center',
                    'availability': 'Mon-Fri: 2PM-8PM',
                    'consultation_fee': 2800.0
                },
                {
                    'name': 'Dr. Ayesha Malik',
                    'age': 33,
                    'gender': 'Female',
                    'cnic': '42301-3333333-3',
                    'email': 'ayesha.malik@clinic.com',
                    'password': 'doctor123',
                    'contact': '0300-3333333',
                    'specialization': 'Dermatology',
                    'qualification': 'MBBS, FCPS (Dermatology)',
                    'experience_years': 8,
                    'license_number': 'PMC-12349',
                    'current_hospital': 'Skin Care Clinic',
                    'availability': 'Tue-Sat: 11AM-7PM',
                    'consultation_fee': 2200.0
                }
            ]
            
            for doc_data in doctors_data:
                doctor = Doctor(**doc_data)
                db.session.add(doctor)
            
            db.session.commit()
            print("✅ Sample doctors created")


# 1. Patient Appointments
# # ============================================
# # DOCTOR APPOINTMENTS - View with Priority Queue
# # ============================================
# @app.route('/doctor/appointments')
# def doctor_appointments():
#     # Check if doctor is logged in
#     if 'doctor' not in session:
#         flash("Please login first", "danger")
#         return redirect(url_for('login_doctor'))
    
#     # Use doctor_id from session
#     doctor = Doctor.query.filter_by(name=session['doctor']).first()
    
#     # Fetch all pending appointments for this doctor
#     # Filter by today's date or just future/pending
#     appointments = Appointment.query.filter(
#         Appointment.doctor_id == doctor.id, 
#         Appointment.status.in_(['pending', 'scheduled']) # Include 'scheduled' too
#     ).order_by(Appointment.appointment_date, Appointment.time_slot).all()
    
#     # Implement Priority Queue using heapq
#     priority_queue = []
    
#     for appointment in appointments:
#         patient = Patient.query.get(appointment.patient_id)
        
#         # Determine priority value (Lower value = Higher Priority)
#         priority_value = PRIORITY_VALUES.get(appointment.priority, 3)
        
#         appointment_data = {
#             'id': appointment.id,
#             'patient_id': appointment.patient_id,
#             'patient_name': patient.name if patient else 'Unknown',
#             'date': appointment.appointment_date.strftime('%Y-%m-%d'),
#             'time': appointment.time_slot,
#             'priority': appointment.priority,
#             'reason': appointment.reason,
#             # Use a combination of priority_value and appointment time/date for tie-breaking
#             'sort_key': (priority_value, appointment.appointment_date, appointment.time_slot)
#         }
        
#         # Push to heap: (priority_value, date_time_tuple, data)
#         # Using a tuple for date/time ensures correct chronological tie-breaking
#         heapq.heappush(priority_queue, (
#             priority_value,
#             (appointment.appointment_date, appointment.time_slot), 
#             appointment_data
#         ))
    
#     # Extract sorted appointments from priority queue
#     sorted_appointments = []
#     while priority_queue:
#         _, _, appointment_data = heapq.heappop(priority_queue)
#         sorted_appointments.append(appointment_data)

#     return render_template('doctor_appointments.html', 
#                             appointments=sorted_appointments)


# # ============================================
# # COMPLETE APPOINTMENT
# # ============================================
# @app.route('/appointment/complete/<int:appointment_id>', methods=['POST'])
# def complete_appointment(appointment_id):
#     """
#     Mark an appointment as completed
#     """
#     doctor_id = session['doctor_id']
    
#     try:
#         appointment = Appointment.query.get_or_404(appointment_id)
        
#         # Verify this appointment belongs to the logged-in doctor
#         if appointment.doctor_id != doctor_id:
#             flash('Unauthorized access to this appointment', 'error')
#             return redirect(url_for('doctor_appointments'))
        
#         appointment.status = 'completed'
#         # appointment.completed_at = datetime.now()
#         db.session.commit()
        
#         flash('Appointment marked as completed!', 'success')
        
#     except Exception as e:
#         db.session.rollback()
#         flash(f'Error completing appointment: {str(e)}', 'error')
    
#     return redirect(url_for('doctor_appointments'))

@app.route('/doctor/appointments')
def doctor_appointments():
    if 'doctor' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('login_doctor'))

    doctor = Doctor.query.filter_by(name=session['doctor']).first()
    if not doctor:
        flash("Doctor not found", "danger")
        return redirect(url_for('login_doctor'))

    # Fetch pending/scheduled appointments for this doctor
    appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.status.in_(['pending', 'scheduled'])
    ).order_by(Appointment.appointment_date, Appointment.time_slot).all()

    # Build priority queue
    priority_queue = []
    for appointment in appointments:
        patient = Patient.query.get(appointment.patient_id)
        priority_value = PRIORITY_VALUES.get(appointment.priority, 3)

        appointment_data = {
            'id': appointment.id,
            'patient_id': appointment.patient_id,
            'patient_name': patient.name if patient else 'Unknown',
            'date': appointment.appointment_date.strftime('%Y-%m-%d'),
            'time': appointment.time_slot,
            'priority': appointment.priority,
            'reason': appointment.reason,
            'status': appointment.status,
            'sort_key': (priority_value, appointment.appointment_date, appointment.time_slot)
        }

        heapq.heappush(priority_queue, (
            priority_value,
            (appointment.appointment_date, appointment.time_slot),
            appointment_data
        ))

    # Pop sorted appointments from the heap
    sorted_appointments = []
    while priority_queue:
        _, _, appointment_data = heapq.heappop(priority_queue)
        sorted_appointments.append(appointment_data)

    return render_template('doctor_appointments.html', appointments=sorted_appointments)

# =====================
# COMPLETE APPOINTMENT
# =====================
@app.route('/appointment/complete/<int:appointment_id>', methods=['POST'])
def complete_appointment(appointment_id):
    if 'doctor' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('login_doctor'))

    doctor = Doctor.query.filter_by(name=session['doctor']).first()
    if not doctor:
        flash("Doctor not found", "danger")
        return redirect(url_for('login_doctor'))

    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.doctor_id != doctor.id:
        flash("Unauthorized access to this appointment", "danger")
        return redirect(url_for('doctor_appointments'))

    appointment.status = 'completed'
    db.session.commit()

    flash("Appointment marked as completed!", "success")
    return redirect(url_for('doctor_appointments'))


# 2. Patient Records
# ============================================
# PATIENT LIST - ALL PATIENTS
# ============================================

@app.route('/doctor/patient-history')
def doctor_patient_history():
    # Check if doctor is logged in
    if 'doctor' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('login_doctor'))
    
    # Get all patients
    patients = Patient.query.all()
    
    return render_template('doctor_patient_history.html', patients=patients)


# ============================================
# PATIENT MEDICAL HISTORY - DETAILED VIEW
# ============================================

@app.route('/doctor/patient/<int:patient_id>')
def patient_medical_history(patient_id):
    # Check if doctor is logged in
    if 'doctor' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('login_doctor'))
    
    # Get current doctor
    doctor = Doctor.query.filter_by(name=session['doctor']).first()
    
    if not doctor:
        flash("Session expired. Please login again.", "danger")
        return redirect(url_for('login_doctor'))
    
    # Get patient details
    patient = Patient.query.get_or_404(patient_id)
    
    # Get all prescriptions for this patient (from this doctor)
    prescriptions = Prescription.query.filter_by(
        patient_id=patient_id,
        doctor_id=doctor.id
    ).order_by(Prescription.date.desc()).all()
    
    # Get all appointments for this patient (with this doctor)
    appointments = Appointment.query.filter_by(
        patient_id=patient_id,
        doctor_id=doctor.id
    ).order_by(Appointment.appointment_date.desc()).all()
    
    # Calculate statistics
    total_visits = len(appointments)
    total_prescriptions = len(prescriptions)
    completed_appointments = len([apt for apt in appointments if apt.status == 'completed'])
    scheduled_appointments = len([apt for apt in appointments if apt.status == 'scheduled'])
    
    return render_template('patient_medical_history.html',
                         patient=patient,
                         prescriptions=prescriptions,
                         appointments=appointments,
                         doctor=doctor,
                         stats={
                             'total_visits': total_visits,
                             'total_prescriptions': total_prescriptions,
                             'completed': completed_appointments,
                             'scheduled': scheduled_appointments
                         })


# ============================================
# UPDATE PATIENT MEDICAL INFORMATION
# ============================================

@app.route('/doctor/patient/<int:patient_id>/update', methods=['POST'])
def update_patient_info(patient_id):
    # Check if doctor is logged in
    if 'doctor' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('login_doctor'))
    
    patient = Patient.query.get_or_404(patient_id)
    
    try:
        # Update only the fields that doctors should be able to update
        # (Not password, email, CNIC - those are patient's personal info)
        if 'contact' in request.form:
            patient.contact = request.form.get('contact')
        
        db.session.commit()
        flash("Patient information updated successfully!", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating patient: {str(e)}", "danger")
    
    return redirect(url_for('patient_medical_history', patient_id=patient_id))


# ============================================
# ADD MEDICAL NOTE TO APPOINTMENT
# ============================================

@app.route('/doctor/appointment/<int:appointment_id>/add-note', methods=['POST'])
def add_appointment_note(appointment_id):
    if 'doctor' not in session:
        return redirect(url_for('login_doctor'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Update the reason field with medical notes
    medical_note = request.form.get('medical_note')
    appointment.reason = appointment.reason + f"\n\n[Medical Note]: {medical_note}"
    
    db.session.commit()
    flash("Medical note added successfully!", "success")
    
    return redirect(url_for('patient_medical_history', patient_id=appointment.patient_id))
#3, prescription
# @app.route('/doctor/prescriptions', methods=['GET', 'POST'])
# def doctor_prescriptions():
#     if 'doctor' not in session:
#         return redirect(url_for('login_doctor'))

#     doctor = Doctor.query.filter_by(name=session['doctor']).first()

#     if request.method == 'POST':
#         # Use current date/time instead of form date since it's not in the form
#         date_value = datetime.utcnow()

#         new_prescription = Prescription(
#             patient_id=request.form['patient_id'],
#             doctor_id=doctor.id,
#             date=date_value,
#             medication=request.form['medication'],
#             dosage=request.form['dosage'],
#             frequency=request.form.get('frequency', 'As directed'),
#             duration=request.form['duration'],
#             instructions=request.form.get('instructions', ''),
#             refills=request.form.get('refills', 0, type=int),
#             active=True
#         )

#         db.session.add(new_prescription)
#         db.session.commit()
#         flash("Prescription added to stack!", "success")
#         return redirect(url_for('doctor_prescriptions'))

#     prescriptions_query = Prescription.query.filter_by(
#         doctor_id=doctor.id
#     ).order_by(Prescription.date.desc()).all()

#     prescriptions = []
#     for p in prescriptions_query:
#         patient = Patient.query.get(p.patient_id)
#         prescriptions.append({
#             'id': p.id,
#             'patient_name': patient.name if patient else 'Unknown',
#             'medication': p.medication,
#             'dosage': p.dosage,
#             'frequency': p.frequency,
#             'duration': p.duration,
#             'instructions': p.instructions,
#             'date': p.date.strftime('%Y-%m-%d %H:%M')
#         })

#     patients = Patient.query.all()

#     return render_template(
#         'doctor_prescriptions.html',
#         prescriptions=prescriptions,
#         patients=patients,
#         doctor=doctor
#     )


# # ===== POP FROM STACK =====
# @app.route('/doctor/prescriptions/delete/<int:prescription_id>', methods=['POST'])
# def delete_prescription(prescription_id):
#     if 'doctor' not in session:
#         return redirect(url_for('login_doctor'))
    
#     # POP operation - Remove prescription
#     prescription = Prescription.query.get(prescription_id)
    
#     if prescription:
#         db.session.delete(prescription)
#         db.session.commit()
#         flash("Prescription removed from stack (POP operation)", "success")
    
#     return redirect(url_for('doctor_prescriptions'))

# In-memory stack for prescriptions
prescription_stack =[]
@app.route('/doctor/prescriptions', methods=['GET', 'POST'])
def doctor_prescriptions():
    if 'doctor' not in session:
        return redirect(url_for('login_doctor'))

    doctor = Doctor.query.filter_by(name=session['doctor']).first()
    patients = Patient.query.all()  # <-- MUST load patients

    if request.method == 'POST':
        # Validate patient_id exists in the form
        if 'patient_id' not in request.form or request.form['patient_id'] == "":
            flash("Please select a patient before adding a prescription.", "danger")
            return redirect(url_for('doctor_prescriptions'))

        date_value = datetime.utcnow()

        new_prescription = Prescription(
            patient_id=request.form['patient_id'],
            doctor_id=doctor.id,
            date=date_value,
            medication=request.form['medication'],
            dosage=request.form['dosage'],
            frequency="As directed",
            duration=request.form['duration'],
            instructions=request.form['instructions'],
            refills=0,
            active=True
        )

        db.session.add(new_prescription)
        db.session.commit()

        # Push to stack
       
        prescription_stack.append({
            'id': new_prescription.id,
            'patient_id': new_prescription.patient_id,
            'doctor_id': new_prescription.doctor_id,
            'medication': new_prescription.medication,
            'dosage': new_prescription.dosage,
            'frequency': new_prescription.frequency,
            'duration': new_prescription.duration,
            'instructions': new_prescription.instructions,
            'date': new_prescription.date.strftime('%Y-%m-%d %H:%M')
        })

        flash("Prescription added successfully!", "success")
        return redirect(url_for('doctor_prescriptions'))

    # GET MODE — Load prescriptions
    prescriptions_query = Prescription.query.filter_by(
        doctor_id=doctor.id
    ).order_by(Prescription.date.desc()).all()

    prescriptions = []
    for p in prescriptions_query:
        patient = Patient.query.get(p.patient_id)
        prescriptions.append({
            'id': p.id,
            'patient_name': patient.name if patient else 'Unknown',
            'medication': p.medication,
            'dosage': p.dosage,
            'frequency': p.frequency,
            'duration': p.duration,
            'instructions': p.instructions,
            'date': p.date.strftime('%Y-%m-%d %H:%M')
        })

    return render_template(
        'doctor_prescriptions.html',
        prescriptions=prescriptions,
        patients=patients,          # <-- REQUIRED
        doctor=doctor,
        stack=prescription_stack
    )


@app.route('/doctor/prescriptions/delete/<int:prescription_id>', methods=['POST'])
def delete_prescription(prescription_id):
    if 'doctor' not in session:
        return redirect(url_for('login_doctor'))

    # 1️⃣ POP from STACK (LIFO behavior)
    for i in range(len(prescription_stack) - 1, -1, -1):
        if prescription_stack[i]['id'] == prescription_id:
            prescription_stack.pop(i)
            break

    # 2️⃣ Delete from DATABASE
    prescription = Prescription.query.get(prescription_id)
    if prescription:
        db.session.delete(prescription)
        db.session.commit()

    flash("Prescription removed from stack (POP operation)", "success")
    return redirect(url_for('doctor_prescriptions'))
    




# 4. Book Appointment
# ============================================
# DOCTOR BOOKS APPOINTMENT
# ============================================
@app.route('/docbook/appointment', methods=['GET', 'POST'])
def docbook_appointment():
    # Check if doctor is logged in
    if 'doctor' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('login_doctor'))
   
    # 1. Get current doctor using the secure ID from session
    doctor = Doctor.query.filter_by(name=session['doctor']).first()
    patients = Patient.query.all()
    
    # --- POST Request: Handle Form Submission ---
    if request.method == 'POST':
        try:
            # Basic Input Validation
            appointment_date_str = request.form['appointment_date']
            time_slot = request.form['time_slot']
            patient_id = request.form['patient_id']
            priority = request.form.get('priority', 'normal')
            reason = request.form['reason']
            
            # Convert date string to date object
            appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()

            # Security: Check if patient exists
            if not Patient.query.get(patient_id):
                flash("🚫 Invalid patient selected.", "error")
                return redirect(url_for('docbook_appointment'))

            # Check for existing appointment at this slot (Prevent double booking)
            existing = Appointment.query.filter_by(
                doctor_id=doctor.id,
                appointment_date=appointment_date,
                time_slot=time_slot
            ).filter(
                Appointment.status.in_(['pending', 'scheduled']) # Only check pending/scheduled
            ).first()

            if existing:
                flash("⚠️ This exact time slot is already booked for a pending appointment.", "warning")
                return redirect(url_for('docbook_appointment'))
                
            # 2. Create New Appointment (Inserted into Priority Queue implicitly via DB query)
            new_appointment = Appointment(
                doctor_id=doctor.id,
                patient_id=patient_id,
                appointment_date=appointment_date,
                time_slot=time_slot,
                priority=priority,
                reason=reason,
                status='pending' # Set status to 'pending' to ensure it appears in the queue
            )
            
            db.session.add(new_appointment)
            db.session.commit()
            
            flash("✅ Appointment successfully scheduled and added to the Doctor's Queue!", "success")
            
            # Redirect to the Doctor Appointments page to show the new appointment in the prioritized list
            return redirect(url_for('doctor_appointments'))
            
        except ValueError:
            db.session.rollback()
            flash("Invalid date format provided.", "error")
            return redirect(url_for('docbook_appointment'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error booking appointment: {str(e)}", "danger")
            return redirect(url_for('docbook_appointment'))
            
    # --- GET Request: Render Form ---
    return render_template('docbook_appointment.html', 
                            doctor=doctor, 
                            patients=patients,
                            today=datetime.now().strftime('%Y-%m-%d'))


# ============================================
# DOCTOR APPOINTMENTS - View with Priority Queue
# ============================================
# @app.route('/doctor/appointments', methods=['GET', 'POST'])
# def doctor_appointments():
#     # Check if doctor is logged in
#     if 'doctor' not in session:
#         flash("Please login first", "danger")
#         return redirect(url_for('login_doctor'))
    
#     # Use doctor_id from session
#     doctor = Doctor.query.filter_by(name=session['doctor']).first()
    
#     # Handle POST request (if any form is submitting to this route)
#     if request.method == 'POST':
#         # This could be for completing appointments or other actions
#         appointment_id = request.form.get('appointment_id')
#         action = request.form.get('action')
        
#         if action == 'complete' and appointment_id:
#             try:
#                 appointment = Appointment.query.get_or_404(appointment_id)
                
#                 # Verify this appointment belongs to the logged-in doctor
#                 if appointment.doctor_id == doctor.id:
#                     appointment.status = 'completed'
#                     db.session.commit()
#                     flash('Appointment marked as completed!', 'success')
#                 else:
#                     flash('Unauthorized access to this appointment', 'error')
                    
#             except Exception as e:
#                 db.session.rollback()
#                 flash(f'Error completing appointment: {str(e)}', 'error')
        
#         return redirect(url_for('doctor_appointments'))
    
#     # GET request - Fetch all pending appointments for this doctor
#     appointments = Appointment.query.filter(
#         Appointment.doctor_id == doctor.id, 
#         Appointment.status.in_(['pending', 'scheduled'])
#     ).order_by(Appointment.appointment_date, Appointment.time_slot).all()
    
#     # Implement Priority Queue using heapq
#     priority_queue = []
    
#     for appointment in appointments:
#         patient = Patient.query.get(appointment.patient_id)
        
#         # Determine priority value (Lower value = Higher Priority)
#         priority_value = PRIORITY_VALUES.get(appointment.priority, 3)
        
#         appointment_data = {
#             'id': appointment.id,
#             'patient_id': appointment.patient_id,
#             'patient_name': patient.name if patient else 'Unknown',
#             'date': appointment.appointment_date.strftime('%Y-%m-%d'),
#             'time': appointment.time_slot,
#             'priority': appointment.priority,
#             'reason': appointment.reason or appointment.symptoms or 'No reason provided',
#             # Use a combination of priority_value and appointment time/date for tie-breaking
#             'sort_key': (priority_value, appointment.appointment_date, appointment.time_slot)
#         }
        
#         # Push to heap: (priority_value, date_time_tuple, data)
#         heapq.heappush(priority_queue, (
#             priority_value,
#             (appointment.appointment_date, appointment.time_slot), 
#             appointment_data
#         ))
    
#     # Extract sorted appointments from priority queue
#     sorted_appointments = []
#     while priority_queue:
#         _, _, appointment_data = heapq.heappop(priority_queue)
#         sorted_appointments.append(appointment_data)

#     return render_template('doctor_appointments.html', 
#                           appointments=sorted_appointments,
#                           doctor=doctor)

# # 5. Edit Profile
# # ============================================
# # DOCTOR EDIT PROFILE
# # ============================================
@app.route('/doctor/editprofile', methods=['GET', 'POST'])
def doctor_editprofile():
    # Check if doctor is logged in
    if 'doctor' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('login_doctor'))
    
    # Get current doctor from database
    doctor = Doctor.query.filter_by(name=session['doctor']).first()
    
    # If doctor not found
    if not doctor:
        flash("Session expired. Please login again.", "danger")
        session.pop('doctor', None)
        return redirect(url_for('login_doctor'))
    
    if request.method == 'POST':
        try:
            # Update doctor information from form
            doctor.name = request.form.get('name')
            doctor.age = request.form.get('age')
            doctor.gender = request.form.get('gender')
            doctor.cnic = request.form.get('cnic')
            doctor.email = request.form.get('email')
            doctor.contact = request.form.get('contact')
            doctor.specialization = request.form.get('specialization')
            doctor.qualification = request.form.get('qualification')
            doctor.experience_years = request.form.get('experience_years')
            doctor.license_number = request.form.get('license_number')
            doctor.current_hospital = request.form.get('current_hospital')
            doctor.availability = request.form.get('availability')
            
            # Update session if name changed
            session['doctor'] = doctor.name
            
            # Save to database
            db.session.commit()
            
            flash("Profile updated successfully!", "success")
            return redirect(url_for('dashboard_doctor'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating profile: {str(e)}", "danger")
    
    return render_template('doctor_editprofile.html', doctor=doctor)


# 6. Schedule Management
PRIORITY_VALUES = {
    # 'critical': 1,  # Highest priority
    # 'high': 2,
    'emergency': 1,
    'urgent': 2,
    'normal': 3     # Lowest priority
}
# ============================================
# DOCTOR SCHEDULE - Set Availability
# ============================================
@app.route('/doctor/schedule', methods=['GET', 'POST'])
def doctor_schedule():
    # Check if doctor is logged in
    if 'doctor' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('login_doctor'))
    
    doctor = Doctor.query.filter_by(name=session['doctor']).first()
    
    if request.method == 'POST':
        try:
            # Get form data for each day
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            
            # Clear existing availability for the doctor
            DoctorAvailability.query.filter_by(doctor_id=doctor.id).delete()
            
            # Process each day
            for day in days:
                day_enabled = request.form.get(f'{day}_enabled')
                
                if day_enabled:  # If the day is enabled
                    time_slots = request.form.getlist(f'{day}_slots')
                    
                    # Save each time slot
                    for time_slot in time_slots:
                        availability = DoctorAvailability(
                            doctor_id=doctor.id,
                            day_of_week=day.capitalize(),
                            time_slot=time_slot,
                            is_available=True
                        )
                        db.session.add(availability)
            
            db.session.commit()
            flash('Availability saved successfully!', 'success')
            return redirect(url_for('dashboard_doctor'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving availability: {str(e)}', 'error')
    
    # GET request - Load existing availability
    availability = DoctorAvailability.query.filter_by(doctor_id=doctor.id).all()
    
    # Organize availability by day
    availability_by_day = {}
    for avail in availability:
        day = avail.day_of_week.lower()
        if day not in availability_by_day:
            availability_by_day[day] = []
        availability_by_day[day].append(avail.time_slot)
    
    return render_template('doctor_schedule.html', 
                         availability=availability_by_day)


# ==================== RUN APP ====================

if __name__ == '__main__':
    with app.app_context():
        # Create tables
        db.create_all()

        # Initialize sample data
        init_sample_data()

        # Check appointment fields
        check_appointment_fields()

        # Inspect database
        inspector = db.inspect(db.engine)
        print("📊 Tables in DB:", inspector.get_table_names())
        print("🏥 Total Doctors:", Doctor.query.count())
        print("👥 Total Patients:", Patient.query.count())

    # Run Flask app (only once!)
    app.run(debug=True)

