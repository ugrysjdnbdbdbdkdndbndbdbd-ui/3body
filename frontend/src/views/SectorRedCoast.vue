<script setup lang="ts">
/**
 * Sector R: Red Coast Base (红岸基地)
 * 1970s Retro-Futurism Console
 * 核心功能：天线校准、太阳增益、信号监听、发射授权
 * 特性：中英文系统切换 (CN/EN Toggle)
 */
import { ref, reactive, onMounted, computed, onUnmounted } from 'vue'
import { API, apiUrl } from '@/constants'
import { NSlider, NSwitch, NProgress, useMessage } from 'naive-ui'
import type { Signal } from '@/types/red_coast'
import ETOAssembly from '@/components/ETOAssembly.vue'

const message = useMessage()
const viewMode = ref<'CONSOLE' | 'ETO'>('CONSOLE')

// --- I18n System ---
type Lang = 'CN' | 'EN'
const lang = ref<Lang>('CN')

const i18n = {
  CN: {
    TITLE: '红岸基地 // 中央控制系统',
    STATUS: '系统状态',
    ONLINE: '在线',
    TX: '发射中',
    ALERT: '警报',
    ANTENNA_ALIGNMENT: '天线姿态校准',
    AZIMUTH: '方位角',
    ELEVATION: '仰角',
    SIGNAL_GAIN: '信号增益',
    AUTO_TRACKING: '自动追踪',
    MANUAL_MODE: '手动模式',
    MONITOR: '主监视器',
    WARNING: '警告',
    ACKNOWLEDGE: '确认',
    TRANSMISSION_CONTROL: '发射控制',
    FREQUENCY: '发射频率',
    OUTPUT_POWER: '输出功率',
    SOLAR_AMP: '太阳增益',
    CHARGE_CAPACITORS: '电容充能',
    CHARGING: '充能中...',
    AUTH_CODE: '授权码',
    BROADCAST: '发射广播',
    // Logs
    LOG_BOOT: '系统启动序列初始化...',
    LOG_PERIPHERALS: '检查外设... 完成',
    LOG_DRIVERS: '加载天线驱动... 完成',
    LOG_UPLINK: '建立上行链路... 等待中',
    LOG_READY: '就绪。等待指令。',
    LOG_AUTH_HINT: '注意：A级安全权限。发射需授权码（提示：首次发射年份）',
    LOG_TRACKING_ON: '自动追踪已开启。正在校准至太阳目标...',
    LOG_TARGET_LOCKED: '目标锁定：太阳',
    LOG_MANUAL_OVERRIDE: '手动接管。追踪已解除。',
    LOG_CHARGE_START: '电容充能序列启动...',
    LOG_CHARGE_COMPLETE: '电容满载。随时可以发射。',
    LOG_ERR_CHARGE: '错误：能量不足',
    LOG_ERR_AUTH: '错误：授权码无效。拒绝访问。',
    LOG_TX_START: '发射中... 频率:{freq}MHz 功率:{power}MW',
    LOG_SOLAR_WARN: '警告：检测到日凌干扰。信号增益已确认。',
    LOG_TX_COMPLETE: '发射完成。系统冷却中。',
    LOG_STANDBY: '系统待机。',
    LOG_ANOMALY: '警告：检测到异常信号。',
    LOG_DECODED: '消息已解码。优先级：ALPHA。',
    LOG_BUFFER_CLEARED: '缓冲区已清除。恢复监听。',
    MSG_DO_NOT_ANSWER: '不要回答！不要回答！不要回答！'
  },
  EN: {
    TITLE: 'RED COAST BASE // CONTROL SYSTEM',
    STATUS: 'STATUS',
    ONLINE: 'ONLINE',
    TX: 'TX',
    ALERT: 'ALERT',
    ANTENNA_ALIGNMENT: 'ANTENNA ALIGNMENT',
    AZIMUTH: 'AZIMUTH',
    ELEVATION: 'ELEVATION',
    SIGNAL_GAIN: 'SIGNAL GAIN',
    AUTO_TRACKING: 'AUTO TRACKING',
    MANUAL_MODE: 'MANUAL MODE',
    MONITOR: 'MONITOR',
    WARNING: 'WARNING',
    ACKNOWLEDGE: 'ACKNOWLEDGE',
    TRANSMISSION_CONTROL: 'TRANSMISSION CONTROL',
    FREQUENCY: 'FREQUENCY',
    OUTPUT_POWER: 'OUTPUT POWER',
    SOLAR_AMP: 'SOLAR AMP',
    CHARGE_CAPACITORS: 'CHARGE CAPACITORS',
    CHARGING: 'CHARGING...',
    AUTH_CODE: 'AUTH CODE',
    BROADCAST: 'BROADCAST',
    // Logs
    LOG_BOOT: 'SYSTEM_BOOT_SEQUENCE_INITIATED...',
    LOG_PERIPHERALS: 'CHECKING_PERIPHERALS... OK',
    LOG_DRIVERS: 'LOADING_ANTENNA_DRIVERS... OK',
    LOG_UPLINK: 'ESTABLISHING_UPLINK... WAITING',
    LOG_READY: 'READY_FOR_INPUT.',
    LOG_AUTH_HINT: 'NOTICE: SECURITY_LEVEL_A. AUTH_CODE_REQUIRED_FOR_TX (HINT: FIRST_TRANSMISSION_YEAR)',
    LOG_TRACKING_ON: 'AUTO_TRACKING_ENGAGED. ALIGNING TO SOLAR TARGET...',
    LOG_TARGET_LOCKED: 'TARGET_LOCKED: SOL',
    LOG_MANUAL_OVERRIDE: 'MANUAL_OVERRIDE. TRACKING_DISENGAGED.',
    LOG_CHARGE_START: 'CAPACITOR_CHARGING_STARTED...',
    LOG_CHARGE_COMPLETE: 'CAPACITORS_FULL. READY_TO_FIRE.',
    LOG_ERR_CHARGE: 'ERROR: INSUFFICIENT_CHARGE',
    LOG_ERR_AUTH: 'ERROR: AUTH_CODE_INVALID. PERMISSION_DENIED.',
    LOG_TX_START: 'TRANSMITTING... FREQ:{freq}MHz POWER:{power}MW',
    LOG_SOLAR_WARN: 'CRITICAL: SOLAR_AMPLIFICATION_ACTIVE. SIGNAL_BOOST_CONFIRMED.',
    LOG_TX_COMPLETE: 'TRANSMISSION_COMPLETE. SYSTEM_COOLING.',
    LOG_STANDBY: 'SYSTEM_STANDBY.',
    LOG_ANOMALY: 'WARNING: ANOMALOUS_SIGNAL_DETECTED.',
    LOG_DECODED: 'MESSAGE_DECODED. PRIORITY: ALPHA.',
    LOG_BUFFER_CLEARED: 'BUFFER_CLEARED. RESUMING_MONITOR.',
    MSG_DO_NOT_ANSWER: 'DO NOT ANSWER! DO NOT ANSWER! DO NOT ANSWER!'
  }
}

