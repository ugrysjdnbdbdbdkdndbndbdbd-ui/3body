<script setup lang="ts">
/**
 * Sector G: The 4th Dimension (四维碎片)
 * 核心：四维视觉 (Tesseract), 魔戒对话 (The Ring), 高维手术 (Surgery)
 * 风格：故障艺术 (Glitch), 深紫/霓虹
 */
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { NTabs, NTabPane, NInput, NButton, useMessage } from 'naive-ui'
import { TresCanvas } from '@tresjs/core'
import { OrbitControls } from '@tresjs/cientos'
import The4DTesseract from '@/components/The4DTesseract.vue'
import { soundManager } from '@/utils/sound'
import { useUserStore } from '@/stores/user'

onMounted(() => {
  soundManager.startAmbient('void')
})

onUnmounted(() => {
  soundManager.stopAmbient()
})

const message = useMessage()
const userStore = useUserStore()
const activeTab = ref('tesseract')

// --- Tab 2: The Ring (Chat) ---
const chatHistory = reactive([
  { role: 'ring', text: '我是墓地。我是死人。我是死的。' },
  { role: 'ring', text: '海干了。鱼要到水洼里去，只有那里有水。' }
])
const userInput = ref('')
const isTyping = ref(false)

function sendToRing() {
  if (!userInput.value.trim()) return
  
  const q = userInput.value
  chatHistory.push({ role: 'human', text: q })
  userInput.value = ''
  isTyping.value = true
  
  setTimeout(() => {
    let reply = '...'
    if (q.includes('海') || q.includes('干')) reply = '把海弄干的鱼在海干前上了陆地，从一片黑暗森林奔向另一片黑暗森林。'
    else if (q.includes('你') || q.includes('谁')) reply = '我只是一个记忆体。'
    else if (q.includes('四维') || q.includes('高维')) reply = '方寸之间，深不见底。'
    else if (q.includes('人类')) reply = '弱小的鱼。'
    else reply = '不懂。数据已丢失。'
    
    chatHistory.push({ role: 'ring', text: reply })
    isTyping.value = false
  }, 1500)
}

// --- Tab 3: High-Dim Surgery (Game) ---
// 简化的逻辑游戏：从 3x3 网格的封闭“盒子”中取出中心的“心”，而不经过边界。
// 实际上通过“切换层级”来模拟第4维移动。
const surgeryState = reactive({
  layer: 0, // 0: 3D Slice A, 1: 3D Slice B (High Dim)
  grid: [
    [1, 1, 1],
    [1, 2, 1], // 2 is the Target (Heart)
    [1, 1, 1]
  ],
  hasHeart: false,
  message: '目标：取出红心。规则：不能穿过白墙。'
})

function toggleLayer() {
  if (!userStore.checkPermission(1, '高维移动 (High-Dimensional Movement)')) {
    return
  }
  surgeryState.layer = surgeryState.layer === 0 ? 1 : 0
  surgeryState.message = surgeryState.layer === 1 
    ? '进入四维空间... 墙壁消失了。' 
    : '返回三维空间... 墙壁闭合。'
}

function clickCell(r: number, c: number) {
  const cell = surgeryState.grid[r][c]
  
  // Layer 0: Wall (1) blocks interaction
  if (surgeryState.layer === 0) {
    if (cell === 1) {
      message.error('无法穿过墙壁！')
      return
    }
    if (cell === 2) {
      // In 3D, fully enclosed, cannot reach
      message.error('无法触及！它被封在里面。')
      return
    }
  }
  
  // Layer 1: High Dim - Walls are "below" us, accessible
  if (surgeryState.layer === 1) {
    if (cell === 2) {
      surgeryState.grid[r][c] = 0
      surgeryState.hasHeart = true
      message.success('已从高维取走心脏！')
      surgeryState.message = '手术成功。请返回三维确认。'
    } else if (cell === 1) {
      message.info('这是三维的墙，在四维看来只是一条线。')
    }
  }
}

