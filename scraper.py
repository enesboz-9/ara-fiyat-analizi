def get_live_data(url):
    with sync_playwright() as p:
        # headless=True olmalı (Sunucuda ekran yok)
        # Sitenin bot olduğunu anlamaması için bazı argümanlar ekliyoruz
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-gpu"])
        
        # Gerçekçi bir ekran çözünürlüğü ve User-Agent ayarla
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = context.new_page()
        
        try:
            # networkidle yerine domcontentloaded kullanıyoruz (daha hızlı ve az takılır)
            # timeout süresini 60 saniyeye çıkardık
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Sayfanın yüklenmesi için 3 saniye manuel bekle
            time.sleep(3) 
            
            # Veri çekme kodların buraya gelecek...
            # Örn: items = page.query_selector_all(".listing-item")
            
        except Exception as e:
            print(f"Hata oluştu: {e}")
            return pd.DataFrame() # Hata durumunda boş dön
        finally:
            browser.close()
