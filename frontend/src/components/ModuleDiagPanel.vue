<script setup lang="ts">
defineProps<{
  moduleKey: string
  status: 'IDLE' | 'RUNNING' | 'SUCCESS' | 'ERROR'
  durationMs: number
  updatedAt: string
  error: string
  history?: Array<{
    at: string
    status: string
    durationMs: number
    error?: string
  }>
}>()
</script>

<template>
  <div class="diag-wrap">
    <div class="diag-line">
      TASK={{ moduleKey }} | {{ status }} | {{ durationMs }}ms | {{ updatedAt }}
      <span v-if="error"> | {{ error }}</span>
    </div>
    <div v-if="history && history.length" class="diag-history">
      <div class="diag-history-title">Recent Calls</div>
      <div v-for="(h, idx) in history" :key="idx" class="diag-history-item">
        <span>[{{ h.at }}]</span>
        <span>{{ h.status }}</span>
        <span>{{ h.durationMs }}ms</span>
        <span v-if="h.error">{{ h.error }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.diag-wrap {
  display: grid;
  gap: 0.3rem;
}

.diag-line {
  font-family: monospace;
  font-size: 12px;
  color: #8ba5a5;
  border: 1px dashed #294040;
  padding: 0.3rem 0.45rem;
}

.diag-history {
  border: 1px solid #202f2f;
  padding: 0.35rem 0.5rem;
  font-family: monospace;
  font-size: 11px;
  color: #86a1a1;
}

.diag-history-title {
  color: #9bc0c0;
  margin-bottom: 0.2rem;
}

.diag-history-item {
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px dotted #1f2a2a;
  padding: 0.1rem 0;
}
</style>
