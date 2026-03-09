# 妆策AI：面向美妆新零售实战场景的智能推荐与营销转化平台

> **校赛MVP版本** | 让品牌用预测代替试错，让增长更聪明。

---

## 项目定位

妆策AI聚焦"预测→决策→转化→复盘"最小闭环，帮助美妆品牌回答四个核心问题：
- **什么值得推？** → 爆款预测引擎
- **推给谁？** → 高潜人群画像
- **什么时候推？** → 最佳推广时间建议
- **推完如何复盘？** → 数据看板与结论

## 样板案例（模拟验证）

| 字段 | 内容 |
|---|---|
| 品牌 | DEAR SEED |
| 产品 | 玫瑰修护洗发水 |
| 品类 | 洗护 / 修护洗发 |
| 卖点 | 修护 + 柔顺 + 玫瑰香氛 |
| 价格带 | 100-150 元 |
| 目标人群 | 学生党女性用户 |
| 传播潜力评分 | **8.2 / 10** |
| 推荐场景 | 宿舍日常 / 开学季 |
| 推荐平台 | 小红书 > 社群 > 视频号 |

> 注：以上结果基于公开内容样本、标签体系与模拟验证逻辑生成，不等同于真实运营数据。

---

## 核心功能

| 功能模块 | 描述 | 接口 |
|---|---|---|
| 用户洞察 | 提取热词、用户标签、场景标签 | `GET /api/home/overview` |
| 爆款预测 | 基于卖点标签匹配输出传播潜力评分 | `POST /api/predict` |
| 推荐决策 | 输出推荐商品、场景、平台优先级 | `POST /api/recommend` |
| 内容种草 | 生成小红书标题、社群话术、视频开场 | `POST /api/content/generate` |
| 转化复盘 | ECharts看板展示预测-推荐-复盘链路 | `GET /api/dashboard` |

---

## 技术栈

| 层次 | 技术选型 |
|---|---|
| 数据分析 | Python 3.10+, Pandas, NumPy, Matplotlib, Seaborn, Jieba |
| 预测引擎 | 基于标签评分 + 协同过滤思路 + 多因子加权 |
| 后端框架 | Flask 3.x, Flask-CORS |
| 前端框架 | Vue 3 + Vite |
| UI组件库 | Element Plus |
| 数据可视化 | ECharts 5.x (Apache ECharts) |
| 数据存储 | JSON / CSV（校赛MVP阶段） |

---

## 数据来源

| 数据集 | 用途 | 路径 |
|---|---|---|
| 2023年11月美妆销售数据集 | EDA分析、品类洞察、价格分布 | `E:/meiz/数据集/2023年11月 美妆销售数据集/数据集.xlsx` |
| 美妆用户行为数据集【脱敏】 | 用户行为分析、人群画像 | `E:/meiz/数据集/美妆用户行为数据集【脱敏】/...xlsx` |
| 天猫双十一美妆销售数据 | 品牌/品类分析模板参考 | `E:/meiz/天猫双十一美妆销售数据分析模板/...` |
| 产品经理表格 | 竞品分析、新品开发参考 | `E:/meiz/数据集/产品经理表格/` |

---

## 项目目录结构

```
zhuangce-ai-project/
├── README.md                        # 本文件
├── backend/                         # Flask 后端
│   ├── app.py                       # 主应用入口（5个API）
│   ├── requirements.txt             # Python依赖
│   ├── predict_engine.py            # 爆款预测引擎（标签评分+多因子加权）
│   ├── recommend_engine.py          # 推荐引擎（场景+人群+协同过滤思路）
│   ├── content_engine.py            # 内容生成引擎（模板+关键词）
│   └── data/                        # 数据文件
│       ├── annotation_examples.csv  # 标注示例20条
│       ├── label_config.json        # 标签体系配置
│       └── mock_responses/          # Mock JSON（演示用）
│           ├── home_overview.json
│           ├── predict_response.json
│           ├── recommend_response.json
│           ├── content_response.json
│           └── dashboard_response.json
├── data_analysis/                   # 数据分析层（独立可运行）
│   ├── 01_data_cleaning.py          # 数据清洗（引用真实数据集）
│   ├── 02_eda_analysis.py           # EDA探索分析（matplotlib可视化）
│   ├── 03_predict_model.py          # 预测模型构建（标签评分算法）
│   └── output/                      # 分析结果输出（图表/CSV）
├── frontend/                        # Vue3 前端
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── router/index.js
│       ├── views/
│       │   ├── HomeView.vue         # 首页（项目概览+产品卡片）
│       │   ├── PredictView.vue      # 爆款预测页
│       │   ├── RecommendView.vue    # 推荐决策页
│       │   ├── ContentView.vue      # 内容种草生成页
│       │   └── DashboardView.vue    # 数据看板（ECharts图表）
│       └── components/
│           ├── NavBar.vue
│           └── ScoreCard.vue
├── docs/                            # 项目文档归档（引用第1-8批归档）
│   └── see: ../zhuangce-ai-最终归档-第一批到第八批/
└── start.bat                        # 一键启动脚本
```

---

## 快速启动

### 启动后端
```bash
cd backend
pip install -r requirements.txt
python app.py
# 后端运行在 http://localhost:5000
```

### 启动前端
```bash
cd frontend
npm install
npm run dev
# 前端运行在 http://localhost:5173
```

或使用一键启动脚本：
```bash
start.bat
```

---

## 标签体系（洗护品类）

| 标签层 | 示例标签 |
|---|---|
| 品类标签 | 洗护、修护洗发、柔顺护发、香氛洗护 |
| 功效标签 | 修护、柔顺、留香、控油、蓬松、去屑 |
| 人群标签 | 学生党、价格敏感型、通勤党、染烫受损发质用户 |
| 场景标签 | 宿舍日常、开学季、换季护理、日常复购 |
| 情绪标签 | 高级感、治愈感、清新感、氛围感、安心感 |
| 价格标签 | 平价、高性价比、中端、学生可接受 |

---

## 传播潜力评分算法说明

评分因子（权重加权）：
1. **卖点标签匹配度**（40%）：卖点词在热词库中的共现频率
2. **人群标签匹配度**（25%）：目标人群与高潜人群的重叠度
3. **场景标签适配性**（20%）：场景标签在内容中的传播热度
4. **价格带竞争力**（15%）：价格区间在目标人群中的接受度

---

## 项目口号
**让品牌用预测代替试错，让增长更聪明。**

---

## 阶段说明
- **当前阶段**：校赛 MVP 概念验证版本
- **数据说明**：当前结果基于公开样本数据、标注示例与模拟验证逻辑生成
- **后续升级**：省赛阶段可扩充样本量、接入真实运营数据、升级预测模型

## 参考文档
- 第一批：项目立项层（产品确认/预测目标文档）
- 第二批：项目结构层（标签体系/数据采集字段）
- 第四批：答辩严谨版（GitHub README/演讲稿/攻防问答）
- 第七批：DEAR SEED样板页（样板文案/种草30条）
- 第八批：前端与标注支撑（字段清单/接口说明/开发包）
