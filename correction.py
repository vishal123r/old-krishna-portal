from flask import Blueprint, request, jsonify, render_template
import sqlite3
import difflib

correction_bp = Blueprint('correction', __name__, template_folder='templates')

DATABASE = 'crm.db'

def get_words_from_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    text_columns = [
        'firmname', 'city', 'mobile', 'payment_status', 'transport_name', 'transport_number', 
        'bill_image', 'state', 'pincode', 'name', 'status', 'additional_mobile', 'reference_name',
        'company', 'offer_discount', 'image_path', 'order_status', 'bilty_image', 'category',
        'district', 'tehsil'
    ]
    
    words = set()
    
    for col in text_columns:
        query = f"SELECT DISTINCT {col} FROM customers WHERE {col} IS NOT NULL AND TRIM(CAST({col} AS TEXT)) != ''"
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            val = row[0]
            if val is not None:
                val_str = str(val).strip()
                if val_str != '':
                    words.add(val_str.title())
    
    conn.close()
    return sorted(list(words))

def find_similar_words(word, word_list, n=5, cutoff=0.5):
    return difflib.get_close_matches(word.title(), word_list, n=n, cutoff=cutoff)

@correction_bp.route('/get_all_words', methods=['GET'])
def get_all_words():
    words = get_words_from_db()
    return jsonify(words)

@correction_bp.route('/get_similar_words', methods=['POST'])
def get_similar_words():
    data = request.json
    input_text = data.get('text', '')
    words_in_db = get_words_from_db()
    words = input_text.split()
    result = {}
    for w in words:
        sims = find_similar_words(w, words_in_db)
        result[w] = sims if sims else [w]
    return jsonify(result)

@correction_bp.route('/submit_corrections', methods=['POST'])
def submit_corrections():
    data = request.json
    corrections = data.get('corrections', [])
    print("User selected words:", corrections)
    # Yahan DB me ya file me save kar sakte ho agar chaaho
    return jsonify({'status': 'success'})

@correction_bp.route('/correction_widget')
def correction_widget():
    return render_template('correction_widget.html')
