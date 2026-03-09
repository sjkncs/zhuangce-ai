<template>
  <div class="recommend-page">
    <div class="page-header">
      <h2 class="page-title">⭐ 推荐决策中心</h2>
      <p class="page-desc">让预测结果直接转化为商品、场景与内容决策——预测回答"值不值得推"，推荐回答"应该怎么推"</p>
    </div>

    <div class="recommend-layout" v-loading="loading">
      <!-- TOP推荐商品 -->
      <div class="section-block">
        <div class="section-title"><div class="icon"></div>推荐商品 TOP{{ data.recommended_products?.length }}</div>
        <div class="product-grid">
          <div class="rec-product-card card" v-for="(p, i) in data.recommended_products" :key="p.product_name">
            <div class="rec-rank" :class="'rank-' + (i+1)">TOP{{ i+1 }}</div>
            <div class="rec-product-name">{{ p.product_name }}</div>
            <div class="match-score-wrap">
              <el-progress type="circle" :percentage="p.match_score" :width="80"
                :color="matchColors[i]" :stroke-width="8"
                :format="() => p.match_score + '%'" />
              <span class="match-label">匹配度</span>
            </div>
            <div class="rec-reason"><el-icon><InfoFilled /></el-icon> {{ p.reason }}</div>
            <div class="rec-meta">
              <el-tag size="small">{{ p.scenario }}</el-tag>
              <el-tag size="small" type="warning">{{ p.price_band }}</el-tag>
            </div>
          </div>
        </div>
      </div>

      <!-- 推荐策略三列 -->
      <div class="strategy-grid">
        <div class="card strategy-card">
          <div class="section-title"><div class="icon"></div>推荐场景</div>
          <div class="strategy-items">
            <div class="strategy-item" v-for="(s, i) in data.recommended_scenes" :key="s">
              <div class="si-icon" :style="{ background: sceneColors[i % sceneColors.length] + '22', color: sceneColors[i % sceneColors.length] }">
                {{ sceneEmojis[i % sceneEmojis.length] }}
              </div>
              <span>{{ s }}</span>
            </div>
          </div>
        </div>
        <div class="card strategy-card">
          <div class="section-title"><div class="icon"></div>目标人群</div>
          <div class="strategy-items">
            <div class="strategy-item" v-for="(p, i) in data.recommended_personas" :key="p">
              <div class="si-icon" :style="{ background: '#3498DB22', color: '#3498DB' }">👤</div>
              <span>{{ p }}</span>
            </div>
          </div>
        </div>
        <div class="card strategy-card">
          <div class="section-title"><div class="icon"></div>内容方向</div>
          <div class="strategy-items">
            <div class="strategy-item" v-for="(c, i) in data.recommended_content_direction" :key="c">
              <div class="si-icon" :style="{ background: '#27AE6022', color: '#27AE60' }">✍️</div>
              <span>{{ c }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 平台策略 -->
      <div class="section-block">
        <div class="section-title"><div class="icon"></div>平台投放策略</div>
        <div class="platform-strategy-grid">
          <div class="ps-card card" v-for="ps in data.platform_strategy" :key="ps.platform">
            <div class="ps-header">
              <span class="ps-rank">P{{ ps.priority }}</span>
              <span class="ps-platform">{{ ps.platform }}</span>
            </div>
            <p class="ps-strategy">{{ ps.strategy }}</p>
            <el-tag type="success" size="small" effect="plain">{{ ps.expected_reach }}</el-tag>
          </div>
        </div>
      </div>

      <!-- 推荐图表：商品匹配度 + 场景分布 -->
      <div class="charts-row">
        <div class="card chart-card">
          <div class="section-title"><div class="icon"></div>推荐商品匹配度对比</div>
          <v-chart :option="matchBarOption" style="height:240px" autoresize />
        </div>
        <div class="card chart-card">
          <div class="section-title"><div class="icon"></div>推荐场景分布</div>
          <v-chart :option="scenePieOption" style="height:240px" autoresize />
        </div>
      </div>

      <!-- ROI样板案例 -->
      <div class="roi-banner card">
        <div class="roi-icon">💰</div>
        <div class="roi-content">
          <div class="roi-title">样板案例推演</div>
          <div class="roi-text">{{ data.roi_estimate?.note }}</div>
          <div class="roi-note">{{ data.roi_estimate?.description }}</div>
        </div>
        <el-button type="danger" @click="$router.push('/content')">生成种草内容 →</el-button>
      </div>

      <!-- 决策总结 -->
      <div class="summary-card card">
        <div class="section-title"><div class="icon"></div>决策总结</div>
        <p class="summary-text">{{ data.decision_summary }}</p>
      </div>

      <div class="data-notice">{{ data.data_notice }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { InfoFilled } from '@element-plus/icons-vue'

const loading = ref(false)
const data = ref({
  recommended_products: [
    { product_name: 'DEAR SEED 玫瑰护手霜', match_score: 92, reason: '同香型、同场景、适合组合购买', scenario: '宿舍日常', price_band: '100-150元' },
    { product_name: '玫瑰香氛喷雾（示意）', match_score: 85, reason: '增强情绪价值表达', scenario: '宿舍日常、日常复购', price_band: '50-100元' },
    { product_name: '校园洗护礼盒套装（示意）', match_score: 78, reason: '适合开学季与社群拼团', scenario: '开学季、节日送礼', price_band: '100-150元' },
  ],
  recommended_scenes: ['宿舍日常', '开学季采购', '节日送礼', '日常复购'],
  recommended_personas: ['学生党', '价格敏感型用户', '年轻女性用户'],
  recommended_content_direction: ['高性价比修护洗发', '修护柔顺使用体验', '玫瑰香氛氛围种草'],
  platform_strategy: [
    { platform: '小红书', priority: 1, strategy: '图文种草+真实测评，优先腰部博主', expected_reach: '精准触达学生党' },
    { platform: '社群私域', priority: 2, strategy: '拼团活动+开学季限时优惠', expected_reach: '高转化率' },
    { platform: '视频号', priority: 3, strategy: '15-30s短视频，宿舍场景真实拍摄', expected_reach: '扩大品牌曝光' },
  ],
  roi_estimate: {
    description: '基于样板案例模拟推演',
    note: '提前15天规划推广策略，精准投放腰部博主，30天笔记量预计破2万，ROI提升约300%',
  },
  decision_summary: '优先围绕宿舍场景与学生党做种草表达，用高性价比修护体验打动用户，再通过同系列商品搭配提升转化率和复购率。',
  data_notice: '当前为公开样本数据与模拟验证结果。',
})

const matchColors = ['#E74C3C', '#E8834A', '#3498DB']
const sceneColors = ['#E74C3C', '#E8834A', '#27AE60', '#9B59B6']
const sceneEmojis = ['🏠', '📚', '🎁', '🔄']

const matchBarOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 20, right: 20, bottom: 20, top: 10, containLabel: true },
  xAxis: { type: 'category', data: data.value.recommended_products.map(p => p.product_name.slice(0, 10) + '...') },
  yAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' } },
  series: [{
    type: 'bar', barWidth: '50%',
    data: data.value.recommended_products.map((p, i) => ({
      value: p.match_score,
      itemStyle: { color: matchColors[i], borderRadius: [6, 6, 0, 0] },
    })),
    label: { show: true, position: 'top', formatter: '{c}%', fontWeight: 'bold' },
  }],
}))

const scenePieOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c}' },
  legend: { bottom: 0, textStyle: { fontSize: 11 } },
  color: sceneColors,
  series: [{
    type: 'pie', radius: ['35%', '62%'],
    label: { show: true, formatter: '{b}\n{d}%', fontSize: 11 },
    data: [
      { name: '宿舍日常', value: 46 }, { name: '开学季', value: 32 },
      { name: '日常复购', value: 22 }, { name: '节日送礼', value: 10 },
    ],
  }],
}))

onMounted(async () => {
  loading.value = true
  try {
    const res = await axios.post('/api/recommend', {
      selling_points: ['修护', '柔顺', '玫瑰香氛'],
      target_user: '学生党女性用户',
      potential_score: 8.2,
    })
    if (res.data.code === 0) data.value = { ...data.value, ...res.data.data }
  } catch (e) { /* keep defaults */ } finally { loading.value = false }
})
</script>

<style scoped>
.recommend-page { display: flex; flex-direction: column; gap: 24px; }
.page-title { font-size: 28px; font-weight: 800; color: #2c3e50; }
.page-desc { font-size: 14px; color: #888; margin-top: 6px; }
.recommend-layout { display: flex; flex-direction: column; gap: 24px; }
.product-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.rec-product-card { padding: 24px; display: flex; flex-direction: column; align-items: center; gap: 12px; text-align: center; position: relative; }
.rec-rank { position: absolute; top: 14px; left: 14px; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 800; color: #fff; }
.rank-1 { background: linear-gradient(135deg, #E74C3C, #C0392B); }
.rank-2 { background: linear-gradient(135deg, #E8834A, #D35400); }
.rank-3 { background: linear-gradient(135deg, #3498DB, #2980B9); }
.rec-product-name { font-size: 16px; font-weight: 700; color: #2c3e50; margin-top: 8px; }
.match-score-wrap { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.match-label { font-size: 12px; color: #888; }
.rec-reason { font-size: 13px; color: #555; display: flex; align-items: center; gap: 6px; }
.rec-meta { display: flex; gap: 8px; }
.strategy-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.strategy-card { }
.strategy-items { display: flex; flex-direction: column; gap: 12px; }
.strategy-item { display: flex; align-items: center; gap: 10px; font-size: 14px; color: #2c3e50; }
.si-icon { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }
.platform-strategy-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.ps-card { }
.ps-header { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.ps-rank { background: #2c3e50; color: #fff; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 800; }
.ps-platform { font-size: 16px; font-weight: 700; }
.ps-strategy { font-size: 13px; color: #555; margin-bottom: 10px; line-height: 1.6; }
.charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.chart-card { }
.roi-banner { display: flex; align-items: center; gap: 20px; background: linear-gradient(135deg, #1a1a2e, #16213e); color: #fff; }
.roi-icon { font-size: 48px; flex-shrink: 0; }
.roi-content { flex: 1; }
.roi-title { font-size: 16px; font-weight: 700; margin-bottom: 6px; }
.roi-text { font-size: 14px; color: rgba(255,255,255,0.85); line-height: 1.6; }
.roi-note { font-size: 11px; color: rgba(255,255,255,0.5); margin-top: 4px; }
.summary-card { }
.summary-text { font-size: 15px; color: #444; line-height: 1.8; }
</style>
