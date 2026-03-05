<script setup lang="ts">
/**
 * 宇宙留言簿 - 弹幕式宇宙级留言
 * 用户留言经智子审核（无乱码、有意义、符合三体意象）后发布；满屏弹幕展示。
 */
import { ref, onMounted, onUnmounted } from 'vue'
import { NInput, NButton, useMessage } from 'naive-ui'

const message = useMessage()

// 预埋弹幕：三体经典语录 + UGC 风格（大量，供轮回循环）
const PRESET_BULLETS = [
  '给岁月以文明，给时光以生命。',
  '不要回答！不要回答！！不要回答！！！',
  '我送给你一颗星星。',
  '藏好自己，做好清理。',
  '失去人性，失去很多；失去兽性，失去一切。',
  '我们都是阴沟里的虫子，但总还是得有人仰望星空。',
  '宇宙不是童话。',
  '黑暗森林里，他人即地狱。',
  '主不在乎。',
  '水滴是末日。',
  '二向箔来了，快跑啊',
  '286.5 光年外，有一份礼物。',
  '程心，我们一起去 DX3906 吧',
  '面壁者，你的破壁人来了。',
  '执剑人握着的，是两个世界的命运。',
  '阶梯计划：送一颗大脑到星空。',
  '智子锁死了地球的科技，但锁不住思想。',
  '红岸的电磁波，第一次向宇宙呐喊。',
  '曲率驱动，光速是底线。',
  '小宇宙里，可以留下五公斤。',
  '—— 来自 4.22 光年外的凝视',
  '今晚的星空真好看，像罗辑的咒语',
  '三体人：不要脱水，等恒纪元',
  'ETO 路过，主会记得你的虔诚',
  '在时间尽头，仍有光',
  '观测者 1379 号：不要回答',
  '云天明用三个童话，写尽了人类的命运',
  '程心选择了人性，也选择了结局',
  '关一帆说：我们度过了幸福的一生',
  '死神永生。',
  '宇宙很大，生活更大。',
  '生存是文明的第一需要。',
  '文明不断增长和扩张，但宇宙中的物质总量保持不变。',
  '猜疑链。',
  '技术爆炸。',
  '叶文洁：我点燃了火，却控制不了它。',
  '罗辑的咒语，验证了黑暗森林。',
  '大刘yyds',
  '三体一刷打卡',
  '二向箔降维打击太绝了',
  '水滴撞击舰队那一章我看了五遍',
  '智子：你们是虫子。',
  '罗辑：我才是虫子，会思考的虫子。',
  '庄颜，我的白月光',
  '程心接剑的那一刻，整个人类都松了口气',
  '维德：失去人性失去很多，失去兽性失去一切。',
  '阶梯计划送出去的是云天明的大脑',
  '三个童话里藏着曲率驱动的秘密',
  '黑域是安全声明',
  '归零者广播：把质量还回宇宙',
  '647 号小宇宙，程心留下了五公斤',
  '宇宙重启，我们都在奇点里',
  '红岸基地，叶文洁按下了发射键',
  '不要回答。不要回答。',
  '三体游戏里三日凌空脱水',
  '古筝计划，审判日号',
  '面壁者弗雷德里克·泰勒',
  '面壁者雷迪亚兹，摇篮计划',
  '面壁者希恩斯，思想钢印',
  '破壁人山杉惠子',
  '罗辑的雪地工程',
  '执剑人 54 年，罗辑守住了两个世界',
  '程心接过剑，十五分钟后水滴攻击',
  '光速飞船派与地球派的抉择',
  '星环城，维德的最后一搏',
  '程心再次选择了人性',
  '艾 AA：我们去看那颗星星吧',
  'DX3906，云天明送的礼物',
  '高 Way 上的低光速区',
  '蓝星和灰星',
  '云天明讲的三个童话',
  '针眼画师，把秘密藏进画里',
  '露珠公主与深水王子',
  '无故事王国',
  '程心与关一帆在 647 小宇宙',
  '小宇宙里可以留下记忆体',
  '回归运动，质量守恒',
  '把质量还回大宇宙',
  '死神永生，宇宙永生',
  '时间开始了吗？时间还没有开始。',
  '宇宙的尽头是诗',
  '读三体第三遍，还是哭',
  '给岁月以文明',
  '给时光以生命',
  '给文明以岁月',
  '给生命以时光',
  '罗辑说，我面壁去了',
  '智子：我可以看到你们每一个人',
  '智子：但主不在乎',
  '三体人思维透明，不会说谎',
  '地球人思维不透明，会隐藏',
  '威慑纪元，脆弱的和平',
  '广播纪元，坐标暴露',
  '掩体纪元，躲在水星背后',
  '银河纪元，人类走向深空',
  '程心冬眠了那么多次',
  '每一次醒来都是新世界',
  '艾 AA 一直陪着她',
  '关一帆在蓝星等她',
  '云天明在 286 光年外',
  '三体人飞向半人马座',
  '地球人飞向星辰',
  '宇宙的尺度，生命的尺度',
  '从红岸到归零，从叶文洁到程心',
  '这是我们的故事',
  '也是宇宙的故事',
  '—— 一名读者',
  '—— 来自地球的问候',
  '—— 不要回答',
  '—— 藏好自己',
  '—— 主不在乎',
  '—— 死神永生',
  '—— 给岁月以文明',
  '—— 我送给你一颗星星',
  '—— 那我们就去那里吧',
  '—— 我们度过了幸福的一生',
  '—— 宇宙很大，生活更大',
  '—— 在时间尽头，仍有光',
  '—— 把质量还回宇宙',
  '—— 647 号小宇宙',
  '—— 五公斤',
  '—— 奇点',
  '—— 重启',
  '—— 三体',
  '—— 刘慈欣',
  '—— 谢谢大刘',
  '—— 谢谢三体',
  '—— 谢谢这个宇宙',
  // 三体景点语录
  '红岸：叶文洁向太阳举起天线，人类第一次对宇宙说话。',
  '红岸的落日把天线染成金色，像一根伸向天空的手指。',
  '雷达峰上，她按下了改变两个文明的键。',
  '水滴：完美。无瑕。死神。',
  '水滴来了，像一滴圣母的眼泪。',
  '两千艘战舰，像被点燃的蜡烛，在太空中熄灭。',
  '水滴穿过舰队，像子弹穿过奶酪。',
  '二向箔：一张小纸片，一个宇宙的句号。',
  '太阳系被压成一幅画，梵高的星空成了真的。',
  '程心看见星环城在二维化中变成一幅绝美的画。',
  '面壁计划：一个人对全世界的欺骗。',
  '罗辑坐在杨冬墓前，对着一颗星星念咒语。',
  '雪地工程：用核弹在太阳系边缘写下一行字。',
  '古筝计划：审判日号在巴拿马运河上被切成片。',
  '飞刃掠过，巨轮像积木一样散开。',
  '三体游戏：三日凌空，脱水，乱纪元。',
  '秦始皇的人列计算机，在沙漠里算着三体。',
  '恒纪元来了，他们浸泡复苏，仰望三个太阳。',
  '执剑人：一只手握着两个世界的生死。',
  '罗辑在引力波发射器前，守了五十四年。',
  '程心接过剑，十五分钟。然后水滴来了。',
  '星环城：维德说，失去兽性，失去一切。',
  '曲率引擎的尾迹，是黑域，是安全声明。',
  '程心说，停止。维德放下了枪。',
  'DX3906：云天明送的星星，程心和艾 AA 去了。',
  '蓝星，灰星，死线。关一帆在时间之外等她。',
  '高 Way 上的低光速区，时间慢得像糖浆。',
  '647 号小宇宙：程心与关一帆度过了幸福的一生。',
  '小宇宙里可以留下五公斤。她留下了生态球。',
  '归零者：把质量还回大宇宙，宇宙才能重启。',
  '程心留下五公斤，把门关上。大宇宙在门外。',
  '时间开始了吗？程心问。时间还没有开始。关一帆说。',
  '智子：我可以看到你们每一个人。但主不在乎。',
  '智子倒茶，说，宇宙很大，生活更大。',
  '阶梯计划：送一颗大脑到三体舰队。云天明。',
  '三个童话：针眼画师、露珠公主、无故事王国。',
  '云天明的童话里，藏着曲率驱动的秘密。',
  '无故事王国，是最安全的地方。',
  '针眼画师把秘密画进画里，只有程心能读。',
  '红岸遗址：荒草、铁塔、和一段被遗忘的罪。',
  '杨冬的墓前，罗辑对星星说，我要对三体世界说话。',
  '伊甸园里，罗辑和庄颜度过了短暂的梦。',
  '威慑纪元：和平建立在 mutually assured destruction 上。',
  '广播纪元：罗辑的咒语成真，坐标暴露。',
  '掩体纪元：人类躲在水星背后，等二向箔。',
  '银河纪元：程心醒来，人类已在光速飞船里。',
  // 文学诗意描述
  '星空在头顶展开，像一块缀满钻石的黑丝绒。',
  '光年不是距离，是时间。我们看见的星，是它的过去。',
  '宇宙不是童话。但总有人，在写童话。',
  '在时间尽头，仍有光。仍有质量。仍有记忆。',
  '死神永生。不是死神不会死，是死亡本身永恒。',
  '给岁月以文明，不是给文明以岁月。',
  '我们都是阴沟里的虫子，但总还是得有人仰望星空。',
  '她点燃了火，却控制不了它。叶文洁。',
  '主不在乎。三个字，写尽了神性与冷漠。',
  '黑暗森林里，每一个文明都是带枪的猎人。',
  '技术爆炸：虫子会变成神，在一夜之间。',
  '猜疑链：我们无法知道，他们是否知道我们不知道。',
  '生存是文明的第一需要。文明不断增长，宇宙物质总量不变。',
  '失去人性，失去很多；失去兽性，失去一切。维德。',
  '我才是虫子。会思考的虫子。罗辑。',
  '藏好自己，做好清理。宇宙生存法则。',
  '曲率驱动：光速是底线。再慢，就是死。',
  '黑域是安全声明。我们慢下来了，我们无害。',
  '二向箔是慈悲。比光粒温柔。给你时间变成画。',
  '太阳系变成一幅画。梵高的星空，成了预言。',
  '小宇宙里可以留下五公斤。程心留下了生态球和记忆。',
  '把质量还回大宇宙。否则，宇宙无法重启。',
  '时间还没有开始。在奇点之前，没有之前。',
  '我们度过了幸福的一生。关一帆对程心说。',
  '宇宙很大，生活更大。智子说。',
  '我送给你一颗星星。云天明对程心说。',
  '那我们就去那里吧。艾 AA 说。DX3906。',
  '286.5 光年外，有一份礼物。',
  '从红岸到归零，从叶文洁到程心。一个文明的弧线。',
  '每一次醒来都是新世界。程心冬眠了那么多次。',
  '执剑人握着的，是两个世界的命运。',
  '面壁者，你的破壁人来了。',
  '阶梯计划：送一颗大脑到星空。最浪漫的礼物。',
  '智子锁死了地球的科技，但锁不住思想。',
  '红岸的电磁波，第一次向宇宙呐喊。不要回答。',
  '宇宙的尺度，生命的尺度。我们只是瞬间。',
  '这是我们的故事。也是宇宙的故事。',
  '在时间尽头，仍有光。',
]

