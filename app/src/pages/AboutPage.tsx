import styles from './AboutPage.module.css'

export function AboutPage() {
  return (
    <article className={styles.page}>
      <h1 className={styles.title}>About</h1>

      <section aria-labelledby="intent">
        <h2 id="intent" className={styles.h2}>
          Intended use
        </h2>
        <p>
          ECG Second Look is an educational and research prototype. Training mode
          teaches how a simplified cardiac vector projects onto standard leads.
          Second Look digitizes photographs of printed ECGs locally and shows
          inspectable measurements with prototype pattern flags.
        </p>
        <p>
          It is not a medical device, not cleared for clinical use, and not a
          replacement for a clinician. It must not be used to diagnose, exclude
          emergencies, or guide discharge decisions.
        </p>
      </section>

      <section aria-labelledby="modes">
        <h2 id="modes" className={styles.h2}>
          Modes
        </h2>
        <ul>
          <li>
            <strong>Training</strong>: offline vector projection lesson with
            stated model assumptions.
          </li>
          <li>
            <strong>Second Look</strong>: local quality checks, page correction,
            lead regions, trace extraction, limited features, and prototype
            pattern flags with explicit unable-to-assess states.
          </li>
        </ul>
      </section>

      <section aria-labelledby="offline">
        <h2 id="offline" className={styles.h2}>
          Offline
        </h2>
        <p>
          Training can run offline after the app is installed or cached. Second
          Look needs the local Python analysis service on the same machine. See{' '}
          <code>docs/offline.md</code>.
        </p>
      </section>

      <section aria-labelledby="privacy">
        <h2 id="privacy" className={styles.h2}>
          Privacy
        </h2>
        <p>
          Do not upload images that contain patient names, dates of birth, medical
          record numbers, or hospital identifiers. Uploads are processed in memory
          and are not stored by default.
        </p>
      </section>

      <section aria-labelledby="license">
        <h2 id="license" className={styles.h2}>
          License
        </h2>
        <p>
          Software is MIT-licensed unless a file states otherwise. Sample data
          carries its own provenance notes under <code>samples/</code>.
        </p>
      </section>
    </article>
  )
}
