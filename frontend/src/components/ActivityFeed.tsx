import { useState, useEffect } from 'react'
import api from '../api/axios'

type ActivityItem = {
  id: string
  action: string
  subject_type: string | null
  subject_id: string | null
  details: Record<string, any> | null
  created_at: string | null
}

export default function ActivityFeed() {
  const [items, setItems] = useState<ActivityItem[]>([])
  const [loading, setLoading] = useState(false)
  const [nextOffset, setNextOffset] = useState<number | null>(0)
  const pageSize = 20

  const loadPage = async (offset = 0) => {
    setLoading(true)
    try {
      const res = await api.get(`/api/activity?limit=${pageSize}&offset=${offset}`)
      const data = res.data
      if (offset === 0) setItems(data.items)
      else setItems((prev) => [...prev, ...data.items])
      setNextOffset(data.next_offset)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadPage(0)
  }, [])

  return (
    <div className="bg-white rounded shadow p-4">
      <h2 className="font-semibold mb-2">Recent Activity</h2>
      {loading && items.length === 0 ? (
        <div>Loading activity...</div>
      ) : items && items.length ? (
        <>
          <ul className="text-sm">
            {items.map((a) => (
              <li key={a.id} className="py-1 border-b last:border-b-0">
                <div className="flex justify-between">
                  <div>
                    <span className="font-medium">{a.action}</span>
                    {a.subject_type ? <span className="ml-2 text-gray-500">· {a.subject_type}</span> : null}
                  </div>
                  <div className="text-gray-400">{a.created_at ? new Date(a.created_at).toLocaleString() : ''}</div>
                </div>
                {a.details ? <div className="text-gray-600 text-xs mt-1">{JSON.stringify(a.details)}</div> : null}
              </li>
            ))}
          </ul>
          {nextOffset !== null ? (
            <div className="mt-2 text-center">
              <button className="px-3 py-1 bg-cyber-teal text-white rounded" onClick={() => loadPage(nextOffset)} disabled={loading}>
                {loading ? 'Loading...' : 'Load more'}
              </button>
            </div>
          ) : null}
        </>
      ) : (
        <div className="text-sm text-gray-500">No recent activity.</div>
      )}
    </div>
  )
}