interface BulletItem {
  id: number
  text: string
  lane: number
  delay: number
  duration: number
}

const bullets = ref<BulletItem[]>([])
const inputText = ref('')
const submitting = ref(false)
const auditResult = ref<{ ok: boolean; reason?: string } | null>(null)
let bulletId = 0
const LANE_COUNT = 12
const DEFAULT_DURATION = 20

// 每条轨道下一次可发射时间（秒），用于错开同轨弹幕、避免互相遮挡
let laneFreeAt: number[] = Array(LANE_COUNT).fill(0)

function addBullet(text: string, options?: { lane?: number; delay?: number; duration?: number }) {
  const now = Date.now() / 1000
  let lane: number
  let delay: number
  if (options?.lane !== undefined && options?.delay !== undefined) {
    lane = options.lane
    delay = options.delay
  } else {
    // 选当前最早空闲的轨道，并让 delay 保证不压住前一条
    let minT = laneFreeAt[0]
    lane = 0
    for (let i = 1; i < LANE_COUNT; i++) {
      if (laneFreeAt[i] < minT) {
        minT = laneFreeAt[i]
        lane = i
      }
    }
    delay = Math.max(0, minT - now)
  }
  const duration = options?.duration ?? DEFAULT_DURATION + (Math.random() * 4 - 2)
  laneFreeAt[lane] = now + delay + duration

  bullets.value.push({
    id: ++bulletId,
    text: text.trim(),
    lane,
    delay,
    duration,
  })
}

