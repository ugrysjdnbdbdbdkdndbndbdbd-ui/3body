<script setup lang="ts">
/**
 * 扇区 B：文明全息档案系统 (Chronicle + Archive + Encyclopedia + Apocrypha)
 * 整合四大知识模块，通过顶部维度切换器进行导航。
 */
import { ref, onMounted, computed, reactive } from 'vue'
import TechCard from '@/components/TechCard.vue'
import GalleryModule from '@/components/GalleryModule.vue'
import WikiModule from '@/components/WikiModule.vue'
import ApocryphaModule from '@/components/ApocryphaModule.vue'
import type { ChronicleEvent, ChronicleEventCreate } from '@/types/chronicle'
import { API, apiUrl, ERA_PRESETS, eventYearCE, normalizeEraYearInText } from '@/constants'
import { NModal, NButton, NForm, NFormItem, NInput, NInputNumber, NSelect, NSpace, NList, NListItem, NPopconfirm, useMessage } from 'naive-ui'
import { chronicleImageUrl } from '@/utils/imageFallback'

// 视图维度状态
type DimensionView = 'TIMELINE' | 'ARCHIVE' | 'ENCYCLOPEDIA' | 'APOCRYPHA'
const currentView = ref<DimensionView>('TIMELINE')

const events = ref<ChronicleEvent[]>([])
const loading = ref(true)
const selectedEvent = ref<ChronicleEvent | null>(null)
const showManageModal = ref(false)
const message = useMessage()

// Management (仅限 Timeline)
const isEditing = ref(false)
const editId = ref<number | null>(null)
const formData = reactive<ChronicleEventCreate>({
  era: '危机纪元',
  year: 2000,
  title: '',
  content: '',
  summary: '',
  image_url: '',
  event_type: 'pgc'
})

const eraOptions = ERA_PRESETS.map(e => ({ label: e, value: e }))
const typeOptions = [
  { label: 'PGC (正典)', value: 'pgc' },
  { label: 'UGC (变体)', value: 'ugc' }
]

function resetForm() {
  editId.value = null
  isEditing.value = false
  Object.assign(formData, {
    era: '危机纪元',
    year: 2000,
    title: '',
    content: '',
    summary: '',
    image_url: '',
    event_type: 'pgc'
  })
}

function openEdit(ev: ChronicleEvent) {
  editId.value = ev.id
  isEditing.value = true
  Object.assign(formData, {
    era: ev.era,
    year: ev.year,
    title: ev.title,
    content: ev.content,
    summary: ev.summary || '',
    image_url: ev.image_url || '',
    event_type: ev.event_type || 'pgc'
  })
}

async function handleDelete(id: number) {
  try {
    const res = await fetch(apiUrl(`${API.CHRONICLE_EVENTS}/${id}`), { method: 'DELETE' })
    if (!res.ok) throw new Error()
    message.success('已删除事件')
    loadEvents()
  } catch {
    message.error('删除失败')
  }
}

async function handleSave() {
  const url = editId.value 
    ? apiUrl(`${API.CHRONICLE_EVENTS}/${editId.value}`)
    : apiUrl(API.CHRONICLE_EVENTS)
  
  const method = editId.value ? 'PUT' : 'POST'
  
  try {
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    })
    if (!res.ok) throw new Error()
    message.success(editId.value ? '事件已更新' : '事件已创建')
    isEditing.value = false
    loadEvents()
  } catch {
    message.error('保存失败')
  }
}


async function loadEvents() {
  loading.value = true
  try {
    const res = await fetch(apiUrl(API.CHRONICLE_EVENTS))
    if (!res.ok) throw new Error()
    events.value = (await res.json()) as ChronicleEvent[]
  } catch {
    console.error('Failed to load events')
  } finally {
    loading.value = false
  }
}

