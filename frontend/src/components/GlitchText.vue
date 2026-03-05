<script setup lang="ts">
/**
 * GlitchText.vue - 赛博朋克解密文字
 * 效果：随机字符滚动 -> 最终文字
 */
import { ref, watch, onMounted } from 'vue'

const props = defineProps<{
  text: string
  active?: boolean
  speed?: number // ms per frame
  scramble?: number // duration of scramble
}>()

const displayText = ref('')
const chars = '!@#$%^&*()_+-=[]{}|;:,.<>/?0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

function decrypt() {
  const target = props.text
  const length = target.length
  let frame = 0
  const duration = props.scramble || 20 // frames
  
  const interval = setInterval(() => {
    let result = ''
    for (let i = 0; i < length; i++) {
      if (i < frame / 2) {
        result += target[i]
      } else {
        result += chars[Math.floor(Math.random() * chars.length)]
      }
    }
    displayText.value = result
    
    frame++
    if (frame > length * 2 + duration) {
      clearInterval(interval)
      displayText.value = target
    }
  }, props.speed || 30)
}

watch(() => props.text, () => {
  if (props.active !== false) decrypt()
})

onMounted(() => {
  if (props.active !== false) decrypt()
})
</script>

<template>
  <span class="glitch-text" :data-text="text">{{ displayText }}</span>
</template>

<style scoped>
.glitch-text {
  font-family: var(--font-tech);
  display: inline-block;
  position: relative;
}
</style>
