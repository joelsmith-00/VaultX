import { create } from 'zustand'
import type { User } from '../types'

interface AuthState {
  user: User | null
  accessToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  setUser: (user: User | null) => void
  setToken: (token: string | null) => void
  setLoading: (loading: boolean) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: null,
  isAuthenticated: false,
  isLoading: true,
  setUser: (user) => set({
    user,
    isAuthenticated: !!user
  }),
  setToken: (token) => set({
    accessToken: token
  }),
  setLoading: (loading) => set({
    isLoading: loading
  }),
  logout: () => set({
    user: null,
    accessToken: null,
    isAuthenticated: false
  }),
}))
