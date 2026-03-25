import streamlit as st
import pandas as pd
import time
from datetime import date
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# Sayfa Ayarları (iPad için en iyisi)
st.set_page_config(page_title="Wyndham Puan Avcısı", layout="wide", page_icon="🏖️")

st.title("🏖️ Wyndham 'Free Night' Kontrol Paneli")
st.markdown("Belirlediğiniz tüm yaz sezonu için otellerin puanlı oda uygunluğu taranıyor.")

# Otellerin Temel Linkleri
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

# TÜM YAZ SEZONU TARİHLERİ (30 Kombinasyon)
FULL_DATES =[
    (date(2026, 6, 29), date(2026, 7, 3),  "29 Haz - 3 Tem (Pzt - Cuma)"),
    (date(2026, 6, 29), date(2026, 7, 1),  "29 Haz - 1 Tem (Pzt - Çarş)"),
    (date(2026, 7, 1),  date(2026, 7, 3),  "1 Tem - 3 Tem (Çarş - Cuma)"),

    (date(2026, 7, 6),  date(2026, 7, 10), "6 Tem - 10 Tem (Pzt - Cuma)"),
    (date(2026, 7, 6),  date(2026, 7, 8),  "6 Tem - 8 Tem (Pzt - Çarş)"),
    (date(2026, 7, 8),  date(2026, 7, 10), "8 Tem - 10 Tem (Çarş - Cuma)"),

    (date(2026, 7, 13), date(2026, 7, 17), "13 Tem - 17 Tem (Pzt - Cuma)"),
    (date(2026, 7, 13), date(2026, 7, 15), "13 Tem - 15 Tem (Pzt - Çarş)"),
    (date(2026, 7, 15), date(2026, 7, 17), "15 Tem - 17 Tem (Çarş - Cuma)"),

    (date(2026, 7, 20), date(2026, 7, 24), "20 Tem - 24 Tem (Pzt - Cuma)"),
    (date(2026, 7, 20), date(2026, 7, 22), "20 Tem - 22 Tem (Pzt - Çarş)"),
    (date(2026, 7, 22), date(2026, 7, 24), "22 Tem - 24 Tem (Çarş - Cuma)"),

    (date(2026, 7, 27), date(2026, 7, 31), "27 Tem - 31 Tem (Pzt - Cuma)"),
    (date(2026, 7, 27), date(2026, 7, 29), "27 Tem - 29 Tem (Pzt - Çarş)"),
    (date(2026, 7, 29), date(2026, 7, 31), "29 Tem - 31 Tem (Çarş - Cuma)"),

    (date(2026, 8, 3),  date(2026, 8, 7),  "3 Ağu - 7 Ağu (Pzt - Cuma)"),
    (date(2026, 8, 3),  date(2026, 8, 5),  "3 Ağu - 5 Ağu (Pzt - Çarş)"),
    (date(2026, 8, 5),  date(2026, 8, 7),  "5 Ağu - 7 Ağu (Çarş - Cuma)"),

    (date(2026, 8, 10), date(2026, 8, 14), "10 Ağu - 14 Ağu (Pzt - Cuma)"),
    (date(2026, 8, 10), date(2026, 8, 12), "10 Ağu - 12 Ağu (Pzt - Çarş)"),
    (date(2026, 8, 12), date(2026, 8, 14), "12 Ağu - 14 Ağu (Çarş - Cuma)"),

    (date(2026, 8, 17), date(2026, 8, 21), "17 Ağu - 21 Ağu (Pzt - Cuma)"),
    (date(2026, 8, 17), date(2026, 8, 19), "17 Ağu - 19 Ağu (Pzt - Çarş)"),
    (date(2026, 8, 19), date(2026, 8, 21), "19 Ağu - 21 Ağu (Çarş - Cuma)"),

    (date(2026, 8, 24), date(2026, 8, 28), "24 Ağu - 28 Ağu (Pzt - Cuma)"),
    (date(2026, 8, 24), date(2026, 8, 26), "24 Ağu - 26 Ağu (Pzt - Çarş)"),
    (date(2026, 8, 26), date(2026, 8, 28), "26 Ağu - 28 Ağu (Çarş - Cuma)"),

    (date(2026, 8, 31), date(2026, 9, 4),  "31 Ağu - 4 Eyl (Pzt - Cuma)"),
    (date(2026, 8, 31), date(2026, 9, 2),  "31 Ağu - 2 Eyl (Pzt - Çarş)"),
    (date(2026, 9, 2),  date(2026, 9, 4),  "2 Eyl - 4 Eyl (Çarş - Cuma)")
]

