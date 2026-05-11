import sqlite3
import os


# Veritabanı bağlantısı
def baglanti_kur():
    ana_dizin = os.path.dirname(__file__)
    db_yolu = os.path.join(ana_dizin, "..", "database.db")
    return sqlite3.connect(db_yolu)


# Tablo oluşturma fonksiyonu
def tablo_olustur(db):
    cursor = db.cursor()

    # 1. Hisseler tablosu

    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS Hisseler(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hisse_kodu TEXT NOT NULL,
            hisse_adi TEXT NOT NULL,
            sektor TEXT NOT NULL)
""")

    # 2. İşlemler tablosu

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Islemler(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hisse_kodu TEXT NOT NULL,
            islem_tipi TEXT NOT NULL,
            adet REAL NOT NULL,
            fiyat REAL NOT NULL,
            tarih DATE NOT NULL
    )
""")

    # 3. Fonlar tablosu

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Fonlar(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fon_kodu TEXT NOT NULL,
            islem_tipi TEXT NOT NULL,
            adet REAL NOT NULL,
            birim_fiyat REAL NOT NULL,
            tarih DATE NOT NULL)
""")

    # 4. Temettüler tablosu

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Temettuler(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hisse_kodu TEXT NOT NULL,
            brut_miktar REAL NOT NULL,
            net_miktar REAL NOT NULL,
            tarih DATE NOT NULL
)
""")

    # 5. Portföy özet tablosu

    cursor.execute("""
        CREATE TABLE Portfoy_Ozet (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hisse_kodu TEXT UNIQUE,
            toplam_adet REAL DEFAULT 0,
            ort_maliyet REAL DEFAULT 0,
            satilan_adet REAL DEFAULT 0,
            satis_kari REAL DEFAULT 0,
            temettu_geliri REAL DEFAULT 0,
            real_maliyet REAL DEFAULT 0)
""")

    # 6. Tahvil tablosu

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tahvil(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tahvil_kodu TEXT NOT NULL,
            islem_tipi TEXT NOT NULL,
            fiyat REAL NOT NULL,
            adet REAL NOT NULL,
            kupon_orani REAL,
            vade_sonu DATE NOT NULL)
""")

    # 7. Kuponlar Tablosu

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Kuponlar(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tahvil_kodu TEXT NOT NULL,
        odeme_tarihi DATE NOT NULL,
        oran REAL NOT NULL,   
        islem_durumu TEXT DEFAULT 'BEKLIYOR', -- 'ALINDI' veya 'BEKLIYOR'
        notlar TEXT
            )
""")

    db.commit()


if __name__ == "__main__":
    db = baglanti_kur()

    if db:
        print("... Veritabanı bağlantısı kuruluyor...\n . \n .")
        print("... Veritabanı bağlantısı başarı ile oluşturuldu. ...\n . \n .")
        tablo_olustur(db)
        print("... Tablolar başarı ile oluşturuldu/ güncellendi. ...\n . \n .")
        db.close()
    else:
        print("... Bağlantı sırasında bir hata ile karşılaşıldı. ...\n . \n .")
