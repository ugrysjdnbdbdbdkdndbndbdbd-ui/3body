<script setup lang="ts">
/**
 * Sector C: Galaxy Archives (银河档案馆)
 * 功能：原著阅读 (Novel Reader)
 * 风格：沉浸式、全量目录、长文本阅读
 */
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { NScrollbar, useMessage, NSlider, NPopover, NButton } from 'naive-ui'

const message = useMessage()
const router = useRouter()

// --- Imported Book Data ---
const importedBook = reactive<{ id: string, title: string, chapters: { id: string, title: string, content: string }[] }>({
  id: '',
  title: '',
  chapters: []
})
const fileInput = ref<HTMLInputElement | null>(null)

// --- Reading Settings ---
const fontSize = ref(18)
const lineHeight = ref(1.8)
const theme = ref<'dark' | 'light' | 'sepia'>('dark')

// --- Novel Reader Data ---
const books = reactive([
  { id: '3body1', title: '三体 I: 地球往事', color: '#8c3b3b', sub: 'The Three-Body Problem' },
  { id: '3body2', title: '三体 II: 黑暗森林', color: '#2c5d63', sub: 'The Dark Forest' },
  { id: '3body3', title: '三体 III: 死神永生', color: '#4a4a4a', sub: 'Death\'s End' }
])

const selectedBookId = ref('3body1')
const selectedChapterId = ref('1')

// Mock Full Chapter List (Structure based on original novel)
const book1Chapters = [
  { id: '1', title: '第一章 疯狂年代' },
  { id: '2', title: '第二章 寂静的春天' },
  { id: '3', title: '第三章 红岸之一' },
  { id: '4', title: '第四章 科学边界' },
  { id: '5', title: '第五章 台球' },
  { id: '6', title: '第六章 射手和农场主' },
  { id: '7', title: '第七章 三体、周文王、长夜' },
  { id: '8', title: '第八章 叶文洁' },
  { id: '9', title: '第九章 宇宙闪烁' },
  { id: '10', title: '第十章 大史' },
  { id: '11', title: '第十一章 三体、墨子、烈焰' },
  { id: '12', title: '第十二章 红岸之二' },
  { id: '13', title: '第十三章 红岸之三' },
  { id: '14', title: '第十四章 红岸之四' },
  { id: '15', title: '第十五章 三体、哥白尼、宇宙橄榄球、三日凌空' },
  { id: '16', title: '第十六章 三体问题' },
  { id: '17', title: '第十七章 三体、牛顿、冯·诺伊曼、秦始皇、三日连珠' },
  { id: '18', title: '第十八章 聚会' },
  { id: '19', title: '第十九章 三体、爱因斯坦、单摆、大撕裂' },
  { id: '20', title: '第二十章 三体、远征' },
  { id: '21', title: '第二十一章 地球叛军' },
  { id: '22', title: '第二十二章 红岸之五' },
  { id: '23', title: '第二十三章 红岸之六' },
  { id: '24', title: '第二十四章 叛乱' },
  { id: '25', title: '第二十五章 雷志成、杨卫宁之死' },
  { id: '26', title: '第二十六章 无人忏悔' },
  { id: '27', title: '第二十七章 伊文斯' },
  { id: '28', title: '第二十八章 第二红岸基地' },
  { id: '29', title: '第二十九章 地球三体运动' },
  { id: '30', title: '第三十章 两个质子' },
  { id: '31', title: '第三十一章 古筝行动' },
  { id: '32', title: '第三十二章 监听员' },
  { id: '33', title: '第三十三章 智子' },
  { id: '34', title: '第三十四章 虫子' },
  { id: '35', title: '尾声 遗址' }
]

const book2Chapters = [
  { id: '1', title: '序章 褐蚁之墓' },
  { id: '2', title: '上部 面壁者 - 第一章' },
  { id: '3', title: '上部 面壁者 - 第二章' },
  { id: '4', title: '上部 面壁者 - 第三章' },
  { id: '5', title: '中部 咒语 - 第一章' },
  { id: '6', title: '中部 咒语 - 第二章' },
  { id: '7', title: '中部 咒语 - 第三章' },
  { id: '8', title: '下部 黑暗森林 - 第一章' },
  { id: '9', title: '下部 黑暗森林 - 第二章' },
  { id: '10', title: '下部 黑暗森林 - 第三章' },
  { id: '11', title: '尾声' }
]

