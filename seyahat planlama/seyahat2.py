import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QFrame,
    QStackedWidget, QHeaderView, QLineEdit, QComboBox, QMessageBox,
    QGraphicsDropShadowEffect, QGridLayout, QDialog, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QFont

# --- 1. VERİTABANI MİMARİSİ ---
class Database:
    def __init__(self):
        self.conn = sqlite3.connect("aurora_v7.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS planlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                musteri TEXT,
                mail TEXT,
                kisi INTEGER,
                rota TEXT,
                tarih TEXT,
                gun INTEGER,
                ulasim TEXT,
                otel TEXT,
                tutar REAL
            )
        """)
        self.conn.commit()

    def musteri_plani_var_mi(self, mail, rota):
        self.cursor.execute("SELECT id FROM planlar WHERE mail = ? AND rota = ?", (mail, rota))
        return self.cursor.fetchone() is not None

    def plan_ekle(self, musteri, mail, kisi, rota, tarih, gun, ulasim, otel, tutar):
        self.cursor.execute("""
            INSERT INTO planlar (musteri, mail, kisi, rota, tarih, gun, ulasim, otel, tutar) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (musteri, mail, kisi, rota, tarih, gun, ulasim, otel, tutar))
        self.conn.commit()

    def plan_sil(self, plan_id):
        self.cursor.execute("DELETE FROM planlar WHERE id = ?", (plan_id,))
        self.conn.commit()

    def plan_guncelle(self, plan_id, musteri, mail, ulasim, otel, tutar):
        self.cursor.execute("""
            UPDATE planlar 
            SET musteri=?, mail=?, ulasim=?, otel=?, tutar=? 
            WHERE id=?
        """, (musteri, mail, ulasim, otel, tutar, plan_id))
        self.conn.commit()

    def tum_planlar(self):
        self.cursor.execute("SELECT * FROM planlar")
        return self.cursor.fetchall()

    def finans_ozeti(self):
        self.cursor.execute("SELECT COUNT(*), SUM(tutar) FROM planlar")
        return self.cursor.fetchone()

# --- TASARIM PALETİ ---
C = {
    "bg": "#0F172A", "card": "#1E293B", "border": "#334155", 
    "accent": "#EAB308", "accent_hover": "#CA8A04",
    "text": "#F8FAFC", "text_sub": "#94A3B8", "input_bg": "#0F172A",
    "danger": "#EF4444", "edit": "#3B82F6"
}

def style_card(): return f"background:{C['card']}; border:1px solid {C['border']}; border-radius:12px;"

def style_input(): return f"""
    QLineEdit, QComboBox, QDateEdit {{
        background-color: {C['input_bg']}; color: {C['text']}; 
        border: 1px solid {C['border']}; border-radius: 6px; 
        padding: 12px; font-size: 14px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {C['card']}; color: {C['text']};
        selection-background-color: {C['accent']}; selection-color: #000000;
    }}
"""

def style_btn(color, text_color="#000", hover=C['accent_hover']): 
    return f"QPushButton{{background:{color}; color:{text_color}; border-radius:6px; padding:12px; font-weight:bold; font-size:14px;}} QPushButton:hover{{background:{hover};}}"

def add_shadow(widget):
    fx = QGraphicsDropShadowEffect(widget)
    fx.setBlurRadius(25); fx.setColor(QColor(0, 0, 0, 150)); fx.setOffset(0, 4)
    widget.setGraphicsEffect(fx)

t_style = f"""
    QTableWidget {{ background:{C['card']}; color:{C['text']}; border:1px solid {C['border']}; border-radius:8px; outline:none; }}
    QTableWidget::item {{ border-bottom:1px solid {C['border']}; padding-left:10px; }}
    QHeaderView::section {{ background:{C['input_bg']}; color:{C['text_sub']}; font-weight:bold; padding:15px; border:none; border-bottom:2px solid {C['accent']}; }}
"""

