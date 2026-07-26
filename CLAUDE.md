# Plateforme SaaS Data & IA — Instructions projet

Projet personnel (portfolio) : plateforme SaaS multi-tenant de BI et automatisation
intelligente pour PME marocaines. Voir `CAHIER_DES_CHARGES.md` pour le contexte complet
et `PROGRESS.md` pour l'état d'avancement détaillé étape par étape.

## Méthode de travail avec l'utilisateur

- **Toujours avancer étape par étape**, jamais plusieurs étapes d'un coup, sauf demande explicite.
- L'utilisateur n'est pas développeur — **expliquer chaque étape en langage simple**, sans
  jargon non défini, après chaque action technique importante (voir le style des explications
  dans `PROGRESS.md` comme référence de ton).
- Après chaque étape validée, mettre à jour `PROGRESS.md` (section "État actuel" + historique).

## Stack technique retenu (voir CAHIER_DES_CHARGES.md pour le détail complet)

- Langage : Python (Pandas, scikit-learn, XGBoost)
- Base de données : PostgreSQL avec Row-Level Security (isolation multi-tenant par `tenant_id`)
- Orchestration ETL : Apache Airflow
- Stockage objet : MinIO (Parquet)
- MLOps : MLflow, SHAP, pytest, GitHub Actions
- API : FastAPI (conteneurisée Docker)
- Agents IA : MCP + LangGraph (pas CrewAI)
- Dashboard : Streamlit (pas Power BI)
- Facturation : Stripe (mode test)
- **Écarté du périmètre** : Apache Spark, Power BI, CrewAI (mentionnés en doc comme extensions possibles, non implémentés)

## Comment lancer l'environnement local

```bash
docker compose up -d                                    # démarre PostgreSQL
.venv/Scripts/python.exe -m pytest tests/ -v             # lance les tests
```

- PostgreSQL exposé sur le port hôte **5434** (5432/5433 pris par d'autres projets locaux)
- Compte superutilisateur : `saas_admin` (ne pas l'utiliser pour tester le RLS, il le contourne)
- Compte applicatif réel : `app_user` / `app_password`

## Notes techniques importantes

- `SET app.current_tenant = %s` ne s'exécute pas en paramétré : utiliser
  `SELECT set_config('app.current_tenant', %s, false)`.
- Dépendance PostgreSQL Python : `psycopg` (v3), pas `psycopg2-binary` (échoue à builder sur
  Python 3.13 sur cette machine).
