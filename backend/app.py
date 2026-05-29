from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from models import db, ProjectType, Feature, Quotation

FRONTEND_DIST = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
)
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "softara.db"))

CONTACT_EMAIL = os.environ.get("SOFTARA_CONTACT_EMAIL", "assidikouattara@gmail.com")
SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")


def _send_mail(subject, body, reply_to=None):
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS):
        print(f"[MAIL] (SMTP non configuré) {subject}\n{body}", flush=True)
        return True, None
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = CONTACT_EMAIL
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.set_content(body)
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
        return True, None
    except Exception as e:
        return False, str(e)


def create_app():
    app = Flask(__name__, static_folder=FRONTEND_DIST, static_url_path="")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", f"sqlite:///{DB_PATH}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    CORS(app)
    db.init_app(app)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

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
        ok, err = _send_mail(
            subject=f"[Softara] Nouveau contact - {name}",
            body=f"De: {name} <{email}>\n\n{message}",
            reply_to=email,
        )
        if not ok:
            return jsonify({"ok": False, "error": err}), 500
        return jsonify({"ok": True})

    @app.post("/api/quotations")
    def create_quotation():
        data = request.get_json(silent=True) or {}
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip()
        project_type_slug = (data.get("project_type") or "").strip()
        feature_slugs = data.get("features") or []

        if not name or not email or not project_type_slug:
            return jsonify({"ok": False, "error": "Nom, email et type de projet sont requis."}), 400

        ptype = ProjectType.query.filter_by(slug=project_type_slug).first()
        if not ptype:
            return jsonify({"ok": False, "error": "Type de projet inconnu."}), 400

        features = []
        if feature_slugs:
            features = Feature.query.filter(Feature.slug.in_(feature_slugs)).all()

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

        feat_list = "\n  - " + "\n  - ".join(f.name for f in features) if features else " (aucune)"
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
        _send_mail(subject=f"[Softara] Devis #{q.id} - {name}", body=body, reply_to=email)
        return jsonify({"ok": True, "quotation": q.to_dict()}), 201

    @app.get("/api/quotations")
    def list_quotations():
        rows = Quotation.query.order_by(Quotation.created_at.desc()).all()
        return jsonify([r.to_dict() for r in rows])

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_spa(path):
        full = os.path.join(FRONTEND_DIST, path)
        if path and os.path.exists(full):
            return send_from_directory(FRONTEND_DIST, path)
        index = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index):
            return send_from_directory(FRONTEND_DIST, "index.html")
        return jsonify({"status": "api-only", "build": "not found - run npm run build"}), 200

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", "6060"))
    print(f"[softara] Backend Flask en ecoute sur http://0.0.0.0:{port}", flush=True)
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
