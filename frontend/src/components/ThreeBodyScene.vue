<script setup lang="ts">
import { shallowRef, ref, watchEffect } from 'vue'
import { useLoop } from '@tresjs/core'
import { Stars, OrbitControls, Precipitation } from '@tresjs/cientos'
import { Vector3, Color } from 'three'

// 物理参数
const G = 1.5 // 略微增加引力
const SOFTENING = 5.0
const BOUNDS = 50
const CENTER_PULL = 0.008
const TIME_STEP = 0.016

// 恒星数据结构
interface Body {
  id: number
  position: Vector3
  velocity: Vector3
  mass: number
  radius: number
  color: string
  emissive: string
}

// 与 3BODY X V2.1 截图一致：主星亮橙、左青、右白，高饱和发光
const bodies = ref<Body[]>([
  {
    id: 1,
    position: new Vector3(12, 0, 0),
    velocity: new Vector3(0, 0.5, 0.2),
    mass: 1200,
    radius: 3.5,
    color: '#ff6600', // 主星：截图同款亮橙
    emissive: '#ff5500'
  },
  {
    id: 2,
    position: new Vector3(-10, 8, 0),
    velocity: new Vector3(-0.3, -0.4, -0.1),
    mass: 900,
    radius: 2.8,
    color: '#00e5e5', // 青/teal 伴星，与 logo 左侧一致
    emissive: '#00cccc'
  },
  {
    id: 3,
    position: new Vector3(-5, -12, 6),
    velocity: new Vector3(0.2, 0.2, 0.1),
    mass: 700,
    radius: 2.2,
    color: '#ffffff', // 白色伴星，与 logo 右侧一致
    emissive: '#e0e0e0'
  }
])

// 使用 Map 存储 Mesh 引用，确保稳定性
const meshRefs = new Map<number, any>()

const setMeshRef = (el: any, id: number) => {
  if (el) {
    meshRefs.set(id, el)
  }
}

// 物理引擎循环
const { onBeforeRender } = useLoop()

onBeforeRender(() => {
  // 1. 计算受力
  const forces: Vector3[] = bodies.value.map(() => new Vector3(0, 0, 0))

  for (let i = 0; i < bodies.value.length; i++) {
    const bodyA = bodies.value[i]
    
    for (let j = 0; j < bodies.value.length; j++) {
      if (i === j) continue
      const bodyB = bodies.value[j]
      
      const diff = new Vector3().subVectors(bodyB.position, bodyA.position)
      const distSq = diff.lengthSq()
      // 防止除零
      if (distSq < 0.1) continue

      const forceMag = (G * bodyA.mass * bodyB.mass) / (distSq + SOFTENING)
      const forceVec = diff.normalize().multiplyScalar(forceMag)
      
      forces[i].add(forceVec)
    }

    // 边界约束
    const distFromCenter = bodyA.position.length()
    if (distFromCenter > BOUNDS) {
      const pullDir = bodyA.position.clone().negate().normalize()
      const pullMag = (distFromCenter - BOUNDS) * bodyA.mass * CENTER_PULL
      forces[i].add(pullDir.multiplyScalar(pullMag))
    }
  }

  // 2. 更新位置
  for (let i = 0; i < bodies.value.length; i++) {
    const body = bodies.value[i]
    const acceleration = forces[i].divideScalar(body.mass)
    
    body.velocity.add(acceleration.multiplyScalar(TIME_STEP))
    body.position.add(body.velocity.clone().multiplyScalar(TIME_STEP))

    // 同步到 Mesh
    const mesh = meshRefs.get(body.id)
    if (mesh) {
      mesh.position.copy(body.position)
    }
  }
})
</script>

<template>
  <TresPerspectiveCamera :position="[0, 0, 80]" :fov="45" :look-at="[0, 0, 0]" />
  <OrbitControls :enable-zoom="false" :enable-pan="false" :auto-rotate="true" :auto-rotate-speed="0.3" />
  
  <TresAmbientLight :intensity="0.1" />
  
  <!-- 星空背景 -->
  <Stars :radius="150" :depth="50" :count="3000" :size="0.6" :size-attenuation="true" />
  
  <!-- 每一个恒星 -->
  <TresMesh
    v-for="body in bodies"
    :key="body.id"
    :ref="(el) => setMeshRef(el, body.id)"
    :position="[body.position.x, body.position.y, body.position.z]"
  >
    <TresSphereGeometry :args="[body.radius, 32, 32]" />
    <TresMeshStandardMaterial 
      :color="body.color"
      :emissive="body.emissive"
      :emissive-intensity="3"
      :roughness="0.1"
      :metalness="0.5"
    />
    <!-- 恒星自发光点光源 -->
    <TresPointLight 
      :color="body.color" 
      :intensity="2.5" 
      :distance="60" 
      :decay="1.5" 
    />
  </TresMesh>
</template>
