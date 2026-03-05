/**
 * UniverseStore - PRD 统一总线：当前纪元、威慑度、舰队距离、掩体人口等。
 * 扇区共享，威慑度驱动全站色调（红 <-> 蓝）。
 * 失败时设置 error，避免静默失败（质检：UniverseStore 式静默失败）。
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { API, ERROR_MSG, apiUrl } from '@/constants'
import type { UserSeal } from '@/types/mental_seal'

export interface UniverseMetrics {
  dark_forest_deterrence: number
  trisolaran_fleet_distance_ly: number
  fleet_years_remaining: number
  current_era: string
  shelter_population: number
  timestamp: string
  resonance_state?: '3d' | '2d' | '1d' // 全服共振状态
  environment_state?: 'stable' | 'cold' | 'heat' | 'rip'
  temperature?: number
  gravity?: number
}

export const useUniverseStore = defineStore('universe', () => {
  const metrics = ref<UniverseMetrics | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const resonanceState = ref<'3d' | '2d' | '1d'>('3d')
  const dehydrated = ref(false) // 主动脱水
  const mentalSeal = ref<UserSeal | null>(null)

  const deterrence = computed(() => metrics.value?.dark_forest_deterrence ?? 0.5)
  const currentEra = computed(() => metrics.value?.current_era ?? '—')
  const fleetYearsRemaining = computed(() => metrics.value?.fleet_years_remaining ?? 400)
  const fleetDistanceLy = computed(() => metrics.value?.trisolaran_fleet_distance_ly ?? 0)
  const shelterPopulation = computed(() => metrics.value?.shelter_population ?? 0)
  const environment = computed(() => metrics.value?.environment_state ?? 'stable')
  const temperature = computed(() => metrics.value?.temperature ?? 293)
  const gravity = computed(() => metrics.value?.gravity ?? 1.0)

  /** 威慑度驱动色调：低→红岸红，高→切伦科夫蓝，用于 CSS 变量或 class */
  const themeTint = computed(() => {
    const d = deterrence.value
    if (d >= 0.6) return 'blue'
    if (d >= 0.4) return 'mixed'
    return 'red'
  })

  async function fetchMetrics() {
    loading.value = true
    error.value = null
    try {
      const res = await fetch(apiUrl(API.UNIVERSE_METRICS))
      if (!res.ok) throw new Error(res.statusText)
      const data = (await res.json()) as UniverseMetrics
      metrics.value = data
      // 启用共振同步
      if (data.resonance_state) resonanceState.value = data.resonance_state
      
      // Fetch Seal
      const sealRes = await fetch(apiUrl(API.MENTAL_SEAL_STATE))
      if (sealRes.ok) {
        mentalSeal.value = await sealRes.json()
      }
    } catch {
      error.value = ERROR_MSG.NETWORK
      metrics.value = null
    } finally {
      loading.value = false
    }
  }

  function setResonance(state: '3d' | '2d' | '1d') {
    resonanceState.value = state
  }

  function toggleDehydrate() {
    dehydrated.value = !dehydrated.value
  }

  return {
    metrics,
    loading,
    error,
    deterrence,
    currentEra,
    fleetYearsRemaining,
    fleetDistanceLy,
    shelterPopulation,
    themeTint,
    resonanceState,
    environment,
    temperature,
    gravity,
    dehydrated,
    mentalSeal,
    fetchMetrics,
    setResonance,
    toggleDehydrate,
  }
})
