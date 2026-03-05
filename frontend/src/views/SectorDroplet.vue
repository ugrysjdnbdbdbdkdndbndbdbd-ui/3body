<script setup lang="ts">
/**
 * Sector W: The Droplet (水滴)
 * 核心：绝对光滑 (Mirror), 动态打击 (Strike), 太阳封锁 (Blockade)
 * 技术：TresJS (3D), Canvas (2D Game)
 */
import { ref, onMounted, computed } from 'vue'
import { NTabs, NTabPane } from 'naive-ui'
import { TresCanvas } from '@tresjs/core'
import { OrbitControls, Stars, Environment } from '@tresjs/cientos'
const activeTab = ref('mirror')

// --- 1. Mirror Inspection (3D) ---
const magnification = ref(1)
const cameraZ = ref(5)

// 水滴航程：模拟航行中经过的星体与宇宙现象，镜面反射随之变化（核心玩法）
// 九站推荐反射图资源与 URL 见：docs/水滴航程-站点反射图资源.md
type EnvPresetKey = 'night' | 'sunset' | 'dawn' | 'city' | 'studio' | 'snow' | 'modern'
interface Waypoint {
  id: string
  name: string
  desc: string
  preset: EnvPresetKey
}
const WAYPOINTS: Waypoint[] = [
  { id: 'deep', name: '深空', desc: '星际空间，只有微弱星光', preset: 'night' },
  { id: 'earth', name: '地球附近', desc: '蓝色星球与人类空间站', preset: 'city' },
  { id: 'cislunar', name: '地月空间', desc: '荒凉与日光', preset: 'studio' },
  { id: 'belt', name: '小行星带', desc: '碎片与冰尘', preset: 'snow' },
  { id: 'jupiter', name: '木星阴影', desc: '气态巨行星的辉光', preset: 'sunset' },
  { id: 'nebula', name: '星云边缘', desc: '恒星诞生区的光芒', preset: 'dawn' },
  { id: 'stellar', name: '掠过恒星', desc: '恒星光晕', preset: 'sunset' },
  { id: 'oort', name: '奥尔特云', desc: '冰冻与远方', preset: 'snow' },
  { id: 'station', name: '人类前哨', desc: '空间站与金属结构', preset: 'modern' },
]
const currentWaypointIndex = ref(0)
const currentWaypoint = computed(() => WAYPOINTS[currentWaypointIndex.value] ?? WAYPOINTS[0])
const envPreset = computed(() => currentWaypoint.value.preset)

function goToWaypoint(index: number) {
  const i = Math.max(0, Math.min(index, WAYPOINTS.length - 1))
  currentWaypointIndex.value = i
}

function nextWaypoint() {
  goToWaypoint(currentWaypointIndex.value + 1)
}

function prevWaypoint() {
  goToWaypoint(currentWaypointIndex.value - 1)
}

const surfaceInfo = computed(() => {
  const mag = magnification.value
  if (mag < 10) return `倍率: x${mag.toFixed(1)} (宏观)`
  if (mag < 1000) return `倍率: x${mag.toFixed(0)} (显微)`
  if (mag < 1000000) return `倍率: x${(mag/1000).toFixed(1)}k (纳米)`
  if (mag < 1000000000) return `倍率: x${(mag/1000000).toFixed(1)}M (皮米)`
  return `倍率: x${(mag/1000000000).toFixed(1)}B (强互作用力)`
})

function handleWheel(e: WheelEvent) {
  e.preventDefault()
  // Zoom In/Out
  const delta = e.deltaY > 0 ? 0.9 : 1.1
  magnification.value *= delta
  if (magnification.value < 1) magnification.value = 1
  
  // Camera Loop effect for "Infinite Smoothness"
  // Move camera from 5 to 2. When it hits 2, reset to 5 but keep magnification high.
  // This illusion shows that "zooming in changes nothing".
  // Actually, let's just let OrbitControls handle real zoom, and we just track the "virtual" magnification.
  // Wait, OrbitControls clamps zoom.
  // Let's manually adjust camera position for the visual effect.
  
  let newZ = cameraZ.value / delta
  if (newZ < 2.5) newZ = 4.5 // Loop back to simulate infinite smooth surface
  if (newZ > 5) newZ = 5
  cameraZ.value = newZ
}


