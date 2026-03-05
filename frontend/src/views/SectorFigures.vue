<script setup lang="ts">
/**
 * 扇区 E：人物志 (Sector Figures)
 * 档案风格展示三体关键人物：关键决策、关键语录、人物关系图谱
 * 子模块：档案列表 | 关系星图（Constellation Network）
 */
import { ref, onMounted, computed, nextTick } from 'vue'
import { NModal, NProgress, NTimeline, NTimelineItem, NInput, NButton, NCheckbox, NCollapse, NCollapseItem, NFormItem } from 'naive-ui'
import { API, apiUrl } from '@/constants'
import type { Figure, KeyDecision, FigureRelationship, KeyQuote } from '@/types/figures'
import FiguresNetworkGraph from '@/components/FiguresNetworkGraph.vue'
import { figureImageUrl } from '@/utils/imageFallback'
import { hasDialogue, getDialogueSet } from '@/data/figureDialogues'
import { useLlmConfigStore } from '@/stores/llmConfig'
import { streamFigureChat } from '@/api/figureChat'

const figures = ref<Figure[]>([])
const loading = ref(true)
const selectedFigure = ref<Figure | null>(null)
const searchQuery = ref('')
/** 选择式对话：是否显示对话模态 */
const showDialogueModal = ref(false)
/** 对话消息列表：user / figure，统一为实时对话（预埋问题仅作引导，回复均由 AI 生成） */
const conversation = ref<{ role: 'user' | 'figure'; content: string }[]>([])
const dialogueLoading = ref(false)
const dialogueError = ref('')
const dialogueInput = ref('')
/** 滚动到底部的 ref，用于对话列表 */
const dialogueListRef = ref<HTMLElement | null>(null)
const llmConfig = useLlmConfigStore()
/** 子模块：'list' 档案列表 | 'graph' 关系星图 */
const subModule = ref<'list' | 'graph'>('list')

function parseJson<T = unknown>(str: string | null | undefined): T | null {
  if (!str) return null
  try {
    return JSON.parse(str) as T
  } catch {
    return null
  }
}

// Helper to handle mixed JSON string or Object
function getParsed<T>(data: string | object | null | undefined): T[] {
  if (!data) return []
  if (typeof data === 'string') {
    const parsed = parseJson<T[]>(data)
    return Array.isArray(parsed) ? parsed : []
  }
  return Array.isArray(data) ? data as T[] : []
}

function keyDecisions(f: Figure): KeyDecision[] {
  return getParsed<KeyDecision>(f.key_decisions)
}

function relationships(f: Figure): FigureRelationship[] {
  return getParsed<FigureRelationship>(f.relationships)
}

function keyQuotes(f: Figure): KeyQuote[] {
  return getParsed<KeyQuote>(f.key_quotes)
}

interface KeyEventItem {
  role?: string
  impact_description?: string
}
function keyEvents(f: Figure): KeyEventItem[] {
  return getParsed<KeyEventItem>(f.key_events)
}

function metricsEntries(f: Figure): [string, number][] {
  let o: Record<string, number> | null = null
  if (typeof f.metrics === 'string') {
    o = parseJson<Record<string, number>>(f.metrics)
  } else if (f.metrics && typeof f.metrics === 'object') {
    o = f.metrics as Record<string, number>
  }
  if (!o) return []
  return Object.entries(o)
}

