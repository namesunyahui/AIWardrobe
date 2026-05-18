export const API_BASE = '/api'

export function toImageUrl(path) {
  if (!path) return ''
  if (/^https?:\/\//i.test(path)) return path
  const normalized = path.startsWith('/') ? path : `/${path}`
  // 图片使用代理
  return normalized
}
