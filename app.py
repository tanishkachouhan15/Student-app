from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# ✅ Fix database path for deployment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "students.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            course TEXT
        )
    ''')

    conn.commit()
    conn.close()


init_db()


@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    search = request.form.get('search')

    if search:
        cur.execute("SELECT * FROM students WHERE name LIKE ?", ('%' + search + '%',))
    else:
        cur.execute("SELECT * FROM students")

    students = cur.fetchall()
    conn.close()

    return render_template('index.html', students=students)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        course = request.form['course']

        conn = get_db_connection()
        cur = conn.cursor()

        # ✅ AUTO ID (fixed)
        cur.execute(
            "INSERT INTO students (name, age, course) VALUES (?, ?, ?)",
            (name, age, course)
        )

        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('add.html')


@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        course = request.form['course']

        cur.execute(
            "UPDATE students SET name = ?, age = ?, course = ? WHERE id = ?",
            (name, age, course, id)
        )

        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    cur.execute("SELECT * FROM students WHERE id = ?", (id,))
    student = cur.fetchone()
    conn.close()

    return render_template('update.html', student=student)


# ✅ IMPORTANT FOR RENDER
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)