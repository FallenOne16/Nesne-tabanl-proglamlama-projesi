# 🚀 Executive Management Systems (Aurora & Crimson OS)

Bu depo, nesne yönelimli programlama (OOP) ve ilişkisel veritabanı (SQLite) mimarileri kullanılarak geliştirilmiş iki farklı kurumsal yönetim sistemini içermektedir. Projeler, son kullanıcı hatalarını (Failsafe/Validation) minimize edecek algoritmalarla ve PyQt6 kullanılarak modern, lüks bir arayüzle tasarlanmıştır.

**Geliştirici:** Mustafa Erdoğan

---

## 🌍 Proje 1: Aurora Enterprise | Global Travel OS
Gelişmiş bir seyahat ve rota planlama otomasyonudur. Lüks kurumsal taşımacılık operasyonlarını yönetmek için tasarlanmıştır.

### 🌟 Temel Özellikler
* **Dinamik Dashboard:** Aktif rotaları ve anlık finansal hasılatı salt okunur (read-only) modda anlık olarak raporlar.
* **Akıllı Rota Planlama:** Gidiş ve varış noktalarının aynı seçilmesini engelleyen mantıksal doğrulama.
* **Güvenli Veri Girişi:** Müşteri adına rakam, kişi sayısına ve gün sayısına harf girilmesini engelleyen `.isalpha()` ve `.isdigit()` tabanlı filtreleme.
* **Mükerrer Kayıt Engeli:** Aynı müşteri adına aktif bir plan varken ikinci bir planın açılmasını SQL seviyesinde engeller.
* **CRUD Operasyonları:** Veritabanındaki tüm planlar düzenlenebilir veya onay alınarak silinebilir.

**Veritabanı:** `aurora_enterprise.db`
**Tema:** Luxury Navy & Gold (Lacivert ve Altın)

---

## 🎟️ Proje 2: Crimson Event Planner | OS
Profesyonel gişe yönetimi ve etkinlik biletleme sistemidir. Festivaller, konserler ve özel etkinlikler için geliştirilmiş, yüksek güvenlikli bir kayıt aracıdır.

### 🌟 Temel Özellikler
* **Yaş Sınırı Doğrulaması:** Sisteme girilen yaş verisini analiz ederek 18 yaşından küçük katılımcılara bilet kesilmesini otomatik olarak reddeder.
* **Tür Bazlı Dinamik Fiyatlandırma:** Standart ve VIP biletler arasında otomatik tutar hesaplaması. VIP biletlerin veritabanı tablosunda özel renklendirme (Highlight) ile belirtilmesi.
* **Aksiyon Merkezi:** Emojilerden arındırılmış, tipografik olarak belirginleştirilmiş "DÜZENLE" ve "SİL" butonları ile tablo üzerinden doğrudan SQL UPDATE ve DELETE işlemleri.
* **Güçlü Hata Yakalama:** `try-except` blokları sayesinde geçersiz veri girişlerinde uygulamanın çökmesini (Crash) önleyen zırhlı mimari.

**Veritabanı:** `crimson_events.db`
**Tema:** Dark Crimson (Saf Siyah ve Kan Kırmızısı)

---

## 🛠️ Kullanılan Teknolojiler

* **Programlama Dili:** Python 3.x
* **Arayüz Geliştirme (GUI):** PyQt6
* **Veritabanı:** SQLite3
* **Veri Yapıları:** Sınıflar (Classes), Nesne Yönelimli Programlama (OOP), QTableWidget, QStackedWidget

---

## ⚙️ Kurulum ve Çalıştırma

Projeleri kendi yerel makinenizde çalıştırmak için sisteminizde Python ve PyQt6 kütüphanesinin kurulu olması gerekmektedir.

**1. Gerekli kütüphaneyi kurun:**
```bash
python -m pip install PyQt6