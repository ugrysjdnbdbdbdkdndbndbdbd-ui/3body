<script setup lang="ts">
/**
 * Sector T: The Trisolaran Pendulum (三体摆)
 * Dynamic environment engine and chaos simulation.
 */
import { ref, onMounted } from 'vue'
import { API, apiUrl } from '@/constants'
import { NSpin } from 'naive-ui'
import type { Figure } from '@/types/figures'
import type { ChronicleEvent } from '@/types/chronicle'
import { figureImageUrl } from '@/utils/imageFallback'

const loading = ref(true)
const pendulumFigure = ref<Figure | null>(null)
const dehydrationEvent = ref<ChronicleEvent | null>(null)
const environmentState = ref({
  era: 'CHAOTIC ERA',
  suns: 3,
  temperature: '400℃',
  gravity: '1.2G'
})

async function loadData() {
  loading.value = true
  try {
    // Load Figure: Pendulum-001
    const figuresRes = await fetch(apiUrl(API.FIGURES_LIST))
    if (figuresRes.ok) {
      const figures = await figuresRes.json()
      pendulumFigure.value = figures.find((f: Figure) => f.name.includes('守摆人')) || null
    }

    // Load Chronicle: Double Sun Dehydration
    const eventsRes = await fetch(apiUrl(API.CHRONICLE_EVENTS))
    if (eventsRes.ok) {
      const events = await eventsRes.json()
      dehydrationEvent.value = events.find((e: ChronicleEvent) => e.title.includes('双日凌空')) || null
    }
  } catch (e) {
    console.error('Sector T data load failed', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <div class="sector-t cosmic-void">
    <div class="void-noise"></div>
    <div class="void-dust"></div>
    <div class="void-vignette"></div>

    <div class="content-layer">
      <!-- Header -->
      <header class="header">
        <h1 class="title tech-glow">SECTOR_T // TRISOLARAN PENDULUM</h1>
        <div class="status-bar mono-data">
          <span>ERA: <span class="text-red-500">{{ environmentState.era }}</span></span>
          <span>SUNS: {{ environmentState.suns }}</span>
          <span>TEMP: {{ environmentState.temperature }}</span>
        </div>
      </header>

      <main class="main-grid">
        <!-- Visual: The Pendulum -->
        <div class="pendulum-container">
          <div class="pendulum">
            <div class="rod"></div>
            <div class="bob warning-glow"></div>
          </div>
          <div class="pendulum-base"></div>
          <div class="message text-red-500 warning-glow">
            WARNING: GRAVITATIONAL ANOMALY DETECTED
          </div>
        </div>

        <!-- Data Panel -->
        <div class="data-panel">
          
          <!-- Chronicle Event -->
          <div v-if="dehydrationEvent" class="data-block chronicle-block">
            <h2 class="block-title">CHRONICLE_NODE // {{ dehydrationEvent.year }}</h2>
            <div class="event-card">
              <h3 class="event-title">{{ dehydrationEvent.title }}</h3>
              <p class="event-content">{{ dehydrationEvent.content }}</p>
              <div class="event-meta mono-data">
                CAUSALITY: {{ (dehydrationEvent.causality_status || 'collapsed').toUpperCase() }}
              </div>
            </div>
          </div>
          <div v-else-if="!loading" class="data-block error">
            CHRONICLE DATA CORRUPTED
          </div>

          <!-- Figure Dossier -->
          <div v-if="pendulumFigure" class="data-block figure-block">
            <h2 class="block-title">OBSERVER_LOG // PENDULUM-001</h2>
            <div class="figure-card">
              <div class="figure-header">
                <img :src="figureImageUrl(pendulumFigure.image_url, pendulumFigure.en_name, '')" class="figure-avatar" />
                <div class="figure-info">
                  <div class="name">{{ pendulumFigure.name }}</div>
                  <div class="role mono-data">{{ pendulumFigure.role }}</div>
                </div>
              </div>
              <p class="figure-desc">{{ pendulumFigure.description }}</p>
              <blockquote class="figure-quote">
                {{ pendulumFigure.quotes }}
              </blockquote>
              <div class="logic-score mono-data">
                SOPHON_EVAL: <span class="text-red-500">{{ pendulumFigure.logic_score }}</span>
              </div>
            </div>
          </div>
           <div v-else-if="!loading" class="data-block error">
            OBSERVER SIGNAL LOST
          </div>

           <div v-if="loading" class="loading-state">
            <NSpin size="large" stroke="#00FFC8" />
            <div class="mono-data mt-4">SYNCING WITH SOPHON...</div>
          </div>

        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.sector-t {
  min-height: 0;
  flex: 1;
  position: relative;
  overflow: hidden;
  color: #E0FFF8;
  font-family: 'Inter', sans-serif;
}

.content-layer {
  position: relative;
  z-index: 10;
  padding: 2rem;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(0, 255, 200, 0.2);
  padding-bottom: 1rem;
  margin-bottom: 2rem;
}

.title {
  font-size: 1.5rem;
  font-weight: 200;
  letter-spacing: 0.2em;
  color: var(--holo-blue);
}

.status-bar {
  display: flex;
  gap: 2rem;
  color: var(--text-muted);
}

.main-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  flex: 1;
  overflow: hidden;
}

/* Pendulum Animation */
.pendulum-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  border: 1px solid rgba(255, 60, 0, 0.1);
  background: rgba(255, 60, 0, 0.02);
}

.pendulum {
  position: absolute;
  top: 10%;
  transform-origin: top center;
  animation: swing 4s ease-in-out infinite;
}

.rod {
  width: 2px;
  height: 300px;
  background: linear-gradient(to bottom, transparent, var(--holo-red));
  margin: 0 auto;
}

.bob {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--holo-red);
  margin: -2px auto 0;
  box-shadow: 0 0 20px var(--holo-red);
}

