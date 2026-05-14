import plotly.express as px


def portfoy_ozet_grafikleri(df):
    if df.empty:
        return None

    # 1. Pasta Grafiği: Yatırılan Para Dağılımı (Sermaye Dağılımı)
    # Burada 'toplam_maliyet' kullanıyoruz çünkü hangi hisseye ne kadar para bağladığınızı gösterir.
    fig_pasta = px.pie(
        df,
        values="toplam_maliyet",
        names="hisse_kodu",
        title="Sermaye Dağılımı (Yatırılan Para)",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig_pasta.update_traces(textinfo="percent+label")

    # 2. Sütun Grafiği: Hisse Bazlı Kâr / Zarar Durumu
    # Veritabanından gelen 'kar_zarar' sütununu kullanarak gerçek durumu görelim.
    # Pozitifler (kâr) yeşil, negatifler (zarar) kırmızı görünecek şekilde renk skalası ekleyebiliriz.
    fig_sutun = px.bar(
        df,
        x="hisse_kodu",
        y="kar_zarar",
        title="Hisse Bazlı Güncel Kâr / Zarar Durumu",
        labels={"kar_zarar": "Kâr / Zarar Tutarı", "hisse_kodu": "Hisse"},
        color="kar_zarar",
        color_continuous_scale=[
            "red",
            "lightgray",
            "green",
        ],  # Zarar: Kırmızı, Kâr: Yeşil
        color_continuous_midpoint=0,
    )

    return fig_pasta, fig_sutun
