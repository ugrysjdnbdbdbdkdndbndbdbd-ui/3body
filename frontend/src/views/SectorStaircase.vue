<script setup lang="ts">
/**
 * Sector S: The Staircase (阶梯计划)
 * 核心：轨道计算 (Trajectory), 童话解码 (Fairytales), 星星的礼物 (The Star)
 * 风格：手绘插画，忧伤浪漫
 */
import { ref, reactive, onUnmounted, computed, onMounted } from 'vue'
import { NTabs, NTabPane, useMessage, NInput, NButton, NProgress, NTag } from 'naive-ui'
import { encodeSecretAsFairytale, decodeFairytaleSimilarity } from '@/api/zero_v2'
import { loadVersionedState, saveVersionedState } from '@/composables/useZeroV2State'
import ModuleDiagPanel from '@/components/ModuleDiagPanel.vue'
import type { EncryptedFairytale } from '@/types/zero_v2'

const message = useMessage()
const activeTab = ref('trajectory')

// --- 1. Trajectory Calculation (Game) ---
const gameState = reactive({
  playing: false,
  position: 0, // 0-100%
  speed: 0,
  bombs: [10, 30, 50, 70, 90], // Bomb positions %
  activeBombIndex: 0,
  status: 'READY' // READY, FLYING, LOST, SUCCESS
})

let gameLoop: number
let pulseSeq = 0
const blastPulses = ref<Array<{ id: number; x: number; quality: 'perfect' | 'good' }>>([])
const speedHistory = ref<number[]>([])

const speedCurvePoints = computed(() => {
  const maxPoints = 80
  const maxSpeed = 3
  const width = 360
  const height = 100
  if (speedHistory.value.length === 0) return ''
  return speedHistory.value
    .slice(-maxPoints)
    .map((v, i, arr) => {
      const x = (i / Math.max(arr.length - 1, 1)) * width
      const normalized = Math.min(v / maxSpeed, 1)
      const y = height - normalized * height
      return `${x},${y}`
    })
    .join(' ')
})

function startGame() {
  if (gameState.playing) return
  gameState.playing = true
  gameState.position = 0
  gameState.speed = 0.2 // Initial drift
  gameState.activeBombIndex = 0
  gameState.status = 'FLYING'
  speedHistory.value = [gameState.speed]
  blastPulses.value = []
  loop()
}

function loop() {
  if (!gameState.playing) return
  
  gameState.position += gameState.speed
  
  // Friction/Gravity loss
  gameState.speed *= 0.99
  speedHistory.value.push(gameState.speed)
  if (speedHistory.value.length > 100) {
    speedHistory.value.shift()
  }
  
  // Check bounds
  if (gameState.position > 100) {
    if (gameState.speed > 1.5) {
      gameState.status = 'SUCCESS'
      message.success('达到光速的 1%！大脑成功入轨。')
    } else {
      gameState.status = 'LOST'
      message.error('速度不足，偏离航线。')
    }
    gameState.playing = false
    return
  }
  
  if (gameState.speed < 0.05 && gameState.position < 100) {
    gameState.status = 'LOST'
    message.error('动力丧失。任务失败。')
    gameState.playing = false
    return
  }
  
  gameLoop = requestAnimationFrame(loop)
}

function detonate() {
  if (!gameState.playing) return
  
  // Check proximity to active bomb
  const bombPos = gameState.bombs[gameState.activeBombIndex]
  if (bombPos === undefined) return
  
  const diff = Math.abs(gameState.position - bombPos)
  
  if (diff < 5) {
    // Perfect hit
    gameState.speed += 0.8
    const quality: 'perfect' | 'good' = diff < 2 ? 'perfect' : 'good'
    const pulse = { id: ++pulseSeq, x: bombPos, quality }
    blastPulses.value.push(pulse)
    setTimeout(() => {
      blastPulses.value = blastPulses.value.filter((p) => p.id !== pulse.id)
    }, 750)
    gameState.activeBombIndex++
    // Visual effect handled by CSS
  } else {
    // Miss or too early/late
    message.warning('引爆时机错误！')
    gameState.speed *= 0.8 // Penalty
  }
}

// --- 2. Fairytale Decoder (Interactive Puzzle) ---
interface Secret {
  text: string
  meaning: string
  solved: boolean
  id: string
}

interface StoryItem {
  title: string
  content: string
  secrets: Secret[]
}

interface Concept {
  id: string
  label: string
  desc: string
}

const concepts: Concept[] = [
  { id: '2D_FOIL', label: '二向箔 / 维度打击', desc: '将三维空间坍缩为二维' },
  { id: 'CURVATURE', label: '曲率驱动引擎', desc: '利用空间曲率差异进行光速航行' },
  { id: 'BLACK_DOMAIN', label: '低光速黑洞 / 黑域', desc: '光速降低至第三宇宙速度以下' },
  { id: 'ENTROPY', label: '熵增 / 资源消耗', desc: '生命对宇宙的消耗' },
  { id: 'LIGHTSPEED', label: '光速恒定', desc: '无论参考系如何，光速不变' },
  { id: 'DEEP_SEA', label: '深海状态 / 低温休眠', desc: '充满液体的保护性环境' }
]

