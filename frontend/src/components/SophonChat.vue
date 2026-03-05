<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { NInput, NButton } from 'naive-ui'
import { API, ERROR_MSG, apiUrl } from '@/constants'

const input = ref('')
const messages = ref<Array<{ role: 'user' | 'sophon'; text: string }>>([])
const streamingText = ref('')
const isLoading = ref(false)

async function send() {
  const text = input.value.trim()
  if (!text || isLoading.value) return
  input.value = ''
  messages.value.push({ role: 'user', text })
  streamingText.value = ''
  isLoading.value = true

  try {
    const res = await fetch(apiUrl(API.CHAT_STREAM), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    })
    if (!res.ok) throw new Error(res.statusText)
    const reader = res.body?.getReader()
    const decoder = new TextDecoder()
    if (!reader) throw new Error('No body')
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() ?? ''
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const raw = line.slice(6).trim()
        if (raw === '[DONE]') continue
        try {
          const parsed = JSON.parse(raw)
          const content = parsed?.data ?? parsed
          if (typeof content === 'string') streamingText.value += content
        } catch {
          if (raw) streamingText.value += raw
        }
      }
      await nextTick()
    }
  } catch {
    streamingText.value = ERROR_MSG.NETWORK
  } finally {
    if (streamingText.value) {
      messages.value.push({ role: 'sophon', text: streamingText.value })
      streamingText.value = ''
    }
    isLoading.value = false
  }
}
</script>

<template>
  <div class="sophon-chat flex h-full flex-col p-4">
    <div class="chat-area retina-projection flex-1 space-y-4 overflow-y-auto font-mono text-sm">
      <div
        v-for="(msg, i) in messages"
        :key="i"
        class="message"
        :class="msg.role === 'user' ? 'text-primary-dim' : 'text-primary'"
      >
        <span v-if="msg.role === 'sophon'" class="mr-2 text-danger">[智子]</span>
        <span class="whitespace-pre-wrap">{{ msg.text }}</span>
      </div>
      <div v-if="streamingText" class="message text-primary">
        <span class="mr-2 text-danger">[智子]</span>
        <span class="whitespace-pre-wrap">{{ streamingText }}</span>
        <span class="cursor-blink">|</span>
      </div>
    </div>
    <form class="mt-4 flex gap-2" @submit.prevent="send">
      <NInput
        v-model:value="input"
        placeholder="虫子，你想知道什么？"
        class="flex-1"
        :disabled="isLoading"
        @keydown.enter.prevent="send"
      />
      <NButton type="primary" :loading="isLoading" @click="send">发送</NButton>
    </form>
  </div>
</template>

<style scoped>
.retina-projection {
  position: relative;
}
.retina-projection::after {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent 0,
    transparent 2px,
    rgba(0, 255, 255, 0.03) 2px,
    rgba(0, 255, 255, 0.03) 4px
  );
  pointer-events: none;
}
.cursor-blink {
  animation: blink 0.8s step-end infinite;
}
@keyframes blink {
  50% {
    opacity: 0;
  }
}
</style>
