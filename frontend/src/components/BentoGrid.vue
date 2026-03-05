<script setup lang="ts">
/**
 * 便当盒网格 — 12 列，高信息密度首页。
 */
</script>

<template>
  <div class="bento-grid">
    <slot />
  </div>
</template>

<style scoped>
.bento-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-auto-rows: minmax(180px, auto); /* 自适应行高，最小180px */
  gap: 1.5rem;
  width: 100%;
}
</style>
