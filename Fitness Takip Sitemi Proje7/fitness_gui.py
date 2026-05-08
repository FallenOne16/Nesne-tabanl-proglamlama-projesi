import sys
from datetime import date
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QFrame,
    QStackedWidget, QHeaderView, QLineEdit, QGridLayout,
    QSpinBox, QDoubleSpinBox, QMessageBox, QComboBox, QDialog, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from fitness_sistemi import Sporcu, Antrenman, Takip, FitnessDB

# ── Fitness Temalı SaaS Paleti ──
C = {
    "bg": "#F3F4F6", "sidebar": "#FFFFFF", "card": "#FFFFFF", "border": "#E5E7EB",
    "accent": "#0D9488", "accent_hover": "#0F766E", "success": "#10B981", 
    "warning": "#F59E0B", "danger": "#EF4444", "text": "#1F2937", 
    "text_sub": "#6B7280", "row_alt": "#F9FAFB", "row_sel": "#F0FDFA", "input_bg": "#FFFFFF",
}

def card_ss(): return f"background:{C['card']}; border:1px solid {C['border']}; border-radius:12px;"
def btn_primary_ss(): return f"QPushButton{{background:{C['accent']}; color:#fff; border-radius:8px; padding:9px 20px; font-weight:bold;}} QPushButton:hover{{background:{C['accent_hover']};}}"
def btn_success_ss(): return f"QPushButton{{background:{C['success']}; color:#fff; border-radius:8px; padding:9px 20px; font-weight:bold;}}"
def input_ss(): 
    return f"QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{ background:{C['input_bg']}; color:{C['text']}; border:1px solid {C['border']}; border-radius:6px; padding:7px 10px; }}"
TABLE_SS = f"QTableWidget {{ background:{C['card']}; border:1px solid {C['border']}; border-radius:8px; alternate-background-color:{C['row_alt']}; }} QHeaderView::section {{ background:{C['row_alt']}; font-weight:bold; border:none; border-bottom:1px solid {C['border']}; }}"
# Tablo içindeki küçük silme butonları için özel stil
TBL_BTN_SS = f"QPushButton{{background:{C['danger']}; color:white; border-radius:4px; padding:4px 8px; font-weight:bold;}} QPushButton:hover{{background:#DC2626;}}"

def shadow(widget):
    fx = QGraphicsDropShadowEffect(); fx.setBlurRadius(15); fx.setColor(QColor(0,0,0,15)); fx.setOffset(0,2)
    widget.setGraphicsEffect(fx)

class KpiCard(QFrame):
    def __init__(self, baslik, deger, alt, renk):
        super().__init__(); self.setFixedHeight(110); self.setStyleSheet(f"QFrame{{background:{C['card']}; border:1px solid {C['border']}; border-radius:12px; border-left:5px solid {renk};}}"); shadow(self)
        lay = QVBoxLayout(self); lay.setContentsMargins(20, 15, 20, 15)
        l1 = QLabel(baslik.upper()); l1.setStyleSheet(f"color:{C['text_sub']}; font-size:11px; font-weight:bold;")
        l2 = QLabel(str(deger)); l2.setStyleSheet(f"color:{C['text']}; font-size:26px; font-weight:900;")
        l3 = QLabel(alt); l3.setStyleSheet(f"color:{C['text_sub']}; font-size:11px;")
        lay.addWidget(l1); lay.addWidget(l2); lay.addWidget(l3)

class SideBtn(QPushButton):
    def __init__(self, ikon, metin):
        super().__init__(f"   {ikon}   {metin}"); self.setCheckable(True); self.setFixedHeight(45); self.setCursor(Qt.PointingHandCursor); self._refresh(False)
    def _refresh(self, aktif):
        if aktif: self.setStyleSheet(f"QPushButton{{background:{C['row_sel']}; color:{C['accent']}; border:none; border-right:3px solid {C['accent']}; text-align:left; padding-left:20px; font-weight:bold;}}")
        else: self.setStyleSheet(f"QPushButton{{background:transparent; color:{C['text_sub']}; border:none; text-align:left; padding-left:20px; font-weight:500;}}")
    def setChecked(self, v): super().setChecked(v); self._refresh(v)

