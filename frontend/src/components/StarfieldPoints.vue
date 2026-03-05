<script setup lang="ts">
/**
 * 星场粒子 — 用于 TresCanvas 内，缓慢漂浮 + 极弱视差。
 */
import { ref, onUnmounted } from 'vue'
import * as THREE from 'three'
import { useLoop } from '@tresjs/core'

const count = 3200
const positions = new Float32Array(count * 3)
for (let i = 0; i < count; i++) {
  positions[i * 3] = (Math.random() - 0.5) * 24
  positions[i * 3 + 1] = (Math.random() - 0.5) * 24
  positions[i * 3 + 2] = (Math.random() - 0.5) * 24
}

const geometry = new THREE.BufferGeometry()
geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
const material = new THREE.PointsMaterial({
  size: 0.035,
  color: 0xb8e6f5,
  transparent: true,
  opacity: 0.82,
  sizeAttenuation: true,
})
const points = new THREE.Points(geometry, material)
const pointsRef = ref<THREE.Points>(points)

const start = Date.now() * 0.001
const { onBeforeRender } = useLoop()
const unsub = onBeforeRender(() => {
  const t = Date.now() * 0.001 - start
  const pos = points.geometry.attributes.position as THREE.BufferAttribute
  const arr = pos.array as Float32Array
  for (let i = 0; i < pos.count; i++) {
    arr[i * 3] = positions[i * 3] + Math.sin(t * 0.15 + i * 0.008) * 0.12
    arr[i * 3 + 1] = positions[i * 3 + 1] + Math.cos(t * 0.12 + i * 0.006) * 0.12
  }
  pos.needsUpdate = true
})

onUnmounted(() => {
  unsub.off()
  geometry.dispose()
  material.dispose()
})
</script>

<template>
  <primitive v-if="pointsRef" :object="pointsRef" />
</template>
