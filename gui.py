"""
╔══════════════════════════════════════════════════════════════╗
║   ✈️  SEYAHAT PLANLAMA UYGULAMASI — Modern PyQt5 GUI        ║
║   Warm Terracotta + Deep Navy — Travel Aesthetic             ║
║   Requires: PyQt5                                            ║
╚══════════════════════════════════════════════════════════════╝
"""

import sys
import math
from datetime import datetime
from typing import Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QScrollArea,
    QGraphicsDropShadowEffect, QSizePolicy, QStackedWidget,
    QGridLayout, QSpacerItem, QDialog, QDateTimeEdit, QSpinBox,
    QDoubleSpinBox, QMessageBox, QProgressBar, QTextEdit,
    QListWidget, QListWidgetItem, QSplitter
)
from PyQt5.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve,
    QRect, QPoint, QSize, pyqtSignal, QThread, QDateTime
)
from PyQt5.QtGui import (
    QFont, QColor, QPalette, QPainter, QLinearGradient,
    QRadialGradient, QPixmap, QBrush, QPen, QFontDatabase,
    QIcon
)

from seyahat import (Seyahat, Konaklama, Plan,
                     UlasimTuru, KonaklamaTuru, PlanDurumu)
from seyahat_sistemi import SeyahatSistemi

# ══════════════════════════════════════════════════════
#  DESIGN TOKENS — Warm Travel Palette
# ══════════════════════════════════════════════════════
BG_DEEP    = "#0D1117"
BG_CARD    = "#161B22"
BG_MID     = "#21262D"
BG_HOVER   = "#30363D"

TERRACOTTA = "#E8735A"     # Primary accent
GOLD       = "#F0A500"     # Secondary accent
SAGE       = "#7EB8A4"     # Success / nature
LAVENDER   = "#A78BFA"     # Plan/info
SKY        = "#60A5FA"     # Info

TEXT_PRI   = "#F0F6FC"
TEXT_SEC   = "#8B949E"
TEXT_MUTED = "#484F58"

BORDER     = "rgba(240,106,90,0.15)"


def shadow(widget, radius=16, color="#E8735A", alpha=60):
    fx = QGraphicsDropShadowEffect()
    fx.setBlurRadius(radius)
    fx.setColor(QColor(color))
    fx.setOffset(0, 2)
    widget.setGraphicsEffect(fx)


def make_label(text, size=12, color=TEXT_PRI, bold=False, align=Qt.AlignLeft):
    lbl = QLabel(text)
    weight = "bold" if bold else "normal"
    lbl.setStyleSheet(f"color:{color}; font-size:{size}px; font-weight:{weight}; background:transparent;")
    lbl.setAlignment(align)
    return lbl


def card_style(radius=14, border_color=BORDER):
    return f"""
        QWidget {{
            background: {BG_CARD};
            border-radius: {radius}px;
            border: 1px solid {border_color};
        }}
    """


def btn_style(bg=TERRACOTTA, hover="#C95942", radius=10, padding="8px 18px"):
    return f"""
        QPushButton {{
            background: {bg};
            color: {TEXT_PRI};
            border: none;
            border-radius: {radius}px;
            padding: {padding};
            font-size: 12px;
            font-weight: bold;
        }}
        QPushButton:hover {{ background: {hover}; }}
        QPushButton:pressed {{ background: #A04535; }}
        QPushButton:disabled {{ background: {BG_HOVER}; color:{TEXT_MUTED}; }}
    """


def input_style():
    return f"""
        QLineEdit, QComboBox, QDateTimeEdit, QSpinBox, QDoubleSpinBox, QTextEdit {{
            background: {BG_MID};
            color: {TEXT_PRI};
            border: 1px solid rgba(232,115,90,0.25);
            border-radius: 8px;
            padding: 6px 10px;
            font-size: 12px;
        }}
        QLineEdit:focus, QComboBox:focus, QDateTimeEdit:focus,
        QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {{
            border: 1px solid {TERRACOTTA};
        }}
        QComboBox::drop-down {{ border: none; width: 20px; }}
        QComboBox QAbstractItemView {{
            background: {BG_MID};
            color: {TEXT_PRI};
            selection-background-color: {TERRACOTTA};
        }}
    """


def table_style():
    return f"""
        QTableWidget {{
            background: {BG_CARD};
            color: {TEXT_PRI};
            border: none;
            gridline-color: {BG_MID};
            font-size: 12px;
        }}
        QTableWidget::item {{ padding: 6px 10px; border-bottom: 1px solid {BG_MID}; }}
        QTableWidget::item:selected {{ background: rgba(232,115,90,0.2); color: {TEXT_PRI}; }}
        QHeaderView::section {{
            background: {BG_MID};
            color: {TEXT_SEC};
            font-size: 11px;
            font-weight: bold;
            padding: 6px 10px;
            border: none;
            border-bottom: 1px solid rgba(232,115,90,0.2);
        }}
        QScrollBar:vertical {{
            background: {BG_DEEP};
            width: 6px;
        }}
        QScrollBar::handle:vertical {{
            background: {BG_HOVER};
            border-radius: 3px;
        }}
    """


# ══════════════════════════════════════════════════════
#  ANIMATED BACKGROUND
# ══════════════════════════════════════════════════════

class AnimatedBG(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._t = 0
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        timer = QTimer(self)
        timer.timeout.connect(self._tick)
        timer.start(40)

    def _tick(self):
        self._t += 1
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor(BG_DEEP))
        t = self._t * 0.012
        # Floating orbs
        orbs = [
            (0.15, 0.2,  180, TERRACOTTA, 0.06),
            (0.8,  0.7,  140, GOLD,       0.05),
            (0.5,  0.5,  160, SAGE,       0.04),
        ]
        for ox, oy, r, col, alpha in orbs:
            cx = int((ox + math.sin(t + ox * 3) * 0.06) * self.width())
            cy = int((oy + math.cos(t + oy * 2) * 0.06) * self.height())
            grad = QRadialGradient(cx, cy, r)
            c = QColor(col)
            c.setAlphaF(alpha)
            grad.setColorAt(0, c)
            grad.setColorAt(1, QColor(0, 0, 0, 0))
            p.setBrush(QBrush(grad))
            p.setPen(Qt.NoPen)
            p.drawEllipse(cx - r, cy - r, r * 2, r * 2)
        p.end()


