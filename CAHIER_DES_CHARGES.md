# Cahier des Charges — Version finale

## Plateforme SaaS Data & IA
BI et automatisation intelligente multi-tenant pour PME
Projet personnel — Data Engineering, MLOps, IA générative multi-agents, SaaS

---

## 1. Contexte et justification

Les PME marocaines disposent rarement des ressources humaines et techniques nécessaires pour exploiter leurs propres données (ventes, stock, tickets support, retours clients). Elles utilisent des outils bureautiques standards, ce qui limite leur capacité de décision rapide et leur détection des anomalies ou tendances.

Ce projet propose une plateforme SaaS multi-tenant permettant à chaque entreprise cliente de connecter ses données, d'obtenir des prédictions, un reporting automatisé et un assistant conversationnel, sans expertise technique requise.

Le projet est réalisé à titre personnel, en dehors de tout stage, dans l'objectif de constituer une réalisation concrète et démontrable pour la recherche d'emploi ou de stage dans le secteur data/IA au Maroc (ESN, startups tech).

---

## 2. Objectifs du projet

- Concevoir une chaîne complète de traitement de la donnée, de l'ingestion à la restitution
- Développer un modèle prédictif explicable, industrialisé et versionné
- Mettre en place une architecture d'agents autonomes consultable en langage naturel (MCP + LangGraph)
- Structurer le produit sous forme de SaaS multi-tenant avec **isolation stricte des données au niveau base de données** (PostgreSQL Row-Level Security), pas seulement au niveau applicatif
- Produire une documentation et une démonstration exploitables en entretien d'embauche
- Livrer un stack resserré mais entièrement fonctionnel, plutôt qu'une liste de technologies superficiellement intégrées

---

## 3. Périmètre fonctionnel

### 3.1 Fonctionnalités incluses

- Inscription et gestion de compte par entreprise cliente (tenant)
- Import de données (fichiers CSV, API simple) par tenant
- Nettoyage et transformation automatique des données (pipeline ETL orchestré)
- Génération de prédictions et détection d'anomalies, avec explicabilité (SHAP)
- Restitution via tableau de bord visuel (Streamlit)
- Assistant conversationnel (architecture multi-agents) répondant aux questions sur les données du client connecté
- Abonnement et facturation simulée (Stripe, mode test)

### 3.2 Fonctionnalités exclues du périmètre

