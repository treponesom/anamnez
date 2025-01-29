import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import random
from datetime import datetime
import logging
import sys

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('anamnez_asistan')

# Çevre değişkenlerini yükle
load_dotenv()
logger.info("Çevre değişkenleri yüklendi")

# Gemini API'yi yapılandır
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    logger.info("Gemini API başarıyla yapılandırıldı")
except Exception as e:
    logger.error(f"Gemini API yapılandırma hatası: {str(e)}")

# Streamlit konfigürasyonu
st.set_page_config(
    page_title="Anamnez Eğitim Asistanı",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)
logger.info("Streamlit konfigürasyonu tamamlandı")

def yukle_hasta_senaryolari():
    """Hasta senaryolarını JSON dosyasından yükler"""
    try:
        with open('hasta_senaryolari.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info("Hasta senaryoları başarıyla yüklendi")
            return data["senaryolar"]
    except FileNotFoundError:
        logger.error("Hasta senaryoları dosyası bulunamadı!")
        st.error("Hasta senaryoları dosyası bulunamadı!")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"JSON dosyası okuma hatası: {str(e)}")
        st.error("Hasta senaryoları dosyası okunamadı!")
        return []

def kaydet_gorusme(messages):
    """Görüşmeyi JSON formatında kaydeder"""
    try:
        if not os.path.exists('gorusmeler'):
            os.makedirs('gorusmeler')
            logger.info("Görüşmeler klasörü oluşturuldu")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dosya_adi = f"gorusmeler/gorusme_{timestamp}.json"
        
        gorusme_kaydi = {
            "tarih": timestamp,
            "senaryo": st.session_state.get("current_scenario", {}),
            "mesajlar": messages
        }
        
        with open(dosya_adi, 'w', encoding='utf-8') as f:
            json.dump(gorusme_kaydi, f, ensure_ascii=False, indent=4)
            logger.info(f"Görüşme başarıyla kaydedildi: {dosya_adi}")
    except Exception as e:
        logger.error(f"Görüşme kaydetme hatası: {str(e)}")
        st.error("Görüşme kaydedilemedi!")

def yeni_hasta_sec(secili_brans=None):
    """Seçili branştan rastgele bir hasta senaryosu seçer"""
    try:
        senaryolar = yukle_hasta_senaryolari()
        if not senaryolar:
            logger.warning("Senaryo bulunamadı, varsayılan senaryo kullanılıyor")
            return {
                "yaş": 45,
                "cinsiyet": "Erkek",
                "branş": "Genel",
                "şikayet": "Karın ağrısı",
                "detaylar": "Varsayılan senaryo yüklenemedi.",
                "tanı": "Bilinmiyor"
            }
        
        if secili_brans:
            brans_senaryolari = [s for s in senaryolar if s["branş"] == secili_brans]
            if brans_senaryolari:
                senaryo = random.choice(brans_senaryolari)
                logger.info(f"Seçili branştan ({secili_brans}) yeni hasta senaryosu seçildi")
            else:
                senaryo = random.choice(senaryolar)
                logger.warning(f"Seçili branşta ({secili_brans}) senaryo bulunamadı, rastgele senaryo seçildi")
        else:
            senaryo = random.choice(senaryolar)
            logger.info("Rastgele yeni hasta senaryosu seçildi")
        
        st.session_state.current_scenario = senaryo
        return senaryo
    except Exception as e:
        logger.error(f"Hasta senaryo seçme hatası: {str(e)}")
        st.error("Hasta senaryosu seçilemedi!")
        return None

def initialize_session_state():
    if "messages" not in st.session_state:
        senaryo = yeni_hasta_sec()
        st.session_state.messages = [
            {"role": "system", "content": f"""Sen bir sanal hastasın. Bir tıp öğrencisinin anamnez alma pratiği yapması için onunla etkileşime geçeceksin. 
             Verdiğin cevaplar tutarlı olmalı ve gerçekçi bir hasta görüşmesini yansıtmalı. 
             Başlangıçta sadece temel şikayetini belirt, detayları ancak sorulduğunda paylaş.
             
             Hasta Bilgileri:
             Yaş: {senaryo['yaş']}
             Cinsiyet: {senaryo['cinsiyet']}
             Branş: {senaryo['branş']}
             Ana Şikayet: {senaryo['şikayet']}
             
             Detaylar:
             {senaryo['detaylar']}
             
             Tanı: {senaryo['tanı']} (Bu tanıyı direkt söyleme, sadece uygun semptomları ver)"""}
        ]

