import sys

from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QColor, QIntValidator, QRegularExpressionValidator

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QFrame,
    QStackedWidget, QHeaderView, QLineEdit, QDoubleSpinBox, QMessageBox,
    QGraphicsDropShadowEffect, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from crm_backend import CRMYoneticisi

# ── TASARIM PALETİ (Ferah Açık Tema - Clean White & Indigo) ─────────────────────
C = {
    "bg": "#F8FAFC",          # Açık gri/mavi arka plan
    "sidebar": "#FFFFFF",     # Bembeyaz yan menü
    "card": "#FFFFFF",        # Bembeyaz kartlar
    "border": "#E2E8F0",      # Çok hafif gri çizgiler
    "accent": "#4F46E5",      # Kurumsal Çivit Mavisi (İndigo)
    "accent_hover": "#4338CA",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "text": "#1E293B",        # Koyu gri/siyah okunaklı metin
    "text_sub": "#64748B",    # Soluk gri alt metinler
    "input_bg": "#F1F5F9"     # Açık gri veri giriş kutuları
}

def card_ss(): return f"background:{C['card']}; border:1px solid {C['border']}; border-radius:12px;"
def btn_primary_ss(): return f"QPushButton{{background:{C['accent']}; color:#ffffff; border-radius:8px; padding:10px; font-weight:bold;}} QPushButton:hover{{background:{C['accent_hover']};}}"
def input_ss(): return f"QLineEdit, QDoubleSpinBox{{background:{C['input_bg']}; color:{C['text']}; border:1px solid {C['border']}; border-radius:8px; padding:8px;}}"

# Tabloyu açık temaya özel, temiz başlıklı yapıyoruz
TABLE_SS = f"""
QTableWidget {{ background:{C['card']}; color:{C['text']}; border:none; gridline-color:{C['border']}; }} 
QTableWidget::item {{ padding:10px; border-bottom:1px solid {C['border']}; }}
QHeaderView::section {{ background:{C['input_bg']}; color:{C['text_sub']}; font-weight:bold; padding:8px; border:none; border-bottom:2px solid {C['border']}; }}
"""

def shadow(widget):
    # Açık temada gölgeler çok daha yumuşak ve zarif olmalı (Alpha: 15)
    fx = QGraphicsDropShadowEffect(widget)
    fx.setBlurRadius(25); fx.setColor(QColor(0, 0, 0, 15)); fx.setOffset(0, 4)
    widget.setGraphicsEffect(fx)

class SideBtn(QPushButton):
    def __init__(self, ikon, metin):
        super().__init__(f"  {ikon}  {metin}")
        self.setCheckable(True); self.setFixedHeight(50); self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._refresh(False)

    def _refresh(self, aktif):
        if aktif: self.setStyleSheet(f"QPushButton{{background:#EEF2FF; color:{C['accent']}; border:none; border-left:4px solid {C['accent']}; text-align:left; padding-left:15px; font-weight:bold; border-radius:0px;}}")
        else: self.setStyleSheet(f"QPushButton{{background:transparent; color:{C['text_sub']}; border:none; text-align:left; padding-left:15px; font-weight:bold; border-radius:0px;}} QPushButton:hover{{color:{C['text']}; background:#F8FAFC;}}")
    def setChecked(self, v): super().setChecked(v); self._refresh(v)

# ── SAYFALAR ──────────────────────────────────────────────

