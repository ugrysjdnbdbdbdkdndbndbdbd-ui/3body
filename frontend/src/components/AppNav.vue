<script setup lang="ts">
/**
 * AppNav - 战术导航栏 (Grouped Layout v2)
 * 风格：Command Center HUD - 首页独立 + 五字分类
 */
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 一级入口：首页
const topLevelItems = [
  { path: '/sector-c', label: '首页', code: 'HOME' },
]
// 时间和尽头右侧的一级入口
const rightLevelItems = [
  { path: '/sector-guestbook', label: '宇宙留言簿', code: 'GUESTBOOK' },
]

// 定义导航结构 (5字分类)
const navGroups = [
  {
    label: '起源和接触',
    code: 'ORIGINS',
    items: [
      { path: '/sector-r', label: '红岸', code: 'RED-COAST' },
      { path: '/sector-t', label: '三体摆', code: 'PENDULUM' },
      { path: '/sector-v', label: '人列计算机', code: 'VON-NEUMANN' },
      { path: '/sector-a', label: '智子', code: 'SOPHON' },
      { path: '/sector-boundary', label: '科学边界', code: 'BOUNDARY' },
    ]
  },
  {
    label: '危机和战略',
    code: 'CRISIS',
    items: [
      { path: '/sector-pdc', label: '行星防御', code: 'PDC' },
      { path: '/sector-ravine', label: '大低谷', code: 'RAVINE' },
      { path: '/sector-f', label: '面壁计划', code: 'WALLFACER' },
      { path: '/sector-s', label: '阶梯', code: 'STAIRCASE' },
      { path: '/sector-w', label: '水滴', code: 'DROPLET' },
      { path: '/sector-e', label: '黑暗森林', code: 'FOREST' },
    ]
  },
  {
    label: '宇宙和维度',
    code: 'UNIVERSE',
    items: [
      { path: '/sector-j', label: '掩体', code: 'BUNKER' },
      { path: '/sector-l', label: '曲率', code: 'LIGHTSPEED' },
      { path: '/sector-g', label: '四维', code: '4D-FRAG' },
      { path: '/sector-blind', label: '盲区', code: 'BLIND-ZONE' },
    ]
  },
  {
    label: '岁月和文明',
    code: 'HISTORY',
    items: [
      { path: '/sector-b', label: '编年史', code: 'CHRONICLE' },
      { path: '/sector-library', label: '原著阅读', code: 'LIBRARY' },
      { path: '/sector-p', label: '人物志', code: 'PRISMS' },
      { path: '/sector-d', label: '二向箔画廊', code: '2D-GALLERY' },
      { path: '/sector-tomb', label: '文明墓碑', code: 'TOMB' },
      { path: '/sector-human', label: '银河人类', code: 'GALAXY-HUMAN' },
    ]
  },
  {
    label: '时间和尽头',
    code: 'ETERNITY',
    items: [
      { path: '/sector-u', label: '小宇宙', code: 'UNI-647' },
      { path: '/sector-x', label: '未知', code: 'UNKNOWN' },
      { path: '/sector-m', label: '宇宙膜', code: 'MEMBRANE' },
    ]
  }
]

const activeGroupIndex = ref<number | null>(null)
const mobileMenuOpen = ref(false)

function isActive(path: string) {
  return route.path.startsWith(path)
}

function isGroupActive(groupItems: { path: string }[]) {
  return groupItems.some(item => isActive(item.path))
}

function handleGroupClick(index: number) {
  if (activeGroupIndex.value === index) {
    activeGroupIndex.value = null
  } else {
    activeGroupIndex.value = index
  }
}

function navigate(path: string) {
  router.push(path)
  activeGroupIndex.value = null
  mobileMenuOpen.value = false
}

function toggleMobileMenu() {
  mobileMenuOpen.value = !mobileMenuOpen.value
}
</script>

