<script setup lang="ts">
/**
 * Sector Scientific Boundary (科学边界)
 * 农场主假说、射手假说、台球实验 — 升级版
 */
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { NTabs, NTabPane, NButton, NSlider, NProgress, useMessage } from 'naive-ui'

type TabName = 'farmer' | 'shooter' | 'billiard'
interface Bullet { x: number; y: number }
interface Ball { x: number; y: number; vx: number; vy: number; r: number; color: string }

const message = useMessage()
const activeTab = ref<TabName>('farmer')

// --- 全局控制 ---
const globalPaused = ref(false)
const simSpeed = ref(1)
const chaosLevel = ref(0.35)

function toggleGlobalPause() {
  globalPaused.value = !globalPaused.value
}

// --- 视网膜倒计时 ---
const showCountdown = ref(false)
const countdownSeconds = ref(1185 * 3600 + 12 * 60 + 44)
let countdownInterval: ReturnType<typeof setInterval> | undefined

const countdownTime = computed(() => {
  const sec = Math.max(0, countdownSeconds.value)
  const h = Math.floor(sec / 3600)
  const m = Math.floor((sec % 3600) / 60)
  const s = sec % 60
  return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
})

function toggleCountdown() {
  showCountdown.value = !showCountdown.value
  if (showCountdown.value) {
    message.warning('检测到视网膜异常投影')
    if (!countdownInterval) {
      countdownInterval = setInterval(() => {
        if (globalPaused.value) return
        if (countdownSeconds.value > 0) countdownSeconds.value -= 1
      }, 1000)
    }
  } else if (countdownInterval) {
    clearInterval(countdownInterval)
    countdownInterval = undefined
  }
}

// --- 农场主假说 ---
const farmerDay = ref(0)
const farmerRunning = ref(false)
let farmerTimer: ReturnType<typeof setInterval> | undefined

const farmerConfidence = computed(() => {
  if (farmerDay.value >= 100) return 0
  return Math.min(99, Math.round((farmerDay.value / 100) * 100))
})

function startFarmer() {
  if (farmerRunning.value) return
  farmerRunning.value = true
  if (farmerDay.value >= 100) farmerDay.value = 0
  farmerTimer = setInterval(() => {
    if (globalPaused.value) return
    farmerDay.value += Math.max(1, Math.round(simSpeed.value))
    if (farmerDay.value >= 100) {
      farmerDay.value = 100
      farmerRunning.value = false
      if (farmerTimer) clearInterval(farmerTimer)
      farmerTimer = undefined
      message.warning('第 100 天。农场主来了。')
    }
  }, 120)
}

function pauseFarmer() {
  farmerRunning.value = false
  if (farmerTimer) clearInterval(farmerTimer)
  farmerTimer = undefined
}

function resetFarmer() {
  pauseFarmer()
  farmerDay.value = 0
}

// --- 射手假说 ---
const canvasShooter = ref<HTMLCanvasElement | null>(null)
const shooterAlive = ref(true)
const shooterScore = ref(0)
const shooterBullets = ref<Bullet[]>([])
const shooterAutoEvade = ref(true)
let shooterAnimId = 0
let shooterLastTime = 0
let lifeX = 150
let lifeY = 150
let targetX = 150
let targetY = 150
const W = 420
const H = 280

function clamp(v: number, min: number, max: number) {
  return Math.min(max, Math.max(min, v))
}

