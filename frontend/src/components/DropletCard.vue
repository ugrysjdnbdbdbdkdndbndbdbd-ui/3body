<script setup lang="ts">
/**
 * DropletCard - 水滴质感容器
 * "光滑得像镜子一样，反射着宇宙的一切。"
 */
defineProps<{
  title?: string
  active?: boolean
}>()
</script>

<template>
  <div class="droplet-card" :class="{ active }">
    <!-- 水滴表面反射层 -->
    <div class="reflection"></div>
    
    <!-- 内容层 -->
    <div class="droplet-content">
      <h3 v-if="title" class="droplet-title">{{ title }}</h3>
      <slot />
    </div>

    <!-- 底部光晕 (推进器) -->
    <div class="engine-glow"></div>
  </div>
</template>

<style scoped>
.droplet-card {
  position: relative;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 30px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 
    0 20px 50px rgba(0, 0, 0, 0.5),
    inset 0 0 30px rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(20px);
  overflow: hidden;
  transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1);
  transform-style: preserve-3d;
}

.droplet-card:hover, .droplet-card.active {
  transform: translateY(-5px) scale(1.02);
  border-color: rgba(0, 255, 200, 0.4);
  box-shadow: 
    0 30px 60px rgba(0, 0, 0, 0.6),
    inset 0 0 20px rgba(0, 255, 200, 0.1);
}

.reflection {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 50%;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.1) 0%, transparent 100%);
  border-radius: 30px 30px 100% 100% / 30px 30px 20px 20px;
  pointer-events: none;
  opacity: 0.5;
}

.droplet-content {
  position: relative;
  z-index: 2;
  padding: 1.5rem;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.droplet-title {
  font-family: var(--font-display);
  font-weight: 300;
  font-size: 0.9rem;
  letter-spacing: 0.2em;
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 1rem 0;
  text-transform: uppercase;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 0.5rem;
}

.engine-glow {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  height: 5px;
  background: var(--holo-blue);
  box-shadow: 0 0 20px 5px var(--holo-blue);
  opacity: 0;
  transition: opacity 0.4s;
  border-radius: 50%;
}

.droplet-card:hover .engine-glow {
  opacity: 0.6;
}
</style>
