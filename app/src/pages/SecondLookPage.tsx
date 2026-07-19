import { useEffect, useMemo, useState, type ChangeEvent } from 'react'
import { FeatureEvidence } from '../components/FeatureEvidence'
import { ImageQualityPanel } from '../components/ImageQualityPanel'
import { LeadRegionEditor } from '../components/LeadRegionEditor'
import { OriginalCorrectedCompare } from '../components/OriginalCorrectedCompare'
import { PageCornerEditor } from '../components/PageCornerEditor'
import { TraceComparison } from '../components/TraceComparison'
import {
  analyzeLeads,
  assessQuality,
  base64ToObjectUrl,
  checkApiHealth,
  detectPage,
  extractTrace,
  fetchSampleBlob,
  proposeLayout,
  rectifyPage,
} from '../lib/secondLookApi'
import {
  SAMPLE_FILES,
  type Calibration,
  type CornerSet,
  type LayoutProposal,
  type LeadRegion,
  type MultiLeadAnalysis,
  type PageDetectionResult,
  type QualityReport,
  type TraceExtractionResult,
} from '../lib/secondLookTypes'
import styles from './SecondLookPage.module.css'

interface LoadedImage {
  file: Blob
  filename: string
  objectUrl: string
  width: number
  height: number
}

interface PageImage {
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
  const [pageImage, setPageImage] = useState<PageImage | null>(null)
  const [layout, setLayout] = useState<LayoutProposal | null>(null)
  const [regions, setRegions] = useState<LeadRegion[]>([])
  const [selectedLeadId, setSelectedLeadId] = useState('II')
  const [trace, setTrace] = useState<TraceExtractionResult | null>(null)
  const [showDebug, setShowDebug] = useState(true)
  const [analysis, setAnalysis] = useState<MultiLeadAnalysis | null>(null)
  const [paperSpeed, setPaperSpeed] = useState<25 | 50>(25)
  const [voltageGain, setVoltageGain] = useState<5 | 10>(10)
  const [calibrationConfirmed, setCalibrationConfirmed] = useState(false)

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
      if (pageImage && pageImage.objectUrl !== loaded?.objectUrl && pageImage.objectUrl !== correctedUrl) {
        URL.revokeObjectURL(pageImage.objectUrl)
      }
    }
  }, [loaded, correctedUrl, pageImage])

  const canDetect = Boolean(loaded && quality?.analysis_allowed)
  const canRectify = Boolean(loaded && corners && quality?.analysis_allowed)
  const canProposeLayout = Boolean(
    quality?.analysis_allowed && (pageImage || loaded),
  )

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
    setLayout(null)
    setRegions([])
    setTrace(null)
    setAnalysis(null)
    setError(null)
    setPageImage(null)
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
      // Flat clean pages can go straight to layout without corner correction.
      if (filename.includes('clean_12lead') && report.analysis_allowed) {
        setPageImage({ file: blob, filename, objectUrl, ...dims })
      }
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
      setLayout(null)
      setRegions([])
      setTrace(null)
      setAnalysis(null)
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
      const url = base64ToObjectUrl(result.corrected_image_base64, result.media_type)
      const bytes = Uint8Array.from(atob(result.corrected_image_base64), (c) =>
        c.charCodeAt(0),
      )
      const blob = new Blob([bytes], { type: result.media_type })
      setCorrectedUrl((current) => {
        if (current) URL.revokeObjectURL(current)
        return url
      })
      setRectifyNote(result.note)
      setPageImage({
        file: blob,
        filename: `corrected-${loaded.filename}`,
        objectUrl: url,
        width: result.output_width,
        height: result.output_height,
      })
      setLayout(null)
      setRegions([])
      setTrace(null)
      setAnalysis(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Rectification failed.')
    } finally {
      setBusy(false)
    }
  }

  async function onProposeLayout() {
    const target = pageImage ?? loaded
    if (!target) return
    setBusy(true)
    setError(null)
    try {
      if (!pageImage && loaded) {
        setPageImage(loaded)
      }
      const proposal = await proposeLayout(target.file, target.filename)
      setLayout(proposal)
      setRegions(proposal.regions)
      setSelectedLeadId('II')
      setTrace(null)
      setAnalysis(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Layout proposal failed.')
    } finally {
      setBusy(false)
    }
  }

  async function onExtractTrace() {
    const target = pageImage ?? loaded
    const region = regions.find((item) => item.lead_id === selectedLeadId)
    if (!target || !region) return
    setBusy(true)
    setError(null)
    try {
      const result = await extractTrace(target.file, target.filename, region, true)
      setTrace(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Trace extraction failed.')
    } finally {
      setBusy(false)
    }
  }

  async function onAnalyzeAll() {
    const target = pageImage ?? loaded
    if (!target || regions.length === 0) return
    setBusy(true)
    setError(null)
    try {
      const calibration: Calibration = {
        paper_speed_mm_s: paperSpeed,
        voltage_gain_mm_mv: voltageGain,
        source: calibrationConfirmed ? 'user_confirmed' : 'assumed_defaults',
        note: calibrationConfirmed
          ? 'User confirmed paper speed and voltage gain for this session.'
          : 'FOR EDUCATIONAL PROTOTYPE USE ONLY - REQUIRES CLINICAL REVIEW AND VALIDATION. Defaults assumed unless confirmed.',
      }
      const result = await analyzeLeads(target.file, target.filename, regions, calibration)
      setAnalysis(result)
      const selected = result.traces.find((item) => item.lead_id === selectedLeadId)
      if (selected) setTrace(selected)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Multi-lead analysis failed.')
    } finally {
      setBusy(false)
    }
  }

  function onChangeRegion(updated: LeadRegion) {
    setRegions((current) =>
      current.map((item) => (item.lead_id === updated.lead_id ? updated : item)),
    )
    setTrace(null)
    setAnalysis(null)
  }

  const editorImage = pageImage ?? loaded

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>Second Look</h1>
        <p className={styles.lead}>
          Prototype workflow: quality checks, page corners, 3×4 lead layout,
          multi-lead extraction, and limited feature evidence with explicit
          unable-to-assess states.
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

      {canProposeLayout ? (
        <div className={styles.actions}>
          <button
            type="button"
            className={styles.primary}
            onClick={() => void onProposeLayout()}
            disabled={busy}
          >
            Propose 3×4 lead layout
          </button>
        </div>
      ) : null}

      {layout && editorImage ? (
        <>
          <LeadRegionEditor
            imageUrl={editorImage.objectUrl}
            proposal={layout}
            regions={regions}
            selectedLeadId={selectedLeadId}
            onSelectLead={setSelectedLeadId}
            onChangeRegion={onChangeRegion}
          />

          <section className={styles.controls} aria-labelledby="cal-heading">
            <h2 id="cal-heading" className={styles.sectionTitle}>
              Calibration
            </h2>
            <p className={styles.detectNote}>
              Physical units need paper speed and voltage gain. Leave unconfirmed to
              keep values labeled as assumed defaults.
            </p>
            <div className={styles.sampleRow}>
              <label className={styles.fileLabel}>
                Paper speed
                <select
                  className={styles.fileInput}
                  value={paperSpeed}
                  onChange={(event) => setPaperSpeed(Number(event.target.value) as 25 | 50)}
                >
                  <option value={25}>25 mm/s</option>
                  <option value={50}>50 mm/s</option>
                </select>
              </label>
              <label className={styles.fileLabel}>
                Voltage gain
                <select
                  className={styles.fileInput}
                  value={voltageGain}
                  onChange={(event) => setVoltageGain(Number(event.target.value) as 5 | 10)}
                >
                  <option value={10}>10 mm/mV</option>
                  <option value={5}>5 mm/mV</option>
                </select>
              </label>
              <label className={styles.debugToggleLike}>
                <input
                  type="checkbox"
                  checked={calibrationConfirmed}
                  onChange={(event) => setCalibrationConfirmed(event.target.checked)}
                />
                I confirm these settings for this image
              </label>
            </div>
          </section>

          <div className={styles.actions}>
            <button
              type="button"
              className={styles.primary}
              onClick={() => void onExtractTrace()}
              disabled={busy}
            >
              Extract lead {selectedLeadId}
            </button>
            <button
              type="button"
              className={styles.primary}
              onClick={() => void onAnalyzeAll()}
              disabled={busy}
            >
              Extract all leads + measure features
            </button>
          </div>
        </>
      ) : null}

      {trace ? (
        <TraceComparison
          result={trace}
          showDebug={showDebug}
          onToggleDebug={setShowDebug}
        />
      ) : null}

      {analysis ? (
        <FeatureEvidence
          features={analysis.features}
          extractedCount={analysis.extracted_count}
          failedCount={analysis.failed_count}
        />
      ) : null}

      <section className={styles.next} aria-labelledby="not-yet">
        <h2 id="not-yet" className={styles.sectionTitle}>
          Not in this slice
        </h2>
        <p>
          Prototype pattern rules and highlighted rule evidence are not implemented
          yet.
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
