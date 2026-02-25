import os
import subprocess

# Sunucuda tarayıcı eksikse yükle
try:
    import playwright
except ImportError:
    subprocess.run(["pip", "install", "playwright"])

# Tarayıcı binary dosyalarını sunucuya kur (Kritik nokta)
os.system("playwright install chromium")

from playwright.sync_api import sync_playwright
# ... geri kalan kodların ...
# scraper.py
from playwright.sync_api import sync_playwright
import pandas as pd

def get_live_data(url):
    with sync_playwright() as p:
        # Tarayıcıyı başlat (headless=True arka planda çalıştırır)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Gerçek bir kullanıcı gibi davranmak için User-Agent ekle
        page.goto(url, wait_until="networkidle")
        
        cars = []
        # Burada ilan satırlarını buluyoruz (Class isimleri site değiştikçe güncellenmelidir)
        items = page.query_selector_all(".listing-list-item") 
        
        for item in items:
            try:
                # Örnek seçiciler (Bunlar projenin temelini oluşturur)
                title = item.query_selector(".model-name").inner_text()
                price = item.query_selector(".price").inner_text()
                # Temizleme işlemleri
                clean_price = int(price.replace("TL", "").replace(".", "").strip())
                
                cars.append({"baslik": title, "fiyat": clean_price})
            except:
                continue
                
        browser.close()
        return pd.DataFrame(cars)

