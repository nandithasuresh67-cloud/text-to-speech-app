import { createContext, useContext, useEffect, useState } from 'react'
import client from '../api'

const AuthContext = createContext(null)

const TOKEN_KEY = 'tts_access_token'

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState(null)

  useEffect(() => {
    if (token) {
      localStorage.setItem(TOKEN_KEY, token)
      client.defaults.headers.common.Authorization = `Bearer ${token}`
    } else {
      localStorage.removeItem(TOKEN_KEY)
      delete client.defaults.headers.common.Authorization
      setUser(null)
    }
  }, [token])

  const register = async (email, password) => {
    const response = await client.post('/api/auth/register', { email, password })
    setToken(response.data.access_token)
    setUser(response.data.user)
    return response.data
  }

  const login = async (email, password) => {
    const response = await client.post('/api/auth/login', { email, password })
    setToken(response.data.access_token)
    setUser(response.data.user)
    return response.data
  }

  const logout = () => {
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ token, user, isAuthenticated: !!token, register, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider')
  return ctx
}
