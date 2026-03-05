<script setup lang="ts">
/**
 * Sector: The Great Ravine (大低谷)
 * 文字生存冒险 — 危机纪元中人类文明最黑暗的时期，在地下城挣扎求生。
 * 风格：老式终端 / 生存日志
 */
import { ref, nextTick } from 'vue'
import { NScrollbar, NModal, NCard, NButton } from 'naive-ui'

interface PlayerStats {
  health: number
  hunger: number
  sanity: number
  day: number
}

const stats = ref<PlayerStats>({
  health: 100,
  hunger: 0,
  sanity: 100,
  day: 1,
})

type LogType = 'normal' | 'danger' | 'success'

const logs = ref<{ text: string; type?: LogType }[]>([
  { text: '危机纪元 47 年。大低谷已经持续了五年。', type: 'normal' },
  { text: '资源向太空防御倾斜，地表农业崩溃，地下城配给一减再减。人口从八十亿跌到不足一半。', type: 'normal' },
  { text: '你在地下城的狭窄公寓中醒来。空气中弥漫着霉味和合成食品的甜腻味。', type: 'normal' },
  { text: '肚子在叫。你已经两天没吃东西了。', type: 'danger' },
])

interface Choice {
  id: string
  text: string
  action: () => void
}

const DEFAULT_CHOICES: Choice[] = [
  { id: 'search', text: '搜寻房间', action: () => handleChoice('search') },
  { id: 'rest', text: '继续睡觉（保存体力）', action: () => handleChoice('rest') },
  { id: 'outside', text: '去救济站排队', action: () => handleChoice('outside') },
  { id: 'blackmarket', text: '去黑市碰运气', action: () => handleChoice('blackmarket') },
  { id: 'build', text: '去建设队报名（换口粮）', action: () => handleChoice('build') },
  { id: 'read', text: '在屋里读旧书', action: () => handleChoice('read') },
]

const currentChoices = ref<Choice[]>([...DEFAULT_CHOICES])

const isDead = ref(false)
const showEndModal = ref(false)
const endMessage = ref('')
const endIsWin = ref(false)
const scrollbarRef = ref<InstanceType<typeof NScrollbar> | null>(null)
const lastMilestone = ref(0)

function addLog(text: string, type: LogType = 'normal') {
  logs.value.push({ text, type })
  nextTick(() => {
    const el = scrollbarRef.value?.$el?.querySelector?.('.n-scrollbar-container')
    if (el) el.scrollTo({ top: 99999, behavior: 'smooth' })
  })
}

function refreshChoices() {
  currentChoices.value = [...DEFAULT_CHOICES]
}

function triggerMilestone(day: number) {
  if (lastMilestone.value >= day) return
  lastMilestone.value = day
  if (day === 5) {
    addLog('广播：本周配给再次削减。请市民保持秩序。', 'danger')
  } else if (day === 10) {
    addLog('传闻：第七区有人吃人。你不敢多想。', 'danger')
  } else if (day === 15) {
    addLog('你在救济站听到有人说：技术复兴在望，再撑几年就好。', 'success')
  } else if (day === 20) {
    addLog('建设队发了一份额外的合成蛋白。这是几个月来唯一的好消息。', 'success')
  } else if (day === 25) {
    addLog('广播里开始提到「后危机纪元」和「舰队计划」。希望像一根细线。', 'success')
  }
}

