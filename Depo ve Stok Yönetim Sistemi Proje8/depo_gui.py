import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QFrame,
    QStackedWidget, QHeaderView, QLineEdit, QGridLayout,
    QSpinBox, QDoubleSpinBox, QMessageBox, QComboBox, QDialog, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from depo_sistemi import Urun, Siparis, DepoDB

# ── Depo/Lojistik Temalı SaaS Paleti ──
C = {
    "bg": "#F8FAFC", "sidebar": "#FFFFFF", "card": "#FFFFFF", "border": "#E2E8F0",
    "accent": "#2563EB", "accent_hover": "#1D4ED8", "success": "#16A34A", 
    "warning": "#F97316", "danger": "#EF4444", "text": "#0F172A", 
    "text_sub": "#64748B", "row_alt": "#F8FAFC", "row_sel": "#EFF6FF", "input_bg": "#FFFFFF",
}

def card_ss(): return f"background:{C['card']}; border:1px solid {C['border']}; border-radius:12px;"
def btn_primary_ss(): return f"QPushButton{{background:{C['accent']}; color:#fff; border-radius:8px; padding:9px 20px; font-weight:bold;}} QPushButton:hover{{background:{C['accent_hover']};}}"
def btn_success_ss(): return f"QPushButton{{background:{C['success']}; color:#fff; border-radius:8px; padding:9px 20px; font-weight:bold;}}"
def input_ss(): 
    return f"QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{ background:{C['input_bg']}; color:{C['text']}; border:1px solid {C['border']}; border-radius:6px; padding:7px 10px; }}"
TABLE_SS = f"QTableWidget {{ background:{C['card']}; border:1px solid {C['border']}; border-radius:8px; alternate-background-color:{C['row_alt']}; }} QHeaderView::section {{ background:{C['row_alt']}; font-weight:bold; border:none; border-bottom:1px solid {C['border']}; }}"
TBL_BTN_SS = f"QPushButton{{background:{C['danger']}; color:white; border-radius:4px; padding:4px 8px; font-weight:bold;}} QPushButton:hover{{background:#DC2626;}}"

