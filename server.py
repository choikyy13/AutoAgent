from flask import Flask, request, jsonify, render_template
import os
import sys

# Ensure we can import from current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pipeline import run_pipeline

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/run', methods=['POST'])
def run_analysis():
    data = request.get_json()
    pdf_url = data.get('url')
    
    if not pdf_url:
        return jsonify({"status": "error", "message": "No URL provided"}), 400
    
    try:
        # Run the pipeline
        results = run_pipeline(pdf_url)
        return jsonify(results)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
