# 妆策AI｜前端接口字段 JSON 示例（校赛 MVP 版）

> 用途：给前端、后端、算法同学直接对齐接口返回结构。当前为校赛 MVP 演示结构，后续可替换为真实接口。

## 1. 首页接口 `/api/home/overview`

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "project_name": "妆策AI",
    "project_slogan": "让品牌用预测代替试错，让增长更聪明",
    "current_stage": "校赛MVP",
    "data_notice": "当前结果基于公开样本数据与模拟验证逻辑生成",
    "sample_product": {
      "sample_product_name": "DEAR SEED 玫瑰修护洗发水",
      "primary_category": "洗护",
      "secondary_category": "修护洗发",
      "core_selling_points": ["修护", "柔顺", "玫瑰香氛"],
      "target_price_range": "100-150元",
      "target_user_group": "学生党女性用户"
    },
    "core_cards": {
      "potential_score": 8.2,
      "target_persona_summary": "学生党、宿舍场景、价格敏感型用户",
      "top_scene_tags": ["宿舍日常", "开学季"],
      "platform_priority": ["小红书", "社群私域", "视频号"]
    }
  }
}
```

## 2. 爆款预测接口 `/api/predict`

### 请求示例
```json
{
  "product_name": "DEAR SEED 玫瑰修护洗发水",
  "primary_category": "洗护",
  "secondary_category": "修护洗发",
  "selling_points": ["修护", "柔顺", "玫瑰香氛"],
  "price_range": "100-150元",
  "target_user": "学生党女性用户",
  "platform": "小红书"
}
```

### 响应示例
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "potential_score": 8.2,
    "score_explanation": "卖点组合与平台热点标签匹配度较高，具备较强内容传播潜力。",
    "target_persona": ["学生党女性用户", "宿舍场景用户", "价格敏感型用户"],
    "best_time": "开学季（8月20日-9月10日）",
    "risk_alert": [
      "避免只讲科研背书，需强化性价比与日常体验表达",
      "对价格敏感型用户建议突出学生可接受价格带"
    ],
    "key_tags": ["修护", "柔顺", "留香", "宿舍日常", "开学季"]
  }
}
```

## 3. 推荐决策接口 `/api/recommend`

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "recommended_products": [
      {
        "product_name": "DEAR SEED 玫瑰护手霜",
        "match_score": 92,
        "reason": "同香型、同场景、适合组合购买",
        "scenario": "宿舍日常"
      },
      {
        "product_name": "玫瑰香氛喷雾（示意）",
        "match_score": 85,
        "reason": "增强情绪价值表达",
        "scenario": "日常氛围感护理"
      }
    ],
    "recommended_scenes": ["宿舍日常", "开学季采购", "节日送礼"],
    "recommended_personas": ["学生党", "价格敏感型用户"],
    "recommended_platforms": ["小红书", "社群私域", "视频号"],
    "recommended_content_direction": ["高性价比宿舍洗护", "修护柔顺不毛躁", "玫瑰香氛体验"],
    "decision_summary": "优先围绕宿舍场景与学生党做种草表达。"
  }
}
```

## 4. 内容种草接口 `/api/content/generate`

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "xiaohongshu_titles": [
      "学生党宿舍洗护好物，顺滑和香味终于都有了",
      "开学季洗发水怎么选？这瓶修护香氛型我会回购"
    ],
    "community_scripts": [
      "这款更适合宿舍场景，香味和顺滑度都比较在线。",
      "如果预算卡在学生可接受区间，这款会是更稳的选择。"
    ],
    "video_hooks": [
      "如果你也是宿舍党，这瓶洗发水的顺滑感真的很加分。",
      "不是所有香氛洗发水都实用，但这瓶更像学生党友好型。"
    ],
    "tone_style": "真实分享 + 高性价比种草",
    "selling_point_expression": "修护、柔顺、香味有记忆点",
    "scenario_expression": "宿舍、开学季、日常复购"
  }
}
```

## 5. 数据看板接口 `/api/dashboard`

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "dashboard_potential_score": 8.2,
    "dashboard_trend_data": [
      { "date": "Day1", "score": 7.5 },
      { "date": "Day2", "score": 7.8 },
      { "date": "Day3", "score": 8.2 }
    ],
    "dashboard_scene_distribution": [
      { "name": "宿舍日常", "value": 46 },
      { "name": "开学季", "value": 32 },
      { "name": "日常复购", "value": 22 }
    ],
    "dashboard_persona_distribution": [
      { "name": "学生党", "value": 58 },
      { "name": "价格敏感型", "value": 24 },
      { "name": "年轻女性用户", "value": 18 }
    ],
    "dashboard_top_recommendations": ["玫瑰护手霜", "玫瑰香氛喷雾"],
    "dashboard_match_scores": [92, 85],
    "dashboard_insight_1": "宿舍场景是当前最强内容切入口。",
    "dashboard_insight_2": "学生党更关注顺滑感与价格接受度。",
    "dashboard_insight_3": "香氛表达有助于提升内容点击意愿。",
    "dashboard_notice": "当前为公开样本数据与模拟验证结果。"
  }
}
```
