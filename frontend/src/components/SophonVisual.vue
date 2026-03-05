<script setup lang="ts">
/**
 * 智子视觉容器 — 背景层粒子球，传递鼠标与状态。
 */
import { ref, watch } from 'vue'
import { TresCanvas } from '@tresjs/core'
import SophonSphere from './SophonSphere.vue'

type SophonState = 'idle' | 'sending' | 'response'

const props = withDefaults(
  defineProps<{ streaming?: boolean }>(),
  { streaming: false }
)

const mouseX = ref(0)
const mouseY = ref(0)
const state = ref<SophonState>('idle')

const containerRef = ref<HTMLElement | null>(null)

function onMove(e: MouseEvent) {
  if (!containerRef.value) return
  const rect = containerRef.value.getBoundingClientRect()
  mouseX.value = (e.clientX - rect.left) / rect.width * 2 - 1
  mouseY.value = -((e.clientY - rect.top) / rect.height * 2 - 1)
}

watch(
  () => props.streaming,
  (streaming) => {
    if (streaming) {
      state.value = 'sending'
    } else {
      if (state.value === 'sending') {
        state.value = 'response'
        setTimeout(() => {
          state.value = 'idle'
        }, 1400)
      } else {
        state.value = 'idle'
      }
    }
  },
  { immediate: true }
)
</script>

<template>
  <div
    ref="containerRef"
    class="sophon-visual"
    aria-hidden="true"
    @mousemove="onMove"
  >
    <TresCanvas class="sophon-canvas" :alpha="true" :clear-alpha="0">
      <TresPerspectiveCamera :position="[0, 0, 3.2]" />
      <SophonSphere
        :state="state"
        :mouse-x="mouseX"
        :mouse-y="mouseY"
      />
    </TresCanvas>
  </div>
</template>

<style scoped>
.sophon-visual {
  width: 100%;
  height: 100%;
  min-height: 200px;
}

.sophon-canvas {
  display: block;
  width: 100%;
  height: 100%;
}
</style>
