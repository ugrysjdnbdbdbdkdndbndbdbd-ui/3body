<script setup lang="ts">
/**
 * ApocryphaModule.vue
 * 三体外传 (Three-Body Apocrypha)
 * 同人/COO 创作：基于三体世界观的续写与宏观叙事中的细节展开
 * 交互：点击条目 → 逐字解码（打字机）
 */
import { ref, onMounted } from 'vue'
import { API, apiUrl } from '@/constants'

export interface ApocryphaEntry {
  uuid: string
  title: string
  time_anchor: string
  content: string
  genre?: string
  author?: string
}

const items = ref<ApocryphaEntry[]>([])
const loading = ref(true)
const selectedItem = ref<ApocryphaEntry | null>(null)
const displayedText = ref('')
const isTyping = ref(false)
let typeTimer: number | null = null

async function loadItems() {
  loading.value = true
  try {
    const res = await fetch(apiUrl(API.CHRONICLE_APOCRYPHA))
    if (res.ok) {
      const data = await res.json()
      items.value = Array.isArray(data) ? data : []
    } else {
      items.value = []
    }
  } catch {
    // Fallback content
    items.value = [
      {
        uuid: 'APO-001',
        title: '歌者的清理日志 (Singer\'s Log)',
        time_anchor: '掩体纪元 67年',
        genre: 'Side Story',
        author: 'Unknown',
        content: '我翻看着坐标数据。这个星系有三颗恒星，真是一个狂野的地方。那个被广播的坐标已经被清理过了，是用光粒清理的。很粗糙，很不彻底。我又看了一眼那个星系的边缘，那里有一颗黄色的恒星，还带着几颗行星。那个世界还没被清理，但它已经暴露了。虽然它没有直接广播坐标，但它和那个被清理的星系有过接触。这就是死穴。我叹了口气，从封装场里拿出了一块二向箔。长老说这东西很贵，但为了清理干净，还是用吧。我把它像扔垃圾一样扔了出去。再见，虫子们。'
      },
      {
        uuid: 'APO-002',
        title: '面壁者罗辑的噩梦',
        time_anchor: '危机纪元 8年',
        genre: 'Psychology',
        author: 'Wallfacer',
        content: '罗辑梦见自己走在冰冻的湖面上。冰层下是深不见底的黑暗。他知道那是深渊，是宇宙的真相。忽然，冰面裂开了，并没有水涌出来，而是无数只眼睛。智子的眼睛。它们在看着他，看着他脑子里的每一个念头。他想喊，却发不出声音。“这就是面壁者的诅咒吗？”一个声音问，“你必须对全世界隐瞒真相，直到你也骗过了自己。”'
      },
      {
        uuid: 'APO-003',
        title: '云天明的三个童话 (解读版)',
        time_anchor: '广播纪元 7年',
        genre: 'Analysis',
        author: 'AA',
        content: '关于《国王的新画师》：针眼画师把人画进画里，人就消失了。这暗示了二向箔打击，即三维向二维的跌落。关于《饕餮海》：鱼离开了水就不能活，但这鱼却上了岸。这暗示了光速飞船的曲率驱动，以及脱离低光速黑洞（死线）的方法。关于《深水王子》：他不符合透视原理，无论远近都一样大。这暗示了光速不变，以及低光速区域的物理特性。云天明把人类生存的所有密码，都藏在了这三个童话里。'
      },
      {
        uuid: 'APO-004',
        title: '蓝色空间的最后一次广播',
        time_anchor: '银河纪元 409年',
        genre: 'Transmission',
        author: 'Blue Space',
        content: '“这里是蓝色空间号。我们已经离开了猎户旋臂。前方的星域非常空旷，但也非常安静。我们探测到了多个引力波源，但我们没有回应。我们学会了在黑暗森林里像幽灵一样潜行。告诉地球的孩子们，不要回答。永远不要回答。即使是来自人类的呼唤，也不要回答。因为你永远不知道，那是不是猎人的伪装。”'
      },
      {
        uuid: 'APO-005',
        title: '智子：微观维度的战争',
        time_anchor: '危机纪元 1年',
        genre: 'Sci-Fi',
        author: 'Physics',
        content: '当三体人将质子二维展开时，他们看到了什么？他们看到了一个微观的宇宙，那里有智慧文明。那个文明攻击了三体世界，虽然只是微观层面的反击，却让三体人感到了恐惧。为了制造智子，三体人不得不毁灭了微观宇宙中的所有文明。这是第一次黑暗森林打击，发生在九维空间跌落到二维的过程中。'
      }
    ]
  } finally {
    loading.value = false
  }
}

