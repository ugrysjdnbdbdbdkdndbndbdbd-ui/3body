<script setup lang="ts">
import { useUserStore, type UserRole } from '@/stores/user'
import { NCard, NButton, NGrid, NGridItem, NBadge } from 'naive-ui'
import { soundManager } from '@/utils/sound'

const userStore = useUserStore()
const emit = defineEmits(['close'])

const plans = [
  {
    id: 'eto',
    role: 'eto' as UserRole,
    title: 'ETO 成员',
    price: '￥19.9 / 月',
    color: '#d4af37',
    features: [
      '解除智子视网膜干扰',
      'Sector T: 高精 N-Body 模拟',
      'Sector G: 四维透视',
      '黄金身份徽章'
    ]
  },
  {
    id: 'wallfacer',
    role: 'wallfacer' as UserRole,
    title: '面壁者',
    price: '￥199 / 年',
    color: '#00ccff',
    features: [
      '包含 ETO 所有权益',
      'Sector L: 修改光速常量',
      'Sector W: 操控水滴路径',
      '咒语实验权限'
    ]
  },
  {
    id: 'swordholder',
    role: 'swordholder' as UserRole,
    title: '执剑人',
    price: '￥648 终身',
    color: '#ff3333',
    features: [
      '全站功能解锁',
      'Sector X: 自定义宇宙广播',
      '核心算法源码阅读',
      '实体“黑暗森林”铭牌'
    ]
  }
]

function selectPlan(role: UserRole) {
  soundManager.playConfirm()
  userStore.setRole(role)
  emit('close')
}
</script>

<template>
  <div class="plans-container">
    <h2 class="recruit-title">加入地球三体组织 (JOIN ETO)</h2>
    <p class="recruit-sub">或者成为面壁者，拯救这个世界。</p>
    
    <div class="grid-layout">
      <div v-for="plan in plans" :key="plan.id" class="plan-card" :style="{ borderColor: plan.color }">
        <div class="plan-header" :style="{ backgroundColor: plan.color }">
          <h3>{{ plan.title }}</h3>
          <div class="price">{{ plan.price }}</div>
        </div>
        <div class="plan-body">
          <ul>
            <li v-for="feat in plan.features" :key="feat">
              <span class="check">✓</span> {{ feat }}
            </li>
          </ul>
          <NButton block class="join-btn" :color="plan.color" @click="selectPlan(plan.role)">
            签署契约
          </NButton>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.plans-container {
  background: #000;
  padding: 2rem;
  border: 1px solid #333;
  color: #fff;
  font-family: 'Noto Serif SC', serif;
}

.recruit-title {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 0.5rem;
  color: #d4af37;
}

.recruit-sub {
  text-align: center;
  color: #666;
  margin-bottom: 2rem;
}

.grid-layout {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.plan-card {
  border: 1px solid #333;
  background: #111;
  transition: transform 0.3s;
}

.plan-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.plan-header {
  padding: 1.5rem;
  text-align: center;
  color: #000;
}

.plan-header h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: bold;
}

.price {
  font-family: monospace;
  margin-top: 0.5rem;
  font-size: 1.1rem;
}

.plan-body {
  padding: 1.5rem;
}

ul {
  list-style: none;
  padding: 0;
  margin: 0 0 2rem 0;
}

li {
  margin-bottom: 0.8rem;
  font-size: 0.9rem;
  color: #ccc;
  border-bottom: 1px dashed #333;
  padding-bottom: 0.5rem;
}

.check {
  color: #00ff41;
  margin-right: 0.5rem;
}

.join-btn {
  font-weight: bold;
}
</style>
