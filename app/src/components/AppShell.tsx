import { NavLink, Outlet } from 'react-router-dom'
import { OfflineBanner } from './OfflineBanner'
import styles from './AppShell.module.css'

const NAV = [
  { to: '/', label: 'Home', end: true },
  { to: '/training', label: 'Training', end: false },
  { to: '/second-look', label: 'Second Look', end: false },
  { to: '/about', label: 'About', end: false },
] as const

export function AppShell() {
  return (
    <div className={styles.shell}>
      <a className={styles.skip} href="#main">
        Skip to content
      </a>
      <OfflineBanner />
      <header className={styles.header}>
        <div className={styles.brandBlock}>
          <p className={styles.brand}>ECG Second Look</p>
          <p className={styles.tag}>
            Offline training and inspectable ECG image prototype
          </p>
        </div>
        <nav className={styles.nav} aria-label="Primary">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                isActive ? `${styles.navLink} ${styles.navLinkActive}` : styles.navLink
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>

      <main id="main" className={styles.main} tabIndex={-1}>
        <Outlet />
      </main>

      <footer className={styles.footer}>
        <p>
          Educational and research prototype. Not a medical device. Not for
          patient-care decisions.
        </p>
      </footer>
    </div>
  )
}
