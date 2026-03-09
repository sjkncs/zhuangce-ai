#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
妆策AI - 数据清洗脚本
阶段1：数据清洗与预处理
数据来源：
  - E:/meiz/数据集/2023年11月 美妆销售数据集/数据集.xlsx
  - E:/meiz/天猫双十一美妆销售数据分析模板/.../双十一淘宝美妆数据.csv
"""

import os
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

DATA_2023 = r"E:/meiz/数据集/2023年11月 美妆销售数据集/数据集.xlsx"
DATA_TIANMAO = r"E:/meiz/天猫双十一美妆销售数据分析模板/电商-天猫双十一美妆销售数据分析-约400行（matplotlib可视化、数据分析）/双十一淘宝美妆数据.csv"

CATEGORY_CONFIG = {
    # ── 护肤品 ──
    "套装": ("护肤品", "套装"), "礼盒": ("护肤品", "套装"),
    "乳液": ("护肤品", "乳液类"), "润肤乳": ("护肤品", "乳液类"), "菁华乳": ("护肤品", "乳液类"),
    "眼霜": ("护肤品", "眼部护理"), "眼膜": ("护肤品", "眼部护理"), "眼部精华": ("护肤品", "眼部护理"),
    "眼胶": ("护肤品", "眼部护理"), "眼部": ("护肤品", "眼部护理"),
    "面膜": ("护肤品", "面膜类"), "睡眠面膜": ("护肤品", "面膜类"), "面膜贴": ("护肤品", "面膜类"),
    "洗面": ("护肤品", "清洁类"), "洁面": ("护肤品", "清洁类"), "卸妆": ("护肤品", "清洁类"),
    "洗面奶": ("护肤品", "清洁类"), "洁面膏": ("护肤品", "清洁类"), "洁面乳": ("护肤品", "清洁类"),
    "深层清洁": ("护肤品", "清洁类"), "清洁面膜": ("护肤品", "清洁类"),
    "化妆水": ("护肤品", "化妆水"), "爽肤水": ("护肤品", "化妆水"), "柔肤水": ("护肤品", "化妆水"),
    "柔肤液": ("护肤品", "化妆水"), "收敛水": ("护肤品", "化妆水"), "活肤水": ("护肤品", "化妆水"),
    "面霜": ("护肤品", "面霜类"), "日霜": ("护肤品", "面霜类"), "晚霜": ("护肤品", "面霜类"),
    "润肤霜": ("护肤品", "面霜类"), "保湿霜": ("护肤品", "面霜类"), "滋润霜": ("护肤品", "面霜类"),
    "精华液": ("护肤品", "精华类"), "精华水": ("护肤品", "精华类"), "精华露": ("护肤品", "精华类"),
    "精华油": ("护肤品", "精华类"), "精萃": ("护肤品", "精华类"), "小棕瓶": ("护肤品", "精华类"),
    "小黑瓶": ("护肤品", "精华类"), "原液": ("护肤品", "精华类"),
    "防晒霜": ("护肤品", "防晒类"), "防晒": ("护肤品", "防晒类"), "隔离": ("护肤品", "防晒类"),
    "隔离霜": ("护肤品", "防晒类"), "SPF": ("护肤品", "防晒类"),
    # ── 化妆品/彩妆 ──
    "唇釉": ("化妆品", "口红类"), "口红": ("化妆品", "口红类"), "唇彩": ("化妆品", "口红类"),
    "唇膏": ("化妆品", "口红类"), "润唇膏": ("化妆品", "口红类"), "唇蜜": ("化妆品", "口红类"),
    "散粉": ("化妆品", "底妆类"), "粉底液": ("化妆品", "底妆类"), "气垫": ("化妆品", "底妆类"),
    "粉底": ("化妆品", "底妆类"), "粉饼": ("化妆品", "底妆类"), "遮瑕": ("化妆品", "底妆类"),
    "蜜粉": ("化妆品", "底妆类"), "定妆": ("化妆品", "底妆类"), "BB霜": ("化妆品", "底妆类"),
    "CC霜": ("化妆品", "底妆类"),
    "眼影": ("化妆品", "眼部彩妆"), "睫毛膏": ("化妆品", "眼部彩妆"), "眉笔": ("化妆品", "眼部彩妆"),
    "眼线": ("化妆品", "眼部彩妆"), "眉粉": ("化妆品", "眼部彩妆"), "眼线笔": ("化妆品", "眼部彩妆"),
    "腮红": ("化妆品", "修容类"), "高光": ("化妆品", "修容类"), "修容": ("化妆品", "修容类"),
    # ── 洗护 ──
    "洗发水": ("洗护", "修护洗发"), "洗发": ("洗护", "修护洗发"),
    "护发": ("洗护", "护发素"), "柔顺剂": ("洗护", "护发素"), "发膜": ("洗护", "护发素"),
    "沐浴露": ("洗护", "沐浴类"), "香皂": ("洗护", "沐浴类"), "浴盐": ("洗护", "沐浴类"),
    "护手霜": ("洗护", "手部护理"), "润手霜": ("洗护", "手部护理"), "手膜": ("洗护", "手部护理"),
    "身体乳": ("洗护", "身体护理"), "润肤露": ("洗护", "身体护理"), "润肤乳": ("洗护", "身体护理"),
    # ── 香氛 ──
    "香水": ("香氛", "香水类"), "香氛": ("香氛", "香水类"), "淡香": ("香氛", "香水类"),
    "古龙水": ("香氛", "香水类"),
    # ── 美妆工具 ──
    "美妆工具": ("工具", "美妆工具"), "化妆刷": ("工具", "美妆工具"), "粉扑": ("工具", "美妆工具"),
    "刮胡": ("工具", "男士工具"), "剃须": ("工具", "男士工具"), "须后": ("洗护", "男士护理"),
}

LABEL_KEYWORDS = {
    "efficacy": {
        "补水保湿": ["补水", "保湿", "水润", "锁水", "滋润", "润泽", "水嫩"],
        "美白提亮": ["美白", "提亮", "亮肤", "焕白", "淡斑", "提亮肤色", "透白", "净白"],
        "抗皱紧致": ["抗皱", "紧致", "淡化细纹", "抗衰", "提拉", "弹力", "弹润", "抗老"],
        "修护": ["修护", "修复", "受损", "改善", "舒缓", "镇静", "维稳"],
        "控油": ["控油", "清爽", "去油", "油头", "控痘", "祛痘", "抑菌"],
        "清洁": ["清洁", "深层清洁", "毛孔", "去角质", "清透", "净化"],
        "防晒隔离": ["防晒", "SPF", "UV", "隔离", "防紫外线"],
        "柔顺": ["柔顺", "顺滑", "不毛躁"],
        "留香": ["香氛", "留香", "香味", "好闻"],
        "蓬松": ["蓬松", "发量"],
        "去屑": ["去屑", "头屑", "止痒"],
        "遮瑕": ["遮瑕", "遮盖", "持久", "不脱妆", "不脱色"],
        "防水": ["防水", "不晕染", "防汗"],
    },
    "persona": {
        "学生党": ["学生", "宿舍", "学生党", "大学", "校园"],
        "价格敏感型": ["性价比", "平价", "便宜", "不贵", "实惠", "特价"],
        "男士": ["男士", "男生", "男", "men", "man", "boy"],
        "敏感肌": ["敏感肌", "敏肌", "温和", "不刺激", "无刺激", "脆弱肌"],
        "干性肌肤": ["干性", "干皮", "干燥", "滋润型", "深层滋养"],
        "油性肌肤": ["油性", "油皮", "油脂", "清爽型"],
        "染烫受损": ["染发", "烫发", "受损", "毛躁"],
        "轻熟女": ["抗老", "抗衰", "紧致", "初老", "轻熟"],
    },
    "scene": {
        "双十一": ["双11", "双十一", "11-11", "预售", "抢先预售"],
        "日常护肤": ["日常", "每日", "日夜", "早晚", "日用"],
        "送礼": ["礼盒", "礼物", "送礼", "套装", "伴手礼"],
        "旅行便携": ["旅行", "便携", "迷你", "中样", "小样"],
        "换季护理": ["换季", "秋冬", "季节", "春夏"],
        "官方正品": ["专柜正品", "官方正品", "正品", "旗舰店", "官方"],
    },
    "emotion": {
        "高级感": ["高级", "精致", "品质感", "奢华", "尊享"],
        "治愈感": ["治愈", "放松", "舒适", "舒缓", "温和"],
        "清新感": ["清新", "清爽", "自然", "透气", "轻薄"],
        "安心感": ["安心", "放心", "不踩雷", "温泉", "天然"],
        "专业感": ["专业", "医用", "药用", "皮肤科", "配方"],
    },
}


def generate_mock_sales_data():
    np.random.seed(42)
    n = 500
    brands = ["DEAR SEED", "相宜本草", "欧莱雅", "珀莱雅", "美宝莲", "百雀羚", "自然堂", "韩束"]
    titles_pool = [
        "玫瑰修护洗发水宿舍学生党柔顺",
        "氨基酸洗发水修护受损发质",
        "控油蓬松洗发水油头适用",
        "补水保湿面霜敏感肌适用",
        "遮瑕持久口红不脱色",
        "烟酰胺美白精华液",
        "清洁面膜收缩毛孔",
        "玻尿酸补水爽肤水",
        "防晒霜轻薄不闷",
        "护手霜玫瑰香氛",
    ]
    return pd.DataFrame({
        "update_time": pd.date_range("2023-11-01", periods=n, freq="H"),
        "id": range(1, n + 1),
        "title": [np.random.choice(titles_pool) + " " + np.random.choice(brands) for _ in range(n)],
        "price": np.random.lognormal(5, 0.8, n).clip(10, 800).round(1),
        "sale_count": np.random.negative_binomial(2, 0.1, n),
        "comment_count": np.random.negative_binomial(1, 0.2, n),
        "店名": np.random.choice(brands, n),
    })


def load_data():
    print("=" * 60)
    print("步骤一：加载数据")
    try:
        df = pd.read_excel(DATA_2023)
        print(f"  [OK] 2023美妆销售数据：{len(df)} 行 * {len(df.columns)} 列")
        print(f"  原始字段：{list(df.columns)}")
        # 中文列名 → 英文列名映射（兼容真实数据集）
        col_rename = {
            "售卖日期": "update_time",
            "商品ID": "id",
            "商品名称": "title",
            "价格": "price",
            "售卖数量": "sale_count",
            "评论数量": "comment_count",
            "品牌": "店名",
        }
        df = df.rename(columns={k: v for k, v in col_rename.items() if k in df.columns})
        print(f"  映射后字段：{list(df.columns)}")
    except FileNotFoundError:
        print(f"  [WARN] 数据文件未找到，使用内置模拟数据演示")
        df = generate_mock_sales_data()

    df_tianmao = None
    try:
        df_tianmao = pd.read_csv(DATA_TIANMAO, encoding='utf-8')
        print(f"  [OK] 天猫双十一数据：{len(df_tianmao)} 行 × {len(df_tianmao.columns)} 列")
    except FileNotFoundError:
        print(f"  [i] 天猫数据文件未找到，跳过")

    return df, df_tianmao


def clean_sales_data(df):
    print("\n步骤二：数据清洗")
    orig = len(df)

    df = df.drop_duplicates().reset_index(drop=True)
    print(f"  去重：{orig} → {len(df)} 行（删除 {orig - len(df)} 条）")

    null_info = df.isnull().sum()
    if null_info.any():
        print(f"  缺失值：\n{null_info[null_info > 0]}")
    df = df.fillna(0)

    for col in ["price", "sale_count", "comment_count"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    if "price" in df.columns:
        df = df[df["price"] > 0]

    if "sale_count" in df.columns and "price" in df.columns:
        df["销售额"] = (df["sale_count"] * df["price"]).round(2)

    for col in df.columns:
        if "time" in col.lower() or "date" in col.lower():
            df[col] = pd.to_datetime(df[col], errors="coerce")

    print(f"  清洗完成：{len(df)} 行 × {len(df.columns)} 列")
    return df


def add_category_labels(df):
    print("\n步骤三：品类标签分配")
    try:
        import jieba
        jieba.setLogLevel(20)

        def classify(title):
            words = jieba.lcut(str(title))
            for w in words:
                if w in CATEGORY_CONFIG:
                    return CATEGORY_CONFIG[w]
            return ("其他", "其他")

        labels = df["title"].apply(classify)
        df["main_category"] = labels.apply(lambda x: x[0])
        df["sub_category"] = labels.apply(lambda x: x[1])
        print(f"  品类分布：\n{df['main_category'].value_counts().to_string()}")
    except ImportError:
        print("  [WARN] jieba未安装，跳过分词分类。运行：pip install jieba")
        df["main_category"] = "其他"
        df["sub_category"] = "其他"
    return df


def match_tags(text, label_dict):
    matched = []
    for tag, keywords in label_dict.items():
        if any(kw in str(text) for kw in keywords):
            matched.append(tag)
    return ",".join(matched) if matched else None


def add_content_tags(df):
    print("\n步骤四：内容标签标注")
    if "title" in df.columns:
        df["efficacy_tags"] = df["title"].apply(
            lambda t: match_tags(t, LABEL_KEYWORDS["efficacy"]))
        df["persona_tags"] = df["title"].apply(
            lambda t: match_tags(t, LABEL_KEYWORDS["persona"]))
        df["scene_tags"] = df["title"].apply(
            lambda t: match_tags(t, LABEL_KEYWORDS["scene"]))
        df["emotion_tags"] = df["title"].apply(
            lambda t: match_tags(t, LABEL_KEYWORDS["emotion"]))
        print("  [OK] 功效/人群/场景/情绪标签已添加")
    return df


def add_gender_flag(df):
    """
    新增「是否男士专用」字段
    借鉴天猫双十一模板 2.3：遍历商品标题分词，判断是否含男性关键词
    """
    print("\n步骤五-A：性别属性识别（借鉴天猫双十一模板 2.3）")
    if "title" not in df.columns:
        print("  [WARN] 无 title 字段，跳过")
        return df

    male_keywords = ["男", "男士", "男生", "boy", "men", "man"]

    def is_male_product(title):
        title_lower = str(title).lower()
        return "是" if any(kw in title_lower for kw in male_keywords) else "否"

    df["是否男士专用"] = df["title"].apply(is_male_product)
    male_count = (df["是否男士专用"] == "是").sum()
    print(f"  男士专用产品：{male_count} 件，女性/中性：{len(df) - male_count} 件")
    return df


def add_time_features(df):
    """
    新增时间维度字段（day/month/weekday）
    借鉴天猫双十一模板 2.3：将 update_time 解析为购买日期，分析销售高峰期
    """
    print("\n步骤五-B：时间特征提取（借鉴天猫双十一模板 2.3）")
    time_col = None
    for col in df.columns:
        if "time" in col.lower() or "date" in col.lower():
            time_col = col
            break

    if time_col is None:
        print("  [WARN] 无时间字段，跳过")
        return df

    df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
    df["day"] = df[time_col].dt.day
    df["month"] = df[time_col].dt.month
    df["weekday"] = df[time_col].dt.day_name()
    print(f"  [OK] 已新增 day / month / weekday 时间维度字段")
    if "day" in df.columns:
        peak_day = df.groupby("day")["sale_count"].sum().idxmax() if "sale_count" in df.columns else None
        if peak_day:
            print(f"  销量高峰日（当月）：{int(peak_day)} 日")
    return df


def compute_heat_score(df):
    print("\n步骤五：热度评分计算")
    if "sale_count" in df.columns and "comment_count" in df.columns:
        max_sale = df["sale_count"].max() or 1
        max_comment = df["comment_count"].max() or 1
        df["heat_score"] = (
            0.6 * df["sale_count"] / max_sale +
            0.4 * df["comment_count"] / max_comment
        ).round(4) * 10
        print(f"  热度评分范围：{df['heat_score'].min():.2f} ~ {df['heat_score'].max():.2f}")
    return df


def save_cleaned_data(df, filename="clean_beauty_sales.xlsx"):
    out_path = os.path.join(OUTPUT_DIR, filename)
    df.to_excel(out_path, index=False, sheet_name="clean_data")
    print(f"  [OK] 清洗结果已保存：{out_path}")
    return out_path


def main():
    print("[START] 妆策AI -- 数据清洗脚本启动")
    print("=" * 60)

    df, df_tianmao = load_data()
    df = clean_sales_data(df)
    df = add_category_labels(df)
    df = add_content_tags(df)
    df = add_gender_flag(df)        # 借鉴天猫模板 2.3：是否男士专用
    df = add_time_features(df)      # 借鉴天猫模板 2.3：day/month/weekday
    df = compute_heat_score(df)

    out_path = save_cleaned_data(df)

    print("\n" + "=" * 60)
    print("数据预览（前5行）：")
    cols_to_show = [c for c in ["title", "price", "sale_count", "comment_count",
                                 "main_category", "sub_category", "heat_score",
                                 "efficacy_tags", "persona_tags"] if c in df.columns]
    print(df[cols_to_show].head().to_string())

    print("\n" + "=" * 60)
    print("清洗完成！结果文件：", out_path)
    return df


if __name__ == "__main__":
    df_clean = main()
