import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ErrorMessage } from '../components/ErrorMessage'
import { StatusBadge } from '../components/StatusBadge'
import { api } from '../lib/api'
import { formatDate } from '../lib/format'
import type { Reservation } from '../lib/types'

export function ReservationsPage() {
  const [items, setItems] = useState<Reservation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const load = async () => {
    setLoading(true)
    try { setItems(await api.reservations()) }
    catch (reason) { setError(reason instanceof Error ? reason.message : '予約を取得できませんでした') }
    finally { setLoading(false) }
  }
  useEffect(() => { void load() }, [])
  const cancel = async (id: string) => {
    if (!confirm('この予約をキャンセルしますか？')) return
    setError(null)
    try { await api.cancelReservation(id); await load() }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'キャンセルできませんでした') }
  }
  return <>
    <div className="page-heading"><div><p className="eyebrow">My tickets</p><h1>予約一覧</h1></div></div>
    <ErrorMessage message={error} />
    {loading ? <p className="notice">読み込み中…</p> : items.length === 0 ? <div className="empty">予約はありません。<br /><Link to="/events">イベントを探す</Link></div> : (
      <div className="reservation-list">{items.map((item) => <article key={item.id} className="reservation-card">
        <div><StatusBadge value={item.status} /><h2>{item.event.title}</h2><p>{formatDate(item.event.startsAt)} / {item.event.venue}</p><p className="ticket-number">Ticket #{item.ticket.ticketNumber}</p></div>
        <div className="actions"><Link className="button secondary" to={`/events/${item.event.id}`}>詳細</Link>{item.status === 'RESERVED' && <button className="danger" onClick={() => void cancel(item.id)}>キャンセル</button>}</div>
      </article>)}</div>
    )}
  </>
}
