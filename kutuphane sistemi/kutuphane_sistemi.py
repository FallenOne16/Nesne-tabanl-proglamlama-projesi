"""
============================================================
  DIJITAL KUTUPHANE SISTEMI - Nesne Tabanli Is Mantigi
============================================================

Bu dosyada kullanilan temel siniflar:
  - Kitap
  - Uye
  - Odunc

Uygulama akisini kolaylastirmak icin bu siniflari yoneten
KutuphaneSistemi yardimci sinifi da eklenmistir.
"""

import sqlite3
from contextlib import contextmanager
from datetime import date
from pathlib import Path


class Kitap:
    """Kutuphane sistemindeki bir kitabi temsil eder."""

    def __init__(self, kitap_id: int, ad: str, yazar: str, kategori: str, durum: str = "Rafta"):
        self.kitap_id = kitap_id
        self.ad = ad
        self.yazar = yazar
        self.kategori = kategori
        self.durum = durum

    def kitap_durumu_degistir(self, yeni_durum: str):
        """Kitabin durumunu Rafta veya Oduncte olarak gunceller."""
        if yeni_durum not in ("Rafta", "Oduncte"):
            raise ValueError("Kitap durumu 'Rafta' veya 'Oduncte' olmalidir.")
        self.durum = yeni_durum

    def __str__(self):
        return f"[{self.kitap_id}] {self.ad} - {self.yazar} ({self.kategori}) | {self.durum}"


class Uye:
    """Kutuphane uyesini temsil eder."""

    def __init__(self, uye_id: int, ad: str, email: str):
        self.uye_id = uye_id
        self.ad = ad
        self.email = email
        self.odunc_kitaplar = []

    def kitap_odunc_al(self, kitap: Kitap):
        """Uye uygun durumdaki bir kitabi odunc alir."""
        if kitap.durum != "Rafta":
            return False, f"{kitap.ad} su anda oduncte."
        kitap.kitap_durumu_degistir("Oduncte")
        self.odunc_kitaplar.append(kitap)
        return True, f"{kitap.ad} adli kitap {self.ad} tarafindan odunc alindi."

    def kitap_iade_et(self, kitap: Kitap):
        """Uye odunc aldigi kitabi iade eder."""
        if kitap not in self.odunc_kitaplar:
            return False, f"{kitap.ad} bu uyede gorunmuyor."
        self.odunc_kitaplar.remove(kitap)
        kitap.kitap_durumu_degistir("Rafta")
        return True, f"{kitap.ad} adli kitap iade edildi."

    def __str__(self):
        return f"[{self.uye_id}] {self.ad} | {self.email}"


class Odunc:
    """Bir kitap odunc alma kaydini temsil eder."""

    def __init__(self, odunc_id: int, kitap: Kitap, uye: Uye, odunc_tarihi: date | None = None, iade_tarihi: date | None = None):
        self.odunc_id = odunc_id
        self.kitap = kitap
        self.uye = uye
        self.odunc_tarihi = odunc_tarihi or date.today()
        self.iade_tarihi = iade_tarihi

    def iade_et(self):
        self.iade_tarihi = date.today()

    def aktif_mi(self) -> bool:
        return self.iade_tarihi is None

    def __str__(self):
        iade = self.iade_tarihi.strftime("%d.%m.%Y") if self.iade_tarihi else "Iade edilmedi"
        return (
            f"[{self.odunc_id}] {self.kitap.ad} -> {self.uye.ad} | "
            f"Odunc: {self.odunc_tarihi.strftime('%d.%m.%Y')} | Iade: {iade}"
        )


