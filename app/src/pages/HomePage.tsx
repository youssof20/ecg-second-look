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
            <strong>Working:</strong> offline training lesson; Second Look quality,
            corners, lead regions, multi-lead extraction, features, and prototype
            pattern flags.
          </li>
          <li>
            <strong>Not built yet:</strong> accessibility polish pass and demo
            recording package.
          </li>
        </ul>
      </section>
    </div>
  )
}
