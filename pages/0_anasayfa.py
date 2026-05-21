import streamlit as st
from core.ozet_tablosu import get_grafik_verileri, portfoy_guncelle
from ui.charts import portfoy_ozet_grafikleri
from data.db_json import veritabanini_json_yedekle

veritabanini_json_yedekle(json_dosya_adi="veritabanı_yedek.json")


# 2. Başlık ve Güncelleme Butonu
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
        st.switch_page("pages/1_hisse_detay.py")

else:
    st.warning("Görüntülenecek veri bulunamadı.")
