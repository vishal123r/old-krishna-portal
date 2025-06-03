import sqlite3

def analyze_customers():
    conn = sqlite3.connect("crm.db")
    cursor = conn.cursor()

    # Fetch all customers with relevant details
    cursor.execute("SELECT id, firmname, amount, total_received, payment_status, date, category FROM customers")
    customers = cursor.fetchall()

    results = []
    for customer in customers:
        customer_id, firmname, amount, received, payment_status, order_date, business_type = customer
        amount = amount or 0  # Ensure no None values for amount
        received = received or 0  # Ensure no None values for received amount

        # Calculate Payment Ratio (ensure we handle zero correctly)
        if amount > 0:  # Prevent division by zero
            payment_ratio = received / amount
        else:
            payment_ratio = 0  # If amount is 0, treat it as no payment

        # Payment Categorization Logic (Based on Payment Ratio)
        if payment_ratio >= 0.9:
            payment_category = "Genuine"
            reason = f"Payment ratio is {payment_ratio:.2%}, meaning 90% or more of the total amount has been paid."
        elif payment_ratio < 0.5:
            payment_category = "Risky"
            reason = f"Payment ratio is {payment_ratio:.2%}, meaning less than 50% of the total amount has been paid."
        else:
            payment_category = "Average"
            reason = f"Payment ratio is {payment_ratio:.2%}, meaning 50-90% of the total amount has been paid."

        # Further check for payment status: If payment is pending or overdue
        if payment_status == "Pending":
            payment_category = "Risky"
            reason += f" (Payment status is 'Pending', which makes this risky.)"

        # Append the dictionary of results with calculated category
        results.append({
            "id": customer_id,
            "firmname": firmname,
            "business_type": business_type,  # Original business category
            "payment_category": payment_category,  # Updated to use payment_category
            "payment_category_reason": reason,
            "received_amount": received,
            "total_due": amount - received,
            "last_payment_date": order_date  # Use last payment date if available
        })

    conn.close()
    return results
