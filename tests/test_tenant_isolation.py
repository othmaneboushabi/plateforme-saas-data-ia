"""Vérifie qu'un tenant ne peut jamais lire les données d'un autre tenant."""

import os

import psycopg

DSN = os.environ.get(
    "DATABASE_DSN",
    "host=localhost port=5434 dbname=saas_platform user=app_user password=app_password",
)


def sales_visible_for(tenant_id: int) -> list[tuple]:
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.current_tenant', %s, false)", (str(tenant_id),))
            cur.execute("SELECT id, tenant_id FROM sales")
            return cur.fetchall()


def test_tenant_1_ne_voit_que_ses_propres_ventes():
    rows = sales_visible_for(1)
    assert len(rows) > 0
    assert all(tenant_id == 1 for _, tenant_id in rows)


def test_tenant_2_ne_voit_que_ses_propres_ventes():
    rows = sales_visible_for(2)
    assert len(rows) > 0
    assert all(tenant_id == 2 for _, tenant_id in rows)


def test_tenant_1_et_tenant_2_ne_voient_pas_les_memes_lignes():
    ids_tenant_1 = {row_id for row_id, _ in sales_visible_for(1)}
    ids_tenant_2 = {row_id for row_id, _ in sales_visible_for(2)}
    assert ids_tenant_1.isdisjoint(ids_tenant_2)