function t(key: string, params: Record<string, any> = {}) {
  let text = i18n[lang.value][key as keyof typeof i18n['CN']] || key
  for (const [k, v] of Object.entries(params)) {
    text = text.replace(`{${k}}`, String(v))
  }
  return text
}

function toggleLang() {
  lang.value = lang.value === 'CN' ? 'EN' : 'CN'
}

// --- State Management ---
const systemTime = ref(new Date().toISOString())
const timeInterval = setInterval(() => {
  systemTime.value = new Date().toISOString()
}, 1000)

interface LogEntry {
  key: string
  params?: Record<string, any>
  time: string
}

const rawLogs = ref<LogEntry[]>([
  { key: 'LOG_BOOT', time: new Date().toLocaleTimeString() },
  { key: 'LOG_PERIPHERALS', time: new Date().toLocaleTimeString() },
  { key: 'LOG_DRIVERS', time: new Date().toLocaleTimeString() },
  { key: 'LOG_UPLINK', time: new Date().toLocaleTimeString() },
  { key: 'LOG_READY', time: new Date().toLocaleTimeString() },
  { key: 'LOG_AUTH_HINT', time: new Date().toLocaleTimeString() }
])

const terminalLogs = computed(() => {
  return rawLogs.value.map(log => {
    return `[${log.time}] ${t(log.key, log.params)}`
  })
})

function addLog(key: string, params: Record<string, any> = {}) {
  rawLogs.value.push({
    key,
    params,
    time: new Date().toLocaleTimeString()
  })
  if (rawLogs.value.length > 15) rawLogs.value.shift()
}

