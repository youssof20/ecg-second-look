import { useEffect, useMemo, useState, type ChangeEvent } from 'react'
import { ImageQualityPanel } from '../components/ImageQualityPanel'
import { OriginalCorrectedCompare } from '../components/OriginalCorrectedCompare'
import { PageCornerEditor } from '../components/PageCornerEditor'
import {
  assessQuality,
  checkApiHealth,
  detectPage,
  fetchSampleBlob,
  rectifyPage,
} from '../lib/secondLookApi'
import {
  SAMPLE_FILES,
  type CornerSet,
  type PageDetectionResult,
  type QualityReport,
} from '../lib/secondLookTypes'
import styles from './SecondLookPage.module.css'

interface LoadedImage {
  file: Blob
  filename: string
  objectUrl: string
  width: number
  height: number
}

export function SecondLookPage() {
  const [apiUp, setApiUp] = useState<boolean | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loaded, setLoaded] = useState<LoadedImage | null>(null)
  const [quality, setQuality] = useState<QualityReport | null>(null)
  const [detection, setDetection] = useState<PageDetectionResult | null>(null)
  const [corners, setCorners] = useState<CornerSet | null>(null)
  const [correctedUrl, setCorrectedUrl] = useState<string | null>(null)
  const [rectifyNote, setRectifyNote] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    void checkApiHealth().then((ok) => {
      if (!cancelled) setApiUp(ok)
    })
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    return () => {
      if (loaded) URL.revokeObjectURL(loaded.objectUrl)
      if (correctedUrl) URL.revokeObjectURL(correctedUrl)
    }
  }, [loaded, correctedUrl])

  const canDetect = Boolean(loaded && quality?.analysis_allowed)
  const canRectify = Boolean(loaded && corners && quality?.analysis_allowed)

  const statusText = useMemo(() => {
    if (apiUp === null) return 'Checking local analysis service…'
    if (!apiUp) {
      return 'Local analysis service is not reachable on /api. Start it before uploading.'
    }
    return 'Local analysis service is reachable. Uploads stay in memory on this machine.'
  }, [apiUp])

  async function resetDerived() {
    setQuality(null)
    setDetection(null)
    setCorners(null)
    setRectifyNote(null)
    setError(null)
    setCorrectedUrl((current) => {
      if (current) URL.revokeObjectURL(current)
      return null
    })
  }

  async function loadBlob(blob: Blob, filename: string) {
    setBusy(true)
    await resetDerived()
    try {
      const objectUrl = URL.createObjectURL(blob)
      const dims = await readImageSize(objectUrl)
      setLoaded((previous) => {
        if (previous) URL.revokeObjectURL(previous.objectUrl)
        return { file: blob, filename, objectUrl, ...dims }
      })
      const report = await assessQuality(blob, filename)
      setQuality(report)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed.')
    } finally {
      setBusy(false)
    }
  }

  async function onFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    if (!file) return
    await loadBlob(file, file.name)
    event.target.value = ''
  }

  async function onSample(path: string) {
    setBusy(true)
    setError(null)
    try {
      const sample = await fetchSampleBlob(path)
      await loadBlob(sample.blob, sample.filename)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sample load failed.')
      setBusy(false)
    }
  }

  async function onDetect() {
    if (!loaded) return
    setBusy(true)
    setError(null)
    try {
      const result = await detectPage(loaded.file, loaded.filename)
      setDetection(result)
      setCorners(result.corners)
      setCorrectedUrl((current) => {
        if (current) URL.revokeObjectURL(current)
        return null
      })
      setRectifyNote(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Page detection failed.')
    } finally {
      setBusy(false)
    }
  }

  async function onRectify() {
    if (!loaded || !corners) return
    setBusy(true)
    setError(null)
    try {
      const result = await rectifyPage(loaded.file, loaded.filename, corners)
      const bytes = Uint8Array.from(atob(result.corrected_image_base64), (c) =>
        c.charCodeAt(0),
      )
      const blob = new Blob([bytes], { type: result.media_type })
      const url = URL.createObjectURL(blob)
      setCorrectedUrl((current) => {
        if (current) URL.revokeObjectURL(current)
        return url
      })
      setRectifyNote(result.note)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Rectification failed.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>Second Look</h1>
        <p className={styles.lead}>
          Prototype workflow for photographed ECG pages: quality checks, corner
          confirmation, then an inspectable original/corrected comparison.
        </p>
        <p className={styles.disclaimer}>
          Research and education only. Not a diagnostic system. Do not upload
          identifiable clinical material.
        </p>
        <p className={apiUp ? styles.serviceOk : styles.serviceBad} role="status">
          {statusText}
        </p>
      </header>

      <section className={styles.controls} aria-labelledby="input-heading">
        <h2 id="input-heading" className={styles.sectionTitle}>
          Input
        </h2>
        <label className={styles.fileLabel}>
          <span>Choose image</span>
          <input
            className={styles.fileInput}
            type="file"
            accept="image/png,image/jpeg,image/webp"
            capture="environment"
            onChange={onFileChange}
            disabled={busy || apiUp === false}
          />
        </label>

        <div className={styles.samples}>
          <p className={styles.samplesLabel}>Or use a synthetic sample:</p>
          <div className={styles.sampleRow}>
            {SAMPLE_FILES.map((sample) => (
              <button
                key={sample.id}
                type="button"
                className={styles.sampleButton}
                disabled={busy || apiUp === false}
                onClick={() => void onSample(sample.path)}
              >
                {sample.label}
              </button>
            ))}
          </div>
        </div>
      </section>

      {error ? (
        <p className={styles.error} role="alert">
          {error}
        </p>
      ) : null}

      {busy ? (
        <p className={styles.busy} role="status">
          Working…
        </p>
      ) : null}

      {quality ? <ImageQualityPanel report={quality} /> : null}

      {canDetect ? (
        <div className={styles.actions}>
          <button
            type="button"
            className={styles.primary}
            onClick={() => void onDetect()}
            disabled={busy}
          >
            Detect page corners
          </button>
        </div>
      ) : null}

      {loaded && corners ? (
        <>
          {detection ? (
            <p className={styles.detectNote}>
              Detection: <strong>{detection.status}</strong>. {detection.detail}
            </p>
          ) : null}
          <PageCornerEditor
            imageUrl={loaded.objectUrl}
            imageWidth={loaded.width}
            imageHeight={loaded.height}
            corners={corners}
            onChange={setCorners}
          />
          <div className={styles.actions}>
            <button
              type="button"
              className={styles.primary}
              onClick={() => void onRectify()}
              disabled={busy || !canRectify}
            >
              Apply confirmed corners
            </button>
          </div>
        </>
      ) : null}

      {loaded && correctedUrl && rectifyNote ? (
        <OriginalCorrectedCompare
          originalUrl={loaded.objectUrl}
          correctedUrl={correctedUrl}
          note={rectifyNote}
        />
      ) : null}

      <section className={styles.next} aria-labelledby="not-yet">
        <h2 id="not-yet" className={styles.sectionTitle}>
          Not in this slice
        </h2>
        <p>
          Lead-region editing, trace extraction, feature measurement, and prototype
          pattern rules are not implemented yet.
        </p>
      </section>
    </div>
  )
}

function readImageSize(url: string): Promise<{ width: number; height: number }> {
  return new Promise((resolve, reject) => {
    const image = new Image()
    image.onload = () => resolve({ width: image.naturalWidth, height: image.naturalHeight })
    image.onerror = () => reject(new Error('Could not read image dimensions.'))
    image.src = url
  })
}
