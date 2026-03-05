export type HiddenStrategy = 'ESCAPISM' | 'MUTUAL_DESTRUCTION' | 'DISGUISE'

export interface WallbreakerDirectiveLog {
  id: number
  directive: string
  verdict: 'APPROVED' | 'REJECTED'
  reason: string
  suspicionDelta: number
  suspicionTotal: number
  inferred: HiddenStrategy
  createdAt: string
}

export interface CivilizationAgent {
  id: number
  codename: string
  technology_level: number
  paranoia_index: number
  concealment_skill: number
  x: number
  y: number
  alive: boolean
}

export interface CosmicEpitaph {
  id: number
  epoch: number
  attacker: string
  victim: string
  reason: string
}

export interface EncryptedFairytale {
  id: number
  title: string
  original: string
  fairytale: string
  decodeProgress: number
  createdAt: string
}

export interface MemeHeat {
  token: string
  count: number
}

export interface WorldlineSnapshot {
  id: number
  name: string
  savedAt: string
  epoch: number
  agents: CivilizationAgent[]
  epitaphs: CosmicEpitaph[]
}
