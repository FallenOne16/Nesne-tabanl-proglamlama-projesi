import sqlite3
from datetime import date

# ── 1. ÜRÜN SINIFI ──
class Urun:
    def __init__(self, urun_id, ad, stok, fiyat):
        self.urun_id = urun_id
        self.ad = ad
        self.stok = stok
        self.fiyat = fiyat

    # İstenen Metot: Stok Artır
    def stok_arttir(self, miktar, db_manager):
        self.stok += miktar
        db_manager.guncelle_stok(self.urun_id, self.stok)
        return True, f"Mal girişi başarılı. '{self.ad}' için yeni stok: {self.stok}"

    # İstenen Metot: Stok Azalt
    def stok_azalt(self, miktar, db_manager):
        if self.stok >= miktar:
            self.stok -= miktar
            db_manager.guncelle_stok(self.urun_id, self.stok)
            return True, f"Stoktan {miktar} adet düşüldü. Kalan: {self.stok}"
        return False, f"Yetersiz stok! Mevcut stok: {self.stok}"

# ── 2. SİPARİŞ SINIFI ──
class Siparis:
    def __init__(self, siparis_id, urun_id, adet, tarih=None):
        self.siparis_id = siparis_id
        self.urun_id = urun_id
        self.adet = adet
        self.tarih = tarih or str(date.today())

    # İstenen Metot: Sipariş Oluştur (Stoğu kontrol eder ve düşer)
    def siparis_olustur(self, db_manager):
        urunler = db_manager.get_urunler()
        ilgili_urun = next((u for u in urunler if u.urun_id == self.urun_id), None)
        
        if not ilgili_urun:
            return False, "Hata: Ürün veritabanında bulunamadı!"
            
        # Sipariş oluşturulurken ürün sınıfındaki stok azaltma metodu çağrılır
        stok_durumu, mesaj = ilgili_urun.stok_azalt(self.adet, db_manager)
        
        if stok_durumu:
            db_manager.siparis_kaydet(self)
            return True, f"Sipariş başarıyla oluşturuldu!\n{mesaj}"
        else:
            return False, f"Sipariş başarısız: {mesaj}"

# ── VERİTABANI YÖNETİCİSİ ──
class DepoDB:
    def __init__(self, db_adi="depo.db"):
        self.conn = sqlite3.connect(db_adi)
        self.cursor = self.conn.cursor()
        self._tablolari_kur()

    def _tablolari_kur(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS urunler (id INTEGER PRIMARY KEY, ad TEXT, stok INTEGER, fiyat REAL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS siparisler (id INTEGER PRIMARY KEY AUTOINCREMENT, urun_id INTEGER, adet INTEGER, tarih TEXT)''')
        self.conn.commit()

    def urun_ekle(self, urun):
        try:
            self.cursor.execute("INSERT INTO urunler (id, ad, stok, fiyat) VALUES (?, ?, ?, ?)", (urun.urun_id, urun.ad, urun.stok, urun.fiyat))
            self.conn.commit()
            return True, f"'{urun.ad}' depoya eklendi."
        except sqlite3.IntegrityError:
            return False, "Bu Ürün ID zaten kullanımda!"

    def guncelle_stok(self, urun_id, yeni_stok):
        self.cursor.execute("UPDATE urunler SET stok=? WHERE id=?", (yeni_stok, urun_id))
        self.conn.commit()

    def urun_sil(self, urun_id):
        self.cursor.execute("DELETE FROM siparisler WHERE urun_id=?", (urun_id,))
        self.cursor.execute("DELETE FROM urunler WHERE id=?", (urun_id,))
        self.conn.commit()
        return True, "Ürün ve ona ait tüm sipariş geçmişi silindi."

    def siparis_kaydet(self, siparis):
        self.cursor.execute("INSERT INTO siparisler (urun_id, adet, tarih) VALUES (?, ?, ?)", (siparis.urun_id, siparis.adet, siparis.tarih))
        self.conn.commit()

    def siparis_sil(self, siparis_id):
        # 1. Önce silinecek siparişin hangi üründen kaç adet olduğunu bul
        self.cursor.execute("SELECT urun_id, adet FROM siparisler WHERE id=?", (siparis_id,))
        siparis = self.cursor.fetchone()
        
        if siparis:
            urun_id = siparis[0]
            iade_edilecek_adet = siparis[1]
            
            # 2. Ürünün mevcut stoğunu bul ve iade edilen adeti üzerine ekle
            self.cursor.execute("SELECT stok FROM urunler WHERE id=?", (urun_id,))
            urun = self.cursor.fetchone()
            
            if urun:
                yeni_stok = urun[0] + iade_edilecek_adet
                self.cursor.execute("UPDATE urunler SET stok=? WHERE id=?", (yeni_stok, urun_id))
            
            # 3. Stok güncellendikten sonra sipariş kaydını tamamen sil
            self.cursor.execute("DELETE FROM siparisler WHERE id=?", (siparis_id,))
            self.conn.commit()
            return True
        return False

    def get_urunler(self):
        self.cursor.execute("SELECT * FROM urunler")
        return [Urun(r[0], r[1], r[2], r[3]) for r in self.cursor.fetchall()]

    def get_siparisler_detayli(self):
        self.cursor.execute('''
            SELECT s.id, u.ad, s.adet, u.fiyat, (s.adet * u.fiyat), s.tarih 
            FROM siparisler s
            JOIN urunler u ON s.urun_id = u.id
            ORDER BY s.id DESC
        ''')
        return self.cursor.fetchall()