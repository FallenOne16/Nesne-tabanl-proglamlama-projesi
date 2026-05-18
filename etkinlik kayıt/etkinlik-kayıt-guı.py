import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QFrame,
    QStackedWidget, QHeaderView, QLineEdit, QComboBox, QMessageBox,
    QGraphicsDropShadowEffect, QGridLayout, QDialog, QDateTimeEdit
)
from PyQt6.QtCore import Qt, QDateTime, QDate, QTime
from PyQt6.QtGui import QColor, QFont

# --- 1. VERİTABANI MİMARİSİ (V9.3 - OTOMATİK KAYITLAR TEMİZLENDİ) ---
class Database:
    def __init__(self):
        # Önceki veritabanı ile çakışmasın dersen dosya adını değiştirebilirsin
        self.conn = sqlite3.connect("crimson_v9.db")
        self.cursor = self.conn.cursor()
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS etkinlikler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT,
                baslangic TEXT,
                bitis TEXT
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS biletler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                etkinlik TEXT,
                musteri TEXT,
                mail TEXT,
                yas INTEGER,
                tur TEXT,
                baslangic TEXT,
                bitis TEXT,
                tutar REAL
            )
        """)
        self.conn.commit()
        # BURADAKİ OTOMATİK KAYIT EKLEME KODU KALDIRILDI.

    def etkinlik_ekle(self, ad, baslangic, bitis):
        self.cursor.execute("INSERT INTO etkinlikler (ad, baslangic, bitis) VALUES (?, ?, ?)", (ad, baslangic, bitis))
        self.conn.commit()

    def etkinlik_sil(self, etk_id):
        self.cursor.execute("DELETE FROM etkinlikler WHERE id = ?", (etk_id,))
        self.conn.commit()

    def etkinlik_guncelle(self, etk_id, ad, baslangic, bitis):
        self.cursor.execute("UPDATE etkinlikler SET ad=?, baslangic=?, bitis=? WHERE id=?", (ad, baslangic, bitis, etk_id))
        self.conn.commit()

    def tum_etkinlikler(self):
        self.cursor.execute("SELECT * FROM etkinlikler")
        return self.cursor.fetchall()

    def musteri_bileti_var_mi(self, mail, etkinlik_adi):
        self.cursor.execute("SELECT id FROM biletler WHERE mail = ? AND etkinlik = ?", (mail, etkinlik_adi))
        return self.cursor.fetchone() is not None

    def bilet_ekle(self, etkinlik, musteri, mail, yas, tur, baslangic, bitis, tutar):
        self.cursor.execute("""
            INSERT INTO biletler (etkinlik, musteri, mail, yas, tur, baslangic, bitis, tutar) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (etkinlik, musteri, mail, yas, tur, baslangic, bitis, tutar))
        self.conn.commit()

    def bilet_sil(self, bilet_id):
        self.cursor.execute("DELETE FROM biletler WHERE id = ?", (bilet_id,))
        self.conn.commit()

    def bilet_guncelle(self, bilet_id, musteri, mail, yas, tur, tutar):
        self.cursor.execute("""
            UPDATE biletler 
            SET musteri=?, mail=?, yas=?, tur=?, tutar=? 
            WHERE id=?
        """, (musteri, mail, yas, tur, tutar, bilet_id))
        self.conn.commit()

    def tum_biletler(self):
        self.cursor.execute("SELECT * FROM biletler")
        return self.cursor.fetchall()

    def genel_ozet(self):
        self.cursor.execute("SELECT COUNT(*), SUM(tutar) FROM biletler")
        return self.cursor.fetchone()

# --- TASARIM PALETİ ---
C = {
    "bg": "#000000", "card": "#111111", "border": "#2A2A2A",      
    "accent": "#DC2626", "accent_hover": "#991B1B",
    "text": "#FFFFFF", "text_sub": "#A3A3A3", "input_bg": "#1A1A1A",    
    "danger": "#EF4444", "edit": "#3B82F6", "vip": "#DC2626"
}

