/**
 * 零点计划 — 智子审计 API
 */
import { API, apiUrl } from '@/constants'

export interface AuditDetail {
  violations: string[]
  explanation: string
}

export interface AuditResponse {
  verdict: 'PASS' | 'WARN' | 'REJECT'
  logic_score: number
  message: string
  details: AuditDetail
}

export async function auditFragment(fragment: string): Promise<AuditResponse> {
  const res = await fetch(apiUrl(API.SOPHON_AUDIT), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ fragment: fragment.trim() }),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || res.statusText)
  }
  return res.json() as Promise<AuditResponse>
}
