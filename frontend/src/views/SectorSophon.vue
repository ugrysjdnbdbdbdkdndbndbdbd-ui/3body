<script setup lang="ts">
/**
 * Sector A: Sophon Terminal (智子终端)
 * Concept: Retinal Projection Interface & Dimensional Unfolding
 * Core Features:
 * 1. Dimensionality Control (1D-11D)
 * 2. Doomsday Countdown
 * 3. Retinal Chat Interface
 * 4. Quantum Entanglement Status
 */
import { ref, computed, onMounted, onUnmounted, nextTick, watch, reactive } from 'vue'
import { NSlider } from 'naive-ui'
import { streamChat } from '@/api/chat'
import type { Message } from '@/types/sophon'
import { soundManager } from '@/utils/sound'

// --- State ---
const dimension = ref(3) // 1-11
const arrivalTime = new Date('2400-01-01').getTime() // Approx 400 years
const countdownStr = ref('')
const isBugsMode = ref(false)
const entanglementStable = ref(true)

// Visual Effects State
const containerStyle = computed(() => {
  if (dimension.value === 1) {
    return {
      filter: 'contrast(3) grayscale(1) blur(1px)',
      transform: 'scaleX(2)', // Stretched line
    }
  }
  if (dimension.value === 2) {
    return {
      filter: 'contrast(1.5) grayscale(1)',
      perspective: 'none',
    }
  }
  if (dimension.value === 3) {
    return {} // Standard
  }
  if (dimension.value > 3) {
    // Hyper-dimensional distortion
    const intensity = (dimension.value - 3) * 2
    return {
      filter: `hue-rotate(${intensity * 10}deg) blur(${intensity * 0.5}px)`,
      transform: `perspective(1000px) rotateY(${intensity}deg)`,
    }
  }
  return {}
})

// Chat State
const messages = ref<Message[]>([])
const inputText = ref('')
const isLoading = ref(false)
const streamingId = ref<string | null>(null)
const chatContainer = ref<HTMLElement | null>(null)

// --- Lore Constants ---
const DIMENSION_DESC = {
  1: '1维弦 - 量子电路蚀刻模式 (QUANTUM CIRCUIT)',
  2: '2维面 - 智子工程展开 (SMART FOLDING)',
  3: '3维球体 - 常规观测形态 (STANDARD)',
  4: '4维超球体 - 空间翘曲 (HYPERSPHERE)',
  6: '6维卡拉比-丘空间 (CALABI-YAU)',
  11: '11维微观态 - 超弦极限 (SUPERSTRING)'
}

// --- Logic ---

// Retina Countdown
const mousePos = reactive({ x: 0, y: 0 })
const showRetina = ref(true)

function handleMouseMove(e: MouseEvent) {
  mousePos.x = e.clientX
  mousePos.y = e.clientY
}

// Countdown Timer
let timer: ReturnType<typeof setInterval>
const updateCountdown = () => {
  const now = Date.now()
  const diff = arrivalTime - now
  // Format: HH:MM:SS:MS
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  const secs = Math.floor((diff % (1000 * 60)) / 1000)
  const ms = Math.floor((diff % 1000) / 10)
  
  // Wang Miao style format
  countdownStr.value = `${hours}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}:${ms.toString().padStart(2, '0')}`
}

// Dimension Audio Feedback
watch(dimension, () => {
  soundManager.playTone(440 + dimension.value * 50, 'sine', 0.1, 0.2)
})

// Bugs Trigger
const triggerBugs = () => {
  isBugsMode.value = true
  soundManager.playAlert() // Warning sound
  setTimeout(() => {
    isBugsMode.value = false
  }, 3000)
}

// Chat Logic
const genId = () => `MSG-${Date.now().toString(16).toUpperCase()}`

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

const send = async () => {
  const text = inputText.value.trim()
  if (!text || isLoading.value) return

  // Easter Eggs
  if (text.includes('虫子') || text.includes('bug') || text.includes('Bugs')) {
    triggerBugs()
  }

  // Dimension Control via chat
  if (text === '/unfold') {
    dimension.value = 2
    return
  }
  if (text === '/fold') {
    dimension.value = 11
    return
  }

  isLoading.value = true
  inputText.value = ''

  const userMsg: Message = {
    id: genId(),
    role: 'user',
    content: text,
    timestamp: Date.now(),
    status: 'done'
  }
  messages.value.push(userMsg)

  const sophonMsg: Message = {
    id: genId(),
    role: 'sophon',
    content: '',
    timestamp: Date.now(),
    status: 'streaming'
  }
  messages.value.push(sophonMsg)
  streamingId.value = sophonMsg.id
  scrollToBottom()

  try {
    await streamChat(messages.value, (chunk) => {
      sophonMsg.content += chunk
      soundManager.playTone(600 + Math.random() * 200, 'square', 0.05, 0.05) // Tech typing sound
      scrollToBottom()
    })
    sophonMsg.status = 'done'
  } catch (e) {
    sophonMsg.content += ' [连接中断]'
    sophonMsg.status = 'error'
  } finally {
    isLoading.value = false
    streamingId.value = null
    scrollToBottom()
  }
}

