#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
妆策AI - 聚类与矩阵分解模块
阶段7：P0优先级算法

数据来源：用户行为数据集【脱敏】/ 2023年11月销售数据集

两大核心算法：
  A. K-Means 用户聚类 + 轮廓系数自动选K
     - 来源：MacQueen 1967；Kaufman & Rousseeuw 1990（轮廓系数）
     - 功能：基于行为特征（浏览/收藏/加购/购买次数 + 品类多样性 + 活跃时段）
             无监督分群，输出用户画像标签，补充RFM的有监督视角
  B. SVD 矩阵分解推荐（截断SVD / FunkSVD 思路）
     - 来源：Netflix Prize 2006，Simon Funk
     - 功能：将用户-品类交互矩阵分解为隐因子，生成Top-N品类推荐
             与ItemCF互补：ItemCF依赖显式共现，SVD捕捉隐含偏好
"""

import os
import json
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import Counter
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.decomposition import TruncatedSVD
from scipy.sparse import csr_matrix
warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 120

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

PATH_BEHAVIOR = r"E:/meiz/数据集/美妆用户行为数据集【脱敏】/美妆用户行为数据集【脱敏】.xlsx"
PATH_SALES    = r"E:/meiz/数据集/2023年11月 美妆销售数据集/数据集.xlsx"

BEHAVIOR_WEIGHTS = {"浏览": 1, "收藏": 2, "加购物车": 3, "购买": 5}


def save_fig(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, bbox_inches="tight", dpi=120)
    plt.close()
    print(f"  [OK] 图表已保存：{filename}")


def load_behavior(sample_rows=30000):
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
        df["timestamp"] = pd.to_datetime(df.get("timestamp"), errors="coerce")
        print(f"  已加载 {len(df):,} 行行为记录")
        return df
    except FileNotFoundError:
        print("  [WARN] 行为数据未找到，使用模拟数据")
        np.random.seed(42)
        n = 8000
        behaviors = np.random.choice(
            ["浏览", "收藏", "加购物车", "购买"],
            n, p=[0.70, 0.12, 0.10, 0.08]
        )
        return pd.DataFrame({
            "user_id":     np.random.randint(10000, 50000, n),
            "item_id":     np.random.randint(100000, 999999, n),
            "category_id": np.random.randint(1000, 1030, n),
            "behavior":    behaviors,
            "hour":        np.random.randint(0, 24, n),
            "timestamp":   pd.date_range("2023-12-01", periods=n, freq="3min"),
        })


# ============================================================
# 算法A：K-Means 用户聚类 + 轮廓系数自动选K
# 来源：MacQueen 1967 / Kaufman & Rousseeuw 1990
# ============================================================
def algo_kmeans_clustering(df):
    """
    特征工程 → StandardScaler标准化 → Elbow+Silhouette选K → K-Means聚类
    输出：每个聚类的行为画像标签 + 聚类结果JSON
    """
    print("\n" + "=" * 60)
    print("算法A：K-Means 用户聚类（无监督分群 + 轮廓系数自动选K）")
    print("  来源：MacQueen 1967 / Kaufman & Rousseeuw 1990")

    # ── 特征工程 ──
    user_feat = df.groupby("user_id").agg(
        browse_cnt   = ("behavior", lambda x: (x == "浏览").sum()),
        collect_cnt  = ("behavior", lambda x: (x == "收藏").sum()),
        cart_cnt     = ("behavior", lambda x: (x == "加购物车").sum()),
        buy_cnt      = ("behavior", lambda x: (x == "购买").sum()),
        total_actions = ("behavior", "count"),
        cat_diversity = ("category_id", "nunique"),
        avg_hour      = ("hour", "mean"),
    ).reset_index()

    user_feat["buy_rate"]     = user_feat["buy_cnt"] / user_feat["total_actions"].replace(0, 1)
    user_feat["cart_rate"]    = user_feat["cart_cnt"] / user_feat["total_actions"].replace(0, 1)
    user_feat["collect_rate"] = user_feat["collect_cnt"] / user_feat["total_actions"].replace(0, 1)

    feature_cols = ["browse_cnt", "collect_cnt", "cart_cnt", "buy_cnt",
                    "cat_diversity", "avg_hour", "buy_rate", "cart_rate", "collect_rate"]
    X = user_feat[feature_cols].fillna(0).values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    n_users = len(X_scaled)
    print(f"  用户数：{n_users}，特征维度：{len(feature_cols)}")

    # ── Elbow + Silhouette 选K ──
    K_range = range(2, min(9, n_users // 2))
    inertias    = []
    silhouettes = []

    for k in K_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10, max_iter=300)
        labels = km.fit_predict(X_scaled)
        inertias.append(km.inertia_)
        sil = silhouette_score(X_scaled, labels)
        silhouettes.append(sil)
        print(f"    K={k}  Inertia={km.inertia_:.1f}  Silhouette={sil:.4f}")

    best_k = list(K_range)[int(np.argmax(silhouettes))]
    best_sil = max(silhouettes)
    print(f"\n  [OK] 最优K={best_k}（轮廓系数={best_sil:.4f}）")

    # ── 最终聚类 ──
    km_final = KMeans(n_clusters=best_k, random_state=42, n_init=10, max_iter=300)
    user_feat["cluster"] = km_final.fit_predict(X_scaled)

    # 聚类画像
    cluster_profiles = []
    print(f"\n  聚类画像（K={best_k}）：")
    for c in range(best_k):
        mask = user_feat["cluster"] == c
        profile = {
            "cluster_id": c,
            "user_count": int(mask.sum()),
            "pct": round(float(mask.sum() / n_users * 100), 1),
            "avg_browse": round(float(user_feat.loc[mask, "browse_cnt"].mean()), 1),
            "avg_collect": round(float(user_feat.loc[mask, "collect_cnt"].mean()), 1),
            "avg_cart": round(float(user_feat.loc[mask, "cart_cnt"].mean()), 1),
            "avg_buy": round(float(user_feat.loc[mask, "buy_cnt"].mean()), 1),
            "avg_cat_diversity": round(float(user_feat.loc[mask, "cat_diversity"].mean()), 1),
            "avg_buy_rate": round(float(user_feat.loc[mask, "buy_rate"].mean()), 4),
            "avg_hour": round(float(user_feat.loc[mask, "avg_hour"].mean()), 1),
        }
        # 自动命名
        if profile["avg_buy_rate"] > 0.15:
            profile["label"] = "高转化忠实用户"
        elif profile["avg_cart"] > profile["avg_browse"] * 0.3:
            profile["label"] = "高意向犹豫型"
        elif profile["avg_browse"] > user_feat["browse_cnt"].mean() * 1.5:
            profile["label"] = "深度浏览型"
        elif profile["avg_cat_diversity"] > user_feat["cat_diversity"].mean() * 1.3:
            profile["label"] = "广泛探索型"
        elif profile["avg_collect"] > user_feat["collect_cnt"].mean() * 1.5:
            profile["label"] = "收藏囤货型"
        elif profile["avg_hour"] > 20 or profile["avg_hour"] < 6:
            profile["label"] = "夜间活跃型"
        else:
            profile["label"] = "普通浏览型"
        cluster_profiles.append(profile)

        print(f"    簇{c}【{profile['label']}】 {profile['user_count']}人({profile['pct']}%)"
              f"  浏览={profile['avg_browse']} 收藏={profile['avg_collect']}"
              f"  加购={profile['avg_cart']} 购买={profile['avg_buy']}"
              f"  购买率={profile['avg_buy_rate']:.3f}")

    # ── 可视化 ──
    fig, axes = plt.subplots(2, 2, figsize=(16, 13))

    # (1) Elbow + Silhouette 双图
    ax1a = axes[0, 0]
    ax1b = ax1a.twinx()
    k_list = list(K_range)
    ax1a.plot(k_list, inertias, "o-", color="#3498DB", linewidth=2, markersize=6, label="Inertia (SSE)")
    ax1b.plot(k_list, silhouettes, "s--", color="#E74C3C", linewidth=2, markersize=6, label="Silhouette")
    ax1a.axvline(x=best_k, color="#27AE60", linestyle=":", linewidth=2, alpha=0.8)
    ax1a.set_xlabel("簇数 K", fontsize=11)
    ax1a.set_ylabel("Inertia (SSE)", fontsize=11, color="#3498DB")
    ax1b.set_ylabel("轮廓系数", fontsize=11, color="#E74C3C")
    ax1a.set_title(f"Elbow + Silhouette 选K（最优K={best_k}，轮廓={best_sil:.4f}）",
                    fontsize=12, fontweight="bold")
    lines1, labels1 = ax1a.get_legend_handles_labels()
    lines2, labels2 = ax1b.get_legend_handles_labels()
    ax1a.legend(lines1 + lines2, labels1 + labels2, fontsize=9, loc="center right")
    ax1a.spines["top"].set_visible(False)

    # (2) 聚类散点图（PCA降维到2D）
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2, random_state=42)
    X_2d = pca.fit_transform(X_scaled)
    colors_map = ["#E74C3C", "#3498DB", "#27AE60", "#F39C12", "#9B59B6",
                  "#1ABC9C", "#E67E22", "#2C3E50"]
    for c in range(best_k):
        mask = user_feat["cluster"] == c
        label = cluster_profiles[c]["label"]
        axes[0, 1].scatter(X_2d[mask, 0], X_2d[mask, 1], c=colors_map[c % len(colors_map)],
                           alpha=0.6, s=25, label=f"簇{c} {label}")
    axes[0, 1].set_title("K-Means 聚类可视化（PCA降维）", fontsize=12, fontweight="bold")
    axes[0, 1].set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)", fontsize=10)
    axes[0, 1].set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)", fontsize=10)
    axes[0, 1].legend(fontsize=8, loc="best")
    axes[0, 1].spines["top"].set_visible(False)
    axes[0, 1].spines["right"].set_visible(False)

    # (3) 聚类雷达图（各簇行为特征对比）
    radar_features = ["avg_browse", "avg_collect", "avg_cart", "avg_buy", "avg_cat_diversity"]
    radar_labels   = ["浏览", "收藏", "加购", "购买", "品类多样性"]
    n_feat = len(radar_features)
    angles = np.linspace(0, 2 * np.pi, n_feat, endpoint=False).tolist()
    angles += angles[:1]

    ax_radar = axes[1, 0]
    ax_radar = fig.add_subplot(2, 2, 3, polar=True)
    for c in range(best_k):
        values = [cluster_profiles[c][f] for f in radar_features]
        # 归一化到0-1
        max_vals = [max(p[f] for p in cluster_profiles) or 1 for f in radar_features]
        values_norm = [v / m for v, m in zip(values, max_vals)]
        values_norm += values_norm[:1]
        ax_radar.plot(angles, values_norm, "o-", linewidth=2,
                      color=colors_map[c % len(colors_map)],
                      label=f"簇{c} {cluster_profiles[c]['label']}")
        ax_radar.fill(angles, values_norm, alpha=0.1, color=colors_map[c % len(colors_map)])
    ax_radar.set_xticks(angles[:-1])
    ax_radar.set_xticklabels(radar_labels, fontsize=9)
    ax_radar.set_title("聚类行为雷达图\n（归一化特征对比）", fontsize=12, fontweight="bold", pad=20)
    ax_radar.legend(fontsize=7, loc="upper right", bbox_to_anchor=(1.35, 1.1))

    # (4) 聚类分布饼图
    sizes  = [p["user_count"] for p in cluster_profiles]
    labels_pie = [f"簇{p['cluster_id']}\n{p['label']}\n{p['pct']}%" for p in cluster_profiles]
    explode = [0.05] * best_k
    axes[1, 1].pie(sizes, labels=labels_pie, explode=explode, autopct="%1.1f%%",
                   colors=[colors_map[i % len(colors_map)] for i in range(best_k)],
                   textprops={"fontsize": 9}, startangle=90, pctdistance=0.75)
    axes[1, 1].set_title("用户聚类分布", fontsize=12, fontweight="bold")

    plt.tight_layout()
    save_fig("24_kmeans_user_clustering.png")

    # 输出JSON
    result = {
        "best_k": best_k,
        "silhouette_score": round(float(best_sil), 4),
        "cluster_profiles": cluster_profiles,
        "feature_columns": feature_cols,
    }
    with open(os.path.join(OUTPUT_DIR, "kmeans_clusters.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("  [OK] 聚类结果已保存：kmeans_clusters.json")
    return result, user_feat


# ============================================================
# 算法B：SVD 矩阵分解推荐（截断SVD / FunkSVD 思路）
# 来源：Netflix Prize 2006 — Simon Funk
# ============================================================
def algo_svd_recommendation(df, top_n=5):
    """
    用户-品类交互矩阵 → TruncatedSVD 分解为隐因子 →
    重构评分矩阵 → 为每个用户推荐未交互的品类
    """
    print("\n" + "=" * 60)
    print("算法B：SVD 矩阵分解推荐（截断SVD / FunkSVD 思路）")
    print("  来源：Netflix Prize 2006 — Simon Funk 隐因子模型")

    # ── 构建用户-品类交互矩阵 ──
    df_valid = df.dropna(subset=["user_id", "category_id", "behavior"]).copy()
    df_valid["weight"] = df_valid["behavior"].map(BEHAVIOR_WEIGHTS).fillna(1)

    interaction = (df_valid.groupby(["user_id", "category_id"])["weight"]
                   .sum().reset_index())
    interaction.columns = ["user_id", "category_id", "score"]

    # 创建ID映射
    user_ids = sorted(interaction["user_id"].unique())
    cat_ids  = sorted(interaction["category_id"].unique())
    user2idx = {uid: i for i, uid in enumerate(user_ids)}
    cat2idx  = {cid: i for i, cid in enumerate(cat_ids)}
    idx2cat  = {i: cid for cid, i in cat2idx.items()}

    n_users = len(user_ids)
    n_cats  = len(cat_ids)
    print(f"  交互矩阵规模：{n_users} 用户 × {n_cats} 品类")

    # 构建稀疏矩阵
    rows = interaction["user_id"].map(user2idx).values
    cols = interaction["category_id"].map(cat2idx).values
    vals = interaction["score"].values
    R = csr_matrix((vals, (rows, cols)), shape=(n_users, n_cats))
    R_dense = R.toarray().astype(float)

    # 稀疏度
    sparsity = 1 - np.count_nonzero(R_dense) / (n_users * n_cats)
    print(f"  矩阵稀疏度：{sparsity*100:.2f}%")

    # ── SVD 分解 ──
    n_factors = min(20, n_cats - 1, n_users - 1)
    svd = TruncatedSVD(n_components=n_factors, random_state=42)
    U = svd.fit_transform(R)       # n_users × n_factors
    Sigma = np.diag(svd.singular_values_)  # n_factors × n_factors
    Vt = svd.components_                    # n_factors × n_cats
    explained = svd.explained_variance_ratio_.sum()
    print(f"  SVD隐因子数：{n_factors}，解释方差比例：{explained*100:.2f}%")

    # 重构评分矩阵
    R_pred = U @ Vt

    # ── 为每个用户推荐 ──
    recommendations = []
    for uid in user_ids[:100]:   # 取前100个用户做示例
        u_idx = user2idx[uid]
        already = set(np.where(R_dense[u_idx] > 0)[0])
        scores = R_pred[u_idx].copy()
        for idx in already:
            scores[idx] = -np.inf
        top_idx = np.argsort(scores)[::-1][:top_n]
        rec_cats = [int(idx2cat[i]) for i in top_idx if scores[i] > -np.inf]
        rec_scores = [round(float(scores[i]), 4) for i in top_idx if scores[i] > -np.inf]
        recommendations.append({
            "user_id": int(uid),
            "recommended_categories": rec_cats,
            "predicted_scores": rec_scores,
        })

    # 示例输出
    print(f"\n  SVD推荐示例（TOP {top_n} 品类）：")
    for r in recommendations[:5]:
        cats_str = ", ".join([f"品类{c}({s:.2f})" for c, s in
                             zip(r["recommended_categories"], r["predicted_scores"])])
        print(f"    用户{r['user_id']}: {cats_str}")

    # ── 评估：对已有交互做留一法评估 ──
    hits = 0
    total = 0
    for uid in user_ids[:200]:
        u_idx = user2idx[uid]
        interacted = list(np.where(R_dense[u_idx] > 0)[0])
        if len(interacted) < 2:
            continue
        # 留最后一个作为测试
        test_item = interacted[-1]
        train_items = set(interacted[:-1])
        scores = R_pred[u_idx].copy()
        for idx in train_items:
            scores[idx] = -np.inf
        top_idx = np.argsort(scores)[::-1][:top_n]
        if test_item in top_idx:
            hits += 1
        total += 1

    hit_rate = hits / max(total, 1)
    print(f"\n  留一法评估（前200用户，Top-{top_n}）：")
    print(f"    命中率 = {hits}/{total} = {hit_rate*100:.1f}%")

    # ── 可视化 ──
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # (1) 奇异值分布
    axes[0].bar(range(n_factors), svd.singular_values_, color="#3498DB", alpha=0.8)
    axes[0].set_title(f"SVD 奇异值分布（{n_factors}个隐因子）\n"
                       f"解释方差={explained*100:.1f}%",
                       fontsize=12, fontweight="bold")
    axes[0].set_xlabel("隐因子序号", fontsize=10)
    axes[0].set_ylabel("奇异值", fontsize=10)
    axes[0].spines["top"].set_visible(False)
    axes[0].spines["right"].set_visible(False)

    # (2) 累积解释方差
    cumvar = np.cumsum(svd.explained_variance_ratio_)
    axes[1].plot(range(1, n_factors + 1), cumvar, "o-", color="#E74C3C", linewidth=2)
    axes[1].axhline(y=0.8, color="#95A5A6", linestyle="--", label="80%阈值")
    axes[1].axhline(y=0.9, color="#BDC3C7", linestyle="--", label="90%阈值")
    axes[1].fill_between(range(1, n_factors + 1), cumvar, alpha=0.15, color="#E74C3C")
    axes[1].set_title("累积解释方差比\n（选择的隐因子数是否足够）",
                       fontsize=12, fontweight="bold")
    axes[1].set_xlabel("隐因子数", fontsize=10)
    axes[1].set_ylabel("累积解释方差比", fontsize=10)
    axes[1].legend(fontsize=9)
    axes[1].spines["top"].set_visible(False)
    axes[1].spines["right"].set_visible(False)

    # (3) 用户-品类隐空间可视化（取前2个因子）
    if n_factors >= 2:
        # 用户点
        axes[2].scatter(U[:min(200, n_users), 0], U[:min(200, n_users), 1],
                        c="#5DADE2", alpha=0.4, s=15, label="用户")
        # 品类点
        cat_embeddings = Vt[:2, :].T    # n_cats × 2
        axes[2].scatter(cat_embeddings[:, 0], cat_embeddings[:, 1],
                        c="#E74C3C", alpha=0.7, s=40, marker="^", label="品类")
        # 标注部分品类
        for i in range(min(10, n_cats)):
            axes[2].annotate(f"{idx2cat[i]}", (cat_embeddings[i, 0], cat_embeddings[i, 1]),
                             fontsize=7, alpha=0.7)
    axes[2].set_title("隐因子空间可视化（前2维）\n（距离近=偏好相似）",
                       fontsize=12, fontweight="bold")
    axes[2].set_xlabel("隐因子1", fontsize=10)
    axes[2].set_ylabel("隐因子2", fontsize=10)
    axes[2].legend(fontsize=9)
    axes[2].spines["top"].set_visible(False)
    axes[2].spines["right"].set_visible(False)

    plt.tight_layout()
    save_fig("25_svd_matrix_factorization.png")

    result = {
        "n_users": n_users,
        "n_categories": n_cats,
        "n_factors": n_factors,
        "explained_variance": round(float(explained), 4),
        "sparsity": round(float(sparsity), 4),
        "hit_rate_top5": round(float(hit_rate), 4),
        "sample_recommendations": recommendations[:10],
    }
    with open(os.path.join(OUTPUT_DIR, "svd_recommendations.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("  [OK] SVD推荐结果已保存：svd_recommendations.json")
    return result


# ============================================================
# 主函数
# ============================================================
def main(sample_rows=30000):
    print("妆策AI — 聚类与矩阵分解模块启动（阶段7）")
    print("=" * 60)

    df = load_behavior(sample_rows=sample_rows)

    results = {}
    kmeans_result, user_feat = algo_kmeans_clustering(df)
    results["kmeans"] = kmeans_result
    results["svd"]    = algo_svd_recommendation(df)

    print("\n" + "=" * 60)
    print("P0算法全部完成！新增2张图表：")
    charts = [
        "24_kmeans_user_clustering.png    K-Means聚类（Elbow+Silhouette+PCA+雷达图）",
        "25_svd_matrix_factorization.png  SVD矩阵分解推荐（奇异值+隐空间可视化）",
    ]
    for c in charts:
        print(f"   {c}")

    print("\n新增输出文件：")
    files = [
        "kmeans_clusters.json          → 用户聚类画像（补充RFM分群）",
        "svd_recommendations.json     → SVD隐因子推荐（补充ItemCF）",
    ]
    for f in files:
        print(f"   {f}")

    best_k  = results["kmeans"]["best_k"]
    sil     = results["kmeans"]["silhouette_score"]
    n_f     = results["svd"]["n_factors"]
    hit     = results["svd"]["hit_rate_top5"]

    print("\n核心洞察：")
    print(f"  A. K-Means最优K={best_k}（轮廓系数={sil:.4f}），自动识别用户群体画像")
    print(f"  B. SVD {n_f}维隐因子分解，留一法命中率={hit*100:.1f}%，捕捉隐含品类偏好")

    return results


if __name__ == "__main__":
    main(sample_rows=30000)
