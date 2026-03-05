<script setup lang="ts">
/**
 * Sector Galaxy Human: 银河人类 (Galaxy Human)
 * 展示人类在太空中的演化分支 — 优化版：时间线 + 演化树可视化
 */
import { ref, computed } from 'vue'
import { NTimeline, NTimelineItem, NCard } from 'naive-ui'

interface EvolutionNode {
  era: string
  eraCode: string
  title: string
  content: string
  tech: string
  culture: string
  quote?: string
}

const evolutionTree: EvolutionNode[] = [
  {
    era: '公元时代',
    eraCode: 'AD',
    title: '地球人类 (Earth Humans)',
    content: '生活在地球摇篮中的原始人类，拥有完整的爱与道德。未经历技术爆炸，社会结构稳定但脆弱。',
    tech: '化学动力火箭 / 传统信息技术',
    culture: '普世价值 / 民族国家',
    quote: '给岁月以文明，而不是给文明以岁月。'
  },
  {
    era: '危机纪元',
    eraCode: 'CRISIS',
    title: '黄金时代人类 (Golden Age)',
    content: '大低谷后的技术复兴，建立了庞大的太空舰队。人类极度自信，甚至傲慢，认为三体不足为惧。',
    tech: '可控核聚变 / 恒星级战舰',
    culture: '技术乐观主义 / 享乐主义',
    quote: '他们只是虫子。'
  },
  {
    era: '威慑纪元',
    eraCode: 'DETERRENCE',
    title: '女性化人类 (Feminized Society)',
    content: '在长期的和平与威慑保护下，人类整体气质趋于柔和、精致。失去了兽性与侵略性，却保留了对他人的关爱。',
    tech: '引力波威慑 / 强互作用力材料(初级)',
    culture: '极致人道主义 / 去中心化',
    quote: '把枪口对准自己的脑袋，才是真正的威慑。'
  },
  {
    era: '广播纪元',
    eraCode: 'BROADCAST',
    title: '星舰人类 (Galactic Humans)',
    content: '“蓝色空间”号与“万有引力”号的后裔。在黑暗森林中进化出了新的道德观：生存是第一要务。他们不再是人类，而是新物种。',
    tech: '曲率驱动 / 四维空间技术 / 宇宙社会学',
    culture: '集权 / 极度理性 / 新人类',
    quote: '不要返航，这里不是家。'
  },
  {
    era: '掩体纪元',
    eraCode: 'BUNKER',
    title: '掩体人类 (Bunker Humans)',
    content: '躲藏在木星、土星等巨行星背后的人类，生活在狭窄的太空城中。虽然科技发达，但心态如穴居人般恐惧。',
    tech: '太空城集群 / 黑洞项目',
    culture: '封闭 / 避难所心态',
    quote: '藏好自己，做好清理。'
  },
  {
    era: '银河纪元',
    eraCode: 'GALAXY',
    title: '归零者 (Zero-Homers)',
    content: '在漫长的宇宙流浪中，部分人类可能已经融入了更高级的宇宙文明，成为了重启宇宙的一部分。',
    tech: '物理规律修改 / 小宇宙技术',
    culture: '宇宙大一统 / 责任感',
    quote: '归还质量，重启宇宙。'
  }
]

const selectedIndex = ref<number | null>(null)
const eraColor = (i: number) => {
  const colors = ['#00cccc', '#ff6600', '#aa66ff', '#00ff88', '#ffaa00', '#00ffff']
  return colors[i % colors.length]
}
</script>

