import { useQuery, useQueryClient } from '@tanstack/react-query'
import api from '../api/axios'

export default function ShareList() {
  const qc = useQueryClient()
  const { data, isLoading } = useQuery({
    queryKey: ['my_shares'],
    queryFn: async () => (await api.get('/api/shares/me')).data,
  })

  const revoke = async (id: string) => {
    await api.post(`/api/shares/${id}/revoke`)
    qc.invalidateQueries({ queryKey: ['my_shares'] })
    qc.invalidateQueries({ queryKey: ['activity'] })
  }

  if (isLoading) return <div>Loading shares...</div>

  return (
    <div className="bg-white rounded shadow p-4 mt-4">
      <h3 className="font-semibold mb-2">Your Shares</h3>
      {data && Array.isArray(data) && data.length ? (
        <ul>
          {data.map((s: any) => (
            <li key={s.id} className="flex justify-between items-center py-1 border-b last:border-b-0">
              <div>
                <div className="font-medium">{s.token}</div>
                <div className="text-xs text-gray-500">Uses: {s.uses}{s.max_uses ? ` / ${s.max_uses}` : ''} {s.is_active ? '' : '(revoked)'}</div>
              </div>
              <div>
                {s.is_active ? <button className="px-2 py-1 bg-red-500 text-white rounded" onClick={() => revoke(s.id)}>Revoke</button> : null}
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <div className="text-sm text-gray-500">No shares created yet.</div>
      )}
    </div>
  )
}
