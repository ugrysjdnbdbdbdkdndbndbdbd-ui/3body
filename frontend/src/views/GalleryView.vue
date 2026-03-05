<script setup lang="ts">
/**
 * Sector D: Dual Vector Foil (二向箔 / 画廊)
 * 核心：降维滤镜 (2D Filter) & 冥王星的雪 (Snow of Pluto)
 * 风格：油画质感、金色与深蓝漩涡 (Van Gogh Style)
 * 优化：全面汉化
 */
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import { NTabs, NTabPane, NUpload, NButton, useMessage, NGrid, NGridItem } from 'naive-ui'

const message = useMessage()
const activeTab = ref('filter')

// --- Tab 1: Dimensional Strike (2D Filter) ---
const imageUrl = ref<string | null>(null)
const isFlattening = ref(false)
const flattenProgress = ref(0)
const turbulenceFreq = ref(0.01) // SVG Filter 动态参数

const filterSettings = reactive({
  flatness: 0,
  contrast: 100,
  saturation: 100,
  sepia: 0,
  hueRotate: 0
})

function handleFileUpload(file: File) {
  const reader = new FileReader()
  reader.onload = (e) => {
    imageUrl.value = e.target?.result as string
    resetFilter()
  }
  reader.readAsDataURL(file)
  return false 
}

function resetFilter() {
  flattenProgress.value = 0
  isFlattening.value = false
  turbulenceFreq.value = 0.01
  filterSettings.flatness = 0
  filterSettings.contrast = 100
  filterSettings.saturation = 100
  filterSettings.sepia = 0
  filterSettings.hueRotate = 0
}

function startStrike() {
  if (!imageUrl.value) return
  isFlattening.value = true
  flattenProgress.value = 0
  
  const interval = setInterval(() => {
    flattenProgress.value += 0.5 
    const p = flattenProgress.value

    filterSettings.flatness = p
    filterSettings.contrast = 100 + p * 2 
    filterSettings.saturation = 100 + p * 1.5 
    filterSettings.sepia = p * 0.3 
    filterSettings.hueRotate = p * 0.5 
    
    turbulenceFreq.value = 0.01 + (p / 2000) 
    
    if (flattenProgress.value >= 100) {
      clearInterval(interval)
      message.success('降维打击完成。对象已跌落至二维。')
      turbulenceFreq.value = 0 
    }
  }, 30)
}

// --- Tab 2: Snow of Pluto (Scene) ---
const canvasRef = ref<HTMLCanvasElement | null>(null)
let snowAnimId: number

function initSnow() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight * 0.8
  
  const particles: { x: number, y: number, r: number, d: number, color: string }[] = []
  for (let i = 0; i < 300; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      r: Math.random() * 2 + 0.5,
      d: Math.random() * 20 + 10,
      color: Math.random() > 0.9 ? '#ffd700' : '#ffffff' 
    })
  }
  
  function draw() {
    if (!canvas || !ctx) return
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    const grd = ctx.createLinearGradient(0, 0, 0, canvas.height)
    grd.addColorStop(0, '#020210')
    grd.addColorStop(1, '#000000')
    ctx.fillStyle = grd
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    for (const p of particles) {
      ctx.beginPath()
      ctx.fillStyle = p.color
      ctx.shadowBlur = p.color === '#ffd700' ? 10 : 0
      ctx.shadowColor = '#ffd700'
      ctx.moveTo(p.x, p.y)
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2, true)
      ctx.fill()
    }
    
    for (const p of particles) {
      p.y += Math.cos(p.d) + 1 + p.r / 2
      p.x += Math.sin(p.d) * 0.5 
      
      if (p.x > canvas.width + 5 || p.x < -5 || p.y > canvas.height) {
        if (Math.random() > 0.3) {
          p.x = Math.random() * canvas.width
          p.y = -10
        } else {
          p.x = Math.random() > 0.5 ? -5 : canvas.width + 5
          p.y = Math.random() * canvas.height
        }
      }
    }
    
    snowAnimId = requestAnimationFrame(draw)
  }
  draw()
}

function handleTabUpdate(v: string | number) {
  if (String(v) === 'pluto') {
    window.setTimeout(initSnow, 100)
  }
}

onMounted(() => {
  if (activeTab.value === 'pluto') initSnow()
})

