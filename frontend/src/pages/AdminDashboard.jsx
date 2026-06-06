import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";

const STATUS_LABELS = {
  nouveau: "Nouveau",
  "en-cours": "En cours",
  traite: "Traité",
  archive: "Archivé",
};

function formatDate(iso) {
  if (!iso) return "-";
  const d = new Date(iso);
  return d.toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit", year: "numeric" })
    + " " + d.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });
}

const PER_PAGE = 10;

export default function AdminDashboard() {
  const [quotations, setQuotations] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(null);
  const [downloading, setDownloading] = useState(null);
  const navigate = useNavigate();
  const token = localStorage.getItem("admin-token");

  const fetchQuotations = useCallback(async () => {
    if (!token) { navigate("/admin"); return; }
    setLoading(true);
    try {
      const res = await fetch(`/api/admin/quotations?page=${page}&per_page=${PER_PAGE}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.status === 401) { navigate("/admin"); return; }
      const data = await res.json();
      // compat : ancienne API renvoyait un tableau
      if (Array.isArray(data)) {
        setQuotations(data);
        setTotal(data.length);
        setPages(1);
      } else {
        setQuotations(Array.isArray(data.items) ? data.items : []);
        setTotal(data.total ?? 0);
        setPages(data.pages ?? 1);
      }
    } catch {
      setError("Erreur de chargement des devis");
    } finally {
      setLoading(false);
    }
  }, [token, navigate, page]);

  useEffect(() => { fetchQuotations(); }, [fetchQuotations]);

  useEffect(() => {
    if (selected === null) return;
    const onKey = (e) => e.key === "Escape" && setSelected(null);
    window.addEventListener("keydown", onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [selected]);

  function handleLogout() {
    localStorage.removeItem("admin-token");
    navigate("/admin");
  }

  async function handleDownload(q) {
    setDownloading(q.id);
    try {
      const res = await fetch(`/api/admin/quotations/${q.id}/pdf`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) { alert("Erreur lors du téléchargement"); return; }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `devis-${q.id}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch {
      alert("Erreur lors du téléchargement");
    } finally {
      setDownloading(null);
    }
  }

  return (
    <div className="admin-wrap">
      <header className="admin-header">
        <div className="admin-header-brand">
          <span className="admin-login-s">S</span>
          <span className="admin-login-brand">oftara TECH</span>
          <span className="admin-header-sep">|</span>
          <span className="admin-header-title">Administration</span>
        </div>
        <button className="admin-btn-ghost" onClick={handleLogout}>Déconnexion</button>
      </header>

      <main className="admin-main">
        <div className="admin-section-header">
          <h2>Demandes de devis</h2>
          <span className="admin-badge">{total}</span>
        </div>

        {loading && <div className="admin-loading">Chargement…</div>}
        {error && <div className="admin-alert">{error}</div>}

        {!loading && !error && quotations.length === 0 && (
          <div className="admin-empty">Aucune demande de devis pour l'instant.</div>
        )}

        {!loading && quotations.length > 0 && (
          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Client</th>
                  <th>Email</th>
                  <th>Société</th>
                  <th>Projet</th>
                  <th>Date</th>
                  <th>Statut</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {quotations.map(q => (
                  <tr
                    key={q.id}
                    className={selected === q.id ? "admin-row-selected" : ""}
                    onClick={() => setSelected(selected === q.id ? null : q.id)}
                  >
                    <td className="admin-td-id">#{q.id}</td>
                    <td className="admin-td-name">{q.name}</td>
                    <td className="admin-td-email">{q.email}</td>
                    <td>{q.company || <span className="admin-muted">—</span>}</td>
                    <td>{q.project_type?.name || <span className="admin-muted">—</span>}</td>
                    <td className="admin-td-date">{formatDate(q.created_at)}</td>
                    <td>
                      <span className={`admin-status admin-status-${q.status}`}>
                        {STATUS_LABELS[q.status] || q.status}
                      </span>
                    </td>
                    <td onClick={e => e.stopPropagation()}>
                      <button
                        className="admin-btn-download"
                        onClick={() => handleDownload(q)}
                        disabled={downloading === q.id}
                        title="Télécharger le devis en PDF"
                      >
                        {downloading === q.id ? "…" : "PDF"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {pages > 1 && (
              <div className="admin-pagination">
                <button
                  className="admin-btn-ghost"
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page <= 1 || loading}
                >
                  ← Précédent
                </button>
                <span className="admin-pagination-info">
                  Page {page} / {pages} — {total} demande{total > 1 ? "s" : ""}
                </span>
                <button
                  className="admin-btn-ghost"
                  onClick={() => setPage(p => Math.min(pages, p + 1))}
                  disabled={page >= pages || loading}
                >
                  Suivant →
                </button>
              </div>
            )}
          </div>
        )}

        {selected !== null && (() => {
          const q = quotations.find(x => x.id === selected);
          if (!q) return null;
          return (
            <div className="admin-detail-backdrop" onClick={() => setSelected(null)}>
            <div className="admin-detail" onClick={e => e.stopPropagation()}>
              <div className="admin-detail-header">
                <h3>Devis #{q.id} — {q.name}</h3>
                <button className="admin-btn-ghost" onClick={() => setSelected(null)}>Fermer</button>
              </div>
              <div className="admin-detail-grid">
                <div>
                  <div className="admin-detail-label">Email</div>
                  <div>{q.email}</div>
                </div>
                <div>
                  <div className="admin-detail-label">Téléphone</div>
                  <div>{q.phone || "—"}</div>
                </div>
                <div>
                  <div className="admin-detail-label">Société</div>
                  <div>{q.company || "—"}</div>
                </div>
                <div>
                  <div className="admin-detail-label">Budget</div>
                  <div>{q.budget || "—"}</div>
                </div>
                <div>
                  <div className="admin-detail-label">Délai</div>
                  <div>{q.deadline || "—"}</div>
                </div>
                <div>
                  <div className="admin-detail-label">Statut</div>
                  <div>{STATUS_LABELS[q.status] || q.status}</div>
                </div>
              </div>
              {q.features?.length > 0 && (
                <div className="admin-detail-section">
                  <div className="admin-detail-label">Fonctionnalités</div>
                  <div className="admin-detail-tags">
                    {q.features.map(f => (
                      <span key={f.id} className="admin-tag">{f.name}</span>
                    ))}
                  </div>
                </div>
              )}
              {q.description && (
                <div className="admin-detail-section">
                  <div className="admin-detail-label">Description</div>
                  <p className="admin-detail-desc">{q.description}</p>
                </div>
              )}
              <div className="admin-detail-actions">
                <button
                  className="admin-btn-primary"
                  onClick={() => handleDownload(q)}
                  disabled={downloading === q.id}
                >
                  {downloading === q.id ? "Téléchargement…" : "Télécharger le PDF"}
                </button>
              </div>
            </div>
            </div>
          );
        })()}
      </main>
    </div>
  );
}
