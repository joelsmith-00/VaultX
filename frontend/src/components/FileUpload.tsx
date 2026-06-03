import React, { useState } from 'react'
import api from '../api/axios'
import { useQueryClient } from '@tanstack/react-query'

export default function FileUpload() {
  const [file, setFile] = useState<File | null>(null)
  const qc = useQueryClient()

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return
    const fd = new FormData()
    fd.append('file', file)
    try {
      await api.post('/api/files/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      qc.invalidateQueries({ queryKey: ['files'] })
      setFile(null)
      alert('Upload successful')
    } catch (err) {
      alert('Upload failed')
    }
  }

  return (
    <form onSubmit={submit} className="flex gap-2">
      <input type="file" onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)} />
      <button className="btn-primary" type="submit">Upload</button>
    </form>
  )
}
