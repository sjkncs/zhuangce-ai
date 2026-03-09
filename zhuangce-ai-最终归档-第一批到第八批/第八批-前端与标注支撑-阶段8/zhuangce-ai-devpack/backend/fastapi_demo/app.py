from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

BASE = Path(__file__).resolve().parents[2] / 'data'

def load(name: str):
    return json.loads((BASE / name).read_text(encoding='utf-8'))

app = FastAPI(title='妆策AI FastAPI Demo')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

@app.get('/api/home/overview')
def home_overview():
    return load('home_overview.json')

@app.post('/api/predict')
def predict(payload: dict):
    return load('predict_response.json')

@app.post('/api/recommend')
def recommend(payload: dict):
    return load('recommend_response.json')

@app.post('/api/content/generate')
def content_generate(payload: dict):
    return load('content_response.json')

@app.get('/api/dashboard')
def dashboard():
    return load('dashboard_response.json')
