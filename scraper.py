import os
import time
import pandas as pd
import subprocess

# Streamlit Cloud'da Playwright kurulumunu garantiye alalım
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    # Eğer kütüphane yüklü değilse yükle ve tarayıcıyı kur
    subprocess.run(["pip", "install", "playwright"])
    os.system("playwright install chromium")
    from playwright.sync_api import sync_playwright

def get_live_data(url):
    # Fonksiyonun içinde sync_playwright'ı tekrar import etmek garantidir
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        try:
            # Tarayıcıyı başlatırken sunucu için gerekli ayarlar
            browser = p.chromium.launch(
                headless=True, 
                args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
            )
            
            # Gerçekçi bir kimlik tanımla (User-Agent)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            page = context.new_page()
            
            # Sayfaya git ve DOM yüklenene kadar bekle
            # Timeout süresini 60 saniye yapalım (60000 ms)
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Sayfanın tam oturması için kısa bir bekleme
            time.sleep(2)
            
            cars = []
            
            # Arabam.com ilan listesi seçicisi (Seçicileri kontrol etmelisin)
            # Not: Eğer site yapısı değiştiyse buradaki class isimlerini güncellemen gerekebilir
            rows = page.query_selector_all(".listing-list-item")
            
            if not rows:
                # Alternatif seçici denemesi
                rows = page.query_selector_all("tr.listing-new-item")

            for row in rows:
                try:
                    # Bu kısımları sitenin güncel HTML yapısına göre düzenle
                    title_elem = row.query_selector(".model-name")
                    price_elem = row.query_selector(".price")
                    
                    if title_elem and price_elem:
                        title = title_elem.inner_text()
                        price_text = price_elem.inner_text()
                        
                        # Fiyatı sayıya çevir: "950.000 TL" -> 950000
                        clean_price = int(price_text.replace("TL", "").replace(".", "").strip())
                        
                        cars.append({
                            "baslik": title,
                            "fiyat": clean_price
                        })
                except:
                    continue
            
            browser.close()
            return pd.DataFrame(cars)
            
        except Exception as e:
            print(f"Scraper Hatası: {e}")
            if 'browser' in locals():
                browser.close()
            return pd.DataFrame()
