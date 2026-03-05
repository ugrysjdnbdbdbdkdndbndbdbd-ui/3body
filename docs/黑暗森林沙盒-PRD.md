# 黑暗森林沙盒 · 产品需求文档 (PRD)

**Dark Forest Sandbox — Product Requirements Document**

> 在《黑暗森林沙盒-BRD》商业定位下，定义当前能力边界、用户故事与后续扩展，作为开发与验收指引。

---

## 1. 概述

### 1.1 产品目标

- 将**黑暗森林沙盒**建设为 3Body X 的**特色可玩模块**：用户可在「宇宙社会学」规则下观察或参与多文明演化，获得可回溯、可归档、可导出的结果。
- 本 PRD 覆盖：
  - 当前已实现能力（Sector E + Zero v2 B）；
  - 近期可扩展能力与用户故事；
  - 技术边界与接口约定；
  - 非目标与依赖说明。

### 1.2 与 BRD 的对应关系

- BRD 定义「为什么做」「为谁做」「如何变现」；PRD 定义「做什么」「做到什么程度」「如何验收」。

---

## 2. 当前能力总览

### 2.1 双端架构

| 端 | 入口 | 技术形态 | 核心能力摘要 |
|----|------|----------|--------------|
| **Sector E** | 黑暗森林广场 (SECTOR E // DARK FOREST) | 前端 Canvas + 本地循环 | 实时星图、观测者/猎人模式、光粒打击与探测范围、执剑人威慑小游戏、坐标广播 |
| **Zero v2 B** | Sector Zero v2 · Tab B「B 黑暗森林沙盒」 | 前端状态 + 可选 LLM 网关 `dark-forest.tick` | 多智能体回合演化、宇宙墓志铭、世界线归档/恢复、事件流、JSON/CSV 导出 |

两处共同构成「黑暗森林沙盒」的完整体验；后续扩展需保持叙事与术语一致（如「墓志铭」「世界线」「纪元」）。

---

## 3. Sector E：黑暗森林广场（当前能力）

### 3.1 宇宙沙盒 (SANDBOX)

- **观测者模式 (OBSERVER)**：
  - 200 个星体，约 8% 为文明点（CIV），其余为尘埃；文明具有 `tech`、`hiding`、`aggressive`、`detectedTargets` 等属性。
  - 探测范围由 `tech * 15 * (1 - target.hiding*0.8)` 决定；发现后侵略型文明可发动光粒打击（弹道动画 + 目标状态变为 DYING/DEAD）。
  - 支持暂停/继续、时间倍率 `timeScale`。
- **猎人模式 (HUNTER)**：
  - 玩家视角为扫描圈（`scanRadius`、`ammo`）；圈外文明显示为弱化（仅 alpha），圈内显示为红/蓝（侵略/非侵略）。
  - 点击射击可清除圈内文明，消耗弹药；未命中增加「暴露风险」反馈。
- **数据与持久化**：当前为会话内状态；无跨会话世界线归档（世界线归档在 Zero v2 B 实现）。

### 3.2 执剑人 (SWORD)

- 威慑度/稳定性由鼠标活动度驱动：过静（模拟睡着）或过激（恐慌）导致稳定性下降；稳定性映射为威慑度。
- 三体状态：CALM / SUSPICIOUS / PREPARING / STRIKE；对应文案与音效反馈。
- 红色按钮（需先打开护盖）：触发引力波广播，两世界毁灭结局。

### 3.3 广播坐标

- 输入框 + 广播按钮，发送后展示「引力波广播已启动」及后续错误态（坐标暴露、光粒在途）。

### 3.4 当前限制与已知点

- 星图规模与文明数量固定；无「自定义文明数/地图大小」。
- 执剑人逻辑与沙盒星图无数据联动（独立小游戏）。
- 无与 Zero v2 B 的「世界线」或「墓志铭」数据互通。

---

## 4. Zero v2 B：黑暗森林沙盒（当前能力）

### 4.1 多智能体与回合演化

- **智能体模型**（`CivilizationAgent`）：`id`、`codename`、`technology_level`、`paranoia_index`、`concealment_skill`、`x`、`y`、`alive`。
- **本地种子**：`seedCivilizations(size)` 默认 8 个文明（如 CIV-031 … CIV-999），随机技术等级、疑心、隐蔽与坐标。
- **步进**：
  - 前端可调用本地 `tickUniverse(agents, epoch)`（`sim/zeroDarkForest.ts`）或通过 API `tickDarkForestWorld(agents, epoch, epochStep)` 请求服务端（`task: "dark-forest.tick"`）。
  - 每步：文明移动、技术微增、距离内发现最近目标，按 `paranoia_index` 等概率触发打击，生成 `CosmicEpitaph`（attacker、victim、reason）。
- **纪元**：`epoch` 随步进递增；UI 展示当前纪元、存活文明数、运行/暂停/重置。

### 4.2 宇宙墓志铭与事件流

- **墓志铭**：每次打击写入 `epitaphs`，展示「纪元 X：攻击方 -> 受害方」「原因」；列表有上限（如 16 条）。
- **事件流**：`eventStream` 记录 STRIKE / SYSTEM 事件；支持筛选（全部/打击/系统）、导出 JSON 与 CSV。

### 4.3 世界线 (Worldline)

- **归档**：当前状态（`epoch`、`agents`、`epitaphs`）可保存为 `WorldlineSnapshot`（id、name、savedAt、epoch、agents、epitaphs），持久化到本地（如 `zero_v2_dark_forest_worldlines`），列表上限 12。
- **恢复**：选择归档后恢复 `epoch`、`agents`、`epitaphs`，并写入一条 SYSTEM 事件。
- **对比**：选择归档后显示 `worldlineDelta`（纪元差、存活数差、墓志铭数差）。

### 4.4 地图与日志

- 简单 2D 地图：智能体以点状展示，死亡态样式区分。
- 墓志铭列表 + 事件流列表 + 导出按钮（JSON/CSV）。

### 4.5 当前限制与已知点

- 文明数量与种子规则固定；无 UI 配置「文明数/地图尺寸」。
- 服务端 `dark-forest.tick` 依赖 LLM 网关；需保留本地 fallback（当前前端可走本地 `tickUniverse` 或 API）。
- 世界线仅本地存储；无云同步与分享。

---

## 5. 用户故事与验收（近期扩展方向）

以下为用户故事示例，供迭代排期与验收参考；实现优先级需与 BRD Phase 1/2 对齐。

### 5.1 体验统一与发现

- **US-1**：作为新用户，我能在首页或导航中看到明确的「黑暗森林沙盒」入口，并理解其与「黑暗森林广场」的关系（例如：广场 = 实时沙盒 + 执剑人；Zero v2 B = 回合制宇宙 + 世界线）。
- **US-2**：作为老用户，我能在 Sector E 与 Zero v2 B 之间看到一致术语（墓志铭、纪元、文明代号）与视觉风格。

### 5.2 可玩性增强

- **US-3**：作为玩家，我能在 Zero v2 B 中设置「文明数量」（如 6 / 8 / 12）和「每步纪元长度」，然后开始新局。
- **US-4**：作为玩家，我能在 Sector E 沙盒中选择「文明密度」或「地图大小」（若实现可配置星图），以适配不同设备与偏好。
- **US-5**：作为玩家，我能在 Zero v2 B 中看到单局内「存活曲线」或「墓志铭数量随纪元」的简单图表，便于复盘。

### 5.3 沉淀与分享

- **US-6**：作为玩家，我能在 Zero v2 B 或 Sector E 中一键生成「本局摘要」卡片（如：纪元、存活数、代表性墓志铭 1～3 条），并复制/分享链接或图片。
- **US-7**：作为教师/科普者，我能导出「事件流 + 世界线元数据」的完整包（如 ZIP 含 CSV + JSON），用于课堂或二次分析。

### 5.4 商业化相关（与 COMMERCIAL-PRD 对齐）

- **US-8**：作为免费用户，我能在达到「世界线归档上限」或「导出次数上限」时看到明确提示与升级引导（文案与跳转由 COMMERCIAL-PRD 与前端权限控制）。
- **US-9**：作为付费用户，我能使用「更多世界线槽位」「更长事件流」「猎人模式无限制」等权益（具体边界见 COMMERCIAL-PRD 修订版）。

---

## 6. 技术边界与接口

### 6.1 数据模型（当前）

- **CivilizationAgent**：id, codename, technology_level, paranoia_index, concealment_skill, x, y, alive.
- **CosmicEpitaph**：id, epoch, attacker, victim, reason.
- **WorldlineSnapshot**：id, name, savedAt, epoch, agents, epitaphs.

（详见 `frontend/src/types/zero_v2.ts`。）

### 6.2 API（与 PROJECT-ZERO-V2-API-CONTRACT 一致）

- **dark-forest.tick**：  
  - 入参：currentEpoch, epochStep, agents（数组）。  
  - 出参：nextEpoch, agents, epitaphs。  
- 前端封装：`tickDarkForestWorld(agents, epoch, epochStep)`，可走网关或本地 fallback。

### 6.3 本地持久化

- Zero v2 B 世界线：`zero_v2_dark_forest_worldlines`（版本化 JSON，见 `saveVersionedState`）。
- Sector E 暂无世界线持久化；若未来与 B 打通，需统一 key 或命名空间。

### 6.4 性能与规模建议

- 当前 Zero v2 B 种子为 8 个文明；若扩展文明数量，建议单次步进复杂度 O(n²) 可控（如 n ≤ 24）。
- Sector E 200 星体 + 实时绘制与碰撞检测，需在低端设备上保持 30fps 或可配置降画质。

---

## 7. 非目标与依赖

### 7.1 本 PRD 范围内不承诺

- 多人在线对战或实时协作沙盒。
- 完整 4X 经济/科技树（仅保留「技术等级/疑心/隐蔽」等简化维度）。
- 与其它扇区（A/C/D）的剧情分支或任务线联动（若做，单独 PRD）。

### 7.2 依赖

- **LLM 网关**：Zero v2 B 服务端 tick 依赖网关可用性；必须有本地 fallback 与明确错误提示。
- **权限与计费**：高阶能力（更多世界线、导出增强）依赖 COMMERCIAL-PRD 中的角色与支付状态，由前端 `useUserStore` / 后端鉴权实现。

---

## 8. 附录：文档与代码索引

| 内容 | 位置 |
|------|------|
| Sector E 页面逻辑与状态 | `frontend/src/views/SectorDarkForest.vue` |
| Zero v2 B Tab 与世界线/事件流 | `frontend/src/views/SectorZeroV2.vue`（B 相关 refs、stepUniverse、世界线/导出） |
| 本地回合逻辑与种子 | `frontend/src/sim/zeroDarkForest.ts` |
| 类型定义 | `frontend/src/types/zero_v2.ts` |
| API 封装与 dark-forest.tick | `frontend/src/api/zero_v2.ts` |
| 网关契约 | `docs/PROJECT-ZERO-V2-API-CONTRACT.md` |
| 商业定位与指标 | `docs/黑暗森林沙盒-BRD.md` |
| 会员与付费功能清单 | `docs/COMMERCIAL-PRD.md` |

---

> 文档版本：v1.0  
> 最后更新：基于当前代码库与《黑暗森林沙盒-BRD》整理，供后续开发与迭代验收使用。
