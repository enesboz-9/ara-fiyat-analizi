import pandas as pd
from bs4 import BeautifulSoup

def parse_html_data(html_content):
    if not html_content:
        return pd.DataFrame()
        
    soup = BeautifulSoup(html_content, 'html.parser')
    cars = []

    # Arabam.com ilan satırlarını bul (Farklı görünümler için 3 farklı seçici)
    items = soup.select("tr.listing-new-item") or soup.select(".unf-listing-card") or soup.select(".listing-list-item")

    for item in items:
        try:
            # 1. Başlık ve Model
            title_elem = item.select_one(".model-name, .listing-model-name, h3")
            # 2. Fiyat
            price_elem = item.select_one(".price, .listing-price, .item-price")
            # 3. Kilometre (KM)
            km_elem = item.select_one(".listing-km, .km-value, td:nth-child(4)") 
            # 4. Yıl
            year_elem = item.select_one(".listing-year, .year-value, td:nth-child(3)")

            if title_elem and price_elem:
                title = title_elem.get_text().strip()
                
                # Fiyat temizleme
                price_text = ''.join(filter(str.isdigit, price_elem.get_text()))
                price = int(price_text) if price_text else 0
                
                # KM temizleme
                km_text = ''.join(filter(str.isdigit, km_elem.get_text())) if km_elem else "0"
                km = int(km_text) if km_text else 0

                # Yıl temizleme
                year_text = ''.join(filter(str.isdigit, year_elem.get_text())) if year_elem else "0"
                year = int(year_text) if year_text else 0

                # Tüm metni hasar analizi için sakla
                full_text = item.get_text().lower()

                cars.append({
                    "baslik": title,
                    "fiyat": price,
                    "km": km,
                    "yil": year,
                    "ham_metin": full_text
                })
        except:
            continue
            
    return pd.DataFrame(cars)

def get_live_data(url):
    # Bu fonksiyonun içi önceki gibi kalabilir (Playwright kısmı)
    # Şimdilik hızlı analiz için boş dönebilir veya pas geçebiliriz.
    return pd.DataFrame()