<template>
  <div class="sector-galaxy">
    <div class="bg-grid"></div>

    <header class="header">
      <div class="header-inner">
        <h1 class="title">GALAXY_HUMAN // 银河人类</h1>
        <p class="subtitle">人类在银河中的演化分支 · EVOLUTION OF HUMANITY IN THE DARK FOREST</p>
        <div class="header-meta">
          <span class="meta-tag">CLASSIFIED</span>
          <span class="meta-tag">6 BRANCHES</span>
        </div>
      </div>
    </header>

    <div class="content-wrapper">
      <aside class="evolution-viz">
        <div class="viz-title">EVOLUTION TREE</div>
        <svg class="tree-svg" viewBox="0 0 280 400" fill="none" xmlns="http://www.w3.org/2000/svg">
          <!-- 根节点 -->
          <circle cx="140" cy="22" r="10" class="tree-node root" :class="{ active: selectedIndex === null }" />
          <text x="140" y="48" class="tree-label">HUMAN</text>
          <!-- 主干到第一分支 -->
          <path d="M 140 32 L 140 62" class="tree-edge" />
          <!-- 分支 + 竖直主干 -->
          <template v-for="(node, i) in evolutionTree" :key="i">
            <path
              :d="`M 140 ${62 + i * 54} L 200 ${80 + i * 54}`"
              class="tree-edge"
              :class="{ active: selectedIndex === i }"
            />
            <circle
              :cx="200"
              :cy="80 + i * 54"
              :r="11"
              class="tree-node"
              :class="{ active: selectedIndex === i }"
              :style="{ '--era-color': eraColor(i) }"
              @mouseenter="selectedIndex = i"
              @click="selectedIndex = i"
            />
            <text :x="218" :y="84 + i * 54" class="tree-label small">{{ node.eraCode }}</text>
            <path
              v-if="i < evolutionTree.length - 1"
              :d="`M 140 ${62 + i * 54} L 140 ${62 + (i + 1) * 54}`"
              class="tree-edge"
            />
          </template>
        </svg>
        <p class="viz-hint">悬停或点击节点高亮</p>
      </aside>

      <main class="evolution-chart">
        <NTimeline size="large" class="galaxy-timeline">
          <NTimelineItem
            v-for="(node, i) in evolutionTree"
            :key="i"
            type="info"
            :title="node.title"
            :time="node.era"
            :class="{ focused: selectedIndex === null || selectedIndex === i }"
          >
            <NCard
              class="evo-card"
              :bordered="false"
              @mouseenter="selectedIndex = i"
              @mouseleave="selectedIndex = null"
            >
              <span class="card-era" :style="{ borderColor: eraColor(i), color: eraColor(i) }">
                {{ node.era }}
              </span>
              <p class="card-content">{{ node.content }}</p>
              <blockquote v-if="node.quote" class="card-quote">「{{ node.quote }}」</blockquote>
              <div class="card-meta">
                <div class="meta-row">
                  <span class="meta-label">TECH</span>
                  <span class="meta-val">{{ node.tech }}</span>
                </div>
                <div class="meta-row">
                  <span class="meta-label">CULTURE</span>
                  <span class="meta-val">{{ node.culture }}</span>
                </div>
              </div>
            </NCard>
          </NTimelineItem>
        </NTimeline>
      </main>
    </div>
  </div>
</template>

<style scoped>
.sector-galaxy {
  min-height: 100%;
  background: #050508;
  color: #c0c0c0;
  font-family: 'Noto Serif SC', serif;
  display: flex;
  flex-direction: column;
  position: relative;
}

.bg-grid {
  position: fixed;
  inset: 0;
  background-image:
    linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 24px 24px;
  pointer-events: none;
  z-index: 0;
}

/* Header */
.header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid rgba(0, 255, 255, 0.2);
  position: relative;
  z-index: 1;
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
}

.title {
  font-family: 'Russo One', sans-serif;
  font-size: 1.75rem;
  letter-spacing: 0.08em;
  color: #00ffff;
  margin: 0;
  text-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
}

.subtitle {
  color: #666;
  font-size: 0.75rem;
  margin-top: 0.5rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  font-family: monospace;
}

.header-meta {
  margin-top: 0.75rem;
  display: flex;
  gap: 0.75rem;
}

.meta-tag {
  font-family: monospace;
  font-size: 0.65rem;
  padding: 2px 8px;
  border: 1px solid rgba(0, 255, 255, 0.3);
  color: rgba(0, 255, 255, 0.8);
}

/* Content */
.content-wrapper {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
  z-index: 1;
}