// --- 2. Kinetic Strike (2D Game) ---
const canvasRef = ref<HTMLCanvasElement | null>(null)
const isStriking = ref(false)
const strikeScore = ref(0)
const fleet = ref<Array<{x: number, y: number, alive: boolean}>>([])
const pathPoints = ref<Array<{x: number, y: number}>>([])

function initFleet() {
  fleet.value = []
  for (let i = 0; i < 50; i++) {
    fleet.value.push({
      x: Math.random() * 800,
      y: Math.random() * 400 + 100,
      alive: true
    })
  }
}

function handleMouseDown(e: MouseEvent) {
  if (isStriking.value) return
  const rect = canvasRef.value!.getBoundingClientRect()
  pathPoints.value = [{
    x: e.clientX - rect.left,
    y: e.clientY - rect.top
  }]
}

function handleMouseMove(e: MouseEvent) {
  if (isStriking.value || pathPoints.value.length === 0) return
  const rect = canvasRef.value!.getBoundingClientRect()
  pathPoints.value.push({
    x: e.clientX - rect.left,
    y: e.clientY - rect.top
  })
}

function handleMouseUp() {
  if (!isStriking.value && pathPoints.value.length > 5) {
    executeStrike()
  } else {
    pathPoints.value = []
  }
}

function handleTouchStart(e: TouchEvent) {
  if (isStriking.value) return
  const rect = canvasRef.value!.getBoundingClientRect()
  const touch = e.touches[0]
  pathPoints.value = [{
    x: touch.clientX - rect.left,
    y: touch.clientY - rect.top
  }]
}

function handleTouchMove(e: TouchEvent) {
  if (isStriking.value || pathPoints.value.length === 0) return
  e.preventDefault() // Prevent scroll while drawing
  const rect = canvasRef.value!.getBoundingClientRect()
  const touch = e.touches[0]
  pathPoints.value.push({
    x: touch.clientX - rect.left,
    y: touch.clientY - rect.top
  })
}

function handleTouchEnd() {
  handleMouseUp()
}

function executeStrike() {
  isStriking.value = true
  let step = 0
  const totalSteps = pathPoints.value.length
  
  const interval = setInterval(() => {
    if (step >= totalSteps) {
      clearInterval(interval)
      isStriking.value = false
      pathPoints.value = []
      return
    }
    
    const pos = pathPoints.value[step]
    // Check collisions
    fleet.value.forEach(ship => {
      if (!ship.alive) return
      const dx = ship.x - pos.x
      const dy = ship.y - pos.y
      if (Math.sqrt(dx*dx + dy*dy) < 30) {
        ship.alive = false
        strikeScore.value++
      }
    })
    step+=2 // speed
  }, 10)
}

// --- 3. Sun Blockade ---
const jammingIntensity = ref(0)
const isJammed = computed(() => jammingIntensity.value > 80)

function toggleJamming() {
  jammingIntensity.value = jammingIntensity.value === 0 ? 100 : 0
}

onMounted(() => {
  initFleet()
})

</script>

