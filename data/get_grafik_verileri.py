import pandas as pd
import os
import sqlite3


def get_grafik_verileri():
    ana_dizin = os.path.dirname(os.path.abspath(__file__))
    db_yolu = os.path.join(ana_dizin, "..", "database.db")
    conn = sqlite3.connect(db_yolu)

    query = """
    SELECT hisse_kodu, adet, ort_maliyet, fiyat, toplam_maliyet, kar_zarar, kar_zarar_oran
    FROM Portfoy_Ozet 
    WHERE kar_zarar != 0
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
