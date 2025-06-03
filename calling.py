from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, abort 
import sqlite3
import pandas as pd
from datetime import datetime, date
import os
from werkzeug.utils import secure_filename

calling_bp = Blueprint('calling', __name__, template_folder='templates')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xls', 'xlsx', 'csv'}

def get_connection():
    return sqlite3.connect('crm.db')

def normalize_mobile(mobile):
    return str(mobile).lstrip("0").strip() if mobile else ""

def remove_duplicate_entries(data):
    seen = set()
    unique_data = []

    for row in data:
        mobile = row[2]  # assuming mobile number is in index 2
        justdial = row[9] if len(row) > 9 else None  # adjust index if needed

        normalized_mobile = normalize_mobile(mobile)

        # ✅ Skip entry if mobile is empty but justdial is filled
        if not normalized_mobile and justdial:
            continue

        if normalized_mobile not in seen:
            seen.add(normalized_mobile)
            unique_data.append(row)

    return unique_data

@calling_bp.app_template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d'):
    if value:
        # value might be string from db, try parse first
        if isinstance(value, str):
            try:
                dt = datetime.strptime(value, '%Y-%m-%d')
                return dt.strftime(format)
            except ValueError:
                return value  # return as-is if parsing fails
        elif isinstance(value, datetime):
            return value.strftime(format)
    return ''

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@calling_bp.route('/', methods=['GET'])
def calling_redirect():
    return redirect(url_for('calling.calling_filter_data'))

@calling_bp.route('/calling_filter_data', methods=['GET', 'POST'])
def calling_filter_data():
    # Get filters from form POST or GET args
    state = request.form.get('state') if request.method == 'POST' else request.args.get('state')
    district = request.form.get('district') if request.method == 'POST' else request.args.get('district')
    category = request.form.get('category') if request.method == 'POST' else request.args.get('category')
    today_str = date.today().isoformat()

    conn = get_connection()
    cursor = conn.cursor()

    # Fetch all states and normalize them to uppercase & unique
    cursor.execute('SELECT state FROM calling_data')
    all_states = [row[0] for row in cursor.fetchall() if row[0]]
    states = sorted(set(s.strip().upper() for s in all_states))

    districts = []
    categories = []

    if state:
        # Normalize input state to uppercase for matching
        state_upper = state.strip().upper()
        cursor.execute('SELECT DISTINCT district FROM calling_data WHERE UPPER(state) = ?', (state_upper,))
        districts = [row[0] for row in cursor.fetchall()]

    if state and district:
        state_upper = state.strip().upper()
        district_strip = district.strip()
        cursor.execute('SELECT DISTINCT category FROM calling_data WHERE UPPER(state) = ? AND district = ?', (state_upper, district_strip))
        categories = [row[0] for row in cursor.fetchall()]

    filtered_rows = []
    if state and district and category:
        state_upper = state.strip().upper()
        district_strip = district.strip()
        category_strip = category.strip()
        cursor.execute('''
            SELECT firm_name, mobile_number, justdial, id, remark, status, callback_date
            FROM calling_data
            WHERE UPPER(state) = ? AND district = ? AND category = ?
        ''', (state_upper, district_strip, category_strip))

        results = cursor.fetchall()

        issue_pending_rows = []
        due_callback_rows = []
        no_callback_date_rows = []

        for row in results:
            firm_name_, mobile_number_, justdial_, id_, remark_, status_, callback_date_ = row
            status_lower = (status_ or "").strip().lower()

            # Skip rows with these statuses regardless of date
            if status_lower in ['not called/not interested', 'order confirmed', 'closed']:
                continue
            elif status_lower == 'issue pending':
                issue_pending_rows.append(row)
            else:
                if callback_date_:
                    try:
                        cb_date = datetime.strptime(callback_date_, '%Y-%m-%d').date()
                        if cb_date <= date.today():
                            due_callback_rows.append(row)
                    except ValueError:
                        pass
                else:
                    no_callback_date_rows.append(row)

        filtered_rows = issue_pending_rows + due_callback_rows + no_callback_date_rows

    conn.close()

    return render_template('calling_filter_data.html',
                           states=states,
                           districts=districts,
                           categories=categories,
                           data=filtered_rows,
                           selected_state=state,
                           selected_district=district,
                           selected_category=category,
                           current_date=today_str)


@calling_bp.route('/get_districts/<state>')
def get_districts(state):
    con = get_connection()
    cur = con.cursor()
    # State ko upper kar ke compare karenge, taaki case insensitive ho
    cur.execute("SELECT DISTINCT district FROM calling_data WHERE UPPER(state) = UPPER(?) ORDER BY district ASC", (state,))
    districts = [row[0] for row in cur.fetchall()]
    con.close()
    return jsonify({'districts': districts})