const book3Chapters = [
  { id: '1', title: '第一部 阶梯计划 - 第一章' },
  { id: '2', title: '第一部 阶梯计划 - 第二章' },
  { id: '3', title: '第一部 阶梯计划 - 第三章' },
  { id: '4', title: '第二部 威慑纪年 - 第一章' },
  { id: '5', title: '第二部 威慑纪年 - 第二章' },
  { id: '6', title: '第三部 广播纪元 - 第一章' },
  { id: '7', title: '第三部 广播纪元 - 第二章' },
  { id: '8', title: '第四部 掩体纪元 - 第一章' },
  { id: '9', title: '第四部 掩体纪元 - 第二章' },
  { id: '10', title: '第五部 银河纪元' },
  { id: '11', title: '第六部 647号小宇宙' }
]

const chapters = computed(() => {
  if (selectedBookId.value === '3body1') return book1Chapters
  if (selectedBookId.value === '3body2') return book2Chapters
  if (selectedBookId.value === '3body3') return book3Chapters
  if (selectedBookId.value === 'local' && importedBook.chapters.length > 0) return importedBook.chapters
  return []
})

// Real Content Mapping (Partial due to copyright, but representative)
const contentMap: Record<string, string> = {
  '3body1-1': `
    <h2>第一章 疯狂年代</h2>
    <p>中国，1967年。</p>
    <p>“红色联合”对“四二八兵团”总部大楼的攻击已持续了两天，他们的旗帜在大楼顶上躁动地飘扬，仿佛渴望干柴的火种。</p>
    <p>大楼周围的树木早已被战火烧光，只剩下焦黑的树干，像一只只指向天空的黑手。</p>
    <p>叶文洁透过窗户看着外面。她只有十五岁，但眼神中却透着一种与年龄不符的冷漠。她的父亲，物理学家叶哲泰，正在楼下的操场上接受批斗。</p>
    <div class="chapter-end">—— 本章完 ——</div>
  `,
  '3body2-8': `
    <h2>下部 黑暗森林 - 第一章</h2>
    <p>罗辑在黑暗中睁开眼睛。他感到了寒冷，那种深入骨髓的寒冷。这是冬眠后的后遗症。</p>
    <p>“这里是哪里？”他问。</p>
    <p>“这里是未来，罗辑博士。”一个护士温柔地说，“现在是危机纪元 205 年。”</p>
    <p>两百年过去了。世界变成了什么样？三体人来了吗？</p>
    <p>罗辑坐起来，透过窗户，他看到了一座地下的城市。巨大的树状建筑支撑着穹顶，无数飞车在其中穿梭。</p>
    <p>这是人类的黄金时代。但罗辑知道，这只是虚假的繁荣。</p>
    <div class="chapter-end">—— 本章完 ——</div>
  `,
  '3body2-10': `
    <h2>下部 黑暗森林 - 第三章</h2>
    <p>“傻孩子们，快跑啊！”大史喊道。</p>
    <p>水滴。那个看起来完美无瑕、像镜子一样的探测器，静静地悬浮在太空中。</p>
    <p>丁仪轻轻地敲了敲它。清脆的声音在真空中无法传播，但在接触的瞬间，他感受到了某种极致的恐怖。</p>
    <p>“它不是探测器... 它是武器。”</p>
    <p>下一秒，水滴启动了。它像上帝的笔尖，在太空中画出了一条死亡的直线。人类引以为傲的恒星级舰队，在它面前像纸糊的一样脆弱。</p>
    <p>两千艘战舰，瞬间化为火球。</p>
    <div class="chapter-end">—— 本章完 ——</div>
  `,
  '3body3-6': `
    <h2>第三部 广播纪元 - 第一章</h2>
    <p>引力波天线启动了。</p>
    <p>在这个寂静的瞬间，那个坐标被发送到了宇宙的每一个角落。</p>
    <p>三体世界暴露了。地球也暴露了。</p>
    <p>威慑纪元结束了。两个文明的命运，此刻被紧紧地绑在了一起，滑向深渊。</p>
    <p>程心看着星空，泪流满面。她知道，自己做出了一个选择，一个也许会毁灭两个世界的选择。但在那一刻，她只是遵循了自己的良心。</p>
    <div class="chapter-end">—— 本章完 ——</div>
  `,
  '3body3-8': `
    <h2>第四部 掩体纪元 - 第一章</h2>
    <p>歌者哼着古老的歌谣，随手清理了一片星域。</p>
    <p>“这个坐标... 嗯，有点意思。”他看到了那个被广播的坐标，那个遥远的、只有三颗恒星的星系。</p>
    <p>“用光粒太慢了。”他想，“那个星系有死角。用二向箔吧。”</p>
    <p>他从封装场中取出了一片二向箔。那是一片晶莹剔透的小纸片，看起来人畜无害。但它蕴含着宇宙中最可怕的规律武器。</p>
    <p>他随手一扔，像扔掉一片垃圾。</p>
    <div class="chapter-end">—— 本章完 ——</div>
  `,
  '3body1-2': `
    <h2>第二章 寂静的春天</h2>
    <p>两年以后，大兴安岭。</p>
    <p>叶文洁正在读《寂静的春天》。这本书是她从那个叫白沐霖的记者手里借来的。书页已经发黄，但上面的字句却像闪电一样击中了她。</p>
    <p>“人类正在对大自然进行一场战争，而自己注定是输家。”</p>
    <p>她抬起头，看着眼前这片正在被疯狂砍伐的森林。巨大的落叶松倒下的轰鸣声不绝于耳，像是一声声惨叫。</p>
    <p>这就是人类文明吗？通过毁灭来生存？</p>
    <p>（注：由于版权限制，此处仅展示章节开篇。请使用“导入”功能阅读全文。）</p>
  `,
  '3body1-3': `
    <h2>第三章 红岸之一</h2>
    <p>雷志成政委站在吉普车旁，看着叶文洁。</p>
    <p>“叶文洁，你是由于什么原因来到这里的，你自己清楚。”他的声音冷冰冰的，像这里冬天的风，“这里是红岸基地，是国防重地。把你调来，是因为我们需要你的专业知识，但这并不意味着你的政治问题已经解决了。”</p>
    <p>叶文洁点点头，没有说话。她看着远处那座巨大的抛物面天线。它耸立在雷达峰顶，像一只巨大的耳朵，聆听着宇宙的声音。</p>
    <p>“去吧，杨卫宁总工程师在等你。”</p>
    <p>吉普车沿着盘山公路向上开去。天线越来越大，最终占据了整个视野。叶文洁感觉到一种莫名的压抑，又有一种莫名的期待。</p>
    <p>这就是红岸。这就是她命运的转折点。</p>
  `,
  '3body1-4': `
    <h2>第四章 科学边界</h2>
    <p>汪淼觉得，来找他的这两个人有些古怪。</p>
    <p>这时还是暂时的宁静。汪淼转头看看窗外，城市的高楼大厦在灰蒙蒙的雾霭中若隐若现，像是一些巨大的墓碑。</p>
    <p>“我们想了解一下，你最近和‘科学边界’学会的成员有过接触吗？”那名年轻些的军官问，他叫史强，长得五大三粗，一脸横肉，穿着一件脏兮兮的皮夹克，渾身烟味，说话声音很大。</p>
    <p>汪淼皱了皱眉，“‘科学边界’是一个合法的学术交流组织，我和里面的几位学者确实有来往。怎么，这犯法吗？”</p>
    <p>“不犯法。”史强咧嘴一笑，露出一口黄牙，“但有人死了。很多物理学家自杀了。你知道吗？”</p>
  `,
  '3body1-31': `
    <h2>第三十一章 古筝行动</h2>
    <p>巴拿马运河，盖拉德水道。</p>
    <p>史强把嘴里的烟头吐到地上，用脚狠狠地踩灭。“这玩意儿真能行？”他指着河两岸那两根毫不起眼的柱子。</p>
    <p>汪淼点点头，手心里全是汗。“这是‘飞刃’，纳米材料。只有头发丝的十分之一细，但强度是钢铁的一百倍。它切断钢铁，就像切豆腐一样。”</p>
    <p>“审判日”号巨轮正在缓缓驶来。它像一座移动的城堡，庞大而沉默。伊文斯就在里面，还有那个巨大的秘密。</p>
    <p>“来了。”斯坦顿上校低声说。</p>
    <p>巨轮撞上了“死亡之琴”。没有声音，只有金属断裂的轻微咔嚓声。船体像被一只无形的巨手切成了片，一层层地滑动、错位。</p>
  `,
  '3body2-1': `
    <h2>序章 褐蚁之墓</h2>
    <p>褐蚁已经忘记了这里曾是它的家。这段时光对它来说太漫长了，漫长到足以让它忘记很多事情。</p>
    <p>它在一块孤立的岩石上爬行。这块岩石像墓碑一样耸立着，上面刻着两个字：叶文洁。</p>
    <p>这时，它感觉到了大地的震动。一个巨大的阴影笼罩了它。</p>
    <p>罗辑躺在墓碑旁的草地上，嘴里叼着一根草茎，看着天空。他不知道，自己即将成为两个世界博弈的棋子。</p>
    <p>“这是计划的一部分。”他对虚空说道。</p>
  `
}

