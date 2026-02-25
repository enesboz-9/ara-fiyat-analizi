import pandas as pd
from bs4 import BeautifulSoup

def parse_html_data(html_content):
    """HTML içeriğini parçalara ayırır ve temiz veri setine dönüştürür."""
    soup = BeautifulSoup(html_content, 'html.parser')
    cars = []

    # Arabam.com'da ilanlar genellikle <tr> veya <div> içinde tutulur.
    # En yaygın olanları tek tek deniyoruz.
    items = soup.select("tr.listing-new-item") or soup.select(".unf-listing-card") or soup.select(".listing-list-item")

    for item in items:
        try:
            # Seçicileri genişletiyoruz (Sitede farklı classlar kullanılabiliyor)
            title = item.select_one(".model-name, .listing-model-name, h3")
            price = item.select_one(".price, .listing-price, .item-price")
            
            if title and price:
                # Fiyat temizleme (Sayı dışındaki her şeyi atıyoruz)
                price_text = price.get_text().replace("TL", "").replace(".", "").replace(" ", "").strip()
                clean_price = int(''.join(filter(str.isdigit, price_text)))
                
                cars.append({
                    "baslik": title.get_text().strip(),
                    "fiyat": clean_price
                })
        except:
            continue

    return pd.DataFrame(cars)

# Mevcut get_live_data fonksiyonun kalsın, o da parse_html_data'yı çağırsın.
