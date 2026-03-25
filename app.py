import streamlit as st
import pandas as pd
import os
import time
from otomasyon import run_scan

st.set_page_config(page_title="Wyndham Puan Avcısı", layout="wide", page_icon="🏖️")

st.title("🏖️ Wyndham 'Free Night' Kontrol Paneli")
st.markdown("İstediğin an güncel durumu kontrol etmek için taramayı manuel olarak başlatabilirsin. Otellerin güncel müsaitlik durumunu canlı olarak izle!")

# --- SEKMELER ---
tab1, tab2, tab3 = st.tabs(["🚀 Canlı Tarama Başlat", "📊 Son Tarama Durumu", "🎉 BOŞ ODA GEÇMİŞİ"])

# SEKME 1: CANLI TARAMA
with tab1:
    st.info("💡 **Bilgi:** Sistem şu an **9 otel** ve **30 farklı tarih** varyasyonunu kontrol edecek. Toplam **270** sorgu yapılacaktır.\n\n"
            "⚠️ Anti-Bot engeline takılmamak için aralara bekleme süreleri eklenmiştir. Bu yüzden taramanın tamamlanması yaklaşık **20 - 25 dakika** sürebilir. Tarama sırasında lütfen **bu sekmeyi kapatma**.")
    
    if st.button("🔍 270 Kombinasyonluk Taramayı Şimdi Başlat", type="primary"):
        st.markdown("### ⚙️ Canlı Tarama İlerlemesi")
        
        # İlerleme barı, anlık durum yazısı ve terminal benzeri log alanı oluşturuluyor
        progress_bar = st.progress(0)
        status_text = st.empty()
        log_container = st.empty()
        
        with st.spinner("Tarayıcı hazırlanıyor, işlemler başlıyor..."):
            # Otomasyondaki fonksiyonu çağırıyoruz
            run_scan(progress_bar, status_text, log_container)
            
        status_text.success("🎉 Tarama başarıyla tamamlandı! Sonuçları yandaki sekmelerden inceleyebilirsin.")
        time.sleep(3)
        st.rerun()

# SEKME 2: SON TARAMA SONUÇLARI
with tab2:
    if os.path.exists('son_durum.csv'):
        df = pd.read_csv('son_durum.csv')
        son_zaman = df['Tarama Zamanı'].iloc[0]
        
        st.success(f"**Son Tarama Zamanı:** {son_zaman} (Türkiye Saati)")
        
        # Sadece Boş Olanları Filtrele Seçeneği
        sadece_bos = st.checkbox("Sadece 'Boş Oda Bulunan' Tarihleri Göster")
        
        oteller = df['Otel Adı'].unique()
        for otel in oteller:
            otel_df = df[df['Otel Adı'] == otel].drop(columns=['Otel Adı', 'Tarama Zamanı'])
            
            if sadece_bos:
                otel_df = otel_df[otel_df['Durum'].str.contains("✅")]
                
            # Eğer filtreleme sonucu otelde gösterecek bir şey kaldıysa tabloyu çiz
            if not otel_df.empty:
                with st.expander(f"🏨 {otel}", expanded=True):
                    st.dataframe(
                        otel_df, 
                        column_config={"Rezervasyon": st.column_config.LinkColumn("Siteye Git")},
                        hide_index=True,
                        use_container_width=True
                    )
    else:
        st.warning("Henüz hiç tarama yapılmamış. 'Canlı Tarama Başlat' sekmesinden işlemi başlatabilirsin.")

# SEKME 3: BOŞ ODA GEÇMİŞİ (Sadece yeşil tikliler)
with tab3:
    st.info("Burası senin hazine sandığın! Geçmiş taramalarda yakalanan boş odalar kalıcı olarak buraya kaydedilir.")
    if os.path.exists('bulunan_odalar_gecmisi.csv'):
        df_gecmis = pd.read_csv('bulunan_odalar_gecmisi.csv')
        st.dataframe(
            df_gecmis,
            column_config={"Rezervasyon": st.column_config.LinkColumn("Siteye Git")},
            hide_index=True,
            use_container_width=True
        )
        # Kutlama animasyonu
        st.balloons()
    else:
        st.write("Şu ana kadar yapılan taramalarda henüz boş oda yakalanamadı.")