def style_card(): return f"background:{C['card']}; border:1px solid {C['border']}; border-radius:12px;"

def style_input(): return f"""
    QLineEdit, QComboBox, QDateTimeEdit {{
        background-color: {C['input_bg']}; color: {C['text']}; 
        border: 1px solid {C['border']}; border-radius: 6px; 
        padding: 12px; font-size: 14px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {C['card']}; color: {C['text']};
        selection-background-color: {C['accent']}; selection-color: #FFFFFF;
    }}
"""

def style_btn(color, hover=C['accent_hover']): return f"QPushButton{{background:{color}; color:#FFFFFF; border-radius:6px; padding:10px; font-weight:bold; font-size:14px;}} QPushButton:hover{{background:{hover};}}"

def add_shadow(widget):
    fx = QGraphicsDropShadowEffect(widget)
    fx.setBlurRadius(25); fx.setColor(QColor(220, 38, 38, 40)); fx.setOffset(0, 4)
    widget.setGraphicsEffect(fx)

t_style = f"""
    QTableWidget {{ background:{C['card']}; color:{C['text']}; border:1px solid {C['border']}; border-radius:8px; outline:none; }}
    QTableWidget::item {{ border-bottom:1px solid {C['border']}; padding-left:10px; }}
    QHeaderView::section {{ background:{C['input_bg']}; color:{C['text_sub']}; font-weight:bold; padding:15px; border:none; border-bottom:2px solid {C['accent']}; }}
"""

class EtkinlikEditDialog(QDialog):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.setWindowTitle("Etkinlik Güncelle")
        self.setFixedSize(400, 350)
        self.setStyleSheet(f"background:{C['bg']}; color:{C['text']};")
        self.data = data 
        self.init_ui()

    def init_ui(self):
        lay = QVBoxLayout(self)
        self.inp_ad = QLineEdit(self.data[1]); self.inp_ad.setStyleSheet(style_input())
        min_dt = QDateTime(QDate(2026, 5, 10), QTime(0, 0))
        self.inp_bas = QDateTimeEdit(QDateTime.fromString(self.data[2], "dd.MM.yyyy HH:mm"))
        self.inp_bas.setDisplayFormat("dd.MM.yyyy HH:mm"); self.inp_bas.setStyleSheet(style_input()); self.inp_bas.setCalendarPopup(True); self.inp_bas.setMinimumDateTime(min_dt)
        self.inp_bit = QDateTimeEdit(QDateTime.fromString(self.data[3], "dd.MM.yyyy HH:mm"))
        self.inp_bit.setDisplayFormat("dd.MM.yyyy HH:mm"); self.inp_bit.setStyleSheet(style_input()); self.inp_bit.setCalendarPopup(True); self.inp_bit.setMinimumDateTime(min_dt)
        btn_save = QPushButton("ETKİNLİĞİ GÜNCELLE"); btn_save.setStyleSheet(style_btn(C['accent'])); btn_save.clicked.connect(self.accept)
        lay.addWidget(QLabel("Etkinlik Adı:")); lay.addWidget(self.inp_ad)
        lay.addWidget(QLabel("Başlangıç Zamanı:")); lay.addWidget(self.inp_bas)
        lay.addWidget(QLabel("Bitiş Zamanı:")); lay.addWidget(self.inp_bit)
        lay.addStretch(); lay.addWidget(btn_save)

    def get_data(self):
        return (self.inp_ad.text().strip(), self.inp_bas.dateTime().toString("dd.MM.yyyy HH:mm"), self.inp_bit.dateTime().toString("dd.MM.yyyy HH:mm"))

