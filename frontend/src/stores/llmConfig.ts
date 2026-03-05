/**
 * LLM 配置：API Key / Base URL / Model
 * 通用情况使用本地 Ollama（不填 Key）；填了 Key 或自定义 URL 时走云端/自定义端点。
 * 持久化到 localStorage，供人物志对话等使用。
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const STORAGE_KEY = '3body-llm-config'

export interface LlmConfigState {
  useLocalOllama: boolean
  apiKey: string
  baseUrl: string
  model: string
}

const defaultState: LlmConfigState = {
  useLocalOllama: true,
  apiKey: '',
  baseUrl: '',
  model: '',
}

function load(): LlmConfigState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { ...defaultState }
    const parsed = JSON.parse(raw) as Partial<LlmConfigState>
    return { ...defaultState, ...parsed }
  } catch {
    return { ...defaultState }
  }
}

function save(state: LlmConfigState) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  } catch {
    // ignore
  }
}

export const useLlmConfigStore = defineStore('llmConfig', () => {
  const useLocalOllama = ref(load().useLocalOllama)
  const apiKey = ref(load().apiKey)
  const baseUrl = ref(load().baseUrl)
  const model = ref(load().model)

  /** 当前是否使用本地 Ollama（不传 Key/URL 给后端） */
  const isLocal = computed(() => useLocalOllama.value)

  /** 请求体里要传给后端的覆盖项（仅当非本地时传） */
  const requestOverrides = computed(() => {
    if (useLocalOllama.value) return {}
    return {
      api_key: apiKey.value || undefined,
      base_url: baseUrl.value || undefined,
      model: model.value || undefined,
    }
  })

  function setUseLocalOllama(v: boolean) {
    useLocalOllama.value = v
    persist()
  }

  function setApiKey(v: string) {
    apiKey.value = v
    persist()
  }

  function setBaseUrl(v: string) {
    baseUrl.value = v
    persist()
  }

  function setModel(v: string) {
    model.value = v
    persist()
  }

  function setAll(state: Partial<LlmConfigState>) {
    if (state.useLocalOllama !== undefined) useLocalOllama.value = state.useLocalOllama
    if (state.apiKey !== undefined) apiKey.value = state.apiKey
    if (state.baseUrl !== undefined) baseUrl.value = state.baseUrl
    if (state.model !== undefined) model.value = state.model
    persist()
  }

  function persist() {
    save({
      useLocalOllama: useLocalOllama.value,
      apiKey: apiKey.value,
      baseUrl: baseUrl.value,
      model: model.value,
    })
  }

  function init() {
    const s = load()
    useLocalOllama.value = s.useLocalOllama
    apiKey.value = s.apiKey
    baseUrl.value = s.baseUrl
    model.value = s.model
  }

  return {
    useLocalOllama,
    apiKey,
    baseUrl,
    model,
    isLocal,
    requestOverrides,
    setUseLocalOllama,
    setApiKey,
    setBaseUrl,
    setModel,
    setAll,
    init,
  }
})
