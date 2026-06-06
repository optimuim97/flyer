from __future__ import annotations

import os
import sys
import logging
import secrets
import smtplib
import threading
import traceback
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from functools import wraps

import jwt
from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS

from models import db, ProjectType, Feature, Quotation

# ============================================================
# Logging — vers stdout/stderr pour etre vu dans docker compose logs
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("softara")

FRONTEND_DIST = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
)
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "softara.db"))

CONTACT_EMAIL = os.environ.get("SOFTARA_CONTACT_EMAIL", "contact@softara.tech")

ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "changeme")
# Random per restart in dev; set ADMIN_SECRET in prod so tokens survive restarts.
ADMIN_SECRET = os.environ.get("ADMIN_SECRET") or secrets.token_hex(32)
SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")
SMTP_FROM = os.environ.get("SMTP_FROM", SMTP_USER or "")
SMTP_FROM_NAME = os.environ.get("SMTP_FROM_NAME", "Softara")


def _default_mode():
    if SMTP_PORT == 465:
        return "ssl"
    if SMTP_PORT in (587, 2525, 25):
        return "starttls"
    return "ssl"


SMTP_SECURITY = (os.environ.get("SMTP_SECURITY") or _default_mode()).lower()
SMTP_TIMEOUT = int(os.environ.get("SMTP_TIMEOUT", "15"))


def _send_mail(subject, body, reply_to=None):
    """Envoi synchrone. Retourne (ok, err)."""
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS):
        logger.warning("SMTP non configure - mail non envoye : %s", subject)
        return True, None
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM or SMTP_USER}>"
    msg["To"] = CONTACT_EMAIL
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.set_content(body)
    try:
        logger.info("SMTP connexion %s:%s mode=%s", SMTP_HOST, SMTP_PORT, SMTP_SECURITY)
        if SMTP_SECURITY == "ssl":
            client = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT)
        else:
            client = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT)
        with client as s:
            s.ehlo()
            if SMTP_SECURITY == "starttls":
                s.starttls()
                s.ehlo()
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
        logger.info("SMTP OK -> %s", CONTACT_EMAIL)
        return True, None
    except Exception as e:
        logger.error(
            "SMTP echec (%s:%s/%s) : %s\n%s",
            SMTP_HOST, SMTP_PORT, SMTP_SECURITY, e, traceback.format_exc(),
        )
        return False, str(e)


def _send_mail_async(subject, body, reply_to=None):
    """Envoi en arriere-plan — la requete HTTP n'attend pas."""
    def _run():
        try:
            _send_mail(subject, body, reply_to)
        except Exception:
            logger.exception("Thread mail crashe")
    threading.Thread(target=_run, daemon=True, name="softara-mail").start()


def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"ok": False, "error": "Non autorise"}), 401
        token = auth[7:]
        try:
            jwt.decode(token, ADMIN_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"ok": False, "error": "Session expiree"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"ok": False, "error": "Token invalide"}), 401
        return f(*args, **kwargs)
    return decorated


def _generate_quotation_pdf(q):
    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_margins(20, 20, 20)

    # Header
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(219, 146, 0)
    pdf.cell(0, 12, "SOFTARA TECH", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, "Agence de developpement logiciel", ln=True, align="C")
    pdf.ln(6)

    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, f"Demande de devis #{q.id}", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 5, f"Date : {q.created_at.strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.cell(0, 5, f"Statut : {q.status}", ln=True)
    pdf.ln(6)

    # Separator
    pdf.set_draw_color(219, 146, 0)
    pdf.set_line_width(0.5)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(8)

    def section(title):
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 8, title, ln=True)
        pdf.ln(2)

    def row(label, value):
        if value:
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(55, 6, f"{label} :", ln=False)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(30, 30, 30)
            # encode to latin-1, replace unknown chars
            safe = str(value).encode("latin-1", errors="replace").decode("latin-1")
            pdf.cell(0, 6, safe, ln=True)

    section("Informations client")
    row("Nom", q.name)
    row("Email", q.email)
    row("Telephone", q.phone)
    row("Societe", q.company)
    pdf.ln(6)

    section("Details du projet")
    row("Type de projet", q.project_type.name if q.project_type else "-")
    row("Budget", q.budget)
    row("Delai souhaite", q.deadline)
    pdf.ln(6)

    if q.features:
        section("Fonctionnalites souhaitees")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(50, 50, 50)
        for f in q.features:
            safe = f.name.encode("latin-1", errors="replace").decode("latin-1")
            pdf.cell(8, 6, "-", ln=False)
            pdf.cell(0, 6, safe, ln=True)
        pdf.ln(6)

    if q.description:
        section("Description")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(50, 50, 50)
        safe_desc = q.description.encode("latin-1", errors="replace").decode("latin-1")
        pdf.multi_cell(0, 6, safe_desc)
        pdf.ln(4)

    # Footer
    pdf.set_y(-18)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(160, 160, 160)
    pdf.cell(0, 5, "Softara Tech  |  contact@softara.tech  |  softara.tech", align="C")

    return bytes(pdf.output())


