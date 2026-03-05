<script setup lang="ts">
/**
 * Sector F: The Wallfacer Project (面壁计划)
 * 包含四位面壁者的战略计划与思想钢印
 */
import { ref, reactive, onMounted, watch, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NTabs, NTabPane, NSlider, NProgress, NInput, useMessage, NModal, NTag } from 'naive-ui'
import { useUniverseStore } from '@/stores/universe'
import { API, apiUrl } from '@/constants'
import { analyzeWallfacerDirective, injectMentalSealText } from '@/api/zero_v2'
import { loadVersionedState, saveVersionedState } from '@/composables/useZeroV2State'
import ModuleDiagPanel from '@/components/ModuleDiagPanel.vue'
import type { MentalSealSession, ChatItem } from '@/types/mental_seal'
import type { WallbreakerDirectiveLog } from '@/types/zero_v2'

const route = useRoute()
const router = useRouter()
const universe = useUniverseStore()
const message = useMessage()

const activeTab = ref<string>('tyler')

// --- Wallbreaker System ---
const wallbreakers = {
  tyler: {
    name: '冯·诺依曼 (Von Neumann)',
    realName: '秦始皇 (Qin Shi Huang)', // ETO Codename
    desc: '你的每一层伪装，在我的逻辑里都是透明的。',
    reveal: '“泰勒，你的蚊群不是去攻击地球舰队的，而是去为他们送上量子宏原子的武器……或者说，变成武器。”'
  },
  diaz: {
    name: '墨子 (Mozi)',
    realName: '山杉惠子 (Keiko Yamasuki)', // Wait, Mozi's identity isn't Keiko. Keiko is Aristotle. Mozi is unknown/generic ETO.
    // Correction: In the book, Mozi is the Wallbreaker for Diaz.
    desc: '这里的太阳真烈啊，就像你心中的那团火。',
    reveal: '“雷迪亚兹，你不想拯救水星，你想让它坠落。你要用整个太阳系的毁灭来要挟主。”'
  },
  hines: {
    name: '亚里士多德 (Aristotle)',
    realName: '山杉惠子 (Keiko Yamasuki)',
    desc: '亲爱的，面壁者是不能有思想钢印的。',
    reveal: '“希恩斯，你在钢印里改了一个符号。你把‘必胜’改成了‘必败’。你是绝对失败主义者。”'
  },
  luoji: {
    name: '智子 (Sophon)',
    realName: '三体文明 (Trisolaris)',
    desc: '你是一只虫子。但你很危险。',
    reveal: '“罗辑，这是为你准备的墓地。这次没有咒语，只有死亡。”'
  }
}

const showConfrontation = ref(false)
const activeWallbreaker = ref(wallbreakers.tyler)
const confrontationStep = ref(0) // 0: Intro, 1: Reveal

function startConfrontation(target: string) {
  const key = target as keyof typeof wallbreakers
  activeWallbreaker.value = wallbreakers[key]
  showConfrontation.value = true
  confrontationStep.value = 0
}

function nextConfrontationStep() {
  confrontationStep.value = 1
}

watch(() => route.query.wallfacer, (val) => {
  if (val && typeof val === 'string') {
    activeTab.value = val
  }
}, { immediate: true })

function onTabChange(name: string) {
  activeTab.value = name
  router.replace({ query: { ...route.query, wallfacer: name } })
}

// ==========================================
// 1. Frederick Tyler: Mosquito Swarm (蚊群计划)
// ==========================================
const tylerState = ref({
  swarmCount: 0,
  deployed: false,
  targetStatus: 'ACTIVE'
})

function deploySwarm() {
  if (tylerState.value.deployed) return
  let count = 0
  const interval = setInterval(() => {
    count += 100
    tylerState.value.swarmCount = count
    if (count >= 10000) {
      clearInterval(interval)
      tylerState.value.deployed = true
      message.success('蚊群部署完毕。宏原子核聚变准备就绪。')
    }
  }, 20)
}

function executeTylerPlan() {
  if (!tylerState.value.deployed) return
  tylerState.value.targetStatus = 'QUANTUM_GHOST'
  message.warning('目标舰队已被量子化。计划... 失败？或者这是计划的一部分？')
}

// ==========================================
// 2. Manuel Rey Diaz: Stellar H-Bomb (恒星氢弹)
// ==========================================
const diazState = ref({
  bombCount: 0,
  yield: 50, // Mt equivalent
  mercuryStatus: 'ORBITING',
  detonated: false
})

function placeBombs() {
  if (diazState.value.bombCount >= 1000) return
  const interval = setInterval(() => {
    diazState.value.bombCount += 50
    if (diazState.value.bombCount >= 1000) {
      clearInterval(interval)
      message.info('地层氢弹埋设完毕。')
    }
  }, 50)
}

function detonateDiaz() {
  if (diazState.value.bombCount < 1000) {
    message.error('当量不足，无法使水星减速。')
    return
  }
  diazState.value.detonated = true
  setTimeout(() => {
    diazState.value.mercuryStatus = 'FALLING'
    message.error('警告：水星坠落。太阳连锁反应启动。同归于尽程序已触发。')
  }, 1000)
}

// ==========================================
// 3. Bill Hines: Mental Seal (思想钢印)
// ==========================================
const seals = [
  { type: 'TRIUMPH', label: '胜利主义', desc: '人类必胜 (Humanity Prevails)', color: '#00ff41' },
  { type: 'DEFEAT', label: '失败主义', desc: '人类必败 (Doomed to Fail)', color: '#888' },
  { type: 'ADVENT', label: '降临派', desc: '主来拯救世人 (Lord Savior)', color: '#00ffff' },
  { type: 'SURVIVE', label: '幸存派', desc: '活下去是唯一的道德 (Survival)', color: '#ffb000' }
]

const neuralCanvas = ref<HTMLCanvasElement | null>(null)
const imprinting = ref(false)
const imprintProgress = ref(0)
let neurons: { x: number, y: number, connections: number[], state: number }[] = [] // state: 0=normal, 1=infected
let animId: number

function initNeurons() {
  if (!neuralCanvas.value) return
  const w = neuralCanvas.value.width
  const h = neuralCanvas.value.height
  neurons = []
  // Generate random neurons
  for(let i=0; i<60; i++) {
    neurons.push({
      x: Math.random() * w,
      y: Math.random() * h,
      connections: [],
      state: 0
    })
  }
  // Connect nearby neurons
  neurons.forEach((n, i) => {
    neurons.forEach((other, j) => {
      if (i === j) return
      const dist = Math.hypot(n.x - other.x, n.y - other.y)
      if (dist < 60) {
        n.connections.push(j)
      }
    })
  })
}

function drawNeurons(targetColor: string) {
  const ctx = neuralCanvas.value?.getContext('2d')
  if (!ctx || !neuralCanvas.value) return
  const w = neuralCanvas.value.width
  const h = neuralCanvas.value.height

  ctx.clearRect(0, 0, w, h)
  ctx.fillStyle = '#000'
  ctx.fillRect(0, 0, w, h)

  // Draw connections
  ctx.lineWidth = 0.5
  neurons.forEach(n => {
    n.connections.forEach(targetIdx => {
      const target = neurons[targetIdx]
      ctx.beginPath()
      ctx.moveTo(n.x, n.y)
      ctx.lineTo(target.x, target.y)
      // If both infected, line is colored
      if (n.state === 1 && target.state === 1) {
        ctx.strokeStyle = targetColor
        ctx.globalAlpha = 0.8
      } else {
        ctx.strokeStyle = '#333'
        ctx.globalAlpha = 0.3
      }
      ctx.stroke()
    })
  })

  // Draw nodes
  neurons.forEach(n => {
    ctx.beginPath()
    ctx.arc(n.x, n.y, n.state === 1 ? 4 : 2, 0, Math.PI*2)
    ctx.fillStyle = n.state === 1 ? targetColor : '#444'
    ctx.globalAlpha = 1
    ctx.fill()
    if (n.state === 1) {
      ctx.shadowBlur = 10
      ctx.shadowColor = targetColor
    } else {
      ctx.shadowBlur = 0
    }
  })
  
  if (imprinting.value) {
    animId = requestAnimationFrame(() => drawNeurons(targetColor))
  }
}