class KutuphaneSistemi:
    """Kitap, uye ve odunc kayitlarini bir arada yonetir."""

    def __init__(self, db_yolu: str | Path | None = None):
        self.kitaplar = {}
        self.uyeler = {}
        self.oduncler = {}
        self._siradaki_odunc_id = 1
        self.db_yolu = Path(db_yolu) if db_yolu else Path(__file__).with_name("kutuphane.db")
        self._db_hazirla()
        self._dbden_yukle()

    @contextmanager
    def _baglan(self):
        conn = sqlite3.connect(self.db_yolu)
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _db_hazirla(self):
        with self._baglan() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS kitaplar (
                    kitap_id INTEGER PRIMARY KEY,
                    ad TEXT NOT NULL,
                    yazar TEXT NOT NULL,
                    kategori TEXT NOT NULL,
                    durum TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS uyeler (
                    uye_id INTEGER PRIMARY KEY,
                    ad TEXT NOT NULL,
                    email TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS oduncler (
                    odunc_id INTEGER PRIMARY KEY,
                    kitap_id INTEGER NOT NULL,
                    uye_id INTEGER NOT NULL,
                    odunc_tarihi TEXT NOT NULL,
                    iade_tarihi TEXT,
                    FOREIGN KEY (kitap_id) REFERENCES kitaplar (kitap_id),
                    FOREIGN KEY (uye_id) REFERENCES uyeler (uye_id)
                )
                """
            )

    def _dbden_yukle(self):
        self.kitaplar.clear()
        self.uyeler.clear()
        self.oduncler.clear()

        with self._baglan() as conn:
            for row in conn.execute("SELECT kitap_id, ad, yazar, kategori, durum FROM kitaplar ORDER BY kitap_id"):
                kitap = Kitap(row[0], row[1], row[2], row[3], row[4])
                self.kitaplar[kitap.kitap_id] = kitap

            for row in conn.execute("SELECT uye_id, ad, email FROM uyeler ORDER BY uye_id"):
                uye = Uye(row[0], row[1], row[2])
                self.uyeler[uye.uye_id] = uye

            rows = conn.execute(
                """
                SELECT odunc_id, kitap_id, uye_id, odunc_tarihi, iade_tarihi
                FROM oduncler
                ORDER BY odunc_id
                """
            ).fetchall()

        for odunc_id, kitap_id, uye_id, odunc_tarihi, iade_tarihi in rows:
            kitap = self.kitaplar.get(kitap_id)
            uye = self.uyeler.get(uye_id)
            if not kitap or not uye:
                continue
            odunc = Odunc(
                odunc_id,
                kitap,
                uye,
                date.fromisoformat(odunc_tarihi),
                date.fromisoformat(iade_tarihi) if iade_tarihi else None,
            )
            self.oduncler[odunc.odunc_id] = odunc
            if odunc.aktif_mi() and kitap not in uye.odunc_kitaplar:
                uye.odunc_kitaplar.append(kitap)

        self._siradaki_odunc_id = (max(self.oduncler.keys()) + 1) if self.oduncler else 1

    def kitap_ekle(self, kitap: Kitap):
        if kitap.kitap_id in self.kitaplar:
            return False, "Bu kitap ID zaten kayitli."
        self.kitaplar[kitap.kitap_id] = kitap
        with self._baglan() as conn:
            conn.execute(
                """
                INSERT INTO kitaplar (kitap_id, ad, yazar, kategori, durum)
                VALUES (?, ?, ?, ?, ?)
                """,
                (kitap.kitap_id, kitap.ad, kitap.yazar, kitap.kategori, kitap.durum),
            )
        return True, f"{kitap.ad} kutuphaneye eklendi."

    def uye_ekle(self, uye: Uye):
        if uye.uye_id in self.uyeler:
            return False, "Bu uye ID zaten kayitli."
        self.uyeler[uye.uye_id] = uye
        with self._baglan() as conn:
            conn.execute(
                "INSERT INTO uyeler (uye_id, ad, email) VALUES (?, ?, ?)",
                (uye.uye_id, uye.ad, uye.email),
            )
        return True, f"{uye.ad} sisteme eklendi."

    def kitap_odunc_ver(self, kitap_id: int, uye_id: int):
        kitap = self.kitaplar.get(kitap_id)
        uye = self.uyeler.get(uye_id)

        if not kitap:
            return False, "Kitap bulunamadi.", None
        if not uye:
            return False, "Uye bulunamadi.", None

        basarili, mesaj = uye.kitap_odunc_al(kitap)
        if not basarili:
            return False, mesaj, None

        odunc = Odunc(self._siradaki_odunc_id, kitap, uye)
        self.oduncler[odunc.odunc_id] = odunc
        self._siradaki_odunc_id += 1
        with self._baglan() as conn:
            conn.execute(
                "UPDATE kitaplar SET durum = ? WHERE kitap_id = ?",
                (kitap.durum, kitap.kitap_id),
            )
            conn.execute(
                """
                INSERT INTO oduncler (odunc_id, kitap_id, uye_id, odunc_tarihi, iade_tarihi)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    odunc.odunc_id,
                    kitap.kitap_id,
                    uye.uye_id,
                    odunc.odunc_tarihi.isoformat(),
                    None,
                ),
            )
        return True, mesaj, odunc

    def kitap_iade_al(self, odunc_id: int):
        odunc = self.oduncler.get(odunc_id)
        if not odunc:
            return False, "Odunc kaydi bulunamadi."
        if not odunc.aktif_mi():
            return False, "Bu odunc kaydi zaten iade edilmis."

        basarili, mesaj = odunc.uye.kitap_iade_et(odunc.kitap)
        if basarili:
            odunc.iade_et()
            with self._baglan() as conn:
                conn.execute(
                    "UPDATE kitaplar SET durum = ? WHERE kitap_id = ?",
                    (odunc.kitap.durum, odunc.kitap.kitap_id),
                )
                conn.execute(
                    "UPDATE oduncler SET iade_tarihi = ? WHERE odunc_id = ?",
                    (odunc.iade_tarihi.isoformat(), odunc.odunc_id),
                )
        return basarili, mesaj

    def veritabani_bos_mu(self):
        return not self.kitaplar and not self.uyeler and not self.oduncler

    def aktif_oduncler(self):
        return [odunc for odunc in self.oduncler.values() if odunc.aktif_mi()]

    def gecmis_oduncler(self):
        return list(self.oduncler.values())

    def raftaki_kitap_sayisi(self):
        return sum(1 for kitap in self.kitaplar.values() if kitap.durum == "Rafta")

    def oduncteki_kitap_sayisi(self):
        return sum(1 for kitap in self.kitaplar.values() if kitap.durum == "Oduncte")
