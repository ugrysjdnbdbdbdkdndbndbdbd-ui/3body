export interface GalleryItem {
  id: string | number
  title: string
  description: string | null
  media_url: string
  media_type: string
  prompt_text?: string | null
  created_at?: string
  status?: string // normal | exposed | cleansed
  logic_score?: number
  author_id?: string
}

/** 添加/录入画廊作品请求体 */
export interface GalleryItemCreate {
  title: string
  description?: string | null
  media_url: string
  media_type?: string
  prompt_text?: string | null
}
