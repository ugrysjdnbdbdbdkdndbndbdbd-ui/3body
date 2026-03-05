<script setup lang="ts">
/**
 * Cosmic Romance: 星图式导航
 * 有机丝状结构 + 引力波纹曲线 + 缓慢呼吸脉动
 */
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

interface SectorNode {
  path: string
  label: string
  x: number
  y: number
  dim?: boolean
}

const sectors: SectorNode[] = [
  { path: '/sector-c', label: '宇宙广播', x: 50, y: 12 },
  { path: '/sector-a', label: '智子终端', x: 18, y: 48 },
  { path: '/sector-b', label: '文明编年史', x: 82, y: 45 },
  { path: '/sector-d', label: '二向箔画廊', x: 50, y: 88 },
  { path: '/sector-e', label: '人物志', x: 82, y: 88 },
  { path: '/sector-t', label: '三体摆', x: 18, y: 88 },
  { path: '/sector-u', label: '小宇宙', x: 18, y: 12 },
  { path: '/sector-f', label: '面壁计划', x: 30, y: 30 },
  { path: '/sector-s', label: '阶梯计划', x: 60, y: 15 },
  { path: '/sector-g', label: '四维碎片', x: 70, y: 30 },
  { path: '/sector-l', label: '曲率', x: 80, y: 20 },
  { path: '/sector-j', label: '掩体', x: 60, y: 60 },
  { path: '/sector-r', label: '红岸', x: 70, y: 70 },
  { path: '/sector-w', label: '水滴', x: 40, y: 70 },
  { path: '/sector-x', label: '未知区域', x: 50, y: 50, dim: true },
]

/** 有机曲线：贝塞尔路径，模拟星系丝状结构 */
const paths = [
  'M 50,12 Q 35,30 18,48',
  'M 50,12 Q 68,28 82,45',
  'M 50,12 Q 50,50 50,88',
  'M 18,48 Q 40,55 82,45',
  'M 18,48 Q 34,68 50,88',
  'M 82,45 Q 66,66 50,88',
  'M 50,88 Q 50,70 50,50',
  'M 82,45 Q 82,66 82,88', // B -> E
  'M 50,88 Q 66,88 82,88', // D -> E
  'M 18,48 Q 18,68 18,88', // A -> T
  'M 50,88 Q 34,88 18,88', // D -> T
  'M 50,12 Q 34,12 18,12', // C -> U
  'M 18,48 Q 24,39 30,30', // A -> F
  'M 50,12 Q 40,21 30,30', // C -> F
  'M 50,12 Q 60,21 70,30', // C -> G
  'M 82,45 Q 76,37 70,30', // B -> G
  'M 82,45 Q 76,57 70,70', // B -> R
  'M 50,88 Q 60,79 70,70', // D -> R
  'M 30,30 Q 35,50 40,70', // F -> W
  'M 40,70 Q 50,65 60,60', // W -> J
  'M 60,60 Q 70,40 80,20', // J -> L
  'M 30,30 Q 45,20 60,15', // F -> S
  'M 60,15 Q 70,15 80,20', // S -> L
]

function go(path: string) {
  router.push(path)
}
</script>

<template>
  <nav class="starmap-nav" aria-label="扇区导航">
    <!-- 有机曲线：引力波纹，缓慢脉动 -->
    <svg class="filament-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
      <defs>
        <linearGradient id="filament-grad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="rgba(125,249,255,0.12)" />
          <stop offset="50%" stop-color="rgba(125,249,255,0.25)" />
          <stop offset="100%" stop-color="rgba(125,249,255,0.12)" />
        </linearGradient>
        <filter id="filament-glow">
          <feGaussianBlur stdDeviation="0.3" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      <g filter="url(#filament-glow)">
        <path
          v-for="(d, i) in paths"
          :key="i"
          :d="d"
          class="filament-path"
          fill="none"
          stroke="url(#filament-grad)"
          stroke-width="0.4"
          stroke-linecap="round"
        />
      </g>
    </svg>

    <!-- 节点：浮于太空，自发光 -->
    <div class="starmap-nodes">
      <button
        v-for="s in sectors"
        :key="s.path"
        type="button"
        class="star-node"
        :class="{ active: route.path === s.path, 'star-node-dim': s.dim }"
        :style="{ left: s.x + '%', top: s.y + '%' }"
        :title="s.label"
        @click="go(s.path)"
      >
        <span class="node-core" />
        <span class="node-aura" />
        <span class="node-label">{{ s.label }}</span>
      </button>
    </div>
  </nav>
