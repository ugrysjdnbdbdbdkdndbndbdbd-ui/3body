<script setup lang="ts">
/**
 * Sector L: Curvature Propulsion (曲率驱动)
 * 核心：折纸船隐喻 (Origami), 相对论航行 (Relativistic Flight), 黑域生成 (Black Domain)
 * 风格：梦幻流体，粒子光效，相对论视觉畸变
 */
import { ref, onMounted, onUnmounted, computed, reactive, watch } from 'vue'
import { NTabs, NTabPane, useMessage } from 'naive-ui'
import { soundManager } from '@/utils/sound'
import { useUserStore } from '@/stores/user'

const message = useMessage()
const userStore = useUserStore()
const activeTab = ref('domain') // Default to the main game

// --- 1. Origami Boat (Metaphor) ---
const boatSpeed = ref(1)
const isSoapDropped = ref(false)

const canDropSoap = computed(() => userStore.checkPermission(2, '修改物理常量 (Alter Physics Constants)'))

function dropSoap() {
  if (isSoapDropped.value) return
  if (!canDropSoap.value) {
    message.warning('需面壁者权限方可投放肥皂，改变「水的张力」。')
    return
  }
  isSoapDropped.value = true
  boatSpeed.value = 5
  message.info('曲率驱动启动：空间张力差异产生推力')
  soundManager.playClick()
  setTimeout(() => {
    boatSpeed.value = 1
    isSoapDropped.value = false
  }, 3000)
}

// --- 2. Black Domain (The Game) ---
const domainCanvas = ref<HTMLCanvasElement | null>(null)
const domainCtx = ref<CanvasRenderingContext2D | null>(null)
// Physics state
const ship = reactive({ 
  x: 400, y: 300, 
  vx: 0, vy: 0, 
  angle: -Math.PI/2,
  thrust: 0 
})
const trails = ref<Array<{x: number, y: number, size: number, alpha: number}>>([])
const isDomainSafe = ref(false)
const lightSpeed = ref(300000) // c
const formationProgress = ref(0) // 0 to 1 animates the black domain forming

// Constants
const MAX_SPEED = 4 // Simulating "c" limit for gameplay
const FRICTION = 0.98

// Controls
const keys = reactive({ w: false, a: false, s: false, d: false })
const joystick = reactive({ active: false, dx: 0, dy: 0, originX: 0, originY: 0, curX: 0, curY: 0 })

function initDomain() {
  if (!domainCanvas.value) return
  domainCtx.value = domainCanvas.value.getContext('2d')
  
  // Resize canvas to fit container
  const resize = () => {
    if (domainCanvas.value) {
      domainCanvas.value.width = domainCanvas.value.parentElement?.clientWidth || 800
      domainCanvas.value.height = domainCanvas.value.parentElement?.clientHeight || 500
      // Reset ship center
      ship.x = domainCanvas.value.width / 2
      ship.y = domainCanvas.value.height * 0.8
    }
  }
  window.addEventListener('resize', resize)
  resize()

  window.addEventListener('keydown', handleKey)
  window.addEventListener('keyup', handleKey)
  domainLoop()
}

// Touch Logic
function handleTouchStart(e: TouchEvent) {
  if (activeTab.value !== 'domain') return
  e.preventDefault() // Prevent scroll
  const touch = e.touches[0]
  joystick.active = true
  joystick.originX = touch.clientX
  joystick.originY = touch.clientY
  joystick.curX = touch.clientX
  joystick.curY = touch.clientY
  joystick.dx = 0
  joystick.dy = 0
}

function handleTouchMove(e: TouchEvent) {
  if (!joystick.active) return
  e.preventDefault()
  const touch = e.touches[0]
  joystick.curX = touch.clientX
  joystick.curY = touch.clientY
  
  const deltaX = touch.clientX - joystick.originX
  const deltaY = touch.clientY - joystick.originY
  const maxDist = 50
  const dist = Math.hypot(deltaX, deltaY)
  
  const angle = Math.atan2(deltaY, deltaX)
  const force = Math.min(dist, maxDist) / maxDist
  
  joystick.dx = Math.cos(angle) * force
  joystick.dy = Math.sin(angle) * force
}

function handleTouchEnd() {
  joystick.active = false
  joystick.dx = 0
  joystick.dy = 0
}

