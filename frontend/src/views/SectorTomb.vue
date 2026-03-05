<script setup lang="ts">
/**
 * Sector Tomb: 文明墓碑 (Civilization Tomb)
 * 风格：庄重、石刻质感 + 3body 终端统一
 * 功能：冥王星石碑刻录 + 已知灭绝文明墓志铭
 */
import { ref } from 'vue'
import { NInput, NButton, useMessage } from 'naive-ui'

const message = useMessage()
const stoneMessage = ref('')
const isCarving = ref(false)
const savedMessages = ref<string[]>([
  '给岁月以文明，而不是给文明以岁月。',
  '弱小和无知不是生存的障碍，傲慢才是。',
  '失去人性，失去很多；失去兽性，失去一切。',
  '前进！前进！！不择手段地前进！！！'
])

const MAX_ENGRAVINGS = 12
const CARVE_DURATION_MS = 2200

interface ExtinctCiv {
  name: string
  nameEn: string
  cause: string
  era: string
  desc: string
  status: string
  danger: 'EXTREME' | 'HIGH' | 'MEDIUM' | 'LOW' | 'NONE' | 'UNKNOWN' | 'N/A'
  epitaph?: string
}

const extinctCivs: ExtinctCiv[] = [
  {
    name: '三体文明',
    nameEn: 'Trisolaris',
    cause: '母星毁灭 / 黑暗森林打击',
    era: '威慑纪元末期',
    desc: '在三颗恒星的无序运动中挣扎求生，经历了二百多次毁灭与重生。最终母星被光粒摧毁，舰队流浪星际。',
    status: '流浪中 / 部分消亡',
    danger: 'EXTREME',
    epitaph: '我们曾有三个太阳，后来只剩黑暗。'
  },
  {
    name: '歌者文明',
    nameEn: 'Singer',
    cause: '未知 (高维战争参与者)',
    era: '未知',
    desc: '拥有“二向箔”等规律武器的清扫者文明。将宇宙视为一座黑暗森林，习惯性地清理任何可能暴露的低熵体。',
    status: '活跃',
    danger: 'UNKNOWN',
    epitaph: '藏好自己，做好清理。'
  },
  {
    name: '魔戒文明',
    nameEn: 'The Ring',
    cause: '高维空间跌落 / 海干了',
    era: '四维碎片时期',
    desc: '遗留在四维碎片中的智能体，自称“墓地”。暗示了宇宙从高维向低维跌落的宏大历史。',
    status: '已消亡',
    danger: 'LOW',
    epitaph: '海干了，鱼就要聚集在水洼里。'
  },
  {
    name: '184号文明',
    nameEn: 'Pendulum-184',
    cause: '三日连珠',
    era: '乱纪元',
    desc: '在三体世界的第184次轮回中，因三颗飞星连珠引发的引力叠加，导致地表撕裂，文明毁灭。',
    status: '已重启',
    danger: 'N/A',
    epitaph: '我们曾试图解析三体。'
  },
  {
    name: '边缘世界',
    nameEn: 'Fringe World',
    cause: '低光速黑洞防御',
    era: '掩体纪元',
    desc: '为躲避打击，主动降低光速并将自己包裹在黑洞视界内的文明。被称为“宇宙的隐士”。',
    status: '存活 (自我封闭)',
    danger: 'MEDIUM',
    epitaph: '我们在时间尽头等待。'
  },
  {
    name: '太阳系人类',
    nameEn: 'Solar Humans',
    cause: '二向箔打击',
    era: '掩体纪元 67年',
    desc: '因掩体计划无法防御维度打击，整个太阳系跌落至二维，在这个巨大的画卷中，所有生命凝固为永恒。',
    status: '二维化',
    danger: 'NONE',
    epitaph: '把字刻在石头上。'
  }
]

function dangerColor(d: ExtinctCiv['danger']): string {
  const map: Record<ExtinctCiv['danger'], string> = {
    EXTREME: '#c1121f',
    HIGH: '#dc2626',
    MEDIUM: '#d97706',
    LOW: '#65a30d',
    NONE: '#6b7280',
    UNKNOWN: '#7c3aed',
    'N/A': '#4b5563'
  }
  return map[d] ?? '#4b5563'
}

function carveStone() {
  const trimmed = stoneMessage.value.trim()
  if (!trimmed) return
  isCarving.value = true
  setTimeout(() => {
    savedMessages.value.unshift(trimmed)
    if (savedMessages.value.length > MAX_ENGRAVINGS) savedMessages.value.pop()
    stoneMessage.value = ''
    isCarving.value = false
    message.success('信息已刻入冥王星地层，保存期限：10 亿年。')
  }, CARVE_DURATION_MS)
}
</script>

