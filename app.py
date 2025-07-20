import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask import *
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey123'

DATABASE = 'sqlite_database/tips_calculator.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    #  database for users
    c.execute('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    # database for tips
    c.execute('''CREATE TABLE IF NOT EXISTS tips (id INTEGER PRIMARY KEY, bill REAL, tip_percent REAL, people INTEGER, tip_amount REAL, total_amount REAL, per_person REAL, created_at TEXT )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        session['username'] = None
        return redirect('/login')  # Redirect if not logged in

    # Now this part only runs if user IS logged in:

    if request.method == 'POST':
        bill = float(request.form['bill'])
        tip_percent = float(request.form['tip_percent'])
        people = int(request.form['people'])

        tip_amount = bill * (tip_percent / 100)
        total_amount = bill + tip_amount
        per_person = total_amount / people

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO tips (bill, tip_percent, people, tip_amount, total_amount, per_person, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (bill, tip_percent, people, tip_amount, total_amount, per_person, datetime.now()))
        conn.commit()
        conn.close()

        return render_template('index.html', tip=tip_amount, total=total_amount, per_person=per_person)

    return render_template('index.html')

@app.route('/history')
def history():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM tips ORDER BY created_at DESC LIMIT 10")
    data = c.fetchall()
    conn.close()
    return render_template('history.html', records=data)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute('''
                INSERT INTO users (username, password)
                VALUES (?, ?)
            ''', (username, hashed_password))
            conn.commit()
            conn.close()
            flash('Registration successful! Please login.', 'success')
        except sqlite3.IntegrityError:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute('''
                SELECT * FROM users WHERE username = ?
            ''', (username,))
            user = c.fetchone()
            conn.close()
            if user:
                flash('Username already exists. Please choose a different one.', 'danger')
            else:
                flash('Registration failed. Please try again.', 'danger')
            conn.close()
        return redirect('/')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            SELECT * FROM users WHERE username = ?
        ''', (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect('/')
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()  # Removes all session data
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))  # Redirect back to login page
if __name__ == '__main__':
    init_db()
    app.run(debug=True)