const stories = reactive<StoryItem[]>([
  {
    title: "国王的新画师",
    content: `
      很久很久以前，在这个王国里，住着一个叫针眼画师的人。他的画技出神入化，但奇怪的是，他从来不画具体的东西，只画光影和透视。
      有一天，国王召见了他。国王说：“我听说你能把人画进画里，让他们永远活在纸上？”
      针眼画师点点头：“是的，陛下。我可以把人‘画’进去。在这个过程中，他们会变平，失去厚度，变成一张纸。但他们依然活着，不需要吃东西，不需要喝水，甚至不需要呼吸。他们将生活在二维的世界里，永远不老不死。”
      国王大喜：“这正是我想要的！把我也画进去吧，我要永生！”
      画师拿出了一张雪浪纸，这种纸来自于赫尔辛根默斯肯的深处，洁白无瑕，且永远不会卷曲。他举起那支来自黑曜石森林的笔，笔尖漆黑如夜。
      “陛下，一旦开始，就不能停下。”画师警告道，“而且，您将失去作为‘人’的所有立体感。”
      国王不在乎。于是，画师开始作画。他没有看国王，而是看着虚空。每一笔落下，国王就感觉自己的一部分“坍缩”了。先是他的皇冠，变成了一个金色的圆环；然后是他的身体，压扁成了一张扑克牌。
      周围的大臣们惊恐地看着，他们发现国王的声音变得尖锐而单薄，像是在纸面上摩擦。
      最后，画师收笔了。王座上空空如也，只有一张纸飘落下来。纸上画着一个神气活现的国王，色彩鲜艳，栩栩如生。
      “他现在安全了。”画师说，“只要这张纸不被烧毁，他就永远存在。但他再也无法回到我们的世界，因为对于他来说，并没有‘高度’这个概念。”
      这便是针眼画师的秘密：他不是在画画，而是在进行降维。他把三维的人，封印在了二维的牢笼里。
    `,
    secrets: [
      { text: "针眼画师", meaning: "二向箔 / 降维打击执行者", id: '2D_FOIL', solved: false },
      { text: "变平", meaning: "三维向二维跌落", id: '2D_FOIL', solved: false },
      { text: "不需要吃东西", meaning: "低熵体 / 资源消耗极低", id: 'ENTROPY', solved: false },
      { text: "雪浪纸", meaning: "二维空间 / 平面宇宙", id: '2D_FOIL', solved: false },
      { text: "永远不老不死", meaning: "时间冻结 / 相对论效应", id: 'LIGHTSPEED', solved: false }
    ]
  },
  {
    title: "饕餮海",
    content: `
      深水王子住在一个叫“饕餮海”的地方。但这海里没有水，只有一种奇怪的粘稠液体。
      这种液体非常沉重，如果你跳进去，不会溅起水花，而是像石头砸进泥潭一样。
      这片海最奇怪的地方在于它的“透视”。在我们的世界里，远处的船看起来很小，近处的船看起来很大。但在饕餮海，无论船开多远，它看起来都一样大。
      这就意味着，在饕餮海，光线是不直的，或者是这里没有透视规律。
      有一天，公主来到了海边。她看到深水王子站在海面上，没有倒影。
      “为什么你没有倒影？”公主问。
      王子笑了：“因为这里的光不会反射。这里是饕餮海，它吞噬一切，包括光。”
      如果是这样，那这里应该是一片漆黑才对。但奇怪的是，海面散发着幽幽的蓝光。
      王子解释说：“我们生活在一个‘慢’的世界里。在这里，光走得很慢，就像蜗牛在爬。既然光走得慢，那一切看起来就都不一样了。”
      因为光速慢，所以这里的“因果”也变慢了。你打一个人一拳，他可能要过很久才会感觉到痛。
      这片海是安全的，也是绝望的。它是宇宙中的一个低光速黑洞，一旦进去，就再也出不来。因为它就是所谓的“黑域”。
    `,
    secrets: [
      { text: "看起来都一样大", meaning: "无透视 / 光速恒定", id: 'LIGHTSPEED', solved: false },
      { text: "吞噬一切", meaning: "黑洞 / 事件视界", id: 'BLACK_DOMAIN', solved: false },
      { text: "没有倒影", meaning: "全反射 / 光无法逃逸", id: 'BLACK_DOMAIN', solved: false },
      { text: "光走得很慢", meaning: "低光速陷阱 / 黑域", id: 'BLACK_DOMAIN', solved: false },
      { text: "安全的", meaning: "黑域声明 / 宇宙安全声明", id: 'BLACK_DOMAIN', solved: false }
    ]
  },
  {
    title: "深水王子",
    content: `
      深水王子虽然长相英俊，但他无法在这个世界久留。因为他不属于这里，他属于深海。
      为了去见公主，他必须经过漫长的旅行。但他不想变老。
      于是，赫尔辛根默斯肯教了他一个办法：让自己沉睡。
      “你必须让自己变得像石头一样冷，像死人一样静。”默斯肯说，“只有这样，时间才会把你遗忘。”
      王子照做了。他躺进了一个充满了特殊液体的水晶棺材里。这种液体能穿透他的皮肤，充满他的肺部，替换他的血液。
      他在液体中沉睡了千万年。当他醒来时，世界已经变了，但他依然年轻。
      后来，王子要带公主逃离这个即将毁灭的王国。但他们的船太慢了，无法逃脱饕餮鱼的追捕。
      默斯肯给了他们一块神奇的肥皂。
      “把它放在船尾。”默斯肯说，“它能减小水的张力。”
      王子把肥皂扔在船尾的水里。奇迹发生了，船尾的水不再拉扯船身，而船头的水依然在拉扯。于是，船像箭一样飞了出去，速度快得惊人，甚至快到了看不见影子的地步。
      这便是曲率驱动的秘密：通过改变空间（水）的曲率（张力），让空间自己推着飞船前进。
    `,
    secrets: [
      { text: "沉睡", meaning: "冬眠技术", id: 'DEEP_SEA', solved: false },
      { text: "特殊液体", meaning: "深海加速液 / 液体呼吸", id: 'DEEP_SEA', solved: false },
      { text: "肥皂", meaning: "曲率驱动引擎 / 空间曲率", id: 'CURVATURE', solved: false },
      { text: "水的张力", meaning: "空间结构 / 空间曲率", id: 'CURVATURE', solved: false },
      { text: "快到了看不见影子", meaning: "光速航行", id: 'LIGHTSPEED', solved: false }
    ]
  }
])

