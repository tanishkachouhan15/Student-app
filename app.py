
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn



def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
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

        # 🔥 Get next ID manually
        cur.execute("SELECT COUNT(*) FROM students")
        next_id = cur.fetchone()[0] + 1

        cur.execute(
            "INSERT INTO students (id, name, age, course) VALUES (?, ?, ?, ?)",
            (next_id, name, age, course)
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

    
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()

    
    cur.execute("DELETE FROM students")

    
    for i, student in enumerate(students, start=1):
        cur.execute(
            "INSERT INTO students (id, name, age, course) VALUES (?, ?, ?, ?)",
            (i, student['name'], student['age'], student['course'])
        )

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



if __name__ == '__main__':
    app.run(debug=True)