<script setup lang="ts">
/**
 * Sector PDC: Planetary Defense Council (行星防御理事会)
 * 核心玩法：资源分配模拟器 — 在危机纪元平衡三大计划与民生，生存至威慑或毁灭。
 */
import { ref, computed, onUnmounted } from 'vue'
import { NButton, NSlider, NProgress, useMessage, NModal, NCard, NTag } from 'naive-ui'

const message = useMessage()

// --- Game State ---
const year = ref(2007)
const panicLevel = ref(10)
const population = ref(80)
const techLevel = ref(0)

const allocations = ref({
  bunker: 20,
  blackDomain: 10,
  lightspeed: 10,
  welfare: 60
})

const progress = ref({
  bunker: 0,
  blackDomain: 0,
  lightspeed: 0
})

const isRunning = ref(false)
const gameSpeed = 500
let gameTimer: ReturnType<typeof setInterval> | undefined
const gameOver = ref(false)
const endReason = ref('')
const win = ref(false)

// --- 纪元 (Era) ---
const eraInfo = computed(() => {
  const y = year.value
  if (y < 2082) return { name: '危机纪元', en: 'Crisis Era', color: '#ffcc00' }
  if (y < 2100) return { name: '大低谷', en: 'Great Ravine', color: '#ff6666' }
  if (y < 2208) return { name: '后危机纪元', en: 'Post-Crisis', color: '#66ccff' }
  return { name: '威慑纪元', en: 'Deterrence Era', color: '#00ff88' }
})

// --- 理事会公告 (PDC Resolutions) ---
const PDC_BULLETINS = [
  { id: 117, title: '第 117 号决议', desc: '面壁计划授权。四名面壁者享有最高战略权限，无需向理事会解释。' },
  { id: 1, title: '全球战区体制', desc: '地球按防御区块划分，敌人无国界。常伟思将军宣布人类进入战时状态。' },
  { id: 2, title: 'PIA 战略情报局', desc: '行星防御理事会战略情报局成立，负责阶梯计划等绝密项目。' },
]

// --- Computed ---
const totalAllocated = computed(() => {
  return allocations.value.bunker + allocations.value.blackDomain + allocations.value.lightspeed + allocations.value.welfare
})

// --- Game Logic ---
function tick() {
  year.value++
  
  // 1. Progress Calculation
  progress.value.bunker += (allocations.value.bunker * 0.1) * (1 + techLevel.value * 0.01)
  progress.value.blackDomain += (allocations.value.blackDomain * 0.05) * (1 + techLevel.value * 0.01)
  
  // Lightspeed research requires tech threshold
  if (techLevel.value > 50) {
    progress.value.lightspeed += (allocations.value.lightspeed * 0.15)
  } else {
    // Basic research
    techLevel.value += (allocations.value.lightspeed * 0.2)
  }

  // 2. Social Impact
  if (allocations.value.welfare < 40) {
    panicLevel.value += 5
    population.value -= 0.5 // Starvation
  } else if (allocations.value.welfare > 60) {
    panicLevel.value = Math.max(0, panicLevel.value - 2)
  }

  // 重大事件节点
  if (year.value === 2050) {
    message.warning('大低谷前夕：资源向防御倾斜，民生凋敝。')
    panicLevel.value += 15
  }
  if (year.value === 2082) {
    message.warning('大低谷降临！人口锐减，文明几近崩溃。')
    population.value -= 25
    panicLevel.value += 25
  }
  if (year.value === 2100) {
    message.info('技术爆炸！基础科学突破，曲率理论萌芽。')
    techLevel.value += 25
  }
  if (year.value === 2208) {
    message.success('威慑纪元开启。罗辑建立黑暗森林威慑。')
  }

  checkGameOver()
}

function checkGameOver() {
  if (panicLevel.value >= 100) {
    endGame('全球暴乱，PDC 被推翻。人类文明在内乱中毁灭。', false)
  } else if (population.value <= 0) {
    endGame('人类灭绝。大低谷吞噬了所有人。', false)
  } else if (progress.value.lightspeed >= 100) {
    endGame('曲率引擎试飞成功。部分人类得以光速逃离太阳系。', true)
  } else if (progress.value.bunker >= 100) {
    endGame('掩体世界建成。人类迁居木星等巨行星背后，暂避光粒打击。', true)
  } else if (progress.value.blackDomain >= 100) {
    endGame('黑域生成。太阳系发布宇宙安全声明，再无人可打击。', true)
  }
}

function endGame(reason: string, isWin = false) {
  if (gameTimer) clearInterval(gameTimer)
  isRunning.value = false
  gameOver.value = true
  endReason.value = reason
  win.value = isWin
}

