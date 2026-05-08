# 🏢 ÜNAL CRM Sistemi - Kullanım Kılavuzu

**Ali Emre Ünal tarafından yapılan PyQt6 tabanlı kurumsal müşteri yönetim arayüzü.**

## 1. Sisteme Giriş
* Sistem, Python yüklü bir bilgisayarda terminal (veya CMD) üzerinden aşağıdaki komut ile başlatılır:
  ```bash
  python crm_arayuz.py

Açılan ana ekranda (ÜNAL CRM Paneli), sisteme kayıtlı mevcut müşteriler, son satışlar ve destek talepleri listelenmektedir.

## 2. Yeni Müşteri Kaydı
Sol menüden "Veri Girişi" sekmesine tıklayarak sisteme yeni bir müşteri (ID, Ad Soyad, Telefon) tanımlayabilirsiniz.

(Not: Sistemde satış veya destek işlemi yapabilmek için öncelikle müşteri kaydının bulunması zorunludur.)

## 3. Satış (Ürün Çıkışı) ve Destek Talebi İşlemleri
Yine sol menüdeki "Veri Girişi" sekmesi üzerinden müşteri işlemlerini yönetebilirsiniz:

Satışı Kaydet: Kayıtlı bir Müşteri ID girerek satılan ürünün adını ve fiyatını kaydedin. Sistem, bu satışı anında panele yansıtacaktır.

Talep Aç: Kayıtlı bir müşterinin şikayet veya isteklerini (Açıklama) girerek yeni bir destek talebi oluşturun. Sistem bu talepleri otomatik olarak Açık statüsünde sisteme işleyecektir.