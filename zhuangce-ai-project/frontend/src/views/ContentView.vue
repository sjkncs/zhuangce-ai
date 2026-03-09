<template>
  <div class="content-page">
    <div class="page-header">
      <h2 class="page-title">✍️ 内容种草生成器</h2>
      <p class="page-desc">把预测与推荐结果转化为可执行的种草内容——标题、社群话术、视频开场一键生成</p>
    </div>

    <div class="content-layout" v-loading="loading">
      <!-- 输入配置区 -->
      <div class="config-bar card">
        <div class="config-fields">
          <div class="config-field">
            <label>产品</label>
            <el-input v-model="config.product_name" size="small" style="width:220px" />
          </div>
          <div class="config-field">
            <label>核心卖点</label>
            <el-select v-model="config.selling_points" multiple size="small" style="width:260px">
              <el-option v-for="sp in spOptions" :key="sp" :label="sp" :value="sp" />
            </el-select>
          </div>
          <div class="config-field">
            <label>目标人群</label>
            <el-input v-model="config.target_user" size="small" style="width:160px" />
          </div>
          <div class="config-field">
            <label>调性风格</label>
            <el-select v-model="config.tone_style" size="small" style="width:180px">
              <el-option v-for="t in toneOptions" :key="t" :label="t" :value="t" />
            </el-select>
          </div>
        </div>
        <el-button type="danger" :loading="loading" @click="generateContent">🎨 重新生成</el-button>
      </div>

      <!-- 内容展示区 -->
      <div class="content-grid">
        <!-- 小红书标题 -->
        <div class="card content-block">
          <div class="content-block-header">
            <div class="section-title"><div class="icon"></div>小红书标题</div>
            <el-tag type="danger" size="small">{{ data.xiaohongshu_titles?.length || 0 }}条</el-tag>
          </div>
          <div class="title-list">
            <div class="title-item" v-for="(t, i) in data.xiaohongshu_titles" :key="i">
              <div class="title-num">{{ i + 1 }}</div>
              <div class="title-text">{{ t }}</div>
              <el-button link type="primary" size="small" @click="copyText(t)">复制</el-button>
            </div>
          </div>
        </div>

        <!-- 小红书完整文案 -->
        <div class="card content-block">
          <div class="content-block-header">
            <div class="section-title"><div class="icon"></div>小红书完整文案</div>
            <el-tag type="warning" size="small">可直接发布</el-tag>
          </div>
          <div class="full-copy-list">
            <div class="full-copy-item" v-for="(item, i) in data.xiaohongshu_full" :key="i">
              <div class="fc-title">📌 {{ item.title }}</div>
              <div class="fc-body">{{ item.body }}</div>
              <div class="fc-tags">
                <el-tag v-for="tag in item.tags" :key="tag" size="small" effect="plain" type="info"
                  style="margin:2px">#{{ tag }}</el-tag>
              </div>
              <el-button link type="primary" size="small" @click="copyText(item.title + '\n\n' + item.body)">
                复制全文
              </el-button>
            </div>
          </div>
        </div>

        <!-- 社群话术 -->
        <div class="card content-block">
          <div class="content-block-header">
            <div class="section-title"><div class="icon"></div>社群推荐话术</div>
            <el-tag type="success" size="small">{{ data.community_scripts?.length || 0 }}条</el-tag>
          </div>
          <div class="script-list">
            <div class="script-item" v-for="(s, i) in data.community_scripts" :key="i">
              <div class="script-icon">💬</div>
              <div class="script-text">{{ s }}</div>
              <el-button link type="primary" size="small" @click="copyText(s)">复制</el-button>
            </div>
          </div>
        </div>

        <!-- 短视频开场 -->
        <div class="card content-block">
          <div class="content-block-header">
            <div class="section-title"><div class="icon"></div>短视频开场钩子</div>
            <el-tag size="small">{{ data.video_hooks?.length || 0 }}条</el-tag>
          </div>
          <div class="hook-list">
            <div class="hook-item" v-for="(h, i) in data.video_hooks" :key="i">
              <div class="hook-num">🎬</div>
              <div class="hook-text">{{ h }}</div>
              <el-button link type="primary" size="small" @click="copyText(h)">复制</el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 内容策略总结 -->
      <div class="strategy-summary card">
        <div class="section-title"><div class="icon"></div>内容策略总结</div>
        <div class="strategy-grid-2">
          <div class="ss-item">
            <div class="ss-label">内容调性</div>
            <div class="ss-value">{{ data.tone_style }}</div>
          </div>
          <div class="ss-item">
            <div class="ss-label">推荐卖点表达</div>
            <div class="ss-value">{{ data.selling_point_expression }}</div>
          </div>
          <div class="ss-item">
            <div class="ss-label">推荐场景表达</div>
            <div class="ss-value">{{ data.scenario_expression }}</div>
          </div>
          <div class="ss-item" v-if="data.content_strategy">
            <div class="ss-label">核心角度</div>
            <div class="ss-value">{{ data.content_strategy.primary_angle }}</div>
          </div>
        </div>
        <div class="avoid-tips" v-if="data.content_strategy">
          <div class="avoid-label">⚠️ 避免表达：</div>
          <span class="avoid-text">{{ data.content_strategy.avoid }}</span>
        </div>
        <div class="content-tips" v-if="data.content_strategy?.tips">
          <div class="ss-label" style="margin-bottom:8px">💡 创作建议：</div>
          <ul>
            <li v-for="tip in data.content_strategy.tips" :key="tip">{{ tip }}</li>
          </ul>
        </div>
      </div>

      <!-- 30条样板文案展示（来自第七批文档） -->
      <div class="card sample-30">
        <div class="content-block-header">
          <div class="section-title"><div class="icon"></div>样板种草文案库（30条参考）</div>
          <el-tag type="info" size="small">来自第七批文档归档</el-tag>
        </div>
        <el-tabs v-model="activeTab">
          <el-tab-pane label="小红书标题(10条)" name="xhs">
            <div class="sample-list">
              <div class="sample-item" v-for="(s, i) in sampleContent.xhsTitles" :key="i">
                <span class="si-num">{{ i + 1 }}</span>
                <span class="si-text">{{ s }}</span>
                <el-button link type="primary" size="small" @click="copyText(s)">复制</el-button>
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="短文案(8条)" name="short">
            <div class="sample-list">
              <div class="sample-item" v-for="(s, i) in sampleContent.shortCopy" :key="i">
                <span class="si-num">{{ i + 1 }}</span>
                <span class="si-text">{{ s }}</span>
                <el-button link type="primary" size="small" @click="copyText(s)">复制</el-button>
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="社群话术(6条)" name="community">
            <div class="sample-list">
              <div class="sample-item" v-for="(s, i) in sampleContent.community" :key="i">
                <span class="si-num">{{ i + 1 }}</span>
                <span class="si-text">{{ s }}</span>
                <el-button link type="primary" size="small" @click="copyText(s)">复制</el-button>
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="视频开场(6条)" name="video">
            <div class="sample-list">
              <div class="sample-item" v-for="(s, i) in sampleContent.videoHooks" :key="i">
                <span class="si-num">{{ i + 1 }}</span>
                <span class="si-text">{{ s }}</span>
                <el-button link type="primary" size="small" @click="copyText(s)">复制</el-button>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <div class="data-notice">{{ data.data_notice }}</div>
    </div>

    <el-message ref="msgRef" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const activeTab = ref('xhs')
