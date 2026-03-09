<template>
  <div class="dashboard-page">
    <div class="page-header">
      <h2 class="page-title">📊 增长复盘看板</h2>
      <p class="page-desc">用数据复盘策略效果，让增长形成闭环——传播潜力评分趋势 · 人群分布 · 场景热度 · 结论洞察</p>
      <div class="header-meta">
        <el-tag type="info" size="small">生成时间：{{ data.generated_at }}</el-tag>
        <el-tag type="warning" size="small">校赛MVP版本</el-tag>
      </div>
    </div>

    <div class="dashboard-layout" v-loading="loading">

      <!-- KPI Cards -->
      <div class="kpi-row">
        <div class="kpi-card card" v-for="kpi in kpiCards" :key="kpi.label">
          <div class="kpi-icon" :style="{ background: kpi.color + '18', color: kpi.color }">
            <span class="kpi-emoji">{{ kpi.emoji }}</span>
          </div>
          <div class="kpi-body">
            <div class="kpi-value" :style="{ color: kpi.color }">{{ kpi.value }}</div>
            <div class="kpi-label">{{ kpi.label }}</div>
            <div class="kpi-sub">{{ kpi.sub }}</div>
          </div>
        </div>
      </div>

      <!-- 传播潜力趋势 + 品类对比 -->
      <div class="charts-row-3">
        <div class="card span-2">
          <div class="section-title"><div class="icon"></div>传播潜力评分演进趋势（Day1-Day7）</div>
          <v-chart :option="trendOption" style="height:260px" autoresize />
        </div>
        <div class="card">
          <div class="section-title"><div class="icon"></div>品类竞品评分对比</div>
          <v-chart :option="brandBarOption" style="height:260px" autoresize />
        </div>
      </div>

      <!-- 人群 + 场景分布 -->
      <div class="charts-row-2">
        <div class="card">
          <div class="section-title"><div class="icon"></div>高潜人群分布</div>
          <v-chart :option="personaPieOption" style="height:240px" autoresize />
        </div>
        <div class="card">
          <div class="section-title"><div class="icon"></div>内容场景分布</div>
          <v-chart :option="scenePieOption" style="height:240px" autoresize />
        </div>
      </div>

      <!-- 功效×场景热力图 -->
      <div class="card">
        <div class="section-title"><div class="icon"></div>功效标签 × 场景标签 共现热力图（传播潜力核心依据）</div>
        <v-chart :option="heatmapOption" style="height:300px" autoresize />
        <p class="chart-insight">📌 核心发现：修护×宿舍日常共现最高(18次)，是传播潜力评分8.2的最强支撑因子</p>
      </div>

      <!-- 价格带热度分布 -->
      <div class="card">
        <div class="section-title"><div class="icon"></div>各价格带平均热度评分（目标价格带高亮）</div>
        <v-chart :option="priceBarOption" style="height:240px" autoresize />
      </div>

      <!-- 推荐匹配度 + 子类对比 -->
      <div class="charts-row-2">
        <div class="card">
          <div class="section-title"><div class="icon"></div>TOP推荐商品匹配度</div>
          <v-chart :option="recBarOption" style="height:220px" autoresize />
        </div>
        <div class="card">
          <div class="section-title"><div class="icon"></div>各洗护子类传播潜力对比</div>
          <v-chart :option="subcatBarOption" style="height:220px" autoresize />
        </div>
      </div>

      <!-- 核心洞察 -->
      <div class="insights-section card">
        <div class="section-title"><div class="icon"></div>数据洞察与核心结论</div>
        <div class="insights-grid">
          <div class="insight-block" v-for="(ins, i) in insightList" :key="i"
            :style="{ borderLeftColor: ins.color }">
            <div class="ib-num" :style="{ background: ins.color }">{{ i + 1 }}</div>
            <div class="ib-content">
              <div class="ib-title">{{ ins.title }}</div>
              <p class="ib-text">{{ ins.text }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 综合决策结论 -->
      <div class="conclusion-card card">
        <div class="section-title"><div class="icon"></div>综合决策结论</div>
        <p class="conclusion-text">{{ data.dashboard_conclusion }}</p>
        <div class="cta-row">
          <el-button type="danger" @click="$router.push('/predict')">重新预测 →</el-button>
          <el-button type="warning" @click="$router.push('/recommend')">查看推荐 →</el-button>
          <el-button type="success" @click="$router.push('/content')">生成内容 →</el-button>
        </div>
      </div>

      <div class="data-notice">{{ data.dashboard_notice }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const loading = ref(false)

const data = ref({
  dashboard_potential_score: 8.2,
  score_percentile: 83,
  generated_at: new Date().toLocaleString('zh-CN'),
  dashboard_trend_data: [
    { label: 'Day1', score: 7.1 }, { label: 'Day2', score: 7.4 },
    { label: 'Day3', score: 7.8 }, { label: 'Day4', score: 7.9 },
    { label: 'Day5', score: 8.0 }, { label: 'Day6', score: 8.1 },
    { label: 'Day7', score: 8.2 },
  ],
  dashboard_scene_distribution: [
    { name: '宿舍日常', value: 46 },
    { name: '开学季', value: 32 },
    { name: '日常复购', value: 22 },
  ],
  dashboard_persona_distribution: [
    { name: '学生党', value: 58 },
    { name: '价格敏感型', value: 24 },
    { name: '年轻女性用户', value: 18 },
  ],
  dashboard_efficacy_heatmap: {
    x_axis: ['宿舍日常', '开学季', '日常复购', '换季护理'],
    y_axis: ['修护', '柔顺', '留香', '控油', '蓬松', '去屑'],
    data: [
      [0, 0, 18], [0, 1, 14], [0, 2, 8], [0, 3, 6],
      [1, 0, 16], [1, 1, 12], [1, 2, 11], [1, 3, 5],
      [2, 0, 12], [2, 1, 8],  [2, 2, 7],  [2, 3, 4],
      [3, 0, 4],  [3, 1, 3],  [3, 2, 9],  [3, 3, 7],
      [4, 0, 3],  [4, 1, 4],  [4, 2, 8],  [4, 3, 6],
      [5, 0, 2],  [5, 1, 2],  [5, 2, 5],  [5, 3, 8],
    ],
  },
  dashboard_price_distribution: [
    { band: '0-50元',   avg_heat: 6.2 },
    { band: '50-100元', avg_heat: 7.1 },
    { band: '100-150元',avg_heat: 8.0 },
    { band: '150-200元',avg_heat: 7.6 },
    { band: '200-300元',avg_heat: 7.0 },
    { band: '300-500元',avg_heat: 6.5 },
    { band: '500元+',   avg_heat: 5.8 },
  ],
  dashboard_top_recommendations: [
    { name: 'DEAR SEED 玫瑰护手霜', score: 92 },
    { name: '玫瑰香氛喷雾（示意）',   score: 85 },
    { name: '校园洗护礼盒（示意）',   score: 78 },
  ],
  dashboard_brand_comparison: [
    { brand: 'DEAR SEED（样板）', score: 8.2 },
    { brand: '修护洗发平均',       score: 8.1 },
    { brand: '香氛洗发平均',       score: 7.9 },
    { brand: '控油洗发平均',       score: 7.2 },
    { brand: '洗护品类均值',       score: 7.4 },
  ],
  dashboard_subcat_comparison: [
    { name: '修护洗发',   score: 8.1 },
    { name: '控油洗发',   score: 7.2 },
    { name: '蓬松洗发',   score: 7.6 },
    { name: '去屑洗发',   score: 6.8 },
    { name: '香氛洗发',   score: 7.9 },
    { name: '护发素',     score: 7.5 },
  ],
  dashboard_conclusion: 'DEAR SEED 玫瑰修护洗发水传播潜力评分 8.2，超越同类 83% 产品。建议优先布局小红书宿舍场景种草，结合开学季节点，以修护柔顺+玫瑰香氛为核心卖点组合，精准触达学生党群体。内容策略聚焦真实体验分享而非成分背书，有望在 2-4 周内形成小爆款内容矩阵。',
  dashboard_notice: '当前为公开样本数据与模拟验证结果，用于展示项目方法论与决策逻辑。',
})

const kpiCards = computed(() => [
  { emoji: '📈', label: '传播潜力评分', value: data.value.dashboard_potential_score, sub: `超越同类 ${data.value.score_percentile}% 产品`, color: '#E74C3C' },
  { emoji: '👤', label: '主力人群占比', value: '58%', sub: '学生党 · 宿舍场景', color: '#3498DB' },
  { emoji: '📍', label: '最强场景热度', value: '46%', sub: '宿舍日常内容占比', color: '#27AE60' },
  { emoji: '💰', label: '目标价格带排名', value: 'TOP 2', sub: '100-150元均热度 8.0', color: '#9B59B6' },
])

const insightList = computed(() => [
  { title: '场景切入口洞察', text: '宿舍场景是当前最强内容切入口，修护×宿舍日常共现频率最高(18次)，建议优先布局该场景内容。', color: '#E74C3C' },
  { title: '人群需求洞察',   text: '学生党更关注顺滑感与价格接受度，100-150元价格带热度表现优于同档均值，定价策略吻合需求。', color: '#3498DB' },
  { title: '内容传播洞察',   text: '香氛表达有助于提升内容点击意愿，玫瑰香氛组合可强化情绪价值输出，建议结合"宿舍香氛感"角度创作。', color: '#27AE60' },
])

const trendOption = computed(() => ({
  tooltip: { trigger: 'axis', formatter: (p) => `${p[0].name}<br/>评分：<b>${p[0].value}</b>` },
  grid: { left: 40, right: 20, bottom: 30, top: 20 },
  xAxis: {
    type: 'category',
    data: data.value.dashboard_trend_data.map(d => d.label),
    axisLine: { lineStyle: { color: '#ddd' } },
  },
  yAxis: { type: 'value', min: 6, max: 10, splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } } },
  series: [{
    type: 'line', smooth: true, symbol: 'circle', symbolSize: 8,
    data: data.value.dashboard_trend_data.map(d => d.score),
    lineStyle: { color: '#E74C3C', width: 3 },
    itemStyle: { color: '#E74C3C' },
    areaStyle: {
      color: {
        type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [{ offset: 0, color: 'rgba(231,76,60,0.25)' }, { offset: 1, color: 'rgba(231,76,60,0.02)' }],
      },
    },
    markLine: {
      data: [{ yAxis: 8.2, name: '最终评分' }],
      lineStyle: { color: '#E74C3C', type: 'dashed' },
      label: { formatter: '最终 8.2', color: '#E74C3C', fontWeight: 'bold' },
    },
  }],
}))

const brandBarOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 10, right: 20, bottom: 60, top: 10, containLabel: true },
  xAxis: {
    type: 'category',
    data: data.value.dashboard_brand_comparison.map(b => b.brand),
    axisLabel: { rotate: 20, fontSize: 10 },
  },
  yAxis: { type: 'value', min: 6, max: 10 },
  series: [{
    type: 'bar', barWidth: '55%',
    data: data.value.dashboard_brand_comparison.map((b, i) => ({
      value: b.score,
      itemStyle: { color: i === 0 ? '#E74C3C' : '#5DADE2', borderRadius: [6, 6, 0, 0] },
    })),
    label: { show: true, position: 'top', fontWeight: 'bold', fontSize: 11 },
  }],
}))

const personaPieOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c}%' },
  legend: { bottom: 0, textStyle: { fontSize: 11 } },
  color: ['#E74C3C', '#3498DB', '#27AE60'],
  series: [{
    type: 'pie', radius: ['38%', '62%'],
    label: { formatter: '{b}\n{d}%', fontSize: 11 },
    data: data.value.dashboard_persona_distribution,
  }],
}))

const scenePieOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c}%' },
  legend: { bottom: 0, textStyle: { fontSize: 11 } },
  color: ['#E8834A', '#9B59B6', '#1ABC9C'],
  series: [{
    type: 'pie', radius: ['38%', '62%'],
    label: { formatter: '{b}\n{d}%', fontSize: 11 },
    data: data.value.dashboard_scene_distribution,
  }],
}))

