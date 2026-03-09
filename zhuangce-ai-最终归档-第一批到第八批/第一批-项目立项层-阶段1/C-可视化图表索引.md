# 妆策AI｜可视化图表索引

> 共 34 张图表，由 10 个数据分析脚本生成
> 存放路径：`data_analysis/output/`

---

## 一、探索性分析（EDA）— 脚本02

| 编号 | 文件名 | 内容说明 | 答辩用途 |
|------|--------|----------|----------|
| 01 | 01_brand_sku_count.png | 品牌SKU数量TOP排名 | 展示数据规模和品牌覆盖 |
| 02 | 02_brand_sales.png | 品牌销售额排名 | 行业竞争格局可视化 |
| 03 | 03_category_distribution.png | 品类分布饼图/柱状图 | 说明洗护品类占比 |
| 04 | 04_price_distribution.png | 价格分布直方图 | 证明100-150元价格带选择合理 |
| 05 | 05_haircare_deep_analysis.png | 洗护品类深度分析 | 核心品类深挖 |
| 06 | 06_keyword_heatmap.png | 关键词热力图 | 卖点关键词频率 |
| 07 | 07_potential_score_distribution.png | 传播潜力评分分布 | 潜力评分方法论展示 |
| 08 | 08_brand_heat_scatter.png | 品牌热度散点图 | 品牌竞争定位 |
| 09 | 09_price_boxplot.png | 价格箱线图 | 各品类价格带对比 |
| 10 | 10_time_series_sales.png | 时间序列销量趋势 | 销量随时间变化规律 |

## 二、用户行为分析 — 脚本04

| 编号 | 文件名 | 内容说明 | 答辩用途 |
|------|--------|----------|----------|
| 11 | 11_funnel_analysis.png | 用户行为漏斗图 | 浏览→收藏→加购→购买转化率 |
| 12 | 12_item_cf_similarity_heatmap.png | ItemCF相似度热力图 | 协同过滤推荐依据 |
| 13 | 13_rfm_segmentation.png | RFM用户分层 | 用户价值分层策略 |
| 14 | 14_peak_time_analysis.png | 活跃时段分析 | 最佳推送时间 |
| 15 | 15_geographic_analysis.png | 地域分布分析 | 目标区域定位 |

## 三、高级算法 — 脚本05

| 编号 | 文件名 | 内容说明 | 答辩用途 |
|------|--------|----------|----------|
| 16 | 16_tfidf_selling_keywords.png | TF-IDF卖点关键词 | 数据驱动的卖点提取 |
| 17 | 17_price_elasticity_analysis.png | OLS价格弹性分析 | 定价策略的数据支撑 |
| 18 | 18_gbdt_purchase_prediction.png | GBDT购买预测+特征重要性 | **核心图表**：AUC=0.9993 |
| 19 | 19_apriori_association_rules.png | Apriori关联规则 | 交叉推荐依据 |

## 四、前沿算法 — 脚本06

| 编号 | 文件名 | 内容说明 | 答辩用途 |
|------|--------|----------|----------|
| 20 | 20_din_attention_score.png | DIN注意力评分 | 深度学习推荐展示 |
| 21 | 21_ucb_bandit_content_strategy.png | UCB多臂老虎机策略 | 内容策略探索vs利用 |
| 22 | 22_dijkstra_journey_graph.png | Dijkstra用户旅程图 | 最短转化路径 |
| 23 | 23_feedback_weight_tuning.png | 反馈权重调参 | 模型优化过程 |

## 五、聚类与矩阵分解 — 脚本07

| 编号 | 文件名 | 内容说明 | 答辩用途 |
|------|--------|----------|----------|
| 24 | 24_kmeans_user_clustering.png | K-Means用户聚类 | **核心图表**：4类用户画像 |
| 25 | 25_svd_matrix_factorization.png | SVD矩阵分解 | 隐因子推荐可视化 |

## 六、时序与图算法 — 脚本08

| 编号 | 文件名 | 内容说明 | 答辩用途 |
|------|--------|----------|----------|
| 26 | 26_timeseries_forecast.png | ARIMA时序预测 | **核心图表**：7天销量预测曲线 |
| 27 | 27_pagerank_influence.png | PageRank影响力排名 | 品牌/品类影响力 |
| 28 | 28_item2vec_embeddings.png | Item2Vec嵌入可视化 | 商品向量空间分布 |

## 七、主题模型与马尔可夫 — 脚本09

| 编号 | 文件名 | 内容说明 | 答辩用途 |
|------|--------|----------|----------|
| 29 | 29_lda_topic_model.png | LDA主题模型 | 内容主题分布 |
| 30 | 30_markov_chain_prediction.png | Markov Chain状态转移 | 用户行为预测 |

## 八、论文级算法 — 脚本10

| 编号 | 文件名 | 内容说明 | 答辩用途 |
|------|--------|----------|----------|
| 31 | 31_sasrec_attention.png | SASRec注意力机制 | 序列推荐可视化 |
| 32 | 32_lightgcn_graph.png | LightGCN图结构 | 图神经网络推荐 |
| 33 | 33_contrastive_learning.png | 对比学习 | 表示学习增强 |
| 34 | 34_thompson_sampling.png | Thompson Sampling | **核心图表**：策略优化收敛 |

---

## 答辩推荐使用图表（TOP 8）

| 优先级 | 图表 | 用途 |
|--------|------|------|
| ★★★ | 18_gbdt_purchase_prediction.png | GBDT AUC=0.9993，特征重要性，最有说服力 |
| ★★★ | 24_kmeans_user_clustering.png | 4类用户画像，直观展示用户分群 |
| ★★★ | 26_timeseries_forecast.png | 7天销量预测曲线，时间维度说服力 |
| ★★☆ | 11_funnel_analysis.png | 行为漏斗，展示转化率分析能力 |
| ★★☆ | 16_tfidf_selling_keywords.png | 卖点关键词，内容策略数据依据 |
| ★★☆ | 34_thompson_sampling.png | 策略优化收敛曲线，强化学习应用 |
| ★☆☆ | 03_category_distribution.png | 品类分布，背景介绍用 |
| ★☆☆ | 04_price_distribution.png | 价格分布，定价策略依据 |
