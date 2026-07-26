"""Vérifie que l'ingestion CSV range chaque vente sous le bon tenant."""

import os

import psycopg

from services.ingestion.ingest_csv import DSN, ingest_csv


def test_ingestion_tague_les_lignes_avec_le_bon_tenant(tmp_path):
    csv_path = tmp_path / "ventes_test.csv"
    csv_path.write_text(
        "product,amount,sold_at\n"
        "Produit test A,100,2026-03-01\n"
        "Produit test B,200,2026-03-02\n"
    )

    nb_lignes = ingest_csv(str(csv_path), tenant_id=1)
    assert nb_lignes == 2

    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.current_tenant', '1', false)")
            cur.execute(
                "SELECT product FROM sales WHERE product IN ('Produit test A', 'Produit test B')"
            )
            produits_inseres = {row[0] for row in cur.fetchall()}

            # nettoyage : on retire les lignes de test pour que le test reste rejouable
            cur.execute(
                "DELETE FROM sales WHERE product IN ('Produit test A', 'Produit test B')"
            )
        conn.commit()

    assert produits_inseres == {"Produit test A", "Produit test B"}
