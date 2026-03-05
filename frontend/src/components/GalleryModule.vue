<script setup lang="ts">
/**
 * GalleryModule.vue
 * 宇宙档案馆 (Cosmic Archive)
 * 交互升级：智子视网膜投影模式 (Retina Projection)
 * 点击档案 -> 逐字解码历史 (Typewriter Playback)
 */
import { ref, onMounted } from 'vue'
import type { GalleryItem } from '@/types/gallery'
import { apiUrl } from '@/constants'

const items = ref<GalleryItem[]>([])
const loading = ref(true)
const selectedItem = ref<GalleryItem | null>(null)

// 打字机状态
const displayedText = ref('')
const isTyping = ref(false)
let typeTimer: number | null = null

// PRD 1.6: 宇宙档案馆预置数据
const COSMIC_ARCHIVES: GalleryItem[] = [
  {
    id: 1,
    title: '绝密：红岸工程解密',
    description: '【叶文洁审讯笔录片段】\n\n那是一个阴沉的下午，我在红岸基地的监听室里。太阳的波形在屏幕上跳动，像一颗躁动的心脏。我意识到，这不仅仅是恒星，这是一个超级天线。\n\n发射频率：22000 MHz\n发射功率：25 MW\n目标：半人马座三星\n\n回复内容：不要回答！不要回答！不要回答！',
    media_type: 'image',
    media_url: 'https://images.unsplash.com/photo-1518544806352-a2229232da96?q=80&w=800&auto=format&fit=crop',
    status: 'active',
    created_at: new Date().toISOString(),
    author_id: 'COO'
  },
  {
    id: 2,
    title: '面壁计划：战略白皮书',
    description: '【面壁者：罗辑】\n\n逻辑核心：宇宙社会学公理。\n\n1. 生存是文明的第一需要。\n2. 文明不断增长和扩张，但宇宙中的物质总量保持不变。\n\n战略意图：利用黑暗森林法则，通过向宇宙广播三体星系坐标，建立威慑。\n\n状态：生效中\n威慑度：98%',
    media_type: 'image',
    media_url: 'https://images.unsplash.com/photo-1614728853913-a362395a4eb6?q=80&w=800&auto=format&fit=crop',
    status: 'active',
    created_at: new Date().toISOString(),
    author_id: 'COO'
  },
  {
    id: 3,
    title: '阶梯计划：飞行轨迹',
    description: '【载荷：云天明大脑】\n\n加速方式：核脉冲推进\n航向：天鹅座方向\n当前状态：偏离预定航线\n\n......\n\n检测到第三方文明截获迹象。\n\n“送给三体人的大脑，也许是人类最危险的武器。”',
    media_type: 'image',
    media_url: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=800&auto=format&fit=crop',
    status: 'active',
    created_at: new Date().toISOString(),
    author_id: 'COO'
  },
  {
    id: 4,
    title: '古筝行动：现场记录',
    description: '【行动代号：古筝】\n\n地点：巴拿马运河，盖拉德水道\n武器：飞刃（纳米超导体）\n\n记录：\n审判日号正在通过...\n第一根弦接触...\n船体切片完成...\n伊文斯确认死亡。\n\n三体信息已截获。',
    media_type: 'image',
    media_url: 'https://images.unsplash.com/photo-1605218427306-6354db696faa?q=80&w=800&auto=format&fit=crop',
    status: 'cleansed',
    created_at: new Date().toISOString(),
    author_id: 'COO'
  }
]

/** 从 time_anchor 解析公元年，用于按公元纪年排序 */
function parseTimeAnchorToCE(anchor: string): number {
  if (!anchor) return 0
  const m = anchor.match(/公元\s*(\d{3,4})\s*年/)
  if (m) return parseInt(m[1], 10)
  if (/201[Xx]/.test(anchor)) return 2018
  const ERA_CE_BASE: Record<string, number> = {
    '黄金时代': 1960, '危机纪元': 2015, '威慑纪元': 2212,
    '掩体纪元': 2270, '广播纪元': 2400, '乱纪元': 2500, '银河纪元': 2687
  }
  for (const [era, base] of Object.entries(ERA_CE_BASE)) {
    if (anchor.includes(era)) {
      const n = anchor.match(/(\d+)\s*年/)
      return base + (n ? parseInt(n[1], 10) : 0)
    }
  }
  return 0
}