function openDetail(entry: ApocryphaEntry) {
  selectedItem.value = entry
  displayedText.value = ''
  isTyping.value = true
  if (typeTimer != null) {
    clearTimeout(typeTimer)
    typeTimer = null
  }
  const fullText = entry.content || ''
  let i = 0
  const typeChar = () => {
    if (!selectedItem.value) return
    if (i < fullText.length) {
      displayedText.value += fullText[i]
      i++
      typeTimer = window.setTimeout(typeChar, Math.random() * 30 + 20)
    } else {
      isTyping.value = false
    }
  }
  typeChar()
}

function closeDetail() {
  selectedItem.value = null
  if (typeTimer) {
    clearTimeout(typeTimer)
    typeTimer = null
  }
  displayedText.value = ''
}

onMounted(loadItems)
</script>

<template>
  <div class="apocrypha-module">
    <div class="apocrypha-header">
      <div class="header-info">
        <h2 class="module-title">APOCRYPHA // 三体外传</h2>
        <span class="module-subtitle">同人 · COO 续写与细节展开 [{{ items.length }}]</span>
      </div>
    </div>

    <div class="apocrypha-grid">
      <div
        v-for="entry in items"
        :key="entry.uuid"
        class="apocrypha-card"
        @click="openDetail(entry)"
      >
        <div class="card-frame">
          <div class="card-badge">
            <span class="badge-genre">{{ entry.genre || '外传' }}</span>
            <span class="badge-author">{{ entry.author || 'COO' }}</span>
          </div>
          <div class="card-body">
            <h3 class="card-title">{{ entry.title }}</h3>
            <p class="card-anchor">{{ entry.time_anchor }}</p>
          </div>
          <button class="card-action">阅读</button>
        </div>
      </div>
    </div>

    <transition name="retina-fade">
      <div v-if="selectedItem" class="retina-overlay" @click.self="closeDetail">
        <div class="retina-container">
          <div class="retina-scanline"></div>
          <div class="retina-header">
            <div>
              <h2 class="retina-title">{{ selectedItem.title }}</h2>
              <p class="retina-meta">
                {{ selectedItem.time_anchor }}
                <span class="meta-sep">·</span>
                <span class="meta-genre">{{ selectedItem.genre }}</span>
                <span class="meta-sep">·</span>
                <span class="meta-author">{{ selectedItem.author }}</span>
              </p>
            </div>
            <button class="retina-close" @click="closeDetail">[关闭]</button>
          </div>
          <div class="retina-content">
            <div class="retina-text-box">
              <p class="retina-text">
                {{ displayedText }}<span v-if="isTyping" class="cursor-block">█</span>
              </p>
            </div>
          </div>
          <div class="retina-footer">
            <span>APOCRYPHA_LAYER // 非正典 · 基于三体世界观创作</span>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.apocrypha-module {
  padding: 1rem;
  width: 100%;
}

.apocrypha-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 2rem;
  border-bottom: 1px solid var(--border-tech);
  padding-bottom: 1rem;
}