const activeStoryIndex = ref(0)
const selectedSecret = ref<{ sIndex: number, text: string } | null>(null)
const showConceptModal = ref(false)
const popoverPos = ref({ x: 0, y: 0 })

function selectSecret(sIndex: number, event: MouseEvent) {
  const story = stories[activeStoryIndex.value]
  const secret = story.secrets[sIndex]
  if (secret.solved) return
  
  const target = event.target as HTMLElement
  const rect = target.getBoundingClientRect()
  
  // Calculate position relative to viewport (since popover is fixed)
  popoverPos.value = {
    x: rect.left,
    y: rect.bottom + 10
  }
  
  selectedSecret.value = { sIndex, text: secret.text }
  showConceptModal.value = true
}

function matchConcept(conceptId: string) {
  if (!selectedSecret.value) return
  const story = stories[activeStoryIndex.value]
  const secret = story.secrets[selectedSecret.value.sIndex]
  if (secret.id === conceptId) {
    secret.solved = true
    message.success('解码成功！隐喻已破解。')
    showConceptModal.value = false
    selectedSecret.value = null
  } else {
    message.error('解码错误。该概念不符合隐喻逻辑。')
  }
}

function getStorySegments(story: StoryItem) {
  const text = story.content
  const segments: { text: string, type: 'text' | 'secret', sIndex?: number, solved?: boolean }[] = []

  const matches: { start: number, end: number, sIndex: number }[] = []
  story.secrets.forEach((s, i) => {
    const idx = text.indexOf(s.text)
    if (idx !== -1) {
      matches.push({ start: idx, end: idx + s.text.length, sIndex: i })
    }
  })
  matches.sort((a, b) => a.start - b.start)

  let cursor = 0
  matches.forEach((m) => {
    if (m.start > cursor) {
      segments.push({ text: text.slice(cursor, m.start), type: 'text' })
    }
    segments.push({
      text: text.slice(m.start, m.end),
      type: 'secret',
      sIndex: m.sIndex,
      solved: story.secrets[m.sIndex].solved
    })
    cursor = m.end
  })
  if (cursor < text.length) {
    segments.push({ text: text.slice(cursor), type: 'text' })
  }
  return segments
}

// --- 3. The Star (DX3906) ---
const starGiven = ref(false)

function giveStar() {
  starGiven.value = true
  message.success('星星已送出。愿你拥有属于自己的光芒。')
}

