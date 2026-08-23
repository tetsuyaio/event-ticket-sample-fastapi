import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ErrorMessage } from '../components/ErrorMessage'
import { StatusBadge } from '../components/StatusBadge'
import { api } from '../lib/api'
import { formatDate } from '../lib/format'
import type { Event } from '../lib/types'

export function AdminEventsPage() {
  const [items, setItems] = useState<Event[]>([])
  const [error, setError] = useState<string | null>(null)
  useEffect(() => { api.events('?page=1&limit=100').then(setItems).catch((reason) => setError(reason instanceof Error ? reason.message : 'イベントを取得できませんでした')) }, [])
  return <>
    <div className="page-heading"><div><p className="eyebrow">Administration</p><h1>イベント管理</h1></div><Link className="button primary" to="/admin/events/new">イベントを作成</Link></div>
    <ErrorMessage message={error} />
    <div className="table-wrap"><table><thead><tr><th>イベント</th><th>日時</th><th>状態</th><th>予約数</th><th></th></tr></thead><tbody>
      {items.map((item) => <tr key={item.id}><td><strong>{item.title}</strong><small>{item.venue}</small></td><td>{formatDate(item.startsAt)}</td><td><StatusBadge value={item.status} /></td><td>{item.reservedCount} / {item.capacity}</td><td><Link to={`/events/${item.id}`}>表示</Link></td></tr>)}
    </tbody></table>{items.length === 0 && !error && <p className="empty">イベントはありません。</p>}</div>
  </>
}