async function loadFigures() {
  loading.value = true
  try {
    const res = await fetch(apiUrl(API.FIGURES_LIST))
    if (!res.ok) throw new Error()
    figures.value = await res.json()
  } catch (e) {
    console.error(e)
    // Fallback Data
    figures.value = [
      {
        id: 1,
        name: '罗辑',
        en_name: 'Luo Ji',
        role: '面壁者 / 执剑人',
        era: '危机纪元 - 威慑纪元',
        image_url: '',
        status: 'Active',
        logic_score: 98,
        description: '第四位面壁者，宇宙社会学公理的发现者。通过向宇宙发射咒语验证了黑暗森林理论。建立了对三体世界的黑暗森林威慑，执剑54年。',
        key_decisions: JSON.stringify([
          { decision: '向宇宙发射恒星咒语', context: '危机纪元', outcome: '验证了黑暗森林法则' },
          { decision: '建立引力波威慑', context: '末日之战后', outcome: '迫使三体舰队转向' }
        ]),
        relationships: JSON.stringify([
          { target: '庄颜', relation_type: '爱人', description: '虽然是虚构的具象化，但成为了罗辑最深的羁绊' },
          { target: '大史', relation_type: '守护者', description: '多次拯救罗辑于危难之中' }
        ]),
        key_quotes: JSON.stringify([
          { quote: '这是计划的一部分。', context: '面对质疑时' },
          { quote: '我对三体世界说话。', context: '威慑建立时刻' }
        ]),
        metrics: JSON.stringify({ empathy: 40, logic: 95, determination: 90 }),
      },
      {
        id: 2,
        name: '叶文洁',
        en_name: 'Ye Wenjie',
        role: 'ETO 统帅 / 天体物理学家',
        era: '黄金时代之前',
        image_url: '',
        status: 'Deceased',
        logic_score: 92,
        description: '红岸基地核心技术人员。因对人类人性的绝望，向三体世界发送了太阳系坐标，不仅是ETO的精神领袖，也是人类苦难的开启者。',
        key_decisions: JSON.stringify([
          { decision: '回答三体信号', context: '红岸基地', outcome: '暴露地球坐标' },
          { decision: '向罗辑传授宇宙社会学', context: '杨冬墓前', outcome: '启蒙了面壁者' }
        ]),
        key_quotes: JSON.stringify([
          { quote: '到这里来吧，我将帮助你们获得这个世界。', context: '第一次回复' },
          { quote: '这是人类的落日。', context: '晚年' }
        ]),
        metrics: JSON.stringify({ empathy: 20, logic: 90, determination: 95 }),
      },
      {
        id: 3,
        name: '章北海',
        en_name: 'Zhang Beihai',
        role: '太空军政治部主任 / 自然选择号舰长',
        era: '危机纪元',
        image_url: '',
        status: 'Deceased',
        logic_score: 99,
        description: '最坚定的逃亡主义者，却伪装成最坚定的胜利主义者。为了人类文明的存续，他不惜暗杀异见者，并在最后时刻劫持战舰逃离太阳系，为人类保留了火种。',
        key_decisions: JSON.stringify([
          { decision: '暗杀老航天', context: '陨石雨行动', outcome: '确立了无工质辐射推进的研究方向' },
          { decision: '劫持自然选择号', context: '水滴到达前夕', outcome: '人类文明分支幸存' }
        ]),
        key_quotes: JSON.stringify([
          { quote: '没关系的，都一样。', context: '临死前' },
          { quote: '自然选择，前进四！', context: '逃亡时刻' }
        ]),
        metrics: JSON.stringify({ empathy: 10, logic: 100, determination: 100 }),
      },
      {
        id: 4,
        name: '托马斯·维德',
        en_name: 'Thomas Wade',
        role: 'PIA 局长 / 阶梯计划负责人',
        era: '危机纪元 - 掩体纪元',
        image_url: '',
        status: 'Deceased',
        logic_score: 100,
        description: '极端理性的化身。为了前进，他不择手段。他只差一点就成为了执剑人，也只差一点就让光速飞船提前几十年诞生。他的名言“失去兽性，失去一切”是对那个时代最深刻的警示。',
        key_decisions: JSON.stringify([
          { decision: '提出阶梯计划', context: '只送一个大脑', outcome: '云天明打入三体内部' },
          { decision: '向程心交出光速飞船控制权', context: '星环城', outcome: '遵守诺言，但也导致了人类灭亡' }
        ]),
        key_quotes: JSON.stringify([
          { quote: '前进！前进！！不择手段地前进！！！', context: '座右铭' },
          { quote: '你会把他卖给妓院吗？', context: '对程心说' }
        ]),
        metrics: JSON.stringify({ empathy: 0, logic: 100, determination: 100 }),
      },
      {
        id: 5,
        name: '史强',
        en_name: 'Da Shi',
        role: '前市局反恐大队队长 / 地球防务安全部',
        era: '危机纪元',
        image_url: '',
        status: 'Deceased',
        logic_score: 85,
        description: '看似粗鲁、大大咧咧，实则粗中有细，拥有敏锐的直觉和极高的情商。他是汪淼和罗辑最可靠的守护者，在最黑暗的时刻，是他点醒了绝望的科学家们。',
        key_decisions: JSON.stringify([
          { decision: '提出古筝行动', context: '针对审判日号', outcome: '获取三体信息' },
          { decision: '带罗辑去看虫子', context: '大低谷时期', outcome: '重塑了罗辑的信心' }
        ]),
        key_quotes: JSON.stringify([
          { quote: '虫子从来没有被真正战胜过。', context: '麦田宣言' },
          { quote: '邪乎到家必有鬼。', context: '办案经验' }
        ]),
        metrics: JSON.stringify({ empathy: 90, logic: 80, determination: 90 }),
      }
    ]
  } finally {
    loading.value = false
  }
}

// 筛选
const filterRole = ref<string>('all')
const filteredFigures = computed(() => {
  let list = figures.value

  // Search filter
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(f => 
      f.name.toLowerCase().includes(q) || 
      (f.en_name && f.en_name.toLowerCase().includes(q))
    )
  }

  if (filterRole.value === 'all') return list
  
  if (filterRole.value === '科学家') {
    return list.filter(f => 
      f.role.includes('科学家') || 
      f.role.includes('物理') || 
      f.role.includes('数学') || 
      f.role.includes('学者') ||
      f.role.includes('教授')
    )
  }
  
  if (filterRole.value === '军方/ETO') {
    return list.filter(f => 
      f.role.includes('太空军') || 
      f.role.includes('ETO') || 
      f.role.includes('警官') || 
      f.role.includes('舰长') ||
      f.role.includes('降临派') ||
      f.role.includes('地球防务')
    )
  }

  // 精确或部分匹配
  return list.filter(f => f.role.includes(filterRole.value))
})

// 样式映射
const statusColor = (status: string) => {
  const s = status.toLowerCase()
  if (s === 'active' || s === 'alive') return 'success'
  if (s === 'hibernating') return 'info'
  if (s === 'deceased') return 'error'
  return 'default'
}

/** 威胁度展示：后端可能为 0–1 或 0–100 */
function displayLogicScore(f: Figure): number {
  const v = Number(f.logic_score)
  if (v <= 1 && v > 0) return Math.round(v * 100)
  return Math.min(100, Math.round(v))
}