// --- C. 云天明隐喻加密局（合并自三体体验沙盒）---
const LOCAL_FAIRYTALES = 'zero_v2_fairytales'
const secretText = ref('')
const taleTitle = ref('')
const fairytales = ref<EncryptedFairytale[]>([])
const decodeTargetId = ref<number | null>(null)
const decodeInput = ref('')
const decodeScore = ref<number | null>(null)
const cLoading = ref(false)
type TaskDiag = { status: 'IDLE' | 'RUNNING' | 'SUCCESS' | 'ERROR'; durationMs: number; updatedAt: string; error: string }
type DiagHistoryItem = { at: string; status: 'SUCCESS' | 'ERROR'; durationMs: number; error?: string }
function createDiag(): TaskDiag {
  return { status: 'IDLE', durationMs: 0, updatedAt: '-', error: '' }
}
const diagC = ref<TaskDiag>(createDiag())
const diagHistC = ref<DiagHistoryItem[]>([])
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
const FAIRYTALE_SECRET_PRESETS = [
  '不要回答。',
  '藏好自己，做好清理。',
  '给岁月以文明，给时光以生命。',
  '失去人性，失去很多；失去兽性，失去一切。',
  '我选择人性。',
  '我们度过了幸福的一生。',
]
const DECODE_HINT_PRESETS = ['坐标', '暴露', '不要回答', '文明', '藏好', '清理', '岁月', '生命', '人性', '兽性']
const tianmingStats = computed(() => {
  const count = fairytales.value.length
  const maxProgress = fairytales.value.length ? Math.max(...fairytales.value.map((t) => t.decodeProgress)) : 0
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
    pushDiagHistory(diagHistC.value, { at: diagC.value.updatedAt, status: 'SUCCESS', durationMs: diagC.value.durationMs })
  } catch (err) {
    markError(diagC.value, t0, err)
    pushDiagHistory(diagHistC.value, { at: diagC.value.updatedAt, status: 'ERROR', durationMs: diagC.value.durationMs, error: diagC.value.error })
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
    pushDiagHistory(diagHistC.value, { at: diagC.value.updatedAt, status: 'SUCCESS', durationMs: diagC.value.durationMs })
  } catch (err) {
    markError(diagC.value, t0, err)
    pushDiagHistory(diagHistC.value, { at: diagC.value.updatedAt, status: 'ERROR', durationMs: diagC.value.durationMs, error: diagC.value.error })
    message.error('语义解密失败。')
  } finally {
    cLoading.value = false
  }
}
const decodeTarget = computed(() => fairytales.value.find((f) => f.id === decodeTargetId.value) ?? null)
function escapeHtml(text: string): string {
  return text.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#039;')
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

onMounted(() => {
  fairytales.value = loadVersionedState<EncryptedFairytale[]>(LOCAL_FAIRYTALES, [])
})

onUnmounted(() => {
  cancelAnimationFrame(gameLoop)
})

</script>

<template>
  <div class="sector-s">
    <header class="header">
      <h1 class="title">SECTOR S // THE STAIRCASE</h1>
      <div class="subtitle">阶梯计划与云天明的童话</div>
    </header>

    <NTabs type="segment" v-model:value="activeTab" class="s-tabs">
      
      <!-- Tab 1: Trajectory -->
      <NTabPane name="trajectory" tab="轨道计算 (TRAJECTORY)">
        <div class="game-container">
          <div class="track">
            <!-- Sail/Brain Capsule -->
            <div 
              class="sail-capsule" 
              :style="{ left: `${gameState.position}%` }"
            >
              <div class="capsule-body">
                <div class="brain-matter"></div>
                <div class="glass-shield"></div>
              </div>
              <div class="radiation-sail"></div>
              <div class="engine-exhaust" v-if="gameState.speed > 0.5"></div>
            </div>
            
            <!-- Predicted Path -->
            <div class="trajectory-line"></div>
            
            <!-- Bombs -->
            <div 
              v-for="(pos, i) in gameState.bombs" 
              :key="i"
              class="bomb-wrapper"
              :style="{ left: `${pos}%` }"
            >
              <div 
                class="bomb-zone" 
                :class="{ active: i === gameState.activeBombIndex }"
              ></div>
              <div 
                class="bomb-icon"
                :class="{ active: i === gameState.activeBombIndex, used: i < gameState.activeBombIndex }"
              >
                ☢️
              </div>
            </div>

            <div
              v-for="pulse in blastPulses"
              :key="pulse.id"
              class="blast-pulse"
              :class="pulse.quality"
              :style="{ left: `${pulse.x}%` }"
            ></div>
          </div>
          
          <div class="controls">
            <div class="status-panel">
              <p>SPEED: {{ (gameState.speed * 10).toFixed(1) }}% c</p>
              <p>STATUS: {{ gameState.status }}</p>
            </div>
            <button 
              class="detonate-btn" 
              @mousedown="detonate"
              :disabled="!gameState.playing || gameState.status !== 'FLYING'"
            >
              DETONATE (引爆)
            </button>
            <button class="start-btn" @click="startGame" v-if="!gameState.playing">
              {{ gameState.status === 'READY' ? 'LAUNCH' : 'RETRY' }}
            </button>
          </div>
          <div class="speed-hud">
            <div class="speed-hud-title">速度曲线 HUD / VELOCITY TRACE</div>
            <svg viewBox="0 0 360 100" class="speed-chart">
              <polyline
                class="speed-line"
                fill="none"
                :points="speedCurvePoints"
              />
            </svg>
            <div class="speed-hud-scale">
              <span>0.0c</span>
              <span>1.5c</span>
              <span>3.0c</span>
            </div>
          </div>
          <p class="hint">当辐射帆经过核弹时点击引爆，加速至光速的 1%。</p>
        </div>
      </NTabPane>

      <!-- Tab 2: Fairytales -->
      <NTabPane name="fairytales" tab="童话解码 (DECODER)">
        <div class="decoder-layout">
          <!-- Story Selection -->
          <div class="story-nav">
             <div 
               v-for="(story, i) in stories" 
               :key="i"
               class="story-tab"
               :class="{ active: activeStoryIndex === i }"
               @click="activeStoryIndex = i"
             >
               {{ story.title }}
             </div>
          </div>

          <!-- Active Story Reader -->
          <div class="book-reader">
            <div class="book-page">
              <h3>{{ stories[activeStoryIndex].title }}</h3>
              <p class="story-text-interactive">
                <template v-for="(seg, j) in getStorySegments(stories[activeStoryIndex])" :key="j">
                  <span v-if="seg.type === 'text'">{{ seg.text }}</span>
                  <span 
                    v-else 
                    class="secret-word" 
                    :class="{ solved: seg.solved, active: selectedSecret?.sIndex === seg.sIndex && showConceptModal }"
                    @click="selectSecret(seg.sIndex!, $event)"
                  >
                    {{ seg.text }}
                    <span v-if="seg.solved" class="meaning-tooltip">{{ stories[activeStoryIndex].secrets[seg.sIndex!].meaning }}</span>
                  </span>
                </template>
              </p>
            </div>
          </div>

          <!-- Clue Sidebar -->
          <div class="clue-sidebar">
            <h4>待解密线索 (CLUES)</h4>
            <div class="clue-list">
              <div 
                v-for="(secret, k) in stories[activeStoryIndex].secrets" 
                :key="k"
                class="clue-item"
                :class="{ solved: secret.solved }"
              >
                <div class="clue-text">{{ secret.text }}</div>
                <div class="clue-status">
                  <span v-if="secret.solved" class="status-solved">✓ {{ secret.meaning }}</span>
                  <span v-else class="status-pending">???</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Popover Concept Selector -->
        <div 
          v-if="showConceptModal" 
          class="concept-popover"
          :style="{ top: popoverPos.y + 'px', left: popoverPos.x + 'px' }"
        >
          <div class="popover-header">
            <span>解码: "{{ selectedSecret?.text }}"</span>
            <button class="close-btn" @click="showConceptModal = false">×</button>
          </div>
          <div class="popover-body">
            <div 
              v-for="c in concepts" 
              :key="c.id" 
              class="popover-option"
              @click="matchConcept(c.id)"
            >
              {{ c.label }}
            </div>
          </div>
        </div>
      </NTabPane>

      <!-- C. 云天明隐喻加密局（合并自三体体验沙盒） -->
      <NTabPane name="tianming" tab="云天明隐喻加密局">
        <div class="panel tianming-panel">
          <div class="tianming-intro">
            <span class="intro-title">玩法说明</span>
            <p>将<strong>机密</strong>写成童话发布到公海，他人通过<strong>语义拆解</strong>尝试解密。解密进度达 <strong>80%</strong> 即执剑人候补。已发布 <strong>{{ tianmingStats.count }}</strong> 则童话 · 当前最高进度 <strong>{{ tianmingStats.maxProgress }}%</strong><NTag v-if="tianmingStats.isCandidate" size="small" type="success" class="ml-1">执剑人候补</NTag></p>
          </div>
          <div class="tianming-section">
            <span class="section-label">发布童话（机密 → 寓言）</span>
            <div class="preset-chip-row">
              <button v-for="(s, i) in FAIRYTALE_SECRET_PRESETS" :key="i" type="button" class="tianming-chip" @click="fillSecretPreset(s)">{{ s }}</button>
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
              <button v-for="t in fairytales" :key="t.id" type="button" class="tale-card" :class="{ selected: decodeTargetId === t.id }" @click="decodeTargetId = t.id">
                <span class="tale-card-title">{{ t.title }}</span>
                <span class="tale-card-meta reason">{{ t.createdAt }}</span>
                <NProgress type="line" :percentage="t.decodeProgress" :height="6" :show-indicator="false" class="tale-progress" />
                <span class="tale-card-pct">{{ t.decodeProgress }}%</span>
              </button>
            </div>
          </div>
          <div class="tianming-section">
            <span class="section-label">语义解密（选择童话后拆解）</span>
            <div class="preset-chip-row">
              <button v-for="(w, i) in DECODE_HINT_PRESETS" :key="i" type="button" class="tianming-chip small" :disabled="!decodeTargetId" @click="appendDecodeHint(w)">{{ w }}</button>
            </div>
            <div class="row decode-row">
              <NInput v-model:value="decodeInput" type="textarea" :rows="2" placeholder="输入你的语义拆解，或从上方点击追加关键词" :disabled="!decodeTargetId" />
              <NButton ghost type="warning" @click="decodeFairytale" :loading="cLoading" :disabled="!decodeTargetId || !decodeInput.trim()">执行解密</NButton>
            </div>
            <NProgress v-if="decodeScore !== null" type="line" :percentage="decodeScore" :color="decodeScore >= 80 ? '#00cc88' : '#ffcc00'" />
            <NTag v-if="decodeScore !== null && decodeScore >= 80" type="success" class="decode-badge">执剑人候补：已达 80%</NTag>
          </div>
          <ModuleDiagPanel module-key="C" :status="diagC.status" :duration-ms="diagC.durationMs" :updated-at="diagC.updatedAt" :error="diagC.error" :history="diagHistC" />
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

      <!-- Tab 3: The Star -->
      <NTabPane name="star" tab="星星的礼物 (THE STAR)">
        <div class="star-view">
          <div class="star-view-bg">
            <div class="starfield"></div>
            <div class="star-view-gradient"></div>
          </div>
          <div class="star-content">
            <div class="telescope" :class="{ gifted: starGiven }">
              <div class="telescope-ring"></div>
              <div class="star-dx3906" :class="{ owned: starGiven }">
                <div class="star-core"></div>
                <div class="star-rays"></div>
                <div class="star-corona" v-if="starGiven"></div>
              </div>
              <div class="planet blue" v-if="starGiven">🌍</div>
              <div class="planet gray" v-if="starGiven">🌑</div>
              <div class="star-dust" v-for="i in 12" :key="i" :style="{ '--i': i }"></div>
            </div>

            <div class="star-info">
              <p class="star-label">286.5 光年外的约定</p>
              <h2 class="star-name">DX3906</h2>
              <p class="star-meta">视星等 11.2 · 红矮星</p>
              <p class="star-owner">
                <span v-if="!starGiven">尚未赠出</span>
                <span v-else class="owner-name">程心 (Cheng Xin)</span>
              </p>
              <button class="gift-btn" @click="giveStar" :disabled="starGiven" :class="{ sent: starGiven }">
                <span v-if="!starGiven">送出这颗星</span>
                <span v-else>已赠出</span>
              </button>
              <div class="quote-block" v-if="starGiven">
                <p class="quote">「我送给你一颗星星。」</p>
                <p class="quote reply">「那我们就去那里吧。」</p>
                <p class="quote-ref">—— 云天明 · 程心</p>
              </div>
            </div>
          </div>
        </div>
      </NTabPane>

    </NTabs>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Noto+Serif+SC:wght@400;700&display=swap');

.sector-s {
  min-height: 0;
  background: #0f0f1a;
  color: #d8d8ff;
  font-family: 'Noto Serif SC', serif;
  display: flex;
  flex-direction: column;
}

.header {
  padding: 1rem 2rem;
  border-bottom: 1px solid #333355;
  background: #151525;
}

.title {
  margin: 0;
  font-family: 'Dancing Script', cursive;
  letter-spacing: 2px;
  color: #fff;
}

.s-tabs {
  flex: 1;
}

/* Trajectory */
.game-container {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 3rem;
  align-items: center;
}

.track {
  width: 100%;
  height: 100px;
  border-bottom: 2px solid #555;
  position: relative;
  margin-top: 50px;
}

.blast-pulse {
  position: absolute;
  bottom: -28px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  transform: translateX(-50%);
  border: 2px solid #ff6666;
  box-shadow: 0 0 16px rgba(255, 80, 80, 0.7);
  animation: pulse-ring 0.75s ease-out forwards;
}

.blast-pulse.perfect {
  border-color: #ffd54f;
  box-shadow: 0 0 20px rgba(255, 213, 79, 0.85);
}

.sail-capsule {
  position: absolute;
  bottom: 10px;
  transform: translateX(-50%);
  transition: none; 
  z-index: 10;
}

.capsule-body {
  width: 20px;
  height: 20px;
  background: rgba(200, 230, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  position: relative;
  overflow: hidden;
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}

.brain-matter {
  position: absolute;
  top: 50%; left: 50%;
  width: 12px; height: 12px;
  background: #ffb7b2;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  box-shadow: inset 0 0 5px rgba(0,0,0,0.2);
}

.radiation-sail {
  position: absolute;
  bottom: 22px;
  left: 50%;
  width: 60px;
  height: 60px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 50% 50% 0 0;
  transform: translateX(-50%) rotate(45deg);
  background: linear-gradient(135deg, rgba(255,255,255,0.1), transparent);
  box-shadow: 0 0 15px rgba(255, 255, 255, 0.2);
}

.engine-exhaust {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 20px;
  background: linear-gradient(to bottom, #00ffff, transparent);
  opacity: 0.7;
  filter: blur(2px);
}

.trajectory-line {
  position: absolute;
  bottom: 20px;
  left: 0;
  width: 100%;
  height: 1px;
  background: repeating-linear-gradient(90deg, #444, #444 5px, transparent 5px, transparent 10px);
  z-index: 0;
}

.bomb-wrapper {
  position: absolute;
  bottom: 0;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  display: flex;
  justify-content: center;
  align-items: center;
}

.bomb-zone {
  position: absolute;
  bottom: -20px;
  width: 10vw; /* Approx 10% of viewport width, close enough to track width */
  max-width: 100px;
  height: 60px;
  border: 1px dashed rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  pointer-events: none;
}
.bomb-zone.active {
  border-color: rgba(255, 50, 50, 0.5);
  background: rgba(255, 50, 50, 0.05);
}

.bomb-icon {
  position: absolute;
  bottom: -15px;
  font-size: 1.5rem;
  transform: translateX(-50%);
  opacity: 0.5;
  transition: all 0.3s;
}
.bomb-icon.active { opacity: 1; transform: translateX(-50%) scale(1.2); color: #ff3333; }
.bomb-icon.used { opacity: 0.2; transform: translateX(-50%) scale(0.8); }

.controls {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.speed-hud {
  width: 380px;
  padding: 0.75rem;
  border: 1px solid #3c3c60;
  background: rgba(8, 10, 30, 0.7);
  box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.4);
}

.speed-hud-title {
  font-family: monospace;
  font-size: 0.75rem;
  color: #9fc2ff;
  margin-bottom: 0.35rem;
}

.speed-chart {
  width: 100%;
  height: 100px;
  background: linear-gradient(180deg, rgba(35, 50, 90, 0.2), rgba(10, 15, 35, 0.35));
  border: 1px solid rgba(120, 150, 220, 0.4);
}

.speed-line {
  stroke: #6ce3ff;
  stroke-width: 2;
  filter: drop-shadow(0 0 4px rgba(108, 227, 255, 0.7));
}

.speed-hud-scale {
  display: flex;
  justify-content: space-between;
  font-family: monospace;
  font-size: 0.7rem;
  color: #8f95c9;
  margin-top: 0.25rem;
}

.detonate-btn {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: #ff3333;
  color: #fff;
  font-weight: bold;
  border: 4px solid #aa0000;
  cursor: pointer;
  box-shadow: 0 0 20px rgba(255,0,0,0.3);
}
.detonate-btn:active:not(:disabled) { transform: scale(0.95); }
.detonate-btn:disabled { background: #553333; cursor: not-allowed; }

.start-btn {
  padding: 0.5rem 2rem;
  background: #fff;
  color: #000;
  border: none;
  cursor: pointer;
}

/* Fairytales Decoder */
.decoder-layout {
  display: flex;
  gap: 0;
  height: 650px;
  background: #f4f1ea;
  border: 1px solid #d4d4d4;
  color: #2c3e50;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.story-nav {
  width: 220px;
  background: #e8e4da;
  border-right: 1px solid #d4d4d4;
  padding: 1rem;
  overflow-y: auto;
}

.story-tab {
  padding: 0.8rem 1rem;
  margin-bottom: 0.5rem;
  cursor: pointer;
  border-radius: 4px;
  border: 1px solid transparent;
  font-family: 'Noto Serif SC', serif;
  transition: all 0.2s;
  background: rgba(255,255,255,0.3);
}

.story-tab:hover {
  background: rgba(255,255,255,0.6);
  border-color: #bbb;
}

.story-tab.active {
  background: #fff;
  border-left: 4px solid #d35400;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  font-weight: bold;
}

.book-reader {
  flex: 1;
  background: #fdfbf7;
  padding: 2rem;
  box-shadow: 5px 5px 15px rgba(0,0,0,0.1);
  overflow-y: auto;
  position: relative;
}

.clue-sidebar {
  width: 250px;
  border-left: 1px solid #ccc;
  padding-left: 1rem;
  display: flex;
  flex-direction: column;
}

.clue-sidebar h4 {
  margin: 0 0 1rem 0;
  font-size: 0.9rem;
  color: #666;
  border-bottom: 1px solid #ddd;
  padding-bottom: 0.5rem;
}

.clue-list {
  flex: 1;
  overflow-y: auto;
}

.clue-item {
  padding: 0.8rem;
  margin-bottom: 0.8rem;
  background: rgba(255,255,255,0.5);
  border: 1px dashed #ccc;
  border-radius: 4px;
}

.clue-item.solved {
  border-color: #28a745;
  background: rgba(40, 167, 69, 0.1);
}

.clue-text { font-weight: bold; font-size: 0.9rem; margin-bottom: 0.3rem; }
.clue-status { font-size: 0.8rem; }
.status-solved { color: #155724; }
.status-pending { color: #999; }

.story-text-interactive {
  font-size: 1.2rem;
  line-height: 2;
  font-family: 'Noto Serif SC', serif;
}

.secret-word {
  border-bottom: 2px dashed #999;
  cursor: pointer;
  padding: 0 2px;
  transition: all 0.2s;
  background: rgba(255,255,0,0.1);
}

.secret-word:hover, .secret-word.active {
  background: rgba(255,255,0,0.3);
  color: #d35400;
}

.secret-word.solved {
  border-bottom: 2px solid #28a745;
  color: #155724;
  background: transparent;
  font-weight: bold;
}

/* Popover */
.concept-popover {
  position: fixed;
  z-index: 2000;
  background: #222;
  border: 1px solid #444;
  box-shadow: 0 5px 20px rgba(0,0,0,0.5);
  border-radius: 4px;
  width: 280px;
  color: #eee;
  transform: translateY(5px);
}

.popover-header {
  padding: 0.5rem 0.8rem;
  background: #333;
  border-bottom: 1px solid #444;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  color: #aaa;
}

.close-btn {
  background: none; border: none; color: #aaa; cursor: pointer; font-size: 1.2rem; line-height: 1;
}

.popover-body {
  padding: 0.5rem;
  max-height: 300px;
  overflow-y: auto;
}

.popover-option {
  padding: 0.6rem;
  cursor: pointer;
  border-bottom: 1px solid #333;
  font-size: 0.9rem;
  transition: all 0.2s;
}
.popover-option:last-child { border-bottom: none; }
.popover-option:hover { background: #00ffff; color: #000; }

/* Star — 星星的礼物（浪漫版） */
.star-view {
  position: relative;
  min-height: 420px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.star-view-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.starfield {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(1.5px 1.5px at 20% 30%, rgba(255,255,255,0.4), transparent),
    radial-gradient(1.5px 1.5px at 60% 70%, rgba(255,255,255,0.35), transparent),
    radial-gradient(1px 1px at 80% 20%, rgba(255,255,255,0.5), transparent),
    radial-gradient(1px 1px at 40% 80%, rgba(255,255,255,0.3), transparent),
    radial-gradient(2px 2px at 90% 50%, rgba(255,255,255,0.25), transparent);
  background-size: 200% 200%, 180% 180%, 220% 220%, 160% 160%, 190% 190%;
  animation: starfield-drift 20s ease-in-out infinite;
  opacity: 0.9;
}

.star-view-gradient {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 80% 60% at 50% 50%, rgba(80, 60, 120, 0.25), transparent 60%),
    linear-gradient(180deg, rgba(15, 15, 26, 0.6) 0%, rgba(30, 25, 50, 0.4) 50%, rgba(15, 15, 26, 0.8) 100%);
}

@keyframes starfield-drift {
  0%, 100% { background-position: 0% 0%, 10% 10%, 5% 5%, 15% 0%, 0% 15%; }
  50% { background-position: 20% 20%, 0% 0%, 25% 10%, 5% 20%, 20% 5%; }
}

.star-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4rem;
  padding: 2rem;
  flex-wrap: wrap;
}

.telescope {
  width: 280px;
  height: 280px;
  background: radial-gradient(circle at 50% 50%, #0a0a14 0%, #000 70%);
  border-radius: 50%;
  border: 1px solid rgba(255, 220, 180, 0.15);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 0 80px rgba(0, 0, 0, 0.8), 0 0 60px rgba(80, 60, 120, 0.15);
  transition: box-shadow 0.6s ease, border-color 0.6s ease;
}

.telescope.gifted {
  border-color: rgba(255, 220, 180, 0.35);
  box-shadow: inset 0 0 80px rgba(0, 0, 0, 0.6), 0 0 80px rgba(180, 160, 255, 0.2);
}

.telescope-ring {
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  border: 1px solid transparent;
  background: linear-gradient(135deg, rgba(255,220,180,0.2), transparent 40%, transparent 60%, rgba(200,180,255,0.2)) border-box;
  mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  mask-composite: exclude;
  -webkit-mask-composite: xor;
  padding: 1px;
  opacity: 0.8;
}

.star-dx3906 {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.star-core {
  width: 14px;
  height: 14px;
  background: #fff;
  border-radius: 50%;
  box-shadow: 0 0 20px #fff, 0 0 40px rgba(255, 255, 255, 0.5);
  animation: star-breathe 4s ease-in-out infinite;
}

.owned .star-core {
  background: linear-gradient(135deg, #ffeaa7, #fdcb6e);
  box-shadow: 0 0 25px #fdcb6e, 0 0 50px rgba(253, 203, 110, 0.4);
  animation: star-breathe 3s ease-in-out infinite;
}

@keyframes star-breathe {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.08); opacity: 0.92; }
}

.star-rays {
  position: absolute;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: radial-gradient(circle at 50% 50%, rgba(255,255,255,0.15) 0%, transparent 70%);
  animation: star-rays-pulse 5s ease-in-out infinite;
}

.owned .star-rays {
  width: 90px;
  height: 90px;
  background: radial-gradient(circle at 50% 50%, rgba(253, 203, 110, 0.2) 0%, transparent 65%);
  animation: star-rays-pulse 4s ease-in-out infinite;
}

@keyframes star-rays-pulse {
  0%, 100% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.15); opacity: 1; }
}

.star-corona {
  position: absolute;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: radial-gradient(circle at 50% 50%, transparent 30%, rgba(253, 203, 110, 0.06) 60%, transparent 70%);
  animation: corona-glow 6s ease-in-out infinite;
}

@keyframes corona-glow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.1); opacity: 1; }
}

.star-dust {
  position: absolute;
  width: 2px;
  height: 2px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: rotate(calc(var(--i) * 30deg)) translateY(-100px);
  animation: dust-twinkle 3s ease-in-out infinite;
  animation-delay: calc(var(--i) * -0.15s);
}

@keyframes dust-twinkle {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.8; }
}

.planet {
  position: absolute;
  font-size: 1.1rem;
  filter: drop-shadow(0 0 6px rgba(255, 255, 255, 0.3));
  animation: orbit 8s linear infinite;
}
.planet.blue { top: 45px; left: 45px; animation-duration: 6s; }
.planet.gray { top: -35px; left: -35px; animation-duration: 10s; }

@keyframes orbit {
  from { transform: rotate(0deg) translateX(75px) rotate(0deg); }
  to { transform: rotate(360deg) translateX(75px) rotate(-360deg); }
}

.star-info {
  max-width: 320px;
  text-align: center;
}

.star-label {
  font-size: 0.85rem;
  letter-spacing: 0.2em;
  color: rgba(255, 220, 200, 0.85);
  margin-bottom: 0.5rem;
  font-family: 'Noto Serif SC', serif;
}

.star-name {
  font-family: 'Dancing Script', cursive;
  font-size: 2.5rem;
  color: #fff;
  margin: 0 0 0.25rem;
  letter-spacing: 0.1em;
  text-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
}

.star-meta {
  font-size: 0.9rem;
  color: rgba(200, 190, 220, 0.8);
  margin: 0 0 0.75rem;
}

.star-owner {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 1.25rem;
}

.owner-name {
  color: #fdcb6e;
  font-weight: 600;
}

.gift-btn {
  padding: 0.9rem 2rem;
  background: transparent;
  border: 1px solid rgba(255, 220, 180, 0.5);
  color: rgba(255, 240, 220, 0.95);
  cursor: pointer;
  font-size: 1rem;
  letter-spacing: 0.15em;
  font-family: 'Noto Serif SC', serif;
  transition: all 0.4s ease;
  border-radius: 2px;
}

.gift-btn:hover:not(:disabled) {
  background: rgba(255, 220, 180, 0.15);
  border-color: rgba(255, 220, 180, 0.8);
  color: #fff;
  box-shadow: 0 0 24px rgba(255, 220, 180, 0.2);
}

.gift-btn.sent {
  border-color: rgba(253, 203, 110, 0.4);
  color: rgba(253, 203, 110, 0.9);
  cursor: default;
}

.quote-block {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 220, 180, 0.2);
  animation: quote-fade 1s ease-out;
}

@keyframes quote-fade {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.quote {
  font-style: italic;
  font-family: 'Dancing Script', cursive;
  font-size: 1.35rem;
  color: rgba(255, 240, 220, 0.95);
  margin: 0.5rem 0;
  line-height: 1.5;
}

.quote.reply {
  color: rgba(200, 220, 255, 0.9);
  margin-left: 1rem;
}

.quote-ref {
  font-size: 0.8rem;
  color: rgba(180, 170, 200, 0.7);
  margin-top: 0.75rem;
  font-style: normal;
}

@keyframes pulse-ring {
  0% {
    opacity: 1;
    transform: translateX(-50%) scale(0.4);
  }
  100% {
    opacity: 0;
    transform: translateX(-50%) scale(3.8);
  }
}

/* C. 云天明隐喻加密局（合并自三体体验沙盒） */
.tianming-panel {
  border: 1px solid #252525;
  background: rgba(0, 0, 0, 0.4);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  color: #d0d6d6;
}
.tianming-intro {
  padding: 0.5rem 0.6rem;
  border: 1px solid #25363a;
  background: rgba(0, 25, 30, 0.2);
  border-radius: 4px;
}
.tianming-intro .intro-title { font-size: 0.75rem; color: #7a9a9a; text-transform: uppercase; letter-spacing: 0.08em; margin-right: 0.5rem; }
.tianming-intro p { margin: 0.3rem 0 0; font-size: 0.85rem; color: #a8c0c0; line-height: 1.5; }
.ml-1 { margin-left: 0.35rem; }
.tianming-section { margin-top: 0.8rem; }
.section-label { display: block; font-size: 0.7rem; color: #6a8585; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.4rem; }
.tianming-panel .reason { font-size: 0.8rem; color: #7a9a9a; }
.preset-chip-row { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.tianming-chip {
  appearance: none;
  border: 1px solid #2a4040;
  background: rgba(0, 25, 30, 0.4);
  color: #b8d0d0;
  padding: 0.4rem 0.6rem;
  font-size: 0.8rem;
  border-radius: 6px;
  cursor: pointer;
}
.tianming-chip:hover:not(:disabled) { border-color: #3a6060; background: rgba(0, 40, 50, 0.5); }
.tianming-chip.small { padding: 0.25rem 0.5rem; font-size: 0.75rem; }
.tianming-chip:disabled { opacity: 0.5; cursor: not-allowed; }
.publish-row, .decode-row { display: flex; flex-direction: column; gap: 0.5rem; }
.publish-row .title-input { max-width: 280px; }
.empty-tales { padding: 0.6rem; font-size: 0.85rem; }
.tale-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 0.5rem; }
.tale-card {
  appearance: none;
  border: 1px solid #25363a;
  background: rgba(0, 20, 28, 0.35);
  color: #b8d0d0;
  padding: 0.5rem 0.7rem;
  border-radius: 6px;
  cursor: pointer;
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.tale-card:hover { border-color: #3a6060; background: rgba(0, 35, 45, 0.45); }
.tale-card.selected { border-color: #00d4ff; background: rgba(0, 60, 80, 0.25); box-shadow: 0 0 0 1px rgba(0, 212, 255, 0.3); }
.tale-card-title { font-size: 0.9rem; font-weight: 600; color: #c8e0e0; }
.tale-card-meta { font-size: 0.7rem; }
.tale-progress { margin-top: 0.25rem; }
.tale-card-pct { font-size: 0.75rem; color: #8ab3b3; }
.decode-badge { margin-top: 0.4rem; }
.tianming-compare { margin-top: 1rem; display: flex; flex-direction: column; gap: 0.8rem; }
.compare-block { min-width: 0; }
.compare-pre { margin: 0; padding: 0.5rem; border: 1px solid #222; background: #060606; color: #b7c6c6; white-space: pre-wrap; font-size: 0.85rem; max-height: 200px; overflow: auto; }
.semantic-box { padding: 0.5rem; border: 1px solid #222; background: #060606; color: #b7c6c6; font-size: 0.85rem; }
.sem-empty { color: #666; }
.sem-hit-phrase { color: #00ff88; background: rgba(0, 255, 136, 0.15); }
.sem-hit-char { color: #88ff88; }
.sem-miss { color: #555; }
.sem-stats { margin-top: 0.5rem; }
.sem-stat-item { display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 0.2rem; }

:deep(.n-tabs-nav) { background: #151525; }
:deep(.n-tabs-tab) { color: #8888aa; }
:deep(.n-tabs-tab--active) { color: #fff; font-weight: bold; }
</style>
