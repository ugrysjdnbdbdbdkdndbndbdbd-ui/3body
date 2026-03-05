<script setup lang="ts">
/**
 * TechCard - 高科技感容器组件
 * 特性：四角光标、背景网格、扫描线、Hover发光
 */
withDefaults(defineProps<{
  title?: string
  subtitle?: string
  variant?: 'default' | 'danger' | 'success'
  loading?: boolean
}>(), {
  variant: 'default'
})
</script>

<template>
  <div class="tech-card" :class="[`variant-${variant}`, { loading }]">
    <!-- 装饰性四角 -->
    <div class="corner corner-tl"></div>
    <div class="corner corner-tr"></div>
    <div class="corner corner-bl"></div>
    <div class="corner corner-br"></div>

    <!-- 顶部装饰条 -->
    <div class="tech-header" v-if="title || subtitle">
      <div class="header-line"></div>
      <div class="header-content">
        <h3 v-if="title" class="tech-title">{{ title }}</h3>
        <span v-if="subtitle" class="tech-subtitle">// {{ subtitle }}</span>
      </div>
      <div class="header-deco">
        <span class="deco-dot"></span>
        <span class="deco-dot"></span>
        <span class="deco-dot"></span>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="tech-body">
      <slot />
    </div>

    <!-- 扫描线遮罩 (内部) -->
    <div class="scanline-overlay"></div>
  </div>
</template>

<style scoped>
.tech-card {
  position: relative;
  background: rgba(2, 6, 23, 0.6);
  border: 1px solid rgba(0, 240, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  transition: all 0.3s var(--ease-out-expo);
  overflow: hidden;
  animation: tech-unfold 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
}

@keyframes tech-unfold {
  0% {
    opacity: 0;
    transform: scaleY(0.1) scaleX(0.8);
    filter: brightness(2);
  }
  50% {
    opacity: 1;
    transform: scaleY(1) scaleX(0.95);
  }
  100% {
    transform: scale(1);
    filter: none;
  }
}

.tech-card:hover {
  border-color: rgba(0, 240, 255, 0.3);
  box-shadow: 0 0 20px rgba(0, 240, 255, 0.1);
  background: rgba(2, 6, 23, 0.7);
}

/* 变体：红色警告 */
.tech-card.variant-danger {
  border-color: rgba(255, 42, 42, 0.2);
}
.tech-card.variant-danger:hover {
  border-color: rgba(255, 42, 42, 0.5);
  box-shadow: 0 0 20px rgba(255, 42, 42, 0.15);
}

/* 四角装饰 */
.corner {
  position: absolute;
  width: 8px;
  height: 8px;
  border-color: var(--holo-blue);
  border-style: solid;
  transition: all 0.3s ease;
}
.variant-danger .corner { border-color: var(--holo-red); }

.corner-tl { top: -1px; left: -1px; border-width: 2px 0 0 2px; }
.corner-tr { top: -1px; right: -1px; border-width: 2px 2px 0 0; }
.corner-bl { bottom: -1px; left: -1px; border-width: 0 0 2px 2px; }
.corner-br { bottom: -1px; right: -1px; border-width: 0 2px 2px 0; }

.tech-card:hover .corner {
  width: 12px;
  height: 12px;
}

/* 头部 */
.tech-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  padding-bottom: 0.5rem;
  margin-bottom: 0.5rem;
}

.tech-title {
  margin: 0;
  font-family: var(--font-tech);
  font-size: 0.9rem;
  color: var(--holo-blue);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  text-shadow: 0 0 5px rgba(0, 240, 255, 0.5);
}
.variant-danger .tech-title { color: var(--holo-red); text-shadow: 0 0 5px rgba(255, 42, 42, 0.5); }

.tech-subtitle {
  font-family: var(--font-tech);
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.4);
  margin-left: 0.5rem;
}

.header-deco {
  display: flex;
  gap: 4px;
}

.deco-dot {
  width: 4px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
}
.tech-card:hover .deco-dot:nth-child(1) { background: var(--holo-blue); box-shadow: 0 0 5px var(--holo-blue); }
.tech-card:hover .deco-dot:nth-child(2) { background: var(--holo-blue); animation: blink 1s infinite; }

.tech-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 1;
}

.scanline-overlay {
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0, 240, 255, 0.02) 3px
  );
  pointer-events: none;
  z-index: 0;
}

@keyframes blink {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 1; }
}
</style>
