import sys
import re
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QListWidget, QStackedWidget, QMessageBox, 
                             QFrame, QComboBox, QTextEdit)
from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtCore import Qt

from yemek_sistemi import YemekTarifSistemi

class YemekPlatformuArayuzu(QWidget):
    def __init__(self, sistem_nesnesi):
        super().__init__()
        self.sistem = sistem_nesnesi
        self.pencere_yapilandir()
        self.stil_uygula()

    def pencere_yapilandir(self):
        self.setWindowTitle("Yemek Tarif Platformu - Profesyonel Yönetim Paneli")
        self.resize(1200, 800) # Daha ferah bir görünüm için boyutu biraz artırdık
        self.setFont(QFont("Segoe UI", 11))

        self.ana_layout = QVBoxLayout()
        self.sayfa_yoneticisi = QStackedWidget()

        self.ana_sayfa_hazirla()
        self.sayfa_yoneticisi.addWidget(self.ana_ekran)

        self.ana_layout.addWidget(self.sayfa_yoneticisi)
        self.ana_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.ana_layout)

    def stil_uygula(self):
        # Modern UI/UX Tasarım Kodları (QSS)
        modern_qss = """
        QWidget {
            background-color: #0f172a; /* Slate 900 - Derin arka plan */
            color: #f8fafc; /* Slate 50 - Parlak beyaz metin */
            font-family: 'Segoe UI', system-ui, sans-serif;
        }
        
        /* Sol Menü Arka Planı */
        QFrame#sol_menu {
            background-color: #020617; /* Slate 950 - En koyu ton */
            border-right: 1px solid #1e293b;
        }
        
        QLabel#ana_baslik {
            font-size: 22px;
            font-weight: bold;
            color: #e2e8f0;
            padding: 20px 15px;
            letter-spacing: 1px;
        }
        
        /* Sol Menü Butonları */
        QPushButton#sol_menu_buton {
            background-color: transparent;
            color: #94a3b8; /* Slate 400 - Soluk gri */
            text-align: left;
            padding: 16px 25px;
            font-size: 15px;
            font-weight: 500;
            border: none;
            border-left: 4px solid transparent;
            margin: 2px 0px;
        }
        QPushButton#sol_menu_buton:hover {
            background-color: #1e293b; /* Slate 800 */
            color: #ffffff;
            border-left: 4px solid #6366f1; /* Indigo 500 - Vurgu rengi */
        }
        
        /* Sekme Başlıkları */
        QLabel#sekme_baslik {
            font-size: 18px;
            font-weight: bold;
            color: #818cf8; /* Indigo 400 */
            margin-bottom: 10px;
        }
        
        /* Genel Etiketler */
        QLabel {
            font-size: 14px;
            color: #cbd5e1; /* Slate 300 */
        }
        
        /* Listeler */
        QListWidget {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 10px;
            font-size: 15px;
            outline: none;
        }
        QListWidget::item {
            padding: 16px;
            border-bottom: 1px solid #0f172a;
            border-radius: 6px;
            margin-bottom: 4px;
        }
        QListWidget::item:hover {
            background-color: #334155;
        }
        QListWidget::item:selected {
            background-color: #6366f1;
            color: #ffffff;
            font-weight: bold;
        }
        
        /* Girdi Alanları (Inputlar) */
        QLineEdit, QComboBox, QTextEdit {
            padding: 14px 18px;
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            color: #f8fafc;
            font-size: 14px;
        }
        QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
            border: 1px solid #818cf8;
            background-color: #0f172a;
        }
        QComboBox::drop-down {
            border: none;
            padding-right: 15px;
        }
        QComboBox QAbstractItemView {
            background-color: #1e293b;
            color: #f8fafc;
            selection-background-color: #6366f1;
            border: 1px solid #334155;
            outline: none;
            border-radius: 8px;
        }
        
        /* İşlem Butonları */
        QPushButton#islem_butonu {
            padding: 16px;
            background-color: #4f46e5; /* Indigo 600 */
            color: #ffffff;
            border-radius: 8px;
            font-size: 15px;
            font-weight: bold;
            letter-spacing: 0.5px;
        }
        QPushButton#islem_butonu:hover { 
            background-color: #6366f1; /* Indigo 500 */
        }
        QPushButton#islem_butonu:pressed { 
            background-color: #4338ca; /* Indigo 700 */
        }
        
        /* Yapay Zeka Metin Alanı */
        QTextEdit {
            line-height: 1.6;
            font-size: 15px;
        }
        """
        self.setStyleSheet(modern_qss)

    def ana_sayfa_hazirla(self):
        self.ana_ekran = QWidget()
        layout = QHBoxLayout()
        
        sol_menu = QFrame()
        sol_menu.setObjectName("sol_menu")
        sol_menu.setFixedWidth(280) # Menüyü biraz genişlettik
        sol_layout = QVBoxLayout()
        sol_layout.setContentsMargins(0, 0, 0, 0)
        sol_layout.setSpacing(0)
        
        baslik = QLabel("🍳 TARİF YÖNETİMİ")
        baslik.setObjectName("ana_baslik")
        
        self.btn_tarif_listesi = QPushButton("📋 Tarif Listesi")
        self.btn_yeni_tarif = QPushButton("✨ Yeni Tarif Ekle")
        self.btn_guncelleme = QPushButton("🔄 Tarif Güncelle")
        self.btn_ai_asistan = QPushButton("🤖 AI Tarif Asistanı")
        
        sol_layout.addWidget(baslik)
        sol_layout.addSpacing(10)

        for btn in [self.btn_tarif_listesi, self.btn_yeni_tarif, self.btn_guncelleme, self.btn_ai_asistan]:
            btn.setObjectName("sol_menu_buton")
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            sol_layout.addWidget(btn)

        self.btn_tarif_listesi.clicked.connect(lambda: self.sekme_degistir(0))
        self.btn_yeni_tarif.clicked.connect(lambda: self.sekme_degistir(1))
        self.btn_guncelleme.clicked.connect(lambda: self.sekme_degistir(2))
        self.btn_ai_asistan.clicked.connect(lambda: self.sekme_degistir(3))
        
        sol_layout.addStretch()
        sol_menu.setLayout(sol_layout)

        self.icerik_alani = QStackedWidget()
        
        self.sekme_liste_olustur()
        self.sekme_ekle_olustur()
        self.sekme_guncelle_olustur()
        self.sekme_ai_olustur()
        
        self.icerik_alani.addWidget(self.liste_sekmesi)
        self.icerik_alani.addWidget(self.ekle_sekmesi)
        self.icerik_alani.addWidget(self.guncelle_sekmesi)
        self.icerik_alani.addWidget(self.ai_sekmesi)

        layout.addWidget(sol_menu)
        layout.addWidget(self.icerik_alani)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.ana_ekran.setLayout(layout)
        self.ekran_tazele()

    def sekme_liste_olustur(self):
        self.liste_sekmesi = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(60, 50, 60, 50)
        
        baslik = QLabel("Sistemde Kayıtlı Tüm Tarifler")
        baslik.setObjectName("sekme_baslik")
        
        self.liste_tarifler = QListWidget()
        
        layout.addWidget(baslik)
        layout.addSpacing(15)
        layout.addWidget(self.liste_tarifler)
        self.liste_sekmesi.setLayout(layout)

    def sekme_ekle_olustur(self):
        self.ekle_sekmesi = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(80, 50, 80, 50)
        
        baslik = QLabel("Yeni Tarif Tanımlama Merkezi")
        baslik.setObjectName("sekme_baslik")
        
        self.in_id = QLineEdit()
        self.in_id.setPlaceholderText("Tarif ID (Sadece Rakam, Örn: 6)")
        
        self.in_ad = QLineEdit()
        self.in_ad.setPlaceholderText("Tarif Adı (Sadece Harf, Örn: İskender)")
        
        self.in_kat = QComboBox()
        self.in_kat.addItems(["Çorba", "Ana Yemek", "Ara Sıcak", "Zeytinyağlı", "Salata", "Tatlı", "İçecek"])
        
        self.in_sure = QLineEdit()
        self.in_sure.setPlaceholderText("Hazırlama Süresi (Sadece Rakam, Örn: 45)")
        
        btn = QPushButton("Tarifi Veritabanına Kaydet")
        btn.setObjectName("islem_butonu")
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.clicked.connect(self.tarif_kaydet_islem)
        
        layout.addWidget(baslik)
        layout.addSpacing(25)
        layout.addWidget(QLabel("Benzersiz Kimlik (ID)"))
        layout.addWidget(self.in_id)
        layout.addSpacing(15)
        layout.addWidget(QLabel("Yemek Adı"))
        layout.addWidget(self.in_ad)
        layout.addSpacing(15)
        layout.addWidget(QLabel("Yemek Kategorisi"))
        layout.addWidget(self.in_kat)
        layout.addSpacing(15)
        layout.addWidget(QLabel("Hazırlama Süresi (Dakika)"))
        layout.addWidget(self.in_sure)
        layout.addSpacing(35)
        layout.addWidget(btn)
        layout.addStretch()
        self.ekle_sekmesi.setLayout(layout)

    def sekme_guncelle_olustur(self):
        self.guncelle_sekmesi = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(80, 50, 80, 50)
        
        baslik = QLabel("Mevcut Tarif Konfigürasyonu (Güncelleme)")
        baslik.setObjectName("sekme_baslik")
        
        self.in_guncel_id = QLineEdit()
        self.in_guncel_id.setPlaceholderText("Güncellenecek Tarifin ID'sini Girin")
        
        self.in_yeni_ad = QLineEdit()
        self.in_yeni_ad.setPlaceholderText("Yeni Tarif Adını Girin (Sadece Harf)")
        
        self.in_yeni_sure = QLineEdit()
        self.in_yeni_sure.setPlaceholderText("Yeni Hazırlama Süresini Girin (Dakika)")
        
        btn = QPushButton("Tarif Bilgilerini Güncelle")
        btn.setObjectName("islem_butonu")
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.clicked.connect(self.tarif_guncelle_islem)
        
        layout.addWidget(baslik)
        layout.addSpacing(25)
        layout.addWidget(QLabel("Hedef Tarif ID"))
        layout.addWidget(self.in_guncel_id)
        layout.addSpacing(15)
        layout.addWidget(QLabel("Yeni Yemek Adı"))
        layout.addWidget(self.in_yeni_ad)
        layout.addSpacing(15)
        layout.addWidget(QLabel("Yeni Süre (Dakika)"))
        layout.addWidget(self.in_yeni_sure)
        layout.addSpacing(35)
        layout.addWidget(btn)
        layout.addStretch()
        self.guncelle_sekmesi.setLayout(layout)

    def sekme_ai_olustur(self):
        self.ai_sekmesi = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(60, 40, 60, 40)
        
        baslik_liste = QLabel("Sistemde Kayıtlı Olan Hızlı Tarifler")
        baslik_liste.setObjectName("sekme_baslik")
        
        self.liste_ai_tarifler = QListWidget()
        self.liste_ai_tarifler.setMaximumHeight(160)
        self.liste_ai_tarifler.clicked.connect(self.ai_listeden_secim_yap)
        
        baslik_sorgu = QLabel("Manuel Tarif Sorgulama Alanı")
        baslik_sorgu.setObjectName("sekme_baslik")
        
        self.in_ai_yemek = QLineEdit()
        self.in_ai_yemek.setPlaceholderText("Hangi yemeğin tarifini istiyorsun? (Listeden seçebilir veya buraya yazabilirsiniz)")
        
        btn_ai_sor = QPushButton("Yapay Zeka Aşçıya Sor")
        btn_ai_sor.setObjectName("islem_butonu")
        btn_ai_sor.setCursor(QCursor(Qt.PointingHandCursor))
        btn_ai_sor.clicked.connect(self.ai_sistemi_tetikle)
        
        self.out_ai_cevap = QTextEdit()
        self.out_ai_cevap.setReadOnly(True)
        self.out_ai_cevap.setPlaceholderText("✨ Yapay zekanın üreteceği profesyonel tarif burada görüntülenecektir...")
        
        layout.addWidget(baslik_liste)
        layout.addWidget(self.liste_ai_tarifler)
        layout.addSpacing(25)
        layout.addWidget(baslik_sorgu)
        layout.addWidget(self.in_ai_yemek)
        layout.addSpacing(15)
        layout.addWidget(btn_ai_sor)
        layout.addSpacing(20)
        layout.addWidget(self.out_ai_cevap)
        
        self.ai_sekmesi.setLayout(layout)

    def sekme_degistir(self, i):
        self.icerik_alani.setCurrentIndex(i)

    def ekran_tazele(self):
        self.liste_tarifler.clear()
        self.liste_ai_tarifler.clear()
        
        tarifler = self.sistem.tum_tarifleri_getir()
        for t in tarifler:
            # Daha şık bir formatta verileri ekliyoruz
            self.liste_tarifler.addItem(f"#{t[0]}  |  🍲 {t[1]}   —   Kategori: {t[2]}   —   ⏱ {t[3]} Dk.")
            self.liste_ai_tarifler.addItem(f"🍽️ {t[1]}")

    def ai_listeden_secim_yap(self):
        secili_satir = self.liste_ai_tarifler.currentItem()
        if secili_satir:
            # Baştaki emojiyi temizleyerek text box'a atıyoruz
            temiz_isim = secili_satir.text().replace("🍽️ ", "")
            self.in_ai_yemek.setText(temiz_isim)

    def tarif_kaydet_islem(self):
        id_metni = self.in_id.text().strip()
        sure_metni = self.in_sure.text().strip()
        ad_metni = self.in_ad.text().strip()
        
        if not id_metni.isdigit():
            QMessageBox.warning(self, "Veri Doğrulama Hatası", "Tarif ID alanı sadece rakamlardan oluşmalıdır.")
            return
            
        if not sure_metni.isdigit():
            QMessageBox.warning(self, "Veri Doğrulama Hatası", "Süre alanı sadece rakamlardan oluşmalıdır.")
            return
            
        if not re.match(r"^[A-Za-zÇçĞğİıÖöŞşÜü\s]+$", ad_metni):
            QMessageBox.warning(self, "Veri Doğrulama Hatası", "Tarif adı içerisinde rakam veya özel karakter bulunamaz, sadece harf kullanınız.")
            return

        kategori_secimi = self.in_kat.currentText()
        res, msg = self.sistem.tarif_ekle(int(id_metni), ad_metni, kategori_secimi, int(sure_metni))
        
        if res:
            QMessageBox.information(self, "Sistem Bilgisi", msg)
            self.ekran_tazele()
            self.in_id.clear()
            self.in_ad.clear()
            self.in_kat.setCurrentIndex(0)
            self.in_sure.clear()
        else:
            QMessageBox.critical(self, "Sistem Hatası", msg)

    def tarif_guncelle_islem(self):
        id_metni = self.in_guncel_id.text().strip()
        sure_metni = self.in_yeni_sure.text().strip()
        ad_metni = self.in_yeni_ad.text().strip()
        
        if not id_metni.isdigit():
            QMessageBox.warning(self, "Veri Doğrulama Hatası", "Güncellenecek Tarif ID alanı sadece rakamlardan oluşmalıdır.")
            return
            
        if not sure_metni.isdigit():
            QMessageBox.warning(self, "Veri Doğrulama Hatası", "Yeni süre alanı sadece rakamlardan oluşmalıdır.")
            return
            
        if not re.match(r"^[A-Za-zÇçĞğİıÖöŞşÜü\s]+$", ad_metni):
            QMessageBox.warning(self, "Veri Doğrulama Hatası", "Yeni tarif adı içerisinde rakam veya özel karakter bulunamaz, sadece harf kullanınız.")
            return
            
        res, msg = self.sistem.tarif_guncelle(int(id_metni), ad_metni, int(sure_metni))
        
        if res:
            QMessageBox.information(self, "Sistem Bilgisi", msg)
            self.ekran_tazele()
            self.in_guncel_id.clear()
            self.in_yeni_ad.clear()
            self.in_yeni_sure.clear()
        else:
            QMessageBox.critical(self, "Sistem Hatası", msg)

    def ai_sistemi_tetikle(self):
        aranan_yemek = self.in_ai_yemek.text().strip()
        
        if aranan_yemek == "":
            QMessageBox.warning(self, "Sistem Uyarısı", "Lütfen bir yemek adı yazınız veya listeden seçiniz.")
            return
            
        self.out_ai_cevap.setText("⏳ Yapay Zeka Aşçı tarifi özenle hazırlıyor, lütfen bekleyin...")
        QApplication.processEvents() 
        
        basarili_mi, cevap_metni = self.sistem.ai_tarif_uret(aranan_yemek)
        
        if basarili_mi:
            self.out_ai_cevap.setText(cevap_metni)
        else:
            self.out_ai_cevap.setText(cevap_metni)
            QMessageBox.critical(self, "Bağlantı Hatası", "Tarif üretilirken bir sorun oluştu.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    backend = YemekTarifSistemi()
    pencere = YemekPlatformuArayuzu(backend)
    pencere.show()
    sys.exit(app.exec_())