import sqlite3
import os


def portfoy_guncelle():
    # Veritabanı yolunu ayarla
    ana_dizin = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_yolu = os.path.join(ana_dizin, "database.db")

    conn = sqlite3.connect(db_yolu)
    cursor = conn.cursor()

    print("İşlemler tablosu okunuyor...")

    # 1. Mevcut Portfoy_Ozet tablosunu temizleyelim
    cursor.execute("DELETE FROM Portfoy_Ozet")

    # 2. Tüm işlemleri hisse bazlı çekelim
    cursor.execute("SELECT DISTINCT hisse_kodu FROM Islemler")
    hisseler = cursor.fetchall()

    if not hisseler:
        print(
            "İşlemler tablosunda hiç kayıt bulunamadı! Lütfen DB Browser'dan veri eklediğinizden emin olun."
        )
        return

    for (hisse,) in hisseler:
        print(f"{hisse} hesaplanıyor...")
        cursor.execute(
            "SELECT islem_tipi, adet, fiyat FROM Islemler WHERE hisse_kodu = ? ORDER BY tarih ASC",
            (hisse,),
        )
        islemler = cursor.fetchall()

        toplam_adet = 0
        toplam_maliyet = 0

        for tip, adet, fiyat in islemler:
            if tip.strip().upper() == "ALIŞ":
                toplam_adet += adet
                toplam_maliyet += adet * fiyat
            elif tip.strip().upper() == "SATIŞ":
                # Karı maliyetten düşen senin meşhur stratejin:
                toplam_adet -= adet
                toplam_maliyet -= adet * fiyat

        # Net Maliyet Hesaplama
        net_maliyet = toplam_maliyet / toplam_adet if toplam_adet > 0 else 0

        # 3. Özeti tabloya kaydet (Sütun isimleri: hisse_kodu, toplam_adet, net_maliyet, toplam_sermaye_harcamasi)
        # Sütun adını değiştirdiğini varsayıyorum:
        cursor.execute(
            """
            INSERT INTO Portfoy_Ozet (hisse_kodu, toplam_adet, net_maliyet, net_sermaye_harcamasi)
            VALUES (?, ?, ?, ?)
            """,
            (hisse, toplam_adet, round(net_maliyet, 2), round(toplam_maliyet, 2)),
        )

    conn.commit()
    conn.close()
    print("\n--- Hesaplama Başarıyla Tamamlandı! ---")
    print("Portfoy_Ozet tablosu güncellendi. DB Browser'dan kontrol edebilirsin.")


if __name__ == "__main__":
    print("Program başlatıldı...")
    try:
        portfoy_guncelle()
    except Exception as e:
        print(f"HATA OLUŞTU: {e}")
