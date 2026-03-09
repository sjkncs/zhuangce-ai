#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
妆策AI — Flask 后端主应用
5个核心API：
  GET  /api/home/overview       首页总览
  POST /api/predict             爆款预测
  POST /api/recommend           推荐决策
  POST /api/content/generate    内容种草生成
  GET  /api/dashboard           数据看板
"""

import sys
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data_analysis'))

try:
    from _03_predict_model import (
        full_predict_pipeline,
        compute_potential_score,
        generate_persona_profile,
        recommend_best_time,
        generate_risk_alerts,
        recommend_products,
        generate_content,
        price_to_band,
    )
    PREDICT_ENGINE_AVAILABLE = True
except ImportError:
    PREDICT_ENGINE_AVAILABLE = False

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"])

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data', 'mock_responses')


def ok(data):
    return jsonify({"code": 0, "message": "success", "data": data})


def err(code, msg):
    return jsonify({"code": code, "message": msg, "data": None}), 400


def load_mock(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


# ============================================================
# API 1 ：首页总览
# ============================================================
@app.route('/api/home/overview', methods=['GET'])
def home_overview():
    month = datetime.now().month
    season_tips = {
        range(8, 10): "开学季临近，学生党洗护采购需求正在上升",
        range(11, 13): "双十一大促期间，洗护品类整体搜索量显著提升",
        range(1, 3): "新春换季，香氛修护类产品礼赠场景活跃",
        range(3, 6): "春季换季期，修护柔顺内容热度上升约18%",
    }
    current_tip = "修护洗发内容传播潜力持续稳定，建议优先布局宿舍场景"
    for month_range, tip in season_tips.items():
        if month in month_range:
            current_tip = tip
            break

    data = {
        "project_name": "妆策AI",
        "project_slogan": "让品牌用预测代替试错，让增长更聪明",
        "current_stage": "校赛MVP",
        "data_notice": "当前结果基于公开样本数据与模拟验证逻辑生成",
        "season_tip": current_tip,
        "sample_product": {
            "sample_product_name": "DEAR SEED 玫瑰修护洗发水",
            "brand": "DEAR SEED",
            "primary_category": "洗护",
            "secondary_category": "修护洗发",
            "core_selling_points": ["修护", "柔顺", "玫瑰香氛"],
            "target_price_range": "100-150元",
            "target_user_group": "学生党女性用户",
            "product_image_placeholder": "rose_shampoo",
        },
        "core_cards": {
            "potential_score": 8.2,
            "score_rank": "超越同类83%产品",
            "target_persona_summary": "学生党 · 宿舍场景 · 价格敏感型",
            "top_scene_tags": ["宿舍日常", "开学季", "日常复购"],
            "platform_priority": ["小红书", "社群私域", "视频号"],
            "persona_distribution": [
                {"name": "学生党", "value": 58},
                {"name": "价格敏感型", "value": 24},
                {"name": "年轻女性用户", "value": 18},
            ],
        },
        "stats": {
            "annotated_samples": 20,
            "keywords_covered": 7,
            "label_dimensions": 5,
            "predicted_products": 1,
        },
        "quick_insights": [
            {"icon": "TrendCharts", "title": "修护×宿舍日常", "value": "共现频率最高", "color": "#E74C3C"},
            {"icon": "User", "title": "学生党占比", "value": "58%", "color": "#3498DB"},
            {"icon": "Clock", "title": "最佳推广时间", "value": "开学季(8-9月)", "color": "#27AE60"},
            {"icon": "Money", "title": "目标价格带竞争力", "value": "超均值 12%", "color": "#9B59B6"},
        ],
    }
    return ok(data)


# ============================================================
# API 2：爆款预测
# ============================================================
@app.route('/api/predict', methods=['POST'])
def predict():
    body = request.get_json(force=True, silent=True) or {}

    product_name = body.get('product_name', 'DEAR SEED 玫瑰修护洗发水')
    primary_category = body.get('primary_category', '洗护')
    secondary_category = body.get('secondary_category', '修护洗发')
    selling_points = body.get('selling_points', ['修护', '柔顺', '玫瑰香氛'])
    price_range = body.get('price_range', '100-150元')
    target_user = body.get('target_user', '学生党女性用户')
    platform = body.get('platform', '小红书')

    if isinstance(selling_points, str):
        selling_points = [s.strip() for s in selling_points.replace('，', ',').split(',')]

    if PREDICT_ENGINE_AVAILABLE:
        result = full_predict_pipeline(
            product_name=product_name,
            primary_category=primary_category,
            secondary_category=secondary_category,
            selling_points=selling_points,
            price_range=price_range,
            target_user=target_user,
            platform=platform,
        )
        predict_data = result['predict']
    else:
        predict_data = _mock_predict(selling_points, target_user, price_range, platform)

    data = {
        "product_name": product_name,
        "potential_score": predict_data.get("potential_score", 8.2),
        "score_explanation": predict_data.get("score_explanation", "卖点组合与平台热点标签匹配度较高，具备较强内容传播潜力。"),
        "factors": predict_data.get("factors", {
            "efficacy_score": 9.0, "persona_score": 8.5,
            "scene_score": 8.8, "price_score": 8.1,
        }),
        "target_persona": predict_data.get("target_persona", ["学生党女性用户", "宿舍场景用户", "价格敏感型用户"]),
        "best_time": predict_data.get("best_time", "开学季（8月20日 - 9月10日）"),
        "best_time_windows": predict_data.get("best_time_windows", [
            {"window": "开学季（8月20日 - 9月10日）", "reason": "学生党采购宿舍洗护需求增加", "confidence": "高"},
            {"window": "换季期（3月、9-10月）", "reason": "气候变化导致修护洗护内容热度上升", "confidence": "高"},
        ]),
        "risk_alert": predict_data.get("risk_alert", [
            "避免只讲科研背书，需强化性价比与日常体验表达",
            "对价格敏感型用户建议突出学生可接受价格带",
        ]),
        "key_tags": predict_data.get("key_tags", ["修护", "柔顺", "留香", "宿舍日常", "开学季"]),
        "data_notice": "当前结果基于公开样本数据与模拟验证逻辑生成，不等同于真实投放结果。",
    }
    return ok(data)


def _mock_predict(selling_points, target_user, price_range, platform):
    return {
        "potential_score": 8.2,
        "score_explanation": "卖点组合与平台热点标签匹配度较高，具备较强内容传播潜力。",
        "factors": {"efficacy_score": 9.0, "persona_score": 8.5, "scene_score": 8.8, "price_score": 8.1},
        "target_persona": ["学生党女性用户", "宿舍场景用户", "价格敏感型用户"],
        "best_time": "开学季（8月20日 - 9月10日）",
        "best_time_windows": [
            {"window": "开学季（8月20日 - 9月10日）", "reason": "学生党采购宿舍洗护需求增加", "confidence": "高"},
        ],
        "risk_alert": ["避免只讲科研背书，需强化性价比与日常体验表达"],
        "key_tags": ["修护", "柔顺", "留香", "宿舍日常", "开学季"],
    }


# ============================================================
# API 3：推荐决策
# ============================================================
@app.route('/api/recommend', methods=['POST'])
def recommend():
    body = request.get_json(force=True, silent=True) or {}

    selling_points = body.get('selling_points', ['修护', '柔顺', '玫瑰香氛'])
    target_user = body.get('target_user', '学生党女性用户')
    potential_score = body.get('potential_score', 8.2)
    secondary_category = body.get('secondary_category', '修护洗发')

    if isinstance(selling_points, str):
        selling_points = [s.strip() for s in selling_points.replace('，', ',').split(',')]

    scenes = ["宿舍日常", "开学季", "日常复购"]

    if PREDICT_ENGINE_AVAILABLE:
        products = recommend_products(selling_points, target_user, scenes, top_n=3)
    else:
        products = [
            {"product_name": "DEAR SEED 玫瑰护手霜", "match_score": 92,
             "reason": "同香型、同场景、适合组合购买", "scenario": "宿舍日常", "price_band": "100-150元"},
            {"product_name": "玫瑰香氛喷雾（示意）", "match_score": 85,
             "reason": "增强情绪价值表达", "scenario": "宿舍日常、日常复购", "price_band": "50-100元"},
            {"product_name": "校园洗护礼盒套装（示意）", "match_score": 78,
             "reason": "适合开学季与社群拼团", "scenario": "开学季、节日送礼", "price_band": "100-150元"},
        ]

    data = {
        "recommended_products": products,
        "recommended_scenes": scenes,
        "recommended_personas": ["学生党", "价格敏感型用户"],
        "recommended_platforms": ["小红书", "社群私域", "视频号"],
        "recommended_content_direction": [
            f"高性价比{secondary_category}",
            "修护柔顺使用体验真实分享",
            "玫瑰香氛氛围感种草",
        ],
        "platform_strategy": [
            {"platform": "小红书", "priority": 1, "strategy": "图文种草+真实测评，优先腰部博主",
             "expected_reach": "精准触达学生党"},
            {"platform": "社群私域", "priority": 2, "strategy": "拼团活动+开学季限时优惠",
             "expected_reach": "高转化率"},
            {"platform": "视频号", "priority": 3, "strategy": "15-30s短视频开场，宿舍场景真实拍摄",
             "expected_reach": "扩大品牌曝光"},
        ],
        "decision_summary": (
            "优先围绕宿舍场景与学生党做种草表达，"
            "用高性价比修护体验打动用户，"
            "再通过同系列商品搭配提升转化率和复购率。"
        ),
        "roi_estimate": {
            "description": "基于样板案例模拟推演",
            "scenario": "DEAR SEED玫瑰修护洗发水",
            "note": "提前15天规划推广策略，精准投放腰部博主，30天笔记量预计破2万，ROI提升约300%",
        },
        "data_notice": "当前为公开样本数据与模拟验证结果。",
    }
    return ok(data)


# ============================================================
# API 4：内容种草生成
# ============================================================
@app.route('/api/content/generate', methods=['POST'])
def content_generate():
    body = request.get_json(force=True, silent=True) or {}

    product_name = body.get('product_name', 'DEAR SEED 玫瑰修护洗发水')
    selling_points = body.get('selling_points', ['修护', '柔顺', '玫瑰香氛'])
    target_user = body.get('target_user', '学生党女性用户')
    scenes = body.get('scenes', ['宿舍日常', '开学季'])
    tone_style = body.get('tone_style', '真实分享 + 高性价比种草')

    if isinstance(selling_points, str):
        selling_points = [s.strip() for s in selling_points.replace('，', ',').split(',')]

    if PREDICT_ENGINE_AVAILABLE:
        content = generate_content(product_name, selling_points, target_user, scenes)
    else:
        content = _mock_content(selling_points, target_user, scenes)

    data = {
        "product_name": product_name,
        "xiaohongshu_titles": content.get("xiaohongshu_titles", []) + [
            "学生党宿舍必备洗护，顺滑和香味终于都有了",
            "开学季洗发水怎么选？这瓶修护香氛型我会回购",
        ],
        "xiaohongshu_full": [
            {
                "title": "学生党闭眼冲！这瓶玫瑰修护洗发水真的很懂宿舍女孩",
                "body": "最近在找一瓶适合宿舍日常用的洗发水，修护和柔顺都兼顾，香味还不能太俗，这瓶玫瑰修护路线整体感受不错。如果你和我一样头发有点毛躁，又不想买太贵的洗护，100-150元这个价格段真的很值得重点看。",
                "tags": ["修护洗发水", "宿舍好物", "学生党种草", "玫瑰香氛", "开学季必备"],
            },
            {
                "title": "修护、柔顺、还好闻：学生党也能负担的宿舍洗护选择",
                "body": "对学生党来说，洗发水不是越贵越好，而是要顺、要稳、要好闻、要不踩雷，这也是这类产品最值得被推荐的原因。这种带一点香氛感的修护洗发水，最怕香味过头，但这瓶的表达方向更偏清新和治愈。",
                "tags": ["平价洗护", "学生党", "修护柔顺", "宿舍日常"],
            },
        ],
        "community_scripts": content.get("community_scripts", []) + [
            "姐妹们，开学季宿舍洗护如果还没想好，可以优先看修护柔顺路线，价格友好的那种。",
            "如果你们头发有点毛躁，又不想花太多预算，玫瑰修护这个方向挺适合学生党。",
        ],
        "video_hooks": content.get("video_hooks", []) + [
            "如果你是学生党，开学回宿舍只想带一瓶真正好用又不踩雷的洗发水，那这个修护柔顺路线你真的可以看看。",
            "今天不讲太复杂的成分，我们只聊一件事：什么样的洗发水更适合学生党日常用。",
        ],
        "tone_style": content.get("tone_style", tone_style),
        "selling_point_expression": content.get("selling_point_expression", "修护、柔顺、香味有记忆点"),
        "scenario_expression": content.get("scenario_expression", "宿舍、开学季、日常复购"),
        "content_strategy": {
            "primary_angle": "真实使用体验",
            "secondary_angle": "高性价比对比",
            "avoid": "过度强调科研成分，缺乏生活感",
            "tips": [
                "用第一人称分享宿舍使用感受",
                "搭配真实场景图（宿舍桌面、淋浴间）",
                "强调顺滑感和香味留存，而非成分参数",
                "价格表达用「100多块」而非精确数字，更亲切",
            ],
        },
        "data_notice": "当前为校赛MVP概念验证版本，文案供参考使用。",
    }
    return ok(data)


def _mock_content(selling_points, target_user, scenes):
    return {
        "xiaohongshu_titles": [
            "学生党修护洗发水真的懂宿舍女孩",
            "开学季宿舍洗护这瓶修护柔顺路线真稳",
        ],
        "community_scripts": ["姐妹们开学季洗护推荐这款修护柔顺的，价格真的友好。"],
        "video_hooks": ["如果你是学生党，这个修护柔顺路线真的值得看。"],
        "tone_style": "真实分享 + 高性价比种草",
        "selling_point_expression": "修护、柔顺、香味有记忆点",
        "scenario_expression": "宿舍、开学季、日常复购",
    }


# ============================================================
# API 5：数据看板
# ============================================================
@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    data = {
        "dashboard_potential_score": 8.2,
        "score_percentile": 83,
        "dashboard_trend_data": [
            {"label": "Day1", "score": 7.1, "date": "采集初期"},
            {"label": "Day2", "score": 7.4, "date": "标签补充"},
            {"label": "Day3", "score": 7.8, "date": "热词统计"},
            {"label": "Day4", "score": 7.9, "date": "因子校准"},
            {"label": "Day5", "score": 8.0, "date": "平台系数"},
            {"label": "Day6", "score": 8.1, "date": "季节调整"},
            {"label": "Day7", "score": 8.2, "date": "最终评分"},
        ],
        "dashboard_scene_distribution": [
            {"name": "宿舍日常", "value": 46},
            {"name": "开学季", "value": 32},
            {"name": "日常复购", "value": 22},
        ],
        "dashboard_persona_distribution": [
            {"name": "学生党", "value": 58},
            {"name": "价格敏感型", "value": 24},
            {"name": "年轻女性用户", "value": 18},
        ],
        "dashboard_efficacy_heatmap": {
            "x_axis": ["宿舍日常", "开学季", "日常复购", "换季护理"],
            "y_axis": ["修护", "柔顺", "留香", "控油", "蓬松", "去屑"],
            "data": [
                [0, 0, 18], [0, 1, 14], [0, 2, 8], [0, 3, 6],
                [1, 0, 16], [1, 1, 12], [1, 2, 11], [1, 3, 5],
                [2, 0, 12], [2, 1, 8],  [2, 2, 7],  [2, 3, 4],
                [3, 0, 4],  [3, 1, 3],  [3, 2, 9],  [3, 3, 7],
                [4, 0, 3],  [4, 1, 4],  [4, 2, 8],  [4, 3, 6],
                [5, 0, 2],  [5, 1, 2],  [5, 2, 5],  [5, 3, 8],
            ],
        },
        "dashboard_price_distribution": [
            {"band": "0-50元", "count": 12, "avg_heat": 6.2},
            {"band": "50-100元", "count": 35, "avg_heat": 7.1},
            {"band": "100-150元", "count": 48, "avg_heat": 8.0},
            {"band": "150-200元", "count": 31, "avg_heat": 7.6},
            {"band": "200-300元", "count": 22, "avg_heat": 7.0},
            {"band": "300-500元", "count": 14, "avg_heat": 6.5},
            {"band": "500元+", "count": 8,  "avg_heat": 5.8},
        ],
        "dashboard_top_recommendations": [
            {"name": "DEAR SEED 玫瑰护手霜", "score": 92},
            {"name": "玫瑰香氛喷雾（示意）", "score": 85},
            {"name": "校园洗护礼盒（示意）", "score": 78},
        ],
        "dashboard_brand_comparison": [
            {"brand": "DEAR SEED（样板）", "score": 8.2, "highlight": True},
            {"brand": "修护洗发平均", "score": 8.1, "highlight": False},
            {"brand": "香氛洗发平均", "score": 7.9, "highlight": False},
            {"brand": "控油洗发平均", "score": 7.2, "highlight": False},
            {"brand": "洗护品类均值", "score": 7.4, "highlight": False},
        ],
        "dashboard_insight_1": "宿舍场景是当前最强内容切入口，修护×宿舍日常共现频率最高(18次)。",
        "dashboard_insight_2": "学生党更关注顺滑感与价格接受度，100-150元价格带热度表现优于同档均值。",
        "dashboard_insight_3": "香氛表达有助于提升内容点击意愿，玫瑰香氛组合可强化情绪价值输出。",
        "dashboard_conclusion": (
            "DEAR SEED玫瑰修护洗发水传播潜力评分8.2，超越同类83%产品。"
            "建议优先布局小红书宿舍场景种草，结合开学季节点，"
            "以修护柔顺+玫瑰香氛为核心卖点组合，精准触达学生党。"
        ),
        "dashboard_notice": "当前为公开样本数据与模拟验证结果，用于展示项目方法论与决策逻辑。",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    return ok(data)


# ============================================================
# 健康检查
# ============================================================
@app.route('/api/health', methods=['GET'])
def health():
    return ok({
        "status": "running",
        "version": "1.0.0-MVP",
        "project": "妆策AI",
        "engine": "available" if PREDICT_ENGINE_AVAILABLE else "mock",
        "timestamp": datetime.now().isoformat(),
    })


if __name__ == '__main__':
    print("=" * 50)
    print("🎯 妆策AI 后端服务启动")
    print("   http://localhost:5000")
    print(f"   预测引擎: {'✅ 已加载' if PREDICT_ENGINE_AVAILABLE else '⚠️ Mock模式'}")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
