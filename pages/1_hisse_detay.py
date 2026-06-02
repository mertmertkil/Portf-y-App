import streamlit as st
import pandas as pd
from data.db_manager import get_hisse_hareketleri
from core.ozet_tablosu import get_grafik_verileri
from data.db_manager import get_hisse_temettu_detaylari


# --- YARDIMCI TASARIM FONKSİYONU (Zebra Şerit Yapısı) ---
def tabloyu_seritli_yap(df):
    """Tablo satırlarını bir açık bir koyu (zebra) yapmak için doğru stili uygular."""
    if df.empty:
        return df

    def serit_boya(row):
        # Satırın indeksi (numarası) çift ise tüm satırı hafif griye boya
        if row.name % 2 == 0:
            return ["background-color: rgba(128, 128, 128, 0.05)"] * len(row)
        # Tek ise boş bırak (varsayılan renk kalsın)
        return [""] * len(row)

    # apply() kullanarak satır satır (axis=1) işlem yapıyoruz
    return df.style.apply(serit_boya, axis=1)


# --- ÜST NAVİGASYON VE BAŞLIK ---
col_back, col_title = st.columns([1, 5])

with col_back:
    # Ana sayfaya dönme butonu
    if st.button("⬅️ Ana Sayfa"):
        st.switch_page("pages/0_anasayfa.py")

with col_title:
    st.title("Hisse Detay Analizi")

st.divider()

# 1. Hisse Seçimi ve Session State Kontrolü
df_ozet = get_grafik_verileri()
hisse_listesi = df_ozet["hisse_kodu"].unique()

# Hafızada (Session State) hisse var mı kontrol et
varsayilan_hisse = st.session_state.get("aktif_hisse", hisse_listesi[0])

# Eğer session_state'deki hisse listede yoksa ilkini seç
if varsayilan_hisse not in hisse_listesi:
    varsayilan_index = 0
else:
    varsayilan_index = list(hisse_listesi).index(varsayilan_hisse)

secilen_hisse = st.selectbox(
    "İncelenecek Hisse:", hisse_listesi, index=varsayilan_index
)

# Seçilen hisseyi hafızada güncelle
st.session_state["aktif_hisse"] = secilen_hisse

if secilen_hisse:
    # 2. Üst Özet Kartları (Metrics)
    hisse_ozet = df_ozet[df_ozet["hisse_kodu"] == secilen_hisse].iloc[0]

    # Kâr/Zarar durumuna göre rengi dinamik belirliyoruz
    kz_degeri = hisse_ozet["kar_zarar"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Mevcut Adet", f"{hisse_ozet['adet']:.2f}")
    c2.metric("Maliyet", f"{hisse_ozet['ort_maliyet']:.2f} TL")
    c3.metric("Toplam Yatırılan", f"{hisse_ozet['toplam_maliyet']:,.2f} TL")

    # Net Kâr/Zarar kartına renk yönü (delta_color) verdik
    c4.metric(
        "Net Kâr/Zarar",
        f"{kz_degeri:,.2f} TL",
        delta=(
            f"{(kz_degeri / hisse_ozet['toplam_maliyet'] * 100):.2f}%"
            if hisse_ozet["toplam_maliyet"] > 0
            else "0%"
        ),
        delta_color="normal",
    )

    st.divider()

    # 3. İşlem Geçmişi Tablosu
    st.subheader(f"📜 {secilen_hisse} İşlem Geçmişi")
    hareketler_df = get_hisse_hareketleri(secilen_hisse)

    if not hareketler_df.empty:
        # Satır indekslerini sıfırlıyoruz ki çift/tek kontrolü (row.name) hatasız çalışsın
        hareketler_df = hareketler_df.reset_index(drop=True)

        st.dataframe(
            tabloyu_seritli_yap(hareketler_df),  # Stil fonksiyonunu burada giydirdik
            use_container_width=True,
            hide_index=True,
            column_config={
                "islem_tipi": st.column_config.TextColumn("İşlem"),
                "tarih": st.column_config.DateColumn("Tarih"),
                "fiyat": st.column_config.NumberColumn("Birim Fiyat", format="%.2f TL"),
                "toplam_tutar": st.column_config.NumberColumn(
                    "Toplam", format="%.2f TL"
                ),
            },
        )
    else:
        st.info("Bu hisseye ait işlem geçmişi bulunamadı.")

    # 4. Temettü Bilgileri
    df_temettu_gecmisi = get_hisse_temettu_detaylari(secilen_hisse)

    with st.expander(f"💰 {secilen_hisse} Temettü Ödeme Detayları", expanded=True):
        if not df_temettu_gecmisi.empty:
            # Satır indekslerini sıfırlıyoruz
            df_temettu_gecmisi = df_temettu_gecmisi.reset_index(drop=True)

            st.dataframe(
                tabloyu_seritli_yap(
                    df_temettu_gecmisi
                ),  # Stil fonksiyonunu burada giydirdik
                use_container_width=True,
                hide_index=True,
                column_config={
                    "tarih": st.column_config.DateColumn("Ödeme Tarihi"),
                    "birim_net": st.column_config.NumberColumn(
                        "Birim Net", format="%.4f TL"
                    ),
                    "o_tarihteki_adet": st.column_config.NumberColumn("Hisse Adedi"),
                    "toplam_net_kazanc": st.column_config.NumberColumn(
                        "Yatan Toplam", format="%.2f TL"
                    ),
                },
            )
            total_tahsil = df_temettu_gecmisi["toplam_net_kazanc"].sum()
            st.markdown(
                f"**Toplam Tahsil Edilen Net Temettü:** `{total_tahsil:,.2f} TL`"
            )
        else:
            st.info("Bu hisse için henüz bir temettü ödemesi kaydedilmemiş.")