<template>
  <nav class="tactical-nav">
    <div class="nav-left">
      <div class="brand-wrapper">
        <div class="logo-3body">
          <div class="sun sun-1"></div>
          <div class="sun sun-2"></div>
          <div class="sun sun-3"></div>
        </div>
        <h1 class="brand-logo">3BODY <span class="brand-x">X</span> 三体体验沙盒</h1>
      </div>
      <div class="nav-deco-line"></div>
    </div>

    <button type="button" class="nav-hamburger" aria-label="打开菜单" @click="toggleMobileMenu">
      <span class="hamburger-line" :class="{ open: mobileMenuOpen }"></span>
      <span class="hamburger-line" :class="{ open: mobileMenuOpen }"></span>
      <span class="hamburger-line" :class="{ open: mobileMenuOpen }"></span>
    </button>

    <div class="nav-center">
      <!-- 独立 tab：首页 -->
      <div 
        v-for="item in topLevelItems"
        :key="item.path"
        class="nav-single"
        :class="{ active: isActive(item.path) }"
        @click="navigate(item.path)"
      >
        <span class="single-code">{{ item.code }}</span>
        <span class="single-label">{{ item.label }}</span>
        <div class="single-indicator"></div>
      </div>

      <div class="divider"></div>

      <!-- 分组菜单 -->
      <div 
        v-for="(group, idx) in navGroups" 
        :key="group.code"
        class="nav-group"
        :class="{ 'group-active': isGroupActive(group.items) }"
        @mouseenter="activeGroupIndex = idx"
        @mouseleave="activeGroupIndex = null"
      >
        <div class="group-header" @click="handleGroupClick(idx)">
          <span class="group-code">{{ group.code }}</span>
          <span class="group-label">{{ group.label }}</span>
          <div class="group-indicator"></div>
        </div>

        <transition name="dropdown">
          <div v-show="activeGroupIndex === idx" class="group-dropdown">
            <div 
              v-for="item in group.items" 
              :key="item.path"
              class="dropdown-item"
              :class="{ active: isActive(item.path) }"
              @click.stop="navigate(item.path)"
            >
              <span class="item-label">{{ item.label }}</span>
              <span class="item-code">{{ item.code }}</span>
            </div>
          </div>
        </transition>
      </div>

      <!-- 时间和尽头右侧一级入口：宇宙留言簿 -->
      <div 
        v-for="item in rightLevelItems"
        :key="item.path"
        class="nav-single"
        :class="{ active: isActive(item.path) }"
        @click="navigate(item.path)"
      >
        <span class="single-code">{{ item.code }}</span>
        <span class="single-label">{{ item.label }}</span>
        <div class="single-indicator"></div>
      </div>
    </div>

    <!-- 小屏抽屉菜单 -->
    <transition name="drawer">
      <div v-show="mobileMenuOpen" class="nav-drawer-backdrop" @click="mobileMenuOpen = false">
        <aside class="nav-drawer" @click.stop>
          <div class="drawer-header">
            <span class="drawer-title">导航</span>
            <button type="button" class="drawer-close" aria-label="关闭" @click="mobileMenuOpen = false">×</button>
          </div>
          <div class="drawer-body">
            <div class="drawer-item" :class="{ active: isActive(topLevelItems[0].path) }" @click="navigate(topLevelItems[0].path)">
              <span class="drawer-item-label">{{ topLevelItems[0].label }}</span>
              <span class="drawer-item-code">{{ topLevelItems[0].code }}</span>
            </div>
            <template v-for="(group, idx) in navGroups" :key="group.code">
              <div class="drawer-group-label">{{ group.label }}</div>
              <div
                v-for="item in group.items"
                :key="item.path"
                class="drawer-item"
                :class="{ active: isActive(item.path) }"
                @click="navigate(item.path)"
              >
                <span class="drawer-item-label">{{ item.label }}</span>
                <span class="drawer-item-code">{{ item.code }}</span>
              </div>
            </template>
            <div class="drawer-item" :class="{ active: isActive(rightLevelItems[0].path) }" @click="navigate(rightLevelItems[0].path)">
              <span class="drawer-item-label">{{ rightLevelItems[0].label }}</span>
              <span class="drawer-item-code">{{ rightLevelItems[0].code }}</span>
            </div>
          </div>
        </aside>
      </div>
    </transition>

    <div class="nav-right">
      <div class="identity-badge" @click="userStore.login('bug')">
        <span class="role-icon">{{ userStore.role === 'bug' ? '🐛' : (userStore.role === 'eto' ? '🐍' : (userStore.role === 'wallfacer' ? '🗿' : '⚔️')) }}</span>
        <div class="role-info">
          <span class="role-name">{{ userStore.roleName }}</span>
          <span class="user-name">{{ userStore.username }}</span>
        </div>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.identity-badge {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.4rem 1rem;
  border: 1px solid rgba(0, 255, 200, 0.2);
  border-radius: 4px;
  background: rgba(0, 255, 200, 0.05);
  cursor: pointer;
  transition: all 0.3s;
}

