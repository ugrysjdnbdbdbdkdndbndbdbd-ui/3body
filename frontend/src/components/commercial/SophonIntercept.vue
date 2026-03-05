<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import { ref, computed } from 'vue'
import { NModal, NButton, NCard } from 'naive-ui'
import MembershipPlan from './MembershipPlan.vue'
import { soundManager } from '@/utils/sound'

const userStore = useUserStore()
const showPlans = ref(false)

const handleClose = () => {
  userStore.isIntercepted = false
  showPlans.value = false
}

const unlock = () => {
  soundManager.playClick()
  showPlans.value = true
}

const quotes = [
  "主不在乎。",
  "你们是虫子。",
  "物理学不存在了。",
  "毁灭你，与你何干？"
]
const randomQuote = computed(() => quotes[Math.floor(Math.random() * quotes.length)])
</script>

<template>
  <NModal v-model:show="userStore.isIntercepted" :mask-closable="true" @after-leave="showPlans = false">
    <div class="sophon-intercept">
      <div v-if="!showPlans" class="intercept-content">
        <div class="eye-icon">👁️</div>
        <h2 class="title">智子封锁 (SOPHON BLOCKADE)</h2>
        <p class="reason">检测到越权操作：{{ userStore.interceptReason }}</p>
        <p class="quote">"{{ randomQuote }}"</p>
        
        <div class="actions">
          <NButton type="primary" color="#ff0000" ghost @click="handleClose">
            退缩 (RETREAT)
          </NButton>
          <NButton type="primary" color="#d4af37" class="unlock-btn" @click="unlock">
            打破封锁 (BREAK BLOCKADE)
          </NButton>
        </div>
      </div>

      <div v-else class="plan-wrapper">
        <MembershipPlan @close="handleClose" />
      </div>
    </div>
  </NModal>
</template>

<style scoped>
.sophon-intercept {
  pointer-events: auto;
}

.intercept-content {
  background: rgba(0, 0, 0, 0.9);
  border: 1px solid #ff0000;
  padding: 3rem;
  text-align: center;
  width: 400px;
  box-shadow: 0 0 50px rgba(255, 0, 0, 0.2);
  font-family: 'Share Tech Mono', monospace;
  animation: glitch 0.3s cubic-bezier(.25, .46, .45, .94) both infinite;
}

.plan-wrapper {
  width: 900px;
  max-width: 95vw;
}

.eye-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  animation: pulse 2s infinite;
}

.title {
  color: #ff0000;
  font-size: 1.5rem;
  margin-bottom: 1rem;
  letter-spacing: 2px;
}

.reason {
  color: #fff;
  margin-bottom: 2rem;
  font-size: 1rem;
}

.quote {
  color: #666;
  font-style: italic;
  margin-bottom: 3rem;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.unlock-btn {
  font-weight: bold;
  animation: shimmer 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.8; }
  100% { transform: scale(1); opacity: 1; }
}

@keyframes glitch {
  0% { transform: translate(0) }
  20% { transform: translate(-2px, 2px) }
  40% { transform: translate(-2px, -2px) }
  60% { transform: translate(2px, 2px) }
  80% { transform: translate(2px, -2px) }
  100% { transform: translate(0) }
}
</style>
