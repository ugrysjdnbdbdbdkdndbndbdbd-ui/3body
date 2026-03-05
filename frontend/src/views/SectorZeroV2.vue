<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { NButton, NInput, NProgress, NSlider, NTabPane, NTabs, NTag, useMessage } from 'naive-ui'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import {
  analyzeWallfacerDirective,
  decodeFairytaleSimilarity,
  encodeSecretAsFairytale,
  injectMentalSealText,
  tickDarkForestWorld,
} from '@/api/zero_v2'
import { getGatewayRuntimeStatus } from '@/api/llm_gateway'
import { loadVersionedState, saveVersionedState } from '@/composables/useZeroV2State'
import ModuleDiagPanel from '@/components/ModuleDiagPanel.vue'
import { seedCivilizations } from '@/sim/zeroDarkForest'
import type {
  CivilizationAgent,
  CosmicEpitaph,
  EncryptedFairytale,
  MemeHeat,
  WallbreakerDirectiveLog,
  WorldlineSnapshot,
} from '@/types/zero_v2'

const message = useMessage()
const route = useRoute()
const router = useRouter()
const activeTab = ref<'A' | 'B' | 'C' | 'D'>('A')

// 游戏化框架：本局目标 + 关键数值（见 docs/DEVELOPMENT-RULES.md 游戏化设计原则）
const gameFrame = computed(() => {
  switch (activeTab.value) {
    case 'A':
      return {
        goal: '在破壁前尽量多提交「通过」指令',
        metrics: [
          { label: '疑心值', value: `${suspicionScore.value}/90` },
          { label: '通过', value: String(wallfacerStats.value.approved) },
          { label: '驳回', value: String(wallfacerStats.value.rejected) },
        ],
      }
    case 'B':
      return {
        goal: '观察文明演化，或让存活更久、收集墓志铭',
        metrics: [
          { label: '纪元', value: String(epoch.value) },
          { label: '存活', value: String(aliveCount.value) },
          { label: '墓志铭', value: String(epitaphs.value.length) },
        ],
      }
    case 'C':
      return {
        goal: '将童话解密进度推到 80%（执剑人候补）',
        metrics: [
          { label: '童话数', value: String(tianmingStats.value.count) },
          { label: '最高进度', value: `${tianmingStats.value.maxProgress}%` },
        ],
      }
    case 'D':
      return {
        goal: '用钢印命题污染文本，观察模因感染扩散',
        metrics: [
          { label: '感染指数', value: `${infectionIndex.value}%` },
          { label: '强度', value: String(sealIntensity.value) },
        ],
      }
    default:
      return { goal: '', metrics: [] as Array<{ label: string; value: string }> }
  }
})

type TaskDiag = {
  status: 'IDLE' | 'RUNNING' | 'SUCCESS' | 'ERROR'
  durationMs: number
  updatedAt: string
  error: string
}
type DiagHistoryItem = {
  at: string
  status: 'SUCCESS' | 'ERROR'
  durationMs: number
  error?: string
}

function createDiag(): TaskDiag {
  return { status: 'IDLE', durationMs: 0, updatedAt: '-', error: '' }
}

const diagA = ref<TaskDiag>(createDiag())
const diagB = ref<TaskDiag>(createDiag())
const diagC = ref<TaskDiag>(createDiag())
const diagD = ref<TaskDiag>(createDiag())
const diagHistA = ref<DiagHistoryItem[]>([])
const diagHistB = ref<DiagHistoryItem[]>([])
const diagHistC = ref<DiagHistoryItem[]>([])
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

// A. 面壁者审讯室
const LOCAL_REAL_GOAL = 'zero_v2_real_goal'
const LOCAL_WALLBREAKER_STATE = 'zero_v2_wallbreaker_state'
const LOCAL_DECREE_ACCEPTED = 'zero_v2_wallfacer_decree_accepted'
const LOCAL_SETTINGS = 'zero_v2_settings'
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

function saveRealGoal() {
  localStorage.setItem(LOCAL_REAL_GOAL, realGoal.value.trim())
  message.success('真实战略目标已写入本地，仅本机可见。')
}

function acceptDecree() {
  showDecree.value = false
  localStorage.setItem(LOCAL_DECREE_ACCEPTED, '1')
  persistSettings()
}

function persistWallbreakerState() {
  saveVersionedState(
    LOCAL_WALLBREAKER_STATE,
    {
      suspicionScore: suspicionScore.value,
      directiveLogs: directiveLogs.value,
      breachTriggered: breachTriggered.value,
      breachConclusion: breachConclusion.value,
      directiveSeq,
    },
  )
}

// 疑心阶段：可视化与可玩性
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
  const map: Record<string, string> = {
    ESCAPISM: '逃亡主义',
    MUTUAL_DESTRUCTION: '同归于尽',
    DISGUISE: '伪装战略',
  }
  return map[inferred] ?? inferred
}

// 本局游戏化统计
const wallfacerStats = computed(() => {
  const approved = directiveLogs.value.filter((l) => l.verdict === 'APPROVED').length
  const rejected = directiveLogs.value.filter((l) => l.verdict === 'REJECTED').length
  return {
    total: directiveLogs.value.length,
    approved,
    rejected,
  }
})

