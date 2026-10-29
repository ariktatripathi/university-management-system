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

# --- AUTHENTICATION ROUTES ---

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

# --- MAIN DASHBOARD VIEW ---

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

# --- DEPARTMENT ROUTES ---
@app.route('/add_department', methods=['POST'])
def add_department():
    if not is_admin():
        flash("Access Denied: Admin privileges required.")
        return redirect(url_for('index', tab='departments'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Department (DEPARTMENT_ID, DEPT_NAME, LOCATION) VALUES (%s, %s, %s)",
                   (request.form['department_id'], request.form['dept_name'], request.form['location']))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Department added successfully!")
    return redirect(url_for('index', tab='departments'))

@app.route('/edit_department', methods=['POST'])
def edit_department():
    if not is_admin():
        flash("Access Denied: Admin privileges required.")
        return redirect(url_for('index', tab='departments'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Department SET DEPT_NAME=%s, LOCATION=%s WHERE DEPARTMENT_ID=%s",
                   (request.form['dept_name'], request.form['location'], request.form['department_id']))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Department updated successfully!")
    return redirect(url_for('index', tab='departments'))

@app.route('/delete_department/<department_id>', methods=['POST'])
def delete_department(department_id):
    if not is_admin():
        flash("Access Denied: Admin privileges required.")
        return redirect(url_for('index', tab='departments'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Department WHERE DEPARTMENT_ID = %s", (department_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Department deleted successfully!")
    return redirect(url_for('index', tab='departments'))

# --- STUDENT ROUTES ---
@app.route('/add_student', methods=['POST'])
def add_student():
    if not is_admin():
        flash("Access Denied: Admin privileges required.")
        return redirect(url_for('index', tab='students'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Student (STUDENT_ID, NAME, DOB, EMAIL, PHONE, AGE, DEPARTMENT_ID) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                   (request.form['student_id'], request.form['name'], request.form['dob'], request.form['email'], request.form['phone'], request.form['age'], request.form['department_id']))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Student added successfully!")
    return redirect(url_for('index', tab='students'))

@app.route('/edit_student', methods=['POST'])
def edit_student():
    if not is_admin():
        flash("Access Denied: Admin privileges required.")
        return redirect(url_for('index', tab='students'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Student SET NAME=%s, DOB=%s, EMAIL=%s, PHONE=%s, AGE=%s, DEPARTMENT_ID=%s WHERE STUDENT_ID=%s",
                   (request.form['name'], request.form['dob'], request.form['email'], request.form['phone'], request.form['age'], request.form['department_id'], request.form['student_id']))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Student updated successfully!")
    return redirect(url_for('index', tab='students'))

@app.route('/delete_student/<student_id>', methods=['POST'])
def delete_student(student_id):
    if not is_admin():
        flash("Access Denied: Admin privileges required.")
        return redirect(url_for('index', tab='students'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Student WHERE STUDENT_ID = %s", (student_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Student deleted successfully!")
    return redirect(url_for('index', tab='students'))

# --- COURSE ROUTES ---
@app.route('/add_course', methods=['POST'])
def add_course():
    if not is_admin():
        flash("Access Denied: Admin privileges required.")
        return redirect(url_for('index', tab='courses'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Course (COURSE_ID, COURSE_NAME, CREDITS, DEPARTMENT_ID) VALUES (%s, %s, %s, %s)",
                   (request.form['course_id'], request.form['course_name'], request.form['credits'], request.form['department_id']))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Course added successfully!")
    return redirect(url_for('index', tab='courses'))

@app.route('/edit_course', methods=['POST'])
def edit_course():
    if not is_admin():
        flash("Access Denied: Admin privileges required.")
        return redirect(url_for('index', tab='courses'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Course SET COURSE_NAME=%s, CREDITS=%s, DEPARTMENT_ID=%s WHERE COURSE_ID=%s",
                   (request.form['course_name'], request.form['credits'], request.form['department_id'], request.form['course_id']))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Course updated successfully!")
    return redirect(url_for('index', tab='courses'))

@app.route('/delete_course/<course_id>', methods=['POST'])
def delete_course(course_id):
    if not is_admin():
        flash("Access Denied: Admin privileges required.")
        return redirect(url_for('index', tab='courses'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Course WHERE COURSE_ID = %s", (course_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Course deleted successfully!")
    return redirect(url_for('index', tab='courses'))

# --- PROFESSOR ROUTES ---
@app.route('/add_professor', methods=['POST'])
def add_professor():
    if not is_admin():
        flash("Access Denied: Admin privileges required.")
        return redirect(url_for('index', tab='professors'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Professor (PROFESSOR_ID, NAME, EMAIL, PHONE, DEPARTMENT_ID) VALUES (%s, %s, %s, %s, %s)",
                   (request.form['professor_id'], request.form['name'], request.form['email'], request.form['phone'], request.form['department_id']))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Professor added successfully!")
    return redirect(url_for('index', tab='professors'))

@app.route('/edit_professor', methods=['POST'])
def edit_professor():
    if not is_admin():
        flash("Access Denied: Admin privileges required.")
        return redirect(url_for('index', tab='professors'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Professor SET NAME=%s, EMAIL=%s, PHONE=%s, DEPARTMENT_ID=%s WHERE PROFESSOR_ID=%s",
                   (request.form['name'], request.form['email'], request.form['phone'], request.form['department_id'], request.form['professor_id']))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Professor updated successfully!")
    return redirect(url_for('index', tab='professors'))

@app.route('/delete_professor/<professor_id>', methods=['POST'])
def delete_professor(professor_id):
    if not is_admin():
        flash("Access Denied: Admin privileges required.")
        return redirect(url_for('index', tab='professors'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Professor WHERE PROFESSOR_ID = %s", (professor_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Professor deleted successfully!")
    return redirect(url_for('index', tab='professors'))

# --- ENROLLMENT ROUTES ---
@app.route('/add_enrollment', methods=['POST'])
def add_enrollment():
    if not is_admin():
        flash("Access Denied: Admin privileges required.")
        return redirect(url_for('index', tab='enrollments'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Enrollment (ENROLLMENT_ID, STUDENT_ID, COURSE_ID, GRADE) VALUES (%s, %s, %s, %s)",
                   (request.form['enrollment_id'], request.form['student_id'], request.form['course_id'], request.form['grade']))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Enrollment added successfully!")
    return redirect(url_for('index', tab='enrollments'))

@app.route('/edit_enrollment', methods=['POST'])
def edit_enrollment():
    if not is_admin():
        flash("Access Denied: Admin privileges required.")
        return redirect(url_for('index', tab='enrollments'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Enrollment SET STUDENT_ID=%s, COURSE_ID=%s, GRADE=%s WHERE ENROLLMENT_ID=%s",
                   (request.form['student_id'], request.form['course_id'], request.form['grade'], request.form['enrollment_id']))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Enrollment updated successfully!")
    return redirect(url_for('index', tab='enrollments'))

@app.route('/delete_enrollment/<enrollment_id>', methods=['POST'])
def delete_enrollment(enrollment_id):
    if not is_admin():
        flash("Access Denied: Admin privileges required.")
        return redirect(url_for('index', tab='enrollments'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Enrollment WHERE ENROLLMENT_ID = %s", (enrollment_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Enrollment deleted successfully!")
    return redirect(url_for('index', tab='enrollments'))

# --- TEACHES ROUTES ---
@app.route('/add_teaches', methods=['POST'])
def add_teaches():
    if not is_admin():
        flash("Access Denied: Admin privileges required.")
        return redirect(url_for('index', tab='teaches'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Teaches (COURSE_ID, PROFESSOR_ID, SEMESTER, YEAR) VALUES (%s, %s, %s, %s)",
                   (request.form['course_id'], request.form['professor_id'], request.form['semester'], request.form['year']))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Assignment added successfully!")
    return redirect(url_for('index', tab='teaches'))

@app.route('/edit_teaches', methods=['POST'])
def edit_teaches():
    if not is_admin():
        flash("Access Denied: Admin privileges required.")
        return redirect(url_for('index', tab='teaches'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Teaches SET SEMESTER=%s, YEAR=%s WHERE COURSE_ID=%s AND PROFESSOR_ID=%s AND SEMESTER=%s AND YEAR=%s",
                   (request.form['new_semester'], request.form['new_year'], request.form['old_course_id'], request.form['old_professor_id'], request.form['old_semester'], request.form['old_year']))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Assignment updated successfully!")
    return redirect(url_for('index', tab='teaches'))

@app.route('/delete_teaches/<course_id>/<professor_id>/<semester>/<year>', methods=['POST'])
def delete_teaches(course_id, professor_id, semester, year):
    if not is_admin():
        flash("Access Denied: Admin privileges required.")
        return redirect(url_for('index', tab='teaches'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Teaches WHERE COURSE_ID=%s AND PROFESSOR_ID=%s AND SEMESTER=%s AND YEAR=%s",
                   (course_id, professor_id, semester, year))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Assignment deleted successfully!")
    return redirect(url_for('index', tab='teaches'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)