function toggleGame() {
  if (isRunning.value) {
    if (gameTimer) clearInterval(gameTimer)
    isRunning.value = false
  } else {
    if (totalAllocated.value !== 100) {
      message.error('预算分配总和必须为 100%')
      return
    }
    isRunning.value = true
    gameTimer = setInterval(tick, gameSpeed)
  }
}

function resetGame() {
  year.value = 2007
  panicLevel.value = 10
  population.value = 80
  techLevel.value = 0
  progress.value = { bunker: 0, blackDomain: 0, lightspeed: 0 }
  allocations.value = { bunker: 20, blackDomain: 10, lightspeed: 10, welfare: 60 }
  gameOver.value = false
  win.value = false
  isRunning.value = false
}

onUnmounted(() => {
  if (gameTimer) clearInterval(gameTimer)
})
</script>

<template>
  <div class="sector-pdc">
    <div class="pdc-container">
      <header class="pdc-header">
        <div class="pdc-title-block">
          <h1>行星防御理事会</h1>
          <p class="pdc-sub">PLANETARY DEFENSE COUNCIL · 面壁计划 · 全球战区协调</p>
        </div>
        <div class="pdc-meta">
          <NTag :color="{ color: eraInfo.color, textColor: '#000' }" round size="small">
            {{ eraInfo.name }}
          </NTag>
          <span class="year-display">第 {{ year }} 年</span>
        </div>
      </header>

      <section class="pdc-bulletins">
        <div class="bulletin-label">理事会公告</div>
        <div class="bulletin-list">
          <div v-for="b in PDC_BULLETINS" :key="b.id" class="bulletin-item">
            <span class="bulletin-title">{{ b.title }}</span>
            <span class="bulletin-desc">{{ b.desc }}</span>
          </div>
        </div>
        <div class="status-tags">
          <NTag type="info" size="small" round>智子监控中</NTag>
          <NTag size="small" round>全球战区</NTag>
        </div>
      </section>

      <div class="main-dashboard">
        <div class="control-panel panel">
          <h3>战略预算分配（合计：{{ totalAllocated }}%）</h3>

          <div class="slider-group">
            <div class="slider-label">
              <span>掩体计划</span>
              <span>{{ allocations.bunker }}%</span>
            </div>
            <p class="plan-desc">木星等巨行星背阳侧太空城，应对光粒打击后的氦闪与日冕。</p>
            <NSlider v-model:value="allocations.bunker" :step="5" />
          </div>

          <div class="slider-group">
            <div class="slider-label">
              <span>黑域计划</span>
              <span>{{ allocations.blackDomain }}%</span>
            </div>
            <p class="plan-desc">低光速区包裹太阳系，发布宇宙安全声明，使打击失去意义。</p>
            <NSlider v-model:value="allocations.blackDomain" :step="5" />
          </div>

          <div class="slider-group">
            <div class="slider-label">
              <span>曲率 / 光速飞船</span>
              <span>{{ allocations.lightspeed }}%</span>
            </div>
            <p class="plan-desc">曲率驱动研发。光速是底线；航迹可形成黑域。</p>
            <NSlider v-model:value="allocations.lightspeed" :step="5" />
          </div>

          <div class="slider-group welfare">
            <div class="slider-label">
              <span>民生保障</span>
              <span>{{ allocations.welfare }}%</span>
            </div>
            <p class="plan-desc">大低谷教训：民生不足将导致暴乱与文明崩溃。</p>
            <NSlider v-model:value="allocations.welfare" :step="5" status="success" />
          </div>

          <div class="actions">
            <NButton
              type="primary"
              size="large"
              block
              :disabled="totalAllocated !== 100"
              @click="toggleGame"
            >
              {{ isRunning ? '暂停模拟' : '执行计划' }}
            </NButton>
          </div>
        </div>

        <div class="monitor-panel panel">
          <h3>全球态势</h3>
          <div class="status-row">
            <div class="status-metric">
              <div class="label">恐慌指数</div>
              <NProgress type="dashboard" :percentage="panicLevel" :color="panicLevel > 80 ? '#e03030' : '#f0b020'" />
            </div>
            <div class="status-metric">
              <div class="label">人口（十亿）</div>
              <div class="value">{{ population.toFixed(1) }}</div>
            </div>
            <div class="status-metric">
              <div class="label">科技等级</div>
              <div class="value">{{ Math.round(techLevel) }}</div>
            </div>
          </div>

          <div class="progress-bars">
            <div class="prog-item">
              <span>掩体建设进度</span>
              <NProgress type="line" :percentage="Math.min(100, progress.bunker)" processing />
            </div>
            <div class="prog-item">
              <span>黑域理论进度</span>
              <NProgress type="line" :percentage="Math.min(100, progress.blackDomain)" processing color="#888" />
            </div>
            <div class="prog-item">
              <span>曲率引擎研发</span>
              <NProgress type="line" :percentage="Math.min(100, progress.lightspeed)" processing color="#00ccff" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <NModal v-model:show="gameOver">
      <NCard
        :title="win ? '战略目标达成' : '模拟结束'"
        :bordered="false"
        size="huge"
        class="end-card"
        :class="{ 'end-card--win': win }"
      >
        <div class="end-screen">
          <p class="end-reason">{{ endReason }}</p>
          <p v-if="win" class="end-era">结束于 {{ eraInfo.name }} · 第 {{ year }} 年</p>
          <div class="end-actions">
            <NButton type="primary" @click="resetGame">重新开始</NButton>
          </div>
        </div>
      </NCard>
    </NModal>
  </div>
