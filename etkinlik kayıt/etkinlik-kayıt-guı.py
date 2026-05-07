import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QFrame,
    QStackedWidget, QHeaderView, QLineEdit, QComboBox, QMessageBox,
    QGraphicsDropShadowEffect, QGridLayout, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

# --- 1. VERİTABANI MİMARİSİ (CRIMSON EVENTS) ---
class Database:
    def __init__(self):
        self.conn = sqlite3.connect("crimson_events.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS biletler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                etkinlik TEXT,
                musteri TEXT,
                yas INTEGER,
                tur TEXT,
                tutar REAL
            )
        """)
        self.conn.commit()

    def musteri_bileti_var_mi(self, musteri_adi, etkinlik_adi):
        self.cursor.execute("SELECT id FROM biletler WHERE musteri = ? AND etkinlik = ?", (musteri_adi, etkinlik_adi))
        return self.cursor.fetchone() is not None

    def bilet_ekle(self, etkinlik, musteri, yas, tur, tutar):
        self.cursor.execute("INSERT INTO biletler (etkinlik, musteri, yas, tur, tutar) VALUES (?, ?, ?, ?, ?)", 
                            (etkinlik, musteri, yas, tur, tutar))
        self.conn.commit()

    def bilet_sil(self, bilet_id):
        self.cursor.execute("DELETE FROM biletler WHERE id = ?", (bilet_id,))
        self.conn.commit()

    def bilet_guncelle(self, bilet_id, musteri, yas, tur, tutar):
        self.cursor.execute("""
            UPDATE biletler 
            SET musteri=?, yas=?, tur=?, tutar=? 
            WHERE id=?
        """, (musteri, yas, tur, tutar, bilet_id))
        self.conn.commit()

    def tum_biletler(self):
        self.cursor.execute("SELECT * FROM biletler")
        return self.cursor.fetchall()

    def genel_ozet(self):
        self.cursor.execute("SELECT COUNT(*), SUM(tutar) FROM biletler")
        return self.cursor.fetchone()

# --- TASARIM PALETİ ---
C = {
    "bg": "#000000",          
    "card": "#111111",        
    "border": "#2A2A2A",      
    "accent": "#DC2626",      
    "accent_hover": "#991B1B",
    "text": "#FFFFFF",        
    "text_sub": "#A3A3A3",    
    "input_bg": "#1A1A1A",    
    "danger": "#EF4444", 
    "edit": "#3B82F6", 
    "vip": "#DC2626"
}

def style_card(): return f"background:{C['card']}; border:1px solid {C['border']}; border-radius:12px;"

def style_input(): return f"""
    QLineEdit, QComboBox {{
        background-color: {C['input_bg']}; color: {C['text']}; 
        border: 1px solid {C['border']}; border-radius: 6px; 
        padding: 12px; font-size: 14px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {C['card']}; color: {C['text']};
        selection-background-color: {C['accent']}; selection-color: #FFFFFF;
    }}
"""

def style_btn(color, hover=C['accent_hover']): return f"QPushButton{{background:{color}; color:#FFFFFF; border-radius:6px; padding:12px; font-weight:bold; font-size:14px;}} QPushButton:hover{{background:{hover};}}"

def add_shadow(widget):
    fx = QGraphicsDropShadowEffect(widget)
    fx.setBlurRadius(25); fx.setColor(QColor(220, 38, 38, 40)); fx.setOffset(0, 4)
    widget.setGraphicsEffect(fx)

# --- TABLO TASARIMI (HATANIN ÇÖZÜLDÜĞÜ YER) ---
t_style = f"""
    QTableWidget {{ background:{C['card']}; color:{C['text']}; border:1px solid {C['border']}; border-radius:8px; outline:none; }}
    QTableWidget::item {{ border-bottom:1px solid {C['border']}; padding-left:10px; }}
    QHeaderView::section {{ background:{C['input_bg']}; color:{C['text_sub']}; font-weight:bold; padding:15px; border:none; border-bottom:2px solid {C['accent']}; }}
