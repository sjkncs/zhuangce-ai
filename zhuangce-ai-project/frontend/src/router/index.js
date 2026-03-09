import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import PredictView from '../views/PredictView.vue'
import RecommendView from '../views/RecommendView.vue'
import ContentView from '../views/ContentView.vue'
import DashboardView from '../views/DashboardView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView, meta: { title: '首页 — 妆策AI' } },
  { path: '/predict', name: 'predict', component: PredictView, meta: { title: '爆款预测 — 妆策AI' } },
  { path: '/recommend', name: 'recommend', component: RecommendView, meta: { title: '推荐决策 — 妆策AI' } },
  { path: '/content', name: 'content', component: ContentView, meta: { title: '内容种草 — 妆策AI' } },
  { path: '/dashboard', name: 'dashboard', component: DashboardView, meta: { title: '数据看板 — 妆策AI' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

router.afterEach((to) => {
  document.title = to.meta.title || '妆策AI'
})

export default router
