<template>
  <div class="predict-page">
    <div class="page-header">
      <h2 class="page-title">🔮 爆款预测引擎</h2>
      <p class="page-desc">输入产品卖点、价格区间与目标人群，系统基于样本数据与标签逻辑输出传播潜力判断</p>
    </div>

    <div class="predict-layout">
      <!-- 左侧：输入表单 -->
      <div class="input-panel card">
        <div class="section-title"><div class="icon"></div>产品信息输入</div>
        <el-form :model="form" label-position="top" class="predict-form">
          <el-form-item label="产品名称">
            <el-input v-model="form.product_name" placeholder="如：DEAR SEED 玫瑰修护洗发水" />
          </el-form-item>
          <el-form-item label="一级品类">
            <el-select v-model="form.primary_category" style="width:100%">
              <el-option v-for="c in primaryCats" :key="c" :label="c" :value="c" />
            </el-select>
          </el-form-item>
          <el-form-item label="二级子类">
            <el-input v-model="form.secondary_category" placeholder="如：修护洗发" />
          </el-form-item>
          <el-form-item label="核心卖点（可多选）">
            <el-select v-model="form.selling_points" multiple style="width:100%"
              placeholder="选择或输入卖点标签" allow-create filterable>
              <el-option v-for="sp in sellingPointOptions" :key="sp" :label="sp" :value="sp" />
            </el-select>
          </el-form-item>
          <el-form-item label="价格区间">
            <el-select v-model="form.price_range" style="width:100%">
              <el-option v-for="p in priceOptions" :key="p" :label="p" :value="p" />
            </el-select>
          </el-form-item>
          <el-form-item label="目标人群">
            <el-input v-model="form.target_user" placeholder="如：学生党女性用户" />
          </el-form-item>
          <el-form-item label="目标平台">
            <el-radio-group v-model="form.platform">
              <el-radio-button v-for="p in platforms" :key="p" :label="p" />
            </el-radio-group>
          </el-form-item>
          <div class="form-actions">
            <el-button type="danger" size="large" :loading="loading" @click="doPrediction" style="width:100%">
              🚀 开始预测
            </el-button>
            <el-button size="default" @click="resetToDefault" style="width:100%;margin-top:8px">
              重置为样板数据
            </el-button>
          </div>
        </el-form>
      </div>

      <!-- 右侧：输出结果 -->
      <div class="result-panel">
        <el-skeleton :loading="loading" animated :rows="8">
          <template #default>
            <div v-if="result" class="result-content">
              <!-- 传播潜力评分 -->
              <div class="card score-card">
                <div class="score-header">
                  <div>
                    <div class="section-title"><div class="icon"></div>传播潜力评分</div>
                    <p class="score-explanation">{{ result.score_explanation }}</p>
                  </div>
                  <div class="big-score">
                    <div class="big-score-number">{{ result.potential_score }}</div>
                    <div class="big-score-label">/ 10</div>
                  </div>
                </div>
                <div class="factor-bars">
                  <div class="factor-item" v-for="(val, key) in result.factors" :key="key">
                    <span class="factor-label">{{ factorLabels[key] || key }}</span>
                    <el-progress :percentage="val * 10" :stroke-width="10"
                      :color="factorColors[key] || '#3498DB'" :format="() => val.toFixed(1)" />
                  </div>
                </div>
                <v-chart :option="radarOption" style="height:220px;margin-top:12px" autoresize />
              </div>

              <!-- 高潜人群 + 推广时间 -->
              <div class="two-col-grid" style="margin-top:16px">
                <div class="card">
                  <div class="section-title"><div class="icon"></div>高潜人群画像</div>
                  <div class="tag-list">
                    <el-tag v-for="p in result.target_persona" :key="p"
                      type="danger" effect="plain" size="large" class="tag-item">👤 {{ p }}</el-tag>
                  </div>
                  <div style="margin-top:16px">
                    <div class="section-title" style="font-size:14px"><div class="icon"></div>关键影响标签</div>
                    <div class="tag-list" style="margin-top:8px">
                      <el-tag v-for="t in result.key_tags" :key="t"
                        effect="light" class="tag-item">{{ t }}</el-tag>
                    </div>
                  </div>
                </div>
                <div class="card">
                  <div class="section-title"><div class="icon"></div>最佳推广时间</div>
                  <div class="time-windows">
                    <div class="time-window" v-for="tw in result.best_time_windows" :key="tw.window">
                      <div class="tw-header">
                        <el-tag :type="tw.confidence === '高' ? 'danger' : 'warning'" size="small">
                          {{ tw.confidence }}置信度
                        </el-tag>
                        <span class="tw-window">{{ tw.window }}</span>
                      </div>
                      <p class="tw-reason">{{ tw.reason }}</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 风险提示 -->
              <div class="card" style="margin-top:16px">
                <div class="section-title"><div class="icon"></div>⚠️ 风险提示</div>
                <div class="risk-list">
                  <div class="risk-item" v-for="(r, i) in result.risk_alert" :key="i">
                    <el-icon color="#E8834A"><Warning /></el-icon>
                    <span>{{ r }}</span>
                  </div>
                </div>
              </div>

              <!-- CTA -->
              <div class="cta-row">
                <el-button type="warning" @click="$router.push('/recommend')">查看推荐决策 →</el-button>
                <el-button type="primary" @click="$router.push('/content')">生成内容种草 →</el-button>
              </div>

              <div class="data-notice">{{ result.data_notice }}</div>
            </div>
            <div v-else class="empty-state">
              <el-icon size="64" color="#ddd"><TrendCharts /></el-icon>
              <p>填写左侧表单，点击「开始预测」查看传播潜力分析</p>
            </div>
          </template>
        </el-skeleton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import { Warning, TrendCharts } from '@element-plus/icons-vue'