const heatmapOption = computed(() => {
  const hm = data.value.dashboard_efficacy_heatmap
  const chartData = hm.data.map(d => [d[1], d[0], d[2]])
  return {
    tooltip: {
      position: 'top',
      formatter: (p) => `${hm.y_axis[p.value[1]]} × ${hm.x_axis[p.value[0]]}<br/>共现频率: <b>${p.value[2]}</b>`,
    },
    grid: { left: 70, right: 20, bottom: 60, top: 10 },
    xAxis: { type: 'category', data: hm.x_axis, splitArea: { show: true } },
    yAxis: { type: 'category', data: hm.y_axis, splitArea: { show: true } },
    visualMap: {
      min: 0, max: 20, calculable: true, orient: 'horizontal', left: 'center', bottom: 0,
      inRange: { color: ['#fff5f5', '#ffcdd2', '#ef9a9a', '#e57373', '#E74C3C', '#C0392B'] },
    },
    series: [{
      type: 'heatmap', data: chartData,
      label: { show: true, color: '#333', fontWeight: 'bold' },
    }],
  }
})

const priceBarOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 40, right: 20, bottom: 50, top: 10 },
  xAxis: {
    type: 'category',
    data: data.value.dashboard_price_distribution.map(d => d.band),
    axisLabel: { rotate: 25, fontSize: 11 },
  },
  yAxis: { type: 'value', min: 5, max: 9 },
  series: [{
    type: 'bar', barWidth: '55%',
    data: data.value.dashboard_price_distribution.map(d => ({
      value: d.avg_heat,
      itemStyle: { color: d.band === '100-150元' ? '#E74C3C' : '#5DADE2', borderRadius: [6, 6, 0, 0] },
    })),
    label: { show: true, position: 'top', fontWeight: 'bold', fontSize: 11 },
  }],
}))

const recBarOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 20, right: 20, bottom: 60, top: 10, containLabel: true },
  xAxis: {
    type: 'category',
    data: data.value.dashboard_top_recommendations.map(r => r.name.length > 10 ? r.name.slice(0, 10) + '…' : r.name),
    axisLabel: { rotate: 15, fontSize: 10 },
  },
  yAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' } },
  series: [{
    type: 'bar', barWidth: '50%',
    data: data.value.dashboard_top_recommendations.map((r, i) => ({
      value: r.score,
      itemStyle: {
        color: ['#E74C3C', '#E8834A', '#9B59B6'][i] || '#5DADE2',
        borderRadius: [6, 6, 0, 0],
      },
    })),
    label: { show: true, position: 'top', formatter: '{c}%', fontWeight: 'bold', fontSize: 11 },
  }],
}))

const subcatBarOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 20, right: 20, bottom: 60, top: 10, containLabel: true },
  xAxis: {
    type: 'category',
    data: data.value.dashboard_subcat_comparison.map(d => d.name),
    axisLabel: { rotate: 15, fontSize: 10 },
  },
  yAxis: { type: 'value', min: 5, max: 10 },
  series: [{
    type: 'bar', barWidth: '50%',
    data: data.value.dashboard_subcat_comparison.map(d => ({
      value: d.score,
      itemStyle: { color: d.name === '修护洗发' ? '#E74C3C' : '#5DADE2', borderRadius: [6, 6, 0, 0] },
    })),
    label: { show: true, position: 'top', fontWeight: 'bold', fontSize: 11 },
  }],
}))

const fetchDashboard = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/dashboard')
    if (res.data.code === 0) {
      data.value = { ...data.value, ...res.data.data }
    }
  } catch (e) {
    // use default mock data
  } finally {
    loading.value = false
  }
}

onMounted(() => { fetchDashboard() })
</script>

<style scoped>
.dashboard-page { display: flex; flex-direction: column; gap: 24px; }
.page-title { font-size: 28px; font-weight: 800; color: #2c3e50; }
.page-desc { font-size: 14px; color: #888; margin-top: 6px; }
.header-meta { display: flex; gap: 8px; margin-top: 10px; }
.kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.kpi-card { display: flex; align-items: center; gap: 16px; }
.kpi-icon { width: 56px; height: 56px; border-radius: 16px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.kpi-emoji { font-size: 26px; }
.kpi-value { font-size: 28px; font-weight: 900; line-height: 1; }
.kpi-label { font-size: 13px; color: #555; margin-top: 4px; font-weight: 600; }
.kpi-sub { font-size: 11px; color: #aaa; margin-top: 2px; }
.charts-row-3 { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
.charts-row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.span-2 { grid-column: 1 / 2; }
.chart-insight { margin: 8px 0 0; font-size: 13px; color: #E74C3C; font-weight: 600; padding: 8px 12px; background: #fff5f5; border-radius: 8px; }
.insights-section { }
.insights-grid { display: flex; flex-direction: column; gap: 12px; }
.insight-block { display: flex; align-items: flex-start; gap: 14px; padding: 14px 16px; background: #f9f9f9; border-radius: 10px; border-left: 4px solid; }
.ib-num { min-width: 26px; height: 26px; border-radius: 50%; color: #fff; font-size: 13px; font-weight: 800; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.ib-title { font-size: 14px; font-weight: 700; color: #2c3e50; margin-bottom: 4px; }
.ib-text { font-size: 13px; color: #666; line-height: 1.7; margin: 0; }
.conclusion-card { }
.conclusion-text { font-size: 15px; color: #2c3e50; line-height: 1.8; padding: 14px; background: #f9f9f9; border-radius: 10px; margin-bottom: 16px; }
.cta-row { display: flex; gap: 12px; }
</style>
