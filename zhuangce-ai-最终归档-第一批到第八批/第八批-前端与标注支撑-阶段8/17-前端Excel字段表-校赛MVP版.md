# 妆策AI｜前端 Excel 字段表（校赛 MVP 版）

> 用途：可直接复制到 Excel / WPS 表格中，供产品、前端、后端统一字段。

| 页面 | 模块 | 字段名 | 中文名 | 类型 | 示例值 | 是否必填 | 说明 |
|---|---|---|---|---|---|---|---|
| 首页 | 顶部信息 | project_name | 项目名称 | string | 妆策AI | 是 | 固定展示 |
| 首页 | 顶部信息 | project_slogan | 项目口号 | string | 让品牌用预测代替试错 | 是 | 固定展示 |
| 首页 | 顶部信息 | current_stage | 当前阶段 | string | 校赛MVP | 是 | 固定展示 |
| 首页 | 顶部信息 | data_notice | 数据说明 | string | 当前结果基于公开样本数据与模拟验证逻辑生成 | 是 | 提示说明 |
| 首页 | 产品卡 | sample_product_name | 样板产品名称 | string | DEAR SEED 玫瑰修护洗发水 | 是 | 样板产品 |
| 首页 | 产品卡 | primary_category | 一级品类 | string | 洗护 | 是 | 分类字段 |
| 首页 | 产品卡 | secondary_category | 二级子类 | string | 修护洗发 | 是 | 分类字段 |
| 首页 | 产品卡 | core_selling_points | 核心卖点 | string[] | 修护,柔顺,玫瑰香氛 | 是 | 多值数组 |
| 首页 | 产品卡 | target_price_range | 目标价格带 | string | 100-150元 | 是 | 价格区间 |
| 首页 | 产品卡 | target_user_group | 目标人群 | string | 学生党女性用户 | 是 | 人群描述 |
| 首页 | 数据卡 | potential_score | 传播潜力评分 | number | 8.2 | 是 | 1-10 |
| 首页 | 数据卡 | target_persona_summary | 高潜人群概览 | string | 学生党、宿舍场景、价格敏感型用户 | 是 | 摘要展示 |
| 首页 | 数据卡 | top_scene_tags | 高频场景标签 | string[] | 宿舍日常,开学季 | 是 | 多值数组 |
| 首页 | 数据卡 | platform_priority | 推荐平台优先级 | string[] | 小红书,社群私域,视频号 | 是 | 顺序展示 |
| 预测页 | 输入 | product_name | 产品名称 | string | DEAR SEED 玫瑰修护洗发水 | 是 | 表单输入 |
| 预测页 | 输入 | selling_points | 核心卖点 | string[] | 修护,柔顺,玫瑰香氛 | 是 | 表单输入 |
| 预测页 | 输入 | price_range | 价格区间 | string | 100-150元 | 是 | 表单输入 |
| 预测页 | 输入 | target_user | 目标人群 | string | 学生党女性用户 | 是 | 表单输入 |
| 预测页 | 输入 | platform | 平台 | string | 小红书 | 是 | 表单输入 |
| 预测页 | 输出 | potential_score | 传播潜力评分 | number | 8.2 | 是 | 结果字段 |
| 预测页 | 输出 | score_explanation | 评分解释 | string | 卖点组合与平台热点标签匹配度较高 | 是 | 结果字段 |
| 预测页 | 输出 | target_persona | 高潜人群画像 | string[] | 学生党女性用户,宿舍场景用户 | 是 | 结果字段 |
| 预测页 | 输出 | best_time | 最佳推广时间 | string | 开学季 | 是 | 结果字段 |
| 预测页 | 输出 | risk_alert | 风险提示 | string[] | 避免只讲科研背书 | 否 | 结果字段 |
| 预测页 | 输出 | key_tags | 关键影响标签 | string[] | 修护,柔顺,留香 | 是 | 结果字段 |
| 推荐页 | 列表 | recommended_products | 推荐商品列表 | object[] | 见接口示例 | 是 | 数组对象 |
| 推荐页 | 列表 | product_name | 商品名称 | string | DEAR SEED 玫瑰护手霜 | 是 | 子字段 |
| 推荐页 | 列表 | match_score | 匹配度 | number | 92 | 是 | 子字段 |
| 推荐页 | 列表 | reason | 推荐理由 | string | 同香型、同场景 | 是 | 子字段 |
| 推荐页 | 列表 | scenario | 适用场景 | string | 宿舍日常 | 是 | 子字段 |
| 推荐页 | 策略 | recommended_scenes | 推荐场景 | string[] | 宿舍日常,开学季采购 | 是 | 数组 |
| 推荐页 | 策略 | recommended_personas | 推荐人群 | string[] | 学生党,价格敏感型用户 | 是 | 数组 |
| 推荐页 | 策略 | recommended_platforms | 推荐平台 | string[] | 小红书,社群私域 | 是 | 数组 |
| 推荐页 | 策略 | recommended_content_direction | 推荐内容方向 | string[] | 高性价比宿舍洗护 | 是 | 数组 |
| 推荐页 | 策略 | decision_summary | 决策总结 | string | 优先围绕宿舍场景与学生党做表达 | 是 | 摘要 |
| 内容页 | 文案 | xiaohongshu_titles | 小红书标题 | string[] | 学生党宿舍洗护好物 | 是 | 数组 |
| 内容页 | 文案 | community_scripts | 社群话术 | string[] | 这款更适合宿舍场景 | 是 | 数组 |
| 内容页 | 文案 | video_hooks | 视频开场 | string[] | 如果你也是宿舍党 | 是 | 数组 |
| 内容页 | 策略 | tone_style | 内容调性 | string | 真实分享+高性价比种草 | 是 | 文案策略 |
| 内容页 | 策略 | selling_point_expression | 卖点表达 | string | 修护、柔顺、香味有记忆点 | 是 | 文案策略 |
| 内容页 | 策略 | scenario_expression | 场景表达 | string | 宿舍、开学季、日常复购 | 是 | 文案策略 |
| 看板页 | 趋势 | dashboard_potential_score | 潜力评分 | number | 8.2 | 是 | 看板字段 |
| 看板页 | 趋势 | dashboard_trend_data | 趋势数据 | object[] | 见接口示例 | 是 | 图表数据 |
| 看板页 | 分布 | dashboard_scene_distribution | 场景分布 | object[] | 见接口示例 | 是 | 图表数据 |
| 看板页 | 分布 | dashboard_persona_distribution | 人群分布 | object[] | 见接口示例 | 是 | 图表数据 |
| 看板页 | 推荐 | dashboard_top_recommendations | TOP推荐商品 | string[] | 玫瑰护手霜 | 是 | 摘要字段 |
| 看板页 | 推荐 | dashboard_match_scores | 推荐匹配度 | number[] | 92,85 | 是 | 摘要字段 |
| 看板页 | 结论 | dashboard_insight_1 | 核心结论1 | string | 宿舍场景是最强切入口 | 是 | 摘要字段 |
| 看板页 | 结论 | dashboard_insight_2 | 核心结论2 | string | 学生党更关注顺滑感与价格带 | 是 | 摘要字段 |
| 看板页 | 结论 | dashboard_insight_3 | 核心结论3 | string | 香氛表达有助于提升点击意愿 | 是 | 摘要字段 |
| 通用 | 提示 | stage_notice | 阶段说明 | string | 当前为校赛MVP概念验证版本 | 是 | 页脚说明 |
| 通用 | 提示 | replace_notice | 替换说明 | string | 后续可替换为真实SKU与真实数据 | 是 | 页脚说明 |
