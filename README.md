# ✈️ Seyahat Planlama Uygulaması

Bu proje, Python ve PyQt5 kullanılarak geliştirilmiş, modüler yapıya sahip kapsamlı bir seyahat planlama ve bütçe yönetim sistemidir.

## 🎓 Proje Amacı
Bu uygulama **eğitim amaçlı** geliştirilmiş bir yazılım projesidir. Temel amacı; Nesne Yönelimli Programlama (OOP) prensipleri, modüler mimari tasarımı, veri kalıcılığı (JSON) ve modern grafik arayüz (GUI) geliştirme süreçlerini uygulamalı olarak göstermektir.

## ✨ Özellikler
*   **Seyahat Yönetimi:** Destinasyon, tarih aralığı, ulaşım türü ve bütçe bilgilerini içeren seyahatlerin oluşturulması ve takibi.
*   **Konaklama Takibi:** Otel veya farklı konaklama türleri için rezervasyon yönetimi, gecelik fiyat hesaplamaları ve otomatik bütçe düşümü.
*   **Rota ve Aktivite Planlama:** Seyahatlere özel rota noktaları ekleme ve maliyetli/maliyetsiz aktiviteler planlama.
*   **Bütçe Kontrolü:** Gerçek zamanlı bütçe kullanımı takibi, harcanan/kalan bütçe analizi ve bütçe aşım kontrolleri.
*   **Gelişmiş Raporlama:** Sistem genelinde bütçe dağılımı, aktivite yoğunluğu ve seyahat istatistiklerini içeren raporlar.
*   **Veri Kalıcılığı:** Tüm verilerin `seyahat_verileri.json` dosyasında saklanması ve uygulama açılışında otomatik yüklenmesi.
*   **Modern Arayüz:** PyQt5 ile tasarlanmış, "Warm Terracotta & Deep Navy" temalı, animasyonlu ve kullanıcı dostu grafik arayüz.

## 🛠️ Teknolojiler
*   **Dil:** Python 3.x
*   **GUI Çerçevesi:** PyQt5
*   **Veri Formatı:** JSON
*   **Mühendislik:** OOP (Encapsulation, Enums, Type Hinting)

## 📁 Proje Yapısı
*   `seyahat.py`: Temel veri modelleri (Seyahat, Konaklama, Plan) ve iş mantığı kuralları.
*   `seyahat_sistemi.py`: Veri yönetimi, CRUD operasyonları, JSON işlemleri ve raporlama motoru.
*   `gui.py`: Modern PyQt5 arayüz bileşenleri, animasyonlar ve sayfa yönetimi.

## 🚀 Kurulum ve Çalıştırma

1.  **Bağımlılıkları Yükleyin:**
    Uygulama için PyQt5 kütüphanesi gereklidir. Terminal veya komut istemine aşağıdaki komutu yazarak yükleyebilirsiniz:
    ```bash
    pip install PyQt5
    ```

2.  **Uygulamayı Başlatın:**
    Ana dizinde bulunan `gui.py` dosyasını çalıştırın:
    ```bash
    python gui.py
    ```

## 📝 Kullanım Notları
*   Uygulama ilk açıldığında örnek verilerle (Seed Data) birlikte gelir.
*   Yaptığınız değişikliklerin kalıcı olması için sağ alttaki **Kaydet (💾)** butonunu kullanmayı unutmayın.
*   Raporlar sekmesinden bütçe kullanım oranlarınızı görsel grafikler üzerinden takip edebilirsiniz.

---
*Bu proje bir eğitim materyali olup, geliştirme süreçlerini pekiştirmek amacıyla tasarlanmıştır.*