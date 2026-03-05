/**
 * 3Body X 集中常量（PRD：拒绝硬编码）
 * 设计语言、API 路径、错误文案、超时等
 */

/** Dark Forest 设计语言 - 与 PRD 一致 */
export const DESIGN = {
  /** 深空黑，背景主色 */
  VOID: '#050505',
  /** 切伦科夫蓝，科技/高亮 */
  SOPHONE: '#00FFFF',
  /** 红岸红，危险/警告 */
  RED_COAST: '#FF3333',
  /** 零点计划：智子屏显绿，审计终端感 */
  SOPHON_TERMINAL: '#00FF41',
  /** 零点计划：逻辑崩溃红 */
  LOGIC_COLLAPSE: '#FF0000',
  /** 零点计划：深空黑背景 */
  ZERO_VOID: '#001A00',
  /** 水滴银，强调文字 */
  DROPLET: '#C0C0C0',
} as const

/** 宇宙公理（零点计划宪章，与 docs/Project-Zero-Axioms.md 一致） */
export const UNIVERSE_AXIOMS = [
  '生存是文明的第一需要。',
  '文明不断增长和扩张，但宇宙中的物质总量保持不变。',
  '猜疑链与技术爆炸。',
  '光速恒定与维度的不可逆坍缩。',
] as const

/**
 * API 基址。开发时用 Vite proxy 可留空；静态部署或 405 时设 VITE_API_BASE=http://127.0.0.1:8000
 */
export const API_BASE = (import.meta.env.VITE_API_BASE as string)?.trim() ?? ''

/** 拼出完整 API URL，避免相对路径导致 405 */
export function apiUrl(path: string): string {
  if (!path.startsWith('/')) path = '/' + path
  return API_BASE ? `${API_BASE.replace(/\/$/, '')}${path}` : path
}

/** API 路径前缀 */
export const API = {
  CHAT_STREAM: '/api/chat/stream',
  CHAT: '/api/chat',
  /** 人物志对话：以该人物口吻流式回答 */
  CHAT_FIGURE: '/api/chat/figure',
  UNIVERSE_METRICS: '/api/universe/metrics',
  CHRONICLE_EVENTS: '/api/chronicle/events',
  CHRONICLE_ERAS: '/api/chronicle/eras',
  /** 三体百科（JSON 源） */
  CHRONICLE_ENCYCLOPEDIA: '/api/chronicle/encyclopedia',
  /** 三体外传（同人/COO 续写与细节展开） */
  CHRONICLE_APOCRYPHA: '/api/chronicle/apocrypha',
  /** 零点计划：观测节点，互动达标则坍缩 */
  CHRONICLE_EVENT_INTERACT: (id: number) => `/api/chronicle/events/${id}/interact`,
  GALLERY_ITEMS: '/api/gallery/items',
  /** 零点计划：智子审计文明碎片 */
  SOPHON_AUDIT: '/api/sophon/audit',
  FIGURES_LIST: '/api/figures/list',
  FIGURES_CREATE: '/api/figures/create',
  MINI_UNIVERSE: '/api/sector-u/',
  MINI_UNIVERSE_NOTE: '/api/sector-u/note',
  MINI_UNIVERSE_COLLECT: (id: number) => `/api/sector-u/collect/${id}`,
  MINI_UNIVERSE_RETURN: '/api/sector-u/return',
  MENTAL_SEAL_SESSION: '/api/sector-f/session',
  MENTAL_SEAL_START: '/api/sector-f/start',
  MENTAL_SEAL_REPLY: '/api/sector-f/reply',
  MENTAL_SEAL_STATE: '/api/sector-f/seal',
  MENTAL_SEAL_IMPRINT: '/api/sector-f/imprint',
  RED_COAST_SIGNALS: '/api/sector-r/signals',
  RED_COAST_BROADCAST: '/api/sector-r/broadcast',
  DARK_FOREST_STARS: '/api/sector-e/stars',
  DARK_FOREST_IGNITE: '/api/sector-e/ignite',
  DARK_FOREST_STRIKE: (id: number) => `/api/sector-e/strike/${id}`,
  DARK_FOREST_NURTURE: (id: number) => `/api/sector-e/nurture/${id}`,
  /** 零点计划 v2：统一大模型网关 */
  LLM_GATEWAY: '/api/llm/gateway',
  ZV2_WALLBREAKER_ANALYZE: '/api/zero/v2/wallbreaker/analyze',
  ZV2_DARK_FOREST_TICK: '/api/zero/v2/dark-forest/tick',
  ZV2_FAIRYTALE_ENCODE: '/api/zero/v2/fairytale/encode',
  ZV2_FAIRYTALE_DECODE: '/api/zero/v2/fairytale/decode',
  ZV2_MENTAL_SEAL_INJECT: '/api/zero/v2/mental-seal/inject',
} as const