# ══════════════════════════════════════════════════════
#  NAV BUTTON
# ══════════════════════════════════════════════════════

class NavBtn(QPushButton):
    def __init__(self, icon: str, label: str):
        super().__init__()
        self._active = False
        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 8, 4, 8)
        lay.setSpacing(3)
        lay.setAlignment(Qt.AlignCenter)
        self._icon_lbl = QLabel(icon)
        self._icon_lbl.setAlignment(Qt.AlignCenter)
        self._icon_lbl.setStyleSheet("background:transparent; font-size:18px;")
        self._txt_lbl = QLabel(label)
        self._txt_lbl.setAlignment(Qt.AlignCenter)
        self._txt_lbl.setStyleSheet(f"background:transparent; font-size:9px; font-weight:bold; color:{TEXT_SEC};")
        lay.addWidget(self._icon_lbl)
        lay.addWidget(self._txt_lbl)
        self.setFixedSize(74, 64)
        self.setCursor(Qt.PointingHandCursor)
        self._refresh()

    def setActive(self, v: bool):
        self._active = v
        self._refresh()

    def _refresh(self):
        if self._active:
            self.setStyleSheet(f"""
                QPushButton {{ background: rgba(232,115,90,0.18);
                               border: 1px solid rgba(232,115,90,0.45);
                               border-radius: 12px; }}
                QPushButton:hover {{ background: rgba(232,115,90,0.25); }}
            """)
            self._txt_lbl.setStyleSheet(f"background:transparent; font-size:9px; font-weight:bold; color:{TERRACOTTA};")
        else:
            self.setStyleSheet(f"""
                QPushButton {{ background: transparent; border: none; border-radius: 12px; }}
                QPushButton:hover {{ background: rgba(232,115,90,0.08); }}
            """)
            self._txt_lbl.setStyleSheet(f"background:transparent; font-size:9px; font-weight:bold; color:{TEXT_SEC};")


# ══════════════════════════════════════════════════════
#  TOAST
# ══════════════════════════════════════════════════════

class Toast(QLabel):
    COLORS = {"ok": SAGE, "err": "#E05252", "info": SKY}

    def __init__(self, msg, kind="ok", parent=None):
        super().__init__(f"  {'✅' if kind=='ok' else '❌' if kind=='err' else 'ℹ️'}  {msg}  ", parent)
        c = self.COLORS.get(kind, SKY)
        self.setStyleSheet(f"""
            QLabel {{
                background: {BG_MID};
                color: {TEXT_PRI};
                border: 1px solid {c};
                border-left: 4px solid {c};
                border-radius: 10px;
                padding: 10px 16px;
                font-size: 12px;
            }}
        """)
        shadow(self, 20, c, 80)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)


# ══════════════════════════════════════════════════════
#  STAT CARD
# ══════════════════════════════════════════════════════

class StatCard(QWidget):
    def __init__(self, icon, title, value, color=TERRACOTTA):
        super().__init__()
        self.setStyleSheet(card_style())
        shadow(self, 14, color, 50)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(4)
        top = QHBoxLayout()
        top.addWidget(make_label(icon, 20))
        top.addStretch()
        lay.addLayout(top)
        lay.addWidget(make_label(title, 10, TEXT_SEC))
        self._val = make_label(value, 22, color, bold=True)
        lay.addWidget(self._val)

    def set_value(self, v):
        self._val.setText(v)


# ══════════════════════════════════════════════════════
#  DASHBOARD PAGE
# ══════════════════════════════════════════════════════

class DashboardPage(QWidget):
    toast_signal = pyqtSignal(str, str)

    def __init__(self, sistem: SeyahatSistemi):
        super().__init__()
        self._s = sistem
        self.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(20)

        # Header
        hdr = QHBoxLayout()
        hdr.addWidget(make_label("✈️  Seyahat Planlama", 22, TEXT_PRI, bold=True))
        hdr.addStretch()
        hdr.addWidget(make_label("Dashboard", 12, TEXT_SEC))
        lay.addLayout(hdr)
        lay.addWidget(self._divider())

        # Stats row
        self._stat_row = QHBoxLayout()
        self._stat_row.setSpacing(14)
        self._cards = [
            StatCard("✈️", "Toplam Seyahat",    "0", TERRACOTTA),
            StatCard("🏨", "Konaklamalar",       "0", GOLD),
            StatCard("🗺️", "Aktif Planlar",      "0", SAGE),
            StatCard("💰", "Toplam Bütçe",       "₺0", LAVENDER),
            StatCard("📊", "Harcama Oranı",      "%0", SKY),
        ]
        for c in self._cards:
            self._stat_row.addWidget(c)
        lay.addLayout(self._stat_row)

        # Recent trips table
        lay.addWidget(make_label("Son Seyahatler", 14, TEXT_PRI, bold=True))
        self._tbl = QTableWidget()
        self._tbl.setColumnCount(6)
        self._tbl.setHorizontalHeaderLabels(["ID", "Destinasyon", "Tarihler", "Süre", "Bütçe", "Durum"])
        self._tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tbl.verticalHeader().setVisible(False)
        self._tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tbl.setSelectionBehavior(QTableWidget.SelectRows)
        self._tbl.setStyleSheet(table_style())
        self._tbl.setMinimumHeight(220)
        lay.addWidget(self._tbl)
        lay.addStretch()

    def _divider(self):
        d = QFrame()
        d.setFrameShape(QFrame.HLine)
        d.setStyleSheet(f"background: rgba(232,115,90,0.15); border:none; max-height:1px;")
        return d

    def refresh(self):
        seyahatler = self._s.get_seyahatler()
        kon = self._s.get_gecerli_konaklamalar()
        planlar = self._s.get_tum_planlar()
        top_b = sum(s.get_butce() for s in seyahatler.values())
        top_h = sum(s.get_harcanan() for s in seyahatler.values())
        oran = (top_h / top_b * 100) if top_b > 0 else 0

        self._cards[0].set_value(str(len(seyahatler)))
        self._cards[1].set_value(str(len(kon)))
        self._cards[2].set_value(str(len(planlar)))
        self._cards[3].set_value(f"₺{top_b:,.0f}")
        self._cards[4].set_value(f"%{oran:.1f}")

        self._tbl.setRowCount(0)
        for s in list(seyahatler.values())[-8:]:
            r = self._tbl.rowCount()
            self._tbl.insertRow(r)
            durum = "✅" if s.get_aktif_mi() else "🔒"
            vals = [s.get_seyahat_id(), s.get_gidis_yeri(),
                    f"{s.get_baslangic_tar().strftime('%d.%m.%Y')} – {s.get_bitis_tar().strftime('%d.%m.%Y')}",
                    f"{s.get_sure_gun()} gün",
                    f"₺{s.get_butce():,.0f}",
                    durum]
            for c, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignCenter)
                self._tbl.setItem(r, c, item)