<template>
  <div class="sector-tomb">
    <div class="bg-grid"></div>

    <header class="header">
      <div class="header-inner">
        <h1 class="title">TOMB_OF_CIVILIZATION // 文明墓碑</h1>
        <p class="subtitle">把字刻在石头上 · 这是唯一能保存十亿年的方法</p>
        <div class="header-meta">
          <span class="meta-tag">PLUTO MONUMENT</span>
          <span class="meta-tag">COSMIC EPITAPHS</span>
        </div>
      </div>
    </header>

    <div class="tomb-content">
      <!-- Left: Pluto Stone -->
      <section class="tomb-section stone-section">
        <h2 class="section-title">
          <span class="title-icon">◇</span>
          冥王星石碑
        </h2>
        <div class="stone-tablet">
          <div class="stone-texture"></div>
          <div class="tablet-surface">
            <div v-for="(msg, i) in savedMessages" :key="i" class="engraving">{{ msg }}</div>
            <div v-if="isCarving" class="engraving carving">正在刻录...</div>
          </div>
        </div>
        <div class="carve-tools">
          <p class="tool-hint">“把字刻在石头上。这是唯一能保存十亿年的方法。” — 刘慈欣《三体》</p>
          <div class="input-group">
            <NInput
              v-model:value="stoneMessage"
              type="textarea"
              placeholder="输入你想留给未来的信息..."
              :rows="2"
              :maxlength="200"
              show-count
              class="stone-input"
              :disabled="isCarving"
            />
            <NButton
              type="warning"
              class="carve-btn"
              :loading="isCarving"
              :disabled="!stoneMessage.trim()"
              @click="carveStone"
            >
              {{ isCarving ? '刻录中' : '刻录' }}
            </NButton>
          </div>
          <div class="carve-meta">保存期限：10 亿年 · 冥王星地层</div>
        </div>
      </section>

      <div class="divider-v"></div>

      <!-- Right: Cosmic Epitaphs -->
      <section class="tomb-section epitaph-section">
        <h2 class="section-title">
          <span class="title-icon">◆</span>
          宇宙墓志铭
        </h2>
        <div class="civ-list">
          <article
            v-for="civ in extinctCivs"
            :key="civ.name"
            class="civ-card"
            :style="{ '--danger-color': dangerColor(civ.danger) }"
          >
            <div class="civ-danger-bar"></div>
            <div class="civ-body">
              <div class="civ-header">
                <div class="civ-name-wrap">
                  <span class="civ-name">{{ civ.name }}</span>
                </div>
                <span class="civ-status" :class="civ.status.includes('活跃') || civ.status.includes('存活') ? 'alive' : 'dead'">
                  {{ civ.status }}
                </span>
              </div>
              <div class="civ-name-en-row">{{ civ.nameEn }}</div>
              <blockquote v-if="civ.epitaph" class="civ-epitaph">「{{ civ.epitaph }}」</blockquote>
              <div class="civ-meta">
                <span class="meta-item"><em>死因</em> {{ civ.cause }}</span>
                <span class="meta-item"><em>纪元</em> {{ civ.era }}</span>
              </div>
              <p class="civ-desc">{{ civ.desc }}</p>
              <div class="civ-footer">
                <span class="danger-label" :style="{ color: dangerColor(civ.danger) }">{{ civ.danger }}</span>
              </div>
            </div>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.sector-tomb {
  min-height: 100%;
  background: #050508;
  color: #b0b0b0;
  font-family: 'Noto Serif SC', serif;
  display: flex;
  flex-direction: column;
  position: relative;
}

.bg-grid {
  position: fixed;
  inset: 0;
  background-image:
    linear-gradient(rgba(0, 255, 255, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 255, 255, 0.02) 1px, transparent 1px);
  background-size: 24px 24px;
  pointer-events: none;
  z-index: 0;
}

/* Header */
.header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid rgba(0, 255, 255, 0.15);
  position: relative;
  z-index: 1;
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.title {
  font-family: 'Russo One', sans-serif;
  font-size: 1.6rem;
  letter-spacing: 0.06em;
  color: rgba(255, 255, 255, 0.85);
  margin: 0;
}

.subtitle {
  color: #555;
  font-size: 0.8rem;
  margin-top: 0.5rem;
  letter-spacing: 0.08em;
  font-family: monospace;
}

.header-meta {
  margin-top: 0.75rem;
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.meta-tag {
  font-family: monospace;
  font-size: 0.65rem;
  padding: 2px 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.5);
}

