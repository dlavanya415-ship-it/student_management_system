from flask import Flask, render_template, request, redirect, session, send_from_directory
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        department TEXT,
        email TEXT,
        photo TEXT
    )""")

    conn.commit()
    conn.close()

init_db()

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def do_login():

    username = request.form['username']
    password = request.form['password']

    if username == "admin" and password == "1234":
        session['user'] = username
        return redirect('/dashboard')

    return "Invalid Login"

@app.route('/dashboard')
def dashboard():

    search = request.args.get("search")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    if search:
        cur.execute("SELECT * FROM students WHERE name LIKE ?",('%'+search+'%',))
    else:
        cur.execute("SELECT * FROM students")

    students = cur.fetchall()

    conn.close()

    return render_template("dashboard.html", students=students)

@app.route('/add', methods=['POST'])
def add():

    name = request.form['name']
    department = request.form['department']
    email = request.form['email']

    photo = request.files['photo']
    filename = photo.filename
    photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""INSERT INTO students(name,department,email,photo)
                VALUES(?,?,?,?)""",
                (name,department,email,filename))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

@app.route('/delete/<int:id>')
def delete(id):

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM students WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = sqlite3.connect("database.db")  # Use the correct database
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        department = request.form['department']
        email = request.form['email']

        # Handle photo update if provided
        photo = request.files.get('photo')
        if photo and photo.filename:
            filename = photo.filename
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cur.execute("UPDATE students SET name=?, department=?, email=?, photo=? WHERE id=?",
                        (name, department, email, filename, id))
        else:
            cur.execute("UPDATE students SET name=?, department=?, email=? WHERE id=?",
                        (name, department, email, id))

        conn.commit()
        conn.close()
        return redirect('/dashboard')

    # GET request: fetch and display
    cur.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cur.fetchone()
    conn.close()

    return render_template("edit.html", student=student)

# New route to serve uploaded images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Remove the old separate update route as it's now handled in edit

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)