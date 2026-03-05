<script setup lang="ts">
/**
 * Sector T: The Pendulum (三体摆)
 * 环境监测站 + 巨型单摆可视化 + 脱水控制台 + 人列计算机
 */
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUniverseStore } from '@/stores/universe'
import { useUserStore } from '@/stores/user'
import { NButton, useMessage } from 'naive-ui'

const router = useRouter()
const universe = useUniverseStore()
const userStore = useUserStore()
const message = useMessage()
const canvasRef = ref<HTMLCanvasElement | null>(null)
const civNumber = ref(184) // Start from 184
const doomProgress = ref(0)
const eraHistory = ref<number[]>([]) // 0: Stable, 1: Chaos
const lastDisaster = ref('')

// Local Simulation State
const simEnv = ref<'stable' | 'heat' | 'cold'>('stable')
const nextEraTimer = ref(500)

// 脱水状态：恒纪元时可浸泡，乱纪元时建议脱水
const isChaotic = computed(() => simEnv.value !== 'stable')

// Civilization Logic
function updateSimulation() {
  // Era Change Logic
  nextEraTimer.value--
  if (nextEraTimer.value <= 0) {
    // Change Era
    const rand = Math.random()
    if (simEnv.value === 'stable') {
      // Stable -> Chaos (High probability)
      simEnv.value = rand > 0.5 ? 'heat' : 'cold'
      nextEraTimer.value = Math.floor(Math.random() * 300 + 100)
      message.warning(simEnv.value === 'heat' ? '乱纪元降临！三日凌空！' : '乱纪元降临！严寒！')
    } else {
      // Chaos -> Stable (Low probability)
      if (rand < 0.3) {
        simEnv.value = 'stable'
        nextEraTimer.value = Math.floor(Math.random() * 800 + 400)
        message.success('恒纪元到来！文明复苏。')
        // if (universe.dehydrated) universe.toggleDehydrate()
      } else {
        // Chaos -> Chaos
        simEnv.value = simEnv.value === 'heat' ? 'cold' : 'heat'
        nextEraTimer.value = Math.floor(Math.random() * 300 + 100)
      }
    }
  }

  // Record History
  if (eraHistory.value.length > 50) eraHistory.value.shift()
  eraHistory.value.push(simEnv.value !== 'stable' ? 1 : 0)

  // Civ Logic
  if (simEnv.value === 'stable') {
    // Recovery
    if (doomProgress.value > 0) doomProgress.value -= 0.1
  } else {
    // Damage
    const damage = universe.dehydrated ? 0.02 : 0.1
    doomProgress.value += damage
    
    if (doomProgress.value >= 100) {
      destroyCivilization()
    }
  }
}

function destroyCivilization() {
  const cause = simEnv.value === 'heat' ? '三日凌空 (THREE SUNS)' : '严寒 (EXTREME COLD)'
  lastDisaster.value = `No.${civNumber.value} 毁灭于 ${cause}`
  message.error(`第 ${civNumber.value} 号文明在 ${cause} 中毁灭了。`)
  
  civNumber.value++
  doomProgress.value = 0
  if (!universe.dehydrated) universe.toggleDehydrate() 
}


// 人列计算机相关变量已移除


// 模拟单摆物理
let animationId: number
let angle = 0
let velocity = 0
let length = 300
const gravity = ref(0.5) // Base gravity (Interactive)

function modifyGravity() {
  if (!userStore.checkPermission(1, '修改初始参数 (N-Body Config)')) return
  gravity.value = gravity.value === 0.5 ? 0.1 : (gravity.value === 0.1 ? 2.0 : 0.5)
  message.success(`引力常数已重置: ${gravity.value} G`)
}

// Particle System
interface Particle {
  x: number; y: number; vx: number; vy: number; life: number; size: number; color: string;
}
const particles: Particle[] = []

