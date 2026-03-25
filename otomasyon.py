import pandas as pd
import time
import random
from datetime import date, datetime
import pytz
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import traceback

HOTELS = {
    "Wyndham Alanya 🏆": "https://www.wyndhamhotels.com/wyndham/antalya-turkiye/wyndham-alanya/rooms-rates",
    "Ramada Resort Akbük": "https://www.wyndhamhotels.com/ramada/aydin-turkiye/ramada-resort-akbuk/rooms-rates",
    "Ramada Hotel & Suites Kuşadası": "https://www.wyndhamhotels.com/ramada/kusadasi-turkiye/ramada-hotel-and-suites-kusadasi/rooms-rates",
    "Ramada Resort Kuşadası": "https://www.wyndhamhotels.com/ramada/kusadasi-turkiye/ramada-resort-kusadasi/rooms-rates",
    "Ramada Tire": "https://www.wyndhamhotels.com/ramada/izmir-turkiye/ramada-by-wyndham-tire/rooms-rates",
    "Wyndham Garden Lara": "https://www.wyndhamhotels.com/wyndham-garden/antalya-turkiye/wyndham-garden-lara/rooms-rates",
    "Ramada Resort Lara": "https://www.wyndhamhotels.com/ramada/antalya-turkiye/ramada-resort-lara/rooms-rates",
    "Ramada Resort Side": "https://www.wyndhamhotels.com/ramada/antalya-turkiye/ramada-resort-side/rooms-rates",
    "Ramada Encore İzmir": "https://www.wyndhamhotels.com/ramada/izmir-turkiye/ramada-encore-izmir/rooms-rates"
}

# SADECE PAZARTESİ - CUMA (4 Gece)
FULL_DATES =[
    (date(2026, 6, 29), date(2026, 7, 3), "29 Haz - 3 Tem (Pzt - Cuma)"),
    (date(2026, 7, 6), date(2026, 7, 10), "6 Tem - 10 Tem (Pzt - Cuma)"),
    (date(2026, 7, 13), date(2026, 7, 17), "13 Tem - 17 Tem (Pzt - Cuma)"),
    (date(2026, 7, 20), date(2026, 7, 24), "20 Tem - 24 Tem (Pzt - Cuma)"),
    (date(2026, 7, 27), date(2026, 7, 31), "27 Tem - 31 Tem (Pzt - Cuma)"),
    (date(2026, 8, 3), date(2026, 8, 7), "3 Ağu - 7 Ağu (Pzt - Cuma)"),
    (date(2026, 8, 10), date(2026, 8, 14), "10 Ağu - 14 Ağu (Pzt - Cuma)"),
    (date(2026, 8, 17), date(2026, 8, 21), "17 Ağu - 21 Ağu (Pzt - Cuma)"),
    (date(2026, 8, 24), date(2026, 8, 28), "24 Ağu - 28 Ağu (Pzt - Cuma)"),
    (date(2026, 8, 31), date(2026, 9, 4), "31 Ağu - 4 Eyl (Pzt - Cuma)")
]

def create_driver():
    options = Options()
    options.page_load_strategy = 'eager' # Sayfanın tamamının yüklenmesini beklemez, hızlandırır.
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('window-size=1920x1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(10) # 10 saniyede açılmazsa zorla devam et
    return driver

def check_free_night(driver, hotel_url, checkin, checkout):
    ci_str = f"{checkin.month}%2F{checkin.day}%2F{checkin.year}"
    co_str = f"{checkout.month}%2F{checkout.day}%2F{checkout.year}"
    full_url = f"{hotel_url}?brand_id=ALL&checkInDate={ci_str}&checkOutDate={co_str}&useWRPoints=true&children=0&adults=1&rooms=1"
    
    try:
        driver.get(full_url)
        # Sitenin yüklenmesi için 8 kere 1 saniyelik kontrol
        for _ in range(8):
            time.sleep(1) 
            body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
            if "this hotel is not available for your dates" in body_text:
                return "❌ Dolu", full_url
            if "pts/night" in body_text or "free nights" in body_text:
                return "✅ BOŞ ODA BULUNDU!", full_url
            if "access denied" in body_text or "security check" in body_text:
                 return "⚠️ Güvenlik Engeli", full_url
                 
        return "❓ Belirsiz", full_url
    except Exception as e:
        return "⚠️ Zaman Aşımı/Hata", full_url

def run_scan(progress_bar=None, status_text=None, log_container=None, is_auto=False):
    tz = pytz.timezone('Europe/Istanbul')
    current_time = datetime.now(tz).strftime("%d.%m.%Y %H:%M")
    results = []
    logs =[]
    
    def update_log(msg):
        if not is_auto:
            print(msg)
            if log_container:
                logs.append(msg)
                log_container.code("\n".join(logs[-5:]))

    update_log("🚀 Tarama başlatılıyor...")
    try:
        driver = create_driver()
    except Exception as e:
        update_log("HATA: Tarayıcı başlatılamadı!")
        return pd.DataFrame()

    request_counter = 0 
    total_steps = len(HOTELS) * len(FULL_DATES) # 90 adım
    
    try:
        for hotel_name, base_url in HOTELS.items():
            update_log(f"🏨 {hotel_name} kontrol ediliyor...")
            for checkin, checkout, date_label in FULL_DATES:
                # Anti-bot: 20 aramada bir çerez temizle, hata alırsan görmezden gel
                if request_counter > 0 and request_counter % 20 == 0:
                    update_log("🛡️ Anti-Bot devrede: Tarayıcı yenileniyor...")
                    try:
                        driver.quit()
                    except: pass
                    time.sleep(2)
                    driver = create_driver()
                
                time.sleep(random.uniform(1.5, 3)) # İnsan beklemesi
                
                if status_text and not is_auto:
                    status_text.info(f"⏳ Taranıyor ({request_counter + 1}/{total_steps}): **{hotel_name}** | {date_label}")
                
                status, link = check_free_night(driver, base_url, checkin, checkout)
                update_log(f" -> {date_label}: {status}")
                
                results.append({
                    "Tarama Zamanı": current_time,
                    "Otel Adı": hotel_name,
                    "Tarih": date_label,
                    "Durum": status,
                    "Rezervasyon": link
                })
                
                request_counter += 1
                if progress_bar and not is_auto:
                    progress_bar.progress(min(request_counter / total_steps, 1.0))
                
    except Exception as e:
        update_log(f"Kritik Hata (Ancak kaydedildi): {str(e)}")
    finally:
        try:
            driver.quit() 
        except: pass
        
    update_log("✅ Tarama bitti, veriler kaydediliyor...")
    
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
            
    # Eğer otomatik taramaysa logunu ayrı tutalım
    if is_auto:
        otomatik_log = f"{current_time} - Otomatik tarama tamamlandı. {len(bos_odalar)} oda bulundu.\n"
        with open("otomatik_log.txt", "a", encoding="utf-8") as f:
            f.write(otomatik_log)

    return df

if __name__ == "__main__":
    run_scan()
