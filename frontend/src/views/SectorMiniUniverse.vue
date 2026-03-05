<script setup lang="ts">
/**
 * Sector U: 647号小宇宙 (The Mini-Universe)
 * 核心：封闭生态管理 (Closed Ecosystem), 时间胶囊 (Capsule), 质量归还 (Return)
 * 风格：田园、温馨、伪造的永恒
 */
import { ref, onMounted, computed, reactive, watch, onUnmounted } from 'vue'
import { NInput, NButton, NPopconfirm, useMessage, NSlider } from 'naive-ui'
import { soundManager } from '@/utils/sound'

const message = useMessage()

// --- 1. Life Support System (Ecosphere) ---
// User controls: Light, Gravity, Recycling
// Goal: Maintain Balance (Stability)
const lifeSupport = reactive({
  light: 50,      // 0-100 (Optimal: 40-70)
  gravity: 1.0,   // 0.1-2.0 (Optimal: 0.8-1.2)
  recycling: 50   // 0-100 (Optimal: >80)
})

const ecoStatus = reactive({
  oxygen: 98.5,
  biomass: 50, // 0-100 (Visual growth)
  stability: 100,
  day: 1
})

let ecoTimer: ReturnType<typeof setInterval> | undefined

function updateEcosystem() {
  ecoStatus.day++
  
  // Calculate stress
  let stress = 0
  if (lifeSupport.light < 40 || lifeSupport.light > 70) stress += 5
  if (lifeSupport.gravity < 0.8 || lifeSupport.gravity > 1.2) stress += 10
  if (lifeSupport.recycling < 80) stress += 2 // Trash accumulation
  
  // Update Stability
  if (stress > 0) {
    ecoStatus.stability = Math.max(0, ecoStatus.stability - stress * 0.1)
  } else {
    ecoStatus.stability = Math.min(100, ecoStatus.stability + 1)
  }
  
  // Update Biomass (Plants) based on stability and light
  if (ecoStatus.stability > 80 && lifeSupport.light > 30) {
    ecoStatus.biomass = Math.min(100, ecoStatus.biomass + 0.5)
  } else if (ecoStatus.stability < 40) {
    ecoStatus.biomass = Math.max(0, ecoStatus.biomass - 1)
  }
  
  // Random fluctuation
  ecoStatus.oxygen = 95 + (ecoStatus.biomass / 20) + (Math.random() - 0.5)
}

const stabilityColor = computed(() => {
  if (ecoStatus.stability > 80) return '#4caf50' // Green
  if (ecoStatus.stability > 40) return '#ff9800' // Orange
  return '#f44336' // Red
})

// --- 2. Time Capsule (Local Storage) ---
const noteInput = ref('')
const notes = ref<{id: number, content: string, date: string}[]>([])

function loadNotes() {
  const saved = localStorage.getItem('sector-u-notes')
  if (saved) notes.value = JSON.parse(saved)
}

function addNote() {
  if (!noteInput.value.trim()) return
  const newNote = {
    id: Date.now(),
    content: noteInput.value,
    date: new Date().toLocaleString('zh-CN')
  }
  notes.value.unshift(newNote)
  localStorage.setItem('sector-u-notes', JSON.stringify(notes.value))
  noteInput.value = ''
  message.success('时间胶囊已封存。它将在这里度过宇宙的余生。')
}

// --- 3. Mass Return ---
const mass = ref(5.24) // kg
const isReturned = ref(false)

function returnMass() {
  isReturned.value = true
  mass.value = 0
  message.info('质量已归还大宇宙。小宇宙生态系统即将关闭。')
  clearInterval(ecoTimer)
}

// Plants Visualization (SVG)
const plants = computed(() => {
  // Generate SVG paths based on biomass
  const count = Math.floor(ecoStatus.biomass / 5)
  return Array.from({ length: count }, (_, i) => ({
    x: 10 + (i * 15) % 90,
    height: 20 + (i * 3) % 30,
    delay: i * 0.1
  }))
})

onMounted(() => {
  loadNotes()
  ecoTimer = setInterval(updateEcosystem, 1000)
  // Start gentle ambient
  soundManager.startAmbient('nature')
})

onUnmounted(() => {
  if (ecoTimer) clearInterval(ecoTimer)
  soundManager.stopAmbient()
})
</script>

