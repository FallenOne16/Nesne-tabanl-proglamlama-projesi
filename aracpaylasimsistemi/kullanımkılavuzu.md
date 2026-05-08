# 🚗 ÜNAL Araç Paylaşım Sistemi - Kullanım Kılavuzu

**Ali Emre Ünal tarafından yapılan PyQt6 tabanlı kurumsal araç yönetim arayüzü.**

## 1. Sisteme Giriş
* Sistem, Python yüklü bir bilgisayarda terminal (veya CMD) üzerinden aşağıdaki komut ile başlatılır:
  ```bash
  python arac_arayuz.py
  
Açılan ana ekranda (ÜNAL Paneli), sisteme kayıtlı mevcut araçlar ve geçmiş kiralama saatleri listelenmektedir.

## 2. Yeni Müşteri ve Araç Kaydı
Sol menüden "Müşteri Ekle" sekmesine tıklayarak sisteme yeni bir müşteri (ID, Ad Soyad, Ehliyet No) tanımlayabilirsiniz.

Yine sol menüden "Araç Girişi" sekmesine tıklayarak ÜNAL sistemine yeni bir araç (Marka, Model, Başlangıç KM) dâhil edebilirsiniz.

## 3. Araç Çıkış (Kiralama) ve Dönüş (İade) İşlemleri
Sol menüden "Çıkış / Dönüş" sekmesine tıklayarak kiralama işlemlerini yönetebilirsiniz:

Araç Çıkışı Yap: Kayıtlı bir Araç ID ve Müşteri ID girerek aracı müşteriye teslim edin. Sistem, işlemin yapıldığı anı Başlangıç Saati olarak otomatik kaydedecektir.

Araç Dönüşü Al: İade gelen aracın "Kiralama ID" numarasını ve göstergedeki "Güncel KM" bilgisini girin. Sistem aracı tekrar 'Müsait' duruma getirecek, kilometreyi güncelleyecek ve Bitiş Saatini sisteme işleyecektir.  