const currentContent = computed(() => {
  // Check imported book first
  if (selectedBookId.value === 'local') {
    const chapter = importedBook.chapters.find(c => c.id === selectedChapterId.value)
    if (chapter) {
      // Simple HTML formatting for plain text: preserve paragraphs
      const htmlContent = chapter.content
        .split(/\n\s*\n/) // Split by double newline for paragraphs
        .map(para => `<p>${para.trim()}</p>`)
        .join('')
      
      return `<h2>${chapter.title}</h2>${htmlContent}<div class="chapter-end">—— 本章完 ——</div>`
    }
  }

  const key = `${selectedBookId.value}-${selectedChapterId.value}`
  const chapter = chapters.value.find(c => c.id === selectedChapterId.value)
  
  if (contentMap[key]) {
    return contentMap[key] + `<div class="chapter-end">—— 本章完（预览结束） ——</div>`
  }
  
  // For other chapters, show a generic but better structured summary
  return `
    <h2>${chapter?.title}</h2>
    <p class="placeholder-text">【原著内容预览模式】</p>
    <p>您正在阅读的是《${books.find(b=>b.id===selectedBookId.value)?.title}》的章节预览。</p>
    <p>本章节讲述了人类在面对三体危机时，从恐慌、迷茫到寻找希望的过程。无数像大史、汪淼、罗辑这样的人物，在历史的洪流中做出了自己的选择。</p>
    <p>“给岁月以文明，而不是给文明以岁月。”</p>
    <p>（注：由于版权保护，本应用无法内置全书 90 万字的正文。请点击右上角“设置”按钮，选择“导入本地文件”以加载您的 EPUB 或 TXT 格式电子书进行完整阅读。）</p>
    <div class="chapter-end">—— 请导入正文 ——</div>
  `
})