// 时间之流：按公元纪年统一排序（纪元起点 + 纪元内年数）
const timelineData = computed(() => {
  return [...events.value].sort((a, b) => eventYearCE(a.era, a.year) - eventYearCE(b.era, b.year))
})

/** 纪元对应强调色（时间轴卡片左边框与节点点缀） */
const ERA_ACCENT: Record<string, string> = {
  '黄金时代': '#fbbf24',
  '危机纪元': '#ff4444',
  '威慑纪元': '#00ffff',
  '掩体纪元': '#a78bfa',
  '广播纪元': '#4ade80',
  '乱纪元': '#f97316',
  '银河纪元': '#e879f9',
}

function isSuperposition(ev: ChronicleEvent) {
  return (ev.causality_status || 'collapsed') === 'superposition' || ev.event_type === 'ugc'
}

function eraAccent(era: string): string {
  return ERA_ACCENT[era] ?? 'var(--holo-blue)'
}

/** 编年史视觉记录图 URL：优先 API，否则本地 /images/chronicles/{slug}.webp */
function chronicleEventImageUrl(ev: ChronicleEvent | null): string {
  if (!ev) return ''
  return chronicleImageUrl(ev.image_url, ev.title)
}

onMounted(loadEvents)
</script>

<template>
  <div class="sector-chronicle">
    <div class="chronicle-bg"></div>
    
    <header class="sector-header">
      <div class="header-left">
        <h1 class="title">CHRONICLE_System // 文明全息档案</h1>
        
        <!-- 维度切换器 -->
        <div class="dimension-switch">
          <button 
            class="dim-btn" 
            :class="{ active: currentView === 'TIMELINE' }"
            @click="currentView = 'TIMELINE'"
          >
            时间之流 [T]
          </button>
          <div class="dim-sep"></div>
          <button 
            class="dim-btn" 
            :class="{ active: currentView === 'ARCHIVE' }"
            @click="currentView = 'ARCHIVE'"
          >
            宇宙档案馆 [M]
          </button>
          <div class="dim-sep"></div>
          <button 
            class="dim-btn" 
            :class="{ active: currentView === 'ENCYCLOPEDIA' }"
            @click="currentView = 'ENCYCLOPEDIA'"
          >
            三体百科 [K]
          </button>
          <div class="dim-sep"></div>
          <button 
            class="dim-btn" 
            :class="{ active: currentView === 'APOCRYPHA' }"
            @click="currentView = 'APOCRYPHA'"
          >
            三体外传 [A]
          </button>
        </div>
      </div>

      <div class="header-right">
        <div v-if="currentView === 'TIMELINE'" class="legend">
          <span class="legend-item"><span class="dot solid"></span> 坍缩态</span>
          <span class="legend-item"><span class="dot dashed"></span> 叠加态</span>
          <span class="legend-hint">节点色＝纪元</span>
        </div>
        <NButton v-if="currentView === 'TIMELINE'" size="small" type="primary" ghost @click="showManageModal = true">
          <template #icon>⚡</template>
          管理条目
        </NButton>
      </div>
    </header>

    <!-- 视图容器 -->
    <div class="view-container">
      <transition name="dimension-fold" mode="out-in">
        
        <!-- 视图 A: 时间轴 -->
        <div v-if="currentView === 'TIMELINE'" key="timeline" class="timeline-container">
          <div class="timeline-track">
            <!-- 垂直中轴线 -->
            <div class="axis-line"></div>

            <div 
              v-for="(ev, index) in timelineData" 
              :key="ev.id"
              class="timeline-node"
              :class="{ 
                'is-superposition': isSuperposition(ev),
                'is-left': index % 2 === 0,
                'is-right': index % 2 !== 0,
                'is-selected': selectedEvent?.id === ev.id
              }"
              @click="selectedEvent = ev"
            >
              <!-- 时间标记：纪元 + 年份，紧凑 -->
              <div class="node-year" :style="{ color: eraAccent(ev.era) }">
                {{ ev.era }} · {{ ev.year }}
              </div>
              <div class="node-year-ce">公元 {{ eventYearCE(ev.era, ev.year) }}</div>
              
              <!-- 节点圆点 -->
              <div class="node-point">
                <div class="point-core" :style="{ background: eraAccent(ev.era), boxShadow: `0 0 10px ${eraAccent(ev.era)}` }"></div>
                <div class="point-ring"></div>
              </div>

              <!-- 事件卡片摘要：信息密度提升 -->
              <div class="node-content">
                <div class="content-box" :style="{ '--era-accent': eraAccent(ev.era) }">
                  <div class="ev-meta">
                    <span class="ev-type-badge" :class="ev.event_type === 'ugc' ? 'badge-ugc' : 'badge-pgc'">
                      {{ ev.event_type === 'ugc' ? 'UGC' : 'PGC' }}
                    </span>
                  </div>
                  <h3 class="ev-title">{{ normalizeEraYearInText(ev.era, ev.year, ev.title) }}</h3>
                  <p class="ev-summary line-clamp-3">{{ normalizeEraYearInText(ev.era, ev.year, ev.summary || ev.content) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 视图 B: 档案馆 -->
        <div v-else-if="currentView === 'ARCHIVE'" key="archive" class="gallery-container">
          <GalleryModule />
        </div>

        <!-- 视图 C: 三体百科 -->
        <div v-else-if="currentView === 'ENCYCLOPEDIA'" key="encyclopedia" class="wiki-container">
          <WikiModule />
        </div>

        <!-- 视图 D: 三体外传 -->
        <div v-else key="apocrypha" class="apocrypha-container">
          <ApocryphaModule />
        </div>

      </transition>
    </div>

    <!-- 侧边详情面板 (仅时间轴使用) -->
    <transition name="slide-panel">
      <div v-if="selectedEvent && currentView === 'TIMELINE'" class="detail-panel">
        <TechCard :title="normalizeEraYearInText(selectedEvent.era, selectedEvent.year, selectedEvent.title)" subtitle="EVENT_DETAIL" class="h-full">
          <div class="detail-body">
            <div class="meta-row">
              <span class="meta-tag meta-era" :style="{ color: eraAccent(selectedEvent.era), borderColor: eraAccent(selectedEvent.era) }">{{ selectedEvent.era }}</span>
              <span class="meta-tag">年份 {{ selectedEvent.year }}</span>
              <span class="meta-tag">公元 {{ eventYearCE(selectedEvent.era, selectedEvent.year) }}</span>
              <span class="meta-tag status-tag" :class="isSuperposition(selectedEvent) ? 'tag-warn' : 'tag-success'">
                {{ isSuperposition(selectedEvent) ? '叠加态' : '坍缩态' }}
              </span>
            </div>
            
            <div class="detail-text">
              {{ normalizeEraYearInText(selectedEvent.era, selectedEvent.year, selectedEvent.content) }}
            </div>

            <div v-if="chronicleEventImageUrl(selectedEvent)" class="detail-media">
              <img :src="chronicleEventImageUrl(selectedEvent)" alt="Event Visual" />
              <div class="media-overlay">视觉记录</div>
            </div>

            <button class="close-btn" @click="selectedEvent = null">关闭面板</button>
          </div>
        </TechCard>
      </div>
    </transition>

    <!-- 管理模态框 -->
    <NModal v-model:show="showManageModal" preset="card" title="编年史数据库 // 编辑器" style="width: 800px; max-width: 90vw;">
      <div class="manage-container">
        <!-- 复用之前的管理界面逻辑 -->
        <div v-if="!isEditing" class="list-view">
          <div class="mb-4 flex justify-between items-center">
            <span>事件总数: {{ events.length }}</span>
            <NButton type="primary" @click="resetForm(); isEditing = true">新建条目</NButton>
          </div>
          <NList hoverable clickable>
            <NListItem v-for="ev in events" :key="ev.id">
              <div class="flex justify-between items-center">
                <div class="flex-1">
                  <div class="font-bold">[{{ ev.era }}] {{ ev.year }} - {{ normalizeEraYearInText(ev.era, ev.year, ev.title) }}</div>
                  <div class="text-xs text-gray-500 truncate">{{ ev.summary }}</div>
                </div>
                <NSpace>
                  <NButton size="tiny" @click="openEdit(ev)">编辑</NButton>
                  <NPopconfirm @positive-click="handleDelete(ev.id)">
                    <template #trigger>
                      <NButton size="tiny" type="error" ghost>删</NButton>
                    </template>
                    确认删除?
                  </NPopconfirm>
                </NSpace>
              </div>
            </NListItem>
          </NList>
        </div>

        <div v-else class="edit-view">
          <div class="mb-4 flex justify-between items-center">
            <h3 class="text-lg font-bold">{{ editId ? '编辑节点' : '注入节点' }}</h3>
            <NButton size="small" @click="isEditing = false">返回列表</NButton>
          </div>
          <NForm :model="formData" label-placement="left" label-width="80">
            <NFormItem label="纪元">
              <NSelect v-model:value="formData.era" :options="eraOptions" />
            </NFormItem>
            <NFormItem label="年份">
              <NInputNumber v-model:value="formData.year" />
            </NFormItem>
            <NFormItem label="标题">
              <NInput v-model:value="formData.title" />
            </NFormItem>
            <NFormItem label="摘要">
              <NInput v-model:value="formData.summary" type="textarea" :rows="2" />
            </NFormItem>
            <NFormItem label="正文">
              <NInput v-model:value="formData.content" type="textarea" :rows="5" />
            </NFormItem>
            <NFormItem label="图片URL">
              <NInput v-model:value="formData.image_url" />
            </NFormItem>
            <NFormItem label="类型">
              <NSelect v-model:value="formData.event_type" :options="typeOptions" />
            </NFormItem>
            <div class="flex justify-end gap-2">
              <NButton @click="isEditing = false">取消</NButton>
              <NButton type="primary" @click="handleSave">提交更改</NButton>
            </div>
          </NForm>
        </div>
      </div>
    </NModal>
  </div>
</template>

<style scoped>
.sector-chronicle {
  position: relative;
  /* Allow natural height */
  display: flex;
  flex-direction: column;
}

.chronicle-bg {
  position: fixed;
  inset: 0;
  background: 
    linear-gradient(90deg, rgba(0,240,255,0.03) 1px, transparent 1px),
    linear-gradient(rgba(0,240,255,0.03) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
  z-index: 0;
}

.sector-header {
  position: relative;
  z-index: 10;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-tech);
  background: rgba(2,6,23,0.8);
  backdrop-filter: blur(10px);
}

.title {
  font-family: var(--font-tech);
  color: var(--holo-blue);
  font-size: 1.2rem;
  letter-spacing: 0.1em;
  margin: 0;
  margin-bottom: 0.5rem;
}

/* 维度切换器 */
.dimension-switch {
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--border-tech);
  border-radius: 4px;
  background: rgba(0, 240, 255, 0.05);
  padding: 2px;
}

.dim-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-family: var(--font-tech);
  font-size: 0.75rem;
  padding: 0.4rem 1rem;
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 2px;
}

