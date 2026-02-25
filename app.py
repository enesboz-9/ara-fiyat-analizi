# app.py
import streamlit as st
from scraper import get_live_data # scraper.py dosyasındaki fonksiyonu çağırıyoruz

st.set_page_config(page_title="Canlı Araç Analiz", layout="wide")

st.title("🚗 Anlık Araç Fiyat Analizi")

# Kullanıcıdan URL al
url = st.text_input("Analiz edilecek ilan listesi linkini girin:")

if st.button("Piyasayı Güncelle ve Analiz Et"):
    if url:
        with st.spinner("Veriler canlı olarak çekiliyor..."):
            # scraper.py'deki fonksiyonu burada kullanıyoruz
            df = get_live_data(url)
            
            if not df.empty:
                st.write("### Güncel Veriler", df)
                # Buraya analiz ve grafik kodlarını ekleyebilirsin
            else:
                st.warning("Veri bulunamadı. Lütfen linki kontrol edin.")
    else:
        st.error("Lütfen geçerli bir URL girin.")
