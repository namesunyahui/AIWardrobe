export const API_BASE = '/api'

export function toImageUrl(path) {
  if (!path) return ''
  // 如果已经是后端代理路径，直接返回
  if (path.startsWith('/api/')) return path
  if (/^https?:\/\//i.test(path)) {
    // 替换外部 MinIO 域名为代理路径
    return path.replace('http://aiwardrobe.syhzyt.cc:9000', '/minio')
                 .replace('https://aiwardrobe.syhzyt.cc:9000', '/minio')
  }
  const normalized = path.startsWith('/') ? path : `/${path}`
  // 图片使用代理
  return normalized
}
