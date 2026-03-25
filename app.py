import streamlit as st
import pandas as pd
import os
from otomasyon import run_scan

st.set_page_config(page_title="Wyndham Puan Avcısı", layout="wide", page_icon="🏖️")

st.title("🏖️ Wyndham 'Free Night' Kontrol Paneli")
st.markdown("İstediğin an güncel durumu kontrol etmek için taramayı manuel olarak başlatabilirsin. Otellerin güncel müsaitlik durumunu canlı olarak izle!")

# --- SEKMELER OLUŞTURALIM ---
tab1, tab2, tab3 = st.tabs(["🚀 Canlı Tarama Başlat", "📊 Son Tarama Durumu", "🎉 BOŞ ODA GEÇMİŞİ"])

# SEKME 1: CANLI TARAMA YAPMA EKRANI
with tab1:
    st.info("💡 Toplam 7 otel ve 15 farklı tarih kombinasyonu taranacaktır (Toplam 105 kontrol). Bu işlem sitenin hızına bağlı olarak **yaklaşık 8-10 dakika** sürebilir. Tarama sırasında lütfen telefonunda/bilgisayarında **bu sekmeyi kapatma**.")
    
    if st.button("🔍 Taramayı Şimdi Başlat", type="primary"):
        st.markdown("### ⚙️ Tarama İlerlemesi")
        progress_bar = st.progress(0)
        status_text = st.empty()
        log_container = st.empty()
        
        # otomasyon.py içindeki fonksiyonu çalıştır ve arayüz elemanlarını ona gönder
        with st.spinner("Tarayıcı hazırlanıyor, işlemler başlıyor..."):
            run_scan(progress_bar, status_text, log_container)
            
        status_text.success("🎉 Tarama başarıyla tamamlandı! Sonuçları yandaki sekmelerden inceleyebilirsin.")
        time.sleep(3) # Kullanıcı mesajı görsün diye 3 saniye bekle
        st.rerun() # Diğer sekmelerin güncellenmesi için sayfayı yenile

# SEKME 2: SON TARAMA SONUÇLARI
with tab2:
    if os.path.exists('son_durum.csv'):
        df = pd.read_csv('son_durum.csv')
        son_zaman = df['Tarama Zamanı'].iloc[0]
        
        st.success(f"**Son Tarama Zamanı:** {son_zaman} (Türkiye Saati)")
        
        # Kutuları oluştur
        oteller = df['Otel Adı'].unique()
        for otel in oteller:
            with st.expander(f"🏨 {otel}", expanded=True):
                otel_df = df[df['Otel Adı'] == otel].drop(columns=['Otel Adı', 'Tarama Zamanı'])
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
    st.info("Burası sadece oda bulunduğu zaman dolar. Hangi otelin ne zaman boş oda açtığını buradan takip edebilirsin.")
    if os.path.exists('bulunan_odalar_gecmisi.csv'):
        df_gecmis = pd.read_csv('bulunan_odalar_gecmisi.csv')
        st.dataframe(
            df_gecmis,
            column_config={"Rezervasyon": st.column_config.LinkColumn("Siteye Git")},
            hide_index=True,
            use_container_width=True
        )
        st.balloons()
    else:
        st.write("Şu ana kadar yapılan taramalarda henüz boş oda yakalanamadı.")