onUnmounted(() => {
  cancelAnimationFrame(snowAnimId)
})

// --- Tab 3: Gallery (Collection) ---
const fallenWorks = [
  { id: 1, title: '星月夜', era: '公元 1889', desc: '危机前艺术', color: 'linear-gradient(135deg, #1a237e, #fdd835)' },
  { id: 2, title: '呐喊', era: '公元 1893', desc: '早期焦虑', color: 'linear-gradient(135deg, #e65100, #3e2723)' },
  { id: 3, title: '太阳系防御阵列', era: '掩体纪元', desc: '掩体主体结构', color: 'linear-gradient(135deg, #000000, #424242)' },
  { id: 4, title: '蓝色空间号', era: '银河纪元', desc: '战舰残骸', color: 'linear-gradient(135deg, #0d47a1, #00acc1)' },
]
</script>

<template>
  <div class="sector-d">
    <div class="header">
      <div class="header-content">
        <h1 class="title">SECTOR D // DUAL VECTOR FOIL</h1>
        <div class="deco-line"></div>
        <p class="subtitle">二向箔 · 画廊 · 冥王星的雪</p>
      </div>
    </div>

    <NTabs 
      v-model:value="activeTab" 
      type="line" 
      animated
      class="d-tabs" 
      @update:value="handleTabUpdate"
    >
      <!-- Tab 1: Dimensional Strike -->
      <NTabPane name="filter" tab="降维打击 (DIMENSIONAL STRIKE)">
        <div class="filter-studio">
          <div class="studio-main">
            <div class="canvas-frame">
              <div 
                class="image-preview" 
                :class="{ 'is-flat': flattenProgress >= 100 }"
                :style="{ 
                  backgroundImage: imageUrl ? `url(${imageUrl})` : 'none',
                  filter: `
                    contrast(${filterSettings.contrast}%) 
                    saturate(${filterSettings.saturation}%) 
                    sepia(${filterSettings.sepia}%)
                    hue-rotate(${filterSettings.hueRotate}deg)
                  `
                }"
              >
                <div v-if="!imageUrl" class="upload-area">
                  <div class="upload-cta">
                    <div class="upload-icon" aria-hidden="true">↑</div>
                    <p class="upload-hint">选择一张三维图像，启动降维打击</p>
                    <NUpload :show-file-list="false" @before-upload="data => handleFileUpload(data.file.file as File)">
                      <NButton color="#d4af37" ghost round class="upload-btn">上传图像</NButton>
                    </NUpload>
                    <span class="upload-sub">支持 JPG、PNG</span>
                  </div>
                </div>

                <!-- 降维扫描线 -->
                <div v-if="isFlattening && flattenProgress < 100" class="scan-line" :style="{ top: `${100 - flattenProgress}%` }"></div>
                
                <!-- SVG Filter -->
                <svg v-if="imageUrl" class="filter-svg">
                  <filter id="distortion">
                    <feTurbulence type="turbulence" :baseFrequency="turbulenceFreq" numOctaves="2" result="noise" />
                    <feDisplacementMap in="SourceGraphic" in2="noise" :scale="filterSettings.flatness * 0.5" />
                  </filter>
                </svg>
              </div>
              
              <!-- 覆盖层 -->
              <div 
                v-if="imageUrl"
                class="filter-overlay"
                :style="{ 
                  backgroundImage: `url(${imageUrl})`,
                  filter: 'url(#distortion)',
                  opacity: flattenProgress > 0 ? 1 : 0
                }"
              ></div>
            </div>
            
            <div class="controls-panel">
              <div class="monitor-screen">
                <div class="monitor-row">
                  <span>维度 / DIMENSION</span>
                  <span class="monitor-val">{{ isFlattening ? (3 - flattenProgress * 0.01).toFixed(4) : '3.0000' }}</span>
                </div>
                <div class="monitor-row">
                  <span>逃逸速度 / V-ESCAPE</span>
                  <span class="monitor-val">{{ isFlattening ? (flattenProgress > 50 ? '∞ (光速不可逃逸)' : '299,792 km/s') : '16.7 km/s' }}</span>
                </div>
                <div class="monitor-row">
                  <span>熵值 / ENTROPY</span>
                  <span class="monitor-val">{{ (flattenProgress * 8.5).toFixed(1) }} J/K</span>
                </div>
                <div class="monitor-bar">
                  <div class="monitor-fill" :style="{ width: `${flattenProgress}%` }"></div>
                </div>
              </div>

              <NButton 
                class="strike-btn"
                :type="isFlattening ? 'default' : 'warning'"
                :loading="isFlattening && flattenProgress < 100"
                :disabled="!imageUrl || (isFlattening && flattenProgress < 100)"
                block
                size="large"
                @click="startStrike"
              >
                {{ flattenProgress >= 100 ? '重置目标 (RESET)' : (isFlattening ? '降维中 (FLATTENING)...' : '启动降维打击 (INITIATE STRIKE)') }}
              </NButton>
              
              <div class="lore-box" v-if="flattenProgress >= 100">
                <p>"针眼画师...... 把这个世界画进画里。"</p>
              </div>
            </div>
          </div>
        </div>
      </NTabPane>

      <!-- Tab 2: Gallery Collection -->
      <NTabPane name="collection" tab="沉没的画廊 (FALLEN GALLERY)">
        <div class="gallery-hall">
          <div class="gallery-intro">
            <h2>二维世界收藏</h2>
            <p>这里收藏着那些已经被二维化的文明碎片。它们永远静止在绝对平面中，虽然失去了厚度，却获得了永恒。</p>
          </div>
          <NGrid x-gap="24" y-gap="24" cols="1 s:2 m:4" responsive="screen">
            <NGridItem v-for="work in fallenWorks" :key="work.id">
              <div class="art-frame">
                <div class="art-canvas" :style="{ background: work.color }">
                  <div class="art-glitch"></div>
                </div>
                <div class="art-info">
                  <div class="art-title">{{ work.title }}</div>
                  <div class="art-meta">{{ work.era }} // {{ work.desc }}</div>
                </div>
              </div>
            </NGridItem>
          </NGrid>
        </div>
      </NTabPane>

      <!-- Tab 3: Snow of Pluto -->
      <NTabPane name="pluto" tab="冥王星的雪 (SNOW OF PLUTO)">
        <div class="pluto-scene">
          <canvas ref="canvasRef" class="snow-canvas"></canvas>
          <div class="scene-overlay">
            <div class="dialogue-card">
              <div class="dialogue-lines">
                <p class="line">"像，太像了……"</p>
                <p class="line">"像什么？"</p>
                <p class="line highlight">"像梵高的《星月夜》。"</p>
              </div>
              <div class="dialogue-desc">
                当三维世界向二维跌落时，释放出的巨大能量将一切物质解构重组。<br>
                在冥王星的雪原上，罗辑和庄颜看到了一幅横跨太阳系的宏大油画。<br>
                那是文明最后的挽歌。
              </div>
            </div>
          </div>
        </div>
      </NTabPane>

    </NTabs>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Rajdhani:wght@400;600&display=swap');

