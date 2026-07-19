import styles from './OriginalCorrectedCompare.module.css'

interface OriginalCorrectedCompareProps {
  originalUrl: string
  correctedUrl: string
  note: string
}

export function OriginalCorrectedCompare({
  originalUrl,
  correctedUrl,
  note,
}: OriginalCorrectedCompareProps) {
  return (
    <section className={styles.section} aria-labelledby="compare-heading">
      <h2 id="compare-heading" className={styles.title}>
        Original and corrected
      </h2>
      <p className={styles.note}>{note}</p>
      <div className={styles.grid}>
        <figure className={styles.figure}>
          <figcaption>Original upload</figcaption>
          <img src={originalUrl} alt="Original ECG photograph before correction" />
        </figure>
        <figure className={styles.figure}>
          <figcaption>Corrected page</figcaption>
          <img src={correctedUrl} alt="Perspective-corrected ECG page" />
        </figure>
      </div>
    </section>
  )
}
