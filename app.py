from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Keep this secret!

# Create the database and users table if they don't exist
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    if 'username' in session:
        username = session['username']
        return render_template('index.html', username=username)
    return render_template('index.html', username=None)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result and check_password_hash(result[0], password):
            session['username'] = username
            return redirect(url_for('welcome'))
        else:
            return "Invalid username or password"

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Username already exists"

    return render_template('register.html')

@app.route('/welcome')
def welcome():
    if 'username' in session:
        return render_template('welcome.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))
    
@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']

        # Fetch user info from the database
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user:
            return render_template('profile.html', user=user)
    return redirect(url_for('login'))
    
if __name__ == '__main__':
    app.run(debug=True)
