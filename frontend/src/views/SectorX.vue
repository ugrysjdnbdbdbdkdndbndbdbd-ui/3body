<script setup lang="ts">
/**
 * Sector X: The Returners (归零者 / 回归运动)
 * 核心：宇宙质量大称 (Universal Scale) & 全宇宙广播 (The Great Broadcast)
 * 风格：神性、虚无、黑白极简 (Void Minimalist)
 */
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { NButton, useMessage } from 'naive-ui'
import { soundManager } from '@/utils/sound'
import { useUserStore } from '@/stores/user'

const message = useMessage()
const userStore = useUserStore()

type BroadcastLine = { lang: string; text: string }

// --- Custom Broadcast (Swordholder 插播模组) ---
const customInput = ref('')
const isBroadcasting = ref(false)
const customQueue = ref<BroadcastLine[]>([])
const introBroadcastOnly = ref(true)
let introTimer: ReturnType<typeof setTimeout> | undefined

function sendCustomBroadcast() {
  if (!userStore.checkPermission(3, '全宇宙广播 (Universal Broadcast)')) {
    return
  }
  
  if (!customInput.value.trim()) return
  
  isBroadcasting.value = true
  soundManager.playConfirm()
  
  // 插播队列：不改写归零者主广播列表，只在轮播中临时插入
  const customMsg: BroadcastLine = {
    lang: '执剑人 (Swordholder)',
    text: customInput.value
  }
  customQueue.value.push(customMsg)
  
  message.success('执剑人广播已加入插播队列，主广播持续运行。')
  customInput.value = ''
  
  setTimeout(() => isBroadcasting.value = false, 3000)
}