class DashboardPage(QWidget):
    def __init__(self, sistem):
        super().__init__()
        self.sistem = sistem
        self._build()

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(35, 30, 35, 30)
        
        # Üst Kısım: Müşteriler ve Satışlar Yan Yana
        ust_lay = QHBoxLayout()
        
        # Müşteriler Tablosu
        mus_widget = QWidget(); mus_lay = QVBoxLayout(mus_widget); mus_lay.setContentsMargins(0,0,0,0)
        lbl1 = QLabel("👥 Kayıtlı Müşteriler"); lbl1.setStyleSheet(f"color:{C['text']}; font-size:16px; font-weight:bold;")
        mus_lay.addWidget(lbl1)
        self.t_mus = QTableWidget(); self.t_mus.setColumnCount(3)
        self.t_mus.setHorizontalHeaderLabels(["ID", "Ad Soyad", "Telefon"])
        self.t_mus.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.t_mus.setStyleSheet(TABLE_SS)
        mus_lay.addWidget(self.t_mus); ust_lay.addWidget(mus_widget)

        # Satışlar Tablosu
        sat_widget = QWidget(); sat_lay = QVBoxLayout(sat_widget); sat_lay.setContentsMargins(0,0,0,0)
        lbl2 = QLabel("💰 Son Satışlar"); lbl2.setStyleSheet(f"color:{C['text']}; font-size:16px; font-weight:bold;")
        sat_lay.addWidget(lbl2)
        self.t_sat = QTableWidget(); self.t_sat.setColumnCount(4)
        self.t_sat.setHorizontalHeaderLabels(["Satış ID", "Müşteri", "Ürün", "Fiyat"])
        self.t_sat.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.t_sat.setStyleSheet(TABLE_SS)
        sat_lay.addWidget(self.t_sat); ust_lay.addWidget(sat_widget)

        lay.addLayout(ust_lay)
        lay.addSpacing(20)

        # Alt Kısım: Destek Talepleri Tablosu
        lbl3 = QLabel("🎧 Destek Talepleri"); lbl3.setStyleSheet(f"color:{C['text']}; font-size:16px; font-weight:bold;")
        lay.addWidget(lbl3)
        self.t_des = QTableWidget(); self.t_des.setColumnCount(4)
        self.t_des.setHorizontalHeaderLabels(["Talep ID", "Müşteri", "Durum", "Açıklama"])
        self.t_des.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.t_des.setStyleSheet(TABLE_SS)
        lay.addWidget(self.t_des)

    def refresh(self):
        # Müşterileri Yenile
        self.t_mus.setRowCount(0)
        for m_id, mus in self.sistem.musteriler.items():
            r = self.t_mus.rowCount(); self.t_mus.insertRow(r)
            self.t_mus.setItem(r, 0, QTableWidgetItem(str(mus.musteri_id)))
            self.t_mus.setItem(r, 1, QTableWidgetItem(mus.ad))
            self.t_mus.setItem(r, 2, QTableWidgetItem(mus.telefon))

        # Satışları Yenile
        self.t_sat.setRowCount(0)
        for s in self.sistem.satislar:
            r = self.t_sat.rowCount(); self.t_sat.insertRow(r)
            self.t_sat.setItem(r, 0, QTableWidgetItem(str(s.satis_id)))
            self.t_sat.setItem(r, 1, QTableWidgetItem(s.musteri.ad))
            self.t_sat.setItem(r, 2, QTableWidgetItem(s.urun))
            
            fiyat_hucre = QTableWidgetItem(f"₺{s.fiyat:,.2f}")
            fiyat_hucre.setForeground(QColor("#10B981")) # Yeşile boyar
            self.t_sat.setItem(r, 3, fiyat_hucre)

        # Talepleri Yenile
        self.t_des.setRowCount(0)
        for t in self.sistem.destek_talepleri:
            r = self.t_des.rowCount(); self.t_des.insertRow(r)
            self.t_des.setItem(r, 0, QTableWidgetItem(str(t.talep_id)))
            self.t_des.setItem(r, 1, QTableWidgetItem(t.musteri.ad))
            
            durum_hucre = QTableWidgetItem(t.durum)
            durum_hucre.setForeground(QColor(C['danger'])) # Kırmızıya boyar
            self.t_des.setItem(r, 2, durum_hucre)
            
            self.t_des.setItem(r, 3, QTableWidgetItem(t.aciklama))
