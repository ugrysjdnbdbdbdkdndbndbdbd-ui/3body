<script setup lang="ts">
/**
 * Glassmorphism 3.0 — 磨砂玻璃卡片：无实线边框、边缘光感、顶部内发光。
 */
const props = withDefaults(
  defineProps<{
    cols?: number
    rows?: number
  }>(),
  { cols: 1, rows: 1 }
)
</script>

<template>
  <div
    class="bento-item"
    :style="{
      gridColumn: `span ${props.cols}`,
      gridRow: `span ${props.rows}`,
    }"
  >
    <slot />
  </div>
</template>

<style scoped>
.bento-item {
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: transparent;
  border: none;
  border-radius: 0;
  overflow: visible;
  transition: none;
  box-shadow: none;
}

.bento-item:hover {
  background: transparent;
  box-shadow: none;
}
</style>
