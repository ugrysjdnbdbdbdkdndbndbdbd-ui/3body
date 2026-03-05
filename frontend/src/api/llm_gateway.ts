import { API, apiUrl } from '@/constants'

interface GatewayEnvelope<T> {
  data?: T
}

interface InvokeOptions<T> {
  task: string
  payload: Record<string, unknown>
  mock: () => T
}

export interface GatewayRuntimeStatus {
  circuitOpen: boolean
  consecutiveFailures: number
  lastFailureAt: number | null
  reopenAt: number | null
}

const MAX_RETRIES = 2
const FAILURE_THRESHOLD = 3
const CIRCUIT_OPEN_MS = 15_000

let consecutiveFailures = 0
let circuitOpenedAt: number | null = null

function now(): number {
  return Date.now()
}

function shouldUseCircuitFallback(): boolean {
  if (circuitOpenedAt === null) return false
  const elapsed = now() - circuitOpenedAt
  if (elapsed < CIRCUIT_OPEN_MS) return true
  circuitOpenedAt = null
  consecutiveFailures = 0
  return false
}

function markFailure(): void {
  consecutiveFailures += 1
  if (consecutiveFailures >= FAILURE_THRESHOLD) {
    circuitOpenedAt = now()
  }
}

function markSuccess(): void {
  consecutiveFailures = 0
  circuitOpenedAt = null
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export function getGatewayRuntimeStatus(): GatewayRuntimeStatus {
  const isOpen = circuitOpenedAt !== null && now() - circuitOpenedAt < CIRCUIT_OPEN_MS
  return {
    circuitOpen: isOpen,
    consecutiveFailures,
    lastFailureAt: circuitOpenedAt,
    reopenAt: isOpen && circuitOpenedAt !== null ? circuitOpenedAt + CIRCUIT_OPEN_MS : null,
  }
}

/**
 * 统一 LLM 网关入口：
 * - 有后端时走 /api/llm/gateway
 * - 无后端时自动回退 mock，保证前端闭环
 */
export async function invokeLlmGateway<T>(options: InvokeOptions<T>): Promise<T> {
  if (shouldUseCircuitFallback()) {
    return options.mock()
  }

  let lastError: unknown = null
  for (let attempt = 0; attempt <= MAX_RETRIES; attempt += 1) {
    try {
      const res = await fetch(apiUrl(API.LLM_GATEWAY), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          task: options.task,
          payload: options.payload,
        }),
      })
      if (!res.ok) throw new Error(res.statusText)
      const json = (await res.json()) as GatewayEnvelope<T> | T
      if (typeof json === 'object' && json !== null && 'data' in json) {
        const wrapped = json as GatewayEnvelope<T>
        if (wrapped.data !== undefined) {
          markSuccess()
          return wrapped.data
        }
      }
      markSuccess()
      return json as T
    } catch (error) {
      lastError = error
      markFailure()
      if (attempt < MAX_RETRIES) {
        const backoff = 300 * (attempt + 1)
        await sleep(backoff)
      }
    }
  }

  if (lastError) {
    return options.mock()
  }

  try {
    return options.mock()
  } catch {
    return options.mock()
  }
}
