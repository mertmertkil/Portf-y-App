import sqlite3
import json
import os


def veritabanini_json_yedekle(json_dosya_adi="veritabanı_yedek.json"):
    # Veritabanı yolunu ayarla
    ana_dizin = os.path.dirname(os.path.abspath(__file__))
    db_yolu = os.path.join(ana_dizin, "..", "database.db")
    json_yolu = os.path.join(ana_dizin, json_dosya_adi)

    db = sqlite3.connect(db_yolu)
    db.row_factory = sqlite3.Row  # Verileri sözlük (dictionary) yapısında çekmek için
    cursor = db.cursor()

    # 1. Veritabanındaki tüm tablo isimlerini al
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
    )
    tablolar = [row[0] for row in cursor.fetchall()]

    yedek_verisi = {}

    for tablo_adi in tablolar:
        # 2. Her tablodaki tüm verileri çek
        cursor.execute(f"SELECT * FROM {tablo_adi}")
        satirlar = cursor.fetchall()

        # Row nesnelerini gerçek sözlüklere dönüştür
        yedek_verisi[tablo_adi] = [dict(satir) for satir in satirlar]

    # 3. JSON dosyasına yaz
    try:
        with open(json_yolu, "w", encoding="utf-8") as f:
            json.dump(yedek_verisi, f, ensure_ascii=False, indent=4)
        print(f"Yedekleme başarılı! Dosya: {json_yolu}")
    except Exception as e:
        print(f"Yedekleme sırasında hata oluştu: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    veritabanini_json_yedekle()