const config = ref({
  product_name: 'DEAR SEED 玫瑰修护洗发水',
  selling_points: ['修护', '柔顺', '玫瑰香氛'],
  target_user: '学生党女性用户',
  scenes: ['宿舍日常', '开学季'],
  tone_style: '真实分享 + 高性价比种草',
})
const spOptions = ['修护', '柔顺', '留香', '控油', '蓬松', '去屑', '玫瑰香氛', '高性价比', '温和']
const toneOptions = ['真实分享 + 高性价比种草', '情绪种草 + 氛围感', '专业测评 + 成分解析', '口语化 + 亲切日常']

const data = ref({
  xiaohongshu_titles: [
    '学生党闭眼冲！这瓶玫瑰修护洗发水真的很懂宿舍女孩',
    '开学季宿舍洗护怎么选？这瓶修护香氛型我会回购',
    '修护、柔顺、还好闻：学生党也能负担的宿舍洗护选择',
    '不想踩雷的学生党，洗发水先看这瓶修护柔顺型',
    '学生党宿舍必备洗护，顺滑和香味终于都有了',
  ],
  xiaohongshu_full: [
    {
      title: '学生党闭眼冲！这瓶玫瑰修护洗发水真的很懂宿舍女孩',
      body: '最近在找一瓶适合宿舍日常用的洗发水，修护和柔顺都兼顾，香味还不能太俗，这瓶玫瑰修护路线整体感受不错。如果你和我一样头发有点毛躁，又不想买太贵的洗护，100-150元这个价格段真的很值得重点看。',
      tags: ['修护洗发水', '宿舍好物', '学生党种草', '玫瑰香氛', '开学季必备'],
    },
    {
      title: '修护、柔顺、还好闻：学生党也能负担的宿舍洗护选择',
      body: '对学生党来说，洗发水不是越贵越好，而是要顺、要稳、要好闻、要不踩雷，这也是这类产品最值得被推荐的原因。这种带一点香氛感的修护洗发水，最怕香味过头，但这瓶表达方向更偏清新和治愈。',
      tags: ['平价洗护', '学生党', '修护柔顺', '宿舍日常'],
    },
  ],
  community_scripts: [
    '姐妹们，开学季宿舍洗护如果还没想好，可以优先看修护柔顺路线，价格友好的那种。',
    '如果你们最近头发有点毛躁，又不想花太多预算，玫瑰修护这个方向挺适合学生党。',
    '我觉得宿舍场景选洗发水最重要的是三点：顺、好闻、别踩雷，这类修护柔顺型基本就围绕这三点展开。',
  ],
  video_hooks: [
    '如果你是学生党，开学回宿舍只想带一瓶真正好用又不踩雷的洗发水，那这个修护柔顺路线你真的可以看看。',
    '今天不讲太复杂的成分，我们只聊一件事：什么样的洗发水更适合学生党日常用。',
    '为什么有些洗发水看起来都差不多，但就是有的更容易被学生党买单？关键在场景和表达。',
  ],
  tone_style: '真实分享 + 高性价比种草',
  selling_point_expression: '修护、柔顺、香味有记忆点',
  scenario_expression: '宿舍、开学季、日常复购',
  content_strategy: {
    primary_angle: '真实使用体验',
    secondary_angle: '高性价比对比',
    avoid: '过度强调科研成分，缺乏生活感',
    tips: [
      '用第一人称分享宿舍使用感受',
      '搭配真实场景图（宿舍桌面、淋浴间）',
      '强调顺滑感和香味留存，而非成分参数',
      '价格表达用「100多块」而非精确数字，更亲切',
    ],
  },
  data_notice: '当前为校赛MVP概念验证版本，文案供参考使用。',
})

