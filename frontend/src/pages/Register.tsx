import React, { useState } from 'react'
import api from '../api/axios'
import { useAuthStore } from '../store/authStore'
import { useNavigate } from 'react-router-dom'

export default function Register() {
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()
  const setToken = useAuthStore((s) => s.setToken)

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const res = await api.post('/api/auth/register', { email, username, password })
      setToken(res.data.access_token)
      navigate('/dashboard')
    } catch (err) {
      alert('Registration failed')
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen">
      <form className="cyber-card p-6 w-96" onSubmit={submit}>
        <h2 className="text-2xl font-bold mb-4">Create account</h2>
        <label className="block text-left text-sm">Email</label>
        <input className="input" value={email} onChange={(e) => setEmail(e.target.value)} />
        <label className="block text-left text-sm mt-3">Username</label>
        <input className="input" value={username} onChange={(e) => setUsername(e.target.value)} />
        <label className="block text-left text-sm mt-3">Password</label>
        <input type="password" className="input" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button className="mt-4 btn-primary w-full" type="submit">Create account</button>
      </form>
    </div>
  )
}