function handleChoice(id: string) {
  stats.value.day++
  stats.value.hunger = Math.min(100, stats.value.hunger + 10)

  if (id === 'search') {
    if (Math.random() > 0.55) {
      addLog('你在床底发现了一块过期的压缩饼干。', 'success')
      stats.value.hunger = Math.max(0, stats.value.hunger - 30)
    } else {
      addLog('什么也没找到，只有灰尘和一只死老鼠。', 'normal')
      stats.value.sanity -= 5
    }
  } else if (id === 'rest') {
    addLog('你睡了一整天。梦见了大低谷前的世界：阳光、草地、没有配给。', 'normal')
    stats.value.health = Math.min(100, stats.value.health + 5)
    stats.value.hunger = Math.min(100, stats.value.hunger + 5)
    stats.value.sanity = Math.min(100, stats.value.sanity + 3)
  } else if (id === 'outside') {
    if (Math.random() > 0.5) {
      addLog('救济站爆发了骚乱。你被人推倒，受了点伤，但抢到了一碗粥。', 'danger')
      stats.value.health -= 10
      stats.value.hunger = Math.max(0, stats.value.hunger - 40)
      stats.value.sanity -= 10
    } else {
      addLog('队伍很长。你排了六个小时，终于领到了配给粮。', 'success')
      stats.value.hunger = Math.max(0, stats.value.hunger - 50)
    }
  } else if (id === 'blackmarket') {
    if (Math.random() > 0.6) {
      addLog('黑市上你用仅剩的零件换到一罐罐头。', 'success')
      stats.value.hunger = Math.max(0, stats.value.hunger - 35)
    } else {
      addLog('你被巡逻队发现，东西被没收，还挨了一顿揍。', 'danger')
      stats.value.health -= 15
      stats.value.sanity -= 10
    }
  } else if (id === 'build') {
    addLog('建设队让你搬了一整天砖。累得半死，但领到了两份口粮。', 'normal')
    stats.value.health -= 5
    stats.value.hunger = Math.max(0, stats.value.hunger - 45)
    stats.value.sanity = Math.min(100, stats.value.sanity + 5)
  } else if (id === 'read') {
    addLog('你翻出一本旧书，读了一整天。思绪暂时离开了地下城。', 'normal')
    stats.value.sanity = Math.min(100, stats.value.sanity + 12)
    stats.value.hunger = Math.min(100, stats.value.hunger + 8)
  }

  triggerMilestone(stats.value.day)

  if (Math.random() > 0.75) {
    addLog('有人敲门。「为了人类文明，分我一点吃的吧……」', 'danger')
    currentChoices.value = [
      { id: 'open', text: '开门分享', action: () => handleEvent('share') },
      { id: 'ignore', text: '保持沉默', action: () => handleEvent('ignore') },
    ]
    return
  }

  checkStatus()
  if (!isDead.value) refreshChoices()
}

function handleEvent(id: string) {
  if (id === 'share') {
    addLog('你打开门。那人冲进来抢走了你所有的存粮，并打伤了你。', 'danger')
    stats.value.health -= 30
    stats.value.sanity -= 20
    stats.value.hunger = Math.min(100, stats.value.hunger + 20)
  } else {
    addLog('敲门声持续了很久，最后变成了哭声，然后消失了。', 'normal')
    stats.value.sanity -= 15
  }
  checkStatus()
  refreshChoices()
}

function checkStatus() {
  if (stats.value.hunger >= 100) {
    end('你饿死了。大低谷吞没了又一个灵魂。', false)
    return
  }
  if (stats.value.health <= 0) {
    end('你因伤重不治而亡。', false)
    return
  }
  if (stats.value.sanity <= 0) {
    end('你疯了。在幻觉中走出了地下城，被冻死在荒原上。', false)
    return
  }
  if (stats.value.day > 30) {
    end('你熬过了大低谷最黑暗的时期。文明正在复苏，技术爆炸即将到来。', true)
  }
}

function end(reason: string, win: boolean) {
  isDead.value = true
  endMessage.value = reason
  endIsWin.value = win
  addLog(reason, win ? 'success' : 'danger')
  currentChoices.value = [{ id: 'restart', text: '重新开始', action: resetGame }]
  showEndModal.value = true
}

function resetGame() {
  stats.value = { health: 100, hunger: 0, sanity: 100, day: 1 }
  lastMilestone.value = 0
  logs.value = [
    { text: '再次醒来。无论如何，活下去。', type: 'normal' },
    { text: '肚子又在叫了。新的一天，同样的选择。', type: 'normal' },
  ]
  isDead.value = false
  showEndModal.value = false
  refreshChoices()
}

const RAVINE_QUOTE = '「大低谷时期，人类曾一度将生存置于文明之上。但文明最终没有消失。」'
</script>

<template>
  <div class="sector-ravine">
    <header class="ravine-header">
      <h1 class="ravine-title">大低谷</h1>
      <p class="ravine-sub">THE GREAT RAVINE · 危机纪元中人类文明最黑暗的时期</p>
    </header>

    <div class="terminal-screen">
      <div class="terminal-title-bar">SURVIVAL LOG // 地下城 · 第 {{ stats.day }} 天</div>

      <div class="status-bar">
        <div class="stat-item">
          <span class="stat-label">HEALTH</span>
          <div class="stat-bar"><div class="stat-fill health" :style="{ width: stats.health + '%' }" /></div>
        </div>
        <div class="stat-item">
          <span class="stat-label">HUNGER</span>
          <div class="stat-bar"><div class="stat-fill hunger" :class="{ critical: stats.hunger > 80 }" :style="{ width: stats.hunger + '%' }" /></div>
        </div>
        <div class="stat-item">
          <span class="stat-label">SANITY</span>
          <div class="stat-bar"><div class="stat-fill sanity" :style="{ width: stats.sanity + '%' }" /></div>
        </div>
      </div>

      <NScrollbar ref="scrollbarRef" class="log-window">
        <div class="log-content">
          <div
            v-for="(log, i) in logs"
            :key="i"
            class="log-line"
            :class="`type-${log.type ?? 'normal'}`"
          >
            &gt; {{ log.text }}
          </div>
        </div>
      </NScrollbar>

      <div class="input-area">
        <div class="choices">
          <button
            v-for="c in currentChoices"
            :key="c.id"
            class="cmd-btn"
            @click="c.action()"
          >
            [ {{ c.text }} ]
          </button>
        </div>
      </div>
    </div>

    <NModal v-model:show="showEndModal" display-directive="show">
      <NCard
        :title="endIsWin ? '幸存' : '终结'"
        class="end-card"
        :class="{ 'end-card--win': endIsWin }"
        size="huge"
        bordered
      >
        <p class="end-message">{{ endMessage }}</p>
        <p class="end-quote">{{ RAVINE_QUOTE }}</p>
        <template #footer>
          <NButton type="primary" block @click="resetGame">重新开始</NButton>
        </template>
      </NCard>
    </NModal>
  </div>
