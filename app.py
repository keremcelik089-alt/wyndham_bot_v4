import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import date

# iPad ekranına uygun geniş tasarım
st.set_page_config(page_title="Wyndham Free Night Avcısı", layout="wide")

st.title("🏨 Wyndham 'Free Night' Kontrol Paneli")
st.markdown("**Öncelikli Otel:** Wyndham Alanya 🎯")

# Otellerin Temel Linkleri (Tarihler olmadan)
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

# SADECE TEST TARİHLERİ (2026 Yılı - İstenilen ilk iki haftanın Pzt-Cuma'sı)
TEST_DATES = [
    (date(2026, 6, 29), date(2026, 7, 3), "29 Haz - 3 Tem (4 Gece)"),
    (date(2026, 7, 6), date(2026, 7, 10), "6 Tem - 10 Tem (4 Gece)")
]

# Bot korumasına takılmamak için sahte tarayıcı başlığı
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def check_free_night(hotel_url, checkin, checkout):
    # Wyndham'ın istediği tarih formatı: M/D/YYYY
    ci_str = f"{checkin.month}%2F{checkin.day}%2F{checkin.year}"
    co_str = f"{checkout.month}%2F{checkout.day}%2F{checkout.year}"
    
    # URL'yi oluştur (Puanlı arama parametreleriyle)
    full_url = f"{hotel_url}?brand_id=ALL&checkInDate={ci_str}&checkOutDate={co_str}&useWRPoints=true&children=0&adults=1&rooms=1"
    
    try:
        response = requests.get(full_url, headers=HEADERS, timeout=10)
        # Sitedeki uyarı metinlerini kontrol et
        html = response.text.lower()
        
        # Eğer odalar tükendiyse Wyndham genelde bu tarz kelimeler kullanır
        if "no rooms available" in html or "sold out" in html or "we are unable to find" in html:
            return "❌ Dolu", full_url
        else:
            return "✅ BOŞ ODA OLABİLİR!", full_url
            
    except Exception as e:
        return "⚠️ Hata (Bağlantı)", full_url

# Arayüz - Tarama Butonu
if st.button("🚀 Taramayı Başlat", type="primary"):
    st.info("Tarama başladı... Lütfen bekleyin. (Bot korumasına takılmamak için oteller arası 2 saniye bekleniyor)")
    
    results = []
    progress_bar = st.progress(0)
    total_checks = len(HOTELS) * len(TEST_DATES)
    current_check = 0
    
    # Tabloyu anlık göstermek için boş bir alan oluştur
    table_placeholder = st.empty()
    
    for hotel_name, base_url in HOTELS.items():
        for checkin, checkout, date_label in TEST_DATES:
            
            # Taramayı yap
            status, link = check_free_night(base_url, checkin, checkout)
            
            # Sonucu listeye ekle
            results.append({
                "Otel Adı": hotel_name,
                "Tarih": date_label,
                "Durum": status,
                "Rezervasyon Linki": link
            })
            
            current_check += 1
            progress_bar.progress(current_check / total_checks)
            
            # Tabloyu her adımda güncelle
            df = pd.DataFrame(results)
            # Linkleri tıklanabilir yapmak için Streamlit ayarı
            st.dataframe(
                df, 
                column_config={
                    "Rezervasyon Linki": st.column_config.LinkColumn("Siteye Git")
                },
                hide_index=True
            )
            
            # Çok hızlı istek atıp engellenmemek için ufak bir bekleme
            time.sleep(2)

    st.success("✅ Tarama Tamamlandı! Yukarıdaki tablodan sonuçları inceleyebilirsin.")
    if any("BOŞ" in res["Durum"] for res in results):
        st.balloons() # Eğer boş oda bulursa ekranda balonlar uçar :)