/** 详情弹窗头像 URL：优先 API/本地 /images/figures，空时用占位 */
function figurePortraitUrl(f: Figure | null): string {
  if (!f) return ''
  const url = figureImageUrl(f.image_url, f.en_name, `https://placehold.co/300x400/111/444?text=${encodeURIComponent(f.name)}`)
  return url || `https://placehold.co/300x400/111/444?text=${encodeURIComponent(f.name)}`
}

/** 打开与当前人物的选择式对话 */
function openDialogue() {
  if (!selectedFigure.value || !hasDialogue(selectedFigure.value.name)) return
  conversation.value = []
  dialogueError.value = ''
  dialogueInput.value = ''
  showDialogueModal.value = true
}

function closeDialogue() {
  showDialogueModal.value = false
}

/** 将当前对话转为 API 所需的 history（user -> user，figure -> assistant） */
function conversationToHistory(): { role: 'user' | 'assistant'; content: string }[] {
  return conversation.value.map((m) => ({
    role: m.role === 'user' ? 'user' : 'assistant',
    content: m.content,
  }))
}

/** 发送一条用户消息并请求人物回复（流式追加到 conversation） */
async function sendMessage(userText: string) {
  const fig = selectedFigure.value
  const set = fig ? getDialogueSet(fig.name) : null
  if (!fig || !set || !userText.trim()) return
  dialogueError.value = ''
  const history = conversationToHistory()
  conversation.value.push({ role: 'user', content: userText.trim() })
  scrollDialogueToBottom()
  const figureMsg = { role: 'figure' as const, content: '' }
  conversation.value.push(figureMsg)
  dialogueLoading.value = true
  const payload = {
    figure_name: fig.name,
    figure_role: fig.role || undefined,
    figure_description: fig.description || undefined,
    message: userText.trim(),
    history: history.length ? history : undefined,
    ...llmConfig.requestOverrides,
  }
  await streamFigureChat(
    payload,
    (chunk) => {
      figureMsg.content += chunk
      scrollDialogueToBottom()
    },
    (err) => { dialogueError.value = err }
  )
  dialogueLoading.value = false
  scrollDialogueToBottom()
}

/** 点击推荐问题（预埋问题作引导） */
function onSuggestedQuestion(question: string) {
  sendMessage(question)
}

/** 提交输入框内容并清空 */
function submitInput() {
  const text = dialogueInput.value.trim()
  if (!text || dialogueLoading.value) return
  dialogueInput.value = ''
  sendMessage(text)
}

