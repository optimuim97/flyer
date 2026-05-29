# Softara — Site vitrine

Site flyer pour Softara : conception d'applications, e-commerce, e-paiements.
Page unique, sidebar fixe à gauche (contact + ce qu'on fait), main à droite.
Couleurs : confiance / sécurité / expertise (navy + bleu + teal).

## Stack
- **Backend** : Flask + SQLAlchemy (SQLite). Stocke les demandes de devis et expose les types de projet & fonctionnalités seedés.
- **Frontend** : React + Vite. Modal multi-étapes pour la demande de devis.

## Modèle de données
- `project_types` — catalogue de types de projet (site vitrine, e-commerce, mobile, e-paiement…).
- `features` — palette de fonctionnalités regroupées par catégorie (commerce, paiement, sécurité…).
- `quotations` — demandes de devis client + lien many-to-many vers `features`.

Le seeding est dans [backend/seed.py](backend/seed.py) et s'exécute automatiquement au lancement.

## API
- `GET /api/project-types` → liste des types
- `GET /api/features` → fonctionnalités groupées par catégorie
- `POST /api/quotations` → enregistre une demande de devis
- `GET /api/quotations` → liste les demandes (admin)
- `POST /api/contact` → message de contact simple

## Démarrage rapide (tout en un)
```powershell
.\run-server.ps1
```
ou en double-cliquant sur `run-server.bat`.

Le script crée le venv Python, installe les dépendances, puis lance :
- Backend Flask sur http://localhost:6060
- Frontend Vite sur http://localhost:3000 (proxy `/api` → Flask)

## Démarrage manuel

### Backend
```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Frontend
```powershell
cd frontend
npm install
npm run dev
```

## Production
```powershell
cd frontend
npm run build
cd ..\backend
python app.py
```
Flask sert le build React depuis `frontend/dist` sur le port 5000.

## Configuration email (optionnel)
Définir les variables d'environnement pour activer l'envoi du formulaire :
```
SOFTARA_CONTACT_EMAIL=assidikouattara@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=...
SMTP_PASS=...
```
Sans config SMTP, les messages s'affichent dans la console Flask.

## À personnaliser
- Numéro WhatsApp : `frontend/src/components/Hero.jsx` et `Contact.jsx` (constante `WHATSAPP_NUMBER`)
- E-mail de contact : `frontend/src/components/Contact.jsx` (constante `EMAIL`)
- Logo / favicon : `frontend/public/`