function handleKey(e: KeyboardEvent) {
  const val = e.type === 'keydown'
  if (e.key === 'w' || e.key === 'ArrowUp') keys.w = val
  if (e.key === 'a' || e.key === 'ArrowLeft') keys.a = val
  if (e.key === 's' || e.key === 'ArrowDown') keys.s = val
  if (e.key === 'd' || e.key === 'ArrowRight') keys.d = val
}

function domainLoop() {
  if (!domainCtx.value || !domainCanvas.value) return
  const ctx = domainCtx.value
  const cvs = domainCanvas.value
  
  // --- Physics Update ---
  let turn = 0
  ship.thrust = 0
  
  if (keys.a) turn -= 0.08
  if (keys.d) turn += 0.08
  if (keys.w) ship.thrust = 0.15
  
  // Joystick Override
  if (joystick.active) {
    // Determine target angle
    const joyAngle = Math.atan2(joystick.dy, joystick.dx)
    let diff = joyAngle - ship.angle
    while (diff <= -Math.PI) diff += Math.PI*2
    while (diff > Math.PI) diff -= Math.PI*2
    
    // Smooth turn towards joystick direction
    if (Math.hypot(joystick.dx, joystick.dy) > 0.2) {
      if (Math.abs(diff) > 0.1) turn = Math.sign(diff) * 0.1
      ship.thrust = Math.hypot(joystick.dx, joystick.dy) * 0.15
    }
  }

  ship.angle += turn
  
  if (ship.thrust > 0) {
    ship.vx += Math.cos(ship.angle) * ship.thrust
    ship.vy += Math.sin(ship.angle) * ship.thrust
    
    // Add Trail Particle
    if (Math.random() > 0.3) {
      trails.value.push({
        x: ship.x - Math.cos(ship.angle) * 15,
        y: ship.y - Math.sin(ship.angle) * 15,
        size: 5 + Math.random() * 5,
        alpha: 0.6
      })
    }
  }
  
  // Friction & Limit
  ship.vx *= FRICTION
  ship.vy *= FRICTION
  const speed = Math.hypot(ship.vx, ship.vy)
  if (speed > MAX_SPEED) {
    ship.vx = (ship.vx / speed) * MAX_SPEED
    ship.vy = (ship.vy / speed) * MAX_SPEED
  }
  
  ship.x += ship.vx
  ship.y += ship.vy
  
  // Wrap around screen
  if (ship.x < 0) ship.x = cvs.width
  if (ship.x > cvs.width) ship.x = 0
  if (ship.y < 0) ship.y = cvs.height
  if (ship.y > cvs.height) ship.y = 0

  // --- Rendering ---
  
  // 1. Background (Deep Space or Black Domain)
  if (isDomainSafe.value) {
    // Transition to Black Domain
    if (formationProgress.value < 1) formationProgress.value += 0.01
    
    const darkAlpha = formationProgress.value
    ctx.fillStyle = `rgba(0, 0, 5, ${darkAlpha})`
    ctx.fillRect(0, 0, cvs.width, cvs.height)
    
    // Safe text
    if (formationProgress.value > 0.8) {
      ctx.fillStyle = 'rgba(0, 255, 0, 0.1)'
      ctx.font = '20px monospace'
      ctx.textAlign = 'center'
      ctx.fillText('SAFE ZONE ESTABLISHED', cvs.width/2, cvs.height/2)
    }
  } else {
    // Normal Space - Clear with fade for motion blur
    ctx.fillStyle = '#050510'
    ctx.fillRect(0, 0, cvs.width, cvs.height)
  }
  
  // 2. Star (The Sun)
  const starX = cvs.width / 2
  const starY = cvs.height / 2
  ctx.save()
  ctx.translate(starX, starY)
  const starRedshift = isDomainSafe.value ? 0.8 : 0
  ctx.fillStyle = isDomainSafe.value ? `rgb(100, 0, 0)` : '#ffd700'
  ctx.shadowBlur = isDomainSafe.value ? 5 : 50
  ctx.shadowColor = isDomainSafe.value ? '#500' : '#fc0'
  ctx.beginPath()
  ctx.arc(0, 0, 30, 0, Math.PI*2)
  ctx.fill()
  ctx.restore()
  
  // 3. Trails (Soap Bubbles / Space Distortion)
  ctx.save()
  // "Soap" effect: Screen blend mode + varying colors
  ctx.globalCompositeOperation = 'screen'
  
  for (let i = trails.value.length - 1; i >= 0; i--) {
    const p = trails.value[i]
    p.size += 0.1 // Expand
    p.alpha -= 0.002 // Fade very slowly (Slow fog)
    
    if (p.alpha <= 0) {
      trails.value.splice(i, 1)
      continue
    }
    
    const grad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size)
    // Iridescent colors for soap bubble effect
    grad.addColorStop(0, `rgba(255, 255, 255, ${p.alpha * 0.5})`)
    grad.addColorStop(0.5, `rgba(100, 200, 255, ${p.alpha * 0.3})`)
    grad.addColorStop(1, `rgba(50, 0, 100, 0)`)
    
    ctx.fillStyle = grad
    ctx.beginPath()
    ctx.arc(p.x, p.y, p.size, 0, Math.PI*2)
    ctx.fill()
  }
  ctx.restore()
  
  // 4. Ship (Relativistic Effects)
  ctx.save()
  ctx.translate(ship.x, ship.y)
  ctx.rotate(ship.angle)
  
  // LENGTH CONTRACTION: Scale X based on speed ratio
  // As speed -> MAX_SPEED (c), scaleX -> 0
  const speedRatio = Math.min(1, speed / MAX_SPEED)
  const lorentzFactor = Math.sqrt(1 - speedRatio * speedRatio * 0.9) // Exaggerated
  ctx.scale(lorentzFactor, 1) // Contract length
  
  // DOPPLER SHIFT: Color changes
  // Blue shift at front (engine), Red shift at back?
  // Actually, visual appearance is usually blue-shifted if moving towards viewer, but here we view from top.
  // Let's make the ship glow blue when fast.
  const shipColor = `hsl(${200 + speedRatio * 60}, 100%, ${50 + speedRatio * 50}%)`
  
  // Draw Ship Body
  ctx.fillStyle = shipColor
  ctx.shadowBlur = 10 * speedRatio
  ctx.shadowColor = shipColor
  ctx.beginPath()
  ctx.moveTo(20, 0)
  ctx.lineTo(-15, 12)
  ctx.lineTo(-10, 0)
  ctx.lineTo(-15, -12)
  ctx.fill()
  
  // Engine
  if (ship.thrust > 0) {
    ctx.beginPath()
    ctx.moveTo(-10, 0)
    ctx.lineTo(-30 - Math.random() * 20, 0)
    ctx.strokeStyle = '#0ff'
    ctx.lineWidth = 3
    ctx.stroke()
  }
  
  ctx.restore()
  
  // 5. Joystick Feedback
  if (joystick.active) {
    ctx.save()
    ctx.translate(joystick.originX - cvs.getBoundingClientRect().left, joystick.originY - cvs.getBoundingClientRect().top)
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)'
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.arc(0, 0, 50, 0, Math.PI*2)
    ctx.stroke()
    ctx.beginPath()
    ctx.arc(joystick.dx*50, joystick.dy*50, 20, 0, Math.PI*2)
    ctx.fillStyle = 'rgba(0, 255, 255, 0.5)'
    ctx.fill()
    ctx.restore()
  }
  
  // 6. Check Win Condition
  if (!isDomainSafe.value && trails.value.length > 300) { // Require significant fog
    activateBlackDomain()
  }
  
  requestAnimationFrame(domainLoop)
}

