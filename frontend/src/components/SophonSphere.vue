<script setup lang="ts">
/**
 * 智子粒子球 — 8000+ 粒子，鼠标引力偏移，三态：idle 缓慢旋转 / sending 向心聚集 / response 向外扩散。
 */
import { ref, watch, onUnmounted } from 'vue'
import * as THREE from 'three'
import { useLoop } from '@tresjs/core'

export type SophonState = 'idle' | 'sending' | 'response'

const props = withDefaults(
  defineProps<{
    state?: SophonState
    mouseX?: number
    mouseY?: number
  }>(),
  { state: 'idle', mouseX: 0, mouseY: 0 }
)

const pointsRef = ref<THREE.Points | null>(null)
const count = 8000
const radius = 1.4
const basePositions = new Float32Array(count * 3)
for (let i = 0; i < count; i++) {
  const u = Math.random()
  const v = Math.random()
  const theta = 2 * Math.PI * u
  const phi = Math.acos(2 * v - 1)
  basePositions[i * 3] = radius * Math.sin(phi) * Math.cos(theta)
  basePositions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta)
  basePositions[i * 3 + 2] = radius * Math.cos(phi)
}

const geometry = new THREE.BufferGeometry()
geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(basePositions), 3))
const material = new THREE.PointsMaterial({
  size: 0.018,
  color: 0x7dd3fc,
  transparent: true,
  opacity: 0.85,
  sizeAttenuation: true,
})
const points = new THREE.Points(geometry, material)
pointsRef.value = points

const phase = ref(0)
const startTime = Date.now() * 0.001

watch(
  () => props.state,
  () => {
    phase.value = 0
  }
)

const { onBeforeRender } = useLoop()
const unsub = onBeforeRender(() => {
  const t = Date.now() * 0.001 - startTime
  const pos = geometry.attributes.position as THREE.BufferAttribute
  const arr = pos.array as Float32Array
  const mx = props.mouseX * 0.15
  const my = props.mouseY * 0.15

  if (props.state === 'sending') {
    phase.value = Math.min(1, phase.value + 0.012)
    const p = phase.value
    for (let i = 0; i < pos.count; i++) {
      const bx = basePositions[i * 3]
      const by = basePositions[i * 3 + 1]
      const bz = basePositions[i * 3 + 2]
      arr[i * 3] = bx * (1 - p)
      arr[i * 3 + 1] = by * (1 - p)
      arr[i * 3 + 2] = bz * (1 - p)
    }
  } else if (props.state === 'response') {
    phase.value = Math.min(1, phase.value + 0.02)
    const p = phase.value
    for (let i = 0; i < pos.count; i++) {
      arr[i * 3] = basePositions[i * 3] * p
      arr[i * 3 + 1] = basePositions[i * 3 + 1] * p
      arr[i * 3 + 2] = basePositions[i * 3 + 2] * p
    }
  } else {
    for (let i = 0; i < pos.count; i++) {
      const nx = basePositions[i * 3]
      const ny = basePositions[i * 3 + 1]
      const nz = basePositions[i * 3 + 2]
      const noise = 0.04 * Math.sin(t * 0.8 + i * 0.01)
      const rx = nx + noise + mx
      const ry = ny + 0.04 * Math.cos(t * 0.7 + i * 0.008) + my
      const rz = nz + 0.03 * Math.sin(t * 0.6 + i * 0.012)
      const scale = 0.98 + 0.04 * Math.sin(t * 0.3)
      arr[i * 3] = rx * scale
      arr[i * 3 + 1] = ry * scale
      arr[i * 3 + 2] = rz * scale
    }
  }
  pos.needsUpdate = true
})

watch(
  () => props.state,
  (s) => {
    material.color.setHex(s === 'sending' ? 0xf472b6 : 0x7dd3fc)
  }
)

onUnmounted(() => {
  unsub.off()
  geometry.dispose()
  material.dispose()
})
</script>

<template>
  <primitive v-if="pointsRef" :object="pointsRef" />
</template>
