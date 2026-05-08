import sys

from PyQt6.QtGui import QColor, QIntValidator, QRegularExpressionValidator
from PyQt6.QtCore import Qt, QRegularExpression

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QFrame,
    QStackedWidget, QHeaderView, QLineEdit, QSpinBox, QMessageBox,
    QGraphicsDropShadowEffect, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from arac_backend import SistemYoneticisi

# ── TASARIM PALETİ (Grafit & Zümrüt) ─────────────────────
C = {
    "bg": "#121212", "sidebar": "#1E1E24", "card": "#2A2A35", "border": "#3F3F4E",
    "accent": "#10B981", "accent_hover": "#059669", "warning": "#F59E0B",
    "danger": "#EF4444", "text": "#F3F4F6", "text_sub": "#9CA3AF", "input_bg": "#1F1F28"
}

def card_ss(): return f"background:{C['card']}; border:1px solid {C['border']}; border-radius:10px;"
def btn_primary_ss(): return f"QPushButton{{background:{C['accent']}; color:#fff; border-radius:6px; padding:10px; font-weight:bold;}} QPushButton:hover{{background:{C['accent_hover']};}}"
def input_ss(): return f"QLineEdit, QSpinBox{{background:{C['input_bg']}; color:{C['text']}; border:1px solid {C['border']}; border-radius:6px; padding:8px;}}"
TABLE_SS = f"QTableWidget{{background:{C['card']}; color:{C['text']}; border:none; gridline-color:{C['border']};}} QTableWidget::item{{padding:10px; border-bottom:1px solid {C['border']};}}"

def shadow(widget):
    fx = QGraphicsDropShadowEffect(widget)
    fx.setBlurRadius(20); fx.setColor(QColor(0, 0, 0, 100)); fx.setOffset(0, 5)
    widget.setGraphicsEffect(fx)

class SideBtn(QPushButton):
    def __init__(self, ikon, metin):
        super().__init__(f"  {ikon}  {metin}")
        self.setCheckable(True); self.setFixedHeight(50); self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._refresh(False)

    def _refresh(self, aktif):
        if aktif: self.setStyleSheet(f"QPushButton{{background:rgba(16, 185, 129, 0.1); color:{C['accent']}; border:none; border-left:4px solid {C['accent']}; text-align:left; padding-left:15px; font-weight:bold;}}")
        else: self.setStyleSheet(f"QPushButton{{background:transparent; color:{C['text_sub']}; border:none; text-align:left; padding-left:15px; font-weight:bold;}} QPushButton:hover{{color:{C['text']};}}")
    def setChecked(self, v): super().setChecked(v); self._refresh(v)

