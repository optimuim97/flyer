"""Seed des types de projet et de la palette de fonctionnalités.

Exécution :  python seed.py
Idempotent : update si slug existe déjà, insert sinon.
"""
from models import db, ProjectType, Feature


PROJECT_TYPES = [
    {
        "slug": "site-vitrine",
        "name": "Site vitrine",
        "description": "Site web de présentation, multipage, optimisé SEO.",
        "icon": "globe",
    },
    {
        "slug": "ecommerce",
        "name": "Boutique e-commerce",
        "description": "Vente en ligne avec catalogue, panier, paiement et livraison.",
        "icon": "cart",
    },
    {
        "slug": "marketplace",
        "name": "Marketplace multi-vendeurs",
        "description": "Plateforme qui met en relation plusieurs vendeurs et clients.",
        "icon": "store",
    },
    {
        "slug": "app-mobile",
        "name": "Application mobile",
        "description": "Application Android / iOS native ou cross-platform.",
        "icon": "mobile",
    },
    {
        "slug": "app-web-metier",
        "name": "Application web métier",
        "description": "Outil métier sur mesure (gestion, suivi, automatisation).",
        "icon": "app",
    },
    {
        "slug": "e-paiement",
        "name": "Solution e-paiement",
        "description": "Plateforme ou passerelle d'encaissement (Mobile Money, cartes).",
        "icon": "wallet",
    },
    {
        "slug": "erp-gestion",
        "name": "ERP / Gestion interne",
        "description": "Stock, ventes, achats, RH, comptabilité — modules sur mesure.",
        "icon": "chart",
    },
    {
        "slug": "api-integration",
        "name": "API / Intégration",
        "description": "Création d'API ou intégration de services tiers.",
        "icon": "plug",
    },
]


