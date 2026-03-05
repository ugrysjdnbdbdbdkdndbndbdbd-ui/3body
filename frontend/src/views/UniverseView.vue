<script setup lang="ts">
/**
 * UniverseView - 三体宇宙观测终端 (首页 v2.1)
 * 核心：3D 三体运动背景 + 战术 HUD 布局
 * 优化：全面汉化，修复乱纪元文字抖动导致的布局错乱
 */
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUniverseStore } from '@/stores/universe'
import ThreeBodyBackground from '@/components/ThreeBodyBackground.vue'
import GlitchText from '@/components/GlitchText.vue'

const router = useRouter()
const universe = useUniverseStore()

// 五大分类导航数据
const navGroups = [
  {
    code: 'ORIGINS',
    label: '起源与接触',
    desc: '红岸 · 三体摆 · 智子',
    path: '/sector-r',
    color: '#ff4400'
  },
  {
    code: 'CRISIS',
    label: '危机与战略',
    desc: '面壁 · 阶梯 · 水滴 · 森林',
    path: '/sector-f',
    color: '#ffaa00'
  },
  {
    code: 'UNIVERSE',
    label: '宇宙与维度',
    desc: '掩体 · 曲率 · 四维',
    path: '/sector-j',
    color: '#00ccff'
  },
  {
    code: 'HISTORY',
    label: '岁月与文明',
    desc: '编年史 · 原著阅读 · 人物 · 画廊',
    path: '/sector-b',
    color: '#00ffaa'
  },
  {
    code: 'ETERNITY',
    label: '时间与尽头',
    desc: '小宇宙 · 未知 · 重启',
    path: '/sector-u',
    color: '#aa00ff'
  }
]

// 随机生成的环境状态 (汉化)
const eraStatus = ref('乱纪元')
const sunDistance = ref('0.8 AU')
const surfaceTemp = ref('62°C')

function updateEnvironment() {
  const eras = ['乱纪元', '恒纪元', '三日凌空', '永夜']
  eraStatus.value = eras[Math.floor(Math.random() * eras.length)]
  sunDistance.value = (0.5 + Math.random() * 2).toFixed(2) + ' AU'
  surfaceTemp.value = Math.floor(Math.random() * 200 - 100) + '°C'
}

