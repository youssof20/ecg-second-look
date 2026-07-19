import { useEffect, useState } from 'react'
import styles from './OfflineBanner.module.css'

export function OfflineBanner() {
  const [online, setOnline] = useState(
    typeof navigator === 'undefined' ? true : navigator.onLine,
  )

  useEffect(() => {
    function onOnline() {
      setOnline(true)
    }
    function onOffline() {
      setOnline(false)
    }
    window.addEventListener('online', onOnline)
    window.addEventListener('offline', onOffline)
    return () => {
      window.removeEventListener('online', onOnline)
      window.removeEventListener('offline', onOffline)
    }
  }, [])

  if (online) return null

  return (
    <p className={styles.banner} role="status">
      You are offline. Training still works from the installed app. Second Look
      needs the local analysis service on this machine.
    </p>
  )
}
