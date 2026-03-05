<script setup lang="ts">
/**
 * Sector J: Bunker World (掩体世界)
 * 核心：太空城全景 (City Viewer), 阴影躲避 (Shadow Sim), 光粒预警 (Photoid Alert)
 * 风格：工业科幻，橙色警示风
 */
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import { NTabs, NTabPane, NProgress, NSelect, useMessage } from 'naive-ui'
import { soundManager } from '@/utils/sound'
import { TresCanvas } from '@tresjs/core'
import { OrbitControls, Stars } from '@tresjs/cientos'
import ShadowSimBodies from '@/components/ShadowSimBodies.vue'

const message = useMessage()
const activeTab = ref('city') 

// --- 1. Space City Viewer (3D) ---
const selectedCity = ref('asia1')
const cityOptions = [
  { label: '亚洲一号 (Asia I) - 轮辐式 (Wheel)', value: 'asia1' },
  { label: '北美一号 (North America I) - 滚筒式 (Cylinder)', value: 'na1' },
  { label: '欧洲三号 (Europe III) - 组合式 (Composite)', value: 'eu3' },
  { label: '太平洋一号 (Pacific I) - 环形 (Ring)', value: 'pac1' }
]

const cityMeta: Record<string, { orbit: string; type: string; desc: string }> = {
  asia1: { orbit: 'JUPITER L5', type: '轮辐式 WHEEL', desc: '经典奥尼尔圆环，离心重力' },
  na1: { orbit: 'SATURN L4', type: '滚筒式 CYLINDER', desc: '长筒自转，内壁地表' },
  eu3: { orbit: 'JUPITER L4', type: '组合式 COMPOSITE', desc: '多舱段组合体' },
  pac1: { orbit: 'NEPTUNE L5', type: '环形 RING', desc: '细环结构，轻量殖民' }
}

const currentCityMeta = computed(() => cityMeta[selectedCity.value] ?? null)

const cityViewMode = ref<'exterior' | 'interior'>('exterior')

const cityStats = reactive({
  population: 25000000,
  gravity: 0.98,
  oxygen: 99.8,
  energy: 85.4,
  hull: 100
})

setInterval(() => {
  cityStats.energy = 80 + Math.random() * 20
  cityStats.oxygen = 99 + Math.random()
}, 3000)

// 3D City Config (args: torus [radius, tube, radialSegments, tubularSegments] | cylinder [radiusTop, radiusBottom, height, radialSegments, heightSegments, openEnded])
const cityConfig = computed(() => {
  switch (selectedCity.value) {
    case 'asia1': // Wheel
      return { type: 'torus' as const, args: [10, 3, 16, 100] as [number, number, number, number], color: '#aaa', wireframe: false, rotSpeed: 0.2 }
    case 'na1': // Cylinder
      return { type: 'cylinder' as const, args: [5, 5, 20, 32, 1, true] as [number, number, number, number, number, boolean], color: '#8899aa', wireframe: false, rotSpeed: 0.1 }
    case 'eu3': // Composite
      return { type: 'torus' as const, args: [8, 2, 16, 50] as [number, number, number, number], color: '#d4af37', wireframe: true, rotSpeed: 0.15 }
    case 'pac1': // Ring
      return { type: 'torus' as const, args: [12, 1, 16, 100] as [number, number, number, number], color: '#00ccff', wireframe: false, rotSpeed: 0.05 }
    default:
      return { type: 'torus' as const, args: [10, 3, 16, 100] as [number, number, number, number], color: '#aaa', wireframe: false, rotSpeed: 0.1 }
  }
})

const cityEmissiveIntensity = computed(() => (cityViewMode.value === 'interior' ? 0.15 : 0))
const cityEmissive = computed(() => (cityViewMode.value === 'interior' ? '#0a331a' : '#111'))

