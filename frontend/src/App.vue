<script setup lang="ts">
/**
 * App.vue - 全局配置
 * 强制暗色 + 切伦科夫蓝主色，MainLayout 负责沉浸式背景与状态栏。
 * 零点计划：全服共振状态注入 + 三体摆环境系统
 */
import { NConfigProvider, NMessageProvider, darkTheme } from 'naive-ui'
import type { GlobalThemeOverrides } from 'naive-ui'
import { computed } from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import { useUniverseStore } from '@/stores/universe'

const universe = useUniverseStore()

const appClass = computed(() => {
  const classes = [`theme-tint-${universe.themeTint}`]
  if (universe.resonanceState === '2d') classes.push('resonance-2d')
  if (universe.resonanceState === '1d') classes.push('resonance-1d')
  
  // Phase 1.2: Environment System
  if (universe.dehydrated) classes.push('mode-dehydrated')
  else if (universe.environment === 'cold') classes.push('env-cold')
  else if (universe.environment === 'heat') classes.push('env-heat')
  else if (universe.environment === 'rip') classes.push('env-rip')
  
  // Phase 1.7: Mental Seal Filter
  if (universe.mentalSeal) {
    classes.push(`seal-${universe.mentalSeal.seal_type.toLowerCase()}`)
  }
  
  return classes
})

const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#00FFFF',
    primaryColorHover: '#79F2FF',
    primaryColorPressed: '#00CBCC',
    primaryColorSuppl: '#00CBCC',
  },
}
</script>

<template>
  <NConfigProvider :theme="darkTheme" :theme-overrides="themeOverrides">
    <NMessageProvider>
      <div :class="appClass">
        <MainLayout />
      </div>
    </NMessageProvider>
  </NConfigProvider>
</template>

<style>
/* 全局共振样式 */
.resonance-2d {
  filter: contrast(1.2) grayscale(0.3);
  --depth-perspective: 0;
  --shadow-opacity: 0;
}
.resonance-2d * {
  transform: none !important;
  box-shadow: none !important;
  transition: none !important;
}

.resonance-1d {
  font-family: monospace !important;
  background: #000 !important;
  color: #0f0 !important;
}
.resonance-1d * {
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
}
.resonance-1d img, .resonance-1d video, .resonance-1d canvas {
  display: none !important;
}
.resonance-1d ::before, .resonance-1d ::after {
  content: ' [1D STREAM] ' !important;
  color: #050;
  font-size: 10px;
}

/* --- Environment System --- */

/* Dehydrated: Minimal HTML Mode */
.mode-dehydrated {
  background: #fff !important;
  color: #000 !important;
  font-family: serif !important;
}
.mode-dehydrated * {
  border: none !important;
  box-shadow: none !important;
  background: transparent !important;
  filter: none !important;
  animation: none !important;
  transition: none !important;
}
.mode-dehydrated img, .mode-dehydrated canvas, .mode-dehydrated svg {
  display: none !important;
}
.mode-dehydrated .app-header, .mode-dehydrated .app-footer {
  border-bottom: 1px solid #000 !important;
  border-top: 1px solid #000 !important;
}

/* Chaotic Cold: Frost */
.env-cold {
  filter: brightness(0.8) contrast(1.2) hue-rotate(180deg); /* Shift to blue/purple */
}
.env-cold::after {
  content: '';
  position: fixed;
  inset: 0;
  background: url('data:image/svg+xml;utf8,<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><filter id="noise"><feTurbulence type="fractalNoise" baseFrequency="0.8" /></filter><rect width="100%" height="100%" filter="url(%23noise)" opacity="0.1"/></svg>');
  pointer-events: none;
  z-index: 9999;
  mix-blend-mode: overlay;
}

/* Chaotic Heat: Heat */
.env-heat {
  filter: brightness(1.2) contrast(1.1) sepia(0.4) hue-rotate(-30deg); /* Shift to red/orange */
}
.env-heat body {
  animation: heat-shimmer 0.1s infinite;
}
@keyframes heat-shimmer {
  0% { transform: translate(0, 0); }
  50% { transform: translate(1px, 1px); }
  100% { transform: translate(-1px, -1px); }
}

/* Big Rip */
.env-rip * {
  animation: float-random 5s ease-in-out infinite;
}
@keyframes float-random {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  50% { transform: translate(10px, -10px) rotate(2deg); }
}

/* --- Mental Seal Filters --- */
/* Triumph: Saturation+20%, Brightness+10% */
.seal-triumph {
  filter: saturate(1.2) brightness(1.1);
}
/* Defeat: Grayscale, Noise */
.seal-defeat {
  filter: grayscale(0.8) contrast(1.2);
}
/* Advent: Invert */
.seal-advent {
  filter: invert(0.9) hue-rotate(180deg);
}
/* Survive: Night Vision */
.seal-survive {
  filter: sepia(1) hue-rotate(50deg) saturate(3) contrast(1.2);
}
</style>
