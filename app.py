import os
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = os.urandom(24)


def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='bdd_netinv'
    )

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usr_name = request.form['username']
        usr_password = request.form['password']
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM tbl_users 
            WHERE usr_name = %s AND usr_password = %s
        """, (usr_name, usr_password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['user'] = user['usr_name']
            return redirect(url_for('dashboard'))
        else:
            error = 'Usuario o contraseña incorrectos'
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_devices")
    devices = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('dashboard.html', devices=devices, user=session['user'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