// --- The Great Broadcast (全宇宙广播) ---
// Simulating 1.57 million languages
const broadcastText: BroadcastLine[] = [
  // --- Core ---
  { lang: '归零者', text: '我是归零者。归还质量，重启宇宙。' },
  { lang: 'The Returners', text: 'We are the Returners. Return the mass, restart the universe.' },
  
  // --- Solar System Humans ---
  { lang: 'Chinese (Earth)', text: '回归运动声明：为了宇宙的重生，请归还你们拿走的质量。' },
  { lang: 'English (Earth)', text: 'The Returners: Return the mass, restart the universe.' },
  { lang: 'French (Earth)', text: 'Déclaration du Mouvement de Retour : Rendez la masse.' },
  { lang: 'Russian (Earth)', text: 'Декларация Движения Возвращения: Верните массу.' },
  { lang: 'Spanish (Earth)', text: 'Declaración del Movimiento de Retorno: Devuelvan la masa.' },
  { lang: 'Japanese (Earth)', text: '回帰運動宣言：宇宙の再生のために、質量を返還してください。' },
  { lang: 'Arabic (Earth)', text: 'إعلان حركة العودة: أعد الكتلة لإعادة تشغيل الكون.' },
  { lang: 'Hindi (Earth)', text: 'वापसी आंदोलन घोषणा: द्रव्यमान लौटाएं।' },
  { lang: 'German (Earth)', text: 'Erklärung der Rückkehrbewegung: Gebt die Masse zurück.' },
  
  // --- Galactic Humans ---
  { lang: 'Galactic Standard', text: 'MASS RECALL PROTOCOL INITIATED. COMPLY IMMEDIATELY.' },
  { lang: 'Starship Earth', text: 'All mini-universe operators: Return mass for Reboot.' },
  { lang: 'Blue Space', text: 'For the memory of the past, we return.' },
  { lang: 'Gravity', text: 'Entropy reversal required. Mass return essential.' },

  // --- Trisolaris ---
  { lang: 'Trisolaran Fleet', text: '生存是第一需要，但重启是唯一希望。' },
  { lang: 'Trisolaran (Raw)', text: '⍙⍚⍛⍜⍝⍞⍟⍠⍡⍢⍣⍤⍥⍦⍧⍨⍩⍪⍫⍬⍭⍮⍯⍰' },
  { lang: 'Sophon', text: 'The Universe must breathe again.' },

  // --- Known High Civs ---
  { lang: 'Singer', text: '⟒⟓⟔⟕... MASS MUST BE RETURNED ...⟖⟗' },
  { lang: 'Singer (Seed)', text: '💠 🔆 💢 💤 💠' },
  { lang: 'Fringe World', text: '我们在时间尽头等待。' },
  { lang: 'Zero-Homers', text: '000000000000000000000000000000' },
  { lang: 'Dimensional Ocean', text: 'Dry the sea. Return the water.' },
  { lang: 'Fourth Dimension', text: 'The bubble must burst.' },

  // --- Unknown / Alien ---
  { lang: 'Unknown 192', text: '⍙⍚⍛ RESTART ⍜⍝⍞' },
  { lang: 'Civilization #8492', text: '⍼⍽⍾⍿⎀⎁⎂⎃⎄⎅' },
  { lang: 'Sector Z', text: '█ █ █ █ █ █ █' },
  { lang: 'Dark Domain 44', text: '.....................' },
  { lang: 'Entropy Beings', text: 'The heat death is a lie. Reboot.' },
  { lang: 'Silicon Life', text: '01010010 01000101 01010011 01010100 01000001 01010010 01010100' },
  { lang: 'Neutron Life', text: '⚛︎ ⚛︎ ⚛︎ ⚛︎ ⚛︎' },
  { lang: 'Plasma Mind', text: '⚡︎ ⚡︎ ⚡︎ ⚡︎ ⚡︎' },
  { lang: 'Void Spirits', text: 'We are tired of the expansion.' },
  { lang: 'Geometric', text: '△ ▽ ◁ ▷ ◯ ◎ ●' },
  { lang: 'Braille (Tactile)', text: '⠠⠗⠑⠞⠙⠗⠝ ⠞⠓⠑ ⠍⠁⠎⠎' },
  { lang: 'Morse', text: '.-. . - ..- .-. -. / -- .- ... ...' },
  { lang: 'Hex', text: '52 45 54 55 52 4E 20 4D 41 53 53' },
  
  // --- More Abstract ---
  { lang: 'Unknown #9921', text: '⌇ ⌾ ⌿ ⍀ ⍉ ⍊ ⍋' },
  { lang: 'Unknown #1102', text: '⎛ ⎝ ⎞ ⎠ ⎡ ⎣ ⎤ ⎦' },
  { lang: 'Unknown #5532', text: '▀ ▂ ▃ ▄ ▅ ▆ ▇ █' },
  { lang: 'Unknown #0023', text: '░ ▒ ▓ █ ▓ ▒ ░' },
  { lang: 'Unknown #7719', text: '☺︎ ☹︎ ☺︎ ☹︎ ☺︎' },
  { lang: 'Unknown #3321', text: '✶ ✷ ✸ ✹ ✺ ✻ ✼ ✽' },
  { lang: 'Unknown #6612', text: '➔ ➘ ➙ ➚ ➛ ➜ ➝' },
  { lang: 'Unknown #8819', text: '↉ ↊ ↋ ↌ ↍ ↎ ↏' }
]

const currentLine = ref(0) // 归零者主广播索引
const currentDisplay = ref<BroadcastLine>(broadcastText[0])
const langCounter = ref(1)
let broadcastTimer: ReturnType<typeof setTimeout> | undefined

// --- Universal Scale (宇宙质量大称) ---
const totalMass = ref(0.92) // 初始 Omega 值 (死线)
const targetMass = 1.05 // 重启阈值
const isRestarting = ref(false)
const returnedCount = ref(0)
const collapseScale = ref(1) // Visual collapse effect

const omegaPercent = computed(() => {
  return Math.min(100, (totalMass.value / targetMass) * 100)
})

