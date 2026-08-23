import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ErrorMessage } from '../components/ErrorMessage'
import { api } from '../lib/api'
import { toApiDate } from '../lib/format'
import type { EventStatus } from '../lib/types'

export function AdminEventNewPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ title: '', description: '', venue: '', startsAt: '', endsAt: '', capacity: 10, status: 'DRAFT' as EventStatus })
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const submit = async (event: FormEvent) => {
    event.preventDefault(); setError(null)
    if (new Date(form.startsAt) >= new Date(form.endsAt)) { setError('終了日時は開始日時より後にしてください'); return }
    setBusy(true)
    try {
      const created = await api.createEvent({ title: form.title, description: form.description, venue: form.venue, startsAt: toApiDate(form.startsAt), endsAt: toApiDate(form.endsAt), capacity: form.capacity, status: form.status })
      navigate(`/events/${created.id}`)
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'イベントを作成できませんでした') }
    finally { setBusy(false) }
  }
  return <section className="form-page">
    <Link to="/admin/events">← イベント管理</Link><h1>イベントを作成</h1><ErrorMessage message={error} />
    <form onSubmit={submit}>
      <label>イベント名<input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required maxLength={200} /></label>
      <label>説明<textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} required rows={6} /></label>
      <label>会場<input value={form.venue} onChange={(e) => setForm({ ...form, venue: e.target.value })} required /></label>
      <div className="form-row"><label>開始日時<input type="datetime-local" value={form.startsAt} onChange={(e) => setForm({ ...form, startsAt: e.target.value })} required /></label><label>終了日時<input type="datetime-local" value={form.endsAt} onChange={(e) => setForm({ ...form, endsAt: e.target.value })} required /></label></div>
      <div className="form-row"><label>定員<input type="number" min={1} value={form.capacity} onChange={(e) => setForm({ ...form, capacity: Number(e.target.value) })} required /></label><label>公開状態<select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value as EventStatus })}><option value="DRAFT">下書き</option><option value="PUBLISHED">公開</option></select></label></div>
      <button className="primary" disabled={busy}>{busy ? '作成中…' : 'イベントを作成'}</button>
    </form>
  </section>
}
