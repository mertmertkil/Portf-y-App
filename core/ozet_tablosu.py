import os
import sys

ana_dizin = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if ana_dizin not in sys.path:
    sys.path.append(ana_dizin)

import sqlite3
from data.live_price import get_live_price
from data.get_grafik_verileri import get_grafik_verileri


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
        kar_zarar_oran = 0

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

        if alis_adet > 0:
            ort_alis_fiyati = alis_maliyet / alis_adet
        else:
            ort_alis_fiyati = 0

        if satis_adet > 0:
            ort_satis_fiyati = satis_bedeli / satis_adet
        else:
            ort_satis_fiyati = 0
        # ------------------------------------------

        if toplam_adet == 0:
            kar_zarar = satis_bedeli - alis_maliyet
        elif satis_bedeli == 0:
            kar_zarar = (toplam_adet * anlik_fiyat) - toplam_maliyet
        else:
            kar_zarar = (toplam_adet * anlik_fiyat) - (alis_maliyet - satis_bedeli)

        if toplam_maliyet > 0:
            kar_zarar_oran = (kar_zarar / toplam_maliyet) * 100

        tum_kar_zarar += kar_zarar

        print(f" Tüm kar zarar :  *** {round(tum_kar_zarar)} TL. ***")

        cursor.execute(
            """
            INSERT INTO Portfoy_Ozet(hisse_kodu, adet, ort_maliyet, fiyat, toplam_maliyet, kar_zarar, kar_zarar_oran, ort_alis_fiyati, ort_satis_fiyati)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                hisse_kodu,
                round(toplam_adet, 2),
                round(ort_maliyet, 2),
                anlik_fiyat,
                round(alis_maliyet, 2),
                round(kar_zarar, 2),
                round(kar_zarar_oran, 2),
                round(ort_alis_fiyati, 2),  # Buranın 0 olmadığından emin oluyoruz
                round(ort_satis_fiyati, 2),  # Buranın 0 olmadığından emin oluyoruz
            ),
        )
    db.commit()
    db.close()
    print("\nİşlem başarıyla tamamlandı.")


if __name__ == "__main__":
    print("Program başlatıldı...")
    try:
        portfoy_guncelle()
    except Exception as e:
        print(f"Hata oluştu: {e}")