.pendulum-base {
  position: absolute;
  bottom: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--holo-red), transparent);
}

.message {
  margin-top: auto;
  margin-bottom: 2rem;
  font-family: var(--font-tech);
  letter-spacing: 0.1em;
  animation: blink 2s infinite;
}

@keyframes swing {
  0% { transform: rotate(25deg); }
  50% { transform: rotate(-25deg); }
  100% { transform: rotate(25deg); }
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Data Panel */
.data-panel {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  overflow-y: auto;
  padding-right: 1rem;
}

.data-block {
  background: rgba(0, 5, 16, 0.6);
  border: 1px solid rgba(0, 255, 200, 0.1);
  padding: 1.5rem;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.data-block:hover {
  border-color: var(--holo-blue);
  box-shadow: 0 0 20px rgba(0, 255, 200, 0.1);
}

.chronicle-block:hover {
  border-color: var(--holo-red);
  box-shadow: 0 0 20px rgba(255, 60, 0, 0.15);
}

.block-title {
  font-family: var(--font-tech);
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-bottom: 1rem;
  border-bottom: 1px dashed rgba(255,255,255,0.1);
  padding-bottom: 0.5rem;
}

.event-title {
  font-size: 1.2rem;
  color: var(--holo-red);
  margin-bottom: 0.5rem;
  text-shadow: 0 0 8px rgba(255, 60, 0, 0.4);
}

.event-content {
  font-size: 0.9rem;
  line-height: 1.6;
  color: #ddd;
  margin-bottom: 1rem;
}

.figure-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.figure-avatar {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border: 1px solid var(--holo-blue);
  filter: grayscale(100%);
}

.figure-info {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.name {
  font-size: 1.1rem;
  font-weight: bold;
}

.role {
  font-size: 0.8rem;
  color: var(--holo-blue);
}

.figure-desc {
  font-size: 0.9rem;
  line-height: 1.6;
  color: var(--text-muted);
  margin-bottom: 1rem;
}

.figure-quote {
  font-style: italic;
  color: var(--holo-blue);
  border-left: 2px solid var(--holo-blue);
  padding-left: 1rem;
  margin: 0 0 1rem 0;
  font-size: 0.9rem;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
}
</style>
