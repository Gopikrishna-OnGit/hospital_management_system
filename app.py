from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import qrcode
import io
import base64
from flask_mail import Mail, Message
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Configure Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'youremail@gmail.com'  # 🔥 Change this
app.config['MAIL_PASSWORD'] = 'yourpassword'         # 🔥 Change this
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

# Initialize database
def init_db():
    conn = sqlite3.connect('smartqueue.db')
    c = conn.cursor()

    # Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Doctors Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            available TEXT NOT NULL
        )
    ''')

    # Appointments Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            doctor_id INTEGER,
            date TEXT,
            timeslot TEXT,
            emergency INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(doctor_id) REFERENCES doctors(id)
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# Routes

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('smartqueue.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Credentials', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('smartqueue.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, password))
            conn.commit()
            flash('Registered Successfully!', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists.', 'error')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out!', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('smartqueue.db')
    c = conn.cursor()
    c.execute('SELECT * FROM doctors WHERE available="yes"')
    doctors = c.fetchall()
    conn.close()

    return render_template('dashboard.html', doctors=doctors)

@app.route('/book/<int:doctor_id>', methods=['GET','POST'])
def book(doctor_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        date = request.form['date']
        timeslot = request.form['timeslot']

        conn = sqlite3.connect('smartqueue.db')
        c = conn.cursor()
        c.execute('INSERT INTO appointments (user_id, doctor_id, date, timeslot) VALUES (?,?,?,?)',
                  (session['user_id'], doctor_id, date, timeslot))
        conn.commit()
        conn.close()

        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('appointments'))

    return render_template('book.html', doctor_id=doctor_id)

@app.route('/appointments')
def appointments():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('smartqueue.db')
    c = conn.cursor()
    c.execute('''
        SELECT a.id, d.name, d.specialization, a.date, a.timeslot, a.emergency
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        WHERE a.user_id = ?
    ''', (session['user_id'],))
    appointments = c.fetchall()
    conn.close()

    return render_template('appointments.html', appointments=appointments)

@app.route('/emergency', methods=['GET','POST'])
def emergency():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        doctor_id = request.form['doctor_id']
        date = datetime.now().strftime("%Y-%m-%d")
        timeslot = "Immediate"

        conn = sqlite3.connect('smartqueue.db')
        c = conn.cursor()
        c.execute('INSERT INTO appointments (user_id, doctor_id, date, timeslot, emergency) VALUES (?,?,?,?,1)',
                  (session['user_id'], doctor_id, date, timeslot))
        conn.commit()
        conn.close()

        flash('Emergency Appointment Requested!', 'success')
        return redirect(url_for('appointments'))

    conn = sqlite3.connect('smartqueue.db')
    c = conn.cursor()
    c.execute('SELECT * FROM doctors WHERE available="yes"')
    doctors = c.fetchall()
    conn.close()

    return render_template('emergency.html', doctors=doctors)
@app.route('/appointment')
def appointment():
    return render_template('appointment_booking.html')


@app.route('/generate_qr/<int:appointment_id>')
def generate_qr(appointment_id):
    conn = sqlite3.connect('smartqueue.db')
    c = conn.cursor()
    c.execute('SELECT id FROM appointments WHERE id = ?', (appointment_id,))
    appointment = c.fetchone()
    conn.close()

    if appointment:
        qr_data = f"Appointment ID: {appointment[0]}"
        img = qrcode.make(qr_data)
        buf = io.BytesIO()
        img.save(buf)
        image_stream = base64.b64encode(buf.getvalue()).decode()

        return render_template('qrcode.html', qr_image=image_stream)
    else:
        flash('Appointment not found', 'error')
        return redirect(url_for('appointments'))

@app.route('/admin')
def admin():
    conn = sqlite3.connect('smartqueue.db')
    c = conn.cursor()
    c.execute('SELECT * FROM doctors')
    doctors = c.fetchall()
    conn.close()

    return render_template('admin.html', doctors=doctors)

@app.route('/admin/add_doctor', methods=['POST'])
def add_doctor():
    name = request.form['name']
    specialization = request.form['specialization']
    available = request.form['available']

    conn = sqlite3.connect('smartqueue.db')
    c = conn.cursor()
    c.execute('INSERT INTO doctors (name, specialization, available) VALUES (?,?,?)',
              (name, specialization, available))
    conn.commit()
    conn.close()

    flash('Doctor Added Successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/delete_doctor/<int:doctor_id>')
def delete_doctor(doctor_id):
    conn = sqlite3.connect('smartqueue.db')
    c = conn.cursor()
    c.execute('DELETE FROM doctors WHERE id = ?', (doctor_id,))
    conn.commit()
    conn.close()

    flash('Doctor Deleted!', 'success')
    return redirect(url_for('admin'))

# Notifications Sending Example
@app.route('/send_notification')
def send_notification():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('smartqueue.db')
    c = conn.cursor()
    c.execute('SELECT email FROM users WHERE id = ?', (session['user_id'],))
    user_email = c.fetchone()
    conn.close()

    if user_email:
        msg = Message('Health Tips', sender='youremail@gmail.com', recipients=[user_email[0]])
        msg.body = 'Remember to stay hydrated and follow a balanced diet. Check your health dashboard for updates!'
        mail.send(msg)
        flash('Notification Sent!', 'success')
    else:
        flash('Email not found!', 'error')

    return redirect(url_for('dashboard'))



if __name__ == "__main__":
    app.run(debug=True)
