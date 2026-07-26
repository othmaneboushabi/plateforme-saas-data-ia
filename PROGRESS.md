# Suivi d'avancement du projet

## État actuel

- **Phase en cours** : Phase 1 — Data Engineering
- **Dernière étape validée** : Étape 4 (Git + GitHub Actions CI, workflow vert ✅)
- **Prochaine étape** : Étape 5 — ingestion de données CSV par tenant (début de la partie "vraie" Phase 1 : upload + lecture de fichiers)

## Décisions et pièges à retenir

- Port PostgreSQL hôte : **5434** (5432 et 5433 déjà pris par d'autres projets Docker sur cette machine — `edgeguard_timescaledb` et `ais_postgres`)
- L'utilisateur `saas_admin` (créé via `POSTGRES_USER`) est **superutilisateur** → il contourne toujours le Row-Level Security. Ne jamais l'utiliser pour tester l'isolation.
- L'utilisateur applicatif réel (utilisé par les tests, et plus tard par l'API) est **`app_user`** / `app_password` — c'est lui qui est réellement soumis aux policies RLS.
- Isolation RLS activée sur la table `sales` via `tenant_id` + `SET app.current_tenant` (voir `infra/postgres/init.sql`)
- Dépendance PostgreSQL Python : **`psycopg` (v3)**, pas `psycopg2-binary` — celui-ci ne build pas sur Python 3.13 sur cette machine.
- `SET app.current_tenant = %s` ne fonctionne pas paramétré en SQL classique → utiliser `SELECT set_config('app.current_tenant', %s, false)`.

## Historique des étapes

### Étape 1 — Socle Docker + PostgreSQL
- Créé la structure de dossiers (`services/`, `tests/`, `docs/`, `data/sample_tenants/`, `infra/postgres/`)
- Créé `docker-compose.yml` avec le service `postgres` (image `postgres:16`)
- Créé `infra/postgres/init.sql` (vide à ce stade)
- Résolu un conflit de port (5432 → 5434)
- Vérifié : `pg_isready` répond "accepting connections"

### Étape 2 — Schéma multi-tenant + Row-Level Security
- Ajouté dans `init.sql` : table `tenants`, table `sales` (avec `tenant_id`)
- Activé `ROW LEVEL SECURITY` sur `sales` + policy `tenant_isolation`
- Inséré 2 tenants de test ("PME Alpha", "PME Beta") et des ventes factices
- Créé le rôle applicatif `app_user` (non superutilisateur), avec les droits nécessaires
- Vérifié manuellement (`psql`) que chaque tenant ne voit que ses propres ventes

### Étape 3 — Test automatisé de l'isolation (pytest)
- Créé l'environnement virtuel Python `.venv`
- `requirements.txt` : `psycopg[binary]`, `pytest`
- Créé `tests/test_tenant_isolation.py` : 3 tests vérifiant l'isolation entre tenant 1 et tenant 2
- Tous les tests passent (`pytest tests/test_tenant_isolation.py -v` → 3 passed)

### Étape 4 — Git + GitHub Actions (CI)
- Initialisé le dépôt Git local (`git init`), créé `.gitignore`
- Rendu le DSN de connexion configurable via la variable d'environnement `DATABASE_DSN` (pour que le test fonctionne aussi bien en local qu'en CI, où le port Postgres diffère)
- Créé `.github/workflows/ci.yml` : à chaque push, démarre un PostgreSQL frais, applique `init.sql`, lance `pytest`
- Dépôt distant : https://github.com/othmaneboushabi/plateforme-saas-data-ia
- Installé et authentifié GitHub CLI (`gh`) pour piloter/vérifier GitHub depuis le terminal
- Premier run CI vérifié : **succès** (3 tests passés sur les serveurs GitHub)

## Comment relancer l'environnement (pour reprendre après une pause)

```bash
# Démarrer PostgreSQL
docker compose up -d

# Activer l'environnement Python et lancer les tests
.venv/Scripts/python.exe -m pytest tests/ -v
```
