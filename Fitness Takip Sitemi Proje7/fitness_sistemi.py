import sqlite3
from datetime import date

# ── 1. SPORCU SINIFI ──
class Sporcu:
    def __init__(self, sporcu_id, ad, kilo, boy):
        self.sporcu_id = sporcu_id
        self.ad = ad
        self.kilo = kilo
        self.boy = boy # cm cinsinden

    def ilerleme_kaydet(self, yeni_kilo, db_manager):
        eski_kilo = self.kilo
        self.kilo = yeni_kilo
        db_manager.guncelle_kilo(self.sporcu_id, yeni_kilo)
        fark = eski_kilo - yeni_kilo
        
        if fark > 0:
            return True, f"Tebrikler {self.ad}! {fark:.1f} kg verdiniz. Yeni kilonuz: {yeni_kilo}kg"
        elif fark < 0:
            return True, f"{self.ad}, {abs(fark):.1f} kg aldınız. Yeni kilonuz: {yeni_kilo}kg"
        else:
            return True, f"Kilonuz sabit kaldı: {yeni_kilo}kg"

# ── 2. ANTRENMAN SINIFI ──
class Antrenman:
    def __init__(self, antrenman_id, tur, sure):
        self.antrenman_id = antrenman_id
        self.tur = tur   
        self.sure = sure 

# ── 3. TAKİP SINIFI ──
class Takip:
    def __init__(self, takip_id, sporcu_id, antrenman_id, tarih, kalori):
        self.takip_id = takip_id
        self.sporcu_id = sporcu_id
        self.antrenman_id = antrenman_id
        self.tarih = tarih
        self.kalori = kalori 

# ── VERİTABANI YÖNETİCİSİ ──
class FitnessDB:
    def __init__(self, db_adi="fitness.db"):
        self.conn = sqlite3.connect(db_adi)
        self.cursor = self.conn.cursor()
        self._tablolari_kur()

    def _tablolari_kur(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS sporcular (id INTEGER PRIMARY KEY, ad TEXT, kilo REAL, boy REAL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS antrenmanlar (id INTEGER PRIMARY KEY, tur TEXT, sure INTEGER)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS takipler (id INTEGER PRIMARY KEY AUTOINCREMENT, sporcu_id INTEGER, antrenman_id INTEGER, tarih TEXT, kalori REAL)''')
        self.conn.commit()

    def sporcu_ekle(self, sporcu):
        try:
            self.cursor.execute("INSERT INTO sporcular (id, ad, kilo, boy) VALUES (?, ?, ?, ?)", (sporcu.sporcu_id, sporcu.ad, sporcu.kilo, sporcu.boy))
            self.conn.commit()
            return True, f"{sporcu.ad} sisteme eklendi."
        except sqlite3.IntegrityError:
            return False, "Bu ID ile zaten bir sporcu var!"

    def guncelle_kilo(self, sporcu_id, yeni_kilo):
        self.cursor.execute("UPDATE sporcular SET kilo=? WHERE id=?", (yeni_kilo, sporcu_id))
        self.conn.commit()

    # YENİ: Sporcu Silme Metodu
    def sporcu_sil(self, sporcu_id):
        # Önce bu sporcuya ait eski antrenman geçmişini siliyoruz (Çöp veri kalmaması için)
        self.cursor.execute("DELETE FROM takipler WHERE sporcu_id=?", (sporcu_id,))
        # Sonra sporcunun kendisini siliyoruz
        self.cursor.execute("DELETE FROM sporcular WHERE id=?", (sporcu_id,))
        self.conn.commit()
        return True, "Sporcu ve ona ait tüm antrenman kayıtları başarıyla silindi."

    def antrenman_ekle(self, antrenman):
        try:
            self.cursor.execute("INSERT INTO antrenmanlar (id, tur, sure) VALUES (?, ?, ?)", (antrenman.antrenman_id, antrenman.tur, antrenman.sure))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass

    def takip_ekle(self, sporcu_id, antrenman_id, tarih, kalori):
        self.cursor.execute("INSERT INTO takipler (sporcu_id, antrenman_id, tarih, kalori) VALUES (?, ?, ?, ?)", (sporcu_id, antrenman_id, tarih, kalori))
        self.conn.commit()
        return True, "Antrenman başarıyla kaydedildi!"

    # YENİ: Tekil Antrenman Kaydı Silme Metodu
    def takip_sil(self, takip_id):
        self.cursor.execute("DELETE FROM takipler WHERE id=?", (takip_id,))
        self.conn.commit()
        return True

    def get_sporcular(self):
        self.cursor.execute("SELECT * FROM sporcular")
        return [Sporcu(r[0], r[1], r[2], r[3]) for r in self.cursor.fetchall()]

    def get_antrenmanlar(self):
        self.cursor.execute("SELECT * FROM antrenmanlar")
        return [Antrenman(r[0], r[1], r[2]) for r in self.cursor.fetchall()]

    def get_takipler_detayli(self):
        self.cursor.execute('''
            SELECT t.id, s.ad, a.tur, a.sure, t.kalori, t.tarih 
            FROM takipler t
            JOIN sporcular s ON t.sporcu_id = s.id
            JOIN antrenmanlar a ON t.antrenman_id = a.id
            ORDER BY t.id DESC
        ''')
        return self.cursor.fetchall()