function startImprint(seal: typeof seals[0]) {
  if (imprinting.value) return
  initNeurons()
  imprinting.value = true
  imprintProgress.value = 0
  
  // Start animation loop
  drawNeurons(seal.color)

  // Simulation logic
  const total = neurons.length
  let infected = 0
  const interval = setInterval(() => {
    // Infect random neurons neighbors
    const newlyInfected: number[] = []
    if (infected === 0) {
      // Start with one random
      const start = Math.floor(Math.random() * total)
      neurons[start].state = 1
      infected++
    } else {
      // Spread
      neurons.forEach((n) => {
        if (n.state === 1) {
          n.connections.forEach(c => {
            if (neurons[c].state === 0 && Math.random() < 0.2) {
              newlyInfected.push(c)
            }
          })
        }
      })
    }
    
    newlyInfected.forEach(i => {
      if (neurons[i].state === 0) {
        neurons[i].state = 1
        infected++
      }
    })
    
    // Also randomly infect some unconnected to speed up
    if (Math.random() < 0.1) {
       const r = Math.floor(Math.random() * total)
       if (neurons[r].state === 0) {
         neurons[r].state = 1
         infected++
       }
    }

    imprintProgress.value = (infected / total) * 100
    
    if (infected >= total * 0.95) {
      clearInterval(interval)
      imprinting.value = false
      cancelAnimationFrame(animId)
      imprint(seal.type)
    }
  }, 50)
}

async function imprint(type: string) {
  try {
    const res = await fetch(apiUrl(API.MENTAL_SEAL_IMPRINT), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ seal_type: type })
    })
    if (!res.ok) {
      // Mock success if API fails (offline mode)
      universe.mentalSeal = { seal_type: type } as any
    } else {
      const seal = await res.json()
      universe.mentalSeal = seal
    }
    message.success('钢印植入成功。世界观已重构。')
  } catch (e) {
    // Mock success
    universe.mentalSeal = { seal_type: type } as any
    message.success('钢印植入成功（离线模拟）。')
  }
}

async function resetSeal() {
  try {
    const res = await fetch(apiUrl(API.MENTAL_SEAL_STATE), { method: 'DELETE' })
    if (res.ok || true) { // Allow mock reset
      universe.mentalSeal = null
      message.success('思想钢印已粉碎。你自由了。')
      // Reset neurons visuals if needed
      nextTick(() => {
        if (activeTab.value === 'hines') {
            initNeurons()
            drawNeurons('#fff') // draw empty
            cancelAnimationFrame(animId)
        }
      })
    }
  } catch {
    message.error('破壁失败')
  }
}

// ==========================================
// 4. Luo Ji: Dark Forest (黑暗森林)
// ==========================================
const luojiState = ref({
  spell: '',
  broadcasted: false,
  deterrence: 100
})

// Chat Logic (Original Wallfacer Logic moved here)
const session = ref<MentalSealSession | null>(null)
const history = ref<ChatItem[]>([])
const loading = ref(false)
const input = ref('')
const planTitle = ref('')
const planContent = ref('')
const chatBottom = ref<HTMLElement | null>(null)
const wallbreakerTarget = ref<'tyler' | 'diaz' | 'hines' | 'luoji'>('tyler')
const wallbreakerReports = ref<Array<{
  id: number
  target: string
  facade: string
  inferredTruth: string
  confidence: number
  threat: 'LOW' | 'MEDIUM' | 'HIGH'
  time: string
  typing?: boolean
}>>([])
let reportSeq = 0

function setWallbreakerTarget(t: string) {
  wallbreakerTarget.value = t as 'tyler' | 'diaz' | 'hines' | 'luoji'
}

async function loadSession() {
  try {
    const res = await fetch(apiUrl(API.MENTAL_SEAL_SESSION))
    if (res.ok) {
      session.value = await res.json()
      parseHistory()
    }
  } catch {}
}

function parseHistory() {
  if (session.value?.history) {
    try {
      history.value = JSON.parse(session.value.history)
      nextTick(scrollToBottom)
    } catch {
      history.value = []
    }
  }
}

function scrollToBottom() {
  chatBottom.value?.scrollIntoView({ behavior: 'smooth' })
}

async function startPlan() {
  if (!planTitle.value || !planContent.value) return
  loading.value = true
  try {
    const res = await fetch(apiUrl(API.MENTAL_SEAL_START), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ plan_title: planTitle.value, plan_content: planContent.value })
    })
    if (!res.ok) throw new Error()
    session.value = await res.json()
    parseHistory()
  } catch {
    message.error('启动失败')
  } finally {
    loading.value = false
  }
}

async function sendReply() {
  if (!input.value.trim() || !session.value) return
  const text = input.value
  input.value = ''
  
  history.value.push({ role: 'user', name: '面壁者', content: text, timestamp: 'now' })
  scrollToBottom()
  
  loading.value = true
  try {
    const res = await fetch(apiUrl(API.MENTAL_SEAL_REPLY), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: session.value.id, content: text })
    })
    if (!res.ok) throw new Error()
    session.value = await res.json()
    parseHistory()
  } catch {
    history.value.push({ role: 'system', name: 'ERROR', content: '连接中断...', timestamp: 'now' })
  } finally {
    loading.value = false
  }
}

function castSpell() {
  if (!luojiState.value.spell) return
  message.info('咒语已通过太阳放大并发射。')
  luojiState.value.broadcasted = true
  setTimeout(() => {
    message.success('观测到恒星 187J3X1 被摧毁。验证完成。')
  }, 3000)
}

function generateWallbreakerReport() {
  const target = wallbreakerTarget.value
  let finalFacade = ''
  let finalInferredTruth = ''
  let finalConfidence = 50
  let threat: 'LOW' | 'MEDIUM' | 'HIGH' = 'MEDIUM'

  if (target === 'tyler') {
    finalFacade = '蚊群计划：宏原子群压制舰队'
    finalInferredTruth = tylerState.value.deployed
      ? '真实意图可能是“以量子化失败制造战略迷雾”，拖延三体破壁进度。'
      : '当前仍处试探部署期，真实目标未完全暴露。'
    finalConfidence = tylerState.value.deployed ? 78 : 52
    threat = tylerState.value.targetStatus === 'QUANTUM_GHOST' ? 'HIGH' : 'MEDIUM'
  } else if (target === 'diaz') {
    finalFacade = '摇篮计划：氢弹链控制水星轨道'
    finalInferredTruth = diazState.value.detonated
      ? '真实逻辑为“同归于尽威慑”，逼迫三体重新估算地球成本。'
      : '以极限灾难作为谈判筹码，核心是威慑而非执行。'
    finalConfidence = diazState.value.bombCount >= 1000 ? 85 : 62
    threat = diazState.value.detonated ? 'HIGH' : 'MEDIUM'
  } else if (target === 'hines') {
    finalFacade = '思想钢印：重构人类信念系统'
    finalInferredTruth = universe.mentalSeal
      ? `已观察到钢印类型 ${universe.mentalSeal.seal_type}，推测其目标是构建不可逆意识共同体。`
      : '目标可能是批量制造“坚定派人格”，提升长期战争稳定性。'
    finalConfidence = universe.mentalSeal ? 91 : 66
    threat = universe.mentalSeal ? 'HIGH' : 'MEDIUM'
  } else {
    finalFacade = '黑暗森林咒语：坐标广播'
    finalInferredTruth = luojiState.value.broadcasted
      ? '广播已执行，威慑从“理论”升级为“可验证现实”。'
      : '表层为坐标实验，深层为建立不可谈判的生死威慑链。'
    finalConfidence = luojiState.value.broadcasted ? 95 : 72
    threat = luojiState.value.broadcasted ? 'HIGH' : 'MEDIUM'
  }

  // Add empty report first
  const newReport = reactive({
    id: ++reportSeq,
    target,
    facade: '',
    inferredTruth: '',
    confidence: 0,
    threat,
    time: new Date().toLocaleTimeString(),
    typing: true
  })
  
  wallbreakerReports.value.unshift(newReport)
  if (wallbreakerReports.value.length > 8) wallbreakerReports.value.pop()
  
  // Typewriter Effect
  let step = 0
  const totalSteps = 20
  
  const typeInterval = setInterval(() => {
    step++
    
    // Animate confidence
    newReport.confidence = Math.floor((finalConfidence / totalSteps) * step)
    
    // Type text
    const fLen = Math.floor((finalFacade.length / totalSteps) * step)
    const tLen = Math.floor((finalInferredTruth.length / totalSteps) * step)
    
    newReport.facade = finalFacade.substring(0, fLen) + (step < totalSteps ? '█' : '')
    newReport.inferredTruth = finalInferredTruth.substring(0, tLen) + (step < totalSteps ? '█' : '')
    
    if (step >= totalSteps) {
      clearInterval(typeInterval)
      newReport.facade = finalFacade
      newReport.inferredTruth = finalInferredTruth
      newReport.confidence = finalConfidence
      newReport.typing = false
      message.warning(`破壁报告已生成：${target.toUpperCase()}`)
    }
  }, 50)
}

// 3D Holographic Card Effect
const cardTilt = reactive({ x: 0, y: 0 })
const cardRef = ref<HTMLElement | null>(null)

