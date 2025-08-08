from flask import Flask, render_template, request, Response, redirect, url_for
from court_scraper import fetch_case_details
import requests
import sqlite3

app = Flask(__name__)
last_pdf_url = None  # Global variable to store last PDF URL

# Home page
@app.route('/')
def index():
    case_types = [
        'Crl.A.', 'Crl.M.C.', 'Bail Appl.', 'WP(Crl.)', 'Tr.P.(Crl.)',
        'Crl.Rev.P.', 'Crl.Ref.', 'Crl.L.P.', 'Crl.M.A.', 'Crl.AC',
        'Crl.M.B.', 'Crl.Pet.', 'Crl.Misc.', 'Crl.Appeal', 'Crl.Case',
        'Crl.S.A.', 'Crl.C.', 'Crl.W.P.', 'Crl.Revision', 'Crl.Tribunal',
        'Criminal Appeal', 'C.M.P.', 'MACA', 'Crl.O.P.', 'CR',
        'Misc.Crl.', 'WP', 'W.P.(C)'
    ]
    return render_template('index.html',case_types=case_types)

# Handle form submission
@app.route('/get_status', methods=['POST'])
def get_status():
    global last_pdf_url
    case_type = request.form['case_type'].strip()
    case_number = request.form['case_number'].strip()
    case_year = request.form['case_year'].strip()

    pdf_url = fetch_case_details(case_type, case_number, case_year)

    # Log to DB
    log_query_to_db(case_type, case_number, case_year, pdf_url)

    if pdf_url.startswith("❌"):
        return render_template('error.html', message=pdf_url)

    last_pdf_url = pdf_url  # Save PDF URL globally
    # ✅ Redirect to /view_pdf page (opens in new tab if link is targeted that way in frontend)
    return redirect(url_for('view_pdf'))

# View PDF in new page
@app.route('/view_pdf')
def view_pdf():
    global last_pdf_url
    try:
        pdf_response = requests.get(last_pdf_url)
        pdf_response.raise_for_status()
        return Response(
            pdf_response.content,
            mimetype='application/pdf',
            headers={"Content-Disposition": "inline; filename=case_status.pdf"}
        )
    except Exception as e:
        return render_template('error.html', message=f"❌ Could not load PDF: {e}")

# Log to SQLite DB
def log_query_to_db(case_type, case_number, case_year, response_summary):
    try:
        conn = sqlite3.connect('court_queries.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS case_queries (
                case_type TEXT,
                case_number TEXT,
                case_year TEXT,
                response_summary TEXT
            )
        ''')
        cursor.execute('''
            INSERT INTO case_queries (case_type, case_number, case_year, response_summary)
            VALUES (?, ?, ?, ?)
        ''', (case_type, case_number, case_year, response_summary))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging to database: {e}")

# View search history
@app.route('/history')
def history():
    try:
        conn = sqlite3.connect('court_queries.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT case_type, case_number, case_year, response_summary 
            FROM case_queries 
            ORDER BY rowid DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return render_template('history.html', rows=rows)
    except Exception as e:
        return render_template('error.html', message=f"❌ Error fetching history: {e}")

# Clear history
@app.route('/clear_history', methods=['POST'])
def clear_history():
    try:
        conn = sqlite3.connect('court_queries.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM case_queries')
        conn.commit()
        conn.close()
        return render_template('success.html', message="✅ History cleared successfully!")
    except Exception as e:
        return render_template('error.html', message=f"❌ Failed to clear history: {e}")

if __name__ == '__main__':
    app.run(debug=True)