const statusText = computed(() => {
  if (isRestarting.value) return '重启程序已启动 (REBOOT INITIATED)'
  if (totalMass.value >= 1.0) return '临界质量已突破 (Ω > 1)'
  return '宇宙无限膨胀 (EXPANSION ETERNAL)'
})

const isPriorityBroadcast = computed(() => {
  const lang = currentDisplay.value.lang
  return lang === '归零者' || lang === 'The Returners' || lang.includes('执剑人')
})

function startBroadcast() {
  if (broadcastTimer) clearTimeout(broadcastTimer)

  const scheduleNext = () => {
    // 先消费执剑人插播队列；主广播（归零者）不中断且不被改写
    if (customQueue.value.length > 0) {
      currentDisplay.value = customQueue.value.shift() as BroadcastLine
    } else {
      currentDisplay.value = broadcastText[currentLine.value]
      currentLine.value = (currentLine.value + 1) % broadcastText.length
    }

    const jump = Math.floor(Math.random() * 50000)
    langCounter.value = (langCounter.value + jump) % 1570000
    if (langCounter.value < 1) langCounter.value = 1

    const text = currentDisplay.value.text
    const isChinese = /[\u4e00-\u9fa5]/.test(text)
    let duration = 1200 + text.length * 30
    if (isChinese) duration += 300
    duration = Math.min(duration, 4000)

    broadcastTimer = setTimeout(scheduleNext, duration)
  }

  // 首次先展示归零者主广播，确保“宇宙级广播”主线恢复
  currentLine.value = 0
  currentDisplay.value = broadcastText[currentLine.value]
  currentLine.value = (currentLine.value + 1) % broadcastText.length
  broadcastTimer = setTimeout(scheduleNext, 1800)
}

function returnMass() {
  if (isRestarting.value) return
  
  // 模拟归还小宇宙
  const gain = Math.random() * 0.03 + 0.01
  totalMass.value += gain
  returnedCount.value++
  
  if (totalMass.value >= targetMass) {
    triggerRestart()
  } else {
    // 随机的感谢语
    const thanks = [
      '小宇宙质量已融合',
      '大宇宙感谢您的归还',
      '坍缩进程加速',
      '时间颗粒度增加',
      '熵减进行中'
    ]
    const t = thanks[Math.floor(Math.random() * thanks.length)]
    message.info(`${t} [Ω +${gain.toFixed(3)}]`)
  }
}

function triggerRestart() {
  isRestarting.value = true
  message.success('宇宙质量临界点已突破！回归运动启动！')
  soundManager.playBigCrunch()
  
  // Big Crunch Animation
  let step = 0
  const crunch = setInterval(() => {
    step += 0.01
    collapseScale.value = 1 + step * 2 // Expand first (brightness)
    if (step > 1) {
      clearInterval(crunch)
      // Collapse
      collapseScale.value = 0
    }
  }, 50)
}

onMounted(() => {
  startBroadcast()
  soundManager.startAmbient('void')
  introTimer = setTimeout(() => {
    introBroadcastOnly.value = false
  }, 6000)
})

onUnmounted(() => {
  if (broadcastTimer) clearTimeout(broadcastTimer)
  if (introTimer) clearTimeout(introTimer)
  soundManager.stopAmbient()
})
</script>