def shadow(widget):
    fx = QGraphicsDropShadowEffect(); fx.setBlurRadius(15); fx.setColor(QColor(0,0,0,10)); fx.setOffset(0,2)
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
        
        lbl_baslik = QLabel("Depo Özeti")
        lbl_baslik.setStyleSheet("font-size:24px; font-weight:900;")
        lay.addWidget(lbl_baslik)
        
        self.kpi_row = QHBoxLayout(); lay.addLayout(self.kpi_row)
        
        self.tablo = QTableWidget(); self.tablo.setColumnCount(7)
        self.tablo.setHorizontalHeaderLabels(["Sipariş No", "Ürün Adı", "Adet", "Birim Fiyat", "Toplam Tutar", "Tarih", "İşlem"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.tablo.setStyleSheet(TABLE_SS); lay.addWidget(self.tablo); self.refresh()

    def refresh(self):
        siparisler = self.db.get_siparisler_detayli(); urunler = self.db.get_urunler()
        ciro = sum(s[4] for s in siparisler) if siparisler else 0
        kritik_stok = sum(1 for u in urunler if u.stok < 10) 
        
        while self.kpi_row.count():
            item = self.kpi_row.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        self.kpi_row.addWidget(KpiCard("Kayıtlı Ürün", len(urunler), "Depodaki çeşit sayısı", C['accent']))
        self.kpi_row.addWidget(KpiCard("Kritik Stok", kritik_stok, "10 adetin altındaki ürünler", C['danger'] if kritik_stok > 0 else C['success']))
        self.kpi_row.addWidget(KpiCard("Gerçekleşen Satış", f"₺{ciro:,.2f}", "Toplam sipariş hacmi", C['warning']))

        self.tablo.setRowCount(0)
        for s in siparisler:
            r = self.tablo.rowCount(); self.tablo.insertRow(r)
            self.tablo.setItem(r, 0, QTableWidgetItem(f"#{s[0]}")); self.tablo.setItem(r, 1, QTableWidgetItem(s[1]))
            self.tablo.setItem(r, 2, QTableWidgetItem(f"{s[2]} Adet")); self.tablo.setItem(r, 3, QTableWidgetItem(f"₺{s[3]:.2f}"))
            
            t_item = QTableWidgetItem(f"₺{s[4]:,.2f}"); t_item.setForeground(QColor(C['success']))
            self.tablo.setItem(r, 4, t_item); self.tablo.setItem(r, 5, QTableWidgetItem(s[5]))
            
            btn_sil = QPushButton("🗑️ İptal"); btn_sil.setStyleSheet(TBL_BTN_SS); btn_sil.setCursor(Qt.PointingHandCursor)
            btn_sil.clicked.connect(lambda _, kayit_id=s[0]: self._siparis_sil(kayit_id))
            btn_w = QWidget(); btn_l = QHBoxLayout(btn_w); btn_l.setContentsMargins(5, 2, 5, 2); btn_l.addWidget(btn_sil)
            self.tablo.setCellWidget(r, 6, btn_w)

    def _siparis_sil(self, siparis_id):
        # Kullanıcıya stoğun geri ekleneceğini belirten yeni uyarı mesajı
        mesaj = "Bu siparişi iptal edip kayıtlardan silmek istediğinize emin misiniz?\n(Düşülen stok otomatik olarak depoya geri eklenecektir.)"
        
        if QMessageBox.question(self, 'Sipariş İptali Onayı', mesaj, QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.db.siparis_sil(siparis_id)
            self.refresh()
class UrunPage(QWidget):
    def __init__(self, db, dash):
        super().__init__(); self.db, self.dash = db, dash; self._build()
    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(30, 25, 30, 25)
        
        lbl_baslik = QLabel("Ürün ve Stok Yönetimi")
        lbl_baslik.setStyleSheet("font-size:24px; font-weight:900;")
        lay.addWidget(lbl_baslik)
        
        h_lay = QHBoxLayout(); h_lay.setSpacing(20)
        
        k1 = QFrame(); k1.setStyleSheet(card_ss()); l1 = QVBoxLayout(k1)
        lbl_k1 = QLabel("YENİ ÜRÜN TANIMLA"); lbl_k1.setStyleSheet(f"color:{C['text_sub']}; font-weight:bold;"); l1.addWidget(lbl_k1)
        self.i_id = QSpinBox(); self.i_id.setRange(1, 99999); self.i_id.setStyleSheet(input_ss())
        self.i_ad = QLineEdit(); self.i_ad.setPlaceholderText("Ürün Adı"); self.i_ad.setStyleSheet(input_ss())
        self.i_stok = QSpinBox(); self.i_stok.setRange(0, 9999); self.i_stok.setStyleSheet(input_ss())
        self.i_fiyat = QDoubleSpinBox(); self.i_fiyat.setRange(1, 999999); self.i_fiyat.setStyleSheet(input_ss())
        l1.addWidget(QLabel("Barkod / ID")); l1.addWidget(self.i_id); l1.addWidget(QLabel("Ürün Adı")); l1.addWidget(self.i_ad)
        l1.addWidget(QLabel("Başlangıç Stoğu")); l1.addWidget(self.i_stok); l1.addWidget(QLabel("Birim Fiyatı (₺)")); l1.addWidget(self.i_fiyat)
        b1 = QPushButton("Kataloğa Ekle"); b1.setStyleSheet(btn_primary_ss()); b1.clicked.connect(self._ekle); l1.addWidget(b1)
        h_lay.addWidget(k1)

        k2 = QFrame(); k2.setStyleSheet(card_ss()); l2 = QVBoxLayout(k2)
        lbl_k2 = QLabel("HIZLI STOK GÜNCELLEME"); lbl_k2.setStyleSheet(f"color:{C['text_sub']}; font-weight:bold;"); l2.addWidget(lbl_k2)
        self.c_urun = QComboBox(); self.c_urun.setStyleSheet(input_ss())
        self.g_miktar = QSpinBox(); self.g_miktar.setRange(1, 9999); self.g_miktar.setStyleSheet(input_ss())
        l2.addWidget(QLabel("İşlem Yapılacak Ürün")); l2.addWidget(self.c_urun)
        l2.addWidget(QLabel("Miktar (Adet)")); l2.addWidget(self.g_miktar)
        
        b2 = QPushButton("Mal Girişi (Stok Artır)"); b2.setStyleSheet(btn_success_ss()); b2.clicked.connect(self._stok_arttir)
        b3 = QPushButton("Zayi / Fire (Stok Azalt)"); b3.setStyleSheet(f"QPushButton{{background:{C['warning']}; color:#fff; border-radius:8px; padding:9px 20px; font-weight:bold;}}"); b3.clicked.connect(self._stok_azalt)
        l2.addWidget(b2); l2.addWidget(b3); l2.addStretch()
        h_lay.addWidget(k2); lay.addLayout(h_lay)

        self.tablo = QTableWidget(); self.tablo.setColumnCount(5)
        self.tablo.setHorizontalHeaderLabels(["ID", "Ürün Adı", "Mevcut Stok", "Birim Fiyat", "İşlem"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.tablo.setStyleSheet(TABLE_SS); lay.addWidget(self.tablo); self.refresh()

    def refresh(self):
        self.c_urun.clear(); urunler = self.db.get_urunler(); self.tablo.setRowCount(0)
        for u in urunler:
            self.c_urun.addItem(u.ad, u.urun_id)
            r = self.tablo.rowCount(); self.tablo.insertRow(r)
            self.tablo.setItem(r, 0, QTableWidgetItem(str(u.urun_id))); self.tablo.setItem(r, 1, QTableWidgetItem(u.ad))
            
            s_item = QTableWidgetItem(f"{u.stok} Adet")
            if u.stok < 10: s_item.setForeground(QColor(C['danger']))
            self.tablo.setItem(r, 2, s_item)
            self.tablo.setItem(r, 3, QTableWidgetItem(f"₺{u.fiyat:.2f}"))
            
            btn_sil = QPushButton("🗑️ Sil"); btn_sil.setStyleSheet(TBL_BTN_SS); btn_sil.setCursor(Qt.PointingHandCursor)
            btn_sil.clicked.connect(lambda _, u_id=u.urun_id, ad=u.ad: self._urun_sil(u_id, ad))
            btn_w = QWidget(); btn_l = QHBoxLayout(btn_w); btn_l.setContentsMargins(5, 2, 5, 2); btn_l.addWidget(btn_sil)
            self.tablo.setCellWidget(r, 4, btn_w)

    def _ekle(self):
        u = Urun(self.i_id.value(), self.i_ad.text(), self.i_stok.value(), self.i_fiyat.value())
        ok, msg = self.db.urun_ekle(u); QMessageBox.information(self, "Bilgi", msg); self.refresh(); self.dash.refresh()

    def _get_secili_urun(self):
        urun_id = self.c_urun.currentData()
        return next((u for u in self.db.get_urunler() if u.urun_id == urun_id), None)

    def _stok_arttir(self):
        urun = self._get_secili_urun()
        if urun:
            ok, msg = urun.stok_arttir(self.g_miktar.value(), self.db)
            QMessageBox.information(self, "İşlem Başarılı", msg); self.refresh(); self.dash.refresh()

    def _stok_azalt(self):
        urun = self._get_secili_urun()
        if urun:
            ok, msg = urun.stok_azalt(self.g_miktar.value(), self.db)
            if ok: QMessageBox.information(self, "İşlem Başarılı", msg)
            else: QMessageBox.warning(self, "Hata", msg)
            self.refresh(); self.dash.refresh()

    def _urun_sil(self, urun_id, ad):
        if QMessageBox.question(self, 'Onay', f"'{ad}' isimli ürünü ve tüm satış geçmişini siliyorsunuz. Emin misiniz?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.db.urun_sil(urun_id); self.refresh(); self.dash.refresh()

class SiparisPage(QWidget):
    def __init__(self, db, dash, urun_page):
        super().__init__(); self.db, self.dash, self.urun_page = db, dash, urun_page; self._build()
        
    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(30, 25, 30, 25); lay.setSpacing(20)
        
        lbl_baslik = QLabel("Yeni Sipariş / Satış Çıkışı")
        lbl_baslik.setStyleSheet("font-size:24px; font-weight:900;")
        lay.addWidget(lbl_baslik)
        
        k = QFrame(); k.setStyleSheet(card_ss()); l = QVBoxLayout(k); l.setSpacing(15)
        self.c_urun = QComboBox(); self.i_adet = QSpinBox(); self.i_adet.setRange(1, 9999)
        for w in [self.c_urun, self.i_adet]: w.setStyleSheet(input_ss()); w.setFixedHeight(40)
        
        l.addWidget(QLabel("Satılacak Ürün")); l.addWidget(self.c_urun)
        l.addWidget(QLabel("Satış Adeti")); l.addWidget(self.i_adet)
        
        btn = QPushButton("Siparişi Onayla ve Çıkış Yap"); btn.setStyleSheet(btn_primary_ss()); btn.clicked.connect(self._kaydet)
        l.addWidget(btn); l.addStretch(); lay.addWidget(k); lay.addStretch(); self.refresh()

    def refresh(self):
        self.c_urun.clear()
        for u in self.db.get_urunler(): self.c_urun.addItem(f"{u.ad} (Stok: {u.stok} | Fiyat: ₺{u.fiyat})", u.urun_id)

    def _kaydet(self):
        if self.c_urun.currentData():
            yeni_siparis = Siparis(None, self.c_urun.currentData(), self.i_adet.value())
            ok, msg = yeni_siparis.siparis_olustur(self.db)
            
            if ok:
                QMessageBox.information(self, "Başarılı", msg)
                self.dash.refresh(); self.urun_page.refresh(); self.refresh()
            else:
                QMessageBox.warning(self, "Stok Hatası", msg)

# ── LOGIN EKRANI (TAMAMEN YENİLENDİ VE GENİŞLETİLDİ) ──
class LoginEkrani(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DepoPro Giriş")
        self.setFixedSize(400, 500) # Daha ferah bir boyut
        self.setStyleSheet(f"QDialog {{ background: {C['bg']}; }}")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 40, 40, 40)
        lay.setSpacing(15)

        # Logo ve Başlık
        lbl_logo = QLabel("📦 DepoPro")
        lbl_logo.setStyleSheet(f"color:{C['accent']}; font-size:32px; font-weight:900;")
        lbl_logo.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl_logo)

        # Alt Açıklama Metni
        lbl_alt = QLabel("Sisteme giriş yapmak için bilgilerinizi girin.")
        lbl_alt.setStyleSheet(f"color:{C['text_sub']}; font-size:13px;")
        lbl_alt.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl_alt)
        
        lay.addSpacing(20)

        # Kullanıcı Adı Alanı
        lbl_user = QLabel("Kullanıcı Adı")
        lbl_user.setStyleSheet(f"color:{C['text']}; font-weight:bold;")
        lay.addWidget(lbl_user)

        self.u = QLineEdit()
        self.u.setPlaceholderText("Örn: ziya")
        self.u.setStyleSheet(input_ss())
        self.u.setFixedHeight(45)
        lay.addWidget(self.u)

        # Şifre Alanı
        lbl_pass = QLabel("Şifre")
        lbl_pass.setStyleSheet(f"color:{C['text']}; font-weight:bold;")
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
        btn.setDefault(True) # Enter'a basınca giriş yapsın
        btn.clicked.connect(self._login)
        lay.addWidget(btn)

        lay.addStretch()

    def _login(self):
        if self.u.text().strip() == "ziya" and self.p.text().strip() == "1234": 
            self.accept()
        else: 
            QMessageBox.warning(self, "Hata", "Kullanıcı adı veya şifre yanlış!")
            self.p.clear()

# ── ANA PENCERE ──
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("DepoPro - Stok ve Lojistik Yönetimi"); self.resize(1150, 700)
        self.setStyleSheet(f"QMainWindow{{background:{C['bg']}; color:{C['text']};}}"); self.db = self._veri_kur(); self._build()

    def _veri_kur(self):
        db = DepoDB()
        if not db.get_urunler():
            db.urun_ekle(Urun(101, "A4 Fotokopi Kağıdı (Koli)", 250, 120.0))
            db.urun_ekle(Urun(102, "Mekanik Klavye (TR Q)", 15, 850.0))
            db.urun_ekle(Urun(103, "Lojistik Taşıma Arabası", 8, 3500.0))
        return db

    def _build(self):
        merkez = QWidget(); self.setCentralWidget(merkez); ana = QHBoxLayout(merkez); ana.setContentsMargins(0, 0, 0, 0); ana.setSpacing(0)
        sb = QFrame(); sb.setFixedWidth(240); sb.setStyleSheet(f"background:{C['sidebar']}; border-right:1px solid {C['border']};")
        slay = QVBoxLayout(sb); slay.setContentsMargins(0, 30, 0, 0)
        
        lbl_logo_side = QLabel(" 📦 DepoPro")
        lbl_logo_side.setStyleSheet(f"color:{C['accent']}; font-size:22px; font-weight:900; margin-bottom:20px;")
        slay.addWidget(lbl_logo_side)
        
        self.nav = []
        for ikon, metin in [("📊", "Genel Bakış"), ("📦", "Stok Yönetimi"), ("📝", "Sipariş (Satış Çıkışı)")]:
            b = SideBtn(ikon, metin); b.clicked.connect(lambda _, m=metin: self._goto(m)); slay.addWidget(b); self.nav.append(b)
        slay.addStretch(); ana.addWidget(sb)

        ic = QWidget(); il = QVBoxLayout(ic); il.setContentsMargins(0,0,0,0); il.setSpacing(0)
        tb = QFrame(); tb.setFixedHeight(65); tb.setStyleSheet(f"background:{C['sidebar']}; border-bottom:1px solid {C['border']};"); tl = QHBoxLayout(tb)
        
        self.lbl = QLabel("Genel Bakış")
        self.lbl.setStyleSheet("font-weight:bold; font-size:14px;")
        tl.addWidget(self.lbl); tl.addStretch()
        
        lbl_user = QLabel("👤 Ziya Eren Yılmaz")
        lbl_user.setStyleSheet("font-weight:bold; padding:8px;")
        tl.addWidget(lbl_user); il.addWidget(tb)

        self.stack = QStackedWidget(); self.p_dash = DashboardPage(self.db); self.p_urun = UrunPage(self.db, self.p_dash); self.p_sip = SiparisPage(self.db, self.p_dash, self.p_urun)
        for p in [self.p_dash, self.p_urun, self.p_sip]: self.stack.addWidget(p)
        il.addWidget(self.stack); ana.addWidget(ic); self._goto("Genel Bakış")

    def _goto(self, s):
        idx = {"Genel Bakış": 0, "Stok Yönetimi": 1, "Sipariş (Satış Çıkışı)": 2}[s]
        self.stack.setCurrentIndex(idx); self.lbl.setText(s.upper())
        for i, b in enumerate(self.nav): b.setChecked(i == idx)
        if idx == 1: self.p_urun.refresh()
        if idx == 2: self.p_sip.refresh()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginEkrani()
    if login.exec_() == QDialog.Accepted: 
        win = MainWindow()
        win.show()
        sys.exit(app.exec_())