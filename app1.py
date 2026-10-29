import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_university_key')

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'mysql-f8a67f6-ariktatripathi-2574.k.aivencloud.com'),
    'user': os.environ.get('DB_USER', 'avnadmin'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'defaultdb'),
    'port': int(os.environ.get('DB_PORT', 23668))
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def is_admin():
    return session.get('user_role') == 'admin'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Users WHERE USERNAME = %s AND PASSWORD = %s", (username, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user:
                session['logged_in'] = True
                session['username'] = user['USERNAME']
                session['user_role'] = user['ROLE']
                flash(f"Logged in successfully as {user['ROLE'].capitalize()}!")
                return redirect(url_for('index'))
            else:
                flash("Invalid credentials. Please try again.")
        except Exception as e:
            flash(f"Database error: {str(e)}")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('index'))

@app.route('/viewer_mode')
def viewer_mode():
    session['logged_in'] = True
    session['username'] = 'Guest'
    session['user_role'] = 'viewer'
    flash("Switched to Viewer-Only mode.")
    return redirect(url_for('index'))

@app.route('/')
def index():
    if 'user_role' not in session:
        session['user_role'] = 'viewer'
        
    active_tab = request.args.get('tab', 'home')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM Department")
    departments = cursor.fetchall()
    
    cursor.execute("SELECT s.*, d.DEPT_NAME FROM Student s LEFT JOIN Department d ON s.DEPARTMENT_ID = d.DEPARTMENT_ID ORDER BY s.STUDENT_ID ASC")
    students = cursor.fetchall()
    
    cursor.execute("SELECT c.*, d.DEPT_NAME FROM Course c LEFT JOIN Department d ON c.DEPARTMENT_ID = d.DEPARTMENT_ID")
    courses = cursor.fetchall()
    
    cursor.execute("SELECT p.*, d.DEPT_NAME FROM Professor p LEFT JOIN Department d ON p.DEPARTMENT_ID = d.DEPARTMENT_ID")
    professors = cursor.fetchall()
    
    cursor.execute("SELECT e.*, s.NAME as STUDENT_NAME, c.COURSE_NAME FROM Enrollment e LEFT JOIN Student s ON e.STUDENT_ID = s.STUDENT_ID LEFT JOIN Course c ON e.COURSE_ID = c.COURSE_ID")
    enrollments = cursor.fetchall()
    
    cursor.execute("SELECT t.*, c.COURSE_NAME, p.NAME as PROFESSOR_NAME FROM Teaches t LEFT JOIN Course c ON t.COURSE_ID = c.COURSE_ID LEFT JOIN Professor p ON t.PROFESSOR_ID = p.PROFESSOR_ID")
    teaches = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('index.html', 
                           active_tab=active_tab,
                           departments=departments, 
                           students=students, 
                           courses=courses, 
                           professors=professors, 
                           enrollments=enrollments, 
                           teaches=teaches)

@app.route('/add_student', methods=['POST'])
def add_student():
    if not is_admin():
        flash("Access Denied: Admin privileges required to make changes.")
        return redirect(url_for('index', tab='students'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Student (STUDENT_ID, NAME, DOB, EMAIL, PHONE, AGE, DEPARTMENT_ID) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (request.form['student_id'], request.form['name'], request.form['dob'], request.form['email'], request.form['phone'], request.form['age'], request.form['department_id'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    flash("Student added successfully!")
    return redirect(url_for('index', tab='students'))

@app.route('/delete_student/<student_id>', methods=['POST'])
def delete_student(student_id):
    if not is_admin():
        flash("Access Denied: Admin privileges required to make changes.")
        return redirect(url_for('index', tab='students'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Student WHERE STUDENT_ID = %s", (student_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Student deleted successfully!")
    return redirect(url_for('index', tab='students'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)