.dim-btn.active {
  background: rgba(0, 240, 255, 0.15);
  color: var(--holo-blue);
  text-shadow: 0 0 5px var(--holo-blue);
  box-shadow: 0 0 10px rgba(0, 240, 255, 0.1);
}

.dim-sep {
  width: 1px;
  height: 12px;
  background: var(--border-tech);
  margin: 0 4px;
}

.legend {
  display: flex;
  gap: 1rem;
  font-family: var(--font-tech);
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-right: 1.5rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.dot.solid { background: var(--holo-blue); box-shadow: 0 0 5px var(--holo-blue); }
.dot.dashed { border: 1px solid var(--holo-green); background: transparent; }
.legend-hint { font-size: 0.65rem; color: var(--text-muted); margin-left: 0.5rem; }

/* View Container */
.view-container {
  position: relative;
  min-height: 80vh;
}

.timeline-container {
  padding: 4rem 0;
  position: relative;
  z-index: 1;
}

.gallery-container, .wiki-container, .apocrypha-container {
  padding: 2rem 0;
}

/* 维度折叠转场 */
.dimension-fold-enter-active,
.dimension-fold-leave-active {
  transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

.dimension-fold-enter-from {
  opacity: 0;
  transform: scaleY(0.01) scaleX(1.5); /* 从一条线展开 */
  filter: blur(10px);
}

.dimension-fold-leave-to {
  opacity: 0;
  transform: scaleY(0.01) scaleX(1.5); /* 压缩成一条线 */
  filter: blur(10px);
}

/* 时间之流：信息密度与展示样式优化，避免文字被遮挡 */
.timeline-track { position: relative; max-width: 900px; margin: 0 auto; padding-top: 1rem; padding-bottom: 3rem; }
.axis-line { position: absolute; top: 0; bottom: 0; left: 50%; width: 2px; background: linear-gradient(180deg, transparent, var(--holo-blue), transparent); transform: translateX(-50%); box-shadow: 0 0 12px var(--holo-blue); overflow: hidden; }
.axis-line::after { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 50%; background: linear-gradient(180deg, transparent, rgba(255,255,255,0.4), transparent); opacity: 0.4; animation: flow 3s linear infinite; }
@keyframes flow { 0% { top: -50%; } 100% { top: 100%; } }
.node-point { position: absolute; left: 50%; top: 2.5rem; transform: translateX(-50%); width: 22px; height: 22px; z-index: 2; display: flex; align-items: center; justify-content: center; background: var(--bg-deep); border-radius: 50%; }
.point-core { width: 8px; height: 8px; border-radius: 50%; z-index: 2; transition: transform 0.25s ease; }
.point-ring { position: absolute; width: 100%; height: 100%; border: 1px solid var(--holo-blue); border-radius: 50%; animation: spin 10s linear infinite; box-shadow: 0 0 5px rgba(0, 240, 255, 0.2); }
.point-ring::before { content: ''; position: absolute; top: -2px; left: 50%; transform: translateX(-50%); width: 4px; height: 4px; background: var(--holo-blue); border-radius: 50%; }
.is-superposition .point-ring { border-color: var(--holo-green); border-style: dashed; animation: spin 5s linear infinite reverse; }
.is-superposition .point-ring::before { background: var(--holo-green); }
.timeline-node { position: relative; min-height: 130px; margin-bottom: 3.5rem; width: 100%; display: flex; justify-content: center; cursor: pointer; transition: all 0.25s ease; }
.timeline-node:hover { filter: brightness(1.15); }
.timeline-node.is-selected .content-box { border-color: var(--holo-blue); box-shadow: 0 0 20px rgba(0, 240, 255, 0.25); }
.node-year { position: absolute; left: 50%; top: 0; transform: translateX(-50%); font-family: var(--font-tech); font-size: 0.7rem; font-weight: 600; letter-spacing: 0.05em; background: rgba(2,6,23,0.9); padding: 0.25rem 0.6rem; border: 1px solid var(--border-tech); border-radius: 2px; white-space: nowrap; z-index: 1; }
.node-year-ce { position: absolute; left: 50%; top: 1.35rem; transform: translateX(-50%); font-family: var(--font-tech); font-size: 0.65rem; color: var(--text-muted); opacity: 0.9; z-index: 1; }
.node-content { width: 42%; min-width: 260px; position: absolute; top: 2rem; bottom: 0; }
.is-left .node-content { left: 0; text-align: right; }
.is-right .node-content { right: 0; left: auto; text-align: left; }
.content-box { background: rgba(2, 6, 23, 0.88); border: 1px solid var(--border-tech); padding: 1rem 1.15rem 1.2rem; border-radius: 3px; transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1); position: relative; overflow: hidden; min-height: 4.5rem; }
.content-box::before { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: var(--era-accent, var(--holo-blue)); opacity: 0.7; }
.is-superposition .content-box::before { background: var(--holo-green); }
.timeline-node:hover .content-box { transform: translateY(-2px) scale(1.02); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45); }
.timeline-node:hover .content-box::before { opacity: 1; }
.timeline-node:hover .point-core { transform: scale(1.4); }
.ev-meta { margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.4rem; }
.is-right .ev-meta { justify-content: flex-start; }
.is-left .ev-meta { justify-content: flex-end; }
.ev-type-badge { font-family: var(--font-tech); font-size: 0.6rem; padding: 0.15rem 0.4rem; border-radius: 2px; letter-spacing: 0.05em; }
.ev-type-badge.badge-pgc { background: rgba(0, 240, 255, 0.12); color: var(--holo-blue); border: 1px solid rgba(0, 240, 255, 0.4); }
.ev-type-badge.badge-ugc { background: rgba(0, 255, 65, 0.1); color: var(--holo-green); border: 1px solid rgba(0, 255, 65, 0.4); }
.ev-title { font-family: var(--font-tech); color: var(--holo-blue); margin: 0 0 0.5rem; font-size: 0.95rem; font-weight: 600; line-height: 1.3; text-shadow: 0 0 6px rgba(0, 240, 255, 0.25); }
.is-superposition .ev-title { color: var(--holo-green); text-shadow: 0 0 6px rgba(0, 255, 65, 0.25); }
.ev-summary { font-size: 0.78rem; color: var(--text-muted); margin: 0 0 0.25rem; line-height: 1.5; display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 3; overflow: hidden; }

