import FileUpload from '../components/FileUpload'
import FileList from '../components/FileList'
import ActivityFeed from '../components/ActivityFeed'

export default function Dashboard() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2">
          <div className="mb-4">
            <FileUpload />
          </div>
          <div>
            <FileList />
          </div>
        </div>
        <div>
          <ActivityFeed />
        </div>
      </div>
    </div>
  )
}