function initShooter() {
  if (shooterAnimId) cancelAnimationFrame(shooterAnimId)
  shooterAnimId = 0
  const canvas = canvasShooter.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  canvas.width = W
  canvas.height = H
  lifeX = W / 2
  lifeY = H / 2
  targetX = W / 2
  targetY = H / 2
  shooterAlive.value = true
  shooterScore.value = 0
  shooterBullets.value = []

  canvas.onmousemove = (e: MouseEvent) => {
    const rect = canvas.getBoundingClientRect()
    targetX = clamp(e.clientX - rect.left, 10, W - 10)
    targetY = clamp(e.clientY - rect.top, 10, H - 10)
  }

  shooterLastTime = performance.now()
  const draw = (now: number) => {
    const dt = Math.min(0.04, (now - shooterLastTime) / 1000)
    shooterLastTime = now
    ctx.fillStyle = 'rgba(0,0,0,0.2)'
    ctx.fillRect(0, 0, W, H)
    ctx.strokeStyle = '#333'
    ctx.strokeRect(0, 0, W, H)
    ctx.fillStyle = '#666'
    ctx.font = '12px monospace'
    ctx.fillText(`二维靶纸 · 生存 ${shooterScore.value.toFixed(1)}s`, 10, 20)

    if (!globalPaused.value && shooterAlive.value) {
      if (shooterAutoEvade.value) {
        const near = shooterBullets.value.find((b) => ((b.x - lifeX) ** 2 + (b.y - lifeY) ** 2) < 1600)
        if (near) {
          const dx = lifeX - near.x
          const dy = lifeY - near.y
          targetX = clamp(lifeX + dx, 10, W - 10)
          targetY = clamp(lifeY + dy, 10, H - 10)
        }
      }
      lifeX += (targetX - lifeX) * Math.min(1, dt * 8)
      lifeY += (targetY - lifeY) * Math.min(1, dt * 8)
      shooterScore.value += dt
      if (Math.random() < (0.02 + chaosLevel.value * 0.05) * simSpeed.value) {
        const side = Math.floor(Math.random() * 4)
        let x = 0
        let y = 0
        if (side === 0) { x = Math.random() * W; y = 0 }
        else if (side === 1) { x = W; y = Math.random() * H }
        else if (side === 2) { x = Math.random() * W; y = H }
        else { x = 0; y = Math.random() * H }
        shooterBullets.value.push({ x, y })
      }
    }

    if (!shooterAlive.value) {
      ctx.fillStyle = '#ff0000'
      ctx.font = '14px sans-serif'
      ctx.fillText('已被击中。规律不存在。', 100, H / 2)
    }

    ctx.fillStyle = shooterAlive.value ? '#00ff88' : '#777'
    ctx.beginPath()
    ctx.arc(lifeX, lifeY, 8, 0, Math.PI * 2)
    ctx.fill()

    const next: Bullet[] = []
    for (const b of shooterBullets.value) {
      const dx = lifeX - b.x
      const dy = lifeY - b.y
      const dist = Math.sqrt(dx * dx + dy * dy) || 1
      if (!globalPaused.value && shooterAlive.value) {
        const speed = (95 + chaosLevel.value * 120) * dt * simSpeed.value
        b.x += (dx / dist) * speed
        b.y += (dy / dist) * speed
      }
      if (dist < 14 && shooterAlive.value) {
        shooterAlive.value = false
        message.error('高维射手命中')
      }
      if (b.x > -10 && b.x < W + 10 && b.y > -10 && b.y < H + 10) {
        next.push(b)
        ctx.fillStyle = '#ff4444'
        ctx.beginPath()
        ctx.arc(b.x, b.y, 3.5, 0, Math.PI * 2)
        ctx.fill()
      }
    }
    shooterBullets.value = next
    shooterAnimId = requestAnimationFrame(draw)
  }
  shooterAnimId = requestAnimationFrame(draw)
}

function resetShooter() {
  if (activeTab.value !== 'shooter') return
  initShooter()
}

// --- 台球实验 ---
const canvasBilliard = ref<HTMLCanvasElement | null>(null)
let billiardAnimId = 0
let billiardLastTime = 0
const balls = ref<Ball[]>([])
const BW = 420
const BH = 280
const billiardShots = ref(0)
const billiardEnergy = ref(0)
const deterministicMode = ref(false)
const billiardRunning = ref(true)
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const dragCurrent = ref({ x: 0, y: 0 })

function updateBilliardEnergy() {
  billiardEnergy.value = balls.value.reduce((sum, b) => sum + b.vx * b.vx + b.vy * b.vy, 0)
}

