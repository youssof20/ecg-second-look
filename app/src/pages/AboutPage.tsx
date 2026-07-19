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
          Second Look (not yet available) will digitize photographs of printed
          ECGs and show inspectable measurements with prototype pattern flags.
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
            <strong>Second Look</strong>: local image quality checks and page
            correction with inspectable original/corrected comparison. Lead
            extraction and pattern rules are not implemented yet.
          </li>
        </ul>
      </section>

      <section aria-labelledby="privacy">
        <h2 id="privacy" className={styles.h2}>
          Privacy
        </h2>
        <p>
          Do not upload images that contain patient names, dates of birth, medical
          record numbers, or hospital identifiers. Future demos will process files
          locally where possible and will not store uploads by default.
        </p>
      </section>

      <section aria-labelledby="license">
        <h2 id="license" className={styles.h2}>
          License
        </h2>
        <p>
          Software is MIT-licensed unless a file states otherwise. Sample data, if
          added later, carries its own provenance notes.
        </p>
      </section>
    </article>
  )
}