# ══════════════════════════════════════════════════════
#  SEYAHAT PAGE
# ══════════════════════════════════════════════════════

class SeyahatPage(QWidget):
    toast_signal = pyqtSignal(str, str)

    def __init__(self, sistem: SeyahatSistemi):
        super().__init__()
        self._s = sistem
        self.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(16)

        lay.addWidget(make_label("✈️  Seyahatler", 20, TEXT_PRI, bold=True))
        lay.addWidget(self._divider())

        # Form card
        form_card = QWidget()
        form_card.setStyleSheet(card_style())
        shadow(form_card, 12, TERRACOTTA, 40)
        fl = QGridLayout(form_card)
        fl.setContentsMargins(20, 16, 20, 16)
        fl.setSpacing(10)

        fl.addWidget(make_label("Seyahat ID", 11, TEXT_SEC), 0, 0)
        self._sid = QLineEdit(); self._sid.setPlaceholderText("S001")
        self._sid.setStyleSheet(input_style())
        fl.addWidget(self._sid, 1, 0)

        fl.addWidget(make_label("Destinasyon", 11, TEXT_SEC), 0, 1)
        self._dest = QLineEdit(); self._dest.setPlaceholderText("Paris, Fransa")
        self._dest.setStyleSheet(input_style())
        fl.addWidget(self._dest, 1, 1)

        fl.addWidget(make_label("Ulaşım Türü", 11, TEXT_SEC), 0, 2)
        self._ulasim = QComboBox()
        for u in UlasimTuru:
            self._ulasim.addItem(u.value)
        self._ulasim.setStyleSheet(input_style())
        fl.addWidget(self._ulasim, 1, 2)

        fl.addWidget(make_label("Gidiş Tarihi", 11, TEXT_SEC), 2, 0)
        self._bas = QDateTimeEdit(QDateTime.currentDateTime())
        self._bas.setDisplayFormat("dd.MM.yyyy HH:mm")
        self._bas.setStyleSheet(input_style())
        fl.addWidget(self._bas, 3, 0)

        fl.addWidget(make_label("Dönüş Tarihi", 11, TEXT_SEC), 2, 1)
        self._bit = QDateTimeEdit(QDateTime.currentDateTime().addDays(7))
        self._bit.setDisplayFormat("dd.MM.yyyy HH:mm")
        self._bit.setStyleSheet(input_style())
        fl.addWidget(self._bit, 3, 1)

        fl.addWidget(make_label("Bütçe (₺)", 11, TEXT_SEC), 2, 2)
        self._butce = QDoubleSpinBox()
        self._butce.setRange(0, 9999999)
        self._butce.setSingleStep(100)
        self._butce.setValue(5000)
        self._butce.setStyleSheet(input_style())
        fl.addWidget(self._butce, 3, 2)

        fl.addWidget(make_label("Notlar", 11, TEXT_SEC), 4, 0)
        self._notlar = QLineEdit()
        self._notlar.setPlaceholderText("Opsiyonel notlar...")
        self._notlar.setStyleSheet(input_style())
        fl.addWidget(self._notlar, 5, 0, 1, 3)

        btn_row = QHBoxLayout()
        self._add_btn = QPushButton("➕  Seyahat Ekle")
        self._add_btn.setStyleSheet(btn_style())
        self._add_btn.clicked.connect(self._ekle)
        self._del_btn = QPushButton("🗑️  Seçiliyi Sil")
        self._del_btn.setStyleSheet(btn_style(BG_MID, BG_HOVER))
        self._del_btn.clicked.connect(self._sil)
        btn_row.addWidget(self._add_btn)
        btn_row.addWidget(self._del_btn)
        btn_row.addStretch()
        fl.addLayout(btn_row, 6, 0, 1, 3)

        lay.addWidget(form_card)

        # Table
        self._tbl = QTableWidget()
        self._tbl.setColumnCount(8)
        self._tbl.setHorizontalHeaderLabels(
            ["ID", "Destinasyon", "Gidiş", "Dönüş", "Süre", "Ulaşım", "Bütçe", "Kalan"])
        self._tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tbl.verticalHeader().setVisible(False)
        self._tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tbl.setSelectionBehavior(QTableWidget.SelectRows)
        self._tbl.setStyleSheet(table_style())
        lay.addWidget(self._tbl)

    def _divider(self):
        d = QFrame(); d.setFrameShape(QFrame.HLine)
        d.setStyleSheet(f"background: rgba(232,115,90,0.15); border:none; max-height:1px;")
        return d

    def _ekle(self):
        sid = self._sid.text().strip()
        dest = self._dest.text().strip()
        if not sid or not dest:
            self.toast_signal.emit("ID ve destinasyon zorunlu!", "err")
            return
        bas = self._bas.dateTime().toPyDateTime()
        bit = self._bit.dateTime().toPyDateTime()
        ulasim = list(UlasimTuru)[self._ulasim.currentIndex()]
        butce = self._butce.value()
        notlar = self._notlar.text().strip()
        s = Seyahat(sid, dest, bas, bit, ulasim, butce, notlar)
        ok, msg = self._s.seyahat_ekle(s)
        self.toast_signal.emit(msg, "ok" if ok else "err")
        if ok:
            self._sid.clear(); self._dest.clear(); self._notlar.clear()
            self.refresh()

    def _sil(self):
        row = self._tbl.currentRow()
        if row < 0:
            self.toast_signal.emit("Silinecek seyahati seçin.", "err")
            return
        sid = self._tbl.item(row, 0).text()
        ok, msg = self._s.seyahat_sil(sid)
        self.toast_signal.emit(msg, "ok" if ok else "err")
        if ok:
            self.refresh()

    def refresh(self):
        self._tbl.setRowCount(0)
        for s in self._s.get_seyahatler().values():
            r = self._tbl.rowCount()
            self._tbl.insertRow(r)
            vals = [
                s.get_seyahat_id(),
                s.get_gidis_yeri(),
                s.get_baslangic_tar().strftime("%d.%m.%Y"),
                s.get_bitis_tar().strftime("%d.%m.%Y"),
                f"{s.get_sure_gun()} gün",
                s.get_ulasim_turu().value,
                f"₺{s.get_butce():,.0f}",
                f"₺{s.get_kalan_butce():,.0f}",
            ]
            for c, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignCenter)
                self._tbl.setItem(r, c, item)


