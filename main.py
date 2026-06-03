import streamlit as st
import pandas as pd
from core.ozet_tablosu import portfoy_guncelle
from data.get_grafik_verileri import get_grafik_verileri
from ui.charts import portfoy_ozet_grafikleri
from data.db_json import veritabanini_json_yedekle

# 1. TÜM UYGULAMANIN AYARINI BURADA YAP (Hata almamak için en üstte olmalı)
st.set_page_config(page_title="Mert Portföy", layout="wide")

# Sayfaları tanımla
ana_sayfa = st.Page("pages/0_anasayfa.py", title="Genel Özet", icon="🏠")
detay_sayfasi = st.Page(
    "pages/1_hisse_detay.py", title="Hisse Analiz Paneli", icon="📊"
)
# YENİ SAYFA: İşlem ekleme sayfasını sisteme dahil ediyoruz
islem_ekle_sayfasi = st.Page(
    "pages/2_islem_ekle.py", title="Yeni İşlem Ekle", icon="➕"
)

temettu_ekle_sayfasi = st.Page(
    "pages/3_temettu_ekle.py", title="Temettü Ödemesi Ekle", icon="💰"
)

sonlanan_islemler_sayfasi = st.Page(
    "pages/4_sonlanan_islemler.py", title="Sonlanan İşlemler", icon="🔚"
)

# Navigasyonu çalıştır (Yeni sayfayı listeye ekledik)
pg = st.navigation(
    [
        ana_sayfa,
        detay_sayfasi,
        islem_ekle_sayfasi,
        temettu_ekle_sayfasi,
        sonlanan_islemler_sayfasi,
    ]
)
pg.run()
