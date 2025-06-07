import csv
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from datetime import datetime
import random
import os
import pytesseract
from PIL import Image
import re
import requests
import io
from pdf2image import convert_from_bytes
import functools
import logging
import os

add_customer_bp = Blueprint('add_customer_bp', __name__)

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('crm.db')
    conn.row_factory = sqlite3.Row
    return conn

# Generate unique KHC code for customer
def generate_unique_khc_code(conn):
    cursor = conn.cursor()
    while True:
        code_number = str(random.randint(1000, 9999))
        code = f"KHC{code_number}"
        cursor.execute("SELECT 1 FROM customers WHERE khccode = ?", (code,))
        if not cursor.fetchone():
            return code

# Check if any mobile number conflicts with other customers
def mobile_conflicts_exist(conn, khc_code, all_mobiles):
    cursor = conn.cursor()
    placeholders = ','.join('?' for _ in all_mobiles)
    query = f'''
        SELECT mobile, khccode FROM (
            SELECT mobile AS mobile, khccode FROM customers
            UNION ALL
            SELECT mobile_number AS mobile, c.khccode FROM additional_mobiles am
            JOIN customers c ON am.customer_id = c.id
        )
        WHERE mobile IN ({placeholders}) AND khccode != ?
    '''
    cursor.execute(query, (*all_mobiles, khc_code))
    return cursor.fetchall()

