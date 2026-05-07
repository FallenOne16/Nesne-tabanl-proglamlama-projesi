"""
============================================================
  DIJITAL KUTUPHANE SISTEMI - PyQt5 Arayuzu
============================================================
Kurulum  : pip install PyQt5
Calistir : python kutuphane_gui.py
Not      : kutuphane_sistemi.py ile ayni klasorde olmalidir.
"""

import sys

from PyQt5.QtCore import QRegularExpression, Qt
from PyQt5.QtGui import QColor, QRegularExpressionValidator
from PyQt5.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from kutuphane_sistemi import Kitap, KutuphaneSistemi, Uye


C = {
    "bg": "#101820",
    "sidebar": "#16232E",
    "card": "#1E2E3A",
    "border": "#314756",
    "accent": "#2EC4B6",
    "accent2": "#3A86FF",
    "success": "#8AC926",
    "warning": "#FFCA3A",
    "danger": "#FF595E",
    "text": "#F4F7F5",
    "text_sub": "#B7C6C2",
    "text_dim": "#7E9290",
    "row_alt": "#182633",
    "row_sel": "#253D4C",
    "input_bg": "#14222C",
}


def shadow(widget, blur=18, dy=4):
    fx = QGraphicsDropShadowEffect(widget)
    fx.setBlurRadius(blur)
    fx.setColor(QColor(0, 0, 0, 75))
    fx.setOffset(0, dy)
    widget.setGraphicsEffect(fx)


def btn_primary_ss():
    return f"""
        QPushButton {{
            background:{C['accent2']}; color:#fff; border:none; border-radius:8px;
            padding:9px 18px; font-size:13px; font-weight:700;
        }}
        QPushButton:hover {{ background:#5A9BFF; }}
    """


def btn_success_ss():
    return f"""
        QPushButton {{
            background:{C['success']}; color:#102018; border:none; border-radius:8px;
            padding:9px 18px; font-size:13px; font-weight:800;
        }}
        QPushButton:hover {{ background:#A7E845; }}
    """


def btn_danger_ss():
    return f"""
        QPushButton {{
            background:{C['danger']}; color:#fff; border:none; border-radius:8px;
            padding:9px 18px; font-size:13px; font-weight:700;
        }}
        QPushButton:hover {{ background:#FF7478; }}
    """


def input_ss():
    return f"""
        QLineEdit, QSpinBox {{
            background:{C['input_bg']}; color:{C['text']};
            border:1px solid {C['border']}; border-radius:8px;
            padding:7px 10px; font-size:13px;
        }}
        QLineEdit:focus, QSpinBox:focus {{
            border:1.5px solid {C['accent']};
        }}
        QSpinBox::up-button, QSpinBox::down-button {{
            background:{C['border']}; width:18px; border-radius:3px;
        }}
    """


def harf_dogrulayici():
    return QRegularExpressionValidator(QRegularExpression(r"[\p{L} .'-]*"))


TABLE_SS = f"""
    QTableWidget {{
        background:{C['card']}; color:{C['text']}; border:none;
        gridline-color:{C['border']}; font-size:13px;
        selection-background-color:{C['row_sel']}; outline:none;
        alternate-background-color:{C['row_alt']};
    }}
    QTableWidget::item {{ padding:8px 11px; border-bottom:1px solid {C['border']}; }}
    QTableWidget::item:selected {{ background:{C['row_sel']}; color:{C['accent']}; }}
    QHeaderView::section {{
        background:{C['sidebar']}; color:{C['accent']};
        padding:9px 11px; border:none; border-bottom:2px solid {C['accent']};
        font-size:11px; font-weight:700;
    }}
"""


class KpiCard(QFrame):
    def __init__(self, baslik, deger, alt, renk, parent=None):
        super().__init__(parent)
        self.setFixedHeight(108)
        self.setStyleSheet(
            f"QFrame{{background:{C['card']};border:1px solid {C['border']};"
            f"border-radius:10px;border-left:4px solid {renk};}}"
        )
        shadow(self)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 12, 18, 12)
        lay.setSpacing(3)

        lbl_t = QLabel(baslik.upper())
        lbl_t.setStyleSheet(f"color:{C['text_sub']};font-size:10px;font-weight:700;background:transparent;border:none;")
        lbl_v = QLabel(str(deger))
        lbl_v.setStyleSheet(f"color:{renk};font-size:28px;font-weight:800;background:transparent;border:none;")
        lbl_a = QLabel(alt)
        lbl_a.setStyleSheet(f"color:{C['text_dim']};font-size:11px;background:transparent;border:none;")

        lay.addWidget(lbl_t)
        lay.addWidget(lbl_v)
        lay.addWidget(lbl_a)