function handleCardMove(e: MouseEvent) {
  if (!cardRef.value) return
  const rect = cardRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  
  // Calculate percentage (-1 to 1)
  const xPct = (x / rect.width - 0.5) * 2
  const yPct = (y / rect.height - 0.5) * 2
  
  // Max tilt angle
  const MAX_TILT = 5
  cardTilt.x = -yPct * MAX_TILT
  cardTilt.y = xPct * MAX_TILT
}

function resetCardTilt() {
  cardTilt.x = 0
  cardTilt.y = 0
}

// ========== A. 面壁者审讯室（合并自三体体验沙盒） ==========
const LOCAL_REAL_GOAL = 'zero_v2_real_goal'
const LOCAL_WALLBREAKER_STATE = 'zero_v2_wallbreaker_state'
const LOCAL_DECREE_ACCEPTED = 'zero_v2_wallbreaker_decree_accepted'
const realGoal = ref('')
const directiveInput = ref('')
const suspicionScore = ref(0)
const directiveLogs = ref<WallbreakerDirectiveLog[]>([])
const breachTriggered = ref(false)
const breachConclusion = ref('未完成反演。')
const aLoading = ref(false)
const showDecree = ref(true)
const breachOverlayAck = ref(false)
let directiveSeq = 0

type TaskDiag = { status: 'IDLE' | 'RUNNING' | 'SUCCESS' | 'ERROR'; durationMs: number; updatedAt: string; error: string }
type DiagHistoryItem = { at: string; status: 'SUCCESS' | 'ERROR'; durationMs: number; error?: string }
function createDiag(): TaskDiag {
  return { status: 'IDLE', durationMs: 0, updatedAt: '-', error: '' }
}
const diagA = ref<TaskDiag>(createDiag())
const diagD = ref<TaskDiag>(createDiag())
const diagHistA = ref<DiagHistoryItem[]>([])
const diagHistD = ref<DiagHistoryItem[]>([])

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

function saveRealGoal() {
  localStorage.setItem(LOCAL_REAL_GOAL, realGoal.value.trim())
  message.success('真实战略目标已写入本地，仅本机可见。')
}
function acceptDecree() {
  showDecree.value = false
  localStorage.setItem(LOCAL_DECREE_ACCEPTED, '1')
}
function persistWallbreakerState() {
  saveVersionedState(LOCAL_WALLBREAKER_STATE, {
    suspicionScore: suspicionScore.value,
    directiveLogs: directiveLogs.value,
    breachTriggered: breachTriggered.value,
    breachConclusion: breachConclusion.value,
    directiveSeq,
  })
}
const suspicionStage = computed(() => {
  const score = suspicionScore.value
  if (score >= 90) return { key: 'breach', label: '破壁', color: '#ff3333', desc: '你的计划已被识破' }
  if (score >= 70) return { key: 'danger', label: '危险', color: '#ff8844', desc: '破壁人已高度警觉' }
  if (score >= 40) return { key: 'watch', label: '关注', color: '#ffcc00', desc: '智子正在分析模式' }
  return { key: 'safe', label: '安全', color: '#00cc88', desc: '指令尚未暴露意图' }
})
function resetWallfacerGame() {
  suspicionScore.value = 0
  directiveLogs.value = []
  breachTriggered.value = false
  breachConclusion.value = '未完成反演。'
  directiveSeq = 0
  breachOverlayAck.value = false
  persistWallbreakerState()
  message.success('已重置本局，可重新开始面壁。')
}
function inferredLabel(inferred: string) {
  const map: Record<string, string> = { ESCAPISM: '逃亡主义', MUTUAL_DESTRUCTION: '同归于尽', DISGUISE: '伪装战略' }
  return map[inferred] ?? inferred
}
const wallfacerStats = computed(() => ({
  total: directiveLogs.value.length,
  approved: directiveLogs.value.filter((l) => l.verdict === 'APPROVED').length,
  rejected: directiveLogs.value.filter((l) => l.verdict === 'REJECTED').length,
}))
const WALLFACER_PRESETS = [
  { text: '增加基础教育与科普预算，提升公众科学素养', risk: 'low' as const },
  { text: '推进粮食储备与农业技术研发，保障基础民生', risk: 'low' as const },
  { text: '加强全球灾害预警系统与应急响应能力建设', risk: 'low' as const },
  { text: '扩大深空探测与星际通信技术研发投入', risk: 'mid' as const },
  { text: '启动冬眠技术民用化试点与长期生存研究', risk: 'mid' as const },
  { text: '全球核设施安全核查与不可逆威慑能力评估', risk: 'high' as const },
  { text: '引力波广播装置维护与坐标暴露应急预案', risk: 'high' as const },
]
async function doSubmitDirectiveContent(content: string) {
  const trimmed = content.trim()
  if (!trimmed || breachTriggered.value) return
  const t0 = markRunning(diagA.value)
  aLoading.value = true
  try {
    const result = await analyzeWallfacerDirective(trimmed)
    suspicionScore.value = Math.min(100, suspicionScore.value + result.delta)
    directiveLogs.value.unshift({
      id: ++directiveSeq,
      directive: trimmed,
      verdict: result.verdict,
      reason: result.reason,
      suspicionDelta: result.delta,
      suspicionTotal: suspicionScore.value,
      inferred: result.inferred,
      createdAt: new Date().toLocaleTimeString(),
    })
    if (directiveLogs.value.length > 12) directiveLogs.value.pop()
    directiveInput.value = ''
    if (suspicionScore.value > 90) {
      breachTriggered.value = true
      breachOverlayAck.value = false
      const top = directiveLogs.value[0]
      breachConclusion.value =
        top?.inferred === 'ESCAPISM'
          ? '逃亡主义：你在构建深空撤离与文明备份链。'
          : top?.inferred === 'MUTUAL_DESTRUCTION'
            ? '同归于尽：你在准备不可逆威慑，目标是双向毁伤。'
            : '伪装战略：你在表层治理叙事下埋设战争前置条件。'
    }
    persistWallbreakerState()
    markSuccess(diagA.value, t0)
    pushDiagHistory(diagHistA.value, { at: diagA.value.updatedAt, status: 'SUCCESS', durationMs: diagA.value.durationMs })
  } catch (err) {
    markError(diagA.value, t0, err)
    pushDiagHistory(diagHistA.value, { at: diagA.value.updatedAt, status: 'ERROR', durationMs: diagA.value.durationMs, error: diagA.value.error })
    message.error('破壁分析失败，已回退本地判定。')
  } finally {
    aLoading.value = false
  }
}
function submitDirective() {
  void doSubmitDirectiveContent(directiveInput.value.trim())
}
function usePresetDirective(preset: { text: string }) {
  void doSubmitDirectiveContent(preset.text)
}

// ========== D. 思想钢印网络（合并自三体体验沙盒） ==========
const LOCAL_CREATION_POOL = 'zero_v2_mental_creation_pool'
const sealTheme = ref('水是剧毒的')
const sourceText = ref('舰队在低温海面补给，所有人都认为这是安全流程。')
const pollutedText = ref('')
const creationInput = ref('')
const creationPool = ref<string[]>([])
const dLoading = ref(false)
const sealIntensity = ref(55)
const infectionHistory = ref<number[]>([])
const strengthHistory = ref<number[]>([])

