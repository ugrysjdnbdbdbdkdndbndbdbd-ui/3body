<script setup lang="ts">
/**
 * 会呼吸的虚空 — TresJS 全屏星场，透明叠在 CSS 渐变层上。
 */
import { TresCanvas } from '@tresjs/core'
import StarfieldPoints from './StarfieldPoints.vue'
</script>

<template>
  <div class="void-canvas-wrap">
    <TresCanvas
      window-size
      :clear-alpha="0"
      :alpha="true"
      class="void-canvas"
    >
      <TresPerspectiveCamera :position="[0, 0, 10]" />
      <StarfieldPoints />
    </TresCanvas>
  </div>
</template>

<style scoped>
.void-canvas-wrap {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: -2;
}

.void-canvas {
  display: block;
  width: 100%;
  height: 100%;
}
</style>
