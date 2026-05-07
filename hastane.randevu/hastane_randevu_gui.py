"""
============================================================
  RANDEVU YÖNETİM SİSTEMİ — PyQt5 Arayüzü
============================================================
Kurulum  : pip install PyQt5
Çalıştır : py -3.13 randevu_gui.py
Not      : randevu_sistemi.py ile aynı klasörde olmalıdır.
"""

import sys
from datetime import date, datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QFrame,
    QStackedWidget, QHeaderView, QLineEdit, QGridLayout,
    QDateEdit, QComboBox, QMessageBox,
    QAbstractItemView, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QColor, QPalette

from hastane_randevu_sistemi import DatabaseManager, Hasta, Doktor, Randevu

# ══════════════════════════════════════════════════════════
#  RENK PALETİ
# ══════════════════════════════════════════════════════════
C = {
    "bg":        "#121212",
    "sidebar":   "#1E1E2E",
    "card":      "#242436",
    "border":    "#3B3B54",
    "accent":    "#9D4EDD",
    "accent2":   "#7B2CBF",
    "success":   "#10B981",
    "warning":   "#F59E0B",
    "danger":    "#EF4444",
    "text":      "#F8F8F2",
    "text_sub":  "#A6ACCD",
    "text_dim":  "#6272A4",
    "row_alt":   "#202030",
    "row_sel":   "#3B2554",
    "input_bg":  "#181825",
}

# ── Stil yardımcıları ──────────────────────────────────────
def card_ss():
    return f"""
        background:{C['card']};
        border:1px solid {C['border']};
        border-radius:12px;
    """

def btn_primary_ss():
    return f"""
        QPushButton{{
            background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {C['accent2']},stop:1 {C['accent']});
            color:#fff;border:none;border-radius:8px;
            padding:9px 20px;font-size:13px;font-weight:600;
        }}
        QPushButton:hover{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 {C['accent']},stop:1 #48CAE4);}}
        QPushButton:pressed{{background:{C['accent2']};}}
    """

def btn_danger_ss():
    return f"""
        QPushButton{{background:{C['danger']};color:#fff;border:none;
            border-radius:8px;padding:9px 20px;font-size:13px;font-weight:600;}}
        QPushButton:hover{{background:#FF6B8A;}}
    """

def input_ss():
    return f"""
        QLineEdit, QComboBox, QDateEdit{{
            background:{C['input_bg']};color:{C['text']};
            border:1px solid {C['border']};border-radius:8px;
            padding:7px 10px;font-size:13px;
        }}
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus{{
            border:1.5px solid {C['accent']};
        }}
        QComboBox::drop-down{{border:none;}}
        QDateEdit::drop-down{{background:{C['border']};width:22px;border-radius:3px;}}
    """

TABLE_SS = f"""
    QTableWidget{{
        background:{C['card']};color:{C['text']};border:none;
        gridline-color:{C['border']};font-size:13px;
        selection-background-color:{C['row_sel']};outline:none;
        alternate-background-color:{C['row_alt']};
    }}
    QTableWidget::item{{padding:9px 13px;border-bottom:1px solid {C['border']};}}
    QTableWidget::item:selected{{background:{C['row_sel']};color:{C['accent']};}}
    QHeaderView::section{{
        background:{C['sidebar']};color:{C['accent']};
        padding:9px 13px;border:none;
        border-bottom:2px solid {C['accent']};
        font-size:11px;font-weight:700;letter-spacing:0.8px;
    }}
    QScrollBar:vertical{{background:{C['bg']};width:8px;border-radius:4px;}}
    QScrollBar::handle:vertical{{background:{C['border']};border-radius:4px;min-height:20px;}}
    QScrollBar::handle:vertical:hover{{background:{C['accent']};}}
    QScrollBar:horizontal{{background:{C['bg']};height:8px;border-radius:4px;}}
    QScrollBar::handle:horizontal{{background:{C['border']};border-radius:4px;}}
"""

def shadow(widget, blur=18, dy=4):
    fx = QGraphicsDropShadowEffect(widget)
    fx.setBlurRadius(blur)
    fx.setColor(QColor(0, 0, 0, 80))
    fx.setOffset(0, dy)
    widget.setGraphicsEffect(fx)

