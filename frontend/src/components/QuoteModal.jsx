import { Fragment, useEffect, useState } from "react";

const STEPS = [
  { id: 1, label: "Type de projet" },
  { id: 2, label: "Fonctionnalités" },
  { id: 3, label: "Vos coordonnées" },
];

const initialForm = {
  project_type: "",
  features: [],
  name: "",
  email: "",
  phone: "",
  company: "",
  description: "",
  budget: "",
  deadline: "",
};

export default function QuoteModal({ onClose }) {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState(initialForm);
  const [projectTypes, setProjectTypes] = useState([]);
  const [featureGroups, setFeatureGroups] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [submitted, setSubmitted] = useState(null);

  useEffect(() => {
    fetch("/api/project-types").then((r) => r.json()).then(setProjectTypes).catch(() => {});
    fetch("/api/features").then((r) => r.json()).then(setFeatureGroups).catch(() => {});
  }, []);

  useEffect(() => {
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [onClose]);

  const toggleFeature = (slug) => {
    setForm((f) => ({
      ...f,
      features: f.features.includes(slug)
        ? f.features.filter((s) => s !== slug)
        : [...f.features, slug],
    }));
  };

  const update = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const canNext =
    (step === 1 && !!form.project_type) ||
    (step === 2) ||
    (step === 3 && form.name.trim() && form.email.trim());

  const submit = async () => {
    setLoading(true); setError(null);
    try {
      const r = await fetch("/api/quotations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await r.json();
      if (r.ok && data.ok) {
        setSubmitted(data.quotation);
      } else {
        setError(data.error || "Erreur lors de l'envoi.");
      }
    } catch {
      setError("Connexion impossible au serveur.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h2>{submitted ? "Demande envoyée" : "Demander un devis"}</h2>
          <button className="close" onClick={onClose} aria-label="Fermer">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><path d="M6 6l12 12M18 6l-12 12"/></svg>
          </button>
        </div>

        {!submitted && (
          <div className="stepper">
            {STEPS.map((s, i) => (
              <Fragment key={s.id}>
                <div className={`step-pill ${step === s.id ? "active" : step > s.id ? "done" : ""}`}>
                  <span className="n">{step > s.id ? "✓" : s.id}</span>
                  {s.label}
                </div>
                {i < STEPS.length - 1 && <div className="bar" />}
              </Fragment>
            ))}
          </div>
        )}

        <div className="modal-body">
          {submitted ? (
            <div className="success-state">
              <div className="icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><path d="m5 12 5 5L20 7"/></svg>
              </div>
              <h3>Merci {submitted.name} !</h3>
              <p className="helper">
                Votre demande <b>#{submitted.id}</b> a bien été enregistrée.<br />
                Nous revenons vers vous sous 48h ouvrées.
              </p>
              {submitted.pdf_url && (
                <a
                  className="btn btn-primary"
                  href={submitted.pdf_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  download={`devis-${submitted.id}.pdf`}
                  style={{ marginBottom: 10, textDecoration: "none", display: "inline-block" }}
                >
                  Télécharger le récapitulatif PDF
                </a>
              )}
              <button className="btn btn-ghost" onClick={onClose}>Fermer</button>
            </div>
          ) : step === 1 ? (
            <>
              <h3>Quel type de projet souhaitez-vous réaliser ?</h3>
              <p className="helper">Sélectionnez la catégorie qui correspond le mieux à votre besoin.</p>
              <div className="ptype-grid">
                {projectTypes.map((p) => (
                  <button
                    key={p.slug}
                    type="button"
                    className={`ptype ${form.project_type === p.slug ? "selected" : ""}`}
                    onClick={() => setForm({ ...form, project_type: p.slug })}
                  >
                    <b>{p.name}</b>
                    <span>{p.description}</span>
                  </button>
                ))}
                {projectTypes.length === 0 && <p className="helper">Chargement…</p>}
              </div>
            </>
          ) : step === 2 ? (
            <>
              <h3>Quelles fonctionnalités souhaitez-vous ?</h3>
              <p className="helper">Cochez ce qui s'applique. Vous pouvez tout préciser à l'étape suivante.</p>
              {Object.entries(featureGroups).map(([cat, list]) => (
                <div className="feature-group" key={cat}>
                  <div className="cat">{cat}</div>
                  <div className="feature-grid">
                    {list.map((f) => {
                      const sel = form.features.includes(f.slug);
                      return (
                        <button
                          key={f.slug}
                          type="button"
                          className={`feature ${sel ? "selected" : ""}`}
                          onClick={() => toggleFeature(f.slug)}
                        >
                          <span className="check">
                            {sel && (
                              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="m5 12 5 5L20 7"/></svg>
                            )}
                          </span>
                          <div className="label">
                            <b>{f.name}</b>
                            <small>{f.description}</small>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </>
          ) : (
            <>
              <h3>Vos coordonnées</h3>
              <p className="helper">Pour vous répondre avec une proposition adaptée.</p>
              <div className="field-row">
                <div className="field">
                  <label>Nom complet *</label>
                  <input value={form.name} onChange={update("name")} placeholder="Votre nom" required />
                </div>
                <div className="field">
                  <label>Société</label>
                  <input value={form.company} onChange={update("company")} placeholder="Votre entreprise" />
                </div>
              </div>
              <div className="field-row">
                <div className="field">
                  <label>E-mail *</label>
                  <input type="email" value={form.email} onChange={update("email")} placeholder="vous@entreprise.com" required />
                </div>
                <div className="field">
                  <label>Téléphone</label>
                  <input value={form.phone} onChange={update("phone")} placeholder="+225 ..." />
                </div>
              </div>
              <div className="field-row">
                <div className="field">
                  <label>Budget envisagé</label>
                  <select value={form.budget} onChange={update("budget")}>
                    <option value="">— Sélectionner —</option>
                    <option>Moins de 1M FCFA</option>
                    <option>1M – 5M FCFA</option>
                    <option>5M – 15M FCFA</option>
                    <option>15M – 50M FCFA</option>
                    <option>Plus de 50M FCFA</option>
                    <option>À discuter</option>
                  </select>
                </div>
                <div className="field">
                  <label>Échéance souhaitée</label>
                  <select value={form.deadline} onChange={update("deadline")}>
                    <option value="">— Sélectionner —</option>
                    <option>Moins d'un mois</option>
                    <option>1 à 3 mois</option>
                    <option>3 à 6 mois</option>
                    <option>Plus de 6 mois</option>
                    <option>Pas de contrainte</option>
                  </select>
                </div>
              </div>
              <div className="field">
                <label>Décrivez votre projet</label>
                <textarea value={form.description} onChange={update("description")} placeholder="Contexte, objectifs, contraintes..." />
              </div>
              {error && <div className="form-msg err">{error}</div>}
            </>
          )}
        </div>

        {!submitted && (
          <div className="modal-foot">
            <div className="summary">
              {step === 2 && (
                <>{form.features.length} fonctionnalité{form.features.length > 1 ? "s" : ""} sélectionnée{form.features.length > 1 ? "s" : ""}</>
              )}
              {step === 1 && form.project_type && (
                <>Projet : <b>{projectTypes.find((p) => p.slug === form.project_type)?.name}</b></>
              )}
            </div>
            <div className="actions">
              {step > 1 && (
                <button className="btn btn-ghost" onClick={() => setStep(step - 1)} disabled={loading}>
                  Précédent
                </button>
              )}
              {step < 3 ? (
                <button className="btn btn-primary" onClick={() => setStep(step + 1)} disabled={!canNext}>
                  Suivant
                </button>
              ) : (
                <button className="btn btn-primary" onClick={submit} disabled={loading || !canNext}>
                  {loading ? "Envoi..." : "Envoyer la demande"}
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
