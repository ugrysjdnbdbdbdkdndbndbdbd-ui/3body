/** 变数来源（因果回溯）— 谁在何时做出了什么选择 */
export interface VariantSourceItem {
  user_id?: string
  action: string
  timestamp: string
}

export interface ChronicleEvent {
  id: number
  era: string
  year: number
  title: string
  content: string
  summary?: string | null
  image_url: string | null
  event_type?: string
  created_at?: string
  /** 零点计划：叠加态 | 已坍缩 */
  causality_status?: string
  interaction_count?: number
  collapse_threshold?: number
  parent_node_id?: number | null
  /** JSON 字符串，解析为 VariantSourceItem[] */
  variant_source?: string | null
}

/** PGC/UGC 录入请求体 */
export interface ChronicleEventCreate {
  era: string
  year: number
  title: string
  content: string
  summary?: string | null
  image_url?: string | null
  event_type?: string
}