</template>

<style scoped>
.starmap-nav {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 100;
}

.starmap-nodes {
  position: absolute;
  inset: 0;
  pointer-events: auto;
}

/* ========== 有机曲线：丝状结构 ========== */
.filament-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.filament-path {
  stroke-dasharray: 100;
  stroke-dashoffset: 100;
  animation: filament-draw 3s ease-out forwards;
}

.filament-path:nth-child(1) { animation-delay: 0.2s; }
.filament-path:nth-child(2) { animation-delay: 0.4s; }
.filament-path:nth-child(3) { animation-delay: 0.6s; }
.filament-path:nth-child(4) { animation-delay: 0.8s; }
.filament-path:nth-child(5) { animation-delay: 1s; }
.filament-path:nth-child(6) { animation-delay: 1.2s; }
.filament-path:nth-child(7) { animation-delay: 1.4s; }
.filament-path:nth-child(8) { animation-delay: 1.6s; }
.filament-path:nth-child(9) { animation-delay: 1.8s; }
.filament-path:nth-child(10) { animation-delay: 2.0s; }
.filament-path:nth-child(11) { animation-delay: 2.2s; }

@keyframes filament-draw {
  to { stroke-dashoffset: 0; }
}

/* 脉动：像呼吸一样缓慢 */
.filament-path {
  animation: filament-draw 3s ease-out forwards,
             filament-pulse 10s ease-in-out infinite;
}

.filament-path:nth-child(1) { animation-delay: 0.2s, 0s; }
.filament-path:nth-child(2) { animation-delay: 0.4s, 0.3s; }
.filament-path:nth-child(3) { animation-delay: 0.6s, 0.6s; }
.filament-path:nth-child(4) { animation-delay: 0.8s, 0.9s; }
.filament-path:nth-child(5) { animation-delay: 1s, 1.2s; }
.filament-path:nth-child(6) { animation-delay: 1.2s, 1.5s; }
.filament-path:nth-child(7) { animation-delay: 1.4s, 1.8s; }

@keyframes filament-pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* ========== 节点：浮于太空 ========== */
.star-node {
  position: absolute;
  transform: translate(-50%, -50%);
  width: 1px;
  height: 1px;
  border: none;
  background: transparent;
  cursor: pointer;
  pointer-events: auto;
  transition: transform 1.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.star-node:hover {
  transform: translate(-50%, -50%) scale(1.5);
}

.node-core {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 6px;
  height: 6px;
  margin: -3px 0 0 -3px;
  border-radius: 50%;
  background: radial-gradient(
    circle at 30% 30%,
    rgba(184, 245, 255, 0.95),
    rgba(125, 249, 255, 0.7)
  );
  box-shadow:
    0 0 8px rgba(125, 249, 255, 0.5),
    0 0 20px rgba(125, 249, 255, 0.2);
}

.node-aura {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 20px;
  height: 20px;
  margin: -10px 0 0 -10px;
  border-radius: 50%;
  background: radial-gradient(
    circle,
    rgba(125, 249, 255, 0.15) 0%,
    transparent 70%
  );
  opacity: 0;
  transition: opacity 1s ease;
}

.star-node:hover .node-aura,
.star-node.active .node-aura {
  opacity: 1;
}

.star-node.active .node-core {
  box-shadow:
    0 0 12px rgba(125, 249, 255, 0.8),
    0 0 30px rgba(125, 249, 255, 0.3);
}

/* ========== 标签：优雅无衬线 ========== */
.node-label {
  position: absolute;
  left: 50%;
  top: 100%;
  transform: translateX(-50%);
  margin-top: 12px;
  font-family: var(--font-display);
  font-weight: 300;
  font-size: 11px;
  letter-spacing: 0.2em;
  color: rgba(184, 245, 255, 0.9);
  white-space: nowrap;
  opacity: 0;
  transition: opacity 1s ease;
  text-shadow: 0 0 16px rgba(125, 249, 255, 0.4);
}

.star-node:hover .node-label,
.star-node.active .node-label {
  opacity: 1;
}

.star-node.active .node-label {
  color: var(--color-primary);
}

/* PRD 扇区 X：未知区域，视觉上弱化表示预留 */
.star-node-dim .node-core {
  opacity: 0.5;
  box-shadow: 0 0 4px rgba(125, 249, 255, 0.3);
}
.star-node-dim:hover .node-core,
.star-node-dim.active .node-core {
  opacity: 1;
}
</style>