# ══════════════════════════════════════════════════════════
#  BİLEŞENLER
# ══════════════════════════════════════════════════════════
class KpiCard(QFrame):
    def __init__(self, baslik, deger, alt, renk, parent=None):
        super().__init__(parent)
        self.setFixedHeight(114)
        self.setStyleSheet(f"""
            QFrame{{background:{C['card']};border:1px solid {C['border']};
                border-radius:13px;border-left:4px solid {renk};}}
        """)
        shadow(self)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 12, 18, 12)
        lay.setSpacing(3)

        t = f"color:{C['text_sub']};font-size:10px;font-weight:700;letter-spacing:1px;background:transparent;border:none;"
        v = f"color:{renk};font-size:29px;font-weight:800;background:transparent;border:none;"
        a = f"color:{C['text_dim']};font-size:11px;background:transparent;border:none;"

        lbl_t = QLabel(baslik.upper()); lbl_t.setStyleSheet(t)
        self.lbl_v = QLabel(str(deger)); self.lbl_v.setStyleSheet(v)
        lbl_a = QLabel(alt);            lbl_a.setStyleSheet(a)

        lay.addWidget(lbl_t)
        lay.addWidget(self.lbl_v)
        lay.addWidget(lbl_a)
        
    def set_value(self, val):
        self.lbl_v.setText(str(val))


class SideBtn(QPushButton):
    def __init__(self, metin, parent=None):
        super().__init__(f"  {metin}", parent)
        self.setCheckable(True)
        self.setFixedHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        self._refresh(False)

    def _refresh(self, aktif):
        if aktif:
            self.setStyleSheet(f"""
                QPushButton{{background:{C['row_sel']};color:{C['accent']};
                    border:none; border-radius:8px; margin: 2px 12px;
                    text-align:left; padding-left:16px;
                    font-size:13px;font-weight:700;}}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton{{background:transparent;color:{C['text_sub']};
                    border:none; border-radius:8px; margin: 2px 12px;
                    text-align:left; padding-left:16px;font-size:13px;}}
                QPushButton:hover{{background:{C['card']};color:{C['text']};}}
            """)

    def setChecked(self, v):
        super().setChecked(v)
        self._refresh(v)

# ══════════════════════════════════════════════════════════
#  SAYFALAR
# ══════════════════════════════════════════════════════════

class DashboardPage(QWidget):
    def __init__(self, db: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.setStyleSheet(f"background:{C['bg']};")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 22, 28, 22)
        lay.setSpacing(18)

        lbl = QLabel("Dashboard")
        lbl.setStyleSheet(f"color:{C['text']};font-size:21px;font-weight:800;")
        lay.addWidget(lbl)

        self.kpi_row = QHBoxLayout()
        self.kpi_row.setSpacing(14)
        lay.addLayout(self.kpi_row)
        
        self.k_doktor = KpiCard("Toplam Doktor", 0, "sistemde kayıtlı", C['accent'])
        self.k_hasta = KpiCard("Toplam Hasta", 0, "sistemde kayıtlı", C['success'])
        self.k_randevu = KpiCard("Toplam Randevu", 0, "tüm zamanlar", C['warning'])
        self.k_bugun = KpiCard("Bugünkü Randevular", 0, "aktif randevu", C['danger'])
        
        self.kpi_row.addWidget(self.k_doktor)
        self.kpi_row.addWidget(self.k_hasta)
        self.kpi_row.addWidget(self.k_randevu)
        self.kpi_row.addWidget(self.k_bugun)

        lay.addStretch()
        self.refresh()

    def refresh(self):
        doktorlar = self.db.get_all_doktorlar()
        hastalar = self.db.get_all_hastalar()
        randevular = self.db.get_all_randevular()
        bugun = datetime.now().strftime("%d.%m.%Y")
        bugunku_randevular = self.db.get_randevular_by_date(bugun)
        
        self.k_doktor.set_value(len(doktorlar))
        self.k_hasta.set_value(len(hastalar))
        self.k_randevu.set_value(len(randevular))
        self.k_bugun.set_value(len(bugunku_randevular))