.module-title {
  font-family: var(--font-tech);
  color: var(--holo-green, #00ff41);
  font-size: 1.2rem;
  letter-spacing: 0.1em;
  margin: 0;
  text-shadow: 0 0 10px rgba(0, 255, 65, 0.3);
}

.module-subtitle {
  font-family: var(--font-tech);
  color: var(--text-muted);
  font-size: 0.75rem;
  margin-left: 0.5rem;
}

.apocrypha-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.apocrypha-card {
  cursor: pointer;
}

.card-frame {
  background: rgba(2, 6, 23, 0.6);
  border: 1px solid rgba(0, 255, 65, 0.25);
  padding: 1rem;
  transition: all 0.3s ease;
  position: relative;
}

.apocrypha-card:hover .card-frame {
  border-color: var(--holo-green, #00ff41);
  box-shadow: 0 0 20px rgba(0, 255, 65, 0.15);
}

.card-badge {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.badge-genre {
  font-family: var(--font-tech);
  font-size: 0.65rem;
  padding: 0.2rem 0.5rem;
  background: rgba(0, 255, 65, 0.15);
  color: var(--holo-green, #00ff41);
  border: 1px solid rgba(0, 255, 65, 0.4);
}

.badge-author {
  font-family: var(--font-tech);
  font-size: 0.65rem;
  color: var(--text-muted);
}

.card-body {
  margin-bottom: 0.5rem;
}

.card-title {
  font-family: var(--font-tech);
  color: var(--text);
  font-size: 0.95rem;
  margin: 0 0 0.4rem;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-anchor {
  font-size: 0.7rem;
  color: var(--text-muted);
  margin: 0;
}

.card-action {
  background: transparent;
  border: 1px solid var(--holo-green, #00ff41);
  color: var(--holo-green, #00ff41);
  font-family: var(--font-tech);
  font-size: 0.7rem;
  padding: 0.3rem 0.6rem;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
  margin-top: 0.5rem;
}

.apocrypha-card:hover .card-action {
  background: rgba(0, 255, 65, 0.2);
}

/* Retina overlay */
.retina-overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: rgba(0, 0, 0, 0.9);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.retina-container {
  width: 90%;
  max-width: 800px;
  height: 80vh;
  border: 1px solid var(--holo-green, #00ff41);
  background: rgba(0, 20, 15, 0.85);
  position: relative;
  overflow: hidden;
  box-shadow: 0 0 50px rgba(0, 255, 65, 0.1);
  display: flex;
  flex-direction: column;
}

.retina-scanline {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 8px;
  background: rgba(0, 255, 65, 0.25);
  opacity: 0.6;
  animation: scan 4s linear infinite;
  pointer-events: none;
  z-index: 10;
}

.retina-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(0, 255, 65, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.retina-title {
  font-family: var(--font-tech);
  font-size: 1.25rem;
  color: var(--holo-green, #00ff41);
  margin: 0 0 0.35rem;
  letter-spacing: 0.05em;
}

.retina-meta {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin: 0;
}

.meta-sep {
  margin: 0 0.35rem;
  opacity: 0.6;
}

.meta-genre {
  color: var(--holo-green, #00ff41);
}

.meta-author {
  color: var(--text-muted);
}

.retina-close {
  background: transparent;
  border: 1px solid var(--text-muted);
  color: var(--text-muted);
  font-family: var(--font-tech);
  font-size: 0.75rem;
  padding: 0.4rem 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}

.retina-close:hover {
  border-color: var(--holo-green, #00ff41);
  color: var(--holo-green, #00ff41);
}

.retina-content {
  flex: 1;
  overflow: hidden;
}

.retina-text-box {
  padding: 1.5rem 2rem;
  height: 100%;
  overflow-y: auto;
  font-family: var(--font-tech);
}

.retina-text {
  color: var(--text);
  font-size: 0.95rem;
  line-height: 1.85;
  white-space: pre-wrap;
}

.cursor-block {
  display: inline-block;
  width: 0.5em;
  height: 1.1em;
  background: var(--holo-green, #00ff41);
  animation: blink 0.8s step-end infinite;
  vertical-align: text-bottom;
  margin-left: 2px;
}

.retina-footer {
  padding: 0.6rem 1.5rem;
  border-top: 1px solid rgba(0, 255, 65, 0.2);
  font-family: var(--font-tech);
  font-size: 0.65rem;
  color: var(--text-muted);
}

@keyframes scan {
  0% { top: -10%; }
  100% { top: 110%; }
}
@keyframes blink {
  50% { opacity: 0; }
}

.retina-fade-enter-active,
.retina-fade-leave-active {
  transition: opacity 0.25s;
}
.retina-fade-enter-from,
.retina-fade-leave-to {
  opacity: 0;
}
</style>