// Antenna State
const antenna = reactive({
  azimuth: 120, // 0-360
  elevation: 45, // 0-90
  targetAzimuth: 180, // Sun position (simulated)
  targetElevation: 60,
  aligned: false,
  tracking: false
})

// Transmission State
const tx = reactive({
  powerLevel: 15, // MW
  frequency: 12000, // MHz
  charging: false,
  chargeProgress: 0,
  ready: false,
  transmitting: false,
  cooling: false,
  sunAmplified: false,
  authCode: ''
})

// Incoming State
const rx = reactive({
  listening: true,
  signalStrength: 10,
  noiseLevel: 5,
  detectedMessage: null as string | null,
  decoding: false,
  decodeProgress: 0
})

// --- Computed ---
const alignmentQuality = computed(() => {
  const azDiff = Math.abs(antenna.azimuth - antenna.targetAzimuth)
  const elDiff = Math.abs(antenna.elevation - antenna.targetElevation)
  const totalDiff = Math.sqrt(azDiff * azDiff + elDiff * elDiff)
  return Math.max(0, 100 - totalDiff * 5) // 0-100%
})

const isAligned = computed(() => alignmentQuality.value > 95)

const outputPower = computed(() => {
  let base = tx.powerLevel
  if (tx.sunAmplified && isAligned.value) {
    return base * 10000 // Sun amplification factor
  }
  return base
})

// --- Methods ---

function toggleTracking() {
  antenna.tracking = !antenna.tracking
  if (antenna.tracking) {
    addLog('LOG_TRACKING_ON')
    // Simulate auto-alignment
    const interval = setInterval(() => {
      if (!antenna.tracking) {
        clearInterval(interval)
        return
      }
      
      if (antenna.azimuth < antenna.targetAzimuth) antenna.azimuth += 1
      else if (antenna.azimuth > antenna.targetAzimuth) antenna.azimuth -= 1
      
      if (antenna.elevation < antenna.targetElevation) antenna.elevation += 1
      else if (antenna.elevation > antenna.targetElevation) antenna.elevation -= 1
      
      if (Math.abs(antenna.azimuth - antenna.targetAzimuth) < 2 && Math.abs(antenna.elevation - antenna.targetElevation) < 2) {
        antenna.azimuth = antenna.targetAzimuth
        antenna.elevation = antenna.targetElevation
        addLog('LOG_TARGET_LOCKED')
        clearInterval(interval)
      }
    }, 50)
  } else {
    addLog('LOG_MANUAL_OVERRIDE')
  }
}

function startCharge() {
  if (tx.charging || tx.ready || tx.transmitting) return
  
  tx.charging = true
  addLog('LOG_CHARGE_START')
  
  const interval = setInterval(() => {
    tx.chargeProgress += 2
    if (tx.chargeProgress >= 100) {
      tx.chargeProgress = 100
      tx.charging = false
      tx.ready = true
      clearInterval(interval)
      addLog('LOG_CHARGE_COMPLETE')
    }
  }, 50)
}

function broadcast() {
  if (!tx.ready) {
    addLog('LOG_ERR_CHARGE')
    return
  }
  if (tx.authCode !== '1971') {
    addLog('LOG_ERR_AUTH')
    return
  }
  
  tx.transmitting = true
  tx.ready = false
  tx.chargeProgress = 0
  
  addLog('LOG_TX_START', { freq: tx.frequency, power: outputPower.value.toFixed(1) })
  
  if (tx.sunAmplified && isAligned.value) {
    addLog('LOG_SOLAR_WARN')
  }

  // Simulate API Call
  setTimeout(() => {
    tx.transmitting = false
    tx.cooling = true
    addLog('LOG_TX_COMPLETE')
    setTimeout(() => {
      tx.cooling = false
      addLog('LOG_STANDBY')
    }, 3000)
    
    // Check for "Do Not Answer" event
    checkForResponse()
  }, 2000)
}

function checkForResponse() {
  // Easter egg probability
  if (Math.random() > 0.5) {
    setTimeout(() => {
      triggerIncomingSignal()
    }, 5000)
  }
}

function triggerIncomingSignal() {
  rx.listening = false // Interrupted
  addLog('LOG_ANOMALY')
  rx.decoding = true
  
  let p = 0
  const interval = setInterval(() => {
    p += 1
    rx.decodeProgress = p
    if (p >= 100) {
      clearInterval(interval)
      rx.decoding = false
      rx.detectedMessage = "MSG_DO_NOT_ANSWER" // Key
      addLog('LOG_DECODED')
    }
  }, 100)
}

