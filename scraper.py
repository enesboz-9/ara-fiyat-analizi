import os
import time
import pandas as pd
import subprocess
from bs4 import BeautifulSoup

# Playwright kurulum kontrolü
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    subprocess.run(["pip", "install", "playwright"])
    os.system("playwright install chromium")
    from playwright.sync_api import sync_playwright

def get_live_data(url):
    """Link üzerinden canlı veri çekmeye çalışır."""
    with sync_playwright() as p:
        try:
            # Tarayıcıyı gizli modda ve güvenlik önlemleriyle başlat
            browser = p.chromium.launch(
                headless=True, 
                args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
            )
            
            # Gerçek bir kullanıcı gibi davran (User-Agent ve Dil ayarları)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                extra_http_headers={"Accept-Language": "tr-TR,tr;q=0.9"}
            )
            
            page = context.new_page()
            
            # Sayfaya git ve içeriğin oturması için bekle
            # timeout 60 saniye, domcontentloaded daha hızlı sonuç verir
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Sayfa yüklendikten sonra 5 saniye bekle (Bot korumasını aşmak için)
            time.sleep(5)
            
            # Sayfa kaynağını al ve BeautifulSoup'a gönder
            html_content = page.content()
            browser.close()
            
            return parse_html_data(html_content)
            
        except Exception as e:
            print(f"Bağlantı Hatası: {e}")
            return pd.DataFrame()

def parse_html_data(html_content):
    """HTML içeriğini parçalara ayırır ve temiz veri setine dönüştürür."""
    soup = BeautifulSoup(html_content, 'html.parser')
    cars = []

    # Arabam.com güncel seçicileri (2024-2025 yapısı)
    # Liste öğelerini bul (Hem tablo hem kart görünümü için farklı seçiciler)
    items = soup.select("tr.listing-new-item, .unf-listing-card")

    for item in items:
        try:
            # Başlık/Model seçimi
            title = item.select_one(".model-name, .listing-model-name")
            # Fiyat seçimi
            price = item.select_one(".price, .listing-price")
            # KM seçimi
            km = item.select_one(".year, .listing-km")
            # Yıl seçimi
            year = item.select_one(".year, .listing-year")

            if title and price:
                # Veriyi temizleme
                clean_price = int(price.get_text().replace("TL", "").replace(".", "").strip())
                clean_km = km.get_text().replace(".", "").replace("km", "").strip() if km else "0"
                clean_year = year.get_text().strip() if year else "0"

                cars.append({
                    "baslik": title.get_text().strip(),
                    "fiyat": clean_price,
                    "km": int(clean_km) if clean_km.isdigit() else 0,
                    "yil": int(clean_year) if clean_year.isdigit() else 0
                })
        except Exception as e:
            continue

    return pd.DataFrame(cars)
