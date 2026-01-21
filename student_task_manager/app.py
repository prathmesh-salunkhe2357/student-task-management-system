from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

app = Flask(__name__)
app.secret_key = "task_secret"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Prs@7581",  
    database="student_tasks"
)
cursor = db.cursor(dictionary=True)



@app.route('/')
def home():
    if 'user_id' in session:
        if session['role'] == 'admin':
            return redirect('/admin')
        else:
            return redirect('/student')
    return redirect('/login')


@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        hashed_password = generate_password_hash(password)
        try:
            cursor.execute("INSERT INTO users (name,email,password,role) VALUES (%s,%s,%s,%s)", 
                           (name,email,hashed_password,role))
            db.commit()
            flash("Signup successful! Please login.", "success")
            return redirect('/login')
        except mysql.connector.Error:
            flash("Email already exists!", "error")
            return redirect('/signup')
    return render_template('signup.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = cursor.fetchone()
        if user:
            if check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['role'] = user['role']
                return redirect('/')
            else:
                flash("Incorrect password!", "error")
        else:
            flash("Email not registered!", "error")
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/admin')
def admin_dashboard():
    if 'role' in session and session['role']=='admin':
        cursor.execute("SELECT tasks.id, tasks.title, tasks.due_date, tasks.status, users.name FROM tasks JOIN users ON tasks.student_id=users.id")
        tasks = cursor.fetchall()
        cursor.execute("SELECT * FROM users WHERE role='student'")
        students = cursor.fetchall()
        return render_template('admin_dashboard.html', tasks=tasks, students=students)
    return redirect('/login')


@app.route('/add_task', methods=['GET','POST'])
def add_task():
    if 'role' in session and session['role']=='admin':
        if request.method=='POST':
            title = request.form['title']
            due_date = request.form['due_date']
            student_id = request.form['student_id']
            cursor.execute("INSERT INTO tasks (title,due_date,student_id) VALUES (%s,%s,%s)", (title,due_date,student_id))
            db.commit()
            flash("Task added successfully!", "success")
            return redirect('/admin')
        cursor.execute("SELECT * FROM users WHERE role='student'")
        students = cursor.fetchall()
        return render_template('add_task.html', students=students)
    return redirect('/login')


@app.route('/complete_task/<int:task_id>')
def complete_task(task_id):
    cursor.execute("UPDATE tasks SET status='Completed' WHERE id=%s",(task_id,))
    db.commit()
    flash("Task marked as completed!", "success")
    return redirect('/admin')


@app.route('/student')
def student_dashboard():
    if 'role' in session and session['role']=='student':
        today = date.today()
        cursor.execute("SELECT * FROM tasks WHERE student_id=%s", (session['user_id'],))
        tasks = cursor.fetchall()
        for task in tasks:
            if task['status']=='In Progress' and task['due_date'] < today:
                cursor.execute("UPDATE tasks SET status='Overdue' WHERE id=%s",(task['id'],))
                db.commit()
        cursor.execute("SELECT * FROM tasks WHERE student_id=%s", (session['user_id'],))
        tasks = cursor.fetchall()
        return render_template('student_dashboard.html', tasks=tasks)
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)