// Auto-rotate logic would be handled inside the template via ref or simple rotation prop if supported,
// or we can use useRenderLoop inside a sub-component. For simplicity, we use simple reactive rotation here.
const rotation = reactive({ x: 0, y: 0, z: 0 })
let rotateFrame: number
function animateCity() {
  if (activeTab.value !== 'city') {
    rotateFrame = requestAnimationFrame(animateCity)
    return
  }
  if (cityViewMode.value === 'exterior') {
    rotation.y += 0.005 * (cityConfig.value.rotSpeed * 5)
    rotation.z += 0.01 * (cityConfig.value.rotSpeed * 5)
  } else {
    rotation.z += 0.002
  }
  rotateFrame = requestAnimationFrame(animateCity)
}

// Watch view mode to reset camera/rotation logic if needed
watch(cityViewMode, (mode) => {
  if (mode === 'interior') {
    message.info('切换至内景视角：模拟离心重力环境')
  }
})

// --- 2. Shadow Hiding Sim ---
const gameActive = ref(true)
const timeSpeed = ref(1)
const exposureTime = ref(0)
const shadowSimTick = ref(0)

// Celestial Bodies
interface Body {
  id: string, name: string, distance: number, radius: number, angle: number, speed: number, color: string, shadowWidth: number
}

const sun = { x: 0, y: 300, r: 40 }
const planets = reactive<Body[]>([
  { id: 'jupiter', name: 'JUPITER', distance: 250, radius: 35, angle: 0, speed: 0.002, color: '#d4a373', shadowWidth: 0.35 },
  { id: 'saturn', name: 'SATURN', distance: 400, radius: 28, angle: 2, speed: 0.0015, color: '#f4e4bc', shadowWidth: 0.28 },
  { id: 'uranus', name: 'URANUS', distance: 550, radius: 20, angle: 4, speed: 0.001, color: '#73d7ee', shadowWidth: 0.2 },
  { id: 'neptune', name: 'NEPTUNE', distance: 700, radius: 18, angle: 5, speed: 0.0008, color: '#5b5ddf', shadowWidth: 0.18 }
])

interface City {
  id: string, label: string, x: number, y: number, planetId: string, angleOffset: number, orbitRadius: number, exposed: boolean
}

const cities = reactive<City[]>([
  { id: 'c1', label: 'Asia I', x: 0, y: 0, planetId: 'jupiter', angleOffset: Math.PI, orbitRadius: 50, exposed: false },
  { id: 'c2', label: 'NA I', x: 0, y: 0, planetId: 'saturn', angleOffset: Math.PI + 0.2, orbitRadius: 45, exposed: false },
  { id: 'c3', label: 'Europe III', x: 0, y: 0, planetId: 'jupiter', angleOffset: Math.PI - 0.2, orbitRadius: 60, exposed: false },
  { id: 'c4', label: 'Gravity', x: 0, y: 0, planetId: 'uranus', angleOffset: Math.PI, orbitRadius: 40, exposed: false }
])

let animationFrame: number
let shadowSimInterval: ReturnType<typeof setInterval> | undefined

// 3D 比例：放大以便看清行星与太空城运动
const SHADOW_SCALE = 0.15
const SUN_RADIUS_3D = 4
const PLANET_RADIUS_SCALE = 0.2
const CITY_ORBIT_SCALE = 0.15

const planets3d = computed(() =>
  planets.map((p) => ({
    ...p,
    x: p.distance * SHADOW_SCALE * Math.cos(p.angle),
    y: 0,
    z: p.distance * SHADOW_SCALE * Math.sin(p.angle),
    r3d: p.radius * PLANET_RADIUS_SCALE
  }))
)

const cities3d = computed(() =>
  cities.map((c) => {
    const parent = planets.find((p) => p.id === c.planetId)!
    const px = parent.distance * SHADOW_SCALE * Math.cos(parent.angle)
    const pz = parent.distance * SHADOW_SCALE * Math.sin(parent.angle)
    const absAngle = parent.angle + c.angleOffset
    const orbitR = c.orbitRadius * CITY_ORBIT_SCALE
    return {
      ...c,
      x: px + orbitR * Math.cos(absAngle),
      y: 0,
      z: pz + orbitR * Math.sin(absAngle)
    }
  })
)