# ── SAYFALAR ──────────────────────────────────────────────
class DashboardPage(QWidget):
    def __init__(self, sistem):
        super().__init__()
        self.sistem = sistem
        self._build()

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(30, 30, 30, 30)
        
        # --- Üst Kısım: Araçlar ve Müşteriler ---
        ust_lay = QHBoxLayout()
        
        arac_widget = QWidget()
        arac_lay = QVBoxLayout(arac_widget); arac_lay.setContentsMargins(0,0,0,0)
        lbl1 = QLabel("🚘 Araç Durumu"); lbl1.setStyleSheet(f"color:{C['text']}; font-size:16px; font-weight:bold;")
        arac_lay.addWidget(lbl1)
        self.t_arac = QTableWidget()
        self.t_arac.setColumnCount(4)
        self.t_arac.setHorizontalHeaderLabels(["ID", "Araç", "KM", "Durum"])
        self.t_arac.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.t_arac.setStyleSheet(TABLE_SS)
        arac_lay.addWidget(self.t_arac)
        ust_lay.addWidget(arac_widget)

        mus_widget = QWidget()
        mus_lay = QVBoxLayout(mus_widget); mus_lay.setContentsMargins(0,0,0,0)
        lbl_mus = QLabel("👥 Kayıtlı Müşteriler"); lbl_mus.setStyleSheet(f"color:{C['text']}; font-size:16px; font-weight:bold;")
        mus_lay.addWidget(lbl_mus)
        self.t_mus = QTableWidget()
        self.t_mus.setColumnCount(3)
        self.t_mus.setHorizontalHeaderLabels(["ID", "Ad Soyad", "Ehliyet No"])
        self.t_mus.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.t_mus.setStyleSheet(TABLE_SS)
        mus_lay.addWidget(self.t_mus)
        ust_lay.addWidget(mus_widget)

        lay.addLayout(ust_lay)
        lay.addSpacing(15)

        # --- Alt Kısım: Kiralama İşlemleri ---
        lbl2 = QLabel("⏱️ Kiralama İşlemleri ve Saat Kayıtları"); lbl2.setStyleSheet(f"color:{C['text']}; font-size:16px; font-weight:bold;")
        lay.addWidget(lbl2)
        self.t_kir = QTableWidget()
        self.t_kir.setColumnCount(5)
        self.t_kir.setHorizontalHeaderLabels(["Kayıt No", "Araç", "Müşteri (Ehliyet)", "Başlangıç Saati", "Bitiş Saati"])
        self.t_kir.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.t_kir.setStyleSheet(TABLE_SS)
        lay.addWidget(self.t_kir)

    def refresh(self):
        self.t_arac.setRowCount(0)
        for a_id, arac in self.sistem.araclar.items():
            r = self.t_arac.rowCount(); self.t_arac.insertRow(r)
            self.t_arac.setItem(r, 0, QTableWidgetItem(str(arac.arac_id)))
            self.t_arac.setItem(r, 1, QTableWidgetItem(f"{arac.marka} {arac.model}"))
            self.t_arac.setItem(r, 2, QTableWidgetItem(f"{arac.kilometre:,}"))
            durum = "🟢 Müsait" if arac.musait_mi else "🔴 Kirada"
            self.t_arac.setItem(r, 3, QTableWidgetItem(durum))

        self.t_mus.setRowCount(0)
        for k_id, kul in self.sistem.kullanicilar.items():
            r = self.t_mus.rowCount(); self.t_mus.insertRow(r)
            self.t_mus.setItem(r, 0, QTableWidgetItem(str(kul.kullanici_id)))
            self.t_mus.setItem(r, 1, QTableWidgetItem(kul.ad))
            self.t_mus.setItem(r, 2, QTableWidgetItem(kul.ehliyet_no))

        self.t_kir.setRowCount(0)
        for k in self.sistem.kiralamalar:
            r = self.t_kir.rowCount(); self.t_kir.insertRow(r)
            bas = k.baslangic_saati.strftime("%d.%m.%Y %H:%M:%S") if k.baslangic_saati else "-"
            bit = k.bitis_saati.strftime("%d.%m.%Y %H:%M:%S") if k.bitis_saati else "⌛ Devam Ediyor..."
            self.t_kir.setItem(r, 0, QTableWidgetItem(str(k.kiralama_id)))
            self.t_kir.setItem(r, 1, QTableWidgetItem(k.arac.marka))
            self.t_kir.setItem(r, 2, QTableWidgetItem(f"{k.kullanici.ad} ({k.kullanici.ehliyet_no})"))
            self.t_kir.setItem(r, 3, QTableWidgetItem(bas))
            self.t_kir.setItem(r, 4, QTableWidgetItem(bit))

