import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QListWidget, QStackedWidget, QMessageBox, 
                             QFrame, QSplitter)
from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtCore import Qt
from sistem import KursSistemi

# arayuzu olusturan ve pyqt5 widget'indan miras alan ana sinif
class PlatformArayuzu(QWidget):
    def __init__(self, sistem_nesnesi):
        super().__init__()
        # arka planda calisan KursSistemi objesi gui icine dahil edilir
        self.sistem = sistem_nesnesi
        
        # veritabanindan cekilen verilerin arayuzde gecici olarak tutuldugu listeler
        self.guncel_ogrenciler = []
        self.guncel_kurslar = []
        
        # arayuzu baslatan fonksiyonlar cagirilir
        self.pencere_yapilandir()
        self.stil_uygula()

    def pencere_yapilandir(self):
        self.setWindowTitle("Online Kurs Platformu - Müdür Paneli")
        # program ilk acildiginda giris panelinin orantili gorunmesi icin boyut kucuk tutulur
        self.resize(360, 400)
        self.setFont(QFont("Segoe UI", 11))

        # ana dikey duzen (layout) olusturulur
        self.ana_layout = QVBoxLayout()
        
        # birden fazla sayfayi ust uste koyup sadece secileni gosteren yonetici (stacked widget)
        self.sayfa_yoneticisi = QStackedWidget()

        self.giris_sayfasi_hazirla()
        self.ana_sayfa_hazirla()

        # hazirlanan sayfalar yoneticiye eklenir
        self.sayfa_yoneticisi.addWidget(self.giris_ekrani)
        self.sayfa_yoneticisi.addWidget(self.ana_ekran)

        self.ana_layout.addWidget(self.sayfa_yoneticisi)
        self.ana_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.ana_layout)

    def stil_uygula(self):
        # qss (qt style sheets) kullanilarak elemanlarin renk, kavis ve boyutlari ayarlanir.
        modern_qss = """
        QWidget {
            background-color: #121212;
            color: #ffffff;
        }
        QLabel {
            font-size: 16px;
            color: #bb86fc;
            margin-bottom: 5px;
        }
        QLineEdit {
            padding: 10px;
            font-size: 14px;
            background-color: #1e1e1e;
            border: 2px solid #333333;
            border-radius: 6px;
            color: #ffffff;
        }
        QLineEdit:focus {
            border: 2px solid #bb86fc;
        }
        QPushButton {
            padding: 10px;
            font-size: 14px;
            color: #ffffff;
            background-color: #bb86fc;
            border: none;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #9965f4;
        }
        QPushButton:pressed {
            background-color: #7743d1;
        }
        QListWidget {
            background-color: #1e1e1e;
            border: 2px solid #333333;
            border-radius: 6px;
            padding: 10px;
            font-size: 14px;
            outline: 0;
        }
        QListWidget::item {
            padding: 10px;
            border-bottom: 1px solid #333333;
        }
        QListWidget::item:selected {
            background-color: #bb86fc;
            color: #121212;
            border-radius: 5px;
        }
        QFrame#sol_menu_cerceve {
            background-color: #1e1e1e;
            border-right: 2px solid #333333;
        }
        QPushButton#sol_menu_buton {
            color: #ffffff;
            background-color: transparent;
            text-align: left;
            padding-left: 20px;
            font-weight: normal;
        }
        QPushButton#sol_menu_buton:hover {
            background-color: #333333;
        }
        """
        self.setStyleSheet(modern_qss)

    def giris_sayfasi_hazirla(self):
        # ilk acilan kucuk giris panelini tasarlar
        self.giris_ekrani = QWidget()
        ana_dikey = QVBoxLayout()
        
        # gorsel acidan elemanlari ortada gruplamak icin bir cerceve (QFrame) kullanilir
        merkez_kutu = QFrame()
        merkez_kutu.setFixedWidth(300) 
        merkez_kutu.setStyleSheet("background-color: #1e1e1e; border-radius: 10px; border: 1px solid #333333;")
        
        merkez_layout = QVBoxLayout()
        merkez_layout.setContentsMargins(25, 25, 25, 25)
        merkez_layout.setSpacing(15)
        
        baslik = QLabel("Platform Giriş Paneli")
        baslik.setAlignment(Qt.AlignCenter)
        baslik.setStyleSheet("font-size: 20px; color: #ffffff; border: none; margin-bottom: 10px;")
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Kullanıcı Adı")
        self.user_input.setStyleSheet("border: 1px solid #555555;") 
        
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Şifre")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setStyleSheet("border: 1px solid #555555;")
        
        btn_giris = QPushButton("Sisteme Giriş Yap")
        btn_giris.setCursor(QCursor(Qt.PointingHandCursor))
        btn_giris.clicked.connect(self.login_denemesi)
        
        # elemanlar merkez kutuya yerlestirilir
        merkez_layout.addWidget(baslik)
        merkez_layout.addWidget(self.user_input)
        merkez_layout.addWidget(self.pass_input)
        merkez_layout.addWidget(btn_giris)
        merkez_kutu.setLayout(merkez_layout)
        
        # dikey ortalama yapmak icin kutunun altina ve ustune esnek bosluk (stretch) eklenir
        ana_dikey.addStretch()
        ana_dikey.addWidget(merkez_kutu, alignment=Qt.AlignCenter)
        ana_dikey.addStretch()
        
        self.giris_ekrani.setLayout(ana_dikey)

    def ana_sayfa_hazirla(self):
        # ana modul. sol tarafta menuyu, sag tarafta ise sekmeleri barindirir
        self.ana_ekran = QWidget()
        layout = QHBoxLayout()
        
        # 1. sol menu tasarimi
        sol_menu = QFrame()
        sol_menu.setObjectName("sol_menu_cerceve")
        sol_menu.setFixedWidth(220)
        sol_layout = QVBoxLayout()
        sol_layout.setContentsMargins(0, 20, 0, 0)
        
        baslik = QLabel("Müdür Sistemi")
        baslik.setAlignment(Qt.AlignCenter)
        baslik.setStyleSheet("color: #ffffff; border: none; margin-bottom: 20px; font-weight: normal;")
        
        self.btn_sistem_paneli = QPushButton("Sistem Paneli")
        self.btn_yeni_kayit = QPushButton("Yeni Kayıt Oluştur")
        self.btn_atama_yonetimi = QPushButton("Atama Yönetimi")
        self.btn_kayit_silme = QPushButton("Kayıt Silme")
        self.btn_ogrenci_raporu = QPushButton("Öğrenci Detay Raporu")
        
        # butonlar bir dongu ile listeye eklenir
        butonlar = [self.btn_sistem_paneli, self.btn_yeni_kayit, self.btn_atama_yonetimi, self.btn_kayit_silme, self.btn_ogrenci_raporu]
        for btn in butonlar:
            btn.setObjectName("sol_menu_buton")
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            sol_layout.addWidget(btn)
            sol_layout.addSpacing(5)
            
        # sayfalara gecis baglantilari
        self.btn_sistem_paneli.clicked.connect(lambda: self.sekme_degistir(0))
        self.btn_yeni_kayit.clicked.connect(lambda: self.sekme_degistir(1))
        self.btn_atama_yonetimi.clicked.connect(lambda: self.sekme_degistir(2))
        self.btn_kayit_silme.clicked.connect(lambda: self.sekme_degistir(3))
        self.btn_ogrenci_raporu.clicked.connect(lambda: self.sekme_degistir(4))
        
        sol_layout.addStretch()
        sol_layout.addWidget(QLabel("Yönetici: Admin"), alignment=Qt.AlignCenter)
        sol_layout.addSpacing(10)
        sol_menu.setLayout(sol_layout)
        
        # 2. sag icerik alani tasarimi (sayfalari ust uste koyan qstackedwidget)
        self.icerik_alani = QStackedWidget()
        
        # 5 farkli sekmenin widget (panel) ayarlamalari
        self.sekme_sistem_paneli_olustur()
        self.sekme_yeni_kayit_olustur()
        self.sekme_atama_yonetimi_olustur()
        self.sekme_kayit_silme_olustur()
        self.sekme_ogrenci_raporu_olustur()
        
        # uretilen widgetlar icerik alanina dahil edilir
        self.icerik_alani.addWidget(self.panel_sekmesi)
        self.icerik_alani.addWidget(self.yeni_kayit_sekmesi)
        self.icerik_alani.addWidget(self.atama_yonetimi_sekmesi)
        self.icerik_alani.addWidget(self.silme_sekmesi)
        self.icerik_alani.addWidget(self.rapor_sekmesi)
        
        layout.addWidget(sol_menu)
        layout.addWidget(self.icerik_alani)
        layout.setContentsMargins(0, 0, 0, 0)
        self.ana_ekran.setLayout(layout)

    def sekme_sistem_paneli_olustur(self):
        self.panel_sekmesi = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        
        self.etiket_yonetici = QLabel("Platform Genel Durumu")
        self.etiket_yonetici.setStyleSheet("font-size: 20px; color: #ffffff;")
        
        self.liste_tum_ogrenciler = QListWidget()
        
        layout.addWidget(self.etiket_yonetici)
        layout.addSpacing(20)
        layout.addWidget(QLabel("Sistemdeki Kayıtlı Tüm Öğrenciler (Tc No | İsim)"))
        layout.addWidget(self.liste_tum_ogrenciler)
        self.panel_sekmesi.setLayout(layout)

    def sekme_yeni_kayit_olustur(self):
        # text boxlarin uyarilari yeni kurallara gore guncellendi
        self.yeni_kayit_sekmesi = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        
        self.input_ogrenci_tc = QLineEdit()
        self.input_ogrenci_tc.setPlaceholderText("Tc Kimlik Numarası (Sadece 11 Haneli Rakam)")
        # max uzunluk 11 karaktere sabitlendi, fazlasi yazilamaz
        self.input_ogrenci_tc.setMaxLength(11)
        
        self.input_ogrenci_ad = QLineEdit()
        self.input_ogrenci_ad.setPlaceholderText("Öğrenci Adı Ve Soyadı (Sadece Harf)")
        
        self.input_ogrenci_email = QLineEdit()
        self.input_ogrenci_email.setPlaceholderText("Email Adresi (@ İşareti Zorunlu)")
        
        self.input_ogrenci_tel = QLineEdit()
        self.input_ogrenci_tel.setPlaceholderText("Telefon Numarası (Sadece Rakam)")
        # telefon numarasi da max 11 karaktere sabitlendi
        self.input_ogrenci_tel.setMaxLength(11)
        
        btn_ogrenci_kaydet = QPushButton("Yeni Öğrenciyi Sisteme Kaydet")
        btn_ogrenci_kaydet.setCursor(QCursor(Qt.PointingHandCursor))
        btn_ogrenci_kaydet.clicked.connect(self.yeni_ogrenci_islemi)
        
        layout.addWidget(QLabel("Tc Kimlik No"))
        layout.addWidget(self.input_ogrenci_tc)
        layout.addSpacing(15)
        layout.addWidget(QLabel("Öğrenci Ad Soyad"))
        layout.addWidget(self.input_ogrenci_ad)
        layout.addSpacing(15)
        layout.addWidget(QLabel("Öğrenci Email"))
        layout.addWidget(self.input_ogrenci_email)
        layout.addSpacing(15)
        layout.addWidget(QLabel("Telefon Numarası"))
        layout.addWidget(self.input_ogrenci_tel)
        layout.addSpacing(25)
        layout.addWidget(btn_ogrenci_kaydet)
        layout.addStretch()
        self.yeni_kayit_sekmesi.setLayout(layout)

    def sekme_atama_yonetimi_olustur(self):
        self.atama_yonetimi_sekmesi = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        
        splitter = QSplitter(Qt.Horizontal)
        
        sol_cerceve = QFrame()
        sol_layout = QVBoxLayout()
        self.liste_atama_ogrenciler = QListWidget()
        sol_layout.addWidget(QLabel("1. Atama Yapılacak Öğrenciyi Seçin"))
        sol_layout.addWidget(self.liste_atama_ogrenciler)
        sol_cerceve.setLayout(sol_layout)
        
        sag_cerceve = QFrame()
        sag_layout = QVBoxLayout()
        
        self.liste_atama_kurslar = QListWidget()
        btn_kurs_ata = QPushButton("Seçili Öğrenciyi Seçili Kursa Ata")
        btn_kurs_ata.setCursor(QCursor(Qt.PointingHandCursor))
        btn_kurs_ata.clicked.connect(self.kurs_atama_islemi)
        
        sag_layout.addWidget(QLabel("2. Atama Yapılacak Kursu Seçin"))
        sag_layout.addWidget(self.liste_atama_kurslar)
        sag_layout.addWidget(btn_kurs_ata)
        sag_cerceve.setLayout(sag_layout)
        
        splitter.addWidget(sol_cerceve)
        splitter.addWidget(sag_cerceve)
        splitter.setSizes([400, 400])
        
        layout.addWidget(QLabel("Öğrenci Kurs Atama İşlemleri"))
        layout.addWidget(splitter)
        self.atama_yonetimi_sekmesi.setLayout(layout)

    def sekme_kayit_silme_olustur(self):
        self.silme_sekmesi = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        
        splitter = QSplitter(Qt.Horizontal)
        
        sol_cerceve = QFrame()
        sol_layout = QVBoxLayout()
        self.liste_silme_ogrenciler = QListWidget()
        self.liste_silme_ogrenciler.clicked.connect(self.silme_icin_ogrenci_secildi)
        sol_layout.addWidget(QLabel("1. İşlem Yapılacak Öğrenciyi Seçin"))
        sol_layout.addWidget(self.liste_silme_ogrenciler)
        sol_cerceve.setLayout(sol_layout)
        
        sag_cerceve = QFrame()
        sag_layout = QVBoxLayout()
        
        btn_tamamen_sil = QPushButton("Seçili Öğrenciyi Sistemden Ve Tüm Kurslardan Sil")
        btn_tamamen_sil.setCursor(QCursor(Qt.PointingHandCursor))
        btn_tamamen_sil.setStyleSheet("background-color: #cf6679; color: #121212;")
        btn_tamamen_sil.clicked.connect(self.tamamen_sil_islemi)
        
        self.liste_silme_kurslar = QListWidget()
        
        btn_kurstan_sil = QPushButton("Öğrenciyi Sadece Seçili Kurstan Sil")
        btn_kurstan_sil.setCursor(QCursor(Qt.PointingHandCursor))
        btn_kurstan_sil.setStyleSheet("background-color: #ffb74d; color: #121212;")
        btn_kurstan_sil.clicked.connect(self.kurstan_sil_islemi)
        
        sag_layout.addWidget(QLabel("Kökten Silme İşlemi"))
        sag_layout.addWidget(btn_tamamen_sil)
        sag_layout.addSpacing(20)
        sag_layout.addWidget(QLabel("2. Öğrencinin Kayıtlı Olduğu Kurslar"))
        sag_layout.addWidget(self.liste_silme_kurslar)
        sag_layout.addWidget(btn_kurstan_sil)
        sag_cerceve.setLayout(sag_layout)
        
        splitter.addWidget(sol_cerceve)
        splitter.addWidget(sag_cerceve)
        splitter.setSizes([300, 500])
        
        layout.addWidget(QLabel("Kayıt Silme İşlemleri Paneli"))
        layout.addWidget(splitter)
        self.silme_sekmesi.setLayout(layout)

    def sekme_ogrenci_raporu_olustur(self):
        self.rapor_sekmesi = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        
        splitter = QSplitter(Qt.Horizontal)
        
        sol_cerceve = QFrame()
        sol_layout = QVBoxLayout()
        self.liste_rapor_ogrenciler = QListWidget()
        self.liste_rapor_ogrenciler.clicked.connect(self.rapor_detay_goster)
        sol_layout.addWidget(QLabel("İncelenecek Öğrenciyi Seçin"))
        sol_layout.addWidget(self.liste_rapor_ogrenciler)
        sol_cerceve.setLayout(sol_layout)
        
        sag_cerceve = QFrame()
        sag_layout = QVBoxLayout()
        self.lbl_rapor_tc = QLabel("Tc Kimlik Numarası: -")
        self.lbl_rapor_ad = QLabel("Ad Soyad: -")
        self.lbl_rapor_email = QLabel("Email Adresi: -")
        self.lbl_rapor_telefon = QLabel("Telefon Numarası: -")
        self.liste_rapor_kurslar = QListWidget()
        
        sag_layout.addWidget(QLabel("Sistem Veritabanı Bilgileri"))
        sag_layout.addWidget(self.lbl_rapor_tc)
        sag_layout.addWidget(self.lbl_rapor_ad)
        sag_layout.addWidget(self.lbl_rapor_email)
        sag_layout.addWidget(self.lbl_rapor_telefon)
        sag_layout.addSpacing(20)
        sag_layout.addWidget(QLabel("Öğrencinin Aktif Olduğu Kurslar"))
        sag_layout.addWidget(self.liste_rapor_kurslar)
        sag_cerceve.setLayout(sag_layout)
        
        splitter.addWidget(sol_cerceve)
        splitter.addWidget(sag_cerceve)
        splitter.setSizes([300, 500])
        
        layout.addWidget(QLabel("Gelişmiş Öğrenci Arama Ve Detay Raporu"))
        layout.addWidget(splitter)
        self.rapor_sekmesi.setLayout(layout)

    def sekme_degistir(self, indeks):
        self.icerik_alani.setCurrentIndex(indeks)

    def login_denemesi(self):
        kullanici = self.user_input.text()
        sifre = self.pass_input.text()
        
        unvan_kontrol, unvan = self.sistem.giris_kontrol(kullanici, sifre)
        
        if unvan_kontrol:
            self.sayfa_yoneticisi.setCurrentIndex(1)
            self.resize(1100, 750) 
            self.ekran_verilerini_tazele()
        else:
            QMessageBox.critical(self, "Hata", "Geçersiz Müdür Kimlik Bilgileri")

    def ekran_verilerini_tazele(self):
        self.guncel_ogrenciler = self.sistem.tum_ogrencileri_getir()
        self.guncel_kurslar = self.sistem.tum_kurslari_getir()
        
        self.etiket_yonetici.setText(f"Platform Genel Durumu | Veritabanı Kayıtlı Öğrenci: {len(self.guncel_ogrenciler)}")
        
        self.liste_tum_ogrenciler.clear()
        self.liste_atama_ogrenciler.clear()
        self.liste_silme_ogrenciler.clear()
        self.liste_rapor_ogrenciler.clear()
        self.liste_silme_kurslar.clear()
        
        for o in self.guncel_ogrenciler:
            ogrenci_bilgi = f"{o.tc_no} | {o.ad}"
            self.liste_tum_ogrenciler.addItem(ogrenci_bilgi)
            self.liste_atama_ogrenciler.addItem(ogrenci_bilgi)
            self.liste_silme_ogrenciler.addItem(ogrenci_bilgi)
            self.liste_rapor_ogrenciler.addItem(ogrenci_bilgi)
        
        self.liste_atama_kurslar.clear()
        for k in self.guncel_kurslar:
            self.liste_atama_kurslar.addItem(f"{k.kurs_adi} | Eğitmen: {k.egitmen.ad} | Doluluk: {k.kayitli_ogrenci_sayisi}/{k.kontenjan}")

    def yeni_ogrenci_islemi(self):
        tc_no = self.input_ogrenci_tc.text().strip()
        ad = self.input_ogrenci_ad.text().strip()
        email = self.input_ogrenci_email.text().strip()
        telefon = self.input_ogrenci_tel.text().strip()
        
        # 1. tc kimlik numarasi dogrulamasi (11 hane ve sadece rakam)
        if not tc_no.isdigit() or len(tc_no) != 11:
            QMessageBox.warning(self, "Hata", "Tc Kimlik Numarası Tam Olarak 11 Haneli Bir Rakam Olmalıdır.")
            return
            
        # 2. ad soyad dogrulamasi (sadece harf ve bosluk, rakam yok)
        ad_harf_kontrolu = ad.replace(" ", "")
        if not ad_harf_kontrolu.isalpha():
            QMessageBox.warning(self, "Hata", "Ad Ve Soyad Kısmında Rakam Veya Özel Karakter Kullanılamaz.")
            return
            
        # 3. email dogrulamasi (@ isareti var mi)
        if "@" not in email:
            QMessageBox.warning(self, "Hata", "Geçersiz Email Adresi. Lütfen @ İşaretini Kullanın.")
            return
            
        # 4. telefon numarasi dogrulamasi (sadece rakam ve 11 hane)
        if not telefon.isdigit() or len(telefon) != 11:
            QMessageBox.warning(self, "Hata", "Telefon Numarası Tam Olarak 11 Haneli Bir Rakam Olmalıdır.")
            return
            
        kontrol, mesaj = self.sistem.ogrenci_olustur(tc_no, ad, email, telefon)
        
        if kontrol:
            QMessageBox.information(self, "Başarılı", mesaj)
            self.ekran_verilerini_tazele()
            self.input_ogrenci_tc.clear()
            self.input_ogrenci_ad.clear()
            self.input_ogrenci_email.clear()
            self.input_ogrenci_tel.clear()
        else:
            QMessageBox.critical(self, "Hata", mesaj)

    def kurs_atama_islemi(self):
        ogrenci_indeks = self.liste_atama_ogrenciler.currentRow()
        kurs_indeks = self.liste_atama_kurslar.currentRow()
        
        if ogrenci_indeks >= 0 and kurs_indeks >= 0:
            ogrenci = self.guncel_ogrenciler[ogrenci_indeks]
            kurs = self.guncel_kurslar[kurs_indeks]
            
            kontrol, mesaj = self.sistem.ogrenci_kursa_kaydet(ogrenci.tc_no, kurs.kurs_id)
            if kontrol:
                QMessageBox.information(self, "Durum", mesaj)
            else:
                QMessageBox.warning(self, "Uyarı", mesaj)
                
            self.ekran_verilerini_tazele() 
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen Listelerden Bir Öğrenci Ve Atanacak Bir Kurs Seçin")

    def silme_icin_ogrenci_secildi(self):
        self.liste_silme_kurslar.clear()
        
        secili_indeks = self.liste_silme_ogrenciler.currentRow()
        if secili_indeks >= 0:
            ogrenci = self.guncel_ogrenciler[secili_indeks]
            aktif_kurslar = self.sistem.ogrenci_kurslarini_getir(ogrenci.tc_no)
            for kurs_adi in aktif_kurslar:
                self.liste_silme_kurslar.addItem(kurs_adi)

    def tamamen_sil_islemi(self):
        indeks = self.liste_silme_ogrenciler.currentRow()
        
        if indeks >= 0:
            secili_ogrenci = self.guncel_ogrenciler[indeks]
            cevap = QMessageBox.question(self, "Onay", f"{secili_ogrenci.ad} İsimli Öğrenciyi Tamamen Silmek İstediğinize Emin Misiniz?", QMessageBox.Yes | QMessageBox.No)
            
            if cevap == QMessageBox.Yes:
                kontrol, mesaj = self.sistem.ogrenci_sil(secili_ogrenci.tc_no)
                QMessageBox.information(self, "Durum", mesaj)
                self.ekran_verilerini_tazele()
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen Tamamen Silmek İçin Listeden Bir Öğrenci Seçin")

    def kurstan_sil_islemi(self):
        ogrenci_indeks = self.liste_silme_ogrenciler.currentRow()
        kurs_item = self.liste_silme_kurslar.currentItem()
        
        if ogrenci_indeks >= 0 and kurs_item:
            ogrenci = self.guncel_ogrenciler[ogrenci_indeks]
            secili_kurs_adi = kurs_item.text()
            
            kontrol, mesaj = self.sistem.ogrenci_kurstan_cikar(ogrenci.tc_no, secili_kurs_adi)
            QMessageBox.information(self, "Durum", mesaj)
            
            self.ekran_verilerini_tazele()
            self.silme_icin_ogrenci_secildi()
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen Listelerden Öğrenci Ve Silinecek Bir Kurs Seçin")

    def rapor_detay_goster(self):
        indeks = self.liste_rapor_ogrenciler.currentRow()
        if indeks >= 0:
            ogr = self.guncel_ogrenciler[indeks]
            self.lbl_rapor_tc.setText(f"Tc Kimlik Numarası: {ogr.tc_no}")
            self.lbl_rapor_ad.setText(f"Ad Soyad: {ogr.ad}")
            self.lbl_rapor_email.setText(f"Email Adresi: {ogr.email}")
            self.lbl_rapor_telefon.setText(f"Telefon Numarası: {ogr.telefon}")
            
            aktif_kurslar = self.sistem.ogrenci_kurslarini_getir(ogr.tc_no)
            self.liste_rapor_kurslar.clear()
            for k in aktif_kurslar:
                self.liste_rapor_kurslar.addItem(k)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    backend_sistem = KursSistemi()
    ana_pencere = PlatformArayuzu(backend_sistem)
    ana_pencere.show()
    sys.exit(app.exec_())