class DoktorPage(QWidget):
    def __init__(self, db: DatabaseManager, main_app, parent=None):
        super().__init__(parent)
        self.db = db
        self.main_app = main_app
        self.setStyleSheet(f"background:{C['bg']};")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 22, 28, 22)
        
        lbl = QLabel("Doktor Yönetimi")
        lbl.setStyleSheet(f"color:{C['text']};font-size:21px;font-weight:800;")
        lay.addWidget(lbl)

        kart = QFrame(); kart.setStyleSheet(card_ss()); shadow(kart)
        klay = QVBoxLayout(kart); klay.setContentsMargins(22,18,22,18)
        
        grid = QGridLayout(); grid.setSpacing(10)
        self.inp_ad = QLineEdit(); self.inp_ad.setPlaceholderText("Ad Soyad")
        self.inp_uzmanlik = QLineEdit(); self.inp_uzmanlik.setPlaceholderText("Uzmanlık Alanı")
        self.inp_saatler = QLineEdit(); self.inp_saatler.setPlaceholderText("09:00, 10:00, 11:30")
        
        for w in [self.inp_ad, self.inp_uzmanlik, self.inp_saatler]:
            w.setStyleSheet(input_ss())
            
        grid.addWidget(QLabel("Doktor Adı", styleSheet=f"color:{C['text_sub']};"), 0, 0)
        grid.addWidget(self.inp_ad, 1, 0)
        grid.addWidget(QLabel("Uzmanlık", styleSheet=f"color:{C['text_sub']};"), 0, 1)
        grid.addWidget(self.inp_uzmanlik, 1, 1)
        grid.addWidget(QLabel("Uygun Saatler (Virgülle ayırın)", styleSheet=f"color:{C['text_sub']};"), 0, 2)
        grid.addWidget(self.inp_saatler, 1, 2)
        
        klay.addLayout(grid)
        btn_ekle = QPushButton("＋  Doktor Ekle")
        btn_ekle.setStyleSheet(btn_primary_ss()); btn_ekle.setCursor(Qt.PointingHandCursor)
        btn_ekle.clicked.connect(self._ekle)
        klay.addWidget(btn_ekle, alignment=Qt.AlignLeft)
        lay.addWidget(kart)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(4)
        self.tablo.setHorizontalHeaderLabels(["ID", "Ad Soyad", "Uzmanlık", "Uygun Saatler"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.setAlternatingRowColors(True)
        self.tablo.setStyleSheet(TABLE_SS)
        lay.addWidget(self.tablo)
        
        self.refresh()

    def _ekle(self):
        ad = self.inp_ad.text().strip()
        uzmanlik = self.inp_uzmanlik.text().strip()
        saatler_raw = self.inp_saatler.text().strip()
        if not ad or not uzmanlik or not saatler_raw:
            self.main_app._bildirim("Lütfen tüm alanları doldurun.", False)
            return
            
        if any(char.isdigit() for char in ad):
            self.main_app._bildirim("Doktor adı rakam içeremez.", False)
            return
            
        if any(char.isdigit() for char in uzmanlik):
            self.main_app._bildirim("Uzmanlık alanı rakam içeremez.", False)
            return
        
        saatler = [s.strip() for s in saatler_raw.split(',') if s.strip()]
        ok, msg = self.db.add_doktor(ad, uzmanlik, saatler)
        if ok:
            self.main_app._bildirim("Doktor başarıyla eklendi.", True)
            self.inp_ad.clear()
            self.inp_uzmanlik.clear()
            self.inp_saatler.clear()
            self.refresh()
            self.main_app.refresh_all()

    def refresh(self):
        self.tablo.setRowCount(0)
        doktorlar = self.db.get_all_doktorlar()
        for d in doktorlar:
            r = self.tablo.rowCount(); self.tablo.insertRow(r)
            self.tablo.setItem(r, 0, QTableWidgetItem(str(d.doktor_id)))
            self.tablo.setItem(r, 1, QTableWidgetItem(d.ad))
            self.tablo.setItem(r, 2, QTableWidgetItem(d.uzmanlik))
            self.tablo.setItem(r, 3, QTableWidgetItem(", ".join(d.uygun_saatler)))


class HastaPage(QWidget):
    def __init__(self, db: DatabaseManager, main_app, parent=None):
        super().__init__(parent)
        self.db = db
        self.main_app = main_app
        self.setStyleSheet(f"background:{C['bg']};")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 22, 28, 22)
        
        lbl = QLabel("Hasta Yönetimi")
        lbl.setStyleSheet(f"color:{C['text']};font-size:21px;font-weight:800;")
        lay.addWidget(lbl)

        kart = QFrame(); kart.setStyleSheet(card_ss()); shadow(kart)
        klay = QVBoxLayout(kart); klay.setContentsMargins(22,18,22,18)
        
        grid = QGridLayout(); grid.setSpacing(10)
        self.inp_ad = QLineEdit(); self.inp_ad.setPlaceholderText("Ad Soyad")
        self.inp_tc = QLineEdit(); self.inp_tc.setPlaceholderText("11 Haneli TC")
        self.inp_tel = QLineEdit(); self.inp_tel.setPlaceholderText("05XX XXX XX XX")
        
        for w in [self.inp_ad, self.inp_tc, self.inp_tel]:
            w.setStyleSheet(input_ss())
            
        grid.addWidget(QLabel("Hasta Adı", styleSheet=f"color:{C['text_sub']};"), 0, 0)
        grid.addWidget(self.inp_ad, 1, 0)
        grid.addWidget(QLabel("TC Kimlik", styleSheet=f"color:{C['text_sub']};"), 0, 1)
        grid.addWidget(self.inp_tc, 1, 1)
        grid.addWidget(QLabel("Telefon", styleSheet=f"color:{C['text_sub']};"), 0, 2)
        grid.addWidget(self.inp_tel, 1, 2)
        
        klay.addLayout(grid)
        btn_ekle = QPushButton("＋  Hasta Ekle")
        btn_ekle.setStyleSheet(btn_primary_ss()); btn_ekle.setCursor(Qt.PointingHandCursor)
        btn_ekle.clicked.connect(self._ekle)
        klay.addWidget(btn_ekle, alignment=Qt.AlignLeft)
        lay.addWidget(kart)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(4)
        self.tablo.setHorizontalHeaderLabels(["ID", "Ad Soyad", "TC", "Telefon"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.setAlternatingRowColors(True)
        self.tablo.setStyleSheet(TABLE_SS)
        lay.addWidget(self.tablo)
        
        self.refresh()

    def _ekle(self):
        ad = self.inp_ad.text().strip()
        tc = self.inp_tc.text().strip()
        tel = self.inp_tel.text().strip()
        if not ad or not tc or not tel:
            self.main_app._bildirim("Lütfen tüm alanları doldurun.", False)
            return
            
        if any(char.isdigit() for char in ad):
            self.main_app._bildirim("Hasta adı rakam içeremez.", False)
            return
            
        if not tc.isdigit() or len(tc) != 11:
            self.main_app._bildirim("TC Kimlik No 11 haneli ve sadece rakamlardan oluşmalıdır.", False)
            return
            
        if not tel.isdigit():
            self.main_app._bildirim("Telefon numarası sadece rakamlardan oluşmalıdır.", False)
            return
        
        ok, msg = self.db.add_hasta(ad, tc, tel)
        self.main_app._bildirim(msg if not ok else "Hasta başarıyla eklendi.", ok)
        if ok:
            self.inp_ad.clear(); self.inp_tc.clear(); self.inp_tel.clear()
            self.refresh()
            self.main_app.refresh_all()

    def refresh(self):
        self.tablo.setRowCount(0)
        hastalar = self.db.get_all_hastalar()
        for h in hastalar:
            r = self.tablo.rowCount(); self.tablo.insertRow(r)
            self.tablo.setItem(r, 0, QTableWidgetItem(str(h.hasta_id)))
            self.tablo.setItem(r, 1, QTableWidgetItem(h.ad))
            self.tablo.setItem(r, 2, QTableWidgetItem(h.tc))
            self.tablo.setItem(r, 3, QTableWidgetItem(h.telefon))


class RandevuAlPage(QWidget):
    def __init__(self, db: DatabaseManager, main_app, parent=None):
        super().__init__(parent)
        self.db = db
        self.main_app = main_app
        self.setStyleSheet(f"background:{C['bg']};")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 22, 28, 22)
        
        lbl = QLabel("Randevu Oluştur")
        lbl.setStyleSheet(f"color:{C['text']};font-size:21px;font-weight:800;")
        lay.addWidget(lbl)

        kart = QFrame(); kart.setStyleSheet(card_ss()); shadow(kart)
        klay = QVBoxLayout(kart); klay.setContentsMargins(22,18,22,18)
        
        grid = QGridLayout(); grid.setSpacing(10)
        self.cb_hasta = QComboBox(); self.cb_hasta.setStyleSheet(input_ss())
        self.cb_doktor = QComboBox(); self.cb_doktor.setStyleSheet(input_ss())
        self.inp_tarih = QDateEdit(); self.inp_tarih.setCalendarPopup(True)
        self.inp_tarih.setDate(QDate.currentDate())
        self.inp_tarih.setStyleSheet(input_ss())
        self.cb_saat = QComboBox(); self.cb_saat.setStyleSheet(input_ss())
        
        self.cb_doktor.currentIndexChanged.connect(self._doktor_degisti)
        
        grid.addWidget(QLabel("Hasta Seçin", styleSheet=f"color:{C['text_sub']};"), 0, 0)
        grid.addWidget(self.cb_hasta, 1, 0)
        grid.addWidget(QLabel("Doktor Seçin", styleSheet=f"color:{C['text_sub']};"), 0, 1)
        grid.addWidget(self.cb_doktor, 1, 1)
        grid.addWidget(QLabel("Tarih", styleSheet=f"color:{C['text_sub']};"), 0, 2)
        grid.addWidget(self.inp_tarih, 1, 2)
        grid.addWidget(QLabel("Saat", styleSheet=f"color:{C['text_sub']};"), 0, 3)
        grid.addWidget(self.cb_saat, 1, 3)
        
        klay.addLayout(grid)
        btn_ekle = QPushButton("＋  Randevu Oluştur")
        btn_ekle.setStyleSheet(btn_primary_ss()); btn_ekle.setCursor(Qt.PointingHandCursor)
        btn_ekle.clicked.connect(self._olustur)
        klay.addWidget(btn_ekle, alignment=Qt.AlignLeft)
        lay.addWidget(kart)
        lay.addStretch()

    def _doktor_degisti(self):
        self.cb_saat.clear()
        doktor_id = self.cb_doktor.currentData()
        if not doktor_id: return
        doktor = self.db.get_doktor(doktor_id)
        if doktor:
            self.cb_saat.addItems(doktor.uygun_saatler)

    def refresh(self):
        self.cb_hasta.clear()
        self.cb_doktor.clear()
        
        for h in self.db.get_all_hastalar():
            self.cb_hasta.addItem(f"{h.ad} (TC: {h.tc})", h.hasta_id)
            
        for d in self.db.get_all_doktorlar():
            self.cb_doktor.addItem(f"Dr. {d.ad} ({d.uzmanlik})", d.doktor_id)
            
        self._doktor_degisti()

    def _olustur(self):
        h_id = self.cb_hasta.currentData()
        d_id = self.cb_doktor.currentData()
        saat = self.cb_saat.currentText()
        tarih = self.inp_tarih.date().toString("dd.MM.yyyy")
        
        if not h_id or not d_id or not saat:
            self.main_app._bildirim("Lütfen tüm alanları doldurun.", False)
            return
            
        hasta = self.db.get_hasta(h_id)
        doktor = self.db.get_doktor(d_id)
        
        # Hasta sınıfı üzerinden randevu oluşturma tetikleniyor
        ok, msg_or_obj = hasta.randevu_al(doktor, tarih, saat, self.db)
        
        if ok:
            self.main_app._bildirim("Randevu başarıyla oluşturuldu.", True)
            self.main_app.refresh_all()
        else:
            self.main_app._bildirim(msg_or_obj, False)


class GunlukRandevuPage(QWidget):
    def __init__(self, db: DatabaseManager, main_app, parent=None):
        super().__init__(parent)
        self.db = db
        self.main_app = main_app
        self.setStyleSheet(f"background:{C['bg']};")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 22, 28, 22)
        
        lbl = QLabel("Günlük Randevu Listesi")
        lbl.setStyleSheet(f"color:{C['text']};font-size:21px;font-weight:800;")
        
        ust = QHBoxLayout()
        ust.addWidget(lbl)
        ust.addStretch()
        
        self.inp_filtre = QDateEdit(); self.inp_filtre.setCalendarPopup(True)
        self.inp_filtre.setDate(QDate.currentDate())
        self.inp_filtre.setStyleSheet(input_ss())
        self.inp_filtre.dateChanged.connect(self.refresh)
        
        ust.addWidget(QLabel("Tarih Seçin:", styleSheet=f"color:{C['text_sub']};"))
        ust.addWidget(self.inp_filtre)
        lay.addLayout(ust)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(5)
        self.tablo.setHorizontalHeaderLabels(["ID", "Saat", "Doktor", "Hasta", "İşlem"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.setAlternatingRowColors(True)
        self.tablo.setStyleSheet(TABLE_SS)
        lay.addWidget(self.tablo)
        
        self.refresh()

    def refresh(self):
        self.tablo.setRowCount(0)
        tarih = self.inp_filtre.date().toString("dd.MM.yyyy")
        randevular = self.db.get_randevular_by_date(tarih)
        
        for r_obj in randevular:
            row = self.tablo.rowCount()
            self.tablo.insertRow(row)
            self.tablo.setItem(row, 0, QTableWidgetItem(str(r_obj.randevu_id)))
            self.tablo.setItem(row, 1, QTableWidgetItem(r_obj.saat))
            self.tablo.setItem(row, 2, QTableWidgetItem(f"Dr. {r_obj.doktor.ad}"))
            self.tablo.setItem(row, 3, QTableWidgetItem(r_obj.hasta.ad))
            
            btn_iptal = QPushButton("İptal Et")
            btn_iptal.setStyleSheet(btn_danger_ss())
            btn_iptal.setCursor(Qt.PointingHandCursor)
            btn_iptal.clicked.connect(lambda _, r=r_obj: self._iptal(r))
            self.tablo.setCellWidget(row, 4, btn_iptal)
            self.tablo.setRowHeight(row, 40)

    def _iptal(self, randevu):
        # Randevu sınıfı üzerinden iptal metodu çağrılıyor
        ok, msg = randevu.randevu_iptal(self.db)
        if ok:
            self.main_app._bildirim(msg, True)
            self.main_app.refresh_all()
        else:
            self.main_app._bildirim(msg, False)


# ══════════════════════════════════════════════════════════
#  ANA PENCERE
# ══════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🩺 Randevu Yönetim Sistemi")
        self.setMinimumSize(1150, 700)
        self.resize(1300, 780)
        self.setStyleSheet(f"QMainWindow{{background:{C['bg']};color:{C['text']};}}")

        self.db = DatabaseManager()
        self._build_ui()
        self._saat_timer()
        
        # Test verisi eklemek isterseniz, sadece ilk çalıştırmada çalışır (tablolar boşsa)
        self._add_demo_data()

    def _add_demo_data(self):
        if len(self.db.get_all_doktorlar()) == 0:
            self.db.add_doktor("Ahmet Yılmaz", "Kardiyoloji", ["09:00", "10:00", "11:00", "14:00"])
            self.db.add_doktor("Ayşe Kılıç", "Dahiliye", ["09:30", "10:30", "13:30", "15:00"])
        if len(self.db.get_all_hastalar()) == 0:
            self.db.add_hasta("Mehmet Demir", "12345678901", "05321234567")
            self.db.add_hasta("Zeynep Şahin", "10987654321", "05559876543")
        self.refresh_all()

    def _build_ui(self):
        merkez = QWidget()
        merkez.setStyleSheet(f"background:{C['bg']};")
        self.setCentralWidget(merkez)

        ana = QHBoxLayout(merkez)
        ana.setContentsMargins(0, 0, 0, 0)
        ana.setSpacing(0)

        # ─ Sidebar ─
        sidebar = QFrame()
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet(f"background:{C['sidebar']};border-right:1px solid {C['border']};")

        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(0, 0, 0, 18)
        sb.setSpacing(0)

        # Logo
        logo = QFrame()
        logo.setFixedHeight(76)
        logo.setStyleSheet(f"""
            background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {C['accent2']},stop:1 {C['accent']});
        """)
        ll = QVBoxLayout(logo); ll.setContentsMargins(16, 10, 16, 10)
        t1 = QLabel("Randevu Sistemi")
        t1.setStyleSheet("color:white;font-size:16px;font-weight:800;background:transparent;")
        t2 = QLabel("Poliklinik Yönetimi")
        t2.setStyleSheet("color:rgba(255,255,255,0.72);font-size:10px;background:transparent;")
        ll.addWidget(t1); ll.addWidget(t2)
        sb.addWidget(logo)
        sb.addSpacing(18)

        self.nav = []
        pages = ["Dashboard", "Doktor Yönetimi", "Hasta Yönetimi", "Randevu Oluştur", "Günlük Randevular"]
        for metin in pages:
            btn = SideBtn(metin)
            btn.clicked.connect(lambda _, m=metin: self._goto(m))
            sb.addWidget(btn)
            self.nav.append(btn)

        sb.addStretch()

        self.lbl_saat = QLabel()
        self.lbl_saat.setAlignment(Qt.AlignCenter)
        self.lbl_saat.setStyleSheet(f"color:{C['text_dim']};font-size:11px;background:transparent;")
        sb.addWidget(self.lbl_saat)
        ana.addWidget(sidebar)

        # ─ İçerik ─
        icerik = QWidget()
        icerik.setStyleSheet(f"background:{C['bg']};")
        il = QVBoxLayout(icerik); il.setContentsMargins(0,0,0,0); il.setSpacing(0)

        # Top bar
        topbar = QFrame()
        topbar.setFixedHeight(50)
        topbar.setStyleSheet(f"background:{C['sidebar']};border-bottom:1px solid {C['border']};")
        tl = QHBoxLayout(topbar); tl.setContentsMargins(22, 0, 22, 0)
        self.lbl_page = QLabel("Dashboard")
        self.lbl_page.setStyleSheet(f"color:{C['text_sub']};font-size:12px;background:transparent;")
        tl.addWidget(self.lbl_page); tl.addStretch()
        user_lbl = QLabel("Poliklinik Sekreteri")
        user_lbl.setStyleSheet(f"color:{C['text_sub']};font-size:12px;background:transparent;")
        tl.addWidget(user_lbl)
        il.addWidget(topbar)

        # Stack
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background:{C['bg']};")

        self.p_dashboard = DashboardPage(self.db)
        self.p_doktor    = DoktorPage(self.db, self)
        self.p_hasta     = HastaPage(self.db, self)
        self.p_randevu   = RandevuAlPage(self.db, self)
        self.p_gunluk    = GunlukRandevuPage(self.db, self)

        for p in [self.p_dashboard, self.p_doktor, self.p_hasta, self.p_randevu, self.p_gunluk]:
            self.stack.addWidget(p)

        il.addWidget(self.stack)
        ana.addWidget(icerik)

        self._goto("Dashboard")

    def _goto(self, sayfa):
        idx = {"Dashboard": 0, "Doktor Yönetimi": 1, "Hasta Yönetimi": 2, 
               "Randevu Oluştur": 3, "Günlük Randevular": 4}[sayfa]
        self.stack.setCurrentIndex(idx)
        self.lbl_page.setText(sayfa)
        for i, b in enumerate(self.nav):
            b.setChecked(i == idx)
            
        self.refresh_all()

    def refresh_all(self):
        self.p_dashboard.refresh()
        self.p_doktor.refresh()
        self.p_hasta.refresh()
        self.p_randevu.refresh()
        self.p_gunluk.refresh()

    def _saat_timer(self):
        self._saat_guncelle()
        t = QTimer(self); t.timeout.connect(self._saat_guncelle); t.start(1000)

    def _saat_guncelle(self):
        self.lbl_saat.setText(datetime.now().strftime("%d.%m.%Y\n%H:%M:%S"))

    def _bildirim(self, mesaj, ok=True):
        renk = C['success'] if ok else C['danger']
        dlg = QMessageBox(self)
        dlg.setText(mesaj)
        dlg.setWindowTitle("Sistem")
        dlg.setStyleSheet(f"""
            QMessageBox{{background:{C['card']};}}
            QLabel{{color:{renk};font-size:13px;}}
            QPushButton{{{btn_primary_ss()[len('QPushButton'):].split('}')[0]}padding:6px 18px;}}
        """)
        dlg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    p = QPalette()
    p.setColor(QPalette.Window, QColor(C['bg']))
    p.setColor(QPalette.WindowText, QColor(C['text']))
    app.setPalette(p)
    
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
