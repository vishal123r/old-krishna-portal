from flask_mail import Message
import pandas as pd
from io import BytesIO
from datetime import datetime

class EmailHelper:
    def __init__(self, app, mail):
        self.app = app
        self.mail = mail

    def send_email(self, subject, recipients, body, attachment=None):
        msg = Message(subject, recipients=[recipients], body=body)
        msg.sender = 'krishnahomecare27@gmail.com'

        if attachment:
            msg.attach("weekly_entries.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", attachment)

        try:
            self.mail.send(msg)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")

    def create_excel_report(self, rows):
        columns = [
            "KHC Code", "Bill No", "Bilty No", "Firm Name", "City", 
            "Mobile No", "Amount", "Extra Column"
        ]
        
        # Prepare formatted rows
        formatted_rows = []
        for row in rows:
            mobile_combined = f"{row[5]} / {row[6]}" if row[6] else row[5]
            formatted_date = datetime.strptime(row[8], "%Y-%m-%d").strftime("%d/%m/%Y")
            formatted_rows.append([row[0], row[1], row[2], row[3], row[4], mobile_combined, row[7], ""])

        # Convert data to pandas DataFrame
        df = pd.DataFrame(formatted_rows, columns=columns)

        # Capitalize all text in the DataFrame
        df = df.applymap(lambda x: x.upper() if isinstance(x, str) else x)

        # Save to BytesIO object (in-memory file)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Weekly Entries')

        output.seek(0)
        return output
