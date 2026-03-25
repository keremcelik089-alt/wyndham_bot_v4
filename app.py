import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Wyndham Puan Avcısı", layout="wide", page_icon="🏖️")

st.title("🏖️ Wyndham 'Free Night' Kontrol Paneli")
st.markdown("Arka plandaki robotumuz **her 12 saatte bir** tüm otelleri tarayıp sonuçları buraya kaydeder. Uygulama açıldığı an en güncel sonuçları anında görürsün!")

# --- SEKMELER OLUŞTURALIM ---
tab1, tab2 = st.tabs(["📊 Son Tarama Durumu (Tüm Liste)", "🎉 SADECE BOŞ ODALAR (Geçmiş)"])

# SEKME 1: SON TARAMA SONUÇLARI
with tab1:
    if os.path.exists('son_durum.csv'):
        df = pd.read_csv('son_durum.csv')
        son_zaman = df['Tarama Zamanı'].iloc[0]
        
        st.success(f"**Son Otomatik Tarama Zamanı:** {son_zaman} (Türkiye Saati)")
        
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
        st.warning("Henüz otomatik tarama yapılmamış. Arka plan robotu 12 saatlik döngüsünü tamamladığında veriler buraya düşecektir.")

# SEKME 2: BOŞ ODA GEÇMİŞİ (Sadece yeşil tikliler)
with tab2:
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
