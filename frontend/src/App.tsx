import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Login from './pages/Login'
import Register from './pages/Register'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-cyber-dark">
          <Toaster
            position="top-right"
            toastOptions={{
              style: {
                background: '#111118',
                color: '#fff',
                border: '1px solid #2E2E3A',
              },
              success: {
                iconTheme: { primary: '#2CB67D', secondary: '#fff' },
              },
              error: {
                iconTheme: { primary: '#ef4444', secondary: '#fff' },
              },
            }}
          />
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/dashboard" element={
              <div className="flex items-center justify-center min-h-screen">
                <div className="cyber-card text-center glow-purple">
                  <h1 className="text-4xl font-bold text-cyber-purple mb-2">
                    ⚡ VaultX
                  </h1>
                  <p className="text-cyber-teal text-lg">
                    Secure Cloud Storage Platform
                  </p>
                  <p className="text-gray-400 mt-4">
                    Frontend is running successfully!
                  </p>
                  <div className="mt-4 px-4 py-2 bg-gray-900 rounded-lg">
                    <p className="text-green-400 text-sm">
                      ✅ React + TypeScript + Vite + Tailwind Ready
                    </p>
                  </div>
                </div>
              </div>
            } />
          </Routes>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