const loading = ref(false)
const result = ref(null)

const defaultForm = {
  product_name: 'DEAR SEED 玫瑰修护洗发水',
  primary_category: '洗护',
  secondary_category: '修护洗发',
  selling_points: ['修护', '柔顺', '玫瑰香氛'],
  price_range: '100-150元',
  target_user: '学生党女性用户',
  platform: '小红书',
}
const form = ref({ ...defaultForm })

const primaryCats = ['洗护', '护肤品', '化妆品']
const sellingPointOptions = ['修护', '柔顺', '留香', '控油', '蓬松', '去屑', '滋养', '温和', '玫瑰香氛', '高性价比']
const priceOptions = ['0-50元', '50-100元', '100-150元', '150-200元', '200-300元', '300-500元', '500元+']
const platforms = ['小红书', '抖音', '微博', '视频号', 'B站']

const factorLabels = { efficacy_score: '卖点匹配度', persona_score: '人群匹配度', scene_score: '场景适配性', price_score: '价格带竞争力' }
const factorColors = { efficacy_score: '#E74C3C', persona_score: '#3498DB', scene_score: '#27AE60', price_score: '#9B59B6' }

const radarOption = computed(() => {
  if (!result.value?.factors) return {}
  const f = result.value.factors
  return {
    radar: {
      indicator: [
        { name: '卖点匹配', max: 10 }, { name: '人群匹配', max: 10 },
        { name: '场景适配', max: 10 }, { name: '价格竞争', max: 10 },
        { name: '综合潜力', max: 10 },
      ],
      splitArea: { areaStyle: { color: ['rgba(231,76,60,0.04)', 'rgba(231,76,60,0.02)', '#fff'] } },
    },
    series: [{
      type: 'radar',
      data: [{
        value: [f.efficacy_score, f.persona_score, f.scene_score, f.price_score, result.value.potential_score],
        name: '传播潜力雷达',
        areaStyle: { color: 'rgba(231,76,60,0.15)' },
        lineStyle: { color: '#E74C3C', width: 2 },
        itemStyle: { color: '#E74C3C' },
      }],
    }],
  }
})

const resetToDefault = () => { form.value = { ...defaultForm } }

const doPrediction = async () => {
  loading.value = true
  try {
    const res = await axios.post('/api/predict', {
      product_name: form.value.product_name,
      primary_category: form.value.primary_category,
      secondary_category: form.value.secondary_category,
      selling_points: form.value.selling_points,
      price_range: form.value.price_range,
      target_user: form.value.target_user,
      platform: form.value.platform,
    })
    if (res.data.code === 0) result.value = res.data.data
  } catch (e) {
    result.value = {
      potential_score: 8.2,
      score_explanation: '卖点组合与平台热点标签匹配度较高，具备较强内容传播潜力。',
      factors: { efficacy_score: 9.0, persona_score: 8.5, scene_score: 8.8, price_score: 8.1 },
      target_persona: ['学生党女性用户', '宿舍场景用户', '价格敏感型用户'],
      best_time: '开学季（8月20日 - 9月10日）',
      best_time_windows: [
        { window: '开学季（8月20日 - 9月10日）', reason: '学生党采购宿舍洗护需求增加，内容互动频率高', confidence: '高' },
        { window: '换季期（3月、9-10月）', reason: '气候变化导致修护洗护内容热度上升', confidence: '高' },
      ],
      risk_alert: ['避免只讲科研背书，需强化性价比与日常体验表达', '对价格敏感型用户建议突出学生可接受价格带'],
      key_tags: ['修护', '柔顺', '留香', '宿舍日常', '开学季'],
      data_notice: '当前结果基于公开样本数据与模拟验证逻辑生成，不等同于真实投放结果。',
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.predict-page { display: flex; flex-direction: column; gap: 20px; }
.page-header { }
.page-title { font-size: 28px; font-weight: 800; color: #2c3e50; }
.page-desc { font-size: 14px; color: #888; margin-top: 6px; }
.predict-layout { display: grid; grid-template-columns: 360px 1fr; gap: 24px; align-items: start; }
.input-panel { }
.predict-form :deep(.el-form-item__label) { font-weight: 600; color: #2c3e50; }
.form-actions { margin-top: 8px; }
.result-panel { min-height: 400px; }
.score-card { }
.score-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 20px; }
.score-explanation { font-size: 13px; color: #666; margin-top: 6px; line-height: 1.6; max-width: 400px; }
.big-score { display: flex; align-items: baseline; gap: 4px; }
.big-score-number { font-size: 64px; font-weight: 900; color: #E74C3C; line-height: 1; }
.big-score-label { font-size: 18px; color: #aaa; }
.factor-bars { display: flex; flex-direction: column; gap: 10px; }
.factor-item { display: flex; align-items: center; gap: 12px; }
.factor-label { min-width: 90px; font-size: 13px; color: #555; font-weight: 600; }
.two-col-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.time-windows { display: flex; flex-direction: column; gap: 12px; }
.time-window { background: #f9f9f9; border-radius: 8px; padding: 12px; }
.tw-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.tw-window { font-size: 13px; font-weight: 700; color: #2c3e50; }
.tw-reason { font-size: 12px; color: #666; line-height: 1.5; }
.risk-list { display: flex; flex-direction: column; gap: 10px; }
.risk-item { display: flex; align-items: flex-start; gap: 8px; font-size: 13px; color: #555; line-height: 1.6; }
.cta-row { display: flex; gap: 12px; margin-top: 16px; }
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center;
  height: 400px; color: #bbb; gap: 16px; font-size: 14px; }
</style>
