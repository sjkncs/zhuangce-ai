# 妆策AI｜前端字段清单（校赛 MVP 版）

## 一、首页字段清单
### 1. 顶部基础信息
- project_name：项目名称
- project_slogan：项目口号
- current_stage：当前阶段（校赛MVP）
- data_notice：数据说明（模拟验证/样本验证）

### 2. 样板产品卡片
- sample_product_name：样板产品名称
- primary_category：一级品类
- secondary_category：二级子类
- core_selling_points：核心卖点
- target_price_range：目标价格带
- target_user_group：目标人群

### 3. 首页核心数据卡
- potential_score：传播潜力评分
- target_persona_summary：高潜人群概览
- top_scene_tags：高频场景标签
- platform_priority：推荐平台优先级

### 4. 首页按钮区
- btn_predict：开始预测
- btn_recommend：查看推荐
- btn_dashboard：进入看板

---

## 二、爆款预测页字段清单
### 1. 输入字段
- input_product_name：产品名称
- input_primary_category：一级品类
- input_secondary_category：二级子类
- input_selling_points：核心卖点
- input_price_range：价格区间
- input_target_user：目标人群
- input_platform：平台选择

### 2. 输出字段
- output_potential_score：传播潜力评分
- output_score_explanation：评分解释
- output_target_persona：高潜人群画像
- output_best_time：最佳推广时间
- output_risk_alert：风险提示
- output_key_tags：关键影响标签

---

## 三、推荐决策页字段清单
### 1. 推荐商品模块
- recommended_products：推荐商品数组
  - product_name：商品名称
  - match_score：匹配度
  - reason：推荐理由
  - scenario：适用场景

### 2. 推荐策略模块
- recommended_scenes：推荐场景
- recommended_personas：推荐人群
- recommended_platforms：推荐平台优先级
- recommended_content_direction：推荐内容方向
- decision_summary：决策总结

---

## 四、内容种草页字段清单
### 1. 标题文案模块
- xiaohongshu_titles：小红书标题数组

### 2. 社群文案模块
- community_scripts：社群话术数组

### 3. 视频开场模块
- video_hooks：短视频开场数组

### 4. 内容策略模块
- tone_style：内容调性
- selling_point_expression：推荐卖点表达
- scenario_expression：推荐场景表达

---

## 五、数据看板页字段清单
### 1. 评分与趋势模块
- dashboard_potential_score：潜力评分
- dashboard_trend_data：趋势数据
- dashboard_scene_distribution：场景分布
- dashboard_persona_distribution：人群分布

### 2. 推荐结果模块
- dashboard_top_recommendations：TOP推荐商品
- dashboard_match_scores：推荐匹配度

### 3. 结论模块
- dashboard_insight_1：核心结论1
- dashboard_insight_2：核心结论2
- dashboard_insight_3：核心结论3
- dashboard_notice：数据说明

---

## 六、统一前端说明字段
每一页建议都保留：
- data_type_notice：当前结果基于公开样本数据与模拟验证逻辑生成
- stage_notice：当前为校赛 MVP 概念验证版本
- replace_notice：后续可替换为真实 SKU 与真实数据
