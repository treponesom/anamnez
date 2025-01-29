# Anamnez Eğitim Asistanı

Bu proje, tıp öğrencileri ve stajyerlerin anamnez alma becerilerini geliştirmek için tasarlanmış yapay zeka destekli bir eğitim aracıdır.

## Özellikler

- 7 farklı üroloji alt branşında toplam 28 hasta senaryosu
- Yapay zeka destekli gerçekçi hasta yanıtları
- Branşa göre hasta seçimi
- Görüşme kayıtları
- Kullanıcı dostu arayüz

## Kurulum

1. Python 3.8 veya daha yüksek bir sürüm yükleyin
2. Gerekli paketleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
3. Google API anahtarınızı `.env` dosyasına ekleyin:
   ```
   GOOGLE_API_KEY=sizin_api_anahtarınız
   ```
4. Uygulamayı başlatın:
   ```bash
   streamlit run app.py
   ```

## Kullanım

1. Branş seçin (isteğe bağlı)
2. "Yeni Hasta" butonu ile yeni bir hasta senaryosu başlatın
3. Hastaya sorular sorun ve yanıtları alın
4. Görüşmeyi kaydetmek için "Görüşmeyi Kaydet" butonunu kullanın

## Katkıda Bulunma

1. Bu repoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin yeni-ozellik`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın. 