import { create } from 'zustand'
import type { FileItem, Folder } from '../types'

interface FileState {
  files: FileItem[]
  folders: Folder[]
  currentFolderId: string | null
  selectedFiles: string[]
  viewMode: 'grid' | 'list'
  searchQuery: string
  isUploading: boolean
  uploadProgress: Record<string, number>
  setFiles: (files: FileItem[]) => void
  setFolders: (folders: Folder[]) => void
  setCurrentFolder: (folderId: string | null) => void
  toggleFileSelect: (fileId: string) => void
  clearSelection: () => void
  setViewMode: (mode: 'grid' | 'list') => void
  setSearchQuery: (query: string) => void
  setUploading: (uploading: boolean) => void
  setUploadProgress: (fileId: string, progress: number) => void
  clearUploadProgress: (fileId: string) => void
}

export const useFileStore = create<FileState>((set) => ({
  files: [],
  folders: [],
  currentFolderId: null,
  selectedFiles: [],
  viewMode: 'grid',
  searchQuery: '',
  isUploading: false,
  uploadProgress: {},
  setFiles: (files) => set({ files }),
  setFolders: (folders) => set({ folders }),
  setCurrentFolder: (folderId) => set({
    currentFolderId: folderId,
    selectedFiles: []
  }),
  toggleFileSelect: (fileId) => set((state) => ({
    selectedFiles: state.selectedFiles.includes(fileId)
      ? state.selectedFiles.filter(id => id !== fileId)
      : [...state.selectedFiles, fileId]
  })),
  clearSelection: () => set({ selectedFiles: [] }),
  setViewMode: (mode) => set({ viewMode: mode }),
  setSearchQuery: (query) => set({ searchQuery: query }),
  setUploading: (uploading) => set({ isUploading: uploading }),
  setUploadProgress: (fileId, progress) => set((state) => ({
    uploadProgress: { ...state.uploadProgress, [fileId]: progress }
  })),
  clearUploadProgress: (fileId) => set((state) => {
    const newProgress = { ...state.uploadProgress }
    delete newProgress[fileId]
    return { uploadProgress: newProgress }
  }),
}))