.identity-badge:hover {
  background: rgba(0, 255, 200, 0.1);
  border-color: var(--holo-blue);
}

.role-icon {
  font-size: 1.2rem;
}

.role-info {
  display: flex;
  flex-direction: column;
}

.role-name {
  font-family: 'Russo One', sans-serif;
  font-size: 0.7rem;
  color: var(--holo-green);
  letter-spacing: 0.05em;
}

.user-name {
  font-family: monospace;
  font-size: 0.6rem;
  color: rgba(255, 255, 255, 0.5);
}

.tactical-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
  padding: 0 2rem;
  background: rgba(2, 6, 23, 0.9);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(0, 255, 200, 0.15);
  position: relative;
  z-index: 100;
  box-shadow: 0 4px 30px rgba(0,0,0,0.3);
}

.nav-hamburger {
  display: none;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  width: 40px;
  height: 40px;
  padding: 0;
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  cursor: pointer;
  color: #fff;
  transition: background 0.2s, border-color 0.2s;
}
.nav-hamburger:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: var(--holo-blue);
}
.hamburger-line {
  display: block;
  width: 18px;
  height: 2px;
  margin: 0 auto;
  background: currentColor;
  transition: transform 0.25s, opacity 0.25s;
}
.nav-hamburger .hamburger-line:nth-child(1).open { transform: translateY(7px) rotate(45deg); }
.nav-hamburger .hamburger-line:nth-child(2).open { opacity: 0; }
.nav-hamburger .hamburger-line:nth-child(3).open { transform: translateY(-7px) rotate(-45deg); }

.nav-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  min-width: 200px;
}