const sampleContent = {
  xhsTitles: [
    '学生党闭眼冲！这瓶玫瑰修护洗发水真的很懂宿舍女孩',
    '开学季宿舍洗护怎么选？我最近被这瓶玫瑰修护种草了',
    '100多块的修护洗发水，居然把顺滑和香味都给到我了',
    '发尾毛躁星人看过来，这瓶修护柔顺路线真的很稳',
    '宿舍也能用出高级感？这瓶玫瑰香氛洗发水有点东西',
    '不想踩雷的学生党，洗发水先看这瓶修护柔顺型',
    '修护、柔顺、还好闻，这瓶洗发水真的很适合开学季',
    '如果你想找一瓶日常不出错的洗发水，可以看看这一支',
    '玫瑰香但不腻，修护感在线，这瓶洗发水我愿意回购',
    '学生党预算内的高性价比洗护，我先帮你们试过了',
  ],
  shortCopy: [
    '最近在找一瓶适合宿舍日常用的洗发水，最好是修护和柔顺都兼顾，香味还不能太俗，这瓶玫瑰修护路线给我的整体感受还不错。',
    '如果你和我一样头发有点毛躁，又不想买太贵的洗护，这种100-150元左右、主打修护柔顺的产品其实很值得重点看。',
    '这类带一点香氛感的修护洗发水，最怕香味过头，但这瓶的表达方向更偏清新和治愈，比较适合学生党日常使用。',
    '开学季买洗护用品，我更看重性价比和宿舍场景友好度，这瓶修护柔顺路线的产品就比较符合这个逻辑。',
    '对学生党来说，洗发水不是越贵越好，而是要顺、要稳、要好闻、要不踩雷，这也是这类产品最值得被推荐的原因。',
    '如果品牌后续想推这类产品，「宿舍场景+修护柔顺+玫瑰香氛」会比只讲科研背书更容易打动用户。',
    '我最近越来越觉得，洗护内容如果只讲成分和技术，很难让人立刻心动，反而「顺滑、好闻、适合日常」更有传播力。',
    '对这类产品来说，好用是基础，愿不愿意复购往往取决于气味记忆点和使用场景是否贴近日常生活。',
  ],
  community: [
    '姐妹们，开学季宿舍洗护如果还没想好，可以优先看修护柔顺路线，尤其是这种香味好接受、价格也还友好的产品。',
    '如果你们最近头发有点毛躁，又不想一次性花太多预算，玫瑰修护这种方向其实挺适合学生党。',
    '我觉得宿舍场景选洗发水最重要的是三点：顺、好闻、别踩雷，这类修护柔顺型基本就围绕这三点展开。',
    '这类洗护如果后续做团购，建议优先搭配护手霜或者同香型护理小单品，更容易形成组合购买。',
    '如果你们要做开学季内容，真的可以重点讲「宿舍日常可用」和「高性价比修护感」这两个点。',
    '从种草角度看，这类产品最适合的不是特别硬的广告表达，而是「真实分享+日常体验」路线。',
  ],
  videoHooks: [
    '如果你是学生党，最近又在纠结宿舍洗发水怎么选，那这个修护柔顺路线你可以先收藏。',
    '一瓶适合开学季带回宿舍的洗发水，至少得满足三个条件：顺、好闻、预算别太高。',
    '今天不讲太复杂的成分，我们只聊一件事：什么样的洗发水更适合学生党日常用。',
    '如果你的头发最近有点毛躁，又想找一瓶香味舒服的修护型洗发水，这类产品就很值得看。',
    '为什么有些洗发水看起来都差不多，但就是有的更容易被学生党买单？关键在场景和表达。',
    '今天我想用一个很简单的逻辑，告诉你为什么「修护+柔顺+玫瑰香氛」这个组合更容易火。',
  ],
}

