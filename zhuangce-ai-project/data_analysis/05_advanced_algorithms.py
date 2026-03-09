#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
妆策AI - 高阶算法增强脚本
阶段5：基于真实多源数据集的算法深化

数据来源：
  - E:/meiz/数据集/产品经理表格/产品话术.xlsx           → TF-IDF卖点提取
  - E:/meiz/数据集/2023年11月 美妆销售数据集/数据集.xlsx → 价格弹性 & 销量预测
  - E:/meiz/数据集/美妆用户行为数据集【脱敏】/*.xlsx      → GBDT购买预测 & Apriori关联规则

四大算法模块：
  A. TF-IDF 成分/卖点关键词提取 → 自动推荐卖点标签（接入 /api/predict）
  B. 价格弹性分析 + OLS回归 → 定价策略支撑
  C. GBDT 用户购买概率预测 → 精准人群触达
  D. Apriori 品类关联规则挖掘 → "买了A也看了B"推荐增强
"""

import os
import re
import json
import math
import warnings
import itertools
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 120

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

PATH_TALK     = r"E:/meiz/数据集/产品经理表格/产品话术.xlsx"
PATH_SALES    = r"E:/meiz/数据集/2023年11月 美妆销售数据集/数据集.xlsx"
PATH_BEHAVIOR = r"E:/meiz/数据集/美妆用户行为数据集【脱敏】/美妆用户行为数据集【脱敏】.xlsx"

BEHAVIOR_WEIGHTS = {"浏览": 1, "收藏": 2, "加购物车": 3, "购买": 5}


def save_fig(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, bbox_inches="tight", dpi=120)
    plt.close()
    print(f"  [OK] 图表已保存：{filename}")


# ============================================================
# 算法A：TF-IDF 卖点关键词提取
# 数据源：产品话术.xlsx（成分名称+功效+描述）
# 输出：top_selling_keywords.json，供 /api/predict 自动建议卖点标签
# ============================================================
def algo_tfidf_selling_points():
    print("\n" + "=" * 60)
    print("算法A：TF-IDF 成分/卖点关键词提取")

    try:
        raw = pd.read_excel(PATH_TALK)
    except FileNotFoundError:
        print("  [WARN] 话术文件未找到，使用内置样本演示")
        raw = pd.DataFrame({
            "col0": ["成分名", "透明质酸", "烟酰胺", "视黄醇", "积雪草"],
            "col1": ["功效", "保湿锁水 补水修护", "美白提亮 控油缩孔", "抗衰老 淡纹修护", "舒敏修护 促愈合"],
            "col2": ["描述", "HA能锁住千倍水分保湿天然保湿因子", "B3促进细胞代谢美白亮肤烟酰胺",
                     "维A酸前体刺激胶原蛋白生成抗衰老", "修护屏障镇静舒缓积雪草苷"],
        })

    # 提取所有文本单元格（过滤NaN）
    all_texts = []
    for col in raw.columns:
        texts = raw[col].dropna().astype(str).tolist()
        all_texts.extend(texts)

    # 清洗：去除短字符串、英文字母、数字
    def clean(t):
        t = re.sub(r"[A-Za-z0-9\(\)\（\）\n\r\t\s]+", " ", t)
        return t.strip()

    docs = [clean(t) for t in all_texts if len(str(t).strip()) > 4]
    docs = [d for d in docs if len(d) > 3]
    print(f"  有效文本片段数：{len(docs)}")

    # jieba分词
    try:
        import jieba
        def tokenize(text):
            return [w for w in jieba.cut(text) if len(w) >= 2]
    except ImportError:
        def tokenize(text):
            return [text[i:i+2] for i in range(len(text)-1)]

    tokenized = [tokenize(d) for d in docs]

    # TF-IDF 手工计算（不依赖sklearn）
    N = len(tokenized)
    df_count = defaultdict(int)
    for tokens in tokenized:
        for w in set(tokens):
            df_count[w] += 1

    idf = {w: math.log((N + 1) / (cnt + 1)) + 1 for w, cnt in df_count.items()}

    tfidf_scores = defaultdict(float)
    for tokens in tokenized:
        tf_map = Counter(tokens)
        total = len(tokens) or 1
        for w, cnt in tf_map.items():
            tfidf_scores[w] += (cnt / total) * idf.get(w, 1)

    # 过滤无意义词及碎片词（数字/标点/英文片段/单字）
    stopwords = {"NaN", "nan", "产品", "名称", "功效", "成分", "描述", "类型", "一种",
                 "可以", "具有", "使用", "适合", "皮肤", "含有", "进行", "因此", "通过",
                 "分：", "--", "、持", "油、", "分子", "品  ", "品 "}
    def is_valid_kw(w):
        if w in stopwords:
            return False
        if re.search(r'[\-\–\—、。，：；！？…\s]', w):
            return False
        if re.search(r'^[a-zA-Z0-9]+$', w):
            return False
        if not re.search(r'[\u4e00-\u9fff]', w):
            return False
        if len(w) < 2:
            return False
        return True
    top_keywords = sorted(
        [(w, round(s, 4)) for w, s in tfidf_scores.items() if is_valid_kw(w)],
        key=lambda x: x[1], reverse=True
    )[:60]

    print(f"\n  TOP20 卖点关键词（TF-IDF权重）：")
    for w, s in top_keywords[:20]:
        print(f"    {w}  {s:.4f}")

    # 分类映射：关键词 → 功效标签
    efficacy_map = {
        "保湿": ["透明质酸", "玻尿酸", "甘油", "水分", "锁水", "补水", "保水", "润肤"],
        "美白": ["烟酰胺", "美白", "亮肤", "提亮", "淡斑", "VC", "维C"],
        "抗衰": ["视黄醇", "胶原", "抗衰", "紧致", "弹力", "淡纹", "细纹"],
        "修护": ["积雪草", "修护", "屏障", "舒敏", "修复", "镇静", "愈合"],
        "控油": ["水杨酸", "控油", "祛痘", "清洁", "毛孔", "BHA"],
        "防晒": ["SPF", "防晒", "紫外线", "PA", "UVA", "UVB"],
    }

    keyword_efficacy = {}
    for kw, _ in top_keywords:
        for efficacy, tags in efficacy_map.items():
            if any(tag in kw for tag in tags):
                keyword_efficacy[kw] = efficacy
                break

    # 保存结果 JSON
    result = {
        "top_keywords": [{"word": w, "tfidf_score": s} for w, s in top_keywords],
        "keyword_to_efficacy": keyword_efficacy,
        "total_docs": N,
    }
    out_path = os.path.join(OUTPUT_DIR, "tfidf_selling_keywords.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"  [OK] 结果已保存：tfidf_selling_keywords.json（共{len(top_keywords)}个关键词）")

    # ── 可视化：TOP25词条权重柱状图 ──
    fig, ax = plt.subplots(figsize=(14, 7))
    top25 = top_keywords[:25]
    words  = [x[0] for x in top25]
    scores = [x[1] for x in top25]
    colors = ["#E74C3C" if keyword_efficacy.get(w) else "#5DADE2" for w in words]
    bars = ax.barh(words[::-1], scores[::-1], color=colors[::-1], alpha=0.85, height=0.7)

    # 添加功效标注
    for i, w in enumerate(words[::-1]):
        eff = keyword_efficacy.get(w, "")
        if eff:
            ax.text(scores[len(words)-1-i] + 0.005, i, eff,
                    va="center", fontsize=8.5, color="#E74C3C", fontweight="bold")

    ax.set_xlabel("TF-IDF 权重分", fontsize=11)
    ax.set_title("产品话术TF-IDF卖点关键词 TOP25\n（红色=已匹配功效标签，可自动注入 /api/predict）",
                 fontsize=13, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    from matplotlib.patches import Patch
    legend_elems = [Patch(facecolor="#E74C3C", alpha=0.8, label="已映射功效标签"),
                    Patch(facecolor="#5DADE2", alpha=0.8, label="待分类词汇")]
    ax.legend(handles=legend_elems, loc="lower right", fontsize=10)
    plt.tight_layout()
    save_fig("16_tfidf_selling_keywords.png")

    return result


# ============================================================
# 算法B：价格弹性分析 + OLS线性回归
# 数据源：2023年11月美妆销售数据集（售卖日期/价格/售卖数量/品牌）
# 输出：price_elasticity.json，定价策略支撑
# ============================================================
def algo_price_elasticity():
    print("\n" + "=" * 60)
    print("算法B：价格弹性分析 + OLS回归（2023年11月数据）")

    try:
        df = pd.read_excel(PATH_SALES)
        df.columns = ["date", "item_id", "name", "price", "sales", "comments", "brand"]
        df["price"]  = pd.to_numeric(df["price"],  errors="coerce")
        df["sales"]  = pd.to_numeric(df["sales"],  errors="coerce")
        df["comments"] = pd.to_numeric(df["comments"], errors="coerce")
        df = df.dropna(subset=["price", "sales"])
        print(f"  数据规模：{len(df):,} 行，品牌数：{df['brand'].nunique()}")
    except FileNotFoundError:
        print("  [WARN] 销售数据未找到，使用模拟数据")
        np.random.seed(42)
        n = 500
        prices = np.random.choice([39, 59, 89, 129, 179, 239, 299, 399], n)
        df = pd.DataFrame({
            "price":  prices,
            "sales":  (50000 / prices * np.random.uniform(0.5, 1.5, n)).astype(int),
            "brand":  np.random.choice(["自然堂", "珀莱雅", "薇诺娜", "花西子", "完美日记"], n),
            "comments": np.random.randint(100, 5000, n),
        })

    # 价格分段
    bins = [0, 50, 100, 200, 300, 500, 10000]
    labels = ["<50", "50-100", "100-200", "200-300", "300-500", "500+"]
    df["price_band"] = pd.cut(df["price"], bins=bins, labels=labels, right=False)

    band_stats = df.groupby("price_band", observed=True).agg(
        avg_sales=("sales", "mean"),
        total_sales=("sales", "sum"),
        sku_count=("price", "count"),
        avg_comments=("comments", "mean"),
    ).round(1)
    print(f"\n  价格带销量统计：\n{band_stats.to_string()}")

    # OLS 回归：log(sales) ~ log(price)，求价格弹性系数
    df_reg = df[(df["price"] > 0) & (df["sales"] > 0)].copy()
    df_reg["log_price"] = np.log(df_reg["price"])
    df_reg["log_sales"] = np.log(df_reg["sales"])

    # 最小二乘法手工实现
    x = df_reg["log_price"].values
    y = df_reg["log_sales"].values
    x_mean, y_mean = x.mean(), y.mean()
    beta = np.sum((x - x_mean) * (y - y_mean)) / np.sum((x - x_mean) ** 2)
    alpha = y_mean - beta * x_mean
    y_pred = alpha + beta * x
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y_mean) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0

    print(f"\n  价格弹性系数（双对数OLS）：β = {beta:.4f}")
    print(f"  R² = {r2:.4f}")
    if beta < -1:
        print(f"  结论：高弹性产品（|β|>1），降价可有效提升销量")
    elif beta < 0:
        print(f"  结论：弱弹性产品（-1<β<0），定价策略空间较大")
    else:
        print(f"  结论：正相关（β>0），高价品存在品牌溢价效应")

    # TOP品牌销量对比
    brand_perf = (df.groupby("brand")
                    .agg(total_sales=("sales", "sum"),
                         avg_price=("price", "mean"),
                         sku_cnt=("price", "count"))
                    .sort_values("total_sales", ascending=False)
                    .head(10))

    # ── 可视化（2×2）──
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))

    # (0,0) 价格带平均销量
    band_stats["avg_sales"].plot(kind="bar", ax=axes[0, 0],
                                  color="#3498DB", alpha=0.85, width=0.65, edgecolor="white")
    axes[0, 0].set_title("各价格带平均单品销量\n（找出最高性价比价格区间）",
                          fontsize=12, fontweight="bold")
    axes[0, 0].set_xlabel("价格带（元）", fontsize=10)
    axes[0, 0].set_ylabel("平均销量", fontsize=10)
    axes[0, 0].tick_params(axis="x", rotation=0)
    for bar in axes[0, 0].patches:
        axes[0, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                         f"{bar.get_height():,.0f}", ha="center", va="bottom", fontsize=9)
    axes[0, 0].spines["top"].set_visible(False)
    axes[0, 0].spines["right"].set_visible(False)

    # (0,1) 价格 vs 销量 散点 + OLS回归线
    sample = df_reg.sample(min(2000, len(df_reg)), random_state=42)
    axes[0, 1].scatter(sample["price"], sample["sales"],
                        alpha=0.25, s=8, color="#9B59B6", label="单品数据点")
    px = np.linspace(df_reg["price"].min(), df_reg["price"].max(), 200)
    py = np.exp(alpha) * px ** beta
    axes[0, 1].plot(px, py, color="#E74C3C", linewidth=2.5,
                     label=f"OLS回归线 (β={beta:.2f}, R²={r2:.3f})")
    axes[0, 1].set_title("价格 vs 销量 散点图 + OLS回归\n（弹性系数β反映降价对销量的拉动效果）",
                          fontsize=12, fontweight="bold")
    axes[0, 1].set_xlabel("价格（元）", fontsize=10)
    axes[0, 1].set_ylabel("销量", fontsize=10)
    axes[0, 1].legend(fontsize=9)
    axes[0, 1].set_xlim(0, min(df_reg["price"].quantile(0.95), 600))
    axes[0, 1].set_ylim(0, df_reg["sales"].quantile(0.95))
    axes[0, 1].spines["top"].set_visible(False)
    axes[0, 1].spines["right"].set_visible(False)

    # (1,0) TOP10品牌总销量
    brand_colors = plt.cm.Set3(np.linspace(0, 1, len(brand_perf)))
    axes[1, 0].barh(brand_perf.index[::-1], brand_perf["total_sales"][::-1],
                     color=brand_colors, alpha=0.85, height=0.65)
    axes[1, 0].set_title("TOP10品牌总销量对比\n（竞争格局一览）",
                          fontsize=12, fontweight="bold")
    axes[1, 0].set_xlabel("总销量", fontsize=10)
    axes[1, 0].spines["top"].set_visible(False)
    axes[1, 0].spines["right"].set_visible(False)

    # (1,1) 品牌平均客单价 vs 总销量气泡图
    bp = brand_perf.reset_index()
    bubble_size = bp["sku_cnt"] * 20
    sc = axes[1, 1].scatter(
        bp["avg_price"], bp["total_sales"],
        s=bubble_size, alpha=0.7,
        c=range(len(bp)), cmap="tab10", edgecolors="white", linewidths=1,
    )
    for _, row in bp.iterrows():
        axes[1, 1].annotate(row["brand"],
                             (row["avg_price"], row["total_sales"]),
                             textcoords="offset points", xytext=(5, 3), fontsize=9)
    axes[1, 1].set_title("品牌定价 vs 销量 气泡图\n（气泡大小=SKU数量，定位竞争象限）",
                          fontsize=12, fontweight="bold")
    axes[1, 1].set_xlabel("平均客单价（元）", fontsize=10)
    axes[1, 1].set_ylabel("总销量", fontsize=10)
    axes[1, 1].spines["top"].set_visible(False)
    axes[1, 1].spines["right"].set_visible(False)

    plt.tight_layout()
    save_fig("17_price_elasticity_analysis.png")

    result = {
        "elasticity_beta": round(float(beta), 4),
        "r_squared": round(float(r2), 4),
        "band_avg_sales": band_stats["avg_sales"].to_dict(),
        "optimal_price_band": str(band_stats["avg_sales"].idxmax()),
    }
    out_path = os.path.join(OUTPUT_DIR, "price_elasticity.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"  [OK] 结果已保存：price_elasticity.json")
    print(f"  最高销量价格带：{result['optimal_price_band']} 元")
    return result


# ============================================================
# 算法C：GBDT 用户购买概率预测
# 数据源：用户行为数据集（特征工程 → 二分类：是否购买）
# 输出：feature_importance.json，模型预测AUC
# ============================================================
def algo_gbdt_purchase_prediction(sample_rows=30000):
    print("\n" + "=" * 60)
    print("算法C：GBDT 用户购买概率预测（梯度提升树）")

    try:
        df = pd.read_excel(PATH_BEHAVIOR, nrows=sample_rows)
        rename = {}
        for c in df.columns:
            cl = c.strip()
            if "唯一" in cl: rename[c] = "user_id"
            elif cl == "商品ID": rename[c] = "item_id"
            elif "类别" in cl: rename[c] = "category_id"
            elif "行为" in cl: rename[c] = "behavior"
            elif "整点" in cl: rename[c] = "hour"
            elif "时间" in cl: rename[c] = "timestamp"
            elif "省份" in cl: rename[c] = "province"
        df = df.rename(columns=rename)
        df["timestamp"] = pd.to_datetime(df.get("timestamp"), errors="coerce")
        df["weight"] = df["behavior"].map(BEHAVIOR_WEIGHTS).fillna(1)
        print(f"  已加载 {len(df):,} 行行为记录")
    except FileNotFoundError:
        print("  [WARN] 行为数据未找到，使用模拟数据")
        np.random.seed(42)
        n = 5000
        df = pd.DataFrame({
            "user_id":     np.random.randint(1e7, 9e7, n),
            "category_id": np.random.randint(1000, 1030, n),
            "behavior":    np.random.choice(["浏览","浏览","浏览","收藏","加购物车","购买"],
                                             n, p=[0.60,0.10,0.10,0.10,0.06,0.04]),
            "hour":        np.random.randint(0, 24, n),
            "province":    np.random.choice(["天津市","广东省","北京市","上海市"], n),
        })
        df["timestamp"] = pd.date_range("2023-12-01", periods=n, freq="5min")
        df["weight"] = df["behavior"].map(BEHAVIOR_WEIGHTS).fillna(1)

    # ── 特征工程 ──
    # 用户级特征
    user_feat = df.groupby("user_id").agg(
        browse_cnt    = ("behavior", lambda x: (x == "浏览").sum()),
        collect_cnt   = ("behavior", lambda x: (x == "收藏").sum()),
        cart_cnt      = ("behavior", lambda x: (x == "加购物车").sum()),
        buy_cnt       = ("behavior", lambda x: (x == "购买").sum()),
        total_weight  = ("weight", "sum"),
        cat_diversity = ("category_id", "nunique"),
        fav_hour      = ("hour", lambda x: x.mode()[0] if len(x) > 0 else 0),
    ).reset_index()

    # 目标变量：该用户是否有购买行为
    user_feat["has_purchase"] = (user_feat["buy_cnt"] > 0).astype(int)
    pos = user_feat["has_purchase"].sum()
    neg = len(user_feat) - pos
    print(f"  样本分布：购买用户 {pos}，未购买用户 {neg}（正负比 1:{neg//max(pos,1):.0f}）")

    feature_cols = ["browse_cnt", "collect_cnt", "cart_cnt", "total_weight",
                    "cat_diversity", "fav_hour"]
    X = user_feat[feature_cols].fillna(0).values
    y = user_feat["has_purchase"].values

    # 手动标准化
    X_mean = X.mean(axis=0)
    X_std  = X.std(axis=0) + 1e-8
    X_norm = (X - X_mean) / X_std

    # 训练集 / 测试集 8:2 分割
    np.random.seed(42)
    idx = np.random.permutation(len(X_norm))
    split = int(len(idx) * 0.8)
    train_idx, test_idx = idx[:split], idx[split:]
    X_train, X_test = X_norm[train_idx], X_norm[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    # 使用 sklearn GradientBoostingClassifier（轻量无需GPU）
    try:
        from sklearn.ensemble import GradientBoostingClassifier
        from sklearn.metrics import roc_auc_score, classification_report

        model = GradientBoostingClassifier(
            n_estimators=80, max_depth=4,
            learning_rate=0.1, subsample=0.8,
            random_state=42
        )
        model.fit(X_train, y_train)
        y_prob  = model.predict_proba(X_test)[:, 1]
        y_pred  = (y_prob >= 0.5).astype(int)
        auc     = roc_auc_score(y_test, y_prob) if len(np.unique(y_test)) > 1 else 0.5
        feat_imp = dict(zip(feature_cols, model.feature_importances_.tolist()))

        print(f"\n  GBDT 训练完成")
        print(f"  测试集 AUC = {auc:.4f}")
        print(f"  特征重要性：")
        for feat, imp in sorted(feat_imp.items(), key=lambda x: x[1], reverse=True):
            print(f"    {feat}: {imp:.4f}")

        report = classification_report(y_test, y_pred, output_dict=True)
        model_backend = "sklearn_GBDT"

    except ImportError:
        # 备用：简单逻辑回归（sigmoid）手工实现
        print("  sklearn 未安装，使用手工逻辑回归备用方案")

        def sigmoid(z):
            return 1 / (1 + np.exp(-np.clip(z, -500, 500)))

        w = np.zeros(X_train.shape[1])
        b = 0.0
        lr = 0.05
        for _ in range(300):
            z = X_train @ w + b
            p = sigmoid(z)
            err = p - y_train
            w -= lr * X_train.T @ err / len(y_train)
            b -= lr * err.mean()

        y_prob = sigmoid(X_test @ w + b)
        y_pred = (y_prob >= 0.5).astype(int)
        auc = 0.0
        feat_imp = {f: abs(float(w[i])) for i, f in enumerate(feature_cols)}
        report = {}
        model_backend = "logistic_regression_fallback"

    # ── 可视化 ──
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # 特征重要性
    fi_sorted = sorted(feat_imp.items(), key=lambda x: x[1])
    feat_names_cn = {
        "browse_cnt":    "浏览次数",
        "collect_cnt":   "收藏次数",
        "cart_cnt":      "加购次数",
        "total_weight":  "行为加权总分",
        "cat_diversity": "浏览品类多样性",
        "fav_hour":      "活跃时段",
    }
    labels = [feat_names_cn.get(f, f) for f, _ in fi_sorted]
    values = [v for _, v in fi_sorted]
    bar_colors = ["#E74C3C" if v >= max(values) * 0.5 else "#5DADE2" for v in values]
    axes[0].barh(labels, values, color=bar_colors, alpha=0.85, height=0.65)
    axes[0].set_title(f"GBDT 特征重要性\n(AUC={auc:.3f}，模型={model_backend})",
                       fontsize=12, fontweight="bold")
    axes[0].set_xlabel("重要性分值", fontsize=10)
    for i, v in enumerate(values):
        axes[0].text(v + 0.002, i, f"{v:.3f}", va="center", fontsize=9)
    axes[0].spines["top"].set_visible(False)
    axes[0].spines["right"].set_visible(False)

    # 购买概率分布
    axes[1].hist(y_prob[y_test == 0], bins=30, alpha=0.65,
                  color="#5DADE2", label="未购买用户", density=True)
    axes[1].hist(y_prob[y_test == 1], bins=30, alpha=0.65,
                  color="#E74C3C", label="购买用户", density=True)
    axes[1].axvline(0.5, color="#F39C12", linestyle="--",
                     linewidth=2, label="决策阈值 0.5")
    axes[1].set_title("购买概率分布（购买 vs 未购买用户）\n（分布分离度越高，模型判别力越强）",
                       fontsize=12, fontweight="bold")
    axes[1].set_xlabel("预测购买概率", fontsize=10)
    axes[1].set_ylabel("密度", fontsize=10)
    axes[1].legend(fontsize=10)
    axes[1].spines["top"].set_visible(False)
    axes[1].spines["right"].set_visible(False)

    plt.tight_layout()
    save_fig("18_gbdt_purchase_prediction.png")

    result = {
        "model": model_backend,
        "auc": round(float(auc), 4),
        "feature_importance": {k: round(v, 4) for k, v in feat_imp.items()},
        "top_feature": max(feat_imp, key=feat_imp.get),
        "train_size": int(len(X_train)),
        "test_size": int(len(X_test)),
    }
    out_path = os.path.join(OUTPUT_DIR, "gbdt_model_result.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"  [OK] 结果已保存：gbdt_model_result.json（AUC={auc:.4f}）")
    return result


# ============================================================
# 算法D：Apriori 品类关联规则挖掘
# 数据源：用户行为数据集（同一用户行为序列）
# 输出：association_rules.json，"买了A也看B"推荐增强
# ============================================================
def algo_apriori_association(sample_rows=20000, min_support=0.02, min_confidence=0.3):
    print("\n" + "=" * 60)
    print('算法D：Apriori 品类关联规则挖掘（买了A也看了B）')

    try:
        df = pd.read_excel(PATH_BEHAVIOR, nrows=sample_rows)
        rename = {}
        for c in df.columns:
            cl = c.strip()
            if "唯一" in cl: rename[c] = "user_id"
            elif "类别" in cl: rename[c] = "category_id"
            elif "行为" in cl: rename[c] = "behavior"
        df = df.rename(columns=rename)
    except FileNotFoundError:
        np.random.seed(42)
        n = 5000
        df = pd.DataFrame({
            "user_id":     np.random.randint(1000, 5000, n),
            "category_id": np.random.randint(1000, 1025, n),
            "behavior":    np.random.choice(["浏览","收藏","加购物车","购买"],
                                             n, p=[0.70, 0.12, 0.10, 0.08]),
        })

    # 构建用户→品类集合（高于浏览权重的行为才算入事务）
    strong_behaviors = {"收藏", "加购物车", "购买"}
    user_cats = (df[df["behavior"].isin(strong_behaviors)]
                   .groupby("user_id")["category_id"]
                   .apply(lambda x: list(set(x.tolist())))
                   .reset_index())
    user_cats.columns = ["user_id", "categories"]
    # 过滤只有1个品类的用户（无关联）
    transactions = [cats for cats in user_cats["categories"] if len(cats) >= 2]
    n_trans = len(transactions)
    print(f"  有效事务数（>=2品类行为用户）：{n_trans}")

    if n_trans < 5:
        print("  事务数过少，跳过关联规则挖掘")
        return {}

    # Step1: 统计单品类支持度
    item_count = Counter()
    for trans in transactions:
        for item in trans:
            item_count[item] += 1

    freq_items = {item for item, cnt in item_count.items()
                  if cnt / n_trans >= min_support}
    print(f"  频繁品类数（support>={min_support}）：{len(freq_items)}")

    # Step2: 2-itemset 关联规则
    pair_count = Counter()
    for trans in transactions:
        filtered = [c for c in trans if c in freq_items]
        for pair in itertools.combinations(sorted(filtered), 2):
            pair_count[pair] += 1

    rules = []
    for (a, b), cnt in pair_count.items():
        support = cnt / n_trans
        if support < min_support:
            continue
        conf_ab = cnt / item_count[a] if item_count[a] > 0 else 0
        conf_ba = cnt / item_count[b] if item_count[b] > 0 else 0
        lift_ab = conf_ab / (item_count[b] / n_trans) if item_count[b] > 0 else 0
        lift_ba = conf_ba / (item_count[a] / n_trans) if item_count[a] > 0 else 0

        if conf_ab >= min_confidence:
            rules.append({
                "antecedent": int(a), "consequent": int(b),
                "support": round(support, 4),
                "confidence": round(conf_ab, 4),
                "lift": round(lift_ab, 4),
            })
        if conf_ba >= min_confidence:
            rules.append({
                "antecedent": int(b), "consequent": int(a),
                "support": round(support, 4),
                "confidence": round(conf_ba, 4),
                "lift": round(lift_ba, 4),
            })

    rules.sort(key=lambda x: x["lift"], reverse=True)
    top_rules = rules[:30]

    print(f"  挖掘出关联规则 {len(rules)} 条，TOP10：")
    for r in top_rules[:10]:
        print(f"    品类{r['antecedent']} → 品类{r['consequent']}"
              f"  support={r['support']:.3f}  conf={r['confidence']:.3f}  lift={r['lift']:.2f}")

    # ── 可视化 ──
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # 规则散点（support vs confidence，气泡=lift）
    if top_rules:
        sups   = [r["support"]    for r in top_rules]
        confs  = [r["confidence"] for r in top_rules]
        lifts  = [r["lift"]       for r in top_rules]
        sc = axes[0].scatter(sups, confs, s=[l * 80 for l in lifts],
                              c=lifts, cmap="YlOrRd", alpha=0.75,
                              edgecolors="white", linewidths=0.8)
        plt.colorbar(sc, ax=axes[0], label="Lift 提升度")
        axes[0].set_xlabel("支持度（Support）", fontsize=10)
        axes[0].set_ylabel("置信度（Confidence）", fontsize=10)
        axes[0].set_title("关联规则分布\n（气泡越大越红=提升度高=更有价值的关联）",
                           fontsize=12, fontweight="bold")
        axes[0].spines["top"].set_visible(False)
        axes[0].spines["right"].set_visible(False)

    # TOP15规则 Lift 排序
    top15 = top_rules[:15]
    if top15:
        rule_labels = [f"{r['antecedent']}→{r['consequent']}" for r in top15]
        lift_vals   = [r["lift"] for r in top15]
        bar_colors  = ["#E74C3C" if v >= 1.5 else "#5DADE2" for v in lift_vals]
        axes[1].barh(rule_labels[::-1], lift_vals[::-1],
                      color=bar_colors[::-1], alpha=0.85, height=0.65)
        axes[1].axvline(1.0, color="#F39C12", linestyle="--",
                         linewidth=1.5, label="Lift=1（随机基准）")
        axes[1].set_xlabel("Lift 提升度", fontsize=10)
        axes[1].set_title("TOP15 品类关联规则（按Lift排序）\n（Lift>1=正相关，越大=关联越强）",
                           fontsize=12, fontweight="bold")
        axes[1].legend(fontsize=9)
        axes[1].spines["top"].set_visible(False)
        axes[1].spines["right"].set_visible(False)

    plt.tight_layout()
    save_fig("19_apriori_association_rules.png")

    out_path = os.path.join(OUTPUT_DIR, "association_rules.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"rules": top_rules, "total_transactions": n_trans,
                   "min_support": min_support, "min_confidence": min_confidence},
                  f, ensure_ascii=False, indent=2)
    print(f"  结果已保存：association_rules.json（{len(top_rules)} 条规则）")
    return {"total_rules": len(rules), "top_rules": top_rules[:5]}


# ============================================================
# 主函数
# ============================================================
def main():
    print("妆策AI — 高阶算法增强脚本启动")
    print("=" * 60)

    results = {}
    results["tfidf"]         = algo_tfidf_selling_points()
    results["price_elastic"] = algo_price_elasticity()
    results["gbdt"]          = algo_gbdt_purchase_prediction(sample_rows=30000)
    results["apriori"]       = algo_apriori_association(sample_rows=20000, min_support=0.01, min_confidence=0.12)

    print("\n" + "=" * 60)
    print("高阶算法全部完成！新增4张可视化图表：")
    charts = [
        "16_tfidf_selling_keywords.png    TF-IDF卖点关键词提取（产品话术数据）",
        "17_price_elasticity_analysis.png 价格弹性OLS回归+品牌竞争分析（11月销售数据）",
        "18_gbdt_purchase_prediction.png  GBDT购买预测特征重要性+概率分布",
        "19_apriori_association_rules.png Apriori品类关联规则散点+Lift排序",
    ]
    for c in charts:
        print(f"   {c}")

    print(f"\n新增输出文件（可供后端直接调用）：")
    files = [
        "tfidf_selling_keywords.json  → /api/predict 自动建议卖点标签",
        "price_elasticity.json        → /api/dashboard 定价策略洞察",
        "gbdt_model_result.json       → /api/predict 用户购买概率评分",
        "association_rules.json       → /api/recommend 关联规则推荐增强",
    ]
    for f in files:
        print(f"   {f}")

    gbdt_auc = results["gbdt"].get("auc", 0)
    top_feat = results["gbdt"].get("top_feature", "")
    opt_band = results["price_elastic"].get("optimal_price_band", "")
    n_rules  = results["apriori"].get("total_rules", 0)
    kw_count = len(results["tfidf"].get("top_keywords", []))

    print("\n核心洞察：")
    print(f"  A. TF-IDF提取{kw_count}个卖点关键词，可自动注入推荐卖点标签，替代人工填写")
    print(f"  B. 最高销量价格带：{opt_band}元，OLS回归揭示价格弹性系数")
    print(f"  C. GBDT购买预测AUC={gbdt_auc:.3f}，最重要特征：{top_feat}")
    print(f'  D. Apriori挖掘{n_rules}条品类关联规则，支持买了A也推B协同推荐')

    return results


if __name__ == "__main__":
    main()
