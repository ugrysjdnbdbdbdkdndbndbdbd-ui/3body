import type { CivilizationAgent, CosmicEpitaph } from '@/types/zero_v2'

const CODENAMES = [
  'CIV-031',
  'CIV-117',
  'CIV-208',
  'CIV-404',
  'CIV-617',
  'CIV-739',
  'CIV-881',
  'CIV-999',
  'CIV-002',
  'CIV-055',
  'CIV-266',
  'CIV-512',
]

function rand(min: number, max: number): number {
  return min + Math.random() * (max - min)
}

export function seedCivilizations(size = 8): CivilizationAgent[] {
  return Array.from({ length: size }, (_, idx) => ({
    id: idx + 1,
    codename: CODENAMES[idx] ?? `CIV-${idx + 1}`,
    technology_level: Number(rand(0.6, 1.8).toFixed(2)),
    paranoia_index: Number(rand(0.35, 0.95).toFixed(2)),
    concealment_skill: Number(rand(0.2, 0.9).toFixed(2)),
    x: Number(rand(6, 94).toFixed(2)),
    y: Number(rand(6, 94).toFixed(2)),
    alive: true,
  }))
}

function distance(a: CivilizationAgent, b: CivilizationAgent): number {
  return Math.hypot(a.x - b.x, a.y - b.y)
}

function bounded(v: number): number {
  if (v < 2) return 2
  if (v > 98) return 98
  return v
}

export function tickUniverse(
  agents: CivilizationAgent[],
  epoch: number,
): { agents: CivilizationAgent[]; epitaphs: CosmicEpitaph[] } {
  const next = agents.map((a) => ({ ...a }))
  const epitaphs: CosmicEpitaph[] = []

  for (const agent of next) {
    if (!agent.alive) continue
    agent.x = bounded(agent.x + rand(-1.8, 1.8))
    agent.y = bounded(agent.y + rand(-1.8, 1.8))
    agent.technology_level = Number(Math.min(2.2, agent.technology_level + rand(0, 0.04)).toFixed(2))
  }

  for (const agent of next) {
    if (!agent.alive) continue
    const targets = next.filter((t) => t.id !== agent.id && t.alive)
    if (targets.length === 0) continue

    const nearest = targets.reduce((acc, cur) => {
      return distance(agent, cur) < distance(agent, acc) ? cur : acc
    }, targets[0])

    const detectRange = 8 + agent.technology_level * 11 * (1 - nearest.concealment_skill * 0.5)
    if (distance(agent, nearest) > detectRange) continue

    const strikeChance = agent.paranoia_index * 0.72
    const probeChance = 0.18 + agent.technology_level * 0.12
    const roll = Math.random()

    if (roll < strikeChance) {
      nearest.alive = false
      epitaphs.push({
        id: Date.now() + nearest.id,
        epoch,
        attacker: agent.codename,
        victim: nearest.codename,
        reason: '光粒打击：接触即暴露，暴露即清除。',
      })
      continue
    }

    if (roll < strikeChance + probeChance) {
      nearest.concealment_skill = Number(Math.max(0.05, nearest.concealment_skill - 0.03).toFixed(2))
      continue
    }
  }

  return { agents: next, epitaphs }
}
