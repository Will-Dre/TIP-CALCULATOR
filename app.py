from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)
DATABASE = 'sqlite_database/tips_calculator.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tips (
            id INTEGER PRIMARY KEY,
            bill REAL,
            tip_percent REAL,
            people INTEGER,
            tip_amount REAL,
            total_amount REAL,
            per_person REAL,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
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
    c.execute("SELECT * FROM tips ORDER BY created_at DESC")
    data = c.fetchall()
    conn.close()
    return render_template('history.html', records=data)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)