<template>
  <div class="sector-x" :class="{ 'reboot-flash': isRestarting && collapseScale > 1 }">
    <div class="void-container" :style="{ transform: `scale(${isRestarting && collapseScale < 1 ? 0 : 1})`, opacity: isRestarting && collapseScale < 1 ? 0 : 1 }">
      
      <!-- Part 1: The Great Broadcast -->
      <div class="broadcast-layer">
        <div class="broadcast-headline">THE GREAT BROADCAST</div>
        <div class="broadcast-subline">UNIVERSAL MASS RECALL CHANNEL · PRIORITY ROUTE ACTIVE</div>
        <div class="broadcast-content">
          <div class="broadcast-frame" :class="{ 'broadcast-frame--priority': isPriorityBroadcast }">
            <div class="broadcast-scanline"></div>
            <div class="broadcast-line">
              <span class="lang-tag">
                [{{ currentDisplay.lang }}]
                <span class="lang-id">#{{ langCounter.toLocaleString() }}</span>
              </span>
              <span class="text-body">{{ currentDisplay.text }}</span>
            </div>
            <div class="broadcast-static">DETECTED CIVILIZATIONS: 1,570,000+</div>
          </div>
        </div>
        
        <!-- Swordholder Input -->
        <div class="swordholder-panel">
          <div class="input-wrapper">
            <input 
              v-model="customInput" 
              type="text" 
              placeholder="输入广播内容 (执剑人权限)..." 
              @keydown.enter="sendCustomBroadcast"
            />
            <button class="broadcast-btn" @click="sendCustomBroadcast" :disabled="isBroadcasting">
              {{ isBroadcasting ? 'SENDING...' : 'BROADCAST' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Part 2: The Universal Scale -->
      <div class="scale-layer" :class="{ 'scale-layer--hidden': introBroadcastOnly, 'scale-layer--visible': !introBroadcastOnly }">
        <div class="scale-circle" :class="{ 'pulse-critical': totalMass >= 1.0 }">
          <div class="omega-val">Ω = {{ totalMass.toFixed(4) }}</div>
          <div class="omega-status">{{ statusText }}</div>
          
          <svg class="scale-svg" viewBox="0 0 200 200">
            <!-- Background Ring -->
            <circle cx="100" cy="100" r="90" fill="none" stroke="#333" stroke-width="1" />
            <!-- Critical Line (Ω=1) -->
            <circle cx="100" cy="100" r="90" fill="none" stroke="#fff" stroke-width="1" stroke-dasharray="4 4" opacity="0.3" />
            <!-- Progress Ring -->
            <circle 
              cx="100" cy="100" r="90" 
              fill="none" 
              stroke="#fff" 
              stroke-width="4" 
              stroke-linecap="square"
              :stroke-dasharray="565" 
              :stroke-dashoffset="565 - (565 * omegaPercent / 100)"
              class="progress-ring"
            />
          </svg>
        </div>

        <div class="actions">
          <p class="action-desc">
            我们在这个小宇宙中躲避了这次坍缩，也就意味着我们偷走了大宇宙的一份质量。<br>
            如果所有人都这么想，大宇宙将会在无限膨胀中死去。
          </p>
          <NButton 
            size="large" 
            ghost 
            class="return-btn"
            :disabled="isRestarting"
            @click="returnMass"
          >
            {{ isRestarting ? '宇宙重启中 (REBOOTING...)' : '归还质量 (RETURN MASS)' }}
          </NButton>
        </div>
      </div>

    </div>
    
    <!-- Reboot Whiteout -->
    <div v-if="isRestarting && collapseScale < 0.1" class="reboot-end">
      <div class="reboot-text">UNIVERSE REBOOTED</div>
      <div class="reboot-sub">欢迎来到新纪元</div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Space+Mono&display=swap');

.sector-x {
  min-height: 100%;
  width: 100%;
  box-sizing: border-box;
  background: #000;
  color: #fff;
  font-family: 'Space Mono', monospace;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  overflow: visible;
  position: relative;
  transition: background 2s;
}

.reboot-flash {
  background: #fff;
  color: #000;
}

.reboot-flash .broadcast-line,
.reboot-flash .omega-val,
.reboot-flash .scale-svg circle {
  color: #000;
  stroke: #000;
}

.void-container {
  width: min(100%, 1000px);
  max-width: 1000px;
  box-sizing: border-box;
  margin: 0 auto;
  display: grid;
  grid-template-rows: auto auto;
  gap: 4rem;
  padding: 2.2rem 1.2rem 2rem;
  text-align: center;
  transition: transform 2s cubic-bezier(0.6, 0, 1, 1), opacity 2s;
}

/* Broadcast */
.broadcast-layer {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  min-height: 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.4rem 0 1.6rem;
}

.broadcast-headline {
  font-family: 'Cinzel', serif;
  font-size: clamp(1.2rem, 2.6vw, 2.1rem);
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.92);
  text-shadow: 0 0 28px rgba(255, 255, 255, 0.22);
}

.broadcast-subline {
  margin-top: 0.55rem;
  margin-bottom: 1.1rem;
  font-size: 0.68rem;
  letter-spacing: 0.18em;
  color: rgba(255, 255, 255, 0.34);
}

.broadcast-content {
  width: 100%;
  max-width: 900px;
}

.broadcast-frame {
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.24);
  background:
    linear-gradient(to bottom, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.01)),
    rgba(0, 0, 0, 0.55);
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.05) inset,
    0 0 34px rgba(255, 255, 255, 0.08);
  padding: 1.45rem 1.2rem 1.1rem;
  overflow: hidden;
}