</script>

<template>
  <div class="sector-g">
    <div class="header">
      <h1 class="glitch-text" data-text="SECTOR G // 4TH DIMENSION">SECTOR G // 4TH DIMENSION</h1>
      <p class="subtitle">魔戒 · 墓地 · 维度碎片</p>
    </div>

    <NTabs v-model:value="activeTab" type="segment" class="g-tabs">
      
      <!-- Module 1: Tesseract -->
      <NTabPane name="tesseract" tab="四维视觉 (VISION)">
        <div class="canvas-container">
          <TresCanvas window-size clear-color="#050005" presets="realistic">
            <TresPerspectiveCamera :position="[4, 4, 4]" :look-at="[0, 0, 0]" />
            <OrbitControls :enable-zoom="true" :auto-rotate="true" :auto-rotate-speed="1" />
            <TresAmbientLight :intensity="1" />
            <The4DTesseract />
          </TresCanvas>
          <div class="overlay-info">
            <p>"方寸之间，深不见底。"</p>
            <p class="sub-info">超立方体投影 (TESSERACT PROJECTION)</p>
          </div>
        </div>
      </NTabPane>

      <!-- Module 2: The Ring -->
      <NTabPane name="ring" tab="魔戒对话 (THE RING)">
        <div class="ring-interface">
          <div class="ring-monitor">
            <div class="scan-line"></div>
            <div class="chat-flow">
              <div v-for="(msg, i) in chatHistory" :key="i" class="msg-row" :class="msg.role">
                <span class="role-label">{{ msg.role === 'ring' ? '魔戒' : '你' }} ></span>
                <span class="msg-text">{{ msg.text }}</span>
              </div>
              <div v-if="isTyping" class="msg-row ring">
                <span class="role-label">魔戒 ></span>
                <span class="msg-text blink">_</span>
              </div>
            </div>
          </div>
          <div class="ring-input">
            <input 
              v-model="userInput" 
              @keyup.enter="sendToRing" 
              type="text" 
              placeholder="向它提问..." 
              :disabled="isTyping"
            />
            <button @click="sendToRing" :disabled="isTyping">发送 (SEND)</button>
          </div>
        </div>
      </NTabPane>

      <!-- Module 3: High-Dim Surgery -->
      <NTabPane name="surgery" tab="高维手术 (SURGERY)">
        <div class="surgery-container">
          <div class="surgery-board" :class="{ 'high-dim': surgeryState.layer === 1 }">
            <div class="board-header">
              <span>维度: {{ surgeryState.layer === 0 ? '3D (常规)' : '4D (高维)' }}</span>
              <button class="dim-switch" @click="toggleLayer">
                {{ surgeryState.layer === 0 ? '进入四维 (ENTER 4D)' : '返回三维 (RETURN 3D)' }}
              </button>
            </div>
            
            <div class="grid-3x3">
              <template v-for="(row, r) in surgeryState.grid" :key="r">
                <div 
                  v-for="(cell, c) in row" 
                  :key="`${r}-${c}`"
                  class="cell"
                  :class="{ 
                    wall: cell === 1, 
                    target: cell === 2, 
                    empty: cell === 0,
                    'wall-faded': surgeryState.layer === 1 && cell === 1
                  }"
                  @click="clickCell(r, c)"
                >
                  <span v-if="cell === 2">❤️</span>
                </div>
              </template>
            </div>
            
            <div class="status-log">
              {{ surgeryState.message }}
            </div>
            
            <div class="inventory" v-if="surgeryState.hasHeart">
              物品栏: [ ❤️ 心脏 ]
            </div>
          </div>
        </div>
      </NTabPane>

    </NTabs>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Share+Tech+Mono&display=swap');

.sector-g {
  min-height: 0;
  background: #050005;
  color: #d0a0ff;
  font-family: 'Share Tech Mono', monospace;
  display: flex;
  flex-direction: column;
}

