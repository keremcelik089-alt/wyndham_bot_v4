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
        if now.hour in [3, 11, 19] and now.minute == 0:
            try:
                run_scan(is_auto=True)
                time.sleep(65) 
            except:
                pass
        time.sleep(30)

if 'scheduler_started' not in st.session_state:
    t = threading.Thread(target=schedule_task, daemon=True)
    t.start()
    st.session_state['scheduler_started'] = True

# --- GOOGLE AI STUDIO MATERIAL DESIGN CSS ---
st.set_page_config(page_title="Wyndham Puan Avcısı", layout="wide", page_icon="🔍")

st.markdown("""
    <style>
    /* Google Fontu İçe Aktarma */
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Google Sans', sans-serif !important;
        background-color: #f8f9fa !important; /* AI Studio açık gri arkaplan */
        color: #1f1f1f !important;
    }
    
    /* Ana Başlık */
    .main-header { 
        font-weight: 500; 
        color: #1f1f1f; 
        font-size: 32px;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }
    
    /* Subtitle (Alt Açıklama) */
    .sub-text {
        color: #444746;
        font-size: 16px;
        margin-bottom: 24px;
    }
    
    /* Özel Buton Tasarımı (Google Mavi Hap Buton) */
    div.stButton > button:first-child {
        background-color: #0b57d0 !important;
        color: white !important;
        border-radius: 100px !important; /* Tam oval */
        padding: 10px 24px !important;
        font-weight: 500 !important;
        border: none !important;
        box-shadow: none !important;
        transition: background-color 0.2s;
    }
    div.stButton > button:first-child:hover {
        background-color: #0842a0 !important;
        box-shadow: 0 1px 3px 0 rgba(0,0,0,0.3) !important;
    }

    /* Kart Tasarımları (Oteller İçin) */
    .google-card { 
        background-color: #ffffff; 
        padding: 24px; 
        border-radius: 16px; 
        border: 1px solid #dadce0;
        margin-bottom: 16px; 
    }
    .card-title { 
        font-size: 18px; 
        font-weight: 500; 
        color: #1f1f1f; 
        margin-bottom: 12px; 
    }
    .status-ok { 
        color: #146c2e; 
        font-weight: 500; 
        background-color: #e6f4ea; 
        padding: 6px 12px; 
        border-radius: 8px; 
        display: inline-block;
        font-size: 14px;
        margin-bottom: 12px;
    }
    .status-fail { 
        color: #b3261e; 
        font-size: 14px; 
        font-weight: 500;
    }
    .date-text { 
        font-size: 14px; 
        color: #444746; 
        margin-top: 4px;
        padding-left: 8px;
        border-left: 3px solid #0b57d0;
    }
    
    /* Streamlit Üst Menüyü Gizleme */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">Wyndham Puan Avcısı</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Sistem 9 oteli Pazartesi - Cuma aralığında (toplam 90 kombinasyon) tarayacak şekilde yapılandırılmıştır.</div>', unsafe_allow_html=True)

# SEKMELER (Google AI Studio tarzı sade sekmeler)
tab1, tab2, tab3 = st.tabs(["Kontrol Paneli", "Otomatik Geçmiş", "Bulunan Fırsatlar"])

# SEKME 1: KONTROL PANELİ
with tab1:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Taramayı Başlat", use_container_width=True):
            st.markdown("### Tarama İlerlemesi")
            progress_bar = st.progress(0)
            status_text = st.empty()
            log_container = st.empty()
            
            with st.spinner("Motor başlatılıyor... Lütfen sayfadan ayrılmayın."):
                run_scan(progress_bar, status_text, log_container, is_auto=False)
                
            status_text.success("Tarama tamamlandı!")
            time.sleep(2)
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    if os.path.exists('son_durum.csv'):
        df = pd.read_csv('son_durum.csv')
        st.markdown(f"<div style='color: #444746; font-size: 14px; margin-bottom: 16px;'>Son Güncelleme: {df['Tarama Zamanı'].iloc[0]}</div>", unsafe_allow_html=True)
        
        oteller = df['Otel Adı'].unique()
        cols = st.columns(3)
        for i, otel in enumerate(oteller):
            otel_df = df[df['Otel Adı'] == otel]
            basarili_tarihler = otel_df[otel_df['Durum'].str.contains("✅")]
            
            with cols[i % 3]:
                html_content = f"""
                <div class="google-card">
                    <div class="card-title">{otel}</div>
                """
                if not basarili_tarihler.empty:
                    html_content += f'<div class="status-ok">✨ {len(basarili_tarihler)} Fırsat Bulundu</div>'
                    for _, row in basarili_tarihler.iterrows():
                        html_content += f'<div class="date-text">{row["Tarih"]}</div>'
                else:
                    html_content += f'<div class="status-fail">Uygun oda bulunamadı</div>'
                
                html_content += "</div>"
                st.markdown(html_content, unsafe_allow_html=True)
    else:
        st.info("Sistemi başlatmak için 'Taramayı Başlat' butonuna tıklayın.")

# SEKME 2: OTOMATİK TAKİP
with tab2:
    st.markdown("### Arka Plan Çalışmaları")
    st.write("Sistem TR saati ile **03:00, 11:00 ve 19:00**'da otomatik tetiklenmektedir.")
    
    if os.path.exists("otomatik_log.txt"):
        with open("otomatik_log.txt", "r", encoding="utf-8") as f:
            loglar = f.readlines()
            for log in reversed(loglar[-15:]):
                st.code(log.strip())
    else:
        st.write("Henüz otomatik tarama saati gelmedi.")

# SEKME 3: BULUNAN ODALAR
with tab3:
    st.markdown("### Geçmiş Fırsatlar")
    if os.path.exists('bulunan_odalar_gecmisi.csv'):
        df_gecmis = pd.read_csv('bulunan_odalar_gecmisi.csv')
        st.dataframe(
            df_gecmis,
            column_config={"Rezervasyon": st.column_config.LinkColumn("Siteye Git")},
            hide_index=True,
            use_container_width=True
        )
    else:
        st.write("Veritabanında henüz fırsat bulunmuyor.")
