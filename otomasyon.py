import pandas as pd
import time
import random
from datetime import date, datetime
import pytz
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

HOTELS = {
    "Ramada Hotel & Suites Kuşadası": "https://www.wyndhamhotels.com/ramada/kusadasi-turkiye/ramada-hotel-and-suites-kusadasi/rooms-rates",
    "Ramada Resort Kuşadası": "https://www.wyndhamhotels.com/ramada/kusadasi-turkiye/ramada-resort-kusadasi/rooms-rates",
    "Ramada Tire": "https://www.wyndhamhotels.com/ramada/izmir-turkiye/ramada-by-wyndham-tire/rooms-rates",
    "Wyndham Garden Lara": "https://www.wyndhamhotels.com/wyndham-garden/antalya-turkiye/wyndham-garden-lara/rooms-rates",
    "Ramada Resort Lara": "https://www.wyndhamhotels.com/ramada/antalya-turkiye/ramada-resort-lara/rooms-rates",
    "Ramada Resort Side": "https://www.wyndhamhotels.com/ramada/antalya-turkiye/ramada-resort-side/rooms-rates",
    "Ramada Encore İzmir": "https://www.wyndhamhotels.com/ramada/izmir-turkiye/ramada-encore-izmir/rooms-rates"
}

FULL_DATES =[
    (date(2026, 6, 29), date(2026, 7, 3), "29 Haz - 3 Tem (Pzt - Cuma)"),
    (date(2026, 6, 29), date(2026, 7, 1), "29 Haz - 1 Tem (Pzt - Çarş)"),
    (date(2026, 7, 1), date(2026, 7, 3), "1 Tem - 3 Tem (Çarş - Cuma)"),
    (date(2026, 7, 6), date(2026, 7, 10), "6 Tem - 10 Tem (Pzt - Cuma)"),
    (date(2026, 7, 6), date(2026, 7, 8), "6 Tem - 8 Tem (Pzt - Çarş)"),
]

# TEMİZ TARAYICI OLUŞTURMA FONKSİYONU
def create_driver():
    options = Options()
    options.page_load_strategy = 'eager'
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # Sitenin bizi mobil cihaz veya gerçek bilgisayar sanması için rastgelelik
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    return webdriver.Chrome(options=options)

def check_free_night(driver, hotel_url, checkin, checkout):
    ci_str = f"{checkin.month}%2F{checkin.day}%2F{checkin.year}"
    co_str = f"{checkout.month}%2F{checkout.day}%2F{checkout.year}"
    full_url = f"{hotel_url}?brand_id=ALL&checkInDate={ci_str}&checkOutDate={co_str}&useWRPoints=true&children=0&adults=1&rooms=1"
    
    try:
        driver.set_page_load_timeout(15) # 15 Saniyede açılmazsa zorlama
        driver.get(full_url)
        
        for _ in range(12):
            time.sleep(1) 
            body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
            if "this hotel is not available for your dates" in body_text:
                return "❌ Dolu", full_url
            if "pts/night" in body_text:
                return "✅ BOŞ ODA BULUNDU!", full_url
            if "access denied" in body_text or "security check" in body_text:
                 return "⚠️ Güvenlik Engeli", full_url
                 
        return "❓ Belirsiz", full_url
    except:
        return "⚠️ Bağlantı Hatası", full_url

def main():
    print("Otomatik tarama başlatılıyor... Hayalet modu aktif!")
    
    tz = pytz.timezone('Europe/Istanbul')
    current_time = datetime.now(tz).strftime("%d.%m.%Y %H:%M")
    results =[]
    
    driver = create_driver()
    request_counter = 0 # Kaç arama yaptığımızı sayacak
    
    try:
        for hotel_name, base_url in HOTELS.items():
            print(f"\n🏨 Taranıyor: {hotel_name}")
            
            for checkin, checkout, date_label in FULL_DATES:
                # GÜVENLİK ZIRHI: Her 15 aramada bir tarayıcıyı tamamen kapat ve yenisini aç
                if request_counter > 0 and request_counter % 15 == 0:
                    print("🛡️ Anti-Bot devrede: Çerezler temizleniyor, yeni gizli sekme açılıyor...")
                    driver.quit()
                    time.sleep(random.uniform(5, 8)) # Şüphe çekmemek için 5-8 saniye bekle
                    driver = create_driver()
                
                # Her arama arası hafif rastgele bekleme (İnsan taklidi)
                time.sleep(random.uniform(2, 4))
                
                status, link = check_free_night(driver, base_url, checkin, checkout)
                print(f"   -> {date_label}: {status}")
                
                results.append({
                    "Tarama Zamanı": current_time,
                    "Otel Adı": hotel_name,
                    "Tarih": date_label,
                    "Durum": status,
                    "Rezervasyon": link
                })
                
                request_counter += 1
                
    finally:
        driver.quit() # En sonunda tarayıcıyı kesin kapat
        
    print("Tarama bitti! Veriler kaydediliyor...")
    
    # ---------------- KAYIT İŞLEMLERİ ----------------
    df = pd.DataFrame(results)
    df.to_csv('son_durum.csv', index=False)
    
    bos_odalar = df[df['Durum'].str.contains("✅")]
    if not bos_odalar.empty:
        try:
            eski_gecmis = pd.read_csv('bulunan_odalar_gecmisi.csv')
            yeni_gecmis = pd.concat([eski_gecmis, bos_odalar])
            yeni_gecmis.drop_duplicates(subset=['Otel Adı', 'Tarih', 'Durum'], keep='last', inplace=True)
            yeni_gecmis.to_csv('bulunan_odalar_gecmisi.csv', index=False)
        except FileNotFoundError:
            bos_odalar.to_csv('bulunan_odalar_gecmisi.csv', index=False)
            
    print("Kayıt Başarılı!")

if __name__ == "__main__":
    main()
