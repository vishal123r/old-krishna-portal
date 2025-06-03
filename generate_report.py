import logging
import os
from flask import Flask, render_template, request, send_from_directory, redirect
import sqlite3
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

def fetch_bill_data(billno):
    try:
        with sqlite3.connect("crm.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT khccode, name, mobile, firmname, amount, date, city, state, pincode FROM customers WHERE billno=?", (billno,))
            data = cursor.fetchone()
            if data:
                logging.debug(f"Data for Bill Number {billno}: {data}")
                return data
            else:
                logging.error(f"No data found for Bill Number: {billno}")
                return None
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return None

def generate_pdf(billno, logo_path, font, font_size, text_color, border):
    data = fetch_bill_data(billno)
    if not data:
        logging.error(f"No data found for Bill Number: {billno}")
        return None  # No data found

    # Create a folder for storing PDFs
    pdf_folder = "static/bills"
    os.makedirs(pdf_folder, exist_ok=True)
    
    filename = f"bill_report_{billno}.pdf"
    pdf_path = os.path.join(pdf_folder, filename)

    try:
        # Create the PDF document
        doc = SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=10, bottomMargin=40, leftMargin=40, rightMargin=40)
        story = []

        # Title (Centered)
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        title_style.fontSize = font_size + 4
        title_style.fontName = font
        title_style.textColor = text_color
        title_style.alignment = 1  # Centered
        story.append(Paragraph('Tax Invoice', title_style))

        # Create Company Info Box (Bordered Box 1)
        company_info = (
            f"Your Company Name\n"
            f"Address: Company Address\n"
            f"Pincode: 123456"
        )

        # Add logo next to Company Info (Logo on the left side)
        if logo_path:
            try:
                logo = Image(logo_path, width=60, height=60)  # Smaller logo size
                logo.hAlign = 'LEFT'
                story.append(Spacer(1, 10))
                story.append(logo)
            except Exception as e:
                logging.error(f"Error adding logo: {e}")
        
        # Create Customer Info Box (Bordered Box 2)
        customer_info = (
            f"{data[1]}\n"  # Customer Name
            f"{data[3]}\n"  # Firm Name
            f"{data[6]}\n"  # City
            f"{data[7]}\n"  # State
            f"{data[8] if data[8] else 'N/A'}\n"  # Pincode
            f"{data[2]}"  # Mobile
        )

        # Box Style (Set border for the boxes)
        box_style = TableStyle([ 
            ('BOX', (0, 0), (-1, -1), 1, colors.black),  # Border around each box
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Inner grid for each box
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Align text inside boxes to the left
            ('FONTNAME', (0, 0), (-1, -1), font),
            ('FONTSIZE', (0, 0), (-1, -1), font_size),
            ('TEXTCOLOR', (0, 0), (-1, -1), text_color),
        ])

        # Company Info Table (Box 1)
        company_table_data = [[company_info]]
        company_table = Table(company_table_data, colWidths=[300], rowHeights=[80])  # Smaller box width
        company_table.setStyle(box_style)
        story.append(Spacer(1, 10))
        story.append(company_table)

        # Customer Info Table (Box 2)
        customer_table_data = [[customer_info]]
        customer_table = Table(customer_table_data, colWidths=[300], rowHeights=[100])  # Smaller box width
        customer_table.setStyle(box_style)
        story.append(Spacer(1, 10))
        story.append(customer_table)

        # Footer (Left-Aligned)
        footer_text = "Computer Generated Tax Invoice!"
        footer_style = styles['Normal']
        footer_style.fontSize = font_size - 2
        footer_style.leading = 12
        footer_style.alignment = 0  # Left-aligned footer
        story.append(Spacer(1, 18))
        story.append(Paragraph(footer_text, footer_style))

        # Build the PDF
        doc.build(story)

        logging.info(f"PDF generated successfully for Bill Number: {billno} at {pdf_path}")
        return pdf_path
    except Exception as e:
        logging.error(f"Error generating PDF: {e}")
        return None

@app.route('/search_bill_page')
def search_bill_page():
    return render_template("search_bill_page.html")  # Display the customization page

@app.route('/search_bill', methods=['POST'])
def search_bill():
    billno = request.form.get('billno')
    font = request.form.get('font', 'Helvetica')
    font_size = int(request.form.get('font_size', 12))
    text_color = request.form.get('text_color', '#000000')  # Default color black
    border = 'border' in request.form  # Check if border is selected

    if not billno:
        logging.error("No bill number provided.")
        return "<h2>Please provide a bill number.</h2>"

    logging.debug(f"Received Bill Number: {billno}, Font: {font}, Font Size: {font_size}, Border: {border}")

    # Logo path (you can update this path as needed)
    logo_path = 'static/images/logo.png'  # Default path to the logo

    # Generate the PDF with the specified options
    pdf_path = generate_pdf(billno, logo_path, font, font_size, text_color, border)

    if pdf_path:
        logging.info(f"Sending file for download: {pdf_path}")
        return send_from_directory(directory='static/bills', path=os.path.basename(pdf_path), as_attachment=True)

    logging.error(f"Failed to generate PDF for Bill Number: {billno}")
    return "<h2>No data found for this Bill Number or error generating PDF.</h2>"

@app.route('/company_details', methods=['GET'])
def company_details_page():
    company_name = company_address = company_pincode = ''

    try:
        with sqlite3.connect("crm.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT company_name, company_address, company_pincode FROM company_details ORDER BY rowid DESC LIMIT 1")
            data = cursor.fetchone()
            if data:
                company_name, company_address, company_pincode = data
    except sqlite3.Error as e:
        logging.error(f"Error fetching company details: {e}")

    # Pass the company details to the template
    return render_template("company_details.html", company_name=company_name, company_address=company_address, company_pincode=company_pincode)

@app.route('/save_company_details', methods=['POST'])
def save_company_details():
    company_name = request.form.get('company_name')
    company_address = request.form.get('company_address')
    company_pincode = request.form.get('company_pincode')

    # Validate the input
    if not company_name or not company_address or not company_pincode:
        return "<h2>Please fill all the fields.</h2>"

    # Save the company details to the database
    try:
        with sqlite3.connect("crm.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO company_details (company_name, company_address, company_pincode)
                VALUES (?, ?, ?)
            """, (company_name, company_address, company_pincode))
            conn.commit()

        logging.info(f"Company details saved: {company_name}, {company_address}, {company_pincode}")
        return redirect('/company_details')  # Redirect to the details page to see the updated data
    except sqlite3.Error as e:
        logging.error(f"Error saving company details: {e}")
        return "<h2>Error saving company details.</h2>"


if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    app.run(host="0.0.0.0", port=1000, debug=True)
