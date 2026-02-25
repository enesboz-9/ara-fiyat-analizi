import streamlit as st
import pandas as pd
import plotly.express as px
from scraper import parse_html_data

# Sayfa Genişlik Ayarı
st.set_page_config(page_title="Araç Piyasa Analiz AI", layout="wide")

# Başlık
st.title("🚗 Akıllı Araç Değerleme Sistemi")
st.markdown("Verileri yapıştırın, sistem **Piyasa Ortalamasını** ve **Fırsat Araçları** anında hesaplasın.")

# 1. HAFIZA YÖNETİMİ (Session State)
# Bu kısım, seçim kutusunu değiştirdiğinizde verilerin silinmesini engeller.
if 'car_df' not in st.session_state:
    st.session_state.car_df = None

# 2. VERİ GİRİŞ ALANI
with st.sidebar:
    st.header("Veri Girişi")
    html_input = st.text_area("İlan Listesi Kaynağını Buraya Yapıştırın:", height=300)
    if st.button("Verileri İşle ve Analiz Et"):
        if html_input:
            df = parse_html_data(html_input)
            if not df.empty:
                st.session_state.car_df = df
                st.success(f"{len(df)} araç yüklendi!")
            else:
                st.error("Veri ayıklanamadı. Kaynağı kontrol edin.")

# 3. ANALİZ VE GÖRSELLEŞTİRME
if st.session_state.car_df is not None:
    all_data = st.session_state.car_df
    
    # Model Seçimi (Aynı modeldeki araçları gruplar)
    model_list = sorted(all_data['baslik'].unique())
    secilen_model = st.selectbox("Analiz Edilecek Modeli Seçin:", model_list)
    
    # Filtrelenmiş veri seti
    df = all_data[all_data['baslik'] == secilen_model].copy()

    if len(df) > 0:
        # --- MATEMATİKSEL ANALİZ (UCUZ/PAHALI AYRIMI) ---
        min_fiyat = df['fiyat'].min()
        max_fiyat = df['fiyat'].max()
        ortalama_fiyat = df['fiyat'].mean()
        fiyat_araligi = max_fiyat - min_fiyat

        def piyasa_etiketi(fiyat):
            # Eğer tek bir fiyat varsa kıyaslama yapma
            if fiyat_araligi == 0: return "✅ NORMAL"
            
            # Yüzdelik dilimlere göre matematiksel ayırma (En ucuz %25 - En pahalı %25)
            if fiyat <= min_fiyat + (fiyat_araligi * 0.25):
                return "🔥 UCUZ (Fırsat)"
            elif fiyat >= max_fiyat - (fiyat_araligi * 0.25):
                return "🚩 PAHALI"
            else:
                return "✅ NORMAL"

        df['Analiz'] = df['fiyat'].apply(piyasa_etiketi)

        # Üst Metrikler
        c1, c2, c3 = st.columns(3)
        c1.metric("Piyasa Ortalaması", f"{ortalama_fiyat:,.0f} TL")
        c2.metric("En Uygun İlan", f"{min_fiyat:,.0f} TL")
        c3.metric("Örnek Sayısı", len(df))

        # Görselleştirme (KM vs Fiyat)
        st.subheader(f"📊 {secilen_model} - Fiyat/KM Dağılım Grafiği")
        
        
        
        fig = px.scatter(
            df, x="km", y="fiyat", 
            color="Analiz",
            size="fiyat",
            hover_data=['yil'],
            color_discrete_map={
                "🔥 UCUZ (Fırsat)": "#00CC96", # Yeşil
                "✅ NORMAL": "#636EFA",        # Mavi
                "🚩 PAHALI": "#EF553B"         # Kırmızı
            },
            title=f"{secilen_model} Piyasa Dağılımı"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Sonuç Tablosu
        st.subheader("📋 Analiz Edilen Araçların Listesi")
        # Fiyata göre sıralı göster
        st.dataframe(
            df[['yil', 'km', 'fiyat', 'Analiz']].sort_values(by="fiyat"),
            use_container_width=True
        )
    else:
        st.warning("Seçilen model için veri bulunamadı.")
else:
    st.info("Lütfen sol taraftaki alana verileri yapıştırıp 'İşle' butonuna basın.")