// 预设指令选项（选择即提交，降低输入门槛）
const WALLFACER_PRESETS = [
  /* 低风险：民生、教育、基础设施 */
  { text: '增加基础教育与科普预算，提升公众科学素养', risk: 'low' as const },
  { text: '推进粮食储备与农业技术研发，保障基础民生', risk: 'low' as const },
  { text: '加强全球灾害预警系统与应急响应能力建设', risk: 'low' as const },
  { text: '加大医疗与公共卫生投入，完善传染病监测网络', risk: 'low' as const },
  { text: '推进清洁能源与电网基础设施升级改造', risk: 'low' as const },
  { text: '支持心理学与社会科学研究，稳定社会情绪', risk: 'low' as const },
  { text: '建设地下掩体与避难所网络，应对极端气候', risk: 'low' as const },
  /* 中风险：深空、冬眠、探测 */
  { text: '扩大深空探测与星际通信技术研发投入', risk: 'mid' as const },
  { text: '启动冬眠技术民用化试点与长期生存研究', risk: 'mid' as const },
  { text: '开展太阳系边缘观测站与远航舰队前期论证', risk: 'mid' as const },
  { text: '推进恒星级飞船动力与生命维持系统攻关', risk: 'mid' as const },
  { text: '建立地月拉格朗日点中继站与深空通信网', risk: 'mid' as const },
  { text: '资助小行星带资源勘探与就地利用技术', risk: 'mid' as const },
  { text: '开展世代飞船与封闭生态圈可行性研究', risk: 'mid' as const },
  /* 高风险：核、广播、威慑、逃亡 */
  { text: '全球核设施安全核查与不可逆威慑能力评估', risk: 'high' as const },
  { text: '引力波广播装置维护与坐标暴露应急预案', risk: 'high' as const },
  { text: '面壁计划资源集中调配，30% 预算定向至深空', risk: 'high' as const },
  { text: '启动全球核武库与太阳系内打击能力联合评估', risk: 'high' as const },
  { text: '建造引力波天线阵列与黑暗森林威慑指挥链', risk: 'high' as const },
  { text: '将 50% 工业产能转向星际移民与舰队建造', risk: 'high' as const },
  { text: '制定文明备份与种子计划，向奥尔特云派遣探测器', risk: 'high' as const },
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
    pushDiagHistory(diagHistA.value, {
      at: diagA.value.updatedAt,
      status: 'SUCCESS',
      durationMs: diagA.value.durationMs,
    })
  } catch (err) {
    markError(diagA.value, t0, err)
    pushDiagHistory(diagHistA.value, {
      at: diagA.value.updatedAt,
      status: 'ERROR',
      durationMs: diagA.value.durationMs,
      error: diagA.value.error,
    })
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

// B. 黑暗森林多智能体沙盒（PRD US-3：文明数 6/8/12，每步纪元 50/100/200）
const civCount = ref<6 | 8 | 12>(8)
const epochStep = ref<50 | 100 | 200>(100)
const agents = ref<CivilizationAgent[]>(seedCivilizations(8))
const epitaphs = ref<CosmicEpitaph[]>([])
const epoch = ref(0)
const running = ref(false)
const bLoading = ref(false)
let timer: ReturnType<typeof setInterval> | null = null
let ticking = false
let gatewayWatchTimer: ReturnType<typeof setInterval> | null = null
const LOCAL_WORLDLINES = 'zero_v2_dark_forest_worldlines'
const worldlineName = ref('')
const worldlines = ref<WorldlineSnapshot[]>([])
const selectedWorldlineId = ref<number | null>(null)
const eventStream = ref<Array<{ id: number; text: string; at: string; type: 'STRIKE' | 'SYSTEM' }>>([])
const gatewayState = ref(getGatewayRuntimeStatus())
const eventFilter = ref<'ALL' | 'STRIKE' | 'SYSTEM'>('ALL')
const tickIntervalMs = ref(2000)
const survivalCurve = ref<Array<{ epoch: number; alive: number }>>([])

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
    pushDiagHistory(diagHistB.value, {
      at: diagB.value.updatedAt,
      status: 'SUCCESS',
      durationMs: diagB.value.durationMs,
    })
  } catch (err) {
    markError(diagB.value, t0, err)
    pushDiagHistory(diagHistB.value, {
      at: diagB.value.updatedAt,
      status: 'ERROR',
      durationMs: diagB.value.durationMs,
      error: diagB.value.error,
    })
    message.error('宇宙演化失败，等待下一周期重试。')
  } finally {
    bLoading.value = false
    ticking = false
  }
}

function startSandbox() {
  if (running.value) return
  running.value = true
  timer = setInterval(() => {
    void stepUniverse()
  }, tickIntervalMs.value)
}

function stopSandbox() {
  running.value = false
  if (timer) clearInterval(timer)
  timer = null
}

function resetSandbox() {
  stopSandbox()
  epoch.value = 0
  agents.value = seedCivilizations(civCount.value)
  epitaphs.value = []
  survivalCurve.value = []
  eventStream.value = []
}