function updateParticles(width: number, height: number) {
  // Spawn
  if (particles.length < 200) {
    if (simEnv.value === 'cold') {
      // Snow
      particles.push({
        x: Math.random() * width,
        y: -10,
        vx: (Math.random() - 0.5) * 1,
        vy: Math.random() * 2 + 1,
        life: 1,
        size: Math.random() * 2 + 1,
        color: `rgba(200, 230, 255, ${Math.random() * 0.5 + 0.3})`
      })
    } else if (simEnv.value === 'heat') {
      // Embers / Heat rising
      particles.push({
        x: Math.random() * width,
        y: height + 10,
        vx: (Math.random() - 0.5) * 0.5,
        vy: -(Math.random() * 2 + 1),
        life: 1,
        size: Math.random() * 3 + 1,
        color: `rgba(255, ${Math.floor(Math.random() * 100)}, 0, ${Math.random() * 0.5})`
      })
    } else {
      // Dust (Stable)
      if (Math.random() < 0.1) {
        particles.push({
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.2,
          vy: (Math.random() - 0.5) * 0.2,
          life: 1,
          size: Math.random() * 1.5,
          color: `rgba(255, 255, 255, ${Math.random() * 0.2})`
        })
      }
    }
  }

  // Update & Draw
  const canvas = canvasRef.value
  const ctx = canvas?.getContext('2d')
  if (!ctx) return

  for (let i = particles.length - 1; i >= 0; i--) {
    const p = particles[i]
    p.x += p.vx
    p.y += p.vy
    p.life -= 0.005
    
    if (simEnv.value === 'heat') p.size *= 0.99 // Shrink embers
    
    // Draw
    ctx.beginPath()
    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
    ctx.fillStyle = p.color
    ctx.fill()
    
    // Remove dead or out of bounds
    if (p.life <= 0 || p.y > height + 20 || p.y < -20) {
      particles.splice(i, 1)
    }
  }
}

function drawPendulum() {
  updateSimulation() // Run Logic

  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const width = canvas.width
  const height = canvas.height
  const originX = width / 2
  const originY = 50

  // 物理模拟 (简化版)
  // 乱纪元引力波动
  const envG = simEnv.value === 'stable' ? 1.0 : (simEnv.value === 'heat' ? 0.5 : 2.0)
  const chaos = simEnv.value === 'stable' ? 0 : (Math.random() - 0.5) * 0.2
  const force = -1 * (gravity.value * envG) * Math.sin(angle)
  
  velocity += force + chaos
  velocity *= 0.995 // Damping
  angle += velocity

  // Draw
  ctx.clearRect(0, 0, width, height)
  
  // Draw Particles Background
  updateParticles(width, height)
  
  // Cord
  const bobX = originX + length * Math.sin(angle)
  const bobY = originY + length * Math.cos(angle)
  
  ctx.beginPath()
  ctx.moveTo(originX, originY)
  ctx.lineTo(bobX, bobY)
  ctx.strokeStyle = simEnv.value === 'heat' ? '#ff3333' : simEnv.value === 'cold' ? '#88ccff' : '#00ffff'
  ctx.lineWidth = 2
  ctx.stroke()
  
  // Bob
  ctx.beginPath()
  ctx.arc(bobX, bobY, 20, 0, Math.PI * 2)
  ctx.fillStyle = '#000'
  ctx.fill()
  ctx.strokeStyle = ctx.strokeStyle
  ctx.lineWidth = 2
  ctx.stroke()
  
  // Glow
  ctx.shadowBlur = 15
  ctx.shadowColor = ctx.strokeStyle
  
  animationId = requestAnimationFrame(drawPendulum)
}

onMounted(() => {
  const canvas = canvasRef.value
  if (canvas) {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight * 0.8
    drawPendulum()
  }
})

onUnmounted(() => cancelAnimationFrame(animationId))

const envText = computed(() => {
  switch (simEnv.value) {
    case 'stable': return '恒纪元 (STABLE ERA)'
    case 'cold': return '乱纪元 · 严寒 (CHAOTIC COLD)'
    case 'heat': return '乱纪元 · 酷热 (CHAOTIC HEAT)'
    default: return 'UNKNOWN'
  }
})
</script>

