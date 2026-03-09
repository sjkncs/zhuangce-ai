import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.js'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import ECharts from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import {
  BarChart, LineChart, PieChart, ScatterChart, HeatmapChart, RadarChart,
} from 'echarts/charts'
import {
  TitleComponent, TooltipComponent, LegendComponent, GridComponent,
  DataZoomComponent, VisualMapComponent, ToolboxComponent,
} from 'echarts/components'

use([
  CanvasRenderer,
  BarChart, LineChart, PieChart, ScatterChart, HeatmapChart, RadarChart,
  TitleComponent, TooltipComponent, LegendComponent, GridComponent,
  DataZoomComponent, VisualMapComponent, ToolboxComponent,
])

const app = createApp(App)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.component('v-chart', ECharts)
app.use(router)
app.use(ElementPlus, { size: 'default', zIndex: 3000 })
app.mount('#app')