class SideBtn(QPushButton):
    def __init__(self, metin, parent=None):
        super().__init__(metin, parent)
        self.setCheckable(True)
        self.setFixedHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        self._refresh(False)

    def _refresh(self, aktif):
        if aktif:
            self.setStyleSheet(
                f"QPushButton{{background:rgba(46,196,182,0.12);color:{C['accent']};"
                f"border:none;border-left:3px solid {C['accent']};border-radius:0;"
                "text-align:left;padding-left:18px;font-size:13px;font-weight:800;}}"
            )
        else:
            self.setStyleSheet(
                f"QPushButton{{background:transparent;color:{C['text_sub']};border:none;"
                "border-left:3px solid transparent;border-radius:0;text-align:left;"
                "padding-left:18px;font-size:13px;}}"
                f"QPushButton:hover{{background:{C['card']};color:{C['text']};}}"
            )

    def setChecked(self, v):
        super().setChecked(v)
        self._refresh(v)


class BasePage(QWidget):
    def title(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color:{C['text']};font-size:22px;font-weight:800;")
        return lbl

    def subtitle(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:700;")
        return lbl

    def make_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setStyleSheet(TABLE_SS)
        return table


class DashboardPage(BasePage):
    def __init__(self, sistem: KutuphaneSistemi, parent=None):
        super().__init__(parent)
        self.sistem = sistem
        self.setStyleSheet(f"background:{C['bg']};")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 22, 28, 22)
        lay.setSpacing(18)

        lay.addWidget(self.title("Dijital Kutuphane Paneli"))

        self.kpi_row = QHBoxLayout()
        self.kpi_row.setSpacing(14)
        lay.addLayout(self.kpi_row)

        lay.addWidget(self.subtitle("Son Odunc Kayitlari"))
        self.table = self.make_table(["Odunc ID", "Kitap", "Uye", "Odunc Tarihi", "Iade Tarihi"])
        lay.addWidget(self.table, 1)
        self.refresh()

    def refresh(self):
        while self.kpi_row.count():
            item = self.kpi_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        kartlar = [
            ("Toplam Kitap", len(self.sistem.kitaplar), "Kutuphane koleksiyonu", C["accent"]),
            ("Raftaki Kitap", self.sistem.raftaki_kitap_sayisi(), "Odunc alinabilir", C["success"]),
            ("Oduncteki Kitap", self.sistem.oduncteki_kitap_sayisi(), "Aktif odunc", C["warning"]),
            ("Uye Sayisi", len(self.sistem.uyeler), "Kayitli okuyucu", C["accent2"]),
        ]
        for baslik, deger, alt, renk in kartlar:
            self.kpi_row.addWidget(KpiCard(baslik, deger, alt, renk))

        kayitlar = self.sistem.gecmis_oduncler()[-12:]
        self.table.setRowCount(len(kayitlar))
        for r, odunc in enumerate(kayitlar):
            iade = odunc.iade_tarihi.strftime("%d.%m.%Y") if odunc.iade_tarihi else "Devam ediyor"
            vals = [
                odunc.odunc_id,
                odunc.kitap.ad,
                odunc.uye.ad,
                odunc.odunc_tarihi.strftime("%d.%m.%Y"),
                iade,
            ]
            for c, val in enumerate(vals):
                self.table.setItem(r, c, QTableWidgetItem(str(val)))


class KitapPage(BasePage):
    def __init__(self, sistem: KutuphaneSistemi, on_change, parent=None):
        super().__init__(parent)
        self.sistem = sistem
        self.on_change = on_change
        self.setStyleSheet(f"background:{C['bg']};")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 22, 28, 22)
        lay.setSpacing(16)
        lay.addWidget(self.title("Kitap Yonetimi"))

        form = QFrame()
        form.setStyleSheet(f"QFrame{{background:{C['card']};border:1px solid {C['border']};border-radius:10px;}}")
        shadow(form)
        grid = QGridLayout(form)
        grid.setContentsMargins(18, 16, 18, 16)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)

        self.kitap_id = QSpinBox()
        self.kitap_id.setRange(1, 999999)
        self.ad = QLineEdit()
        self.yazar = QLineEdit()
        self.kategori = QLineEdit()
        self.yazar.setValidator(harf_dogrulayici())
        self.kategori.setValidator(harf_dogrulayici())
        for w in (self.kitap_id, self.ad, self.yazar, self.kategori):
            w.setStyleSheet(input_ss())

        alanlar = [
            ("Kitap ID", self.kitap_id),
            ("Ad", self.ad),
            ("Yazar", self.yazar),
            ("Kategori", self.kategori),
        ]
        for i, (etiket, widget) in enumerate(alanlar):
            lbl = QLabel(etiket)
            lbl.setStyleSheet(f"color:{C['text_sub']};background:transparent;border:none;font-weight:700;")
            grid.addWidget(lbl, 0, i)
            grid.addWidget(widget, 1, i)

        btn = QPushButton("Kitap Ekle")
        btn.setStyleSheet(btn_success_ss())
        btn.clicked.connect(self.kitap_ekle)
        grid.addWidget(btn, 1, 4)
        lay.addWidget(form)

        self.table = self.make_table(["ID", "Ad", "Yazar", "Kategori", "Durum"])
        lay.addWidget(self.table, 1)
        self.refresh()

    def kitap_ekle(self):
        ad = self.ad.text().strip()
        yazar = self.yazar.text().strip()
        kategori = self.kategori.text().strip()
        if not ad or not yazar or not kategori:
            QMessageBox.warning(self, "Eksik Bilgi", "Lutfen kitap adi, yazar ve kategori girin.")
            return

        kitap = Kitap(self.kitap_id.value(), ad, yazar, kategori)
        ok, msg = self.sistem.kitap_ekle(kitap)
        if ok:
            self.ad.clear()
            self.yazar.clear()
            self.kategori.clear()
            self.kitap_id.setValue(self.kitap_id.value() + 1)
            self.on_change()
        QMessageBox.information(self, "Kitap", msg)

    def refresh(self):
        kitaplar = list(self.sistem.kitaplar.values())
        self.table.setRowCount(len(kitaplar))
        for r, kitap in enumerate(kitaplar):
            vals = [kitap.kitap_id, kitap.ad, kitap.yazar, kitap.kategori, kitap.durum]
            for c, val in enumerate(vals):
                item = QTableWidgetItem(str(val))
                if c == 4:
                    item.setForeground(QColor(C["success"] if val == "Rafta" else C["warning"]))
                self.table.setItem(r, c, item)


