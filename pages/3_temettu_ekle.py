import streamlit as st
import sqlite3
import os
from datetime import datetime

# --- ÜST NAVİGASYON VE BAŞLIK ---
col_back, col_title = st.columns([1, 5])

with col_back:
    # Ana sayfaya dönme butonu
    if st.button("⬅️ Ana Sayfa"):
        st.switch_page("pages/0_anasayfa.py")

with col_title:
    st.title("💰 Yeni Temettü Ödemesi Ekle")
    st.write("Almış olduğunuz temettü ödemelerini veri tabanına kaydedin.")

st.divider()


def temettu_ekle_to_db(hisse, brut, net, tarih):
    try:
        # pages klasöründen bir üst dizine çıkıp database.db'yi bulur
        ana_dizin = os.path.dirname(os.path.abspath(__file__))
        db_yolu = os.path.join(ana_dizin, "..", "database.db")

        db = sqlite3.connect(db_yolu)
        cursor = db.cursor()

        # Temettuler tablosunun sütun yapısına uygun INSERT sorgusu
        cursor.execute(
            """
                       INSERT INTO Temettuler (hisse_kodu, brut_miktar, net_miktar, tarih)
                       VALUES (?, ?, ?, ?)""",
            (hisse, brut, net, tarih),
        )

        db.commit()
        db.close()
        return True
    except sqlite3.OperationalError as e:
        st.error(
            f"Tablo veya Sütun Hatası: Lütfen 'Temettuler' tablosundaki sütun isimlerini kontrol edin. Detay: {e}"
        )
        return False
    except Exception as e:
        st.error(f"Beklenmedik bir hata oluştu: {e}")
        return False


# --- KULLANICI ARAYÜZÜ FORMU ---
with st.form("yeni_temettu_formu", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        hisse_kodu = (
            st.text_input("Hisse Kodu", placeholder="Örn: FROTO").upper().strip()
        )
        temettu_tarihi = st.date_input("Ödeme Tarihi", datetime.now().date())

    with col2:
        brut_miktar = st.number_input(
            "Toplam Brüt Miktar (TL)",
            min_value=0.00,
            step=0.01,
            format="%.2f",
            value=0.00,
        )
        net_miktar = st.number_input(
            "Toplam Net Miktar (TL)",
            min_value=0.00,
            step=0.01,
            format="%.2f",
            value=0.00,
        )

        # Küçük bir yardım: Eğer kullanıcı net miktarı girmeyi unutursa
        # veya pratiklik olsun diye brüt yazıldığında stopajı (%10) otomatik hesaplamak istersen,
        # varsayılan değerleri form gönderilirken de check edebiliriz.

    submit_button = st.form_submit_button("Temettü Kaydını Veri Tabanına İşle")

if submit_button:
    if not hisse_kodu:
        st.warning("Lütfen geçerli bir hisse kodu girin.")
    elif brut_miktar <= 0 or net_miktar <= 0:
        st.warning("Lütfen brüt ve net miktarları sıfırdan büyük giriniz.")
    else:
        # .IS uzantı kontrolü ve standardizasyon
        temiz_hisse = hisse_kodu
        if not temiz_hisse.endswith(".IS"):
            temiz_hisse = f"{temiz_hisse}.IS"

        tarih_str = temettu_tarihi.strftime("%Y-%m-%d")

        if temettu_ekle_to_db(temiz_hisse, brut_miktar, net_miktar, tarih_str):
            st.success(
                f"💰 {temiz_hisse} için Net {net_miktar:.2f} TL temettü kaydı başarıyla eklendi!"
            )
