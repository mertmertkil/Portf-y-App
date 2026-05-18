import sqlite3
import os
import pandas as pd


import yfinance as yf  # Kütüphaneyi ekledik


def get_live_price(hisse_kodu):
    try:
        # Yahoo Finance BIST hisselerini .IS uzantısıyla tanır
        ticker_kod = f"{hisse_kodu.upper()}"
        ticker = yf.Ticker(ticker_kod)

        # En güncel fiyatı alalım (fast_info veya history ile)
        data = ticker.history(period="1d")
        if not data.empty:
            return data["Close"].iloc[-1]
        return 0
    except Exception as e:
        print(f"{hisse_kodu} fiyatı alınamadı: {e}")
        return 0


def portfoy_guncelle():
    ana_dizin = os.path.dirname(os.path.abspath(__file__))
    db_yolu = os.path.join(ana_dizin, "..", "database.db")

    db = sqlite3.connect(db_yolu)
    cursor = db.cursor()

    cursor.execute("DELETE FROM Portfoy_Ozet")
    cursor.execute("SELECT DISTINCT hisse_kodu FROM Islemler")
    hisseler = cursor.fetchall()

    tum_kar_zarar = 0
    for row in hisseler:
        hisse_kodu = row[0]  # Tuple içinden string'i aldık
        anlik_fiyat = get_live_price(hisse_kodu)
        anlik_fiyat = round(anlik_fiyat, 2)

        if anlik_fiyat == 0:
            anlik_fiyat = 1.0
        else:
            cursor.execute(
                "SELECT islem_tipi, adet, fiyat FROM Islemler WHERE hisse_kodu = ? ORDER BY tarih ASC",
                (hisse_kodu,),
            )
        islemler = cursor.fetchall()

        print(
            f"\n\n-----{hisse_kodu} hissesi için hesaplamalar başlatılıyor.------\n\n"
        )

        # Temettu hesapalaması
        cursor.execute(
            """
                        SELECT brut_miktar, net_miktar, tarih FROM Temettuler WHERE hisse_kodu = ? ORDER BY tarih ASC
        """,
            (hisse_kodu,),
        )
        temettuler = cursor.fetchall()

        toplam_brut_gelir = 0
        toplam_net_gelir = 0

        for brut_birim, net_birim, t_tarih in temettuler:
            # Temettü tarihine kadar olan (o gün dahil) alış ve satışları topla
            cursor.execute(
                """
                SELECT SUM(CASE WHEN islem_tipi = 'Alış' THEN adet ELSE -adet END) 
                FROM Islemler 
                WHERE hisse_kodu = ? AND tarih <= ?
                """,
                (hisse_kodu, t_tarih),
            )

            sonuc = cursor.fetchone()[0]
            o_tarihteki_adet = sonuc if sonuc is not None else 0

            # Eğer o tarihte elinizde hisse varsa hesapla
            if o_tarihteki_adet > 0:
                donemlik_brut = o_tarihteki_adet * brut_birim
                donemlik_net = o_tarihteki_adet * net_birim

                toplam_brut_gelir += donemlik_brut
                toplam_net_gelir += donemlik_net
            print(
                f"* {t_tarih} * tarihinde dönemlik temettu * {o_tarihteki_adet} * tane hisse için * {round(donemlik_net, 2)} TL. *\n"
            )
            print(
                f"* {hisse_kodu} * için toplam temettu: * {round(toplam_net_gelir, 2)} TL. *\n"
            )

        # ALIŞ SATIŞ Hesaplamaları

        alis_maliyet = 0
        alis_adet = 0
        satis_adet = 0
        toplam_adet = 0
        toplam_maliyet = 0
        ort_maliyet = 0
        satis_bedeli = 0

        for islem_tipi, adet, fiyat in islemler:
            tip_temiz = islem_tipi.strip().upper()

            if tip_temiz == "ALIŞ":
                alis_maliyet += adet * fiyat
                alis_adet += adet
                print(
                    f"* {hisse_kodu} *. için alış işlemi yapılıyor.\n * {adet} * adet, * {fiyat} * TL'den * {adet*fiyat} *' TL'lik {hisse_kodu} alımı yapıldı.\n"
                )
                ort_maliyet = (alis_maliyet / alis_adet) - (
                    toplam_net_gelir / alis_adet
                )

            elif tip_temiz == "SATIŞ":
                satis_adet += adet
                satis_bedeli += fiyat * adet
                print(
                    f"** {hisse_kodu} ** için satış işlemi yapılıyor.\n ** {adet} ** adet, ** {fiyat} ** TL'den ** {adet*fiyat} ** TL'lik ** {hisse_kodu} ** satışı yapıldı.\n"
                )

        toplam_adet = alis_adet - satis_adet
        toplam_maliyet = alis_maliyet - toplam_net_gelir

        if toplam_adet == 0:
            print(
                f"{hisse_kodu} tamamı satıldığı için ortalama maliyet hesaplanmadı.\n"
            )
            pass

        # Kar/Zarar hesaplama: (Anlık Fiyat - Ort. Maliyet) * Adet
        if toplam_adet == 0:
            kar_zarar = satis_bedeli - alis_maliyet
        elif satis_bedeli == 0:
            print(
                f"* {hisse_kodu} * toplam adet :  { toplam_adet} * {anlik_fiyat} eksi { alis_maliyet} ort maliyet {ort_maliyet}\n"
            )
            kar_zarar = (toplam_adet * anlik_fiyat) - toplam_maliyet

        else:
            kar_zarar = (toplam_adet * anlik_fiyat) - (alis_maliyet - satis_bedeli)

        tum_kar_zarar += kar_zarar

        print(f" Tüm kar zarar :  *** {round(tum_kar_zarar)} TL. ***")

        cursor.execute(
            """
            INSERT INTO Portfoy_Ozet(hisse_kodu, adet, ort_maliyet, fiyat, toplam_maliyet, kar_zarar)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (
                hisse_kodu,
                toplam_adet,
                round(ort_maliyet, 2),
                anlik_fiyat,
                round(alis_maliyet, 2),
                round(kar_zarar, 2),
            ),
        )
    db.commit()
    db.close()
    print("\nİşlem başarıyla tamamlandı.")


def get_grafik_verileri():
    ana_dizin = os.path.dirname(os.path.abspath(__file__))
    db_yolu = os.path.join(ana_dizin, "..", "database.db")

    conn = sqlite3.connect(db_yolu)

    query = "SELECT hisse_kodu, adet, ort_maliyet, toplam_maliyet, kar_zarar FROM Portfoy_Ozet WHERE adet > 0 OR kar_zarar != 0"

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


if __name__ == "__main__":
    print("Program başlatıldı...")
    try:
        portfoy_guncelle()
    except Exception as e:
        print(f"Hata oluştu: {e}")