class UyePage(BasePage):
    def __init__(self, sistem: KutuphaneSistemi, on_change, parent=None):
        super().__init__(parent)
        self.sistem = sistem
        self.on_change = on_change
        self.setStyleSheet(f"background:{C['bg']};")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 22, 28, 22)
        lay.setSpacing(16)
        lay.addWidget(self.title("Uye Yonetimi"))

        form = QFrame()
        form.setStyleSheet(f"QFrame{{background:{C['card']};border:1px solid {C['border']};border-radius:10px;}}")
        shadow(form)
        grid = QGridLayout(form)
        grid.setContentsMargins(18, 16, 18, 16)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)

        self.uye_id = QSpinBox()
        self.uye_id.setRange(1, 999999)
        self.ad = QLineEdit()
        self.email = QLineEdit()
        self.ad.setValidator(harf_dogrulayici())
        for w in (self.uye_id, self.ad, self.email):
            w.setStyleSheet(input_ss())

        alanlar = [("Uye ID", self.uye_id), ("Ad", self.ad), ("Email", self.email)]
        for i, (etiket, widget) in enumerate(alanlar):
            lbl = QLabel(etiket)
            lbl.setStyleSheet(f"color:{C['text_sub']};background:transparent;border:none;font-weight:700;")
            grid.addWidget(lbl, 0, i)
            grid.addWidget(widget, 1, i)

        btn = QPushButton("Uye Ekle")
        btn.setStyleSheet(btn_success_ss())
        btn.clicked.connect(self.uye_ekle)
        grid.addWidget(btn, 1, 3)
        lay.addWidget(form)

        self.table = self.make_table(["ID", "Ad", "Email", "Aktif Odunc"])
        lay.addWidget(self.table, 1)
        self.refresh()

    def uye_ekle(self):
        ad = self.ad.text().strip()
        email = self.email.text().strip()
        if not ad or not email:
            QMessageBox.warning(self, "Eksik Bilgi", "Lutfen uye adi ve email girin.")
            return

        uye = Uye(self.uye_id.value(), ad, email)
        ok, msg = self.sistem.uye_ekle(uye)
        if ok:
            self.ad.clear()
            self.email.clear()
            self.uye_id.setValue(self.uye_id.value() + 1)
            self.on_change()
        QMessageBox.information(self, "Uye", msg)

    def refresh(self):
        uyeler = list(self.sistem.uyeler.values())
        self.table.setRowCount(len(uyeler))
        for r, uye in enumerate(uyeler):
            vals = [uye.uye_id, uye.ad, uye.email, len(uye.odunc_kitaplar)]
            for c, val in enumerate(vals):
                self.table.setItem(r, c, QTableWidgetItem(str(val)))


