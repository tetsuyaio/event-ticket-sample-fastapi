export function StatusBadge({ value }: { value: string }) {
  const labels: Record<string, string> = {
    DRAFT: '下書き', PUBLISHED: '公開中', CLOSED: '受付終了', CANCELLED: 'キャンセル済み', RESERVED: '予約済み', VALID: '有効',
  }
  return <span className={`badge badge-${value.toLowerCase()}`}>{labels[value] ?? value}</span>
}
