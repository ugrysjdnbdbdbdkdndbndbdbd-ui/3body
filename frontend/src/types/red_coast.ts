export interface Signal {
  id: number
  source_type: string
  frequency: number
  content_encrypted: string
  content_decrypted: string
  power_level: string
  integrity: number
  created_at?: string
}

export interface SignalCreate {
  source_type: string
  frequency: number
  content_decrypted: string
  power_level: string
}
