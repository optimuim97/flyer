# Déploiement Softara — Docker + Caddy (HTTPS auto)

Stack : un container Flask/Gunicorn servant le build React + un container Caddy
qui gère le reverse-proxy et les certificats Let's Encrypt automatiquement
pour `softara.tech`.

## 1. Prérequis sur le serveur

- Docker + docker-compose (`docker compose version` ≥ v2)
- Ports **80** et **443** ouverts (pour Let's Encrypt + HTTPS)
- DNS : enregistrement **A** (et **AAAA** si IPv6) pour `softara.tech`
  ET `www.softara.tech` pointant sur l'IP du serveur.
  ⚠️ Sans DNS correct, Caddy ne pourra pas obtenir le certificat.

## 2. Première installation

```bash
# Cloner / transférer les sources
git clone <repo> /opt/softara
cd /opt/softara

# Variables d'env (SMTP, email contact)
cp .env.example .env
nano .env

# Build + lancement
docker compose up -d --build

# Suivre les logs
docker compose logs -f
```

Au premier démarrage :
- Le container `softara` exécute le seed (`seed.py`) puis lance Gunicorn sur :6060
- Le container `caddy` détecte le domaine, demande un certificat Let's Encrypt
  et expose le site en HTTPS sur :443

Vérification :
```bash
curl -I https://softara.tech
curl https://softara.tech/api/health
```

## 3. Mise à jour

```bash
cd /opt/softara
git pull
docker compose up -d --build
```

Le seed est idempotent : il met à jour les types de projet et fonctionnalités
sans toucher aux devis (`quotations`) déjà reçus.

## 4. Sauvegarder les données

Toutes les données (base SQLite + certificats TLS) sont dans des volumes Docker.

```bash
# Backup de la base
docker compose exec softara cp /app/backend/data/softara.db /tmp/softara.db
docker cp softara-app:/tmp/softara.db ./softara-$(date +%Y%m%d).db

# Ou directement depuis le volume
docker run --rm -v softara_softara-data:/data -v $(pwd):/backup alpine \
  tar czf /backup/softara-data-$(date +%Y%m%d).tar.gz -C /data .
```

## 5. Consulter les devis reçus

```bash
# Liste JSON
curl https://softara.tech/api/quotations | jq

# Ou via SQLite directement
docker compose exec softara sqlite3 /app/backend/data/softara.db \
  "SELECT id, name, email, created_at FROM quotations ORDER BY created_at DESC;"
```

> ⚠️ L'endpoint `/api/quotations` GET est public dans cette version. Pour la prod,
> ajouter une authentification basique ou retirer la route (et lire la DB en direct).

## 6. Diagnostic

```bash
docker compose ps                 # État des containers
docker compose logs softara       # Logs app
docker compose logs caddy         # Logs Caddy / TLS
docker compose restart softara    # Redémarrer l'app
docker compose down               # Tout arrêter
```

Si Caddy n'obtient pas le certificat : vérifier le DNS (`dig softara.tech`),
que les ports 80/443 sont bien ouverts au firewall, et regarder `docker compose logs caddy`.