/** 常用纪元（PGC 录入预设），按公元纪年顺序 */
export const ERA_PRESETS = [
  '黄金时代',
  '危机纪元',
  '威慑纪元',
  '掩体纪元',
  '广播纪元',
  '乱纪元',
  '银河纪元',
] as const

/**
 * 纪元起点对应的公元年份（用于时间之流按公元纪年统一排序）
 * 黄金时代：year 字段已是公元年，不再加基准。
 * 参考原著时间线：黄金时代→危机纪元(2015起)→威慑纪元(2212起)→掩体→广播→乱纪元→银河
 */
export const ERA_CE_BASE: Record<string, number> = {
  '危机纪元': 2015,
  '威慑纪元': 2212,
  '掩体纪元': 2270,
  '广播纪元': 2400,
  '乱纪元': 2500,
  '银河纪元': 2687,
}

/**
 * 将 (era, year) 转为可排序的公元年。
 * 黄金时代：year 即公元年；其余纪元：公元年 = 纪元起点(ERA_CE_BASE) + 纪元内年(year)。
 */
export function eventYearCE(era: string, year: number): number {
  if (era === '黄金时代') return year
  const base = ERA_CE_BASE[era] ?? 2000
  return base + year
}

/**
 * 修正文本中误将「纪元内年」写作「公元 X年」的展示（非黄金时代时 year 为纪元内年，非公元年）。
 * 将 公元{year}年 替换为 公元{eventYearCE(era, year)}年，仅当 era !== 黄金时代 且 CE !== year 时替换。
 */
export function normalizeEraYearInText(era: string, year: number, text: string | null | undefined): string {
  if (!text || era === '黄金时代') return text ?? ''
  const ce = eventYearCE(era, year)
  if (ce === year) return text
  let out = text
  for (const re of [
    new RegExp(`公元\\s*${year}\\s*年`, 'g'),
    new RegExp(`公元\\s*${year}年`, 'g'),
    new RegExp(`公元${year}\\s*年`, 'g'),
  ]) {
    out = out.replace(re, `公元 ${ce} 年`)
  }
  return out
}

/** 画廊占位图（Fork 待生成时） */
export const GALLERY_PLACEHOLDER_MEDIA =
  'https://placehold.co/400x400/0d0d0d/00ffff?text=%E5%BE%85%E7%94%9F%E6%88%90'

/** 沉浸式错误文案（三体语境） */
export const ERROR_MSG = {
  NETWORK: '系统受到强互作用力干扰，智子连接暂时中断。',
  SERVER: '智子遭遇未知扰动，无法完成请求。',
  DATA_MISSING: '该坐标信息已被降维打击抹除。',
  /** 智子/API 报错时 UI 显示（QA：红色三体风格） */
  ETO_REDACTED: '[REDACTED BY ETO]',
} as const

/** 请求超时（毫秒） */
export const FETCH_TIMEOUT_MS = 60_000