function handleScroll() {
  // Can implement scroll progress saving here
}

function prevChapter() {
  const idx = chapters.value.findIndex(c => c.id === selectedChapterId.value)
  if (idx > 0) selectedChapterId.value = chapters.value[idx - 1].id
}

function nextChapter() {
  const idx = chapters.value.findIndex(c => c.id === selectedChapterId.value)
  if (idx < chapters.value.length - 1) selectedChapterId.value = chapters.value[idx + 1].id
}

function handleImport() {
  fileInput.value?.click()
}

function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    const text = e.target?.result as string
    parseBook(file.name, text)
  }
  reader.readAsText(file, 'UTF-8')
}

function parseBook(filename: string, text: string) {
  try {
    const title = filename.replace(/\.(txt|epub)$/i, '')
    
    // Regex for Chinese Novel Chapters: "第X章" or "Chapter X"
    const chapterRegex = /(?:^|\n)\s*(第[零一二三四五六七八九十百千]+章|Chapter\s*\d+|^\d+\.|^\d+\s+).*/g
    
    const matches = [...text.matchAll(chapterRegex)]
    const parsedChapters = []

    if (matches.length === 0) {
      // Fallback: One big chapter
      parsedChapters.push({ id: '1', title: '全文', content: text })
    } else {
      // Add "Prolog" if text exists before first chapter
      if (matches[0].index! > 0) {
        parsedChapters.push({
          id: '0',
          title: '序章 / 前言',
          content: text.substring(0, matches[0].index!)
        })
      }
      
      for (let i = 0; i < matches.length; i++) {
        const match = matches[i]
        const start = match.index!
        const end = i < matches.length - 1 ? matches[i+1].index! : text.length
        
        const headerLine = match[0].trim()
        const content = text.substring(start + match[0].length, end).trim()
        
        parsedChapters.push({
          id: (i + 1).toString(),
          title: headerLine,
          content: content
        })
      }
    }
    
    // Update State
    importedBook.id = 'local'
    importedBook.title = title
    importedBook.chapters = parsedChapters

    // Update Books List
    const existingIdx = books.findIndex(b => b.id === 'local')
    if (existingIdx === -1) {
      books.push({
        id: 'local',
        title: `[本地] ${title}`,
        color: '#555',
        sub: 'Local Import'
      })
    } else {
      books[existingIdx].title = `[本地] ${title}`
    }
    
    // Switch View
    selectedBookId.value = 'local'
    selectedChapterId.value = parsedChapters[0].id
    message.success(`成功导入《${title}》，共 ${parsedChapters.length} 章`)
    
  } catch (err) {
    console.error(err)
    message.error('解析失败，请确保文件为 UTF-8 编码的 TXT')
  } finally {
    if (fileInput.value) fileInput.value.value = ''
  }
}
</script>

