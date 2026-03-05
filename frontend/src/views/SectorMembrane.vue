<script setup lang="ts">
/**
 * Sector Membrane: Time & Eternity (时间与尽头)
 * 核心：宇宙膜 (Cosmic Membrane)
 * 风格：抽象、流体、高维质感（纯 Canvas 2D 实现，避免 TresJS 依赖问题）
 */
import { ref, onMounted, onUnmounted } from 'vue'

const canvasRef = ref<HTMLCanvasElement | null>(null)
const animId = ref<number>(0)
let resizeHandler: () => void

onMounted(() => {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  resizeHandler = () => {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
  }
  resizeHandler()
  window.addEventListener('resize', resizeHandler)

  let t = 0
  function draw() {
    if (!canvas || !ctx) return
    const w = canvas.width
    const h = canvas.height

    ctx.fillStyle = '#000'
    ctx.fillRect(0, 0, w, h)

    const gradient = ctx.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w * 0.8)
    gradient.addColorStop(0, 'rgba(68, 0, 255, 0.3)')
    gradient.addColorStop(0.5, 'rgba(0, 255, 255, 0.15)')
    gradient.addColorStop(1, 'rgba(0, 0, 0, 0)')
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, w, h)

    ctx.strokeStyle = 'rgba(0, 255, 255, 0.2)'
    ctx.lineWidth = 1
    for (let i = 0; i < 8; i++) {
      ctx.beginPath()
      for (let x = 0; x <= w + 50; x += 10) {
        const y = h / 2 + Math.sin((x * 0.005) + t * 0.5 + i) * 80 + Math.sin((x * 0.01) + t * 0.3) * 40
        if (x === 0) ctx.moveTo(x, y)
        else ctx.lineTo(x, y)
      }
      ctx.stroke()
    }
    t += 0.02
    animId.value = requestAnimationFrame(draw)
  }
  draw()
})

onUnmounted(() => {
  cancelAnimationFrame(animId.value)
  if (resizeHandler) window.removeEventListener('resize', resizeHandler)
})
</script>

<template>
  <div class="sector-membrane">
    <canvas ref="canvasRef" class="membrane-canvas"></canvas>
    <div class="header-overlay">
      <h1>SECTOR M // COSMIC MEMBRANE</h1>
      <p>宇宙膜 · 边缘体验</p>
    </div>
    <div class="footer-overlay">
      <p>“我们到了宇宙的边缘。”</p>
      <p>前方没有任何东西。连“无”都没有。</p>
    </div>
  </div>
</template>

<style scoped>
.sector-membrane {
  width: 100%;
  min-height: 0;
  position: relative;
  background: #000;
  overflow: hidden;
}

.membrane-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: block;
}

.header-overlay {
  position: absolute;
  top: 2rem;
  left: 0;
  width: 100%;
  text-align: center;
  color: #fff;
  z-index: 10;
  pointer-events: none;
}

.header-overlay h1 {
  font-family: 'Rajdhani', sans-serif;
  letter-spacing: 0.2em;
  font-size: 2rem;
  text-shadow: 0 0 10px #00ffff;
  margin: 0;
}

.header-overlay p {
  color: #00cccc;
  margin-top: 0.5rem;
}

.footer-overlay {
  position: absolute;
  bottom: 4rem;
  width: 100%;
  text-align: center;
  color: #fff;
  z-index: 10;
  pointer-events: none;
  font-family: 'Noto Serif SC', serif;
}

.footer-overlay p {
  margin: 0.5rem;
  font-size: 1.1rem;
  text-shadow: 0 0 5px #000;
}
</style>
