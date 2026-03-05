<script setup lang="ts">
/**
 * Sector Blind: The Blind Zones (盲区)
 * 包含：智子盲区 (Sophon Blind Zone) & 深空扫描 (Deep Space Scan)
 * 风格：高对比度、噪点、雷达绿/加密红
 */
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { NTabs, NTabPane, NInput, NButton, NScrollbar, useMessage } from 'naive-ui'

const message = useMessage()
const activeTab = ref('shield')

// --- Tab 1: Sophon Blind Zone (智子盲区) ---
const chatHistory = ref<{ id: number; text: string; encrypted: boolean; sender: 'me' | 'system' }[]>([
  { id: 1, text: '智子屏蔽场已激活。此处为绝对隐私空间。', encrypted: false, sender: 'system' },
  { id: 2, text: '你可以畅所欲言。主不在乎。', encrypted: false, sender: 'system' }
])
const inputMsg = ref('')
const isShieldActive = ref(true)

function sendMsg() {
  if (!inputMsg.value.trim()) return
  
  const originalText = inputMsg.value
  const isSafe = isShieldActive.value
  
  // 模拟发送
  chatHistory.value.push({
    id: Date.now(),
    text: isSafe ? originalText : encryptText(originalText),
    encrypted: !isSafe,
    sender: 'me'
  })
  
  inputMsg.value = ''
  
  // 系统回复
  setTimeout(() => {
    chatHistory.value.push({
      id: Date.now() + 1,
      text: isSafe ? '消息已安全归档。' : '警告：智子已捕获该信息。',
      encrypted: false,
      sender: 'system'
    })
  }, 500)
}

function encryptText(text: string) {
  // 简单的“乱码”模拟
  return text.split('').map(() => String.fromCharCode(Math.floor(Math.random() * 50 + 800))).join('')
}

function toggleShield() {
  isShieldActive.value = !isShieldActive.value
  message.info(isShieldActive.value ? '屏蔽场已开启' : '屏蔽场已关闭，智子正在监听')
}

// --- Tab 2: Deep Space Scan (深空扫描) ---
const canvasRef = ref<HTMLCanvasElement | null>(null)
const scanResults = ref<string[]>([])
let scanAnimId: number
let scanAngle = 0

function initScanner() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  canvas.width = 600
  canvas.height = 600
  const cx = canvas.width / 2
  const cy = canvas.height / 2
  
  const signals: { x: number, y: number, life: number, label: string }[] = []
  
  function draw() {
    if (!canvas || !ctx) return
    // Fade out trail
    ctx.fillStyle = 'rgba(0, 20, 0, 0.1)'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    // Grid
    ctx.strokeStyle = '#004400'
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.arc(cx, cy, 100, 0, Math.PI * 2)
    ctx.arc(cx, cy, 200, 0, Math.PI * 2)
    ctx.arc(cx, cy, 280, 0, Math.PI * 2)
    ctx.moveTo(0, cy); ctx.lineTo(canvas.width, cy)
    ctx.moveTo(cx, 0); ctx.lineTo(cx, canvas.height)
    ctx.stroke()
    
    // Scanner Line
    scanAngle += 0.02
    ctx.strokeStyle = '#00ff00'
    ctx.lineWidth = 2
    ctx.shadowBlur = 10
    ctx.shadowColor = '#00ff00'
    ctx.beginPath()
    ctx.moveTo(cx, cy)
    ctx.lineTo(cx + Math.cos(scanAngle) * 300, cy + Math.sin(scanAngle) * 300)
    ctx.stroke()
    ctx.shadowBlur = 0
    
    // Random Signals
    if (Math.random() > 0.98) {
      const dist = Math.random() * 280
      const angle = scanAngle + Math.random() * 0.5 // Appear near scan line
      const x = cx + Math.cos(angle) * dist
      const y = cy + Math.sin(angle) * dist
      const types = ['尘埃云', '曲率航迹', '强相互作用力探测器', '未知碎片']
      const label = types[Math.floor(Math.random() * types.length)]
      
      signals.push({ x, y, life: 100, label })
      scanResults.value.unshift(`[${new Date().toLocaleTimeString()}] 发现目标：${label} (距离 ${(dist/10).toFixed(1)} 光年)`)
      if (scanResults.value.length > 5) scanResults.value.pop()
    }
    
    // Draw Signals
    for (let i = signals.length - 1; i >= 0; i--) {
      const s = signals[i]
      ctx.fillStyle = `rgba(255, 0, 0, ${s.life / 100})`
      ctx.beginPath()
      ctx.arc(s.x, s.y, 3, 0, Math.PI * 2)
      ctx.fill()
      
      ctx.fillStyle = `rgba(0, 255, 0, ${s.life / 100})`
      ctx.font = '10px monospace'
      ctx.fillText(s.label, s.x + 5, s.y)
      
      s.life--
      if (s.life <= 0) signals.splice(i, 1)
    }
    
    scanAnimId = requestAnimationFrame(draw)
  }
  draw()
}

function handleTabUpdate(v: string | number) {
  if (String(v) === 'scan') {
    window.setTimeout(initScanner, 100)
  }
}

