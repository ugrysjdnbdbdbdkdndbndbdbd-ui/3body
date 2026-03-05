/** 关键决策 */
export interface KeyDecision {
  decision: string
  context: string
  outcome: string
}

/** 人物关系 */
export interface FigureRelationship {
  target: string
  relation_type: string
  description: string
}

/** 关键语录（带语境） */
export interface KeyQuote {
  quote: string
  context: string
}

export interface Figure {
  id: number
  name: string
  en_name?: string | null
  role: string
  era: string
  status: string
  description: string
  image_url?: string | null
  quotes?: string | null
  logic_score: number
  metrics?: string | null
  key_events?: string | null
  key_decisions?: string | null
  relationships?: string | null
  key_quotes?: string | null
  created_at?: string
}

export interface FigureCreate {
  name: string
  en_name?: string | null
  role: string
  era: string
  status: string
  description: string
  image_url?: string | null
  quotes?: string | null
  logic_score: number
  metrics?: string | null
  key_events?: string | null
  key_decisions?: string | null
  relationships?: string | null
  key_quotes?: string | null
}
