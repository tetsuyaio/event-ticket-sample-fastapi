import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ErrorMessage } from '../components/ErrorMessage'
import { useAuth } from '../lib/AuthContext'

export function SignupPage() {
  const { signup } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const submit = async (event: FormEvent) => {
    event.preventDefault(); setError(null); setBusy(true)
    try { await signup(form.email, form.password, form.name); navigate('/events', { replace: true }) }
    catch (reason) { setError(reason instanceof Error ? reason.message : '登録できませんでした') }
    finally { setBusy(false) }
  }
  return <section className="auth-card">
    <h1>新規登録</h1>
    <ErrorMessage message={error} />
    <form onSubmit={submit}>
      <label>名前<input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required maxLength={100} autoComplete="name" /></label>
      <label>メールアドレス<input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required autoComplete="email" /></label>
      <label>パスワード<input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required minLength={8} autoComplete="new-password" /><small>8文字以上で入力してください</small></label>
      <button className="primary" disabled={busy}>{busy ? '登録中…' : '登録する'}</button>
    </form>
    <p>登録済みですか？ <Link to="/login">ログイン</Link></p>
  </section>
}
