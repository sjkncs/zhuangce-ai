# 妆策AI｜第八批可运行开发包

## 目录说明
- data/：原始 JSON 与 CSV 数据
- frontend/mock/：前端可直接读取的 mock 数据
- backend/fastapi_demo/：FastAPI 演示接口
- backend/flask_demo/：Flask 演示接口

## 启动方式
### FastAPI
```bash
cd backend/fastapi_demo
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

### Flask
```bash
cd backend/flask_demo
pip install -r requirements.txt
python app.py
```

## 接口清单
- GET /api/home/overview
- POST /api/predict
- POST /api/recommend
- POST /api/content/generate
- GET /api/dashboard