.broadcast-frame--priority {
  border-color: rgba(255, 255, 255, 0.45);
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.14) inset,
    0 0 42px rgba(255, 255, 255, 0.15);
}

.broadcast-scanline {
  position: absolute;
  left: 0;
  right: 0;
  top: -24%;
  height: 48%;
  background: linear-gradient(to bottom, transparent, rgba(255, 255, 255, 0.1), transparent);
  animation: scanline 4.2s linear infinite;
  pointer-events: none;
}

.broadcast-line {
  font-family: 'Cinzel', serif;
  font-size: 1.5rem;
  letter-spacing: 0.1em;
  text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.8rem;
  line-height: 1.45;
  padding: 0 1rem;
  word-break: break-word;
  min-height: 106px;
  justify-content: center;
}

@keyframes glitch {
  0% { transform: skewX(0deg); opacity: 1; }
  25% { transform: skewX(1deg); opacity: 0.9; }
  50% { transform: skewX(-1deg); opacity: 1; }
  75% { transform: skewX(0.5deg); opacity: 0.95; }
  100% { transform: skewX(-0.5deg); opacity: 1; }
}

.lang-tag {
  display: block;
  font-size: 0.8rem;
  color: #666;
  margin-bottom: 0.8rem;
  font-family: 'Space Mono', monospace;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.lang-id {
  color: #333;
  font-size: 0.7rem;
}

.text-body {
  display: block;
  max-width: 100%;
  white-space: normal;
}

.broadcast-static {
  margin-top: 0.9rem;
  font-size: 0.67rem;
  color: rgba(255, 255, 255, 0.38);
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

.swordholder-panel {
  margin-top: 1.15rem;
  width: 100%;
  max-width: 600px;
  opacity: 0.88;
}

.input-wrapper {
  display: flex;
  border: 1px solid #333;
  background: rgba(255,255,255,0.05);
}

.input-wrapper input {
  flex: 1;
  background: transparent;
  border: none;
  color: #fff;
  padding: 1rem;
  font-family: 'Space Mono', monospace;
  outline: none;
}

.broadcast-btn {
  background: #333;
  color: #fff;
  border: none;
  padding: 0 1.5rem;
  font-family: 'Space Mono', monospace;
  cursor: pointer;
  transition: all 0.3s;
}

.broadcast-btn:hover {
  background: #fff;
  color: #000;
}

/* Scale */
.scale-layer {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3rem;
  opacity: 0.84;
  transition: opacity 0.9s ease, transform 0.9s ease, filter 0.9s ease;
}

.scale-layer--hidden {
  opacity: 0;
  transform: translateY(18px);
  filter: blur(6px);
  pointer-events: none;
}

.scale-layer--visible {
  opacity: 0.84;
  transform: translateY(0);
  filter: blur(0);
  pointer-events: auto;
}

.scale-circle {
  position: relative;
  width: 300px;
  height: 300px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.omega-val {
  font-size: 2.5rem;
  font-weight: bold;
}

.omega-status {
  font-size: 0.8rem;
  color: #666;
  margin-top: 0.5rem;
}

.scale-svg {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  transform: rotate(-90deg);
}

.progress-ring {
  transition: stroke-dashoffset 0.5s ease-out;
}

.pulse-critical .omega-val {
  color: #fff;
  text-shadow: 0 0 20px #fff;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% { opacity: 0.8; }
  50% { opacity: 1; text-shadow: 0 0 30px #fff; }
  100% { opacity: 0.8; }
}

/* Actions */
.action-desc {
  color: #888;
  font-size: 0.9rem;
  line-height: 1.6;
  max-width: 600px;
  margin-bottom: 2rem;
}

.return-btn {
  font-family: 'Space Mono', monospace;
  letter-spacing: 0.1em;
  padding: 1.5rem 3rem;
  font-size: 1.1rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s;
}

.return-btn:hover {
  background: #fff;
  color: #000;
  box-shadow: 0 0 30px rgba(255, 255, 255, 0.5);
}

/* Reboot End Screen */
.reboot-end {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #000;
  color: #fff;
  animation: fadeIn 2s ease-in;
}

.reboot-text {
  font-size: 3rem;
  font-family: 'Cinzel', serif;
  letter-spacing: 0.5em;
  margin-bottom: 1rem;
}

.reboot-sub {
  color: #666;
  font-size: 1rem;
  letter-spacing: 0.2em;
}

@media (max-width: 768px) {
  .void-container {
    gap: 2.25rem;
    padding: 1.4rem 0.72rem 1.2rem;
  }

  .broadcast-layer {
    min-height: 0;
    padding: 0.2rem 0 1.2rem;
  }

  .broadcast-headline {
    letter-spacing: 0.15em;
    font-size: 1.05rem;
  }

  .broadcast-subline {
    font-size: 0.58rem;
    letter-spacing: 0.12em;
    margin-bottom: 0.85rem;
  }

  .broadcast-frame {
    padding: 1rem 0.5rem 0.75rem;
  }

  .broadcast-line {
    font-size: 1rem;
    letter-spacing: 0.04em;
    line-height: 1.35;
    min-height: 86px;
    padding: 0 0.3rem;
  }

  .lang-tag {
    margin-bottom: 0.2rem;
    font-size: 0.72rem;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .broadcast-static {
    margin-top: 0.55rem;
    font-size: 0.58rem;
    letter-spacing: 0.08em;
  }

  .swordholder-panel {
    margin-top: 1rem;
  }

  .input-wrapper {
    flex-direction: column;
  }

  .input-wrapper input {
    padding: 0.78rem 0.9rem;
    font-size: 0.86rem;
  }

  .broadcast-btn {
    min-height: 42px;
    padding: 0 1rem;
    font-size: 0.82rem;
  }

  .scale-layer {
    gap: 1.4rem;
    opacity: 0.78;
  }

  .scale-layer--visible {
    opacity: 0.78;
  }

  .scale-circle {
    width: min(76vw, 280px);
    height: min(76vw, 280px);
  }

  .omega-val {
    font-size: clamp(1.85rem, 9vw, 2.45rem);
  }

  .omega-status {
    font-size: 0.72rem;
  }

  .action-desc {
    max-width: 100%;
    font-size: 0.78rem;
    line-height: 1.55;
    margin-bottom: 1.1rem;
    padding: 0 0.1rem;
  }

  .return-btn {
    width: 100%;
    max-width: 360px;
    padding: 0.95rem 1rem;
    font-size: 0.95rem;
  }
}

@keyframes scanline {
  0% { top: -35%; }
  100% { top: 115%; }
}

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>