<template>
  <div class="sector-pendulum">
    <div class="monitor-overlay">
      <h1 class="font-mono text-xl tracking-widest text-sophone">SECTOR T // THE PENDULUM</h1>
      <div class="status-panel">
        <div class="metric highlight-civ">
          <span class="label">CIVILIZATION</span>
          <span class="value">No. {{ civNumber }}</span>
        </div>
        <div class="metric">
          <span class="label">ENVIRONMENT</span>
          <span class="value" :class="simEnv">{{ envText }}</span>
        </div>
        <div class="metric">
          <span class="label">DOOMSDAY CLOCK</span>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: doomProgress + '%', backgroundColor: simEnv === 'stable' ? '#00ff41' : '#ff3333' }"></div>
          </div>
          <span class="sub-value">{{ doomProgress.toFixed(1) }}% TO DESTRUCTION</span>
        </div>
        <div class="metric">
          <span class="label">STATE</span>
          <span class="value" :class="{ dehydrated: universe.dehydrated }">
            {{ universe.dehydrated ? '干纤维形态 (DEHYDRATED)' : '常态 (ACTIVE)' }}
          </span>
        </div>
        <div class="metric">
          <span class="label">TEMPERATURE</span>
          <span class="value">{{ universe.temperature }} K</span>
        </div>
        <div class="metric">
          <span class="label">GRAVITY</span>
          <span class="value">{{ universe.gravity }} G</span>
        </div>
      </div>
      
      <div class="action-panel">
        <NButton 
          size="large" 
          :type="universe.dehydrated ? 'primary' : 'warning'" 
          ghost 
          @click="universe.toggleDehydrate"
        >
          {{ universe.dehydrated ? '浸泡 (REHYDRATE)' : '脱水 (DEHYDRATE)' }}
        </NButton>
        <p class="hint lore" v-if="universe.dehydrated">
          恒纪元到来后可执行浸泡复苏。代谢趋近于零，可度过乱纪元。
        </p>
        <p class="hint warn" v-else-if="isChaotic">
          警告：乱纪元生存需消耗大量资源，建议脱水。
        </p>
        <p class="hint" v-else>脱水后代谢趋近于零，可在乱纪元中保存生命。</p>

        <!-- Dehydration Visual -->
        <div class="granary" :class="{ active: universe.dehydrated }">
          <div class="granary-label">干仓 (STORAGE)</div>
          <div class="granary-slots">
            <div 
              class="roll" 
              v-for="i in 5" 
              :key="i"
              :class="{ filled: universe.dehydrated }"
              :style="{ animationDelay: `${i * 0.1}s` }"
            >
              📜
            </div>
          </div>
        </div>
        
        <NButton 
          class="mt-4" 
          block 
          ghost 
          type="warning"
          @click="modifyGravity"
        >
          修改引力参数 (MODIFY G)
        </NButton>

        <NButton 
          class="mt-4" 
          block 
          ghost 
          type="info"
          @click="router.push('/sector-v')"
        >
          前往人列计算机 (VON NEUMANN)
        </NButton>
      </div>
    </div>
    
    <canvas ref="canvasRef" class="pendulum-canvas"></canvas>
  </div>
</template>

<style scoped>
.sector-pendulum {
  position: relative;
  min-height: 0;
  background: #000;
  overflow: hidden;
}
.pendulum-canvas {
  display: block;
  width: 100%;
  height: 100%;
}

.monitor-overlay {
  position: absolute;
  top: 2rem;
  left: 2rem;
  z-index: 10;
  pointer-events: auto;
  max-width: 320px;
  max-height: calc(100vh - 4rem);
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 255, 255, 0.3) rgba(0, 0, 0, 0.5);
}

.monitor-overlay::-webkit-scrollbar {
  width: 4px;
}
.monitor-overlay::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.5);
}
.monitor-overlay::-webkit-scrollbar-thumb {
  background: rgba(0, 255, 255, 0.3);
  border-radius: 2px;
}

.status-panel {
  margin-top: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: rgba(0, 255, 255, 0.05);
  padding: 1.5rem;
  border: 1px solid rgba(0, 255, 255, 0.2);
  backdrop-filter: blur(5px);
}
.metric {
  display: flex;
  flex-direction: column;
}
.label {
  font-size: 0.7rem;
  color: #888;
  font-family: monospace;
}
.value {
  font-size: 1.2rem;
  font-family: monospace;
  color: #00ffff;
}
.value.stable { color: #00ff41; }
.value.cold { color: #88ccff; text-shadow: 0 0 10px #88ccff; }
.value.heat { color: #ff3333; text-shadow: 0 0 10px #ff3333; }
.value.rip { color: #ff00ff; animation: shake 0.1s infinite; }
.value.dehydrated { color: #b8860b; }

.metric.highlight-civ .value {
  color: #b8860b;
  text-shadow: 0 0 10px #b8860b;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: #333;
  margin: 0.5rem 0;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  transition: width 0.1s linear, background-color 0.5s;
}

.sub-value {
  font-size: 0.7rem;
  font-family: monospace;
  color: #666;
}

.action-panel {
  margin-top: 2rem;
}
.hint {
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: #888;
}
.hint.warn { color: #f59e0b; }
.hint.lore { color: #00ffff; opacity: 0.9; }

/* Granary Visual */
.granary {
  margin-top: 1.5rem;
  padding: 1rem;
  border: 1px dashed #444;
  background: rgba(0,0,0,0.5);
  opacity: 0.5;
  transition: opacity 0.3s;
}
.granary.active { opacity: 1; border-color: #b8860b; }
.granary-label { font-size: 0.7rem; color: #888; margin-bottom: 0.5rem; font-family: monospace; }
.granary-slots { display: flex; gap: 0.5rem; justify-content: center; }
.roll {
  font-size: 1.5rem;
  opacity: 0.1;
  transform: scaleY(0);
  transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.roll.filled {
  opacity: 1;
  transform: scaleY(1);
}

/* Computer Styles Removed */

@keyframes shake {
  0% { transform: translate(0, 0); }
  50% { transform: translate(2px, -2px); }
  100% { transform: translate(-2px, 2px); }
}

</style>
