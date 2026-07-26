-- Schéma multi-tenant : tables + Row-Level Security (isolation par tenant)

-- 1. Table des entreprises clientes (tenants)
CREATE TABLE tenants (
    id   SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

-- 2. Table métier d'exemple : les ventes de chaque tenant
CREATE TABLE sales (
    id        SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    product   TEXT NOT NULL,
    amount    NUMERIC NOT NULL,
    sold_at   DATE NOT NULL
);

-- 3. Active la Row-Level Security sur la table sales
ALTER TABLE sales ENABLE ROW LEVEL SECURITY;

-- 4. Policy : une requête ne voit que les lignes dont le tenant_id
--    correspond au tenant courant (défini via `SET app.current_tenant = ...`)
CREATE POLICY tenant_isolation ON sales
    USING (tenant_id = current_setting('app.current_tenant')::INTEGER);

-- 5. Deux tenants simulés pour tester l'isolation
INSERT INTO tenants (name) VALUES ('PME Alpha'), ('PME Beta');

-- 6. Quelques ventes factices pour chacun
INSERT INTO sales (tenant_id, product, amount, sold_at) VALUES
    (1, 'Ordinateur portable', 8500, '2026-01-10'),
    (1, 'Souris sans fil',     150,  '2026-01-12'),
    (2, 'Chaise de bureau',    900,  '2026-01-11'),
    (2, 'Bureau réglable',     2200, '2026-01-15');

-- 7. Utilisateur applicatif "normal" (non superutilisateur) : c'est lui que
--    l'API utilisera plus tard, et c'est lui qui est réellement soumis à la RLS
--    (saas_admin, superutilisateur, contourne toujours la RLS)
CREATE ROLE app_user LOGIN PASSWORD 'app_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON sales TO app_user;
GRANT SELECT ON tenants TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
