import streamlit as st
import pandas as pd
import plotly.express as px
from scraper import parse_html_data

st.set_page_config(page_title="Araç Analiz AI", layout="wide")
st.title("🚗 Akıllı Araç Analiz ve Fiyatlandırma")

# 1. HAFIZA YÖNETİMİ: Veriyi oturum boyunca saklamak için kontrol ediyoruz
if 'car_data' not in st.session_state:
    st.session_state.car_data = None

# Giriş Alanı
html_input = st.text_area("Sayfa Kaynağını Buraya Yapıştırın", height=200)

if st.button("Verileri İşle"):
    if html_input:
        df = parse_html_data(html_input)
        if not df.empty:
            # Çekilen veriyi hafızaya (Session State) kaydediyoruz
            st.session_state.car_data = df
            st.success(f"{len(df)} araç hafızaya alındı. Şimdi aşağıdan filtreleme yapabilirsiniz.")
        else:
            st.error("Veri ayıklanamadı.")

# 2. ANALİZ KISMI: Eğer hafızada veri varsa burası görünür olur
if st.session_state.car_data is not None:
    df = st.session_state.car_data
    
    st.divider()
    
    # Model Filtreleme
    model_list = sorted(df['baslik'].unique())
    secilen_model = st.selectbox("Analiz edilecek modeli seçin:", model_list)
    
    # Seçilen modele göre filtrele
    analiz_df = df[df['baslik'] == secilen_model].copy()

    # Hasar Analizi Fonksiyonu
    def hasar_tespit(text):
        if any(x in text for x in ["hatasız", "boyasız", "değişensiz", "hasar kaydı yok"]):
            return "Hatasız"
        if any(x in text for x in ["hasar kayıtlı", "tramer", "boyalı", "değişen"]):
            return "Hasarlı/Boyalı"
        return "Belirtilmemiş"

    analiz_df['Hasar Durumu'] = analiz_df['ham_metin'].apply(hasar_tespit)

    # İstatistiksel Analiz (Fiyat Sınıflandırma)
    avg_price = analiz_df['fiyat'].mean()
    
    def siniflandir(row):
        if row['fiyat'] < avg_price * 0.92: return "🔥 Fırsat (Ucuz)"
        if row['fiyat'] > avg_price * 1.08: return "🚩 Pahalı"
        return "✅ Normal"

    analiz_df['Piyasa Durumu'] = analiz_df.apply(siniflandir, axis=1)

    # Metrikler ve Görselleştirme
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.metric("Model Ortalaması", f"{avg_price:,.0f} TL")
        st.metric("Örnek Sayısı", len(analiz_df))
        st.dataframe(analiz_df[['yil', 'km', 'fiyat', 'Piyasa Durumu']].sort_values(by="fiyat"))

    with c2:
        fig = px.scatter(analiz_df, x="km", y="fiyat", 
                         color="Piyasa Durumu", size="yil",
                         hover_data=['yil', 'Hasar Durumu'],
                         title=f"{secilen_model} - KM/Fiyat Grafiği")
        st.plotly_chart(fig, use_container_width=True)
