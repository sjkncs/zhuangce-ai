# 妆策AI｜接口说明书（校赛 MVP 版）

## 1. 文档目的
本说明书用于前端、后端、算法三方统一接口命名、请求参数、响应结构与页面对接方式。

## 2. 接口设计原则
1. 校赛阶段优先保证演示稳定，接口以静态 JSON / mock 数据优先。
2. 所有接口统一返回 `code`、`message`、`data`。
3. 所有结果页保留“数据说明”和“阶段说明”。
4. 当前结果属于公开样本 + 模拟验证，不冒充真实企业投放结果。

## 3. 通用返回格式
```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

## 4. 接口清单

| 接口名称 | Method | 路径 | 用途 |
|---|---|---|---|
| 首页总览 | GET | `/api/home/overview` | 首页展示项目概览、样板产品、核心数据卡 |
| 爆款预测 | POST | `/api/predict` | 输入产品信息，输出传播潜力与人群建议 |
| 推荐决策 | POST | `/api/recommend` | 输出推荐商品、推荐场景、平台优先级 |
| 内容生成 | POST | `/api/content/generate` | 输出标题、话术、短视频开场 |
| 数据看板 | GET | `/api/dashboard` | 输出趋势、分布、结论 |

## 5. 各接口说明

### 5.1 首页总览
- **Method:** GET
- **Path:** `/api/home/overview`
- **说明:** 页面初始化时调用一次。
- **前端用途:** 渲染首页标题、样板产品卡、核心评分卡。

### 5.2 爆款预测
- **Method:** POST
- **Path:** `/api/predict`
- **请求参数:**
  - `product_name`
  - `primary_category`
  - `secondary_category`
  - `selling_points`
  - `price_range`
  - `target_user`
  - `platform`
- **前端用途:** 用户点击“开始预测”后返回预测结果。
- **后端建议:** 校赛阶段可直接从静态样例表读取。

### 5.3 推荐决策
- **Method:** POST
- **Path:** `/api/recommend`
- **请求参数:**
  - 可直接复用 `/api/predict` 的请求参数
  - 或增加 `potential_score` 作为上游结果输入
- **前端用途:** 生成推荐商品列表、推荐内容方向。
- **后端建议:** 先做规则引擎版，后续再升级协同过滤或排序模型。

### 5.4 内容生成
- **Method:** POST
- **Path:** `/api/content/generate`
- **请求参数:**
  - `product_name`
  - `selling_points`
  - `target_user`
  - `scenes`
  - `tone_style`
- **前端用途:** 展示标题文案、社群文案、视频开场。
- **后端建议:** 校赛阶段可写死模板生成逻辑。

### 5.5 数据看板
- **Method:** GET
- **Path:** `/api/dashboard`
- **前端用途:** 驱动 ECharts 图表与结论卡片。
- **后端建议:** 使用 mock JSON 即可完成演示。

## 6. 错误码建议

| code | 含义 | 说明 |
|---|---|---|
| 0 | success | 请求成功 |
| 4001 | invalid_param | 参数缺失或格式错误 |
| 4004 | not_found | 未找到对应样板数据 |
| 5000 | internal_error | 服务内部错误 |

## 7. 前后端联调建议
1. 先让前端完全按 mock JSON 开发页面。
2. 后端先把 5 个接口跑通，即使数据是静态的也没问题。
3. 校赛版以“稳定演示”优先，不追求复杂后端架构。
4. 如时间不够，可把 `/api/predict`、`/api/recommend`、`/api/content/generate` 都先写成固定返回。

## 8. 最低可运行方案
- 前端：Vue + ECharts
- 后端：Flask / FastAPI 任一
- 数据：本地 JSON 文件
- 演示策略：输入固定样板产品，输出固定但看起来完整的一组结果

## 9. 结论
对于校赛 MVP，接口的核心目标不是做复杂，而是：
**能跑、能演示、能解释、能答辩。**
