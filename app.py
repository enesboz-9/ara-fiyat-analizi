import streamlit as st
import pandas as pd
import plotly.express as px
from scraper import parse_html_data

st.set_page_config(page_title="Araç Analiz AI", layout="wide")
st.title("🚗 Akıllı Araç Analiz ve Fiyatlandırma")

html_input = st.text_area("Sayfa Kaynağını veya Kopyalanan Metni Buraya Yapıştırın", height=250)

if st.button("Analizi Başlat"):
    if html_input:
        df = parse_html_data(html_input)
        
        if not df.empty:
            st.success(f"{len(df)} araç bulundu.")

            # 1. Model Filtreleme (Sadece seçilen modeli analiz et)
            model_list = sorted(df['baslik'].unique())
            secilen_model = st.selectbox("Analiz etmek istediğiniz tam modeli seçin:", model_list)
            
            analiz_df = df[df['baslik'] == secilen_model].copy()

            # 2. Hasar Analizi (Metin Madenciliği)
            def hasar_tespit(text):
                if any(x in text for x in ["hatasız", "boyasız", "değişensiz", "hasar kaydı yok"]):
                    return "Hatasız"
                if any(x in text for x in ["hasar kayıtlı", "tramer", "boyalı", "değişen"]):
                    return "Hasarlı/Boyalı"
                return "Belirtilmemiş"

            analiz_df['Hasar Durumu'] = analiz_df['ham_metin'].apply(hasar_tespit)

            # 3. İstatistiksel Analiz (AI Sınıflandırma)
            avg_price = analiz_df['fiyat'].mean()
            
            def siniflandir(row):
                if row['fiyat'] < avg_price * 0.92: return "🔥 Fırsat (Ucuz)"
                if row['fiyat'] > avg_price * 1.08: return "🚩 Pahalı"
                return "✅ Normal"

            analiz_df['Piyasa Durumu'] = analiz_df.apply(siniflandir, axis=1)

            # 4. Metrikler
            c1, c2, c3 = st.columns(3)
            c1.metric("Ortalama Fiyat", f"{avg_price:,.0f} TL")
            c2.metric("Örnek Sayısı", len(analiz_df))
            c3.metric("Piyasa Altı İlanlar", len(analiz_df[analiz_df['Piyasa Durumu'] == "🔥 Fırsat (Ucuz)"]))

            # 5. Görselleştirme (KM vs Fiyat)
            fig = px.scatter(analiz_df, x="km", y="fiyat", 
                             color="Piyasa Durumu", size="yil",
                             hover_data=['yil', 'Hasar Durumu'],
                             title=f"{secilen_model} - KM/Fiyat Analizi")
            st.plotly_chart(fig, use_container_width=True)

            # 6. Sonuç Tablosu
            st.dataframe(analiz_df[['baslik', 'yil', 'km', 'fiyat', 'Hasar Durumu', 'Piyasa Durumu']])
        else:
            st.warning("Veri ayıklanamadı. Lütfen içeriği doğru kopyaladığınızdan emin olun.")
