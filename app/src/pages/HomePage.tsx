import { Link } from 'react-router-dom'
import styles from './HomePage.module.css'

export function HomePage() {
  return (
    <div className={styles.page}>
      <section className={styles.hero} aria-labelledby="home-title">
        <p className={styles.product}>ECG Second Look</p>
        <h1 id="home-title" className={styles.headline}>
          Practice lead vectors offline. Digitize printed ECGs with inspectable
          evidence when that pipeline is ready.
        </h1>
        <p className={styles.support}>
          A solo prototype for clinicians who need clear teaching mechanics and
          honest failure states, not a diagnostic claim.
        </p>
        <div className={styles.actions}>
          <Link className={styles.primary} to="/training">
            Open Training
          </Link>
          <Link className={styles.secondary} to="/second-look">
            Open Second Look
          </Link>
        </div>
      </section>

      <section className={styles.status} aria-labelledby="status-title">
        <h2 id="status-title" className={styles.statusTitle}>
          What this build includes
        </h2>
        <ul className={styles.statusList}>
          <li>
            <strong>Working:</strong> offline frontal-plane vector lesson; local
            Second Look quality checks, page-corner editing, 3×4 lead-region
            proposal, and single-lead trace extraction with failure states.
          </li>
          <li>
            <strong>Not built yet:</strong> multi-lead batch extraction, feature
            measurement, and prototype pattern rules.
          </li>
        </ul>
      </section>
    </div>
  )
}