function resetSystem() {
  rx.detectedMessage = null
  rx.decodeProgress = 0
  rx.listening = true
  addLog('LOG_BUFFER_CLEARED')
}

onUnmounted(() => {
  clearInterval(timeInterval)
})

</script>

<template>
  <div class="sector-r-console">
    <!-- Overlay Effects -->
    <div class="crt-lines"></div>
    <div class="vignette"></div>

    <!-- Top Bar -->
    <header class="top-bar">
      <div class="brand">
        <span class="logo-icon">📡</span>
        <span class="logo-text">{{ t('TITLE') }}</span>
      </div>
      <div class="sys-controls">
        <button class="lang-btn" @click="viewMode = viewMode === 'CONSOLE' ? 'ETO' : 'CONSOLE'" :class="{ active: viewMode === 'ETO' }">
          {{ viewMode === 'CONSOLE' ? 'ETO_NET' : 'RED_COAST' }}
        </button>
        <button class="lang-btn" @click="toggleLang">{{ lang }}</button>
        <div class="sys-info">
          <span>{{ t('STATUS') }}: {{ rx.detectedMessage ? t('ALERT') : tx.transmitting ? t('TX') : t('ONLINE') }}</span>
          <span>{{ systemTime }}</span>
        </div>
      </div>
    </header>

    <!-- ETO Assembly View -->
    <div v-if="viewMode === 'ETO'" class="eto-wrapper">
      <ETOAssembly />
    </div>

    <!-- Red Coast Console View -->
    <div v-else class="console-grid">
      
      <!-- Left: Antenna Control -->
      <div class="panel antenna-panel">
        <h3 class="panel-title">{{ t('ANTENNA_ALIGNMENT') }}</h3>
        
        <div class="radar-scope">
          <div class="scope-grid"></div>
          <div class="sun-target" 
               :style="{ 
                 left: `${(antenna.targetAzimuth / 360) * 100}%`, 
                 top: `${100 - (antenna.targetElevation / 90) * 100}%` 
               }">
             ☀
          </div>
          <div class="current-aim"
               :style="{ 
                 left: `${(antenna.azimuth / 360) * 100}%`, 
                 top: `${100 - (antenna.elevation / 90) * 100}%` 
               }">
             ✛
          </div>
        </div>

        <div class="controls">
          <div class="control-group">
            <label>{{ t('AZIMUTH') }} ({{ antenna.azimuth.toFixed(1) }}°)</label>
            <NSlider v-model:value="antenna.azimuth" :min="0" :max="360" :step="0.1" :disabled="antenna.tracking" />
          </div>
          <div class="control-group">
            <label>{{ t('ELEVATION') }} ({{ antenna.elevation.toFixed(1) }}°)</label>
            <NSlider v-model:value="antenna.elevation" :min="0" :max="90" :step="0.1" :disabled="antenna.tracking" />
          </div>
          
          <div class="alignment-meter">
             <label>{{ t('SIGNAL_GAIN') }}</label>
             <NProgress 
               type="line" 
               :percentage="alignmentQuality" 
               :color="isAligned ? '#00ff41' : '#ff0000'"
               :show-indicator="false"
               processing
             />
          </div>

          <button class="retro-btn" :class="{ active: antenna.tracking }" @click="toggleTracking">
            {{ antenna.tracking ? t('AUTO_TRACKING') : t('MANUAL_MODE') }}
          </button>
        </div>
      </div>

      <!-- Center: Monitor -->
      <div class="panel monitor-panel">
        <div class="screen-content">
          <div v-if="rx.detectedMessage" class="alert-message">
            <h1>{{ t('WARNING') }}</h1>
            <p class="blink">{{ t(rx.detectedMessage) }}</p>
            <button class="retro-btn small" @click="resetSystem">{{ t('ACKNOWLEDGE') }}</button>
          </div>
          <div v-else class="waterfall-display">
            <!-- Simulated Waveform -->
            <div class="waveform" :class="{ active: tx.transmitting }"></div>
            <div class="logs">
              <div v-for="(log, i) in terminalLogs" :key="i" class="log-line">{{ log }}</div>
            </div>
          </div>
        </div>
        <div class="scan-line"></div>
      </div>

      <!-- Right: Transmission -->
      <div class="panel tx-panel">
        <h3 class="panel-title">{{ t('TRANSMISSION_CONTROL') }}</h3>
        
        <div class="control-group">
          <label>{{ t('FREQUENCY') }} (MHz)</label>
          <div class="digital-readout">{{ tx.frequency }}</div>
        </div>

        <div class="control-group">
          <label>{{ t('OUTPUT_POWER') }} (MW)</label>
          <div class="digital-readout danger">{{ outputPower.toFixed(2) }}</div>
        </div>

        <div class="switch-row">
          <label>{{ t('SOLAR_AMP') }}</label>
          <NSwitch v-model:value="tx.sunAmplified" />
        </div>

        <div class="charge-section">
          <div class="charge-bar">
            <div class="fill" :style="{ width: `${tx.chargeProgress}%` }"></div>
          </div>
          <button class="retro-btn" @click="startCharge" :disabled="tx.charging || tx.ready">
            {{ tx.charging ? t('CHARGING') : t('CHARGE_CAPACITORS') }}
          </button>
        </div>

        <div class="auth-section">
          <input v-model="tx.authCode" :placeholder="t('AUTH_CODE')" class="auth-input" maxlength="4" />
        </div>

        <button 
          class="big-red-button" 
          :class="{ disabled: !tx.ready || tx.transmitting }"
          @click="broadcast"
        >
          <div class="cover"></div>
          <span>{{ t('BROADCAST') }}</span>
        </button>
      </div>

    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

