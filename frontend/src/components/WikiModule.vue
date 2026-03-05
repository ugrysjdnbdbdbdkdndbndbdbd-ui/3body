<script setup lang="ts">
/**
 * WikiModule.vue - 三体百科 (The Encyclopedia)
 * 数据源：/api/chronicle/encyclopedia（data/encyclopedia.json）
 * 交互：思想钢印注入模式，点击词条展开详情
 */
import { ref, computed, onMounted } from 'vue'
import { API, apiUrl } from '@/constants'

interface WikiEntry {
  id: string
  term: string
  category: string
  summary: string
  detail?: string
  tags: string[]
}

const entries = ref<WikiEntry[]>([])
const loading = ref(true)

/** API 返回形状 */
interface EncyclopediaItem {
  id: string
  term: string
  category: string
  definition: string
  explanation: string
  related_terms?: string[]
}

const CATEGORY_LABELS: Record<string, string> = {
  Theory: '理论',
  Technology: '技术',
  Weapon: '武器',
  History: '历史',
  Cosmology: '宇宙学',
  Culture: '文化',
  Biology: '生物',
  Civilization: '文明',
  Character: '人物',
  Location: '地点',
  Organization: '组织',
}

const activeCategory = ref<string>('ALL')
const selectedEntry = ref<WikiEntry | null>(null)

const filteredEntries = computed(() => {
  if (activeCategory.value === 'ALL') return entries.value
  return entries.value.filter(e => e.category === activeCategory.value)
})

const categories = computed(() => {
  const base = [{ label: '全库', value: 'ALL' }]
  const seen = new Set<string>()
  for (const e of entries.value) {
    if (e.category && !seen.has(e.category)) {
      seen.add(e.category)
      base.push({ label: CATEGORY_LABELS[e.category] ?? e.category, value: e.category })
    }
  }
  return base
})

function getCategoryColor(cat: string): string {
  const colors: Record<string, string> = {
    Civilization: 'var(--holo-red)',
    Technology: 'var(--holo-blue)',
    Weapon: '#ff6b6b',
    Theory: '#fbbf24',
    Phenomenon: '#fbbf24',
    Cosmology: '#a78bfa',
    History: 'var(--holo-green)',
    Character: '#22d3ee',
    Location: '#4ade80',
    Organization: '#fb923c',
    Culture: '#e879f9',
    Biology: '#2dd4bf',
  }
  return colors[cat] ?? 'var(--text-muted)'
}

