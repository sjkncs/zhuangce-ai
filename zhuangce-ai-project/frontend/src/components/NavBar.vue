<template>
  <nav class="navbar">
    <div class="navbar-inner">
      <router-link to="/" class="brand">
        <span class="brand-icon">💄</span>
        <span class="brand-name">妆策AI</span>
        <span class="brand-tag">校赛MVP</span>
      </router-link>
      <ul class="nav-links">
        <li v-for="item in navItems" :key="item.path">
          <router-link :to="item.path" class="nav-link" :class="{ active: $route.path === item.path }">
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ item.label }}</span>
          </router-link>
        </li>
      </ul>
      <div class="navbar-right">
        <el-tag type="warning" size="small" effect="dark">DEAR SEED 样板案例</el-tag>
      </div>
    </div>
  </nav>
</template>

<script setup>
const navItems = [
  { path: '/', label: '首页', icon: 'House' },
  { path: '/predict', label: '爆款预测', icon: 'TrendCharts' },
  { path: '/recommend', label: '推荐决策', icon: 'Star' },
  { path: '/content', label: '内容种草', icon: 'Edit' },
  { path: '/dashboard', label: '数据看板', icon: 'DataAnalysis' },
]
</script>

<style scoped>
.navbar {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  box-shadow: 0 2px 20px rgba(0,0,0,0.2);
  position: sticky; top: 0; z-index: 1000;
}
.navbar-inner {
  max-width: 1400px; margin: 0 auto;
  display: flex; align-items: center; gap: 32px;
  padding: 0 32px; height: 60px;
}
.brand {
  display: flex; align-items: center; gap: 10px;
  text-decoration: none; white-space: nowrap;
}
.brand-icon { font-size: 22px; }
.brand-name { font-size: 20px; font-weight: 800; color: #fff; letter-spacing: 1px; }
.brand-tag {
  font-size: 11px; padding: 2px 8px; border-radius: 10px;
  background: rgba(231,76,60,0.8); color: #fff; font-weight: 600;
}
.nav-links { display: flex; gap: 4px; list-style: none; flex: 1; }
.nav-link {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 16px; border-radius: 8px;
  text-decoration: none; color: rgba(255,255,255,0.75);
  font-size: 14px; font-weight: 500;
  transition: all 0.2s;
}
.nav-link:hover { background: rgba(255,255,255,0.1); color: #fff; }
.nav-link.active { background: rgba(231,76,60,0.85); color: #fff; }
.navbar-right { margin-left: auto; }
</style>
