import plotly.express as px


def portfoy_ozet_grafikleri(df):
    if df.empty:
        return None

    fig_pasta = px.pie(
        df,
        values="toplam_maliyet",
        names="hisse_kodu",
        title="Sermaye Dağılımı (Yatırılan Para)",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig_pasta.update_traces(textinfo="percent+label")

    return fig_pasta