onMounted(() => {
  if (activeTab.value === 'scan') window.setTimeout(initScanner, 100)
})

onUnmounted(() => {
  cancelAnimationFrame(scanAnimId)
})
</script>

<template>
  <div class="sector-blind">
    <div class="header">
      <h1 class="title">SECTOR B // THE BLIND ZONES</h1>
      <p class="subtitle">智子盲区 · 深空扫描</p>
    </div>

    <NTabs 
      v-model:value="activeTab" 
      type="line" 
      animated
      class="blind-tabs"
      @update:value="handleTabUpdate"
    >
      
      <!-- Tab 1: Sophon Blind Zone -->
      <NTabPane name="shield" tab="智子盲区 (SOPHON BLIND ZONE)">
        <div class="shield-room">
          <div class="shield-status" :class="{ active: isShieldActive }">
            <div class="status-icon"></div>
            <span>{{ isShieldActive ? '屏蔽场运行中 (SECURE)' : '警告：智子监听中 (MONITORED)' }}</span>
            <NButton size="small" :type="isShieldActive ? 'success' : 'error'" ghost @click="toggleShield">
              {{ isShieldActive ? '关闭屏蔽' : '开启屏蔽' }}
            </NButton>
          </div>
          
          <div class="chat-window">
            <NScrollbar>
              <div class="chat-content">
                <div 
                  v-for="msg in chatHistory" 
                  :key="msg.id" 
                  class="chat-bubble"
                  :class="[msg.sender, { encrypted: msg.encrypted }]"
                >
                  <div class="bubble-text">{{ msg.text }}</div>
                </div>
              </div>
            </NScrollbar>
          </div>
          
          <div class="chat-input">
            <NInput v-model:value="inputMsg" placeholder="在此输入计划..." @keyup.enter="sendMsg" />
            <NButton type="primary" @click="sendMsg">发送 (SEND)</NButton>
          </div>
        </div>
      </NTabPane>

      <!-- Tab 2: Deep Space Scan -->
      <NTabPane name="scan" tab="深空扫描 (DEEP SPACE SCAN)">
        <div class="scan-room">
          <div class="radar-container">
            <canvas ref="canvasRef" class="radar-canvas"></canvas>
            <div class="radar-overlay">
              <div class="scan-line-deco"></div>
            </div>
          </div>
          <div class="scan-log">
            <h3>扫描日志 (SCAN LOG)</h3>
            <div v-for="(log, i) in scanResults" :key="i" class="log-item">
              > {{ log }}
            </div>
          </div>
        </div>
      </NTabPane>

    </NTabs>
  </div>
</template>

<style scoped>
.sector-blind {
  min-height: 0;
  background: #050a05;
  color: #aaffaa;
  font-family: 'Rajdhani', sans-serif;
  display: flex;
  flex-direction: column;
}

.header {
  padding: 1.5rem 2rem;
  background: #020502;
  border-bottom: 1px solid #113311;
  text-align: center;
}

.title {
  font-size: 2rem;
  color: #33ff33;
  letter-spacing: 0.2em;
  margin: 0;
  text-shadow: 0 0 10px rgba(51, 255, 51, 0.3);
}

.subtitle {
  color: #558855;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.blind-tabs {
  flex: 1;
}

:deep(.n-tabs-nav) {
  background: #020502;
  padding: 0 2rem;
}

:deep(.n-tabs-tab) { color: #558855 !important; }
:deep(.n-tabs-tab--active) { color: #33ff33 !important; font-weight: bold; }
:deep(.n-tabs-bar) { background-color: #33ff33 !important; }

/* Shield Room */
.shield-room {
  max-width: 800px;
  margin: 2rem auto;
  border: 1px solid #113311;
  background: #001100;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 600px;
}

.shield-status {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background: #002200;
  border: 1px solid #33ff33;
  color: #33ff33;
}

.shield-status.active {
  box-shadow: 0 0 15px rgba(51, 255, 51, 0.2);
}

.chat-window {
  flex: 1;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid #113311;
  padding: 1rem;
  overflow: hidden;
}

.chat-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chat-bubble {
  padding: 0.8rem 1rem;
  border-radius: 4px;
  max-width: 70%;
}

.chat-bubble.system {
  align-self: flex-start;
  background: #002200;
  border: 1px solid #114411;
  color: #88cc88;
}

.chat-bubble.me {
  align-self: flex-end;
  background: #003300;
  border: 1px solid #33ff33;
  color: #fff;
}

.chat-bubble.encrypted {
  font-family: 'Courier New', monospace;
  color: #ff3333;
  border-color: #ff3333;
  background: #220000;
}

.chat-input {
  display: flex;
  gap: 1rem;
}

/* Scan Room */
.scan-room {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  padding: 2rem;
}

.radar-container {
  position: relative;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  border: 2px solid #004400;
  background: #000800;
  overflow: hidden;
}

.radar-canvas {
  width: 100%;
  height: 100%;
}

.scan-log {
  width: 100%;
  max-width: 600px;
  background: #001100;
  border: 1px solid #113311;
  padding: 1rem;
  font-family: monospace;
}

.log-item {
  color: #33ff33;
  margin-bottom: 0.5rem;
}
</style>