def get_assistant_response(messages):
    try:
        conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(conversation_history)
        logger.info("AI yanıtı başarıyla alındı")
        return response.text
    except Exception as e:
        error_msg = f"Gemini API Hatası: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
        return "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin."

def main():
    logger.info("Uygulama başlatıldı")
    st.title("Anamnez Eğitim Asistanı")
    
    # Sol sütun - Ana sohbet arayüzü
    col1, col2 = st.columns([3, 1])
    
    with col1:
        try:
            initialize_session_state()
            
            st.write("Bu uygulama, anamnez alma becerilerinizi geliştirmenize yardımcı olacak bir sanal hasta simülasyonudur. "
                    "Hastaya sorular sorarak bilgi toplayın ve tanıya ulaşmaya çalışın.")
            
            # Mesajları göster
            for message in st.session_state.messages[1:]:  # system mesajını gösterme
                if message["role"] == "assistant":
                    st.chat_message("assistant").write(message["content"])
                else:
                    st.chat_message("user").write(message["content"])
            
            # Kullanıcı girişi
            if prompt := st.chat_input("Hastaya sormak istediğiniz soruyu yazın"):
                logger.info("Yeni kullanıcı sorusu alındı")
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.chat_message("user").write(prompt)
                
                # Asistan yanıtı
                response = get_assistant_response(st.session_state.messages)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.chat_message("assistant").write(response)
        except Exception as e:
            logger.error(f"Ana uygulama hatası: {str(e)}")
            st.error("Beklenmeyen bir hata oluştu!")
    
    # Sağ sütun - Kontroller ve bilgiler
    with col2:
        try:
            st.subheader("Kontroller")
            
            # Branş seçimi
            branslar = [
                "Pediatrik Üroloji",
                "Androloji",
                "Üroonkoloji",
                "Transplantasyon",
                "Endoüroloji",
                "Kadın Ürolojisi",
                "Nöroüroloji"
            ]
            secili_brans = st.selectbox("Branş Seçin", ["Tümü"] + branslar)
            
            if st.button("Yeni Hasta"):
                logger.info("Yeni hasta talebi alındı")
                # Mevcut görüşmeyi kaydet
                if len(st.session_state.messages) > 1:
                    kaydet_gorusme(st.session_state.messages)
                
                # Yeni hasta senaryosu başlat
                senaryo = yeni_hasta_sec(secili_brans if secili_brans != "Tümü" else None)
                st.session_state.messages = [st.session_state.messages[0]]  # Sadece system mesajını tut
                st.rerun()
            
            if st.button("Görüşmeyi Kaydet"):
                logger.info("Görüşme kaydetme talebi alındı")
                kaydet_gorusme(st.session_state.messages)
                st.success("Görüşme kaydedildi!")
            
            # Mevcut hasta bilgileri
            st.subheader("Mevcut Hasta")
            senaryo = st.session_state.get("current_scenario", {})
            st.write(f"Yaş: {senaryo.get('yaş')}")
            st.write(f"Cinsiyet: {senaryo.get('cinsiyet')}")
            st.write(f"Branş: {senaryo.get('branş')}")
            st.write(f"Ana Şikayet: {senaryo.get('şikayet')}")
        except Exception as e:
            logger.error(f"Kontrol paneli hatası: {str(e)}")
            st.error("Kontrol panelinde bir hata oluştu!")

if __name__ == "__main__":
    try:
        main()
        logger.info("Uygulama başarıyla çalışıyor")
    except Exception as e:
        logger.critical(f"Kritik uygulama hatası: {str(e)}")
        st.error("Uygulama başlatılamadı!") 
