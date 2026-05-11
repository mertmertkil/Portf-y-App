import sqlite3
import os


def portfoy_guncelle():
    # Dosya yolu ayarı
    ana_dizin = os.path.dirname(os.path.abspath(__file__))
    db_yolu = os.path.join(ana_dizin, "..", "database.db")

    db = sqlite3.connect(db_yolu)
    cursor = db.cursor()

    print("İşlemler tablosu okunuyor...\n")

    # 1. Önce portföy özet tablosunu temizleyelim.
    cursor.execute("DELETE FROM Portfoy_Ozet")

    # 2. Tüm işlemleri hisse bazlı çekelim.
    cursor.execute("SELECT DISTINCT hisse_kodu FROM Islemler")
    hisseler = cursor.fetchall()

    if not hisseler:
        print("Hiç işlem bulunamadı. Veri tabanını kontrol edin.")
        return

    for satir in hisseler:
        hisse = satir[0]
        # işlemler tablosu ile temettü tablosunu sanal olarak birleştiriyoruz ki tarihe göre hesap yapabilelim.
        cursor.execute(
            """
            SELECT 'ISLEM' as kaynak, islem_tipi, adet, fiyat, 0 as brut, 0 as net, tarih
             FROM Islemler WHERE hisse_kodu = ?
             UNION ALL
             SELECT 'TEMETTU' as kaynak, 'TEMETTU' as islem_tipi, 0 as adet, 0 as fiyat, brut_miktar, net_miktar, tarih
             FROM Temettuler WHERE hisse_kodu = ?
             ORDER BY tarih ASC
         """,
            (hisse, hisse),
        )

        zaman_cizelgesi = cursor.fetchall()
        toplam_kar = 0
        alinan_adet = 0
        alis_maliyeti = 0
        toplam_adet = 0
        toplam_satis_degeri = 0
        toplam_satilan_adet = 0
        toplam_temettu_geliri = 0
        ort_maliyet = 0
        toplam_brut_temettu = 0

        for kaynak, tip, adet, fiyat, brut_birim, net_birim, tarih in zaman_cizelgesi:
            tip_temiz = tip.strip().upper()

            if tip_temiz == "ALIŞ":
                alinan_adet += adet
                toplam_adet += adet
                alis_maliyeti += adet * fiyat

            elif tip_temiz == "SATIŞ":
                if toplam_adet > 0:
                    toplam_satis_degeri += adet * fiyat
                    toplam_satilan_adet += adet
                    toplam_adet -= adet

            elif tip_temiz == "TEMETTU":
                toplam_temettu_geliri += toplam_adet * net_birim
                toplam_brut_temettu += toplam_adet * brut_birim

        mevcut_adet = alinan_adet - toplam_satilan_adet

        real_maliyet = round(
            (alis_maliyeti - toplam_satis_degeri)
            - (
                toplam_temettu_geliri * 2
            ),  # hisse alımına eklendiği için 2 ile çarptım.
            2,
        )

        if mevcut_adet > 0:
            # 1. Ham Ortalama Maliyet (Brüt temettü düşülmemiş)
            # Sadece alışları baz alır: Toplam Alış Tutarı / Toplam Alınan Adet
            ham_ort_maliyet = alis_maliyeti / alinan_adet

            # 2. Brüt Temettü Düşülmüş Ortalama Maliyet
            # (Toplam Alış Tutarı - Toplam Brüt Temettü) / Alınan Adet
            ort_maliyet = round((alis_maliyeti - toplam_brut_temettu) / alinan_adet, 2)

        else:
            ort_maliyet = 0
            real_maliyet = 0

        cursor.execute(
            """
             INSERT INTO Portfoy_Ozet
             (hisse_kodu, toplam_adet, ort_maliyet, satilan_adet, satis_kari, temettu_geliri, real_maliyet)
             VALUES (?, ?, ?, ?, ?, ?, ?)
         """,
            (
                hisse,
                toplam_adet,
                ort_maliyet,
                toplam_satilan_adet,
                round(toplam_satis_degeri, 2),
                round(toplam_temettu_geliri, 2),
                real_maliyet,
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