.sector-r-console {
  min-height: 0;
  background-color: #050505;
  color: #0f0;
  font-family: 'Share Tech Mono', monospace;
  padding: 1rem;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* CRT Effects Enhanced */
.crt-lines {
  position: fixed;
  inset: 0;
  background: linear-gradient(
    rgba(18, 16, 16, 0) 50%,
    rgba(0, 0, 0, 0.25) 50%
  ),
  linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
  background-size: 100% 4px, 3px 100%;
  pointer-events: none;
  z-index: 100;
  opacity: 0.6;
  animation: crt-flicker 0.15s infinite;
}

.crt-lines::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 5px;
  background-color: rgba(0, 255, 0, 0.2);
  box-shadow: 0 0 10px rgba(0, 255, 0, 0.4);
  animation: scanline 6s linear infinite;
  opacity: 0.3;
}

.vignette {
  position: fixed;
  inset: 0;
  background: radial-gradient(circle, transparent 60%, rgba(0, 20, 0, 0.4) 90%, rgba(0,0,0,0.9) 100%);
  pointer-events: none;
  z-index: 101;
  box-shadow: inset 0 0 50px rgba(0,0,0,0.7);
}

@keyframes scanline {
  0% { top: -5%; }
  100% { top: 105%; }
}

@keyframes crt-flicker {
  0% { opacity: 0.58; }
  5% { opacity: 0.62; }
  10% { opacity: 0.59; }
  15% { opacity: 0.63; }
  20% { opacity: 0.58; }
  25% { opacity: 0.6; }
  30% { opacity: 0.61; }
  35% { opacity: 0.59; }
  40% { opacity: 0.62; }
  45% { opacity: 0.58; }
  50% { opacity: 0.6; }
  55% { opacity: 0.61; }
  60% { opacity: 0.59; }
  65% { opacity: 0.62; }
  70% { opacity: 0.6; }
  75% { opacity: 0.58; }
  80% { opacity: 0.61; }
  85% { opacity: 0.59; }
  90% { opacity: 0.62; }
  95% { opacity: 0.6; }
  100% { opacity: 0.58; }
}

.sector-r-console {
  min-height: 0;
  background-color: #050505;
  color: #0f0;
  font-family: 'Share Tech Mono', monospace;
  padding: 1rem;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  text-shadow: 0 0 2px #0f0, 0 0 5px rgba(0, 255, 0, 0.5); /* Glow */
}

.sys-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.lang-btn {
  background: #003300;
  border: 1px solid #0f0;
  color: #0f0;
  font-family: inherit;
  cursor: pointer;
  padding: 0 0.5rem;
  transition: all 0.2s;
}

.lang-btn:hover, .lang-btn.active {
  background: #0f0;
  color: #000;
}


.sys-info {
  display: flex;
  gap: 1rem;
}

.eto-wrapper {
  flex: 1;
  min-height: 0;
  border: 1px solid #333;
}

