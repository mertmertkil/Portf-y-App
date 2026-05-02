import sqlite3
import os


def baglanti_kur():
    # os.path.abspath kullanarak tam yolu garantiye alıyoruz
    ana_dizin = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_yolu = os.path.join(ana_dizin, "database.db")
    return sqlite3.connect(db_yolu)


def tablo_olustur():
    conn = baglanti_kur()
    cursor = conn.cursor()

    # Mevcut tablolara dokunmaz, eksik olanı oluşturur
    cursor.execute(""" CREATE TABLE IF NOT EXISTS Islemler(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hisse_kodu TEXT NOT NULL,
        islem_tipi TEXT NOT NULL, 
        adet REAL NOT NULL,
        fiyat REAL NOT NULL,
        tarih DATE NOT NULL
    )""")

    # HİSSELER TABLOSU OLUŞTURULUYOR
    cursor.execute(""" CREATE TABLE IF NOT EXISTS Hisseler(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hisse_kodu TEXT NOT NULL,
        hisse_adi TEXT NOT NULL,
        sektor TEXT NOT NULL
        )
        """)

    # TEMETTÜ TABLOSU OLUŞTURULUYOR
    cursor.execute("""CREATE TABLE IF NOT EXISTS Temettuler(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hisse_kodu TEXT NOT NULL,
        miktar_net REAL NOT NULL,
        tarih DATE NOT NULL
    )
    """)

    # Portföy özet tablosu oluşturuluyor
    # db_create.py içindeki tablo yapısını şöyle güncelleyebilirsin:
    cursor.execute(""" CREATE TABLE IF NOT EXISTS Portfoy_Ozet(
    hisse_kodu TEXT PRIMARY KEY,
    toplam_adet REAL DEFAULT 0,
    net_maliyet REAL DEFAULT 0,
    toplam_sermaye_harcamasi REAL DEFAULT 0 -- 'toplam_kar_zarar' yerine
    )
""")

    cursor.execute(""" CREATE TABLE IF NOT EXISTS Fonlar(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fon_kodu TEXT NOT NULL,
        islem_tipi TEXT NOT NULL,
        adet REAL NOT NULL,
        birim_fiyat REAL NOT NULL,
        tarih DATE NOT NULL)
""")

    # Buraya diğer tablolarını (Fon_Islemleri, Temettuler vb.) aynı mantıkla ekle

    conn.commit()
    conn.close()


if __name__ == "__main__":
    # Sadece bu dosya elle çalıştırıldığında kontrol yapar
    tablo_olustur()
    print("Kontrol tamamlandı, mevcut verileriniz korundu.")
