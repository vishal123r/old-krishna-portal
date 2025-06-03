from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3

# Blueprint for admin
admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')

DATABASE = 'crm.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Root route redirects to admin login
@admin_bp.route('/admin', methods=['GET'])
def admin_home():
    return redirect(url_for('admin.admin_login'))

# Admin login route
@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    users = {'krishnahomecare': 'Krishna@1212'}  # Hardcoded user credentials

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users and users[username] == password:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('admin.admin_login'))

    return render_template('admin_login.html')

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize DB tables on blueprint load
init_db()

# Admin dashboard
@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash('Please login first.', 'error')
        return redirect(url_for('admin.admin_login'))

    return render_template('admin_dashboard.html', username=session.get('admin_username'))

# Admin logout
@admin_bp.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.admin_login'))

# Manage customers page
@admin_bp.route('/admin/manage_customers')
def manage_customers():
    if not session.get('admin_logged_in'):
        flash('Please login first.', 'error')
        return redirect(url_for('admin.admin_login'))

    conn = get_db_connection()
    customers = conn.execute('SELECT * FROM customers').fetchall()
    conn.close()

    return render_template('manage_customers.html', customers=customers)

# View reports page
@admin_bp.route('/admin/view_reports')
def view_reports():
    if not session.get('admin_logged_in'):
        flash('Please login first.', 'error')
        return redirect(url_for('admin.admin_login'))

    conn = get_db_connection()
    reports = conn.execute('SELECT * FROM reports').fetchall()
    conn.close()

    return render_template('view_reports.html', reports=reports)

# Settings page
@admin_bp.route('/admin/settings')
def settings():
    if not session.get('admin_logged_in'):
        flash('Please login first.', 'error')
        return redirect(url_for('admin.admin_login'))

    return render_template('settings.html')