.header {
  padding: 1rem 2rem;
  border-bottom: 1px solid #330033;
  background: #0a000a;
}

.glitch-text {
  font-family: 'Press Start 2P', cursive;
  font-size: 1.5rem;
  color: #ff00ff;
  text-shadow: 2px 2px #00ffff;
  position: relative;
}

.subtitle {
  color: #8855aa;
  font-size: 0.8rem;
  margin-top: 0.5rem;
}

.g-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
}

:deep(.n-tabs-nav) {
  background: #0a000a;
  border-bottom: 1px solid #330033;
}
:deep(.n-tabs-tab) { color: #8855aa !important; }
:deep(.n-tabs-tab--active) { color: #ff00ff !important; font-weight: bold; }

/* Tesseract */
.canvas-container {
  width: 100%;
  height: 100%;
  position: relative;
  min-height: 60vh;
}
.overlay-info {
  position: absolute;
  bottom: 2rem;
  left: 2rem;
  pointer-events: none;
  background: rgba(0,0,0,0.5);
  padding: 1rem;
  border: 1px solid #ff00ff;
}
.sub-info { font-size: 0.7rem; color: #00ffff; }

/* The Ring */
.ring-interface {
  max-width: 800px;
  margin: 2rem auto;
  border: 4px solid #333;
  background: #000;
  display: flex;
  flex-direction: column;
  height: 60vh;
}
.ring-monitor {
  flex: 1;
  background: radial-gradient(circle, #1a001a 0%, #000 100%);
  padding: 2rem;
  overflow-y: auto;
  position: relative;
  font-family: monospace;
}
.scan-line {
  position: absolute;
  top: 0; left: 0; right: 0; height: 2px;
  background: rgba(255, 0, 255, 0.1);
  animation: scan 3s linear infinite;
  pointer-events: none;
}
@keyframes scan { 0% { top: 0; } 100% { top: 100%; } }

.msg-row { margin-bottom: 1rem; line-height: 1.4; }
.role-label { margin-right: 1rem; opacity: 0.5; }
.msg-row.ring { color: #ff00ff; text-shadow: 0 0 5px #ff00ff; }
.msg-row.human { color: #00ffff; }
.blink { animation: blink 1s infinite; }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }

.ring-input {
  display: flex;
  border-top: 2px solid #333;
}
.ring-input input {
  flex: 1;
  background: #111;
  border: none;
  color: #fff;
  padding: 1rem;
  font-family: inherit;
}
.ring-input button {
  background: #330033;
  color: #ff00ff;
  border: none;
  padding: 0 2rem;
  cursor: pointer;
  font-weight: bold;
}
.ring-input button:hover { background: #550055; }

/* Surgery */
.surgery-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  padding: 2rem;
}
.surgery-board {
  background: #111;
  padding: 2rem;
  border: 2px solid #444;
  width: 400px;
  transition: all 0.5s;
}
.surgery-board.high-dim {
  border-color: #00ffff;
  box-shadow: 0 0 20px rgba(0,255,255,0.2);
  transform: scale(1.05) rotateX(10deg);
}

.board-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.dim-switch {
  background: #004444;
  color: #00ffff;
  border: 1px solid #00ffff;
  padding: 0.5rem 1rem;
  cursor: pointer;
}
.dim-switch:hover { background: #006666; }

.grid-3x3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 2rem;
}
.cell {
  aspect-ratio: 1;
  background: #222;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  cursor: pointer;
  transition: all 0.3s;
}
.cell.wall { background: #fff; }
.cell.wall-faded { background: rgba(255,255,255,0.1); border: 1px dashed #fff; }
.cell.target { background: #220000; }
.cell:hover { opacity: 0.8; }

.status-log {
  padding: 1rem;
  background: #000;
  border: 1px solid #333;
  color: #aaa;
  font-size: 0.9rem;
}
.inventory {
  margin-top: 1rem;
  color: #ff3333;
  font-weight: bold;
}
</style>
