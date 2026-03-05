const LOCAL_STATE_VERSION = 2

type VersionedState<T> = {
  version: number
  data: T
}

export function saveVersionedState<T>(key: string, data: T) {
  const payload: VersionedState<T> = { version: LOCAL_STATE_VERSION, data }
  localStorage.setItem(key, JSON.stringify(payload))
}

export function loadVersionedState<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key)
    if (!raw) return fallback
    const parsed = JSON.parse(raw) as VersionedState<T> | T
    if (typeof parsed === 'object' && parsed !== null && 'version' in parsed && 'data' in parsed) {
      const wrapped = parsed as VersionedState<T>
      return wrapped.data ?? fallback
    }
    return parsed as T
  } catch {
    return fallback
  }
}
