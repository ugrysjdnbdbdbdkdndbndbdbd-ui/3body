<script setup lang="ts">
/**
 * 微尘系统 — Canvas 2D 极细粒子，缓慢漂移，疏密如引力场。
 */
import { ref, onMounted, onUnmounted } from 'vue'

const canvasRef = ref<HTMLCanvasElement | null>(null)
let raf = 0
let resizeHandler: (() => void) | null = null
let particles: { x: number; y: number; vx: number; vy: number; r: number; density: number }[] = []

onMounted(() => {
  const canvas = canvasRef.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const resize = () => {
    const dpr = Math.min(window.devicePixelRatio, 2)
    canvas.width = window.innerWidth * dpr
    canvas.height = window.innerHeight * dpr
    canvas.style.width = `${window.innerWidth}px`
    canvas.style.height = `${window.innerHeight}px`
    ctx.scale(dpr, dpr)
    initParticles()
  }

  const initParticles = () => {
    const w = window.innerWidth
    const h = window.innerHeight
    const count = Math.min(800, Math.floor((w * h) / 12000))
    particles = []
    for (let i = 0; i < count; i++) {
      const x = Math.random() * w
      const y = Math.random() * h
      const angle = Math.random() * Math.PI * 2
      const speed = 0.08 + Math.random() * 0.12
      const density = 0.3 + Math.random() * 0.7
      particles.push({
        x,
        y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        r: 0.4 + Math.random() * 0.6,
        density,
      })
    }
  }

  const draw = () => {
    const w = window.innerWidth
    const h = window.innerHeight
    ctx.clearRect(0, 0, w, h)

    for (const p of particles) {
      p.x += p.vx
      p.y += p.vy
      if (p.x < 0 || p.x > w) p.vx *= -1
      if (p.y < 0 || p.y > h) p.vy *= -1
      const alpha = 0.15 * p.density
      ctx.beginPath()
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(200, 220, 255, ${alpha})`
      ctx.fill()
    }
    raf = requestAnimationFrame(draw)
  }

  resizeHandler = resize
  resize()
  window.addEventListener('resize', resize)
  raf = requestAnimationFrame(draw)
})

onUnmounted(() => {
  if (resizeHandler) window.removeEventListener('resize', resizeHandler)
  cancelAnimationFrame(raf)
})
</script>

<template>
  <canvas
    ref="canvasRef"
    class="void-dust"
    aria-hidden="true"
  />
</template>

<style scoped>
.void-dust {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}
</style>