.brand-wrapper {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.logo-3body {
  position: relative;
  width: 24px;
  height: 24px;
}

.sun {
  position: absolute;
  border-radius: 50%;
  box-shadow: 0 0 4px currentColor;
}

.sun-1 {
  width: 8px;
  height: 8px;
  background: #ff4400;
  color: #ff4400;
  top: 0;
  left: 50%;
  animation: orbit-1 4s linear infinite;
}

.sun-2 {
  width: 6px;
  height: 6px;
  background: #00ccff;
  color: #00ccff;
  bottom: 0;
  left: 0;
  animation: orbit-2 5s linear infinite;
}

.sun-3 {
  width: 5px;
  height: 5px;
  background: #fff;
  color: #fff;
  bottom: 4px;
  right: 0;
  animation: orbit-3 3s linear infinite;
}

@keyframes orbit-1 {
  0% { transform: translate(-50%, 0) rotate(0deg) translateX(8px); }
  100% { transform: translate(-50%, 0) rotate(360deg) translateX(8px); }
}

@keyframes orbit-2 {
  0% { transform: rotate(0deg) translateX(10px); }
  100% { transform: rotate(-360deg) translateX(10px); }
}

@keyframes orbit-3 {
  0% { transform: rotate(0deg) translateY(6px); }
  100% { transform: rotate(360deg) translateY(6px); }
}

.brand-logo {
  font-family: 'Russo One', sans-serif;
  font-size: 1.4rem;
  color: #fff;
  margin: 0;
  letter-spacing: 0.1em;
  text-shadow: 0 0 10px rgba(0,255,255,0.3);
  display: flex;
  align-items: center;
}

.brand-x {
  color: var(--holo-blue);
  margin: 0 4px;
  font-style: italic;
}

.nav-deco-line {
  width: 30px;
  height: 2px;
  background: linear-gradient(90deg, var(--holo-blue), transparent);
  opacity: 0.5;
}

.nav-center {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  height: 100%;
  flex: 1;
  min-width: 0;
  justify-content: center;
}

/* Single Item (Home) */
.nav-single {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 0 1.5rem;
  cursor: pointer;
  position: relative;
  transition: all 0.3s;
}
.nav-single:hover { background: rgba(255,255,255,0.03); }

.single-code {
  font-family: monospace;
  font-size: 0.55rem;
  color: rgba(255,255,255,0.4);
  margin-bottom: 2px;
}
.single-label {
  font-size: 1rem; /* Slightly larger for Home */
  font-weight: 600;
  color: rgba(255,255,255,0.9);
}
.single-indicator {
  position: absolute;
  bottom: 0;
  width: 100%;
  height: 2px;
  background: var(--holo-blue);
  box-shadow: 0 0 10px var(--holo-blue);
  transform: scaleX(0);
  transition: transform 0.3s;
}
.nav-single.active .single-indicator { transform: scaleX(1); }
.nav-single.active .single-label { color: #fff; text-shadow: 0 0 8px rgba(255,255,255,0.5); }
.nav-single.active .single-code { color: var(--holo-blue); }

.divider {
  width: 1px;
  height: 24px;
  background: rgba(255,255,255,0.1);
  margin: 0 0.5rem;
}

/* Nav Group */
.nav-group {
  position: relative;
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 1.2rem;
  cursor: pointer;
  transition: all 0.3s;
}

.nav-group:hover {
  background: rgba(255,255,255,0.03);
}

.group-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.group-code {
  font-family: monospace;
  font-size: 0.55rem;
  color: rgba(255,255,255,0.4);
  letter-spacing: 0.1em;
  margin-bottom: 2px;
  transition: color 0.3s;
}

.group-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: rgba(255,255,255,0.8);
  letter-spacing: 0.05em;
  transition: color 0.3s;
}

.nav-group:hover .group-code,
.nav-group.group-active .group-code {
  color: var(--holo-blue);
}

.nav-group:hover .group-label,
.nav-group.group-active .group-label {
  color: #fff;
  text-shadow: 0 0 8px rgba(255,255,255,0.5);
}

.group-indicator {
  position: absolute;
  bottom: -21px; /* Align with bottom edge */
  left: 50%;
  transform: translateX(-50%) scaleX(0);
  width: 120%;
  height: 2px;
  background: var(--holo-blue);
  box-shadow: 0 0 10px var(--holo-blue);
  transition: transform 0.3s;
}

.nav-group.group-active .group-indicator {
  transform: translateX(-50%) scaleX(1);
}

/* Dropdown */
.group-dropdown {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(5, 10, 20, 0.95);
  border: 1px solid rgba(0, 255, 200, 0.2);
  border-top: none;
  min-width: 160px;
  padding: 0.5rem 0;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
  backdrop-filter: blur(10px);
  clip-path: polygon(0 0, 100% 0, 100% 100%, 10px 100%, 0 calc(100% - 10px));
}

.dropdown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem 1.2rem;
  color: rgba(255,255,255,0.7);
  transition: all 0.2s;
  border-left: 2px solid transparent;
}

.dropdown-item:hover {
  background: rgba(0, 255, 200, 0.05);
  color: #fff;
  padding-left: 1.5rem;
}

.dropdown-item.active {
  background: rgba(0, 255, 200, 0.1);
  color: var(--holo-blue);
  border-left-color: var(--holo-blue);
}

.item-label { font-size: 0.85rem; }
.item-code { font-family: monospace; font-size: 0.6rem; opacity: 0.5; }

/* Transitions */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px);
}

.nav-right {
  display: flex;
  align-items: center;
  min-width: 180px;
  justify-content: flex-end;
}

.status-box {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.4rem 1rem;
  border: 1px solid rgba(0, 255, 200, 0.2);
  border-radius: 4px;
  background: rgba(0, 255, 200, 0.05);
}

.status-dot {
  width: 6px;
  height: 6px;
  background: var(--holo-green);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--holo-green);
  animation: pulse 2s infinite;
}

.status-text {
  font-family: monospace;
  font-size: 0.7rem;
  color: var(--holo-green);
  letter-spacing: 0.1em;
}