<template>
  <div class="sector-u">
    <div class="u-bg-pattern"></div>

    <main class="u-main">
      <header class="u-header">
        <div class="u-header-inner">
          <h1 class="u-title">Universe 647</h1>
          <p class="u-tagline">第 {{ ecoStatus.day }} 天 · 质量与记忆的归宿</p>
          <div class="u-mass-bar">
            <span class="u-mass-label">TOTAL MASS</span>
            <span class="u-mass-value">{{ mass.toFixed(2) }} kg</span>
          </div>
        </div>
      </header>

      <!-- Life Support Control -->
      <section class="u-card u-card--eco" :class="{ 'power-off': isReturned }">
        <div class="eco-visual">
          <div class="sky" :style="{ opacity: lifeSupport.light / 100 }"></div>
          <div class="ground">
            <svg class="plants-svg" viewBox="0 0 100 50" preserveAspectRatio="none">
              <g v-for="(p, i) in plants" :key="i">
                <path 
                  :d="`M ${p.x},50 Q ${p.x-2},${50-p.height/2} ${p.x},${50-p.height}`" 
                  stroke="#4caf50" 
                  stroke-width="1" 
                  fill="none"
                  class="plant-stem"
                  :style="{ animationDelay: p.delay + 's' }"
                />
                <circle :cx="p.x" :cy="50-p.height" r="1.5" fill="#81c784" />
              </g>
            </svg>
          </div>
          <div class="status-overlay">
            <div class="stat-badge">氧气: {{ ecoStatus.oxygen.toFixed(1) }}%</div>
            <div class="stat-badge" :style="{ color: stabilityColor }">
              生态稳定度: {{ Math.floor(ecoStatus.stability) }}%
            </div>
          </div>
        </div>

        <div class="eco-controls">
          <h2 class="u-card-title">维生系统 (LIFE SUPPORT)</h2>
          <div class="control-row">
            <label>模拟光照 (LIGHT)</label>
            <NSlider v-model:value="lifeSupport.light" :step="1" />
          </div>
          <div class="control-row">
            <label>人工重力 (GRAVITY)</label>
            <NSlider v-model:value="lifeSupport.gravity" :min="0.1" :max="2.0" :step="0.1" />
          </div>
          <div class="control-row">
            <label>物质循环 (RECYCLING)</label>
            <NSlider v-model:value="lifeSupport.recycling" :step="1" />
          </div>
          <p class="hint">提示：保持参数在适宜范围以维持生态。光照需适中，重力需接近 1G，循环效率需高。</p>
        </div>
      </section>

      <!-- Time Capsule -->
      <section class="u-card u-card--capsule" v-if="!isReturned">
        <h2 class="u-card-title">时间胶囊 (TIME CAPSULE)</h2>
        <div class="u-input-row">
          <NInput
            v-model:value="noteInput"
            type="textarea"
            placeholder="写给新宇宙的信..."
            :rows="2"
            class="u-textarea"
          />
          <NButton type="primary" secondary @click="addNote" :disabled="!noteInput.trim()">
            封存
          </NButton>
        </div>
        <div class="u-notes">
          <div v-for="n in notes" :key="n.id" class="u-note">
            <span class="u-note-time">{{ n.date }}</span>
            <p class="u-note-text">{{ n.content }}</p>
          </div>
        </div>
      </section>

      <!-- Return Mass -->
      <section class="u-card u-card--return">
        <h2 class="u-card-title">回归运动 (THE RETURN)</h2>
        <p class="u-return-desc">
          如果小宇宙不归还质量，大宇宙将会在无限膨胀中死去。
        </p>
        <NPopconfirm @positive-click="returnMass" :disabled="isReturned">
          <template #trigger>
            <NButton type="warning" ghost block class="u-return-btn" :disabled="isReturned">
              {{ isReturned ? '已归还 (RETURNED)' : '归还质量 (RETURN MASS)' }}
            </NButton>
          </template>
          这将摧毁小宇宙的生态系统。确定吗？
        </NPopconfirm>
      </section>

    </main>
  </div>
</template>

<style scoped>
.sector-u {
  min-height: 0;
  background: #f8f6f2;
  color: #3e2723;
  font-family: 'Noto Serif SC', serif;
  padding: 2rem;
  overflow-y: auto;
}

.u-bg-pattern {
  position: fixed;
  inset: 0;
  background-image: radial-gradient(circle at 50% 50%, rgba(141, 110, 99, 0.05) 0%, transparent 60%);
  pointer-events: none;
}

.u-main {
  max-width: 600px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.u-header { text-align: center; margin-bottom: 2rem; border-bottom: 1px solid #e0d0c0; padding-bottom: 1rem; }
.u-title { font-size: 2rem; margin: 0; color: #5d4037; }
.u-tagline { color: #8d6e63; font-size: 0.9rem; margin-bottom: 1rem; }
.u-mass-value { font-weight: bold; color: #d84315; }

.u-card {
  background: #fff;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  border: 1px solid #f0eadd;
}

.u-card-title {
  font-size: 1.1rem;
  color: #4e342e;
  border-left: 3px solid #8d6e63;
  padding-left: 0.5rem;
  margin: 0 0 1rem 0;
}

/* Ecosphere */
.eco-visual {
  height: 150px;
  background: #e0f2f1;
  border-radius: 4px;
  position: relative;
  overflow: hidden;
  margin-bottom: 1.5rem;
  border: 1px solid #b2dfdb;
}

.power-off .eco-visual {
  filter: grayscale(1) brightness(0.5);
}

.sky {
  position: absolute; top: 0; left: 0; right: 0; height: 100px;
  background: linear-gradient(to bottom, #fff9c4, #fff);
  transition: opacity 0.5s;
}

.ground {
  position: absolute; bottom: 0; left: 0; right: 0; height: 50px;
  background: #5d4037;
}

.plants-svg { width: 100%; height: 100%; }
.plant-stem {
  transform-origin: bottom center;
  animation: sway 3s ease-in-out infinite alternate;
}

@keyframes sway { from { transform: rotate(-5deg); } to { transform: rotate(5deg); } }

.status-overlay {
  position: absolute; top: 10px; right: 10px;
  text-align: right;
  font-family: monospace;
  font-size: 0.8rem;
}

.eco-controls .control-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.8rem;
}
.eco-controls label { width: 140px; font-size: 0.85rem; color: #6d4c41; }
.hint { font-size: 0.75rem; color: #8d6e63; font-style: italic; margin-top: 1rem; }

/* Capsule */
.u-input-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
.u-textarea { flex: 1; }
.u-notes { display: flex; flex-direction: column; gap: 0.8rem; }
.u-note { background: #fdfbf7; padding: 0.8rem; border-radius: 4px; border: 1px solid #eee; }
.u-note-time { display: block; font-size: 0.7rem; color: #aaa; margin-bottom: 0.3rem; }
.u-note-text { margin: 0; font-size: 0.9rem; line-height: 1.5; }

/* Return */
.u-card--return { background: #fff8e1; border-color: #ffe0b2; }
.u-return-desc { font-size: 0.9rem; color: #f57c00; margin-bottom: 1rem; }
</style>
