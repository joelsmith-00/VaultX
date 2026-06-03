// VaultX TypeScript Types

export interface User {
  id: string
  email: string
  username: string
  avatar_url?: string
  is_verified: boolean
  storage_used: number
  storage_limit: number
  created_at: string
}

export interface FileItem {
  id: string
  name: string
  original_name: string
  size: number
  mime_type: string
  extension: string
  is_starred: boolean
  folder_id?: string
  created_at: string
  download_url?: string
}

export interface Folder {
  id: string
  name: string
  parent_id?: string
  color?: string
  is_starred: boolean
  created_at: string
  file_count?: number
  subfolder_count?: number
}

export interface Share {
  id: string
  token: string
  permission: 'view' | 'download'
  expires_at?: string
  max_downloads?: number
  download_count: number
  scan_count: number
  is_active: boolean
  created_at: string
  qr_url?: string
  share_url: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface ApiError {
  detail: string
  status_code: number
}

export interface DashboardStats {
  total_files: number
  total_folders: number
  storage_used: number
  storage_limit: number
  storage_percent: number
  active_shares: number
  recent_files: FileItem[]
  storage_by_type: {
    images: number
    documents: number
    videos: number
    audio: number
    archives: number
    other: number
  }
}
