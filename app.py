# app.py
import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd

st.title("🚗 Akıllı Araç Analizörü")

tab1, tab2 = st.tabs(["Link ile Analiz (Beta)", "Hızlı Analiz (Kopyala-Yapıştır)"])

with tab2:
    st.info("Sitenin bot engeline takılmamak için: İlan listesindeyken 'Sağ Tık -> Sayfa Kaynağını Görüntüle' yapın, hepsini seçip buraya yapıştırın.")
    html_data = st.text_area("Sayfa Kaynağını (HTML) Buraya Yapıştırın", height=300)
    
    if st.button("Hemen Analiz Et"):
        soup = BeautifulSoup(html_data, 'html.parser')
        # BeautifulSoup ile verileri ayıkla (Hız limiti yok, ban riski yok!)
        # Örnek:
        names = [item.get_text() for item in soup.select(".model-name")]
        prices = [item.get_text() for item in soup.select(".price")]
        
        df = pd.DataFrame({"baslik": names, "fiyat": prices})
        st.write(df)
