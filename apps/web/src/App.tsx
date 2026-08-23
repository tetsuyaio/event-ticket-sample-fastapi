import { Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { RequireAdmin, RequireAuth } from './components/RouteGuards'
import { AdminEventNewPage } from './pages/AdminEventNewPage'
import { AdminEventsPage } from './pages/AdminEventsPage'
import { EventDetailPage } from './pages/EventDetailPage'
import { EventsPage } from './pages/EventsPage'
import { LoginPage } from './pages/LoginPage'
import { ReservationsPage } from './pages/ReservationsPage'
import { SignupPage } from './pages/SignupPage'

export function App() {
  return <Routes>
    <Route element={<Layout />}>
      <Route index element={<Navigate to="/events" replace />} />
      <Route path="login" element={<LoginPage />} />
      <Route path="signup" element={<SignupPage />} />
      <Route path="events" element={<EventsPage />} />
      <Route path="events/:id" element={<EventDetailPage />} />
      <Route element={<RequireAuth />}>
        <Route path="my/reservations" element={<ReservationsPage />} />
      </Route>
      <Route element={<RequireAdmin />}>
        <Route path="admin/events" element={<AdminEventsPage />} />
        <Route path="admin/events/new" element={<AdminEventNewPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/events" replace />} />
    </Route>
  </Routes>
}
