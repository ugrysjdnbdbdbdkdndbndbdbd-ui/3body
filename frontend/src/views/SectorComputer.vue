<script setup lang="ts">
/**
 * Sector V: Human Computer (人列计算机)
 * 冯·诺依曼架构 + 秦始皇人列方阵 + 逻辑门模拟
 */
import { ref, computed } from 'vue'
import { NButton, useMessage } from 'naive-ui'

const message = useMessage()

// --- Logic Gate State ---
type GateType = 'xor' | 'and' | 'half-adder' | 'full-adder'
const gateStep = ref<GateType>('xor')
const inputA = ref(0)
const inputB = ref(0)
const inputC = ref(0) // Carry In for Full Adder
const result = ref<number | null>(null)
const carryOut = ref<number | null>(null)

// --- Logic Functions ---
function expectedXor(): number {
  return inputA.value ^ inputB.value
}
function expectedAnd(): number {
  return inputA.value && inputB.value ? 1 : 0
}
function expectedHalfAdder(): { sum: number; carry: number } {
  const a = inputA.value
  const b = inputB.value
  return { sum: a ^ b, carry: a && b ? 1 : 0 }
}
// Bonus: Full Adder
function expectedFullAdder(): { sum: number; carry: number } {
  const a = inputA.value
  const b = inputB.value
  const c = inputC.value
  const sum = a ^ b ^ c
  const carry = (a & b) | (c & (a ^ b))
  return { sum, carry }
}

// --- Interaction ---
function setInputA() { inputA.value = inputA.value ? 0 : 1 }
function setInputB() { inputB.value = inputB.value ? 0 : 1 }
function setInputC() { inputC.value = inputC.value ? 0 : 1 }
function setResult() { result.value = result.value === null ? 0 : result.value === 0 ? 1 : null }
function setCarry() { carryOut.value = carryOut.value === null ? 0 : carryOut.value === 0 ? 1 : null }

function resetState() {
  inputA.value = 0
  inputB.value = 0
  inputC.value = 0
  result.value = null
  carryOut.value = null
}

function checkGate() {
  if (gateStep.value === 'xor') {
    if (result.value === expectedXor()) {
      message.success('异或门阵列校验通过。')
      gateStep.value = 'and'
      resetState()
    } else {
      message.error('异或输出错误。请检查举旗状态。')
    }
  } else if (gateStep.value === 'and') {
    if (result.value === expectedAnd()) {
      message.success('与门阵列校验通过。')
      gateStep.value = 'half-adder'
      resetState()
    } else {
      message.error('与门输出错误。')
    }
  } else if (gateStep.value === 'half-adder') {
    const { sum, carry } = expectedHalfAdder()
    if (result.value === sum && carryOut.value === carry) {
      message.success('半加器运行完美。')
      gateStep.value = 'full-adder'
      resetState()
    } else {
      message.error('计算错误。乱纪元逼近。')
    }
  } else if (gateStep.value === 'full-adder') {
    const { sum, carry } = expectedFullAdder()
    if (result.value === sum && carryOut.value === carry) {
      message.success('全加器运行完美！人列计算机已具备图灵完备性。')
      // Loop back or stay?
      // gateStep.value = 'xor' 
      // resetState()
    } else {
      message.error('全加器计算错误。')
    }
  }
}

const currentTitle = computed(() => {
  switch (gateStep.value) {
    case 'xor': return '异或门方阵 (XOR GATE)'
    case 'and': return '与门方阵 (AND GATE)'
    case 'half-adder': return '半加器 (HALF ADDER)'
    case 'full-adder': return '全加器 (FULL ADDER)'
  }
})

const currentDesc = computed(() => {
  switch (gateStep.value) {
    case 'xor': return '当两名输入士兵举旗颜色不同时，输出红旗(1)。'
    case 'and': return '仅当两名输入士兵都举红旗(1)时，输出红旗(1)。'
    case 'half-adder': return '组合异或门与与门，计算两位二进制数的和与进位。'
    case 'full-adder': return '引入进位输入(Carry In)，实现多位二进制加法的核心单元。'
  }
})

