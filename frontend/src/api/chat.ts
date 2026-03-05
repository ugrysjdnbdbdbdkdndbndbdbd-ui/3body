import type { Message } from '@/types/sophon'

export const streamChat = async (
  messages: Message[], 
  onChunk: (chunk: string) => void
): Promise<void> => {
  // Mock Sophon response
  const lastUserMsg = messages[messages.length - 2]?.content || ''
  
  let responseText = ''
  if (lastUserMsg.includes('虫子')) {
    responseText = '你们是虫子。我们正在看着你们。'
  } else if (lastUserMsg.includes('你好')) {
    responseText = '我是智子。我在倾听。'
  } else {
    responseText = `[智子回复] 我收到了你的信息: "${lastUserMsg}"。但在十一维视角下，这就如同在纸上爬行的蚂蚁留下的痕迹。`
  }

  // Simulate streaming
  const chunks = responseText.split('')
  for (const chunk of chunks) {
    await new Promise(resolve => setTimeout(resolve, 50))
    onChunk(chunk)
  }
}