@add_customer_bp.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    customer = {}
    conn = None
    try:
        conn = get_db_connection()

        if request.method == 'POST':
            # Get main and additional mobiles
            mobile = request.form.get('mobile', '').strip()
            additional_mobiles = [m.strip() for m in request.form.getlist('additional_mobile[]') if m.strip()]
            all_mobiles = [mobile] + additional_mobiles

            # Check if any mobile already exists and get its khccode
            cursor = conn.cursor()
            placeholders = ','.join('?' for _ in all_mobiles)
            query = f'''
                SELECT khccode FROM (
                    SELECT mobile AS mobile, khccode FROM customers
                    UNION ALL
                    SELECT mobile_number AS mobile, c.khccode FROM additional_mobiles am
                    JOIN customers c ON am.customer_id = c.id
                )
                WHERE mobile IN ({placeholders})
                LIMIT 1
            '''
            cursor.execute(query, all_mobiles)
            existing = cursor.fetchone()
            khc_code = existing['khccode'] if existing else generate_unique_khc_code(conn)

            # Validate & extract other fields
            bill_no = request.form.get('billno', '').strip()
            bilty_no = request.form.get('biltyno', '').strip()

            date_str = request.form.get('date', datetime.now().strftime('%d/%m/%Y')).replace('-', '/')
            try:
                date = datetime.strptime(date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
            except ValueError:
                flash('Invalid date format. Use DD/MM/YYYY.', 'error')
                return render_template('add_customer.html', current_date=datetime.now().strftime('%d/%m/%Y'), customer=customer, khccode=khc_code)

            name = request.form.get('name', '').strip()
            firm_name = request.form.get('firmname', '').strip()
            state = request.form.get('state', '').strip()
            city = request.form.get('city', '').strip()
            category = request.form.get('category', '').strip()
            district = request.form.get('district', '').strip()
            tehsil = request.form.get('tehsil', '').strip()

            try:
                pincode_str = request.form.get('pincode', '').strip()
                pincode = int(pincode_str) if pincode_str else None
            except ValueError:
                flash('Invalid pincode.', 'error')
                return render_template('add_customer.html', current_date=datetime.now().strftime('%d/%m/%Y'), customer=customer, khccode=khc_code)

            if not mobile:
                flash('Main mobile number is required.', 'error')
                return render_template('add_customer.html', current_date=datetime.now().strftime('%d/%m/%Y'), customer=customer, khccode=khc_code)

            try:
                amount_str = request.form.get('amount', '0').strip()
                amount = float(amount_str) if amount_str else 0.0
            except ValueError:
                flash('Invalid amount.', 'error')
                return render_template('add_customer.html', current_date=datetime.now().strftime('%d/%m/%Y'), customer=customer, khccode=khc_code)

            reference_name = request.form.get('reference_name', '').strip()
            transport_name = request.form.get('transport_name', '').strip()
            transport_number = request.form.get('transport_number', '').strip()

            # Check for mobile conflicts with other customers
            conflicts = mobile_conflicts_exist(conn, khc_code, all_mobiles)
            if conflicts:
                conflict_msgs = [f"Mobile number {row['mobile']} linked with KHC Code {row['khccode']}" for row in conflicts]
                flash("Conflict: " + "; ".join(conflict_msgs), 'error')
                return render_template('add_customer.html', current_date=datetime.now().strftime('%d/%m/%Y'), customer=customer, khccode=khc_code)

            # Insert new customer
            cursor.execute('''
                INSERT INTO customers 
                (khccode, billno, biltyno, date, name, firmname, state, city, pincode, mobile, amount, reference_name, category, district, tehsil, transport_name, transport_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (khc_code, bill_no, bilty_no, date, name, firm_name, state, city, pincode, mobile, amount, reference_name, category, district, tehsil, transport_name, transport_number))

            customer_id = cursor.lastrowid

            # Insert additional mobiles
            for add_mobile in additional_mobiles:
                cursor.execute('''
                    INSERT INTO additional_mobiles (customer_id, mobile_number)
                    VALUES (?, ?)
                ''', (customer_id, add_mobile))

            conn.commit()
            flash('Customer added successfully!', 'success')
            return redirect(url_for('add_customer_bp.add_customer'))

        # For GET request render form with current date
        return render_template('add_customer.html', current_date=datetime.now().strftime('%d/%m/%Y'), customer=customer, khccode='')

    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"Unexpected error: {str(e)}", "error")
        return render_template('add_customer.html', current_date=datetime.now().strftime('%d/%m/%Y'), customer=customer, khccode='')

    finally:
        if conn:
            conn.close()


# AJAX endpoint to check if mobile exists and fetch related data
@add_customer_bp.route('/add_customer/check_mobile_khc', methods=['POST'])
def check_mobile_khc():
    conn = None
    try:
        data = request.get_json()
        main_mobile = data.get('mobile', '').strip()
        additional_mobiles = data.get('additional_mobiles', [])

        def clean_mobile(m):
            return ''.join(filter(str.isdigit, m))

        main_mobile = clean_mobile(main_mobile)
        additional_mobiles = [clean_mobile(mob) for mob in additional_mobiles]

        # Validate main mobile number length and digits
        if len(main_mobile) != 10 or not main_mobile.isdigit():
            return jsonify({'status': 'error', 'message': 'Invalid main mobile number format. Must be exactly 10 digits.'})

        for mob in additional_mobiles:
            if len(mob) != 10 or not mob.isdigit():
                return jsonify({'status': 'error', 'message': f'Invalid additional mobile number format: {mob}. Must be exactly 10 digits.'})

        all_mobiles = [main_mobile] + additional_mobiles

        conn = get_db_connection()
        cursor = conn.cursor()

        placeholders = ','.join('?' for _ in all_mobiles)
        query = f'''
            SELECT mobile, khccode FROM (
                SELECT mobile AS mobile, khccode FROM customers
                UNION ALL
                SELECT mobile_number AS mobile, c.khccode FROM additional_mobiles am
                JOIN customers c ON am.customer_id = c.id
            )
            WHERE mobile IN ({placeholders})
            LIMIT 1
        '''
        cursor.execute(query, all_mobiles)
        existing = cursor.fetchone()

        if existing:
            khc_code = existing['khccode']
            cursor.execute("SELECT * FROM customers WHERE khccode = ?", (khc_code,))
            customer = cursor.fetchone()

            cursor.execute("SELECT mobile_number FROM additional_mobiles WHERE customer_id = (SELECT id FROM customers WHERE khccode = ?)", (khc_code,))
            additional_mobs = [row['mobile_number'] for row in cursor.fetchall()]

            if customer:
                return jsonify({
                    'status': 'exists',
                    'khccode': khc_code,
                    'main_mobile': customer['mobile'],
                    'additional_mobiles': additional_mobs,
                    'customer': {
                        'billno': customer['billno'],
                        'biltyno': customer['biltyno'],
                        'date': customer['date'],
                        'name': customer['name'],
                        'firmname': customer['firmname'],
                        'state': customer['state'],
                        'city': customer['city'],
                        'pincode': customer['pincode'],
                        'amount': customer['amount'],
                        'reference_name': customer['reference_name'],
                        'category': customer['category'],
                        'district': customer['district'],
                        'tehsil': customer['tehsil'],
                        'transport_name': customer['transport_name'],
                        'transport_number': customer['transport_number']
                    }
                })
            else:
                new_code = generate_unique_khc_code(conn)
                return jsonify({'status': 'new', 'khccode': new_code})
        else:
            new_code = generate_unique_khc_code(conn)
            return jsonify({'status': 'new', 'khccode': new_code})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

    finally:
        if conn:
            conn.close()

# ✅ Transport data cache
_transport_cache = {}

def load_transport_data():
    global _transport_cache
    _transport_cache.clear()

    csv_path = os.path.join(os.path.dirname(__file__), 'transport_data.csv')

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        # Read first line, clean all header names (remove spaces and uppercase)
        raw_headers = next(csvfile).strip().split(',')
        headers = [h.strip().upper() for h in raw_headers]

        # Go back to start and re-read with cleaned headers
        csvfile.seek(0)
        reader = csv.DictReader(csvfile, fieldnames=headers)
        next(reader)  # Skip header

        for row in reader:
            # Clean all keys and values (remove extra spaces)
            clean_row = {k.strip().upper(): (v.strip() if v else '') for k, v in row.items()}

            city_key = clean_row.get('CITY', '').lower()
            if not city_key:
                continue

            if city_key not in _transport_cache:
                _transport_cache[city_key] = []

            _transport_cache[city_key].append({
                'transport_name': clean_row.get('TRANSPORT NAME', ''),
                'transport_number': clean_row.get('NUMBER', '')
            })

# ✅ Load on startup
load_transport_data()

@add_customer_bp.route('/get_transports_by_city', methods=['GET'])
def get_transports_by_city():
    try:
        city = request.args.get('city', '').strip().lower()
        if not city:
            return jsonify({'status': 'error', 'message': 'City parameter missing'}), 400

        transports = _transport_cache.get(city, [])
        return jsonify({'status': 'success', 'transports': transports})

    except Exception as e:
        print(f"❌ Error in get_transports_by_city: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


# Path to tesseract executable (adjust if needed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache for pincode lookups
pincode_cache = {}

def cache_results(func):
    @functools.wraps(func)
    def wrapper(arg):
        if arg in pincode_cache:
            logger.info(f"Using cached location for pincode {arg}")
            return pincode_cache[arg]
        result = func(arg)
        pincode_cache[arg] = result
        return result
    return wrapper

@cache_results
def get_location_from_pincode(pincode):
    """Fetch location details from pincode API."""
    try:
        response = requests.get(f'https://api.postalpincode.in/pincode/{pincode}', timeout=5)
        response.raise_for_status()
        data = response.json()
        if data and data[0]['Status'] == 'Success':
            post = data[0]['PostOffice'][0]
            return {
                'state': post.get('State', ''),
                'district': post.get('District', ''),
                'tehsil': post.get('Taluk', ''),
                'city': post.get('Block', '')
            }
    except Exception as e:
        logger.error(f"Error fetching location for pincode {pincode}: {e}")
    return {'state': '', 'district': '', 'tehsil': '', 'city': ''}

def extract_khc_code(lines):
    for line in lines:
        line = line.strip().upper()
        if 'KRISHNA HOME CARE' in line:
            return 'KHC'
        elif 'KRISHNA TRADERS' in line:
            return 'KT'
    return ''

def extract_invoice_no(lines):
    for i, line in enumerate(lines):
        match = re.search(r'invoice\s*no\.?\s*[:\-]?\s*([A-Za-z0-9\-]+)', line, re.I)
        if match:
            val = match.group(1).strip()
            if val.lower() not in ['dated', 'date', '']:
                return val
            if i + 1 < len(lines):
                nums = re.findall(r'\b\d+\b', lines[i + 1])
                if nums:
                    return nums[0]
    for line in lines:
        if line.strip().isdigit() and len(line.strip()) > 2:
            return line.strip()
    return ''

def extract_date(line, next_line=''):
    date_patterns = [
        r'\b\d{1,2}[-/][A-Za-z]{3,9}[-/]\d{2,4}\b',
        r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',
        r'\b\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4}\b',
    ]
    for pattern in date_patterns:
        m = re.search(pattern, line)
        if m:
            return m.group(0)
        if next_line:
            m_next = re.search(pattern, next_line)
            if m_next:
                return m_next.group(0)
    return ''

def extract_biltyno(line):
    match = re.search(r'(dispatch doc no|bilty no)[^\d]*(\d+)', line, re.I)
    if match:
        return match.group(2)
    fallback = re.findall(r'\d{4,}', line)
    return fallback[0] if fallback else ''

def extract_firmname_name(line, next_line):
    firmname = ''
    name = ''
    if next_line:
        if ',' in next_line:
            parts = [p.strip() for p in next_line.split(',') if p.strip()]
            if len(parts) >= 2:
                firmname = parts[0]
                name = parts[-1]
        else:
            words = next_line.split()
            if len(words) >= 2:
                firmname = ' '.join(words[:-1])
                name = words[-1]
    return firmname, name

def extract_any_pincode(lines):
    for line in lines:
        match = re.search(r'\b[1-9]\d{5}\b', line)
        if match:
            return match.group(0)
    return ''

def extract_mobile(lines):
    for line in lines:
        if 'contact' in line.lower():
            mobiles = re.findall(r'\b[789]\d{9}\b', line)
            if mobiles:
                return mobiles[0]
    mobiles_all = []
    for line in lines:
        mobiles_all.extend(re.findall(r'\b[789]\d{9}\b', line))
    return mobiles_all[-1] if mobiles_all else ''

def extract_state(lines):
    for line in lines:
        match = re.search(r'State Name\s*:\s*([A-Za-z ]+)', line, re.I)
        if match:
            return match.group(1).strip()
    return ''

def extract_city(lines):
    for i, line in enumerate(lines):
        if 'consignee' in line.lower() or 'buyer' in line.lower():
            if i + 1 < len(lines):
                candidate = lines[i + 1].strip()
                if candidate.isalpha() and len(candidate) > 2:
                    return candidate
    return ''

def extract_amount(line):
    line = line.replace(',', '')
    matches = re.findall(r'\d+\.\d+|\d+', line)
    return matches[-1] if matches else ''

def extract_reference_name(lines, index):
    for i in range(1, 4):
        if index + i < len(lines):
            candidate = lines[index + i].strip()
            if candidate.isalpha() and 2 <= len(candidate) <= 15:
                return candidate.upper()
    return ''

def extract_reference_name_from_other_references(lines):
    for i, line in enumerate(lines):
        if re.search(r'Other References', line, re.I):
            if i + 1 < len(lines):
                candidate = lines[i + 1].strip()
                if candidate.isalpha():
                    return candidate.upper()
    return ''

def ocr_from_image_or_pdf(file_bytes, filename):
    try:
        # Make sure poppler binaries path is set correctly
        os.environ["PATH"] += os.pathsep + r"C:\poppler-24.08.0\Library\bin"

        if filename.lower().endswith('.pdf'):
            pages = convert_from_bytes(file_bytes)
            logger.info(f"PDF converted to {len(pages)} images")
            full_text = ''
            for i, page in enumerate(pages):
                text = pytesseract.image_to_string(page)
                logger.info(f"Page {i+1} OCR text length: {len(text)}")
                full_text += text + '\n'
            return full_text
        else:
            img = Image.open(io.BytesIO(file_bytes))
            text = pytesseract.image_to_string(img)
            logger.info(f"Image OCR text length: {len(text)}")
            return text
    except Exception as e:
        logger.error(f"OCR error on file {filename}: {e}")
        return ''

@add_customer_bp.route('/add_special')
def add_customer_special():
    extracted_text = ''
    data = {
        'khc code': '',
        'billno': '',
        'biltyno': '',
        'date': '',
        'name': '',
        'firmname': '',
        'state': '',
        'city': '',
        'district': '',
        'tehsil': '',
        'pincode': '',
        'mobile': '',
        'amount': '',
        'reference_name': '',
    }

    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            flash("Please upload a file (image or PDF).", "warning")
            return render_template('add_customer.html', extracted_text=extracted_text, data=data)

        file_bytes = file.read()
        extracted_text = ocr_from_image_or_pdf(file_bytes, file.filename)
        if not extracted_text.strip():
            flash("No text could be extracted. Try a clearer scan or different file.", "danger")
            return render_template('add_customer.html', extracted_text=extracted_text, data=data)

        lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
        billno_found = ''
        date_line_index = None
        alc_holder = ''

        # Main parsing loop
        for i, line in enumerate(lines):
            low = line.lower()
            next_line = lines[i + 1] if i + 1 < len(lines) else ''

            # Extract KHC code
            if not data['khc code']:
                khc_code = extract_khc_code([line])
                if khc_code:
                    data['khc code'] = khc_code

            # Extract invoice/bill number once
            if not billno_found:
                billno = extract_invoice_no(lines)
                if billno:
                    billno_found = billno

            # Extract date if not found yet
            if not data['date'] and ('dated' in low or 'invoice no' in low):
                dt = extract_date(line, next_line)
                if dt:
                    data['date'] = dt
                    date_line_index = i

            # Extract bilty number
            if not data['biltyno'] and ('dispatch doc' in low or 'bilty no' in low):
                bilty = extract_biltyno(line)
                if bilty:
                    data['biltyno'] = bilty

            # Extract firmname and name
            if ('buyer' in low or 'consignee' in low) and next_line:
                # Avoid headers as next line
                if not any(h in next_line.lower() for h in ['dispatch', 'doc', 'delivery', 'note', 'invoice', 'date', 'bill no', 'buyer', 'consignee']):
                    firm, name = extract_firmname_name(line, next_line)
                    if firm:
                        data['firmname'] = firm
                    if name:
                        data['name'] = name

            # Clear name if it equals city/state/district
            name_upper = data['name'].strip().upper()
            city_upper = data.get('city', '').strip().upper()
            state_upper = data.get('state', '').strip().upper()
            district_upper = data.get('district', '').strip().upper()

            if name_upper in [city_upper, state_upper, district_upper]:
                data['name'] = ''

            # Extract pincode, state, city, mobile, amount
            if not data['pincode']:
                data['pincode'] = extract_any_pincode(lines)
            if not data['state']:
                data['state'] = extract_state(lines)
            if not data['city']:
                data['city'] = extract_city(lines)
            if not data['mobile']:
                data['mobile'] = extract_mobile(lines)
            if not data['amount'] and ('total' in low or 'amount' in low):
                amt = extract_amount(line)
                if amt:
                    data['amount'] = amt

            # Extract alc holder name if available
            if not alc_holder and ('alc holder' in low or "alc holder's name" in low):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    alc_holder = parts[1].strip().lower()

        # Assign billno prefix based on alc holder or khc code
        if alc_holder:
            if 'krishna home care' in alc_holder:
                data['billno'] = f'KHC-{billno_found}'
            elif 'krishna traders' in alc_holder:
                data['billno'] = f'KT-{billno_found}'
            else:
                data['billno'] = billno_found
        else:
            if data['khc code'] and billno_found:
                data['billno'] = f"{data['khc code']}-{billno_found}"
            else:
                data['billno'] = billno_found

        # Extract reference name near date line or from other references section
        if date_line_index is not None:
            ref_name = extract_reference_name(lines, date_line_index)
            if ref_name:
                data['reference_name'] = ref_name

        other_ref = extract_reference_name_from_other_references(lines)
        if other_ref and other_ref.upper() not in ['UPI', 'RTGS', 'NEFT', 'BANK', 'ONLINE']:
            data['reference_name'] = other_ref
        else:
            if data['reference_name'].upper() in ['UPI', 'RTGS', 'NEFT', 'BANK', 'ONLINE']:
                data['reference_name'] = ''

        # Fetch location info if pincode available
        if data['pincode']:
            loc = get_location_from_pincode(data['pincode'])
            data.update(loc)

        # Clear khc code and name as you requested (optional, remove if needed)
        data['khc code'] = ''
        data['name'] = ''

        flash("File processed successfully!", "success")

    return render_template('add_customer.html', extracted_text=extracted_text, data=data)
