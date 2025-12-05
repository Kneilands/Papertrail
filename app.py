import os
import datetime
import re
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from pypdf import PdfReader

# Initialize App
app = Flask(__name__)
app.secret_key = 'dev_secret_key_change_in_production'

# Database Config
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'papertrail.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Upload Config
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

db = SQLAlchemy(app)

# --- Models ---
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    issuer = db.Column(db.String(100))  # e.g., "State of IL"
    expiration_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default="Active")  # Active, Expiring, Expired
    file_path = db.Column(db.String(200), nullable=True)
    ai_summary = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# --- Helpers ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_status(expiry_date):
    if not expiry_date:
        return "Active"
    today = datetime.date.today()
    delta = (expiry_date - today).days
    if delta < 0:
        return "Expired"
    elif delta <= 30:
        return "Expiring Soon"
    return "Active"

def seed_database():
    """Populate DB with realistic starter data if empty."""
    if Document.query.first():
        return
    
    demos = [
        {"name": "General Business License", "category": "Legal", "issuer": "City of Chicago", "days_offset": 200},
        {"name": "Food Sanitation Cert", "category": "Health", "issuer": "Dept of Health", "days_offset": 15},
        {"name": "Liquor Liability Insurance", "category": "Insurance", "issuer": "State Farm", "days_offset": -5},
        {"name": "Annual Report Filing", "category": "Compliance", "issuer": "Secretary of State", "days_offset": 365},
    ]
    
    for d in demos:
        exp = datetime.date.today() + datetime.timedelta(days=d['days_offset'])
        doc = Document(
            name=d['name'],
            category=d['category'],
            issuer=d['issuer'],
            expiration_date=exp,
            status=calculate_status(exp)
        )
        db.session.add(doc)
    db.session.commit()
    print("Database seeded with demo data.")

# --- Routes ---

@app.route('/')
def dashboard():
    docs = Document.query.all()
    
    # Calculate Stats
    total_docs = len(docs)
    active_docs = sum(1 for d in docs if d.status == 'Active')
    expiring_soon = sum(1 for d in docs if d.status == 'Expiring Soon')
    expired = sum(1 for d in docs if d.status == 'Expired')
    
    # Simple Compliance Score (Active / Total)
    score = int((active_docs / total_docs * 100)) if total_docs > 0 else 0
    
    stats = {
        "total": total_docs,
        "expiring": expiring_soon,
        "score": score,
        "ai_insights": sum(1 for d in docs if d.ai_summary)
    }
    
    # Recent docs (last 5)
    recent_docs = Document.query.order_by(Document.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', stats=stats, recent_docs=recent_docs)

@app.route('/documents', methods=['GET', 'POST'])
def documents():
    if request.method == 'POST':
        # Add New Document Logic
        try:
            name = request.form.get('name')
            category = request.form.get('category')
            issuer = request.form.get('issuer')
            date_str = request.form.get('expiration_date')
            
            exp_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None
            
            new_doc = Document(
                name=name,
                category=category,
                issuer=issuer,
                expiration_date=exp_date,
                status=calculate_status(exp_date)
            )
            db.session.add(new_doc)
            db.session.commit()
            flash('Document added successfully.', 'success')
        except Exception as e:
            flash(f'Error adding document: {e}', 'error')
        return redirect(url_for('documents'))

    # Filter Logic
    status_filter = request.args.get('status')
    query = Document.query
    if status_filter and status_filter != 'All':
        query = query.filter_by(status=status_filter)
    
    docs = query.order_by(Document.expiration_date.asc()).all()
    return render_template('documents.html', docs=docs)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_document(id):
    doc = Document.query.get_or_404(id)
    db.session.delete(doc)
    db.session.commit()
    flash('Document deleted.', 'success')
    return redirect(url_for('documents'))

@app.route('/assistant')
def assistant():
    return render_template('assistant.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # Placeholder for saving settings logic
        flash('Settings saved successfully.', 'success')
        return redirect(url_for('settings'))
    return render_template('settings.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_file():
    """
    AI Logic:
    1. Saves file.
    2. Extracts text (Local pypdf).
    3. Sends text to Hugging Face Inference API (Summarization).
    4. Uses Regex to guess dates.
    5. AUTO-SAVE: Adds the document to the database.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        extracted_text = "Could not extract text (image files require OCR)."
        
        # 1. Local Text Extraction (PDF)
        if filename.endswith('.pdf'):
            try:
                reader = PdfReader(filepath)
                extracted_text = ""
                for page in reader.pages[:2]: # Limit to first 2 pages for speed
                    extracted_text += page.extract_text() + "\n"
            except Exception as e:
                extracted_text = f"Error reading PDF: {str(e)}"

        # 2. AI Summarization (Hugging Face API)
        summary = "AI summarization unavailable (Missing API Key or API Error)."
        hf_key = os.environ.get('HF_API_KEY') # Set this in your terminal
        
        # UPDATE: Using new Router URL
        API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"
        
        if hf_key and len(extracted_text) > 50:
            headers = {"Authorization": f"Bearer {hf_key}"}
            try:
                # Truncate text to avoid token limits
                payload = {"inputs": extracted_text[:2000]} 
                response = requests.post(API_URL, headers=headers, json=payload)
                result = response.json()
                if isinstance(result, list) and 'summary_text' in result[0]:
                    summary = result[0]['summary_text']
                elif 'error' in result:
                    summary = f"HF API Error: {result['error']}"
            except Exception as e:
                summary = f"Connection Error: {str(e)}"
        elif not hf_key:
            summary = "Please set HF_API_KEY environment variable to enable AI summarization."

        # 3. Heuristic Date Extraction (Regex)
        # Look for patterns like 12/31/2025, 2025-12-31, Dec 31 2025
        date_pattern = r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4})|(?:\d{4}[-/]\d{1,2}[-/]\d{1,2})\b'
        dates_found = re.findall(date_pattern, extracted_text)
        
        # --- 4. AUTO-SAVE LOGIC ---
        determined_date = None
        if dates_found:
            try:
                # Try to match YYYY-MM-DD specifically (common in our test PDF)
                if re.match(r'\d{4}-\d{2}-\d{2}', dates_found[0]):
                     determined_date = datetime.datetime.strptime(dates_found[0], '%Y-%m-%d').date()
            except:
                pass

        new_doc = Document(
            name=filename,
            category="AI Upload",
            issuer="AI Detected",
            expiration_date=determined_date,
            status=calculate_status(determined_date),
            file_path=filename,
            ai_summary=summary
        )
        db.session.add(new_doc)
        db.session.commit()
        # --------------------------
        
        return jsonify({
            "filename": filename,
            "text_preview": extracted_text[:500] + "...",
            "ai_summary": summary,
            "detected_dates": list(set(dates_found)) if dates_found else ["None detected"],
            "success": True,
            "message": "Document saved to Dashboard!"
        })

    return jsonify({"error": "Invalid file type"}), 400

# --- Main ---
if __name__ == '__main__':
    with app.app_context():
        # Create DB and Seed if new
        if not os.path.exists(os.path.join(basedir, 'instance')):
            os.makedirs(os.path.join(basedir, 'instance'))
        db.create_all()
        seed_database()
        
    app.run(debug=True)