def create_app():
    # Disable Flask built-in static route (it returns 404 before SPA fallback on deep links).
    app = Flask(__name__, static_folder=None)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", f"sqlite:///{DB_PATH}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JSON_AS_ASCII"] = False
    CORS(app)
    db.init_app(app)

    # ============================================================
    # Gestion globale des erreurs — toujours retourner un JSON propre
    # avec le traceback dans les logs
    # ============================================================
    @app.errorhandler(Exception)
    def _handle_exception(e):
        from werkzeug.exceptions import HTTPException
        if isinstance(e, HTTPException):
            return jsonify({"ok": False, "error": e.description}), e.code
        logger.exception("Erreur non geree dans %s %s", request.method, request.path)
        try:
            db.session.rollback()
        except Exception:
            pass
        return jsonify({
            "ok": False,
            "error": "Erreur interne du serveur.",
            "detail": str(e),
        }), 500

    @app.before_request
    def _log_request():
        if request.path.startswith("/api/"):
            logger.info("%s %s", request.method, request.path)

    # ============================================================
    # API
    # ============================================================
    @app.get("/api/health")
    def health():
        return {
            "status": "ok",
            "smtp": {
                "host": SMTP_HOST or None,
                "port": SMTP_PORT,
                "security": SMTP_SECURITY,
                "configured": bool(SMTP_HOST and SMTP_USER and SMTP_PASS),
            },
        }

    @app.get("/api/project-types")
    def list_project_types():
        rows = ProjectType.query.order_by(ProjectType.sort_order).all()
        return jsonify([r.to_dict() for r in rows])

    @app.get("/api/features")
    def list_features():
        rows = Feature.query.order_by(Feature.sort_order).all()
        grouped = {}
        for r in rows:
            grouped.setdefault(r.category or "Autres", []).append(r.to_dict())
        return jsonify(grouped)

    @app.post("/api/contact")
    def contact():
        data = request.get_json(silent=True) or {}
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip()
        message = (data.get("message") or "").strip()
        if not name or not email or not message:
            return jsonify({"ok": False, "error": "Champs requis manquants."}), 400
        _send_mail_async(
            subject=f"[Softara] Nouveau contact - {name}",
            body=f"De: {name} <{email}>\n\n{message}",
            reply_to=email,
        )
        return jsonify({"ok": True})

    @app.post("/api/quotations")
    def create_quotation():
        data = request.get_json(silent=True) or {}
        logger.info("Quotation payload reçu : %s", {k: v for k, v in data.items() if k != "password"})

        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip()
        project_type_slug = (data.get("project_type") or "").strip()
        feature_slugs = data.get("features") or []

        if not name or not email or not project_type_slug:
            return jsonify({"ok": False, "error": "Nom, email et type de projet sont requis."}), 400

        ptype = ProjectType.query.filter_by(slug=project_type_slug).first()
        if not ptype:
            logger.warning("Type de projet inconnu : %r", project_type_slug)
            return jsonify({"ok": False, "error": "Type de projet inconnu."}), 400

        features = []
        if feature_slugs:
            features = Feature.query.filter(Feature.slug.in_(feature_slugs)).all()

        try:
            q = Quotation(
                name=name,
                email=email,
                phone=(data.get("phone") or "").strip() or None,
                company=(data.get("company") or "").strip() or None,
                project_type=ptype,
                description=(data.get("description") or "").strip() or None,
                budget=(data.get("budget") or "").strip() or None,
                deadline=(data.get("deadline") or "").strip() or None,
                features=features,
            )
            db.session.add(q)
            db.session.commit()
            logger.info("Quotation #%s enregistree pour %s", q.id, email)
        except Exception:
            db.session.rollback()
            logger.exception("Echec INSERT quotation")
            raise  # remontee a _handle_exception

        # Construction du body mail
        feat_list = (
            "\n  - " + "\n  - ".join(f.name for f in features)
            if features else " (aucune)"
        )
        body = (
            f"Nouvelle demande de devis #{q.id}\n\n"
            f"Client : {name} <{email}>\n"
            f"Telephone : {q.phone or '-'}\n"
            f"Societe : {q.company or '-'}\n"
            f"Type de projet : {ptype.name}\n"
            f"Budget : {q.budget or '-'}\n"
            f"Echeance : {q.deadline or '-'}\n\n"
            f"Fonctionnalites souhaitees :{feat_list}\n\n"
            f"Description :\n{q.description or '-'}\n"
        )
        # Envoi mail en arriere-plan -> la requete repond immediatement
        _send_mail_async(
            subject=f"[Softara] Devis #{q.id} - {name}",
            body=body,
            reply_to=email,
        )

        _send_mail_async(
            subject=f"Demande #{q.id}",
            body=body,
            reply_to=email
        )

        # Reponse client — meme si le mail echoue plus tard, le devis est sauvegarde
        try:
            payload = q.to_dict()
        except Exception:
            logger.exception("to_dict() a echoue, fallback payload minimal")
            payload = {"id": q.id, "name": q.name, "email": q.email}

        return jsonify({"ok": True, "quotation": payload}), 201

    @app.get("/api/quotations")
    def list_quotations():
        rows = Quotation.query.order_by(Quotation.created_at.desc()).all()
        return jsonify([r.to_dict() for r in rows])

    # ============================================================
    # Admin API (JWT-protected)
    # ============================================================
    @app.post("/api/admin/login")
    def admin_login():
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip()
        password = (data.get("password") or "").strip()
        if username != ADMIN_USER or not password or password != ADMIN_PASS:
            logger.warning("Tentative connexion admin echouee pour user=%r", username)
            return jsonify({"ok": False, "error": "Identifiants incorrects"}), 401
        token = jwt.encode(
            {"sub": username, "exp": datetime.now(timezone.utc) + timedelta(hours=8)},
            ADMIN_SECRET,
            algorithm="HS256",
        )
        logger.info("Admin connecte : %s", username)
        return jsonify({"ok": True, "token": token})

    @app.get("/api/admin/quotations")
    @require_admin
    def admin_list_quotations():
        rows = Quotation.query.order_by(Quotation.created_at.desc()).all()
        return jsonify([r.to_dict() for r in rows])

    @app.get("/api/admin/quotations/<int:qid>/pdf")
    @require_admin
    def admin_download_quotation(qid):
        q = Quotation.query.get_or_404(qid)
        pdf_bytes = _generate_quotation_pdf(q)
        response = make_response(pdf_bytes)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = f'attachment; filename="devis-{qid}.pdf"'
        return response

    @app.route("/assets/<path:path>")
    def serve_assets(path):
        full = os.path.join(FRONTEND_DIST, "assets", path)
        if os.path.exists(full):
            return send_from_directory(os.path.join(FRONTEND_DIST, "assets"), path)
        return jsonify({"ok": False, "error": "Not found"}), 404

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_spa(path):
        # Ne jamais "manger" les routes API meme si serve_spa est plus generique
        if path.startswith("api/"):
            return jsonify({"ok": False, "error": "Not found"}), 404
        full = os.path.join(FRONTEND_DIST, path)
        if path and os.path.exists(full):
            return send_from_directory(FRONTEND_DIST, path)
        index = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index):
            return send_from_directory(FRONTEND_DIST, "index.html")
        return jsonify({"status": "api-only", "build": "not found - run npm run build"}), 200

    with app.app_context():
        db.create_all()

    logger.info(
        "Softara demarre. SMTP host=%s port=%s security=%s configured=%s",
        SMTP_HOST, SMTP_PORT, SMTP_SECURITY, bool(SMTP_HOST and SMTP_USER and SMTP_PASS),
    )

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", "6060"))
    print(f"[softara] Backend Flask en ecoute sur http://0.0.0.0:{port}", flush=True)
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