async function loadEncyclopedia() {
  loading.value = true
  try {
    const res = await fetch(apiUrl(API.CHRONICLE_ENCYCLOPEDIA))
    if (!res.ok) throw new Error('Encyclopedia fetch failed')
    const data = await res.json()
    if (Array.isArray(data) && data.length > 0) {
      entries.value = (data as EncyclopediaItem[]).map(item => ({
        id: item.id,
        term: item.term,
        category: item.category,
        summary: item.definition,
        detail: item.explanation,
        tags: Array.isArray(item.related_terms) ? item.related_terms : [],
      }))
    }
  } catch {
    // Fallback Data
    entries.value = [
      {
        id: 'THEORY-001',
        term: '黑暗森林法则 (Dark Forest)',
        category: 'Theory',
        summary: '宇宙社会学的核心公理。宇宙是一座黑暗森林，每个文明都是带枪的猎人。',
        detail: '一旦发现别的生命，能做的只有一件事：开枪消灭之。在这片森林中，他人就是地狱，就是永恒的威胁，任何暴露自己存在的生命都将很快被消灭。',
        tags: ['Cosmic Sociology', 'Axiom', 'Luo Ji']
      },
      {
        id: 'TECH-001',
        term: '水滴 (The Droplet)',
        category: 'Weapon',
        summary: '三体文明的强互作用力探测器。',
        detail: '表面绝对光滑，由被强互作用力紧密锁死的质子构成，其强度超过太阳系已知任何材料。在末日战役中，仅凭一颗水滴就摧毁了人类两千艘恒星级战舰。',
        tags: ['Strong Interaction', 'Doomsday Battle']
      },
      {
        id: 'CIV-001',
        term: '歌者 (Singer)',
        category: 'Civilization',
        summary: '清理者文明的底层职员。',
        detail: '所在的文明被称为“清理者”或“神级文明”。他们习惯于将宇宙规律武器化（如降低光速、维度打击）。歌者随手向太阳系投掷了一片二向箔，导致太阳系二维化。',
        tags: ['2D Foil', 'Entropy', 'Cleaner']
      },
      {
        id: 'CIV-002',
        term: '归零者 (Zero-Homer)',
        category: 'Civilization',
        summary: '致力于重启宇宙的神级文明。',
        detail: '也被称为“回归运动”。他们试图通过将宇宙的总质量回归到临界值，从而使宇宙坍缩并重启，回到十维的田园时代。',
        tags: ['Reset', '10th Dimension', 'Macro-Universe']
      },
      {
        id: 'CHAR-001',
        term: '章北海 (Zhang Beihai)',
        category: 'Character',
        summary: '第五位面壁者（非官方），自然选择号舰长。',
        detail: '深沉、冷酷、坚定的逃亡主义者。他不仅骗过了人类，也骗过了三体人。在最后一刻，他果断劫持“自然选择”号逃离太阳系，为人类文明保留了火种。',
        tags: ['Natural Selection', 'Escapism', 'Hero']
      },
      {
        id: 'TECH-002',
        term: '二向箔 (Dual Vector Foil)',
        category: 'Weapon',
        summary: '维度打击武器，将三维空间坍缩为二维。',
        detail: '一种封装在力场中的规律武器。一旦力场消失，它会无限膨胀，将周围的三维空间“跌落”至二维，所有三维物质的厚度瞬间归零，展现出无限的细节。',
        tags: ['Dimensional Strike', 'Singer', 'Solar System']
      },
      {
        id: 'THEORY-002',
        term: '猜疑链 (Chain of Suspicion)',
        category: 'Theory',
        summary: '两个文明无法判断对方是否善意。',
        detail: '“不管你是否善意，我无法判断你是否认为我是善意的……”这种无限循环的猜疑，导致两个文明之间无法建立信任，最终导向先发制人的打击。',
        tags: ['Cosmic Sociology', 'Axiom']
      },
      {
        id: 'CHAR-002',
        term: '托马斯·维德 (Thomas Wade)',
        category: 'Character',
        summary: '阶梯计划负责人，光速飞船计划领导者。',
        detail: '“失去人性，失去很多；失去兽性，失去一切。”他是绝对理性的化身，为了人类的生存可以不择手段。如果他成为了执剑人，三体人绝不敢进犯。',
        tags: ['Advance', 'Deterrence', 'Anti-Matter']
      },
      {
        id: 'LOC-001',
        term: '红岸基地 (Red Coast Base)',
        category: 'Location',
        summary: '人类第一次向宇宙发送信号的地方。',
        detail: '位于大兴安岭雷达峰。叶文洁在这里向太阳发射了增益电波，回复了三体世界的信号，从而按下了人类命运的倒计时开关。',
        tags: ['Ye Wenjie', 'Signal', 'Beginning']
      },
      {
        id: 'ORG-001',
        term: 'ETO (Earth-Trisolaris Org)',
        category: 'Organization',
        summary: '地球三体组织，人类的背叛者。',
        detail: '由伊文斯和叶文洁创立。分为降临派（由于对人类绝望而希望三体主来毁灭人类）、拯救派（崇拜三体文明）和幸存派。',
        tags: ['Rebels', 'Sophon', 'Judgment Day']
      },
      {
        id: 'TECH-003',
        term: '曲率驱动 (Curvature Propulsion)',
        category: 'Technology',
        summary: '光速飞船的引擎技术。',
        detail: '通过熨平空间曲率来驱动飞船，可以达到光速。但其副作用是会留下“航迹”，即低光速黑洞，这实际上也是一种宇宙安全声明。',
        tags: ['Lightspeed', 'Safety Declaration', 'Yun Tianming']
      },
      {
        id: 'BIO-001',
        term: '脱水 (Dehydration)',
        category: 'Biology',
        summary: '三体人的生存技能。',
        detail: '在乱纪元来临时，三体人可以排出体内的水分，变成一张干皮，储存在干仓中休眠，以度过漫长的恶劣环境。浸泡后可复活。',
        tags: ['Survival', 'Chaotic Era', 'Biology']
      }
    ]
  } finally {
    loading.value = false
  }
}

