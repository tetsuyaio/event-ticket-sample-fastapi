import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../lib/AuthContext'

export function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const signOut = () => { logout(); navigate('/events') }

  return (
    <>
      <header className="header">
        <NavLink className="brand" to="/events">Event Tickets</NavLink>
        <nav aria-label="メインナビゲーション">
          <NavLink to="/events">イベント</NavLink>
          {user && <NavLink to="/my/reservations">予約一覧</NavLink>}
          {user?.role === 'ADMIN' && <NavLink to="/admin/events">イベント管理</NavLink>}
          {!user ? <><NavLink to="/login">ログイン</NavLink><NavLink to="/signup">新規登録</NavLink></> : (
            <button className="link-button" onClick={signOut}>{user.name} / ログアウト</button>
          )}
        </nav>
      </header>
      <main className="container"><Outlet /></main>
      <footer>Event Ticket Reservation App</footer>
    </>
  )
}
