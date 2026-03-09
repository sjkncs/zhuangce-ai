<template>
  <div id="app-wrapper">
    <NavBar />
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <footer class="app-footer">
      <span>妆策AI · 校赛MVP版本 · 数据说明：当前结果基于公开样本与模拟验证逻辑生成</span>
    </footer>
  </div>
</template>

<script setup>
import NavBar from './components/NavBar.vue'
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
  background: #f5f6fa;
  color: #2c3e50;
  min-height: 100vh;
}
#app-wrapper { display: flex; flex-direction: column; min-height: 100vh; }
.main-content { flex: 1; padding: 24px 32px; max-width: 1400px; margin: 0 auto; width: 100%; }
.app-footer {
  background: #2c3e50;
  color: rgba(255,255,255,0.6);
  text-align: center;
  padding: 12px 24px;
  font-size: 12px;
}
.fade-enter-active, .fade-leave-active { transition: opacity 0.25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* Global card styles */
.card { background: #fff; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); padding: 24px; }
.section-title { font-size: 18px; font-weight: 700; color: #2c3e50; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
.section-title .icon { width: 4px; height: 20px; background: linear-gradient(135deg, #E74C3C, #C0392B); border-radius: 2px; }
.data-notice { font-size: 11px; color: #aaa; margin-top: 16px; padding: 8px 12px; background: #f9f9f9; border-radius: 6px; border-left: 3px solid #ddd; }
.score-badge { display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px; border-radius: 50%; font-size: 22px; font-weight: 800; color: #fff; background: linear-gradient(135deg, #E74C3C, #C0392B); box-shadow: 0 4px 16px rgba(231,76,60,0.35); }
.tag-list { display: flex; flex-wrap: wrap; gap: 8px; }
.tag-item { padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 500; }
</style>
