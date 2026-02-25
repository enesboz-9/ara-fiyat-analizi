import streamlit as st
import pandas as pd
from scraper import get_live_data, parse_html_data

st.title("🚗 Araç Fiyat Analizi")

tab1, tab2 = st.tabs(["🔗 Link ile Analiz", "📋 Kopyala-Yapıştır Analiz"])

with tab1:
    url = st.text_input("İlan listesi linkini buraya yapıştırın:")
    if st.button("Linkten Çek"):
        df = get_live_data(url)
        if not df.empty:
            st.success(f"{len(df)} araç bulundu.")
            st.dataframe(df)
        else:
            st.error("Site engeline takıldı veya veri bulunamadı. Lütfen Kopyala-Yapıştır yöntemini deneyin.")

with tab2:
    st.info("İlan listesi sayfasındayken CTRL+A ile her şeyi seçin, CTRL+C ile kopyalayın ve buraya yapıştırın.")
    html_input = st.text_area("Sayfa İçeriğini Buraya Yapıştırın", height=300)
    
    if st.button("Metni Analiz Et"):
        if html_input:
            df = parse_html_data(html_input)
            if not df.empty:
                st.success(f"{len(df)} araç başarıyla ayıklandı!")
                
                # Basit bir AI Analizi (Ortalama Hesabı)
                avg_price = df['fiyat'].mean()
                df['Durum'] = df['fiyat'].apply(lambda x: "🔥 Ucuz" if x < avg_price * 0.9 else ("🚩 Pahalı" if x > avg_price * 1.1 else "✅ Normal"))
                
                st.dataframe(df)
            else:
                st.warning("Yapıştırılan metinden araç bilgisi çıkarılamadı. Sayfa kaynağını (HTML) yapıştırmayı deneyin.")