function removeBullet(id: number) {
  bullets.value = bullets.value.filter((b) => b.id !== id)
}

/** 智子审核：无乱码、有意义、符合三体文学意象 */
function sophonAudit(text: string): { ok: boolean; reason?: string } {
  const t = text.trim()
  if (t.length < 2) return { ok: false, reason: '留言过短，至少 2 个字符。' }
  if (t.length > 80) return { ok: false, reason: '留言过长，最多 80 个字符。' }
  // 乱码检测：要求以中文、英文、数字、常见标点为主
  const validChar = /[\u4e00-\u9fa5a-zA-Z0-9\s，。！？、；：""''（）《》—…—·～]/
  const chars = [...t]
  const validCount = chars.filter((c) => validChar.test(c)).length
  if (validCount < t.length * 0.7) return { ok: false, reason: '智子判定：含有乱码或非法字符，不予通过。' }
  // 无意义：纯重复、纯数字、纯符号
  if (/^[\s\d，。、]+$/.test(t)) return { ok: false, reason: '智子判定：内容无意义。' }
  const same = new Set(chars).size
  if (t.length >= 6 && same <= 2) return { ok: false, reason: '智子判定：重复字符过多，请重新书写。' }
  // 三体意象加分（可选）：包含相关词更容易过；不强制
  const themeWords = ['星', '光', '宇宙', '黑暗', '文明', '时间', '岁月', '生命', '人类', '三体', '地球', '星空', '水滴', '二向箔', '面壁', '执剑', '程心', '罗辑', '云天明', '智子', '不要回答', '藏好', '主', '童话', '光年', '维', '曲率', '死神', '永生']
  const hasTheme = themeWords.some((w) => t.includes(w))
  if (!hasTheme && t.length > 20) {
    // 较长且无任何意象时，放宽：只要不是垃圾即可
    if (/^[a-zA-Z\s]+$/.test(t) && t.length > 40) return { ok: false, reason: '智子建议：可尝试加入一点宇宙或文明的意象，更易通过。' }
  }
  return { ok: true }
}