.console-grid {
  flex: 1;
  display: grid;
  grid-template-columns: 300px 1fr 300px;
  gap: 1rem;
  min-height: 0;
}

.panel {
  border: 1px solid #005500;
  background: rgba(0, 20, 0, 0.3);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.panel-title {
  margin: 0;
  border-bottom: 1px dashed #0f0;
  padding-bottom: 0.5rem;
  font-size: 1.2rem;
  color: #0f0;
}

/* Antenna Panel */
.radar-scope {
  width: 100%;
  aspect-ratio: 1;
  background: #001100;
  border: 1px solid #0f0;
  position: relative;
  border-radius: 50%;
  overflow: hidden;
}

.scope-grid {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(#003300 1px, transparent 1px),
    linear-gradient(90deg, #003300 1px, transparent 1px);
  background-size: 20px 20px;
  border-radius: 50%;
}

.sun-target {
  position: absolute;
  color: #ff0;
  font-size: 1.5rem;
  transform: translate(-50%, -50%);
  text-shadow: 0 0 10px #ff0;
}

.current-aim {
  position: absolute;
  color: #0f0;
  font-size: 1.5rem;
  transform: translate(-50%, -50%);
  transition: all 0.1s;
}

/* Monitor Panel */
.monitor-panel {
  position: relative;
  background: #000;
  border: 2px solid #0f0;
  box-shadow: 0 0 15px rgba(0, 255, 0, 0.2);
}

.screen-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 1rem;
}

.logs {
  font-size: 0.9rem;
  line-height: 1.4;
  opacity: 0.8;
}

.alert-message {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(50, 0, 0, 0.9);
  color: #f00;
  z-index: 10;
}

.blink {
  animation: blink 0.5s infinite;
  font-size: 1.5rem;
  font-weight: bold;
}

/* Tx Panel */
.digital-readout {
  background: #000;
  border: 1px inset #0f0;
  padding: 0.5rem;
  font-size: 1.2rem;
  text-align: right;
  color: #0f0;
}

.digital-readout.danger {
  color: #ff9900;
  border-color: #ff9900;
}

.charge-bar {
  height: 20px;
  background: #111;
  border: 1px solid #555;
  margin-bottom: 0.5rem;
}

.fill {
  height: 100%;
  background: repeating-linear-gradient(
    45deg,
    #ff9900,
    #ff9900 10px,
    #cc7a00 10px,
    #cc7a00 20px
  );
  transition: width 0.1s linear;
}

.auth-input {
  background: #000;
  border: 1px solid #0f0;
  color: #0f0;
  padding: 0.5rem;
  width: 100%;
  font-family: inherit;
  font-size: 1.2rem;
  text-align: center;
  letter-spacing: 5px;
}

.big-red-button {
  height: 80px;
  background: #a00;
  border: none;
  color: white;
  font-weight: bold;
  font-size: 1.2rem;
  cursor: pointer;
  position: relative;
  box-shadow: 0 5px #500;
  margin-top: 1rem;
}

.big-red-button:active {
  transform: translateY(2px);
  box-shadow: 0 3px #500;
}

.big-red-button.disabled {
  background: #333;
  color: #555;
  box-shadow: none;
  cursor: not-allowed;
}

.retro-btn {
  background: #003300;
  border: 1px solid #0f0;
  color: #0f0;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s;
}

.retro-btn:hover {
  background: #0f0;
  color: #000;
}

.retro-btn.active {
  background: #0f0;
  color: #000;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* Custom Scrollbar */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #000; }
::-webkit-scrollbar-thumb { background: #005500; }

/* Naive UI Overrides */
:deep(.n-slider .n-slider-rail) {
  background-color: #003300;
}
:deep(.n-slider .n-slider-rail .n-slider-rail__fill) {
  background-color: #0f0;
}
:deep(.n-slider .n-slider-handle) {
  background-color: #000;
  border: 2px solid #0f0;
  box-shadow: 0 0 5px #0f0;
}
:deep(.n-switch.n-switch--active .n-switch__rail) {
  background-color: #0f0;
}
:deep(.n-switch__rail) {
  background-color: #003300;
  border: 1px solid #0f0;
}
:deep(.n-progress .n-progress-graph-line-rail) {
  background-color: #003300;
}
:deep(.n-progress .n-progress-graph-line-fill) {
  background-color: #0f0;
  box-shadow: 0 0 5px #0f0;
}

</style>
