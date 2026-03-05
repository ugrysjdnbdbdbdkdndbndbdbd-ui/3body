export interface MiniUniverse {
  id: number
  user_id: string
  mass: number
  items: string // JSON
  notes: string // JSON
  created_at?: string
}

export interface MiniUniverseUpdate {
  note_add?: string
  action?: string
}
