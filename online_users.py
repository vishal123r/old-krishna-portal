from flask import Blueprint, render_template
from datetime import datetime
from threading import Lock
import sqlite3

online_users_bp = Blueprint('online_users_bp', __name__, template_folder='templates')


class OnlineUsers:
    """
    Manage online users with multiple login sessions per user.
    Each user can have multiple active sessions identified by login datetime.
    """

    def __init__(self):
        # users: {username: [datetime_of_login1, datetime_of_login2, ...]}
        self.users = {}
        self.lock = Lock()

    def add_user(self, username, login_time=None):
        with self.lock:
            if username not in self.users:
                self.users[username] = []
            if not login_time:
                login_time = datetime.now().replace(microsecond=0)
            self.users[username].append(login_time)
        self.log_user_action(username, 'login')


    def remove_user(self, username, login_time_str=None):
        if not login_time_str:
            print("No login_time_str provided, no session removed.")
            return

        try:
            # Parse time with no microseconds
            login_time_obj = datetime.strptime(login_time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            print(f"Invalid datetime format: {login_time_str}")
            return

        with self.lock:
            if username in self.users:
                # Find a session that matches ignoring microseconds
                matched_session = None
                for session_time in self.users[username]:
                    # Compare datetime ignoring microseconds
                    if session_time.replace(microsecond=0) == login_time_obj:
                        matched_session = session_time
                        break
                
                if matched_session:
                    self.users[username].remove(matched_session)
                    if not self.users[username]:
                        del self.users[username]
                    self.log_user_action(username, 'logout')
                else:
                    print(f"Session {login_time_str} not found for user {username}.")
            else:
                print(f"User {username} not found in online users.")

    def get_online_users(self):
        """Return a copy of the current online users and their session times."""
        with self.lock:
            return {user: list(times) for user, times in self.users.items()}

    def format_user_info(self):
        """
        Format user data for display:
        returns list of tuples (username, latest_login_time_str, active_session_count)
        """
        with self.lock:
            result = []
            for user, times in self.users.items():
                session_count = len(times)
                latest_time = max(times)
                result.append((user, latest_time.strftime("%Y-%m-%d %H:%M:%S"), session_count))
            return result

    def log_user_action(self, username, action):
        """
        Log login or logout action into the database.
        Creates the table if it does not exist.
        """
        conn = sqlite3.connect('crm.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                action TEXT CHECK(action IN ('login', 'logout')) NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        cursor.execute('''
            INSERT INTO login_history (username, action)
            VALUES (?, ?)
        ''', (username, action))
        conn.commit()
        conn.close()


def get_login_logout_history():
    """
    Fetch login/logout history of last 2 months from database.
    """
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username, action, timestamp
        FROM login_history
        WHERE timestamp >= datetime('now', '-2 months')
        ORDER BY timestamp DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows


# Singleton instance
online_users = OnlineUsers()


@online_users_bp.route('/online-users')
def online_users_page():
    users = online_users.format_user_info()  # List of (user, login_time, session_count)
    history = get_login_logout_history()
    return render_template('online_users.html', users=users, datetime=datetime, history=history)


def initialize_login_history_table():
    """Ensure login_history table exists on startup."""
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            action TEXT CHECK(action IN ('login', 'logout')) NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()


# Initialize the table at module load
initialize_login_history_table()