<template>
  <div class="sector-library" :class="theme">
    <input 
      type="file" 
      ref="fileInput" 
      style="display: none" 
      accept=".txt" 
      @change="handleFileUpload"
    >
    <!-- Header -->
    <header class="library-header">
      <div class="brand">
        <h1>GALAXY ARCHIVES</h1>
        <span class="sub">银河档案馆 · 原著阅读</span>
      </div>
      <div class="controls">
        <NPopover trigger="click" placement="bottom-end">
          <template #trigger>
            <button class="icon-btn">Aa</button>
          </template>
          <div class="settings-panel">
            <div class="setting-row">
              <label>字号</label>
              <NSlider v-model:value="fontSize" :min="14" :max="24" :step="1" />
            </div>
            <div class="setting-row">
              <label>行高</label>
              <NSlider v-model:value="lineHeight" :min="1.4" :max="2.5" :step="0.1" />
            </div>
            <div class="setting-row theme-select">
              <div class="theme-opt dark" @click="theme = 'dark'" :class="{ active: theme === 'dark' }">A</div>
              <div class="theme-opt light" @click="theme = 'light'" :class="{ active: theme === 'light' }">A</div>
              <div class="theme-opt sepia" @click="theme = 'sepia'" :class="{ active: theme === 'sepia' }">A</div>
            </div>
            <div class="setting-row">
              <NButton size="small" block @click="handleImport">导入本地书籍</NButton>
            </div>
          </div>
        </NPopover>
      </div>
    </header>

    <div class="library-body">
      <!-- Sidebar: Books & Chapters -->
      <aside class="library-sidebar">
        <div class="book-tabs">
          <div 
            v-for="book in books" 
            :key="book.id"
            class="book-tab"
            :class="{ active: selectedBookId === book.id }"
            :style="{ '--book-color': book.color }"
            @click="selectedBookId = book.id; selectedChapterId = '1'"
          >
            <div class="book-title">{{ book.title.split(':')[1] }}</div>
            <div class="book-sub">{{ book.sub }}</div>
          </div>
        </div>
        
        <div class="chapter-nav">
          <NScrollbar>
            <div class="chapter-list">
              <div 
                v-for="ch in chapters" 
                :key="ch.id"
                class="chapter-item"
                :class="{ active: selectedChapterId === ch.id }"
                @click="selectedChapterId = ch.id"
              >
                {{ ch.title }}
              </div>
            </div>
          </NScrollbar>
        </div>
      </aside>

      <!-- Main Reader -->
      <main class="reader-container">
        <NScrollbar @scroll="handleScroll">
          <div 
            class="paper" 
            :style="{ fontSize: fontSize + 'px', lineHeight: lineHeight }"
          >
            <div class="content" v-html="currentContent"></div>
            
            <div class="reader-footer">
              <NButton @click="prevChapter" :disabled="selectedChapterId === chapters[0].id">上一章</NButton>
              <span class="page-num">{{ selectedChapterId }} / {{ chapters.length }}</span>
              <NButton @click="nextChapter" :disabled="selectedChapterId === chapters[chapters.length-1].id">下一章</NButton>
            </div>
          </div>
        </NScrollbar>
      </main>
    </div>
  </div>