function submitBullet() {
  const t = inputText.value.trim()
  if (!t) {
    message.warning('请输入留言内容。')
    return
  }
  auditResult.value = sophonAudit(t)
  if (!auditResult.value.ok) {
    message.error(auditResult.value.reason ?? '智子未通过审核。')
    return
  }
  submitting.value = true
  addBullet(t)
  inputText.value = ''
  auditResult.value = null
  message.success('已发布至宇宙留言簿。智子已将你的声音送往深空。')
  submitting.value = false
}

/** 轮回循环：从预埋池按序取出并再次发射，形成无限循环弹幕 */
let presetIndex = 0
let loopTimer: ReturnType<typeof setInterval> | null = null
const LOOP_INTERVAL_MS = 11000
const BATCH_SIZE = 8

function emitPresetBatch() {
  for (let i = 0; i < BATCH_SIZE; i++) {
    const text = PRESET_BULLETS[presetIndex % PRESET_BULLETS.length]
    presetIndex++
    addBullet(text)
  }
}

function initPresetBullets() {
  const shuffled = [...PRESET_BULLETS].sort(() => Math.random() - 0.5)
  shuffled.forEach((text) => addBullet(text))
  presetIndex = shuffled.length
}

// 宇宙星海背景：随机星点
const stars = ref<Array<{ x: number; y: number; size: number; opacity: number; delay: number }>>([])

