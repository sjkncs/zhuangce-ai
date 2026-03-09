<template>
  <div class="home-page">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">妆策AI</h1>
        <p class="hero-subtitle">让品牌用预测代替试错，让增长更聪明</p>
        <p class="hero-desc">美妆新零售实战场景 · 智能推荐与营销转化平台</p>
        <div class="hero-actions">
          <el-button type="danger" size="large" @click="$router.push('/predict')" :icon="TrendCharts">
            开始预测
          </el-button>
          <el-button size="large" @click="$router.push('/dashboard')" :icon="DataAnalysis" plain>
            进入看板
          </el-button>
        </div>
      </div>
      <div class="hero-stats">
        <div class="stat-item" v-for="stat in heroStats" :key="stat.label">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
      </div>
    </div>

    <!-- Season Tip -->
    <el-alert v-if="overview.season_tip" :title="overview.season_tip"
      type="warning" :closable="false" show-icon class="season-tip" />

    <!-- 样板产品卡片 -->
    <div class="section-block">
      <div class="section-title"><div class="icon"></div>今日样板产品</div>
      <div class="product-card card" v-loading="loading">
        <div class="product-main">
          <div class="product-avatar">🌹</div>
          <div class="product-info">
            <div class="product-name">{{ product.sample_product_name }}</div>
            <div class="product-brand">品牌：{{ product.brand }}</div>
            <div class="product-meta">
              <el-tag>{{ product.primary_category }}</el-tag>
              <el-tag type="info">{{ product.secondary_category }}</el-tag>
              <el-tag type="warning">{{ product.target_price_range }}</el-tag>
            </div>
            <div class="product-points">
              <el-tag v-for="pt in product.core_selling_points" :key="pt"
                type="danger" effect="plain" class="point-tag">{{ pt }}</el-tag>
            </div>
            <div class="product-target">目标人群：{{ product.target_user_group }}</div>
          </div>
          <div class="product-score-block">
            <div class="score-label">传播潜力评分</div>
            <div class="score-badge">{{ coreCards.potential_score }}</div>
            <div class="score-rank">{{ coreCards.score_rank }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 核心数据卡 -->
    <div class="section-block">
      <div class="section-title"><div class="icon"></div>核心洞察卡片</div>
      <div class="insight-grid" v-loading="loading">
        <div class="insight-card card" v-for="ins in overview.quick_insights" :key="ins.title">
          <div class="ins-icon" :style="{ background: ins.color + '18', color: ins.color }">
            <el-icon size="24"><component :is="ins.icon" /></el-icon>
          </div>
          <div class="ins-title">{{ ins.title }}</div>
          <div class="ins-value" :style="{ color: ins.color }">{{ ins.value }}</div>
        </div>
      </div>
    </div>

    <!-- 人群分布 + 场景标签 -->
    <div class="two-col-grid">
      <div class="card" v-loading="loading">
        <div class="section-title"><div class="icon"></div>高潜人群分布</div>
        <v-chart :option="personaChartOption" style="height:220px" autoresize />
      </div>
      <div class="card">
        <div class="section-title"><div class="icon"></div>推荐平台优先级</div>
        <div class="platform-list">
          <div class="platform-item" v-for="(p, i) in coreCards.platform_priority" :key="p">
            <div class="platform-rank" :class="'rank-' + (i+1)">{{ i+1 }}</div>
            <div class="platform-name">{{ p }}</div>
            <el-progress :percentage="[90, 72, 58][i]" :stroke-width="10"
              :color="['#E74C3C','#E8834A','#3498DB'][i]" />
          </div>
        </div>
        <div class="section-title" style="margin-top:20px"><div class="icon"></div>场景标签热度</div>
        <div class="tag-list">
          <el-tag v-for="(t, i) in coreCards.top_scene_tags" :key="t"
            :type="['danger','warning',''][i]" effect="light" size="large" class="tag-item">
            {{ t }}
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 功能入口 -->
    <div class="section-block">
      <div class="section-title"><div class="icon"></div>核心功能入口</div>
      <div class="feature-grid">
        <div class="feature-card card" v-for="feat in features" :key="feat.path"
          @click="$router.push(feat.path)">
          <div class="feat-icon" :style="{ background: feat.color + '18' }">
            <el-icon size="32" :style="{ color: feat.color }"><component :is="feat.icon" /></el-icon>
          </div>
          <div class="feat-title">{{ feat.title }}</div>
          <div class="feat-desc">{{ feat.desc }}</div>
          <el-button :style="{ background: feat.color, borderColor: feat.color }"
            type="primary" size="small">进入 →</el-button>
        </div>
      </div>
    </div>

    <div class="data-notice">
      ⚠️ 数据说明：{{ overview.data_notice }} | 当前为校赛MVP概念验证版本
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { TrendCharts, DataAnalysis } from '@element-plus/icons-vue'
import axios from 'axios'

const loading = ref(false)
const overview = ref({ season_tip: '', data_notice: '', quick_insights: [] })
const product = ref({
  sample_product_name: 'DEAR SEED 玫瑰修护洗发水', brand: 'DEAR SEED',
  primary_category: '洗护', secondary_category: '修护洗发',
  core_selling_points: ['修护', '柔顺', '玫瑰香氛'],
  target_price_range: '100-150元', target_user_group: '学生党女性用户',
})
const coreCards = ref({
  potential_score: 8.2, score_rank: '超越同类83%产品',
  target_persona_summary: '学生党·宿舍场景·价格敏感型',
  top_scene_tags: ['宿舍日常', '开学季', '日常复购'],
  platform_priority: ['小红书', '社群私域', '视频号'],
  persona_distribution: [
    { name: '学生党', value: 58 }, { name: '价格敏感型', value: 24 }, { name: '年轻女性用户', value: 18 },
  ],
})

const heroStats = [
  { value: '8.2 / 10', label: '传播潜力评分' },
  { value: '83%', label: '超越同类产品' },
  { value: '5', label: '标签分析维度' },
  { value: '20条', label: '标注样本示例' },
]

const features = [
  { path: '/predict', title: '爆款预测引擎', icon: 'TrendCharts', color: '#E74C3C',
    desc: '输入卖点→输出传播潜力评分+人群建议' },
  { path: '/recommend', title: '推荐决策中心', icon: 'Star', color: '#E8834A',
    desc: '输出推荐商品、场景、平台优先级' },
  { path: '/content', title: '内容种草生成器', icon: 'Edit', color: '#27AE60',
    desc: '生成小红书标题、社群话术、视频开场' },
  { path: '/dashboard', title: '增长复盘看板', icon: 'DataAnalysis', color: '#3498DB',
    desc: '可视化趋势、分布、结论与策略' },
]

const personaChartOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c}%' },
  legend: { bottom: 0, textStyle: { fontSize: 12 } },
  color: ['#E74C3C', '#3498DB', '#27AE60'],
  series: [{
    type: 'pie', radius: ['38%', '65%'],
    label: { show: true, formatter: '{b}\n{d}%', fontSize: 12 },
    data: coreCards.value.persona_distribution,
  }],
}))