function scrollDialogueToBottom() {
  nextTick(() => {
    const el = dialogueListRef.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

/** 对话按钮文案：与她/与他 */
const dialogueEntryLabel = computed(() => {
  const name = selectedFigure.value?.name
  if (!name) return '与他对话'
  const femaleNames = ['叶文洁', '程心', '智子 (仿生人)']
  return femaleNames.includes(name) ? '与她对话' : '与他对话'
})

onMounted(() => {
  loadFigures()
  llmConfig.init()
})
</script>

<template>
  <div class="sector-figures">
    <div class="bg-grid"></div>
    <header class="header">
      <div class="header-left">
        <h1 class="title">HUMANITY_DOSSIER // 人物志</h1>
        <div class="subtitle">PDC 绝密档案库</div>
      </div>

      <!-- 子模块切换：档案列表 | 关系星图 -->
      <div class="sub-module-tabs">
        <button
          type="button"
          class="sub-tab"
          :class="{ active: subModule === 'list' }"
          @click="subModule = 'list'"
        >
          <span class="sub-tab-icon">📁</span>
          <span>档案列表</span>
        </button>
        <button
          type="button"
          class="sub-tab"
          :class="{ active: subModule === 'graph' }"
          @click="subModule = 'graph'"
        >
          <span class="sub-tab-icon">◇</span>
          <span>关系星图</span>
        </button>
      </div>
      
      <div class="header-right">
        <div class="search-box">
          <NInput 
            v-model:value="searchQuery" 
            placeholder="SEARCH RECORDS..." 
            class="tech-input"
            clearable
          >
            <template #prefix>🔍</template>
          </NInput>
        </div>
        <div v-if="subModule === 'list'" class="filters">
          <span 
            v-for="role in ['all', '面壁者', '执剑人', '科学家', '军方/ETO']" 
            :key="role"
            class="filter-tag"
            :class="{ active: filterRole === role }"
            @click="filterRole = role"
          >
            {{ role === 'all' ? 'ALL RECORDS' : role.toUpperCase() }}
          </span>
        </div>
      </div>
    </header>

    <!-- 加载态 -->
    <div v-if="loading" class="loading-state">
      <span class="loading-text">智子正在同步档案…</span>
    </div>
    <!-- 空状态 -->
    <div v-else-if="subModule === 'list' && filteredFigures.length === 0" class="empty-state">
      <div class="empty-icon">📁</div>
      <h2>暂无档案记录</h2>
      <p>智子档案库未同步或当前筛选无匹配人物。请检查后端服务或切换筛选条件。</p>
    </div>

    <!-- 关系星图子模块 -->
    <div v-else-if="subModule === 'graph'" class="graph-module">
      <FiguresNetworkGraph
        :figures="figures"
        @select="selectedFigure = $event"
      />
    </div>

    <div v-else class="grid-container">
      <transition-group name="list">
        <div 
          v-for="f in filteredFigures" 
          :key="f.id" 
          class="figure-card"
          @click="selectedFigure = f"
        >
          <div class="card-img">
            <img :src="figureImageUrl(f.image_url, f.en_name, `https://placehold.co/300x400/111/444?text=${encodeURIComponent(f.name)}`)" alt="Portrait" />
            <div class="status-indicator" :class="f.status.toLowerCase()"></div>
            <div class="logic-score-badge">
              THREAT LEVEL: {{ displayLogicScore(f) }}
            </div>
            <div class="scan-line"></div>
          </div>
          <div class="card-info">
            <div class="name-row">
              <span class="cn-name">{{ f.name }}</span>
              <span class="en-name">{{ f.en_name }}</span>
            </div>
            <div class="meta-row">
              <span class="role-tag">{{ f.role }}</span>
              <span class="era-tag">{{ f.era }}</span>
            </div>
          </div>
          <div class="card-decor">
            <span class="corner tl"></span>
            <span class="corner tr"></span>
            <span class="corner bl"></span>
            <span class="corner br"></span>
          </div>
        </div>
      </transition-group>
    </div>

    <!-- 详情档案 -->
    <NModal
      :show="!!selectedFigure"
      @update:show="(v) => { if (!v) selectedFigure = null }"
      preset="card"
      class="dossier-modal"
      style="width: 800px; max-width: 95vw;"
      :title="`CLASSIFIED FILE #${selectedFigure?.id.toString().padStart(4, '0')}`"
    >
      <div v-if="selectedFigure" class="dossier-content">
        <!-- Watermark -->
        <div class="watermark">TOP SECRET</div>

        <div class="dossier-layout">
          <!-- Left Column: Portrait & Stats -->
          <div class="col-left">
            <div class="portrait-wrapper">
              <img :src="figurePortraitUrl(selectedFigure)" alt="" class="portrait-img" />
              <div class="portrait-overlay">
                <div class="status-badge" :class="selectedFigure.status.toLowerCase()">
                  {{ selectedFigure.status.toUpperCase() }}
                </div>
              </div>
            </div>

            <div class="basic-info">
              <h2 class="cn-name-lg">{{ selectedFigure.name }}</h2>
              <p class="en-name-lg">{{ selectedFigure.en_name }}</p>
              
              <div class="info-grid">
                <div class="info-item">
                  <label>ROLE</label>
                  <span>{{ selectedFigure.role }}</span>
                </div>
                <div class="info-item">
                  <label>ERA</label>
                  <span>{{ selectedFigure.era }}</span>
                </div>
                <div class="info-item">
                  <label>THREAT</label>
                  <span class="text-red-500 font-bold">{{ displayLogicScore(selectedFigure) }}/100</span>
                </div>
              </div>
            </div>

            <!-- 与他/与她对话：核心人物主入口，置于左侧显著位置 -->
            <div v-if="hasDialogue(selectedFigure.name)" class="dossier-dialogue-cta">
              <button type="button" class="dialogue-cta-btn" @click="openDialogue">
                <span class="dialogue-cta-icon">💬</span>
                <span class="dialogue-cta-text">{{ dialogueEntryLabel }}</span>
                <span class="dialogue-cta-sub">选择问题或输入提问，与 TA 实时对话</span>
              </button>
            </div>

            <div class="dossier-section">
              <h3 class="section-title">人格光谱 (Personality)</h3>
              <div v-if="metricsEntries(selectedFigure).length" class="metrics-list">
                <div class="metric-row" v-for="([key, val]) in metricsEntries(selectedFigure)" :key="key">
                  <span class="metric-name">{{ key.toUpperCase() }}</span>
                  <div class="metric-bar-container">
                    <div 
                      class="metric-bar" 
                      :style="{ width: `${val}%`, backgroundColor: key === 'empathy' ? '#ff3333' : '#00ffff' }"
                    ></div>
                  </div>
                  <span class="metric-val">{{ val }}</span>
                </div>
              </div>
              <p v-else class="text-xs text-gray-500">NO DATA AVAILABLE</p>
            </div>
          </div>

          <!-- Right Column: Details -->
          <div class="col-right">
            
            <div class="dossier-section">
              <h3 class="section-title">履历摘要 (Summary)</h3>
              <p class="desc-text">{{ selectedFigure.description }}</p>
            </div>

            <div v-if="keyQuotes(selectedFigure).length || selectedFigure.quotes" class="dossier-section">
              <h3 class="section-title">语录 (Quotes)</h3>
              <template v-if="keyQuotes(selectedFigure).length">
                <div v-for="(q, i) in keyQuotes(selectedFigure)" :key="i" class="quote-block">
                  <p class="quote-text">"{{ q.quote }}"</p>
                  <p class="quote-meta">— {{ q.context }}</p>
                </div>
              </template>
              <div v-else class="quote-block">
                <p class="quote-text">"{{ selectedFigure.quotes }}"</p>
              </div>
            </div>

            <div v-if="keyDecisions(selectedFigure).length" class="dossier-section">
              <h3 class="section-title">关键决策 (Key Decisions)</h3>
              <div class="timeline-simple">
                <div v-for="(d, i) in keyDecisions(selectedFigure)" :key="i" class="timeline-event">
                  <div class="timeline-dot"></div>
                  <div class="timeline-content">
                    <div class="decision-name">{{ d.decision }}</div>
                    <div class="decision-ctx">{{ d.context }}</div>
                    <div class="decision-res">➔ {{ d.outcome }}</div>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="relationships(selectedFigure).length" class="dossier-section">
              <h3 class="section-title">关系网络 (Network)</h3>
              <div class="network-grid">
                <div v-for="(r, i) in relationships(selectedFigure)" :key="i" class="network-card">
                  <div class="rel-header">
                    <span class="rel-target">{{ r.target }}</span>
                    <span class="rel-type">{{ r.relation_type }}</span>
                  </div>
                  <div class="rel-desc">{{ r.description }}</div>
                </div>
              </div>
            </div>

          </div>
        </div>

      </div>
    </NModal>

    <!-- 选择式对话模态：对话式气泡，预埋问题作引导，回复统一为人物 AI -->
    <NModal
      :show="showDialogueModal"
      @update:show="(v) => { if (!v) closeDialogue() }"
      preset="card"
      class="dialogue-modal"
      style="width: 620px; max-width: 95vw;"
      :title="selectedFigure && getDialogueSet(selectedFigure.name) ? `与 ${selectedFigure.name} 对话` : ''"
    >
      <template v-if="selectedFigure && getDialogueSet(selectedFigure.name)">
        <div class="dialogue-content">
          <header class="dialogue-header">
            <span class="dialogue-header-name">{{ selectedFigure.name }}</span>
            <span class="dialogue-header-role">{{ selectedFigure.role }}</span>
            <p v-if="getDialogueSet(selectedFigure.name)!.intro" class="dialogue-intro">
              {{ getDialogueSet(selectedFigure.name)!.intro }}
            </p>
          </header>

          <div ref="dialogueListRef" class="dialogue-messages">
            <template v-for="(msg, idx) in conversation" :key="idx">
              <div v-if="msg.role === 'user'" class="dialogue-row dialogue-row-user">
                <div class="dialogue-bubble dialogue-bubble-user">{{ msg.content }}</div>
              </div>
              <div v-else class="dialogue-row dialogue-row-figure">
                <div class="dialogue-bubble dialogue-bubble-figure">
                  <span class="dialogue-figure-name">{{ selectedFigure.name }}</span>
                  <span class="dialogue-bubble-text">{{ msg.content }}</span>
                  <span v-if="dialogueLoading && idx === conversation.length - 1" class="dialogue-cursor">|</span>
                </div>
              </div>
            </template>
            <p v-if="dialogueError" class="dialogue-err-inline">{{ dialogueError }}</p>
          </div>

          <div class="dialogue-suggested">
            <span class="dialogue-suggested-label">可问：</span>
            <div class="dialogue-suggested-chips">
              <button
                v-for="(item, idx) in getDialogueSet(selectedFigure.name)!.qa"
                :key="idx"
                type="button"
                class="dialogue-chip"
                :disabled="dialogueLoading"
                @click="onSuggestedQuestion(item.question)"
              >
                {{ item.question }}
              </button>
            </div>
          </div>

          <div class="dialogue-input-row">
            <NInput
              v-model:value="dialogueInput"
              type="text"
              placeholder="输入你想问的…"
              clearable
              :disabled="dialogueLoading"
              class="dialogue-input"
              @keydown.enter.prevent="submitInput"
            />
            <NButton
              type="primary"
              :disabled="!dialogueInput.trim() || dialogueLoading"
              @click="submitInput"
            >
              发送
            </NButton>
          </div>

          <NCollapse class="dialogue-llm-config" :default-expanded-names="[]">
            <NCollapseItem title="⚙️ API / Ollama 连接设置" name="llm">
              <p class="dialogue-llm-hint">不填则使用本地 Ollama（http://localhost:11434）；填写 Key 或自定义地址则走云端/自定义端点。</p>
              <NCheckbox :checked="llmConfig.useLocalOllama" @update:checked="(v: boolean) => llmConfig.setUseLocalOllama(v)">
                使用本地 Ollama
              </NCheckbox>
              <NFormItem label="API Key（可选）" class="dialogue-llm-item">
                <NInput
                  :value="llmConfig.apiKey"
                  type="password"
                  placeholder="留空则用本地"
                  show-password-on="click"
                  @update:value="(v: string) => llmConfig.setApiKey(v)"
                />
              </NFormItem>
              <NFormItem label="Base URL（可选）" class="dialogue-llm-item">
                <NInput
                  :value="llmConfig.baseUrl"
                  placeholder="如 https://api.openai.com/v1"
                  @update:value="(v: string) => llmConfig.setBaseUrl(v)"
                />
              </NFormItem>
              <NFormItem label="Model（可选）" class="dialogue-llm-item">
                <NInput
                  :value="llmConfig.model"
                  placeholder="如 gpt-4、deepseek-chat"
                  @update:value="(v: string) => llmConfig.setModel(v)"
                />
              </NFormItem>
            </NCollapseItem>
          </NCollapse>
        </div>
      </template>
    </NModal>
  </div>
</template>

<style scoped>
.sector-figures {
  min-height: 0;
  padding: 2rem;
  background: #050505;
  color: #c0c0c0;
  position: relative;
  font-family: 'Noto Serif SC', serif;
}
.bg-grid {
  position: fixed;
  inset: 0;
  background: 
    linear-gradient(rgba(0,255,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,255,255,0.03) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
}

/* Header */
.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-bottom: 2px solid rgba(0,255,255,0.2);
  padding-bottom: 1.5rem;
  margin-bottom: 2rem;
  position: relative;
  z-index: 1;
}
.header-left {
  flex-shrink: 0;
}
.title {
  font-family: 'Russo One', sans-serif; /* Tech font */
  color: #00ffff;
  font-size: 2rem;
  letter-spacing: 2px;
  margin: 0;
  text-shadow: 0 0 10px rgba(0,255,255,0.3);
}
.subtitle {
  color: #666;
  font-family: monospace;
  margin-top: 0.5rem;
  letter-spacing: 1px;
}

.sub-module-tabs {
  display: flex;
  gap: 0;
  border: 1px solid rgba(0, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  bottom: -2px;
}
.sub-tab {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  font-family: monospace;
  font-size: 0.8rem;
  color: #888;
  background: rgba(0, 0, 0, 0.5);
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  border-right: 1px solid rgba(0, 255, 255, 0.15);
}
.sub-tab:last-child {
  border-right: none;
}
.sub-tab:hover {
  color: #00ffff;
  background: rgba(0, 255, 255, 0.08);
}
.sub-tab.active {
  color: #00ffff;
  background: rgba(0, 255, 255, 0.15);
  box-shadow: inset 0 0 12px rgba(0, 255, 255, 0.1);
}
.sub-tab-icon {
  opacity: 0.9;
}

.graph-module {
  position: relative;
  z-index: 1;
  width: 100%;
  height: calc(100vh - 220px);
  min-height: 520px;
}

.header-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 1rem;
}
.search-box {
  width: 250px;
}
.tech-input :deep(.n-input__input-el) {
  font-family: monospace;
}

.filters {
  display: flex;
  gap: 0.5rem;
}
.filter-tag {
  cursor: pointer;
  font-family: monospace;
  font-size: 0.75rem;
  padding: 4px 10px;
  border: 1px solid rgba(255,255,255,0.2);
  color: #888;
  transition: all 0.2s;
  background: rgba(0,0,0,0.5);
}
.filter-tag:hover, .filter-tag.active {
  border-color: #00ffff;
  color: #00ffff;
  background: rgba(0,255,255,0.1);
  box-shadow: 0 0 10px rgba(0,255,255,0.1);
}

/* Grid */
/* Loading state */
.loading-state {
  padding: 4rem 2rem;
  text-align: center;
  position: relative;
  z-index: 1;
}
.loading-text {
  font-family: monospace;
  color: #00ffff;
  font-size: 0.95rem;
  animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
  50% { opacity: 0.5; }
}

/* Empty state */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  position: relative;
  z-index: 1;
  border: 1px dashed rgba(0,255,255,0.2);
  background: rgba(0,255,255,0.02);
  border-radius: 4px;
}
.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}
.empty-state h2 {
  color: #00ffff;
  font-family: monospace;
  font-size: 1.2rem;
  margin: 0 0 0.5rem;
}
.empty-state p {
  color: #888;
  font-size: 0.9rem;
  max-width: 400px;
  margin: 0 auto;
  line-height: 1.6;
}

.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 2rem;
  position: relative;
  z-index: 1;
}