<template>
  <div class="sector-w">
    <div class="header">
      <h1 class="title">SECTOR W // THE DROPLET</h1>
      <div class="subtitle">强互作用力宇宙探测器</div>
    </div>

    <NTabs type="segment" v-model:value="activeTab" class="w-tabs">
      
      <!-- Tab 1: Mirror -->
      <NTabPane name="mirror" tab="绝对光滑 (MIRROR)">
        <div class="scene-3d" @wheel="handleWheel">
          <TresCanvas clear-color="#000">
            <TresPerspectiveCamera :position="[0, 0, cameraZ]" :look-at="[0,0,0]" />
            <OrbitControls :enable-zoom="false" :enable-pan="false" :auto-rotate="true" :auto-rotate-speed="0.5" />
            
            <Stars :radius="100" :count="5000" :size="0.5" />
            <Environment :preset="envPreset" :blur="0.5" />

            <!-- The Droplet -->
            <TresMesh :scale="[1, 1, 1.8]" :position="[0,0,0]">
              <TresSphereGeometry :args="[1.5, 128, 128]" />
              <TresMeshStandardMaterial 
                color="#a0a0a0" 
                :metalness="1" 
                :roughness="0" 
                :envMapIntensity="3"
              />
            </TresMesh>
            
            <TresDirectionalLight :position="[5, 5, 5]" :intensity="2" />
            <TresAmbientLight :intensity="0.5" />
          </TresCanvas>
          
          <div class="journey-panel">
            <h3 class="journey-title">水滴航程 · 镜面反射</h3>
            <p class="journey-desc">水滴在航行中经过不同星体与宇宙现象，表面将反射当时的环境。选择一站，观察镜面变化。</p>
            <div class="journey-current">
              <span class="journey-label">当前经过</span>
              <div class="journey-name">{{ currentWaypoint.name }}</div>
              <div class="journey-detail reason">{{ currentWaypoint.desc }}</div>
              <div class="journey-nav">
                <button type="button" class="journey-btn" :disabled="currentWaypointIndex <= 0" @click="prevWaypoint">上一站</button>
                <span class="journey-progress">{{ currentWaypointIndex + 1 }} / {{ WAYPOINTS.length }}</span>
                <button type="button" class="journey-btn" :disabled="currentWaypointIndex >= WAYPOINTS.length - 1" @click="nextWaypoint">下一站</button>
              </div>
            </div>
            <div class="waypoint-list">
              <button
                v-for="(wp, i) in WAYPOINTS"
                :key="wp.id"
                type="button"
                class="waypoint-chip"
                :class="{ active: currentWaypointIndex === i }"
                @click="goToWaypoint(i)"
              >
                {{ wp.name }}
              </button>
            </div>
          </div>
          <div class="hud-overlay">
            <div class="data-row">
              <span class="label">表面温度:</span>
              <span class="val">~0 K</span>
            </div>
            <div class="data-row">
              <span class="label">反射率:</span>
              <span class="val">100.00%</span>
            </div>
            <div class="data-row highlight">
              <span class="label">{{ surfaceInfo }}</span>
            </div>
            <div class="hint-text">
              滚动鼠标滚轮放大观察表面细节 · 航程中切换站点体验不同反射
            </div>
          </div>
        </div>
      </NTabPane>

      <!-- Tab 2: Strike -->
      <NTabPane name="strike" tab="末日战役 (STRIKE)">
        <div class="game-container">
          <div class="game-header">
            <span>目标: 联合舰队 ({{ fleet.filter(s => s.alive).length }} / 50)</span>
            <span>击毁数: {{ strikeScore }}</span>
            <span class="hint">拖动鼠标规划水滴轨迹</span>
          </div>
          <canvas 
            ref="canvasRef" 
            width="800" 
            height="500" 
            class="strike-canvas"
            @mousedown="handleMouseDown"
            @mousemove="handleMouseMove"
            @mouseup="handleMouseUp"
            @touchstart="handleTouchStart"
            @touchmove="handleTouchMove"
            @touchend="handleTouchEnd"
          ></canvas>
          
          <!-- Canvas Logic in Template via overlays for simplicity -->
          <div class="canvas-overlay">
            <!-- Ships -->
            <div 
              v-for="(ship, i) in fleet" 
              :key="i" 
              class="ship" 
              :class="{ destroyed: !ship.alive }"
              :style="{ left: ship.x + 'px', top: ship.y + 'px' }"
            >
              <div v-if="!ship.alive" class="explosion">💥</div>
            </div>
            
            <!-- Droplet (only when striking) -->
            <!-- Simplified: Actual logic handles logic, visuals via CSS for ships, Canvas for path? -->
            <!-- Actually let's just use CSS for ships for easier reactivity -->
          </div>
        </div>
      </NTabPane>

      <!-- Tab 3: Blockade -->
      <NTabPane name="blockade" tab="太阳封锁 (BLOCKADE)">
        <div class="blockade-ui">
          <div class="sun-view" :class="{ jammed: isJammed }">
            <div class="sun-core"></div>
            <div class="droplet-silhouette"></div>
            <div class="waves">
              <div class="wave" v-for="n in 5" :key="n"></div>
            </div>
          </div>
          
          <div class="controls">
            <h2>恒星电波放大功能</h2>
            <div class="status" :class="isJammed ? 'danger' : 'ok'">
              {{ isJammed ? '全频段阻塞 (JAMMED)' : '正常 (ACTIVE)' }}
            </div>
            <button class="jam-btn" @click="toggleJamming">
              {{ isJammed ? '解除封锁' : '发射干扰波' }}
            </button>
          </div>
        </div>
      </NTabPane>

    </NTabs>
  </div>