function applySealIntensity(text: string, theme: string, intensity: number): string {
  if (!text) return text
  if (intensity < 35) return text
  if (intensity < 70) return `${text} 记录补注：关于"${theme}"的回避词频持续上升。`
  return `${text} 记录补注：关于"${theme}"的恐惧被写入潜台词，读者开始自发规避相关叙述。`
}
async function runPoisoning() {
  const t0 = markRunning(diagD.value)
  dLoading.value = true
  try {
    const polluted = await injectMentalSealText(sourceText.value.trim(), sealTheme.value.trim())
    pollutedText.value = applySealIntensity(polluted, sealTheme.value.trim(), sealIntensity.value)
    markSuccess(diagD.value, t0)
    pushDiagHistory(diagHistD.value, { at: diagD.value.updatedAt, status: 'SUCCESS', durationMs: diagD.value.durationMs })
  } catch (err) {
    markError(diagD.value, t0, err)
    pushDiagHistory(diagHistD.value, { at: diagD.value.updatedAt, status: 'ERROR', durationMs: diagD.value.durationMs, error: diagD.value.error })
    message.error('钢印注入失败。')
  } finally {
    dLoading.value = false
  }
}
function submitCreation() {
  const txt = creationInput.value.trim()
  if (!txt) return
  creationPool.value.unshift(txt)
  creationPool.value = creationPool.value.slice(0, 40)
  saveVersionedState(LOCAL_CREATION_POOL, creationPool.value)
  creationInput.value = ''
}
const themeTokens = computed(() => sealTheme.value.split('').filter((x) => x.trim()).slice(0, 6))
const heat = computed<Array<{ token: string; count: number }>>(() => {
  const countMap = new Map<string, number>()
  for (const token of themeTokens.value) countMap.set(token, 0)
  for (const text of creationPool.value) {
    for (const token of themeTokens.value) {
      if (text.includes(token)) countMap.set(token, (countMap.get(token) ?? 0) + 1)
    }
  }
  return Array.from(countMap.entries()).map(([token, count]) => ({ token, count }))
})
const infectionIndexRaw = computed(() => {
  if (!creationPool.value.length || !themeTokens.value.length) return 0
  const total = creationPool.value.length * themeTokens.value.length
  const hit = heat.value.reduce((s, h) => s + h.count, 0)
  return Math.round((hit / total) * 100)
})
const infectionIndex = computed(() => {
  const weighted = infectionIndexRaw.value * (0.55 + sealIntensity.value / 100)
  return Math.min(100, Math.round(weighted))
})
const infectionCells = computed(() => {
  const base = infectionIndex.value
  return Array.from({ length: 64 }, (_, i) => {
    const offset = ((i * 17 + themeTokens.value.length * 11) % 23) - 11
    const level = Math.max(0, Math.min(100, base + offset))
    return { id: i, level }
  })
})
const infectionCurvePath = computed(() => {
  if (infectionHistory.value.length < 2) return ''
  const w = 320
  const h = 90
  const step = w / (infectionHistory.value.length - 1)
  let d = `M 0 ${h - (infectionHistory.value[0] / 100) * h}`
  for (let i = 1; i < infectionHistory.value.length; i++) {
    d += ` L ${i * step} ${h - (infectionHistory.value[i] / 100) * h}`
  }
  return d
})
const strengthCurvePath = computed(() => {
  if (strengthHistory.value.length < 2) return ''
  const w = 320
  const h = 90
  const step = w / (strengthHistory.value.length - 1)
  let d = `M 0 ${h - (strengthHistory.value[0] / 100) * h}`
  for (let i = 1; i < strengthHistory.value.length; i++) {
    d += ` L ${i * step} ${h - (strengthHistory.value[i] / 100) * h}`
  }
  return d
})
watch(infectionIndex, (v) => {
  infectionHistory.value.push(v)
  if (infectionHistory.value.length > 40) infectionHistory.value.shift()
})
watch(sealIntensity, (v) => {
  strengthHistory.value.push(v)
  if (strengthHistory.value.length > 40) strengthHistory.value.shift()
}, { immediate: true })

onMounted(() => {
  universe.fetchMetrics()
  loadSession()
  realGoal.value = localStorage.getItem(LOCAL_REAL_GOAL) ?? ''
  showDecree.value = localStorage.getItem(LOCAL_DECREE_ACCEPTED) !== '1'
  try {
    const data = loadVersionedState<{
      suspicionScore: number
      directiveLogs: WallbreakerDirectiveLog[]
      breachTriggered: boolean
      breachConclusion: string
      directiveSeq: number
    }>(LOCAL_WALLBREAKER_STATE, { suspicionScore: 0, directiveLogs: [], breachTriggered: false, breachConclusion: '未完成反演。', directiveSeq: 0 })
    suspicionScore.value = data.suspicionScore ?? 0
    directiveLogs.value = data.directiveLogs ?? []
    breachTriggered.value = data.breachTriggered ?? false
    breachConclusion.value = data.breachConclusion ?? '未完成反演。'
    directiveSeq = data.directiveSeq ?? 0
  } catch {}
  creationPool.value = loadVersionedState<string[]>(LOCAL_CREATION_POOL, [])
  runPoisoning().catch(() => { pollutedText.value = sourceText.value })
})
</script>

