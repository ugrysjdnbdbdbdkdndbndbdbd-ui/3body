<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NTag } from 'naive-ui'
import { apiUrl } from '@/constants'

const entries = ref<any[]>([])

onMounted(async () => {
  try {
    const res = await fetch(apiUrl('/api/chronicle/wiki'))
    if (res.ok) entries.value = await res.json()
  } catch {}
})
</script>

<template>
  <div class="wiki-grid">
    <div v-for="e in entries" :key="e.id" class="wiki-card" :class="e.visual_effect">
      <div class="wiki-header">
        <span class="wiki-term">{{ e.term }}</span>
        <NTag size="small" type="primary" ghost>{{ e.category }}</NTag>
      </div>
      <p class="wiki-summary">{{ e.summary }}</p>
      <div class="wiki-body">{{ e.content_markdown }}</div>
    </div>
  </div>
</template>

<style scoped>
.wiki-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
  padding: 1rem;
}
.wiki-card {
  background: rgba(0, 255, 255, 0.05);
  border: 1px solid rgba(0, 255, 255, 0.2);
  padding: 1.5rem;
  backdrop-filter: blur(10px);
  transition: all 0.3s;
}
.wiki-card:hover {
  border-color: #00ffff;
  box-shadow: 0 0 15px rgba(0, 255, 255, 0.2);
}
.wiki-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.wiki-term {
  font-size: 1.2rem;
  font-weight: bold;
  color: #00ffff;
}
.wiki-summary {
  font-size: 0.9rem;
  color: #aaa;
  margin-bottom: 1rem;
  font-style: italic;
}
.wiki-body {
  font-size: 0.85rem;
  line-height: 1.6;
}

/* Effects */
.wiki-card.flatten {
  transform: scaleY(0.8);
  filter: contrast(1.5);
}
.wiki-card.glitch {
  border-style: dashed;
  animation: glitch-border 2s infinite;
}
.wiki-card.4d_rotate:hover {
  transform: rotateY(180deg);
}

@keyframes glitch-border {
  0% { border-color: #00ffff; }
  50% { border-color: #ff00ff; }
  100% { border-color: #00ffff; }
}
</style>