/* Left: Evolution Tree Viz */
.evolution-viz {
  width: 280px;
  flex-shrink: 0;
  padding: 2rem 1rem;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  align-items: center;
  background: rgba(0, 0, 0, 0.25);
}

.viz-title {
  font-family: monospace;
  font-size: 0.7rem;
  letter-spacing: 0.2em;
  color: rgba(0, 255, 255, 0.6);
  margin-bottom: 1.5rem;
}

.tree-svg {
  width: 100%;
  max-height: 380px;
}

.tree-edge {
  stroke: rgba(255, 255, 255, 0.12);
  stroke-width: 1.5;
  transition: stroke 0.25s;
}

.tree-edge.active {
  stroke: rgba(0, 255, 255, 0.6);
  stroke-width: 2;
}

.tree-node {
  fill: rgba(255, 255, 255, 0.08);
  stroke: rgba(255, 255, 255, 0.25);
  stroke-width: 1.5;
  cursor: pointer;
  transition: fill 0.2s, stroke 0.2s, filter 0.2s;
}

.tree-node.root {
  fill: rgba(0, 255, 255, 0.15);
  stroke: rgba(0, 255, 255, 0.4);
}

.tree-node:hover,
.tree-node.active {
  fill: var(--era-color, rgba(0, 255, 255, 0.3));
  stroke: var(--era-color, #00ffff);
  filter: drop-shadow(0 0 8px var(--era-color, rgba(0, 255, 255, 0.5)));
}

.tree-label {
  fill: rgba(255, 255, 255, 0.5);
  font-size: 10px;
  font-family: monospace;
  text-anchor: middle;
}

.tree-label.small {
  font-size: 8px;
  text-anchor: start;
}

.viz-hint {
  margin-top: 1rem;
  font-size: 0.65rem;
  color: #555;
  font-family: monospace;
}

/* Main: Timeline */
.evolution-chart {
  flex: 1;
  padding: 2rem 3rem;
  overflow-y: auto;
}

.galaxy-timeline :deep(.n-timeline-item) {
  opacity: 0.6;
  transition: opacity 0.25s;
}

.galaxy-timeline :deep(.n-timeline-item.focused) {
  opacity: 1;
}

.galaxy-timeline :deep(.n-timeline-item-content__title) {
  color: #e0e0e0;
  font-size: 1.05rem;
}

.galaxy-timeline :deep(.n-timeline-item-content__time) {
  color: rgba(0, 255, 255, 0.6);
  font-family: monospace;
  font-size: 0.75rem;
}

.card-era {
  display: inline-block;
  font-family: monospace;
  font-size: 0.7rem;
  padding: 2px 8px;
  border: 1px solid;
  border-radius: 2px;
  margin-bottom: 0.5rem;
}

.evo-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  margin-top: 0.5rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.evo-card:hover {
  border-color: rgba(0, 255, 255, 0.2);
  box-shadow: 0 0 20px rgba(0, 255, 255, 0.06);
}

.card-content {
  font-size: 0.95rem;
  line-height: 1.7;
  color: #bbb;
  margin-bottom: 0.75rem;
}

.card-quote {
  font-size: 0.85rem;
  color: rgba(0, 255, 255, 0.7);
  border-left: 3px solid rgba(0, 255, 255, 0.4);
  padding-left: 1rem;
  margin: 0 0 1rem;
  font-style: italic;
}

.card-meta {
  border-top: 1px dashed rgba(255, 255, 255, 0.1);
  padding-top: 0.75rem;
  font-family: monospace;
  font-size: 0.78rem;
  color: #777;
}

.meta-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.meta-label {
  color: #555;
  font-weight: bold;
  min-width: 72px;
}

.meta-val {
  color: #6aa;
}

@media (max-width: 900px) {
  .content-wrapper {
    flex-direction: column;
  }

  .evolution-viz {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
    gap: 1rem;
  }

  .tree-svg {
    max-height: 200px;
  }

  .evolution-chart {
    padding: 1.5rem 1.5rem;
  }
}
</style>