// Dimensional Effects
const coreStyle = computed(() => {
  if (dimension.value === 1) return { width: '100%', height: '2px', borderRadius: '0' }
  if (dimension.value === 2) return { width: '100%', height: '100%', borderRadius: '0', opacity: 0.1 }
  if (dimension.value === 3) return { width: '300px', height: '300px', borderRadius: '50%' }
  // Higher dimensions shrink it
  const size = 300 - (dimension.value - 3) * 30
  return { width: `${size}px`, height: `${size}px`, borderRadius: '50%' }
})

onMounted(() => {
  timer = setInterval(updateCountdown, 50)
  // Initial Greeting
  if (messages.value.length === 0) {
    messages.value.push({
      id: genId(),
      role: 'sophon',
      content: '我是智子。宇宙对我来说是透明的。',
      timestamp: Date.now(),
      status: 'done'
    })
  }
})

onUnmounted(() => {
  clearInterval(timer)
})

</script>

<template>
  <div 
    class="sector-sophon" 
    :class="{ 'bugs-mode': isBugsMode, 'dimension-2': dimension === 2 }"
    @mousemove="handleMouseMove"
  >
    <!-- Retina Countdown Overlay -->
    <div 
      class="retina-countdown" 
      :style="{ left: mousePos.x + 'px', top: mousePos.y + 'px' }"
      v-if="showRetina"
    >
      {{ countdownStr }}
    </div>
    
    <!-- Background Layer -->
    <div class="quantum-field" :style="containerStyle">
      <div class="particles"></div>
      <div v-if="dimension === 2" class="mirror-surface"></div>
    </div>

    <!-- HUD Overlay -->
    <div class="hud-layer">
      <!-- Top Bar: Countdown & Status -->
      <header class="hud-top">
        <div class="countdown-box">
          <span class="label">TRISOLARAN FLEET ARRIVAL</span>
          <span class="timer">{{ countdownStr }}</span>
        </div>
        <div class="status-box">
          <div class="status-row">
            <span>ENTANGLEMENT:</span>
            <span :class="entanglementStable ? 'ok' : 'err'">{{ entanglementStable ? '稳定' : '中断' }}</span>
          </div>
          <div class="status-row">
            <span>LATENCY:</span>
            <span>0.00ms (实时)</span>
          </div>
        </div>
      </header>

      <!-- Central Visual: Sophon Core -->
      <div class="core-container">
        <div class="sophon-core" :style="{ ...coreStyle, ...containerStyle }">
          <div class="core-inner"></div>
          <div class="core-ring"></div>
        </div>
        <div v-if="isBugsMode" class="bugs-overlay">
          <div v-for="i in 20" :key="i" class="bug-text" :style="{ left: Math.random()*100 + '%', top: Math.random()*100 + '%' }">
            你们是虫子
          </div>
        </div>
      </div>

      <!-- Chat Interface: Retinal Projection -->
      <div class="chat-interface">
        <div class="messages-area" ref="chatContainer">
          <div v-for="msg in messages" :key="msg.id" class="msg-row" :class="msg.role">
            <div class="msg-bubble">
              <span class="sender">{{ msg.role === 'user' ? 'HUMAN' : 'SOPHON' }} //</span>
              <span class="content">{{ msg.content }}</span>
              <span v-if="msg.status === 'streaming'" class="cursor">_</span>
            </div>
          </div>
        </div>
        
        <div class="input-area">
          <input 
            v-model="inputText" 
            @keydown.enter="send" 
            type="text" 
            placeholder="投射思维..." 
            :disabled="isLoading"
          />
        </div>
      </div>

      <!-- Bottom Control: Dimension Slider -->
      <footer class="hud-bottom">
        <div class="dim-control">
          <span class="dim-label">DIMENSIONAL UNFOLDING: {{ dimension }}D</span>
          <NSlider v-model:value="dimension" :min="1" :max="11" :step="1" :tooltip="false" />
          <span class="dim-desc">{{ DIMENSION_DESC[dimension as keyof typeof DIMENSION_DESC] || '未知状态' }}</span>
        </div>
      </footer>

    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap');

.sector-sophon {
  height: 100%;
  flex: 1;
  min-height: 0;
  background: #000;
  color: #fff;
  font-family: 'Rajdhani', sans-serif;
  overflow: hidden;
  position: relative;
}

/* Retina Countdown */
.retina-countdown {
  position: fixed;
  pointer-events: none;
  font-family: 'Orbitron', monospace;
  font-size: 1.5rem;
  color: rgba(255, 0, 0, 0.6);
  text-shadow: 0 0 5px rgba(255, 0, 0, 0.8);
  z-index: 9999;
  transform: translate(20px, 20px);
  mix-blend-mode: screen;
  animation: flicker 0.1s infinite alternate;
  user-select: none;
}

@keyframes flicker {
  0% { opacity: 0.5; }
  100% { opacity: 0.7; }
}