const copyText = (text) => {
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(() => {
    ElMessage.info('请手动复制')
  })
}

const generateContent = async () => {
  loading.value = true
  try {
    const res = await axios.post('/api/content/generate', {
      product_name: config.value.product_name,
      selling_points: config.value.selling_points,
      target_user: config.value.target_user,
      scenes: config.value.scenes,
      tone_style: config.value.tone_style,
    })
    if (res.data.code === 0) data.value = { ...data.value, ...res.data.data }
  } catch (e) {
    ElMessage.warning('使用默认内容演示')
  } finally {
    loading.value = false
  }
}

onMounted(() => { generateContent() })
</script>

<style scoped>
.content-page { display: flex; flex-direction: column; gap: 24px; }
.page-title { font-size: 28px; font-weight: 800; color: #2c3e50; }
.page-desc { font-size: 14px; color: #888; margin-top: 6px; }
.config-bar { display: flex; align-items: center; gap: 20px; flex-wrap: wrap; }
.config-fields { display: flex; gap: 16px; flex-wrap: wrap; flex: 1; }
.config-field { display: flex; align-items: center; gap: 8px; }
.config-field label { font-size: 13px; font-weight: 600; color: #555; white-space: nowrap; }
.content-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.content-block { }
.content-block-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.content-block-header .section-title { margin-bottom: 0; }
.title-list, .script-list, .hook-list { display: flex; flex-direction: column; gap: 10px; }
.title-item, .script-item, .hook-item {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 10px 12px; background: #f9f9f9; border-radius: 8px;
  transition: background 0.2s;
}
.title-item:hover, .script-item:hover, .hook-item:hover { background: #f0f0f0; }
.title-num { min-width: 22px; height: 22px; border-radius: 50%; background: #E74C3C; color: #fff;
  font-size: 11px; font-weight: 800; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.title-text, .script-text, .hook-text { flex: 1; font-size: 13px; color: #2c3e50; line-height: 1.6; }
.script-icon, .hook-num { font-size: 18px; flex-shrink: 0; }
.full-copy-list { display: flex; flex-direction: column; gap: 16px; }
.full-copy-item { padding: 14px; background: #f9f9f9; border-radius: 10px; }
.fc-title { font-size: 14px; font-weight: 700; color: #2c3e50; margin-bottom: 6px; }
.fc-body { font-size: 13px; color: #555; line-height: 1.7; margin-bottom: 8px; }
.fc-tags { margin-bottom: 8px; }
.strategy-summary { }
.strategy-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
.ss-item { padding: 12px; background: #f9f9f9; border-radius: 8px; }
.ss-label { font-size: 12px; color: #888; margin-bottom: 4px; font-weight: 600; }
.ss-value { font-size: 14px; color: #2c3e50; font-weight: 600; }
.avoid-tips { display: flex; align-items: center; gap: 8px; padding: 10px 14px; background: #fff5f5;
  border-radius: 8px; margin-bottom: 12px; border-left: 3px solid #E74C3C; }
.avoid-label { font-size: 13px; font-weight: 700; color: #E74C3C; white-space: nowrap; }
.avoid-text { font-size: 13px; color: #c0392b; }
.content-tips ul { padding-left: 20px; }
.content-tips li { font-size: 13px; color: #555; line-height: 2; }
.sample-30 { }
.sample-list { display: flex; flex-direction: column; gap: 8px; padding: 8px 0; }
.sample-item { display: flex; align-items: flex-start; gap: 10px; padding: 8px 12px;
  border-radius: 6px; transition: background 0.2s; }
.sample-item:hover { background: #f5f5f5; }
.si-num { min-width: 22px; height: 22px; border-radius: 50%; background: #2c3e50; color: #fff;
  font-size: 11px; font-weight: 800; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.si-text { flex: 1; font-size: 13px; color: #444; line-height: 1.6; }
</style>
