import sqlite3

# tariflerin icerdigi malzemeleri ram (bellek) uzerinde tasimak icin veri sinifi
class Malzeme:
    def __init__(self, malzeme_adi, miktar):
        self.malzeme_adi = malzeme_adi
        self.miktar = miktar

# tarif detaylarini tutan temel veri nesnesi
class Tarif:
    def __init__(self, tarif_id, tarif_adi, kategori, hazirlama_suresi):
        self.tarif_id = tarif_id
        self.tarif_adi = tarif_adi
        self.kategori = kategori
        self.hazirlama_suresi = hazirlama_suresi
        # bir tarifin icinde birden fazla malzeme nesnesi olabilecegi icin liste kullanilir
        self.malzemeler = []

# platformu kullanan kisileri temsil eden sinif
class Kullanici:
    def __init__(self, kullanici_id, ad):
        self.kullanici_id = kullanici_id
        self.ad = ad

# projenin ana motoru. tum veritabani islenleri ve mantiksal kontroller bu sinifta gerceklesir.
class YemekTarifSistemi:
    def __init__(self):
        # sqlite veritabanina kalici baglanti acilir. eger bu adda dosya yoksa diskte yeni olusturulur.
        self.baglanti = sqlite3.connect("yemek_platformu.db")
        # sql komutlarini calistirmak amaciyla imlec (cursor) nesnesi yaratilir
        self.imlec = self.baglanti.cursor()
        
        # sistem baslatildiginda tablolari kontrol eden ve verileri basan metodlar cagirilir
        self.veritabani_kurulumu()
        self.varsayilan_verileri_yukle()

    # eger tablolar veritabaninda mevcut degilse (ilk calistirma) bunlari insa eden metod
    def veritabani_kurulumu(self):
        # primary key (birincil anahtar) ile benzersiz id'lere sahip tarif tablosu
        self.imlec.execute("CREATE TABLE IF NOT EXISTS tarifler (id INTEGER PRIMARY KEY, ad TEXT, kategori TEXT, sure INTEGER)")
        
        # ilerleyen asamalarda eklenebilecek iliskisel tablolar
        self.imlec.execute("CREATE TABLE IF NOT EXISTS malzemeler (tarif_id INTEGER, malzeme_ad TEXT, miktar TEXT)")
        self.imlec.execute("CREATE TABLE IF NOT EXISTS kullanicilar (id INTEGER PRIMARY KEY, ad TEXT)")
        self.imlec.execute("CREATE TABLE IF NOT EXISTS degerlendirmeler (kullanici_id INTEGER, tarif_id INTEGER, puan INTEGER)")
        
        # yapilan ddl (data definition language) degisikliklerini disk uzerine kaydeder
        self.baglanti.commit()

    # sistem ilk kez aciliyorsa, ici bos kalmasin diye rastgele 5 adet veriyi kalici olarak isler
    def varsayilan_verileri_yukle(self):
        # tarifler tablosundaki kayit sayisi sayilir
        self.imlec.execute("SELECT COUNT(*) FROM tarifler")
        if self.imlec.fetchone()[0] == 0: # tablo bos ise
            # executemany metodu ile liste icindeki tum tuple verileri tek seferde tabloya yazilir
            tarifler = [
                (1, 'Mercimek Çorbası', 'Çorba', 30),
                (2, 'Karnıyarık', 'Ana Yemek', 50),
                (3, 'Pirinç Pilavı', 'Yan Lezzet', 20),
                (4, 'Gavurdağı Salatası', 'Salata', 15),
                (5, 'Sütlaç', 'Tatlı', 45)
            ]
            self.imlec.executemany("INSERT INTO tarifler VALUES (?, ?, ?, ?)", tarifler)
            self.baglanti.commit()

    # arayuzden gelen yeni tarif parametrelerini sql injection riskini onlemek icin (?) parametreleriyle veritabanina yazar
    def tarif_ekle(self, tarif_id, ad, kategori, sure):
        try:
            self.imlec.execute("INSERT INTO tarifler VALUES (?, ?, ?, ?)", (tarif_id, ad, kategori, sure))
            self.baglanti.commit()
            return True, "Tarif Sisteme Başarıyla Eklendi"
        except sqlite3.Error:
            # ayni id'ye sahip ikinci bir kayit eklenmeye calisilirsa unique constraint hatasi yakalanir
            return False, "Sistem Hatası: Tarif Eklenemedi (ID Kullanımda Olabilir)"

    # mevcut bir tarifin ismini ve suresini id parametresi uzerinden bularak update eden (guncelleyen) metod
    def tarif_guncelle(self, tarif_id, yeni_ad, yeni_sure):
        self.imlec.execute("UPDATE tarifler SET ad=?, sure=? WHERE id=?", (yeni_ad, yeni_sure, tarif_id))
        self.baglanti.commit()
        return True, "Tarif Bilgileri Güncellendi"

    # arayuzdeki qlistwidget gorselini doldurmak icin tablodaki tum satir verilerini (tuple listesi olarak) ceken metod
    def tum_tarifleri_getir(self):
        self.imlec.execute("SELECT * FROM tarifler")
        return self.imlec.fetchall()