@keyframes pulse {
  0% { opacity: 1; box-shadow: 0 0 5px var(--holo-green); }
  50% { opacity: 0.5; box-shadow: 0 0 2px var(--holo-green); }
  100% { opacity: 1; box-shadow: 0 0 5px var(--holo-green); }
}

/* 小屏抽屉 */
.nav-drawer-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 200;
  backdrop-filter: blur(4px);
}
.nav-drawer {
  position: absolute;
  top: 0;
  right: 0;
  width: min(320px, 85vw);
  height: 100%;
  background: rgba(5, 12, 28, 0.98);
  border-left: 1px solid rgba(0, 255, 200, 0.2);
  box-shadow: -10px 0 40px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
}
.drawer-title {
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  letter-spacing: 0.05em;
}
.drawer-close {
  width: 36px;
  height: 36px;
  padding: 0;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s, color 0.2s;
}
.drawer-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}
.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem 0;
}
.drawer-group-label {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.45);
  letter-spacing: 0.1em;
  padding: 1rem 1.25rem 0.35rem;
  text-transform: uppercase;
}
.drawer-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.7rem 1.25rem;
  color: rgba(255, 255, 255, 0.85);
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  border-left: 3px solid transparent;
}
.drawer-item:hover {
  background: rgba(0, 255, 200, 0.06);
  color: #fff;
}
.drawer-item.active {
  background: rgba(0, 255, 200, 0.1);
  color: var(--holo-blue);
  border-left-color: var(--holo-blue);
}
.drawer-item-label { font-size: 0.9rem; }
.drawer-item-code { font-family: monospace; font-size: 0.6rem; opacity: 0.5; }

.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.25s ease;
}
.drawer-enter-active .nav-drawer,
.drawer-leave-active .nav-drawer {
  transition: transform 0.25s ease;
}
.drawer-enter-from .nav-drawer,
.drawer-leave-to .nav-drawer {
  transform: translateX(100%);
}
.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}
.drawer-enter-to .nav-drawer,
.drawer-leave-from .nav-drawer {
  transform: translateX(0);
}

/* 全局自适应断点 */
@media (max-width: 1200px) {
  .tactical-nav { padding: 0 1.25rem; }
  .brand-logo { font-size: 1.2rem; }
  .nav-left { min-width: 140px; gap: 1rem; flex: 0 0 auto; }
  .nav-center {
    gap: 0.35rem;
    flex-wrap: nowrap;
    overflow-x: auto;
    overflow-y: hidden;
    justify-content: flex-start;
    padding: 0 0.25rem;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: thin;
  }
  .nav-center::-webkit-scrollbar { height: 4px; }
  .nav-center::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 2px; }
  .nav-single { padding: 0 0.9rem; flex-shrink: 0; }
  .single-label { font-size: 0.9rem; }
  .group-label { font-size: 0.82rem; }
  .nav-group { padding: 0 0.75rem; flex-shrink: 0; }
  .nav-right { min-width: 120px; flex: 0 0 auto; }
  .identity-badge { padding: 0.35rem 0.75rem; gap: 0.5rem; }
  .role-name { font-size: 0.65rem; }
  .user-name { font-size: 0.55rem; }
}

@media (max-width: 992px) {
  .tactical-nav { height: 56px; padding: 0 1rem; }
  .brand-logo { font-size: 1.05rem; }
  .brand-logo .brand-x { margin: 0 2px; }
  .nav-deco-line { display: none; }
  .nav-left { min-width: 0; flex: 1; }
  .nav-center {
    display: none;
  }
  .nav-hamburger {
    display: flex;
    flex-shrink: 0;
  }
  .nav-right { min-width: 0; margin-left: 0.5rem; flex-shrink: 0; }
  .identity-badge .role-info { display: none; }
  .identity-badge { padding: 0.4rem 0.6rem; }
}

@media (max-width: 576px) {
  .tactical-nav { padding: 0 0.75rem; }
  .brand-logo {
    font-size: 0.95rem;
  }
  .logo-3body { width: 20px; height: 20px; }
  .sun-1 { width: 6px; height: 6px; }
  .sun-2 { width: 5px; height: 5px; }
  .sun-3 { width: 4px; height: 4px; }
}
</style>