FEATURES = [
    # --- Commerce ---
    {"slug": "catalogue-produits", "name": "Catalogue produits", "category": "Commerce",
     "description": "Fiches produits, photos, variantes, stock."},
    {"slug": "panier-commande", "name": "Panier & commandes", "category": "Commerce",
     "description": "Panier persistant, validation, suivi de commande."},
    {"slug": "multi-vendeurs", "name": "Multi-vendeurs", "category": "Commerce",
     "description": "Plusieurs marchands sur la même plateforme."},
    {"slug": "codes-promo", "name": "Codes promo & remises", "category": "Commerce",
     "description": "Coupons, remises automatiques, programmes fidélité."},
    {"slug": "livraison-tracking", "name": "Livraison & suivi", "category": "Commerce",
     "description": "Zones, tarifs et suivi de livraison."},

    # --- Paiement ---
    {"slug": "mobile-money", "name": "Mobile Money", "category": "Paiement",
     "description": "Orange Money, MTN, Moov, Wave."},
    {"slug": "carte-bancaire", "name": "Carte bancaire (Visa/Mastercard)", "category": "Paiement",
     "description": "Encaissement carte via passerelle sécurisée."},
    {"slug": "paiement-lien", "name": "Paiement par lien", "category": "Paiement",
     "description": "Génération de liens de paiement à partager."},
    {"slug": "paiement-livraison", "name": "Paiement à la livraison", "category": "Paiement",
     "description": "Cash on delivery avec confirmation."},
    {"slug": "abonnement-recurrent", "name": "Abonnements récurrents", "category": "Paiement",
     "description": "Prélèvements automatiques mensuels/annuels."},

    # --- Utilisateurs ---
    {"slug": "auth-compte", "name": "Inscription & connexion", "category": "Utilisateurs",
     "description": "Comptes clients, mot de passe oublié, vérification email."},
    {"slug": "auth-social", "name": "Connexion Google/Facebook", "category": "Utilisateurs",
     "description": "OAuth 2.0 / SSO."},
    {"slug": "roles-permissions", "name": "Rôles & permissions", "category": "Utilisateurs",
     "description": "Admin, manager, agent, client — droits par module."},
    {"slug": "profils-clients", "name": "Profils clients", "category": "Utilisateurs",
     "description": "Historique, adresses, préférences."},

    # --- Communication ---
    {"slug": "emails-transactionnels", "name": "Emails transactionnels", "category": "Communication",
     "description": "Confirmations, factures, notifications par email."},
    {"slug": "sms", "name": "SMS", "category": "Communication",
     "description": "OTP, alertes, confirmations par SMS."},
    {"slug": "whatsapp", "name": "Notifications WhatsApp", "category": "Communication",
     "description": "Envoi via WhatsApp Business API."},
    {"slug": "notifications-push", "name": "Notifications push", "category": "Communication",
     "description": "Push web et mobile."},
    {"slug": "chat-support", "name": "Chat / support en ligne", "category": "Communication",
     "description": "Messagerie temps réel avec les clients."},

    # --- Administration ---
    {"slug": "tableau-bord", "name": "Tableau de bord admin", "category": "Administration",
     "description": "Vue d'ensemble des KPI en temps réel."},
    {"slug": "rapports-export", "name": "Rapports & export", "category": "Administration",
     "description": "Export Excel / PDF, rapports planifiés."},
    {"slug": "gestion-stock", "name": "Gestion de stock", "category": "Administration",
     "description": "Entrées, sorties, alertes seuil bas."},
    {"slug": "facturation", "name": "Facturation", "category": "Administration",
     "description": "Génération de factures, devis, avoirs."},

    # --- Mobile ---
    {"slug": "app-android", "name": "Application Android", "category": "Mobile",
     "description": "App publiée sur Google Play."},
    {"slug": "app-ios", "name": "Application iOS", "category": "Mobile",
     "description": "App publiée sur l'App Store."},
    {"slug": "responsive", "name": "Site responsive", "category": "Mobile",
     "description": "Adapté mobile, tablette et desktop."},

    # --- Avancé ---
    {"slug": "geolocalisation", "name": "Géolocalisation & cartes", "category": "Avancé",
     "description": "Carte interactive, tracking, livreurs."},
    {"slug": "ia-reco", "name": "IA / recommandations", "category": "Avancé",
     "description": "Suggestions personnalisées, scoring."},
    {"slug": "multilingue", "name": "Multilingue", "category": "Avancé",
     "description": "Plusieurs langues (FR, EN, etc.)."},
    {"slug": "recherche-avancee", "name": "Recherche avancée & filtres", "category": "Avancé",
     "description": "Recherche full-text, facettes, tri."},

    # --- Sécurité ---
    {"slug": "2fa", "name": "Double authentification (2FA)", "category": "Sécurité",
     "description": "Second facteur par SMS, email ou app."},
    {"slug": "audit-logs", "name": "Journaux d'audit", "category": "Sécurité",
     "description": "Traçabilité de toutes les actions sensibles."},
    {"slug": "rgpd", "name": "Conformité RGPD", "category": "Sécurité",
     "description": "Gestion des consentements, export et suppression."},
    {"slug": "chiffrement", "name": "Chiffrement renforcé", "category": "Sécurité",
     "description": "Données sensibles chiffrées au repos et en transit."},
]


def upsert_project_types():
    for i, p in enumerate(PROJECT_TYPES):
        row = ProjectType.query.filter_by(slug=p["slug"]).first()
        if row is None:
            row = ProjectType(slug=p["slug"], sort_order=i)
            db.session.add(row)
        row.name = p["name"]
        row.description = p["description"]
        row.icon = p["icon"]
        row.sort_order = i


def upsert_features():
    for i, f in enumerate(FEATURES):
        row = Feature.query.filter_by(slug=f["slug"]).first()
        if row is None:
            row = Feature(slug=f["slug"], sort_order=i)
            db.session.add(row)
        row.name = f["name"]
        row.description = f["description"]
        row.category = f["category"]
        row.sort_order = i


def run(app=None):
    if app is None:
        from app import create_app
        app = create_app()
    print(f"[seed] DB : {app.config['SQLALCHEMY_DATABASE_URI']}", flush=True)
    with app.app_context():
        db.create_all()
        upsert_project_types()
        upsert_features()
        db.session.commit()
        n_pt = ProjectType.query.count()
        n_f = Feature.query.count()
        print(f"[seed] OK — {n_pt} types de projet, {n_f} fonctionnalités.")


if __name__ == "__main__":
    run()