- Facturation réelle avec transactions bancaires effectives
- Support de volumes de données à très grande échelle (pas de cluster Spark/Big Data en production — architecture documentée comme "scalable vers Spark" mais non implémentée)
- Application mobile native (produit accessible via navigateur web uniquement)
- Intégration Power BI réelle (mentionnée comme point d'extension possible en entreprise, non développée)

---

## 4. Exigences non fonctionnelles

- **Isolation stricte des données entre tenants**, garantie au niveau moteur de base de données (Row-Level Security), et non uniquement par filtrage applicatif
- Documentation claire (README, diagramme d'architecture, doc technique par phase)
- Code testé automatiquement avant toute mise à jour (CI via GitHub Actions)
- Déploiement reproductible via conteneurisation (Docker / Docker Compose)
- Explicabilité systématique des prédictions du modèle (SHAP)
- Chaque phase mensuelle produit une brique fonctionnelle démontrable de manière autonome

---

## 5. Stratégie multi-tenant (point d'architecture central)

Le multi-tenant est l'exigence non-fonctionnelle la plus critique du projet ; elle est traitée comme telle plutôt que comme un détail d'implémentation.

**Choix retenu : base unique PostgreSQL + `tenant_id` + Row-Level Security (RLS)**, plutôt qu'un schéma par tenant.

- Chaque table métier porte une colonne `tenant_id`
- Des policies RLS PostgreSQL filtrent automatiquement chaque requête selon le tenant courant — impossible d'oublier un `WHERE tenant_id = ...` côté application
- Le tenant courant est déterminé à partir du JWT de l'utilisateur authentifié, puis injecté en début de requête via une variable de session (`SET app.current_tenant = ...`) par un middleware FastAPI
- Ce mécanisme est testé explicitement : un test automatisé vérifie qu'un tenant A ne peut sous aucune requête lire les données du tenant B

Ce choix est plus simple à opérer qu'un schéma-par-tenant (une seule base à migrer/sauvegarder) tout en offrant une garantie d'isolation démontrable et auditable — c'est le détail technique mis en avant en entretien.

---

## 6. Architecture technique

```
Ingestion (par tenant, CSV/API)
        │
        ▼
Pipeline ETL orchestré (Airflow, DAGs par tenant)
        │
        ▼
Stockage : PostgreSQL (RLS multi-tenant) + MinIO (Parquet, data lake léger)
        │
        ▼
Entraînement et suivi du modèle (scikit-learn / XGBoost, MLflow, SHAP)
        │
        ▼
API de service (FastAPI, conteneurisée Docker, tenant-aware via JWT)
        │
        ▼
Serveur MCP (expose données et modèles par tenant comme outils standardisés)
        │
        ▼
Architecture multi-agents (LangGraph : agent données / agent analyse / agent rapport)
        │
        ▼
Interface conversationnelle et dashboard (Streamlit)
        │
        ▼
Couche SaaS (authentification JWT, gestion des rôles, abonnement Stripe test)
```

---

## 7. Planning et livrables par phase

| Phase | Durée | Livrable attendu |
|---|---|---|
| **Phase 1 — Data Engineering** | Mois 1 | Pipeline ETL automatisé (Airflow), ingestion multi-source par tenant, données propres stockées en PostgreSQL (RLS) et Parquet (MinIO) |
| **Phase 2 — ML/MLOps** | Mois 2 | Modèle prédictif (scikit-learn/XGBoost) explicable (SHAP), versionné (MLflow), servi via API FastAPI testée (pytest) et conteneurisée, intégrée en CI (GitHub Actions) |
| **Phase 3 — IA générative & agents** | Mois 3 | Serveur MCP + architecture multi-agents (LangGraph) consultable en langage naturel via interface conversationnelle |
| **Phase 4 — SaaS & finalisation** | Mois 4 | Authentification multi-tenant, facturation simulée (Stripe test), dashboard Streamlit finalisé, documentation complète, déploiement public (API + dashboard + agents) |

---

## 8. Technologies retenues (version finale)

| Domaine | Technologie | Justification du choix |
|---|---|---|
| Langage & traitement | Python, Pandas | Standard du marché, suffisant pour les volumes visés |
| Analytique locale | DuckDB (optionnel) | Requêtes analytiques rapides sans infrastructure Spark |
| Orchestration ETL | Apache Airflow | Standard industrie, forte reconnaissance recruteur, DAG par tenant |
| Base de données | PostgreSQL + Row-Level Security | Isolation multi-tenant démontrable au niveau moteur, plus simple à opérer qu'un schéma-par-tenant |
| Stockage objet / data lake | MinIO (S3-compatible) | Démontre le pattern data lake sans coût cloud ni complexité Spark |
| Machine Learning | scikit-learn, XGBoost | Modèles robustes, rapides à entraîner et à expliquer |
| Explicabilité | SHAP | Exigence non-fonctionnelle du projet |
| Suivi d'expériences | MLflow | Versioning et traçabilité des modèles |
| API de service | FastAPI | Performant, typé, standard pour API Python modernes |
| Conteneurisation | Docker, Docker Compose | Déploiement reproductible, orchestration locale multi-services |
| Tests & CI | Pytest, GitHub Actions | Exigence non-fonctionnelle "code testé avant mise à jour" |
| Protocole agents/outils | MCP (Model Context Protocol) | Standardise l'exposition des données/modèles comme outils, différenciateur fort en 2026 |
| Orchestration multi-agents | LangGraph | Plus proche des patterns de production (state machine explicite) que CrewAI, forte demande marché |
| Restitution / dashboard | Streamlit | Déploiement simple, intégration directe Python/API, remplace Power BI pour la démo publique |
| Facturation SaaS | Stripe (mode test) | Simule un vrai cycle d'abonnement sans transaction réelle |
| Déploiement | Render / Railway | Hébergement gratuit/accessible pour une démo publique consultable par un recruteur |

**Technologies écartées du périmètre d'implémentation** (mentionnées en documentation comme axes d'extension, non développées) : Apache Spark, Power BI, CrewAI.

---

## 9. Contrainte de déploiement (réalisme opérationnel)

Airflow ne tient pas durablement sur les offres gratuites de Render/Railway (nécessite un worker persistant). Approche retenue :

- Airflow tourne en local et en CI pour prouver le pipeline (capturé dans la vidéo de démonstration)
- Seuls l'API FastAPI, le dashboard Streamlit et la couche agents/MCP sont déployés publiquement, pour être testés en direct par un recruteur

---

## 10. Critères de succès

- Le pipeline traite automatiquement les données d'au moins un cas d'usage simulé de bout en bout
- Le modèle produit une prédiction accompagnée d'une explication compréhensible (SHAP)
- L'assistant conversationnel répond correctement à des questions simples sur les données, via l'architecture multi-agents
- Deux tenants simulés n'ont accès qu'à leurs propres données — vérifié par un test automatisé dédié à l'isolation RLS
- Une démonstration vidéo et une documentation complète sont disponibles publiquement

---

## 11. Livrable final

Un dépôt de code public (GitHub) contenant :
- L'ensemble du code, organisé en monorepo par service/phase
- Une documentation détaillée (README, diagramme d'architecture, choix techniques justifiés)
- Une vidéo de démonstration
- Un déploiement public accessible pour consultation par un recruteur (API + dashboard + agents)
