import { useQuery } from '@tanstack/react-query'
import api from '../api/axios'

export default function FileList() {
  const { data, isLoading } = useQuery({
    queryKey: ['files'],
    queryFn: async () => {
      const res = await api.get('/api/files')
      return res.data
    },
  })

  if (isLoading) return <div>Loading files...</div>

  return (
    <div>
      {data && data.length ? (
        <ul>
          {data.map((f: any) => (
            <li key={f.id} className="py-2">
              <a href={f.url} target="_blank" rel="noreferrer" className="text-cyber-teal">{f.filename}</a>
              <span className="text-gray-400 ml-2">({Math.round(f.size / 1024)} KB)</span>
            </li>
          ))}
        </ul>
      ) : (
        <div>No files uploaded yet.</div>
      )}
    </div>
  )
}
