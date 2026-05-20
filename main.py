import streamlit as st
import pandas as pd
from core.ozet_tablosu import get_grafik_verileri
from ui.charts import portfoy_ozet_grafikleri

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="Mert Portföy", layout="wide")

# 2. Başlık
st.title("📊 Mertkil Portföy Yönetim Sistemi")
st.divider()

df = get_grafik_verileri()

if not df.empty:
    # --- YAN YANA DÜZEN ---
    # col1 (Grafik için) ve col2 (Tablo için) alanlarını oluşturuyoruz.
    # [1, 1.2] oranı tablonun biraz daha geniş durmasını sağlar.
    col1, col2 = st.columns([1, 1.2], gap="medium")

    with col1:
        st.subheader("🍕 Sermaye Dağılımı")
        fig_pasta = portfoy_ozet_grafikleri(df)
        # Grafiği sütun genişliğine sığdırıyoruz
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

        # Pandas map (yeni sürüm) ile stil uygulama
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

        # Tabloyu göster
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

    # --- Alt Kısım: Seçim Widget'ı ---
    selected = st.selectbox(
        "Detaylı analiz için bir hisse seçin:",
        df["hisse_kodu"].unique(),
        index=None,
        placeholder="Hisse seçiniz...",
    )

    if selected:
        st.session_state["aktif_hisse"] = selected
        st.success(
            f"{selected} seçildi! Sol menüden 'Hisse Analizi' sayfasına geçebilirsiniz."
        )

else:
    st.warning("Görüntülenecek veri bulunamadı.")