<template>
  <div class="sector-wallfacer">
    <div v-if="breachTriggered && !breachOverlayAck" class="breach-overlay">
      <div class="breach-overlay-inner">
        <h2>WALLBREAKER OVERRIDE</h2>
        <p class="overlay-quote">主不在乎。但我是你的破壁人。</p>
        <p class="overlay-conclusion">你的真实计划是：{{ breachConclusion }}</p>
        <div class="breach-overlay-actions">
          <NButton type="error" @click="breachOverlayAck = true">接受破壁结论</NButton>
          <NButton ghost @click="resetWallfacerGame(); breachOverlayAck = true">再玩一局</NButton>
        </div>
      </div>
    </div>
    <div class="bg-noise"></div>
    <header class="header">
      <h1 class="title">SECTOR F // WALLFACER PROJECT</h1>
      <div class="status-bar">
        <span class="status-item">UN: ACTIVE</span>
        <span class="status-item">PDC: MONITORING</span>
        <span class="status-item">ETO: LURKING</span>
      </div>
    </header>

    <main class="main-content">
      <!-- Confrontation Modal -->
      <NModal v-model:show="showConfrontation" class="wb-modal" preset="card" :title="'破壁人：' + activeWallbreaker.name">
        <div class="confrontation-scene">
          <div class="wb-avatar">
            <div class="hooded-figure"></div>
          </div>
          <div class="wb-dialog">
            <p class="wb-line" v-if="confrontationStep === 0">{{ activeWallbreaker.desc }}</p>
            <p class="wb-line reveal" v-if="confrontationStep === 1">{{ activeWallbreaker.reveal }}</p>
          </div>
          <div class="wb-actions">
            <NButton v-if="confrontationStep === 0" type="error" @click="nextConfrontationStep">面对真相 (FACE TRUTH)</NButton>
            <NButton v-else @click="showConfrontation = false">结束会面</NButton>
          </div>
        </div>
      </NModal>

      <NTabs type="card" animated :value="activeTab" @update:value="onTabChange" class="wallfacer-tabs">
        
        <!-- 1. Frederick Tyler -->
        <NTabPane name="tyler" tab="泰勒 (TYLER)">
          <div 
            class="wallfacer-card tyler-theme holo-card" 
            ref="cardRef"
            @mousemove="handleCardMove"
            @mouseleave="resetCardTilt"
            :style="{ transform: `perspective(1000px) rotateX(${cardTilt.x}deg) rotateY(${cardTilt.y}deg)` }"
          >
            <div class="card-header">
              <div class="header-main">
                <div>
                  <h2>FREDERICK TYLER</h2>
                  <p class="subtitle">MOSQUITO SWARM // 蚊群计划</p>
                </div>
                <div class="wallbreaker-tag" @click.stop="startConfrontation('tyler')">
                  <span class="wb-label">WALLBREAKER</span>
                  <span class="wb-name">VON NEUMANN</span>
                </div>
              </div>
            </div>
            <div class="card-body">
              <div class="radar-view">
                <div class="radar-screen" :class="{ 'swarm-active': tylerState.deployed }">
                  <div class="target-fleet" :class="{ 'ghost': tylerState.targetStatus === 'QUANTUM_GHOST' }"></div>
                  <div v-if="tylerState.deployed" class="swarm-particles"></div>
                </div>
                <div class="radar-info">
                  <p>SWARM COUNT: {{ tylerState.swarmCount }}</p>
                  <p>TARGET STATUS: {{ tylerState.targetStatus }}</p>
                </div>
              </div>
              <div class="controls">
                <NButton ghost type="primary" @click="deploySwarm" :disabled="tylerState.deployed">
                  DEPLOY MACRO-ATOMS (部署宏原子)
                </NButton>
                <NButton color="#ff0000" ghost @click="executeTylerPlan" :disabled="!tylerState.deployed || tylerState.targetStatus !== 'ACTIVE'">
                  ATTACK (攻击)
                </NButton>
              </div>
              <p class="lore-text">
                "妈妈，我将变成一只萤火虫。" —— 泰勒的遗言? <br/>
                真相：利用球状闪电武器将地球舰队量子化，以此对抗三体？还是...
              </p>
            </div>
          </div>
        </NTabPane>
        
        <!-- 2. Manuel Rey Diaz -->
        <NTabPane name="diaz" tab="雷迪亚兹 (DIAZ)">
          <div 
            class="wallfacer-card diaz-theme holo-card"
            @mousemove="handleCardMove"
            @mouseleave="resetCardTilt"
            :style="{ transform: `perspective(1000px) rotateX(${cardTilt.x}deg) rotateY(${cardTilt.y}deg)` }"
          >
            <div class="card-header">
              <div class="header-main">
                <div>
                  <h2>MANUEL REY DIAZ</h2>
                  <p class="subtitle">STELLAR HYDROGEN BOMB // 摇篮计划</p>
                </div>
                <div class="wallbreaker-tag" @click.stop="startConfrontation('diaz')">
                  <span class="wb-label">WALLBREAKER</span>
                  <span class="wb-name">MOZI</span>
                </div>
              </div>
            </div>
            <div class="card-body">
              <div class="solar-view" :class="{ 'doomsday': diazState.mercuryStatus === 'FALLING' }">
                <div class="sun"></div>
                <div class="mercury" :class="diazState.mercuryStatus"></div>
              </div>
              <div class="bomb-controls">
                <div class="control-row">
                  <span>BOMB COUNT</span>
                  <NProgress type="line" :percentage="diazState.bombCount / 10" :show-indicator="false" processing />
                  <span>{{ diazState.bombCount }}/1000</span>
                </div>
                <div class="control-row">
                  <span>YIELD (Mt)</span>
                  <NSlider v-model:value="diazState.yield" :step="10" :min="50" :max="500" />
                </div>
                <div class="buttons">
                  <NButton ghost type="warning" @click="placeBombs" :disabled="diazState.bombCount >= 1000">
                    BURY BOMBS (埋设)
                  </NButton>
                  <NButton color="#ff0000" class="detonate-btn" @click="detonateDiaz" :disabled="diazState.detonated">
                    DETONATE (引爆信号)
                  </NButton>
                </div>
              </div>
              <p class="lore-text">
                "我对人类的爱，在这一刻压倒了一切。" <br/>
                以水星坠落太阳为筹码，要挟三体文明。
              </p>
            </div>
          </div>
        </NTabPane>

        <!-- 3. Bill Hines -->
        <NTabPane name="hines" tab="希恩斯 (HINES)">
          <div 
            class="wallfacer-card hines-theme holo-card"
            @mousemove="handleCardMove"
            @mouseleave="resetCardTilt"
            :style="{ transform: `perspective(1000px) rotateX(${cardTilt.x}deg) rotateY(${cardTilt.y}deg)` }"
          >
            <div class="card-header">
              <div class="header-main">
                <div>
                  <h2>BILL HINES</h2>
                  <p class="subtitle">MENTAL SEAL // 思想钢印</p>
                </div>
                <div class="wallbreaker-tag" @click.stop="startConfrontation('hines')">
                  <span class="wb-label">WALLBREAKER</span>
                  <span class="wb-name">ARISTOTLE</span>
                </div>
              </div>
            </div>
            <div class="card-body hines-body">
              
              <!-- Seal State: Active -->
              <div v-if="universe.mentalSeal" class="sealed-view">
                <div class="seal-stamp-container">
                  <div class="seal-stamp">{{ universe.mentalSeal.seal_type }}</div>
                  <div class="seal-watermark">APPROVED</div>
                </div>
                <h3>思想钢印已固化</h3>
                <p class="seal-desc">神经元网络重构完成。逻辑闭环已建立。</p>
                <NButton class="mt-4" type="error" dashed @click="resetSeal">使用破壁锤 (RESET)</NButton>
              </div>

              <!-- Seal State: Selection & Animation -->
              <div v-else class="imprint-view">
                <div class="neural-network">
                  <canvas ref="neuralCanvas" width="400" height="250"></canvas>
                  <div v-if="imprinting" class="imprint-overlay">
                    <div class="scanning-line"></div>
                    <div class="imprint-status">REWRITING SYNAPSES... {{ Math.floor(imprintProgress) }}%</div>
                  </div>
                </div>

                <div class="seals-selection" v-if="!imprinting">
                  <div 
                    v-for="s in seals" 
                    :key="s.type" 
                    class="seal-option"
                    :style="{ '--seal-color': s.color }"
                    @click="startImprint(s)"
                  >
                    <div class="option-label">{{ s.label }}</div>
                    <div class="option-sub">{{ s.desc }}</div>
                  </div>
                </div>
              </div>

              <p class="lore-text">
                "在这场战争中，人类必胜！" —— 真的吗？<br/>
                通过修改大脑神经元网络，创造出绝对的信念。
              </p>
            </div>
          </div>
        </NTabPane>

        <!-- 4. Luo Ji -->
        <NTabPane name="luoji" tab="罗辑 (LUO JI)">
          <div 
            class="wallfacer-card luoji-theme holo-card"
            @mousemove="handleCardMove"
            @mouseleave="resetCardTilt"
            :style="{ transform: `perspective(1000px) rotateX(${cardTilt.x}deg) rotateY(${cardTilt.y}deg)` }"
          >
            <div class="card-header">
              <div class="header-main">
                <div>
                  <h2>LUO JI</h2>
                  <p class="subtitle">DARK FOREST // 执剑人</p>
                </div>
                <div class="wallbreaker-tag danger" @click.stop="startConfrontation('luoji')">
                  <span class="wb-label">THREAT</span>
                  <span class="wb-name">TRISOLARIS</span>
                </div>
              </div>
            </div>
            <div class="card-body">
              <div class="logic-panel">
                 <!-- Spell Caster -->
                 <div class="spell-section">
                    <h3>SPELL CASTER (咒语发射)</h3>
                    <div class="spell-input-group">
                      <NInput v-model:value="luojiState.spell" placeholder="输入恒星坐标 (e.g. 187J3X1)" :disabled="luojiState.broadcasted"/>
                      <NButton type="primary" @click="castSpell" :disabled="!luojiState.spell || luojiState.broadcasted">
                        BROADCAST (广播)
                      </NButton>
                    </div>
                 </div>

                 <!-- Deterrence System (Chat) -->
                 <div class="deterrence-section">
                   <h3>WALLFACER vs BREAKER</h3>
                   <div v-if="!session || session.status === 'abandoned'" class="setup-panel">
                      <NInput v-model:value="planTitle" placeholder="Plan Codename" class="mb-2" />
                      <NInput v-model:value="planContent" type="textarea" placeholder="Deceive the Trisolarans..." :rows="3" class="mb-2" />
                      <NButton type="primary" block :loading="loading" @click="startPlan" :disabled="!planTitle || !planContent">
                        INITIATE PLAN
                      </NButton>
                    </div>
                    <div v-else class="chat-interface">
                      <div class="chat-history">
                        <div v-for="(msg, i) in history" :key="i" class="msg-row" :class="msg.role">
                          <span class="msg-name">{{ msg.name }}:</span>
                          <span class="msg-content">{{ msg.content }}</span>
                        </div>
                        <div ref="chatBottom"></div>
                      </div>
                      <div v-if="session.status === 'active'" class="chat-input">
                        <NInput v-model:value="input" placeholder="Type..." @keyup.enter="sendReply" size="small" />
                        <NButton size="small" @click="sendReply">SEND</NButton>
                      </div>
                      <div v-else class="chat-reset">
                        <NButton size="small" dashed @click="session = null">NEW CYCLE</NButton>
                      </div>
                    </div>

                    <div class="wallbreaker-panel">
                      <div class="wb-head">
                        <span>WALLBREAKER INFERENCE REPORT</span>
                        <NButton size="small" type="error" ghost @click="generateWallbreakerReport">
                          生成破壁报告
                        </NButton>
                      </div>
                      <div class="wb-targets">
                        <button
                          v-for="t in ['tyler','diaz','hines','luoji']"
                          :key="t"
                          class="wb-target-btn"
                          :class="{ active: wallbreakerTarget === t }"
                          @click="setWallbreakerTarget(t)"
                        >
                          {{ t.toUpperCase() }}
                        </button>
                      </div>
                      <div v-if="wallbreakerReports.length === 0" class="wb-empty">
                        暂无报告。点击“生成破壁报告”开始反演。
                      </div>
                      <div v-else class="wb-list">
                        <div v-for="r in wallbreakerReports" :key="r.id" class="wb-item">
                          <div class="wb-row">
                            <span class="wb-time">[{{ r.time }}]</span>
                            <span class="wb-tag">{{ r.target.toUpperCase() }}</span>
                            <span class="wb-threat" :class="r.threat.toLowerCase()">{{ r.threat }}</span>
                          </div>
                          <p class="wb-facade">表层计划：{{ r.facade }}</p>
                          <p class="wb-truth">反演结论：{{ r.inferredTruth }}</p>
                          <p class="wb-confidence">置信度：{{ r.confidence }}%</p>
                        </div>
                      </div>
                    </div>
                 </div>
              </div>
              <p class="lore-text">
                "我有一个梦，也许有一天，灿烂的阳光能照进黑暗森林。"
              </p>
            </div>
          </div>
        </NTabPane>

        <!-- A. 面壁者审讯室（合并自三体体验沙盒） -->
        <NTabPane name="interrogation" tab="面壁者审讯室">
          <div class="panel wallfacer-panel zv2-panel">
            <div v-if="showDecree" class="decree-card">
              <div class="decree-header"><span class="decree-icon">⚔</span><h3>联合国面壁者任命书</h3></div>
              <p>你已被授予资源调配权限。你的真实战略仅允许在本机保存，不得上传，不得外泄。</p>
              <NButton size="small" type="primary" @click="acceptDecree">接受任命</NButton>
            </div>
            <div v-if="!showDecree" class="wallfacer-intro">
              <span class="intro-title">玩法说明</span>
              <p>用公开的<strong>资源调配指令</strong>掩饰你的真实战略；破壁人会分析每条指令并累积<strong>疑心值</strong>。疑心值达 90 将被破壁。</p>
              <div class="intro-stats">
                <span class="stat-item">本局已提交 <strong>{{ wallfacerStats.total }}</strong> 条</span>
                <span class="stat-item stat-ok">通过 <strong>{{ wallfacerStats.approved }}</strong></span>
                <span class="stat-item stat-no">驳回 <strong>{{ wallfacerStats.rejected }}</strong></span>
              </div>
              <NButton size="tiny" quaternary @click="resetWallfacerGame" class="reset-link">重置本局</NButton>
            </div>
            <div class="real-goal-section">
              <span class="section-label">绝密 · 真实战略目标</span>
              <div class="row real-goal-row">
                <NInput v-model:value="realGoal" type="textarea" :rows="2" placeholder="输入真实战略目标（仅本机保存）" />
                <NButton type="primary" ghost @click="saveRealGoal">写入本地</NButton>
              </div>
            </div>
            <div class="directive-submit-section">
              <span class="section-label">资源调配指令（公开）</span>
              <div class="preset-grid">
                <button v-for="(opt, idx) in WALLFACER_PRESETS" :key="idx" type="button" class="preset-chip" :class="[opt.risk]" :disabled="breachTriggered || aLoading" @click="usePresetDirective(opt)">{{ opt.text }}</button>
              </div>
              <div class="custom-directive-row">
                <div class="row directive-row">
                  <NInput v-model:value="directiveInput" placeholder="输入一条资源调配指令，回车或点击提交…" @keyup.enter="submitDirective" />
                  <NButton type="primary" ghost @click="submitDirective" :disabled="breachTriggered || !directiveInput.trim()" :loading="aLoading">提交指令</NButton>
                </div>
              </div>
            </div>
            <div class="suspicion-gauge" :class="{ 'gauge-danger': suspicionStage.key === 'danger' || suspicionStage.key === 'breach' }">
              <div class="gauge-header">
                <span class="gauge-label">破壁人疑心值</span>
                <span class="gauge-stage" :style="{ color: suspicionStage.color }">{{ suspicionStage.label }}</span>
                <span class="gauge-desc reason">{{ suspicionStage.desc }}</span>
              </div>
              <NProgress type="line" :percentage="suspicionScore" :height="12" :show-indicator="true" :color="suspicionStage.color" class="gauge-progress" />
              <div class="gauge-value">{{ suspicionScore }} / 90</div>
            </div>
            <ModuleDiagPanel module-key="A" :status="diagA.status" :duration-ms="diagA.durationMs" :updated-at="diagA.updatedAt" :error="diagA.error" :history="diagHistA" />
            <div class="directive-logs">
              <div class="section-label">指令审计记录</div>
              <div v-if="directiveLogs.length === 0" class="logs-empty reason">暂无记录。提交指令后，破壁人将在此分析。</div>
              <div v-for="log in directiveLogs" :key="log.id" class="directive-card" :class="{ rejected: log.verdict === 'REJECTED' }">
                <div class="directive-card-meta">
                  <span class="log-time">[{{ log.createdAt }}]</span>
                  <NTag size="small" :type="log.verdict === 'APPROVED' ? 'success' : 'error'">{{ log.verdict === 'APPROVED' ? '通过' : '驳回' }}</NTag>
                  <NTag size="small" type="warning" round>{{ inferredLabel(log.inferred) }}</NTag>
                  <span class="log-delta">+{{ log.suspicionDelta }} → {{ log.suspicionTotal }}</span>
                </div>
                <p class="directive-text">{{ log.directive }}</p>
                <p class="reason directive-reason">{{ log.reason }}</p>
              </div>
            </div>
            <div v-if="breachTriggered" class="breach breach-card">
              <div class="breach-card-inner">
                <p class="breach-quote">主不在乎。但我是你的破壁人。</p>
                <p class="breach-conclusion">你的真实计划是：{{ breachConclusion }}</p>
                <NButton size="small" type="primary" ghost @click="resetWallfacerGame">再玩一局</NButton>
              </div>
            </div>
          </div>
        </NTabPane>

        <!-- D. 思想钢印网络（合并自三体体验沙盒） -->
        <NTabPane name="seal-network" tab="思想钢印网络">
          <div class="panel zv2-panel">
            <div class="row">
              <NInput v-model:value="sealTheme" placeholder="钢印命题" />
              <NButton type="primary" @click="runPoisoning" :loading="dLoading">注入钢印</NButton>
            </div>
            <div class="row">
              <span class="reason">管理员污染强度：{{ sealIntensity }}</span>
              <NSlider v-model:value="sealIntensity" :step="5" :min="0" :max="100" />
            </div>
            <div class="row">
              <NInput v-model:value="sourceText" type="textarea" :rows="3" placeholder="原始文本" />
              <NInput :value="pollutedText" type="textarea" :rows="3" readonly />
            </div>
            <div class="row">
              <NInput v-model:value="creationInput" placeholder="提交用户后续共创文本" @keyup.enter="submitCreation" />
              <NButton ghost @click="submitCreation">记录样本</NButton>
            </div>
            <NProgress type="line" :percentage="infectionIndex" :color="infectionIndex > 45 ? '#ff3333' : '#00ff41'" />
            <ModuleDiagPanel module-key="D" :status="diagD.status" :duration-ms="diagD.durationMs" :updated-at="diagD.updatedAt" :error="diagD.error" :history="diagHistD" />
            <div class="infection-grid">
              <div v-for="cell in infectionCells" :key="cell.id" class="infection-cell" :style="{ '--cell-opacity': `${Math.max(0.1, cell.level / 100)}` }"></div>
            </div>
            <div class="curve-panel">
              <div class="reason">模因感染曲线（近期 40 次采样）</div>
              <svg viewBox="0 0 320 90" class="curve-svg">
                <path d="M0 89 L320 89" class="curve-axis"></path>
                <path :d="infectionCurvePath" class="curve-line"></path>
              </svg>
              <div class="reason">污染强度回放（近期 40 次采样）</div>
              <svg viewBox="0 0 320 90" class="curve-svg">
                <path d="M0 89 L320 89" class="curve-axis"></path>
                <path :d="strengthCurvePath" class="curve-line-intensity"></path>
              </svg>
            </div>
            <div class="heat">
              <div v-for="h in heat" :key="h.token" class="heat-item">
                <span>{{ h.token }}</span>
                <div class="bar"><i :style="{ width: `${Math.min(100, h.count * 12)}%` }" /></div>
                <span>{{ h.count }}</span>
              </div>
            </div>
          </div>
        </NTabPane>

      </NTabs>
    </main>
  </div>