def check_free_night(driver, hotel_url, checkin, checkout):
    ci_str = f"{checkin.month}%2F{checkin.day}%2F{checkin.year}"
    co_str = f"{checkout.month}%2F{checkout.day}%2F{checkout.year}"
    full_url = f"{hotel_url}?brand_id=ALL&checkInDate={ci_str}&checkOutDate={co_str}&useWRPoints=true&children=0&adults=1&rooms=1"
    
    try:
        driver.get(full_url)
        
        # Akıllı Bekleme ve Radar
        for _ in range(12):
            time.sleep(1) 
            body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
            
            if "this hotel is not available for your dates" in body_text:
                return "❌ Dolu", full_url
                
            if "pts/night" in body_text:
                return "✅ BOŞ ODA BULUNDU!", full_url
                
            if "access denied" in body_text or "security check" in body_text:
                 return "⚠️ Sistem Engeli", full_url
                 
        return "❓ Belirsiz (Yavaş Yüklendi)", full_url
            
    except Exception as e:
        return "⚠️ Bağlantı Hatası", full_url

# ARAYÜZ ve BAŞLATMA
if st.button("🚀 Tüm Sezonu Tara (Başlat)", type="primary"):
    total_checks = len(HOTELS) * len(FULL_DATES)
    st.info(f"⏳ Toplam **{total_checks}** arama yapılacak. Arkanıza yaslanın, sistem hepsini kontrol edip kutuları dolduracak.")
    
    # İlerleme Çubuğu ve Durum Metni
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # GÖRSEL DÜZENLEME: Her Otel İçin Ayrı Bir "Açılır Kutu (Expander)" Oluştur
    hotel_uis = {}
    for hotel in HOTELS:
        with st.expander(f"🏨 {hotel}", expanded=True):
            hotel_uis[hotel] = st.empty()
            hotel_uis[hotel].markdown("*Sıra bekleniyor...*")
            
    # Tarayıcı Ayarları
    options = Options()
    options.page_load_strategy = 'eager' # HIZLANDIRICI: Sitenin fotoğraflarını yüklemesini bekleme!
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    
    hotel_results = {h:[] for h in HOTELS}
    current_check = 0
    found_any_room = False
    
    try:
        driver = webdriver.Chrome(service=service, options=options)
        
        for hotel_name, base_url in HOTELS.items():
            # Kutunun içindeki yazıyı güncelle
            hotel_uis[hotel_name].info("🔍 Tarihler taranıyor...")
            
            for checkin, checkout, date_label in FULL_DATES:
                status, link = check_free_night(driver, base_url, checkin, checkout)
                
                # Sadece o otele ait listeye ekle
                hotel_results[hotel_name].append({
                    "Tarih": date_label,
                    "Durum": status,
                    "Rezervasyon": link
                })
                
                if "✅" in status:
                    found_any_room = True
                
                # Otelin kendi kutusunu ANLIK güncelle (Otel ismini tablodan çıkardık, çünkü zaten kutu isminde yazıyor)
                df = pd.DataFrame(hotel_results[hotel_name])
                hotel_uis[hotel_name].dataframe(
                    df, 
                    column_config={"Rezervasyon": st.column_config.LinkColumn("Siteye Git")},
                    hide_index=True,
                    use_container_width=True
                )
                
                # İlerleme çubuğunu güncelle
                current_check += 1
                progress_bar.progress(current_check / total_checks)
                status_text.markdown(f"**İlerleme:** {current_check} / {total_checks} tarih kontrol edildi.")
                
    except Exception as e:
        st.error(f"Sistem Hatası: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()
        
    st.success("✅ Tüm Yaz Sezonu Taraması Başarıyla Tamamlandı!")
    
    # Eğer herhangi bir otelde, herhangi bir tarihte oda bulduysa kutlama yap
    if found_any_room:
        st.balloons()
