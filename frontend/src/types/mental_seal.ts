export interface MentalSealSession {
  id: number
  user_id: string
  plan_title: string
  plan_content: string
  status: string // active, broken, success, abandoned
  history: string // JSON
  round_count: number
  created_at?: string
}

export interface ChatItem {
  role: string // user, breaker, system
  name: string
  content: string
  timestamp: string
}

export interface UserSeal {
  id: number
  seal_type: 'TRIUMPH' | 'DEFEAT' | 'ADVENT' | 'SURVIVE'
  strength: number
  imprinted_at: string
}
