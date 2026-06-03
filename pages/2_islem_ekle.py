import streamlit as st
import sqlite3
import os
from datetime import datetime


# 1. HATA DÜZELTİLDİ: Fonksiyona dışarıdan gelecek parametreler eklendi
def islem_ekle_to_db(hisse, tip, adet, fiyat, tarih):
    try:
        # pages klasöründen bir üst dizine çıkıp database.db'yi bulur
        ana_dizin = os.path.dirname(os.path.abspath(__file__))
        db_yolu = os.path.join(ana_dizin, "..", "database.db")

        db = sqlite3.connect(db_yolu)
        cursor = db.cursor()

        cursor.execute(
            """
                       INSERT INTO Islemler (hisse_kodu, islem_tipi, adet, fiyat, tarih)
                       VALUES (?, ?, ?, ?, ?)""",
            (hisse, tip, adet, fiyat, tarih),
        )

        db.commit()
        db.close()
        return True
    except sqlite3.OperationalError as e:
        st.error(
            f"Tablo veya Sütun Hatası: Lütfen veri tabanındaki sütun isimlerini kontrol edin. Detay: {e}"
        )
        return False
    except Exception as e:
        st.error(f"Beklenmedik bir hata oluştu: {e}")
        return False


# --- ÜST NAVİGASYON VE BAŞLIK ---
col_back, col_title = st.columns([1, 5])

with col_back:
    # Ana sayfaya dönme butonu
    if st.button("⬅️ Ana Sayfa"):
        st.switch_page("pages/0_anasayfa.py")

with col_title:
    st.title("➕ Yeni İşlem Ekle")
    st.write("Mevcut işlemler tablonuza yeni bir alım veya satım kaydı ekleyin.")


st.divider()


with st.form("yeni_islem_formu", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        hisse_kodu = (
            st.text_input("Hisse Kodu", placeholder="Örn: TUPRS").upper().strip()
        )
        islem_tipi = st.selectbox("İşlem Tipi", ["Alış", "Satış"])
        islem_tarihi = st.date_input("İşlem Tarihi", datetime.now().date())

    with col2:
        adet = st.number_input("Adet", min_value=1, step=1, value=10)
        fiyat = st.number_input(
            "Birim Fiyat (TL)", min_value=0.01, step=0.01, format="%.2f", value=10.00
        )

    # Buton formun tam içinde olmalı
    submit_button = st.form_submit_button("İşlemi Veri Tabanına Kaydet")

# 3. HATA DÜZELTİLDİ: Tıklama kontrolü form bittikten sonra en dış hizaya alındı
if submit_button:
    if not hisse_kodu:
        st.warning("Lütfen geçerli bir hisse kodu girin.")
    else:
        # 1. Girdiyi temizle, büyük harfe çevir ve boşlukları at
        temiz_hisse = hisse_kodu.upper().strip()

        # 2. Eğer zaten sonunda .IS yoksa otomatik olarak ekle
        if not temiz_hisse.endswith(".IS"):
            temiz_hisse = f"{temiz_hisse}.IS"

        # Tarihi veri tabanına standart metin formatında (YYYY-MM-DD) kaydediyoruz
        tarih_str = islem_tarihi.strftime("%Y-%m-%d")

        # Fonksiyonu .IS formatına getirilmiş temiz_hisse değişkeniyle çağırıyoruz
        if islem_ekle_to_db(temiz_hisse, islem_tipi, adet, fiyat, tarih_str):
            st.success(
                f"İşlem başarıyla '{temiz_hisse}' olarak 'Islemler' tablosuna eklendi! Ana sayfadaki özet tablonuz otomatik olarak güncellenecektir."
            )