/* Detail Panel */
.detail-panel { position: fixed; top: 60px; right: 0; bottom: 0; width: 400px; max-width: 90vw; z-index: 50; padding: 1rem; }
.detail-body { display: flex; flex-direction: column; gap: 1.5rem; height: 100%; }
.meta-row { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.meta-tag { font-family: var(--font-tech); font-size: 0.7rem; padding: 0.2rem 0.5rem; border: 1px solid var(--border-tech); color: var(--holo-blue); }
.status-tag.tag-warn { color: var(--holo-green); border-color: var(--holo-green); }
.status-tag.tag-success { color: var(--holo-blue); border-color: var(--holo-blue); }
.detail-text { font-size: 0.9rem; line-height: 1.6; color: var(--text); flex: 1; overflow-y: auto; }
.detail-media { position: relative; border: 1px solid var(--border-tech); overflow: hidden; }
.detail-media img { width: 100%; display: block; }
.media-overlay { position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,0.7); padding: 0.3rem; font-family: var(--font-tech); font-size: 0.7rem; color: var(--holo-blue); text-align: center; }
.close-btn { width: 100%; padding: 0.8rem; background: transparent; border: 1px solid var(--border-tech); color: var(--text-muted); font-family: var(--font-tech); cursor: pointer; transition: all 0.2s; }
.close-btn:hover { background: rgba(255,255,255,0.1); color: var(--text); }

/* Transitions & Anim */
.slide-panel-enter-active, .slide-panel-leave-active { transition: transform 0.3s ease; }
.slide-panel-enter-from, .slide-panel-leave-to { transform: translateX(100%); }
@keyframes pulse { 0% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.5); opacity: 0; } 100% { transform: scale(1); opacity: 0; } }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.header-left { display: flex; flex-direction: column; gap: 0.5rem; }
.header-right { display: flex; align-items: center; }
.manage-container { max-height: 70vh; overflow-y: auto; }
</style>
