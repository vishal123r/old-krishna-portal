from flask import Blueprint, render_template, session, redirect, url_for

user_activity_bp = Blueprint('user_activity', __name__, template_folder='templates')

@user_activity_bp.route('/activity')
def activity():
    if 'username' not in session:
        return redirect(url_for('user_activity.login'))
    return render_template('activity.html', username=session['username'], login_time=session.get('login_time', 'Unknown'))

@user_activity_bp.route('/logout')
def logout():
    session.clear()
    return "Logged out due to inactivity. <a href='/user_activity/login'>Login again</a>"

@user_activity_bp.route('/login')
def login():
    # Demo login logic
    session['username'] = 'krishnahomecare'
    from datetime import datetime
    session['login_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return redirect(url_for('user_activity.activity'))
