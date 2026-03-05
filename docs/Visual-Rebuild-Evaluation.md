# 视觉重构技术评估

**目标**：Cosmic Romance & Elegant Hard Sci-Fi — 写给宇宙的视觉情诗

---

## 1. 背景层方案

| 方案 | 实现 | 优点 | 缺点 | 建议 |
|------|------|------|------|------|
| **Three.js / VueGL** | WebGL 粒子系统 + Shader 星云 | 真实物理感、引力透镜、极致质感 | 包体大(~150KB)、低端设备压力 | 二期扇区 G（四维碎片）引入 |
| **CSS 多层视差** | 3-5 层 radial-gradient + 缓慢 transform | 零依赖、性能好、兼容性佳 | 效果受限，无法做复杂物理 | **Phase 1 采用** |
| **Canvas 2D** | requestAnimationFrame 粒子 + 模糊 | 折中方案，可控粒子数 | 需手动管理帧率、复杂 | 备选 |

**结论**：Phase 1 采用 **纯 CSS 多层视差 + 关键帧动画** 实现「呼吸感」星云背景。使用 `radial-gradient` 叠加、`animation` 控制 opacity 和 transform，营造缓慢流动的深空感。Three.js 留待 PRD 扇区 G（四维碎片）实现非欧几何时统一引入。

---

## 2. Bloom/Glow 效果

| 实现 | 说明 |
|------|------|
| `filter: drop-shadow()` | 无性能问题，支持多层叠加，实现柔和外发光 |
| `box-shadow` 多层 | 文字/节点外发光，配合 `text-shadow` |
| `backdrop-filter: blur()` | 磨砂玻璃质感，需注意 Safari 兼容 |
| CSS `mask-image` + `gradient` | 边缘渐变遮罩，实现辉光衰减 |

**结论**：全部采用纯 CSS，无需 Post-processing Shader。

---

## 3. 有机曲线拓扑

| 方案 | 说明 |
|------|------|
| SVG `<path d="M... Q... C...">` | 二次/三次贝塞尔曲线，模拟引力波纹、丝状结构 |
| SVG `stroke-dasharray` + `stroke-dashoffset` 动画 | 线条缓慢「绘制」与脉动 |
| 替换当前 `<line>` 为 `<path>` | 节点间用平滑曲线连接 |

**结论**：使用 SVG path 重绘拓扑，曲线控制点基于节点坐标计算，添加 8–12s 的缓慢脉动动画。

---

## 4. 色散与镜头畸变

| 方案 | 说明 |
|------|------|
| `filter: blur()` 轻微边缘模糊 | 模拟景深 |
| 多层 `::before/::after` 红蓝偏移 | 模拟色散，约 0.5–1px |
| CSS `perspective` + `transform` | 轻微透视畸变 |

**结论**：使用极轻微的 `box-shadow` 红/蓝偏移（各 1px）叠加在关键 UI 边缘，避免过度导致不适。

---

## 5. 字体与排版

| 用途 | 字体 | 权重 | 字间距 |
|------|------|------|--------|
| 数据 / 代码 | JetBrains Mono | 300 (Thin) | 0.05em |
| 标题 / 叙事 | Inter / Montserrat | 300–400 | 0.15em |
| 状态栏 | JetBrains Mono | 300 | 0.08em |

**结论**：引入 Google Fonts `JetBrains+Mono:wght@300;400`、`Inter:wght@300;400`，通过 `letter-spacing` 营造史诗感。