</script>

<template>
  <div class="sector-computer">
    <div class="header">
      <h1 class="title">SECTOR V // VON NEUMANN ARCHITECTURE</h1>
      <p class="subtitle">人列计算机主板 · 秦始皇一号</p>
    </div>

    <div class="main-stage">
      <!-- Left: Lore / Status -->
      <div class="info-panel">
        <div class="lore-box">
          <h2>{{ currentTitle }}</h2>
          <p class="desc">{{ currentDesc }}</p>
        </div>
        
        <div class="stats-box">
          <div class="stat">
            <span class="label">CPU CLOCK</span>
            <span class="val">0.003 Hz</span>
          </div>
          <div class="stat">
            <span class="label">CORES</span>
            <span class="val">30,000,000</span>
          </div>
          <div class="stat">
            <span class="label">ARCHITECTURE</span>
            <span class="val">HUMAN-PHALANX</span>
          </div>
        </div>
        
        <div class="controls">
          <NButton type="primary" size="large" block @click="checkGate">执行运算 (EXECUTE)</NButton>
          <NButton dashed class="mt-4" block @click="resetState">重置信号 (RESET)</NButton>
        </div>
      </div>

      <!-- Right: Visualization -->
      <div class="visual-panel">
        <div class="phalanx-wrapper">
          
          <!-- Input Layer -->
          <div class="layer input-layer">
            <div class="soldier-group" @click="setInputA">
              <div class="soldier" :class="{ active: inputA === 1 }">
                <div class="flag" :class="inputA === 1 ? 'red' : 'black'"></div>
                <div class="body">♟</div>
              </div>
              <div class="label">INPUT A <span class="bit">{{ inputA }}</span></div>
            </div>
            
            <div class="soldier-group" @click="setInputB">
              <div class="soldier" :class="{ active: inputB === 1 }">
                <div class="flag" :class="inputB === 1 ? 'red' : 'black'"></div>
                <div class="body">♟</div>
              </div>
              <div class="label">INPUT B <span class="bit">{{ inputB }}</span></div>
            </div>

            <div class="soldier-group" v-if="gateStep === 'full-adder'" @click="setInputC">
              <div class="soldier" :class="{ active: inputC === 1 }">
                <div class="flag" :class="inputC === 1 ? 'red' : 'black'"></div>
                <div class="body">♟</div>
              </div>
              <div class="label">CARRY IN <span class="bit">{{ inputC }}</span></div>
            </div>
          </div>

          <!-- Processing Visual (Circuit Lines) -->
          <div class="circuit-lines">
            <div class="line" :class="{ active: inputA || inputB || inputC }"></div>
            <div class="gate-symbol">
              {{ gateStep === 'xor' ? '⊕' : gateStep === 'and' ? '&' : '∑' }}
            </div>
            <div class="line" :class="{ active: result !== null }"></div>
          </div>

          <!-- Output Layer -->
          <div class="layer output-layer">
            <div class="soldier-group" @click="setResult">
              <div class="soldier output" :class="{ active: result === 1, unknown: result === null }">
                <div class="flag" :class="result === 1 ? 'red' : result === 0 ? 'black' : 'none'"></div>
                <div class="body">♟</div>
              </div>
              <div class="label">SUM / OUT <span class="bit">{{ result === null ? '?' : result }}</span></div>
            </div>

            <div class="soldier-group" v-if="gateStep === 'half-adder' || gateStep === 'full-adder'" @click="setCarry">
              <div class="soldier output" :class="{ active: carryOut === 1, unknown: carryOut === null }">
                <div class="flag" :class="carryOut === 1 ? 'red' : carryOut === 0 ? 'black' : 'none'"></div>
                <div class="body">♟</div>
              </div>
              <div class="label">CARRY OUT <span class="bit">{{ carryOut === null ? '?' : carryOut }}</span></div>
            </div>
          </div>

        </div>
        
        <div class="hint-text">
          点击士兵切换举旗状态。红旗=1，黑旗=0。<br>
          "成千上万面旗帜的翻动，形成了一幅幅数字电路的波纹。"
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sector-computer {
  height: 100%;
  background: #050505;
  color: #ccc;
  display: flex;
  flex-direction: column;
  padding: 2rem;
  background-image: radial-gradient(circle at 50% 50%, #111 0%, #050505 80%);
}

.header {
  border-bottom: 1px solid #333;
  padding-bottom: 1rem;
  margin-bottom: 2rem;
}

.title {
  font-family: monospace;
  color: #00ffff;
  font-size: 1.8rem;
  letter-spacing: 0.1em;
  margin: 0;
}

.subtitle {
  color: #666;
  font-size: 0.9rem;
  margin: 0.5rem 0 0 0;
}

.main-stage {
  flex: 1;
  display: flex;
  gap: 3rem;
  align-items: center;
  justify-content: center;
}

.info-panel {
  flex: 0 0 350px;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.lore-box h2 {
  color: #fff;
  font-family: monospace;
  border-left: 3px solid #00ffff;
  padding-left: 1rem;
  margin: 0 0 1rem 0;
}

.desc {
  color: #888;
  line-height: 1.6;
  font-size: 0.9rem;
}

.stats-box {
  background: rgba(255, 255, 255, 0.05);
  padding: 1.5rem;
  border: 1px solid #333;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.stat {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat .label { font-size: 0.7rem; color: #666; font-family: monospace; }
.stat .val { font-size: 1rem; color: #00ffff; font-family: monospace; }

.visual-panel {
  flex: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
  border: 1px dashed #333;
  position: relative;
}

.phalanx-wrapper {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  align-items: center;
}

.layer {
  display: flex;
  gap: 4rem;
}

.soldier-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
  transition: transform 0.2s;
}

.soldier-group:hover { transform: translateY(-5px); }

.soldier {
  font-size: 5rem;
  line-height: 1;
  position: relative;
  width: 80px;
  height: 100px;
  display: flex;
  justify-content: center;
  align-items: flex-end;
}

.body {
  color: #444;
  z-index: 1;
  transition: color 0.3s;
}

.soldier.active .body { color: #fff; text-shadow: 0 0 20px rgba(255,255,255,0.5); }

.flag {
  position: absolute;
  top: 10px;
  left: 50%;
  width: 4px;
  height: 80px;
  background: #666;
  transform-origin: bottom center;
  transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  transform: rotate(-30deg); /* Down/Black */
  z-index: 0;
}

.flag::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 40px;
  height: 30px;
  background: #111;
  transition: background 0.3s, box-shadow 0.3s;
}

.flag.red {
  transform: rotate(0deg) translateY(-20px);
}
.flag.red::after {
  background: #ff3333;
  box-shadow: 0 0 15px #ff3333;
}

.flag.black {
  transform: rotate(-45deg);
}

.flag.none { opacity: 0; }

.label {
  font-family: monospace;
  font-size: 0.8rem;
  color: #666;
  letter-spacing: 0.1em;
}

.bit {
  color: #00ffff;
  font-weight: bold;
  margin-left: 0.5rem;
  font-size: 1rem;
}

.circuit-lines {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100px;
  justify-content: center;
  position: relative;
}

.line {
  width: 2px;
  height: 30px;
  background: #333;
  transition: background 0.3s, box-shadow 0.3s;
}

.line.active { background: #00ffff; box-shadow: 0 0 10px #00ffff; }

.gate-symbol {
  width: 50px;
  height: 50px;
  border: 2px solid #666;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: #666;
  background: #111;
  margin: 10px 0;
  font-family: monospace;
}

.hint-text {
  margin-top: 3rem;
  text-align: center;
  color: #555;
  font-style: italic;
  font-size: 0.85rem;
}

.mt-4 { margin-top: 1rem; }
</style>
