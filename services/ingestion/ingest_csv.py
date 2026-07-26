"""Ingestion d'un fichier CSV de ventes pour un tenant donné.

Lit un CSV (colonnes: product, amount, sold_at) et insère chaque ligne
dans la table `sales`, taguée avec le tenant_id fourni.
"""

import os
import sys

import pandas as pd
import psycopg

DSN = os.environ.get(
    "DATABASE_DSN",
    "host=localhost port=5434 dbname=saas_platform user=app_user password=app_password",
)


def ingest_csv(csv_path: str, tenant_id: int) -> int:
    df = pd.read_csv(csv_path)

    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.current_tenant', %s, false)", (str(tenant_id),))
            for _, row in df.iterrows():
                cur.execute(
                    "INSERT INTO sales (tenant_id, product, amount, sold_at) VALUES (%s, %s, %s, %s)",
                    (tenant_id, row["product"], row["amount"], row["sold_at"]),
                )
        conn.commit()

    return len(df)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python ingest_csv.py <chemin_csv> <tenant_id>")
        sys.exit(1)

    path, tid = sys.argv[1], int(sys.argv[2])
    nb_lignes = ingest_csv(path, tid)
    print(f"{nb_lignes} ligne(s) insérée(s) pour le tenant {tid}.")