# ── SAYFALAR ──
class DashboardPage(QWidget):
    def __init__(self, db):
        super().__init__(); self.db = db; self._build()
    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(30, 25, 30, 25); lay.setSpacing(20)
        lbl = QLabel("Aktivite Özeti"); lbl.setStyleSheet("font-size:24px; font-weight:900;"); lay.addWidget(lbl)
        self.kpi_row = QHBoxLayout(); lay.addLayout(self.kpi_row)
        
        # Tabloya 7. Sütun (İşlem) eklendi
        self.tablo = QTableWidget(); self.tablo.setColumnCount(7)
        self.tablo.setHorizontalHeaderLabels(["Kayıt No", "Sporcu", "Antrenman Türü", "Süre (Dk)", "Yakılan Kalori", "Tarih", "İşlem"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents) # Buton sütunu dar kalsın
        self.tablo.setStyleSheet(TABLE_SS)
        lay.addWidget(self.tablo); self.refresh()

    def refresh(self):
        takipler = self.db.get_takipler_detayli(); sporcular = self.db.get_sporcular()
        toplam_kalori = sum(t[4] for t in takipler) if takipler else 0
        
        while self.kpi_row.count():
            item = self.kpi_row.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        self.kpi_row.addWidget(KpiCard("Kayıtlı Sporcu", len(sporcular), "Aktif Üyeler", C['accent']))
        self.kpi_row.addWidget(KpiCard("Toplam Antrenman", len(takipler), "Tamamlanan Seans", C['success']))
        self.kpi_row.addWidget(KpiCard("Yakılan Kalori", f"{toplam_kalori:,.0f} kcal", "Tüm zamanlar", C['warning']))

        self.tablo.setRowCount(0)
        for t in takipler:
            r = self.tablo.rowCount(); self.tablo.insertRow(r)
            self.tablo.setItem(r, 0, QTableWidgetItem(f"#{t[0]}")); self.tablo.setItem(r, 1, QTableWidgetItem(t[1]))
            self.tablo.setItem(r, 2, QTableWidgetItem(t[2])); self.tablo.setItem(r, 3, QTableWidgetItem(f"{t[3]} dk"))
            k_item = QTableWidgetItem(f"{t[4]} kcal"); k_item.setForeground(QColor(C['warning']))
            self.tablo.setItem(r, 4, k_item); self.tablo.setItem(r, 5, QTableWidgetItem(t[5]))
            
            # YENİ: Kayıt Silme Butonu
            btn_sil = QPushButton("🗑️ Sil"); btn_sil.setStyleSheet(TBL_BTN_SS); btn_sil.setCursor(Qt.PointingHandCursor)
            btn_sil.clicked.connect(lambda _, kayit_id=t[0]: self._kayit_sil(kayit_id))
            
            # Butonu hücrenin ortasına hizalamak için küçük bir layout kullanıyoruz
            btn_w = QWidget(); btn_l = QHBoxLayout(btn_w); btn_l.setContentsMargins(5, 2, 5, 2); btn_l.addWidget(btn_sil)
            self.tablo.setCellWidget(r, 6, btn_w)

    def _kayit_sil(self, kayit_id):
        cevap = QMessageBox.question(self, 'Onay Gerekli', f"#{kayit_id} numaralı antrenman kaydını silmek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if cevap == QMessageBox.Yes:
            self.db.takip_sil(kayit_id)
            self.refresh()

class SporcuPage(QWidget):
    def __init__(self, db, dash):
        super().__init__(); self.db, self.dash = dash, dash; self.db_ref = db; self._build()
    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(30, 25, 30, 25)
        lbl = QLabel("Sporcu Yönetimi"); lbl.setStyleSheet("font-size:24px; font-weight:900;"); lay.addWidget(lbl)
        
        h_lay = QHBoxLayout(); h_lay.setSpacing(20)
        
        k1 = QFrame(); k1.setStyleSheet(card_ss()); l1 = QVBoxLayout(k1); l1.addWidget(QLabel("YENİ SPORCU KAYDI"))
        self.i_id = QSpinBox(); self.i_id.setRange(1, 9999); self.i_id.setStyleSheet(input_ss())
        self.i_ad = QLineEdit(); self.i_ad.setPlaceholderText("Ad Soyad"); self.i_ad.setStyleSheet(input_ss())
        self.i_kilo = QDoubleSpinBox(); self.i_kilo.setRange(30, 200); self.i_kilo.setStyleSheet(input_ss())
        self.i_boy = QDoubleSpinBox(); self.i_boy.setRange(100, 250); self.i_boy.setStyleSheet(input_ss())
        l1.addWidget(QLabel("ID")); l1.addWidget(self.i_id); l1.addWidget(QLabel("Ad Soyad")); l1.addWidget(self.i_ad)
        l1.addWidget(QLabel("Kilo (kg)")); l1.addWidget(self.i_kilo); l1.addWidget(QLabel("Boy (cm)")); l1.addWidget(self.i_boy)
        b1 = QPushButton("Kaydet"); b1.setStyleSheet(btn_primary_ss()); b1.clicked.connect(self._ekle); l1.addWidget(b1)
        h_lay.addWidget(k1)

        k2 = QFrame(); k2.setStyleSheet(card_ss()); l2 = QVBoxLayout(k2); l2.addWidget(QLabel("İLERLEME KAYDET (KİLO GÜNCELLE)"))
        self.c_sporcu = QComboBox(); self.c_sporcu.setStyleSheet(input_ss())
        self.g_kilo = QDoubleSpinBox(); self.g_kilo.setRange(30, 200); self.g_kilo.setStyleSheet(input_ss())
        l2.addWidget(QLabel("Sporcu Seçin")); l2.addWidget(self.c_sporcu)
        l2.addWidget(QLabel("Yeni Kilo (kg)")); l2.addWidget(self.g_kilo)
        b2 = QPushButton("Güncelle"); b2.setStyleSheet(btn_success_ss()); b2.clicked.connect(self._ilerleme); l2.addWidget(b2); l2.addStretch()
        h_lay.addWidget(k2); lay.addLayout(h_lay)

        # Tabloya 5. Sütun (İşlem) eklendi
        self.tablo = QTableWidget(); self.tablo.setColumnCount(5)
        self.tablo.setHorizontalHeaderLabels(["ID", "Ad Soyad", "Mevcut Kilo", "Boy", "İşlem"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.tablo.setStyleSheet(TABLE_SS); lay.addWidget(self.tablo)
        self.refresh()

    def refresh(self):
        self.c_sporcu.clear(); sporcular = self.db_ref.get_sporcular(); self.tablo.setRowCount(0)
        for s in sporcular:
            self.c_sporcu.addItem(s.ad, s.sporcu_id)
            r = self.tablo.rowCount(); self.tablo.insertRow(r)
            self.tablo.setItem(r, 0, QTableWidgetItem(str(s.sporcu_id))); self.tablo.setItem(r, 1, QTableWidgetItem(s.ad))
            self.tablo.setItem(r, 2, QTableWidgetItem(f"{s.kilo} kg")); self.tablo.setItem(r, 3, QTableWidgetItem(f"{s.boy} cm"))
            
            # YENİ: Sporcu Silme Butonu
            btn_sil = QPushButton("🗑️ Sil"); btn_sil.setStyleSheet(TBL_BTN_SS); btn_sil.setCursor(Qt.PointingHandCursor)
            btn_sil.clicked.connect(lambda _, s_id=s.sporcu_id, ad=s.ad: self._sporcu_sil(s_id, ad))
            
            btn_w = QWidget(); btn_l = QHBoxLayout(btn_w); btn_l.setContentsMargins(5, 2, 5, 2); btn_l.addWidget(btn_sil)
            self.tablo.setCellWidget(r, 4, btn_w)

    def _ekle(self):
        s = Sporcu(self.i_id.value(), self.i_ad.text(), self.i_kilo.value(), self.i_boy.value())
        ok, msg = self.db_ref.sporcu_ekle(s); QMessageBox.information(self, "Bilgi", msg); self.refresh(); self.dash.refresh()

    def _ilerleme(self):
        if self.c_sporcu.currentData() is None: return
        sporcu_id = self.c_sporcu.currentData()
        sporcular = self.db_ref.get_sporcular()
        secilen = next((s for s in sporcular if s.sporcu_id == sporcu_id), None)
        if secilen:
            ok, msg = secilen.ilerleme_kaydet(self.g_kilo.value(), self.db_ref)
            QMessageBox.information(self, "İlerleme Raporu", msg); self.refresh()
            
    def _sporcu_sil(self, sporcu_id, ad):
        mesaj = f"DİKKAT!\n'{ad}' isimli sporcuyu siliyorsunuz.\n\nBu sporcuya ait geçmiş tüm 'Antrenman Kayıtları' da veritabanından kalıcı olarak silinecektir.\nEmin misiniz?"
        cevap = QMessageBox.question(self, 'Kalıcı Silme Onayı', mesaj, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if cevap == QMessageBox.Yes:
            ok, msg = self.db_ref.sporcu_sil(sporcu_id)
            QMessageBox.information(self, "Silindi", msg)
            self.refresh()
            self.dash.refresh() # Dashboard'daki istatistikleri de güncelle

class TakipPage(QWidget):
    def __init__(self, db, dash):
        super().__init__(); self.db, self.dash = db, dash; self._build()
        
    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(30, 25, 30, 25); lay.setSpacing(20)
        lbl_baslik = QLabel("Antrenman Takibi (Yeni Seans)")
        lbl_baslik.setStyleSheet("font-size:24px; font-weight:900;")
        lay.addWidget(lbl_baslik)
        
        k = QFrame(); k.setStyleSheet(card_ss()); l = QVBoxLayout(k); l.setSpacing(15)
        self.c_spor = QComboBox(); self.c_ant = QComboBox(); self.i_kalori = QDoubleSpinBox(); self.i_kalori.setRange(10, 5000)
        for w in [self.c_spor, self.c_ant, self.i_kalori]: w.setStyleSheet(input_ss()); w.setFixedHeight(40)
        
        l.addWidget(QLabel("Sporcu")); l.addWidget(self.c_spor)
        l.addWidget(QLabel("Yapılan Antrenman")); l.addWidget(self.c_ant)
        l.addWidget(QLabel("Yakılan Kalori Hesaplaması (kcal)")); l.addWidget(self.i_kalori)
        
        btn = QPushButton("Antrenmanı Kaydet"); btn.setStyleSheet(btn_primary_ss()); btn.clicked.connect(self._kaydet)
        l.addWidget(btn); l.addStretch(); lay.addWidget(k); lay.addStretch(); self.refresh()

    def refresh(self):
        self.c_spor.clear(); self.c_ant.clear()
        for s in self.db.get_sporcular(): self.c_spor.addItem(s.ad, s.sporcu_id)
        for a in self.db.get_antrenmanlar(): self.c_ant.addItem(f"{a.tur} ({a.sure} Dk)", a.antrenman_id)

    def _kaydet(self):
        if self.c_spor.currentData() and self.c_ant.currentData():
            ok, msg = self.db.takip_ekle(self.c_spor.currentData(), self.c_ant.currentData(), str(date.today()), self.i_kalori.value())
            QMessageBox.information(self, "Başarılı", msg); self.dash.refresh()

# ── LOGIN EKRANI ──
# ── LOGIN EKRANI ──
class LoginEkrani(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FitTrack Pro Giriş")
        self.setFixedSize(400, 500) # Daha ferah bir pencere boyutu
        self.setStyleSheet(f"QDialog {{ background: {C['bg']}; }}")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 40, 40, 40) # Kenar boşlukları
        lay.setSpacing(15)

        # Logo ve Başlık
        lbl_logo = QLabel("🏃 Fit Z ")
        lbl_logo.setStyleSheet(f"color:{C['accent']}; font-size:32px; font-weight:900;")
        lbl_logo.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl_logo)

        # Alt Bilgi Metni
        lbl_alt = QLabel("Sisteme giriş yapmak için bilgilerinizi girin.")
        lbl_alt.setStyleSheet(f"color:{C['text_sub']}; font-size:13px;")
        lbl_alt.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl_alt)
        
        lay.addSpacing(20)

        # Kullanıcı Adı Alanı
        lbl_user = QLabel("Kullanıcı Adı")
        lbl_user.setStyleSheet(f"color:{C['text']}; font-weight:bold; font-size:13px;")
        lay.addWidget(lbl_user)

        self.u = QLineEdit()
        self.u.setPlaceholderText("Örn: ziya")
        self.u.setStyleSheet(input_ss())
        self.u.setFixedHeight(45)
        lay.addWidget(self.u)

        # Şifre Alanı
        lbl_pass = QLabel("Şifre")
        lbl_pass.setStyleSheet(f"color:{C['text']}; font-weight:bold; font-size:13px;")
        lay.addWidget(lbl_pass)

        self.p = QLineEdit()
        self.p.setPlaceholderText("••••••••")
        self.p.setEchoMode(QLineEdit.Password)
        self.p.setStyleSheet(input_ss())
        self.p.setFixedHeight(45)
        lay.addWidget(self.p)

        lay.addSpacing(20)

        # Giriş Butonu
        btn = QPushButton("Giriş Yap")
        btn.setStyleSheet(f"QPushButton{{background:{C['accent']}; color:#fff; border-radius:8px; padding:12px; font-weight:bold; font-size: 15px;}} QPushButton:hover{{background:{C['accent_hover']};}}")
        btn.setFixedHeight(45)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setDefault(True) # Enter'a basınca direkt giriş yapsın
        btn.clicked.connect(self._login)
        lay.addWidget(btn)

        lay.addStretch()
        
    def _login(self):
        if self.u.text().strip() == "ziya" and self.p.text().strip() == "1234": 
            self.accept()
        else: 
            QMessageBox.warning(self, "Hata", "Kullanıcı adı veya şifre yanlış!")
            self.p.clear() # Hatalı girişte şifre kutusunu temizle

# ── ANA PENCERE ──
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("Fit Z - Fitness Takip Sistemi"); self.resize(1100, 700)
        self.setStyleSheet(f"QMainWindow{{background:{C['bg']}; color:{C['text']};}}"); self.db = self._veri_kur(); self._build()

    def _veri_kur(self):
        db = FitnessDB()
        if not db.get_sporcular():
            db.sporcu_ekle(Sporcu(1, "Ziya Eren", 75.5, 180)); db.sporcu_ekle(Sporcu(2, "Ahmet Yılmaz", 82.0, 175))
            db.antrenman_ekle(Antrenman(101, "Kardiyo (Koşu)", 45)); db.antrenman_ekle(Antrenman(102, "Ağırlık", 60))
        return db

    def _build(self):
        merkez = QWidget(); self.setCentralWidget(merkez); ana = QHBoxLayout(merkez); ana.setContentsMargins(0, 0, 0, 0); ana.setSpacing(0)
        sb = QFrame(); sb.setFixedWidth(240); sb.setStyleSheet(f"background:{C['sidebar']}; border-right:1px solid {C['border']};")
        slay = QVBoxLayout(sb); slay.setContentsMargins(0, 30, 0, 0)
        lbl_logo_side = QLabel(" 🏃 Fit Z"); lbl_logo_side.setStyleSheet(f"color:{C['accent']}; font-size:22px; font-weight:900; margin-bottom:20px;")
        slay.addWidget(lbl_logo_side)
        
        self.nav = []
        for ikon, metin in [("📊", "Genel Bakış"), ("👤", "Sporcu Yönetimi"), ("⏱️", "Antrenman Takibi")]:
            b = SideBtn(ikon, metin); b.clicked.connect(lambda _, m=metin: self._goto(m)); slay.addWidget(b); self.nav.append(b)
        slay.addStretch(); ana.addWidget(sb)

        ic = QWidget(); il = QVBoxLayout(ic); il.setContentsMargins(0,0,0,0); il.setSpacing(0)
        tb = QFrame(); tb.setFixedHeight(65); tb.setStyleSheet(f"background:{C['sidebar']}; border-bottom:1px solid {C['border']};"); tl = QHBoxLayout(tb)
        self.lbl = QLabel("Genel Bakış"); self.lbl.setStyleSheet("font-weight:bold; font-size:14px;"); tl.addWidget(self.lbl); tl.addStretch()
        lbl_user = QLabel("👤 Ziya Eren Yılmaz"); lbl_user.setStyleSheet("font-weight:bold; padding:8px;"); tl.addWidget(lbl_user); il.addWidget(tb)

        self.stack = QStackedWidget(); self.p_dash = DashboardPage(self.db); self.p_sp = SporcuPage(self.db, self.p_dash); self.p_tk = TakipPage(self.db, self.p_dash)
        for p in [self.p_dash, self.p_sp, self.p_tk]: self.stack.addWidget(p)
        il.addWidget(self.stack); ana.addWidget(ic); self._goto("Genel Bakış")

    def _goto(self, s):
        idx = {"Genel Bakış": 0, "Sporcu Yönetimi": 1, "Antrenman Takibi": 2}[s]
        self.stack.setCurrentIndex(idx); self.lbl.setText(s.upper())
        for i, b in enumerate(self.nav): b.setChecked(i == idx)
        if idx == 1: self.p_sp.refresh()
        if idx == 2: self.p_tk.refresh()

if __name__ == "__main__":
    app = QApplication(sys.argv); login = LoginEkrani()
    if login.exec_() == QDialog.Accepted: win = MainWindow(); win.show(); sys.exit(app.exec_())