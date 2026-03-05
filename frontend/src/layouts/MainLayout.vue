<script setup lang="ts">
/**
 * MainLayout - The Viewport
 * "The ship was a small world, and the universe was a dark forest."
 */
import { RouterView, useRoute } from 'vue-router'
import { onMounted, onUnmounted, watch } from 'vue'
import { useUniverseStore } from '@/stores/universe'
import { useUserStore } from '@/stores/user'
import AppNav from '@/components/AppNav.vue'
import SophonIntercept from '@/components/commercial/SophonIntercept.vue'
import { soundManager } from '@/utils/sound'

const universe = useUniverseStore()
const userStore = useUserStore()
const route = useRoute()

// --- Global Sound Handling ---
const handleGlobalClick = (e: MouseEvent) => {
  const target = e.target as HTMLElement
  // Check if clicked element is interactive
  if (target.closest('button') || target.closest('a') || target.closest('.n-tab-tab') || target.closest('.control-item')) {
    soundManager.playClick()
  }
}

const handleGlobalHover = (e: MouseEvent) => {
  const target = e.target as HTMLElement
  // Using a throttle might be better, but simple check is fine for now
  if (target.closest('button') || target.closest('a') || target.closest('.n-tab-tab')) {
    // Only play if we haven't played recently for this element? 
    // For now, let's keep it simple. The soundManager is short.
    soundManager.playHover()
  }
}

// Watch route changes for "navigation" sound
watch(() => route.path, () => {
  soundManager.playConfirm()
})

let metricsInterval: ReturnType<typeof setInterval>
onMounted(() => {
  // 延迟首请求，让首屏先完成渲染，提升可感知加载速度
  setTimeout(() => universe.fetchMetrics().catch(() => {}), 80)
  metricsInterval = setInterval(universe.fetchMetrics, 30_000)
  
  // Attach listeners
  window.addEventListener('click', handleGlobalClick)
  // Mouseover can be noisy, let's try it. If too much, we remove.
  // window.addEventListener('mouseover', handleGlobalHover) 
  
  userStore.init()
})

onUnmounted(() => {
  clearInterval(metricsInterval)
  window.removeEventListener('click', handleGlobalClick)
  // window.removeEventListener('mouseover', handleGlobalHover)
})
</script>

<template>
  <div class="app-layout">
    <!-- The Void Canvas -->
    <div class="cosmic-void">
      <div class="void-noise"></div>
      <div class="void-dust"></div>
      <div class="void-vignette"></div>
    </div>

    <header class="app-header">
      <AppNav />
    </header>

    <main class="app-main" :class="{ 'app-main--full': route.path === '/sector-c' }">
      <RouterView v-slot="{ Component }">
        <transition name="dimension-unfold" mode="out-in">
          <Suspense>
            <template #default>
              <component :is="Component" :key="route.fullPath" />
            </template>
            <template #fallback>
              <div class="loading-state">
                <div class="loading-spinner"></div>
                <span>LOADING SYSTEM...</span>
              </div>
            </template>
          </Suspense>
        </transition>
      </RouterView>
    </main>

    <SophonIntercept />

    <footer class="app-footer">
      <span class="slogan">给岁月以文明，而不是给文明以岁月</span>
      <span class="meta mono-data">ERA: {{ universe.currentEra }} // DETERRENCE: {{ (universe.deterrence * 100).toFixed(0) }}%</span>
    </footer>
  </div>
</template>

<style scoped>
.app-layout {
  height: 100vh;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  color: #E0FFF8;
  position: relative;
}

.app-main {
  flex: 1 1 0;
  min-height: 0;
  overflow: auto;
  padding: 2rem 3rem;
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
}

/* 扇区根节点：去除强制高度，避免 padding 导致溢出 */
.app-main > * {
  width: 100%;
  /* min-height: 100%;  <-- 移除此行，防止 content + padding > 100% 导致滚动条 */
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
}

