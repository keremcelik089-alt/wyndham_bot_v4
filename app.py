import streamlit as st
import pandas as pd
import time
from datetime import date
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service # YENİ: Servis kütüphanesi eklendi
from selenium.webdriver.common.by import By

# Ekran ayarı
st.set_page_config(page_title="Wyndham Free Night Avcısı", layout="wide")

st.title("🏨 Wyndham 'Free Night' Kontrol Paneli")
st.markdown("**Öncelikli Otel:** Wyndham Alanya 🎯")

# Otellerin Temel Linkleri
HOTELS = {
    "Ramada Tire": "https://www.wyndhamhotels.com/ramada/izmir-turkiye/ramada-by-wyndham-tire/rooms-rates",
    "Wyndham Garden Lara": "https://www.wyndhamhotels.com/wyndham-garden/antalya-turkiye/wyndham-garden-lara/rooms-rates",
    "Ramada Resort Lara": "https://www.wyndhamhotels.com/ramada/antalya-turkiye/ramada-resort-lara/rooms-rates",
    "Ramada Resort Side": "https://www.wyndhamhotels.com/ramada/antalya-turkiye/ramada-resort-side/rooms-rates",
    "Ramada Encore İzmir": "https://www.wyndhamhotels.com/ramada/izmir-turkiye/ramada-encore-izmir/rooms-rates"
}

# TEST TARİHLERİ
TEST_DATES =[
    (date(2026, 6, 29), date(2026, 7, 3),  "29 Haz - 3 Tem (Pzt - Cuma)"),
    (date(2026, 6, 29), date(2026, 7, 1),  "29 Haz - 1 Tem (Pzt - Çarş)"),
    (date(2026, 7, 1),  date(2026, 7, 3),  "1 Tem - 3 Tem (Çarş - Cuma)"),
    (date(2026, 7, 6),  date(2026, 7, 10), "6 Tem - 10 Tem (Pzt - Cuma)"),
    (date(2026, 7, 6),  date(2026, 7, 8),  "6 Tem - 8 Tem (Pzt - Çarş)"),
    (date(2026, 7, 8),  date(2026, 7, 10), "8 Tem - 10 Tem (Çarş - Cuma)")
]

def check_free_night(driver, hotel_url, checkin, checkout):
    ci_str = f"{checkin.month}%2F{checkin.day}%2F{checkin.year}"
    co_str = f"{checkout.month}%2F{checkout.day}%2F{checkout.year}"
    full_url = f"{hotel_url}?brand_id=ALL&checkInDate={ci_str}&checkOutDate={co_str}&useWRPoints=true&children=0&adults=1&rooms=1"
    
    try:
        driver.get(full_url)
        # Sitenin verileri yüklemesi ve odayı bulması için bekleme
        time.sleep(6) 
        
        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        
        if "free nights" in body_text or "pts/night" in body_text or "15,000" in body_text:
            return "✅ BOŞ ODA BULUNDU!", full_url
        elif "this hotel is not available for your dates" in body_text:
            return "❌ Dolu", full_url
        elif "access denied" in body_text or "security" in body_text:
             return "⚠️ Sistem Engeli", full_url
        else:
            return "❓ Belirsiz (Linke Tıkla)", full_url
            
    except Exception as e:
        return "⚠️ Bağlantı Hatası", full_url

if st.button("🚀 Taramayı Başlat", type="primary"):
    st.info("Tarama başladı... Sistem sayfaların tam yüklenmesini beklediği için her otel yaklaşık 6 saniye sürecektir.")
    
    table_placeholder = st.empty()
    
    # YENİ: Streamlit Cloud (Linux) için özel Chrome Ayarları ve Dosya Yolları
    options = Options()
    options.add_argument('--headless') # Görünmez mod
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # BURASI ÇOK ÖNEMLİ: Streamlit sunucusundaki tarayıcının yerini gösteriyoruz
    options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    
    try:
        # Chrome'u tanımlanan servis ve yollarla başlat
        driver = webdriver.Chrome(service=service, options=options)
        
        results =[]
        progress_bar = st.progress(0)
        total_checks = len(HOTELS) * len(TEST_DATES)
        current_check = 0
        
        for hotel_name, base_url in HOTELS.items():
            for checkin, checkout, date_label in TEST_DATES:
                status, link = check_free_night(driver, base_url, checkin, checkout)
                
                results.append({
                    "Otel Adı": hotel_name,
                    "Tarih": date_label,
                    "Durum": status,
                    "Rezervasyon Linki": link
                })
                
                current_check += 1
                progress_bar.progress(current_check / total_checks)
                
                df = pd.DataFrame(results)
                
                table_placeholder.dataframe(
                    df, 
                    column_config={"Rezervasyon Linki": st.column_config.LinkColumn("Siteye Git")},
                    hide_index=True,
                    use_container_width=True
                )
                
    except Exception as e:
        st.error(f"Chrome başlatılamadı! Hata detayı: {e}")
    finally:
        # Hata olsa da olmasa da sekmeleri kapat (sunucu şişmesin)
        if 'driver' in locals():
            driver.quit()
        
    st.success("✅ Tarama Tamamlandı!")
    if any("BOŞ" in res["Durum"] for res in results):
        st.balloons()