let timer: ReturnType<typeof setInterval> | undefined
onMounted(() => {
  universe.fetchMetrics()
  timer = setInterval(updateEnvironment, 5000)
  updateEnvironment()
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

function handleNavClick(path: string) {
  router.push(path)
}
</script>

<template>
  <div class="terminal">
    <!-- Layer 0: 3D Background -->
    <div class="terminal__bg">
      <ThreeBodyBackground />
      <div class="terminal__vignette"></div>
      <div class="terminal__scanlines"></div>
    </div>

    <!-- Layer 1: HUD UI -->
    <div class="terminal__ui">
      
      <!-- 左上：标题 + 状态栏（独立左侧区域，避免被右侧导航遮挡） -->
      <header class="hud-header">
        <div class="hud-left">
          <div class="hud-brand">
            <h1 class="brand-title">THREE BODY</h1>
            <div class="brand-sub">PLANETARY DEFENSE SYSTEM // 行星防御系统</div>
          </div>
          <div class="hud-status-grid">
            <div class="status-item">
              <span class="label">恒星纪元</span>
              <div class="value-container">
                <GlitchText :text="eraStatus" class="value value--alert" />
              </div>
            </div>
            <div class="status-item">
              <span class="label">文明纪元</span>
              <div class="value-container">
                <span class="value">No. 192</span>
              </div>
            </div>
            <div class="status-item">
              <span class="label">日地距离</span>
              <div class="value-container">
                <span class="value">{{ sunDistance }}</span>
              </div>
            </div>
            <div class="status-item">
              <span class="label">地表温度</span>
              <div class="value-container">
                <span class="value">{{ surfaceTemp }}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Center: Reticle (Visual Only) -->
      <div class="hud-center-reticle">
        <svg viewBox="0 0 100 100" class="reticle-svg">
          <circle cx="50" cy="50" r="48" stroke="rgba(255,255,255,0.1)" stroke-width="0.5" fill="none" />
          <line x1="50" y1="0" x2="50" y2="100" stroke="rgba(255,255,255,0.05)" stroke-width="0.5" />
          <line x1="0" y1="50" x2="100" y2="50" stroke="rgba(255,255,255,0.05)" stroke-width="0.5" />
        </svg>
      </div>

      <!-- Right: Navigation Modules -->
      <nav class="hud-nav">
        <div 
          v-for="(item, idx) in navGroups" 
          :key="item.code"
          class="nav-module"
          :style="{ '--module-color': item.color }"
          @click="handleNavClick(item.path)"
        >
          <div class="module-code">0{{ idx + 1 }} // {{ item.code }}</div>
          <div class="module-content">
            <div class="module-label">{{ item.label }}</div>
            <div class="module-desc">{{ item.desc }}</div>
          </div>
          <div class="module-bar"></div>
        </div>
      </nav>

      <!-- Bottom: Ticker -->
      <footer class="hud-footer">
        <div class="scrolling-ticker">
          <div class="ticker-content">
            生存是文明的第一需要 /// 宇宙就是一座黑暗森林，每个文明都是带枪的猎人 /// 弱小和无知不是生存的障碍，傲慢才是 /// 不要回答！不要回答！不要回答！ ///
            生存是文明的第一需要 /// 宇宙就是一座黑暗森林，每个文明都是带枪的猎人 /// 弱小和无知不是生存的障碍，傲慢才是 /// 不要回答！不要回答！不要回答！ ///
          </div>
        </div>
      </footer>

    </div>
  </div>
</template>

<style scoped>
/* Base Layout：绝对定位填满父容器，强制解决 flex 高度计算偏差 */
.terminal {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: #000;
  font-family: 'Rajdhani', monospace;
  color: #fff;
}

/* Background Layer */
.terminal__bg {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.terminal__vignette {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at center, transparent 40%, #000 100%);
  pointer-events: none;
}

.terminal__scanlines {
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    rgba(0, 0, 0, 0.2) 0px,
    rgba(0, 0, 0, 0.2) 1px,
    transparent 1px,
    transparent 2px
  );
  pointer-events: none;
  opacity: 0.5;
}

/* UI Layer */
.terminal__ui {
  position: relative;
  z-index: 10;
  width: 100%;
  height: 100%;
  padding: 2rem;
  padding-top: 100px; /* 避开顶部导航栏 */
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

/* Header：左侧集中，避免与右侧导航重叠 */
.hud-header {
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
}

.hud-left {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 420px; /* 限制宽度，与右侧导航留出安全距离 */
}

.brand-title {
  font-size: 3rem;
  font-weight: 700;
  letter-spacing: 0.2em;
  line-height: 1;
  margin: 0;
  text-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
}

.brand-sub {
  font-size: 0.8rem;
  letter-spacing: 0.4em;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 0.5rem;
}

.hud-status-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem 2rem;
  text-align: left;
}

.status-item {
  display: flex;
  flex-direction: column;
}

.status-item .label {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}

.value-container {
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.status-item .value {
  font-size: 1.2rem;
  font-weight: 600;
  color: #00ccff;
}

.status-item .value--alert {
  color: #ff4400;
  text-shadow: 0 0 10px #ff4400;
}

/* Center Reticle */
.hud-center-reticle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60vh;
  height: 60vh;
  pointer-events: none;
  opacity: 0.3;
}

.reticle-svg {
  width: 100%;
  height: 100%;
  animation: rotate-reticle 60s linear infinite;
}

@keyframes rotate-reticle {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Right Navigation */
.hud-nav {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-right: 2rem;
  align-items: flex-end;
}

.nav-module {
  position: relative;
  width: 260px;
  background: rgba(0, 10, 20, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
  clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px);
}

.nav-module:hover {
  width: 300px;
  background: rgba(0, 20, 40, 0.8);
  border-color: var(--module-color);
  box-shadow: -10px 0 30px rgba(0,0,0,0.5);
}

.nav-module:hover .module-bar {
  background: var(--module-color);
  box-shadow: 0 0 10px var(--module-color);
}

.module-code {
  font-size: 0.6rem;
  color: rgba(255, 255, 255, 0.4);
  letter-spacing: 0.1em;
  margin-bottom: 0.5rem;
}

.module-label {
  font-size: 1.2rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 0.2rem;
}

.nav-module:hover .module-label {
  color: var(--module-color);
  text-shadow: 0 0 8px var(--module-color);
}

.module-desc {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
}

.module-bar {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: rgba(255, 255, 255, 0.1);
  transition: all 0.3s;
}

/* Footer Ticker */
.hud-footer {
  width: 100%;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.5);
  padding: 0.5rem 0;
  overflow: hidden;
}

.scrolling-ticker {
  white-space: nowrap;
  overflow: hidden;
}

.ticker-content {
  display: inline-block;
  font-size: 0.8rem;
  letter-spacing: 0.1em;
  color: rgba(0, 255, 255, 0.7);
  animation: ticker-move 40s linear infinite; /* 调慢一点 */
}

@keyframes ticker-move {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}

/* Responsive */
@media (max-width: 768px) {
  .hud-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .hud-status-grid {
    grid-template-columns: 1fr 1fr;
    text-align: left;
    width: 100%;
  }

  .value-container {
    justify-content: flex-start;
  }

  .hud-nav {
    position: relative;
    top: auto;
    right: auto;
    transform: none;
    align-items: stretch;
    margin-top: 2rem;
    padding: 0;
  }

  .nav-module {
    width: 100%;
  }
  
  .nav-module:hover {
    width: 100%;
  }
}
</style>
