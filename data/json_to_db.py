# bir sorun halinde veritabanına aktaracak kodlar.

import sqlite3
import json
import os


def json_yedeginden_geri_yukle(json_dosya_adi="veritabanı_yedek.json"):
    # Dosya yolları
    ana_dizin = os.path.dirname(os.path.abspath(__file__))
    db_yolu = os.path.join(ana_dizin, "..", "database.db")
    json_yolu = os.path.join(ana_dizin, json_dosya_adi)

    if not os.path.exists(json_yolu):
        print("Hata: Yedek dosyası bulunamadı!")
        return

    with open(json_yolu, "r", encoding="utf-8") as f:
        yedek_verisi = json.load(f)

    db = sqlite3.connect(db_yolu)
    cursor = db.cursor()

    try:
        for tablo_adi, satirlar in yedek_verisi.items():
            if not satirlar:
                continue

            # 1. Önce mevcut tablonun içini temizleyelim (çakışma olmaması için)
            cursor.execute(f"DELETE FROM {tablo_adi}")

            # 2. Sütun isimlerini JSON'daki ilk veriden çekelim
            sutunlar = list(satirlar[0].keys())
            sutun_adlari = ", ".join(sutunlar)
            yer_tutucular = ", ".join(["?" for _ in sutunlar])

            # 3. Verileri toplu halde ekleyelim (Batch Insert)
            ekleme_sorgusu = (
                f"INSERT INTO {tablo_adi} ({sutun_adlari}) VALUES ({yer_tutucular})"
            )

            veri_listesi = [tuple(satir.values()) for satir in satirlar]
            cursor.executemany(ekleme_sorgusu, veri_listesi)

            print(f"[{tablo_adi}] tablosuna {len(satirlar)} kayıt geri yüklendi.")

        db.commit()
        print("\nVeritabanı başarıyla eski haline döndürüldü!")

    except Exception as e:
        db.rollback()  # Bir hata olursa işlemleri geri al
        print(f"Geri yükleme sırasında kritik hata: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    # DİKKAT: Bu fonksiyon mevcut verilerin üzerine yazar!
    onay = input(
        "Mevcut veriler silinecek. Geri yüklemek istediğinize emin misiniz? (E/H): "
    )
    if onay.lower() == "e":
        json_yedeginden_geri_yukle()
