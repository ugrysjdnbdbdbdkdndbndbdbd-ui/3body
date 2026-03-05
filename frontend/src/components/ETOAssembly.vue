<script setup lang="ts">
/**
 * ETO Assembly (地球三体组织集会)
 * 包含：派系选择、审判日号通讯、组织纲领
 */
import { ref, computed } from 'vue'
import { useMessage } from 'naive-ui'

const message = useMessage()

// Factions
type Faction = 'ADVENTIST' | 'REDEMPTIONIST' | 'SURVIVOR'
const activeFaction = ref<Faction | null>(null)

const factions = [
  {
    id: 'ADVENTIST',
    name: '降临派',
    leader: '麦克·伊文斯',
    slogan: '消灭人类暴政，世界属于三体。',
    desc: '对人类文明彻底绝望，渴望主降临并通过强制手段改造地球。',
    color: '#ff4444'
  },
  {
    id: 'REDEMPTIONIST',
    name: '拯救派',
    leader: '申玉菲',
    slogan: '主在受难，我们要拯救主。',
    desc: '崇拜三体文明，致力于解决三体问题，帮助主脱离苦海。',
    color: '#4488ff'
  },
  {
    id: 'SURVIVOR',
    name: '幸存派',
    leader: '无名氏',
    slogan: '给子孙留一口饭吃。',
    desc: '出卖人类利益，只为在三体占领后为后代争取生存空间。',
    color: '#88ff88'
  }
]

// Chat/Logs
const chatLogs = ref([
  { sender: 'System', content: '连接至“审判日”号服务器...', type: 'info' },
  { sender: 'System', content: '身份验证通过。欢迎加入 ETO。', type: 'info' },
  { sender: 'Evans', content: '同志们，主的舰队已经启航。', type: 'msg' },
  { sender: 'Pan Han', content: '必须清除组织内的异端。拯救派不仅愚蠢，而且危险。', type: 'msg' },
])

const inputMsg = ref('')

function sendMsg() {
  if (!inputMsg.value.trim()) return
  if (!activeFaction.value) {
    message.error('请先选择您的派系立场')
    return
  }
  
  chatLogs.value.push({
    sender: 'You',
    content: inputMsg.value,
    type: 'msg'
  })
  
  // Simple Auto-reply
  setTimeout(() => {
    let reply = ''
    if (activeFaction.value === 'ADVENTIST') {
      reply = '主不在乎。但你的忠诚被记录了。'
    } else if (activeFaction.value === 'REDEMPTIONIST') {
      reply = '你计算过三体问题的数学模型吗？'
    } else {
      reply = '活下去才是最重要的。'
    }
    
    chatLogs.value.push({
      sender: 'Admin',
      content: reply,
      type: 'msg'
    })
  }, 1000)
  
  inputMsg.value = ''
}

function selectFaction(id: string) {
  activeFaction.value = id as Faction
  message.success(`您已加入 ${factions.find(f => f.id === id)?.name}`)
  chatLogs.value.push({
    sender: 'System',
    content: `用户更改立场为：${id}`,
    type: 'info'
  })
}

</script>

<template>
  <div class="eto-terminal">
    <div class="eto-header">
      <div class="eto-logo">
        <span class="star">★</span>
        <span class="star">★</span>
        <span class="star">★</span>
      </div>
      <h1>EARTH-TRISOLARIS ORGANIZATION</h1>
      <div class="subtitle">消灭人类暴政 · 世界属于三体</div>
    </div>

    <div class="eto-content">
      <!-- Faction Selection -->
      <div class="factions-grid">
        <div 
          v-for="f in factions" 
          :key="f.id"
          class="faction-card"
          :class="{ active: activeFaction === f.id }"
          :style="{ '--theme-color': f.color }"
          @click="selectFaction(f.id)"
        >
          <h3>{{ f.name }}</h3>
          <p class="leader">领袖: {{ f.leader }}</p>
          <p class="slogan">"{{ f.slogan }}"</p>
          <p class="desc">{{ f.desc }}</p>
        </div>
      </div>

      <!-- Chat Interface -->
      <div class="comm-panel">
        <div class="panel-header">
          <span>// JUDGMENT DAY COMM LINK</span>
          <span class="status online">ONLINE</span>
        </div>
        <div class="chat-window">
          <div 
            v-for="(log, i) in chatLogs" 
            :key="i" 
            class="chat-line"
            :class="log.type"
          >
            <span class="sender" v-if="log.sender">[{{ log.sender }}]:</span>
            <span class="content">{{ log.content }}</span>
          </div>
        </div>
        <div class="input-area">
          <input 
            v-model="inputMsg" 
            placeholder="输入指令或发言..." 
            @keyup.enter="sendMsg"
            :disabled="!activeFaction"
          />
          <button @click="sendMsg" :disabled="!activeFaction">SEND</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.eto-terminal {
  height: 100%;
  background: #111;
  color: #eee;
  font-family: 'Helvetica Neue', sans-serif;
  display: flex;
  flex-direction: column;
  padding: 1rem;
  box-sizing: border-box;
}

.eto-header {
  text-align: center;
  margin-bottom: 2rem;
  border-bottom: 1px solid #333;
  padding-bottom: 1rem;
}

.eto-logo {
  color: gold;
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}
.eto-logo .star { margin: 0 0.2rem; }

.eto-header h1 {
  margin: 0;
  font-weight: 300;
  letter-spacing: 4px;
  font-size: 1.8rem;
}

.subtitle {
  color: #666;
  margin-top: 0.5rem;
  font-size: 0.9rem;
  letter-spacing: 2px;
}

.eto-content {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  overflow: hidden;
}

.factions-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  overflow-y: auto;
}

.faction-card {
  background: #1a1a1a;
  border: 1px solid #333;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s;
  border-left: 4px solid #555;
}

.faction-card:hover {
  background: #222;
  transform: translateX(5px);
}

.faction-card.active {
  background: #252525;
  border-color: var(--theme-color);
  border-left-color: var(--theme-color);
  box-shadow: 0 0 15px rgba(0,0,0,0.5);
}

.faction-card h3 { margin: 0 0 0.5rem 0; color: #fff; }
.leader { font-size: 0.8rem; color: #888; margin-bottom: 0.5rem; }
.slogan { font-style: italic; color: var(--theme-color); margin-bottom: 0.5rem; }
.desc { font-size: 0.9rem; color: #aaa; line-height: 1.4; margin: 0; }

.comm-panel {
  display: flex;
  flex-direction: column;
  border: 1px solid #333;
  background: #000;
}

.panel-header {
  padding: 0.5rem 1rem;
  background: #222;
  border-bottom: 1px solid #333;
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #888;
}

.status.online { color: #0f0; }

.chat-window {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  font-family: monospace;
}

.chat-line { margin-bottom: 0.5rem; line-height: 1.4; }
.chat-line.info { color: #555; font-style: italic; }
.chat-line.msg { color: #ccc; }
.sender { color: gold; margin-right: 0.5rem; font-weight: bold; }

.input-area {
  display: flex;
  border-top: 1px solid #333;
}

.input-area input {
  flex: 1;
  background: #000;
  border: none;
  color: #fff;
  padding: 1rem;
  font-family: monospace;
  outline: none;
}

.input-area button {
  background: #333;
  color: #fff;
  border: none;
  padding: 0 1.5rem;
  cursor: pointer;
}

.input-area button:hover:not(:disabled) { background: #444; }
.input-area button:disabled { opacity: 0.5; cursor: not-allowed; }
</style>