function setDefaultBalls() {
  balls.value = [
    { x: 95, y: BH / 2, vx: 0, vy: 0, r: 10, color: '#fff' },
    { x: 255, y: BH / 2, vx: 0, vy: 0, r: 10, color: '#ff0' },
    { x: 276, y: BH / 2 - 12, vx: 0, vy: 0, r: 10, color: '#f00' },
    { x: 276, y: BH / 2 + 12, vx: 0, vy: 0, r: 10, color: '#00f' }
  ]
}

function initBilliard() {
  if (billiardAnimId) cancelAnimationFrame(billiardAnimId)
  billiardAnimId = 0
  const canvas = canvasBilliard.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  canvas.width = BW
  canvas.height = BH
  setDefaultBalls()
  updateBilliardEnergy()

  canvas.onmousedown = (e: MouseEvent) => {
    const rect = canvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    const whiteBall = balls.value[0]
    const dist = Math.hypot(x - whiteBall.x, y - whiteBall.y)
    if (dist < 28) {
      isDragging.value = true
      dragStart.value = { x: whiteBall.x, y: whiteBall.y }
      dragCurrent.value = { x, y }
    }
  }
  canvas.onmousemove = (e: MouseEvent) => {
    if (!isDragging.value) return
    const rect = canvas.getBoundingClientRect()
    dragCurrent.value = { x: e.clientX - rect.left, y: e.clientY - rect.top }
  }
  canvas.onmouseup = () => {
    if (!isDragging.value) return
    isDragging.value = false
    const dx = dragStart.value.x - dragCurrent.value.x
    const dy = dragStart.value.y - dragCurrent.value.y
    const power = 0.16
    const chaos = deterministicMode.value ? 0 : (Math.random() - 0.5) * chaosLevel.value
    const cos = Math.cos(chaos)
    const sin = Math.sin(chaos)
    const pvx = dx * power
    const pvy = dy * power
    balls.value[0].vx = pvx * cos - pvy * sin
    balls.value[0].vy = pvx * sin + pvy * cos
    billiardShots.value += 1
  }

  billiardLastTime = performance.now()
  const draw = (now: number) => {
    const dt = Math.min(0.04, (now - billiardLastTime) / 1000)
    billiardLastTime = now
    ctx.fillStyle = '#0a2a0a'
    ctx.fillRect(0, 0, BW, BH)
    ctx.strokeStyle = '#335533'
    ctx.lineWidth = 10
    ctx.strokeRect(5, 5, BW - 10, BH - 10)

    if (!globalPaused.value && billiardRunning.value) {
      for (let i = 0; i < balls.value.length; i++) {
        const b = balls.value[i]
        b.x += b.vx * dt * 60 * simSpeed.value
        b.y += b.vy * dt * 60 * simSpeed.value
        b.vx *= 0.985
        b.vy *= 0.985
        if (Math.abs(b.vx) < 0.05) b.vx = 0
        if (Math.abs(b.vy) < 0.05) b.vy = 0
        if (b.x - b.r < 10) { b.x = 10 + b.r; b.vx *= -0.8 }
        if (b.x + b.r > BW - 10) { b.x = BW - 10 - b.r; b.vx *= -0.8 }
        if (b.y - b.r < 10) { b.y = 10 + b.r; b.vy *= -0.8 }
        if (b.y + b.r > BH - 10) { b.y = BH - 10 - b.r; b.vy *= -0.8 }
        if (!deterministicMode.value && (Math.abs(b.vx) > 0.5 || Math.abs(b.vy) > 0.5) && Math.random() < 0.01 + chaosLevel.value * 0.04) {
          b.vx += (Math.random() - 0.5) * 2
          b.vy += (Math.random() - 0.5) * 2
          b.color = `hsl(${Math.random() * 360}, 70%, 50%)`
        }
      }
      for (let i = 0; i < balls.value.length; i++) {
        for (let j = i + 1; j < balls.value.length; j++) {
          const b1 = balls.value[i]
          const b2 = balls.value[j]
          const dx = b2.x - b1.x
          const dy = b2.y - b1.y
          const dist = Math.sqrt(dx * dx + dy * dy) || 1
          if (dist < b1.r + b2.r) {
            const tempVx = b1.vx
            const tempVy = b1.vy
            b1.vx = b2.vx
            b1.vy = b2.vy
            b2.vx = tempVx
            b2.vy = tempVy
            const angle = Math.atan2(dy, dx)
            const overlap = (b1.r + b2.r - dist) / 2
            b1.x -= Math.cos(angle) * overlap
            b1.y -= Math.sin(angle) * overlap
            b2.x += Math.cos(angle) * overlap
            b2.y += Math.sin(angle) * overlap
          }
        }
      }
    }

    for (const b of balls.value) {
      ctx.fillStyle = b.color
      ctx.beginPath()
      ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2)
      ctx.fill()
      ctx.fillStyle = 'rgba(255,255,255,0.3)'
      ctx.beginPath()
      ctx.arc(b.x - 3, b.y - 3, b.r / 3, 0, Math.PI * 2)
      ctx.fill()
    }

    if (isDragging.value) {
      const wb = balls.value[0]
      ctx.beginPath()
      ctx.moveTo(wb.x, wb.y)
      ctx.lineTo(dragCurrent.value.x, dragCurrent.value.y)
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)'
      ctx.lineWidth = 2
      ctx.setLineDash([5, 5])
      ctx.stroke()
      ctx.setLineDash([])
    }
    updateBilliardEnergy()
    billiardAnimId = requestAnimationFrame(draw)
  }
  billiardAnimId = requestAnimationFrame(draw)
}