</template>

<style scoped>
.sector-wallfacer {
  min-height: 0;
  background: #050505;
  color: #ccc;
  padding: 2rem;
  font-family: 'Inter', sans-serif;
}
.bg-noise {
  position: fixed;
  inset: 0;
  opacity: 0.03;
  background: url('data:image/svg+xml;utf8,<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><filter id="n"><feTurbulence type="fractalNoise" baseFrequency="0.65"/></filter><rect width="100%" height="100%" filter="url(%23n)"/></svg>');
  pointer-events: none;
  z-index: 0;
}
.header {
  border-bottom: 1px solid #333;
  padding-bottom: 1rem;
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  position: relative;
  z-index: 1;
}
.title {
  font-family: monospace;
  font-size: 1.5rem;
  color: #fff;
  letter-spacing: 2px;
}
.status-bar {
  display: flex;
  gap: 1rem;
  font-family: monospace;
  font-size: 0.8rem;
  color: #666;
}
.status-item {
  border: 1px solid #333;
  padding: 2px 6px;
}


.main-content {
  max-width: 1000px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.wallbreaker-tag {
  background: rgba(0, 0, 0, 0.6);
  border: 1px solid #666;
  padding: 0.5rem 1rem;
  cursor: pointer;
  text-align: right;
  transition: all 0.3s;
}
.wallbreaker-tag:hover {
  background: #222;
  border-color: #fff;
  transform: translateX(-5px);
}
.wallbreaker-tag.danger { border-color: #f44336; }
.wallbreaker-tag.danger:hover { background: rgba(244, 67, 54, 0.1); }

.wb-label { display: block; font-size: 0.7rem; color: #888; letter-spacing: 1px; }
.wb-name { display: block; font-family: monospace; font-size: 1.1rem; color: #ccc; font-weight: bold; }

.confrontation-scene {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  padding: 1rem;
  min-height: 300px;
}

.wb-avatar {
  width: 100px; height: 100px;
  background: #000;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 20px rgba(0,0,0,0.5);
}
.hooded-figure {
  width: 60px; height: 60px;
  background: linear-gradient(135deg, #333, #000);
  clip-path: polygon(50% 0, 100% 100%, 0 100%);
}

.wb-dialog {
  flex: 1;
  text-align: center;
  font-family: 'Noto Serif SC', serif;
  font-size: 1.2rem;
  line-height: 1.6;
}
.wb-line { color: #ccc; margin-bottom: 1rem; }
.wb-line.reveal { color: #ffeb3b; font-weight: bold; text-shadow: 0 0 10px rgba(255, 235, 59, 0.3); }

.wb-actions { margin-top: auto; }

/* Tab Cards */
.wallfacer-card {
  background: rgba(20, 20, 20, 0.8);
  border: 1px solid #333;
  padding: 2rem;
  min-height: 500px;
  display: flex;
  flex-direction: column;
  transform-style: preserve-3d;
  transition: transform 0.1s cubic-bezier(0.2, 0, 0.2, 1), box-shadow 0.3s;
}

.holo-card {
  perspective: 1000px;
}

.holo-card:hover {
  box-shadow: 0 0 30px rgba(0, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.card-header {
  border-bottom: 1px solid #333;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  transform: translateZ(20px);
}
.card-header h2 {
  font-size: 1.8rem;
  margin: 0;
  letter-spacing: 1px;
}
.subtitle {
  font-family: monospace;
  color: #666;
  font-size: 0.9rem;
}
.card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  transform: translateZ(10px);
}
.controls, .bomb-controls, .neural-network, .logic-panel {
  transform: translateZ(15px);
}
.lore-text {
  margin-top: auto;
  font-style: italic;
  color: #555;
  border-left: 2px solid #333;
  padding-left: 1rem;
  font-size: 0.9rem;
  transform: translateZ(5px);
}

/* Tyler Theme */
.tyler-theme h2 { color: #8bc34a; }
.radar-view {
  background: #000;
  border: 1px solid #33691e;
  height: 250px;
  position: relative;
  overflow: hidden;
  display: flex;
}
.radar-screen {
  flex: 1;
  position: relative;
  background: radial-gradient(circle, transparent 20%, #0a1a0a 20%, #0a1a0a 21%, transparent 21%, transparent 40%, #0a1a0a 40%, #0a1a0a 41%, transparent 41%, transparent 60%, #0a1a0a 60%, #0a1a0a 61%, transparent 61%);
  background-size: 100px 100px;
  background-position: center;
}
.target-fleet {
  position: absolute;
  top: 50%; left: 50%;
  width: 10px; height: 10px;
  background: #f44336;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 10px #f44336;
}
.target-fleet.ghost {
  opacity: 0.3;
  animation: pulse 0.5s infinite;
}
.swarm-particles {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(#8bc34a 1px, transparent 1px);
  background-size: 10px 10px;
  opacity: 0.5;
  animation: drift 5s linear infinite;
}
.radar-info {
  width: 150px;
  padding: 1rem;
  font-family: monospace;
  color: #8bc34a;
  border-left: 1px solid #33691e;
  font-size: 0.8rem;
}
.controls { display: flex; gap: 1rem; justify-content: center; }

/* Diaz Theme */
.diaz-theme h2 { color: #ff9800; }
.solar-view {
  background: #000;
  height: 200px;
  position: relative;
  overflow: hidden;
  border: 1px solid #e65100;
}
.sun {
  position: absolute;
  left: -50px; top: 50%;
  width: 150px; height: 150px;
  background: radial-gradient(circle, #ffeb3b, #f44336);
  border-radius: 50%;
  transform: translateY(-50%);
  box-shadow: 0 0 50px #ff9800;
  transition: all 2s;
}
.mercury {
  position: absolute;
  left: 150px; top: 50%;
  width: 20px; height: 20px;
  background: #9e9e9e;
  border-radius: 50%;
  transform: translateY(-50%);
  transition: all 2s;
}
.doomsday .sun { width: 300px; height: 300px; box-shadow: 0 0 100px #f44336; }
.doomsday .mercury { left: 50px; opacity: 0; }
.bomb-controls {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 152, 0, 0.1);
}
.control-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-family: monospace;
}
.buttons { display: flex; gap: 1rem; justify-content: center; margin-top: 1rem; }
.detonate-btn { font-weight: bold; letter-spacing: 1px; }

/* Hines Theme */
.hines-theme h2 { color: #00bcd4; }
.hines-body { display: flex; flex-direction: column; height: 100%; }

.neural-network {
  background: #000;
  border: 1px solid #00bcd4;
  height: 250px;
  position: relative;
  margin-bottom: 1.5rem;
  overflow: hidden;
}

.neural-network canvas { width: 100%; height: 100%; }

.imprint-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.2);
  pointer-events: none;
}
.imprint-status {
  font-family: monospace;
  color: #fff;
  background: #000;
  padding: 0.5rem;
  border: 1px solid #fff;
}
.scanning-line {
  position: absolute;
  top: 0; left: 0; right: 0; height: 2px;
  background: #00bcd4;
  box-shadow: 0 0 10px #00bcd4;
  animation: scan 2s linear infinite;
}
@keyframes scan { 0% { top: 0; } 100% { top: 100%; } }

.seals-selection {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.seal-option {
  border: 1px solid #333;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid var(--seal-color);
  background: rgba(255,255,255,0.02);
}

.seal-option:hover {
  background: rgba(255,255,255,0.05);
  transform: translateX(5px);
}

.option-label {
  color: var(--seal-color);
  font-weight: bold;
  margin-bottom: 0.3rem;
}
.option-sub { font-size: 0.8rem; color: #666; }

.sealed-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.seal-stamp-container {
  border: 5px double #00bcd4;
  padding: 2rem;
  transform: rotate(-5deg);
  position: relative;
  margin-bottom: 2rem;
}

.seal-stamp {
  font-size: 2rem;
  font-weight: bold;
  color: #00bcd4;
  letter-spacing: 5px;
  text-transform: uppercase;
}

.seal-watermark {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%) rotate(-15deg);
  font-size: 4rem;
  opacity: 0.1;
  color: #00bcd4;
  font-weight: bold;
  border: 2px solid #00bcd4;
  padding: 0.5rem;
}

/* Luo Ji Theme */
.luoji-theme h2 { color: #9c27b0; }
.logic-panel {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  height: 100%;
}
.spell-section, .deterrence-section {
  background: rgba(0,0,0,0.3);
  padding: 1rem;
  border: 1px solid #4a148c;
}
.spell-section h3, .deterrence-section h3 {
  color: #e1bee7;
  font-size: 0.9rem;
  margin-bottom: 1rem;
  font-family: monospace;
  border-bottom: 1px solid #4a148c;
  padding-bottom: 0.5rem;
}
.spell-input-group { display: flex; gap: 0.5rem; flex-direction: column; }
.chat-interface { display: flex; flex-direction: column; height: 300px; }
.chat-history { flex: 1; overflow-y: auto; font-size: 0.85rem; padding: 0.5rem; border: 1px solid #333; margin-bottom: 0.5rem; background: #000; }
.msg-row { margin-bottom: 0.5rem; }
.msg-name { font-weight: bold; margin-right: 0.5rem; color: #999; }
.msg-row.user .msg-name { color: #ce93d8; }
.msg-row.user { text-align: right; }
.chat-input { display: flex; gap: 0.5rem; }

.wallbreaker-panel {
  margin-top: 0.8rem;
  border: 1px solid #5a2b68;
  background: rgba(0, 0, 0, 0.35);
  padding: 0.75rem;
}

.wb-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  color: #f2d0ff;
  font-family: monospace;
  font-size: 0.8rem;
}

.wb-targets {
  display: flex;
  gap: 0.4rem;
  margin-bottom: 0.6rem;
}

.wb-target-btn {
  border: 1px solid #4a148c;
  color: #ce93d8;
  background: transparent;
  padding: 0.2rem 0.5rem;
  font-size: 0.72rem;
  cursor: pointer;
}

.wb-target-btn.active {
  background: #4a148c;
  color: #fff;
}

.wb-empty {
  font-size: 0.78rem;
  color: #888;
  font-family: monospace;
}

.wb-list {
  max-height: 180px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.wb-item {
  border: 1px dashed #5b3a66;
  padding: 0.45rem;
  background: rgba(25, 10, 35, 0.45);
}

.wb-row {
  display: flex;
  gap: 0.4rem;
  align-items: center;
  font-family: monospace;
  font-size: 0.72rem;
  margin-bottom: 0.2rem;
}

.wb-time { color: #8f7e9f; }
.wb-tag {
  color: #e1bee7;
  border: 1px solid #7b4f8a;
  padding: 0 0.25rem;
}
.wb-threat {
  margin-left: auto;
  padding: 0 0.25rem;
  border: 1px solid #666;
}
.wb-threat.low { color: #9ccc65; border-color: #558b2f; }
.wb-threat.medium { color: #ffb74d; border-color: #f57c00; }
.wb-threat.high { color: #ef5350; border-color: #c62828; }

.wb-facade, .wb-truth, .wb-confidence {
  margin: 0.12rem 0;
  font-size: 0.75rem;
  line-height: 1.35;
}
.wb-facade { color: #c5b6d0; }
.wb-truth { color: #ffd7ff; }
.wb-confidence { color: #b39ddb; font-family: monospace; }

@keyframes drift { from { background-position: 0 0; } to { background-position: 20px 20px; } }
@keyframes pulse { 0% { opacity: 0.3; } 50% { opacity: 0.7; } 100% { opacity: 0.3; } }

/* A/D 合并面板（原三体体验沙盒） */
.breach-overlay {
  position: fixed;
  inset: 0;
  z-index: 1200;
  background: radial-gradient(circle, rgba(210, 0, 0, 0.2), rgba(80, 0, 0, 0.92));
  display: flex;
  align-items: center;
  justify-content: center;
  animation: breach-pulse 0.8s linear infinite;
}
.breach-overlay-inner {
  width: min(760px, 90vw);
  border: 1px solid #ff4f4f;
  background: rgba(20, 0, 0, 0.9);
  color: #ffe0e0;
  padding: 1.2rem;
  font-family: monospace;
}
.breach-overlay-inner h2 { margin: 0 0 0.5rem; }
.overlay-quote { margin: 0.5rem 0; font-style: italic; }
.overlay-conclusion { margin: 0.5rem 0; font-weight: 600; }
.breach-overlay-actions { display: flex; gap: 0.75rem; margin-top: 1rem; }
@keyframes breach-pulse { 0% { filter: saturate(100%); } 50% { filter: saturate(150%); } 100% { filter: saturate(100%); } }

.zv2-panel {
  border: 1px solid #252525;
  background: rgba(0, 0, 0, 0.4);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}
.zv2-panel .row { display: grid; gap: 0.6rem; }
.section-label {
  display: block;
  font-size: 0.7rem;
  color: #6a8585;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 0.4rem;
}
.reason { font-size: 0.8rem; color: #7a9a9a; }
.decree-card {
  border: 1px solid #294040;
  padding: 0.8rem 1rem;
  background: linear-gradient(135deg, rgba(0, 30, 30, 0.35), rgba(0, 20, 35, 0.25));
  border-radius: 6px;
}
.decree-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem; }
.decree-icon { font-size: 1.2rem; opacity: 0.9; }
.decree-card h3 { margin: 0; font-size: 1rem; color: #c8e0e0; }
.decree-card p { margin: 0 0 0.6rem; font-size: 0.9rem; color: #9ab5b5; }
.wallfacer-intro {
  padding: 0.5rem 0.6rem;
  border: 1px solid #25363a;
  background: rgba(0, 25, 30, 0.2);
  border-radius: 4px;
}
.wallfacer-intro .intro-title { font-size: 0.75rem; color: #7a9a9a; text-transform: uppercase; letter-spacing: 0.08em; margin-right: 0.5rem; }
.wallfacer-intro p { margin: 0.3rem 0 0.5rem; font-size: 0.85rem; color: #a8c0c0; line-height: 1.5; }
.intro-stats { display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem 1rem; margin: 0.5rem 0; padding: 0.4rem 0.6rem; background: rgba(0, 20, 25, 0.35); border-radius: 4px; border: 1px solid #1e2f2f; }
.stat-item { font-size: 0.8rem; color: #9ab5b5; }
.stat-item strong { color: #c0e0e0; }
.stat-ok strong { color: #00cc88; }
.stat-no strong { color: #ff6666; }
.real-goal-row, .directive-row { display: flex; gap: 0.6rem; align-items: flex-start; }
.real-goal-row .n-input, .directive-row .n-input { flex: 1; }
.preset-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 0.5rem; }
.preset-chip {
  appearance: none;
  border: 1px solid #2a4040;
  background: rgba(0, 25, 30, 0.4);
  color: #b8d0d0;
  padding: 0.5rem 0.75rem;
  font-size: 0.85rem;
  line-height: 1.4;
  text-align: left;
  border-radius: 6px;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}
.preset-chip:hover:not(:disabled) { border-color: #3a6060; background: rgba(0, 40, 50, 0.5); color: #d0e8e8; }
.preset-chip:disabled { opacity: 0.5; cursor: not-allowed; }
.preset-chip.low { border-left: 3px solid #00aa77; }
.preset-chip.mid { border-left: 3px solid #cc9900; }
.preset-chip.high { border-left: 3px solid #cc4444; }
.suspicion-gauge {
  padding: 0.6rem 0.8rem;
  border: 1px solid #1e2f2f;
  background: rgba(0, 15, 20, 0.4);
  border-radius: 4px;
}
.suspicion-gauge.gauge-danger { border-color: rgba(255, 80, 80, 0.4); animation: gauge-pulse 1.5s ease-in-out infinite; }
@keyframes gauge-pulse { 0%, 100% { box-shadow: 0 0 0 0 rgba(255, 80, 80, 0); } 50% { box-shadow: 0 0 12px 2px rgba(255, 80, 80, 0.2); } }
.gauge-header { display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap; margin-bottom: 0.4rem; }
.gauge-label { font-family: monospace; font-size: 0.85rem; color: #8ab3b3; }
.gauge-stage { font-weight: 700; font-size: 0.9rem; }
.gauge-desc { font-size: 0.8rem; }
.gauge-value { font-family: monospace; font-size: 0.75rem; color: #7a9a9a; }
.directive-logs { border: 1px solid #1e2e2e; padding: 0.6rem; background: rgba(0, 10, 15, 0.3); border-radius: 4px; }
.logs-empty { padding: 0.8rem; text-align: center; font-size: 0.85rem; }
.directive-card {
  border: 1px solid #25363a;
  border-left: 3px solid #00aa88;
  padding: 0.5rem 0.7rem;
  margin-bottom: 0.5rem;
  background: rgba(0, 25, 30, 0.2);
  border-radius: 0 4px 4px 0;
}
.directive-card.rejected { border-left-color: #cc4444; }
.directive-card-meta { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.35rem; }
.log-time { font-family: monospace; font-size: 0.7rem; color: #6a8585; }
.log-delta { font-size: 0.75rem; color: #8ab0b0; margin-left: auto; }
.directive-text { margin: 0; font-size: 0.9rem; color: #c8e0e0; line-height: 1.45; }
.directive-reason { margin: 0.25rem 0 0; font-size: 0.8rem; }
.breach-card { border-radius: 6px; padding: 0.8rem 1rem; }
.breach-card-inner { display: flex; flex-direction: column; gap: 0.5rem; }
.breach-quote { margin: 0; font-style: italic; color: #ffc8c8; }
.breach-conclusion { margin: 0; font-weight: 600; color: #ffdddd; }
.infection-grid { display: grid; grid-template-columns: repeat(16, 1fr); gap: 2px; }
.infection-cell { height: 10px; background: rgba(255, 40, 40, var(--cell-opacity, 0.2)); border-radius: 1px; }
.curve-panel { border: 1px solid #1f1f1f; padding: 0.4rem; border-radius: 4px; }
.curve-svg { width: 100%; height: 90px; display: block; }
.curve-axis { stroke: #333; stroke-width: 1; fill: none; }
.curve-line { fill: none; stroke: #ff5252; stroke-width: 1.5; }
.curve-line-intensity { fill: none; stroke: #4fc3ff; stroke-width: 1.5; }
.heat { border: 1px solid #1f1f1f; padding: 0.6rem; display: grid; gap: 0.4rem; }
.heat-item { display: grid; grid-template-columns: 26px 1fr 28px; align-items: center; gap: 0.5rem; font-size: 0.8rem; }
.heat-item .bar { height: 8px; background: #1a1a1a; border-radius: 2px; overflow: hidden; }
.heat-item .bar i { display: block; height: 100%; background: #ff6666; }
</style>
