import sqlite3
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO
from flask_mail import Message, Mail
from flask import Flask, current_app as app, render_template, request, send_file

# Initialize Flask app
app = Flask(__name__)

# Flask-Mail setup (inside the app context)
def create_mail():
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = 'krishnahomecare27@gmail.com'
    app.config['MAIL_PASSWORD'] = 'your_email_password_or_app_password'
    app.config['MAIL_DEFAULT_SENDER'] = 'krishnahomecare27@gmail.com'

    mail = Mail(app)
    return mail

# Ensure Flask-Mail is initialized inside app context
with app.app_context():
    mail = create_mail()

# Helper function to get the database connection
def get_db_connection():
    conn = sqlite3.connect('auto.db')  # Replace with your actual database path
    conn.row_factory = sqlite3.Row
    return conn

# Function to fetch weekly entries
def fetch_weekly_entries():
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)  # Sunday

    start_date = start_of_week.strftime('%Y-%m-%d')
    end_date = end_of_week.strftime('%Y-%m-%d')

    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
        SELECT khccode, billno, biltyno, firmname, city, mobile, additional_mobile, amount, date
        FROM customers
        WHERE date BETWEEN ? AND ?
        ORDER BY date DESC
    '''
    cursor.execute(query, (start_date, end_date))
    rows = cursor.fetchall()
    conn.close()

    formatted_rows = []
    for row in rows:
        mobile_combined = f"{row[5]} / {row[6]}" if row[6] else row[5]
        formatted_date = datetime.strptime(row[8], "%Y-%m-%d").strftime("%d/%m/%Y")

        formatted_rows.append([row[0], row[1], row[2], formatted_date, row[3], row[4], mobile_combined, row[7], ""])
    
    return formatted_rows, start_date, end_date

# Function to generate and return the Excel file
def generate_excel_file(formatted_rows):
    columns = [
        "KHC Code", "Bill No", "Bilty No", "Date", "Firm Name", 
        "City", "Mobile No", "Amount", "Extra Column"
    ]

    df = pd.DataFrame(formatted_rows, columns=columns)
    df = df.applymap(lambda x: x.upper() if isinstance(x, str) else x)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Weekly Entries')

    output.seek(0)
    return output

# Function to send email with attachment
def send_email(subject, recipients, body, attachment):
    msg = Message(subject, recipients=[recipients], body=body)
    msg.sender = 'krishnahomecare27@gmail.com'

    if attachment:
        msg.attach("weekly_entries.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", attachment)

    try:
        mail.send(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# Export and send weekly entries
def export_and_send_weekly_entries():
    formatted_rows, start_date, end_date = fetch_weekly_entries()
    excel_file = generate_excel_file(formatted_rows)

    send_email(
        subject="Weekly Entries Report",
        recipients="rkvyas555555@gmail.com",  # Recipient email address
        body="Hello, Please find the weekly entries report attached.",
        attachment=excel_file.read()  # Attach the Excel file
    )

    return send_file(
        excel_file,
        as_attachment=True,
        download_name="weekly_entries.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route('/weekly_entries', methods=['GET'])
def weekly_entries():
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)  # Sunday

    start_date = start_of_week.strftime('%Y-%m-%d')
    end_date = end_of_week.strftime('%Y-%m-%d')

    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()

    query = '''
        SELECT khccode, billno, biltyno, firmname, city, mobile, additional_mobile, amount, date
        FROM customers
        WHERE date BETWEEN ? AND ?
        ORDER BY date DESC
    '''
    cursor.execute(query, (start_date, end_date))
    rows = cursor.fetchall()
    conn.close()

    columns = [
        "KHC Code", "Bill No", "Bilty No", "Date", "Firm Name", 
        "City", "Mobile No", "Amount", "Extra Column"
    ]

    formatted_rows = []
    for row in rows:
        mobile_combined = f"{row[5]} / {row[6]}" if row[6] else row[5]
        formatted_date = datetime.strptime(row[8], "%Y-%m-%d").strftime("%d/%m/%Y")

        formatted_rows.append([row[0], row[1], row[2], formatted_date, row[3], row[4], mobile_combined, row[7], ""])

    if request.args.get("download") == "true":
        df = pd.DataFrame(formatted_rows, columns=columns)
        df = df.applymap(lambda x: x.upper() if isinstance(x, str) else x)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Weekly Entries')

        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="weekly_entries.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    return render_template(
        'weekly_entries.html',
        entries=formatted_rows,
        start_date=start_date,
        end_date=end_date
    )

@app.route('/export_weekly_entries', methods=['GET'], endpoint='export_weekly_entries')
def export_weekly_entries():
    # Your export logic here
    return export_and_send_weekly_entries()