class IslemPage(QWidget):
    def __init__(self, sistem, dashboard):
        super().__init__()
        self.sistem = sistem; self.dashboard = dashboard; self._build()

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(35, 30, 35, 30)
        lbl = QLabel("⚙️ Veri Girişi"); lbl.setStyleSheet(f"color:{C['text']}; font-size:24px; font-weight:900;")
        lay.addWidget(lbl); lay.addSpacing(20)

        # 1. Müşteri Ekleme Formu
        kart1 = QFrame(); kart1.setStyleSheet(card_ss()); shadow(kart1)
        k1_lay = QHBoxLayout(kart1)
        
        self.i_m_id = QLineEdit(); self.i_m_id.setPlaceholderText("Müşteri ID"); self.i_m_id.setStyleSheet(input_ss())
        self.i_m_id.setValidator(QIntValidator(1, 999999)) # Sadece sayı
        
        self.i_m_ad = QLineEdit(); self.i_m_ad.setPlaceholderText("Ad Soyad"); self.i_m_ad.setStyleSheet(input_ss())
        # Sadece harf ve boşluk
        self.i_m_ad.setValidator(QRegularExpressionValidator(QRegularExpression("^[a-zA-ZğüşıöçĞÜŞİÖÇ ]+$")))
        
        self.i_m_tel = QLineEdit(); self.i_m_tel.setPlaceholderText("Telefon"); self.i_m_tel.setStyleSheet(input_ss())
        # Rakam, boşluk, +, -, parantez kabul eden telefon filtresi
        self.i_m_tel.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[0-9+ ()\-]+$")))
        
        btn_m_ekle = QPushButton("Müşteri Kaydet"); btn_m_ekle.setStyleSheet(btn_primary_ss())
        btn_m_ekle.clicked.connect(self._musteri_ekle)
        k1_lay.addWidget(self.i_m_id); k1_lay.addWidget(self.i_m_ad); k1_lay.addWidget(self.i_m_tel); k1_lay.addWidget(btn_m_ekle)
        lay.addWidget(kart1); lay.addSpacing(15)

        # 2. Satış Yapma Formu
        kart2 = QFrame(); kart2.setStyleSheet(card_ss()); shadow(kart2)
        k2_lay = QHBoxLayout(kart2)
        
        self.i_s_id = QLineEdit(); self.i_s_id.setPlaceholderText("Satış ID"); self.i_s_id.setStyleSheet(input_ss())
        self.i_s_id.setValidator(QIntValidator(1, 999999)) # Sadece sayı
        
        self.i_s_mid = QLineEdit(); self.i_s_mid.setPlaceholderText("Müşteri ID"); self.i_s_mid.setStyleSheet(input_ss())
        self.i_s_mid.setValidator(QIntValidator(1, 999999)) # Sadece sayı
        
        self.i_s_urun = QLineEdit(); self.i_s_urun.setPlaceholderText("Ürün Adı"); self.i_s_urun.setStyleSheet(input_ss())
        # Ürün adında rakam da olabileceği için serbest bırakıyoruz (Örn: Paket 1)
        
        self.i_s_fiyat = QDoubleSpinBox()
        self.i_s_fiyat.setRange(0, 999999); self.i_s_fiyat.setSuffix(" ₺")
        self.i_s_fiyat.setStyleSheet(input_ss() + f" QDoubleSpinBox::up-button{{background:{C['border']};}} QDoubleSpinBox::down-button{{background:{C['border']};}}")
        
        btn_s_yap = QPushButton("Satışı Kaydet")
        btn_s_yap.setStyleSheet(f"QPushButton{{background:#10B981; color:#fff; border-radius:8px; padding:10px; font-weight:bold;}} QPushButton:hover{{background:#059669;}}")
        btn_s_yap.clicked.connect(self._satis_yap)
        
        k2_lay.addWidget(self.i_s_id); k2_lay.addWidget(self.i_s_mid); k2_lay.addWidget(self.i_s_urun); k2_lay.addWidget(self.i_s_fiyat); k2_lay.addWidget(btn_s_yap)
        lay.addWidget(kart2); lay.addSpacing(15)

        # 3. Destek Talebi Formu
        kart3 = QFrame(); kart3.setStyleSheet(card_ss()); shadow(kart3)
        k3_lay = QHBoxLayout(kart3)
        
        self.i_t_id = QLineEdit(); self.i_t_id.setPlaceholderText("Talep ID"); self.i_t_id.setStyleSheet(input_ss())
        self.i_t_id.setValidator(QIntValidator(1, 999999)) # Sadece sayı
        
        self.i_t_mid = QLineEdit(); self.i_t_mid.setPlaceholderText("Müşteri ID"); self.i_t_mid.setStyleSheet(input_ss())
        self.i_t_mid.setValidator(QIntValidator(1, 999999)) # Sadece sayı
        
        self.i_t_aciklama = QLineEdit(); self.i_t_aciklama.setPlaceholderText("Sorun Açıklaması"); self.i_t_aciklama.setStyleSheet(input_ss())
        
        btn_t_olustur = QPushButton("Talep Aç")
        btn_t_olustur.setStyleSheet(f"QPushButton{{background:#EF4444; color:#fff; border-radius:8px; padding:10px; font-weight:bold;}} QPushButton:hover{{background:#DC2626;}}")
        btn_t_olustur.clicked.connect(self._talep_ac)
        
        k3_lay.addWidget(self.i_t_id); k3_lay.addWidget(self.i_t_mid); k3_lay.addWidget(self.i_t_aciklama); k3_lay.addWidget(btn_t_olustur)
        lay.addWidget(kart3); lay.addStretch()

    def _msg(self, tip, baslik, metin):
        dlg = QMessageBox(self); dlg.setWindowTitle(baslik); dlg.setText(metin)
        dlg.setStyleSheet(f"QMessageBox{{background:{C['card']};}} QLabel{{color:{C['text']}; font-size:13px;}} QPushButton{{background:{C['input_bg']}; padding:5px 15px; border-radius:4px; border:1px solid {C['border']};}}")
        if tip == "basari": dlg.setIcon(QMessageBox.Icon.Information)
        else: dlg.setIcon(QMessageBox.Icon.Warning)
        dlg.exec()

    def _musteri_ekle(self):
        try:
            m_id = int(self.i_m_id.text())
            if not self.i_m_ad.text().strip() or not self.i_m_tel.text().strip():
                self._msg("hata", "Hata", "Lütfen tüm alanları doldurun.")
                return
            basari, msg = self.sistem.yeni_musteri_kaydi(m_id, self.i_m_ad.text(), self.i_m_tel.text())
            if basari:
                self.i_m_id.clear(); self.i_m_ad.clear(); self.i_m_tel.clear()
                self.dashboard.refresh()
                self._msg("basari", "Başarılı", msg)
            else: self._msg("hata", "Hata", msg)
        except ValueError: self._msg("hata", "Hata", "Müşteri ID sayı olmalıdır.")

    def _satis_yap(self):
        try:
            s_id = int(self.i_s_id.text())
            m_id = int(self.i_s_mid.text())
            if not self.i_s_urun.text().strip():
                self._msg("hata", "Hata", "Lütfen ürün adını girin.")
                return
            basari, msg = self.sistem.yeni_satis_yap(s_id, m_id, self.i_s_urun.text(), self.i_s_fiyat.value())
            if basari:
                self.i_s_id.clear(); self.i_s_mid.clear(); self.i_s_urun.clear(); self.i_s_fiyat.setValue(0)
                self.dashboard.refresh()
                self._msg("basari", "Başarılı", msg)
            else: self._msg("hata", "Hata", msg)
        except ValueError: self._msg("hata", "Hata", "ID alanlarına sadece sayı giriniz.")

    def _talep_ac(self):
        try:
            t_id = int(self.i_t_id.text())
            m_id = int(self.i_t_mid.text())
            if not self.i_t_aciklama.text().strip():
                self._msg("hata", "Hata", "Lütfen açıklama girin.")
                return
            basari, msg = self.sistem.destek_talebi_olustur(t_id, m_id, self.i_t_aciklama.text())
            if basari:
                self.i_t_id.clear(); self.i_t_mid.clear(); self.i_t_aciklama.clear()
                self.dashboard.refresh()
                self._msg("basari", "Başarılı", msg)
            else: self._msg("hata", "Hata", msg)
        except ValueError: self._msg("hata", "Hata", "ID alanlarına sadece sayı giriniz.")