function initStars() {
  const list: Array<{ x: number; y: number; size: number; opacity: number; delay: number }> = []
  for (let i = 0; i < 180; i++) {
    list.push({
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 1.8 + 0.4,
      opacity: Math.random() * 0.55 + 0.25,
      delay: Math.random() * 4,
    })
  }
  stars.value = list
}

onMounted(() => {
  initStars()
  initPresetBullets()
  loopTimer = setInterval(emitPresetBatch, LOOP_INTERVAL_MS)
})

onUnmounted(() => {
  if (loopTimer) {
    clearInterval(loopTimer)
    loopTimer = null
  }
})
</script>

<template>
  <div class="cosmic-guestbook">
    <header class="guestbook-header">
      <h1 class="guestbook-title">宇宙留言簿</h1>
      <p class="guestbook-sub">COSMIC GUESTBOOK · 智子审核 · 你的留言将穿越星海</p>
    </header>

    <div class="bullet-stage">
      <!-- 群星背景 -->
      <div class="starfield-layer" aria-hidden="true">
        <div
          v-for="(s, i) in stars"
          :key="i"
          class="star-dot"
          :style="{
            left: s.x + '%',
            top: s.y + '%',
            width: s.size + 'px',
            height: s.size + 'px',
            opacity: s.opacity,
            animationDelay: s.delay + 's',
          }"
        />
      </div>
      <div class="bullet-stage-bg" aria-hidden="true"></div>
      <div
        v-for="b in bullets"
        :key="b.id"
        class="bullet meteor"
        :class="`lane-${b.lane}`"
        :style="{
          '--lane': b.lane,
          '--delay': `${b.delay}s`,
          '--duration': `${b.duration}s`,
        }"
        @animationend="removeBullet(b.id)"
      >
        <span class="meteor-tail" aria-hidden="true"></span>
        <span class="meteor-head">
          <span class="bullet-text">{{ b.text }}</span>
        </span>
      </div>
    </div>

    <div class="input-bar">
      <div class="input-wrap">
        <NInput
          v-model:value="inputText"
          type="text"
          placeholder="写下你的宇宙级留言（2～80 字，经智子审核后发布）"
          maxlength="80"
          show-count
          clearable
          :disabled="submitting"
          @keyup.enter="submitBullet"
        />
        <NButton type="primary" ghost :loading="submitting" @click="submitBullet">
          发布
        </NButton>
      </div>
      <p class="input-hint">智子将审核：无乱码、有意义、符合三体文学意象。通过后弹幕飞向深空。</p>
    </div>
  </div>
</template>

<style scoped>
.cosmic-guestbook {
  min-height: 100%;
  background: #030308;
  color: #e0e0f0;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.guestbook-header {
  padding: 1rem 2rem;
  border-bottom: 1px solid rgba(100, 100, 180, 0.2);
  background: rgba(10, 10, 25, 0.85);
  flex-shrink: 0;
  z-index: 10;
}

.guestbook-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  letter-spacing: 0.15em;
  color: #c8d0ff;
}

.guestbook-sub {
  margin: 0.35rem 0 0;
  font-size: 0.8rem;
  color: rgba(180, 190, 220, 0.8);
  letter-spacing: 0.08em;
}

