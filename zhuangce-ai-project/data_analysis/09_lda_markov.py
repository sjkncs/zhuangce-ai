#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
妆策AI - 主题模型与序列预测模块
阶段9：P2优先级算法

数据来源：产品经理表格（产品话术）/ 用户行为数据集【脱敏】

两大算法：
  A. LDA 主题模型（Latent Dirichlet Allocation）
     - 来源：Blei, Ng & Jordan 2003 — JMLR 顶刊
     - 功能：对产品话术文本做主题聚类，发现隐含卖点主题簇
             输出：每个主题的关键词分布 + 文档-主题分配
  B. Markov Chain 行为序列预测
     - 来源：Markov 1906 / 隐马尔可夫模型(HMM) Rabiner 1989
     - 功能：一阶/二阶马尔可夫链建模用户行为转移，预测下一步行为概率
             与Dijkstra互补：Dijkstra找全局最优路径，Markov做实时下一步预测
"""

import os
import re
import json
import math
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
PATH_PRODUCT  = r"E:/meiz/数据集/产品经理表格/产品话术.xlsx"


def save_fig(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, bbox_inches="tight", dpi=120)
    plt.close()
    print(f"  [OK] 图表已保存：{filename}")


# ============================================================
# 算法A：LDA 主题模型
# 来源：Blei, Ng & Jordan, JMLR 2003
# 轻量实现：NMF (Non-negative Matrix Factorization) 替代变分推断
# ============================================================
def algo_lda_topics(n_topics=5, top_words=10):
    """
    LDA / NMF 主题模型流程：
    1. 加载产品话术文本 → jieba 分词
    2. 构建 TF-IDF 文档-词矩阵
    3. NMF 分解（等效于 PLSA/LDA 的点估计版本）
    4. 输出每个主题的关键词 + 文档-主题分配
    """
    print("\n" + "=" * 60)
    print("算法A：LDA 主题模型（NMF实现）")
    print("  来源：Blei, Ng & Jordan, JMLR 2003")
    print(f"  参数：主题数K={n_topics}，每主题展示{top_words}个关键词")

    # ── 加载文本数据 ──
    try:
        df = pd.read_excel(PATH_PRODUCT)
        texts = []
        for col in df.columns:
            # 列名本身可能含有效文本
            col_str = str(col).strip()
            if len(col_str) > 5 and re.search(r'[\u4e00-\u9fff]{3,}', col_str):
                texts.append(col_str)
            for val in df[col].dropna().astype(str):
                val = val.strip()
                if val.lower() == "nan" or len(val) < 5:
                    continue
                if re.search(r'[\u4e00-\u9fff]{2,}', val):
                    texts.append(val)
        print(f"  加载文本片段数：{len(texts)}")
    except FileNotFoundError:
        print("  [WARN] 产品话术文件未找到，使用模拟文本")
        texts = [
            "玻尿酸补水保湿精华液，深层锁水，持久滋润肌肤",
            "氨基酸温和洁面乳，清洁毛孔不紧绷，敏感肌适用",
            "烟酰胺美白淡斑精华，提亮肤色，改善暗沉",
            "视黄醇抗皱修护面霜，紧致弹力，淡化细纹",
            "水杨酸祛痘控油凝胶，疏通毛孔，调节水油平衡",
            "神经酰胺修护屏障乳液，修复敏感，强韧肌肤屏障",
            "VC衍生物抗氧化精华，对抗自由基，延缓肌肤老化",
            "角鲨烷滋养面部精华油，深层养护，改善干燥粗糙",
            "熊果苷亮肤精华水，均匀肤色，焕亮透白",
            "胶原蛋白紧致面膜，补充胶原，重塑饱满弹力",
        ] * 5

    if len(texts) < 3:
        print("  [WARN] 文本数据不足，跳过LDA")
        return {}

    # ── 分词 ──
    try:
        import jieba
        jieba.setLogLevel(20)
    except ImportError:
        jieba = None

    stopwords = {"的", "了", "和", "是", "在", "有", "不", "与", "中", "对", "也",
                 "可以", "能", "被", "让", "等", "及", "或", "但", "从", "到",
                 "这", "那", "它", "一个", "一种", "进行", "使用", "通过", "具有",
                 "产品", "NaN", "nan", "方法", "效果", "所以", "因此", "如果"}

    tokenized_docs = []
    for text in texts:
        text_clean = re.sub(r'[a-zA-Z0-9\s\-—.,;:!?。，；：！？、"\'【】（）()\[\]\d]', ' ', text)
        if jieba:
            words = list(jieba.cut(text_clean))
        else:
            words = list(text_clean)
        words = [w.strip() for w in words
                 if len(w.strip()) >= 2 and w.strip() not in stopwords
                 and re.search(r'[\u4e00-\u9fff]', w.strip())]
        if len(words) >= 2:
            tokenized_docs.append(words)

    print(f"  有效文档数：{len(tokenized_docs)}")

    if len(tokenized_docs) < 3:
        print("  [WARN] 有效文档不足，跳过LDA")
        return {}

    # ── TF-IDF 矩阵 ──
    vocab = {}
    for doc in tokenized_docs:
        for w in set(doc):
            if w not in vocab:
                vocab[w] = len(vocab)

    n_docs = len(tokenized_docs)
    n_vocab = len(vocab)
    print(f"  词汇量：{n_vocab}")

    # 文档频次
    df_count = Counter()
    for doc in tokenized_docs:
        for w in set(doc):
            df_count[w] += 1

    # TF-IDF矩阵
    tfidf_matrix = np.zeros((n_docs, n_vocab))
    for i, doc in enumerate(tokenized_docs):
        tf = Counter(doc)
        total = len(doc) or 1
        for w, cnt in tf.items():
            j = vocab[w]
            tf_val = cnt / total
            idf_val = math.log((n_docs + 1) / (df_count[w] + 1)) + 1
            tfidf_matrix[i, j] = tf_val * idf_val

    # ── NMF 分解 ──
    from sklearn.decomposition import NMF

    actual_topics = min(n_topics, n_docs - 1, n_vocab - 1)
    if actual_topics < 2:
        actual_topics = 2
    nmf = NMF(n_components=actual_topics, random_state=42, max_iter=500)
    W = nmf.fit_transform(tfidf_matrix)  # n_docs × n_topics
    H = nmf.components_                   # n_topics × n_vocab

    recon_error = nmf.reconstruction_err_
    print(f"  NMF重构误差：{recon_error:.4f}")

    idx2word = {i: w for w, i in vocab.items()}

    topic_results = []
    print(f"\n  {actual_topics} 个主题及关键词：")
    for t in range(actual_topics):
        top_idx = np.argsort(H[t])[::-1][:top_words]
        keywords = [(idx2word[i], round(float(H[t, i]), 4)) for i in top_idx if H[t, i] > 0]
        # 自动命名主题
        kw_names = [w for w, _ in keywords[:3]]
        topic_name = "/".join(kw_names) if kw_names else f"主题{t}"
        topic_results.append({
            "topic_id": t,
            "topic_name": topic_name,
            "keywords": keywords,
            "doc_count": int((W[:, t] > W.mean()).sum()),
        })
        kw_str = " | ".join([f"{w}({s:.3f})" for w, s in keywords[:6]])
        print(f"    主题{t}【{topic_name}】: {kw_str}")

    # 文档-主题分配
    doc_topics = np.argmax(W, axis=1)
    topic_dist = Counter(doc_topics)
    print(f"\n  文档-主题分配分布：")
    for t in range(actual_topics):
        cnt = topic_dist.get(t, 0)
        print(f"    主题{t}【{topic_results[t]['topic_name']}】: {cnt}篇 ({cnt/n_docs*100:.1f}%)")

    # ── 可视化 ──
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # (1) 主题-关键词权重热力图
    n_show = min(8, top_words)
    all_top_words = set()
    for tr in topic_results:
        for w, _ in tr["keywords"][:n_show]:
            all_top_words.add(w)
    all_top_words = sorted(all_top_words)[:30]  # 最多展示30个
    word2show_idx = {w: i for i, w in enumerate(all_top_words)}

    heat_data = np.zeros((actual_topics, len(all_top_words)))
    for t in range(actual_topics):
        for w, s in topic_results[t]["keywords"]:
            if w in word2show_idx:
                heat_data[t, word2show_idx[w]] = s

    try:
        import seaborn as sns
        sns.heatmap(heat_data, xticklabels=all_top_words,
                    yticklabels=[f"主题{t}" for t in range(actual_topics)],
                    cmap="YlOrRd", ax=axes[0], linewidths=0.3, linecolor="white",
                    cbar_kws={"label": "NMF权重"}, annot_kws={"size": 7})
        axes[0].tick_params(axis="x", rotation=45, labelsize=8)
    except ImportError:
        im = axes[0].imshow(heat_data, cmap="YlOrRd", aspect="auto")
        plt.colorbar(im, ax=axes[0])
        axes[0].set_xticks(range(len(all_top_words)))
        axes[0].set_xticklabels(all_top_words, rotation=45, fontsize=7)
        axes[0].set_yticks(range(actual_topics))
        axes[0].set_yticklabels([f"主题{t}" for t in range(actual_topics)])

    axes[0].set_title("LDA/NMF 主题-关键词权重热力图\n"
                       "（颜色深=该词对该主题贡献大）",
                       fontsize=12, fontweight="bold")

    # (2) 主题分布饼图
    sizes = [topic_dist.get(t, 0) for t in range(actual_topics)]
    labels_pie = [f"主题{t}\n{topic_results[t]['topic_name']}" for t in range(actual_topics)]
    colors_pie = ["#E74C3C", "#3498DB", "#27AE60", "#F39C12", "#9B59B6",
                  "#1ABC9C", "#E67E22", "#2C3E50"][:actual_topics]
    axes[1].pie(sizes, labels=labels_pie, autopct="%1.1f%%",
                colors=colors_pie, textprops={"fontsize": 9},
                startangle=90, pctdistance=0.78,
                explode=[0.03] * actual_topics)
    axes[1].set_title("文档-主题分配分布\n（每篇产品话术归属的主题）",
                       fontsize=12, fontweight="bold")

    plt.tight_layout()
    save_fig("29_lda_topic_model.png")

    result = {
        "n_topics": actual_topics,
        "n_documents": n_docs,
        "n_vocabulary": n_vocab,
        "reconstruction_error": round(float(recon_error), 4),
        "topics": topic_results,
    }
    with open(os.path.join(OUTPUT_DIR, "lda_topics.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("  [OK] LDA主题模型结果已保存：lda_topics.json")
    return result


# ============================================================
# 算法B：Markov Chain 行为序列预测
# 来源：Markov 1906 / Rabiner 1989 (HMM)
# ============================================================
def algo_markov_chain(sample_rows=20000):
    """
    一阶 + 二阶马尔可夫链：
    一阶：P(next | current)  → 转移矩阵
    二阶：P(next | prev, current) → 高阶转移张量
    应用：实时预测用户下一步行为，触发精准营销动作
    """
    print("\n" + "=" * 60)
    print("算法B：Markov Chain 行为序列预测（一阶+二阶）")
    print("  来源：Markov 1906 / Rabiner 1989 (HMM)")

    # ── 加载数据 ──
    try:
        df = pd.read_excel(PATH_BEHAVIOR, nrows=sample_rows)
        rename = {}
        for c in df.columns:
            cl = c.strip()
            if "唯一" in cl:       rename[c] = "user_id"
            elif "行为" in cl:     rename[c] = "behavior"
            elif cl == "时间":     rename[c] = "timestamp"
            elif "整点" in cl:     rename[c] = "hour"
        df = df.rename(columns=rename)
        if "user_id" in df.columns:
            df["user_id"] = df["user_id"].astype(str).str.extract(r"(\d+)")[0]
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        print(f"  已加载 {len(df):,} 行行为记录")
    except FileNotFoundError:
        print("  [WARN] 行为数据未找到，使用模拟数据")
        np.random.seed(42)
        n = 5000
        df = pd.DataFrame({
            "user_id": np.random.randint(1000, 5000, n).astype(str),
            "behavior": np.random.choice(["浏览", "收藏", "加购物车", "购买"],
                                          n, p=[0.70, 0.12, 0.10, 0.08]),
            "timestamp": pd.date_range("2023-12-01", periods=n, freq="3min"),
        })

    states = ["浏览", "收藏", "加购物车", "购买"]
    state2idx = {s: i for i, s in enumerate(states)}
    n_states = len(states)

    # ── 一阶转移矩阵 ──
    df_sorted = df.sort_values(["user_id", "timestamp"]).copy()
    trans1 = np.zeros((n_states, n_states))

    for uid, group in df_sorted.groupby("user_id"):
        behaviors = [b for b in group["behavior"].tolist() if b in state2idx]
        for i in range(len(behaviors) - 1):
            src = state2idx[behaviors[i]]
            dst = state2idx[behaviors[i + 1]]
            trans1[src, dst] += 1

    # 归一化为概率
    row_sums = trans1.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    trans1_prob = trans1 / row_sums

    print(f"\n  一阶转移概率矩阵：")
    header = "           " + "  ".join([f"{s:>6}" for s in states])
    print(f"  {header}")
    for i, s in enumerate(states):
        row = "  ".join([f"{trans1_prob[i, j]:.4f}" for j in range(n_states)])
        print(f"    {s:<6} {row}")

    # ── 二阶转移矩阵 ──
    trans2 = defaultdict(lambda: np.zeros(n_states))
    for uid, group in df_sorted.groupby("user_id"):
        behaviors = [b for b in group["behavior"].tolist() if b in state2idx]
        for i in range(len(behaviors) - 2):
            key = (behaviors[i], behaviors[i + 1])
            dst = state2idx[behaviors[i + 2]]
            trans2[key][dst] += 1

    # 归一化
    trans2_prob = {}
    for key, counts in trans2.items():
        total = counts.sum()
        if total > 0:
            trans2_prob[key] = counts / total

    print(f"\n  二阶转移概率（条件概率 P(next | prev, current)）：")
    for (prev, cur), probs in sorted(trans2_prob.items()):
        most_likely = states[np.argmax(probs)]
        print(f"    {prev}→{cur} → 最可能：{most_likely}({probs[np.argmax(probs)]:.3f})")

    # ── 稳态分布（一阶链） ──
    # 幂迭代法
    pi = np.ones(n_states) / n_states
    for _ in range(1000):
        pi_new = pi @ trans1_prob
        if np.abs(pi_new - pi).sum() < 1e-10:
            break
        pi = pi_new

    print(f"\n  马尔可夫链稳态分布（长期行为占比预测）：")
    for i, s in enumerate(states):
        bar = "#" * int(pi[i] * 100)
        print(f"    {s:<6} π={pi[i]:.4f}  {bar}")

    # ── 预测场景示例 ──
    scenarios = [
        ("浏览", "刚浏览商品的用户"),
        ("收藏", "刚收藏商品的用户"),
        ("加购物车", "刚加购的用户"),
    ]
    predictions = []
    print(f"\n  实时预测示例（一阶 Markov）：")
    for current, desc in scenarios:
        idx = state2idx[current]
        next_probs = trans1_prob[idx]
        sorted_next = sorted(zip(states, next_probs), key=lambda x: x[1], reverse=True)
        pred = {"current_state": current, "description": desc,
                "predictions": [{"next": s, "prob": round(float(p), 4)} for s, p in sorted_next]}
        predictions.append(pred)
        top = sorted_next[0]
        print(f"    {desc} → 最可能下一步：{top[0]}（{top[1]:.3f}）")
        # 营销建议
        if current == "浏览":
            if next_probs[state2idx["购买"]] < 0.02:
                print(f"      [TIP] 建议：浏览→购买概率仅{next_probs[state2idx['购买']]:.3f}，"
                       "需增强收藏/加购引导，缩短转化路径")
        elif current == "加购物车":
            buy_prob = next_probs[state2idx["购买"]]
            if buy_prob > 0.05:
                print(f"      [TIP] 建议：加购→购买概率{buy_prob:.3f}，"
                       "发送限时优惠券可进一步提升转化")

    # ── 可视化 ──
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))

    # (1) 一阶转移概率热力图
    try:
        import seaborn as sns
        sns.heatmap(trans1_prob, annot=True, fmt=".3f", cmap="Blues",
                    xticklabels=states, yticklabels=states,
                    ax=axes[0], linewidths=0.5, linecolor="white",
                    cbar_kws={"label": "转移概率"},
                    annot_kws={"size": 11, "fontweight": "bold"})
    except ImportError:
        im = axes[0].imshow(trans1_prob, cmap="Blues", aspect="auto")
        plt.colorbar(im, ax=axes[0])
        axes[0].set_xticks(range(n_states))
        axes[0].set_xticklabels(states)
        axes[0].set_yticks(range(n_states))
        axes[0].set_yticklabels(states)
        for i in range(n_states):
            for j in range(n_states):
                axes[0].text(j, i, f"{trans1_prob[i,j]:.3f}", ha="center", va="center")

    axes[0].set_title("一阶 Markov 转移概率矩阵\n（行=当前行为 → 列=下一步行为）",
                       fontsize=12, fontweight="bold")
    axes[0].set_xlabel("下一步行为", fontsize=10)
    axes[0].set_ylabel("当前行为", fontsize=10)

    # (2) 稳态分布
    colors_bar = ["#3498DB", "#9B59B6", "#E8834A", "#27AE60"]
    bars = axes[1].bar(states, pi, color=colors_bar, alpha=0.85, width=0.55)
    for bar, v in zip(bars, pi):
        axes[1].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                     f"{v:.4f}", ha="center", va="bottom", fontsize=11, fontweight="bold")
    axes[1].set_title("Markov链稳态分布 π\n（系统长期运行后各行为的均衡占比）",
                       fontsize=12, fontweight="bold")
    axes[1].set_ylabel("稳态概率", fontsize=10)
    axes[1].spines["top"].set_visible(False)
    axes[1].spines["right"].set_visible(False)

    # (3) 行为转移Sankey风格（用堆叠条形图模拟）
    for i, src in enumerate(states):
        bottom = 0
        for j, dst in enumerate(states):
            p = trans1_prob[i, j]
            if p > 0.005:
                axes[2].barh(i, p, left=bottom, height=0.6,
                             color=colors_bar[j], alpha=0.8)
                if p > 0.05:
                    axes[2].text(bottom + p / 2, i, f"{dst}\n{p:.2f}",
                                 ha="center", va="center", fontsize=7, color="white",
                                 fontweight="bold")
                bottom += p

    axes[2].set_yticks(range(n_states))
    axes[2].set_yticklabels(states, fontsize=10)
    axes[2].set_xlabel("转移概率", fontsize=10)
    axes[2].set_title("行为转移概率堆叠图\n（每行=从该行为出发的转移分布）",
                       fontsize=12, fontweight="bold")
    axes[2].spines["top"].set_visible(False)
    axes[2].spines["right"].set_visible(False)

    # 添加图例
    import matplotlib.patches as mpatches
    patches = [mpatches.Patch(color=colors_bar[i], label=states[i]) for i in range(n_states)]
    axes[2].legend(handles=patches, fontsize=8, loc="lower right")

    plt.tight_layout()
    save_fig("30_markov_chain_prediction.png")

    # ── 输出 ──
    result = {
        "transition_matrix_order1": trans1_prob.tolist(),
        "stationary_distribution": {s: round(float(pi[i]), 4) for i, s in enumerate(states)},
        "predictions": predictions,
        "n_order2_transitions": len(trans2_prob),
        "states": states,
    }
    with open(os.path.join(OUTPUT_DIR, "markov_chain.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("  [OK] Markov Chain结果已保存：markov_chain.json")
    return result


# ============================================================
# 主函数
# ============================================================
def main():
    print("妆策AI — 主题模型与序列预测模块启动（阶段9）")
    print("=" * 60)

    results = {}
    results["lda"]    = algo_lda_topics(n_topics=5, top_words=10)
    results["markov"] = algo_markov_chain(sample_rows=20000)

    print("\n" + "=" * 60)
    print("P2算法全部完成！新增2张图表：")
    charts = [
        "29_lda_topic_model.png          LDA主题-关键词热力图+文档分配饼图",
        "30_markov_chain_prediction.png   Markov链转移矩阵+稳态分布+转移堆叠图",
    ]
    for c in charts:
        print(f"   {c}")

    print("\n新增输出文件：")
    files = [
        "lda_topics.json              → 产品话术主题聚类（内容策略分组依据）",
        "markov_chain.json            → 行为转移概率+实时预测（精准营销触发）",
    ]
    for f in files:
        print(f"   {f}")

    n_topics = results["lda"].get("n_topics", 0)
    steady   = results["markov"].get("stationary_distribution", {})
    browse_p = steady.get("浏览", 0)

    print("\n核心洞察：")
    print(f"  A. LDA发现{n_topics}个卖点主题簇，可指导内容分组策略和自动化标签分配")
    print(f"  B. Markov稳态分布：浏览占比={browse_p:.3f}，揭示系统长期均衡行为结构")
    print(f"     营销建议：在高转移概率节点（加购→购买）部署限时优惠券触发机制")

    return results


if __name__ == "__main__":
    main()
