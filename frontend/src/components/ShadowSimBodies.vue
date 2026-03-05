<script setup lang="ts">
/**
 * 在 Three 渲染循环中每帧同步行星与太空城位置，解决 Vue 响应式未驱动 Tres 更新的问题。
 */
import { onMounted, onUnmounted } from 'vue'
import { useTresContext, useLoop } from '@tresjs/core'
import * as THREE from 'three'

const props = defineProps<{
  planets3d: { id: string; x: number; y: number; z: number; r3d: number; color: string }[]
  cities3d: { id: string; x: number; y: number; z: number; exposed: boolean }[]
}>()

const { scene } = useTresContext()
const { onBeforeRender } = useLoop()

const group = new THREE.Group()
const planetMeshes: THREE.Mesh[] = []
const cityMeshes: THREE.Mesh[] = []
let offBeforeRender: { off: () => void } | null = null

function syncPositions() {
  props.planets3d.forEach((p, i) => {
    if (planetMeshes[i]) {
      planetMeshes[i].position.set(p.x, p.y, p.z)
    }
  })
  props.cities3d.forEach((c, i) => {
    if (cityMeshes[i]) {
      cityMeshes[i].position.set(c.x, c.y, c.z)
      const mat = cityMeshes[i].material as THREE.MeshStandardMaterial
      if (mat) {
        mat.color.set(c.exposed ? '#ff3333' : '#00ff41')
        mat.emissive.set(c.exposed ? 0x440000 : 0x002200)
      }
    }
  })
}

onMounted(() => {
  const planetGeo = new THREE.SphereGeometry(1, 24, 24)
  const cityGeo = new THREE.SphereGeometry(0.8, 16, 16)

  props.planets3d.forEach((p, i) => {
    const mat = new THREE.MeshStandardMaterial({
      color: p.color,
      roughness: 0.7,
      metalness: 0.2
    })
    const mesh = new THREE.Mesh(planetGeo.clone(), mat)
    mesh.position.set(p.x, p.y, p.z)
    mesh.scale.setScalar(p.r3d)
    group.add(mesh)
    planetMeshes.push(mesh)
  })

  props.cities3d.forEach((c) => {
    const mat = new THREE.MeshStandardMaterial({
      color: c.exposed ? '#ff3333' : '#00ff41',
      emissive: c.exposed ? 0x440000 : 0x002200,
      emissiveIntensity: 0.3
    })
    const mesh = new THREE.Mesh(cityGeo.clone(), mat)
    mesh.position.set(c.x, c.y, c.z)
    group.add(mesh)
    cityMeshes.push(mesh)
  })

  scene.value.add(group)
  offBeforeRender = onBeforeRender(syncPositions)
})

onUnmounted(() => {
  offBeforeRender?.off()
  if (group.parent) group.parent.remove(group)
  planetMeshes.forEach((m) => {
    m.geometry.dispose()
    if (Array.isArray(m.material)) m.material.forEach((mat) => mat.dispose())
    else m.material.dispose()
  })
  cityMeshes.forEach((m) => {
    m.geometry.dispose()
    if (Array.isArray(m.material)) m.material.forEach((mat) => mat.dispose())
    else m.material.dispose()
  })
})
</script>

<template>
  <!-- 行星/城由 onMounted 加入 scene，onBeforeRender 每帧同步位置 -->
  <TresGroup />
</template>