class MuseriGirisPage(QWidget):
    def __init__(self, sistem, dashboard):
        super().__init__()
        self.sistem = sistem; self.dashboard = dashboard; self._build()

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(30, 30, 30, 30)
        lbl = QLabel("👤 Yeni Müşteri Ekleme"); lbl.setStyleSheet(f"color:{C['text']}; font-size:22px; font-weight:bold;")
        lay.addWidget(lbl); lay.addSpacing(20)

        kart = QFrame(); kart.setStyleSheet(card_ss()); shadow(kart)
        klay = QGridLayout(kart); klay.setSpacing(15)
        self.i_id = QLineEdit(); self.i_id.setPlaceholderText("ID Belirleyin"); self.i_id.setStyleSheet(input_ss())
        # Sadece sayı girilmesine izin ver (1 ile 999999 arası)
        self.i_id.setValidator(QIntValidator(1, 999999))

        self.i_ad = QLineEdit(); self.i_ad.setPlaceholderText("Müşteri Ad Soyad"); self.i_ad.setStyleSheet(input_ss())
        # Sadece Türkçe/İngilizce harfler ve boşluk girilmesine izin ver
        regex_isim = QRegularExpression("^[a-zA-ZğüşıöçĞÜŞİÖÇ ]+$")
        self.i_ad.setValidator(QRegularExpressionValidator(regex_isim))

        self.i_ehliyet = QLineEdit(); self.i_ehliyet.setPlaceholderText("Ehliyet Numarası"); self.i_ehliyet.setStyleSheet(input_ss())

        klay.addWidget(QLabel("Müşteri ID:", styleSheet=f"color:{C['text_sub']}"), 0, 0)
        klay.addWidget(self.i_id, 1, 0)
        klay.addWidget(QLabel("Ad Soyad:", styleSheet=f"color:{C['text_sub']}"), 0, 1)
        klay.addWidget(self.i_ad, 1, 1)
        klay.addWidget(QLabel("Ehliyet Numarası:", styleSheet=f"color:{C['text_sub']}"), 2, 0)
        klay.addWidget(self.i_ehliyet, 3, 0, 1, 2)

        btn_ekle = QPushButton("Müşteriyi Kaydet"); btn_ekle.setStyleSheet(btn_primary_ss())
        btn_ekle.clicked.connect(self._ekle)
        klay.addWidget(btn_ekle, 4, 0, 1, 2)
        
        lay.addWidget(kart); lay.addStretch()

    def _ekle(self):
        try:
            k_id = int(self.i_id.text())
            if not self.i_ad.text() or not self.i_ehliyet.text():
                QMessageBox.warning(self, "Hata", "Lütfen tüm bilgileri doldurun.")
                return
            basari, msg = self.sistem.yeni_kullanici_ekle(k_id, self.i_ad.text(), self.i_ehliyet.text())
            if basari:
                QMessageBox.information(self, "Başarılı", msg)
                self.i_id.clear(); self.i_ad.clear(); self.i_ehliyet.clear()
                self.dashboard.refresh()
            else:
                QMessageBox.warning(self, "Hata", msg)
        except ValueError:
            QMessageBox.warning(self, "Hata", "Lütfen ID için geçerli bir sayı girin.")

class AracGirisPage(QWidget):
    def __init__(self, sistem, dashboard):
        super().__init__()
        self.sistem = sistem; self.dashboard = dashboard; self._build()
        
    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(30, 30, 30, 30)
        lbl = QLabel("🚘 Yeni Araç Girişi"); lbl.setStyleSheet(f"color:{C['text']}; font-size:22px; font-weight:bold;")
        lay.addWidget(lbl); lay.addSpacing(20)
        kart = QFrame(); kart.setStyleSheet(card_ss()); shadow(kart)
        klay = QGridLayout(kart); klay.setSpacing(15)
        
        self.i_id = QLineEdit(); self.i_id.setPlaceholderText("Araç ID"); self.i_id.setStyleSheet(input_ss())
        self.i_id.setValidator(QIntValidator(1, 999999)) # Sadece sayı
        
        self.i_marka = QLineEdit(); self.i_marka.setPlaceholderText("Marka"); self.i_marka.setStyleSheet(input_ss())
        # Sadece Türkçe/İngilizce harfler ve boşluk girilmesine izin veren kural
        regex_marka = QRegularExpression("^[a-zA-ZğüşıöçĞÜŞİÖÇ ]+$")
        self.i_marka.setValidator(QRegularExpressionValidator(regex_marka))
        
        self.i_model = QLineEdit(); self.i_model.setPlaceholderText("Model"); self.i_model.setStyleSheet(input_ss())
        # Model kısmında rakam ve harf bir arada olabileceği için buraya kısıtlama koymuyoruz.
        
        self.i_km = QLineEdit(); self.i_km.setPlaceholderText("Başlangıç KM"); self.i_km.setStyleSheet(input_ss())
        self.i_km.setValidator(QIntValidator(0, 2000000)) # Sadece sayı
        
        klay.addWidget(QLabel("Araç ID:", styleSheet=f"color:{C['text_sub']}"), 0, 0); klay.addWidget(self.i_id, 1, 0)
        klay.addWidget(QLabel("Marka:", styleSheet=f"color:{C['text_sub']}"), 0, 1); klay.addWidget(self.i_marka, 1, 1)
        klay.addWidget(QLabel("Model:", styleSheet=f"color:{C['text_sub']}"), 2, 0); klay.addWidget(self.i_model, 3, 0)
        klay.addWidget(QLabel("Başlangıç KM:", styleSheet=f"color:{C['text_sub']}"), 2, 1); klay.addWidget(self.i_km, 3, 1)
        
        btn_ekle = QPushButton("Aracı Ekle"); btn_ekle.setStyleSheet(btn_primary_ss()); btn_ekle.clicked.connect(self._ekle)
        klay.addWidget(btn_ekle, 4, 0, 1, 2); lay.addWidget(kart); lay.addStretch()
        
    def _ekle(self):
        try:
            a_id = int(self.i_id.text())
            km = int(self.i_km.text())
            
            # Boş veri gönderilmesini engelleyen kontrol
            if not self.i_marka.text().strip() or not self.i_model.text().strip():
                QMessageBox.warning(self, "Hata", "Lütfen marka ve model kısımlarını boş bırakmayın.")
                return
                
            basari, msg = self.sistem.yeni_arac_ekle(a_id, self.i_marka.text(), self.i_model.text(), km)
            QMessageBox.information(self, "Bilgi", msg)
            if basari: 
                self.i_id.clear(); self.i_marka.clear(); self.i_model.clear(); self.i_km.clear()
                self.dashboard.refresh()
        except ValueError:
            QMessageBox.warning(self, "Hata", "Lütfen ID ve KM için sayısal değerler girin.")

