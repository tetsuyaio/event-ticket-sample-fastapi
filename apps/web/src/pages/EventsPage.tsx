import { useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { ErrorMessage } from '../components/ErrorMessage'
import { StatusBadge } from '../components/StatusBadge'
import { api } from '../lib/api'
import { formatDate } from '../lib/format'
import type { Event } from '../lib/types'

export function EventsPage() {
  const [events, setEvents] = useState<Event[]>([])
  const [keyword, setKeyword] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = async (query = '') => {
    setLoading(true); setError(null)
    try { setEvents(await api.events(query)) }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'イベントを取得できませんでした') }
    finally { setLoading(false) }
  }
  useEffect(() => { void load('?status=PUBLISHED&page=1&limit=20') }, [])
  const search = (event: FormEvent) => {
    event.preventDefault()
    const params = new URLSearchParams({ status: 'PUBLISHED', page: '1', limit: '20' })
    if (keyword.trim()) params.set('keyword', keyword.trim())
    void load(`?${params}`)
  }

  return <>
    <div className="page-heading"><div><p className="eyebrow">Discover</p><h1>開催予定のイベント</h1></div></div>
    <form className="search" onSubmit={search}><input value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="イベント名・キーワード" aria-label="イベント検索" /><button>検索</button></form>
    <ErrorMessage message={error} />
    {loading ? <p className="notice">読み込み中…</p> : events.length === 0 ? <p className="empty">公開中のイベントはありません。</p> : (
      <div className="card-grid">{events.map((item) => <article className="event-card" key={item.id}>
        <div className="card-top"><StatusBadge value={item.status} /><span>残り {Math.max(item.capacity - item.reservedCount, 0)} 席</span></div>
        <h2><Link to={`/events/${item.id}`}>{item.title}</Link></h2>
        <p className="clamp">{item.description}</p>
        <dl><div><dt>日時</dt><dd>{formatDate(item.startsAt)}</dd></div><div><dt>会場</dt><dd>{item.venue}</dd></div></dl>
        <Link className="button secondary" to={`/events/${item.id}`}>詳細を見る</Link>
      </article>)}</div>
    )}
  </>
}