function tickShadowSim() {
  if (!gameActive.value) return
  planets.forEach(p => {
    p.angle += p.speed * timeSpeed.value
  })
  cities.forEach(c => {
    const parent = planets.find(p => p.id === c.planetId)!
    const parentX = sun.x + Math.cos(parent.angle) * parent.distance
    const parentY = sun.y + Math.sin(parent.angle) * parent.distance
    const absAngle = parent.angle + c.angleOffset
    c.x = parentX + Math.cos(absAngle) * c.orbitRadius
    c.y = parentY + Math.sin(absAngle) * c.orbitRadius
    let normOffset = c.angleOffset % (2 * Math.PI)
    if (normOffset < 0) normOffset += 2 * Math.PI
    if (Math.random() < 0.05) {
      c.angleOffset += (Math.random() - 0.5) * 0.02
    }
    const distFromSafe = Math.abs(normOffset - Math.PI)
    c.exposed = distFromSafe >= parent.shadowWidth
  })
  if (cities.some(c => c.exposed)) {
    exposureTime.value += 0.5
  } else {
    exposureTime.value = Math.max(0, exposureTime.value - 0.2)
  }
  shadowSimTick.value++
}

function updatePositions() {
  if (gameActive.value && activeTab.value === 'shadow') {
    tickShadowSim()
  }
  animationFrame = requestAnimationFrame(updatePositions)
}

watch(activeTab, (tab) => {
  if (shadowSimInterval) {
    clearInterval(shadowSimInterval)
    shadowSimInterval = undefined
  }
  if (tab === 'shadow') {
    tickShadowSim()
    shadowSimInterval = setInterval(tickShadowSim, 50)
  }
})

// --- 3. Photoid Alert System (Doomsday Radar) ---
const isStriking = ref(false)
const strikeTime = ref(0)
const shockwaveRadius = ref(0)
const impactLogs = ref<{time: string, msg: string, type: 'info'|'warn'|'crit'}[]>([
  { time: '00:00:00', msg: 'SYSTEM_INIT: EARLY_WARNING_NETWORK', type: 'info' },
  { time: '00:00:01', msg: 'SENSORS: NOMINAL', type: 'info' }
])

const planetDists = {
  jupiter: 43,
  saturn: 79,
  uranus: 159,
  neptune: 250
}

const SIM_SPEED = 5 

let alertTimer: ReturnType<typeof setInterval> | undefined

function addLog(msg: string, type: 'info'|'warn'|'crit' = 'info') {
  const now = new Date()
  const ts = `${now.getHours().toString().padStart(2,'0')}:${now.getMinutes().toString().padStart(2,'0')}:${now.getSeconds().toString().padStart(2,'0')}`
  impactLogs.value.unshift({ time: ts, msg, type })
  if (impactLogs.value.length > 20) impactLogs.value.pop()
}

function startStrike() {
  if (isStriking.value) return
  isStriking.value = true
  shockwaveRadius.value = 0
  strikeTime.value = 0
  
  addLog('WARNING: GRAVITATIONAL WAVE DETECTED', 'warn')
  addLog('PHOTOID IMPACT ON SUN CONFIRMED', 'crit')
  message.error('警报：光粒已击中太阳！激波正在扩散！')
  soundManager.playAlert()
  
  alertTimer = setInterval(() => {
    strikeTime.value += 0.1 // seconds
    shockwaveRadius.value += 0.1 * SIM_SPEED 
    
    Object.entries(planetDists).forEach(([p, dist]) => {
      if (Math.abs(shockwaveRadius.value - dist) < 1) {
        addLog(`IMPACT ALERT: ${p.toUpperCase()} SECTOR HIT`, 'crit')
        soundManager.playBigCrunch()
      }
    })
    
    if (shockwaveRadius.value > 300) {
      clearInterval(alertTimer)
      isStriking.value = false
      addLog('SIMULATION ENDED. SOLAR SYSTEM DESTROYED.', 'info')
    }
  }, 100)
}

