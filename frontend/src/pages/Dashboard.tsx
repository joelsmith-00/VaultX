import FileUpload from '../components/FileUpload'
import FileList from '../components/FileList'

export default function Dashboard() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
      <div className="mb-4">
        <FileUpload />
      </div>
      <div>
        <FileList />
      </div>
    </div>
  )
}
