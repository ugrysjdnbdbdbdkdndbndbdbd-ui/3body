/**
 * 人物志 AI 对话：调用 POST /api/chat/figure，流式返回
 */
import { apiUrl } from '@/constants'

export interface FigureChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface FigureChatPayload {
  figure_name: string
  figure_role?: string
  figure_description?: string
  message: string
  history?: FigureChatMessage[]
  api_key?: string
  base_url?: string
  model?: string
}

/**
 * 请求人物对话流式接口，通过 onChunk 逐段接收文本。
 * 返回的 Promise 在流结束或出错时 resolve；出错时 onError 会被调用。
 */
export async function streamFigureChat(
  payload: FigureChatPayload,
  onChunk: (chunk: string) => void,
  onError?: (err: string) => void
): Promise<void> {
  const url = apiUrl('/api/chat/figure')
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const msg = res.status === 502 || res.status === 503
      ? '无法连接 LLM，请确认 Ollama 已启动或已配置正确的 API 地址与 Key。'
      : `请求失败: ${res.status} ${res.statusText}`
    onError?.(msg)
    return
  }
  const reader = res.body?.getReader()
  if (!reader) {
    onError?.('无法读取响应流')
    return
  }
  const decoder = new TextDecoder()
  let buffer = ''
  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const events = buffer.split('\n\n')
      buffer = events.pop() ?? ''
      for (const event of events) {
        if (event.startsWith('data: ')) {
          const data = event.slice(6)
          if (data.trim() === '[DONE]') continue
          onChunk(data)
        }
      }
    }
    if (buffer.startsWith('data: ')) {
      const data = buffer.slice(6)
      if (data.trim() !== '[DONE]') onChunk(data)
    }
  } catch (e) {
    onError?.(e instanceof Error ? e.message : String(e))
  }
}