function toggleBilliardRun() {
  billiardRunning.value = !billiardRunning.value
}

function resetBilliard() {
  billiardShots.value = 0
  setDefaultBalls()
  updateBilliardEnergy()
  if (activeTab.value === 'billiard') initBilliard()
}

function resetAll() {
  resetFarmer()
  if (activeTab.value === 'shooter') resetShooter()
  if (activeTab.value === 'billiard') resetBilliard()
}

function handleTabUpdate(name: string | number) {
  const tab = String(name) as TabName
  activeTab.value = tab
  if (tab === 'shooter') initShooter()
  if (tab === 'billiard') initBilliard()
}

onMounted(() => {
  if (activeTab.value === 'shooter') initShooter()
  if (activeTab.value === 'billiard') initBilliard()
})

onUnmounted(() => {
  pauseFarmer()
  if (countdownInterval) clearInterval(countdownInterval)
  cancelAnimationFrame(shooterAnimId)
  cancelAnimationFrame(billiardAnimId)
})
</script>

<template>
  <div class="sector-boundary">
    <header class="boundary-header">
      <h1>科学边界</h1>
      <p class="subtitle">物理学从未存在 · SCIENTIFIC BOUNDARY</p>
      <div class="header-actions">
        <NButton text size="small" @click="toggleCountdown" class="cmb-btn">
          <template #icon>👁️</template>
          {{ showCountdown ? '关闭视网膜投影' : '观测宇宙背景辐射' }}
        </NButton>
      </div>
      <div class="global-controls">
        <div class="ctrl-item">
          <span>仿真速度</span>
          <NSlider v-model:value="simSpeed" :step="0.1" :min="0.5" :max="3" />
          <strong>{{ simSpeed.toFixed(1) }}x</strong>
        </div>
        <div class="ctrl-item">
          <span>混沌强度</span>
          <NSlider v-model:value="chaosLevel" :step="0.01" :min="0" :max="1" />
          <strong>{{ (chaosLevel * 100).toFixed(0) }}%</strong>
        </div>
        <div class="ctrl-actions">
          <NButton size="small" type="warning" @click="toggleGlobalPause">
            {{ globalPaused ? '继续仿真' : '暂停仿真' }}
          </NButton>
          <NButton size="small" type="error" ghost @click="resetAll">
            重置全部
          </NButton>
        </div>
      </div>
    </header>

    <!-- 视网膜倒计时浮层 -->
    <div v-if="showCountdown" class="retina-countdown">
      <div class="countdown-digits">{{ countdownTime }}</div>
    </div>

    <NTabs v-model:value="activeTab" type="line" animated class="boundary-tabs" @update:value="handleTabUpdate">
      <NTabPane name="farmer" tab="农场主假说">
        <div class="panel farmer-panel">
          <p class="lore">火鸡中的科学家发现，每天上午十点会有食物降临。他们总结出了“定律”。直到感恩节前一天。</p>
          <div class="farmer-viz">
            <div class="turkey" v-for="i in 5" :key="i"></div>
            <div class="feed" :style="{ opacity: farmerDay < 100 ? 1 : 0 }"></div>
            <div class="day">第 {{ farmerDay }} 天</div>
            <div class="collapse-tip" v-if="farmerDay >= 100">模型崩塌：感恩节事件触发</div>
          </div>
          <div class="metrics">
            <div class="metric-line">
              <span>规律置信度</span>
              <NProgress :percentage="farmerConfidence" status="success" />
            </div>
          </div>
          <div class="actions">
            <NButton v-if="!farmerRunning && farmerDay < 100" type="primary" @click="startFarmer">开始观测</NButton>
            <NButton v-if="farmerRunning" type="warning" @click="pauseFarmer">暂停观测</NButton>
            <NButton type="error" ghost @click="resetFarmer">重置实验</NButton>
          </div>
        </div>
      </NTabPane>

      <NTabPane name="shooter" tab="射手假说">
        <div class="panel shooter-panel">
          <p class="lore">二维靶纸上的生命无法理解“射手”的存在。子弹从他们无法感知的维度飞来。</p>
          <div class="metrics shooter-metrics">
            <span>状态：{{ shooterAlive ? '存活' : '已命中' }}</span>
            <span>生存时长：{{ shooterScore.toFixed(1) }}s</span>
            <span>弹丸数量：{{ shooterBullets.length }}</span>
          </div>
          <div class="shooter-viz">
            <canvas ref="canvasShooter" class="shooter-canvas"></canvas>
          </div>
          <div class="actions">
            <NButton type="primary" @click="resetShooter">重置靶纸</NButton>
            <NButton type="default" ghost @click="shooterAutoEvade = !shooterAutoEvade">
              {{ shooterAutoEvade ? '关闭自动规避' : '开启自动规避' }}
            </NButton>
          </div>
        </div>
      </NTabPane>

      <NTabPane name="billiard" tab="台球实验">
        <div class="panel billiard-panel">
          <p class="lore">当智子锁死加速器，物理规律在微观层面被篡改。台球不再守恒。</p>
          <div class="metrics billiard-metrics">
            <span>击球次数：{{ billiardShots }}</span>
            <span>系统动能：{{ billiardEnergy.toFixed(2) }}</span>
            <span>模式：{{ deterministicMode ? '确定性' : '混沌扰动' }}</span>
          </div>
          <div class="billiard-viz">
            <canvas ref="canvasBilliard" class="billiard-canvas"></canvas>
          </div>
          <p class="hint">球体会随机受到“扰动”，模拟定律失效。</p>
          <div class="actions">
            <NButton type="primary" @click="toggleBilliardRun">
              {{ billiardRunning ? '暂停台球' : '继续台球' }}
            </NButton>
            <NButton type="default" ghost @click="deterministicMode = !deterministicMode">
              {{ deterministicMode ? '切换混沌模式' : '切换确定性模式' }}
            </NButton>
            <NButton type="error" ghost @click="resetBilliard">重置球桌</NButton>
          </div>
        </div>
      </NTabPane>
    </NTabs>
  </div>