</template>

<style scoped>
.sector-w {
  height: 100%;
  min-height: 0;
  background: #000;
  color: #e0e0e0;
  font-family: 'Arial', sans-serif;
  display: flex;
  flex-direction: column;
}

.header {
  padding: 1rem 2rem;
  border-bottom: 1px solid #333;
  background: #0a0a0a;
}

.title {
  margin: 0;
  color: #00ffff;
  font-family: monospace;
  letter-spacing: 2px;
}

.subtitle {
  color: #666;
  font-size: 0.8rem;
}

.w-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* Tab 1: 3D */
.scene-3d {
  width: 100%;
  flex: 1;
  min-height: 0;
  position: relative;
}

/* 水滴航程：主玩法面板 */
.journey-panel {
  position: absolute;
  top: 1rem;
  left: 1rem;
  right: auto;
  max-width: 320px;
  background: rgba(0, 0, 0, 0.75);
  border: 1px solid rgba(0, 255, 255, 0.35);
  color: #e0e0e0;
  padding: 1rem;
  font-family: monospace;
  z-index: 10;
  border-radius: 6px;
}

.journey-title {
  margin: 0 0 0.4rem;
  font-size: 1rem;
  color: #00ffff;
  letter-spacing: 0.05em;
}

.journey-desc {
  margin: 0 0 0.75rem;
  font-size: 0.8rem;
  color: #9ab;
  line-height: 1.45;
}

.journey-current {
  margin-bottom: 0.75rem;
  padding: 0.5rem 0.6rem;
  background: rgba(0, 40, 50, 0.3);
  border-radius: 4px;
  border-left: 3px solid #00ffff;
}

.journey-label {
  font-size: 0.7rem;
  color: #7a9;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.journey-name {
  font-size: 1.05rem;
  font-weight: 600;
  color: #fff;
  margin: 0.2rem 0 0.25rem;
}

.journey-detail {
  font-size: 0.8rem;
  margin-bottom: 0.5rem;
}

