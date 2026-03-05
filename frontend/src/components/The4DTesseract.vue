<script setup lang="ts">
import { shallowRef } from 'vue'
import { useLoop } from '@tresjs/core'
import { Vector3, BufferGeometry, Float32BufferAttribute } from 'three'

// 4D Vertices of a Tesseract
const vertices4D: number[][] = []
for (let i = 0; i < 16; i++) {
  vertices4D.push([
    (i & 1) ? 1 : -1,
    (i & 2) ? 1 : -1,
    (i & 4) ? 1 : -1,
    (i & 8) ? 1 : -1
  ])
}

// Edges
const edges: number[][] = []
for (let i = 0; i < 16; i++) {
  for (let j = i + 1; j < 16; j++) {
    let diff = 0
    for (let k = 0; k < 4; k++) {
      if (vertices4D[i][k] !== vertices4D[j][k]) diff++
    }
    if (diff === 1) edges.push([i, j])
  }
}

// Rotation Matrices (4D)
function rotateZW(point: number[], theta: number) {
  const [x, y, z, w] = point
  return [
    x,
    y,
    z * Math.cos(theta) - w * Math.sin(theta),
    z * Math.sin(theta) + w * Math.cos(theta)
  ]
}

function rotateXW(point: number[], theta: number) {
  const [x, y, z, w] = point
  return [
    x * Math.cos(theta) - w * Math.sin(theta),
    y,
    z,
    x * Math.sin(theta) + w * Math.cos(theta)
  ]
}

// 4D to 3D Projection
function project(point: number[]) {
  const [x, y, z, w] = point
  const distance = 3
  const wInv = 1 / (distance - w)
  return new Vector3(
    x * wInv,
    y * wInv,
    z * wInv
  )
}

// Create Geometry Instance directly
const positions = new Float32Array(edges.length * 2 * 3)
const geometry = new BufferGeometry()
geometry.setAttribute('position', new Float32BufferAttribute(positions, 3))

const { onBeforeRender } = useLoop()

onBeforeRender(({ elapsed }) => {
  const angle = elapsed * 0.5
  
  const positionAttribute = geometry.attributes.position
  const posArray = positionAttribute.array as Float32Array
  let ptr = 0
  
  // Calculate transformed vertices
  const projectedVerts = vertices4D.map(v => {
    let p = [...v]
    p = rotateZW(p, angle)
    p = rotateXW(p, angle * 0.5)
    return project(p)
  })
  
  // Update edges
  edges.forEach(edge => {
    const v1 = projectedVerts[edge[0]]
    const v2 = projectedVerts[edge[1]]
    
    posArray[ptr++] = v1.x
    posArray[ptr++] = v1.y
    posArray[ptr++] = v1.z
    
    posArray[ptr++] = v2.x
    posArray[ptr++] = v2.y
    posArray[ptr++] = v2.z
  })
  
  positionAttribute.needsUpdate = true
})
</script>

<template>
  <TresGroup>
    <!-- Wireframe: Pass geometry instance via prop -->
    <TresLineSegments :geometry="geometry">
      <TresLineBasicMaterial color="#00ffff" :linewidth="2" :opacity="0.8" transparent />
    </TresLineSegments>
    
    <!-- Inner Glow -->
    <TresMesh>
      <TresBoxGeometry :args="[0.5, 0.5, 0.5]" />
      <TresMeshBasicMaterial color="#ff00ff" :opacity="0.2" transparent />
    </TresMesh>
  </TresGroup>
</template>
