# 妆策AI｜第二阶段推进计划

> 前置条件：第一阶段（项目立项层）已全部完成
> 目标：将分散的成果整合为可运行、可演示的系统

---

## 一、当前状态评估

### 已完成（第一阶段交付物）

| 类别 | 数量 | 说明 |
|------|------|------|
| 项目文档 | 6份MD | 品类/产品/预测目标/清单/模板全部确认 |
| 数据分析脚本 | 10个Python | 全部跑通，无报错 |
| 可视化图表 | 34张PNG | 按8大类别索引（见C-可视化图表索引） |
| 算法结果JSON | 21个JSON | 含预测/推荐/聚类/时序等全量输出 |
| 清洗数据 | 1个XLSX+1个CSV | 27,512行×19列+标注样本 |
| 后端API骨架 | 1个app.py+5个mock | Flask 5个接口已定义 |
| 前端页面骨架 | 5个Vue组件 | Home/Predict/Recommend/Content/Dashboard |

### 未完成（第二阶段目标）

| 任务 | 优先级 | 说明 |
|------|--------|------|
| 后端API对接真实数据 | P0 | mock JSON → 算法输出JSON |
| 前端页面UI完善 | P0 | 骨架 → 含图表和交互的完整页面 |
| 前后端联调 | P1 | API返回格式与前端组件对齐 |
| predict_result中平台引用更新 | ✅已完成 | "小红书"→"抖音电商"（第一阶段已修复） |
| 答辩材料准备 | P1 | PPT+演示流程+Q&A预案 |
| 部署上线 | P2 | Nginx+gunicorn生产部署 |

---

## 二、第二阶段分解为4个里程碑

### M1：后端真实数据对接（预计1-2天）

**目标**：5个API全部返回真实算法数据，不再依赖mock

**具体任务**：

1. 读取 `app.py` 当前代码结构
2. 建立数据转换层：将21个算法JSON按API需求重新组织
3. 逐个替换5个API的数据源：

| API | 数据源映射 |
|-----|-----------|
| `/api/home/overview` | clean_beauty_sales.xlsx统计 + predict_result_sample.json概要 |
| `/api/predict` | predict_result_sample.json + gbdt_model_result.json + timeseries_forecast.json |
| `/api/recommend` | item_cf_similarity.json + svd_recommendations.json + sasrec_results.json + lightgcn_results.json + kmeans_clusters.json |
| `/api/content/generate` | tfidf_selling_keywords.json + thompson_sampling.json + lda_topics.json |
| `/api/dashboard` | 综合全部数据源 + ucb_bandit_result.json + pagerank_scores.json |

4. ✅ 已更新 `predict_result_sample.json` 中的平台引用（小红书→抖音电商，内容key改为douyin前缀）
5. 每个API单元测试

**验收标准**：`curl localhost:5000/api/predict` 返回真实算法数据

### M2：前端页面完善（预计2-3天）

**目标**：5个页面从骨架升级为含图表和交互的完整页面

**具体任务**：

1. **HomeView.vue**：
   - 项目概览卡片（传播潜力评分7.5、SKU总数27512、洗护品类324条、算法数12+）
   - 项目闭环流程图（预测→推荐→内容→复盘）
   - 快速导航入口

2. **PredictView.vue**：
   - 传播潜力评分雷达图（功效/人群/场景/价格四维）
   - GBDT特征重要性柱状图（ECharts）
   - ARIMA 7天预测折线图（含置信区间阴影）
   - 最佳推广时间窗口展示

3. **RecommendView.vue**：
   - 推荐商品卡片列表（含匹配分/推荐理由/算法来源）
   - 用户分群雷达图（K-Means 4类用户画像）
   - 多算法融合对比表（ItemCF/SVD/SASRec/LightGCN）

4. **ContentView.vue**：
   - 抖音短视频脚本生成卡片（前3秒hook + 卖点 + 转化引导）
   - 直播话术模板（开场/讲解/逼单/追单）
   - TF-IDF关键词云图
   - Thompson Sampling策略优化结果

5. **DashboardView.vue**：
   - 多图表布局（2×3网格）
   - 品类分布饼图
   - 价格分布直方图
   - 用户行为漏斗图
   - 时序销量趋势线图
   - 品牌热度散点图
   - 关键指标卡片

**验收标准**：每个页面至少包含2个ECharts图表 + 结构化数据展示

### M3：前后端联调+部署（预计1天）

**具体任务**：

1. vite.config.js 配置开发代理（proxy → Flask 5000端口）
2. 前端axios封装统一请求模块
3. 5个页面逐一联调验证
4. Flask-CORS配置
5. 前端 `npm run build` 生产构建
6. Nginx配置反向代理
7. gunicorn 或 nohup 后台运行Flask

**验收标准**：浏览器访问公网IP能看到完整的5页面系统

### M4：答辩材料准备（预计1-2天）

**具体任务**：

1. 答辩PPT制作（10-15页）：
   - 项目背景与痛点
   - 技术方案（闭环架构图）
   - 数据分析成果（TOP 8图表）
   - 系统演示截图
   - 创新点与差异化
   - 未来规划

2. 演示流程设计（5分钟版/10分钟版）
3. 评委Q&A预案（20个预设问题+标准答案）
4. 项目亮点一页纸

**验收标准**：完整PPT + 流畅的演示流程

---

## 三、三个飞书机器人的分工

| 里程碑 | Moltbot（开发） | 研究员助手 | 产品经理助手 |
|--------|-----------------|-----------|-------------|
| M1 | **主力**：改app.py对接真实数据 | 验证数据展示准确性 | 确认API返回格式满足PRD |
| M2 | **主力**：Vue页面+ECharts图表 | 提供图表解读文案 | **主力**：5个页面PRD |
| M3 | **主力**：联调+部署 | — | 验收页面交互体验 |
| M4 | 系统演示录屏 | **主力**：行业背景+数据论据 | **主力**：PPT+演示流程+Q&A |

---

## 四、风险与应对

| 风险 | 影响 | 应对策略 |
|------|------|----------|
| 算法JSON格式与API需求不匹配 | M1延期 | 建数据转换层，不改原始JSON |
| ECharts图表渲染异常 | M2延期 | 先用表格展示，图表渐进增强 |
| 服务器环境缺依赖 | M3延期 | 提前准备requirements.txt+Dockerfile |
| 校赛评分标准不明确 | M4方向偏 | 找指导老师确认评分维度 |
| 团队成员时间冲突 | 整体延期 | 每日飞书同步进度，关键路径由Moltbot独立推进 |

---

## 五、立即可执行的3件事

1. **发给Moltbot**：让它开始M1任务（后端API对接真实数据），消息模板已准备好（见 `openclaw-deploy/飞书消息-发给Moltbot.md`）

2. **发给产品经理助手**：让它开始写5个页面的PRD
   > 请为以下5个页面各写一份PRD：HomeView（首页概览）、PredictView（爆款预测）、RecommendView（智能推荐）、ContentView（内容生成）、DashboardView（数据仪表盘）。每个PRD包含用户故事、功能清单、数据指标、验收标准。

3. **发给研究员助手**：让它读取数据并输出竞品分析
   > 请读取 /root/zhuangce-ai/project/data_analysis/output/clean_beauty_sales.xlsx，输出以下分析：1)洗护品类数据摘要 2)DEAR SEED品牌在数据中的定位 3)100-150元修护洗发水竞品格局。
