import streamlit as st
from core.ozet_tablosu import get_grafik_verileri
from ui.charts import portfoy_ozet_grafikleri

st.set_page_config(page_title="Hisse Portföyüm", layout="wide")

st.title("🚀 Portföy Yönetim Paneli")

df = get_grafik_verileri()

if not df.empty:
    # Grafikleri oluştur
    fig_pasta, fig_sutun = portfoy_ozet_grafikleri(df)

    # Görselleştirme Alanı
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig_pasta, use_container_width=True)

    with col2:
        st.plotly_chart(fig_sutun, use_container_width=True)

    # Alt kısımda ham veriyi gösterelim
    with st.expander("Veri Detaylarını Gör"):
        st.table(df)  # Veya st.dataframe(df)
else:
    st.info("Portföyünüzde aktif hisse bulunmuyor.")