</template>

<style scoped>
.sector-ravine {
  min-height: 0;
  background: #050508;
  padding: 1.5rem 2rem 2rem;
  font-family: 'Courier New', 'Consolas', monospace;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.ravine-header {
  text-align: center;
}

.ravine-title {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 600;
  letter-spacing: 0.2em;
  color: #8b9a6b;
}

.ravine-sub {
  margin: 0.35rem 0 0;
  font-size: 0.8rem;
  color: rgba(139, 154, 107, 0.85);
  letter-spacing: 0.08em;
}

.terminal-screen {
  width: 100%;
  max-width: 720px;
  height: 75vh;
  min-height: 420px;
  border: 1px solid #4a5d2a;
  background: #0a0f08;
  box-shadow: 0 0 30px rgba(74, 93, 42, 0.15);
  display: flex;
  flex-direction: column;
  padding: 0;
  color: #7d9a3c;
  position: relative;
}

.terminal-screen::after {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0, 0, 0, 0.12) 2px,
    rgba(0, 0, 0, 0.12) 4px
  );
  pointer-events: none;
  z-index: 1;
}

.terminal-title-bar {
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
  letter-spacing: 0.15em;
  color: rgba(125, 154, 60, 0.9);
  border-bottom: 1px dashed #3d4e20;
  flex-shrink: 0;
}

.status-bar {
  display: flex;
  gap: 1.5rem;
  padding: 0.6rem 1rem;
  border-bottom: 1px dashed #3d4e20;
  flex-shrink: 0;
}

.stat-item {
  flex: 1;
  min-width: 0;
}

.stat-label {
  display: block;
  font-size: 0.7rem;
  color: rgba(125, 154, 60, 0.8);
  margin-bottom: 0.25rem;
}

.stat-bar {
  height: 6px;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid #3d4e20;
  overflow: hidden;
}

.stat-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.stat-fill.health {
  background: #5a7a2e;
}

.stat-fill.hunger {
  background: #8b6b2e;
}

.stat-fill.hunger.critical {
  background: #a03020;
  animation: blink 1s infinite;
}

.stat-fill.sanity {
  background: #3d5a4a;
}

.log-window {
  flex: 1;
  min-height: 0;
  padding: 1rem;
}

.log-window :deep(.n-scrollbar-container) {
  padding-right: 0.5rem;
}

.log-content {
  padding-bottom: 1rem;
}

.log-line {
  margin-bottom: 0.65rem;
  line-height: 1.55;
  font-size: 0.9rem;
}

.type-normal {
  color: #7d9a3c;
}

.type-danger {
  color: #c05040;
}

.type-success {
  color: #b8a030;
}

.input-area {
  border-top: 1px dashed #3d4e20;
  padding: 1rem;
  flex-shrink: 0;
}

.choices {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.cmd-btn {
  background: transparent;
  border: 1px solid #4a5d2a;
  color: #7d9a3c;
  font-family: inherit;
  font-size: 0.85rem;
  cursor: pointer;
  padding: 0.45rem 0.85rem;
  transition: background 0.2s, color 0.2s;
}

.cmd-btn:hover {
  background: rgba(125, 154, 60, 0.2);
  color: #9fb85a;
}

.end-card {
  width: 100%;
  max-width: 440px;
}

.end-card--win {
  border-color: rgba(90, 122, 46, 0.5);
}

.end-message {
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 1rem;
  color: #1f2937;
}

.end-quote {
  font-size: 0.85rem;
  color: #6b7280;
  font-style: italic;
  margin: 0;
}

@keyframes blink {
  50% { opacity: 0.6; }
}
</style>