</template>

<style scoped>
.sector-boundary {
  min-height: 0;
  background: #0a0a12;
  color: #ccc;
  font-family: 'Noto Serif SC', serif;
  display: flex;
  flex-direction: column;
}
.boundary-header {
  padding: 1.5rem 2rem;
  background: #050508;
  border-bottom: 1px solid #222;
  text-align: center;
}
.boundary-header h1 { font-size: 2rem; color: #8af; margin: 0; }
.subtitle { color: #555; font-size: 0.9rem; margin-top: 0.5rem; }
.header-actions { margin-top: 1rem; }
.cmb-btn { color: #444; transition: color 0.3s; }
.cmb-btn:hover { color: #d00; }
.global-controls {
  margin-top: 1rem;
  padding: 0.8rem;
  border: 1px solid #1f1f29;
  background: rgba(120, 140, 220, 0.06);
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 0.8rem;
  align-items: center;
}
.ctrl-item {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 0.5rem;
}
.ctrl-item span {
  color: #8893b0;
  font-size: 0.82rem;
  white-space: nowrap;
}
.ctrl-item strong {
  color: #8af;
  font-size: 0.82rem;
}
.ctrl-actions {
  display: flex;
  gap: 0.5rem;
}

.retina-countdown {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  pointer-events: none;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  background: radial-gradient(circle, transparent 30%, rgba(0,0,0,0.8) 100%);
  mix-blend-mode: difference;
}
.countdown-digits {
  font-family: 'Courier New', monospace;
  font-size: 10vw;
  color: rgba(255, 0, 0, 0.4);
  text-shadow: 0 0 20px rgba(255, 0, 0, 0.8), 2px 2px 0px rgba(0,0,0,0.5);
  animation: pulse 4s infinite ease-in-out;
  letter-spacing: -5px;
}
@keyframes pulse {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.02); }
}
.boundary-tabs { flex: 1; }
:deep(.n-tabs-nav) { background: #050508; padding: 0 2rem; }
:deep(.n-tabs-tab) { color: #666 !important; }
:deep(.n-tabs-tab--active) { color: #8af !important; font-weight: bold; }

.panel {
  max-width: 860px;
  margin: 2rem auto;
  padding: 2rem;
  border: 1px solid #222;
  background: rgba(255,255,255,0.02);
}
.lore { color: #888; line-height: 1.6; margin-bottom: 1.5rem; font-size: 0.95rem; }
.hint { color: #555; font-size: 0.85rem; margin-top: 1rem; }
.metrics {
  margin-bottom: 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
  color: #9ab;
  font-size: 0.84rem;
}
.metric-line {
  width: 100%;
}
.metric-line span {
  display: block;
  margin-bottom: 0.35rem;
}
.shooter-metrics,
.billiard-metrics {
  justify-content: space-between;
}

.farmer-viz {
  position: relative;
  height: 180px;
  background: linear-gradient(180deg, #1a2a1a 0%, #0d150d 100%);
  border: 1px solid #333;
  margin-bottom: 1.5rem;
}
.turkey {
  position: absolute;
  width: 24px; height: 24px;
  background: #664422;
  border-radius: 50%;
  bottom: 20px;
}
.turkey:nth-child(1) { left: 20%; }
.turkey:nth-child(2) { left: 35%; }
.turkey:nth-child(3) { left: 50%; }
.turkey:nth-child(4) { left: 65%; }
.turkey:nth-child(5) { left: 80%; }
.feed {
  position: absolute;
  left: 0; right: 0;
  bottom: 50px;
  height: 8px;
  background: #886622;
  transition: opacity 0.3s;
}
.day {
  position: absolute;
  top: 10px;
  right: 10px;
  font-family: monospace;
  color: #6a6;
}
.collapse-tip {
  position: absolute;
  left: 12px;
  top: 10px;
  color: #ff6677;
  font-size: 0.84rem;
}

.shooter-viz, .billiard-viz { display: flex; justify-content: center; margin: 1rem 0; }
.shooter-canvas {
  border: 1px solid #333;
  background: #000;
  width: 100%;
  max-width: 420px;
}
.billiard-canvas {
  border: 1px solid #335533;
  width: 100%;
  max-width: 420px;
}
.actions {
  margin-top: 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

@media (max-width: 900px) {
  .global-controls {
    grid-template-columns: 1fr;
  }
}
</style>
