from pathlib import Path
from flask import Flask, jsonify, request
import json

BASE = Path(__file__).resolve().parents[2] / 'data'

def load(name: str):
    return json.loads((BASE / name).read_text(encoding='utf-8'))

app = Flask(__name__)

@app.get('/api/home/overview')
def home_overview():
    return jsonify(load('home_overview.json'))

@app.post('/api/predict')
def predict():
    _ = request.get_json(silent=True)
    return jsonify(load('predict_response.json'))

@app.post('/api/recommend')
def recommend():
    _ = request.get_json(silent=True)
    return jsonify(load('recommend_response.json'))

@app.post('/api/content/generate')
def content_generate():
    _ = request.get_json(silent=True)
    return jsonify(load('content_response.json'))

@app.get('/api/dashboard')
def dashboard():
    return jsonify(load('dashboard_response.json'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