function activateBlackDomain() {
  if (isDomainSafe.value) return
  isDomainSafe.value = true
  lightSpeed.value = 16.7
  message.success('黑域生成！光速已降低至 16.7 km/s。安全声明发布。')
  soundManager.playConfirm() // Use specific sound if available
  // Maybe add a low thud later
}

onMounted(() => {
  initDomain()
  soundManager.startAmbient('void') // Use void ambient for space
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKey)
  window.removeEventListener('keyup', handleKey)
  soundManager.stopAmbient()
})

</script>

<template>
  <div class="sector-l">
    <div class="header">
      <h1 class="title">SECTOR L // LIGHTSPEED</h1>
      <p class="subtitle">曲率驱动与黑域 (Curvature & Black Domain)</p>
    </div>

    <NTabs type="segment" v-model:value="activeTab" class="l-tabs">
      
      <!-- Tab 1: Black Domain Game -->
      <NTabPane name="domain" tab="黑域模拟 (SIMULATION)">
        <div class="domain-view">
          <div class="domain-hud">
            <div class="hud-item speed">
              <span class="label">C-LIMIT</span>
              <span class="value" :class="{ 'c-reduced': isDomainSafe }">{{ lightSpeed }} km/s</span>
            </div>
            <div class="hud-item status">
              <span class="label">STATUS</span>
              <span class="value">{{ isDomainSafe ? 'SAFE (BLACK DOMAIN)' : 'EXPOSED (DARK FOREST)' }}</span>
            </div>
            <div class="hud-item hint">
              [WASD] 飞行并产生慢雾，包裹恒星以发布安全声明。
            </div>
          </div>
          
          <div class="canvas-wrapper">
            <canvas 
              ref="domainCanvas" 
              @touchstart="handleTouchStart"
              @touchmove="handleTouchMove"
              @touchend="handleTouchEnd"
            ></canvas>
          </div>
        </div>
      </NTabPane>

      <!-- Tab 2: 折纸隐喻 -->
      <NTabPane name="origami" tab="折纸隐喻 (METAPHOR)">
        <div class="origami-view">
          <header class="origami-header">
            <h2 class="origami-title">折纸隐喻</h2>
            <p class="origami-sub">云天明童话 · 赫尔辛根默斯肯的肥皂与船</p>
          </header>

          <div class="metaphor-card">
            <blockquote class="metaphor-quote">
              「把肥皂弄在船尾的水里，改变水的张力，船就自己动了。」
            </blockquote>
            <p class="metaphor-cite">—— 赫尔辛根默斯肯</p>
            <ul class="metaphor-keys">
              <li><span class="key">肥皂</span> → 空间曲率 / 张力差异</li>
              <li><span class="key">船</span> → 曲率驱动飞船</li>
              <li><span class="key">船尾的航迹</span> → 黑域、慢雾（低光速区）</li>
            </ul>
          </div>

          <div class="paper-lake">
            <div class="lake-wave"></div>
            <div class="boat-container" :style="{ animationDuration: `${4 / boatSpeed}s` }">
              <div class="boat">⛵</div>
              <template v-if="isSoapDropped">
                <div class="ripple r1"></div>
                <div class="ripple r2"></div>
                <div class="ripple r3"></div>
              </template>
            </div>
          </div>

          <div class="controls">
            <button
              class="soap-btn"
              :class="{ locked: !canDropSoap, active: isSoapDropped }"
              :disabled="isSoapDropped"
              @click="dropSoap"
            >
              {{ isSoapDropped ? '曲率驱动中…' : '投放肥皂 (DROP SOAP)' }}
            </button>
            <p v-if="!canDropSoap" class="soap-hint">面壁者权限可解锁投放，体验「改变水的张力」。</p>
          </div>
        </div>
      </NTabPane>

    </NTabs>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