/* Background Effects */
.quantum-field {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 50%, #0a0a1a 0%, #000 100%);
  z-index: 0;
}

.particles {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(white 1px, transparent 1px);
  background-size: 50px 50px;
  opacity: 0.1;
  animation: drift 20s linear infinite;
}

.mirror-surface {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.1), transparent);
  backdrop-filter: blur(2px);
}

/* HUD Layer */
.hud-layer {
  position: absolute;
  inset: 0;
  z-index: 10;
  display: flex;
  flex-direction: column;
  padding: 2rem;
  pointer-events: none; /* Let clicks pass to inputs */
}

/* Enable pointer events for interactive elements */
.input-area, .dim-control {
  pointer-events: auto;
}

/* Header */
.hud-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid rgba(255,255,255,0.2);
  padding-bottom: 1rem;
}

.countdown-box {
  display: flex;
  flex-direction: column;
}

.countdown-box .label {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.8rem;
  color: #00f0ff;
  letter-spacing: 2px;
}

.countdown-box .timer {
  font-family: 'Orbitron', sans-serif;
  font-size: 2rem;
  color: #fff;
  text-shadow: 0 0 10px #00f0ff;
}

.status-box {
  text-align: right;
  font-size: 0.9rem;
  color: #888;
}

.ok { color: #0f0; }
.err { color: #f00; animation: blink 0.5s infinite; }

/* Core Visual */
.core-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  perspective: 1000px;
}

.sophon-core {
  background: radial-gradient(circle at 30% 30%, #fff, #888, #000);
  box-shadow: 0 0 50px rgba(255, 255, 255, 0.2);
  position: relative;
  transition: all 1s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.core-inner {
  position: absolute;
  inset: 10%;
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  animation: spin 10s linear infinite reverse;
}

.core-ring {
  position: absolute;
  inset: -20%;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 50%;
  animation: spin 20s linear infinite;
}

/* Bugs Mode */
.bugs-mode .sophon-core {
  filter: invert(1) contrast(2);
}

.bugs-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.bug-text {
  position: absolute;
  font-family: 'Orbitron', sans-serif;
  color: #f00;
  font-size: 2rem;
  font-weight: bold;
  opacity: 0.8;
  text-shadow: 0 0 5px #f00;
  animation: shake 0.5s infinite;
}

/* Chat Interface */
.chat-interface {
  position: absolute;
  bottom: 120px;
  right: 2rem;
  width: 400px;
  height: 400px;
  display: flex;
  flex-direction: column;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(5px);
  border-radius: 4px;
  pointer-events: auto;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.msg-row {
  display: flex;
  flex-direction: column;
  animation: fadeIn 0.3s ease-out;
}

.msg-row.user { align-items: flex-end; }
.msg-row.sophon { align-items: flex-start; }

.msg-bubble {
  max-width: 90%;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-left: 2px solid #00f0ff;
}

.user .msg-bubble {
  border-left: none;
  border-right: 2px solid #0f0;
  text-align: right;
}

.sender {
  font-size: 0.7rem;
  color: #888;
  display: block;
  margin-bottom: 0.2rem;
  letter-spacing: 1px;
}

.content {
  font-size: 1rem;
  line-height: 1.4;
  text-shadow: 0 0 2px rgba(255,255,255,0.5);
}

.cursor {
  display: inline-block;
  width: 8px;
  background: #00f0ff;
  animation: blink 1s infinite;
}

.input-area {
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.input-area input {
  width: 100%;
  background: transparent;
  border: none;
  border-bottom: 1px solid #444;
  color: #fff;
  font-family: 'Rajdhani', sans-serif;
  font-size: 1.2rem;
  padding: 0.5rem;
  outline: none;
  transition: border-color 0.3s;
}

.input-area input:focus {
  border-color: #00f0ff;
}

/* Bottom Control */
.hud-bottom {
  border-top: 1px solid rgba(255,255,255,0.2);
  padding-top: 1rem;
}

.dim-control {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
}

.dim-label {
  display: block;
  font-family: 'Orbitron', sans-serif;
  color: #00f0ff;
  margin-bottom: 0.5rem;
}

.dim-desc {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: #888;
  letter-spacing: 2px;
}

/* Animations */
@keyframes drift { from { background-position: 0 0; } to { background-position: 50px 50px; } }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
@keyframes shake { 0% { transform: translate(0,0); } 25% { transform: translate(2px, 2px); } 50% { transform: translate(-2px, -2px); } 75% { transform: translate(2px, -2px); } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-thumb { background: #333; }

/* Naive UI Overrides */
:deep(.n-slider .n-slider-rail) { background-color: #333; }
:deep(.n-slider .n-slider-rail .n-slider-rail__fill) { background-color: #00f0ff; box-shadow: 0 0 10px #00f0ff; }
:deep(.n-slider .n-slider-handle) { background-color: #000; border: 2px solid #00f0ff; box-shadow: 0 0 10px #00f0ff; }

</style>