class EditDialog(QDialog):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.setWindowTitle("Rezervasyon Güncelleme")
        self.setFixedSize(400, 450)
        self.setStyleSheet(f"background:{C['bg']}; color:{C['text']};")
        self.data = data 
        self.init_ui()

    def init_ui(self):
        lay = QVBoxLayout(self)
        self.inp_mus = QLineEdit(self.data[1]); self.inp_mus.setStyleSheet(style_input())
        self.inp_mail = QLineEdit(self.data[2]); self.inp_mail.setStyleSheet(style_input())
        
        self.cb_ulasim = QComboBox(); self.cb_ulasim.addItems(["Otobüs", "Uçak", "Özel Araç", "VIP Transfer (Lüks)"]); self.cb_ulasim.setStyleSheet(style_input())
        self.cb_ulasim.setCurrentText(self.data[7])
        
        self.cb_otel = QComboBox(); self.cb_otel.addItems(["Ekonomik (3 Yıldız)", "Standart (4 Yıldız)", "Premium (5 Yıldız)", "Ultra Lüks (5+ Yıldız)"]); self.cb_otel.setStyleSheet(style_input())
        self.cb_otel.setCurrentText(self.data[8])
        
        btn_save = QPushButton("VERİLERİ GÜNCELLE")
        btn_save.setStyleSheet(style_btn(C['accent'], "#000")); btn_save.clicked.connect(self.accept)

        lay.addWidget(QLabel(f"Rota: {self.data[4]} (Değiştirilemez)", styleSheet=f"color:{C['text_sub']}; font-weight:bold;")); lay.addSpacing(10)
        lay.addWidget(QLabel("Müşteri Ad Soyad:")); lay.addWidget(self.inp_mus)
        lay.addWidget(QLabel("E-Posta:")); lay.addWidget(self.inp_mail)
        lay.addWidget(QLabel("Ulaşım Aracı:")); lay.addWidget(self.cb_ulasim)
        lay.addWidget(QLabel("Konaklama Kalitesi:")); lay.addWidget(self.cb_otel)
        lay.addStretch(); lay.addWidget(btn_save)

    def get_data(self):
        kisi = self.data[3]; gun = self.data[6]
        u_fiyat = {"Otobüs": 800, "Uçak": 2500, "Özel Araç": 1500, "VIP Transfer (Lüks)": 6000}
        o_fiyat = {"Ekonomik (3 Yıldız)": 1000, "Standart (4 Yıldız)": 2000, "Premium (5 Yıldız)": 4000, "Ultra Lüks (5+ Yıldız)": 8000}
        tutar = (kisi * u_fiyat[self.cb_ulasim.currentText()]) + (kisi * gun * o_fiyat[self.cb_otel.currentText()])
        return (self.inp_mus.text(), self.inp_mail.text(), self.cb_ulasim.currentText(), self.cb_otel.currentText(), tutar)

