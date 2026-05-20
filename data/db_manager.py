import sqlite3
import pandas as pd
import os


def get_hisse_hareketleri(hisse_kodu):
    ana_dizin = os.path.dirname(os.path.abspath(__file__))
    db_yolu = os.path.join(ana_dizin, "..", "database.db")

    conn = sqlite3.connect(db_yolu)

    # İşlemleri tarih sırasına göre (en yeniden en eskiye) getiriyoruz
    query = """
    SELECT tarih, islem_tipi, adet, fiyat
    FROM Islemler 
    WHERE hisse_kodu = ? 
    ORDER BY tarih DESC
    """

    df = pd.read_sql_query(query, conn, params=(hisse_kodu,))
    conn.close()
    return df


def get_hisse_temettu_detaylari(hisse_kodu):
    conn = sqlite3.connect("database.db")

    # Tarihe göre tersten sıralayarak en son yatan temettüyü en üste alıyoruz
    query = """
    SELECT tarih, net_miktar 
    FROM Temettuler 
    WHERE hisse_kodu = ? 
    ORDER BY tarih DESC
    """

    df = pd.read_sql_query(query, conn, params=(hisse_kodu,))
    conn.close()
    return df
