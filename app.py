import streamlit as st
import cloudscraper # Bot korumasını aşmak için özel kütüphane
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

# İLK 2 HAFTA İÇİN TEST TARİHLERİ (2026 Yılı - İstenilen Kombinasyonlar)
TEST_DATES =[
    # 1. Hafta Kombinasyonları
    (date(2026, 6, 29), date(2026, 7, 3),  "29 Haz - 3 Tem (Pzt - Cuma)"),
    (date(2026, 6, 29), date(2026, 7, 1),  "29 Haz - 1 Tem (Pzt - Çarş)"),
    (date(2026, 7, 1),  date(2026, 7, 3),  "1 Tem - 3 Tem (Çarş - Cuma)"),
    
    # 2. Hafta Kombinasyonları
    (date(2026, 7, 6),  date(2026, 7, 10), "6 Tem - 10 Tem (Pzt - Cuma)"),
    (date(2026, 7, 6),  date(2026, 7, 8),  "6 Tem - 8 Tem (Pzt - Çarş)"),
    (date(2026, 7, 8),  date(2026, 7, 10), "8 Tem - 10 Tem (Çarş - Cuma)")
]

def check_free_night(hotel_url, checkin, checkout):
    # Wyndham'ın istediği tarih formatı: M/D/YYYY
    ci_str = f"{checkin.month}%2F{checkin.day}%2F{checkin.year}"
    co_str = f"{checkout.month}%2F{checkout.day}%2F{checkout.year}"
    
    # URL'yi oluştur (Puanlı arama parametreleriyle)
    full_url = f"{hotel_url}?brand_id=ALL&checkInDate={ci_str}&checkOutDate={co_str}&useWRPoints=true&children=0&adults=1&rooms=1"
    
    # cloudscraper ile Wyndham'ın bot korumasını aşıyoruz
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'ios', 'desktop': False})
    
    try:
        response = scraper.get(full_url, timeout=15)
        html = response.text.lower() # Küçük harfe çevir ki eşleşme kolay olsun
        
        # Ekran görüntülerinden aldığımız KESİN sonuç kelimeleri
        if "this hotel is not available for your dates" in html:
            return "❌ Dolu", full_url
        elif "free nights" in html or "pts/night" in html:
            return "✅ BOŞ ODA BULUNDU!", full_url
        elif "access denied" in html or "security check" in html:
            return "⚠️ Engellendi (Bot Koruması)", full_url
        else:
            return "❓ Belirsiz (Linke Tıkla)", full_url
            
    except Exception as e:
        return "⚠️ Hata (Bağlantı Kurulamadı)", full_url

# Arayüz - Tarama Butonu
if st.button("🚀 Taramayı Başlat", type="primary"):
    st.info("Tarama başladı... Lütfen bekleyin. (Bot korumasına takılmamak için oteller arası 3 saniye bekleniyor)")
    
    results =[]
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
            # Linkleri tıklanabilir yapmak
            st.dataframe(
                df, 
                column_config={
                    "Rezervasyon Linki": st.column_config.LinkColumn("Siteye Git")
                },
                hide_index=True
            )
            
            # Wyndham engellemesin diye aralarda zorunlu bekleme
            time.sleep(3)

    st.success("✅ Tarama Tamamlandı! Yukarıdaki tablodan sonuçları inceleyebilirsin.")
    if any("BOŞ" in res["Durum"] for res in results):
        st.balloons() # Eğer boş oda bulursa ekranda kutlama balonları uçar!
