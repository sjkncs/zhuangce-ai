#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
妆策AI - 时序预测与图算法模块
阶段8：P1优先级算法

数据来源：2023年11月销售数据集 / 用户行为数据集【脱敏】

三大算法：
  A. 指数平滑 + ARIMA 销量时序预测
     - 来源：Box-Jenkins 1970 / Holt-Winters 1960
     - 功能：对11月每日销量做短期预测，输出未来7天预测值 + 置信区间
  B. PageRank 商品影响力评分
     - 来源：Brin & Page 1998（Google创始论文）
     - 功能：基于用户共浏行为构建商品有向图，PageRank得分=商品影响力
  C. Item2Vec 商品嵌入 + t-SNE 可视化
     - 来源：Barkan & Koenigstein 2016（微软研究院）
     - 功能：将用户行为序列视为"句子"，商品视为"词"，用Word2Vec学习嵌入
"""

import os
import json
import warnings
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

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

PATH_BEHAVIOR = r"E:/meiz/数据集/美妆用户行为数据集【脱敏】/美妆用户行为数据集【脱敏】.xlsx"
PATH_SALES    = r"E:/meiz/数据集/2023年11月 美妆销售数据集/数据集.xlsx"


def save_fig(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, bbox_inches="tight", dpi=120)
    plt.close()
    print(f"  [OK] 图表已保存：{filename}")


def load_behavior(sample_rows=20000):
    try:
        df = pd.read_excel(PATH_BEHAVIOR, nrows=sample_rows)
        rename = {}
        for c in df.columns:
            cl = c.strip()
            if "唯一" in cl:     rename[c] = "user_id"
            elif cl == "商品ID":  rename[c] = "item_id"
            elif "类别" in cl:   rename[c] = "category_id"
            elif "行为" in cl:   rename[c] = "behavior"
            elif "整点" in cl:   rename[c] = "hour"
            elif "时间" in cl:   rename[c] = "timestamp"
        df = df.rename(columns=rename)
        if "user_id" in df.columns:
            df["user_id"] = df["user_id"].astype(str).str.extract(r"(\d+)")[0]
            df["user_id"] = pd.to_numeric(df["user_id"], errors="coerce")
        if "category_id" in df.columns:
            df["category_id"] = pd.to_numeric(df["category_id"], errors="coerce")
        if "item_id" in df.columns:
            df["item_id"] = pd.to_numeric(df["item_id"], errors="coerce")
        df["timestamp"] = pd.to_datetime(df.get("timestamp"), errors="coerce")
        print(f"  已加载 {len(df):,} 行行为记录")
        return df
    except FileNotFoundError:
        print("  [WARN] 行为数据未找到，使用模拟数据")
        np.random.seed(42)
        n = 6000
        behaviors = np.random.choice(
            ["浏览", "收藏", "加购物车", "购买"],
            n, p=[0.70, 0.12, 0.10, 0.08])
        return pd.DataFrame({
            "user_id":     np.random.randint(10000, 50000, n),
            "item_id":     np.random.randint(100, 500, n),
            "category_id": np.random.randint(1000, 1030, n),
            "behavior":    behaviors,
            "hour":        np.random.randint(0, 24, n),
            "timestamp":   pd.date_range("2023-12-01", periods=n, freq="3min"),
        })


# ============================================================
# 算法A：指数平滑 + ARIMA 销量时序预测
# 来源：Box-Jenkins 1970 / Holt-Winters 1960
# ============================================================
def algo_timeseries_forecast():
    """
    1. 按日聚合销量 → 时序序列
    2. 简单指数平滑（SES）+ Holt线性趋势 + ARIMA(p,d,q)
    3. 输出7天预测 + 置信区间
    """
    print("\n" + "=" * 60)
    print("算法A：指数平滑 + ARIMA 销量时序预测")
    print("  来源：Box-Jenkins 1970 / Holt-Winters 1960")

    try:
        df = pd.read_excel(PATH_SALES)
        cols = list(df.columns)
        df.columns = ["date", "item_id", "name", "price", "sales", "comments", "brand"]
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date", "sales"])
        df["sales"] = pd.to_numeric(df["sales"], errors="coerce").fillna(0)
    except FileNotFoundError:
        print("  [WARN] 销售数据未找到，使用模拟数据")
        dates = pd.date_range("2023-11-01", "2023-11-30")
        np.random.seed(42)
        base = 5000 + np.arange(30) * 100
        noise = np.random.normal(0, 500, 30)
        # 双11高峰
        base[10] *= 3.5
        base[11] *= 2.8
        sales_vals = (base + noise).clip(min=100)
        df = pd.DataFrame({"date": dates, "sales": sales_vals})

    # 日级聚合
    daily = df.groupby("date")["sales"].sum().sort_index()
    daily = daily[daily.index.notna()]
    print(f"  日级时序长度：{len(daily)} 天")
    print(f"  日均销量：{daily.mean():,.0f}  峰值：{daily.max():,.0f}")

    if len(daily) < 5:
        print("  [WARN] 数据天数不足，跳过时序预测")
        return {}

    # ── 方法1：简单指数平滑（SES） ──
    alpha = 0.3
    ses = [daily.iloc[0]]
    for i in range(1, len(daily)):
        ses.append(alpha * daily.iloc[i] + (1 - alpha) * ses[-1])
    ses = np.array(ses)

    # ── 方法2：Holt 线性趋势 ──
    alpha_h, beta_h = 0.3, 0.1
    level = [float(daily.iloc[0])]
    trend = [float(daily.iloc[1] - daily.iloc[0]) if len(daily) > 1 else 0.0]
    for i in range(1, len(daily)):
        new_level = alpha_h * float(daily.iloc[i]) + (1 - alpha_h) * (level[-1] + trend[-1])
        new_trend = beta_h * (new_level - level[-1]) + (1 - beta_h) * trend[-1]
        level.append(new_level)
        trend.append(new_trend)

    # 7天预测
    forecast_days = 7
    holt_forecast = [level[-1] + (i + 1) * trend[-1] for i in range(forecast_days)]

    # ── 方法3：ARIMA (手工实现简化版：差分+AR(1)) ──
    diff = daily.diff().dropna().values
    if len(diff) > 2:
        # AR(1): diff[t] = phi * diff[t-1] + epsilon
        y = diff[1:]
        x = diff[:-1]
        phi = float(np.corrcoef(x, y)[0, 1]) if len(x) > 1 else 0.5
        phi = max(min(phi, 0.95), -0.95)
        residuals = y - phi * x
        sigma = float(np.std(residuals))

        arima_forecast = []
        last_diff = float(diff[-1])
        last_val = float(daily.iloc[-1])
        for i in range(forecast_days):
            next_diff = phi * last_diff
            last_val = last_val + next_diff
            arima_forecast.append(last_val)
            last_diff = next_diff
    else:
        arima_forecast = [float(daily.iloc[-1])] * forecast_days
        sigma = float(daily.std())
        phi = 0

    # 置信区间（±1.96σ）
    ci_upper = [v + 1.96 * sigma * np.sqrt(i + 1) for i, v in enumerate(arima_forecast)]
    ci_lower = [v - 1.96 * sigma * np.sqrt(i + 1) for i, v in enumerate(arima_forecast)]

    forecast_dates = pd.date_range(daily.index[-1] + pd.Timedelta(days=1), periods=forecast_days)

    print(f"\n  AR(1)系数 phi={phi:.4f}  残差标准差 sigma={sigma:,.0f}")
    print(f"  未来{forecast_days}天 ARIMA 预测：")
    for d, v, lo, hi in zip(forecast_dates, arima_forecast, ci_lower, ci_upper):
        print(f"    {d.strftime('%Y-%m-%d')}  预测={v:,.0f}  95%CI=[{lo:,.0f}, {hi:,.0f}]")

    # ── 可视化 ──
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # (1) 历史 + 三种方法拟合
    axes[0].plot(daily.index, daily.values, "o-", color="#2C3E50", linewidth=1.5,
                 markersize=4, label="实际销量", alpha=0.8)
    axes[0].plot(daily.index, ses, "--", color="#3498DB", linewidth=1.5,
                 label=f"SES (alpha={alpha})", alpha=0.7)
    holt_fit = [level[i] for i in range(len(daily))]
    axes[0].plot(daily.index, holt_fit, "--", color="#E74C3C", linewidth=1.5,
                 label="Holt线性趋势", alpha=0.7)
    axes[0].set_title("销量时序拟合对比\n（SES vs Holt线性趋势 vs 实际值）",
                       fontsize=12, fontweight="bold")
    axes[0].set_xlabel("日期", fontsize=10)
    axes[0].set_ylabel("日销量", fontsize=10)
    axes[0].legend(fontsize=9)
    axes[0].tick_params(axis="x", rotation=30)
    axes[0].spines["top"].set_visible(False)
    axes[0].spines["right"].set_visible(False)

    # (2) ARIMA预测 + 置信区间
    axes[1].plot(daily.index, daily.values, "o-", color="#2C3E50", linewidth=1.5,
                 markersize=4, label="历史销量")
    axes[1].plot(forecast_dates, arima_forecast, "s-", color="#E74C3C",
                 linewidth=2, markersize=6, label="ARIMA预测")
    axes[1].plot(forecast_dates, holt_forecast, "^--", color="#27AE60",
                 linewidth=1.5, markersize=5, label="Holt预测")
    axes[1].fill_between(forecast_dates, ci_lower, ci_upper,
                          color="#E74C3C", alpha=0.15, label="95% 置信区间")
    axes[1].axvline(x=daily.index[-1], color="#95A5A6", linestyle=":", linewidth=1.5)
    axes[1].set_title(f"未来{forecast_days}天销量预测（ARIMA+Holt）\n"
                       f"AR(1) phi={phi:.3f}",
                       fontsize=12, fontweight="bold")
    axes[1].set_xlabel("日期", fontsize=10)
    axes[1].set_ylabel("日销量", fontsize=10)
    axes[1].legend(fontsize=9)
    axes[1].tick_params(axis="x", rotation=30)
    axes[1].spines["top"].set_visible(False)
    axes[1].spines["right"].set_visible(False)

    plt.tight_layout()
    save_fig("26_timeseries_forecast.png")

    result = {
        "series_length": len(daily),
        "daily_mean": round(float(daily.mean()), 0),
        "daily_peak": round(float(daily.max()), 0),
        "ar1_phi": round(float(phi), 4),
        "forecast": [
            {"date": d.strftime("%Y-%m-%d"),
             "predicted": round(float(v), 0),
             "ci_lower": round(float(lo), 0),
             "ci_upper": round(float(hi), 0)}
            for d, v, lo, hi in zip(forecast_dates, arima_forecast, ci_lower, ci_upper)
        ],
    }
    with open(os.path.join(OUTPUT_DIR, "timeseries_forecast.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("  [OK] 预测结果已保存：timeseries_forecast.json")
    return result


# ============================================================
# 算法B：PageRank 商品影响力评分
# 来源：Brin & Page 1998（Google 创始论文）
# ============================================================
def algo_pagerank(df, damping=0.85, max_iter=100, tol=1e-6):
    """
    构建商品共浏图：
      如果同一用户先后浏览了商品A和商品B，则 A→B 有一条有向边。
    对该有向图执行 PageRank 迭代：
      PR(i) = (1-d)/N + d * Σ PR(j)/OutDeg(j)
    商品PageRank得分 = 该商品在用户浏览流中的"中心地位"
    """
    print("\n" + "=" * 60)
    print("算法B：PageRank 商品影响力评分")
    print("  来源：Brin & Page 1998 — Google 创始论文核心算法")

    df_sorted = df.dropna(subset=["user_id", "category_id", "timestamp"]).copy()
    df_sorted = df_sorted.sort_values(["user_id", "timestamp"])

    # 构建品类级有向图（品类粒度更有意义）
    edges = defaultdict(lambda: defaultdict(int))
    for uid, group in df_sorted.groupby("user_id"):
        cats = group["category_id"].tolist()
        for i in range(len(cats) - 1):
            if cats[i] != cats[i + 1]:  # 去除自环
                edges[cats[i]][cats[i + 1]] += 1

    all_nodes = set()
    for src, dst_dict in edges.items():
        all_nodes.add(src)
        all_nodes.update(dst_dict.keys())
    all_nodes = sorted(all_nodes)
    N = len(all_nodes)
    node2idx = {n: i for i, n in enumerate(all_nodes)}
    print(f"  图节点数（品类）：{N}，边数：{sum(len(d) for d in edges.values())}")

    if N < 2:
        print("  [WARN] 节点过少，跳过PageRank")
        return {}

    # 手工实现 PageRank 迭代
    pr = np.ones(N) / N
    out_degree = np.zeros(N)
    for src, dst_dict in edges.items():
        out_degree[node2idx[src]] = sum(dst_dict.values())

    for iteration in range(max_iter):
        pr_new = np.ones(N) * (1 - damping) / N
        for src, dst_dict in edges.items():
            src_idx = node2idx[src]
            if out_degree[src_idx] == 0:
                continue
            for dst, weight in dst_dict.items():
                dst_idx = node2idx[dst]
                pr_new[dst_idx] += damping * pr[src_idx] * (weight / out_degree[src_idx])

        # 处理悬挂节点（无出边）
        dangling_mass = damping * sum(pr[node2idx[n]] for n in all_nodes
                                       if out_degree[node2idx[n]] == 0)
        pr_new += dangling_mass / N

        diff = np.abs(pr_new - pr).sum()
        pr = pr_new
        if diff < tol:
            print(f"  PageRank在第{iteration+1}轮收敛（diff={diff:.2e}）")
            break

    # 排序输出
    pr_ranked = sorted(zip(all_nodes, pr), key=lambda x: x[1], reverse=True)
    print(f"\n  TOP15 最具影响力品类（PageRank得分）：")
    for cat, score in pr_ranked[:15]:
        bar = "#" * int(score * N * 10)
        print(f"    品类{int(cat):>6}  PR={score:.6f}  {bar}")

    # ── 可视化 ──
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # (1) TOP20 PageRank 柱状图
    top20 = pr_ranked[:20]
    cats_top = [f"{int(c)}" for c, _ in top20]
    scores_top = [s for _, s in top20]
    colors = ["#E74C3C" if i < 3 else "#3498DB" if i < 10 else "#AED6F1"
              for i in range(len(top20))]
    axes[0].barh(cats_top[::-1], scores_top[::-1], color=colors[::-1], alpha=0.85, height=0.7)
    for i, (c, s) in enumerate(zip(cats_top[::-1], scores_top[::-1])):
        axes[0].text(s + max(scores_top) * 0.01, i, f"{s:.5f}", va="center", fontsize=8)
    axes[0].set_xlabel("PageRank 得分", fontsize=10)
    axes[0].set_ylabel("品类ID", fontsize=10)
    axes[0].set_title("TOP20 商品品类 PageRank 影响力排名\n"
                       "（红色=最核心品类，蓝色=重要品类）",
                       fontsize=12, fontweight="bold")
    axes[0].spines["top"].set_visible(False)
    axes[0].spines["right"].set_visible(False)

    # (2) PageRank分布直方图
    all_pr = [s for _, s in pr_ranked]
    axes[1].hist(all_pr, bins=30, color="#5DADE2", alpha=0.75, edgecolor="white")
    axes[1].axvline(x=np.mean(all_pr), color="#E74C3C", linestyle="--",
                    linewidth=2, label=f"均值={np.mean(all_pr):.5f}")
    axes[1].axvline(x=1/N, color="#27AE60", linestyle=":",
                    linewidth=2, label=f"均匀分布={1/N:.5f}")
    axes[1].set_title("PageRank 得分分布\n（偏右=少数品类占据核心地位，符合幂律分布）",
                       fontsize=12, fontweight="bold")
    axes[1].set_xlabel("PageRank 得分", fontsize=10)
    axes[1].set_ylabel("品类数量", fontsize=10)
    axes[1].legend(fontsize=9)
    axes[1].spines["top"].set_visible(False)
    axes[1].spines["right"].set_visible(False)

    plt.tight_layout()
    save_fig("27_pagerank_influence.png")

    result = {
        "n_nodes": N,
        "n_edges": sum(len(d) for d in edges.values()),
        "damping": damping,
        "top10": [{"category": int(c), "pagerank": round(float(s), 6)}
                  for c, s in pr_ranked[:10]],
        "gini_coefficient": round(float(1 - 2 * np.sum(
            np.sort(np.array(all_pr)) * np.arange(1, N + 1) / (N * np.sum(all_pr))
        ) + (N + 1) / N), 4),
    }
    with open(os.path.join(OUTPUT_DIR, "pagerank_scores.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("  [OK] PageRank结果已保存：pagerank_scores.json")
    return result


# ============================================================
# 算法C：Item2Vec 商品嵌入 + t-SNE 可视化
# 来源：Barkan & Koenigstein 2016（微软研究院）
# 轻量实现：用 SVD 代替 Word2Vec（无需 gensim 依赖），PPMI矩阵分解
# ============================================================
def algo_item2vec(df, embed_dim=32, window=5):
    """
    Item2Vec 轻量版（PPMI + SVD）：
    1. 将每个用户的行为序列视为一个"句子"，品类视为"词"
    2. 统计品类共现矩阵（窗口大小=window）
    3. 计算 PPMI（正逐点互信息）矩阵
    4. SVD 降维得到品类嵌入向量
    5. t-SNE 可视化品类在嵌入空间的分布
    """
    print("\n" + "=" * 60)
    print("算法C：Item2Vec 商品嵌入（PPMI+SVD 轻量版）")
    print("  来源：Barkan & Koenigstein 2016 — 微软研究院")
    print(f"  参数：嵌入维度={embed_dim}，共现窗口={window}")

    df_sorted = df.dropna(subset=["user_id", "category_id"]).copy()
    df_sorted = df_sorted.sort_values(["user_id", "timestamp"])

    # 构建用户行为序列
    sequences = []
    for uid, group in df_sorted.groupby("user_id"):
        seq = group["category_id"].tolist()
        if len(seq) >= 2:
            sequences.append(seq)

    print(f"  用户行为序列数：{len(sequences)}")
    print(f"  平均序列长度：{np.mean([len(s) for s in sequences]):.1f}")

    # 统计品类词汇
    all_cats = set()
    for seq in sequences:
        all_cats.update(seq)
    all_cats = sorted(all_cats)
    cat2idx = {c: i for i, c in enumerate(all_cats)}
    n_cats = len(all_cats)
    print(f"  品类词汇量：{n_cats}")

    if n_cats < 3:
        print("  [WARN] 品类数过少，跳过Item2Vec")
        return {}

    # ── 共现矩阵 ──
    cooccurrence = np.zeros((n_cats, n_cats), dtype=float)
    cat_freq = Counter()
    total_pairs = 0

    for seq in sequences:
        for i, cat in enumerate(seq):
            cat_freq[cat] += 1
            for j in range(max(0, i - window), min(len(seq), i + window + 1)):
                if i != j:
                    ci, cj = cat2idx[cat], cat2idx[seq[j]]
                    cooccurrence[ci, cj] += 1
                    total_pairs += 1

    # ── PPMI 矩阵 ──
    D = total_pairs if total_pairs > 0 else 1
    freq_arr = np.array([cat_freq.get(c, 0) for c in all_cats], dtype=float)
    # P(w) = freq(w) / D
    pw = freq_arr / D
    # PPMI(i,j) = max(0, log(P(i,j) / (P(i)*P(j))))
    ppmi = np.zeros_like(cooccurrence)
    for i in range(n_cats):
        for j in range(n_cats):
            if cooccurrence[i, j] > 0 and pw[i] > 0 and pw[j] > 0:
                pij = cooccurrence[i, j] / D
                pmi = np.log(pij / (pw[i] * pw[j]) + 1e-12)
                ppmi[i, j] = max(0, pmi)

    # ── SVD 降维 ──
    from sklearn.decomposition import TruncatedSVD
    from scipy.sparse import csr_matrix

    actual_dim = min(embed_dim, n_cats - 1)
    svd = TruncatedSVD(n_components=actual_dim, random_state=42)
    embeddings = svd.fit_transform(csr_matrix(ppmi))
    explained = svd.explained_variance_ratio_.sum()
    print(f"  SVD嵌入维度：{actual_dim}，解释方差：{explained*100:.1f}%")

    # ── 品类相似度 TOP 示例 ──
    from sklearn.metrics.pairwise import cosine_similarity
    sim_matrix = cosine_similarity(embeddings)
    np.fill_diagonal(sim_matrix, -1)

    print(f"\n  品类相似度 TOP10（Item2Vec余弦相似度）：")
    flat_idx = np.argsort(sim_matrix.ravel())[::-1][:10]
    for idx in flat_idx:
        i, j = divmod(idx, n_cats)
        print(f"    品类{int(all_cats[i])} ↔ 品类{int(all_cats[j])}  "
              f"similarity={sim_matrix[i, j]:.4f}")

    # ── t-SNE 可视化 ──
    if n_cats >= 5:
        from sklearn.manifold import TSNE
        perp = min(30, n_cats - 1)
        tsne = TSNE(n_components=2, random_state=42, perplexity=max(2, perp))
        emb_2d = tsne.fit_transform(embeddings)
    else:
        emb_2d = embeddings[:, :2] if embeddings.shape[1] >= 2 else np.zeros((n_cats, 2))

    # ── 可视化 ──
    fig, axes = plt.subplots(1, 2, figsize=(15, 7))

    # (1) t-SNE 嵌入空间
    # 用频次着色
    freq_vals = np.array([cat_freq.get(c, 0) for c in all_cats])
    sc = axes[0].scatter(emb_2d[:, 0], emb_2d[:, 1], c=freq_vals,
                         cmap="YlOrRd", s=50, alpha=0.7, edgecolors="white", linewidths=0.5)
    plt.colorbar(sc, ax=axes[0], label="行为频次", shrink=0.8)
    # 标注高频品类
    top_freq_idx = np.argsort(freq_vals)[::-1][:8]
    for idx in top_freq_idx:
        axes[0].annotate(f"{int(all_cats[idx])}", (emb_2d[idx, 0], emb_2d[idx, 1]),
                          fontsize=8, fontweight="bold", alpha=0.8,
                          xytext=(5, 5), textcoords="offset points")
    axes[0].set_title("Item2Vec 品类嵌入 t-SNE 可视化\n"
                       "（距离近=用户共浏行为相似，颜色深=高频品类）",
                       fontsize=12, fontweight="bold")
    axes[0].set_xlabel("t-SNE 维度1", fontsize=10)
    axes[0].set_ylabel("t-SNE 维度2", fontsize=10)
    axes[0].spines["top"].set_visible(False)
    axes[0].spines["right"].set_visible(False)

    # (2) 品类共现热力图（TOP15高频品类）
    top15_cats = [c for c, _ in sorted(cat_freq.items(), key=lambda x: x[1], reverse=True)[:15]]
    top15_idx  = [cat2idx[c] for c in top15_cats if c in cat2idx]
    if len(top15_idx) >= 3:
        sub_ppmi = ppmi[np.ix_(top15_idx, top15_idx)]
        try:
            import seaborn as sns
            cat_labels = [str(int(all_cats[i])) for i in top15_idx]
            sns.heatmap(sub_ppmi, xticklabels=cat_labels, yticklabels=cat_labels,
                        cmap="Blues", ax=axes[1], linewidths=0.3, linecolor="white",
                        annot=sub_ppmi > 0, fmt=".1f",
                        cbar_kws={"label": "PPMI值"}, annot_kws={"size": 7})
        except ImportError:
            im = axes[1].imshow(sub_ppmi, cmap="Blues", aspect="auto")
            plt.colorbar(im, ax=axes[1])

    axes[1].set_title("TOP15高频品类 PPMI 共现矩阵\n"
                       "（PPMI>0=品类经常被同一用户浏览）",
                       fontsize=12, fontweight="bold")
    axes[1].set_xlabel("品类ID", fontsize=10)
    axes[1].set_ylabel("品类ID", fontsize=10)

    plt.tight_layout()
    save_fig("28_item2vec_embeddings.png")

    # 保存嵌入向量
    embedding_dict = {int(all_cats[i]): embeddings[i].tolist() for i in range(n_cats)}
    result = {
        "n_categories": n_cats,
        "embed_dim": actual_dim,
        "explained_variance": round(float(explained), 4),
        "n_sequences": len(sequences),
        "top10_similar_pairs": [
            {"cat_a": int(all_cats[divmod(idx, n_cats)[0]]),
             "cat_b": int(all_cats[divmod(idx, n_cats)[1]]),
             "similarity": round(float(sim_matrix[divmod(idx, n_cats)[0],
                                                   divmod(idx, n_cats)[1]]), 4)}
            for idx in flat_idx[:10]
        ],
    }
    with open(os.path.join(OUTPUT_DIR, "item2vec_embeddings.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("  [OK] Item2Vec嵌入结果已保存：item2vec_embeddings.json")
    return result


# ============================================================
# 主函数
# ============================================================
def main(sample_rows=20000):
    print("妆策AI — 时序预测与图算法模块启动（阶段8）")
    print("=" * 60)

    df = load_behavior(sample_rows=sample_rows)

    results = {}
    results["timeseries"] = algo_timeseries_forecast()
    results["pagerank"]   = algo_pagerank(df)
    results["item2vec"]   = algo_item2vec(df)

    print("\n" + "=" * 60)
    print("P1算法全部完成！新增3张图表：")
    charts = [
        "26_timeseries_forecast.png      ARIMA+Holt销量时序预测（含置信区间）",
        "27_pagerank_influence.png       PageRank品类影响力排名（Google核心算法）",
        "28_item2vec_embeddings.png      Item2Vec品类嵌入t-SNE可视化（微软研究院）",
    ]
    for c in charts:
        print(f"   {c}")

    print("\n新增输出文件：")
    files = [
        "timeseries_forecast.json     → 7天销量预测（备货/营销决策支持）",
        "pagerank_scores.json         → 品类影响力排名（选品优先级）",
        "item2vec_embeddings.json     → 品类向量嵌入（相似品类推荐）",
    ]
    for f in files:
        print(f"   {f}")

    ts_peak  = results["timeseries"].get("daily_peak", 0)
    pr_top   = results["pagerank"].get("top10", [{}])[0].get("category", "")
    i2v_cats = results["item2vec"].get("n_categories", 0)

    print("\n核心洞察：")
    print(f"  A. ARIMA时序预测覆盖未来7天，峰值日销量{ts_peak:,.0f}，可指导备货策略")
    print(f"  B. PageRank识别最核心品类={pr_top}（该品类在用户浏览流中处于枢纽地位）")
    print(f"  C. Item2Vec对{i2v_cats}个品类做向量化嵌入，支持相似品类发现与跨品类推荐")

    return results


if __name__ == "__main__":
    main(sample_rows=20000)
