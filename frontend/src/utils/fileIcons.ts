import {
  FileText, FileImage, FileVideo, FileAudio,
  FileCode, FileArchive, File
} from 'lucide-react'

export function getFileIcon(mimeType: string, extension: string) {
  if (mimeType.startsWith('image/')) return FileImage
  if (mimeType.startsWith('video/')) return FileVideo
  if (mimeType.startsWith('audio/')) return FileAudio
  if (mimeType.includes('pdf') || mimeType.includes('document') ||
      mimeType.includes('text')) return FileText
  if (['js','ts','py','html','css','json','jsx','tsx',
       'java','cpp','c','go','rs'].includes(extension)) return FileCode
  if (['zip','tar','gz','rar','7z'].includes(extension)) return FileArchive
  return File
}

export function getFileColor(mimeType: string): string {
  if (mimeType.startsWith('image/')) return '#7F5AF0'
  if (mimeType.startsWith('video/')) return '#2CB67D'
  if (mimeType.startsWith('audio/')) return '#f59e0b'
  if (mimeType.includes('pdf')) return '#ef4444'
  return '#6b7280'
}