class OduncPage(BasePage):
    def __init__(self, sistem: KutuphaneSistemi, on_change, parent=None):
        super().__init__(parent)
        self.sistem = sistem
        self.on_change = on_change
        self.setStyleSheet(f"background:{C['bg']};")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 22, 28, 22)
        lay.setSpacing(16)
        lay.addWidget(self.title("Odunc ve Iade Islemleri"))

        form = QFrame()
        form.setStyleSheet(f"QFrame{{background:{C['card']};border:1px solid {C['border']};border-radius:10px;}}")
        shadow(form)
        grid = QGridLayout(form)
        grid.setContentsMargins(18, 16, 18, 16)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)

        self.kitap_id = QSpinBox()
        self.kitap_id.setRange(1, 999999)
        self.uye_id = QSpinBox()
        self.uye_id.setRange(1, 999999)
        self.iade_odunc_id = QSpinBox()
        self.iade_odunc_id.setRange(1, 999999)
        for w in (self.kitap_id, self.uye_id, self.iade_odunc_id):
            w.setStyleSheet(input_ss())

        grid.addWidget(self._label("Kitap ID"), 0, 0)
        grid.addWidget(self._label("Uye ID"), 0, 1)
        grid.addWidget(self.kitap_id, 1, 0)
        grid.addWidget(self.uye_id, 1, 1)

        odunc_btn = QPushButton("Odunc Ver")
        odunc_btn.setStyleSheet(btn_primary_ss())
        odunc_btn.clicked.connect(self.odunc_ver)
        grid.addWidget(odunc_btn, 1, 2)

        grid.addWidget(self._label("Iade Edilecek Odunc ID"), 0, 3)
        grid.addWidget(self.iade_odunc_id, 1, 3)
        iade_btn = QPushButton("Iade Al")
        iade_btn.setStyleSheet(btn_danger_ss())
        iade_btn.clicked.connect(self.iade_al)
        grid.addWidget(iade_btn, 1, 4)
        lay.addWidget(form)

        lay.addWidget(self.subtitle("Tum Odunc Kayitlari"))
        self.table = self.make_table(["Odunc ID", "Kitap", "Uye", "Odunc Tarihi", "Iade Tarihi", "Durum"])
        lay.addWidget(self.table, 1)
        self.refresh()

    def _label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color:{C['text_sub']};background:transparent;border:none;font-weight:700;")
        return lbl

    def odunc_ver(self):
        ok, msg, odunc = self.sistem.kitap_odunc_ver(self.kitap_id.value(), self.uye_id.value())
        if ok and odunc:
            self.iade_odunc_id.setValue(odunc.odunc_id)
            self.on_change()
        QMessageBox.information(self, "Odunc", msg)

    def iade_al(self):
        ok, msg = self.sistem.kitap_iade_al(self.iade_odunc_id.value())
        if ok:
            self.on_change()
        QMessageBox.information(self, "Iade", msg)

    def refresh(self):
        kayitlar = self.sistem.gecmis_oduncler()
        self.table.setRowCount(len(kayitlar))
        for r, odunc in enumerate(kayitlar):
            iade = odunc.iade_tarihi.strftime("%d.%m.%Y") if odunc.iade_tarihi else "-"
            durum = "Aktif" if odunc.aktif_mi() else "Iade edildi"
            vals = [
                odunc.odunc_id,
                odunc.kitap.ad,
                odunc.uye.ad,
                odunc.odunc_tarihi.strftime("%d.%m.%Y"),
                iade,
                durum,
            ]
            for c, val in enumerate(vals):
                item = QTableWidgetItem(str(val))
                if c == 5:
                    item.setForeground(QColor(C["warning"] if durum == "Aktif" else C["success"]))
                self.table.setItem(r, c, item)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dijital Kutuphane Sistemi")
        self.resize(1180, 720)
        self.sistem = KutuphaneSistemi()
        if self.sistem.veritabani_bos_mu():
            self._seed_data()
        self._build()
        self.refresh_all()

    def _seed_data(self):
        kitaplar = [
            Kitap(1, "Kurk Mantolu Madonna", "Sabahattin Ali", "Roman"),
            Kitap(2, "Saatleri Ayarlama Enstitusu", "Ahmet Hamdi Tanpinar", "Roman"),
            Kitap(3, "Seker Portakali", "Jose Mauro de Vasconcelos", "Roman"),
            Kitap(4, "1984", "George Orwell", "Distopya"),
            Kitap(5, "Nutuk", "Mustafa Kemal Ataturk", "Tarih"),
        ]
        uyeler = [
            Uye(1, "Ayse Yilmaz", "ayse@example.com"),
            Uye(2, "Mehmet Demir", "mehmet@example.com"),
            Uye(3, "Zeynep Kaya", "zeynep@example.com"),
        ]
        for kitap in kitaplar:
            self.sistem.kitap_ekle(kitap)
        for uye in uyeler:
            self.sistem.uye_ekle(uye)
        self.sistem.kitap_odunc_ver(2, 1)
        self.sistem.kitap_odunc_ver(4, 2)

    def _build(self):
        root = QWidget()
        self.setCentralWidget(root)
        root.setStyleSheet(f"background:{C['bg']};")
        main = QHBoxLayout(root)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        sidebar = QFrame()
        sidebar.setFixedWidth(235)
        sidebar.setStyleSheet(f"QFrame{{background:{C['sidebar']};border:none;}}")
        side_lay = QVBoxLayout(sidebar)
        side_lay.setContentsMargins(0, 22, 0, 22)
        side_lay.setSpacing(8)

        brand = QLabel("DIJITAL\nKUTUPHANE")
        brand.setStyleSheet(
            f"color:{C['text']};font-size:20px;font-weight:900;"
            "padding:0 22px 18px 22px;background:transparent;"
        )
        side_lay.addWidget(brand)

        self.buttons = []
        for metin in ("Panel", "Kitaplar", "Uyeler", "Odunc/Iade"):
            btn = SideBtn(metin)
            btn.clicked.connect(lambda checked, b=btn: self.switch_page(b))
            self.buttons.append(btn)
            side_lay.addWidget(btn)
        side_lay.addStretch()

        info = QLabel("Proje 3\nKitap - Uye - Odunc")
        info.setStyleSheet(f"color:{C['text_dim']};font-size:12px;padding:0 22px;background:transparent;")
        side_lay.addWidget(info)

        self.stack = QStackedWidget()
        self.pages = [
            DashboardPage(self.sistem),
            KitapPage(self.sistem, self.refresh_all),
            UyePage(self.sistem, self.refresh_all),
            OduncPage(self.sistem, self.refresh_all),
        ]
        for page in self.pages:
            self.stack.addWidget(page)

        main.addWidget(sidebar)
        main.addWidget(self.stack, 1)
        self.buttons[0].setChecked(True)

    def switch_page(self, button):
        index = self.buttons.index(button)
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)
        self.pages[index].refresh()

    def refresh_all(self):
        for page in self.pages:
            page.refresh()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(app.font())
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