class KiralamaPage(QWidget):
    def __init__(self, sistem, dashboard):
        super().__init__()
        self.sistem = sistem; self.dashboard = dashboard; self._build()
        
    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(30, 30, 30, 30)
        lbl = QLabel("🔄 Araç Çıkış / Dönüş İşlemleri"); lbl.setStyleSheet(f"color:{C['text']}; font-size:22px; font-weight:bold;")
        lay.addWidget(lbl); lay.addSpacing(20)
        
        # --- Çıkış Formu ---
        kart1 = QFrame(); kart1.setStyleSheet(card_ss()); shadow(kart1)
        k1_lay = QHBoxLayout(kart1)
        self.inp_a_id = QLineEdit(); self.inp_a_id.setPlaceholderText("Araç ID Girin"); self.inp_a_id.setStyleSheet(input_ss())
        self.inp_a_id.setValidator(QIntValidator(1, 999999)) # Sadece sayı
        
        self.inp_k_id = QLineEdit(); self.inp_k_id.setPlaceholderText("Müşteri ID Girin"); self.inp_k_id.setStyleSheet(input_ss())
        self.inp_k_id.setValidator(QIntValidator(1, 999999)) # Sadece sayı
        
        btn_cikis = QPushButton("Araç Çıkışı Yap"); btn_cikis.setStyleSheet(btn_primary_ss())
        btn_cikis.clicked.connect(self._cikis_yap)
        
        k1_lay.addWidget(QLabel("Araç ID:", styleSheet=f"color:{C['text_sub']}")); k1_lay.addWidget(self.inp_a_id)
        k1_lay.addWidget(QLabel("Müşteri ID:", styleSheet=f"color:{C['text_sub']}")); k1_lay.addWidget(self.inp_k_id)
        k1_lay.addWidget(btn_cikis); lay.addWidget(kart1); lay.addSpacing(15)
        
        # --- Dönüş Formu ---
        kart2 = QFrame(); kart2.setStyleSheet(card_ss()); shadow(kart2)
        k2_lay = QHBoxLayout(kart2)
        
        self.inp_kir_id = QLineEdit(); self.inp_kir_id.setPlaceholderText("Kayıt No Girin"); self.inp_kir_id.setStyleSheet(input_ss())
        self.inp_kir_id.setValidator(QIntValidator(1, 999999)) # Sadece sayı
        
        self.inp_km = QLineEdit(); self.inp_km.setPlaceholderText("Güncel KM Girin"); self.inp_km.setStyleSheet(input_ss())
        self.inp_km.setValidator(QIntValidator(0, 2000000)) # Sadece sayı
        
        btn_donus = QPushButton("Araç Dönüşü Al"); btn_donus.setStyleSheet(btn_primary_ss().replace(C['accent'], C['warning']).replace(C['accent_hover'], "#D97706"))
        btn_donus.clicked.connect(self._donus_al)
        
        k2_lay.addWidget(QLabel("Kiralama ID:", styleSheet=f"color:{C['text_sub']}")); k2_lay.addWidget(self.inp_kir_id)
        k2_lay.addWidget(QLabel("Güncel KM:", styleSheet=f"color:{C['text_sub']}")); k2_lay.addWidget(self.inp_km)
        k2_lay.addWidget(btn_donus); lay.addWidget(kart2); lay.addStretch()
        
    def _cikis_yap(self):
        try:
            a_id = int(self.inp_a_id.text())
            k_id = int(self.inp_k_id.text())
            basari, msg = self.sistem.arac_cikisi_yap(a_id, k_id)
            QMessageBox.information(self, "Bilgi", msg)
            if basari: 
                self.dashboard.refresh()
                self.inp_a_id.clear() # İşlem sonrası kutuyu temizler
                self.inp_k_id.clear()
        except ValueError:
            QMessageBox.warning(self, "Hata", "Lütfen sadece sayı giriniz!")
            
    def _donus_al(self):
        try:
            kir_id = int(self.inp_kir_id.text())
            km = int(self.inp_km.text())
            basari, msg = self.sistem.arac_donusu_al(kir_id, km)
            QMessageBox.information(self, "Bilgi", msg)
            if basari: 
                self.dashboard.refresh()
                self.inp_kir_id.clear() # İşlem sonrası kutuyu temizler
                self.inp_km.clear()
        except ValueError:
            QMessageBox.warning(self, "Hata", "Lütfen sadece sayı giriniz!")
