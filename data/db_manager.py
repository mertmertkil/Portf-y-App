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
    ana_dizin = os.path.dirname(os.path.abspath(__file__))
    db_yolu = os.path.join(ana_dizin, "..", "database.db")
    conn = sqlite3.connect(db_yolu)
    cursor = conn.cursor()

    # Temettüleri çek
    cursor.execute(
        "SELECT net_miktar, tarih FROM Temettuler WHERE hisse_kodu = ? ORDER BY tarih ASC",
        (hisse_kodu,),
    )
    temettuler = cursor.fetchall()

    sonuclar = []
    for net_birim, t_tarih in temettuler:
        # O tarihteki toplam hisse adedini hesapla (Alış - Satış)
        cursor.execute(
            """
            SELECT SUM(CASE WHEN islem_tipi = 'Alış' THEN adet ELSE -adet END) 
            FROM Islemler 
            WHERE hisse_kodu = ? AND tarih <= ?
        """,
            (hisse_kodu, t_tarih),
        )

        adet_sonuc = cursor.fetchone()[0]
        o_tarihteki_adet = adet_sonuc if adet_sonuc is not None else 0

        # Toplam yatan parayı hesapla
        toplam_net_kazanc = o_tarihteki_adet * net_birim

        sonuclar.append(
            {
                "tarih": t_tarih,
                "birim_net": net_birim,
                "o_tarihteki_adet": o_tarihteki_adet,
                "toplam_net_kazanc": toplam_net_kazanc,
            }
        )

    conn.close()
    return pd.DataFrame(sonuclar)
