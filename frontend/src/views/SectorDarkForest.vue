<script setup lang="ts">
// @ts-nocheck
/**
 * Sector E: 黑暗森林广场 (Dark Forest Square)
 * 宇宙社会学公理 + 猜疑链可视化 + 星际猎人模拟器 + 广播坐标
 */
import { ref, onMounted, onUnmounted, reactive, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { NInput, NButton, NModal, useMessage, NTabs, NTabPane, NProgress } from 'naive-ui'
import { soundManager } from '@/utils/sound'
import { tickDarkForestWorld } from '@/api/zero_v2'
import { loadVersionedState, saveVersionedState } from '@/composables/useZeroV2State'
import ModuleDiagPanel from '@/components/ModuleDiagPanel.vue'
import { getGatewayRuntimeStatus } from '@/api/llm_gateway'
import { seedCivilizations } from '@/sim/zeroDarkForest'
import type { CivilizationAgent, CosmicEpitaph, WorldlineSnapshot } from '@/types/zero_v2'

const message = useMessage()
const router = useRouter()

// --- Game State ---
const showIgniteModal = ref(false)
const igniteContent = ref('')
const activeTab = ref('simulator')

// --- Swordholder System State ---
const deterrence = ref(100) // 0-100%
const stability = ref(100) // 0-100%
const mouseActivity = ref(0) // Instantaneous mouse speed/activity
const lastMousePos = { x: 0, y: 0 }
let lastTime = Date.now()
const trisolarisStatus = ref<'CALM' | 'SUSPICIOUS' | 'PREPARING' | 'STRIKE'>('CALM')
const trisolarisMsg = ref('三体世界保持沉默。威慑建立。')
const isButtonCoverOpen = ref(false)
const isBroadcastTriggered = ref(false)
const stabilityHistory = ref<number[]>(new Array(50).fill(100))
let swordholderTimer: number

// Swordholder Logic
function updateSwordholder() {
  if (activeTab.value !== 'swordholder') return
  if (isBroadcastTriggered.value) return

  const now = Date.now()
  const dt = (now - lastTime) / 1000
  lastTime = now

  // Decay stability naturally (Entropy)
  // If mouse is too still (sleeping) -> stability drops (Luo Ji falling asleep)
  // If mouse is too erratic (panic) -> stability drops
  // Optimal: Slow, steady movements or small micro-adjustments
  
  if (mouseActivity.value < 5) {
    // Too still
    stability.value = Math.max(0, stability.value - 2 * dt)
  } else if (mouseActivity.value > 100) {
    // Too fast (Panic)
    stability.value = Math.max(0, stability.value - 5 * dt)
  } else {
    // Focused
    stability.value = Math.min(100, stability.value + 5 * dt)
  }
  
  // Reset instant activity
  mouseActivity.value *= 0.9

  // Update History Graph data
  stabilityHistory.value.push(stability.value)
  if (stabilityHistory.value.length > 50) stabilityHistory.value.shift()

  // Calculate Deterrence
  // Deterrence is a function of Stability
  deterrence.value = stability.value

  // Trisolaris Reaction
  if (deterrence.value > 80) {
    if (trisolarisStatus.value !== 'CALM') {
      trisolarisStatus.value = 'CALM'
      trisolarisMsg.value = '三体世界保持沉默。威慑有效。'
      soundManager.playConfirm()
    }
  } else if (deterrence.value > 40) {
    if (trisolarisStatus.value !== 'SUSPICIOUS') {
      trisolarisStatus.value = 'SUSPICIOUS'
      trisolarisMsg.value = '三体世界正在观测你的生理体征...'
      soundManager.playAlert()
    }
  } else if (deterrence.value > 0) {
    if (trisolarisStatus.value !== 'PREPARING') {
      trisolarisStatus.value = 'PREPARING'
      trisolarisMsg.value = '警告：水滴探测器正在加速！威慑即将失效！'
      soundManager.playAlert()
    }
  } else {
    if (trisolarisStatus.value !== 'STRIKE') {
      trisolarisStatus.value = 'STRIKE'
      trisolarisMsg.value = '威慑终结。水滴已穿过地球。'
      soundManager.playAlert()
      // Trigger Game Over?
    }
  }
  
  requestAnimationFrame(updateSwordholder)
}

function handleSwordholderMouseMove(e: MouseEvent) {
  if (activeTab.value !== 'swordholder') return
  const dist = Math.hypot(e.clientX - lastMousePos.x, e.clientY - lastMousePos.y)
  mouseActivity.value += dist
  lastMousePos.x = e.clientX
  lastMousePos.y = e.clientY
}

function toggleCover() {
  isButtonCoverOpen.value = !isButtonCoverOpen.value
  soundManager.playClick()
}

function triggerBroadcast() {
  if (!isButtonCoverOpen.value) return
  isBroadcastTriggered.value = true
  soundManager.playAlert() // Siren
  
  // Animation sequence
  trisolarisMsg.value = '引力波广播已启动。两个世界已毁灭。'
  trisolarisStatus.value = 'STRIKE' // Mutual destruction
  
  setTimeout(() => {
     message.error('坐标已暴露。光粒打击在途。')
  }, 2000)
}

// Watch tab change to start/stop loop
watch(activeTab, (newTab) => {
  if (newTab === 'swordholder') {
    lastTime = Date.now()
    requestAnimationFrame(updateSwordholder)
  }
})

// Swordholder Visuals
const deterrenceColor = computed(() => {
  if (deterrence.value > 80) return '#00ff41'
  if (deterrence.value > 40) return '#ffcc00'
  return '#ff3333'
})

const stabilityPath = computed(() => {
  if (stabilityHistory.value.length < 2) return ''
  // Map values to SVG path
  const w = 300
  const h = 100
  const step = w / (stabilityHistory.value.length - 1)
  
  let d = `M 0 ${h - stabilityHistory.value[0]}`
  stabilityHistory.value.forEach((val, i) => {
    if (i === 0) return
    d += ` L ${i * step} ${h - (val / 100) * h}`
  })
  return d
})

// --- 1. Cosmic Sociology Sandbox (Canvas) ---
const canvasRef = ref<HTMLCanvasElement | null>(null)
const sandboxMode = ref<'OBSERVER' | 'HUNTER'>('OBSERVER')
const timeScale = ref(1.0)

interface Star {
  x: number; y: number; size: number; alpha: number;
  type: 'civ' | 'dead' | 'dust';
  name?: string;
  // Civ Props
  tech: number; // 0.1 - 2.0 (Detection Range & Defense)
  hiding: number; // 0.1 - 1.0 (Visibility)
  aggressive: boolean;
  status: 'ALIVE' | 'DYING' | 'DEAD';
  lastAction?: string;
  detectedTargets: number[]; // Indices of discovered stars
}

const stars = ref<Star[]>([])
const projectiles = ref<{ sx: number, sy: number, tx: number, ty: number, progress: number, speed: number }[]>([])
const hunter = reactive({ x: 50, y: 50, scanRadius: 15, ammo: 3 })
let animId: number

// 跑马灯：沙盒结果不阻断浏览，底部单行滚动展示（最多保留条数）
const TICKER_MAX = 24
const sandboxTickerLog = ref<{ id: number; text: string; type: 'destroy' | 'strike' | 'warn' }[]>([])
let tickerId = 0
function pushTicker(text: string, type: 'destroy' | 'strike' | 'warn' = 'destroy') {
  sandboxTickerLog.value.push({ id: ++tickerId, text, type })
  if (sandboxTickerLog.value.length > TICKER_MAX) sandboxTickerLog.value.shift()
}

// 模拟步进间隔（毫秒）：降低频率让用户有时间观察
const SIM_TICK_MS = 550
let lastSandboxTick = 0

function initStars() {
  sandboxTickerLog.value = []
  const count = 200
  const arr: Star[] = []
  for (let i = 0; i < count; i++) {
    const isCiv = Math.random() < 0.08 // 8% chance
    arr.push({
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 1.5 + (isCiv ? 2 : 0.5),
      alpha: Math.random() * 0.5 + 0.2,
      type: isCiv ? 'civ' : 'dust',
      name: isCiv ? `CIV-${Math.floor(Math.random()*9999)}` : undefined,
      tech: Math.random() * 1.0 + 0.5,
      hiding: Math.random(),
      aggressive: Math.random() > 0.3, // 70% aggressive (Dark Forest)
      status: 'ALIVE',
      detectedTargets: []
    })
  }
  stars.value = arr
}

const isPaused = ref(false)

function togglePause() {
  isPaused.value = !isPaused.value
}

function updateCivLogic() {
  if (sandboxMode.value === 'HUNTER') return
  if (isPaused.value) return

  const civs = stars.value.map((s, i) => ({ s, i })).filter(item => item.s.type === 'civ' && item.s.status === 'ALIVE')

  civs.forEach(source => {
    if (Math.random() < 0.005) source.s.tech += 0.01

    civs.forEach(target => {
      if (source.i === target.i) return
      if (source.s.detectedTargets.includes(target.i)) return

      const dist = Math.hypot(source.s.x - target.s.x, source.s.y - target.s.y)
      const detectThreshold = (source.s.tech * 15) * (1 - target.s.hiding * 0.8)

      if (dist < detectThreshold) {
        source.s.detectedTargets.push(target.i)
        if (source.s.aggressive) {
          source.s.lastAction = `Detected ${target.s.name}. Launching Strike.`
          launchStrike(source.s, target.s)
        } else {
          source.s.lastAction = `Detected ${target.s.name}. Staying Silent.`
          if (Math.random() < 0.1) source.s.hiding -= 0.1
        }
      }
    })
  })
}

function updateProjectiles() {
  for (let i = projectiles.value.length - 1; i >= 0; i--) {
    const p = projectiles.value[i]
    p.progress += p.speed * timeScale.value
    if (p.progress >= 1) projectiles.value.splice(i, 1)
  }
}

function launchStrike(source: Star, target: Star) {
  // Visual
  projectiles.value.push({
    sx: source.x, sy: source.y,
    tx: target.x, ty: target.y,
    progress: 0,
    speed: 0.02
  })
  
  // Logic
  setTimeout(() => {
    if (target.status === 'ALIVE') {
      target.status = 'DYING'
      target.type = 'dead'
      target.lastAction = 'DESTROYED BY PHOTOID'
      pushTicker(`${target.name} 被光粒摧毁`, 'destroy')
    }
  }, 1000) // Travel time approx
}

function draw() {
  const now = Date.now()
  if (now - lastSandboxTick >= SIM_TICK_MS) {
    lastSandboxTick = now
    updateCivLogic()
  }
  updateProjectiles()

  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  const w = canvas.width
  const h = canvas.height
  
  // Clear with trails
  ctx.fillStyle = 'rgba(5, 5, 5, 0.3)'
  ctx.fillRect(0, 0, w, h)
  
  // Draw Stars
  stars.value.forEach(star => {
    const sx = (star.x / 100) * w
    const sy = (star.y / 100) * h
    
    // Draw Detection Range (Observer Mode)
    if (sandboxMode.value === 'OBSERVER' && star.type === 'civ' && star.status === 'ALIVE') {
      ctx.beginPath()
      ctx.arc(sx, sy, (star.tech * 15 / 100) * Math.min(w,h), 0, Math.PI * 2)
      ctx.strokeStyle = `rgba(50, 50, 50, 0.1)`
      ctx.lineWidth = 1
      ctx.stroke()
    }

    // Draw Star
    ctx.beginPath()
    const size = star.status === 'DYING' ? star.size * 3 : star.size
    ctx.arc(sx, sy, size, 0, Math.PI * 2)
    
    if (star.type === 'dead') {
      ctx.fillStyle = '#222'
    } else if (star.type === 'civ') {
       if (star.status === 'DYING') {
         ctx.fillStyle = '#ffcc00'
         ctx.shadowBlur = 20
         ctx.shadowColor = '#ff0000'
       } else {
         // Civ Color based on aggressive/hiding
         ctx.fillStyle = star.aggressive ? '#ff5555' : '#00aaff'
         if (sandboxMode.value === 'HUNTER') {
            // Hunter Mode: Hide unless scanned
            const dist = Math.hypot(sx - (hunter.x/100)*w, sy - (hunter.y/100)*h)
            const inRange = dist < (hunter.scanRadius/100)*Math.min(w,h)
            if (!inRange) ctx.fillStyle = `rgba(255, 255, 255, ${star.alpha})`
         }
       }
    } else {
      ctx.fillStyle = `rgba(255, 255, 255, ${star.alpha})`
    }
    ctx.fill()
    ctx.shadowBlur = 0
    
    // Draw Name (Observer)
    if (sandboxMode.value === 'OBSERVER' && star.type === 'civ' && star.status === 'ALIVE') {
      ctx.fillStyle = '#666'
      ctx.font = '10px monospace'
      ctx.fillText(star.name || '', sx + 5, sy - 5)
    }
  })
  
  // Draw Projectiles
  ctx.strokeStyle = '#fff'
  ctx.lineWidth = 2
  projectiles.value.forEach(p => {
    const cx = (p.sx + (p.tx - p.sx) * p.progress) / 100 * w
    const cy = (p.sy + (p.ty - p.sy) * p.progress) / 100 * h
    
    ctx.beginPath()
    ctx.moveTo(cx, cy)
    ctx.lineTo(cx - (p.tx-p.sx)*0.05, cy - (p.ty-p.sy)*0.05) // Trail
    ctx.stroke()
    
    // Glow head
    ctx.beginPath()
    ctx.arc(cx, cy, 2, 0, Math.PI*2)
    ctx.fillStyle = '#fff'
    ctx.shadowBlur = 10
    ctx.shadowColor = '#fff'
    ctx.fill()
    ctx.shadowBlur = 0
  })
  
  // Draw Hunter Scope
  if (sandboxMode.value === 'HUNTER') {
    const hx = (hunter.x / 100) * w
    const hy = (hunter.y / 100) * h
    
    ctx.beginPath()
    ctx.arc(hx, hy, (hunter.scanRadius/100)*Math.min(w,h), 0, Math.PI * 2)
    ctx.strokeStyle = 'rgba(0, 255, 255, 0.5)'
    ctx.lineWidth = 2
    ctx.stroke()
  }

  animId = requestAnimationFrame(draw)
}


const hoveredStar = ref<Star | null>(null)

function handleMouseMove(e: MouseEvent) {
  const canvas = canvasRef.value
  if (!canvas) return
  const rect = canvas.getBoundingClientRect()
  const mx = ((e.clientX - rect.left) / rect.width) * 100
  const my = ((e.clientY - rect.top) / rect.height) * 100
  
  hunter.x = mx
  hunter.y = my

  if (sandboxMode.value === 'OBSERVER') {
    // Find hovered star
    let found = null
    // Search civs first
    for (const star of stars.value) {
      if (star.type === 'civ') {
         const dist = Math.hypot(star.x - mx, star.y - my)
         if (dist < 2) { // Tolerance
           found = star
           break
         }
      }
    }
    hoveredStar.value = found
  } else {
    hoveredStar.value = null
  }
}

function handleShoot() {
  if (sandboxMode.value === 'OBSERVER') {
    // In Observer mode, click spawns a civ
    // Not implemented yet
    return
  }

  if (hunter.ammo <= 0) {
    pushTicker('光粒储量耗尽 (OUT OF AMMO)', 'warn')
    return
  }
  
  // Find nearest civ in range
  let hit = false
  stars.value.forEach(star => {
    if (star.type === 'civ' && star.status === 'ALIVE') {
      const w = canvasRef.value!.width
      const h = canvasRef.value!.height
      const sx = (star.x / 100) * w
      const sy = (star.y / 100) * h
      const hx = (hunter.x / 100) * w
      const hy = (hunter.y / 100) * h
      const dist = Math.hypot(sx - hx, sy - hy)
      
      if (dist < 30) { // Precision hit
        star.status = 'DYING'
        hit = true
        pushTicker(`已清除潜在威胁: ${star.name}`, 'strike')
        setTimeout(() => { star.type = 'dead'; star.status = 'DEAD'; }, 1000)
      }
    }
  })
  
  hunter.ammo--
  if (!hit) {
    pushTicker('打击落空。暴露风险增加。', 'warn')
  }
}

// --- 2. Broadcast System ---
const broadcastCode = ref('')
const isBroadcasting = ref(false)

// --- B. 世界线沙盒（合并自三体体验沙盒）---
const LOCAL_WORLDLINES = 'zero_v2_dark_forest_worldlines'
const civCount = ref<6 | 8 | 12>(8)
const epochStep = ref<50 | 100 | 200>(100)
const agents = ref<CivilizationAgent[]>(seedCivilizations(8))
const epitaphs = ref<CosmicEpitaph[]>([])
const epoch = ref(0)
const running = ref(false)
const bLoading = ref(false)
let worldlineTimer: ReturnType<typeof setInterval> | null = null
let ticking = false
const worldlineName = ref('')
const worldlines = ref<WorldlineSnapshot[]>([])
const selectedWorldlineId = ref<number | null>(null)
const eventStream = ref<Array<{ id: number; text: string; at: string; type: 'STRIKE' | 'SYSTEM' }>>([])
const gatewayState = ref(getGatewayRuntimeStatus())
const eventFilter = ref<'ALL' | 'STRIKE' | 'SYSTEM'>('ALL')
const tickIntervalMs = ref(2000)
const survivalCurve = ref<Array<{ epoch: number; alive: number }>>([])
type TaskDiag = { status: 'IDLE' | 'RUNNING' | 'SUCCESS' | 'ERROR'; durationMs: number; updatedAt: string; error: string }
type DiagHistoryItem = { at: string; status: 'SUCCESS' | 'ERROR'; durationMs: number; error?: string }
function createDiag(): TaskDiag {
  return { status: 'IDLE', durationMs: 0, updatedAt: '-', error: '' }
}
const diagB = ref<TaskDiag>(createDiag())
const diagHistB = ref<DiagHistoryItem[]>([])
function markRunning(diag: TaskDiag): number {
  diag.status = 'RUNNING'
  diag.error = ''
  return performance.now()
}
function markSuccess(diag: TaskDiag, startAt: number) {
  diag.status = 'SUCCESS'
  diag.durationMs = Math.round(performance.now() - startAt)
  diag.updatedAt = new Date().toLocaleTimeString()
}
function markError(diag: TaskDiag, startAt: number, err: unknown) {
  diag.status = 'ERROR'
  diag.durationMs = Math.round(performance.now() - startAt)
  diag.updatedAt = new Date().toLocaleTimeString()
  diag.error = err instanceof Error ? err.message : 'UNKNOWN_ERROR'
}
function pushDiagHistory(list: DiagHistoryItem[], item: DiagHistoryItem) {
  list.unshift(item)
  if (list.length > 8) list.pop()
}
async function stepUniverse() {
  if (ticking) return
  ticking = true
  const t0 = markRunning(diagB.value)
  bLoading.value = true
  try {
    const ret = await tickDarkForestWorld(agents.value, epoch.value, epochStep.value)
    epoch.value = ret.nextEpoch
    agents.value = ret.agents
    survivalCurve.value.push({ epoch: epoch.value, alive: ret.agents.filter((a) => a.alive).length })
    if (survivalCurve.value.length > 80) survivalCurve.value = survivalCurve.value.slice(-80)
    if (ret.epitaphs.length) {
      epitaphs.value = [...ret.epitaphs, ...epitaphs.value].slice(0, 16)
      const streamEvents = ret.epitaphs.map((e) => ({
        id: Date.now() + e.id,
        at: new Date().toLocaleTimeString(),
        type: 'STRIKE' as const,
        text: `纪元 ${e.epoch}：${e.attacker} -> ${e.victim} // ${e.reason}`,
      }))
      eventStream.value = [...streamEvents, ...eventStream.value].slice(0, 24)
    }
    markSuccess(diagB.value, t0)
    pushDiagHistory(diagHistB.value, { at: diagB.value.updatedAt, status: 'SUCCESS', durationMs: diagB.value.durationMs })
  } catch (err) {
    markError(diagB.value, t0, err)
    pushDiagHistory(diagHistB.value, { at: diagB.value.updatedAt, status: 'ERROR', durationMs: diagB.value.durationMs, error: diagB.value.error })
    message.error('宇宙演化失败，等待下一周期重试。')
  } finally {
    bLoading.value = false
    ticking = false
  }
}
function startSandbox() {
  if (running.value) return
  running.value = true
  worldlineTimer = setInterval(() => { void stepUniverse() }, tickIntervalMs.value)
}
function stopSandbox() {
  running.value = false
  if (worldlineTimer) clearInterval(worldlineTimer)
  worldlineTimer = null
}
function resetSandbox() {
  stopSandbox()
  epoch.value = 0
  agents.value = seedCivilizations(civCount.value)
  epitaphs.value = []
  survivalCurve.value = []
  eventStream.value = []
}
function saveWorldline() {
  const snapshot: WorldlineSnapshot = {
    id: Date.now(),
    name: worldlineName.value.trim() || `世界线-${new Date().toLocaleTimeString()}`,
    savedAt: new Date().toLocaleString(),
    epoch: epoch.value,
    agents: JSON.parse(JSON.stringify(agents.value)) as CivilizationAgent[],
    epitaphs: JSON.parse(JSON.stringify(epitaphs.value)) as CosmicEpitaph[],
  }
  worldlines.value.unshift(snapshot)
  worldlines.value = worldlines.value.slice(0, 12)
  worldlineName.value = ''
  saveVersionedState(LOCAL_WORLDLINES, worldlines.value)
  message.success('世界线已归档。')
}
function restoreWorldline() {
  if (!selectedWorldlineId.value) return
  const target = worldlines.value.find((w) => w.id === selectedWorldlineId.value)
  if (!target) return
  stopSandbox()
  epoch.value = target.epoch
  agents.value = JSON.parse(JSON.stringify(target.agents)) as CivilizationAgent[]
  epitaphs.value = JSON.parse(JSON.stringify(target.epitaphs)) as CosmicEpitaph[]
  eventStream.value.unshift({
    id: Date.now(),
    at: new Date().toLocaleTimeString(),
    type: 'SYSTEM',
    text: `系统：已恢复世界线 ${target.name}（纪元 ${target.epoch}）`,
  })
  eventStream.value = eventStream.value.slice(0, 24)
  message.success(`已恢复：${target.name}`)
}
function deleteWorldline() {
  if (!selectedWorldlineId.value) return
  worldlines.value = worldlines.value.filter((w) => w.id !== selectedWorldlineId.value)
  selectedWorldlineId.value = null
  saveVersionedState(LOCAL_WORLDLINES, worldlines.value)
  message.warning('归档已删除。')
}
const aliveCount = computed(() => agents.value.filter((a) => a.alive).length)
const filteredEventStream = computed(() => {
  if (eventFilter.value === 'ALL') return eventStream.value
  return eventStream.value.filter((evt) => evt.type === eventFilter.value)
})
const selectedWorldline = computed(() => worldlines.value.find((w) => w.id === selectedWorldlineId.value) ?? null)
const worldlineDelta = computed(() => {
  if (!selectedWorldline.value) return null
  const selectedAlive = selectedWorldline.value.agents.filter((a) => a.alive).length
  const currentAlive = agents.value.filter((a) => a.alive).length
  return {
    aliveDiff: currentAlive - selectedAlive,
    epochDiff: epoch.value - selectedWorldline.value.epoch,
    epitaphDiff: epitaphs.value.length - selectedWorldline.value.epitaphs.length,
  }
})
const survivalCurvePath = computed(() => {
  const data = survivalCurve.value
  if (data.length < 2) return ''
  const width = 320
  const height = 90
  const maxEpoch = Math.max(1, ...data.map((d) => d.epoch))
  const maxAlive = Math.max(1, ...data.map((d) => d.alive))
  const x = (e: number) => (e / maxEpoch) * (width - 4) + 2
  const y = (alive: number) => height - 4 - (alive / maxAlive) * (height - 8)
  let d = `M ${x(data[0].epoch)} ${y(data[0].alive)}`
  for (let i = 1; i < data.length; i++) {
    d += ` L ${x(data[i].epoch)} ${y(data[i].alive)}`
  }
  return d
})
const sessionSummaryText = computed(() => {
  const lines = [
    '【黑暗森林沙盒 · 本局摘要】',
    `纪元：${epoch.value}`,
    `存活文明：${aliveCount.value}`,
    `墓志铭数：${epitaphs.value.length}`,
    '',
    '代表性墓志铭：',
  ]
  epitaphs.value.slice(0, 3).forEach((e) => {
    lines.push(`  纪元 ${e.epoch}：${e.attacker} → ${e.victim} | ${e.reason}`)
  })
  if (epitaphs.value.length === 0) lines.push('  （暂无）')
  return lines.join('\n')
})
async function copySessionSummary() {
  try {
    await navigator.clipboard.writeText(sessionSummaryText.value)
    message.success('本局摘要已复制到剪贴板。')
  } catch {
    message.error('复制失败，请手动选择摘要文本复制。')
  }
}
function downloadText(filename: string, text: string, mime = 'text/plain;charset=utf-8') {
  const blob = new Blob([text], { type: mime })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
function exportEventStreamJson() {
  const payload = JSON.stringify(filteredEventStream.value, null, 2)
  downloadText(`event-stream-${Date.now()}.json`, payload, 'application/json;charset=utf-8')
}
function exportEventStreamCsv() {
  const rows = filteredEventStream.value.map((e) => {
    const safeText = e.text.replaceAll('"', '""')
    return `"${e.at}","${e.type}","${safeText}"`
  })
  const csv = ['time,type,text', ...rows].join('\n')
  downloadText(`event-stream-${Date.now()}.csv`, csv, 'text/csv;charset=utf-8')
}
async function exportFullPackage() {
  try {
    const fflate = await import('fflate')
    const enc = new TextEncoder()
    const ts = Date.now()
    const eventJson = JSON.stringify(eventStream.value, null, 2)
    const rows = eventStream.value.map((e) => {
      const safeText = e.text.replaceAll('"', '""')
      return `"${e.at}","${e.type}","${safeText}"`
    })
    const eventCsv = ['time,type,text', ...rows].join('\n')
    const worldlinesMeta = JSON.stringify(
      worldlines.value.map((w) => ({
        id: w.id,
        name: w.name,
        savedAt: w.savedAt,
        epoch: w.epoch,
        agentsCount: w.agents.length,
        aliveCount: w.agents.filter((a) => a.alive).length,
        epitaphsCount: w.epitaphs.length,
      })),
      null,
      2,
    )
    const zippable: fflate.Zippable = {
      'event-stream.json': enc.encode(eventJson),
      'event-stream.csv': enc.encode(eventCsv),
      'session-summary.txt': enc.encode(sessionSummaryText.value),
      'worldlines-meta.json': enc.encode(worldlinesMeta),
    }
    const zipBytes = fflate.zipSync(zippable, { level: 6 })
    const blob = new Blob([zipBytes], { type: 'application/zip' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `dark-forest-sandbox-${ts}.zip`
    a.click()
    URL.revokeObjectURL(url)
    message.success('完整包已导出（ZIP 含事件流与世界线元数据）。')
  } catch (err) {
    message.error(err instanceof Error ? err.message : '导出完整包失败')
  }
}

function sendBroadcast() {
  if (!broadcastCode.value) return
  isBroadcasting.value = true
  setTimeout(() => {
    message.success(`引力波广播已发送: ${broadcastCode.value}`)
    message.error('警告：自身坐标已随波发送')
    isBroadcasting.value = false
    broadcastCode.value = ''
  }, 2000)
}

// --- 3. Sociology Game Lab ---
const gameStatus = ref<'ACTIVE' | 'WON' | 'LOST' | 'DESTROYED'>('ACTIVE')
const playerStatus = ref('生存中')
const playerTech = ref(1.0)
const opponentStatus = ref('生存中')
const opponentTech = ref(0.8) // Initially weaker or stronger
const opponentBenevolence = ref(false) // true: kind, false: malicious
const opponentRevealed = ref(false)
const distance = ref(100)
const gameLogs = ref<{ text: string; type: string }[]>([])
const actionIcon = ref('')

function resetGame() {
  gameStatus.value = 'ACTIVE'
  playerStatus.value = '生存中'
  playerTech.value = 1.0
  opponentStatus.value = '生存中'
  // Random Opponent
  opponentTech.value = Math.random() * 0.5 + 0.8 // 0.8 - 1.3
  opponentBenevolence.value = Math.random() > 0.5
  opponentRevealed.value = false
  distance.value = Math.floor(Math.random() * 500 + 50)
  gameLogs.value = [{ text: `系统重置。探测到距离 ${distance.value} 光年的微弱信号。`, type: 'info' }]
  actionIcon.value = ''
}

function addLog(text: string, type: 'info' | 'success' | 'warn' | 'error' = 'info') {
  gameLogs.value.push({ text, type })
  if (gameLogs.value.length > 6) gameLogs.value.shift()
}

function opponentAction() {
  if (gameStatus.value !== 'ACTIVE') return
  
  // Opponent Turn
  // If opponent is malicious and stronger, they strike
  // If opponent is benevolent, they might communicate or hide
  
  if (!opponentBenevolence.value) {
    // Malicious
    if (opponentTech.value > playerTech.value) {
      // Stronger: Strike immediately
      addLog('警报！检测到强光粒打击！', 'error')
      setTimeout(() => {
        gameStatus.value = 'DESTROYED'
        playerStatus.value = '已毁灭'
        addLog('文明 A 已被毁灭。黑暗森林法则生效。', 'error')
      }, 1000)
    } else {
      // Weaker: Hide and explode tech
      addLog('对方保持沉默。但在暗中加速发展。', 'warn')
      opponentTech.value += 0.2 // Tech explosion
    }
  } else {
    // Benevolent
    if (Math.random() > 0.7) {
      addLog('接收到对方的善意问候。', 'success')
      opponentRevealed.value = true
    } else {
      addLog('对方保持沉默。', 'info')
    }
  }
}

function chooseSilence() {
  addLog('你选择了沉默。技术正在缓慢积累。', 'info')
  playerTech.value += 0.1
  setTimeout(opponentAction, 1000)
}

function chooseCommunicate() {
  addLog('你发送了问候信号。坐标已暴露！', 'warn')
  actionIcon.value = '📡'
  setTimeout(() => {
    actionIcon.value = ''
    if (!opponentBenevolence.value) {
      addLog('对方是恶意的！它锁定了你的位置。', 'error')
      setTimeout(() => {
        addLog('打击已至。光粒摧毁了恒星。', 'error')
        gameStatus.value = 'DESTROYED'
        playerStatus.value = '已毁灭'
      }, 1500)
    } else {
      addLog('对方回应了善意。建立了脆弱的信任。', 'success')
      opponentRevealed.value = true
      gameStatus.value = 'WON'
    }
  }, 1000)
}

function chooseStrike() {
  addLog('你发射了光粒。正在清理目标。', 'warn')
  actionIcon.value = '💥'
  setTimeout(() => {
    actionIcon.value = ''
    opponentStatus.value = '已毁灭'
    opponentRevealed.value = true
    gameStatus.value = 'WON' // Survived
    if (opponentBenevolence.value) {
      addLog(`目标已清除。事后分析：这是一个善意文明。你毁灭了无辜者。`, 'warn')
    } else {
      addLog(`目标已清除。事后分析：这是一个恶意文明。你做出了正确选择。`, 'success')
    }
  }, 1000)
}

// Initialize Game
onMounted(() => {
  resetGame()
})

// --- Lifecycle ---
onMounted(() => {
  initStars()
  worldlines.value = loadVersionedState<WorldlineSnapshot[]>(LOCAL_WORLDLINES, [])
  const canvas = canvasRef.value
  if (canvas) {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight * 0.6
    draw()
  }
  window.addEventListener('resize', resizeCanvas)
})

onUnmounted(() => {
  stopSandbox()
  cancelAnimationFrame(animId)
  window.removeEventListener('resize', resizeCanvas)
})

function resizeCanvas() {
  if (canvasRef.value) {
    canvasRef.value.width = window.innerWidth
    canvasRef.value.height = window.innerHeight * 0.6
  }
}

// Axioms
const axioms = [
  "生存是文明的第一需要。",
  "文明不断增长和扩张，但宇宙中的物质总量保持不变。"
]
</script>

<template>
  <div class="df-page">
    <header class="df-header">
      <h1 class="df-title">SECTOR E // DARK FOREST</h1>
      <p class="df-subtitle">黑暗森林广场</p>
    </header>

    <NTabs v-model:value="activeTab" type="segment" class="df-tabs">
      <!-- Tab 1: Hunter Simulator -->
      <NTabPane name="simulator" tab="宇宙沙盒 (SANDBOX)">
        <div class="sim-container">
          <div class="hud-top">
            <div class="hud-item mode-switch">
              <button :class="{ active: sandboxMode === 'OBSERVER' }" @click="sandboxMode = 'OBSERVER'">OBSERVER</button>
              <button :class="{ active: sandboxMode === 'HUNTER' }" @click="sandboxMode = 'HUNTER'">HUNTER</button>
            </div>
            <div class="hud-item">
              <span class="label">CIVILIZATIONS</span>
              <span class="value text-green">{{ stars.filter(s => s.type === 'civ' && s.status === 'ALIVE').length }}</span>
            </div>
            <div class="hud-item">
              <span class="label">DESTROYED</span>
              <span class="value text-red">{{ stars.filter(s => s.type === 'dead' || s.status === 'DYING').length }}</span>
            </div>
            <div class="hud-item" v-if="sandboxMode === 'HUNTER'">
              <span class="label">AMMO</span>
              <span class="value">{{ hunter.ammo }}</span>
            </div>
    </div>

          <div class="canvas-wrapper">
            <canvas 
              ref="canvasRef" 
              class="star-canvas"
              @mousemove="handleMouseMove"
              @click="handleShoot"
            ></canvas>
            <div class="scan-overlay"></div>
            
            <div class="civ-tooltip" v-if="sandboxMode === 'OBSERVER' && hoveredStar" :style="{ left: hoveredStar.x + '%', top: hoveredStar.y + '%' }">
              <div class="tt-header">{{ hoveredStar.name }}</div>
              <div class="tt-row">STATUS: <span :class="hoveredStar.status === 'ALIVE' ? 'text-green' : 'text-red'">{{ hoveredStar.status }}</span></div>
              <div class="tt-row">TECH: {{ hoveredStar.tech.toFixed(2) }}</div>
              <div class="tt-row">HIDING: {{ (hoveredStar.hiding * 100).toFixed(0) }}%</div>
              <div class="tt-row">AGGRESSIVE: {{ hoveredStar.aggressive ? 'YES' : 'NO' }}</div>
              <div class="tt-log" v-if="hoveredStar.lastAction">> {{ hoveredStar.lastAction }}</div>
      </div>
    </div>

          <!-- 跑马灯：沙盒结果不阻断浏览，底部单行滚动 -->
          <div class="sandbox-ticker" v-if="sandboxTickerLog.length > 0">
            <div class="ticker-label">EVENT LOG</div>
            <div class="ticker-track">
              <div class="ticker-inner">
                <span
                  v-for="(item, idx) in [...sandboxTickerLog, ...sandboxTickerLog]"
                  :key="idx"
                  class="ticker-chip"
                  :class="item.type"
                >{{ item.text }}</span>
              </div>
            </div>
          </div>

          <div class="sim-controls">
            <p class="hint" v-if="sandboxMode === 'HUNTER'">移动鼠标搜寻文明。点击发射光粒清除威胁。</p>
            <p class="hint" v-else>观察者模式：文明自动演化。点击重置宇宙。</p>
            <div class="observer-actions" v-if="sandboxMode === 'OBSERVER'">
              <NButton size="small" @click="togglePause">{{ isPaused ? 'RESUME' : 'PAUSE' }}</NButton>
              <NButton size="small" @click="initStars">BIG BANG (重置宇宙)</NButton>
            </div>
          </div>
        </div>
      </NTabPane>

      <!-- B. 世界线沙盒（合并自三体体验沙盒） -->
      <NTabPane name="worldline" tab="世界线沙盒">
        <div class="panel worldline-panel">
          <div class="worldline-intro reason">回合制宇宙演化 + 世界线归档 + 墓志铭事件流。与上方「宇宙沙盒」为同一主题的 API 驱动多智能体版本。</div>
          <div class="row config-row">
            <span class="reason">文明数量</span>
            <select v-model="civCount" class="select">
              <option :value="6">6</option>
              <option :value="8">8</option>
              <option :value="12">12</option>
            </select>
            <span class="reason">每步纪元</span>
            <select v-model="epochStep" class="select">
              <option :value="50">50</option>
              <option :value="100">100</option>
              <option :value="200">200</option>
            </select>
            <NButton size="small" type="warning" ghost @click="resetSandbox">新局</NButton>
          </div>
          <div class="toolbar">
            <span>纪元：{{ epoch }}</span>
            <span>存活文明：{{ aliveCount }}</span>
            <NButton size="small" @click="startSandbox" :disabled="running">运行</NButton>
            <NButton size="small" ghost @click="stopSandbox" :disabled="!running">暂停</NButton>
            <NButton size="small" type="warning" ghost @click="resetSandbox">重置</NButton>
            <NButton size="small" type="info" ghost :loading="bLoading" @click="stepUniverse">单步推进</NButton>
            <select v-model="tickIntervalMs" class="select">
              <option :value="1000">1s</option>
              <option :value="2000">2s</option>
              <option :value="5000">5s</option>
            </select>
          </div>
          <ModuleDiagPanel module-key="B" :status="diagB.status" :duration-ms="diagB.durationMs" :updated-at="diagB.updatedAt" :error="diagB.error" :history="diagHistB" />
          <div class="row worldline-row">
            <NInput v-model:value="worldlineName" placeholder="归档名称（可选）" />
            <NButton size="small" @click="saveWorldline">归档世界线</NButton>
            <select v-model="selectedWorldlineId" class="select">
              <option :value="null">选择归档</option>
              <option v-for="w in worldlines" :key="w.id" :value="w.id">{{ w.name }} / 纪元 {{ w.epoch }}</option>
            </select>
            <NButton size="small" ghost type="success" @click="restoreWorldline">恢复</NButton>
            <NButton size="small" ghost type="error" @click="deleteWorldline">删除</NButton>
          </div>
          <div v-if="worldlineDelta" class="diag-line reason">COMPARE | Epoch Δ={{ worldlineDelta.epochDiff }} | Alive Δ={{ worldlineDelta.aliveDiff }} | Epitaph Δ={{ worldlineDelta.epitaphDiff }}</div>
          <div v-if="survivalCurve.length >= 2" class="curve-panel">
            <div class="reason">存活曲线（存活文明数 vs 纪元）</div>
            <svg viewBox="0 0 320 90" class="curve-svg">
              <path d="M0 89 L320 89" class="curve-axis" />
              <path :d="survivalCurvePath" class="curve-line" fill="none" stroke="#00ff41" stroke-width="1.5" />
            </svg>
          </div>
          <div class="summary-card">
            <div class="reason">本局摘要</div>
            <pre class="summary-pre">{{ sessionSummaryText }}</pre>
            <NButton size="small" ghost @click="copySessionSummary">复制摘要</NButton>
          </div>
          <div class="worldline-map">
            <div v-for="a in agents" :key="a.id" class="agent-dot" :class="{ dead: !a.alive }" :style="{ left: `${a.x}%`, top: `${a.y}%` }">
              <span>{{ a.codename }}</span>
            </div>
          </div>
          <div class="logs">
            <div v-if="epitaphs.length === 0" class="reason">暂无墓志铭。宇宙仍在沉默。</div>
            <div v-for="e in epitaphs" :key="e.id" class="log-item">
              <p>纪元 {{ e.epoch }}：{{ e.attacker }} -> {{ e.victim }}</p>
              <p class="reason">{{ e.reason }}</p>
            </div>
          </div>
          <div class="logs">
            <div class="reason">红岸监听：墓志铭事件流</div>
            <div class="toolbar">
              <NButton size="tiny" ghost :type="eventFilter === 'ALL' ? 'primary' : 'default'" @click="eventFilter = 'ALL'">全部</NButton>
              <NButton size="tiny" ghost :type="eventFilter === 'STRIKE' ? 'error' : 'default'" @click="eventFilter = 'STRIKE'">打击</NButton>
              <NButton size="tiny" ghost :type="eventFilter === 'SYSTEM' ? 'warning' : 'default'" @click="eventFilter = 'SYSTEM'">系统</NButton>
              <NButton size="tiny" ghost @click="exportEventStreamJson">导出JSON</NButton>
              <NButton size="tiny" ghost @click="exportEventStreamCsv">导出CSV</NButton>
              <NButton size="tiny" type="primary" ghost @click="exportFullPackage">导出完整包 (ZIP)</NButton>
            </div>
            <div v-if="filteredEventStream.length === 0" class="reason">尚无流事件。</div>
            <div v-for="evt in filteredEventStream" :key="evt.id" class="stream-line">[{{ evt.at }}] {{ evt.text }}</div>
          </div>
        </div>
      </NTabPane>

      <!-- Tab 2: Sociology (Interactive Game Theory) -->
      <NTabPane name="sociology" tab="博弈论 (GAME)">
        <div class="theory-panel">
          <div class="game-lab">
            <div class="lab-header">
              <h2>猜疑链模拟器</h2>
              <p>在黑暗森林中，他人即地狱。请做出你的选择。</p>
            </div>

            <div class="lab-scene">
              <!-- Player (Civ A) -->
              <div class="civ-card player" :class="{ destroyed: gameStatus === 'DESTROYED' }">
                <div class="avatar a">A</div>
                <div class="info">
                  <h3>你的文明</h3>
                  <p>状态: {{ playerStatus }}</p>
                  <p>技术等级: {{ playerTech.toFixed(1) }}</p>
                </div>
              </div>

              <!-- Connection / Distance -->
              <div class="connection">
                <div class="line" :class="{ active: communicationActive }"></div>
                <div class="distance-label">{{ distance }} 光年</div>
                <div class="action-icon" v-if="actionIcon">{{ actionIcon }}</div>
              </div>

              <!-- Opponent (Civ B) -->
              <div class="civ-card opponent" :class="{ destroyed: opponentStatus === 'DESTROYED', unknown: !opponentRevealed }">
                <div class="avatar b">?</div>
                <div class="info">
                  <h3>{{ opponentRevealed ? '文明 B' : '未知信号' }}</h3>
                  <p v-if="opponentRevealed">性质: {{ opponentBenevolence ? '善意' : '恶意' }}</p>
                  <p v-else>性质: ???</p>
                  <p v-if="opponentRevealed">技术: {{ opponentTech.toFixed(1) }}</p>
        </div>
      </div>
    </div>

            <!-- Log / Outcome -->
            <div class="game-log">
              <p v-for="(log, i) in gameLogs" :key="i" :class="log.type">> {{ log.text }}</p>
            </div>

            <!-- Actions -->
            <div class="lab-actions" v-if="gameStatus === 'ACTIVE'">
              <button class="action-btn silence" @click="chooseSilence">
                <span class="icon">🤫</span>
                <span class="label">沉默 (Silence)</span>
                <span class="desc">保持静默，观察发展</span>
              </button>
              <button class="action-btn communicate" @click="chooseCommunicate">
                <span class="icon">📡</span>
                <span class="label">交流 (Contact)</span>
                <span class="desc">发送善意，暴露坐标</span>
              </button>
              <button class="action-btn strike" @click="chooseStrike">
                <span class="icon">💥</span>
                <span class="label">打击 (Strike)</span>
                <span class="desc">清理威胁，确保生存</span>
              </button>
            </div>
            
            <div class="lab-actions" v-else>
              <NButton type="primary" @click="resetGame">重新开始实验</NButton>
            </div>

            <div class="axiom-ref">
              <p>公理参考：1.生存是第一需要 2.物资总量不变</p>
            </div>
          </div>
        </div>
      </NTabPane>

      <!-- Tab 3: Swordholder System -->
      <NTabPane name="swordholder" tab="执剑人 (SWORD)">
        <div class="swordholder-lab" @mousemove="handleSwordholderMouseMove">
          <!-- 1. Status Dashboard -->
          <div class="status-dash">
            <div class="deterrence-meter">
              <NProgress
                type="dashboard"
                gap-position="bottom"
                :percentage="Math.floor(deterrence)"
                :color="deterrenceColor"
                :stroke-width="15"
                class="meter-gauge"
              >
                <template #default>
                  <div class="meter-text">
                    <span class="val">{{ Math.floor(deterrence) }}%</span>
                    <span class="label">DETERRENCE</span>
                  </div>
      </template>
              </NProgress>
            </div>
            
            <div class="psych-monitor">
              <div class="monitor-screen">
                <svg viewBox="0 0 300 100" class="graph-svg">
                  <path :d="stabilityPath" fill="none" :stroke="deterrenceColor" stroke-width="2" vector-effect="non-scaling-stroke" />
                </svg>
                <div class="scan-line"></div>
              </div>
              <div class="monitor-label">
                PSYCH-WAVE // STABILITY: {{ Math.floor(stability) }}%
              </div>
            </div>
          </div>

          <!-- 2. Trisolaris Comms -->
          <div class="trisolaris-feed" :class="trisolarisStatus.toLowerCase()">
            <div class="feed-header">
              <span class="source">SOURCE: TRISOLARIS // 4.22 LY</span>
              <span class="status-indicator">STATUS: {{ trisolarisStatus }}</span>
            </div>
            <div class="feed-content">
              <span class="cursor">></span>
              <span class="msg-text">{{ trisolarisMsg }}</span>
            </div>
          </div>

          <!-- 3. Doomsday Switch -->
          <div class="doomsday-console">
            <div class="switch-housing">
              <div class="safety-cover" :class="{ open: isButtonCoverOpen }" @click="toggleCover">
                <div class="stripes"></div>
                <span class="danger-text">危险 // 请勿开启 (DANGER)</span>
              </div>
              <button 
                class="red-button" 
                @click="triggerBroadcast" 
                :disabled="!isButtonCoverOpen || isBroadcastTriggered"
                :class="{ pressed: isBroadcastTriggered }"
              >
                <div class="btn-face">
                  <span class="nuc-icon">☢</span>
                  <span class="btn-label">广播 (BROADCAST)</span>
                </div>
              </button>
            </div>
            <p class="console-hint">
              一旦按下，无法撤销。<br>
              两个世界将同归于尽。
            </p>
          </div>
        </div>
      </NTabPane>
    </NTabs>
  </div>
</template>

<style scoped>
.df-page {
  min-height: 0;
  background: #050505;
  color: #ccc;
  display: flex;
  flex-direction: column;
}

.df-header {
  padding: 1rem 2rem;
  background: #0a0a0f;
  border-bottom: 1px solid #222;
}

.df-title {
  font-family: monospace;
  color: #00ffff;
  margin: 0;
  font-size: 1.5rem;
}

.df-subtitle {
  margin: 0;
  font-size: 0.8rem;
  color: #666;
}


.df-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
}

:deep(.n-tabs-nav) {
  background: #0a0a0f;
  border-bottom: 1px solid #222;
}

/* Simulator */
.sim-container {
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.mode-switch {
  display: flex;
  gap: 0.5rem;
}

.mode-switch button {
  background: #111;
  border: 1px solid #333;
  color: #666;
  padding: 0.2rem 0.5rem;
  font-family: monospace;
  cursor: pointer;
}

.mode-switch button.active {
  background: #003333;
  color: #00ffff;
  border-color: #00ffff;
}

.hud-top {
  display: flex;
  gap: 2rem;
  padding: 1rem;
  background: rgba(0,0,0,0.8);
  border-bottom: 1px solid #333;
}

.hud-item {
  display: flex;
  flex-direction: column;
}

.label { font-size: 0.6rem; color: #666; font-family: monospace; }
.value { font-size: 1.2rem; font-family: monospace; color: #fff; }
.text-green { color: #00ff41; }
.text-red { color: #ff3333; }

.canvas-wrapper {
  position: relative;
  flex: 1;
  background: #000;
  overflow: hidden;
  cursor: none; /* Hide default cursor for crosshair */
}

.star-canvas {
  display: block;
  width: 100%;
  height: 100%;
}

.scan-overlay {
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent 0,
    transparent 2px,
    rgba(0, 255, 255, 0.03) 3px
  );
  pointer-events: none;
}

.observer-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 1rem;
}

.civ-tooltip {
  position: absolute;
  transform: translate(15px, 15px);
  background: rgba(0, 0, 0, 0.9);
  border: 1px solid #333;
  padding: 0.8rem;
  pointer-events: none;
  z-index: 10;
  width: 200px;
  backdrop-filter: blur(5px);
  font-family: monospace;
}

.tt-header {
  color: #00ffff;
  font-weight: bold;
  border-bottom: 1px solid #333;
  padding-bottom: 0.3rem;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.tt-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.2rem;
  font-size: 0.75rem;
  color: #ccc;
}

.tt-log {
  margin-top: 0.5rem;
  font-size: 0.7rem;
  color: #ffcc00;
  border-top: 1px dashed #333;
  padding-top: 0.3rem;
  line-height: 1.2;
}

/* 跑马灯：底部单行滚动，不阻断浏览 */
.sandbox-ticker {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  height: 36px;
  padding: 0 1rem;
  background: rgba(0, 0, 0, 0.85);
  border-top: 1px solid #333;
  flex-shrink: 0;
  overflow: hidden;
}

.ticker-label {
  flex-shrink: 0;
  font-family: monospace;
  font-size: 0.7rem;
  color: #666;
  letter-spacing: 0.1em;
}

.ticker-track {
  flex: 1;
  overflow: hidden;
  mask-image: linear-gradient(to right, transparent, black 2%, black 98%, transparent);
  -webkit-mask-image: linear-gradient(to right, transparent, black 2%, black 98%, transparent);
}

.ticker-inner {
  display: inline-flex;
  align-items: center;
  gap: 1rem;
  white-space: nowrap;
  padding-right: 2rem;
  animation: ticker-scroll 45s linear infinite;
}

@keyframes ticker-scroll {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}

.ticker-chip {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  font-family: monospace;
  font-size: 0.75rem;
  border-radius: 2px;
  flex-shrink: 0;
}

.ticker-chip.destroy {
  color: #ff6666;
  background: rgba(255, 50, 50, 0.15);
  border: 1px solid rgba(255, 80, 80, 0.4);
}

.ticker-chip.strike {
  color: #00ff88;
  background: rgba(0, 255, 136, 0.08);
  border: 1px solid rgba(0, 255, 136, 0.3);
}

.ticker-chip.warn {
  color: #ffaa00;
  background: rgba(255, 170, 0, 0.1);
  border: 1px solid rgba(255, 170, 0, 0.35);
}

.sim-controls {
  padding: 1rem;
  text-align: center;
  background: #0a0a0f;
}

/* Sociology */
.theory-panel {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.axiom-box {
  margin-bottom: 3rem;
  border: 1px solid #444;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.05);
}

.axiom-box h2, .chain-box h2 {
  color: #00ffff;
  font-family: monospace;
  margin-bottom: 1.5rem;
}

.axiom-box ul {
  list-style: none;
  padding: 0;
}
.axiom-box li {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  font-family: 'Noto Serif SC', serif;
}

.chain-diagram {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 3rem 0;
}

.civ-node {
  width: 150px;
  height: 150px;
  border: 2px solid #666;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 1rem;
}
.civ-a { border-color: #00ffff; color: #00ffff; }
.civ-b { border-color: #ff3333; color: #ff3333; }

.arrow { font-size: 2rem; color: #666; }

.conclusion {
  margin-top: 2rem;
  font-style: italic;
  color: #aaa;
  line-height: 1.6;
}

/* Swordholder System */
.swordholder-lab {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding: 2rem;
  background: radial-gradient(circle at 50% 30%, #111, #000);
  height: 100%;
}

.status-dash {
  display: flex;
  justify-content: center;
  gap: 4rem;
  align-items: center;
  flex-wrap: wrap;
}

.deterrence-meter {
  position: relative;
  width: 200px;
  height: 200px;
}

.meter-gauge {
  width: 100%;
  height: 100%;
}

.meter-text {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.meter-text .val {
  font-size: 2.5rem;
  font-family: monospace;
  font-weight: bold;
  color: #fff;
}

.psych-monitor {
  width: 300px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.monitor-screen {
  background: #000;
  border: 1px solid #333;
  height: 100px;
  position: relative;
  overflow: hidden;
}

.graph-svg {
  width: 100%;
  height: 100%;
}

.graph-svg path {
  transition: d 0.1s linear;
}

.scan-line {
  position: absolute;
  top: 0; bottom: 0; width: 2px;
  background: rgba(0, 255, 255, 0.5);
  box-shadow: 0 0 10px #00ffff;
  animation: scan 2s linear infinite;
}

@keyframes scan { 0% { left: 0; } 100% { left: 100%; } }

.monitor-label {
  font-family: monospace;
  font-size: 0.8rem;
  color: #666;
  text-align: right;
}

.trisolaris-feed {
  background: #0a0a0f;
  border: 1px solid #333;
  padding: 1rem;
  font-family: monospace;
  min-height: 100px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.feed-header {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid #222;
  padding-bottom: 0.5rem;
  color: #666;
  font-size: 0.8rem;
}

.feed-content {
  font-size: 1.1rem;
  color: #00ffff;
}

.trisolaris-feed.strike { border-color: #ff3333; animation: shake 0.5s infinite; }
.trisolaris-feed.strike .msg-text { color: #ff3333; }

.doomsday-console {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: auto;
  gap: 1rem;
}

.switch-housing {
  position: relative;
  width: 200px;
  height: 200px;
  background: #222;
  border-radius: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.safety-cover {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255, 200, 0, 0.1);
  border: 2px solid #ffcc00;
  border-radius: 10px;
  z-index: 10;
  cursor: pointer;
  transform-origin: top center;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  justify-content: center;
  align-items: center;
  background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(255, 204, 0, 0.1) 10px, rgba(255, 204, 0, 0.1) 20px);
}

.safety-cover.open {
  transform: rotateX(100deg);
  opacity: 0.5;
}

.danger-text {
  color: #ffcc00;
  font-weight: bold;
  font-family: monospace;
  letter-spacing: 2px;
  background: rgba(0,0,0,0.8);
  padding: 0.2rem 0.5rem;
  border: 1px solid #ffcc00;
}

.red-button {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #ff6666, #cc0000);
  border: none;
  box-shadow: 0 10px 0 #990000, 0 10px 20px rgba(0,0,0,0.5);
  cursor: pointer;
  transition: all 0.1s;
  display: flex;
  justify-content: center;
  align-items: center;
}

.red-button:active:not(:disabled), .red-button.pressed {
  transform: translateY(10px);
  box-shadow: 0 0 0 #990000, inset 0 5px 10px rgba(0,0,0,0.5);
}

.red-button:disabled {
  filter: grayscale(1);
  cursor: not-allowed;
}

.btn-face {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #fff;
  text-shadow: 0 2px 2px rgba(0,0,0,0.5);
}

.nuc-icon { font-size: 2rem; }
.btn-label { font-size: 0.7rem; font-weight: bold; }

.console-hint {
  color: #666;
  text-align: center;
  font-size: 0.8rem;
}

/* Game Theory Lab */
.game-lab {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding: 1rem;
  background: rgba(0,0,0,0.5);
  border: 1px solid #333;
}

.lab-header {
  text-align: center;
  border-bottom: 1px solid #333;
  padding-bottom: 1rem;
}

.lab-scene {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem;
  background: #080808;
  border: 1px dashed #333;
  position: relative;
}

.civ-card {
  width: 150px;
  height: 180px;
  background: #111;
  border: 2px solid #555;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  text-align: center;
  transition: all 0.3s;
}

.civ-card.player { border-color: #00ffff; }
.civ-card.opponent { border-color: #ff3333; }
.civ-card.opponent.unknown { border-color: #666; border-style: dashed; }
.civ-card.destroyed { opacity: 0.3; filter: grayscale(1); border-color: #333; transform: scale(0.9); }

.avatar {
  width: 50px; height: 50px;
  border-radius: 50%;
  background: #222;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin-bottom: 1rem;
  border: 1px solid #fff;
}
.player .avatar { background: #003333; border-color: #00ffff; }
.opponent .avatar { background: #330000; border-color: #ff3333; }
.unknown .avatar { background: #222; border-color: #666; color: #666; }

.info h3 { margin: 0 0 0.5rem 0; font-size: 1rem; color: #ccc; }
.info p { margin: 0; font-size: 0.8rem; color: #888; }

.connection {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.line {
  width: 100%;
  height: 2px;
  background: #333;
  position: relative;
}
.line.active { background: #00ffff; box-shadow: 0 0 10px #00ffff; }

.distance-label {
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: #666;
}

.action-icon {
  position: absolute;
  top: -20px;
  font-size: 2rem;
  animation: fly 1s linear forwards;
}

@keyframes fly { from { left: 0%; opacity: 0; } 50% { opacity: 1; } to { left: 100%; opacity: 0; } }

.game-log {
  height: 150px;
  background: #000;
  border: 1px solid #333;
  padding: 1rem;
  overflow-y: auto;
  font-family: monospace;
  font-size: 0.9rem;
}
.game-log p { margin: 0.2rem 0; }
.game-log .info { color: #888; }
.game-log .success { color: #00ff41; }
.game-log .warn { color: #ff9900; }
.game-log .error { color: #ff3333; }

.lab-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.action-btn {
  flex: 1;
  background: #111;
  border: 1px solid #333;
  color: #ccc;
  padding: 1rem;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: all 0.2s;
}

.action-btn:hover { background: #222; border-color: #666; }
.action-btn.strike:hover { border-color: #ff3333; background: #330000; }
.action-btn.communicate:hover { border-color: #00ffff; background: #003333; }

.icon { font-size: 1.5rem; margin-bottom: 0.5rem; }
.label { font-weight: bold; margin-bottom: 0.2rem; }
.desc { font-size: 0.7rem; color: #666; }

.axiom-ref {
  text-align: center;
  font-size: 0.8rem;
  color: #444;
  margin-top: 1rem;
}

/* B. 世界线沙盒（合并自三体体验沙盒） */
.worldline-panel {
  border: 1px solid #252525;
  background: rgba(0, 0, 0, 0.4);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}
.worldline-intro { margin-bottom: 0.5rem; }
.worldline-panel .row { display: grid; gap: 0.6rem; }
.worldline-panel .reason { font-size: 0.8rem; color: #7a9a9a; }
.config-row, .worldline-row { display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem 1rem; }
.config-row .select, .worldline-row .select { min-width: 120px; }
.toolbar { display: flex; gap: 0.6rem; align-items: center; font-family: monospace; flex-wrap: wrap; }
.diag-line { font-family: monospace; font-size: 12px; color: #8ba5a5; border: 1px dashed #294040; padding: 0.3rem 0.45rem; }
.curve-panel { border: 1px solid #1f1f1f; padding: 0.4rem; border-radius: 4px; }
.curve-svg { width: 100%; height: 90px; display: block; }
.curve-axis { stroke: #333; stroke-width: 1; fill: none; }
.curve-line { fill: none; stroke: #00ff41; stroke-width: 1.5; }
.summary-card { border: 1px solid #1e2e2e; padding: 0.6rem; background: rgba(0, 10, 15, 0.3); border-radius: 4px; }
.summary-pre { margin: 0; font-size: 0.8rem; white-space: pre-wrap; color: #b8d0d0; max-height: 120px; overflow: auto; }
.worldline-map { position: relative; height: 180px; background: #080808; border: 1px solid #222; border-radius: 4px; }
.agent-dot { position: absolute; transform: translate(-50%, -50%); padding: 2px 6px; font-size: 0.7rem; background: rgba(0, 200, 100, 0.3); border: 1px solid #00cc88; border-radius: 2px; color: #00ff88; }
.agent-dot.dead { background: rgba(80, 80, 80, 0.5); border-color: #444; color: #666; }
.worldline-panel .logs { border: 1px solid #1e2e2e; padding: 0.6rem; background: rgba(0, 10, 15, 0.2); border-radius: 4px; max-height: 200px; overflow-y: auto; }
.log-item { margin-bottom: 0.5rem; font-size: 0.85rem; }
.log-item p { margin: 0.2rem 0; }
.stream-line { font-size: 0.75rem; color: #9ab5b5; margin-bottom: 0.2rem; font-family: monospace; }
</style>
