const FEATURES = [
  {
    title: "Applications sur mesure",
    desc: "Web, mobile et logiciels métiers conçus pour vos process.",
    icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><rect x="3" y="4" width="18" height="14" rx="2"/><path d="M8 20h8M12 18v2"/></svg>,
  },
  {
    title: "E-commerce",
    desc: "Catalogue, panier, livraison, statistiques — clé en main.",
    icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><circle cx="9" cy="20" r="1.4"/><circle cx="18" cy="20" r="1.4"/><path d="M3 4h2l2.5 12h12l2-8H7"/></svg>,
  },
  {
    title: "E-paiement",
    desc: "Mobile Money, cartes, paiement par lien — sécurisé.",
    icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><rect x="2" y="6" width="20" height="13" rx="2"/><path d="M2 10h20M6 15h4"/></svg>,
  },
  {
    title: "Sécurité by design",
    desc: "Chiffrement, 2FA, audits, conformité dès la conception.",
    icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><path d="M12 2 4 6v6c0 5 3.5 8.5 8 10 4.5-1.5 8-5 8-10V6z"/><path d="m9 12 2 2 4-4"/></svg>,
  },
  {
    title: "Intégrations & API",
    desc: "Connexions avec vos outils (CRM, ERP, comptabilité).",
    icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><path d="M9 2v6M15 2v6M9 22v-4M15 22v-4M2 9h6M2 15h6M22 9h-4M22 15h-4"/><rect x="8" y="8" width="8" height="8" rx="1"/></svg>,
  },
  {
    title: "Support & maintenance",
    desc: "Supervision, mises à jour et accompagnement continu.",
    icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z"/></svg>,
  },
];

export default function Main({ onOpenQuote }) {
  return (
    <main className="main">
      <section className="hero-block">
        <span className="eyebrow">Solutions logicielles sur mesure</span>
        <h1 className="hero-title">
          Des applications <span>sûres, fiables</span><br />
          faites pour vos clients.
        </h1>
        <p className="hero-lead">
          Softara conçoit des applications, plateformes e-commerce et solutions
          d'e-paiement pour les entreprises qui placent la confiance et la sécurité
          au cœur de leur croissance.
        </p>
        <div className="hero-actions">
          <button className="btn btn-primary" onClick={onOpenQuote}>
            Demander un devis
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="M13 5l7 7-7 7"/></svg>
          </button>
          <a className="btn btn-whatsapp" href="https://wa.me/2250779920203" target="_blank" rel="noreferrer">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M20.5 3.5A11 11 0 0 0 3.3 17l-1.3 4.8 4.9-1.3a11 11 0 0 0 16.7-9.3 11 11 0 0 0-3.1-7.7Z"/></svg>
            WhatsApp
          </a>
        </div>
      </section>

      <section>
        <div className="section-head">
          <h2>Ce que nous concevons</h2>
          <p>Des solutions adaptées à vos enjeux, du code au paiement.</p>
        </div>
        <div className="cards-grid">
          {FEATURES.map((f) => (
            <article className="card" key={f.title}>
              <div className="ico">{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </article>
          ))}
        </div>
      </section>

      <div className="main-foot">
        <span>© {new Date().getFullYear()} Softara</span>
        <a href="https://questions.softara.tech" target="_blank" rel="noreferrer">questions.softara.tech →</a>
      </div>
    </main>
  );
}
