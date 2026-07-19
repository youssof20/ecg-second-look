import { VectorLesson } from '../components/VectorLesson'
import styles from './TrainingPage.module.css'

export function TrainingPage() {
  return (
    <div className={styles.page}>
      <p className={styles.banner}>
        Training mode runs entirely in the browser. No network call is required
        after the app is loaded.
      </p>
      <VectorLesson />
    </div>
  )
}