.sector-d {
  min-height: 0;
  background: #050510;
  color: #e0d0a0;
  font-family: 'Cinzel', serif;
  display: flex;
  flex-direction: column;
}

.header {
  padding: 1.5rem 2rem;
  background: radial-gradient(circle at center, #1a1a2e 0%, #050510 100%);
  border-bottom: 1px solid #333;
  text-align: center;
}

.title {
  font-family: 'Cinzel', serif;
  font-size: 2rem;
  color: #d4af37;
  letter-spacing: 0.2em;
  text-shadow: 0 0 15px rgba(212, 175, 55, 0.4);
  margin: 0;
}

.deco-line {
  width: 60px;
  height: 2px;
  background: #d4af37;
  margin: 0.5rem auto;
}

.subtitle {
  color: #8899aa;
  font-family: 'Rajdhani', sans-serif;
  letter-spacing: 0.1em;
  font-size: 0.9rem;
}

.d-tabs {
  flex: 1;
}

:deep(.n-tabs-nav) {
  background: rgba(10, 10, 20, 0.95);
  padding: 0 2rem;
}

:deep(.n-tabs-tab-wrapper) {
  flex: 1;
  justify-content: center;
}

:deep(.n-tabs-tab__label) {
  font-family: 'Rajdhani', sans-serif;
  letter-spacing: 0.1em;
  font-weight: 600;
  font-size: 1rem;
}

/* Studio & Strike */
.filter-studio {
  padding: 2rem;
  display: flex;
  justify-content: center;
  min-height: 600px;
}

.studio-main {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  width: 100%;
  max-width: 500px;
}

.canvas-frame {
  position: relative;
  aspect-ratio: 1/1;
  background: #000;
  border: 12px solid #1a1a1a;
  box-shadow: 0 0 40px rgba(0,0,0,0.6);
  overflow: hidden;
}

.image-preview {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  transition: filter 0.1s;
}

.filter-overlay {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  pointer-events: none;
  mix-blend-mode: hard-light;
}

.upload-area {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 15, 25, 0.9);
}

