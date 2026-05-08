import sqlite3
from google import genai

class Malzeme:
    def __init__(self, malzeme_adi, miktar):
        self.malzeme_adi = malzeme_adi
        self.miktar = miktar

class Tarif:
    def __init__(self, tarif_id, tarif_adi, kategori, hazirlama_suresi):
        self.tarif_id = tarif_id
        self.tarif_adi = tarif_adi
        self.kategori = kategori
        self.hazirlama_suresi = hazirlama_suresi
        self.malzemeler = []

class Kullanici:
    def __init__(self, kullanici_id, ad):
        self.kullanici_id = kullanici_id
        self.ad = ad

class YemekTarifSistemi:
    def __init__(self):
        self.baglanti = sqlite3.connect("yemek_platformu.db")
        self.imlec = self.baglanti.cursor()
        
        self.veritabani_kurulumu()
        self.varsayilan_verileri_yukle()
        
        # api sifresi string (metin) formatinda cift tirnak icine alindi
        self.api_key = "AIzaSyDas03fCoBDYuhbKdy2cpXXyq8oJwcL83g"
        
        # yeni genai kutuphanesi ile client (istemci) baglantisi baslatiliyor
        self.ai_client = genai.Client(api_key=self.api_key)

    def veritabani_kurulumu(self):
        self.imlec.execute("CREATE TABLE IF NOT EXISTS tarifler (id INTEGER PRIMARY KEY, ad TEXT, kategori TEXT, sure INTEGER)")
        self.imlec.execute("CREATE TABLE IF NOT EXISTS malzemeler (tarif_id INTEGER, malzeme_ad TEXT, miktar TEXT)")
        self.imlec.execute("CREATE TABLE IF NOT EXISTS kullanicilar (id INTEGER PRIMARY KEY, ad TEXT)")
        self.imlec.execute("CREATE TABLE IF NOT EXISTS degerlendirmeler (kullanici_id INTEGER, tarif_id INTEGER, puan INTEGER)")
        self.baglanti.commit()

    def varsayilan_verileri_yukle(self):
        self.imlec.execute("SELECT COUNT(*) FROM tarifler")
        if self.imlec.fetchone()[0] == 0:
            tarifler = [
                (1, 'Mercimek Çorbası', 'Çorba', 30),
                (2, 'Karnıyarık', 'Ana Yemek', 50),
                (3, 'Pirinç Pilavı', 'Yan Lezzet', 20),
                (4, 'Gavurdağı Salatası', 'Salata', 15),
                (5, 'Sütlaç', 'Tatlı', 45)
            ]
            self.imlec.executemany("INSERT INTO tarifler VALUES (?, ?, ?, ?)", tarifler)
            self.baglanti.commit()

    def tarif_ekle(self, tarif_id, ad, kategori, sure):
        try:
            self.imlec.execute("INSERT INTO tarifler VALUES (?, ?, ?, ?)", (tarif_id, ad, kategori, sure))
            self.baglanti.commit()
            return True, "Tarif Sisteme Başarıyla Eklendi"
        except sqlite3.Error:
            return False, "Sistem Hatası: Tarif Eklenemedi (ID Kullanımda Olabilir)"

    def tarif_guncelle(self, tarif_id, yeni_ad, yeni_sure):
        self.imlec.execute("UPDATE tarifler SET ad=?, sure=? WHERE id=?", (yeni_ad, yeni_sure, tarif_id))
        self.baglanti.commit()
        return True, "Tarif Bilgileri Güncellendi"

    def tum_tarifleri_getir(self):
        self.imlec.execute("SELECT * FROM tarifler")
        return self.imlec.fetchall()

    def ai_tarif_uret(self, yemek_adi):
        try:
            prompt = f"Sen usta bir aşçısın. Lütfen bana {yemek_adi} yemeğinin tam malzemelerini ve adım adım yapılışını profesyonel ama anlaşılır bir dille anlat, noktalama işaretlerini çok kullanmana gerek yok sadece basit ve anlaşılır bir türkçe ile açıklamanı istiyorum, 'Servis','Pişirme' bunun gibi temel ve ufak başlıkları kalın harflerle yazar mısın."
            
            # yeni guncel kutuphane uzerinden gemini-2.5-flash modeline veri gonderimi
            response = self.ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
            )
            return True, response.text
        except Exception as e:
            return False, f"Bağlantı Hatası: Yapay zeka ile iletişim kurulamadı.\nDetay: {str(e)}"