import streamlit as st
import pandas as pd
import plotly.express as px
from scraper import parse_html_data

st.set_page_config(page_title="Araç Piyasa Analiz AI", layout="wide")

# Başlık ve Açıklama
st.title("🚗 Araç Piyasa Değerleme ve Analiz Sistemi")
st.markdown("""
Bu sistem, yapıştırdığınız verileri analiz ederek **piyasa ortalamasını** hesaplar ve 
araçları fiyatlarına göre sınıflandırır.
""")

# Hafıza Yönetimi (Session State)
if 'raw_df' not in st.session_state:
    st.session_state.raw_df = None

# Veri Giriş Alanı
with st.expander("📥 Veri Girişi (HTML veya Metin Yapıştırın)", expanded=True):
    html_input = st.text_area("İlan listesini buraya yapıştırın:", height=150)
    if st.button("Verileri Analiz Et"):
        if html_input:
            df = parse_html_data(html_input)
            if not df.empty:
                st.session_state.raw_df = df
                st.success(f"Analiz Başarılı: {len(df)} araç yüklendi.")
            else:
                st.error("Veri ayıklanamadı. Lütfen kopyaladığınız içeriği kontrol edin.")

# Analiz ve Görselleştirme Kısmı
if st.session_state.raw_df is not None:
    df = st.session_state.raw_df
    
    st.divider()
    
    # 1. Filtreleme: Aynı modeldeki araçları bir grupta toplayalım
    model_list = sorted(df['baslik'].unique())
    secilen_model = st.selectbox("Analiz edilecek modeli seçin:", model_list)
    
    # Sadece seçilen modele odaklan
    analiz_df = df[df['baslik'] == secilen_model].copy()

    if len(analiz_df) > 0:
        # --- ZEKA KISMI: FİYAT SINIFLANDIRMA ---
        ortalama_fiyat = analiz_df['fiyat'].mean()
        
        def fiyat_etiketi_koy(fiyat):
            # Ortalamanın %8 altı ucuz, %8 üstü pahalı kabul edilsin
            if fiyat < ortalama_fiyat * 0.92:
                return "🔥 UCUZ (Fırsat)"
            elif fiyat > ortalama_fiyat * 1.08:
                return "🚩 PAHALI"
            else:
                return "✅ NORMAL (Piyasa Değeri)"

        analiz_df['Piyasa Analizi'] = analiz_df['fiyat'].apply(fiyat_etiketi_koy)

        # Üst Metrikler
        m1, m2, m3 = st.columns(3)
        m1.metric("Piyasa Ortalaması", f"{ortalama_fiyat:,.0f} TL")
        m2.metric("En Uygun Fiyat", f"{analiz_df['fiyat'].min():,.0f} TL")
        m3.metric("Analiz Edilen Araç", len(analiz_df))

        # Görsel Analiz (Grafik)
        st.subheader(f"📊 {secilen_model} İçin Fiyat Dağılımı")
        fig = px.scatter(
            analiz_df, 
            x="km", 
            y="fiyat", 
            color="Piyasa Analizi",
            symbol="Piyasa Analizi",
            size="fiyat",
            hover_data=['yil'],
            color_discrete_map={
                "🔥 UCUZ (Fırsat)": "#2ecc71", 
                "✅ NORMAL (Piyasa Değeri)": "#3498db", 
                "🚩 PAHALI": "#e74c3c"
            }
        )
        st.plotly_chart(fig, use_container_width=True)

        # Liste Halinde Gösterim
        st.subheader("📋 Detaylı Araç Listesi")
        # Fiyata göre sırala (En ucuz en üstte)
        st.dataframe(
            analiz_df[['yil', 'km', 'fiyat', 'Piyasa Analizi']].sort_values(by="fiyat"),
            use_container_width=True
        )
    else:
        st.info("Bu model için yeterli veri bulunamadı.")