class EditDialog(QDialog):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.setWindowTitle("Bilet Güncelleme Paneli")
        self.setFixedSize(400, 450)
        self.setStyleSheet(f"background:{C['bg']}; color:{C['text']};")
        self.data = data 
        self.init_ui()

    def init_ui(self):
        lay = QVBoxLayout(self)
        self.inp_mus = QLineEdit(self.data[2]); self.inp_mus.setStyleSheet(style_input())
        self.inp_mail = QLineEdit(self.data[3]); self.inp_mail.setStyleSheet(style_input())
        self.inp_yas = QLineEdit(str(self.data[4])); self.inp_yas.setStyleSheet(style_input())
        self.cb_tur = QComboBox(); self.cb_tur.addItems(["Standart Bilet", "VIP Kulis Erişimli"]); self.cb_tur.setStyleSheet(style_input())
        self.cb_tur.setCurrentText(self.data[5])
        btn_save = QPushButton("BİLETİ GÜNCELLE"); btn_save.setStyleSheet(style_btn(C['accent'])); btn_save.clicked.connect(self.accept)
        lay.addWidget(QLabel(f"Etkinlik: {self.data[1]} (Değiştirilemez)")); lay.addSpacing(10)
        lay.addWidget(QLabel("Katılımcı:")); lay.addWidget(self.inp_mus)
        lay.addWidget(QLabel("E-Posta:")); lay.addWidget(self.inp_mail)
        lay.addWidget(QLabel("Yaş:")); lay.addWidget(self.inp_yas)
        lay.addWidget(QLabel("Bilet Türü:")); lay.addWidget(self.cb_tur)
        lay.addStretch(); lay.addWidget(btn_save)

    def get_data(self):
        tutar = 1500 if "VIP" in self.cb_tur.currentText() else 500
        return (self.inp_mus.text(), self.inp_mail.text(), int(self.inp_yas.text()), self.cb_tur.currentText(), tutar)