# ══════════════════════════════════════════════════════
#  KONAKLAMA PAGE
# ══════════════════════════════════════════════════════

class KonaklamaPage(QWidget):
    toast_signal = pyqtSignal(str, str)

    def __init__(self, sistem: SeyahatSistemi):
        super().__init__()
        self._s = sistem
        self.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(16)

        lay.addWidget(make_label("🏨  Konaklamalar", 20, TEXT_PRI, bold=True))
        lay.addWidget(self._divider())

        # Form card
        fc = QWidget(); fc.setStyleSheet(card_style())
        shadow(fc, 12, GOLD, 40)
        fl = QGridLayout(fc)
        fl.setContentsMargins(20, 16, 20, 16); fl.setSpacing(10)

        fl.addWidget(make_label("Seyahat", 11, TEXT_SEC), 0, 0)
        self._sey_cb = QComboBox(); self._sey_cb.setStyleSheet(input_style())
        fl.addWidget(self._sey_cb, 1, 0)

        fl.addWidget(make_label("Otel / Yer Adı", 11, TEXT_SEC), 0, 1)
        self._otel = QLineEdit(); self._otel.setPlaceholderText("Hilton İstanbul")
        self._otel.setStyleSheet(input_style())
        fl.addWidget(self._otel, 1, 1)

        fl.addWidget(make_label("Konaklama Türü", 11, TEXT_SEC), 0, 2)
        self._tur_cb = QComboBox()
        for k in KonaklamaTuru:
            self._tur_cb.addItem(k.value)
        self._tur_cb.setStyleSheet(input_style())
        fl.addWidget(self._tur_cb, 1, 2)

        fl.addWidget(make_label("Gece Fiyatı (₺)", 11, TEXT_SEC), 2, 0)
        self._fiyat = QDoubleSpinBox(); self._fiyat.setRange(0, 99999)
        self._fiyat.setSingleStep(50); self._fiyat.setValue(500)
        self._fiyat.setStyleSheet(input_style())
        fl.addWidget(self._fiyat, 3, 0)

        fl.addWidget(make_label("Check-in", 11, TEXT_SEC), 2, 1)
        self._cin = QDateTimeEdit(QDateTime.currentDateTime())
        self._cin.setDisplayFormat("dd.MM.yyyy"); self._cin.setStyleSheet(input_style())
        fl.addWidget(self._cin, 3, 1)

        fl.addWidget(make_label("Check-out", 11, TEXT_SEC), 2, 2)
        self._cout = QDateTimeEdit(QDateTime.currentDateTime().addDays(3))
        self._cout.setDisplayFormat("dd.MM.yyyy"); self._cout.setStyleSheet(input_style())
        fl.addWidget(self._cout, 3, 2)

        fl.addWidget(make_label("Adres (opsiyonel)", 11, TEXT_SEC), 4, 0)
        self._adres = QLineEdit(); self._adres.setStyleSheet(input_style())
        fl.addWidget(self._adres, 5, 0, 1, 3)

        br = QHBoxLayout()
        ab = QPushButton("🏨  Rezervasyon Ekle"); ab.setStyleSheet(btn_style(GOLD, "#C88500"))
        ab.clicked.connect(self._ekle)
        cb = QPushButton("❌  Rezervasyon İptal"); cb.setStyleSheet(btn_style(BG_MID, BG_HOVER))
        cb.clicked.connect(self._iptal)
        br.addWidget(ab); br.addWidget(cb); br.addStretch()
        fl.addLayout(br, 6, 0, 1, 3)
        lay.addWidget(fc)

        self._tbl = QTableWidget()
        self._tbl.setColumnCount(7)
        self._tbl.setHorizontalHeaderLabels(
            ["ID", "Seyahat", "Otel", "Tür", "Gece Fiyatı", "Gece", "Toplam"])
        self._tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tbl.verticalHeader().setVisible(False)
        self._tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tbl.setSelectionBehavior(QTableWidget.SelectRows)
        self._tbl.setStyleSheet(table_style())
        lay.addWidget(self._tbl)

    def _divider(self):
        d = QFrame(); d.setFrameShape(QFrame.HLine)
        d.setStyleSheet(f"background: rgba(240,165,0,0.15); border:none; max-height:1px;")
        return d

    def _ekle(self):
        idx = self._sey_cb.currentIndex()
        seyahatler = list(self._s.get_seyahatler().keys())
        if not seyahatler:
            self.toast_signal.emit("Önce seyahat ekleyin!", "err"); return
        sid = seyahatler[idx]
        otel = self._otel.text().strip()
        if not otel:
            self.toast_signal.emit("Otel adı zorunlu!", "err"); return
        tur = list(KonaklamaTuru)[self._tur_cb.currentIndex()]
        fiyat = self._fiyat.value()
        cin = self._cin.dateTime().toPyDateTime()
        cout = self._cout.dateTime().toPyDateTime()
        adres = self._adres.text().strip()
        ok, msg = self._s.konaklama_ekle(sid, otel, tur, fiyat, cin, cout, adres)
        self.toast_signal.emit(msg, "ok" if ok else "err")
        if ok:
            self._otel.clear(); self._adres.clear(); self.refresh()

    def _iptal(self):
        row = self._tbl.currentRow()
        if row < 0:
            self.toast_signal.emit("İptal edilecek rezervasyonu seçin.", "err"); return
        kid = self._tbl.item(row, 0).text()
        ok, msg = self._s.konaklama_iptal_et(kid)
        self.toast_signal.emit(msg, "ok" if ok else "err")
        if ok: self.refresh()

    def refresh(self):
        self._sey_cb.clear()
        for sid, s in self._s.get_seyahatler().items():
            self._sey_cb.addItem(f"{sid} — {s.get_gidis_yeri()}")

        self._tbl.setRowCount(0)
        for k in self._s.get_gecerli_konaklamalar():
            r = self._tbl.rowCount(); self._tbl.insertRow(r)
            vals = [
                k.get_konaklama_id(),
                k.get_seyahat().get_gidis_yeri(),
                k.get_otel_adi(),
                k.get_tur().value,
                f"₺{k.get_fiyat_gece():,.0f}",
                str(k.get_gece_sayisi()),
                f"₺{k.get_toplam_ucret():,.0f}",
            ]
            for c, v in enumerate(vals):
                item = QTableWidgetItem(v); item.setTextAlignment(Qt.AlignCenter)
                self._tbl.setItem(r, c, item)


