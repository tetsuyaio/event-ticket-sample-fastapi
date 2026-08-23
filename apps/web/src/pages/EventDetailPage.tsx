import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ErrorMessage } from '../components/ErrorMessage'
import { StatusBadge } from '../components/StatusBadge'
import { api } from '../lib/api'
import { useAuth } from '../lib/AuthContext'
import { formatDate } from '../lib/format'
import type { Event } from '../lib/types'

export function EventDetailPage() {
  const { id = '' } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [item, setItem] = useState<Event | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [complete, setComplete] = useState(false)
  useEffect(() => { api.event(id).then(setItem).catch((reason) => setError(reason instanceof Error ? reason.message : 'イベントを取得できませんでした')) }, [id])

  const reserve = async () => {
    if (!user) { navigate('/login', { state: { from: `/events/${id}` } }); return }
    if (!confirm('このイベントを予約しますか？')) return
    setBusy(true); setError(null)
    try { await api.reserve(id); setComplete(true); setItem(await api.event(id)) }
    catch (reason) { setError(reason instanceof Error ? reason.message : '予約できませんでした') }
    finally { setBusy(false) }
  }

  if (!item && !error) return <p className="notice">読み込み中…</p>
  if (!item) return <ErrorMessage message={error} />
  const remaining = Math.max(item.capacity - item.reservedCount, 0)
  return <article className="detail">
    <Link to="/events">← イベント一覧</Link>
    <div className="detail-header"><div><StatusBadge value={item.status} /><h1>{item.title}</h1><p className="lead">{item.description}</p></div><aside><strong>{remaining}</strong><span>席 残っています</span></aside></div>
    <ErrorMessage message={error} />
    {complete && <p className="success">予約が完了しました。<Link to="/my/reservations">予約一覧を確認</Link></p>}
    <dl className="detail-list"><div><dt>開催日時</dt><dd>{formatDate(item.startsAt)} 〜 {formatDate(item.endsAt)}</dd></div><div><dt>会場</dt><dd>{item.venue}</dd></div><div><dt>定員</dt><dd>{item.capacity} 名</dd></div></dl>
    <button className="primary wide" onClick={reserve} disabled={busy || remaining === 0 || item.status !== 'PUBLISHED' || complete}>{busy ? '予約中…' : complete ? '予約済み' : remaining === 0 ? '満席です' : 'このイベントを予約する'}</button>
  </article>
}
