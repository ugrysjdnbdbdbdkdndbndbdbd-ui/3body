<script setup lang="ts">
import SophonChat from '@/components/SophonChat.vue'
</script>

<template>
  <div class="sophon-layout">
    <header class="border-b border-primary/30 px-6 py-4">
      <h1 class="font-mono text-primary">智子终端 · Sophon Interface</h1>
    </header>
    <main class="flex-1 overflow-hidden">
      <SophonChat />
    </main>
  </div>
</template>

<style scoped>
.sophon-layout {
  @apply flex min-h-screen flex-col bg-space;
}
</style>
