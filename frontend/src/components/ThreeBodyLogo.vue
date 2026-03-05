<script setup lang="ts">
/**
 * 三体 Logo：三圆互锁 + 左右箭头 + 顶圆内五角星
 * 模仿金属徽章造型，可用于导航品牌与底纹。
 */
defineProps<{
  /** 类名，用于底纹时加 transparent/watermark */
  class?: string
  /** 是否仅描边（底纹常用） */
  outline?: boolean
}>()
</script>

<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 100 100"
    fill="none"
    class="three-body-logo"
    :class="[$props.class, { outline: $props.outline }]"
    aria-hidden="true"
  >
    <!-- 三圆互锁：底左、底右、顶中。为表现“在上”，顶圆后绘并略压住两底圆 -->
    <!-- 底左圆（带向左箭头） -->
    <g class="circle-left">
      <circle cx="28" cy="62" r="20" stroke="currentColor" :stroke-width="outline ? 1.2 : 2" fill="none" />
      <path
        d="M8 62 L18 57 L18 67 Z"
        stroke="currentColor"
        :stroke-width="outline ? 1 : 1.5"
        fill="none"
      />
    </g>
    <!-- 底右圆（带向右箭头） -->
    <g class="circle-right">
      <circle cx="72" cy="62" r="20" stroke="currentColor" :stroke-width="outline ? 1.2 : 2" fill="none" />
      <path
        d="M92 62 L82 57 L82 67 Z"
        stroke="currentColor"
        :stroke-width="outline ? 1 : 1.5"
        fill="none"
      />
    </g>
    <!-- 顶圆（内含五角星） -->
    <g class="circle-top">
      <circle cx="50" cy="34" r="20" stroke="currentColor" :stroke-width="outline ? 1.2 : 2" fill="none" />
      <!-- 五角星：中心 (50,34)，外径 10，内径约 4，一顶点略偏左上 -->
      <polygon
        points="50,24 46.2,32.8 40.5,30.9 47.7,37.2 44.1,42.1 52.4,37.2 55.9,42.1 53.8,32.8 59.5,30.9 50,24"
        stroke="currentColor"
        :stroke-width="outline ? 0.8 : 1.2"
        fill="none"
      />
    </g>
  </svg>
</template>

<style scoped>
.three-body-logo {
  display: block;
  color: inherit;
}
.three-body-logo.outline {
  opacity: 0.9;
}
</style>