/* Content */
.tomb-content {
  flex: 1;
  display: flex;
  padding: 2rem;
  gap: 2rem;
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.tomb-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.section-title {
  font-size: 1rem;
  color: rgba(0, 255, 255, 0.7);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 0.5rem;
  margin-bottom: 1.25rem;
  font-family: monospace;
  letter-spacing: 0.12em;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.title-icon {
  color: rgba(0, 255, 255, 0.5);
  font-size: 0.75rem;
}

.divider-v {
  width: 1px;
  background: rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
}

/* Stone Tablet */
.stone-section {
  max-width: 520px;
}

.stone-tablet {
  background: linear-gradient(145deg, #1a1a1a 0%, #0d0d0d 100%);
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow:
    inset 0 0 80px rgba(0, 0, 0, 0.6),
    0 4px 20px rgba(0, 0, 0, 0.4);
  flex: 1;
  overflow-y: auto;
  margin-bottom: 1.5rem;
  position: relative;
  border-radius: 2px;
}

.stone-texture {
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
  pointer-events: none;
  border-radius: inherit;
}

.tablet-surface {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
  align-items: center;
  padding: 0.5rem 0;
}

.engraving {
  font-size: 1rem;
  color: #6a6a6a;
  text-shadow: 0 1px 0 rgba(0, 0, 0, 0.8);
  letter-spacing: 0.08em;
  text-align: center;
  line-height: 1.6;
  font-family: 'Noto Serif SC', serif;
}

.carving {
  color: rgba(212, 160, 23, 0.9);
  animation: pulse 1.2s ease-in-out infinite;
}

.carve-tools {
  margin-top: auto;
}

.tool-hint {
  text-align: center;
  color: #444;
  font-size: 0.75rem;
  margin-bottom: 1rem;
  font-style: italic;
  line-height: 1.5;
}

.input-group {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.stone-input {
  flex: 1;
}

.stone-input :deep(.n-input__input-el),
.stone-input :deep(textarea) {
  background: rgba(0, 0, 0, 0.4) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  color: #bbb !important;
  font-family: 'Noto Serif SC', serif !important;
}

.carve-btn {
  flex-shrink: 0;
  font-family: monospace;
}

.carve-meta {
  margin-top: 0.5rem;
  font-size: 0.65rem;
  color: #444;
  text-align: center;
  font-family: monospace;
  letter-spacing: 0.1em;
}

/* Civ Cards */
.epitaph-section {
  min-width: 320px;
}

.civ-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  overflow-y: auto;
  padding-right: 0.25rem;
}

.civ-card {
  background: rgba(8, 12, 18, 0.88);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 2px;
  overflow: visible;
  display: flex;
  min-height: 156px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.civ-card:hover {
  border-color: rgba(255, 255, 255, 0.12);
  box-shadow: 0 0 24px rgba(0, 0, 0, 0.3);
}

.civ-danger-bar {
  width: 4px;
  flex-shrink: 0;
  background: var(--danger-color, #4b5563);
}

.civ-body {
  flex: 1;
  padding: 1rem 1.25rem 1.1rem;
  display: flex;
  flex-direction: column;
  gap: 0.38rem;
  position: relative;
  z-index: 1;
}

.civ-header {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 0.1rem;
}

.civ-name-wrap {
  min-width: 0;
  position: relative;
  z-index: 1;
}

.civ-name {
  font-size: 1.05rem;
  color: #ddd;
  font-weight: 600;
  line-height: 1.42;
  word-break: break-word;
  white-space: normal;
}

.civ-name-en-row {
  margin-top: 0.06rem;
  margin-bottom: 0.15rem;
  min-height: 1.25em;
  display: block;
  font-size: 0.74rem;
  color: #8b97aa;
  font-family: monospace;
  line-height: 1.45;
  word-break: break-word;
  white-space: normal;
  letter-spacing: 0.02em;
  position: relative;
  z-index: 1;
}

.civ-status {
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 2px;
  flex-shrink: 0;
  align-self: flex-start;
  font-family: monospace;
  white-space: nowrap;
  position: relative;
  z-index: 2;
}

.civ-status.alive {
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.4);
}

.civ-status.dead {
  color: #94a3b8;
  border: 1px solid rgba(148, 163, 184, 0.3);
}

.civ-epitaph {
  font-size: 0.85rem;
  color: rgba(0, 255, 255, 0.6);
  border-left: 2px solid rgba(0, 255, 255, 0.3);
  padding-left: 0.75rem;
  margin: 0 0 0.75rem;
  font-style: italic;
}

.civ-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.72rem;
  color: #555;
  margin-bottom: 0.2rem;
  font-family: monospace;
}

.civ-meta .meta-item em {
  color: #444;
  font-style: normal;
  margin-right: 0.25rem;
}

.civ-desc {
  font-size: 0.88rem;
  color: #888;
  line-height: 1.6;
  margin: 0;
}

.civ-footer {
  margin-top: auto;
  padding-top: 0.5rem;
  border-top: 1px dashed rgba(255, 255, 255, 0.06);
}

.danger-label {
  font-size: 0.65rem;
  font-family: monospace;
  letter-spacing: 0.1em;
}

@keyframes pulse {
  50% { opacity: 0.5; }
}

/* Scrollbar */
.sector-tomb :deep(::-webkit-scrollbar) {
  width: 6px;
  height: 6px;
}
.sector-tomb :deep(::-webkit-scrollbar-track) {
  background: rgba(0, 0, 0, 0.2);
}
.sector-tomb :deep(::-webkit-scrollbar-thumb) {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 3px;
}
.sector-tomb :deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(255, 255, 255, 0.25);
}

@media (max-width: 900px) {
  .tomb-content {
    flex-direction: column;
    padding: 1.5rem;
  }

  .divider-v {
    width: 100%;
    height: 1px;
  }

  .stone-section {
    max-width: none;
  }

  .epitaph-section {
    min-width: 0;
  }

  .civ-card {
    min-height: 168px;
  }
}
</style>