onMounted(loadEncyclopedia)
</script>

<template>
  <div class="wiki-module">
    <!-- 过滤器 -->
    <div class="wiki-filter">
      <button 
        v-for="cat in categories" 
        :key="cat.value"
        class="filter-tab"
        :class="{ active: activeCategory === cat.value }"
        @click="activeCategory = cat.value"
      >
        {{ cat.label }}
      </button>
    </div>

    <!-- 晶体矩阵列表 -->
    <div v-if="loading" class="wiki-loading">智子正在同步词库…</div>
    <div v-else class="wiki-grid">
      <div 
        v-for="item in filteredEntries" 
        :key="item.id" 
        class="wiki-card"
        :style="{ '--cat-color': getCategoryColor(item.category) }"
        @click="selectedEntry = item"
      >
        <div class="card-edge top-left"></div>
        <div class="card-edge bottom-right"></div>
        
        <div class="wiki-header">
          <span class="cat-tag">{{ item.category }}</span>
          <h3 class="wiki-term">{{ item.term }}</h3>
        </div>
        
        <p class="wiki-summary">{{ item.summary }}</p>
        
        <div class="wiki-tags">
          <span v-for="tag in item.tags" :key="tag" class="wiki-tag">#{{ tag }}</span>
        </div>

        <div class="card-glow"></div>
      </div>
    </div>

    <!-- 神经连接详情页 (Mental Seal Modal) -->
    <transition name="seal-expand">
      <div v-if="selectedEntry" class="seal-overlay" @click.self="selectedEntry = null">
        <div class="seal-container" :style="{ '--seal-color': getCategoryColor(selectedEntry.category) }">
          <div class="seal-header">
            <h2 class="seal-title">{{ selectedEntry.term }}</h2>
            <div class="seal-meta">
              <span>CATEGORY: {{ selectedEntry.category }}</span>
              <span>INDEX: {{ selectedEntry.id.toUpperCase() }}</span>
            </div>
          </div>
          
          <div class="seal-body">
            <div class="seal-line-deco"></div>
            <p class="seal-text">{{ selectedEntry.detail || selectedEntry.summary }}</p>
            
            <div class="seal-tags-large">
              <span v-for="tag in selectedEntry.tags" :key="tag" class="tag-large">
                {{ tag }}
              </span>
            </div>
          </div>

          <div class="seal-footer">
            <button class="seal-close" @click="selectedEntry = null">断开连接</button>
            <span class="seal-status">MENTAL SEAL IMPRINTING... 100%</span>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.wiki-module { padding: 1rem; width: 100%; }
.wiki-loading { font-family: var(--font-tech); color: var(--text-muted); padding: 3rem; text-align: center; }

/* Filter Styles */
.wiki-filter { display: flex; gap: 1rem; margin-bottom: 2rem; border-bottom: 1px solid var(--border-tech); padding-bottom: 0.5rem; }
.filter-tab { background: transparent; border: none; color: var(--text-muted); font-family: var(--font-tech); font-size: 0.8rem; padding: 0.5rem 1rem; cursor: pointer; transition: all 0.3s; position: relative; }
.filter-tab.active { color: var(--holo-blue); text-shadow: 0 0 5px var(--holo-blue); }
.filter-tab.active::after { content: ''; position: absolute; bottom: -0.6rem; left: 0; width: 100%; height: 2px; background: var(--holo-blue); box-shadow: 0 0 10px var(--holo-blue); }