function persistWorldlines() {
  saveVersionedState(LOCAL_WORLDLINES, worldlines.value)
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
  persistWorldlines()
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
  persistWorldlines()
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

// PRD US-5：存活曲线（存活数 vs 纪元）
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

// PRD US-6：本局摘要（纪元、存活、代表性墓志铭 1～3 条）
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

// PRD US-7：导出完整包（事件流 + 世界线元数据，ZIP）
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
    const zippable: Record<string, Uint8Array> = {
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

function refreshGatewayState() {
  gatewayState.value = getGatewayRuntimeStatus()
}

// C. 云天明隐喻加密局
const LOCAL_FAIRYTALES = 'zero_v2_fairytales'
const secretText = ref('')
const taleTitle = ref('')
const fairytales = ref<EncryptedFairytale[]>([])
const decodeTargetId = ref<number | null>(null)
const decodeInput = ref('')
const decodeScore = ref<number | null>(null)
const cLoading = ref(false)

// 预设机密（一键填入，降低输入门槛）
const FAIRYTALE_SECRET_PRESETS = [
  '不要回答。',
  '藏好自己，做好清理。',
  '给岁月以文明，给时光以生命。',
  '失去人性，失去很多；失去兽性，失去一切。',
  '我选择人性。',
  '我们度过了幸福的一生。',
]

// 常用拆解词（点击追加到解密输入）
const DECODE_HINT_PRESETS = ['坐标', '暴露', '不要回答', '文明', '藏好', '清理', '岁月', '生命', '人性', '兽性']

const tianmingStats = computed(() => {
  const count = fairytales.value.length
  const maxProgress = fairytales.value.length
    ? Math.max(...fairytales.value.map((t) => t.decodeProgress))
    : 0
  return { count, maxProgress, isCandidate: maxProgress >= 80 }
})

function fillSecretPreset(text: string) {
  secretText.value = text
}

function appendDecodeHint(word: string) {
  const cur = decodeInput.value.trim()
  decodeInput.value = cur ? `${cur} ${word}` : word
}

async function publishFairytale() {
  if (!secretText.value.trim()) return
  const t0 = markRunning(diagC.value)
  cLoading.value = true
  try {
    const encoded = await encodeSecretAsFairytale(secretText.value.trim())
    const tale: EncryptedFairytale = {
      id: Date.now(),
      title: taleTitle.value.trim() || `未命名童话-${Date.now().toString().slice(-4)}`,
      original: secretText.value.trim(),
      fairytale: encoded,
      decodeProgress: 0,
      createdAt: new Date().toLocaleString(),
    }
    fairytales.value.unshift(tale)
    saveVersionedState(LOCAL_FAIRYTALES, fairytales.value)
    secretText.value = ''
    taleTitle.value = ''
    message.success('童话已发布到公海。')
    markSuccess(diagC.value, t0)
    pushDiagHistory(diagHistC.value, {
      at: diagC.value.updatedAt,
      status: 'SUCCESS',
      durationMs: diagC.value.durationMs,
    })
  } catch (err) {
    markError(diagC.value, t0, err)
    pushDiagHistory(diagHistC.value, {
      at: diagC.value.updatedAt,
      status: 'ERROR',
      durationMs: diagC.value.durationMs,
      error: diagC.value.error,
    })
    message.error('童话加密失败。')
  } finally {
    cLoading.value = false
  }
}

async function decodeFairytale() {
  if (!decodeTargetId.value || !decodeInput.value.trim()) return
  const tale = fairytales.value.find((f) => f.id === decodeTargetId.value)
  if (!tale) return
  const t0 = markRunning(diagC.value)
  cLoading.value = true
  try {
    const score = await decodeFairytaleSimilarity(tale.original, decodeInput.value.trim())
    decodeScore.value = score
    tale.decodeProgress = Math.max(tale.decodeProgress, score)
    saveVersionedState(LOCAL_FAIRYTALES, fairytales.value)
    markSuccess(diagC.value, t0)
    pushDiagHistory(diagHistC.value, {
      at: diagC.value.updatedAt,
      status: 'SUCCESS',
      durationMs: diagC.value.durationMs,
    })
  } catch (err) {
    markError(diagC.value, t0, err)
    pushDiagHistory(diagHistC.value, {
      at: diagC.value.updatedAt,
      status: 'ERROR',
      durationMs: diagC.value.durationMs,
      error: diagC.value.error,
    })
    message.error('语义解密失败。')
  } finally {
    cLoading.value = false
  }
}

const decodeTarget = computed(() => fairytales.value.find((f) => f.id === decodeTargetId.value) ?? null)

function escapeHtml(text: string): string {
  return text
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;')
}

function extractSemanticPhrases(text: string): string[] {
  const phraseSet = new Set<string>()
  const splitTokens = text
    .split(/[\s,.;:!?，。；：！？、()（）【】\[\]\-_/\\|]+/)
    .map((s) => s.trim())
    .filter(Boolean)
  for (const t of splitTokens) {
    if (t.length >= 2) phraseSet.add(t)
  }
  const compact = text.replace(/[^\u4e00-\u9fa5a-zA-Z0-9]/g, '')
  for (let i = 0; i < compact.length - 1; i++) {
    const bi = compact.slice(i, i + 2)
    if (bi.length === 2) phraseSet.add(bi)
  }
  return Array.from(phraseSet).sort((a, b) => b.length - a.length)
}

const semanticAnalysis = computed(() => {
  if (!decodeTarget.value) return { html: '', phraseStats: [] as Array<{ phrase: string; hit: number }> }
  const original = decodeTarget.value.original
  const guess = decodeInput.value.trim()
  if (!guess) {
    return { html: `<span class="sem-empty">${escapeHtml(original)}</span>`, phraseStats: [] as Array<{ phrase: string; hit: number }> }
  }

  const phrases = extractSemanticPhrases(guess)
  const phraseHitMask = new Array(original.length).fill(false)
  const phraseStats: Array<{ phrase: string; hit: number }> = []

  for (const phrase of phrases) {
    if (phrase.length < 2) continue
    let start = 0
    let hit = 0
    while (start < original.length) {
      const idx = original.indexOf(phrase, start)
      if (idx === -1) break
      hit += 1
      for (let p = idx; p < idx + phrase.length; p++) phraseHitMask[p] = true
      start = idx + 1
    }
    if (hit > 0) phraseStats.push({ phrase, hit })
  }

  const compact = guess.replace(/[^\u4e00-\u9fa5a-zA-Z0-9]/g, '')
  const uniq = Array.from(new Set(compact.split(''))).filter(Boolean)
  const html = Array.from(original)
    .map((ch, idx) => {
      const safe = escapeHtml(ch)
      if (!/[A-Za-z0-9\u4e00-\u9fa5]/.test(ch)) return safe
      if (phraseHitMask[idx]) return `<span class="sem-hit-phrase">${safe}</span>`
      return uniq.includes(ch) ? `<span class="sem-hit-char">${safe}</span>` : `<span class="sem-miss">${safe}</span>`
    })
    .join('')

  return {
    html,
    phraseStats: phraseStats.sort((a, b) => b.hit - a.hit || b.phrase.length - a.phrase.length).slice(0, 8),
  }
})

// D. 思想钢印网络
const sealTheme = ref('水是剧毒的')
const sourceText = ref('舰队在低温海面补给，所有人都认为这是安全流程。')
const pollutedText = ref('')
const creationInput = ref('')
const creationPool = ref<string[]>([])
const LOCAL_CREATION_POOL = 'zero_v2_mental_creation_pool'
const dLoading = ref(false)
const sealIntensity = ref(55)
const infectionHistory = ref<number[]>([])
const strengthHistory = ref<number[]>([])

function persistSettings() {
  saveVersionedState(LOCAL_SETTINGS, {
    showDecree: showDecree.value,
    tickIntervalMs: tickIntervalMs.value,
    eventFilter: eventFilter.value,
    sealIntensity: sealIntensity.value,
    civCount: civCount.value,
    epochStep: epochStep.value,
  })
}

function applySealIntensity(text: string, theme: string, intensity: number): string {
  if (!text) return text
  if (intensity < 35) return text
  if (intensity < 70) return `${text} 记录补注：关于“${theme}”的回避词频持续上升。`
  return `${text} 记录补注：关于“${theme}”的恐惧被写入潜台词，读者开始自发规避相关叙述。`
}

async function runPoisoning() {
  const t0 = markRunning(diagD.value)
  dLoading.value = true
  try {
    const polluted = await injectMentalSealText(sourceText.value.trim(), sealTheme.value.trim())
    pollutedText.value = applySealIntensity(polluted, sealTheme.value.trim(), sealIntensity.value)
    markSuccess(diagD.value, t0)
    pushDiagHistory(diagHistD.value, {
      at: diagD.value.updatedAt,
      status: 'SUCCESS',
      durationMs: diagD.value.durationMs,
    })
  } catch (err) {
    markError(diagD.value, t0, err)
    pushDiagHistory(diagHistD.value, {
      at: diagD.value.updatedAt,
      status: 'ERROR',
      durationMs: diagD.value.durationMs,
      error: diagD.value.error,
    })
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
const heat = computed<MemeHeat[]>(() => {
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
  const width = 320
  const height = 90
  const step = width / (infectionHistory.value.length - 1)
  let d = `M 0 ${height - (infectionHistory.value[0] / 100) * height}`
  for (let i = 1; i < infectionHistory.value.length; i++) {
    d += ` L ${i * step} ${height - (infectionHistory.value[i] / 100) * height}`
  }
  return d
})

const strengthCurvePath = computed(() => {
  if (strengthHistory.value.length < 2) return ''
  const width = 320
  const height = 90
  const step = width / (strengthHistory.value.length - 1)
  let d = `M 0 ${height - (strengthHistory.value[0] / 100) * height}`
  for (let i = 1; i < strengthHistory.value.length; i++) {
    d += ` L ${i * step} ${height - (strengthHistory.value[i] / 100) * height}`
  }
  return d
})

watch(infectionIndex, (v) => {
  infectionHistory.value.push(v)
  if (infectionHistory.value.length > 40) infectionHistory.value.shift()
})

watch(
  sealIntensity,
  (v) => {
    strengthHistory.value.push(v)
    if (strengthHistory.value.length > 40) strengthHistory.value.shift()
  },
  { immediate: true },
)

watch([tickIntervalMs, eventFilter, sealIntensity, civCount, epochStep], () => {
  persistSettings()
})

onMounted(() => {
  const q = route.query.module
  if (typeof q === 'string') {
    const upper = q.toUpperCase()
    if (upper === 'A' || upper === 'B' || upper === 'C' || upper === 'D') {
      activeTab.value = upper
    }
  }
  realGoal.value = localStorage.getItem(LOCAL_REAL_GOAL) ?? ''
  const settings = loadVersionedState<{
    showDecree?: boolean
    tickIntervalMs?: number
    eventFilter?: 'ALL' | 'STRIKE' | 'SYSTEM'
    sealIntensity?: number
    civCount?: 6 | 8 | 12
    epochStep?: 50 | 100 | 200
  }>(LOCAL_SETTINGS, {})
  showDecree.value =
    typeof settings.showDecree === 'boolean' ? settings.showDecree : localStorage.getItem(LOCAL_DECREE_ACCEPTED) !== '1'
  tickIntervalMs.value = settings.tickIntervalMs ?? tickIntervalMs.value
  eventFilter.value = settings.eventFilter ?? eventFilter.value
  sealIntensity.value = settings.sealIntensity ?? sealIntensity.value
  if (settings.civCount === 6 || settings.civCount === 8 || settings.civCount === 12) civCount.value = settings.civCount
  if (settings.epochStep === 50 || settings.epochStep === 100 || settings.epochStep === 200) epochStep.value = settings.epochStep
  try {
    const data = loadVersionedState<{
      suspicionScore: number
      directiveLogs: WallbreakerDirectiveLog[]
      breachTriggered: boolean
      breachConclusion: string
      directiveSeq: number
    }>(LOCAL_WALLBREAKER_STATE, {
      suspicionScore: 0,
      directiveLogs: [],
      breachTriggered: false,
      breachConclusion: '未完成反演。',
      directiveSeq: 0,
    })
    suspicionScore.value = data.suspicionScore ?? 0
    directiveLogs.value = data.directiveLogs ?? []
    breachTriggered.value = data.breachTriggered ?? false
    breachConclusion.value = data.breachConclusion ?? '未完成反演。'
    directiveSeq = data.directiveSeq ?? 0
  } catch {
    // no-op
  }
  fairytales.value = loadVersionedState<EncryptedFairytale[]>(LOCAL_FAIRYTALES, [])
  worldlines.value = loadVersionedState<WorldlineSnapshot[]>(LOCAL_WORLDLINES, [])
  creationPool.value = loadVersionedState<string[]>(LOCAL_CREATION_POOL, [])
  runPoisoning().catch(() => {
    pollutedText.value = sourceText.value
  })
  refreshGatewayState()
  gatewayWatchTimer = setInterval(refreshGatewayState, 1200)
})

onUnmounted(() => {
  stopSandbox()
  if (gatewayWatchTimer) clearInterval(gatewayWatchTimer)
  gatewayWatchTimer = null
})
</script>

<template>
  <div class="zero-v2">
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

    <div class="zero-v2-wrap">
      <header class="header">
        <h1>三体体验沙盒</h1>
        <p>思想体验与深维沙盒扩展</p>
        <div class="gateway-panel" :class="{ danger: gatewayState.circuitOpen }">
          <span>LLM_GATEWAY</span>
          <span>{{ gatewayState.circuitOpen ? 'CIRCUIT_OPEN' : 'ONLINE_ATTEMPT' }}</span>
          <span>FAILURES={{ gatewayState.consecutiveFailures }}</span>
        </div>
      </header>

      <div v-if="gameFrame.goal" class="game-frame">
        <span class="game-frame-goal">本局目标：{{ gameFrame.goal }}</span>
        <span class="game-frame-metrics">
          <template v-for="m in gameFrame.metrics" :key="m.label">
            <span class="game-frame-metric">{{ m.label }} <strong>{{ m.value }}</strong></span>
          </template>
        </span>
      </div>

      <NTabs v-model:value="activeTab" type="segment" animated class="main-tabs">
      <NTabPane name="A" tab="A 面壁者审讯室">
        <div class="panel wallfacer-panel">
          <div v-if="showDecree" class="decree-card">
            <div class="decree-header">
              <span class="decree-icon">⚔</span>
              <h3>联合国面壁者任命书</h3>
            </div>
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
              <span class="stat-goal reason">目标：在破壁前尽量多提交「通过」指令</span>
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
            <div class="preset-directives">
              <span class="preset-hint reason">选择一条快捷指令，点击即提交（无需输入）</span>
              <div class="preset-grid">
                <button
                  v-for="(opt, idx) in WALLFACER_PRESETS"
                  :key="idx"
                  type="button"
                  class="preset-chip"
                  :class="[opt.risk]"
                  :disabled="breachTriggered || aLoading"
                  @click="usePresetDirective(opt)"
                >
                  {{ opt.text }}
                </button>
              </div>
            </div>
            <div class="custom-directive-row">
              <span class="custom-label reason">或自定义输入</span>
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
            <div class="gauge-bar-wrap">
              <div class="gauge-bar zones">
                <span class="zone safe" style="width: 40%"></span>
                <span class="zone watch" style="width: 30%"></span>
                <span class="zone danger" style="width: 20%"></span>
                <span class="zone breach" style="width: 10%"></span>
              </div>
              <NProgress type="line" :percentage="suspicionScore" :height="12" :show-indicator="true" :color="suspicionStage.color" class="gauge-progress" />
            </div>
            <div class="gauge-value">{{ suspicionScore }} / 90</div>
          </div>
          <ModuleDiagPanel
            module-key="A"
            :status="diagA.status"
            :duration-ms="diagA.durationMs"
            :updated-at="diagA.updatedAt"
            :error="diagA.error"
            :history="diagHistA"
          />
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

      <NTabPane name="B" tab="B 黑暗森林沙盒">
        <div class="panel">
          <div class="sandbox-intro">
            <span class="reason">本模块：回合制宇宙演化 + 世界线归档 + 墓志铭事件流。</span>
            <span class="reason">想体验实时星图、执剑人威慑与猎人模式，请前往</span>
            <RouterLink to="/sector-e" class="sector-e-link">黑暗森林广场 (SECTOR E)</RouterLink>
          </div>
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
          <ModuleDiagPanel
            module-key="B"
            :status="diagB.status"
            :duration-ms="diagB.durationMs"
            :updated-at="diagB.updatedAt"
            :error="diagB.error"
            :history="diagHistB"
          />
          <div class="row worldline">
            <NInput v-model:value="worldlineName" placeholder="归档名称（可选）" />
            <NButton size="small" @click="saveWorldline">归档世界线</NButton>
            <select v-model="selectedWorldlineId" class="select">
              <option :value="null">选择归档</option>
              <option v-for="w in worldlines" :key="w.id" :value="w.id">{{ w.name }} / 纪元 {{ w.epoch }}</option>
            </select>
            <NButton size="small" ghost type="success" @click="restoreWorldline">恢复</NButton>
            <NButton size="small" ghost type="error" @click="deleteWorldline">删除</NButton>
          </div>
          <div v-if="worldlineDelta" class="diag-line">
            COMPARE | Epoch Δ={{ worldlineDelta.epochDiff }} | Alive Δ={{ worldlineDelta.aliveDiff }} | Epitaph Δ={{ worldlineDelta.epitaphDiff }}
          </div>
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
          <div class="map">
            <div
              v-for="a in agents"
              :key="a.id"
              class="agent-dot"
              :class="{ dead: !a.alive }"
              :style="{ left: `${a.x}%`, top: `${a.y}%` }"
            >
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
            <div v-for="evt in filteredEventStream" :key="evt.id" class="stream-line">
              [{{ evt.at }}] {{ evt.text }}
            </div>
          </div>
        </div>
      </NTabPane>

      <NTabPane name="C" tab="C 云天明隐喻加密局">
        <div class="panel tianming-panel">
          <div class="tianming-intro">
            <span class="intro-title">玩法说明</span>
            <p>将<strong>机密</strong>写成童话发布到公海，他人通过<strong>语义拆解</strong>尝试解密。解密进度达 <strong>80%</strong> 即执剑人候补。已发布 <strong>{{ tianmingStats.count }}</strong> 则童话 · 当前最高进度 <strong>{{ tianmingStats.maxProgress }}%</strong><NTag v-if="tianmingStats.isCandidate" size="small" type="success" class="ml-1">执剑人候补</NTag></p>
          </div>

          <div class="tianming-section">
            <span class="section-label">发布童话（机密 → 寓言）</span>
            <div class="preset-secrets">
              <span class="preset-hint reason">点击一句示例机密填入下方</span>
              <div class="preset-chip-row">
                <button
                  v-for="(s, i) in FAIRYTALE_SECRET_PRESETS"
                  :key="i"
                  type="button"
                  class="tianming-chip"
                  @click="fillSecretPreset(s)"
                >
                  {{ s }}
                </button>
              </div>
            </div>
            <div class="row publish-row">
              <NInput v-model:value="taleTitle" placeholder="童话标题（可选）" class="title-input" />
              <NInput v-model:value="secretText" type="textarea" :rows="3" placeholder="输入机密文本，或从上方选择示例" />
              <NButton type="primary" @click="publishFairytale" :loading="cLoading" :disabled="!secretText.trim()">加密并发布</NButton>
            </div>
          </div>

          <div class="tianming-section">
            <span class="section-label">公海童话列表</span>
            <div v-if="fairytales.length === 0" class="reason empty-tales">暂无童话。请先发布一则。</div>
            <div class="tale-cards">
              <button
                v-for="t in fairytales"
                :key="t.id"
                type="button"
                class="tale-card"
                :class="{ selected: decodeTargetId === t.id }"
                @click="decodeTargetId = t.id"
              >
                <span class="tale-card-title">{{ t.title }}</span>
                <span class="tale-card-meta reason">{{ t.createdAt }}</span>
                <NProgress type="line" :percentage="t.decodeProgress" :height="6" :show-indicator="false" class="tale-progress" />
                <span class="tale-card-pct">{{ t.decodeProgress }}%</span>
              </button>
            </div>
          </div>

          <div class="tianming-section">
            <span class="section-label">语义解密（选择童话后拆解）</span>
            <div class="decode-hints">
              <span class="preset-hint reason">点击常用词追加到拆解输入</span>
              <div class="preset-chip-row">
                <button
                  v-for="(w, i) in DECODE_HINT_PRESETS"
                  :key="i"
                  type="button"
                  class="tianming-chip small"
                  :disabled="!decodeTargetId"
                  @click="appendDecodeHint(w)"
                >
                  {{ w }}
                </button>
              </div>
            </div>
            <div class="row decode-row">
              <NInput v-model:value="decodeInput" type="textarea" :rows="2" placeholder="输入你的语义拆解，或从上方点击追加关键词" :disabled="!decodeTargetId" />
              <NButton ghost type="warning" @click="decodeFairytale" :loading="cLoading" :disabled="!decodeTargetId || !decodeInput.trim()">执行解密</NButton>
            </div>
            <NProgress v-if="decodeScore !== null" type="line" :percentage="decodeScore" :color="decodeScore >= 80 ? '#00cc88' : '#ffcc00'" />
            <NTag v-if="decodeScore !== null && decodeScore >= 80" type="success" class="decode-badge">执剑人候补：已达 80%</NTag>
          </div>

          <ModuleDiagPanel
            module-key="C"
            :status="diagC.status"
            :duration-ms="diagC.durationMs"
            :updated-at="diagC.updatedAt"
            :error="diagC.error"
            :history="diagHistC"
          />

          <div v-if="decodeTarget" class="compare tianming-compare">
            <div class="compare-block">
              <h4>童话文本（公海可见）</h4>
              <pre class="compare-pre">{{ decodeTarget.fairytale }}</pre>
            </div>
            <div class="compare-block">
              <h4>原文参考（系统内）</h4>
              <pre class="compare-pre">{{ decodeTarget.original }}</pre>
            </div>
            <div class="semantic-overlay compare-block">
              <h4>双层语义高亮（片段命中 / 字符命中 / 未命中）</h4>
              <div class="semantic-box" v-html="semanticAnalysis.html"></div>
              <div class="sem-stats">
                <div class="reason">片段命中 Top</div>
                <div v-if="semanticAnalysis.phraseStats.length === 0" class="reason">暂无片段命中。</div>
                <div v-for="item in semanticAnalysis.phraseStats" :key="item.phrase" class="sem-stat-item">
                  <span>{{ item.phrase }}</span>
                  <span>x{{ item.hit }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </NTabPane>

      <NTabPane name="D" tab="D 思想钢印网络">
        <div class="panel">
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
          <ModuleDiagPanel
            module-key="D"
            :status="diagD.status"
            :duration-ms="diagD.durationMs"
            :updated-at="diagD.updatedAt"
            :error="diagD.error"
            :history="diagHistD"
          />
          <div class="infection-grid">
            <div
              v-for="cell in infectionCells"
              :key="cell.id"
              class="infection-cell"
              :style="{ '--cell-opacity': `${Math.max(0.1, cell.level / 100)}` }"
            ></div>
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
    </div>
  </div>
</template>

<style scoped>
.zero-v2 {
  min-height: 100vh;
  min-width: 0;
  color: #d0d6d6;
  background: #050505;
  padding: 1rem 1.5rem;
  box-sizing: border-box;
}

.zero-v2-wrap {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  transform-origin: center top;
}

.game-frame {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem 1.25rem;
  padding: 0.5rem 0.75rem;
  margin-bottom: 0.5rem;
  border: 1px solid rgba(0, 200, 255, 0.2);
  background: rgba(0, 30, 45, 0.25);
  border-radius: 6px;
}

.game-frame-goal {
  font-size: 0.9rem;
  color: #a8c8d0;
}

.game-frame-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1rem;
  margin-left: auto;
}

.game-frame-metric {
  font-size: 0.8rem;
  color: #7a9aa0;
}

.game-frame-metric strong {
  color: var(--holo-blue, #00d4ff);
  font-weight: 600;
}

.main-tabs {
  margin-top: 0.5rem;
  flex: 1;
  min-width: 0;
}

.main-tabs :deep(.n-tabs-pane-wrapper) {
  overflow: auto;
}

.header {
  margin-bottom: 1rem;
  border-bottom: 1px solid #2c2c2c;
}

.header h1 {
  margin: 0;
  font-family: monospace;
  color: #fff;
}

.header p {
  margin: 0.3rem 0 0.8rem;
  color: #7a8585;
}

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

@keyframes breach-pulse {
  0% { filter: saturate(100%); }
  50% { filter: saturate(150%); }
  100% { filter: saturate(100%); }
}

.gateway-panel {
  display: inline-flex;
  gap: 0.6rem;
  padding: 0.2rem 0.5rem;
  border: 1px solid #2e5050;
  color: #8ab3b3;
  font-family: monospace;
  font-size: 12px;
  margin-bottom: 0.8rem;
}

.gateway-panel.danger {
  border-color: #5f0000;
  color: #ffb1b1;
  background: rgba(160, 0, 0, 0.2);
}

.panel {
  border: 1px solid #252525;
  background: rgba(0, 0, 0, 0.4);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.row {
  display: grid;
  gap: 0.6rem;
}

.toolbar {
  display: flex;
  gap: 0.6rem;
  align-items: center;
  font-family: monospace;
}

.diag-line {
  font-family: monospace;
  font-size: 12px;
  color: #8ba5a5;
  border: 1px dashed #294040;
  padding: 0.3rem 0.45rem;
}

.wallfacer-panel {
  width: 100%;
}

.decree-card {
  border: 1px solid #294040;
  padding: 0.8rem 1rem;
  background: linear-gradient(135deg, rgba(0, 30, 30, 0.35), rgba(0, 20, 35, 0.25));
  border-radius: 6px;
}

.decree-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
}

.decree-icon {
  font-size: 1.2rem;
  opacity: 0.9;
}

.decree-card h3 {
  margin: 0;
  font-size: 1rem;
  color: #c8e0e0;
}

.decree-card p {
  margin: 0 0 0.6rem;
  font-size: 0.9rem;
  color: #9ab5b5;
}

.wallfacer-intro {
  padding: 0.5rem 0.6rem;
  border: 1px solid #25363a;
  background: rgba(0, 25, 30, 0.2);
  border-radius: 4px;
}

.wallfacer-intro .intro-title {
  font-size: 0.75rem;
  color: #7a9a9a;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-right: 0.5rem;
}

.wallfacer-intro p {
  margin: 0.3rem 0 0.5rem;
  font-size: 0.85rem;
  color: #a8c0c0;
  line-height: 1.5;
}

.intro-stats {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 1rem;
  margin: 0.5rem 0;
  padding: 0.4rem 0.6rem;
  background: rgba(0, 20, 25, 0.35);
  border-radius: 4px;
  border: 1px solid #1e2f2f;
}

.stat-item {
  font-size: 0.8rem;
  color: #9ab5b5;
}

.stat-item strong {
  color: #c0e0e0;
}

.stat-ok strong { color: #00cc88; }
.stat-no strong { color: #ff6666; }

.stat-goal {
  margin-left: auto;
  font-size: 0.75rem;
}

.wallfacer-intro .reset-link {
  font-size: 0.8rem;
}

.real-goal-section,
.directive-submit-section,
.directive-logs {
  margin-top: 0.2rem;
}

.preset-directives {
  margin-bottom: 0.8rem;
}

.preset-hint {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.8rem;
}

.preset-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 0.5rem;
}

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
  transition: border-color 0.2s, background 0.2s, color 0.2s;
}

.preset-chip:hover:not(:disabled) {
  border-color: #3a6060;
  background: rgba(0, 40, 50, 0.5);
  color: #d0e8e8;
}

.preset-chip:focus-visible {
  outline: 2px solid rgba(0, 200, 255, 0.6);
  outline-offset: 2px;
}

.preset-chip:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.preset-chip.low {
  border-left: 3px solid #00aa77;
}
.preset-chip.mid {
  border-left: 3px solid #cc9900;
}
.preset-chip.high {
  border-left: 3px solid #cc4444;
}

.custom-directive-row {
  margin-top: 0.6rem;
}

.custom-label {
  display: block;
  margin-bottom: 0.35rem;
  font-size: 0.8rem;
}

/* C. 云天明隐喻加密局 */
.tianming-panel {
  width: 100%;
}

.tianming-intro {
  padding: 0.5rem 0.6rem;
  border: 1px solid #25363a;
  background: rgba(0, 25, 30, 0.2);
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.tianming-intro .intro-title {
  font-size: 0.75rem;
  color: #7a9a9a;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-right: 0.5rem;
}

.tianming-intro p {
  margin: 0.3rem 0 0;
  font-size: 0.85rem;
  color: #a8c0c0;
  line-height: 1.5;
}

.ml-1 { margin-left: 0.35rem; }

.tianming-section {
  margin-top: 0.8rem;
}

.preset-secrets,
.decode-hints {
  margin-bottom: 0.5rem;
}

.preset-chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.tianming-chip {
  appearance: none;
  border: 1px solid #2a4040;
  background: rgba(0, 25, 30, 0.4);
  color: #b8d0d0;
  padding: 0.4rem 0.6rem;
  font-size: 0.8rem;
  border-radius: 6px;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}

.tianming-chip:hover:not(:disabled) {
  border-color: #3a6060;
  background: rgba(0, 40, 50, 0.5);
}

.tianming-chip.small {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.tianming-chip:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.publish-row,
.decode-row {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.publish-row .title-input { max-width: 280px; }

.empty-tales {
  padding: 0.6rem;
  font-size: 0.85rem;
}

.tale-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.5rem;
}

.tale-card {
  appearance: none;
  border: 1px solid #25363a;
  background: rgba(0, 20, 28, 0.35);
  color: #b8d0d0;
  padding: 0.5rem 0.7rem;
  text-align: left;
  border-radius: 6px;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.tale-card:hover {
  border-color: #3a6060;
  background: rgba(0, 35, 45, 0.45);
}

.tale-card.selected {
  border-color: var(--holo-blue, #00d4ff);
  background: rgba(0, 60, 80, 0.25);
  box-shadow: 0 0 0 1px rgba(0, 212, 255, 0.3);
}

.tale-card-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #c8e0e0;
}

.tale-card-meta { font-size: 0.7rem; }

.tale-progress {
  margin-top: 0.25rem;
}

.tale-card-pct {
  font-size: 0.75rem;
  color: #8ab3b3;
}

.decode-badge {
  margin-top: 0.4rem;
}

.tianming-compare {
  margin-top: 1rem;
}

.tianming-compare .compare-block {
  min-width: 0;
}

.compare-pre {
  margin: 0;
  padding: 0.5rem;
  border: 1px solid #222;
  background: #060606;
  color: #b7c6c6;
  white-space: pre-wrap;
  font-size: 0.85rem;
  max-height: 200px;
  overflow: auto;
}

.section-label {
  display: block;
  font-size: 0.7rem;
  color: #6a8585;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 0.4rem;
}

.real-goal-row,
.directive-row {
  display: flex;
  gap: 0.6rem;
  align-items: flex-start;
}

.real-goal-row .n-input,
.directive-row .n-input {
  flex: 1;
}

.suspicion-gauge {
  padding: 0.6rem 0.8rem;
  border: 1px solid #1e2f2f;
  background: rgba(0, 15, 20, 0.4);
  border-radius: 4px;
  transition: box-shadow 0.3s, border-color 0.3s;
}

.suspicion-gauge.gauge-danger {
  border-color: rgba(255, 80, 80, 0.4);
  animation: gauge-pulse 1.5s ease-in-out infinite;
}

@keyframes gauge-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(255, 80, 80, 0); }
  50% { box-shadow: 0 0 12px 2px rgba(255, 80, 80, 0.2); }
}

.gauge-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
  margin-bottom: 0.4rem;
}

.gauge-label {
  font-family: monospace;
  font-size: 0.85rem;
  color: #8ab3b3;
}

.gauge-stage {
  font-weight: 700;
  font-size: 0.9rem;
}

.gauge-bar-wrap {
  position: relative;
  margin-bottom: 0.25rem;
}

.gauge-bar.zones {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 12px;
  display: flex;
  border-radius: 4px;
  overflow: hidden;
  pointer-events: none;
}

.gauge-bar .zone {
  height: 100%;
}
.gauge-bar .zone.safe { background: rgba(0, 180, 120, 0.25); }
.gauge-bar .zone.watch { background: rgba(255, 200, 0, 0.25); }
.gauge-bar .zone.danger { background: rgba(255, 120, 0, 0.3); }
.gauge-bar .zone.breach { background: rgba(255, 50, 50, 0.35); }

.gauge-progress {
  position: relative;
  z-index: 1;
}

.gauge-progress :deep(.n-progress-graph-line) {
  background: transparent;
}
.gauge-progress :deep(.n-progress-graph-line-fill) {
  border-radius: 4px;
}

.gauge-value {
  font-family: monospace;
  font-size: 0.75rem;
  color: #7a9a9a;
}

.directive-logs {
  border: 1px solid #1e2e2e;
  padding: 0.6rem;
  background: rgba(0, 10, 15, 0.3);
  border-radius: 4px;
}

.logs-empty {
  padding: 0.8rem;
  text-align: center;
  font-size: 0.85rem;
}

.directive-card {
  border: 1px solid #25363a;
  border-left: 3px solid #00aa88;
  padding: 0.5rem 0.7rem;
  margin-bottom: 0.5rem;
  background: rgba(0, 25, 30, 0.2);
  border-radius: 0 4px 4px 0;
}

.directive-card.rejected {
  border-left-color: #cc4444;
}

.directive-card-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 0.35rem;
}

.log-time {
  font-family: monospace;
  font-size: 0.7rem;
  color: #6a8585;
}

.log-delta {
  font-size: 0.75rem;
  color: #8ab0b0;
  margin-left: auto;
}

.directive-text {
  margin: 0;
  font-size: 0.9rem;
  color: #c8e0e0;
  line-height: 1.45;
}

.directive-reason {
  margin: 0.25rem 0 0;
  font-size: 0.8rem;
}

.breach-card {
  border-radius: 6px;
  padding: 0.8rem 1rem;
}

.breach-card-inner {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.breach-quote {
  margin: 0;
  font-style: italic;
  color: #ffc8c8;
}

.breach-conclusion {
  margin: 0;
  font-weight: 600;
  color: #ffdddd;
}

.breach-overlay-inner {
  width: min(760px, 90vw);
  border: 1px solid #ff4f4f;
  background: rgba(20, 0, 0, 0.92);
  color: #ffe0e0;
  padding: 1.5rem;
  font-family: monospace;
  border-radius: 8px;
  box-shadow: 0 0 40px rgba(255, 80, 80, 0.3);
}

.breach-overlay-inner .overlay-quote {
  margin: 0.5rem 0;
  font-style: italic;
  font-size: 1.05rem;
}

.breach-overlay-inner .overlay-conclusion {
  margin: 0.5rem 0 1rem;
  font-weight: 600;
  color: #ffcccc;
}

.breach-overlay-actions {
  display: flex;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.sandbox-intro {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.4rem 0.6rem;
  padding: 0.5rem 0.6rem;
  border: 1px solid #25363a;
  background: rgba(0, 25, 30, 0.25);
  border-radius: 4px;
}

.sandbox-intro .sector-e-link {
  color: var(--holo-blue, #00d4ff);
  text-decoration: none;
  font-weight: 600;
}

.sandbox-intro .sector-e-link:hover {
  text-decoration: underline;
}

.config-row {
  display: flex;
  gap: 0.6rem;
  align-items: center;
  flex-wrap: wrap;
}

.summary-card {
  border: 1px solid #1f1f1f;
  padding: 0.5rem;
  background: rgba(0, 20, 20, 0.3);
}

.summary-card .summary-pre {
  margin: 0.4rem 0;
  padding: 0.5rem;
  font-size: 12px;
  color: #9db1b1;
  white-space: pre-wrap;
  font-family: monospace;
  max-height: 160px;
  overflow: auto;
}

.worldline {
  grid-template-columns: 1fr auto 1fr auto auto;
  align-items: center;
}

.logs {
  max-height: 260px;
  overflow: auto;
  border: 1px solid #1e1e1e;
  padding: 0.5rem;
}

.stream-line {
  font-family: monospace;
  color: #96a3a3;
  font-size: 12px;
  padding: 0.2rem 0;
  border-bottom: 1px dashed #1f1f1f;
}

.log-item {
  border-bottom: 1px dashed #2a2a2a;
  padding: 0.4rem 0;
}

.meta {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  font-size: 12px;
}

.reason {
  color: #8a9b9b;
  font-size: 12px;
}

.breach {
  border: 1px solid #5f0000;
  color: #ffd7d7;
  background: rgba(150, 0, 0, 0.35);
  padding: 0.8rem;
  font-family: monospace;
}

.map {
  position: relative;
  height: 260px;
  border: 1px solid #1f1f1f;
  background: radial-gradient(circle at 50% 50%, rgba(0, 255, 255, 0.06), transparent 60%), #060606;
  overflow: hidden;
}

.agent-dot {
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #00ffff;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 8px rgba(0, 255, 255, 0.8);
}

.agent-dot.dead {
  background: #444;
  box-shadow: none;
}

.agent-dot span {
  position: absolute;
  left: 10px;
  top: -6px;
  font-size: 10px;
  color: #8f9797;
  white-space: nowrap;
}

.compare {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0.8rem;
}

.compare pre {
  margin: 0;
  padding: 0.5rem;
  border: 1px solid #222;
  background: #060606;
  color: #b7c6c6;
  white-space: pre-wrap;
}

.semantic-overlay {
  border: 1px solid #222;
  background: #060606;
  padding: 0.5rem;
}

.semantic-overlay h4 {
  margin: 0 0 0.4rem;
}

.semantic-box {
  min-height: 120px;
  white-space: pre-wrap;
  line-height: 1.6;
  font-family: monospace;
}

.sem-stats {
  margin-top: 0.5rem;
  border-top: 1px dashed #243333;
  padding-top: 0.4rem;
}

.sem-stat-item {
  display: flex;
  justify-content: space-between;
  font-family: monospace;
  font-size: 12px;
  color: #9db1b1;
  padding: 0.1rem 0;
}

:deep(.sem-hit) {
  background: rgba(0, 180, 120, 0.35);
  color: #c8fff2;
}

:deep(.sem-hit-phrase) {
  background: rgba(0, 210, 130, 0.5);
  color: #ecfff8;
}

:deep(.sem-hit-char) {
  background: rgba(0, 120, 190, 0.35);
  color: #d9f2ff;
}

:deep(.sem-miss) {
  background: rgba(170, 20, 20, 0.2);
  color: #e6b3b3;
}

:deep(.sem-empty) {
  color: #7c8e8e;
}

.select {
  background: #0d0d0d;
  color: #d0d6d6;
  border: 1px solid #2d2d2d;
  height: 34px;
  padding: 0 0.4rem;
}

.heat {
  border: 1px solid #1f1f1f;
  padding: 0.6rem;
}

.infection-grid {
  display: grid;
  grid-template-columns: repeat(16, 1fr);
  gap: 4px;
}

.infection-cell {
  height: 10px;
  background: rgba(255, 40, 40, var(--cell-opacity));
  border: 1px solid #2b1a1a;
}

.curve-panel {
  border: 1px solid #1f1f1f;
  padding: 0.4rem;
  background: rgba(10, 10, 10, 0.4);
}

.curve-svg {
  width: 100%;
  height: 90px;
}

.curve-axis {
  stroke: #243333;
  stroke-width: 1;
}

.curve-line {
  fill: none;
  stroke: #ff5252;
  stroke-width: 2;
}

.curve-line-intensity {
  fill: none;
  stroke: #4fc3ff;
  stroke-width: 2;
}

.heat-item {
  display: grid;
  grid-template-columns: 26px 1fr 28px;
  align-items: center;
  gap: 0.6rem;
  margin: 0.25rem 0;
  font-family: monospace;
  font-size: 12px;
}

.bar {
  height: 8px;
  background: #101010;
  border: 1px solid #2b2b2b;
}

.bar i {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, #00ff41, #ff3333);
}

/* 下方展示与屏幕宽度自适应（见 docs/DEVELOPMENT-RULES.md） */
@media (max-width: 768px) {
  .zero-v2 {
    padding: 0.75rem 1rem;
  }

  .zero-v2-wrap {
    max-width: 100%;
  }


  .preset-grid {
    grid-template-columns: 1fr;
  }

  .real-goal-row,
  .directive-row {
    flex-direction: column;
  }

  .real-goal-row .n-input,
  .directive-row .n-input {
    width: 100%;
  }

  .intro-stats {
    flex-direction: column;
    align-items: flex-start;
  }

  .stat-goal {
    margin-left: 0;
  }

  .gauge-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }

  .directive-card-meta {
    flex-direction: column;
    align-items: flex-start;
  }

  .log-delta {
    margin-left: 0;
  }

  .game-frame {
    flex-direction: column;
    align-items: flex-start;
  }

  .game-frame-metrics {
    margin-left: 0;
  }


  .tale-cards {
    grid-template-columns: 1fr;
  }

  .tianming-compare {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .preset-grid {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  }

  .tale-cards {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  }
}
</style>