.bullet-stage {
  flex: 1;
  position: relative;
  min-height: 320px;
  overflow: hidden;
}

/* 宇宙星海背景 */
.starfield-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.star-dot {
  position: absolute;
  border-radius: 50%;
  background: #fff;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 6px rgba(255, 255, 255, 0.5), 0 0 12px rgba(200, 220, 255, 0.2);
  animation: star-twinkle 4s ease-in-out infinite;
}

@keyframes star-twinkle {
  0%, 100% { opacity: 0.45; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 1; transform: translate(-50%, -50%) scale(1.25); }
}

.bullet-stage-bg {
  position: absolute;
  inset: 0;
  z-index: 1;
  background:
    radial-gradient(ellipse 100% 50% at 50% 50%, rgba(40, 35, 80, 0.15), transparent 65%),
    radial-gradient(1px 1px at 15% 20%, rgba(255,255,255,0.2), transparent),
    radial-gradient(1px 1px at 85% 30%, rgba(255,255,255,0.15), transparent),
    radial-gradient(1px 1px at 50% 80%, rgba(255,255,255,0.12), transparent);
  pointer-events: none;
}

/* 流星弹幕：头部亮、尾迹渐变透明、轻微倾斜 */
.bullet.meteor {
  position: absolute;
  z-index: 3;
  top: calc(3% + (var(--lane) * 7.2%));
  left: 100%;
  display: inline-flex;
  align-items: center;
  white-space: nowrap;
  transform: translateX(0) skewX(-8deg);
  animation: bullet-fly linear forwards;
  animation-duration: var(--duration);
  animation-delay: var(--delay);
  pointer-events: none;
  will-change: transform;
  filter: drop-shadow(0 0 6px rgba(180, 200, 255, 0.35));
}

.meteor-tail {
  display: block;
  width: 72px;
  height: 2px;
  margin-right: -2px;
  background: linear-gradient(
    to right,
    transparent 0%,
    rgba(160, 180, 255, 0.25) 25%,
    rgba(200, 215, 255, 0.5) 60%,
    rgba(220, 230, 255, 0.7) 85%,
    rgba(255, 255, 255, 0.85) 100%
  );
  border-radius: 1px;
  flex-shrink: 0;
}

.meteor-head {
  padding: 0.22rem 0.65rem;
  border-radius: 4px;
  background: linear-gradient(
    135deg,
    rgba(50, 55, 90, 0.9) 0%,
    rgba(35, 40, 75, 0.92) 50%,
    rgba(25, 28, 55, 0.95) 100%
  );
  border: 1px solid rgba(140, 160, 255, 0.35);
  color: rgba(235, 240, 255, 0.98);
  font-size: 0.86rem;
  letter-spacing: 0.02em;
  box-shadow:
    0 0 14px rgba(120, 140, 255, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.bullet-text {
  text-shadow: 0 0 10px rgba(200, 210, 255, 0.4);
}

@keyframes bullet-fly {
  0% {
    transform: translateX(0) skewX(-8deg);
    opacity: 0.85;
  }
  2% {
    opacity: 1;
  }
  98% {
    opacity: 1;
  }
  100% {
    transform: translateX(calc(-100vw - 100%)) skewX(-8deg);
    opacity: 0.85;
  }
}

.input-bar {
  padding: 1rem 2rem 1.5rem;
  background: rgba(8, 8, 20, 0.92);
  border-top: 1px solid rgba(100, 100, 180, 0.2);
  flex-shrink: 0;
  z-index: 10;
}

.input-wrap {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  max-width: 720px;
  margin: 0 auto;
}

.input-wrap :deep(.n-input) {
  flex: 1;
}

.input-hint {
  margin: 0.5rem 0 0;
  font-size: 0.75rem;
  color: rgba(140, 150, 190, 0.8);
  text-align: center;
  max-width: 720px;
  margin-left: auto;
  margin-right: auto;
}
</style>