/* Grid Styles */
.wiki-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem; }
.wiki-card { position: relative; background: rgba(2, 6, 23, 0.4); border: 1px solid rgba(255, 255, 255, 0.05); padding: 1.5rem; transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); overflow: hidden; cursor: pointer; }
.wiki-card:hover { transform: translateY(-5px); background: rgba(2, 6, 23, 0.8); border-color: var(--cat-color); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(255, 255, 255, 0.02); }
.card-edge { position: absolute; width: 10px; height: 10px; border: 2px solid var(--cat-color); opacity: 0.5; transition: all 0.3s; }
.top-left { top: 0; left: 0; border-right: none; border-bottom: none; }
.bottom-right { bottom: 0; right: 0; border-left: none; border-top: none; }
.wiki-card:hover .card-edge { width: 100%; height: 100%; opacity: 1; }
.wiki-header { margin-bottom: 1rem; }
.cat-tag { font-family: var(--font-tech); font-size: 0.6rem; color: var(--cat-color); letter-spacing: 0.1em; opacity: 0.8; }
.wiki-term { margin: 0.2rem 0 0 0; font-family: var(--font-display); font-size: 1.2rem; color: #fff; font-weight: 300; }
.wiki-summary { font-size: 0.8rem; color: var(--text-muted); line-height: 1.6; margin-bottom: 1.5rem; height: 3.2em; overflow: hidden; }
.wiki-tags { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.wiki-tag { font-size: 0.7rem; color: var(--cat-color); background: rgba(255, 255, 255, 0.05); padding: 0.2rem 0.5rem; border-radius: 2px; font-family: var(--font-tech); }
.card-glow { position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, var(--cat-color) 0%, transparent 60%); opacity: 0; transform: scale(0.5); transition: all 0.5s; pointer-events: none; mix-blend-mode: screen; }
.wiki-card:hover .card-glow { opacity: 0.1; transform: scale(1); }

/* --- Mental Seal Modal --- */
.seal-overlay { position: fixed; inset: 0; z-index: 200; background: rgba(0, 0, 0, 0.8); backdrop-filter: blur(8px); display: flex; align-items: center; justify-content: center; }
.seal-container { width: 90%; max-width: 600px; border: 1px solid var(--seal-color); background: rgba(5, 10, 20, 0.95); position: relative; padding: 2rem; box-shadow: 0 0 50px rgba(0, 0, 0, 0.8), inset 0 0 20px rgba(255, 255, 255, 0.05); }
.seal-header { border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 1rem; margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: flex-end; }
.seal-title { font-family: var(--font-display); font-size: 2rem; color: var(--seal-color); margin: 0; text-shadow: 0 0 15px var(--seal-color); }
.seal-meta { display: flex; flex-direction: column; text-align: right; font-family: var(--font-tech); font-size: 0.7rem; color: var(--text-muted); gap: 0.3rem; }
.seal-body { position: relative; margin-bottom: 2rem; }
.seal-line-deco { position: absolute; left: -2rem; top: 0; bottom: 0; width: 2px; background: linear-gradient(180deg, var(--seal-color), transparent); }
.seal-text { font-size: 1rem; line-height: 1.8; color: #fff; margin-bottom: 2rem; white-space: pre-wrap; }
.seal-tags-large { display: flex; gap: 0.8rem; }
.tag-large { font-family: var(--font-tech); font-size: 0.8rem; border: 1px solid var(--seal-color); color: var(--seal-color); padding: 0.3rem 0.8rem; background: rgba(255,255,255,0.05); }
.seal-footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 1rem; }
.seal-close { background: transparent; border: 1px solid var(--text-muted); color: var(--text-muted); padding: 0.5rem 1.5rem; cursor: pointer; font-family: var(--font-tech); transition: all 0.2s; }
.seal-close:hover { border-color: #fff; color: #fff; }
.seal-status { font-family: var(--font-tech); font-size: 0.7rem; color: var(--seal-color); animation: blink 2s infinite; }

/* Transitions */
.seal-expand-enter-active, .seal-expand-leave-active { transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
.seal-expand-enter-from, .seal-expand-leave-to { opacity: 0; transform: scale(0.9); filter: blur(10px); }
@keyframes blink { 50% { opacity: 0.5; } }
</style>
