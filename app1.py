from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

import os
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Reads credentials from environment variables set on Render, or defaults to local settings
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'YourNewPassword123!'),
    'database': os.environ.get('DB_NAME', 'defaultdb'),
    'port': int(os.environ.get('DB_PORT', 3306))
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/')
def index():
    tab = request.args.get('tab', 'dashboard')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT DEPARTMENT_ID, DEPT_NAME FROM Department")
    departments = cursor.fetchall()
    
    data = []
    if tab != 'dashboard':
        table_map = {
            'student': 'Student',
            'department': 'Department',
            'course': 'Course',
            'professor': 'Professor',
            'enrollment': 'Enrollment',
            'teaches': 'Teaches'
        }
        table_name = table_map.get(tab, 'Student')
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
    
    conn.close()
    return render_template('index.html', active_tab=tab, data=data, departments=departments, is_viewer=False)

# ==================== VIEWER ONLY ROUTE ====================
@app.route('/viewer')
def viewer():
    tab = request.args.get('tab', 'dashboard')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT DEPARTMENT_ID, DEPT_NAME FROM Department")
    departments = cursor.fetchall()
    
    data = []
    if tab != 'dashboard':
        table_map = {
            'student': 'Student',
            'department': 'Department',
            'course': 'Course',
            'professor': 'Professor',
            'enrollment': 'Enrollment',
            'teaches': 'Teaches'
        }
        table_name = table_map.get(tab, 'Student')
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
    
    conn.close()
    return render_template('index.html', active_tab=tab, data=data, departments=departments, is_viewer=True)

# ==================== ADD (CREATE) ROUTES ====================
@app.route('/add_student', methods=['POST'])
def add_student():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Student (STUDENT_ID, NAME, DOB, EMAIL, PHONE, AGE, DEPARTMENT_ID) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (request.form['id'], request.form['name'], request.form['dob'], request.form['email'], request.form['phone'], request.form['age'], request.form['dept_id'])
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index', tab='student'))

@app.route('/add_department', methods=['POST'])
def add_department():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Department (DEPARTMENT_ID, DEPT_NAME, LOCATION) VALUES (%s, %s, %s)",
        (request.form['id'], request.form['name'], request.form['location'])
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index', tab='department'))

@app.route('/add_course', methods=['POST'])
def add_course():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Course (COURSE_ID, COURSE_NAME, CREDITS, DEPARTMENT_ID) VALUES (%s, %s, %s, %s)",
        (request.form['id'], request.form['name'], request.form['credits'], request.form['dept_id'])
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index', tab='course'))

@app.route('/add_professor', methods=['POST'])
def add_professor():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Professor (PROFESSOR_ID, NAME, EMAIL, PHONE, DEPARTMENT_ID) VALUES (%s, %s, %s, %s, %s)",
        (request.form['id'], request.form['name'], request.form['email'], request.form['phone'], request.form['dept_id'])
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index', tab='professor'))

@app.route('/add_enrollment', methods=['POST'])
def add_enrollment():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Enrollment (ENROLLMENT_ID, STUDENT_ID, COURSE_ID, GRADE) VALUES (%s, %s, %s, %s)",
        (request.form['id'], request.form['student_id'], request.form['course_id'], request.form['grade'])
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index', tab='enrollment'))

@app.route('/add_teaches', methods=['POST'])
def add_teaches():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Teaches (COURSE_ID, PROFESSOR_ID, SEMESTER, YEAR) VALUES (%s, %s, %s, %s)",
        (request.form['course_id'], request.form['prof_id'], request.form['semester'], request.form['year'])
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index', tab='teaches'))

# ==================== EDIT (UPDATE) ROUTES ====================
@app.route('/edit_student', methods=['POST'])
def edit_student():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Student SET NAME=%s, DOB=%s, EMAIL=%s, PHONE=%s, AGE=%s, DEPARTMENT_ID=%s WHERE STUDENT_ID=%s",
        (request.form['name'], request.form['dob'], request.form['email'], request.form['phone'], request.form['age'], request.form['dept_id'], request.form['id'])
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index', tab='student'))

@app.route('/edit_department', methods=['POST'])
def edit_department():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Department SET DEPT_NAME=%s, LOCATION=%s WHERE DEPARTMENT_ID=%s",
        (request.form['name'], request.form['location'], request.form['id'])
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index', tab='department'))

@app.route('/edit_course', methods=['POST'])
def edit_course():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Course SET COURSE_NAME=%s, CREDITS=%s, DEPARTMENT_ID=%s WHERE COURSE_ID=%s",
        (request.form['name'], request.form['credits'], request.form['dept_id'], request.form['id'])
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index', tab='course'))

@app.route('/edit_professor', methods=['POST'])
def edit_professor():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Professor SET NAME=%s, EMAIL=%s, PHONE=%s, DEPARTMENT_ID=%s WHERE PROFESSOR_ID=%s",
        (request.form['name'], request.form['email'], request.form['phone'], request.form['dept_id'], request.form['id'])
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index', tab='professor'))

@app.route('/edit_enrollment', methods=['POST'])
def edit_enrollment():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Enrollment SET STUDENT_ID=%s, COURSE_ID=%s, GRADE=%s WHERE ENROLLMENT_ID=%s",
        (request.form['student_id'], request.form['course_id'], request.form['grade'], request.form['id'])
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index', tab='enrollment'))

# ==================== DELETE ROUTES ====================
@app.route('/delete/<table_name>/<pk_column>/<record_id>/<return_tab>')
def delete_record(table_name, pk_column, record_id, return_tab):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name} WHERE {pk_column} = %s", (record_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index', tab=return_tab))

@app.route('/delete_teaches/<course_id>/<prof_id>/<semester>/<year>')
def delete_teaches(course_id, prof_id, semester, year):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM Teaches WHERE COURSE_ID=%s AND PROFESSOR_ID=%s AND SEMESTER=%s AND YEAR=%s",
        (course_id, prof_id, semester, year)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index', tab='teaches'))

if __name__ == '__main__':
    app.run(debug=True)