.upload-cta {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2rem;
  text-align: center;
  max-width: 280px;
}

.upload-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
  color: rgba(212, 175, 55, 0.6);
  border: 2px dashed rgba(212, 175, 55, 0.4);
  border-radius: 50%;
  margin-bottom: 0.25rem;
}

.upload-hint {
  margin: 0;
  font-size: 0.95rem;
  color: #888;
  line-height: 1.4;
}

.upload-btn {
  margin-top: 0.5rem;
  min-width: 140px;
}

.upload-sub {
  font-size: 0.75rem;
  color: #555;
}

.scan-line {
  position: absolute;
  left: 0; right: 0;
  height: 2px;
  background: #fff;
  box-shadow: 0 0 10px #fff, 0 0 20px #00ffff;
  z-index: 10;
}

.filter-svg {
  position: absolute;
  width: 0; height: 0;
}

.controls-panel {
  background: #0a0a12;
  border: 1px solid #222;
  padding: 1.5rem;
}

.monitor-screen {
  font-family: 'Rajdhani', monospace;
  margin-bottom: 1.5rem;
  background: #000;
  padding: 1rem;
  border: 1px solid #333;
  color: #00ffaa;
}

.monitor-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.monitor-val {
  color: #d4af37;
}

.monitor-bar {
  height: 4px;
  background: #111;
  margin-top: 0.5rem;
}
.monitor-fill {
  height: 100%;
  background: #ff3333;
  transition: width 0.1s linear;
}

.strike-btn {
  font-family: 'Rajdhani', sans-serif;
  letter-spacing: 0.1em;
  font-weight: bold;
}

.lore-box {
  margin-top: 1rem;
  text-align: center;
  color: #666;
  font-style: italic;
  font-size: 0.9rem;
}

/* Gallery Collection */
.gallery-hall {
  padding: 3rem 10%;
}

.gallery-intro {
  text-align: center;
  margin-bottom: 3rem;
}

.gallery-intro h2 {
  color: #d4af37;
  font-family: 'Cinzel', serif;
}

.gallery-intro p {
  color: #888;
  max-width: 600px;
  margin: 0 auto;
}

.art-frame {
  background: #0a0a0a;
  border: 1px solid #333;
  padding: 10px;
  transition: transform 0.3s;
}

.art-frame:hover {
  transform: translateY(-5px);
  border-color: #d4af37;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.art-canvas {
  aspect-ratio: 3/4;
  margin-bottom: 1rem;
  position: relative;
  overflow: hidden;
}

.art-glitch {
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(transparent, transparent 2px, rgba(0,0,0,0.1) 3px);
  opacity: 0.3;
}

.art-info {
  text-align: center;
}

.art-title {
  color: #ddd;
  font-family: 'Cinzel', serif;
  margin-bottom: 0.3rem;
}

.art-meta {
  color: #555;
  font-size: 0.7rem;
  font-family: 'Rajdhani', sans-serif;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* Pluto Scene */
.pluto-scene {
  height: 70vh;
  position: relative;
  overflow: hidden;
}

.snow-canvas {
  position: absolute;
  inset: 0;
}

.scene-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.dialogue-card {
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(5px);
  padding: 3rem;
  border: 1px solid rgba(212, 175, 55, 0.3);
  text-align: center;
  max-width: 600px;
}

.line {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  color: #ccc;
  font-family: 'Cinzel', serif;
}

.highlight {
  color: #d4af37;
  font-size: 1.4rem;
  text-shadow: 0 0 10px rgba(212, 175, 55, 0.5);
}

.dialogue-desc {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255,255,255,0.1);
  color: #666;
  line-height: 1.6;
}
</style>
