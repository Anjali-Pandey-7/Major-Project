from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from job_data import jobs
app = Flask(__name__)
CORS(app)  # To allow frontend access


@app.route('/recommend', methods=['GET'])
def recommend_jobs():
    return jsonify(jobs)

@app.route('/upload', methods=['POST'])
def upload_resume():
    file = request.files['resume']
    filepath = file.filename
    file.save(filepath)

    try:
        data = ResumeParser(filepath).get_extracted_data()
    except Exception as e:
        data = {"error": str(e)}

    os.remove(filepath)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