# ── ANA PENCERE ──────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ÜNAL- CRM Sistemi")
        self.resize(1150, 750)
        self.setStyleSheet(f"QMainWindow{{background:{C['bg']}; color:{C['text']};}}")
        self.sistem = CRMYoneticisi()
        self._build_ui()

    def _build_ui(self):
        merkez = QWidget(); self.setCentralWidget(merkez)
        ana = QHBoxLayout(merkez); ana.setContentsMargins(0, 0, 0, 0); ana.setSpacing(0)

        # Beyaz Yan Menü Tasarımı
        sidebar = QFrame(); sidebar.setFixedWidth(240); sidebar.setStyleSheet(f"background:{C['sidebar']}; border-right:1px solid {C['border']};")
        sb = QVBoxLayout(sidebar); sb.setContentsMargins(0, 20, 0, 20)
        
        t1 = QLabel("ÜNAL CRM Sistemi"); t1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t1.setStyleSheet(f"color:{C['accent']}; font-size:22px; font-weight:900; letter-spacing:1px;")
        sb.addWidget(t1); sb.addSpacing(30)

        self.nav = []
        sayfalar = [("📊", "CRM Paneli"), ("✍️", "Veri Girişi")]
        for ikon, metin in sayfalar:
            btn = SideBtn(ikon, metin); btn.clicked.connect(lambda _, m=metin: self._goto(m))
            sb.addWidget(btn); self.nav.append(btn)
        sb.addStretch(); ana.addWidget(sidebar)

        icerik = QWidget(); il = QVBoxLayout(icerik); il.setContentsMargins(0,0,0,0)
        
        self.stack = QStackedWidget()
        self.p_dashboard = DashboardPage(self.sistem)
        self.p_islem = IslemPage(self.sistem, self.p_dashboard)
        
        for p in [self.p_dashboard, self.p_islem]: self.stack.addWidget(p)
        il.addWidget(self.stack); ana.addWidget(icerik)
        self._goto("CRM Paneli")

    def _goto(self, sayfa):
        idx = {"CRM Paneli": 0, "Veri Girişi": 1}[sayfa]
        self.stack.setCurrentIndex(idx)
        for i, b in enumerate(self.nav): b.setChecked(i == idx)
        if idx == 0: self.p_dashboard.refresh()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