# ── ANA PENCERE ──────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ÜNAL Araç Yönetim Sistemi")
        self.resize(1150, 750)
        self.setStyleSheet(f"QMainWindow{{background:{C['bg']}; color:{C['text']};}}")
        self.sistem = SistemYoneticisi()
        self._build_ui()

    def _build_ui(self):
        merkez = QWidget(); self.setCentralWidget(merkez)
        ana = QHBoxLayout(merkez); ana.setContentsMargins(0, 0, 0, 0); ana.setSpacing(0)

        sidebar = QFrame(); sidebar.setFixedWidth(240); sidebar.setStyleSheet(f"background:{C['sidebar']};")
        sb = QVBoxLayout(sidebar)
        t1 = QLabel("ÜNAL Araç"); t1.setStyleSheet(f"color:{C['accent']}; font-size:20px; font-weight:900; margin-top:20px;")
        sb.addWidget(t1); sb.addSpacing(30)

        self.nav = []
        sayfalar = [("📊", "Araç Paneli"), ("👥", "Müşteri Ekle"), ("🚘", "Araç Girişi"), ("🔄", "Çıkış / Dönüş")]
        for ikon, metin in sayfalar:
            btn = SideBtn(ikon, metin); btn.clicked.connect(lambda _, m=metin: self._goto(m))
            sb.addWidget(btn); self.nav.append(btn)
        sb.addStretch(); ana.addWidget(sidebar)

        icerik = QWidget(); il = QVBoxLayout(icerik); il.setContentsMargins(0,0,0,0)
        
        self.stack = QStackedWidget()
        self.p_dashboard = DashboardPage(self.sistem)
        self.p_musteri = MuseriGirisPage(self.sistem, self.p_dashboard)
        self.p_giris = AracGirisPage(self.sistem, self.p_dashboard)
        self.p_kiralama = KiralamaPage(self.sistem, self.p_dashboard)
        
        for p in [self.p_dashboard, self.p_musteri, self.p_giris, self.p_kiralama]: self.stack.addWidget(p)
        il.addWidget(self.stack); ana.addWidget(icerik)
        self._goto("Araç Paneli")

    def _goto(self, sayfa):
        idx = {"Araç Paneli": 0, "Müşteri Ekle": 1, "Araç Girişi": 2, "Çıkış / Dönüş": 3}[sayfa]
        self.stack.setCurrentIndex(idx)
        for i, b in enumerate(self.nav): b.setChecked(i == idx)
        if idx == 0: self.p_dashboard.refresh()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