.sector-l {
  min-height: 0;
  background: #0a0a1a;
  color: #aaddff;
  font-family: 'Share Tech Mono', monospace;
  display: flex;
  flex-direction: column;
}

.header {
  padding: 1rem 2rem;
  border-bottom: 1px solid rgba(170, 221, 255, 0.2);
  background: #050510;
}

.title { margin: 0; letter-spacing: 2px; font-size: 1.5rem; color: #fff; }
.subtitle { color: #557799; font-size: 0.8rem; margin-top: 0.5rem; }

.l-tabs { flex: 1; display: flex; flex-direction: column; }
:deep(.n-tabs-pane-wrapper) { flex: 1; min-height: 0; display: flex; flex-direction: column; }
:deep(.n-tab-pane) { flex: 1; display: flex; flex-direction: column; min-height: 0; }

/* Domain View */
.domain-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #000;
  position: relative;
}

.domain-hud {
  position: absolute;
  top: 0; left: 0; right: 0;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0,0,0,0.7);
  border-bottom: 1px solid rgba(255,255,255,0.1);
  z-index: 10;
  pointer-events: none;
}

.hud-item { display: flex; flex-direction: column; }
.label { font-size: 0.7rem; color: #557799; letter-spacing: 1px; }
.value { font-size: 1.2rem; font-weight: bold; }
.c-reduced { color: #ff3333; text-shadow: 0 0 10px #ff0000; }
.hint { opacity: 0.6; font-size: 0.8rem; max-width: 300px; text-align: right; }

.canvas-wrapper { flex: 1; width: 100%; height: 100%; position: relative; }
canvas { width: 100%; height: 100%; display: block; }

/* Origami 折纸隐喻 */
.origami-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.5rem 1rem 2rem;
  gap: 1.5rem;
  background: radial-gradient(ellipse 80% 60% at 50% 0%, #1a1a2e 0%, #0a0a18 50%, #050508 100%);
  overflow-y: auto;
}

.origami-header {
  text-align: center;
}

.origami-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  letter-spacing: 0.15em;
  color: #c8e4ff;
}

.origami-sub {
  margin: 0.35rem 0 0;
  font-size: 0.8rem;
  color: rgba(170, 221, 255, 0.7);
  letter-spacing: 0.06em;
}

.metaphor-card {
  max-width: 520px;
  width: 100%;
  padding: 1.25rem 1.5rem;
  background: rgba(10, 20, 40, 0.6);
  border: 1px solid rgba(170, 221, 255, 0.2);
  border-radius: 8px;
}

.metaphor-quote {
  margin: 0;
  font-size: 1.05rem;
  line-height: 1.6;
  color: #aaddff;
  font-style: italic;
  border-left: 3px solid rgba(170, 221, 255, 0.4);
  padding-left: 1rem;
}

.metaphor-cite {
  margin: 0.5rem 0 0 1rem;
  font-size: 0.85rem;
  color: rgba(170, 221, 255, 0.6);
}

.metaphor-keys {
  margin: 1rem 0 0;
  padding: 0 0 0 1rem;
  list-style: none;
  font-size: 0.88rem;
  color: rgba(200, 230, 255, 0.85);
  line-height: 1.8;
}

.metaphor-keys .key {
  color: #7dd3fc;
  font-weight: 600;
  margin-right: 0.25rem;
}

.paper-lake {
  width: 100%;
  max-width: 640px;
  height: 180px;
  border: 1px solid rgba(170, 221, 255, 0.15);
  border-radius: 8px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(180deg, #0a1520 0%, #0d1f30 40%, #0a1825 100%);
  box-shadow: inset 0 0 40px rgba(0, 40, 80, 0.3);
}

.lake-wave {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(100, 180, 255, 0.03) 50%, transparent 100%);
  background-size: 200% 100%;
  animation: wave 6s ease-in-out infinite;
  pointer-events: none;
}

.boat-container {
  position: absolute;
  top: 50%;
  left: -60px;
  font-size: 2.75rem;
  transform: translateY(-50%);
  animation: sail 12s linear infinite;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.4));
}