@calling_bp.route('/get_categories')
def get_categories():
    state = request.args.get('state')
    district = request.args.get('district')
    if not state or not district:
        return jsonify({'categories': []})
    con = get_connection()
    cur = con.cursor()
    # State aur district dono ko upper kar ke compare karenge, case insensitive matching ke liye
    cur.execute("SELECT DISTINCT category FROM calling_data WHERE UPPER(state) = UPPER(?) AND UPPER(district) = UPPER(?) ORDER BY category ASC", (state, district))
    categories = [row[0] for row in cur.fetchall()]
    con.close()
    return jsonify({'categories': categories})

@calling_bp.route('/not_interested', methods=['GET'])
def not_interested():
    current_date = datetime.today().strftime('%Y-%m-%d')
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT firm_name, mobile_number, justdial, id, remark, status, callback_date
        FROM calling_data
        WHERE LOWER(status) = 'not called/not interested' AND callback_date < ?
    ''', (current_date,))
    not_interested_rows = cursor.fetchall()
    conn.close()

    return render_template(
        'not_interested.html',
        data=not_interested_rows,
        current_date=current_date
    )

@calling_bp.route('/edit_data/<int:id>', methods=['GET', 'POST'])
def edit_data(id):
    state = request.args.get('state', '')
    district = request.args.get('district', '')
    category = request.args.get('category', '')

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, firm_name, mobile_number, status, callback_date, remark FROM calling_data WHERE id = ?", (id,))
    row = cursor.fetchone()

    if not row:
        flash("Data not found.", "error")
        conn.close()
        return redirect(url_for('calling.calling_filter_data', state=state, district=district, category=category))

    id_, firm_name, mobile_number, status, callback_date, remark = row

    # Format callback_date for input field
    if callback_date:
        try:
            callback_date = datetime.strptime(callback_date, '%Y-%m-%d').strftime('%Y-%m-%d')
        except Exception:
            callback_date = ''
    else:
        callback_date = ''

    if request.method == 'POST':
        call_back_date = request.form.get('callback_date', '')
        remark_form = request.form.get('remark', '')
        status_form = request.form.get('status', '')

        cursor.execute("""
            UPDATE calling_data
            SET callback_date = ?, remark = ?, status = ?
            WHERE id = ?
        """, (call_back_date, remark_form, status_form, id))
        conn.commit()
        conn.close()

        flash("Data updated successfully.", "success")
        return redirect(url_for('calling.calling_filter_data', state=state, district=district, category=category))

    conn.close()

    return render_template('edit_data.html',
                           firm_name=firm_name,
                           mobile_number=mobile_number,
                           status=status,
                           callback_date=callback_date,
                           remark=remark,
                           state_filter=state,
                           district_filter=district,
                           category_filter=category)

@calling_bp.route('/view_all_data')
def view_all_data():
    conn = get_connection()
    cursor = conn.cursor()

    def normalize_mobile(mobile):
        return str(mobile).lstrip("0").strip() if mobile else ""

    def clean_duplicates():
        cursor.execute("SELECT * FROM calling_data")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        id_idx = columns.index('id')
        mobile_idx = columns.index('mobile_number')
        justdial_idx = columns.index('justdial')

        detail_columns = ['status', 'date']  # add more if needed
        detail_idxs = [columns.index(col) for col in detail_columns if col in columns]

        def has_details(row):
            for idx in detail_idxs:
                if row[idx] not in (None, '', 'NULL'):
                    return True
            return False

        mobile_seen = {}
        justdial_seen = {}
        ids_to_delete = set()

        for row in rows:
            _id = row[id_idx]
            raw_mobile = row[mobile_idx]
            mobile = normalize_mobile(raw_mobile)
            justdial = row[justdial_idx]

            curr_has_details = has_details(row)

            # ✅ Remove if mobile is empty and justdial is filled
            if not mobile and justdial and str(justdial).strip():
                ids_to_delete.add(_id)
                continue

            # ✅ Check mobile duplicates
            if mobile:
                if mobile in mobile_seen:
                    prev_id, prev_has_details = mobile_seen[mobile]
                    if not curr_has_details and prev_has_details:
                        ids_to_delete.add(_id)
                    elif curr_has_details and not prev_has_details:
                        ids_to_delete.add(prev_id)
                        mobile_seen[mobile] = (_id, True)
                    else:
                        ids_to_delete.add(_id)
                else:
                    mobile_seen[mobile] = (_id, curr_has_details)

            # ✅ Check justdial duplicates
            if justdial and str(justdial).strip():
                if justdial in justdial_seen:
                    prev_id, prev_has_details = justdial_seen[justdial]
                    if not curr_has_details and prev_has_details:
                        ids_to_delete.add(_id)
                    elif curr_has_details and not prev_has_details:
                        ids_to_delete.add(prev_id)
                        justdial_seen[justdial] = (_id, True)
                    else:
                        ids_to_delete.add(_id)
                else:
                    justdial_seen[justdial] = (_id, curr_has_details)

        if ids_to_delete:
            cursor.executemany("DELETE FROM calling_data WHERE id = ?", [(i,) for i in ids_to_delete])
            conn.commit()

    # Run cleaner
    clean_duplicates()

    # Fetch cleaned data
    cursor.execute("SELECT * FROM calling_data")
    data = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    conn.close()

    # Add Sr. No.
    enumerated_data = [(i + 1,) + row for i, row in enumerate(data)]
    column_names = ['Sr. No.'] + column_names

    return render_template('view_all_data.html', data=enumerated_data, columns=column_names)

@calling_bp.route('/show_status_entries/')
@calling_bp.route('/show_status_entries/<path:status>')
def show_status_entries(status=None):
    conn = get_db_connection()
    if status:
        entries = conn.execute('SELECT * FROM calling_data WHERE status = ?', (status,)).fetchall()
    else:
        entries = conn.execute('SELECT * FROM calling_data').fetchall()
    conn.close()
    return render_template('status_entries.html', entries=entries, status=status)

@calling_bp.route('/api/scanning_status')
def scanning_status():
    conn = get_db_connection()
    result = conn.execute("SELECT COUNT(*) FROM calling_data WHERE status = ?", ("scanning",)).fetchone()
    conn.close()
    scanning = result[0] > 0
    return jsonify({'scanning': scanning})

import re

def is_valid_number(number):
    # Simple check: number me digits hone chahiye, aur kam se kam 7 digits
    if not number:
        return False
    number = str(number).strip()
    if number.lower() in ['nan', 'none', '']:
        return False
    # Digits check
    digits = re.sub(r'\D', '', number)  # Remove non-digit chars
    return len(digits) >= 7  # ya aap apni requirement ke hisab se

@calling_bp.route('/upload_calling_data', methods=['GET', 'POST'])
def upload_calling_data():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part in the request.', 'error')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)

            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            state = request.form.get('state')
            district = request.form.get('district')
            category = request.form.get('category')

            if not (state and district and category):
                flash('Please fill State, District and Category fields.', 'error')
                return redirect(request.url)

            try:
                if filename.lower().endswith('.csv'):
                    df = pd.read_csv(filepath, header=None)
                else:
                    df = pd.read_excel(filepath, header=None)
            except Exception as e:
                flash(f'Failed to read the file: {e}', 'error')
                return redirect(request.url)

            conn = get_connection()
            cursor = conn.cursor()

            inserted_count = 0
            skipped_count = 0

            for _, row in df.iterrows():
                firm_name = str(row[0]).strip() if len(row) > 0 else ''
                mobile_number = str(row[1]).strip() if len(row) > 1 else ''
                justdial = str(row[2]).strip() if len(row) > 2 else ''

                # Clean and check for "nan", "none", "" etc
                firm_name = firm_name if firm_name.lower() not in ['nan', 'none', ''] else ''
                mobile_number = mobile_number if mobile_number.lower() not in ['nan', 'none', ''] else ''
                justdial = justdial if justdial.lower() not in ['nan', 'none', ''] else ''

                # Skip if no firm_name
                if not firm_name:
                    skipped_count += 1
                    continue

                # Check if mobile_number valid; if not, check if justdial valid
                if is_valid_number(mobile_number):
                    valid_number = mobile_number
                elif is_valid_number(justdial):
                    valid_number = justdial
                else:
                    # No valid number found, skip record
                    skipped_count += 1
                    continue

                # Check if record exists
                cursor.execute('''
                    SELECT 1 FROM calling_data 
                    WHERE mobile_number = ? AND state = ? AND district = ? AND category = ?
                ''', (valid_number, state, district, category))
                exists = cursor.fetchone()

                if exists:
                    skipped_count += 1
                    continue

                # Insert record with the valid number found
                cursor.execute('''
                    INSERT INTO calling_data 
                    (firm_name, mobile_number, justdial, category, state, district, status, callback_date, remark)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (firm_name, valid_number, justdial, category, state, district, '', None, ''))

                inserted_count += 1

            conn.commit()
            conn.close()

            flash(f'Successfully inserted {inserted_count} records. Skipped {skipped_count} invalid/duplicate records.', 'success')
            return redirect(url_for('calling.calling_filter_data'))

        else:
            flash('Invalid file type. Only .xls, .xlsx, and .csv files are allowed.', 'error')
            return redirect(request.url)

    return render_template('calling_upload_data.html')

@calling_bp.route('/home1')  # sirf '/home1', prefix blueprint ke url_prefix se aayega
def home1():
    if session.get('username') != 'krishnahomecare':
        flash("Access denied! Only admin can access this page.")
        return redirect(url_for('calling.calling_filter_data'))
    return render_template('calling/home1.html')

def get_db_connection():
    conn = sqlite3.connect('crm.db')
    conn.row_factory = sqlite3.Row
    return conn


@calling_bp.route('/status_buttons')
def status_buttons():
    conn = get_db_connection()
    statuses = conn.execute('SELECT DISTINCT status FROM calling_data').fetchall()
    conn.close()
    # Filter out blank or None statuses
    statuses = [row for row in statuses if row['status'] and row['status'].strip() != '']
    return render_template('status_buttons.html', statuses=statuses)

