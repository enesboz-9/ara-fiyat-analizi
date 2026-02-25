import os
import time
import pandas as pd
import subprocess
from bs4 import BeautifulSoup

# Playwright kurulum kontrolü (Streamlit Cloud için)
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    subprocess.run(["pip", "install", "playwright"])
    os.system("playwright install chromium")
    from playwright.sync_api import sync_playwright

def get_live_data(url):
    """Link üzerinden veri çekmeye çalışır."""
    if not url:
        return pd.DataFrame()
        
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = browser.new_context(user_agent="Mozilla/5.0...")
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)
            html_content = page.content()
            browser.close()
            return parse_html_data(html_content)
        except Exception as e:
            print(f"Hata: {e}")
            return pd.DataFrame()

def parse_html_data(html_content):
    """HTML içeriğini ayıklar."""
    if not html_content:
        return pd.DataFrame()
        
    soup = BeautifulSoup(html_content, 'html.parser')
    cars = []

    # Arabam.com ilan seçicileri
    items = soup.select("tr.listing-new-item") or soup.select(".unf-listing-card") or soup.select(".listing-list-item")

    for item in items:
        try:
            title = item.select_one(".model-name, .listing-model-name, h3")
            price = item.select_one(".price, .listing-price, .item-price")
            
            if title and price:
                price_text = price.get_text().replace("TL", "").replace(".", "").replace(" ", "").strip()
                # Sadece rakamları al
                clean_price = int(''.join(filter(str.isdigit, price_text)))
                
                cars.append({
                    "baslik": title.get_text().strip(),
                    "fiyat": clean_price
                })
        except:
            continue

    return pd.DataFrame(cars)
