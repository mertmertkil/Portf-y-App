import streamlit as st
import pandas as pd
from data.get_grafik_verileri import get_grafik_verileri
from core.fon_ozet import get_fon_verileri

# --- SAYFA AYARLARI VE BAŞLIK ---
st.set_page_config(page_title="Sonlanan İşlemler", page_icon="🏁", layout="wide")

col_back, col_title = st.columns([1, 5])
with col_back:
    if st.button("⬅️ Ana Sayfa"):
        st.switch_page("pages/0_anasayfa.py")

with col_title:
    st.title("🏁 Sonlanan ve Realize Olan İşlemler")
    st.write(
        "Portföyünüzde alım-satımı tamamlanmış, adedi sıfırlanmış ve kâr/zararı kesinleşmiş varlıklar."
    )

st.divider()


# --- STİL FONKSİYONU (Kâr/Zarar Renklendirmesi) ---
def style_realize_kar_zarar(v):
    if v > 0:
        return "color: #2ecc71; font-weight: bold;"  # Yeşil
    elif v < 0:
        return "color: #e74c3c; font-weight: bold;"  # Kırmızı
    return "color: white;"


# --- SEKME (TAB) DÜZENİ ---
tab_hisse, tab_fon = st.tabs(["📈 Sonlanan Hisseler", "📦 Sonlanan Fonlar"])

# =====================================================================
# 1. SEKME: SONLANAN HİSSELER
# =====================================================================
with tab_hisse:
    try:
        df_hisse = get_grafik_verileri()

        if not df_hisse.empty and "adet" in df_hisse.columns:
            # Adedi 0 olan, yani tamamen satılarak kapatılmış hisseleri filtreliyoruz
            df_sonlanan_hisse = df_hisse[df_hisse["adet"] == 0].copy()

            if not df_sonlanan_hisse.empty:
                # --- YENİ SÜTUNLAR eklendi: ort_alis_fiyati, ort_satis_fiyati ---
                view_columns = [
                    "hisse_kodu",
                    "ort_alis_fiyati",  # Veritabanından gelen ortalama alış fiyatı
                    "ort_satis_fiyati",  # Veritabanından gelen ortalama satış fiyatı
                    "toplam_maliyet",
                    "kar_zarar",
                ]
                if "kar_zarar_oran" in df_sonlanan_hisse.columns:
                    view_columns.append("kar_zarar_oran")

                # Sütunların DataFrame'de mevcut olup olmadığını güvenle kontrol edelim
                view_columns = [
                    col for col in view_columns if col in df_sonlanan_hisse.columns
                ]

                hisse_gosterim = df_sonlanan_hisse[view_columns].reset_index(drop=True)

                # Toplam istatistikler
                toplam_realize_hisse_kz = hisse_gosterim["kar_zarar"].sum()

                # Başarı Metriği
                st.metric(
                    label="Hisselerden Realize Edilen Toplam Kâr / Zarar",
                    value=f"{toplam_realize_hisse_kz:,.2f} TL",
                    delta="Kesinleşen Nakit Akışı",
                    delta_color="normal" if toplam_realize_hisse_kz >= 0 else "inverse",
                )

                # Tablo Stili ve Gösterimi
                styled_hisse = hisse_gosterim.style.map(
                    style_realize_kar_zarar,
                    subset=["kar_zarar"]
                    + (
                        ["kar_zarar_oran"]
                        if "kar_zarar_oran" in hisse_gosterim.columns
                        else []
                    ),
                ).format(
                    {
                        "ort_alis_fiyati": "{:,.2f} TL",  # Formatlama eklendi
                        "ort_satis_fiyati": "{:,.2f} TL",  # Formatlama eklendi
                        "toplam_maliyet": "{:,.2f} TL",
                        "kar_zarar": "{:,.2f} TL",
                        "kar_zarar_oran": (
                            "%{:,.2f}"
                            if "kar_zarar_oran" in hisse_gosterim.columns
                            else "{}"
                        ),
                    }
                )

                st.dataframe(
                    styled_hisse,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "hisse_kodu": "Hisse Kodu",
                        "ort_alis_fiyati": "Ort. Alış Fiyatı",  # Tablo başlığı
                        "ort_satis_fiyati": "Ort. Satış Fiyatı",  # Tablo başlığı
                        "toplam_maliyet": "Toplam Çevrilen Hacim",
                        "kar_zarar": "Realize K/Z",
                        "kar_zarar_oran": "Net Başarı (%)",
                    },
                )
            else:
                st.info(
                    "Kapatılmış/sonlanmış herhangi bir hisse pozisyonunuz bulunmuyor."
                )
        else:
            st.info("Hisse özet verisi boş veya adet sütunu bulunamadı.")
    except Exception as e:
        st.error(f"Hisse verileri yüklenirken bir hata oluştu: {e}")

# =====================================================================
# 2. SEKME: SONLANAN FONLAR
# =====================================================================
with tab_fon:
    try:
        # Belirttiğin fon_ozet verilerini üreten fonksiyonu çağırıyoruz
        df_fon = get_fon_verileri()

        if not df_fon.empty:
            if "adet" in df_fon.columns:
                df_sonlanan_fon = df_fon[df_fon["adet"] == 0].copy()
            else:
                # Eğer fon_ozet sadece sonlananları veya tümünü içeriyorsa doğrudan df_fon üzerinden de yürünebilir
                df_sonlanan_fon = df_fon.copy()

            if not df_sonlanan_fon.empty:
                # Sadece fon_kodu ve kar_zarar sütunlarından oluştuğunu belirttiğin için ona göre güvenli seçim yapıyoruz
                mevcut_sutunlar = df_sonlanan_fon.columns
                secilecek_sutunlar = [
                    col
                    for col in ["fon_kodu", "kar_zarar", "kar_zarar_oran"]
                    if col in mevcut_sutunlar
                ]

                fon_gosterim = df_sonlanan_fon[secilecek_sutunlar].reset_index(
                    drop=True
                )

                # Toplam istatistikler
                toplam_realize_fon_kz = fon_gosterim["kar_zarar"].sum()

                st.metric(
                    label="Fonlardan Realize Edilen Toplam Kâr / Zarar",
                    value=f"{toplam_realize_fon_kz:,.2f} TL",
                    delta="Kesinleşen Nakit Akışı",
                    delta_color="normal" if toplam_realize_fon_kz >= 0 else "inverse",
                )

                # Tablo Stili
                styled_fon = fon_gosterim.style.map(
                    style_realize_kar_zarar,
                    subset=["kar_zarar"]
                    + (
                        ["kar_zarar_oran"]
                        if "kar_zarar_oran" in fon_gosterim.columns
                        else []
                    ),
                ).format(
                    {
                        "kar_zarar": "{:,.2f} TL",
                        "kar_zarar_oran": (
                            "%{:,.2f}"
                            if "kar_zarar_oran" in fon_gosterim.columns
                            else "{}"
                        ),
                    }
                )

                st.dataframe(
                    styled_fon,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "fon_kodu": "Fon Kodu",
                        "kar_zarar": "Realize K/Z",
                        "kar_zarar_oran": "Net Başarı (%)",
                    },
                )
            else:
                st.info(
                    "Kapatılmış/sonlanmış herhangi bir fon pozisyonunuz bulunmuyor."
                )
        else:
            st.info("Fon özet verisi bulunamadı.")
    except Exception as e:
        st.error(f"Fon verileri yüklenirken bir hata oluştu: {e}")
