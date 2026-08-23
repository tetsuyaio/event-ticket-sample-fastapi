import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../lib/AuthContext'

export function RequireAuth() {
  const { user, loading } = useAuth()
  const location = useLocation()
  if (loading) return <p className="notice">認証状態を確認しています…</p>
  return user ? <Outlet /> : <Navigate to="/login" replace state={{ from: location.pathname }} />
}

export function RequireAdmin() {
  const { user, loading } = useAuth()
  if (loading) return <p className="notice">認証状態を確認しています…</p>
  if (!user) return <Navigate to="/login" replace />
  return user.role === 'ADMIN' ? <Outlet /> : <Navigate to="/events" replace />
}
