export interface Message {
  id: string
  role: 'user' | 'sophon'
  content: string
  timestamp: number
  status: 'streaming' | 'done' | 'error'
}
