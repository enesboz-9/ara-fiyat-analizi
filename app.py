import streamlit as st
import pandas as pd
import plotly.express as px
from scraper import parse_html_data

st.set_page_config(page_title="Araç Değerleme Robotu", layout="wide")

st.title("🚗 Akıllı Araç Değerleme ve Sınıflandırma")
st.info("İlanları yapıştırın; sistem model yılına göre adil piyasa değerini hesaplasın.")

if 'data' not in st.session_state:
    st.session_state.data = None

# Yan Menü: Veri Girişi
with st.sidebar:
    st.header("Veri Giriş Merkezi")
    html_input = st.text_area("İlan Listesini Kopyalayıp Buraya Yapıştırın:", height=300)
    if st.button("Piyasayı Analiz Et"):
        if html_input:
            df = parse_html_data(html_input)
            if not df.empty:
                st.session_state.data = df
                st.success("Veriler Başarıyla İşlendi!")

# Ana Ekran: Analiz
if st.session_state.data is not None:
    df = st.session_state.data

    # 1. Filtreleme: Model Seçimi
    model_list = sorted(df['baslik'].unique())
    secilen_model = st.selectbox("Analiz Edilecek Tam Modeli Seçin:", model_list)
    
    # 2. Yıl Seçimi (Veri setindeki yılları otomatik alıyoruz)
    model_df = df[df['baslik'] == secilen_model].copy()
    yil_list = sorted(model_df['yil'].unique(), reverse=True)
    secilen_yil = st.selectbox("Model Yılını Seçin:", yil_list)
    
    # Final Filtreleme: Örn. Corolla + 2019
    final_df = model_df[model_df['yil'] == secilen_yil].copy()

    if len(final_df) > 0:
        # --- ZEKA MANTIĞI (Senin Tablo Mantığın) ---
        ort_fiyat = final_df['fiyat'].mean()
        min_fiyat = final_df['fiyat'].min()
        max_fiyat = final_df['fiyat'].max()
        fark = max_fiyat - min_fiyat

        def siniflandir(fiyat):
            if fark == 0: return "✅ ORTALAMA"
            # Senin metodolojin: Alt %25 ucuz, Üst %25 pahalı
            if fiyat <= min_fiyat + (fark * 0.25):
                return "🟢 UCUZ (Fırsat Ürünü)"
            elif fiyat >= max_fiyat - (fark * 0.25):
                return "🔴 PAHALI (Piyasa Üstü)"
            else:
                return "🟡 ORTALAMA (Piyasa Değeri)"

        final_df['Durum'] = final_df['fiyat'].apply(siniflandir)

        # Metrikler
        c1, c2, c3 = st.columns(3)
        c1.metric(f"{secilen_yil} {secilen_model} Ortalaması", f"{ort_fiyat:,.0f} TL")
        c2.metric("Tespit Edilen En Ucuz", f"{min_fiyat:,.0f} TL")
        c3.metric("İlan Sayısı", len(final_df))

        # Görselleştirme
        
        
        st.subheader(f"📊 {secilen_yil} {secilen_model} Fiyat Dağılım Analizi")
        fig = px.bar(final_df.sort_values("fiyat"), x=final_df.index, y="fiyat", color="Durum",
                     color_discrete_map={
                         "🟢 UCUZ (Fırsat Ürünü)": "#2ecc71",
                         "🟡 ORTALAMA (Piyasa Değeri)": "#f1c40f",
                         "🔴 PAHALI (Piyasa Üstü)": "#e74c3c"
                     },
                     labels={'fiyat':'Fiyat (TL)', 'index':'İlan No'},
                     hover_data=['km'])
        st.plotly_chart(fig, use_container_width=True)

        # Liste Gösterimi
        st.subheader("📋 Sınıflandırılmış Araç Listesi")
        st.dataframe(final_df[['yil', 'km', 'fiyat', 'Durum']].sort_values("fiyat"), use_container_width=True)
    else:
        st.warning("Bu yıl için yeterli veri bulunamadı.")
else:
    st.info("Analize başlamak için sol taraftaki alana ilanları yapıştırın.")