function getCountdown(planetDist: number) {
  if (!isStriking.value) return '--:--'
  const distRemaining = planetDist - shockwaveRadius.value
  if (distRemaining <= 0) return 'IMPACTED'
  
  const secondsLeft = distRemaining / (0.1 * SIM_SPEED) * 0.1
  return secondsLeft.toFixed(1) + 's'
}

onMounted(() => {
  updatePositions()
  animateCity()
  if (activeTab.value === 'shadow') {
    tickShadowSim()
    shadowSimInterval = setInterval(tickShadowSim, 50)
  }
})

onUnmounted(() => {
  cancelAnimationFrame(animationFrame)
  cancelAnimationFrame(rotateFrame)
  clearInterval(alertTimer)
  if (shadowSimInterval) clearInterval(shadowSimInterval)
})

</script>

<template>
  <div class="sector-j">
    <header class="header">
      <h1 class="title">SECTOR J // BUNKER WORLD</h1>
      <div class="subtitle">掩体纪元：木星庇护所群</div>
    </header>

    <NTabs type="segment" v-model:value="activeTab" class="j-tabs">
      
      <!-- Tab 1: City Viewer -->
      <NTabPane name="city" tab="太空城全景 (CITY VIEWER)">
        <div class="city-viewer">
          <aside class="viewer-sidebar">
            <div class="selector-group">
              <span class="selector-label">选择太空城 (SELECT COLONY)</span>
              <NSelect v-model:value="selectedCity" :options="cityOptions" />
            </div>
            <div class="city-meta" v-if="currentCityMeta">
              <div class="meta-orbit">ORBIT: {{ currentCityMeta.orbit }}</div>
              <div class="meta-type">{{ currentCityMeta.type }}</div>
              <div class="meta-desc">{{ currentCityMeta.desc }}</div>
            </div>
            <div class="city-stats">
              <h4>生存指数 (HABITABILITY)</h4>
              <div class="stat-row">
                <span>GRAVITY</span>
                <NProgress type="line" :percentage="selectedCity === 'asia1' ? cityStats.gravity * 100 : 90" color="#ffaa00" rail-color="#332211" :show-indicator="false" />
                <span class="val">{{ selectedCity === 'asia1' ? cityStats.gravity : 0.9 }}G</span>
              </div>
              <div class="stat-row">
                <span>OXYGEN</span>
                <NProgress type="line" :percentage="cityStats.oxygen" color="#00ff41" rail-color="#332211" :show-indicator="false" />
                <span class="val">{{ cityStats.oxygen.toFixed(1) }}%</span>
              </div>
              <div class="stat-row">
                <span>ENERGY</span>
                <NProgress type="line" :percentage="cityStats.energy" color="#00ccff" rail-color="#332211" :show-indicator="false" />
                <span class="val">{{ cityStats.energy.toFixed(1) }}%</span>
              </div>
              <div class="stat-row">
                <span>HULL</span>
                <NProgress type="line" :percentage="cityStats.hull" color="#ff3333" rail-color="#332211" :show-indicator="false" />
                <span class="val">OK</span>
              </div>
            </div>
            <div class="view-switch">
              <button :class="{ active: cityViewMode === 'exterior' }" @click="cityViewMode = 'exterior'">外观 (EXTERIOR)</button>
              <button :class="{ active: cityViewMode === 'interior' }" @click="cityViewMode = 'interior'">内景 (INTERIOR)</button>
            </div>
          </aside>
          <div class="viewport-wrap">
            <div class="viewport">
              <TresCanvas clear-color="#0a0806" class="city-canvas">
                <TresPerspectiveCamera :position="cityViewMode === 'exterior' ? [22, 18, 22] : [0, 0, 8]" :look-at="[0, 0, 0]" />
                <OrbitControls :enable-zoom="true" :auto-rotate="false" />
                <Stars :radius="120" :depth="60" :count="6000" :size="0.4" :color="null" />
                <TresAmbientLight :intensity="0.4" />
                <TresDirectionalLight :position="[10, 10, 10]" :intensity="1.2" />
                <TresDirectionalLight :position="[-8, 5, -8]" :intensity="0.5" color="#ffaa33" />
                <TresMesh :rotation-x="rotation.x" :rotation-y="rotation.y" :rotation-z="rotation.z">
                  <TresTorusGeometry v-if="cityConfig.type === 'torus'" :args="cityConfig.args" />
                  <TresCylinderGeometry v-if="cityConfig.type === 'cylinder'" :args="cityConfig.args" />
                  <TresMeshStandardMaterial
                    :color="cityConfig.color"
                    :wireframe="cityConfig.wireframe || cityViewMode === 'interior'"
                    :roughness="0.35"
                    :metalness="0.75"
                    :emissive="cityEmissive"
                    :emissiveIntensity="cityEmissiveIntensity"
                  />
                </TresMesh>
                <TresMesh v-if="cityConfig.type === 'torus'" :rotation-x="rotation.x" :rotation-y="rotation.y" :rotation-z="rotation.z">
                  <TresSphereGeometry :args="[2, 32, 32]" />
                  <TresMeshStandardMaterial color="#444" :metalness="0.8" :roughness="0.4" />
                </TresMesh>
                <TresGroup v-if="cityConfig.type === 'torus'" :rotation-x="rotation.x" :rotation-y="rotation.y" :rotation-z="rotation.z">
                  <TresMesh v-for="idx in 3" :key="idx" :rotation-x="0" :rotation-y="0" :rotation-z="(idx - 1) * 2.09">
                    <TresCylinderGeometry :args="[0.5, 0.5, 10, 8]" :position="[0, 5, 0]" />
                    <TresMeshStandardMaterial color="#333" :metalness="0.7" :roughness="0.5" />
                  </TresMesh>
                </TresGroup>
              </TresCanvas>
              <div class="viewport-vignette" aria-hidden="true"></div>
              <div class="overlay-data">
                <p class="hud-line">ID: {{ selectedCity.toUpperCase() }}</p>
                <p class="hud-line">ORBIT: {{ currentCityMeta?.orbit ?? '--' }}</p>
                <p class="hud-line status">STATUS: OPERATIONAL</p>
              </div>
            </div>
          </div>
        </div>
      </NTabPane>

      <!-- Tab 2: Shadow Sim (3D) -->
      <NTabPane name="shadow" tab="阴影躲避 (SHADOW SIM)">
        <div class="sim-container">
          <div class="sim-header">
            <div class="sim-status" :class="{ danger: exposureTime > 0 }">
              暴露风险 (RISK): {{ Math.min(100, exposureTime).toFixed(1) }}%
            </div>
            <div class="hint-top">拖动滑块使太空城保持在行星背阳面阴影中 · 可旋转/缩放视角</div>
          </div>
          <div class="shadow-scene-3d" :data-tick="shadowSimTick">
            <TresCanvas clear-color="#0a0a0f" class="shadow-canvas">
              <TresPerspectiveCamera :position="[0, 45, 45]" :look-at="[0, 0, 0]" />
              <OrbitControls :enable-zoom="true" :min-distance="20" :max-distance="120" />
              <TresAmbientLight :intensity="0.3" />
              <TresDirectionalLight :position="[0, 30, 0]" :intensity="1" color="#ffaa66" />
              <TresMesh :position="[0, 0, 0]">
                <TresSphereGeometry :args="[SUN_RADIUS_3D, 32, 32]" />
                <TresMeshBasicMaterial color="#ffaa33" />
              </TresMesh>
              <TresPointLight :position="[0, 0, 0]" :intensity="1.5" :distance="150" color="#ffcc88" />
              <!-- 轨道环（静态） -->
              <TresMesh v-for="p in planets3d" :key="'ring-' + p.id" :position="[0, 0, 0]" :rotation-x="-Math.PI/2" rotation-y="0" rotation-z="0">
                <TresRingGeometry :args="[p.distance * SHADOW_SCALE - 0.8, p.distance * SHADOW_SCALE + 0.8, 64]" />
                <TresMeshBasicMaterial color="#332211" transparent :opacity="0.5" />
              </TresMesh>
              <!-- 行星与太空城：由子组件在渲染循环中每帧同步位置 -->
              <ShadowSimBodies :planets3d="planets3d" :cities3d="cities3d" />
            </TresCanvas>
          </div>
          <div class="sim-controls">
            <div v-for="c in cities" :key="c.id" class="control-row">
              <div class="row-header">
                <label :class="{ 'text-danger': c.exposed }">{{ c.label }} {{ c.exposed ? '[EXPOSED]' : '[HIDDEN]' }}</label>
                <span class="drift-val">DEV: {{ (c.angleOffset - Math.PI).toFixed(2) }}</span>
              </div>
              <input type="range" v-model.number="c.angleOffset" min="0" max="6.28" step="0.01" class="orbit-slider" />
            </div>
          </div>
        </div>
      </NTabPane>

      <!-- Tab 3: Alert System (Doomsday Radar) -->
      <NTabPane name="alert" tab="光粒预警 (DOOMSDAY RADAR)">
        <div class="radar-container" :class="{ 'red-alert': isStriking }">
          <div class="radar-main">
            <div class="radar-screen">
              <!-- Sun Center -->
              <div class="radar-sun" :class="{ 'sun-explode': isStriking }"></div>
              
              <!-- Orbits -->
              <div class="radar-orbit" style="width: 150px; height: 150px"></div> <!-- Jupiter -->
              <div class="radar-orbit" style="width: 250px; height: 250px"></div> <!-- Saturn -->
              <div class="radar-orbit" style="width: 350px; height: 350px"></div> <!-- Uranus -->
              <div class="radar-orbit" style="width: 450px; height: 450px"></div> <!-- Neptune -->
              
              <!-- Shockwave -->
              <div 
                v-if="isStriking" 
                class="shockwave" 
                :style="{ width: shockwaveRadius * 3 + 'px', height: shockwaveRadius * 3 + 'px' }"
              ></div>
              
              <!-- Planet Markers -->
              <div class="planet-marker" style="top: 50%; left: calc(50% + 75px)">JUP</div>
              <div class="planet-marker" style="top: 50%; left: calc(50% + 125px)">SAT</div>
              <div class="planet-marker" style="top: 50%; left: calc(50% + 175px)">URA</div>
              <div class="planet-marker" style="top: 50%; left: calc(50% + 225px)">NEP</div>
            </div>
            
            <div class="radar-data">
              <h3>生存倒计时 (T-MINUS)</h3>
              <div class="countdown-grid">
                <div class="count-item" v-for="(dist, p) in planetDists" :key="p">
                  <span class="label">{{ p.toUpperCase() }}</span>
                  <span class="time" :class="{ 'impacted': getCountdown(dist) === 'IMPACTED' }">
                    {{ getCountdown(dist) }}
                  </span>
                </div>
              </div>
              <div class="alert-actions">
                 <button class="trigger-btn" @click="startStrike" :disabled="isStriking">
                   {{ isStriking ? 'IMPACT SEQUENCE RUNNING' : '模拟光粒打击 (SIMULATE PHOTOID)' }}
                 </button>
              </div>
            </div>
          </div>
          
          <div class="radar-logs">
            <div v-for="(log, i) in impactLogs" :key="i" class="log-entry" :class="log.type">
              <span class="log-time">[{{ log.time }}]</span> {{ log.msg }}
            </div>
          </div>
        </div>
      </NTabPane>

    </NTabs>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

