# Hastane Randevu ve Poliklinik Yönetim Sistemi

Bu proje, hastane poliklinik sekreterliği için geliştirilmiş nesne yönelimli (Object-Oriented) bir **Randevu Yönetim Sistemi**'dir. Hem güçlü bir arka plan (SQLite ve Python OOP), hem de kullanıcı dostu ve modern bir PyQt5 grafiksel arayüz (GUI) ile tasarlanmıştır.

## 📌 Proje Geliştirme Adımları ve Analizi

Proje, "Proje Geliştirme Adımları" yönergelerine uygun olarak tasarlanmış ve kodlanmıştır:

### 1. Sistem İşlevleri ve Senaryolar
- **Temel İşlevler:** Hasta kaydı oluşturma, Doktor kaydı ve uygunluk saatleri tanımlama, Randevu alma (uygunluk kontrolüyle çakışma önleme), Günlük randevuları listeleme ve randevu iptal etme.
- **Kullanıcı Türü:** Arayüz, sistemi yönetecek olan **Poliklinik Sekreteri** rolü için tasarlanmıştır.
- **Sistem Senaryosu:** 
  1. Sekreter hasta bilgilerini ve doktor bilgilerini sisteme girer.
  2. Hasta için randevu talep edildiğinde sistem doktorun müsaitliğini ve çalışma saatlerini kontrol eder.
  3. Uygunluk varsa randevu oluşturulur, sekreter bu randevuyu anlık tablo üzerinden ve günlük bültende görüntüleyebilir veya iptal edebilir.

### 2. Sınıf (Class) Yapısı
Proje, **Nesne Yönelimli Programlama (OOP)** mimarisiyle inşa edilmiş olup, en az 3 ana sınıf şartını karşılayan 4 sınıftan oluşur:

1. `DatabaseManager`: Tüm SQLite veritabanı (CRUD) işlemlerini yürüten temel sınıftır.
2. `Hasta`: Hastaların kimlik ve iletişim bilgilerini tutar.
   - *Özellikler:* `hasta_id`, `ad`, `tc`, `telefon`
   - *Metodlar:* `randevu_al(...)` -> Kapsülleme yapılarak doğrudan randevu sınıfını tetikler.
3. `Doktor`: Doktorların uzmanlık ve çalışma saati bilgilerini tutar.
   - *Özellikler:* `doktor_id`, `ad`, `uzmanlik`, `uygun_saatler` (Liste formatında)
   - *Metodlar:* `uygunluk_kontrol(...)` -> Çakışmaları ve çalışma saatlerini kontrol eden ana metot.
4. `Randevu`: Hasta ve Doktor nesnelerini birbirine bağlayan işlem sınıfı.
   - *Özellikler:* `randevu_id`, `tarih`, `saat`, `doktor` (Doktor objesi), `hasta` (Hasta objesi)
   - *Metodlar:* `randevu_olustur(...)` (Static Method), `randevu_iptal(...)`

### 3. Kullanılan Veri Yapıları
- **Liste (List):** `Doktor` sınıfı içindeki "uygun saatler" özelliği bir Python Listesi olarak tutulur. Ayrıca, veritabanından veri okunup objelere dönüştürülürken Nesne Listeleri (Object Lists) döndürülür (`get_all_hastalar()`, `get_all_doktorlar()` metodları).
- **Sözlük (Dictionary):** Arayüz kısmında sayfa ve sekmeler arası yönlendirmeler için index map olarak kullanılmıştır (`idx = {"Dashboard": 0, "Doktor Yönetimi": 1 ...}`).
- **SQLite:** Listeler ve Sözlüklerden bir adım daha ileri gidilerek kalıcı veri saklamak için yerel SQLite yapısı sisteme tam entegre edilmiştir.

### 4. Kullanıcı Arayüzü (GUI)
- Konsol tabanlı yerine çok daha profesyonel bir yaklaşım tercih edilerek **PyQt5** tabanlı grafiksel bir kullanıcı arayüzü kodlanmıştır.
- Dashboard ekranı, metrik kartları ve yumuşatılmış bileşen kenarları ile modern bir "Admin Paneli" hissiyatı sunar.

---

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
- **Python 3.8+**
- **PyQt5** kütüphanesi

```bash
# Gerekli kütüphaneyi yükleyin
pip install PyQt5
```

### Sistemi Başlatma
Projenin ana arayüzünü çalıştırmak için terminalden arayüz dosyasını başlatın:

```bash
python hastane_randevu_gui.py
```

### Test Senaryosu (Manuel Test Adımları)
1. **Arayüz Açılışı:** Programı başlattığınızda sistemde kayıtlı doktor ve hasta yoksa, `Dashboard` tüm metrikleri "0" olarak gösterecektir. Ancak ilk açılışta `_add_demo_data` metodu test verilerini sizin yerinize otomatik ekler.
2. **Doktor Ekleme:** Sol menüden "Doktor Yönetimi"ne gidin. *Ahmet Yılmaz*, Uzmanlık: *Göz*, Saatler: *09:00, 10:00* şeklinde doktor ekleyin. Sayısal veri (ad kısmına rakam) girmeyi deneyin, hata mesajını gözlemleyin.
3. **Hasta Ekleme:** "Hasta Yönetimi"ne gidin. Yeni bir hasta ekleyin (11 haneli geçerli TC girilmelidir).
4. **Randevu Oluşturma:** "Randevu Oluştur" sekmesine gidin. Yukarıda eklediğiniz hastayı ve doktoru seçin. Doktorun kendi saatleri otomatik dropdown (açılır liste) menüsüne gelecektir. Aynı doktora aynı saate arka arkaya 2 kez randevu oluşturmayı deneyin, 2. denemede **"Doktor bu tarih ve saatte uygun değil veya doludur"** uyarısı verecektir (Bu özellik `Doktor` sınıfındaki `uygunluk_kontrol` metodu ile tetiklenmektedir).
5. **Günlük İptaller:** "Günlük Randevular" menüsüne gelin. Randevunuzu listede göreceksiniz. Buradan iptal et butonuna basarak randevuyu sistemden silebilirsiniz.