class CrimsonOS(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("Crimson Event Planner | v9.3")
        self.resize(1400, 850)
        self.setStyleSheet(f"QMainWindow {{background:{C['bg']}; color:{C['text']}; font-family: 'Segoe UI';}}")
        self.main_stack = QStackedWidget()
        self.setCentralWidget(self.main_stack)
        self.build_login_screen()
        self.build_admin_app() 
        self.build_user_app()  
        self.main_stack.addWidget(self.login_widget)
        self.main_stack.addWidget(self.admin_widget)
        self.main_stack.addWidget(self.user_widget)

    def build_login_screen(self):
        self.login_widget = QWidget(); lay = QVBoxLayout(self.login_widget)
        h_lay = QHBoxLayout(); h_lay.addStretch()
        kart_user = QFrame(); kart_user.setFixedSize(500, 450); kart_user.setStyleSheet(style_card()); add_shadow(kart_user)
        ku_lay = QVBoxLayout(kart_user); ku_lay.setContentsMargins(40, 40, 40, 40); ku_lay.setSpacing(20)
        lbl_u = QLabel("CRIMSON BİLET PORTALI"); lbl_u.setStyleSheet(f"color:{C['text']}; font-size:32px; font-weight:900;"); lbl_u.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_user = QPushButton("BİLET SATIN AL"); btn_user.setStyleSheet(f"QPushButton{{background:{C['accent']}; color:#FFF; border-radius:8px; padding:20px; font-weight:bold; font-size:18px;}}"); btn_user.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_user.clicked.connect(lambda: self.nav_user())
        ku_lay.addStretch(); ku_lay.addWidget(lbl_u); ku_lay.addSpacing(30); ku_lay.addWidget(btn_user); ku_lay.addStretch()
        h_lay.addWidget(kart_user); h_lay.addSpacing(40)
        kart_admin = QFrame(); kart_admin.setFixedSize(280, 350); kart_admin.setStyleSheet(f"background:#0A0A0A; border:1px solid #222; border-radius:8px;")
        ka_lay = QVBoxLayout(kart_admin); ka_lay.setContentsMargins(20, 20, 20, 20)
        self.inp_user = QLineEdit(); self.inp_user.setPlaceholderText("ID"); self.inp_user.setStyleSheet(style_input())
        self.inp_pass = QLineEdit(); self.inp_pass.setPlaceholderText("Şifre"); self.inp_pass.setEchoMode(QLineEdit.EchoMode.Password); self.inp_pass.setStyleSheet(style_input())
        btn_admin = QPushButton("Giriş"); btn_admin.setStyleSheet(style_btn("#333")); btn_admin.clicked.connect(self.check_admin_login)
        ka_lay.addStretch(); ka_lay.addWidget(QLabel("Personel Girişi", alignment=Qt.AlignmentFlag.AlignCenter)); ka_lay.addWidget(self.inp_user); ka_lay.addWidget(self.inp_pass); ka_lay.addWidget(btn_admin); ka_lay.addStretch()
        h_lay.addWidget(kart_admin, alignment=Qt.AlignmentFlag.AlignVCenter); h_lay.addStretch()
        lay.addStretch(); lay.addLayout(h_lay); lay.addStretch()

    def check_admin_login(self):
        if self.inp_user.text() == "admin" and self.inp_pass.text() == "1234":
            self.main_stack.setCurrentIndex(1); self.refresh_data()
        else: QMessageBox.warning(self, "Hata", "Erişim Reddedildi!")

    def nav_user(self):
        self.refresh_data(); self.main_stack.setCurrentIndex(2)

    def build_admin_app(self):
        self.admin_widget = QWidget(); ana_lay = QHBoxLayout(self.admin_widget); ana_lay.setContentsMargins(0,0,0,0)
        sidebar = QFrame(); sidebar.setFixedWidth(260); sidebar.setStyleSheet(f"background:{C['card']}; border-right:1px solid {C['border']};")
        sb_lay = QVBoxLayout(sidebar); sb_lay.setContentsMargins(0,30,0,20)
        lbl_brand = QLabel("CRIMSON PRO"); lbl_brand.setStyleSheet(f"color:{C['accent']}; font-size:24px; font-weight:900; margin-left:20px;")
        sb_lay.addWidget(lbl_brand); sb_lay.addSpacing(40)
        sayfalar = [("📊", "Dashboard"), ("📅", "Etkinlik Yönetimi"), ("🎟️", "Bilet Gişesi"), ("✏️", "Bilet Veritabanı")]
        for i, (ico, txt) in enumerate(sayfalar):
            btn = QPushButton(f"  {ico}  {txt}"); btn.setFixedHeight(55); btn.setStyleSheet("text-align:left; padding-left:20px; background:transparent; color:#A3A3A3; font-weight:bold; border:none;")
            btn.clicked.connect(lambda _, x=i: self.pages_admin.setCurrentIndex(x)); sb_lay.addWidget(btn)
        sb_lay.addStretch()
        btn_cikis = QPushButton("🚪 Çıkış"); btn_cikis.setStyleSheet("color:#EF4444; background:transparent; border:none; font-weight:bold;"); btn_cikis.clicked.connect(lambda: self.main_stack.setCurrentIndex(0))
        sb_lay.addWidget(btn_cikis); ana_lay.addWidget(sidebar)
        self.pages_admin = QStackedWidget(); ana_lay.addWidget(self.pages_admin)
        self.build_dashboard(); self.build_etkinlik_page(); self.build_gise_page(self.pages_admin, is_admin=True); self.build_duzenle_page()
        self.pages_admin.addWidget(self.page_dash); self.pages_admin.addWidget(self.page_etkinlik); self.pages_admin.addWidget(self.page_gise_admin); self.pages_admin.addWidget(self.page_duzenle)

    def build_etkinlik_page(self):
        self.page_etkinlik = QWidget(); lay = QVBoxLayout(self.page_etkinlik); lay.setContentsMargins(40,40,40,40)
        lay.addWidget(QLabel("Sisteme Yeni Etkinlik Tanımla", styleSheet="font-size:24px; font-weight:bold;")); lay.addSpacing(10)
        form_kart = QFrame(); form_kart.setStyleSheet(style_card()); form_kart.setFixedHeight(150); add_shadow(form_kart)
        f_lay = QHBoxLayout(form_kart); f_lay.setContentsMargins(20,20,20,20)
        min_dt = QDateTime(QDate(2026, 5, 10), QTime(0, 0))
        self.inp_yeni_etk = QLineEdit(); self.inp_yeni_etk.setPlaceholderText("Etkinlik Adı"); self.inp_yeni_etk.setStyleSheet(style_input())
        self.inp_yeni_bas = QDateTimeEdit(min_dt); self.inp_yeni_bas.setDisplayFormat("dd.MM.yyyy HH:mm"); self.inp_yeni_bas.setStyleSheet(style_input()); self.inp_yeni_bas.setCalendarPopup(True); self.inp_yeni_bas.setMinimumDateTime(min_dt)
        self.inp_yeni_bit = QDateTimeEdit(min_dt.addSecs(7200)); self.inp_yeni_bit.setDisplayFormat("dd.MM.yyyy HH:mm"); self.inp_yeni_bit.setStyleSheet(style_input()); self.inp_yeni_bit.setCalendarPopup(True); self.inp_yeni_bit.setMinimumDateTime(min_dt)
        btn_etk_ekle = QPushButton("Etkinliği Başlat"); btn_etk_ekle.setStyleSheet(style_btn(C['accent'])); btn_etk_ekle.clicked.connect(self.yeni_etkinlik_kaydet)
        f_lay.addWidget(self.inp_yeni_etk); f_lay.addWidget(QLabel("Başlangıç:")); f_lay.addWidget(self.inp_yeni_bas); f_lay.addWidget(QLabel("Bitiş:")); f_lay.addWidget(self.inp_yeni_bit); f_lay.addWidget(btn_etk_ekle)
        lay.addWidget(form_kart); lay.addSpacing(20); lay.addWidget(QLabel("Mevcut Etkinlikler", styleSheet="font-size:18px; font-weight:bold; color:#A3A3A3;"))
        self.t_etk = QTableWidget(); self.t_etk.setColumnCount(5); self.t_etk.setHorizontalHeaderLabels(["ID", "Etkinlik Adı", "Başlangıç Saati", "Bitiş Saati", "İşlem"])
        self.t_etk.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); self.t_etk.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents); self.t_etk.setStyleSheet(t_style); self.t_etk.verticalHeader().setVisible(False); self.t_etk.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers); lay.addWidget(self.t_etk)

    def yeni_etkinlik_kaydet(self):
        ad = self.inp_yeni_etk.text().strip(); st = self.inp_yeni_bas.dateTime(); en = self.inp_yeni_bit.dateTime()
        if not ad: QMessageBox.warning(self, "Hata", "Etkinlik adı boş olamaz!"); return
        if st >= en: QMessageBox.critical(self, "Hata", "Bitiş zamanı başlangıçtan önce olamaz!"); return
        self.db.etkinlik_ekle(ad, st.toString("dd.MM.yyyy HH:mm"), en.toString("dd.MM.yyyy HH:mm"))
        self.inp_yeni_etk.clear(); self.refresh_data(); QMessageBox.information(self, "Başarılı", "Etkinlik eklendi!")

    def etkinlik_edit_btn(self, data):
        d = EtkinlikEditDialog(self, data)
        if d.exec():
            n_ad, n_bas, n_bit = d.get_data()
            if not n_ad: QMessageBox.warning(self, "Hata", "Ad boş olamaz!"); return
            dt_bas = QDateTime.fromString(n_bas, "dd.MM.yyyy HH:mm"); dt_bit = QDateTime.fromString(n_bit, "dd.MM.yyyy HH:mm")
            if dt_bas >= dt_bit: QMessageBox.critical(self, "Hata", "Bitiş tarihi başlangıçtan önce olamaz!"); return
            self.db.etkinlik_guncelle(data[0], n_ad, n_bas, n_bit); self.refresh_data()

    def etkinlik_sil_btn(self, eid):
        if QMessageBox.question(self, "Sil", "Emin misiniz?") == QMessageBox.StandardButton.Yes:
            self.db.etkinlik_sil(eid); self.refresh_data()

    def build_user_app(self):
        self.user_widget = QWidget(); lay = QVBoxLayout(self.user_widget); lay.setContentsMargins(0,0,0,0)
        header = QFrame(); header.setFixedHeight(80); header.setStyleSheet(f"background:{C['card']}; border-bottom:1px solid {C['border']};")
        h_lay = QHBoxLayout(header); h_lay.setContentsMargins(30, 0, 30, 0)
        btn_cikis = QPushButton("Geri Dön"); btn_cikis.setStyleSheet(style_btn("#333")); btn_cikis.clicked.connect(lambda: self.main_stack.setCurrentIndex(0))
        h_lay.addWidget(QLabel("CRIMSON TICKETS", styleSheet="font-size:24px; font-weight:bold;")); h_lay.addStretch(); h_lay.addWidget(btn_cikis); lay.addWidget(header)
        self.pages_user = QStackedWidget(); lay.addWidget(self.pages_user); self.build_gise_page(self.pages_user, is_admin=False); self.pages_user.addWidget(self.page_gise_user)

    def build_gise_page(self, container, is_admin):
        page = QWidget(); lay = QVBoxLayout(page); lay.setContentsMargins(50,50,50,50)
        baslik = "Bilet Satış Noktası" if is_admin else "Hızlı Bilet Al"
        lay.addWidget(QLabel(baslik, styleSheet=f"color:{C['text']}; font-size: 28px; font-weight:bold;")); lay.addSpacing(20)
        kart = QFrame(); kart.setStyleSheet(style_card()); add_shadow(kart)
        klay = QGridLayout(kart); klay.setSpacing(20); klay.setContentsMargins(40,40,40,40)
        cb_etk = QComboBox(); cb_etk.setStyleSheet(style_input())
        if is_admin: self.admin_cb_etk = cb_etk
        else: self.user_cb_etk = cb_etk
        inp_mus = QLineEdit(); inp_mus.setPlaceholderText("Ad Soyad"); inp_mus.setStyleSheet(style_input())
        inp_mail = QLineEdit(); inp_mail.setPlaceholderText("E-Posta"); inp_mail.setStyleSheet(style_input())
        inp_yas = QLineEdit(); inp_yas.setPlaceholderText("Yaş"); inp_yas.setStyleSheet(style_input())
        cb_tur = QComboBox(); cb_tur.addItems(["Standart Bilet", "VIP Kulis Erişimli"]); cb_tur.setStyleSheet(style_input())
        lbl_saat = QLabel("Lütfen bir etkinlik seçin..."); lbl_saat.setStyleSheet(f"color:{C['text_sub']}; font-size:16px; background:{C['input_bg']}; padding:12px; border-radius:6px;")
        def update_saat(idx):
            etkinlikler = self.db.tum_etkinlikler()
            if etkinlikler and idx >= 0 and idx < len(etkinlikler):
                bas = etkinlikler[idx][2]; bit = etkinlikler[idx][3]; lbl_saat.setText(f"🕒 Başlangıç: {bas}   |   Bitiş: {bit}")
        cb_etk.currentIndexChanged.connect(update_saat)
        lbl_fiyat = QLabel("Ödenecek Tutar: 500 ₺"); lbl_fiyat.setStyleSheet(f"color:{C['accent']}; font-size:22px; font-weight:bold;")
        cb_tur.currentTextChanged.connect(lambda t: lbl_fiyat.setText(f"Ödenecek Tutar: {'1.500' if 'VIP' in t else '500'} ₺"))
        btn = QPushButton("BİLETİ SATIN AL"); btn.setStyleSheet(style_btn(C['accent'])); btn.setFixedHeight(50); btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda: self.bilet_kes(cb_etk, inp_mus, inp_mail, inp_yas, cb_tur))
        klay.addWidget(QLabel("Etkinlik:"), 0, 0); klay.addWidget(cb_etk, 0, 1, 1, 3); klay.addWidget(QLabel("Takvim:"), 1, 0); klay.addWidget(lbl_saat, 1, 1, 1, 3); klay.addWidget(QLabel("Katılımcı:"), 2, 0); klay.addWidget(inp_mus, 2, 1); klay.addWidget(QLabel("Yaş:"), 2, 2); klay.addWidget(inp_yas, 2, 3); klay.addWidget(QLabel("E-Posta:"), 3, 0); klay.addWidget(inp_mail, 3, 1, 1, 3); klay.addWidget(QLabel("Bilet Türü:"), 4, 0); klay.addWidget(cb_tur, 4, 1, 1, 3); klay.addWidget(lbl_fiyat, 5, 0, 1, 2); klay.addWidget(btn, 5, 2, 1, 2)
        lay.addWidget(kart); lay.addStretch()
        if is_admin: self.page_gise_admin = page
        else: self.page_gise_user = page

    def bilet_kes(self, cb_etk, inp_mus, inp_mail, inp_yas, cb_tur):
        etkinlikler = self.db.tum_etkinlikler()
        if not etkinlikler: QMessageBox.critical(self, "Hata", "Açık etkinlik yok!"); return
        secilen = etkinlikler[cb_etk.currentIndex()]; etk_ad = secilen[1]; st = secilen[2]; en = secilen[3]; mus = inp_mus.text().strip(); mail = inp_mail.text().strip(); yas = inp_yas.text().strip()
        if not mus or not yas or not mail: QMessageBox.warning(self, "Eksik", "Boş bırakmayın!"); return
        if not all(c.isalpha() or c.isspace() for c in mus): QMessageBox.critical(self, "Hata", "İsimde rakam olamaz!"); return
        if not yas.isdigit(): QMessageBox.critical(self, "Hata", "Yaş rakam olmalı!"); return
        if int(yas) < 18: QMessageBox.critical(self, "Reddedildi", "18 yaş sınırı!"); return
        if self.db.musteri_bileti_var_mi(mail, etk_ad): QMessageBox.warning(self, "Mükerrer", "Biletiniz zaten var!"); return
        tutar = 1500 if "VIP" in cb_tur.currentText() else 500
        self.db.bilet_ekle(etk_ad, mus, mail, int(yas), cb_tur.currentText(), st, en, tutar); QMessageBox.information(self, "Başarılı", "Biletiniz onaylandı."); inp_mus.clear(); inp_mail.clear(); inp_yas.clear(); self.refresh_data()

    def build_dashboard(self):
        self.page_dash = QWidget(); lay = QVBoxLayout(self.page_dash); lay.setContentsMargins(40,40,40,40)
        self.lbl_sum = QLabel("Özet"); self.lbl_sum.setStyleSheet("font-size:24px; font-weight:bold;"); lay.addWidget(self.lbl_sum)
        self.t_dash = QTableWidget(); self.t_dash.setColumnCount(8); self.t_dash.setHorizontalHeaderLabels(["ID", "Etkinlik", "Katılımcı", "Yaş", "Tür", "Başlangıç", "Bitiş", "Tutar"]); self.t_dash.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); self.t_dash.setStyleSheet(t_style); self.t_dash.verticalHeader().setVisible(False); lay.addWidget(self.t_dash)

    def build_duzenle_page(self):
        self.page_duzenle = QWidget(); lay = QVBoxLayout(self.page_duzenle); lay.setContentsMargins(40,40,40,40)
        self.t = QTableWidget(); self.t.setColumnCount(9); self.t.setHorizontalHeaderLabels(["ID", "Etkinlik", "Katılımcı", "Mail", "Tür", "Başlangıç", "Bitiş", "Bütçe", "İşlem"]); self.t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); self.t.setStyleSheet(t_style); self.t.verticalHeader().setVisible(False); lay.addWidget(self.t)

    def refresh_data(self):
        etkinlikler = self.db.tum_etkinlikler()
        if hasattr(self, 't_etk'):
            self.t_etk.setRowCount(0)
            for e in etkinlikler:
                r = self.t_etk.rowCount(); self.t_etk.insertRow(r); self.t_etk.setItem(r, 0, QTableWidgetItem(str(e[0]))); self.t_etk.setItem(r, 1, QTableWidgetItem(e[1])); self.t_etk.setItem(r, 2, QTableWidgetItem(e[2])); self.t_etk.setItem(r, 3, QTableWidgetItem(e[3]))
                w = QWidget(); bl = QHBoxLayout(w); bl.setContentsMargins(5, 5, 5, 5); bl.setSpacing(10); be = QPushButton("✏️"); be.setStyleSheet(style_btn(C['edit'])); be.setCursor(Qt.CursorShape.PointingHandCursor); be.clicked.connect(lambda _, x=e: self.etkinlik_edit_btn(x)); bd = QPushButton("🗑️"); bd.setStyleSheet(style_btn(C['danger'])); bd.setCursor(Qt.CursorShape.PointingHandCursor); bd.clicked.connect(lambda _, x=e[0]: self.etkinlik_sil_btn(x)); bl.addWidget(be); bl.addWidget(bd); self.t_etk.setCellWidget(r, 4, w)
        etk_adlari = [e[1] for e in etkinlikler]
        if hasattr(self, 'admin_cb_etk'): self.admin_cb_etk.clear(); self.admin_cb_etk.addItems(etk_adlari)
        if hasattr(self, 'user_cb_etk'): self.user_cb_etk.clear(); self.user_cb_etk.addItems(etk_adlari)
        kisi, ciro = self.db.genel_ozet(); self.lbl_sum.setText(f"Toplam Bilet: {kisi if kisi else 0} | Toplam Ciro: {ciro if ciro else 0:,.0f} ₺")
        biletler = self.db.tum_biletler(); self.t_dash.setRowCount(0); self.t.setRowCount(0)
        for b in biletler:
            rd = self.t_dash.rowCount(); self.t_dash.insertRow(rd); veriler = [str(b[0]), b[1], b[2], str(b[4]), b[5], b[6], b[7], f"{b[8]:,.0f} ₺"]
            for i, val in enumerate(veriler):
                item = QTableWidgetItem(val); 
                if i == 4 and "VIP" in val: item.setForeground(QColor(C['vip']))
                self.t_dash.setItem(rd, i, item)
            re = self.t.rowCount(); self.t.insertRow(re); veriler_edit = [str(b[0]), b[1], b[2], b[3], b[5], b[6], b[7], f"{b[8]:,.0f} ₺"]
            for i, val in enumerate(veriler_edit):
                item = QTableWidgetItem(val);
                if i == 4 and "VIP" in val: item.setForeground(QColor(C['vip']))
                self.t.setItem(re, i, item)
            w = QWidget(); bl = QHBoxLayout(w); bl.setContentsMargins(5,5,5,5); bl.setSpacing(10); be = QPushButton("✏️"); be.setStyleSheet(style_btn(C['edit'])); be.setCursor(Qt.CursorShape.PointingHandCursor); be.clicked.connect(lambda _, x=b: self.edit(x)); bd = QPushButton("🗑️"); bd.setStyleSheet(style_btn(C['danger'])); bd.setCursor(Qt.CursorShape.PointingHandCursor); bd.clicked.connect(lambda _, x=b[0]: self.delete(x)); bl.addWidget(be); bl.addWidget(bd); self.t.setCellWidget(re, 8, w)

    def delete(self, bid):
        if QMessageBox.question(self, "Sil", "Emin misiniz?") == QMessageBox.StandardButton.Yes: self.db.bilet_sil(bid); self.refresh_data()

    def edit(self, data):
        d = EditDialog(self, data)
        if d.exec():
            n_m, n_mail, n_y, n_tur, n_f = d.get_data(); self.db.bilet_guncelle(data[0], n_m, n_mail, n_y, n_tur, n_f); self.refresh_data()

if __name__ == "__main__":
    app = QApplication(sys.argv); win = CrimsonOS(); win.show(); sys.exit(app.exec())