import { Link } from 'react-router-dom'
import styles from './SecondLookPage.module.css'

export function SecondLookPage() {
  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Second Look</h1>
      <p className={styles.lead}>
        Photograph-to-evidence analysis is not implemented in this build.
      </p>

      <section className={styles.panel} aria-labelledby="planned-heading">
        <h2 id="planned-heading" className={styles.panelTitle}>
          Planned workflow
        </h2>
        <ol className={styles.steps}>
          <li>Upload or capture a printed 12-lead ECG image.</li>
          <li>Review image-quality checks and capture guidance.</li>
          <li>Confirm page corners after perspective correction.</li>
          <li>Confirm lead regions for one supported layout.</li>
          <li>Compare extracted traces with the source image.</li>
          <li>Inspect measurements, prototype pattern flags, and limitations.</li>
        </ol>
      </section>

      <p className={styles.note}>
        Until that pipeline lands, use{' '}
        <Link to="/training">Training</Link> for the vector lesson. Do not upload
        identifiable clinical material into any future public demo.
      </p>
    </div>
  )
}
