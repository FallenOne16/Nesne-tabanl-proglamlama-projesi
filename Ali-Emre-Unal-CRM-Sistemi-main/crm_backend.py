# --- İstenen Sınıflar (Musteri, Satis, DestekTalebi aynı kalacak) ---

class Musteri:
    def __init__(self, musteri_id, ad, telefon):
        self.musteri_id = musteri_id
        self.ad = ad
        self.telefon = telefon

    def musteri_ekle(self, musteri_sozlugu):
        musteri_sozlugu[self.musteri_id] = self
        return True, f"Müşteri '{self.ad}' sisteme eklendi."

class Satis:
    def __init__(self, satis_id, urun, fiyat, musteri):
        self.satis_id = satis_id
        self.urun = urun
        self.fiyat = fiyat
        self.musteri = musteri 

class DestekTalebi:
    def __init__(self, talep_id, aciklama, musteri):
        self.talep_id = talep_id
        self.aciklama = aciklama
        self.musteri = musteri
        self.durum = "Açık"


# --- Sistemi Yönetecek Ana Sınıf ---
class CRMYoneticisi:
    def __init__(self):
        self.musteriler = {}
        self.satislar = []
        self.destek_talepleri = []

        # ---------------------------------------------------------
        # SİSTEME ÖNCEDEN KAYITLI (VARSAYILAN) MÜŞTERİLER EKLENİYOR
        # ---------------------------------------------------------
        self.yeni_musteri_kaydi(1, "Ahmet Yılmaz", "0532 111 22 33")
        self.yeni_musteri_kaydi(2, "Ayşe Demir", "0555 444 55 66")
        self.yeni_musteri_kaydi(3, "Mehmet Kaya", "0505 777 88 99")

        self.destek_talebi_olustur(1001, 2, "Sisteme giriş yapamıyorum.")
        self.yeni_satis_yap(101, 1, "Premium Paket", 1500.0)
        self.yeni_satis_yap(102, 2, "Full Paket", 1000.0)
        self.yeni_satis_yap(103, 3, "VIP Paket", 1250.0)

        
        # İsterseniz varsayılan satış veya destek talebi de ekleyebilirsiniz:
        # self.yeni_satis_yap(101, 1, "Premium Paket", 1500.0)
        # self.destek_talebi_olustur(1001, 2, "Sisteme giriş yapamıyorum.")
        # ---------------------------------------------------------

    def yeni_musteri_kaydi(self, m_id, ad, telefon):
        if m_id in self.musteriler:
            return False, "Bu ID'ye sahip bir müşteri zaten var!"
        
        yeni_musteri = Musteri(m_id, ad, telefon)
        return yeni_musteri.musteri_ekle(self.musteriler)

    def yeni_satis_yap(self, satis_id, m_id, urun, fiyat):
        if m_id not in self.musteriler:
            return False, "Hata: Müşteri bulunamadı!"
        
        for s in self.satislar:
            if s.satis_id == satis_id:
                return False, "Hata: Bu Satış ID zaten kullanılmış!"

        musteri = self.musteriler[m_id]
        yeni_satis = Satis(satis_id, urun, fiyat, musteri)
        self.satislar.append(yeni_satis)
        return True, f"Başarılı: '{urun}' satışı kaydedildi."

    def destek_talebi_olustur(self, talep_id, m_id, aciklama):
        if m_id not in self.musteriler:
            return False, "Hata: Müşteri bulunamadı!"
            
        for t in self.destek_talepleri:
            if t.talep_id == talep_id:
                return False, "Hata: Bu Talep ID zaten kullanılmış!"

        musteri = self.musteriler[m_id]
        yeni_talep = DestekTalebi(talep_id, aciklama, musteri)
        self.destek_talepleri.append(yeni_talep)
        return True, "Başarılı: Destek talebi oluşturuldu."