async function loadItems() {
  loading.value = true
  try {
    const res = await fetch(apiUrl('/api/chronicle/archives'))
    if (res.ok) {
      const data = await res.json()
      if (Array.isArray(data) && data.length > 0) {
        const sorted = [...data].sort((a: any, b: any) =>
          parseTimeAnchorToCE(a.time_anchor || '') - parseTimeAnchorToCE(b.time_anchor || '')
        )
        items.value = sorted.map((item: any) => ({
          id: item.uuid as string,
          title: item.title,
          description: `【${item.time_anchor}】\n\n${item.content}`,
          media_type: 'image',
          media_url: 'https://images.unsplash.com/photo-1462331940025-496dfbfc7564?q=80&w=800&auto=format&fit=crop', // Default cosmic image
          status: 'active',
          created_at: new Date().toISOString(),
          author_id: 'SOPHON'
        }))
      } else {
        items.value = COSMIC_ARCHIVES
      }
    } else {
      items.value = COSMIC_ARCHIVES
    }
  } catch {
    items.value = COSMIC_ARCHIVES
  } finally {
    loading.value = false
  }
}

// 启动视网膜投影
function openDetail(item: GalleryItem) {
  selectedItem.value = item
  displayedText.value = ''
  isTyping.value = true
  
  if (typeTimer != null) {
    clearTimeout(typeTimer)
    typeTimer = null
  }
  
  const fullText = item.description || "NO DATA FOUND..."
  let i = 0
  
  // 打字机逻辑：随机间隔，模拟数据传输不稳
  const typeChar = () => {
    if (!selectedItem.value) return // 停止如果已关闭

    if (i < fullText.length) {
      displayedText.value += fullText[i]
      i++
      const delay = Math.random() * 30 + 20 // 20-50ms
      typeTimer = window.setTimeout(typeChar, delay)
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
  <div class="gallery-module">
    <div class="gallery-header">
      <div class="header-info">
        <h2 class="module-title">COSMIC_ARCHIVES // 宇宙档案馆</h2>
        <span class="module-subtitle">绝密历史档案 [{{ items.length }}] · 智子视网膜投影</span>
      </div>
    </div>

    <div class="gallery-grid">
      <div 
        v-for="item in items" 
        :key="item.id" 
        class="foil-card"
        :class="{ 
          'item-cleansed': item.status === 'cleansed',
          'item-exposed': item.status === 'exposed'
        }"
        @click="openDetail(item)"
      >
        <div class="foil-frame">
          <div class="foil-media">
            <div class="archive-seal">TOP SECRET</div>
            <div v-if="item.status === 'cleansed'" class="cleansed-overlay">
              <span class="text-xs text-red-500 font-mono">[已封存]</span>
            </div>
            <img v-if="item.media_type === 'image'" :src="item.media_url" :alt="item.title" loading="lazy" :class="{ 'img-cleansed': item.status === 'cleansed' }" />
            <div class="scan-line"></div>
            <div class="foil-glare"></div>
          </div>
          
          <div class="foil-info">
            <h3 class="foil-title">{{ item.title }}</h3>
            <div class="foil-meta">
              <span>REF: {{ String(item.id).slice(-6).toUpperCase() }}</span>
              <button class="action-btn">读取</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 视网膜投影模态框 (Retina Projection Overlay) -->
    <transition name="retina-fade">
      <div v-if="selectedItem" class="retina-overlay" @click.self="closeDetail">
        <div class="retina-container">
          <div class="retina-scanline"></div>
          
          <div class="retina-header">
            <h2 class="retina-title">{{ selectedItem.title }}</h2>
            <button class="retina-close" @click="closeDetail">[中断连接]</button>
          </div>

          <div class="retina-content">
            <div class="retina-media-box">
              <img :src="selectedItem.media_url" class="retina-img" />
              <div class="img-grid-overlay"></div>
            </div>
            
            <div class="retina-text-box">
              <p class="retina-text">
                {{ displayedText }}<span v-if="isTyping" class="cursor-block">█</span>
              </p>
            </div>
          </div>
          
          <div class="retina-footer">
            <span>SOPHON_LAYER_PROJECTION // VERIFIED</span>
            <span>TRANSMISSION_RATE: 100%</span>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.gallery-module {
  padding: 1rem;
  width: 100%;
}

.gallery-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 2rem;
  border-bottom: 1px solid var(--border-tech);
  padding-bottom: 1rem;
}

.module-title {
  font-family: var(--font-tech);
  color: var(--holo-blue);
  font-size: 1.2rem;
  letter-spacing: 0.1em;
  margin: 0;
  text-shadow: 0 0 10px rgba(0, 240, 255, 0.3);
}

.module-subtitle {
  font-family: var(--font-tech);
  color: var(--text-muted);
  font-size: 0.75rem;
  margin-left: 0.5rem;
}

/* Grid */
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 2rem;
}

.foil-card { perspective: 1000px; cursor: pointer; }
.foil-frame {
  background: rgba(2, 6, 23, 0.6);
  border: 1px solid var(--border-tech);
  padding: 0.5rem;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
}
.foil-card:hover .foil-frame {
  transform: rotateX(5deg) translateY(-10px);
  border-color: var(--holo-blue);
  box-shadow: 0 15px 30px rgba(0, 240, 255, 0.15);
  background: rgba(2, 6, 23, 0.9);
}