"""

# --- DÜZENLEME PENCERESİ ---
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
        self.inp_yas = QLineEdit(str(self.data[3])); self.inp_yas.setStyleSheet(style_input())
        
        self.cb_tur = QComboBox(); self.cb_tur.addItems(["Standart Bilet", "VIP Kulis Erişimli"]); self.cb_tur.setStyleSheet(style_input())
        self.cb_tur.setCurrentText(self.data[4])
        
        btn_save = QPushButton("VERİTABANINI GÜNCELLE")
        btn_save.setStyleSheet(style_btn(C['accent']))
        btn_save.clicked.connect(self.validate_and_accept)

        lbl_etk = QLabel(f"Etkinlik: {self.data[1]} (Değiştirilemez)")
        lbl_etk.setStyleSheet(f"color:{C['text_sub']}; font-weight:bold;")
        
        lay.addWidget(lbl_etk); lay.addSpacing(10)
        lay.addWidget(QLabel("Katılımcı Ad Soyad:", styleSheet=f"color:{C['text']};")); lay.addWidget(self.inp_mus)
        lay.addWidget(QLabel("Yaş:", styleSheet=f"color:{C['text']};")); lay.addWidget(self.inp_yas)
        lay.addWidget(QLabel("Bilet Türü:", styleSheet=f"color:{C['text']};")); lay.addWidget(self.cb_tur)
        lay.addStretch(); lay.addWidget(btn_save)

    def validate_and_accept(self):
        mus = self.inp_mus.text().strip()
        yas = self.inp_yas.text().strip()
        
        if not mus or not yas:
            QMessageBox.warning(self, "Hata", "Boş alan bırakılamaz!"); return
            
        if not all(char.isalpha() or char.isspace() for char in mus):
            QMessageBox.critical(self, "Hata", "İsim alanına rakam veya özel karakter girilemez!"); return
            
        if not yas.isdigit():
            QMessageBox.critical(self, "Hata", "Yaş alanına sadece rakam girilmelidir!"); return
            
        if int(yas) < 18:
            QMessageBox.warning(self, "Yaş Sınırı", "Bu etkinlik için +18 yaş sınırı vardır!"); return
            
        self.accept()

    def get_data(self):
        tutar = 1500 if "VIP" in self.cb_tur.currentText() else 500
        return (self.inp_mus.text(), int(self.inp_yas.text()), self.cb_tur.currentText(), tutar)

# --- ANA SİSTEM ---
class CrimsonOS(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("Crimson Event Planner | OS")
        self.resize(1250, 850)
        self.setStyleSheet(f"QMainWindow {{background:{C['bg']}; color:{C['text']}; font-family: 'Segoe UI';}}")
        
        self.main_stack = QStackedWidget()
        self.setCentralWidget(self.main_stack)
        
        self.build_login_screen()
        self.build_main_app()
        
        self.main_stack.addWidget(self.login_widget)
        self.main_stack.addWidget(self.app_widget)

    def build_login_screen(self):
        self.login_widget = QWidget()
        lay = QVBoxLayout(self.login_widget)
        kart = QFrame(); kart.setFixedSize(400, 450); kart.setStyleSheet(style_card()); add_shadow(kart)
        k_lay = QVBoxLayout(kart); k_lay.setContentsMargins(40, 40, 40, 40); k_lay.setSpacing(20)
        
        self.lbl_logo = QLabel("CRIMSON")
        self.lbl_logo.setStyleSheet(f"color:{C['accent']}; font-size:36px; font-weight:900; letter-spacing: 6px;")
        self.lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_sub = QLabel("Event Planner & Management"); lbl_sub.setStyleSheet(f"color:{C['text_sub']};"); lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.inp_user = QLineEdit(); self.inp_user.setPlaceholderText("Yetkili ID (admin)"); self.inp_user.setStyleSheet(style_input())
        self.inp_pass = QLineEdit(); self.inp_pass.setPlaceholderText("Şifre (1234)"); self.inp_pass.setEchoMode(QLineEdit.EchoMode.Password); self.inp_pass.setStyleSheet(style_input())
        
        btn_login = QPushButton("SİSTEME GİRİŞ YAP"); btn_login.setStyleSheet(style_btn(C['accent']))
        btn_login.clicked.connect(self.check_login)
        
        k_lay.addStretch(); k_lay.addWidget(self.lbl_logo); k_lay.addWidget(lbl_sub); k_lay.addSpacing(20)
        k_lay.addWidget(self.inp_user); k_lay.addWidget(self.inp_pass); k_lay.addWidget(btn_login); k_lay.addStretch()
        lay.addWidget(kart, alignment=Qt.AlignmentFlag.AlignCenter)

    def check_login(self):
        if self.inp_user.text() == "admin" and self.inp_pass.text() == "1234":
            self.main_stack.setCurrentIndex(1); self.refresh_data()
        else: QMessageBox.warning(self, "Hata", "Erişim Reddedildi!")

    def build_main_app(self):
        self.app_widget = QWidget()
        ana_lay = QHBoxLayout(self.app_widget); ana_lay.setContentsMargins(0,0,0,0); ana_lay.setSpacing(0)
        sidebar = QFrame(); sidebar.setFixedWidth(260); sidebar.setStyleSheet(f"background:{C['card']}; border-right:1px solid {C['border']};")
        sb_lay = QVBoxLayout(sidebar); sb_lay.setContentsMargins(0,30,0,20)
        
        lbl_brand = QLabel("CRIMSON"); lbl_brand.setStyleSheet(f"color:{C['accent']}; font-size:24px; font-weight:900; margin-left:20px;")
        sb_lay.addWidget(lbl_brand); sb_lay.addSpacing(40)
        
        sayfalar = [("📊", "Dashboard"), ("🎟️", "Gişe (Bilet Kes)"), ("✏️", "Düzenle (Veritabanı)")]
        for i, (ico, txt) in enumerate(sayfalar):
            btn = QPushButton(f"  {ico}  {txt}")
            btn.setFixedHeight(55); btn.setStyleSheet(f"text-align:left; padding-left:20px; background:transparent; color:{C['text_sub']}; font-size:15px; font-weight:bold; border:none;")
            btn.clicked.connect(lambda _, x=i: self.nav(x))
            sb_lay.addWidget(btn)
            
        sb_lay.addStretch(); ana_lay.addWidget(sidebar)
        self.pages = QStackedWidget(); ana_lay.addWidget(self.pages)
        
        self.build_dashboard()
        self.build_gise_page()
        self.build_duzenle_page()
        
        self.pages.addWidget(self.page_dash)
        self.pages.addWidget(self.page_gise)
        self.pages.addWidget(self.page_duzenle)

    def nav(self, index): self.pages.setCurrentIndex(index); self.refresh_data()

    # ==========================================
    # 1. DASHBOARD SAYFASI (İZLEME)
    # ==========================================
    def build_dashboard(self):
        self.page_dash = QWidget(); lay = QVBoxLayout(self.page_dash); lay.setContentsMargins(50,50,50,50)
        
        self.lbl_sum = QLabel("Genel Sistem Özeti..."); self.lbl_sum.setStyleSheet("font-size:24px; font-weight:bold;")
        lay.addWidget(self.lbl_sum); lay.addSpacing(20)
        
        self.t_dash = QTableWidget(); self.t_dash.setColumnCount(6)
        self.t_dash.setHorizontalHeaderLabels(["ID", "Etkinlik", "Katılımcı", "Yaş", "Bilet Türü", "Tutar (₺)"])
        self.t_dash.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.t_dash.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) 
        
        # --- TABLO SATIR YÜKSEKLİĞİ VE TASARIMI ---
        self.t_dash.setStyleSheet(t_style)
        self.t_dash.verticalHeader().setDefaultSectionSize(50) # Satırları genişlet
        self.t_dash.verticalHeader().setVisible(False) # Çirkin sıra numaralarını gizle
        add_shadow(self.t_dash)
        
        lay.addWidget(QLabel("📌 Aktif Bilet Kayıtları (Sadece İzleme Modu)", styleSheet="font-size:14px; font-weight:bold; color:#A3A3A3;"))
        lay.addWidget(self.t_dash)

    # ==========================================
    # 2. GİŞE (BİLET SATIŞ) SAYFASI
    # ==========================================
    def build_gise_page(self):
        self.page_gise = QWidget(); lay = QVBoxLayout(self.page_gise); lay.setContentsMargins(50,50,50,50)
        
        lbl_baslik = QLabel("Bilet Satış Noktası"); lbl_baslik.setStyleSheet(f"color:{C['text']}; font-size: 28px; font-weight:bold;")
        lay.addWidget(lbl_baslik); lay.addSpacing(20)
        
        kart = QFrame(); kart.setStyleSheet(style_card()); add_shadow(kart)
        klay = QGridLayout(kart); klay.setSpacing(25); klay.setContentsMargins(40,40,40,40)
        
        self.etkinlikler = ["Açıkhava Rock Festivali", "Kültür Üni Bahar Şenliği", "C# & SQL Bootcamp", "Gece Yarısı Sineması"]
        self.cb_etk = QComboBox(); self.cb_etk.addItems(self.etkinlikler); self.cb_etk.setStyleSheet(style_input())
        
        self.inp_mus = QLineEdit(); self.inp_mus.setPlaceholderText("Katılımcı Ad Soyad"); self.inp_mus.setStyleSheet(style_input())
        self.inp_yas = QLineEdit(); self.inp_yas.setPlaceholderText("Yaş"); self.inp_yas.setStyleSheet(style_input())
        
        self.cb_tur = QComboBox(); self.cb_tur.addItems(["Standart Bilet (500 ₺)", "VIP Kulis Erişimli (1500 ₺)"]); self.cb_tur.setStyleSheet(style_input())
        
        btn = QPushButton("BİLETİ ONAYLA VE KAYDET"); btn.setStyleSheet(style_btn(C['accent']))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self.bilet_kes)
        
        klay.addWidget(QLabel("Etkinlik Seçimi:", styleSheet=f"color:{C['text_sub']}; font-weight:bold;"), 0, 0)
        klay.addWidget(self.cb_etk, 0, 1, 1, 3)
        klay.addWidget(QLabel("Katılımcı Adı:", styleSheet=f"color:{C['text_sub']}; font-weight:bold;"), 1, 0)
        klay.addWidget(self.inp_mus, 1, 1)
        klay.addWidget(QLabel("Katılımcı Yaşı:", styleSheet=f"color:{C['text_sub']}; font-weight:bold;"), 1, 2)
        klay.addWidget(self.inp_yas, 1, 3)
        klay.addWidget(QLabel("Bilet Türü:", styleSheet=f"color:{C['text_sub']}; font-weight:bold;"), 2, 0)
        klay.addWidget(self.cb_tur, 2, 1, 1, 3)
        klay.addWidget(btn, 3, 0, 1, 4)
        lay.addWidget(kart); lay.addStretch()

    def bilet_kes(self):
        try:
            etk = self.cb_etk.currentText()
            mus = self.inp_mus.text().strip()
            yas = self.inp_yas.text().strip()
            
            if not mus or not yas:
                QMessageBox.warning(self, "Eksik Veri", "Lütfen tüm alanları doldurun!"); return
                
            if not all(char.isalpha() or char.isspace() for char in mus):
                QMessageBox.critical(self, "Hata", "Katılımcı adına rakam girilemez!"); return
            if not yas.isdigit():
                QMessageBox.critical(self, "Hata", "Yaş alanına harf girilemez, sadece rakam yazınız!"); return
            
            yas_int = int(yas)
            if yas_int < 18:
                QMessageBox.critical(self, "Reddedildi", f"{mus} çok genç! +18 kuralı ihlali."); return
                
            if self.db.musteri_bileti_var_mi(mus, etk):
                QMessageBox.warning(self, "Mükerrer Kayıt", f"{mus} adına '{etk}' için zaten bilet mevcut!"); return
            
            tur = "VIP Kulis Erişimli" if "VIP" in self.cb_tur.currentText() else "Standart Bilet"
            tutar = 1500 if "VIP" in tur else 500
            
            self.db.bilet_ekle(etk, mus, yas_int, tur, tutar)
            QMessageBox.information(self, "Bilet Onaylandı", f"Bilet başarıyla kesildi.\n\nTutar: {tutar} ₺")
            self.inp_mus.clear(); self.inp_yas.clear()
            self.refresh_data()
            
        except Exception as e:
            QMessageBox.critical(self, "Kritik Hata", "İşlem sırasında beklenmeyen bir hata oluştu.")

    # ==========================================
    # 3. VERİTABANI DÜZENLEME SAYFASI
    # ==========================================
    def build_duzenle_page(self):
        self.page_duzenle = QWidget(); lay = QVBoxLayout(self.page_duzenle); lay.setContentsMargins(40,40,40,40)
        
        lbl_baslik = QLabel("Veritabanı Yönetimi (Düzenle / Sil)"); lbl_baslik.setStyleSheet(f"color:{C['text']}; font-size:24px; font-weight:bold;")
        lay.addWidget(lbl_baslik); lay.addSpacing(20)
        
        self.t = QTableWidget(); self.t.setColumnCount(7)
        self.t.setHorizontalHeaderLabels(["ID", "Etkinlik", "Katılımcı", "Yaş", "Bilet Türü", "Tutar (₺)", "Aksiyon"])
        
        self.t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # --- TABLO SATIR YÜKSEKLİĞİ VE TASARIMI ---
        self.t.setStyleSheet(t_style)
        self.t.verticalHeader().setDefaultSectionSize(60) # BUTONLARIN RAHAT SIĞMASI İÇİN GENİŞLETİLDİ
        self.t.verticalHeader().setVisible(False)
        add_shadow(self.t)
        lay.addWidget(self.t)

    # ==========================================
    # ORTAK REFRESH (YENİLEME) FONKSİYONU
    # ==========================================
    def refresh_data(self):
        kisi, ciro = self.db.genel_ozet()
        self.lbl_sum.setText(f"Toplam Bilet Satışı: {kisi if kisi else 0} Adet   |   Sistemdeki Toplam Hasılat: {ciro if ciro else 0} ₺")
        
        biletler = self.db.tum_biletler()
        
        self.t_dash.setRowCount(0)
        for b in biletler:
            r = self.t_dash.rowCount(); self.t_dash.insertRow(r)
            for i in range(5):
                item = QTableWidgetItem(str(b[i]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
                if i == 4 and "VIP" in str(b[i]): 
                    item.setForeground(QColor(C['vip'])); font = QFont(); font.setBold(True); item.setFont(font)
                self.t_dash.setItem(r, i, item)
            
            tutar_item = QTableWidgetItem(f"{b[5]:,.0f} ₺")
            tutar_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
            self.t_dash.setItem(r, 5, tutar_item)
            
        self.t.setRowCount(0)
        for b in biletler:
            r = self.t.rowCount(); self.t.insertRow(r)
            for i in range(5):
                item = QTableWidgetItem(str(b[i]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
                if i == 4 and "VIP" in str(b[i]): 
                    item.setForeground(QColor(C['vip'])); font = QFont(); font.setBold(True); item.setFont(font)
                self.t.setItem(r, i, item)
                
            tutar_item = QTableWidgetItem(f"{b[5]:,.0f} ₺")
            tutar_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
            self.t.setItem(r, 5, tutar_item)
            
            # --- AKSİYON BUTONLARI YENİDEN YAZILDI ---
            w = QWidget()
            bl = QHBoxLayout(w)
            bl.setContentsMargins(5, 5, 5, 5) # Butonları daraltmasın diye margin ayarı
            bl.setSpacing(10)
            
            be = QPushButton("DÜZENLE")
            be.setCursor(Qt.CursorShape.PointingHandCursor)
            be.setStyleSheet(f"background:{C['edit']}; color:#FFF; font-weight:bold; border-radius:4px; padding:8px;")
            be.clicked.connect(lambda _, x=b: self.edit(x))
            
            bd = QPushButton("SİL")
            bd.setCursor(Qt.CursorShape.PointingHandCursor)
            bd.setStyleSheet(f"background:{C['danger']}; color:#FFF; font-weight:bold; border-radius:4px; padding:8px;")
            bd.clicked.connect(lambda _, x=b[0]: self.delete(x))
            
            bl.addWidget(be)
            bl.addWidget(bd)
            self.t.setCellWidget(r, 6, w)

    def delete(self, bid):
        if QMessageBox.question(self, "İptal", "Bu bileti silmek istediğinize emin misiniz?") == QMessageBox.StandardButton.Yes:
            self.db.bilet_sil(bid); self.refresh_data()

    def edit(self, data):
        d = EditDialog(self, data)
        if d.exec():
            n_m, n_y, n_tur, n_tutar = d.get_data()
            self.db.bilet_guncelle(data[0], n_m, n_y, n_tur, n_tutar); self.refresh_data()

if __name__ == "__main__":
    app = QApplication(sys.argv); win = CrimsonOS(); win.show(); sys.exit(app.exec())