/* 首页全屏铺满，无内边距，避免 100vh 导致底部大量空白 */
.app-main--full {
  padding: 0;
}
.app-main--full > * {
  flex: 1 1 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.app-footer {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
  padding: 1rem 3rem;
  font-size: 0.75rem;
  color: rgba(224, 255, 248, 0.5);
  border-top: 1px solid rgba(0, 255, 200, 0.05);
  position: relative;
  z-index: 50;
  letter-spacing: 0.1em;
}

/* --- COSMIC VOID BACKGROUND --- */
.cosmic-void {
  position: absolute;
  inset: 0;
  z-index: 0;
  background: #050505;
  overflow: hidden;
  pointer-events: none;
}

.void-noise {
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.05'/%3E%3C/svg%3E");
  opacity: 0.03;
  mix-blend-mode: overlay;
}

.void-dust {
  position: absolute;
  inset: -50%;
  width: 200%;
  height: 200%;
  background-image: 
    radial-gradient(1px 1px at 10% 10%, #fff 100%, transparent),
    radial-gradient(1px 1px at 20% 20%, #fff 100%, transparent),
    radial-gradient(2px 2px at 30% 30%, #fff 100%, transparent),
    radial-gradient(1px 1px at 40% 40%, #fff 100%, transparent),
    radial-gradient(1px 1px at 50% 50%, #fff 100%, transparent),
    radial-gradient(2px 2px at 60% 60%, #fff 100%, transparent),
    radial-gradient(1px 1px at 70% 70%, #fff 100%, transparent),
    radial-gradient(1px 1px at 80% 80%, #fff 100%, transparent),
    radial-gradient(2px 2px at 90% 90%, #fff 100%, transparent);
  background-size: 500px 500px;
  opacity: 0.3;
  animation: cosmic-drift 200s linear infinite;
}

.void-dust::after {
  content: '';
  position: absolute;
  inset: 0;
  background-image: 
    radial-gradient(1px 1px at 15% 15%, #fff 100%, transparent),
    radial-gradient(1px 1px at 25% 25%, #fff 100%, transparent),
    radial-gradient(2px 2px at 35% 35%, #fff 100%, transparent),
    radial-gradient(1px 1px at 45% 45%, #fff 100%, transparent),
    radial-gradient(1px 1px at 55% 55%, #fff 100%, transparent),
    radial-gradient(2px 2px at 65% 65%, #fff 100%, transparent),
    radial-gradient(1px 1px at 75% 75%, #fff 100%, transparent),
    radial-gradient(1px 1px at 85% 85%, #fff 100%, transparent),
    radial-gradient(2px 2px at 95% 95%, #fff 100%, transparent);
  background-size: 700px 700px;
  opacity: 0.2;
  animation: cosmic-drift 300s linear infinite reverse;
}

.void-vignette {
  position: absolute;
  inset: 0;
  z-index: 2;
  background: radial-gradient(circle at center, transparent 0%, rgba(0,0,0,0.6) 80%, #000 100%);
  mix-blend-mode: multiply;
}

@keyframes cosmic-drift {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.slogan {
  font-family: 'Noto Serif SC', serif;
  font-style: italic;
  opacity: 0.7;
}

/* --- DIMENSIONAL UNFOLDING TRANSITION --- */
/* Simulates an object emerging from a higher dimension into the viewport */

.loading-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  color: #00ffff;
  font-family: monospace;
  letter-spacing: 2px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 2px solid rgba(0, 255, 255, 0.3);
  border-top-color: #00ffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.dimension-unfold-enter-active {
  transition: all 1.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.dimension-unfold-leave-active {
  transition: all 0.6s cubic-bezier(0.7, 0, 0.84, 0); /* Quicker exit into void */
}

.dimension-unfold-enter-from {
  opacity: 0;
  transform: scale(0.96) translateY(15px); /* Submerged */
  filter: blur(10px);
}

.dimension-unfold-leave-to {
  opacity: 0;
  transform: scale(1.02); /* Dissolving outwards */
  filter: blur(5px);
}
</style>
