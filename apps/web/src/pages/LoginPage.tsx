import { useState, type FormEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { ErrorMessage } from '../components/ErrorMessage'
import { useAuth } from '../lib/AuthContext'

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const submit = async (event: FormEvent) => {
    event.preventDefault(); setError(null); setBusy(true)
    try {
      await login(email, password)
      navigate((location.state as { from?: string } | null)?.from ?? '/events', { replace: true })
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'ログインできませんでした') }
    finally { setBusy(false) }
  }

  return <section className="auth-card">
    <h1>ログイン</h1>
    <p className="muted">予約の確認やイベント管理を続けましょう。</p>
    <ErrorMessage message={error} />
    <form onSubmit={submit}>
      <label>メールアドレス<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" /></label>
      <label>パスワード<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} autoComplete="current-password" /></label>
      <button className="primary" disabled={busy}>{busy ? 'ログイン中…' : 'ログイン'}</button>
    </form>
    <p>アカウントがありませんか？ <Link to="/signup">新規登録</Link></p>
  </section>
}
