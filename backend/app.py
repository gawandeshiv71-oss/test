"""
app.py
======
Flask REST API server for the OMR Sheet Checker.

Endpoints
---------
POST   /api/process              Process a single OMR sheet image
POST   /api/bulk-upload          Process multiple OMR sheet images
GET    /api/results              List all past results
GET    /api/results/<id>         Get single result
DELETE /api/results/<id>         Delete a result
GET    /api/download-pdf/<id>    Download result as PDF

Run
---
    python app.py
Server at http://localhost:5000
"""

import os
import sys
import uuid
import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io

# Add backend dir to path
sys.path.insert(0, os.path.dirname(__file__))
from omr_processor import process_omr
from models import init_db, save_result, get_all_results, get_result_by_id, delete_result
from utils import parse_answer_key, generate_pdf

# ─────────────────────────────────────────────
# App setup
# ─────────────────────────────────────────────
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)   # Allow frontend to call the API

BASE_DIR    = os.path.join(os.path.dirname(__file__), '..')
UPLOAD_DIR  = os.path.join(BASE_DIR, 'uploads')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')

os.makedirs(UPLOAD_DIR,  exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ─────────────────────────────────────────────
# Serve frontend
# ─────────────────────────────────────────────
from flask import send_from_directory

@app.route('/')
def serve_dashboard():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory(FRONTEND_DIR, path)
    except Exception:
        return send_from_directory(FRONTEND_DIR, 'index.html')



# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'message': 'OMR Server running'})


@app.route('/api/process', methods=['POST'])
def process_sheet():
    """
    Process a single OMR sheet image.

    Form data
    ---------
    image        : file (required)
    answer_key   : str  (required) — "1=A, 2=B, ..." or JSON or CSV
    answer_fmt   : str  (optional) — 'auto'|'text'|'json'|'csv'
    total_questions : int (required)
    options      : int  (optional, default 4)
    negative_marking : float (optional, default 0)
    student_name : str  (optional)
    """
    try:
        # ── Validate inputs ──────────────────────────────────────────
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Use PNG/JPG/BMP'}), 400

        raw_key  = request.form.get('answer_key', '')
        if not raw_key:
            return jsonify({'error': 'Answer key is required'}), 400

        total_q  = int(request.form.get('total_questions', 0))
        if total_q < 1:
            return jsonify({'error': 'total_questions must be >= 1'}), 400

        # ── Save uploaded image ──────────────────────────────────────
        ext      = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        img_path = os.path.join(UPLOAD_DIR, filename)
        file.save(img_path)

        # ── Parse answer key ─────────────────────────────────────────
        fmt        = request.form.get('answer_fmt', 'auto')
        answer_key = parse_answer_key(raw_key, fmt=fmt)
        if not answer_key:
            return jsonify({'error': 'Could not parse answer key'}), 400

        # ── Build config ─────────────────────────────────────────────
        config = {
            'total_questions':  total_q,
            'options':          int(request.form.get('options', 4)),
            'negative_marking': float(request.form.get('negative_marking', 0)),
        }

        # ── Run OMR ──────────────────────────────────────────────────
        result = process_omr(img_path, answer_key, config)

        # ── Persist to DB ─────────────────────────────────────────────
        student_name = request.form.get('student_name', '')
        record_id    = save_result(img_path, answer_key, result, student_name)

        result['id']           = record_id
        result['student_name'] = student_name

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/bulk-upload', methods=['POST'])
def bulk_upload():
    """
    Process multiple OMR sheets at once.

    Form data
    ---------
    images[]       : files (required)
    answer_key     : str   (required, same key applied to all)
    answer_fmt     : str   (optional)
    total_questions: int   (required)
    options        : int   (optional)
    negative_marking: float (optional)
    """
    try:
        files = request.files.getlist('images[]')
        if not files:
            return jsonify({'error': 'No images provided'}), 400

        raw_key = request.form.get('answer_key', '')
        total_q = int(request.form.get('total_questions', 0))
        if total_q < 1:
            return jsonify({'error': 'total_questions must be >= 1'}), 400

        fmt        = request.form.get('answer_fmt', 'auto')
        answer_key = parse_answer_key(raw_key, fmt=fmt)
        config = {
            'total_questions':  total_q,
            'options':          int(request.form.get('options', 4)),
            'negative_marking': float(request.form.get('negative_marking', 0)),
        }

        bulk_results = []
        for f in files:
            if not f or not allowed_file(f.filename):
                bulk_results.append({'filename': f.filename, 'error': 'Invalid file'})
                continue
            ext      = f.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            img_path = os.path.join(UPLOAD_DIR, filename)
            f.save(img_path)

            try:
                result    = process_omr(img_path, answer_key, config)
                record_id = save_result(img_path, answer_key, result)
                bulk_results.append({
                    'filename':   f.filename,
                    'id':         record_id,
                    'score':      result['score'],
                    'percentage': result['percentage'],
                    'correct':    result['correct'],
                    'wrong':      result['wrong'],
                })
            except Exception as e:
                bulk_results.append({'filename': f.filename, 'error': str(e)})

        return jsonify({'results': bulk_results}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/results', methods=['GET'])
def list_results():
    """Return all stored results (summary only)."""
    try:
        return jsonify(get_all_results()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/results/<int:result_id>', methods=['GET'])
def get_result(result_id):
    """Return a full single result."""
    try:
        row = get_result_by_id(result_id)
        if row is None:
            return jsonify({'error': 'Result not found'}), 404
        return jsonify(row), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/results/<int:result_id>', methods=['DELETE'])
def delete_result_route(result_id):
    """Delete a result record."""
    try:
        delete_result(result_id)
        return jsonify({'message': 'Deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download-pdf/<int:result_id>', methods=['GET'])
def download_pdf(result_id):
    """Generate and stream a PDF report for the given result id."""
    try:
        row = get_result_by_id(result_id)
        if row is None:
            return jsonify({'error': 'Result not found'}), 404

        result_data  = row['result']
        student_name = row.get('student_name', 'Student')
        pdf_bytes    = generate_pdf(result_data, student_name)

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'OMR_Result_{result_id}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────
# Start server
# ─────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    print("=" * 50)
    print("  OMR Sheet Checker — Backend Server")
    print("  http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