class AuroraOS(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("Aurora Enterprise | v7.1")
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
        lbl_u = QLabel("AURORA MÜŞTERİ PORTALI"); lbl_u.setStyleSheet(f"color:{C['accent']}; font-size:28px; font-weight:900;"); lbl_u.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_info = QLabel("Hayalinizdeki seyahati saniyeler\niçinde planlayın ve bütçenizi görün."); lbl_info.setStyleSheet(f"color:{C['text_sub']}; font-size:16px; line-height:1.5;"); lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_user = QPushButton("HIZLI REZERVASYON YAP"); btn_user.setStyleSheet(style_btn(C['text'], "#000", "#E2E8F0")); btn_user.setFixedHeight(60)
        btn_user.clicked.connect(lambda: self.main_stack.setCurrentIndex(2))
        ku_lay.addStretch(); ku_lay.addWidget(lbl_u); ku_lay.addSpacing(10); ku_lay.addWidget(lbl_info); ku_lay.addSpacing(30); ku_lay.addWidget(btn_user); ku_lay.addStretch()
        h_lay.addWidget(kart_user)

        h_lay.addSpacing(40)

        kart_admin = QFrame(); kart_admin.setFixedSize(280, 350); kart_admin.setStyleSheet(f"background:#111827; border:1px solid {C['border']}; border-radius:8px;")
        ka_lay = QVBoxLayout(kart_admin); ka_lay.setContentsMargins(20, 20, 20, 20)
        self.inp_user = QLineEdit(); self.inp_user.setPlaceholderText("ID"); self.inp_user.setStyleSheet(style_input())
        self.inp_pass = QLineEdit(); self.inp_pass.setPlaceholderText("Şifre"); self.inp_pass.setEchoMode(QLineEdit.EchoMode.Password); self.inp_pass.setStyleSheet(style_input())
        btn_admin = QPushButton("Giriş"); btn_admin.setStyleSheet(style_btn(C['accent'], "#000")); btn_admin.clicked.connect(self.check_admin_login)
        ka_lay.addStretch(); ka_lay.addWidget(QLabel("Acente Personeli", styleSheet="color:#94A3B8; font-weight:bold;", alignment=Qt.AlignmentFlag.AlignCenter)); ka_lay.addSpacing(10); ka_lay.addWidget(self.inp_user); ka_lay.addWidget(self.inp_pass); ka_lay.addWidget(btn_admin); ka_lay.addStretch()
        h_lay.addWidget(kart_admin, alignment=Qt.AlignmentFlag.AlignVCenter)

        h_lay.addStretch()
        lay.addStretch(); lay.addLayout(h_lay); lay.addStretch()

    def check_admin_login(self):
        if self.inp_user.text() == "admin" and self.inp_pass.text() == "1234":
            self.main_stack.setCurrentIndex(1); self.refresh_data()
        else: QMessageBox.warning(self, "Hata", "Erişim Reddedildi!")

    def build_admin_app(self):
        self.admin_widget = QWidget(); ana_lay = QHBoxLayout(self.admin_widget); ana_lay.setContentsMargins(0,0,0,0); ana_lay.setSpacing(0)
        sidebar = QFrame(); sidebar.setFixedWidth(260); sidebar.setStyleSheet(f"background:{C['card']}; border-right:1px solid {C['border']};")
        sb_lay = QVBoxLayout(sidebar); sb_lay.setContentsMargins(0,30,0,20)
        
        lbl_brand = QLabel("AURORA PRO"); lbl_brand.setStyleSheet(f"color:{C['accent']}; font-size:24px; font-weight:900; margin-left:20px;")
        sb_lay.addWidget(lbl_brand); sb_lay.addSpacing(40)
        
        sayfalar = [("📊", "Dashboard"), ("📍", "Manuel Kayıt"), ("✏️", "Veritabanı")]
        for i, (ico, txt) in enumerate(sayfalar):
            btn = QPushButton(f"  {ico}  {txt}"); btn.setFixedHeight(55); btn.setStyleSheet(f"text-align:left; padding-left:20px; background:transparent; color:{C['text_sub']}; font-size:15px; font-weight:bold; border:none;")
            btn.clicked.connect(lambda _, x=i: self.pages_admin.setCurrentIndex(x)); sb_lay.addWidget(btn)
            
        sb_lay.addStretch()
        btn_cikis = QPushButton("🚪 Çıkış"); btn_cikis.setStyleSheet("color:#EF4444; background:transparent; font-weight:bold; border:none;"); btn_cikis.clicked.connect(lambda: self.main_stack.setCurrentIndex(0))
        sb_lay.addWidget(btn_cikis); ana_lay.addWidget(sidebar)
        
        self.pages_admin = QStackedWidget(); ana_lay.addWidget(self.pages_admin)
        self.build_dashboard()
        self.build_rezervasyon_page(self.pages_admin, is_admin=True) 
        self.build_duzenle_page()
        
        self.pages_admin.addWidget(self.page_dash)
        self.pages_admin.addWidget(self.page_rez_admin)
        self.pages_admin.addWidget(self.page_duzenle)

    def build_user_app(self):
        self.user_widget = QWidget(); lay = QVBoxLayout(self.user_widget); lay.setContentsMargins(0,0,0,0)
        header = QFrame(); header.setFixedHeight(80); header.setStyleSheet(f"background:{C['card']}; border-bottom:1px solid {C['border']};")
        h_lay = QHBoxLayout(header); h_lay.setContentsMargins(30, 0, 30, 0)
        lbl_brand = QLabel("AURORA TRAVEL"); lbl_brand.setStyleSheet(f"color:{C['accent']}; font-size:24px; font-weight:bold;")
        btn_cikis = QPushButton("Giriş Ekranına Dön"); btn_cikis.setStyleSheet(style_btn(C['border'], "#FFF")); btn_cikis.clicked.connect(lambda: self.main_stack.setCurrentIndex(0))
        h_lay.addWidget(lbl_brand); h_lay.addStretch(); h_lay.addWidget(btn_cikis)
        lay.addWidget(header)
        
        self.pages_user = QStackedWidget(); lay.addWidget(self.pages_user)
        self.build_rezervasyon_page(self.pages_user, is_admin=False)
        self.pages_user.addWidget(self.page_rez_user)

    def build_rezervasyon_page(self, container, is_admin):
        page = QWidget(); lay = QVBoxLayout(page); lay.setContentsMargins(50,50,50,50)
        baslik = "Acente Manuel Kayıt Paneli" if is_admin else "Seyahatini Planla"
        lay.addWidget(QLabel(baslik, styleSheet=f"color:{C['text']}; font-size: 28px; font-weight:bold;")); lay.addSpacing(20)
        
        kart = QFrame(); kart.setStyleSheet(style_card()); add_shadow(kart)
        klay = QGridLayout(kart); klay.setSpacing(25); klay.setContentsMargins(40,40,40,40)
        
        sehirler = ["İstanbul", "Ankara", "İzmir", "Trabzon", "Antalya", "Nevşehir", "Bursa", "Muğla"]
        cb_n1 = QComboBox(); cb_n1.addItems(sehirler); cb_n1.setStyleSheet(style_input())
        cb_n2 = QComboBox(); cb_n2.addItems(sehirler); cb_n2.setStyleSheet(style_input())
        
        # TAKVİM KISITLAMASI (10 MAYIS 2026)
        min_date = QDate(2026, 5, 10)
        inp_tarih = QDateEdit(min_date)
        inp_tarih.setDisplayFormat("dd.MM.yyyy")
        inp_tarih.setStyleSheet(style_input())
        inp_tarih.setCalendarPopup(True)
        inp_tarih.setMinimumDate(min_date)
        
        inp_gun = QLineEdit(); inp_gun.setPlaceholderText("Örn: 5"); inp_gun.setStyleSheet(style_input())
        cb_ulasim = QComboBox(); cb_ulasim.addItems(["Otobüs", "Uçak", "Özel Araç", "VIP Transfer (Lüks)"]); cb_ulasim.setStyleSheet(style_input())
        cb_otel = QComboBox(); cb_otel.addItems(["Ekonomik (3 Yıldız)", "Standart (4 Yıldız)", "Premium (5 Yıldız)", "Ultra Lüks (5+ Yıldız)"]); cb_otel.setStyleSheet(style_input())
        
        inp_mus = QLineEdit(); inp_mus.setPlaceholderText("Ad Soyad"); inp_mus.setStyleSheet(style_input())
        inp_mail = QLineEdit(); inp_mail.setPlaceholderText("E-Posta"); inp_mail.setStyleSheet(style_input())
        inp_kisi = QLineEdit(); inp_kisi.setPlaceholderText("Kişi Sayısı"); inp_kisi.setStyleSheet(style_input())
        
        lbl_fiyat = QLabel("Hesaplanıyor..."); lbl_fiyat.setStyleSheet(f"color:{C['accent']}; font-size:24px; font-weight:bold;")
        
        def fiyat_hesapla():
            try:
                k = int(inp_kisi.text() if inp_kisi.text() else 0); g = int(inp_gun.text() if inp_gun.text() else 0)
                u = cb_ulasim.currentText(); o = cb_otel.currentText()
                u_fiyat = {"Otobüs": 800, "Uçak": 2500, "Özel Araç": 1500, "VIP Transfer (Lüks)": 6000}
                o_fiyat = {"Ekonomik (3 Yıldız)": 1000, "Standart (4 Yıldız)": 2000, "Premium (5 Yıldız)": 4000, "Ultra Lüks (5+ Yıldız)": 8000}
                total = (k * u_fiyat[u]) + (k * g * o_fiyat[o])
                lbl_fiyat.setText(f"Ödenecek Toplam Tutar: {total:,.0f} ₺")
            except Exception:
                lbl_fiyat.setText("Lütfen geçerli rakamlar girin...")
                
        inp_kisi.textChanged.connect(fiyat_hesapla); inp_gun.textChanged.connect(fiyat_hesapla); cb_ulasim.currentTextChanged.connect(fiyat_hesapla); cb_otel.currentTextChanged.connect(fiyat_hesapla)

        btn = QPushButton(" TAMAMLA"); btn.setStyleSheet(style_btn(C['accent'], "#000")); btn.setFixedHeight(50)
        btn.clicked.connect(lambda: self.kaydet_rota(cb_n1, cb_n2, inp_tarih, inp_gun, cb_ulasim, cb_otel, inp_mus, inp_mail, inp_kisi))
        
        row = 0
        klay.addWidget(QLabel("Nereden:", styleSheet=f"color:{C['text_sub']}; font-weight:bold;"), row, 0); klay.addWidget(cb_n1, row, 1)
        klay.addWidget(QLabel("Nereye:", styleSheet=f"color:{C['text_sub']}; font-weight:bold;"), row, 2); klay.addWidget(cb_n2, row, 3); row+=1
        klay.addWidget(QLabel("Gidiş Tarihi:", styleSheet=f"color:{C['text_sub']}; font-weight:bold;"), row, 0); klay.addWidget(inp_tarih, row, 1)
        klay.addWidget(QLabel("Süre (Gün):", styleSheet=f"color:{C['text_sub']}; font-weight:bold;"), row, 2); klay.addWidget(inp_gun, row, 3); row+=1
        klay.addWidget(QLabel("Ulaşım Tipi:", styleSheet=f"color:{C['text_sub']}; font-weight:bold;"), row, 0); klay.addWidget(cb_ulasim, row, 1)
        klay.addWidget(QLabel("Konaklama:", styleSheet=f"color:{C['text_sub']}; font-weight:bold;"), row, 2); klay.addWidget(cb_otel, row, 3); row+=1
        klay.addWidget(QLabel("Müşteri / E-Posta:", styleSheet=f"color:{C['text_sub']}; font-weight:bold;"), row, 0); klay.addWidget(inp_mus, row, 1); klay.addWidget(inp_mail, row, 2, 1, 2); row+=1
        klay.addWidget(QLabel("Kişi Sayısı:", styleSheet=f"color:{C['text_sub']}; font-weight:bold;"), row, 0); klay.addWidget(inp_kisi, row, 1); row+=1
        klay.addWidget(lbl_fiyat, row, 0, 1, 2); klay.addWidget(btn, row, 2, 1, 2)
        
        lay.addWidget(kart); lay.addStretch()
        if is_admin: self.page_rez_admin = page
        else: self.page_rez_user = page

    def kaydet_rota(self, cb_n1, cb_n2, inp_tarih, inp_gun, cb_ulasim, cb_otel, inp_mus, inp_mail, inp_kisi):
        nereden = cb_n1.currentText(); nereye = cb_n2.currentText()
        mus = inp_mus.text().strip(); mail = inp_mail.text().strip()
        kisi_str = inp_kisi.text().strip(); gun_str = inp_gun.text().strip()
        
        if nereden == nereye: QMessageBox.critical(self, "Hata", "Aynı şehirler olamaz!"); return
        if not mus or not mail or not kisi_str or not gun_str: QMessageBox.warning(self, "Hata", "Boş alan bırakılamaz!"); return
        if "@" not in mail or "." not in mail: QMessageBox.critical(self, "Hata", "Geçersiz e-posta!"); return
        if not kisi_str.isdigit() or not gun_str.isdigit(): QMessageBox.critical(self, "Hata", "Kişi ve gün rakam olmalı!"); return
        
        rota_adi = f"{nereden} -> {nereye}"
        if self.db.musteri_plani_var_mi(mail, rota_adi): QMessageBox.warning(self, "Hata", "Bu rotaya kaydınız var!"); return
        
        kisi = int(kisi_str); gun = int(gun_str)
        u_fiyat = {"Otobüs": 800, "Uçak": 2500, "Özel Araç": 1500, "VIP Transfer (Lüks)": 6000}
        o_fiyat = {"Ekonomik (3 Yıldız)": 1000, "Standart (4 Yıldız)": 2000, "Premium (5 Yıldız)": 4000, "Ultra Lüks (5+ Yıldız)": 8000}
        tutar = (kisi * u_fiyat[cb_ulasim.currentText()]) + (kisi * gun * o_fiyat[cb_otel.currentText()])
        
        self.db.plan_ekle(mus, mail, kisi, rota_adi, inp_tarih.date().toString("dd.MM.yyyy"), gun, cb_ulasim.currentText(), cb_otel.currentText(), tutar)
        QMessageBox.information(self, "Başarılı", "Rezervasyon tamamlandı!"); inp_mus.clear(); inp_mail.clear(); inp_kisi.clear(); inp_gun.clear()
        self.refresh_data()

    def build_dashboard(self):
        self.page_dash = QWidget(); lay = QVBoxLayout(self.page_dash); lay.setContentsMargins(40,40,40,40)
        self.lbl_sum = QLabel("Özet"); self.lbl_sum.setStyleSheet("font-size:24px; font-weight:bold;"); lay.addWidget(self.lbl_sum)
        self.t_dash = QTableWidget(); self.t_dash.setColumnCount(8)
        self.t_dash.setHorizontalHeaderLabels(["ID", "Müşteri", "Kişi", "Rota", "Tarih", "Ulaşım", "Otel", "Ciro (₺)"])
        self.t_dash.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.t_dash.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers); self.t_dash.setStyleSheet(t_style); self.t_dash.verticalHeader().setVisible(False); lay.addWidget(self.t_dash)

    def build_duzenle_page(self):
        self.page_duzenle = QWidget(); lay = QVBoxLayout(self.page_duzenle); lay.setContentsMargins(40,40,40,40)
        self.t = QTableWidget(); self.t.setColumnCount(9)
        self.t.setHorizontalHeaderLabels(["ID", "Müşteri", "E-Posta", "Rota", "Ulaşım", "Konaklama", "Bütçe", "Düzenle", "Sil"])
        self.t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); self.t.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents); self.t.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)
        self.t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers); self.t.setStyleSheet(t_style); self.t.verticalHeader().setVisible(False); lay.addWidget(self.t)

    def refresh_data(self):
        sayi, ciro = self.db.finans_ozeti()
        self.lbl_sum.setText(f"Aktif Rota: {sayi if sayi else 0} | Beklenen Ciro: {ciro if ciro else 0:,.0f} ₺")
        planlar = self.db.tum_planlar()
        
        self.t_dash.setRowCount(0); self.t.setRowCount(0)
        for p in planlar:
            rd = self.t_dash.rowCount(); self.t_dash.insertRow(rd)
            veriler_dash = [str(p[0]), p[1], str(p[3]), p[4], p[5], p[7], p[8], f"{p[9]:,.0f} ₺"]
            for i, val in enumerate(veriler_dash): self.t_dash.setItem(rd, i, QTableWidgetItem(val))
                
            re = self.t.rowCount(); self.t.insertRow(re)
            veriler_edit = [str(p[0]), p[1], p[2], p[4], p[7], p[8], f"{p[9]:,.0f} ₺"]
            for i, val in enumerate(veriler_edit): self.t.setItem(re, i, QTableWidgetItem(val))
            
            be = QPushButton("✏️"); be.setStyleSheet(style_btn(C['edit'])); be.clicked.connect(lambda _, x=p: self.edit(x))
            bd = QPushButton("🗑️"); bd.setStyleSheet(style_btn(C['danger'])); bd.clicked.connect(lambda _, x=p[0]: self.delete(x))
            self.t.setCellWidget(re, 7, be); self.t.setCellWidget(re, 8, bd)

    def delete(self, pid):
        if QMessageBox.question(self, "İptal", "Emin misiniz?") == QMessageBox.StandardButton.Yes:
            self.db.plan_sil(pid); self.refresh_data()

    def edit(self, data):
        d = EditDialog(self, data)
        if d.exec():
            n_m, n_mail, n_u, n_o, n_f = d.get_data()
            self.db.plan_guncelle(data[0], n_m, n_mail, n_u, n_o, n_f); self.refresh_data()

if __name__ == "__main__":
    app = QApplication(sys.argv); win = AuroraOS(); win.show(); sys.exit(app.exec())