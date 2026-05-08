import datetime

# --- İstenen Sınıflar ---
class Arac:
    def __init__(self, arac_id, marka, model, kilometre):
        self.arac_id = arac_id
        self.marka = marka
        self.model = model
        self.kilometre = kilometre
        self.musait_mi = True

    def arac_durumu_guncelle(self, durum):
        self.musait_mi = durum

    def kilometre_guncelle(self, yeni_km):
        if yeni_km > self.kilometre:
            self.kilometre = yeni_km

class Kullanici:
    def __init__(self, kullanici_id, ad, ehliyet_no):
        self.kullanici_id = kullanici_id
        self.ad = ad
        self.ehliyet_no = ehliyet_no
        self.gecmis = []

    def kiralama_gecmisi(self):
        if not self.gecmis:
            return "Geçmiş kiralama bulunmuyor."
        return "\n".join([k.kiralama_bilgisi() for k in self.gecmis])

class Kiralama:
    def __init__(self, kiralama_id, arac, kullanici):
        self.kiralama_id = kiralama_id
        self.arac = arac
        self.kullanici = kullanici
        self.baslangic_saati = None
        self.bitis_saati = None      

    def kiralama_baslat(self):
        self.arac.arac_durumu_guncelle(False)
        self.baslangic_saati = datetime.datetime.now()

    def kiralama_bitir(self, guncel_km):
        self.arac.arac_durumu_guncelle(True)
        self.arac.kilometre_guncelle(guncel_km)
        self.bitis_saati = datetime.datetime.now()
        self.kullanici.gecmis.append(self)

    def kiralama_bilgisi(self):
        bas = self.baslangic_saati.strftime("%d.%m.%Y %H:%M") if self.baslangic_saati else "-"
        bit = self.bitis_saati.strftime("%d.%m.%Y %H:%M") if self.bitis_saati else "Devam Ediyor"
        return f"ID: {self.kiralama_id} | Araç: {self.arac.marka} | Müşteri: {self.kullanici.ad} | Başlangıç: {bas} | Bitiş: {bit}"

# --- Sistem Yöneticisi ---
class SistemYoneticisi:
    def __init__(self):
        self.araclar = {}
        self.kullanicilar = {}
        self.kiralamalar = []
        self.kiralama_sayaci = 1000
        
        # Sınıf başlatıldığında dümenden verileri yükle
        self._doldur_sahte_veriler()

    def _doldur_sahte_veriler(self):
        # 1. Rastgele Araçlar
        sahte_araclar = [
            (1, "Peugeot", "308 1.6 BlueHDi", 120000),
            (2, "Renault", "Megane 1.5 dCi", 85000),
            (3, "Fiat", "Egea 1.4 Fire", 42000),
            (4, "Volkswagen", "Golf 1.5 TSI", 30000),
            (5, "Toyota", "Corolla 1.8 Hybrid", 15000),
            (6, "Honda", "Civic 1.5 VTEC", 54000)
        ]
        for a in sahte_araclar:
            self.yeni_arac_ekle(a[0], a[1], a[2], a[3])

        # 2. Rastgele Müşteriler
        sahte_kullanicilar = [
            (101, "Ali Emre Ünal", "TR-EHL-1234"),
            (102, "Ayşe Yılmaz", "TR-EHL-5566"),
            (103, "Mehmet Kaya", "TR-EHL-7788"),
            (104, "Zeynep Demir", "TR-EHL-9900"),
            (105, "Caner Şahin", "TR-EHL-1122")
        ]
        for k in sahte_kullanicilar:
            self.yeni_kullanici_ekle(k[0], k[1], k[2])

        # 3. Dümenden Kiralama Senaryoları (Geçmiş tarihleri simüle etmek için)
        simdi = datetime.datetime.now()

        # Senaryo 1: Tamamlanmış Kiralama (Ayşe, Megane'ı kiralayıp iade etmiş)
        self.arac_cikisi_yap(2, 102)
        k1 = self.kiralamalar[-1]
        k1.baslangic_saati = simdi - datetime.timedelta(days=3, hours=4) # 3 gün önce kiralanmış
        self.arac_donusu_al(k1.kiralama_id, 85600) # İade alındı, KM arttı
        k1.bitis_saati = simdi - datetime.timedelta(days=1, hours=2) # 1 gün önce teslim edilmiş

        # Senaryo 2: Tamamlanmış Kiralama (Caner, Golf'ü kiralayıp iade etmiş)
        self.arac_cikisi_yap(4, 105)
        k2 = self.kiralamalar[-1]
        k2.baslangic_saati = simdi - datetime.timedelta(days=5, hours=10)
        self.arac_donusu_al(k2.kiralama_id, 30350)
        k2.bitis_saati = simdi - datetime.timedelta(days=4)

        # Senaryo 3: Aktif Kiralama (Mehmet, Egea'yı kiralamış ve hala onda)
        self.arac_cikisi_yap(3, 103)
        k3 = self.kiralamalar[-1]
        k3.baslangic_saati = simdi - datetime.timedelta(hours=14) # 14 saattir onda

        # Senaryo 4: Aktif Kiralama (Zeynep, Corolla'yı kiralamış ve hala onda)
        self.arac_cikisi_yap(5, 104)
        k4 = self.kiralamalar[-1]
        k4.baslangic_saati = simdi - datetime.timedelta(days=1, hours=3) # 1 gündür onda

    def yeni_arac_ekle(self, arac_id, marka, model, km):
        if arac_id in self.araclar:
            return False, "Bu ID'ye sahip bir araç zaten var!"
        self.araclar[arac_id] = Arac(arac_id, marka, model, km)
        return True, f"{marka} {model} Sisteme eklendi."

    def yeni_kullanici_ekle(self, k_id, ad, ehliyet_no):
        if k_id in self.kullanicilar:
            return False, "Bu ID'ye sahip bir müşteri zaten var!"
        self.kullanicilar[k_id] = Kullanici(k_id, ad, ehliyet_no)
        return True, f"Müşteri {ad} sisteme kaydedildi."

    def arac_cikisi_yap(self, a_id, k_id):
        if a_id in self.araclar and k_id in self.kullanicilar:
            arac = self.araclar[a_id]
            kul = self.kullanicilar[k_id]
            if arac.musait_mi:
                yeni = Kiralama(self.kiralama_sayaci, arac, kul)
                yeni.kiralama_baslat()
                self.kiralamalar.append(yeni)
                self.kiralama_sayaci += 1
                return True, f"Başarılı: {arac.marka} aracı {kul.ad} müşterisine verildi. Başlangıç saati işlendi."
            return False, "Hata: Araç şu anda başka müşteride."
        return False, "Hata: Geçersiz Araç veya Müşteri ID."

    def arac_donusu_al(self, kiralama_id, guncel_km):
        for k in self.kiralamalar:
            if k.kiralama_id == kiralama_id and k.bitis_saati is None:
                k.kiralama_bitir(guncel_km)
                return True, "Araç iade alındı. Bitiş saati ve yeni KM sisteme işlendi."
        return False, "Hata: Aktif kiralama bulunamadı."
