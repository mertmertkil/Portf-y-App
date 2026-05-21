import streamlit as st
import pandas as pd
from core.ozet_tablosu import get_grafik_verileri, portfoy_guncelle
from ui.charts import portfoy_ozet_grafikleri
from data.db_json import veritabanini_json_yedekle

# 1. TÜM UYGULAMANIN AYARINI BURADA YAP (Hata almamak için en üstte olmalı)
st.set_page_config(page_title="Mert Portföy", layout="wide")

# Sayfaları tanımla
ana_sayfa = st.Page("pages/0_anasayfa.py", title="Genel Özet", icon="🏠")
detay_sayfasi = st.Page(
    "pages/1_hisse_detay.py", title="Hisse Analiz Paneli", icon="📊"
)

# Navigasyonu çalıştır
pg = st.navigation([ana_sayfa, detay_sayfasi])
pg.run()
