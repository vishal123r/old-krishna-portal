from flask import render_template, request
import sqlite3

class AdjustmentEntries:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def get_adjustments_for_bill(self, billno):
        # Fetch the main bill and its associated cross-adjustments based on the billno
        query = '''
            SELECT id, khccode, billno, biltyno, date, firmname, mobile, amount, 
                   receive_amount, payment_status
            FROM customers
            WHERE billno = ?
        '''
        cursor = self.db_connection.cursor()
        cursor.execute(query, (billno,))
        adjustment_entries = cursor.fetchall()
        return adjustment_entries

    def get_adjustment_entries(self):
        # Fetch adjustments where the amount does not match the received amount
        query = '''
            SELECT id, khccode, billno, biltyno, date, firmname, mobile, amount, 
                   receive_amount, payment_status
            FROM customers
            WHERE amount != receive_amount
        '''
        cursor = self.db_connection.cursor()
        cursor.execute(query)
        adjustment_entries = cursor.fetchall()
        return adjustment_entries

    def get_adjustments_by_date_range(self, start_date, end_date):
        # Fetch adjustments within a specific date range
        query = '''
            SELECT id, khccode, billno, biltyno, date, firmname, mobile, amount, 
                   receive_amount, payment_status
            FROM customers
            WHERE amount != receive_amount AND date BETWEEN ? AND ?
        '''
        cursor = self.db_connection.cursor()
        cursor.execute(query, (start_date, end_date))
        adjustment_entries = cursor.fetchall()
        return adjustment_entries

    def get_adjustments_by_status(self, status):
        # Fetch adjustments based on the payment status
        query = '''
            SELECT id, khccode, billno, biltyno, date, firmname, mobile, amount, 
                   receive_amount, payment_status
            FROM customers
            WHERE amount != receive_amount AND payment_status = ?
        '''
        cursor = self.db_connection.cursor()
        cursor.execute(query, (status,))
        adjustment_entries = cursor.fetchall()
        return adjustment_entries

# Flask routes for adjustment entries
def init_routes(app):
    @app.route('/adjustments')
    def show_adjustments():
        conn = sqlite3.connect('crm.db')
        adjustment_obj = AdjustmentEntries(conn)
        
        # Get all adjustments (only those with amount != receive_amount)
        adjustment_entries = adjustment_obj.get_adjustment_entries()
        
        # Render the adjustments in a template (adjustments.html)
        return render_template('adjustments.html', adjustments=adjustment_entries)

# Flask route for viewing adjustments based on billno
    @app.route('/adjustments/view/<billno>')
    def view_adjustments(billno):
        conn = sqlite3.connect('crm.db')
        adjustment_obj = AdjustmentEntries(conn)

        # Fetch adjustments related to the specific bill (using billno)
        adjustment_entries = adjustment_obj.get_adjustments_for_bill(billno)

        # Render adjustments for the selected bill, showing both the main bill and cross-adjustments
        return render_template('adjustments_view.html', adjustments=adjustment_entries, billno=billno)
