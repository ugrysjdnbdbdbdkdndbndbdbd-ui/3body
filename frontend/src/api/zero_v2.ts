import { invokeLlmGateway } from '@/api/llm_gateway'
import { tickUniverse } from '@/sim/zeroDarkForest'
import type { CivilizationAgent, CosmicEpitaph, HiddenStrategy } from '@/types/zero_v2'

export interface WallbreakerAnalysis {
  inferred: HiddenStrategy
  delta: number
  verdict: 'APPROVED' | 'REJECTED'
  reason: string
}

export async function analyzeWallfacerDirective(directive: string): Promise<WallbreakerAnalysis> {
  return invokeLlmGateway<WallbreakerAnalysis>({
    task: 'wallbreaker.analyze',
    payload: { directive },
    mock: () => {
      const t = directive.toLowerCase()
      const packs = [
        {
          inferred: 'ESCAPISM' as const,
          delta: 18,
          words: ['深空', '舰队', '逃亡', '冬眠', '星际移民'],
          reason: '资源倾向远航与长期生存链，疑似逃亡主义。',
        },
        {
          inferred: 'MUTUAL_DESTRUCTION' as const,
          delta: 22,
          words: ['引爆', '太阳', '坠落', '核', '广播坐标'],
          reason: '指令包含不可逆毁伤词汇，疑似同归于尽威慑。',
        },
        {
          inferred: 'DISGUISE' as const,
          delta: 10,
          words: ['微表情', '教育', '粮食', '基础设施', '心理学'],
          reason: '表层温和但存在伪装信号，疑似策略遮蔽。',
        },
      ]
      const matched = packs
        .map((p) => ({ p, hit: p.words.some((w) => t.includes(w)) }))
        .filter((x) => x.hit)
        .sort((a, b) => b.p.delta - a.p.delta)[0]
      if (!matched) {
        return {
          inferred: 'DISGUISE',
          delta: 6,
          verdict: 'APPROVED',
          reason: '指令噪声较高，暂未锁定核心战略链路。',
        }
      }
      const heavy = /(全球|全部|30%|50%|70%|100%)/.test(t)
      return {
        inferred: matched.p.inferred,
        delta: matched.p.delta + (heavy ? 8 : 0),
        verdict: heavy ? 'REJECTED' : 'APPROVED',
        reason: heavy ? `${matched.p.reason} 但预算波动超阈值，暂不批准。` : `${matched.p.reason} 当前仍允许试探性执行。`,
      }
    },
  })
}

export async function encodeSecretAsFairytale(secret: string): Promise<string> {
  return invokeLlmGateway<string>({
    task: 'yun-tianming.encode',
    payload: { secret },
    mock: () => {
      const lines = secret
        .split(/[。！？\n]/)
        .map((s) => s.trim())
        .filter(Boolean)
      const body = lines.map((line, idx) => `第${idx + 1}幕：画师把“${line}”藏进了会吞光的雪。`).join('\n')
      return `《国王的新画师·变体》\n在一座被真空包裹的王国，所有命令只能以寓言传递。\n${body}\n结尾：谁先读懂童话，谁先暴露坐标。`
    },
  })
}

export async function decodeFairytaleSimilarity(original: string, guess: string): Promise<number> {
  return invokeLlmGateway<number>({
    task: 'yun-tianming.decode',
    payload: { original, guess },
    mock: () => {
      const tokens = Array.from(new Set(original.replace(/[^\u4e00-\u9fa5a-zA-Z0-9]/g, '').split('')))
      if (!tokens.length) return 0
      const hit = tokens.filter((t) => guess.includes(t)).length
      return Math.min(100, Math.round((hit / tokens.length) * 100))
    },
  })
}

export async function injectMentalSealText(source: string, theme: string): Promise<string> {
  return invokeLlmGateway<string>({
    task: 'mental-seal.inject',
    payload: { source, theme },
    mock: () => {
      const clauses = source.split('，')
      if (clauses.length < 2) return `${source} 但传感器记录到一种不应出现的气味，人群本能后退。`
      return clauses
        .map((part, idx) => (idx === clauses.length - 1 ? `${part}。` : `${part}，像有人在耳后轻声提醒：${theme}。`))
        .join('')
    },
  })
}

export interface DarkForestTickResult {
  nextEpoch: number
  agents: CivilizationAgent[]
  epitaphs: CosmicEpitaph[]
}

export async function tickDarkForestWorld(
  agents: CivilizationAgent[],
  currentEpoch: number,
  epochStep = 100,
): Promise<DarkForestTickResult> {
  return invokeLlmGateway<DarkForestTickResult>({
    task: 'dark-forest.tick',
    payload: { agents, currentEpoch, epochStep },
    mock: () => {
      const nextEpoch = currentEpoch + epochStep
      const ret = tickUniverse(agents, nextEpoch)
      return {
        nextEpoch,
        agents: ret.agents,
        epitaphs: ret.epitaphs,
      }
    },
  })
}