.journey-nav {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.journey-btn {
  appearance: none;
  border: 1px solid #00ffff;
  background: transparent;
  color: #00ffff;
  padding: 0.25rem 0.6rem;
  font-size: 0.8rem;
  font-family: monospace;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s;
}

.journey-btn:hover:not(:disabled) {
  background: rgba(0, 255, 255, 0.15);
}

.journey-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.journey-progress {
  font-size: 0.75rem;
  color: #8ab;
}

.waypoint-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.waypoint-chip {
  appearance: none;
  border: 1px solid #334;
  background: rgba(0, 20, 30, 0.5);
  color: #9ab;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  font-family: monospace;
  cursor: pointer;
  border-radius: 4px;
  transition: border-color 0.2s, color 0.2s, background 0.2s;
}

.waypoint-chip:hover {
  border-color: #00ffff;
  color: #00ffff;
  background: rgba(0, 255, 255, 0.08);
}

.waypoint-chip.active {
  border-color: #00ffff;
  color: #00ffff;
  background: rgba(0, 255, 255, 0.2);
}

.hud-overlay {
  position: absolute;
  bottom: 2rem;
  left: 2rem;
  background: rgba(0,0,0,0.5);
  padding: 1rem;
  border: 1px solid #00ffff;
  color: #00ffff;
  font-family: monospace;
}

.data-row { margin-bottom: 0.5rem; }
.data-row.highlight .label { color: #00ff88; }
.label { opacity: 0.7; margin-right: 1rem; }
.val { color: #00ffff; }
.reason { color: #8ab; font-size: 0.8rem; }
.hint-text { margin-top: 0.5rem; font-size: 0.75rem; opacity: 0.8; }

/* Tab 2: Game */
.game-container {
  position: relative;
  width: 800px;
  height: 500px;
  margin: 2rem auto;
  border: 2px solid #333;
  background: #050510;
  overflow: hidden;
}

.game-header {
  position: absolute;
  top: 0; left: 0; right: 0;
  padding: 0.5rem;
  background: rgba(0,255,255,0.1);
  display: flex;
  justify-content: space-between;
  color: #00ffff;
  font-family: monospace;
  z-index: 10;
}

.strike-canvas {
  position: absolute;
  top: 0; left: 0;
  z-index: 5;
  cursor: crosshair;
}

.ship {
  position: absolute;
  width: 6px; height: 6px;
  background: #fff;
  border-radius: 50%;
  box-shadow: 0 0 5px #fff;
  transition: all 0.2s;
}

.ship.destroyed {
  background: transparent;
  box-shadow: none;
}

.explosion {
  font-size: 20px;
  position: absolute;
  transform: translate(-50%, -50%);
  animation: fadeOut 1s forwards;
}

@keyframes fadeOut { to { opacity: 0; transform: scale(2); } }

/* Tab 3: Blockade */
.blockade-ui {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 2rem;
}

.sun-view {
  width: 300px;
  height: 300px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sun-core {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: radial-gradient(circle, #ffd700, #ff8c00, #ff4500);
  box-shadow: 0 0 50px #ff8c00;
  z-index: 1;
}

.droplet-silhouette {
  width: 20px;
  height: 30px;
  background: #000;
  border: 1px solid #fff; /* Rim light */
  border-radius: 50% 50% 5px 5px;
  position: absolute;
  z-index: 2;
}

.waves .wave {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  border: 2px solid rgba(255, 255, 0, 0.5);
  border-radius: 50%;
  width: 220px; height: 220px;
  animation: ripple 2s infinite;
}

.jammed .waves .wave {
  display: none;
}

.jammed .sun-core {
  filter: grayscale(0.8) brightness(0.5);
  box-shadow: none;
}

.controls {
  text-align: center;
}

.status {
  font-size: 1.5rem;
  margin: 1rem 0;
  font-family: monospace;
}
.ok { color: #00ff00; }
.danger { color: #ff0000; }

.jam-btn {
  padding: 1rem 2rem;
  background: transparent;
  border: 1px solid #00ffff;
  color: #00ffff;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.3s;
}
.jam-btn:hover { background: rgba(0,255,255,0.1); }

@keyframes ripple {
  0% { width: 220px; height: 220px; opacity: 1; }
  100% { width: 400px; height: 400px; opacity: 0; }
}

:deep(.n-tabs-nav) { background: #111; }
:deep(.n-tabs-tab) { color: #888; }
:deep(.n-tabs-tab--active) { color: #00ffff; font-weight: bold; }
:deep(.n-tabs-pane-wrapper) { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
:deep(.n-tab-pane) { flex: 1; display: flex; flex-direction: column; height: 100%; width: 100%; }

@media (max-width: 640px) {
  .journey-panel {
    max-width: calc(100% - 2rem);
    top: 0.5rem;
    left: 0.5rem;
    padding: 0.75rem;
  }
  .journey-title { font-size: 0.9rem; }
  .waypoint-chip { font-size: 0.7rem; padding: 0.2rem 0.4rem; }
}
</style>
