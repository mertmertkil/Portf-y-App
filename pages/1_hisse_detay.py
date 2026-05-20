import streamlit as st
from data.db_manager import get_hisse_hareketleri
from core.ozet_tablosu import get_grafik_verileri
from data.db_manager import get_hisse_temettu_detaylari

st.set_page_config(layout="wide")

# 1. Hisse Seçimi
df_ozet = get_grafik_verileri()
hisse_listesi = df_ozet["hisse_kodu"].unique()

# Hafızada (Session State) hisse var mı kontrol et, yoksa listeden seçtir
varsayilan = st.session_state.get("aktif_hisse", hisse_listesi[0])
secilen_hisse = st.selectbox(
    "İncelenecek Hisse:", hisse_listesi, index=list(hisse_listesi).index(varsayilan)
)

if secilen_hisse:
    st.divider()

    # 2. Üst Özet Kartları (Metrics)
    hisse_ozet = df_ozet[df_ozet["hisse_kodu"] == secilen_hisse].iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Mevcut Adet", f"{hisse_ozet['adet']:,}")
    c2.metric("Maliyet", f"{hisse_ozet['ort_maliyet']:.2f} TL")
    c3.metric("Toplam Yatırılan", f"{hisse_ozet['toplam_maliyet']:,.2f} TL")
    c4.metric("Net Kâr/Zarar", f"{hisse_ozet['kar_zarar']:,.2f} TL")

    # 3. İşlem Geçmişi Tablosu
    st.subheader(f"📜 {secilen_hisse} İşlem Geçmişi")
    hareketler_df = get_hisse_hareketleri(secilen_hisse)

    if not hareketler_df.empty:
        # Tabloyu renklendirelim: Alımlar mavi, Satışlar turuncu gibi
        st.dataframe(
            hareketler_df,
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

if secilen_hisse:
    # 1. Veriyi çek
    df_temettu_gecmisi = get_hisse_temettu_detaylari(secilen_hisse)

    # 2. Görünüm (Expander içine alarak sayfayı sade tutabiliriz)
    with st.expander(f"💰 {secilen_hisse} Temettü Ödeme Detayları", expanded=True):
        if not df_temettu_gecmisi.empty:
            # Tabloyu özelleştirerek sunalım
            st.dataframe(
                df_temettu_gecmisi,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "tarih": st.column_config.DateColumn("Ödeme Tarihi"),
                    "net_miktar": st.column_config.NumberColumn(
                        "Net Nakit (TL)", format="%.2f TL"
                    ),
                },
            )

            # Tablonun hemen altına o hisseye özel küçük bir not
            toplam = df_temettu_gecmisi["net_miktar"].sum()
            st.write(f"**Toplam Tahsil Edilen:** {toplam:,.2f} TL")
        else:
            st.info("Bu hisse için henüz bir temettü ödemesi kaydedilmemiş.")