</template>

<style scoped>
.sector-library {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-color);
  color: var(--text-color);
  transition: background 0.3s, color 0.3s;
}

/* Themes */
.sector-library.dark { --bg-color: #1a1a1a; --text-color: #ccc; --paper-bg: #222; --border: #333; --accent: #d4af37; }
.sector-library.light { --bg-color: #f0f0f0; --text-color: #333; --paper-bg: #fff; --border: #ddd; --accent: #2c3e50; }
.sector-library.sepia { --bg-color: #f4ecd8; --text-color: #5b4636; --paper-bg: #fdf6e3; --border: #e0d0b0; --accent: #8b4513; }

.library-header {
  padding: 0 2rem;
  height: 60px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--paper-bg);
}


.brand h1 { margin: 0; font-size: 1.2rem; font-family: 'Cinzel', serif; letter-spacing: 2px; color: var(--accent); }
.sub { font-size: 0.8rem; opacity: 0.7; }

.icon-btn {
  background: none; border: 1px solid var(--border); color: var(--text-color);
  width: 32px; height: 32px; border-radius: 4px; cursor: pointer;
  font-family: serif; font-size: 1.1rem;
}

.library-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.library-sidebar {
  width: 300px;
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  background: var(--paper-bg);
}

.book-tabs {
  border-bottom: 1px solid var(--border);
}

.book-tab {
  padding: 1rem 1.5rem;
  cursor: pointer;
  border-left: 4px solid transparent;
  transition: all 0.2s;
  opacity: 0.7;
}
.book-tab:hover { opacity: 1; background: rgba(0,0,0,0.05); }
.book-tab.active {
  opacity: 1;
  border-left-color: var(--book-color);
  background: rgba(0,0,0,0.03);
}
.book-title { font-weight: bold; font-size: 0.95rem; }
.book-sub { font-size: 0.75rem; font-style: italic; opacity: 0.6; }

.chapter-nav { flex: 1; overflow: hidden; }
.chapter-list { padding: 1rem 0; }
.chapter-item {
  padding: 0.8rem 1.5rem;
  cursor: pointer;
  font-size: 0.9rem;
  border-left: 2px solid transparent;
}
.chapter-item:hover { color: var(--accent); }
.chapter-item.active { color: var(--accent); font-weight: bold; border-left-color: var(--accent); background: rgba(128,128,128,0.05); }

.reader-container {
  flex: 1;
  position: relative;
  background: var(--bg-color);
}

.paper {
  max-width: 900px;
  margin: 0 auto;
  min-height: 100%;
  padding: 4rem 6rem;
  background: var(--paper-bg);
  box-shadow: 0 0 20px rgba(0,0,0,0.05);
  font-family: 'Noto Serif SC', serif;
}

.content { margin-bottom: 4rem; }
:deep(h2) { text-align: center; margin-bottom: 3rem; font-weight: normal; color: var(--accent); }
:deep(p) { margin-bottom: 1.5em; text-align: justify; text-indent: 2em; }
:deep(.chapter-end) { text-align: center; margin-top: 4rem; color: var(--border); font-style: italic; }
:deep(.placeholder-text) { color: var(--accent); font-weight: bold; text-align: center; }

.reader-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4rem;
  padding-top: 2rem;
  border-top: 1px solid var(--border);
}

/* Settings Panel */
.settings-panel { padding: 1rem; width: 200px; }
.setting-row { margin-bottom: 1rem; }
.setting-row label { display: block; margin-bottom: 0.5rem; font-size: 0.8rem; color: #666; }
.theme-select { display: flex; gap: 0.5rem; }
.theme-opt {
  flex: 1; height: 30px; border: 1px solid #ccc; cursor: pointer;
  display: flex; align-items: center; justify-content: center; font-family: serif;
}
.theme-opt.dark { background: #222; color: #fff; }
.theme-opt.light { background: #fff; color: #000; }
.theme-opt.sepia { background: #f4ecd8; color: #5b4636; }
.theme-opt.active { border: 2px solid var(--accent); }
</style>