.figure-card {
  background: rgba(10, 15, 20, 0.8);
  border: 1px solid rgba(0, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(5px);
}
.figure-card:hover {
  transform: translateY(-5px);
  border-color: #00ffff;
  box-shadow: 0 5px 20px rgba(0, 255, 255, 0.15);
}

.card-decor .corner {
  position: absolute;
  width: 6px;
  height: 6px;
  border: 2px solid transparent;
  transition: border-color 0.3s;
}
.figure-card:hover .corner { border-color: #00ffff; }
.tl { top: -1px; left: -1px; border-top: 2px solid rgba(0,255,255,0.3); border-left: 2px solid rgba(0,255,255,0.3); }
.tr { top: -1px; right: -1px; border-top: 2px solid rgba(0,255,255,0.3); border-right: 2px solid rgba(0,255,255,0.3); }
.bl { bottom: -1px; left: -1px; border-bottom: 2px solid rgba(0,255,255,0.3); border-left: 2px solid rgba(0,255,255,0.3); }
.br { bottom: -1px; right: -1px; border-bottom: 2px solid rgba(0,255,255,0.3); border-right: 2px solid rgba(0,255,255,0.3); }

.card-img {
  height: 280px;
  position: relative;
  overflow: hidden;
  border-bottom: 1px solid rgba(0,255,255,0.1);
}
.card-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(1) contrast(1.2);
  transition: filter 0.4s;
}
.figure-card:hover .card-img img {
  filter: grayscale(0) contrast(1.1);
}

.status-indicator {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  box-shadow: 0 0 8px currentColor;
  z-index: 2;
}
.status-indicator.active, .status-indicator.alive { background: #00ff41; color: #00ff41; }
.status-indicator.hibernating { background: #00ffff; color: #00ffff; }
.status-indicator.deceased { background: #ff3333; color: #ff3333; }

.logic-score-badge {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0,0,0,0.8);
  color: #00ffff;
  font-family: monospace;
  font-size: 0.7rem;
  padding: 4px 8px;
  text-align: right;
  border-top: 1px solid rgba(0,255,255,0.2);
}

.scan-line {
  position: absolute;
  top: 0; left: 0; right: 0; height: 2px;
  background: rgba(0,255,255,0.5);
  box-shadow: 0 0 10px rgba(0,255,255,0.8);
  opacity: 0;
  pointer-events: none;
}
.figure-card:hover .scan-line {
  animation: scan 1.5s linear infinite;
  opacity: 1;
}
@keyframes scan {
  0% { top: 0; opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { top: 100%; opacity: 0; }
}

.card-info {
  padding: 1rem;
}
.name-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 0.5rem;
}
.cn-name { font-weight: bold; color: #fff; font-size: 1.1rem; }
.en-name { font-size: 0.7rem; font-family: monospace; opacity: 0.6; }

.meta-row { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.role-tag, .era-tag {
  font-size: 0.7rem;
  padding: 2px 6px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  color: #ccc;
}
.role-tag { color: #00ffff; border-color: rgba(0,255,255,0.2); }

/* List Transition */
.list-enter-active, .list-leave-active { transition: all 0.3s ease; }
.list-enter-from, .list-leave-to { opacity: 0; transform: scale(0.9); }

/* Dossier Modal */
.dossier-modal :deep(.n-card) {
  background: #0f1215;
  border: 1px solid #333;
}
.dossier-modal :deep(.n-card-header) {
  border-bottom: 1px solid #333;
  padding-bottom: 1rem;
}
.dossier-modal :deep(.n-card-header__main) {
  color: #00ffff;
  font-family: monospace;
}

.dossier-content {
  position: relative;
}
.watermark {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(-30deg);
  font-size: 6rem;
  font-weight: bold;
  color: rgba(255, 50, 50, 0.05);
  pointer-events: none;
  z-index: 0;
  white-space: nowrap;
}

.dossier-layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 2rem;
  position: relative;
  z-index: 1;
}

.col-left {
  border-right: 1px solid #222;
  padding-right: 2rem;
}

.portrait-wrapper {
  position: relative;
  margin-bottom: 1.5rem;
  border: 1px solid #444;
  overflow: hidden;
}
.portrait-img {
  width: 100%;
  display: block;
  min-height: 280px;
  object-fit: cover;
  background: #111;
}
.status-badge {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  text-align: center;
  font-family: monospace;
  font-weight: bold;
  font-size: 0.9rem;
  padding: 4px;
  background: rgba(0,0,0,0.8);
}
.status-badge.alive, .status-badge.active { color: #00ff41; border-top: 2px solid #00ff41; }
.status-badge.hibernating { color: #00ffff; border-top: 2px solid #00ffff; }
.status-badge.deceased { color: #ff3333; border-top: 2px solid #ff3333; }

.basic-info { margin-bottom: 2rem; }
.cn-name-lg { font-size: 2rem; color: #fff; margin: 0; line-height: 1.2; }
.en-name-lg { font-family: monospace; color: #666; font-size: 0.9rem; margin: 0 0 1rem; }

.info-grid { display: flex; flex-direction: column; gap: 0.5rem; }
.info-item { display: flex; justify-content: space-between; font-family: monospace; font-size: 0.8rem; border-bottom: 1px dashed #333; padding-bottom: 4px; }
.info-item label { color: #666; }
.info-item span { color: #ccc; text-align: right; }

.section-title {
  font-family: monospace;
  color: #00ffff;
  font-size: 0.9rem;
  border-bottom: 1px solid #333;
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
  text-transform: uppercase;
}

.metrics-list { display: flex; flex-direction: column; gap: 0.5rem; }
.metric-row { display: flex; align-items: center; gap: 0.5rem; font-family: monospace; font-size: 0.7rem; }
.metric-name { width: 60px; color: #888; }
.metric-bar-container { flex: 1; height: 4px; background: #222; }
.metric-bar { height: 100%; }
.metric-val { width: 30px; text-align: right; color: #fff; }

/* Right Column */
.desc-text {
  font-size: 0.95rem;
  line-height: 1.7;
  color: #ddd;
  margin-bottom: 2rem;
  text-align: justify;
}

.quote-block {
  border-left: 3px solid #00ffff;
  padding-left: 1rem;
  margin-bottom: 1rem;
  background: rgba(0,255,255,0.02);
  padding: 1rem;
}
.quote-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.1rem;
  font-style: italic;
  color: #fff;
  margin: 0 0 0.5rem;
}
.quote-meta {
  font-size: 0.8rem;
  color: #666;
  text-align: right;
  font-family: monospace;
}

.timeline-simple {
  position: relative;
  border-left: 1px solid #333;
  margin-left: 10px;
  padding-left: 20px;
}
.timeline-event { margin-bottom: 1.5rem; position: relative; }
.timeline-dot {
  position: absolute;
  left: -25px;
  top: 5px;
  width: 9px;
  height: 9px;
  background: #000;
  border: 2px solid #00ffff;
  border-radius: 50%;
}
.decision-name { font-weight: bold; color: #00ffff; font-size: 0.9rem; }
.decision-ctx { font-size: 0.8rem; color: #888; margin-bottom: 0.25rem; }
.decision-res { font-size: 0.8rem; color: #ccc; }

.network-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
.network-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid #333;
  padding: 0.75rem;
}
.rel-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.8rem;
}
.rel-target { color: #fff; font-weight: bold; }
.rel-type { color: #00ffff; font-family: monospace; }
.rel-desc { font-size: 0.75rem; color: #888; }

/* 与他/与她对话：左侧显著入口 */
.dossier-dialogue-cta {
  margin: 1.25rem 0;
}
.dialogue-cta-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 1rem 1.25rem;
  color: #00ffff;
  background: linear-gradient(135deg, rgba(0,255,255,0.12) 0%, rgba(0,255,255,0.06) 100%);
  border: 2px solid rgba(0,255,255,0.5);
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s, box-shadow 0.2s;
  box-shadow: 0 0 20px rgba(0,255,255,0.15);
}
.dialogue-cta-btn:hover {
  background: linear-gradient(135deg, rgba(0,255,255,0.2) 0%, rgba(0,255,255,0.1) 100%);
  border-color: #00ffff;
  box-shadow: 0 0 28px rgba(0,255,255,0.25);
}
.dialogue-cta-icon {
  font-size: 1.5rem;
  margin-bottom: 0.35rem;
}
.dialogue-cta-text {
  font-size: 1.05rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}
.dialogue-cta-sub {
  font-size: 0.75rem;
  color: rgba(0,255,255,0.75);
  margin-top: 0.25rem;
}

/* 选择式对话模态 */
.dialogue-modal :deep(.n-card-header) { padding-bottom: 0; }
.dialogue-modal :deep(.n-card__content) {
  padding-top: 0.75rem;
  padding-bottom: 1rem;
  background: #0a0a0a;
  border-radius: 0 0 8px 8px;
}
.dialogue-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.dialogue-header {
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(0,255,255,0.15);
}
.dialogue-header-name {
  display: block;
  font-size: 1.35rem;
  font-weight: 600;
  color: #00ffff;
  letter-spacing: 0.5px;
  margin-bottom: 0.2rem;
}
.dialogue-header-role {
  font-size: 0.8rem;
  color: #888;
  font-family: monospace;
}
.dialogue-intro {
  font-size: 0.9rem;
  color: #999;
  font-style: italic;
  margin: 0.75rem 0 0;
  line-height: 1.5;
}
/* 对话消息区：气泡形式 */
.dialogue-messages {
  min-height: 200px;
  max-height: 320px;
  overflow-y: auto;
  padding: 0.5rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.dialogue-row {
  display: flex;
  width: 100%;
}
.dialogue-row-user {
  justify-content: flex-end;
}
.dialogue-row-figure {
  justify-content: flex-start;
}
.dialogue-bubble {
  max-width: 85%;
  padding: 0.65rem 1rem;
  border-radius: 12px;
  font-size: 0.9rem;
  line-height: 1.55;
  word-break: break-word;
}
.dialogue-bubble-user {
  background: rgba(0,255,255,0.15);
  border: 1px solid rgba(0,255,255,0.35);
  color: #e0e0e0;
  border-bottom-right-radius: 4px;
}
.dialogue-bubble-figure {
  background: rgba(0,0,0,0.4);
  border: 1px solid #333;
  color: #ccc;
  border-bottom-left-radius: 4px;
}
.dialogue-figure-name {
  display: block;
  font-size: 0.7rem;
  color: #00ffff;
  margin-bottom: 0.35rem;
  font-family: monospace;
}
.dialogue-bubble-text {
  white-space: pre-wrap;
}
.dialogue-cursor {
  display: inline-block;
  color: #00ffff;
  animation: dialogue-blink 0.8s step-end infinite;
}
@keyframes dialogue-blink {
  50% { opacity: 0; }
}
.dialogue-err-inline {
  margin: 0.5rem 0 0;
  font-size: 0.82rem;
  color: #ff4444;
}
.dialogue-suggested {
  margin-top: 0.25rem;
}
.dialogue-suggested-label {
  font-size: 0.75rem;
  color: #666;
  margin-right: 0.5rem;
}
.dialogue-suggested-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 0.4rem;
}
.dialogue-chip {
  padding: 0.35rem 0.65rem;
  font-size: 0.8rem;
  color: #999;
  background: rgba(255,255,255,0.04);
  border: 1px solid #333;
  border-radius: 999px;
  cursor: pointer;
  transition: color 0.2s, border-color 0.2s, background 0.2s;
}
.dialogue-chip:hover:not(:disabled) {
  color: #00ffff;
  border-color: rgba(0,255,255,0.4);
  background: rgba(0,255,255,0.06);
}
.dialogue-chip:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.dialogue-input-row {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  margin-top: 0.75rem;
}
.dialogue-input {
  flex: 1;
}
.dialogue-llm-config {
  margin-top: 0.5rem;
  border: 1px solid rgba(0,255,255,0.15);
  border-radius: 6px;
}
.dialogue-llm-config :deep(.n-collapse-item__header) {
  font-size: 0.85rem;
  color: #999;
}
.dialogue-llm-hint {
  font-size: 0.78rem;
  color: #777;
  margin: 0 0 0.5rem;
  line-height: 1.45;
}
.dialogue-llm-item {
  margin-bottom: 0.5rem;
}
.dialogue-llm-item :deep(.n-form-item-label) { font-size: 0.8rem; }

@media (max-width: 800px) {
  .dossier-layout { grid-template-columns: 1fr; }
  .col-left { border-right: none; border-bottom: 1px solid #333; padding-right: 0; padding-bottom: 2rem; margin-bottom: 2rem; }
  .portrait-wrapper { max-width: 300px; margin: 0 auto 1.5rem; }
}
</style>
