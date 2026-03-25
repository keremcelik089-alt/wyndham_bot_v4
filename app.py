import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
import pytz
import threading
from otomasyon import run_scan

# Arka Plan Zamanlayıcı (03:00, 11:00, 19:00)
def schedule_task():
    tz = pytz.timezone('Europe/Istanbul')
    while True:
        now = datetime.now(tz)
        # Sadece bu saatlerde ve dakikası 0 iken çalışır
        if now.hour in[3, 11, 19] and now.minute == 0:
            try:
                run_scan(is_auto=True)
                time.sleep(65) # Aynı dakika içinde 2 kere çalışmasını engellemek için
            except:
                pass
        time.sleep(30) # Her 30 saniyede bir saati kontrol et

# Bu kodu Streamlit başlatıldığında sadece 1 kere tetikler
if 'scheduler_started' not in st.session_state:
    t = threading.Thread(target=schedule_task, daemon=True)
    t.start()
    st.session_state['scheduler_started'] = True

# --- SAYFA AYARLARI VE MODERN CSS TASARIMI ---
st.set_page_config(page_title="Wyndham Puan Avcısı", layout="wide", page_icon="🏖️")

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    .main-header { text-align: center; font-family: 'Arial Black', sans-serif; color: #1e3d59; margin-bottom: 20px;}
    .big-btn-container { display: flex; justify-content: center; margin-bottom: 30px; }
    .card-container { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin-bottom: 15px; border-left: 6px solid #ff6e40; }
    .card-title { font-size: 20px; font-weight: bold; color: #1e3d59; margin-bottom: 10px; }
    .status-ok { color: #2e7d32; font-weight: bold; font-size: 16px; background-color: #e8f5e9; padding: 4px 8px; border-radius: 6px; }
    .status-fail { color: #c62828; font-weight: bold; font-size: 14px; }
    .date-text { font-size: 15px; color: #555; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🏖️ Wyndham Puan Avcısı Dashboard</h1>', unsafe_allow_html=True)

# SEKMELER
tab1, tab2, tab3 = st.tabs(["🚀 Canlı Kontrol Merkezi", "🤖 Otomatik Takip Geçmişi", "🎉 BULUNAN ODALAR"])

# SEKME 1: MODERN CANLI KONTROL
with tab1:
    st.write("Tek tıkla 9 otelin 10 farklı tarihini (Sadece Pzt-Cuma) tarayın. Takılma ve çökme koruması aktiftir.")
    
    # EN ÜSTTEKİ DEV BUTON
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("⚡ TÜMÜNÜ KONTROL ET (90 İSTEK)", type="primary", use_container_width=True):
            st.markdown("### ⚙️ Canlı Tarama İlerlemesi")
            progress_bar = st.progress(0)
            status_text = st.empty()
            log_container = st.empty()
            
            with st.spinner("Tarayıcı hazırlanıyor, işlemler başlıyor..."):
                run_scan(progress_bar, status_text, log_container, is_auto=False)
                
            status_text.success("🎉 Tarama başarıyla tamamlandı! Aşağıdan sonuçları inceleyebilirsiniz.")
            time.sleep(2)
            st.rerun()

    st.markdown("---")
    st.subheader("📊 Son Tarama Durumu (Oteller)")

    if os.path.exists('son_durum.csv'):
        df = pd.read_csv('son_durum.csv')
        st.caption(f"🕒 **Son Tarama Zamanı:** {df['Tarama Zamanı'].iloc[0]}")
        
        oteller = df['Otel Adı'].unique()
        
        # Grid sistemiyle otelleri yan yana kartlar halinde diz (3 kolon)
        cols = st.columns(3)
        for i, otel in enumerate(oteller):
            otel_df = df[df['Otel Adı'] == otel]
            basarili_tarihler = otel_df[otel_df['Durum'].str.contains("✅")]
            
            with cols[i % 3]: # Kolonlara sırayla dağıt
                html_content = f"""
                <div class="card-container">
                    <div class="card-title">{otel}</div>
                """
                if not basarili_tarihler.empty:
                    html_content += f'<div style="margin-bottom:10px;"><span class="status-ok">🔥 {len(basarili_tarihler)} Fırsat Bulundu!</span></div>'
                    for _, row in basarili_tarihler.iterrows():
                        html_content += f'<div class="date-text">✔️ {row["Tarih"]}</div>'
                else:
                    html_content += f'<div><span class="status-fail">❌ Şuan Fırsat Yok</span></div>'
                
                html_content += "</div>"
                st.markdown(html_content, unsafe_allow_html=True)
                
                # Link butonunu kartın dışına eklemek zorundayız (Streamlit HTML içinde interaktif click desteklemez)
                if not basarili_tarihler.empty:
                    ilk_link = basarili_tarihler.iloc[0]["Rezervasyon"]
                    st.link_button(f"{otel} - Rezervasyon Yap", ilk_link, use_container_width=True)
    else:
        st.info("Henüz manuel bir arama yapılmadı. Yukarıdaki butona tıklayarak taramayı başlatın.")

# SEKME 2: OTOMATİK TAKİP (03:00, 11:00, 19:00)
with tab2:
    st.markdown("### 🤖 Robot Bekçiniz Devrede!")
    st.write("Sistem arka planda **Türkiye saatiyle 03:00, 11:00 ve 19:00'da** otomatik olarak tüm otelleri tarayacak şekilde ayarlanmıştır. Bu uygulamanın barındırıldığı sunucu (sekme) açık kaldığı sürece bu saatlerde kontroller yapılacaktır.")
    
    st.markdown("**Otomatik Tarama Kayıtları:**")
    if os.path.exists("otomatik_log.txt"):
        with open("otomatik_log.txt", "r", encoding="utf-8") as f:
            loglar = f.readlines()
            for log in reversed(loglar[-15:]): # Son 15 logu ters sırayla göster
                st.code(log.strip())
    else:
        st.write("Henüz otomatik tarama saati gelmedi veya tetiklenmedi.")

# SEKME 3: GEÇMİŞTE BULUNAN ODALAR
with tab3:
    st.markdown("### 🎉 Hazine Sandığı")
    st.write("Geçmiş manuel ve otomatik taramalarda yakalanan boş odaların listesi:")
    if os.path.exists('bulunan_odalar_gecmisi.csv'):
        df_gecmis = pd.read_csv('bulunan_odalar_gecmisi.csv')
        st.dataframe(
            df_gecmis,
            column_config={"Rezervasyon": st.column_config.LinkColumn("Siteye Git")},
            hide_index=True,
            use_container_width=True
        )
    else:
        st.write("Şu ana kadar yapılan taramalarda henüz boş oda yakalanamadı.")
