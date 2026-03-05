<script setup lang="ts">
/**
 * ThreeBodyBackground.vue (Container)
 * 仅负责创建 TresCanvas 上下文
 */
import { TresCanvas } from '@tresjs/core'
import ThreeBodyScene from './ThreeBodyScene.vue'
</script>

<template>
  <div class="tres-container">
    <TresCanvas clear-color="#020617" power-preference="high-performance">
      <ThreeBodyScene />
    </TresCanvas>
  </div>
</template>

<style scoped>
.tres-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}
</style>