# ══════════════════════════════════════════════════════
#  PLAN PAGE
# ══════════════════════════════════════════════════════

class PlanPage(QWidget):
    toast_signal = pyqtSignal(str, str)

    def __init__(self, sistem: SeyahatSistemi):
        super().__init__()
        self._s = sistem
        self._secili_plan: Optional[Plan] = None
        self.setStyleSheet("background:transparent;")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(16)

        lay.addWidget(make_label("🗺️  Seyahat Planları", 20, TEXT_PRI, bold=True))
        lay.addWidget(self._divider())

        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background: rgba(232,115,90,0.15); width:2px; }")

        # Left: plan list
        left = QWidget(); left.setStyleSheet("background:transparent;")
        ll = QVBoxLayout(left); ll.setContentsMargins(0,0,8,0); ll.setSpacing(10)
        ll.addWidget(make_label("Planlar", 13, TEXT_PRI, bold=True))

        pc = QWidget(); pc.setStyleSheet(card_style())
        shadow(pc, 10, SAGE, 40)
        pl = QVBoxLayout(pc); pl.setContentsMargins(14,12,14,12); pl.setSpacing(8)

        pl.addWidget(make_label("Seyahat Seç", 11, TEXT_SEC))
        self._sey_cb = QComboBox(); self._sey_cb.setStyleSheet(input_style())
        pl.addWidget(self._sey_cb)

        ab = QPushButton("➕  Yeni Plan Oluştur"); ab.setStyleSheet(btn_style(SAGE, "#5A9880"))
        ab.clicked.connect(self._yeni_plan)
        pl.addWidget(ab)
        ll.addWidget(pc)

        self._plan_list = QListWidget()
        self._plan_list.setStyleSheet(f"""
            QListWidget {{
                background:{BG_CARD}; border:1px solid {BORDER};
                border-radius:10px; color:{TEXT_PRI}; font-size:12px;
            }}
            QListWidget::item {{ padding:8px 12px; border-bottom:1px solid {BG_MID}; }}
            QListWidget::item:selected {{ background:rgba(126,184,164,0.2); }}
        """)
        self._plan_list.currentRowChanged.connect(self._plan_secildi)
        ll.addWidget(self._plan_list)
        splitter.addWidget(left)

        # Right: plan detail
        right = QWidget(); right.setStyleSheet("background:transparent;")
        rl = QVBoxLayout(right); rl.setContentsMargins(8,0,0,0); rl.setSpacing(10)

        self._plan_baslik = make_label("— Plan Seçilmedi —", 14, TEXT_SEC, bold=True)
        rl.addWidget(self._plan_baslik)

        # Rota section
        rota_card = QWidget(); rota_card.setStyleSheet(card_style())
        shadow(rota_card, 10, LAVENDER, 40)
        rcl = QVBoxLayout(rota_card); rcl.setContentsMargins(14,12,14,12); rcl.setSpacing(8)
        rcl.addWidget(make_label("📍 Rota Noktaları", 12, LAVENDER, bold=True))
        ri = QHBoxLayout()
        self._rota_in = QLineEdit(); self._rota_in.setPlaceholderText("Eyfel Kulesi, Louvre...")
        self._rota_in.setStyleSheet(input_style())
        ri.addWidget(self._rota_in)
        ra = QPushButton("Ekle"); ra.setStyleSheet(btn_style(LAVENDER, "#8B6FE8", padding="6px 14px"))
        ra.clicked.connect(self._rota_ekle)
        ri.addWidget(ra)
        rcl.addLayout(ri)
        self._rota_list = QListWidget()
        self._rota_list.setStyleSheet(f"""
            QListWidget {{ background:{BG_MID}; border-radius:6px; color:{TEXT_PRI}; font-size:11px; }}
            QListWidget::item {{ padding:4px 8px; }}
            QListWidget::item:selected {{ background:rgba(167,139,250,0.2); }}
        """)
        self._rota_list.setMaximumHeight(100)
        rcl.addWidget(self._rota_list)
        rr = QPushButton("🗑️ Seçiliyi Çıkar"); rr.setStyleSheet(btn_style(BG_MID, BG_HOVER, padding="5px 12px"))
        rr.clicked.connect(self._rota_cikar)
        rcl.addWidget(rr, alignment=Qt.AlignRight)
        rl.addWidget(rota_card)

        # Aktivite section
        akt_card = QWidget(); akt_card.setStyleSheet(card_style())
        shadow(akt_card, 10, GOLD, 40)
        acl = QVBoxLayout(akt_card); acl.setContentsMargins(14,12,14,12); acl.setSpacing(8)
        acl.addWidget(make_label("🎯 Aktiviteler", 12, GOLD, bold=True))
        ai = QHBoxLayout()
        self._akt_in = QLineEdit(); self._akt_in.setPlaceholderText("Müze Turu, Tekne Gezisi...")
        self._akt_in.setStyleSheet(input_style())
        ai.addWidget(self._akt_in)
        self._akt_fiyat = QDoubleSpinBox(); self._akt_fiyat.setRange(0, 99999)
        self._akt_fiyat.setSingleStep(50); self._akt_fiyat.setPrefix("₺")
        self._akt_fiyat.setStyleSheet(input_style()); self._akt_fiyat.setFixedWidth(110)
        ai.addWidget(self._akt_fiyat)
        aa = QPushButton("Ekle"); aa.setStyleSheet(btn_style(GOLD, "#C88500", padding="6px 14px"))
        aa.clicked.connect(self._akt_ekle)
        ai.addWidget(aa)
        acl.addLayout(ai)
        self._akt_list = QListWidget()
        self._akt_list.setStyleSheet(f"""
            QListWidget {{ background:{BG_MID}; border-radius:6px; color:{TEXT_PRI}; font-size:11px; }}
            QListWidget::item {{ padding:4px 8px; }}
            QListWidget::item:selected {{ background:rgba(240,165,0,0.2); }}
        """)
        self._akt_list.setMaximumHeight(120)
        acl.addWidget(self._akt_list)
        ar = QPushButton("🗑️ Seçili Aktiviteyi Sil"); ar.setStyleSheet(btn_style(BG_MID, BG_HOVER, padding="5px 12px"))
        ar.clicked.connect(self._akt_sil)
        acl.addWidget(ar, alignment=Qt.AlignRight)
        rl.addWidget(akt_card)
        rl.addStretch()
        splitter.addWidget(right)
        splitter.setSizes([380, 620])
        lay.addWidget(splitter)

    def _divider(self):
        d = QFrame(); d.setFrameShape(QFrame.HLine)
        d.setStyleSheet(f"background: rgba(126,184,164,0.15); border:none; max-height:1px;")
        return d

    def _yeni_plan(self):
        seyahatler = list(self._s.get_seyahatler().keys())
        if not seyahatler:
            self.toast_signal.emit("Önce seyahat ekleyin!", "err"); return
        idx = self._sey_cb.currentIndex()
        sid = seyahatler[idx]
        ok, msg, p = self._s.plan_olustur(sid)
        self.toast_signal.emit(msg, "ok" if ok else "err")
        if ok: self.refresh()

    def _plan_secildi(self, row):
        planlar = self._s.get_tum_planlar()
        if row < 0 or row >= len(planlar):
            self._secili_plan = None
            self._plan_baslik.setText("— Plan Seçilmedi —")
            return
        self._secili_plan = planlar[row]
        self._plan_baslik.setText(
            f"Plan {self._secili_plan.get_plan_id()} — {self._secili_plan.get_seyahat().get_gidis_yeri()}")
        self._refresh_detail()

    def _refresh_detail(self):
        if not self._secili_plan:
            return
        self._rota_list.clear()
        for yer in self._secili_plan.get_rota():
            self._rota_list.addItem(f"📍 {yer}")
        self._akt_list.clear()
        for akt, fiyat in self._secili_plan.get_aktiviteler().items():
            self._akt_list.addItem(f"🎯 {akt}  —  ₺{fiyat:,.0f}")

    def _rota_ekle(self):
        if not self._secili_plan:
            self.toast_signal.emit("Önce bir plan seçin.", "err"); return
        yer = self._rota_in.text().strip()
        if not yer:
            self.toast_signal.emit("Yer adı boş olamaz.", "err"); return
        ok, msg = self._secili_plan.rota_ekle(yer)
        self.toast_signal.emit(msg, "ok" if ok else "err")
        if ok:
            self._rota_in.clear(); self._refresh_detail()

    def _rota_cikar(self):
        if not self._secili_plan: return
        row = self._rota_list.currentRow()
        if row < 0: return
        yer = self._secili_plan.get_rota()[row]
        ok, msg = self._secili_plan.rota_cikar(yer)
        self.toast_signal.emit(msg, "ok" if ok else "err")
        if ok: self._refresh_detail()

    def _akt_ekle(self):
        if not self._secili_plan:
            self.toast_signal.emit("Önce bir plan seçin.", "err"); return
        akt = self._akt_in.text().strip()
        if not akt:
            self.toast_signal.emit("Aktivite adı boş olamaz.", "err"); return
        fiyat = self._akt_fiyat.value()
        ok, msg = self._secili_plan.aktivite_ekle(akt, fiyat)
        self.toast_signal.emit(msg, "ok" if ok else "err")
        if ok:
            self._akt_in.clear(); self._akt_fiyat.setValue(0); self._refresh_detail()

    def _akt_sil(self):
        if not self._secili_plan: return
        row = self._akt_list.currentRow()
        if row < 0: return
        akt = list(self._secili_plan.get_aktiviteler().keys())[row]
        ok, msg = self._secili_plan.aktivite_sil(akt)
        self.toast_signal.emit(msg, "ok" if ok else "err")
        if ok: self._refresh_detail()

    def refresh(self):
        self._sey_cb.clear()
        for sid, s in self._s.get_seyahatler().items():
            self._sey_cb.addItem(f"{sid} — {s.get_gidis_yeri()}")
        self._plan_list.clear()
        for p in self._s.get_tum_planlar():
            akt_say = len(p.get_aktiviteler())
            rota_say = len(p.get_rota())
            self._plan_list.addItem(
                f"{p.get_plan_id()}  ·  {p.get_seyahat().get_gidis_yeri()}\n"
                f"   🗺 {rota_say} durak  ·  🎯 {akt_say} aktivite")
        self._refresh_detail()


