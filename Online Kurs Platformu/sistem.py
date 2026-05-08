import sqlite3

# egitmen bilgilerini ram (bellek) uzerinde tasimak icin olusturulan basit veri sinifi
class Egitmen:
    def __init__(self, ad, uzmanlik):
        self.ad = ad
        self.uzmanlik = uzmanlik

# ogrenci bilgilerini ram uzerinde tasimak icin veri sinifi (telefon eklendi, id yerine tc_no geldi)
class Ogrenci:
    def __init__(self, tc_no, ad, email, telefon):
        self.tc_no = tc_no
        self.ad = ad
        self.email = email
        self.telefon = telefon

# kurs bilgilerini ve egitmen objesini bir arada tutan veri sinifi
class Kurs:
    def __init__(self, kurs_id, kurs_adi, egitmen, kontenjan):
        self.kurs_id = kurs_id
        self.kurs_adi = kurs_adi
        self.egitmen = egitmen
        self.kontenjan = kontenjan
        # arayuzde doluluk oranini (ornegin 3/5) gostermek icin tuttugumuz sayac
        self.kayitli_ogrenci_sayisi = 0


# projenin beyni olan sinif. butun veritabani (sqlite) islenleri ve mantiksal kontroller burada yapilir.
class KursSistemi:
    def __init__(self):
        # eski veritabaniyla cakismamasi icin v2 adinda yeni bir veritabani olusturuyoruz
        self.baglanti = sqlite3.connect("okul_veritabani_v2.db")
        self.imlec = self.baglanti.cursor()
        
        # sinif calistigi an tablolari kuran metot cagirilir
        self.veritabani_kurulumu()
        
        # mudur paneli icin sabit kimlik bilgileri
        self.admin_user = "Admin"
        self.admin_pass = "1234"

    def veritabani_kurulumu(self):
        # ogrenciler tablosu tc_no (primary key) ve telefon icerecek sekilde guncellendi
        self.imlec.execute("CREATE TABLE IF NOT EXISTS ogrenciler (tc_no TEXT PRIMARY KEY, ad TEXT, email TEXT, telefon TEXT)")
        self.imlec.execute("CREATE TABLE IF NOT EXISTS kurslar (id INTEGER PRIMARY KEY, ad TEXT, egitmen TEXT, kontenjan INTEGER)")
        
        # atamalar tablosu artik ogrencinin tc nosu ile kurs id'sini bagliyor
        self.imlec.execute("CREATE TABLE IF NOT EXISTS atamalar (ogrenci_tc TEXT, kurs_id INTEGER)")
        self.baglanti.commit() 
        
        # kurslar tablosu bos mu diye kontrol edilir
        self.imlec.execute("SELECT COUNT(*) FROM kurslar")
        if self.imlec.fetchone()[0] == 0:
            # eger bos ise varsayilan kurslar ve egitmenler sisteme otomatik olarak eklenir
            self.imlec.execute("INSERT INTO kurslar VALUES (10, 'Python İle Gui Programlama', 'Büşra Hoca', 5)")
            self.imlec.execute("INSERT INTO kurslar VALUES (20, 'Sql Veritabanı Yönetimi', 'Erdem Hoca', 3)")
            self.imlec.execute("INSERT INTO kurslar VALUES (30, 'Temel Ağ Güvenliği', 'Muharrem Hoca', 4)")
            self.baglanti.commit()

    def giris_kontrol(self, kullanici_adi, sifre):
        # arayuzden gelen bilgilerin dogrulugunu teyit eder
        if kullanici_adi == self.admin_user and sifre == self.admin_pass:
            return True, "Sistem Müdürü"
        return False, None

    def ogrenci_olustur(self, tc_no, ad, email, telefon):
        # ayni tc numarasiyla baska bir ogrenci var mi diye veritabanina sorulur
        self.imlec.execute("SELECT * FROM ogrenciler WHERE tc_no=?", (tc_no,))
        if self.imlec.fetchone():
            return False, "Bu Tc Kimlik Numaralı Öğrenci Zaten Kayıtlı"
        
        # eger yoksa ogrenci tabloya kalici olarak eklenir
        self.imlec.execute("INSERT INTO ogrenciler VALUES (?, ?, ?, ?)", (tc_no, ad, email, telefon))
        self.baglanti.commit()
        return True, "Öğrenci Sisteme Kaydedildi"

    def ogrenci_sil(self, tc_no):
        # once atamalar tablosundan ogrencinin kayitli oldugu kurs baglantilari silinir
        self.imlec.execute("DELETE FROM atamalar WHERE ogrenci_tc=?", (tc_no,))
        # daha sonra ogrenci ana ogrenciler tablosundan tamamen silinir
        self.imlec.execute("DELETE FROM ogrenciler WHERE tc_no=?", (tc_no,))
        self.baglanti.commit()
        return True, "Öğrenci Ve Kurs Kayıtları Sistemden Tamamen Silindi"

    def tum_ogrencileri_getir(self):
        # arayuzdeki listeleri doldurmak icin tum ogrencileri ceker ve nesne listesi dondurur
        self.imlec.execute("SELECT tc_no, ad, email, telefon FROM ogrenciler")
        return [Ogrenci(s[0], s[1], s[2], s[3]) for s in self.imlec.fetchall()]

    def tum_kurslari_getir(self):
        # tum kurslari dondurur. atamalar tablosunu sayarak doluluk oranini hesaplar
        self.imlec.execute("SELECT id, ad, egitmen, kontenjan FROM kurslar")
        liste = []
        for s in self.imlec.fetchall():
            kurs = Kurs(s[0], s[1], Egitmen(s[2], ""), s[3])
            self.imlec.execute("SELECT COUNT(*) FROM atamalar WHERE kurs_id=?", (s[0],))
            kurs.kayitli_ogrenci_sayisi = self.imlec.fetchone()[0]
            liste.append(kurs)
        return liste

    def ogrenci_kurslarini_getir(self, tc_no):
        # belirli bir ogrencinin kayitli oldugu kurslarin adlarini bulur
        sorgu = "SELECT kurslar.ad FROM atamalar JOIN kurslar ON atamalar.kurs_id = kurslar.id WHERE atamalar.ogrenci_tc=?"
        self.imlec.execute(sorgu, (tc_no,))
        return [s[0] for s in self.imlec.fetchall()]

    def ogrenci_kursa_kaydet(self, tc_no, kurs_id):
        # ogrenci bu kursa zaten onceden atanmis mi kontrolu
        self.imlec.execute("SELECT COUNT(*) FROM atamalar WHERE ogrenci_tc=? AND kurs_id=?", (tc_no, kurs_id))
        if self.imlec.fetchone()[0] > 0:
            return False, "Öğrenci Zaten Bu Kursa Kayıtlı"
            
        # kursun kontenjani dolmus mu kontrolu
        self.imlec.execute("SELECT kontenjan FROM kurslar WHERE id=?", (kurs_id,))
        kontenjan = self.imlec.fetchone()[0]
        
        self.imlec.execute("SELECT COUNT(*) FROM atamalar WHERE kurs_id=?", (kurs_id,))
        mevcut = self.imlec.fetchone()[0]
        
        if mevcut >= kontenjan:
            return False, "Kurs Kontenjanı Dolu"
            
        # kurallar gecildiyse atama gerceklestirilir
        self.imlec.execute("INSERT INTO atamalar VALUES (?, ?)", (tc_no, kurs_id))
        self.baglanti.commit()
        return True, "Öğrenci Kursa Atandı"

    def ogrenci_kurstan_cikar(self, tc_no, kurs_adi):
        # kurs adi uzerinden kursun id numarasini bulur
        self.imlec.execute("SELECT id FROM kurslar WHERE ad=?", (kurs_adi,))
        kurs_s = self.imlec.fetchone()
        
        # kurs bulunduysa atamalar tablosundan o iliskiyi siler
        if kurs_s:
            self.imlec.execute("DELETE FROM atamalar WHERE ogrenci_tc=? AND kurs_id=?", (tc_no, kurs_s[0]))
            self.baglanti.commit()
            return True, "Öğrenci Seçili Kurstan Silindi"
        return False, "Kurs Bulunamadı"