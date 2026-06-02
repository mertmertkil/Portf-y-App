import streamlit as st
from core.ozet_tablosu import get_grafik_verileri, portfoy_guncelle
from ui.charts import portfoy_ozet_grafikleri
from data.db_json import veritabanini_json_yedekle
import os
import sqlite3
from data.db_manager import get_hisse_temettu_detaylari
import yfinance as yf

veritabanini_json_yedekle(json_dosya_adi="veritabanı_yedek.json")


def get_bist100_price():
    try:
        # yfinance üzerinden BIST 100 endeksini çekiyoruz
        bist = yf.Ticker("XU100.IS")
        data = bist.history(period="1d")
        if not data.empty:
            current_price = data["Close"].iloc[-1]
            prev_close = data["Open"].iloc[-1]  # Basit değişim hesabı için
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100
            return current_price, change_percent
        return None, None
    except:
        return None, None


# --- BAŞLIK VE GÜNCELLEME BUTONU ---
col_title, col_btn = st.columns([4, 1])

with col_title:
    st.title("📊 Mertkil Portföy Yönetim Sistemi")

with col_btn:
    st.write("")  # Boşluk için
    if st.button("🔄 Fiyatları Güncelle"):
        with st.spinner("Canlı fiyatlar çekiliyor..."):
            portfoy_guncelle()  # Yahoo Finance'ten çekip DB'yi günceller
            st.rerun()  # Sayfayı yeni verilerle tazeler

st.divider()


df = get_grafik_verileri()
df_hepsi = get_grafik_verileri()

if not df_hepsi.empty:
    # Ana sayfa sadece elindeki (adedi 0'dan büyük olan) hisseleri göstersin
    df = df_hepsi[df_hepsi["adet"] > 0].copy()

if not df.empty:
    # --- ÜST ÖZET METRİK KARTLARI (DİNAMİK) ---
    toplam_maliyet = df["toplam_maliyet"].sum()
    toplam_guncel_deger = (df["adet"] * df["fiyat"]).sum()
    toplam_kar_zarar = df["kar_zarar"].sum()

    genel_kz_oran = (
        (toplam_kar_zarar / toplam_maliyet * 100) if toplam_maliyet > 0 else 0.0
    )

    # --- TÜM HİSSELERİN GERÇEK TOPLAM TEMETTÜLERİNİ HESAPLAMA ---
    toplam_alinan_temettu = 0.0

    # Portföydeki benzersiz hisse kodlarını geziyoruz
    for hisse in df["hisse_kodu"].unique():
        # Senin detay sayfasında kullandığın fonksiyonu çağırıyoruz
        df_hisse_temettu = get_hisse_temettu_detaylari(hisse)

        # Eğer bu hisseye ait ödeme geçmişi varsa, adetle çarpılmış "toplam_net_kazanc" sütununu topluyoruz
        if (
            not df_hisse_temettu.empty
            and "toplam_net_kazanc" in df_hisse_temettu.columns
        ):
            toplam_alinan_temettu += df_hisse_temettu["toplam_net_kazanc"].sum()

    bist_fiyat, bist_degisim = get_bist100_price()

    # 3'lü Kart Düzeni
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric(
            label="💼 Toplam Portföy Değeri",
            value=f"{toplam_guncel_deger:,.2f} TL",
            delta=f"Maliyet: {toplam_maliyet:,.2f} TL",
            delta_color="off",
        )
        with m1:
            reel_maliyet = toplam_maliyet - toplam_alinan_temettu
            st.metric(
                label="💼 Toplam Portföy Değeri",
                value=f"{toplam_guncel_deger:,.2f} TL",
                delta=f"Reel Maliyet: {reel_maliyet:,.2f} TL (Maliyet - Temettü)",
                delta_color="off",  # Gri alt bilgi olarak şık durur
            )

    with m2:
        st.metric(
            label="📈 Toplam Kâr / Zarar Durumu",
            value=f"{toplam_kar_zarar:,.2f} TL",
            delta=f"%{genel_kz_oran:.2f}",
        )

    with m3:
        st.metric(
            label="💰 Toplam Alınan Temettü",
            value=f"{toplam_alinan_temettu:,.2f} TL",
            delta="Toplam Pasif Gelir",
            delta_color="normal",
        )

    with m4:
        if bist_fiyat:
            st.metric(
                label="🏛️ BIST 100",
                value=f"{bist_fiyat:,.2f}",
                delta=f"%{bist_degisim:.2f}",
            )
        else:
            st.metric(label="🏛️ BIST 100", value="Yüklenemedi")

    st.divider()
    # --- YAN YANA DÜZEN (PASTA GRAFİĞİ VE TABLO) ---
    col1, col2 = st.columns([1, 1.2], gap="medium")

    with col1:
        st.subheader("🍕 Sermaye Dağılımı")
        fig_pasta = (
            portfoy_ozet_grafikleri(df)
            if "portfoy_ozet_grafikleri" in globals()
            else portfoy_ozet_grafikleri(df)
        )
        st.plotly_chart(fig_pasta, use_container_width=True)

    with col2:
        st.subheader("📋 Portföy Durumu")

        # Renklendirme fonksiyonu
        def style_kar_zarar(v):
            color = "#2ecc71" if v > 0 else "#e74c3c" if v < 0 else "white"
            return f"color: {color}; font-weight: bold"

        view_df = df[
            [
                "hisse_kodu",
                "adet",
                "ort_maliyet",
                "fiyat",
                "kar_zarar",
                "kar_zarar_oran",
            ]
        ]

        styled_df = view_df.style.map(
            style_kar_zarar, subset=["kar_zarar", "kar_zarar_oran"]
        ).format(
            {
                "ort_maliyet": "{:.2f} TL",
                "fiyat": "{:.2f} TL",
                "kar_zarar": "{:,.2f} TL",
                "kar_zarar_oran": "%{:,.2f}",
            }
        )

        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "hisse_kodu": "Hisse",
                "adet": "Adet",
                "ort_maliyet": "Maliyet",
                "fiyat": "Anlık",
                "kar_zarar": "K/Z",
                "kar_zarar_oran": "Kâr/Zarar (%)",
            },
        )

    st.divider()


else:
    st.warning("Görüntülenecek veri bulunamadı.")