onMounted(async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/home/overview')
    if (res.data.code === 0) {
      const d = res.data.data
      overview.value = d
      if (d.sample_product) product.value = { ...product.value, ...d.sample_product }
      if (d.core_cards) coreCards.value = { ...coreCards.value, ...d.core_cards }
    }
  } catch (e) {
    // keep defaults
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.home-page { display: flex; flex-direction: column; gap: 24px; }
.hero-section {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #E74C3C22 100%);
  border-radius: 16px; padding: 40px 48px; display: flex;
  align-items: center; justify-content: space-between; gap: 32px;
  color: #fff;
}
.hero-title { font-size: 48px; font-weight: 900; letter-spacing: 4px; margin-bottom: 10px;
  background: linear-gradient(135deg, #fff 0%, #E74C3C 100%); -webkit-background-clip: text;
  -webkit-text-fill-color: transparent; background-clip: text; }
.hero-subtitle { font-size: 18px; font-weight: 600; margin-bottom: 8px; color: rgba(255,255,255,0.9); }
.hero-desc { font-size: 14px; color: rgba(255,255,255,0.6); margin-bottom: 24px; }
.hero-actions { display: flex; gap: 12px; }
.hero-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; min-width: 280px; }
.stat-item { background: rgba(255,255,255,0.08); border-radius: 12px; padding: 20px;
  text-align: center; border: 1px solid rgba(255,255,255,0.12); }
.stat-value { font-size: 24px; font-weight: 800; color: #E74C3C; }
.stat-label { font-size: 12px; color: rgba(255,255,255,0.65); margin-top: 4px; }
.season-tip :deep(.el-alert__title) { font-size: 14px; }
.section-block { }
.product-card { padding: 28px; }
.product-main { display: flex; align-items: flex-start; gap: 24px; }
.product-avatar { font-size: 64px; line-height: 1; }
.product-info { flex: 1; }
.product-name { font-size: 22px; font-weight: 800; color: #2c3e50; margin-bottom: 6px; }
.product-brand { font-size: 14px; color: #888; margin-bottom: 10px; }
.product-meta, .product-points { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 8px; }
.point-tag { font-weight: 600; }
.product-target { font-size: 14px; color: #555; margin-top: 4px; }
.product-score-block { text-align: center; min-width: 120px; }
.score-label { font-size: 12px; color: #888; margin-bottom: 8px; }
.score-badge { width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, #E74C3C, #C0392B);
  color: #fff; font-size: 28px; font-weight: 900; display: flex; align-items: center; justify-content: center;
  margin: 0 auto 8px; box-shadow: 0 6px 20px rgba(231,76,60,0.4); }
.score-rank { font-size: 12px; color: #E74C3C; font-weight: 600; }
.insight-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.insight-card { padding: 20px; display: flex; flex-direction: column; align-items: center; gap: 8px; text-align: center; }
.ins-icon { width: 56px; height: 56px; border-radius: 14px; display: flex; align-items: center; justify-content: center; }
.ins-title { font-size: 13px; color: #888; }
.ins-value { font-size: 18px; font-weight: 800; }
.two-col-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.platform-list { display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px; }
.platform-item { display: flex; align-items: center; gap: 12px; }
.platform-rank { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center;
  justify-content: center; font-size: 13px; font-weight: 800; color: #fff; flex-shrink: 0; }
.rank-1 { background: #E74C3C; } .rank-2 { background: #E8834A; } .rank-3 { background: #3498DB; }
.platform-name { font-size: 14px; font-weight: 600; min-width: 72px; }
.feature-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
.feature-card { padding: 24px; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s;
  display: flex; flex-direction: column; align-items: center; gap: 12px; text-align: center; }
.feature-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }
.feat-icon { width: 64px; height: 64px; border-radius: 16px; display: flex; align-items: center; justify-content: center; }
.feat-title { font-size: 16px; font-weight: 700; color: #2c3e50; }
.feat-desc { font-size: 12px; color: #888; line-height: 1.5; }
</style>
