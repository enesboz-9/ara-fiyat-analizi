if not df.empty:
    st.success(f"{len(df)} araç başarıyla ayıklandı!")

    # --- AYNI MODEL ANALİZİ ---
    model_list = df['baslik'].unique()
    secilen_model = st.selectbox("Analiz edilecek spesifik modeli seçin:", model_list)
    
    analiz_df = df[df['baslik'] == secilen_model].copy()
    
    if not analiz_df.empty:
        # Analiz Metrikleri
        avg_price = analiz_df['fiyat'].mean()
        min_price = analiz_df['fiyat'].min()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Ortalama Fiyat", f"{avg_price:,.0f} TL")
        c2.metric("En Düşük", f"{min_price:,.0f} TL")
        c3.metric("Araç Sayısı", len(analiz_df))

        # Hasar Analizi (Basit Anahtar Kelime Tarama)
        def hasar_durumu(text):
            if "hasar kaydı yok" in text or "hatasız" in text: return "Hatasız"
            if "hasar kayıtlı" in text or "tramerli" in text: return "Hasarlı/Tramerli"
            return "Belirtilmemiş"

        analiz_df['Hasar Durumu'] = analiz_df['bilgi'].apply(hasar_durumu)
        
        # Sınıflandırma
        def siniflandir(row):
            if row['fiyat'] < avg_price * 0.9: return "🔥 Fırsat (Ucuz)"
            if row['fiyat'] > avg_price * 1.1: return "🚩 Pahalı"
            return "✅ Normal"

        analiz_df['Analiz'] = analiz_df.apply(siniflandir, axis=1)

        # Görselleştirme (KM ve Fiyat İlişkisi)
        import plotly.express as px
        fig = px.scatter(analiz_df, x="km", y="fiyat", color="Analiz", 
                         size="fiyat", hover_data=['yil', 'Hasar Durumu'],
                         title=f"{secilen_model} KM - Fiyat Dağılımı")
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(analiz_df[['baslik', 'yil', 'km', 'fiyat', 'Hasar Durumu', 'Analiz']])