# ══════════════════════════════════════════════════════
#  RAPOR PAGE
# ══════════════════════════════════════════════════════

class RaporPage(QWidget):
    toast_signal = pyqtSignal(str, str)

    def __init__(self, sistem: SeyahatSistemi):
        super().__init__()
        self._s = sistem
        self.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(16)

        lay.addWidget(make_label("📊  Raporlar & Özet", 20, TEXT_PRI, bold=True))
        d = QFrame(); d.setFrameShape(QFrame.HLine)
        d.setStyleSheet(f"background: rgba(96,165,250,0.15); border:none; max-height:1px;")
        lay.addWidget(d)

        row = QHBoxLayout(); row.setSpacing(14)

        # Genel özet
        self._ozet_card = QWidget(); self._ozet_card.setStyleSheet(card_style())
        shadow(self._ozet_card, 14, SKY, 50)
        ocl = QVBoxLayout(self._ozet_card); ocl.setContentsMargins(18,14,18,14); ocl.setSpacing(6)
        ocl.addWidget(make_label("📋 Sistem Özeti", 13, SKY, bold=True))
        ocl.addWidget(self._divider(SKY))
        self._ozet_lay = QVBoxLayout(); ocl.addLayout(self._ozet_lay)
        ocl.addStretch()
        row.addWidget(self._ozet_card)

        # Bütçe raporu
        self._butce_card = QWidget(); self._butce_card.setStyleSheet(card_style())
        shadow(self._butce_card, 14, LAVENDER, 50)
        bcl = QVBoxLayout(self._butce_card); bcl.setContentsMargins(18,14,18,14); bcl.setSpacing(6)
        bcl.addWidget(make_label("💰 Bütçe Raporu", 13, LAVENDER, bold=True))
        bcl.addWidget(self._divider(LAVENDER))
        self._butce_lay = QVBoxLayout(); bcl.addLayout(self._butce_lay)
        bcl.addStretch()
        row.addWidget(self._butce_card)

        # Aktivite raporu
        self._akt_card = QWidget(); self._akt_card.setStyleSheet(card_style())
        shadow(self._akt_card, 14, GOLD, 50)
        acl = QVBoxLayout(self._akt_card); acl.setContentsMargins(18,14,18,14); acl.setSpacing(6)
        acl.addWidget(make_label("🎯 Aktivite Raporu", 13, GOLD, bold=True))
        acl.addWidget(self._divider(GOLD))
        self._akt_lay = QVBoxLayout(); acl.addLayout(self._akt_lay)
        acl.addStretch()
        row.addWidget(self._akt_card)

        lay.addLayout(row)

        # Per-trip budget bars
        lay.addWidget(make_label("Seyahat Bütçe Kullanımı", 14, TEXT_PRI, bold=True))
        self._bars_widget = QWidget()
        self._bars_widget.setStyleSheet(card_style())
        shadow(self._bars_widget, 10, TERRACOTTA, 30)
        self._bars_lay = QVBoxLayout(self._bars_widget)
        self._bars_lay.setContentsMargins(18, 14, 18, 14)
        self._bars_lay.setSpacing(10)
        lay.addWidget(self._bars_widget)
        lay.addStretch()

    def _divider(self, color=SKY):
        d = QFrame(); d.setFrameShape(QFrame.HLine)
        d.setStyleSheet(f"background: rgba(96,165,250,0.15); border:none; max-height:1px; margin:2px 0;")
        return d

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def refresh(self):
        rapor = self._s.rapor_olustur()

        self._clear_layout(self._ozet_lay)
        for k, v in self._s.detayli_ozet().items():
            row = QHBoxLayout()
            row.addWidget(make_label(k, 11, TEXT_SEC))
            row.addStretch()
            row.addWidget(make_label(str(v), 11, TEXT_PRI, bold=True))
            w = QWidget(); w.setStyleSheet("background:transparent;"); w.setLayout(row)
            self._ozet_lay.addWidget(w)

        self._clear_layout(self._butce_lay)
        for k, v in rapor.butce_raporu().items():
            row = QHBoxLayout()
            row.addWidget(make_label(k, 11, TEXT_SEC))
            row.addStretch()
            row.addWidget(make_label(str(v), 11, LAVENDER, bold=True))
            w = QWidget(); w.setStyleSheet("background:transparent;"); w.setLayout(row)
            self._butce_lay.addWidget(w)

        self._clear_layout(self._akt_lay)
        for k, v in rapor.aktivite_raporu().items():
            row = QHBoxLayout()
            row.addWidget(make_label(k, 11, TEXT_SEC))
            row.addStretch()
            row.addWidget(make_label(str(v), 11, GOLD, bold=True))
            w = QWidget(); w.setStyleSheet("background:transparent;"); w.setLayout(row)
            self._akt_lay.addWidget(w)

        # Budget bars
        self._clear_layout(self._bars_lay)
        for s in self._s.get_seyahatler().values():
            oran = s.get_butce_kullanim_orani()
            bar_row = QVBoxLayout()
            lbl_row = QHBoxLayout()
            lbl_row.addWidget(make_label(f"{s.get_gidis_yeri()} ({s.get_seyahat_id()})", 11, TEXT_PRI))
            lbl_row.addStretch()
            lbl_row.addWidget(make_label(
                f"₺{s.get_harcanan():,.0f} / ₺{s.get_butce():,.0f}  (%{oran:.1f})", 11, TEXT_SEC))
            bar_row.addLayout(lbl_row)

            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(int(oran))
            bar.setTextVisible(False)
            bar.setFixedHeight(8)
            color = TERRACOTTA if oran > 80 else GOLD if oran > 50 else SAGE
            bar.setStyleSheet(f"""
                QProgressBar {{ background:{BG_MID}; border-radius:4px; border:none; }}
                QProgressBar::chunk {{ background:{color}; border-radius:4px; }}
            """)
            bar_row.addWidget(bar)

            w = QWidget(); w.setStyleSheet("background:transparent;"); w.setLayout(bar_row)
            self._bars_lay.addWidget(w)

        if not self._s.get_seyahatler():
            self._bars_lay.addWidget(make_label("Henüz seyahat eklenmedi.", 12, TEXT_MUTED))


