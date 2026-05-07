import sys
import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QFrame,
    QStackedWidget, QHeaderView, QLineEdit, QComboBox, QMessageBox,
    QGraphicsDropShadowEffect, QGridLayout, QDialog
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont

# --- 1. VERİTABANI MİMARİSİ (AURORA ENTERPRISE) ---
class Database:
    def __init__(self):
        # Veritabanı adı yeni markaya göre güncellendi
        self.conn = sqlite3.connect("aurora_enterprise.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS planlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                musteri TEXT,
                rota TEXT,
                tarih TEXT,
                gun INTEGER,
                tutar REAL,
                durum TEXT
            )
        """)
        self.conn.commit()

    def musteri_plani_var_mi(self, musteri_adi):
        self.cursor.execute("SELECT id FROM planlar WHERE musteri = ?", (musteri_adi,))
        return self.cursor.fetchone() is not None

    def plan_ekle(self, musteri, rota, tarih, gun, tutar):
        self.cursor.execute("INSERT INTO planlar (musteri, rota, tarih, gun, tutar, durum) VALUES (?, ?, ?, ?, ?, 'Aktif')", 
                            (musteri, rota, tarih, gun, tutar))
        self.conn.commit()

    def plan_sil(self, plan_id):
        self.cursor.execute("DELETE FROM planlar WHERE id = ?", (plan_id,))
        self.conn.commit()

    def plan_guncelle(self, plan_id, musteri, rota, tarih, gun, tutar):
        self.cursor.execute("""
            UPDATE planlar 
            SET musteri=?, rota=?, tarih=?, gun=?, tutar=? 
            WHERE id=?
        """, (musteri, rota, tarih, gun, tutar, plan_id))
        self.conn.commit()

    def tum_planlar(self):
        self.cursor.execute("SELECT * FROM planlar")
        return self.cursor.fetchall()

    def finans_ozeti(self):
        self.cursor.execute("SELECT COUNT(*), SUM(tutar) FROM planlar")
        return self.cursor.fetchone()

# --- TASARIM PALETİ (Luxury Navy & Gold) ---
C = {
    "bg": "#0F172A", "card": "#1E293B", "border": "#334155", 
    "accent": "#EAB308", "accent_hover": "#CA8A04",
    "text": "#F8FAFC", "text_sub": "#94A3B8", "input_bg": "#0F172A",
    "danger": "#EF4444", "edit": "#3B82F6"
}

def style_card(): return f"background:{C['card']}; border:1px solid {C['border']}; border-radius:12px;"
def style_input(): return f"QLineEdit, QComboBox {{background:{C['input_bg']}; color:{C['text']}; border:1px solid {C['border']}; border-radius:6px; padding:10px; font-size:13px;}}"
def style_btn(color): return f"QPushButton{{background:{color}; color:#000000; border-radius:6px; padding:10px; font-weight:bold; font-size:13px;}} QPushButton:hover{{opacity:0.8;}}"

# --- DÜZENLEME PENCERESİ ---
class EditDialog(QDialog):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.setWindowTitle("Kayıt Güncelleme Paneli")
        self.setFixedSize(400, 500)
        self.setStyleSheet(f"background:{C['bg']}; color:{C['text']};")
        self.data = data
        self.init_ui()

    def init_ui(self):
        lay = QVBoxLayout(self)
        self.inp_mus = QLineEdit(self.data[1]); self.inp_mus.setStyleSheet(style_input())
        self.inp_rota = QLineEdit(self.data[2]); self.inp_rota.setStyleSheet(style_input())
        self.inp_tarih = QLineEdit(self.data[3]); self.inp_tarih.setStyleSheet(style_input())
        self.inp_gun = QLineEdit(str(self.data[4])); self.inp_gun.setStyleSheet(style_input())
        self.inp_tutar = QLineEdit(str(self.data[5])); self.inp_tutar.setStyleSheet(style_input())
        
        btn_save = QPushButton("VERİLERİ GÜNCELLE")
        btn_save.setStyleSheet(style_btn(C['accent']))
        btn_save.clicked.connect(self.validate_and_accept)

        lay.addWidget(QLabel("Müşteri Ad Soyad:")); lay.addWidget(self.inp_mus)
        lay.addWidget(QLabel("Rota:")); lay.addWidget(self.inp_rota)
        lay.addWidget(QLabel("Tarih:")); lay.addWidget(self.inp_tarih)
        lay.addWidget(QLabel("Süre (Gün):")); lay.addWidget(self.inp_gun)
        lay.addWidget(QLabel("Bütçe (₺):")); lay.addWidget(self.inp_tutar)
        lay.addWidget(btn_save)

    def validate_and_accept(self):
        mus = self.inp_mus.text().strip()
        if any(char.isdigit() for char in mus):
            QMessageBox.critical(self, "Hata", "Müşteri adında rakam bulunamaz!"); return
        try:
            int(self.inp_gun.text())
            float(self.inp_tutar.text())
            self.accept()
        except ValueError:
            QMessageBox.critical(self, "Hata", "Gün ve Bütçe alanlarına sadece sayı girmelisiniz!"); return

    def get_data(self):
        return (self.inp_mus.text(), self.inp_rota.text(), self.inp_tarih.text(), 
                int(self.inp_gun.text()), float(self.inp_tutar.text()))

# --- ANA SİSTEM ---
class AuroraOS(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("Aurora Enterprise | Global Travel OS")
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
        kart = QFrame(); kart.setFixedSize(400, 450); kart.setStyleSheet(style_card())
        k_lay = QVBoxLayout(kart); k_lay.setContentsMargins(40, 40, 40, 40); k_lay.setSpacing(20)
        
        self.lbl_logo = QLabel("AURORA")
        self.lbl_logo.setStyleSheet(f"color:{C['accent']}; font-size:32px; font-weight:900; letter-spacing: 5px;")
        self.lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.inp_user = QLineEdit(); self.inp_user.setPlaceholderText("Yetkili ID"); self.inp_user.setStyleSheet(style_input())
        self.inp_pass = QLineEdit(); self.inp_pass.setPlaceholderText("Şifre"); self.inp_pass.setEchoMode(QLineEdit.EchoMode.Password); self.inp_pass.setStyleSheet(style_input())
        
        btn_login = QPushButton("SİSTEME GİRİŞ YAP"); btn_login.setStyleSheet(style_btn(C['accent']))
        btn_login.clicked.connect(self.check_login)
        
        k_lay.addStretch(); k_lay.addWidget(self.lbl_logo); k_lay.addWidget(self.inp_user); k_lay.addWidget(self.inp_pass); k_lay.addWidget(btn_login); k_lay.addStretch()
        lay.addWidget(kart, alignment=Qt.AlignmentFlag.AlignCenter)

    def check_login(self):
        if self.inp_user.text() == "admin" and self.inp_pass.text() == "1234":
            self.main_stack.setCurrentIndex(1); self.refresh_dashboard()
        else: QMessageBox.warning(self, "Hata", "Erişim Reddedildi!")

    def build_main_app(self):
        self.app_widget = QWidget()
        ana_lay = QHBoxLayout(self.app_widget); ana_lay.setContentsMargins(0,0,0,0); ana_lay.setSpacing(0)
        sidebar = QFrame(); sidebar.setFixedWidth(240); sidebar.setStyleSheet(f"background:{C['card']};")
        sb_lay = QVBoxLayout(sidebar); sb_lay.setContentsMargins(0,30,0,20)
        
        sayfalar = [("📊", "Dashboard"), ("📍", "Planlama"), ("✏️", "Düzenle")]
        for i, (ico, txt) in enumerate(sayfalar):
            btn = QPushButton(f"  {ico}  {txt}")
            btn.setFixedHeight(50); btn.setStyleSheet("text-align:left; padding-left:20px; background:transparent; color:#94A3B8; font-weight:bold; border:none;")
            btn.clicked.connect(lambda _, x=i: self.nav(x))
            sb_lay.addWidget(btn)
        sb_lay.addStretch(); ana_lay.addWidget(sidebar)
        self.pages = QStackedWidget(); ana_lay.addWidget(self.pages)
        self.build_dashboard(); self.build_rota_page(); self.build_finans_page()
        self.pages.addWidget(self.page_dash); self.pages.addWidget(self.page_rota); self.pages.addWidget(self.page_finans)

    def nav(self, index): self.pages.setCurrentIndex(index); self.refresh_dashboard()

    def build_dashboard(self):
        self.page_dash = QWidget(); lay = QVBoxLayout(self.page_dash); lay.setContentsMargins(40,40,40,40)
        self.lbl_sum = QLabel("Genel Durum Analizi"); self.lbl_sum.setStyleSheet("font-size:24px; font-weight:bold;")
        lay.addWidget(self.lbl_sum); lay.addSpacing(20)
        
        self.t_dash = QTableWidget(); self.t_dash.setColumnCount(6)
        self.t_dash.setHorizontalHeaderLabels(["ID", "Müşteri", "Rota", "Tarih", "Gün", "Ciro (₺)"])
        self.t_dash.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.t_dash.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.t_dash.setStyleSheet(f"QTableWidget {{ background:{C['card']}; color:{C['text']}; border:none; }}")
        
        lay.addWidget(QLabel("🛣️ Aktif Planlar ve Finansal Dağılım (İzleme)")); lay.addWidget(self.t_dash)

    def build_rota_page(self):
        self.page_rota = QWidget(); lay = QVBoxLayout(self.page_rota); lay.setContentsMargins(40,40,40,40)
        kart = QFrame(); kart.setStyleSheet(style_card())
        klay = QGridLayout(kart); klay.setSpacing(20); klay.setContentsMargins(30,30,30,30)
        
        self.sehirler = ["İstanbul", "Ankara", "İzmir", "Trabzon", "Antalya", "Rize", "Nevşehir", "Samsun", "Muğla"]
        self.inp_m = QLineEdit(); self.inp_m.setPlaceholderText("Müşteri Ad Soyad"); self.inp_m.setStyleSheet(style_input())
        self.inp_k = QLineEdit(); self.inp_k.setPlaceholderText("Kişi Sayısı"); self.inp_k.setStyleSheet(style_input())
        
        self.cb_n1 = QComboBox(); self.cb_n1.addItems(self.sehirler); self.cb_n1.setStyleSheet(style_input())
        self.cb_n2 = QComboBox(); self.cb_n2.addItems(self.sehirler); self.cb_n2.setStyleSheet(style_input())
        
        # Tarih Paneli
        tarih_lay = QHBoxLayout()
        self.cb_gun = QComboBox(); self.cb_gun.addItems([str(i) for i in range(1, 32)]); self.cb_gun.setStyleSheet(style_input())
        self.cb_ay = QComboBox(); self.cb_ay.addItems(["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]); self.cb_ay.setStyleSheet(style_input())
        self.cb_yil = QComboBox(); self.cb_yil.addItems(["2026", "2027", "2028"]); self.cb_yil.setStyleSheet(style_input())
        tarih_lay.addWidget(self.cb_gun); tarih_lay.addWidget(self.cb_ay); tarih_lay.addWidget(self.cb_yil)
        
        self.inp_süre = QLineEdit(); self.inp_süre.setPlaceholderText("Süre (Gün)"); self.inp_süre.setStyleSheet(style_input())
        
        btn = QPushButton("PLANLAMAYI VERİTABANINA İŞLE"); btn.setStyleSheet(style_btn(C['accent'])); btn.clicked.connect(self.kaydet_rota)
        
        klay.addWidget(QLabel("Müşteri Ad Soyad:"), 0, 0); klay.addWidget(self.inp_m, 0, 1)
        klay.addWidget(QLabel("Kişi Sayısı:"), 0, 2); klay.addWidget(self.inp_k, 0, 3)
        klay.addWidget(QLabel("Çıkış Noktası:"), 1, 0); klay.addWidget(self.cb_n1, 1, 1)
        klay.addWidget(QLabel("Varış Noktası:"), 1, 2); klay.addWidget(self.cb_n2, 1, 3)
        klay.addWidget(QLabel("Tarih Seçimi:"), 2, 0); klay.addLayout(tarih_lay, 2, 1)
        klay.addWidget(QLabel("Toplam Süre:"), 2, 2); klay.addWidget(self.inp_süre, 2, 3)
        klay.addWidget(btn, 3, 0, 1, 4)
        lay.addWidget(kart); lay.addStretch()

    def kaydet_rota(self):
        mus = self.inp_m.text().strip()
        kisi = self.inp_k.text().strip()
        süre = self.inp_süre.text().strip()
        nereden = self.cb_n1.currentText()
        nereye = self.cb_n2.currentText()
        
        if nereden == nereye:
            QMessageBox.critical(self, "Mantık Hatası", f"Başlangıç ve varış noktası aynı ({nereden}) olamaz!"); return
        if not mus or not kisi or not süre:
            QMessageBox.warning(self, "Eksik Veri", "Lütfen tüm alanları doldurun!"); return
        if any(char.isdigit() for char in mus):
            QMessageBox.critical(self, "Hata", "Müşteri adında rakam kullanılamaz!"); return
        if not kisi.isdigit() or not süre.isdigit():
            QMessageBox.critical(self, "Hata", "Kişi ve Süre alanları rakam olmalıdır!"); return
        if self.db.musteri_plani_var_mi(mus):
            QMessageBox.warning(self, "Mükerrer Kayıt", "Bu müşteri adına zaten aktif bir plan bulunmaktadır!"); return
        
        tarih = f"{self.cb_gun.currentText()} {self.cb_ay.currentText()} {self.cb_yil.currentText()}"
        tutar = int(kisi) * int(süre) * 1750
        self.db.plan_ekle(mus, f"{nereden} -> {nereye}", tarih, int(süre), tutar)
        self.refresh_dashboard(); QMessageBox.information(self, "Başarılı", "Kayıt Aurora veritabanına işlendi.")

    def build_finans_page(self):
        self.page_finans = QWidget(); lay = QVBoxLayout(self.page_finans); lay.setContentsMargins(40,40,40,40)
        self.t = QTableWidget(); self.t.setColumnCount(7)
        self.t.setHorizontalHeaderLabels(["ID", "Müşteri", "Rota", "Tarih", "Gün", "Bütçe", "İşlem"])
        self.t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.t.setStyleSheet(f"QTableWidget {{ background:{C['card']}; color:{C['text']}; border:none; }}")
        lay.addWidget(self.t)

    def refresh_dashboard(self):
        sayi, ciro = self.db.finans_ozeti()
        self.lbl_sum.setText(f"Aktif Rota: {sayi if sayi else 0} | Toplam Ciro: {ciro if ciro else 0} ₺")
        planlar = self.db.tum_planlar()
        
        # Dashboard Tablosu (Ciro Sütunu Dahil)
        self.t_dash.setRowCount(0)
        for p in planlar:
            r = self.t_dash.rowCount(); self.t_dash.insertRow(r)
            for i in range(5): self.t_dash.setItem(r, i, QTableWidgetItem(str(p[i])))
            self.t_dash.setItem(r, 5, QTableWidgetItem(f"{p[5]:,.0f} ₺"))
            
        # Düzenle Tablosu
        self.t.setRowCount(0)
        for p in planlar:
            r = self.t.rowCount(); self.t.insertRow(r)
            for i in range(6): 
                val = f"{p[i]:,.0f} ₺" if i == 5 else str(p[i])
                self.t.setItem(r, i, QTableWidgetItem(val))
            w = QWidget(); bl = QHBoxLayout(w); bl.setContentsMargins(2,2,2,2)
            be = QPushButton("✏️"); be.setStyleSheet(f"background:{C['edit']}; color:white;")
            be.clicked.connect(lambda _, x=p: self.edit(x))
            bd = QPushButton("🗑️"); bd.setStyleSheet(f"background:{C['danger']}; color:white;")
            bd.clicked.connect(lambda _, x=p[0]: self.delete(x))
            bl.addWidget(be); bl.addWidget(bd); self.t.setCellWidget(r, 6, w)

    def delete(self, pid):
        if QMessageBox.question(self, "Onay", "Bu kaydı silmek istediğinize emin misiniz?") == QMessageBox.StandardButton.Yes:
            self.db.plan_sil(pid); self.refresh_dashboard()

    def edit(self, data):
        d = EditDialog(self, data)
        if d.exec():
            n_m, n_r, n_t, n_g, n_f = d.get_data()
            self.db.plan_guncelle(data[0], n_m, n_r, n_t, n_g, n_f); self.refresh_dashboard()

if __name__ == "__main__":
    app = QApplication(sys.argv); win = AuroraOS(); win.show(); sys.exit(app.exec())