.sector-j {
  min-height: 0;
  flex: 1;
  background: #15100a;
  color: #ffaa00;
  font-family: 'Share Tech Mono', monospace;
  display: flex;
  flex-direction: column;
}

.header {
  padding: 1rem 2rem;
  border-bottom: 2px solid #ffaa00;
  background: #2a2018;
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.title { margin: 0; letter-spacing: 2px; font-size: 1.5rem; }
.subtitle { color: #886644; font-size: 0.9rem; }

.j-tabs { flex: 1; display: flex; flex-direction: column; }
:deep(.n-tabs-pane-wrapper) { flex: 1; display: flex; flex-direction: column; min-height: 0; }
:deep(.n-tab-pane) { flex: 1; display: flex; flex-direction: column; min-height: 0; }

/* City Viewer Layout */
.city-viewer {
  flex: 1;
  display: flex;
  padding: 1rem;
  gap: 1rem;
  overflow: hidden;
}

.viewer-sidebar {
  width: 300px;
  min-width: 280px;
  flex-shrink: 0;
  min-height: 200px;
  overflow-y: auto;
  background: #221a15;
  border: 1px solid #554433;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  position: relative;
  z-index: 2;
}

.selector-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.selector-label {
  display: block;
  margin: 0;
  color: #aa8844;
  font-size: 0.9rem;
  font-weight: 600;
  line-height: 1.3;
}

.city-meta {
  padding: 0.6rem 0;
  border-bottom: 1px solid #332211;
  flex-shrink: 0;
}
.meta-orbit {
  color: #00cc88;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
  margin-bottom: 0.35rem;
}
.meta-type { color: #ffaa00; font-size: 0.85rem; font-weight: bold; margin-bottom: 0.25rem; }
.meta-desc { color: #a09080; font-size: 0.8rem; line-height: 1.4; }

.city-stats h4 { margin: 0 0 1rem 0; color: #ffaa00; border-bottom: 1px solid #554433; padding-bottom: 0.5rem; }
.stat-row { display: flex; align-items: center; margin-bottom: 0.8rem; gap: 0.5rem; font-size: 0.8rem; }
.stat-row span:first-child { width: 60px; }
.stat-row .n-progress { flex: 1; }
.stat-row .val { width: 50px; text-align: right; font-weight: bold; color: #ccc; }

.view-switch { display: flex; gap: 0.5rem; }
.view-switch button {
  flex: 1;
  background: transparent;
  border: 1px solid #554433;
  color: #886644;
  padding: 0.5rem;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s;
}
.view-switch button.active { background: #ffaa00; color: #000; font-weight: bold; }

.viewport-wrap {
  flex: 1;
  min-width: 320px;
  min-height: 380px;
  display: flex;
  flex-direction: column;
}

.viewport {
  flex: 1;
  min-height: 360px;
  background: #0a0806;
  border: 1px solid #554433;
  position: relative;
  overflow: hidden;
  border-radius: 2px;
  box-shadow: inset 0 0 80px rgba(0,0,0,0.6);
}
/* TresCanvas 不用 window-size，避免 fixed 全屏盖住侧栏 */
.viewport :deep(.city-canvas),
.viewport :deep(canvas) {
  display: block;
  width: 100%;
  height: 100%;
  position: absolute;
  inset: 0;
}

.viewport-vignette {
  position: absolute;
  inset: 0;
  pointer-events: none;
  border-radius: inherit;
  box-shadow: inset 0 0 120px 20px rgba(0,0,0,0.5);
}

.overlay-data {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  text-align: right;
  color: #00ff41;
  font-size: 0.75rem;
  letter-spacing: 1px;
  text-shadow: 0 0 8px rgba(0,255,65,0.4);
  pointer-events: none;
  padding: 0.5rem 0.75rem;
  background: linear-gradient(90deg, transparent 0%, rgba(0,0,0,0.7) 30%);
  border-left: 2px solid rgba(0,255,65,0.3);
}

.overlay-data .hud-line { margin: 0.2rem 0; }
.overlay-data .hud-line.status { color: #00cc88; }

/* Shadow Sim (3D) */
.sim-container { display: flex; flex-direction: column; flex: 1; min-height: 0; }
.sim-header { padding: 0.75rem 1rem; background: #221a15; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #554433; flex-shrink: 0; }
.sim-status { font-size: 1.2rem; font-weight: bold; color: #00ff41; }
.sim-status.danger { color: #ff3333; animation: blink 1s infinite; }
.hint-top { color: #886644; font-size: 0.85rem; }
.shadow-scene-3d {
  flex: 1;
  min-height: 320px;
  position: relative;
  background: #0a0a0f;
  border: 1px solid #332211;
}
.shadow-scene-3d .shadow-canvas,
.shadow-scene-3d :deep(canvas) {
  display: block;
  width: 100%;
  height: 100%;
  position: absolute;
  inset: 0;
}
.sim-controls { padding: 1rem; background: #221a15; display: flex; flex-direction: column; gap: 1rem; border-top: 1px solid #554433; flex-shrink: 0; }
.control-row { display: flex; flex-direction: column; background: rgba(0,0,0,0.2); padding: 0.5rem; border: 1px solid #332211; }
.row-header { display: flex; justify-content: space-between; margin-bottom: 0.2rem; font-size: 0.8rem; }
.text-danger { color: #ff3333; }
.blink { animation: blink 0.5s infinite; }
.orbit-slider { width: 100%; }

/* Radar (Simplified) */
.radar-container { flex: 1; display: flex; flex-direction: column; padding: 1rem; gap: 1rem; background: #111; transition: background 0.5s; }
.radar-container.red-alert { background: #220000; box-shadow: inset 0 0 50px #ff0000; }
.radar-main { flex: 2; display: flex; gap: 1rem; }
.radar-screen { flex: 1; background: radial-gradient(circle, #222 0%, #000 100%); border: 2px solid #333; border-radius: 50%; position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center; aspect-ratio: 1; max-height: 500px; }
.red-alert .radar-screen { border-color: #ff0000; box-shadow: 0 0 20px rgba(255,0,0,0.3); }
.radar-sun { width: 10px; height: 10px; background: #fff; border-radius: 50%; position: absolute; z-index: 10; }
.sun-explode { animation: explode 0.5s infinite alternate; box-shadow: 0 0 20px #ffaa00; }
.radar-orbit { position: absolute; border: 1px dashed rgba(255, 255, 255, 0.2); border-radius: 50%; }
.shockwave { position: absolute; border: 2px solid #ff3333; border-radius: 50%; background: rgba(255, 50, 50, 0.1); transform: translate(-50%, -50%); top: 50%; left: 50%; box-shadow: 0 0 10px #ff0000; }
.planet-marker { position: absolute; width: 4px; height: 4px; background: #00ff41; border-radius: 50%; font-size: 0.6rem; color: #ccc; transform: translate(-50%, -50%); }
.radar-data { width: 300px; background: #221a15; border: 1px solid #554433; padding: 1rem; display: flex; flex-direction: column; }
.countdown-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1rem 0; }
.count-item { background: #000; padding: 0.5rem; border: 1px solid #333; text-align: center; }
.count-item .label { display: block; font-size: 0.7rem; color: #888; margin-bottom: 0.2rem; }
.count-item .time { display: block; font-size: 1.2rem; color: #00ff41; }
.count-item .time.impacted { color: #ff0000; text-decoration: line-through; }
.trigger-btn { width: 100%; padding: 1rem; background: #aa2222; color: #fff; border: none; font-weight: bold; cursor: pointer; margin-top: auto; }
.trigger-btn:hover { background: #ff3333; }
.trigger-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.radar-logs { flex: 1; background: #000; border: 1px solid #333; padding: 1rem; font-family: monospace; overflow-y: auto; font-size: 0.8rem; height: 150px; }
.log-entry { margin-bottom: 0.3rem; border-bottom: 1px solid #111; padding-bottom: 0.2rem; }
.log-entry.crit { color: #ff3333; font-weight: bold; }

@keyframes explode { from { transform: scale(1); opacity: 1; } to { transform: scale(3); opacity: 0.8; } }
@keyframes blink { 50% { opacity: 0.5; } }
</style>
