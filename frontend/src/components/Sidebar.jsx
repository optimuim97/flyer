const WHATSAPP_NUMBER = "2250779920203";
const EMAIL = "contact@softara.com";

const SERVICES = [
  "Applications sur mesure",
  "Boutiques e-commerce",
  "Solutions e-paiement",
  "Sécurité & conformité",
  "Support & maintenance",
];

const Icon = {
  whatsapp: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M20.5 3.5A11 11 0 0 0 3.3 17l-1.3 4.8 4.9-1.3a11 11 0 0 0 16.7-9.3 11 11 0 0 0-3.1-7.7Z" />
    </svg>
  ),
  mail: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <rect x="3" y="5" width="18" height="14" rx="2" />
      <path d="m3 7 9 7 9-7" />
    </svg>
  ),
  link: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1" />
      <path d="M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1" />
    </svg>
  ),
  arrow: (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M5 12h14" />
      <path d="M13 5l7 7-7 7" />
    </svg>
  ),
  sun: (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="4"/>
      <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>
    </svg>
  ),
  moon: (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
    </svg>
  ),
};

export default function Sidebar({ onOpenQuote, theme, onToggleTheme }) {
  return (
    <aside className="sidebar">
      <div className="brand-row">
        <span className="brand-mark">S</span>
        <div>
          <div className="name">Softara</div>
          <div className="tag">software · sécurité</div>
        </div>
      </div>

      <div className="sb-section">
        <div className="sb-title">// contact</div>
        <div>
          <a className="contact-link" href={`https://wa.me/${WHATSAPP_NUMBER}`} target="_blank" rel="noreferrer">
            <span className="ci-ico">{Icon.whatsapp}</span>
            <div>
              <b>whatsapp</b>
              <span>+225 07 79 92 02 03</span>
            </div>
          </a>
          <a className="contact-link" href={`mailto:${EMAIL}`}>
            <span className="ci-ico">{Icon.mail}</span>
            <div>
              <b>email</b>
              <span>{EMAIL}</span>
            </div>
          </a>
          <a className="contact-link" href="https://questions.softara.tech/q/1" target="_blank" rel="noreferrer">
            <span className="ci-ico">{Icon.link}</span>
            <div>
              <b>softra e-commerce questions</b>
              <span>questions.softara.tech</span>
            </div>
          </a>
        </div>
      </div>

      <div className="sb-section">
        <div className="sb-title">// ce que nous faisons</div>
        <div className="services-list">
          {SERVICES.map((s) => (
            <div className="service-mini" key={s}>
              <span className="dot" />
              <span>{s}</span>
            </div>
          ))}
        </div>
      </div>

      <button className="sb-cta" onClick={onOpenQuote}>
        Demander un devis {Icon.arrow}
      </button>

      <div className="sb-footer">
        <span>© {new Date().getFullYear()} softara</span>
        <button className="theme-toggle" onClick={onToggleTheme} title="Changer de thème">
          {theme === "dark" ? Icon.sun : Icon.moon}
          {theme === "dark" ? "Light" : "Dark"}
        </button>
      </div>
    </aside>
  );
}
