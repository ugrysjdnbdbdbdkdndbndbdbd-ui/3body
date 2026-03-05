<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiUrl } from '@/constants'

const docs = ref<any[]>([])

onMounted(async () => {
  try {
    const res = await fetch(apiUrl('/api/chronicle/archives'))
    if (res.ok) docs.value = await res.json()
  } catch {}
})
</script>

<template>
  <div class="archive-list">
    <div v-for="doc in docs" :key="doc.id" class="doc-file">
      <div class="doc-header">
        <span class="classification" :class="doc.classification">{{ doc.classification }}</span>
        <span class="doc-date">{{ new Date(doc.created_at).toLocaleDateString() }}</span>
      </div>
      <h3 class="doc-title">{{ doc.title }}</h3>
      <div class="doc-content">{{ doc.content_markdown }}</div>
      <div class="stamp">TOP SECRET</div>
    </div>
  </div>
</template>

<style scoped>
.archive-list {
  display: grid;
  gap: 2rem;
  padding: 1rem;
}
.doc-file {
  background: #fdf6e3;
  color: #333;
  padding: 2rem;
  font-family: 'Courier New', monospace;
  position: relative;
  box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
  transform: rotate(-1deg);
  transition: transform 0.3s;
}
.doc-file:hover {
  transform: rotate(0) scale(1.02);
  z-index: 10;
}
.doc-header {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid #999;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
}
.classification {
  font-weight: bold;
}
.classification.TOP_SECRET { color: #d32f2f; }
.doc-title {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  text-transform: uppercase;
}
.doc-content {
  white-space: pre-wrap;
  line-height: 1.6;
}
.stamp {
  position: absolute;
  top: 1rem;
  right: 1rem;
  border: 3px solid rgba(211, 47, 47, 0.3);
  color: rgba(211, 47, 47, 0.3);
  padding: 0.5rem;
  font-weight: bold;
  transform: rotate(15deg);
  font-size: 1.2rem;
}
</style>
