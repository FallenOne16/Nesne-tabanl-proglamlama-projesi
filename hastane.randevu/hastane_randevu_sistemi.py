import sqlite3
import json
import os
from datetime import datetime

# Veritabanı dosyasının yolu (aynı klasörde randevu.db oluşturulacak)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "randevu.db")

class DatabaseManager:
    """SQLite veritabanı işlemlerini yürüten yönetici sınıf."""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._create_tables()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Hasta Tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS hasta (
                    hasta_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ad TEXT NOT NULL,
                    tc TEXT UNIQUE NOT NULL,
                    telefon TEXT NOT NULL
                )
            ''')
            # Doktor Tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS doktor (
                    doktor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ad TEXT NOT NULL,
                    uzmanlik TEXT NOT NULL,
                    uygun_saatler TEXT NOT NULL
                )
            ''')
            # Randevu Tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS randevu (
                    randevu_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tarih TEXT NOT NULL,
                    saat TEXT NOT NULL,
                    doktor_id INTEGER NOT NULL,
                    hasta_id INTEGER NOT NULL,
                    FOREIGN KEY (doktor_id) REFERENCES doktor (doktor_id),
                    FOREIGN KEY (hasta_id) REFERENCES hasta (hasta_id),
                    UNIQUE(tarih, saat, doktor_id)
                )
            ''')
            conn.commit()

    # --- Hasta İşlemleri ---
    def add_hasta(self, ad, tc, telefon):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO hasta (ad, tc, telefon) VALUES (?, ?, ?)", (ad, tc, telefon))
                conn.commit()
                return True, cursor.lastrowid
            except sqlite3.IntegrityError:
                return False, "Bu TC kimlik numarası ile kayıtlı hasta zaten var."

    def get_all_hastalar(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT hasta_id, ad, tc, telefon FROM hasta")
            return [Hasta(*row) for row in cursor.fetchall()]

    def get_hasta(self, hasta_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT hasta_id, ad, tc, telefon FROM hasta WHERE hasta_id = ?", (hasta_id,))
            r = cursor.fetchone()
            if r:
                return Hasta(*r)
            return None

    # --- Doktor İşlemleri ---
    def add_doktor(self, ad, uzmanlik, uygun_saatler_list):
        uygun_saatler_json = json.dumps(uygun_saatler_list)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO doktor (ad, uzmanlik, uygun_saatler) VALUES (?, ?, ?)", 
                           (ad, uzmanlik, uygun_saatler_json))
            conn.commit()
            return True, cursor.lastrowid

    def get_all_doktorlar(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT doktor_id, ad, uzmanlik, uygun_saatler FROM doktor")
            rows = cursor.fetchall()
            return [Doktor(r[0], r[1], r[2], json.loads(r[3])) for r in rows]
            
    def get_doktor(self, doktor_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT doktor_id, ad, uzmanlik, uygun_saatler FROM doktor WHERE doktor_id = ?", (doktor_id,))
            r = cursor.fetchone()
            if r:
                return Doktor(r[0], r[1], r[2], json.loads(r[3]))
            return None

    # --- Randevu İşlemleri ---
    def is_doktor_available(self, doktor_id, tarih, saat):
        """Belirli bir tarih ve saatte doktorun dolu olup olmadığını kontrol eder."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM randevu WHERE doktor_id = ? AND tarih = ? AND saat = ?", (doktor_id, tarih, saat))
            return cursor.fetchone() is None

    def insert_randevu(self, tarih, saat, doktor_id, hasta_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO randevu (tarih, saat, doktor_id, hasta_id) VALUES (?, ?, ?, ?)", 
                           (tarih, saat, doktor_id, hasta_id))
            conn.commit()
            return cursor.lastrowid

    def delete_randevu(self, randevu_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM randevu WHERE randevu_id = ?", (randevu_id,))
            conn.commit()

    def get_all_randevular(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT randevu_id, tarih, saat, doktor_id, hasta_id FROM randevu ORDER BY tarih DESC, saat DESC")
            rows = cursor.fetchall()
            randevular = []
            for r in rows:
                doktor = self.get_doktor(r[3])
                hasta = self.get_hasta(r[4])
                randevular.append(Randevu(r[0], r[1], r[2], doktor, hasta))
            return randevular
            
    def get_randevular_by_date(self, tarih):
        """Ek Özellik: Günlük randevu listesi görüntüleme için belirli tarihe göre filtreler."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT randevu_id, tarih, saat, doktor_id, hasta_id FROM randevu WHERE tarih = ? ORDER BY saat ASC", (tarih,))
            rows = cursor.fetchall()
            randevular = []
            for r in rows:
                doktor = self.get_doktor(r[3])
                hasta = self.get_hasta(r[4])
                randevular.append(Randevu(r[0], r[1], r[2], doktor, hasta))
            return randevular


# ============================================================
#   DOMAIN SINIFLARI
# ============================================================

class Hasta:
    """Sisteme kayıtlı hastayı temsil eder."""
    def __init__(self, hasta_id, ad, tc, telefon):
        self.hasta_id = hasta_id
        self.ad = ad
        self.tc = tc
        self.telefon = telefon

    def randevu_al(self, doktor, tarih, saat, db_manager):
        """Hasta için randevu oluşturmayı tetikler."""
        return Randevu.randevu_olustur(self, doktor, tarih, saat, db_manager)
        
    def __str__(self):
        return f"{self.ad} (TC: {self.tc})"


class Doktor:
    """Sisteme kayıtlı doktoru temsil eder."""
    def __init__(self, doktor_id, ad, uzmanlik, uygun_saatler):
        self.doktor_id = doktor_id
        self.ad = ad
        self.uzmanlik = uzmanlik
        self.uygun_saatler = uygun_saatler  # ["09:00", "10:00", "11:00", ...] listesi

    def uygunluk_kontrol(self, tarih, saat, db_manager):
        """Doktorun belirtilen tarih ve saatte müsait olup olmadığını kontrol eder."""
        # 1. Saat doktorun çalışma saatleri içinde mi?
        if saat not in self.uygun_saatler:
            return False
        # 2. O saatte başka bir randevusu var mı? (Veritabanı kontrolü)
        return db_manager.is_doktor_available(self.doktor_id, tarih, saat)

    def __str__(self):
        return f"Dr. {self.ad} ({self.uzmanlik})"


class Randevu:
    """Doktor ve Hasta arasındaki randevuyu temsil eder."""
    def __init__(self, randevu_id, tarih, saat, doktor, hasta):
        self.randevu_id = randevu_id
        self.tarih = tarih
        self.saat = saat
        self.doktor = doktor
        self.hasta = hasta

    @staticmethod
    def randevu_olustur(hasta, doktor, tarih, saat, db_manager):
        """Yeni bir randevu oluşturur ve veritabanına kaydeder."""
        # Uygunluk kontrolü çağrılıyor
        if not doktor.uygunluk_kontrol(tarih, saat, db_manager):
            return False, "Doktor bu tarih ve saatte uygun değil veya doludur."
        
        try:
            # Veritabanına ekle
            randevu_id = db_manager.insert_randevu(tarih, saat, doktor.doktor_id, hasta.hasta_id)
            yeni_randevu = Randevu(randevu_id, tarih, saat, doktor, hasta)
            return True, yeni_randevu
        except Exception as e:
            return False, f"Randevu oluşturulamadı: {str(e)}"

    def randevu_iptal(self, db_manager):
        """Randevuyu veritabanından siler (iptal eder)."""
        try:
            db_manager.delete_randevu(self.randevu_id)
            return True, "Randevu başarıyla iptal edildi."
        except Exception as e:
            return False, f"Randevu iptal edilirken hata oluştu: {str(e)}"

    def __str__(self):
        return f"{self.tarih} {self.saat} | {self.doktor.ad} - {self.hasta.ad}"