# ══════════════════════════════════════════════════════
#  MAIN WINDOW
# ══════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sistem = SeyahatSistemi()
        self.sistem.verileri_yukle()
        self._seed_data()

        self.setWindowTitle("✈️  Seyahat Planlama Uygulaması")
        self.setMinimumSize(1200, 760)
        self.resize(1380, 840)
        self.setStyleSheet(f"QMainWindow {{ background: {BG_DEEP}; }}")

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Animated background
        self._bg = AnimatedBG(central)
        self._bg.setGeometry(0, 0, 1380, 840)
        self._bg.lower()

        # Nav rail
        rail = QWidget()
        rail.setFixedWidth(86)
        rail.setStyleSheet(f"""
            QWidget {{
                background: rgba(5,8,14,0.94);
                border-right: 1px solid rgba(232,115,90,0.12);
            }}
        """)
        rl = QVBoxLayout(rail)
        rl.setContentsMargins(6, 18, 6, 18)
        rl.setSpacing(4)
        rl.setAlignment(Qt.AlignTop)

        logo = QLabel("✈️")
        logo.setStyleSheet(f"""
            font-size: 24px;
            background: rgba(232,115,90,0.14);
            border: 1px solid rgba(232,115,90,0.35);
            border-radius: 14px;
            padding: 6px;
        """)
        logo.setAlignment(Qt.AlignCenter)
        logo.setFixedSize(56, 56)
        rl.addWidget(logo, alignment=Qt.AlignHCenter)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: rgba(232,115,90,0.12); border:none; max-height:1px; margin:8px 6px;")
        rl.addWidget(sep)

        nav = [("🏠", "GENEL", 0), ("✈️", "SEYAHAT", 1),
               ("🏨", "KONAKLAMA", 2), ("🗺️", "PLAN", 3), ("📊", "RAPOR", 4)]
        self._nav_btns = []
        for ico, lbl, idx in nav:
            btn = NavBtn(ico, lbl)
            btn.clicked.connect(lambda _, i=idx: self._go(i))
            self._nav_btns.append(btn)
            rl.addWidget(btn, alignment=Qt.AlignHCenter)

        rl.addStretch()

        # Save button
        save_btn = QPushButton("💾")
        save_btn.setToolTip("Kaydet")
        save_btn.setFixedSize(44, 44)
        save_btn.setStyleSheet(f"""
            QPushButton {{ background: rgba(232,115,90,0.12); border:1px solid rgba(232,115,90,0.3);
                           border-radius:10px; font-size:18px; color:{TEXT_PRI}; }}
            QPushButton:hover {{ background: rgba(232,115,90,0.25); }}
        """)
        save_btn.clicked.connect(self._kaydet)
        rl.addWidget(save_btn, alignment=Qt.AlignHCenter)

        root.addWidget(rail)

        # Pages
        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background:transparent;")

        self._pages = [
            DashboardPage(self.sistem),
            SeyahatPage(self.sistem),
            KonaklamaPage(self.sistem),
            PlanPage(self.sistem),
            RaporPage(self.sistem),
        ]
        for pg in self._pages:
            self._stack.addWidget(pg)
            if hasattr(pg, 'toast_signal'):
                pg.toast_signal.connect(self._toast)

        root.addWidget(self._stack)
        self._toasts = []
        self._go(0)

    def _go(self, idx):
        for i, btn in enumerate(self._nav_btns):
            btn.setActive(i == idx)
        self._stack.setCurrentIndex(idx)
        self._pages[idx].refresh()

    def _kaydet(self):
        ok = self.sistem.verileri_kaydet()
        self._toast("Veriler kaydedildi ✅" if ok else "Kayıt hatası ❌", "ok" if ok else "err")

    def _toast(self, msg, kind="ok"):
        t = Toast(msg, kind, self)
        t.show(); t.adjustSize()
        y = self.height() - 70
        for ex in self._toasts:
            y -= ex.height() + 8
        t.move(self.width() - t.width() - 20, y)
        t.raise_()
        self._toasts.append(t)
        QTimer.singleShot(3000, lambda: self._rm_toast(t))

    def _rm_toast(self, t):
        if t in self._toasts:
            self._toasts.remove(t)
        t.deleteLater()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._bg.setGeometry(0, 0, self.width(), self.height())

    def _seed_data(self):
        if self.sistem.get_seyahatler():
            return  # Zaten veri var

        seyahatler = [
            ("S001", "Paris, Fransa",   datetime(2026, 7, 10), datetime(2026, 7, 17), UlasimTuru.UCAK,   15000),
            ("S002", "Tokyo, Japonya",  datetime(2026, 9, 1),  datetime(2026, 9, 14), UlasimTuru.UCAK,   35000),
            ("S003", "Kapadokya, TR",   datetime(2026, 6, 20), datetime(2026, 6, 23), UlasimTuru.ARAC,    4000),
            ("S004", "Barselona, İsp.", datetime(2026, 10, 5), datetime(2026, 10, 12),UlasimTuru.UCAK,   20000),
        ]
        for args in seyahatler:
            sid, dest, bas, bit, ul, but = args
            self.sistem.seyahat_ekle(Seyahat(sid, dest, bas, bit, ul, but))

        self.sistem.konaklama_ekle(
            "S001", "Hôtel Le Marais", KonaklamaTuru.OTEL, 1800,
            datetime(2026, 7, 10), datetime(2026, 7, 17), "Paris, 3e arr.")
        self.sistem.konaklama_ekle(
            "S002", "Shinjuku Hostel", KonaklamaTuru.HOSTEL, 600,
            datetime(2026, 9, 1), datetime(2026, 9, 14), "Shinjuku, Tokyo")
        self.sistem.konaklama_ekle(
            "S003", "Kaya Cave Hotel", KonaklamaTuru.OTEL, 900,
            datetime(2026, 6, 20), datetime(2026, 6, 23), "Göreme, Nevşehir")

        ok, msg, p1 = self.sistem.plan_olustur("S001", ["Eyfel Kulesi", "Louvre", "Montmartre"])
        if ok:
            p1.aktivite_ekle("Louvre Müzesi Turu", 500)
            p1.aktivite_ekle("Seine Nehri Teknesi", 300)
            p1.aktivite_ekle("Şarap Tadımı", 250)

        ok, msg, p2 = self.sistem.plan_olustur("S002", ["Shinjuku", "Akihabara", "Fuji Dağı"])
        if ok:
            p2.aktivite_ekle("TeamLab Planets", 800)
            p2.aktivite_ekle("Sushi Workshop", 1200)


# ══════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Seyahat Planlama Uygulaması")

    pal = QPalette()
    pal.setColor(QPalette.Window,          QColor(BG_DEEP))
    pal.setColor(QPalette.WindowText,      QColor(TEXT_PRI))
    pal.setColor(QPalette.Base,            QColor(BG_CARD))
    pal.setColor(QPalette.Text,            QColor(TEXT_PRI))
    pal.setColor(QPalette.Button,          QColor(BG_MID))
    pal.setColor(QPalette.ButtonText,      QColor(TEXT_PRI))
    pal.setColor(QPalette.Highlight,       QColor(TERRACOTTA))
    pal.setColor(QPalette.HighlightedText, QColor(BG_DEEP))
    app.setPalette(pal)

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
