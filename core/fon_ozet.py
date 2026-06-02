import sqlite3
import os
import pandas as pd


def portfoy_guncelle():
    ana_dizin = os.path.dirname(os.path.abspath(__file__))
    db_yolu = os.path.join(ana_dizin, "..", "database.db")

    try:
        db = sqlite3.connect(db_yolu)
        cursor = db.cursor()

        cursor.execute("DELETE FROM Fon_Ozet")
        cursor.execute("SELECT DISTINCT fon_kodu FROM Fonlar")
        fonlar = cursor.fetchall()

        print(f"FONLAR ARANIYOR...\n")

        for (fon_kodu,) in fonlar:
            alis_maliyet = 0
            satis_bedeli = 0
            alis_adet = 0
            satis_adet = 0

            cursor.execute(
                "SELECT islem_tipi, adet, birim_fiyat FROM Fonlar WHERE fon_kodu = ? ORDER BY tarih ASC",
                (fon_kodu,),
            )
            islemler = cursor.fetchall()

            for tip, adet, fiyat in islemler:
                tip_temiz = tip.strip().upper()

                if tip_temiz == "ALIŞ":
                    alis_maliyet += adet * fiyat
                    alis_adet += adet
                elif tip_temiz == "SATIŞ":
                    satis_bedeli += adet * fiyat
                    satis_adet += adet

            kar_zarar = satis_bedeli - alis_maliyet
            kar_zarar = round(kar_zarar, 2)

            cursor.execute(
                "INSERT INTO Fon_Ozet(fon_kodu, kar_zarar) VALUES (?, ?)",
                (fon_kodu, kar_zarar),
            )
            print(f"{fon_kodu} için Kar/Zarar: {round(kar_zarar, 2)} TL")

        db.commit()
        print("\nİşlem başarıyla tamamlandı.")

    except Exception as e:
        print(f"Hata oluştu: {e}")
    finally:
        if "db" in locals():
            db.close()


def get_fon_verileri():
    ana_dizin = os.path.dirname(os.path.abspath(__file__))
    db_yolu = os.path.join(ana_dizin, "..", "database.db")
    conn = sqlite3.connect(db_yolu)

    query = """
    SELECT fon_kodu, kar_zarar
    FROM Fon_Ozet 
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


if __name__ == "__main__":
    portfoy_guncelle()
