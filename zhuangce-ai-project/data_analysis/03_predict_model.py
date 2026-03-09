#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
妆策AI - 爆款预测模型
阶段3：标签评分算法 + 多因子加权预测引擎
核心逻辑：基于标签体系匹配度 + 价格带竞争力 + 场景适配性计算传播潜力评分
"""

import json
import os
import math
import numpy as np
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# 一、标签权重配置（基于EDA分析结论）
# ============================================================
EFFICACY_WEIGHTS = {
    "修护": 0.95,
    "柔顺": 0.90,
    "留香": 0.85,
    "控油": 0.75,
    "蓬松": 0.70,
    "去屑": 0.65,
    "滋养": 0.72,
    "温和": 0.68,
}

PERSONA_WEIGHTS = {
    "学生党": 0.92,
    "价格敏感型": 0.85,
    "通勤党": 0.70,
    "油皮头皮": 0.68,
    "染烫受损": 0.78,
    "年轻女性用户": 0.75,
}

SCENE_WEIGHTS = {
    "宿舍日常": 0.95,
    "开学季": 0.90,
    "日常复购": 0.80,
    "换季护理": 0.72,
    "节日送礼": 0.65,
    "通勤清洁": 0.68,
}

PRICE_BAND_SCORES = {
    "0-50元": 0.60,
    "50-100元": 0.75,
    "100-150元": 0.90,
    "150-200元": 0.82,
    "200-300元": 0.70,
    "300-500元": 0.55,
    "500元+": 0.40,
}

PLATFORM_MULTIPLIERS = {
    "小红书": 1.15,
    "抖音": 1.05,
    "微博": 0.90,
    "微信": 0.85,
    "B站": 0.88,
}

SEASON_BOOST = {
    1: 0.85, 2: 0.90, 3: 0.88,
    4: 0.82, 5: 0.80, 6: 0.78,
    7: 0.75, 8: 1.10, 9: 1.15,
    10: 0.85, 11: 0.95, 12: 0.88,
}


# ============================================================
# 二、价格带映射
# ============================================================
def price_to_band(price_str):
    price_str = str(price_str).replace("元", "").strip()
    try:
        if "-" in price_str:
            low, high = [float(x.strip()) for x in price_str.split("-")]
            mid = (low + high) / 2
        else:
            mid = float(price_str)
    except ValueError:
        return "100-150元"

    if mid < 50:
        return "0-50元"
    elif mid < 100:
        return "50-100元"
    elif mid < 150:
        return "100-150元"
    elif mid < 200:
        return "150-200元"
    elif mid < 300:
        return "200-300元"
    elif mid < 500:
        return "300-500元"
    else:
        return "500元+"


# ============================================================
# 三、核心预测算法
# ============================================================
def compute_potential_score(
    selling_points,
    target_user,
    price_range,
    platform="小红书",
    month=None,
):
    """
    传播潜力评分算法（多因子加权）

    权重分配：
      - 卖点标签匹配度  40%
      - 人群标签匹配度  25%
      - 场景适配性      20%
      - 价格带竞争力    15%

    最终得分乘以：平台系数 × 季节系数
    """
    if month is None:
        month = datetime.now().month

    # 因子1：卖点标签匹配度（40%）
    efficacy_score = 0.0
    matched_efficacy = []
    for point in selling_points:
        w = EFFICACY_WEIGHTS.get(point, 0.5)
        efficacy_score += w
        if w > 0.4:
            matched_efficacy.append(point)
    efficacy_score = min(1.0, efficacy_score / max(len(selling_points), 1))

    # 因子2：人群标签匹配度（25%）
    persona_score = 0.0
    matched_personas = []
    if isinstance(target_user, str):
        target_users = [u.strip() for u in target_user.replace("，", ",").split(",")]
    else:
        target_users = target_user
    for user in target_users:
        w = PERSONA_WEIGHTS.get(user, 0.55)
        persona_score += w
        matched_personas.append(user)
    persona_score = min(1.0, persona_score / max(len(target_users), 1))

    # 因子3：场景适配性（20%）- 基于卖点×人群推导最匹配场景
    inferred_scenes = _infer_scenes(matched_efficacy, matched_personas)
    scene_score = 0.0
    for scene in inferred_scenes:
        scene_score += SCENE_WEIGHTS.get(scene, 0.6)
    scene_score = min(1.0, scene_score / max(len(inferred_scenes), 1)) if inferred_scenes else 0.65

    # 因子4：价格带竞争力（15%）
    band = price_to_band(price_range)
    price_score = PRICE_BAND_SCORES.get(band, 0.70)

    # 综合加权
    raw_score = (
        efficacy_score * 0.40 +
        persona_score * 0.25 +
        scene_score * 0.20 +
        price_score * 0.15
    )

    # 平台系数
    platform_mult = PLATFORM_MULTIPLIERS.get(platform, 1.0)

    # 季节系数
    season_mult = SEASON_BOOST.get(month, 0.85)

    # 最终得分（1-10）
    final_score = raw_score * platform_mult * season_mult * 10
    final_score = round(min(10.0, max(1.0, final_score)), 1)

    return {
        "final_score": final_score,
        "factors": {
            "efficacy_score": round(efficacy_score * 10, 2),
            "persona_score": round(persona_score * 10, 2),
            "scene_score": round(scene_score * 10, 2),
            "price_score": round(price_score * 10, 2),
        },
        "matched_efficacy": matched_efficacy,
        "matched_personas": matched_personas,
        "inferred_scenes": inferred_scenes,
        "price_band": band,
        "platform_multiplier": platform_mult,
        "season_multiplier": season_mult,
    }


def _infer_scenes(efficacy_tags, persona_tags):
    scenes = set()
    if "学生党" in persona_tags or "价格敏感型" in persona_tags:
        scenes.add("宿舍日常")
        scenes.add("开学季")
    if "通勤党" in persona_tags:
        scenes.add("通勤清洁")
    if "修护" in efficacy_tags or "柔顺" in efficacy_tags:
        scenes.add("日常复购")
    if "留香" in efficacy_tags:
        scenes.add("节日送礼")
    if not scenes:
        scenes.add("日常复购")
    return list(scenes)


# ============================================================
# 四、人群画像生成
# ============================================================
def generate_persona_profile(target_user, selling_points, price_range):
    personas = []
    if isinstance(target_user, str):
        target_users = [u.strip() for u in target_user.replace("，", ",").split(",")]
    else:
        target_users = target_user

    band = price_to_band(price_range)
    age_map = {
        "学生党": "18-22岁",
        "价格敏感型": "18-28岁",
        "通勤党": "24-32岁",
        "染烫受损": "22-35岁",
        "油皮头皮": "20-30岁",
    }
    region_map = {
        "学生党": "一二线城市高校集中区",
        "价格敏感型": "全国普遍分布",
        "通勤党": "一二线城市CBD",
    }
    interest_map = {
        "学生党": ["美妆穿搭", "宿舍好物", "低价平替"],
        "价格敏感型": ["薅羊毛", "好物推荐", "测评"],
        "通勤党": ["职场穿搭", "效率好物", "精致生活"],
    }

    for user in target_users:
        profile = {
            "persona_name": user,
            "age_range": age_map.get(user, "20-30岁"),
            "region": region_map.get(user, "全国分布"),
            "interests": interest_map.get(user, ["美妆护肤", "生活好物"]),
            "price_sensitivity": "高" if band in ["0-50元", "50-100元", "100-150元"] else "中",
            "content_preference": "真实测评+日常分享" if "学生党" in user else "专业测评+功效对比",
        }
        personas.append(profile)
    return personas


# ============================================================
# 五、最佳推广时间推荐
# ============================================================
def recommend_best_time(selling_points, target_user, month=None):
    if month is None:
        month = datetime.now().month

    time_windows = []

    is_student = isinstance(target_user, str) and "学生党" in target_user
    if is_student:
        time_windows.append({
            "window": "开学季（8月20日 - 9月10日）",
            "reason": "学生党集中采购宿舍洗护用品，内容互动频率高",
            "confidence": "高",
            "boost": 1.15,
        })
        time_windows.append({
            "window": "寒假前后（1月-2月）",
            "reason": "新学期前囤货热潮，学生消费意愿回升",
            "confidence": "中",
            "boost": 0.90,
        })

    if "修护" in selling_points or "柔顺" in selling_points:
        time_windows.append({
            "window": "换季期（3月、9-10月）",
            "reason": "气候变化导致头发毛躁，修护洗护内容热度上升",
            "confidence": "高",
            "boost": 1.10,
        })

    if "留香" in selling_points:
        time_windows.append({
            "window": "情人节前后（2月7日 - 14日）",
            "reason": "玫瑰香氛类产品送礼场景需求高，内容传播量增加",
            "confidence": "中",
            "boost": 1.05,
        })

    time_windows.append({
        "window": "618大促期间（6月1日 - 18日）",
        "reason": "电商大促带动洗护品类整体搜索量，内容种草需求增加",
        "confidence": "中",
        "boost": 1.08,
    })

    time_windows.sort(key=lambda x: x["boost"], reverse=True)
    return time_windows[:3]


# ============================================================
# 六、风险提示生成
# ============================================================
def generate_risk_alerts(selling_points, target_user, price_range, score):
    alerts = []

    band = price_to_band(price_range)
    if "学生党" in str(target_user) and band not in ["0-50元", "50-100元", "100-150元"]:
        alerts.append("价格带偏高：目标人群为学生党，建议价格控制在150元以内以降低购买决策门槛。")

    if score < 6.0:
        alerts.append('传播潜力偏低：当前卖点组合与平台热点标签匹配度不足，建议补充[性价比]或[使用体验]类表达。')

    tech_words = ["科研", "专利", "成分", "配方", "技术", "实验室"]
    if any(w in str(selling_points) for w in tech_words):
        alerts.append('卖点表达偏技术化：用户更易被使用体验而非科研背书打动，建议增加[顺滑感][香味记忆点]等感性表达。')

    if len(selling_points) < 2:
        alerts.append("卖点维度单一：建议至少组合2个以上卖点（如功效+情绪），以提升内容丰富度和传播力。")

    if not alerts:
        alerts.append("当前卖点组合表现良好，建议持续监控竞品动态，及时调整内容策略。")

    return alerts


# ============================================================
# 七、物品协同过滤算法（Item-Based CF）
# 借鉴：算法/例子.txt 项目一 — 基于协同过滤的美妆商品推荐系统
# 核心思路：构建物品-标签特征矩阵，计算物品间余弦相似度，
#          找到与目标商品最相似的商品列表，再结合内容匹配加权
# ============================================================

ALL_TAG_FEATURES = [
    "修护", "柔顺", "留香", "控油", "蓬松", "去屑", "滋养", "温和", "清新感", "氛围感",
    "学生党", "价格敏感型", "通勤党", "染烫受损", "油皮头皮", "年轻女性用户",
    "宿舍日常", "开学季", "日常复购", "换季护理", "节日送礼", "通勤清洁",
]

TAG_INDEX = {tag: i for i, tag in enumerate(ALL_TAG_FEATURES)}


def _build_feature_vector(item: dict) -> list:
    """将商品标签字典转为定长二进制特征向量"""
    vec = [0.0] * len(ALL_TAG_FEATURES)
    for field in ("selling_points", "personas", "scenes"):
        for tag in item.get(field, []):
            if tag in TAG_INDEX:
                vec[TAG_INDEX[tag]] = 1.0
    return vec


def _cosine_similarity(vec_a: list, vec_b: list) -> float:
    """计算两个向量的余弦相似度"""
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class ItemCF:
    """
    基于物品的协同过滤推荐引擎
    算法来源：算法/例子.txt 项目一 — 混合推荐策略
      Step1: 构建物品特征矩阵（tag one-hot编码）
      Step2: 计算物品间余弦相似度矩阵
      Step3: 给定目标商品，返回相似度最高的TOP-N商品
      Step4: 结合内容匹配分（卖点/人群/场景）做混合加权推荐
    """

    def __init__(self, product_db: list):
        self.db = product_db
        self._vectors = {p["id"]: _build_feature_vector(p) for p in product_db}
        self._sim_matrix = self._build_sim_matrix()

    def _build_sim_matrix(self) -> dict:
        sim = {}
        ids = [p["id"] for p in self.db]
        for i, id_a in enumerate(ids):
            sim[id_a] = {}
            for id_b in ids:
                if id_a == id_b:
                    sim[id_a][id_b] = 1.0
                else:
                    sim[id_a][id_b] = _cosine_similarity(
                        self._vectors[id_a], self._vectors[id_b]
                    )
        return sim

    def get_similar_items(self, target_id: str, top_n: int = 5) -> list:
        """返回与target_id最相似的top_n个商品（不含自身）"""
        if target_id not in self._sim_matrix:
            return []
        sims = [(pid, score) for pid, score in self._sim_matrix[target_id].items()
                if pid != target_id]
        sims.sort(key=lambda x: x[1], reverse=True)
        results = []
        for pid, sim_score in sims[:top_n]:
            item = next((p for p in self.db if p["id"] == pid), None)
            if item:
                results.append({"item": item, "cf_similarity": round(sim_score, 4)})
        return results

    def hybrid_recommend(
        self,
        selling_points: list,
        target_users: list,
        scenes: list,
        top_n: int = 3,
        cf_weight: float = 0.4,
        content_weight: float = 0.6,
    ) -> list:
        """
        混合推荐：CF相似度（40%）+ 内容匹配分（60%）
        借鉴例子.txt：两阶段策略 — CF候选召回 + 内容精排
        """
        # Step1: 构建查询商品的临时特征向量
        query_item = {
            "id": "__query__",
            "selling_points": selling_points,
            "personas": target_users,
            "scenes": scenes,
        }
        query_vec = _build_feature_vector(query_item)

        scored = []
        for product in self.db:
            # CF分：查询向量与候选商品的余弦相似度
            cf_score = _cosine_similarity(query_vec, self._vectors[product["id"]])

            # 内容匹配分：卖点匹配(40%) + 人群匹配(30%) + 场景匹配(20%) + 商品基础分(10%)
            sp_match = sum(1 for sp in selling_points if sp in product["selling_points"])
            p_match = sum(1 for u in target_users if u in product["personas"])
            s_match = sum(1 for s in scenes if s in product["scenes"])

            content_score = (
                (sp_match / max(len(selling_points), 1)) * 0.40 +
                (p_match / max(len(target_users), 1)) * 0.30 +
                (s_match / max(len(scenes), 1)) * 0.20 +
                (product["score"] / 10.0) * 0.10
            )

            # 混合最终分
            final_score = cf_weight * cf_score + content_weight * content_score

            match_reasons = []
            if sp_match > 0:
                match_reasons.append(f"卖点标签匹配({sp_match}项)")
            if p_match > 0:
                match_reasons.append(f"目标人群重叠({p_match}项)")
            if s_match > 0:
                match_reasons.append(f"场景适配({s_match}项)")
            if cf_score > 0.6:
                match_reasons.append(f"CF相似度高({cf_score:.2f})")

            scored.append({
                "product": product,
                "final_score": final_score,
                "cf_score": round(cf_score, 4),
                "content_score": round(content_score, 4),
                "match_reasons": match_reasons,
            })

        scored.sort(key=lambda x: x["final_score"], reverse=True)

        results = []
        for item in scored[:top_n]:
            p = item["product"]
            match_score_pct = min(99, int(item["final_score"] * 100))
            reasons_str = "；".join(item["match_reasons"]) if item["match_reasons"] else "品类场景适配"
            results.append({
                "product_name": p["name"],
                "match_score": match_score_pct,
                "reason": reasons_str,
                "scenario": "、".join(p["scenes"][:2]),
                "price_band": p["price_band"],
                "cf_similarity": item["cf_score"],
            })
        return results


# ============================================================
# 七-B、推荐商品数据库 + 推荐入口
# ============================================================
PRODUCT_DATABASE = [
    {
        "id": "P001",
        "name": "DEAR SEED 玫瑰护手霜",
        "category": "洗护",
        "price_band": "100-150元",
        "selling_points": ["留香", "滋养", "玫瑰香氛"],
        "personas": ["学生党", "年轻女性用户"],
        "scenes": ["宿舍日常", "节日送礼"],
        "score": 8.5,
    },
    {
        "id": "P002",
        "name": "玫瑰香氛喷雾（示意）",
        "category": "洗护",
        "price_band": "50-100元",
        "selling_points": ["留香", "清新感", "氛围感"],
        "personas": ["学生党", "价格敏感型"],
        "scenes": ["宿舍日常", "日常复购"],
        "score": 7.8,
    },
    {
        "id": "P003",
        "name": "校园洗护礼盒套装（示意）",
        "category": "洗护",
        "price_band": "100-150元",
        "selling_points": ["修护", "柔顺", "留香"],
        "personas": ["学生党", "价格敏感型"],
        "scenes": ["开学季", "节日送礼"],
        "score": 7.5,
    },
    {
        "id": "P004",
        "name": "氨基酸护发精华（示意）",
        "category": "洗护",
        "price_band": "100-150元",
        "selling_points": ["修护", "温和", "滋养"],
        "personas": ["染烫受损", "年轻女性用户"],
        "scenes": ["日常复购", "换季护理"],
        "score": 7.2,
    },
    {
        "id": "P005",
        "name": "头皮控油洗发水（示意）",
        "category": "洗护",
        "price_band": "50-100元",
        "selling_points": ["控油", "蓬松", "清新感"],
        "personas": ["油皮头皮", "通勤党"],
        "scenes": ["通勤清洁", "日常复购"],
        "score": 6.9,
    },
]


# 全局 ItemCF 实例（使用 PRODUCT_DATABASE 初始化）
_item_cf_engine = None


def _get_cf_engine():
    """懒加载 ItemCF 引擎（单例）"""
    global _item_cf_engine
    if _item_cf_engine is None:
        _item_cf_engine = ItemCF(PRODUCT_DATABASE)
    return _item_cf_engine


def recommend_products(selling_points, target_user, scenes, top_n=3):
    """
    混合推荐接口（Item-CF + 内容匹配）
    算法升级：从纯内容匹配 → CF相似度(40%) + 内容匹配(60%) 混合策略
    借鉴：算法/例子.txt 项目一 — 混合推荐策略（协同过滤 + 深度特征匹配）
    """
    if isinstance(target_user, str):
        target_users = [u.strip() for u in target_user.replace("，", ",").split(",")]
    else:
        target_users = list(target_user)

    engine = _get_cf_engine()
    return engine.hybrid_recommend(
        selling_points=selling_points,
        target_users=target_users,
        scenes=scenes,
        top_n=top_n,
        cf_weight=0.4,
        content_weight=0.6,
    )


# ============================================================
# 八、内容生成引擎
# ============================================================
TITLE_TEMPLATES = [
    "学生党{efficacy}！{price}的{product_type}，{emotion}",
    "{season}宿舍洗护怎么选？这瓶{efficacy}路线真的很{emotion}",
    "{efficacy}、{efficacy2}、还好闻：{persona}也能负担的{scene}选择",
    "不想踩雷的{persona}，洗发水先看这瓶{efficacy}柔顺型",
    "{product_type}我会回购：{efficacy}感在线，{price}真的{emotion}",
]

COMMUNITY_TEMPLATES = [
    "姐妹们，{season}{scene}如果还没想好，可以优先看{efficacy}柔顺路线，这种香味好接受、价格也还友好的产品。",
    "如果你们最近头发有点毛躁，又不想一次性花太多预算，{efficacy}这种方向其实挺适合{persona}。",
    "我觉得{scene}选洗发水最重要的是三点：顺、好闻、别踩雷，这类{efficacy}型基本就围绕这三点展开。",
    '从种草角度看，这类产品最适合的不是特别硬的广告表达，而是[真实分享 + 日常体验]路线。',
]

VIDEO_HOOK_TEMPLATES = [
    "如果你是{persona}，最近又在纠结{scene}洗发水怎么选，那这个{efficacy}柔顺路线你可以先收藏。",
    "今天不讲太复杂的成分，我们只聊一件事：什么样的洗发水更适合{persona}日常用。",
    "为什么有些洗发水看起来都差不多，但就是有的更容易被{persona}买单？关键在场景和表达。",
    '一瓶适合{scene}带回去的洗发水，至少得满足三个条件：顺、好闻、预算别太高。',
]


def generate_content(product_name, selling_points, target_user, scenes, platform="小红书"):
    if isinstance(target_user, str):
        users = [u.strip() for u in target_user.replace("，", ",").split(",")]
    else:
        users = target_user

    persona = users[0] if users else "学生党"
    efficacy = selling_points[0] if selling_points else "修护"
    efficacy2 = selling_points[1] if len(selling_points) > 1 else "柔顺"
    scene = scenes[0] if scenes else "宿舍日常"
    season = "开学季" if datetime.now().month in [8, 9] else "日常"
    product_type = "洗发水"
    price = "100多块"
    emotion = "懂你"

    titles = []
    for tmpl in TITLE_TEMPLATES[:3]:
        try:
            title = tmpl.format(
                efficacy=efficacy, efficacy2=efficacy2, persona=persona,
                scene=scene, season=season, product_type=product_type,
                price=price, emotion=emotion,
            )
            titles.append(title)
        except KeyError:
            pass

    community = []
    for tmpl in COMMUNITY_TEMPLATES[:3]:
        try:
            text = tmpl.format(
                efficacy=efficacy, persona=persona, scene=scene, season=season)
            community.append(text)
        except KeyError:
            pass

    hooks = []
    for tmpl in VIDEO_HOOK_TEMPLATES[:3]:
        try:
            hook = tmpl.format(efficacy=efficacy, persona=persona, scene=scene)
            hooks.append(hook)
        except KeyError:
            pass

    return {
        "xiaohongshu_titles": titles,
        "community_scripts": community,
        "video_hooks": hooks,
        "tone_style": "真实分享 + 高性价比种草",
        "selling_point_expression": "、".join(selling_points[:3]),
        "scenario_expression": "、".join(scenes[:3]),
    }


# ============================================================
# 九、完整预测流程（供后端调用）
# ============================================================
def full_predict_pipeline(
    product_name="DEAR SEED 玫瑰修护洗发水",
    primary_category="洗护",
    secondary_category="修护洗发",
    selling_points=None,
    price_range="100-150元",
    target_user="学生党女性用户",
    platform="小红书",
):
    if selling_points is None:
        selling_points = ["修护", "柔顺", "玫瑰香氛"]

    month = datetime.now().month

    score_result = compute_potential_score(
        selling_points=selling_points,
        target_user=target_user,
        price_range=price_range,
        platform=platform,
        month=month,
    )

    personas = generate_persona_profile(target_user, selling_points, price_range)
    time_windows = recommend_best_time(selling_points, target_user, month)
    risks = generate_risk_alerts(selling_points, target_user, price_range, score_result["final_score"])

    inferred_scenes = score_result["inferred_scenes"]
    recommended_products = recommend_products(selling_points, target_user, inferred_scenes)
    content = generate_content(product_name, selling_points, target_user, inferred_scenes, platform)

    return {
        "product_name": product_name,
        "primary_category": primary_category,
        "secondary_category": secondary_category,
        "predict": {
            "potential_score": score_result["final_score"],
            "score_explanation": (
                f"卖点组合({'/'.join(selling_points)})与平台热点标签匹配度"
                f"{'较高' if score_result['final_score'] >= 7.5 else '中等'}，"
                f"具备{'较强' if score_result['final_score'] >= 8.0 else '一定'}内容传播潜力。"
            ),
            "factors": score_result["factors"],
            "target_persona": [p["persona_name"] for p in personas],
            "best_time": time_windows[0]["window"] if time_windows else "开学季（8月-9月）",
            "best_time_windows": time_windows,
            "risk_alert": risks,
            "key_tags": selling_points + [s for s in inferred_scenes[:2]],
        },
        "recommend": {
            "recommended_products": recommended_products,
            "recommended_scenes": inferred_scenes,
            "recommended_personas": [p["persona_name"] for p in personas],
            "recommended_platforms": ["小红书", "社群私域", "视频号"],
            "recommended_content_direction": [
                f"高性价比{secondary_category}",
                f"{'、'.join(selling_points[:2])}使用体验",
                "真实分享感种草",
            ],
            "decision_summary": (
                f"优先围绕{'、'.join(inferred_scenes[:2])}场景与"
                f"{'、'.join([p['persona_name'] for p in personas[:2]])}做种草表达，"
                "用真实体验打动用户，再通过搭配商品提升转化率。"
            ),
        },
        "content": content,
        "data_notice": "当前结果基于公开样本数据与模拟验证逻辑生成，不等同于真实投放结果。",
        "stage_notice": "当前为校赛MVP概念验证版本",
    }


# ============================================================
# 十、主函数（独立运行验证）
# ============================================================
def main():
    print("[>] 妆策AI — 爆款预测模型验证")
    print("=" * 60)
    print("输入：DEAR SEED 玫瑰修护洗发水")
    print("卖点：修护 + 柔顺 + 玫瑰香氛")
    print("价格：100-150元  人群：学生党  平台：小红书")
    print("=" * 60)

    result = full_predict_pipeline()

    print(f"\n【预测结果】")
    print(f"  传播潜力评分：{result['predict']['potential_score']} / 10")
    print(f"  评分说明：{result['predict']['score_explanation']}")
    print(f"\n  因子得分：")
    for k, v in result['predict']['factors'].items():
        print(f"    {k}: {v}")
    print(f"\n  高潜人群：{result['predict']['target_persona']}")
    print(f"  最佳推广时间：{result['predict']['best_time']}")
    print(f"\n  风险提示：")
    for r in result['predict']['risk_alert']:
        print(f"    [WARN] {r}")

    print(f"\n【推荐商品 TOP3】")
    for i, p in enumerate(result['recommend']['recommended_products'], 1):
        print(f"  {i}. {p['product_name']}  匹配度: {p['match_score']}%  场景: {p['scenario']}")

    print(f"\n【内容种草示例】")
    print(f"  小红书标题: {result['content']['xiaohongshu_titles'][0]}")
    print(f"  社群话术: {result['content']['community_scripts'][0]}")

    out_path = os.path.join(OUTPUT_DIR, "predict_result_sample.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] 预测结果已保存：{out_path}")

    return result


if __name__ == "__main__":
    result = main()
