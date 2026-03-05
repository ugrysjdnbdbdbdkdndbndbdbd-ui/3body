export interface ForestStar {
  id: number
  author_id: string
  content: string
  mass: number
  brightness: number
  status: string
  x: number
  y: number
  created_at?: string
}

export interface ForestStarCreate {
  content: string
  author_id?: string
}
