import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useMessage } from 'naive-ui'

export type UserRole = 'bug' | 'eto' | 'wallfacer' | 'swordholder'

export const useUserStore = defineStore('user', () => {
  // State
  const role = ref<UserRole>('bug')
  const username = ref('Anonymous')
  const exp = ref(0)
  const isIntercepted = ref(false) // Global intercept trigger
  const interceptReason = ref('')
  
  // Getters
  const roleLevel = computed(() => {
    switch (role.value) {
      case 'bug': return 0
      case 'eto': return 1
      case 'wallfacer': return 2
      case 'swordholder': return 3
      default: return 0
    }
  })

  const roleName = computed(() => {
    switch (role.value) {
      case 'bug': return '虫子 (The Bug)'
      case 'eto': return 'ETO 成员'
      case 'wallfacer': return '面壁者'
      case 'swordholder': return '执剑人'
      default: return '未知'
    }
  })

  // Actions
  function setRole(newRole: UserRole) {
    role.value = newRole
    // Persist to local storage
    localStorage.setItem('3body-role', newRole)
  }

  function checkPermission(requiredLevel: number, reason: string): boolean {
    if (roleLevel.value >= requiredLevel) {
      return true
    }
    // Trigger Sophon Intercept
    interceptReason.value = reason
    isIntercepted.value = true
    return false
  }

  function login(mockRole: UserRole = 'bug') {
    setRole(mockRole)
    username.value = 'Logic_' + Math.floor(Math.random() * 1000)
  }

  function init() {
    const saved = localStorage.getItem('3body-role') as UserRole
    if (saved) role.value = saved
  }

  return {
    role,
    username,
    roleLevel,
    roleName,
    isIntercepted,
    interceptReason,
    setRole,
    checkPermission,
    login,
    init
  }
})