.foil-media {
  position: relative;
  aspect-ratio: 4/3;
  background: #000;
  overflow: hidden;
  border-bottom: 1px solid var(--border-tech);
}
.foil-media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.6;
  filter: sepia(0.5) grayscale(0.5);
  transition: opacity 0.3s;
}
.foil-card:hover .foil-media img { opacity: 0.9; filter: none; }

.archive-seal {
  position: absolute;
  top: 10px; right: 10px;
  border: 2px solid rgba(255, 60, 0, 0.5);
  color: rgba(255, 60, 0, 0.5);
  padding: 2px 5px;
  font-family: monospace;
  font-weight: bold;
  font-size: 0.8rem;
  transform: rotate(-15deg);
  z-index: 5;
  pointer-events: none;
}

.foil-info { padding: 1rem 0.5rem 0.5rem; }
.foil-title {
  font-family: var(--font-tech);
  color: var(--text);
  font-size: 0.9rem;
  margin: 0 0 0.5rem;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.foil-meta {
  display: flex; justify-content: space-between; align-items: center;
  font-family: var(--font-tech); font-size: 0.65rem; color: var(--text-muted);
}
.action-btn {
  background: transparent; border: 1px solid var(--holo-blue);
  color: var(--holo-blue); font-family: var(--font-tech); font-size: 0.65rem;
  padding: 0.2rem 0.5rem; cursor: pointer;
  transition: all 0.2s;
}
.foil-card:hover .action-btn { background: var(--holo-blue); color: #000; }

.item-cleansed { border-color: #ff0000 !important; transform: scale(0.98); filter: grayscale(1); }
.cleansed-overlay {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.7);
  display: flex; align-items: center; justify-content: center; z-index: 10; pointer-events: none;
}
.img-cleansed { opacity: 0.3; }

/* --- Retina Overlay --- */
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
  max-width: 1000px;
  height: 80vh;
  border: 1px solid var(--holo-blue);
  background: rgba(0, 20, 40, 0.8);
  position: relative;
  overflow: hidden;
  box-shadow: 0 0 50px rgba(0, 240, 255, 0.1);
  display: flex;
  flex-direction: column;
}

.retina-scanline {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 10px;
  background: rgba(0, 240, 255, 0.3);
  opacity: 0.5;
  animation: scan 4s linear infinite;
  pointer-events: none;
  z-index: 10;
}

.retina-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-tech);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.retina-title {
  font-family: var(--font-display);
  font-size: 1.5rem;
  color: var(--holo-blue);
  margin: 0;
  letter-spacing: 0.1em;
  text-shadow: 0 0 10px var(--holo-blue);
}
.retina-close {
  background: transparent; border: 1px solid var(--holo-red);
  color: var(--holo-red); font-family: var(--font-tech);
  padding: 0.5rem 1rem; cursor: pointer; transition: all 0.2s;
}
.retina-close:hover { background: var(--holo-red); color: #000; }

.retina-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.retina-media-box {
  width: 40%;
  border-right: 1px solid var(--border-tech);
  position: relative;
}
.retina-img {
  width: 100%; height: 100%; object-fit: cover;
  filter: grayscale(0.8) contrast(1.2);
}
.img-grid-overlay {
  position: absolute; inset: 0;
  background-image: linear-gradient(rgba(0,255,200,0.1) 1px, transparent 1px),
  linear-gradient(90deg, rgba(0,255,200,0.1) 1px, transparent 1px);
  background-size: 20px 20px;
  pointer-events: none;
}

.retina-text-box {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
  font-family: 'Special Elite', var(--font-tech); /* 优先打字机字体 */
}

.retina-text {
  color: #fff;
  font-size: 1rem;
  line-height: 1.8;
  white-space: pre-wrap;
  text-shadow: 0 0 2px var(--holo-blue);
}

.cursor-block {
  display: inline-block;
  width: 0.6em; height: 1.2em;
  background: var(--holo-blue);
  animation: blink 0.8s step-end infinite;
  vertical-align: text-bottom;
  margin-left: 2px;
}

.retina-footer {
  padding: 0.8rem 1.5rem;
  border-top: 1px solid var(--border-tech);
  display: flex;
  justify-content: space-between;
  font-family: var(--font-tech);
  font-size: 0.7rem;
  color: var(--text-muted);
}

@keyframes scan { 0% { top: -10%; } 100% { top: 110%; } }
@keyframes blink { 50% { opacity: 0; } }

/* Transition */
.retina-fade-enter-active, .retina-fade-leave-active { transition: opacity 0.3s; }
.retina-fade-enter-from, .retina-fade-leave-to { opacity: 0; }
</style>