.ripple {
  position: absolute;
  right: 15px;
  bottom: 50%;
  width: 24px;
  height: 24px;
  margin-bottom: -12px;
  margin-right: -12px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.45);
  animation: ripple-out 1.2s ease-out infinite;
  pointer-events: none;
}

.ripple.r1 { animation-delay: 0s; }
.ripple.r2 { animation-delay: 0.4s; }
.ripple.r3 { animation-delay: 0.8s; }

.controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.soap-btn {
  padding: 0.85rem 2.5rem;
  background: rgba(170, 221, 255, 0.08);
  color: #aaddff;
  border: 1px solid rgba(170, 221, 255, 0.5);
  font-family: inherit;
  font-size: 0.95rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.25s, border-color 0.25s, box-shadow 0.25s;
}

.soap-btn:hover:not(:disabled) {
  background: rgba(170, 221, 255, 0.15);
  border-color: #aaddff;
  box-shadow: 0 0 20px rgba(170, 221, 255, 0.25);
}

.soap-btn.active {
  border-color: #7dd3fc;
  color: #7dd3fc;
  box-shadow: 0 0 15px rgba(125, 211, 252, 0.3);
}

.soap-btn.locked {
  opacity: 0.75;
}

.soap-btn:disabled {
  cursor: not-allowed;
}

.soap-hint {
  font-size: 0.75rem;
  color: rgba(170, 221, 255, 0.55);
  margin: 0;
}

@keyframes sail {
  0% { left: -60px; }
  100% { left: 100%; }
}

@keyframes wave {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

@keyframes ripple-out {
  0% { transform: scale(1); opacity: 0.85; }
  100% { transform: scale(3.5); opacity: 0; }
}

:deep(.n-tabs-nav) { background: #050510; }
:deep(.n-tabs-tab) { color: #557799; }
:deep(.n-tabs-tab--active) { color: #aaddff; font-weight: bold; }

@media (max-width: 600px) {
  .domain-hud { flex-direction: column; align-items: flex-start; gap: 0.5rem; }
  .hint { text-align: left; max-width: 100%; }
  .origami-view { padding: 1rem 0.75rem; gap: 1.25rem; }
  .origami-title { font-size: 1.25rem; }
  .metaphor-card { padding: 1rem 1.25rem; }
  .metaphor-quote { font-size: 0.95rem; }
  .paper-lake { height: 140px; }
  .boat-container { font-size: 2.25rem; }
  .soap-btn { padding: 0.75rem 1.75rem; font-size: 0.9rem; }
}
</style>
