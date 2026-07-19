import type {
  PageDetectionResult,
  QualityReport,
  RectifyResponse,
  CornerSet,
} from './secondLookTypes'

async function readError(response: Response): Promise<string> {
  try {
    const body = await response.json()
    if (typeof body.detail === 'string') return body.detail
    if (body.detail?.message) return body.detail.message
    return JSON.stringify(body.detail ?? body)
  } catch {
    return response.statusText || `Request failed (${response.status})`
  }
}

export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch('/api/v1/health')
    return response.ok
  } catch {
    return false
  }
}

export async function assessQuality(file: Blob, filename: string): Promise<QualityReport> {
  const form = new FormData()
  form.append('file', file, filename)
  const response = await fetch('/api/v1/quality', { method: 'POST', body: form })
  if (!response.ok) throw new Error(await readError(response))
  return response.json() as Promise<QualityReport>
}

export async function detectPage(file: Blob, filename: string): Promise<PageDetectionResult> {
  const form = new FormData()
  form.append('file', file, filename)
  const response = await fetch('/api/v1/detect-page', { method: 'POST', body: form })
  if (!response.ok) throw new Error(await readError(response))
  return response.json() as Promise<PageDetectionResult>
}

export async function rectifyPage(
  file: Blob,
  filename: string,
  corners: CornerSet,
): Promise<RectifyResponse> {
  const form = new FormData()
  form.append('file', file, filename)
  form.append('corners_json', JSON.stringify({ corners }))
  const response = await fetch('/api/v1/rectify', { method: 'POST', body: form })
  if (!response.ok) throw new Error(await readError(response))
  return response.json() as Promise<RectifyResponse>
}

export async function fetchSampleBlob(path: string): Promise<{ blob: Blob; filename: string }> {
  const response = await fetch(path)
  if (!response.ok) {
    throw new Error(`Could not load sample ${path}. Is the API running with /samples mounted?`)
  }
  const blob = await response.blob()
  const filename = path.split('/').pop() ?? 'sample.png'
  return { blob, filename }
}