</template>

<style scoped>
.sector-pdc {
  min-height: 0;
  background: linear-gradient(180deg, #060810 0%, #0b0e18 50%, #080a12 100%);
  color: #e8eaef;
  font-family: 'Rajdhani', 'Segoe UI', sans-serif;
  padding: 2rem;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.pdc-container {
  width: 100%;
  max-width: 1200px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.pdc-header {
  border-bottom: 1px solid rgba(0, 204, 255, 0.25);
  padding-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 1rem;
}

.pdc-title-block h1 {
  font-size: 2rem;
  margin: 0;
  letter-spacing: 0.12em;
  color: #00ccff;
  font-weight: 600;
}

.pdc-sub {
  margin: 0.35rem 0 0;
  font-size: 0.8rem;
  color: rgba(170, 200, 220, 0.85);
  letter-spacing: 0.06em;
}

.pdc-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.year-display {
  font-size: 1.25rem;
  font-weight: 700;
  color: #f0b020;
}

/* 理事会公告 */
.pdc-bulletins {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
  padding: 0.85rem 1rem;
  background: rgba(0, 40, 60, 0.35);
  border: 1px solid rgba(0, 180, 220, 0.15);
  border-radius: 6px;
}

.bulletin-label {
  font-size: 0.75rem;
  color: rgba(150, 180, 200, 0.9);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  flex-shrink: 0;
}

.bulletin-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0 1.5rem;
  flex: 1;
  min-width: 0;
}

.bulletin-item {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.35rem;
}

.bulletin-title {
  font-size: 0.85rem;
  color: #7dd3fc;
  font-weight: 600;
}

.bulletin-desc {
  font-size: 0.8rem;
  color: rgba(180, 200, 220, 0.75);
}

.status-tags {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.main-dashboard {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 2rem;
}

.panel {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 1.75rem;
  border-radius: 8px;
}

h3 {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 0.5rem;
  margin-bottom: 1.25rem;
  font-size: 1.05rem;
  color: #9ca3af;
}

.slider-group {
  margin-bottom: 1.75rem;
}

.slider-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.35rem;
  font-size: 0.9rem;
  color: #c8d0d8;
}

.plan-desc {
  font-size: 0.78rem;
  color: rgba(150, 170, 190, 0.8);
  margin: 0 0 0.5rem;
  line-height: 1.4;
}

.welfare .slider-label {
  color: #6ee7b7;
}

.status-row {
  display: flex;
  justify-content: space-around;
  margin-bottom: 2rem;
  text-align: center;
}

.status-metric .label {
  font-size: 0.78rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.status-metric .value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #e5e7eb;
}

.progress-bars {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.prog-item span {
  display: block;
  margin-bottom: 0.4rem;
  font-size: 0.85rem;
  color: #9ca3af;
}

/* 结束弹窗 */
.end-card {
  width: 100%;
  max-width: 520px;
}

.end-card--win {
  border: 1px solid rgba(0, 255, 136, 0.3);
}

.end-reason {
  font-size: 1.1rem;
  margin-bottom: 1rem;
  line-height: 1.6;
  color: #1f2937;
}

.end-era {
  font-size: 0.9rem;
  color: #6b7280;
  margin-bottom: 1.5rem;
}

.end-actions {
  text-align: right;
}

@media (max-width: 900px) {
  .main-dashboard {
    grid-template-columns: 1fr;
  }

  .pdc-bulletins {
    flex-direction: column;
    align-items: flex-start;
  }

  .bulletin-list {
    flex-direction: column;
  }
}
</style>
