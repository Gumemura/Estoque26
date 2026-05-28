from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QFrame,
    QLineEdit,
    QHeaderView,
    QSizePolicy,
    QAbstractItemView,
    QSplitter,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor

from app.ui.styles.theme import build_stylesheet, DARK, LIGHT
from app.shared.dict.pt_br import STRINGS as PT_BR

LANGUAGES = {
    "pt_BR": PT_BR
}

_THEME = LIGHT
current_language = "pt_BR"

# ---------------------------------------------------------------------------
# Toolbar action button
# ---------------------------------------------------------------------------
class ActionButton(QPushButton):
    def __init__(self, icon_char: str, label: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("actionButton")
        self.setFixedSize(QSize(64, 52))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 4, 2, 2)
        layout.setSpacing(1)
        layout.setAlignment(Qt.AlignHCenter)

        icon_lbl = QLabel(icon_char)
        icon_lbl.setObjectName("actionButtonIcon")
        icon_lbl.setAlignment(Qt.AlignHCenter)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 18))
        icon_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        layout.addWidget(icon_lbl)

        text_lbl = QLabel(label)
        text_lbl.setObjectName("actionButtonLabel")
        text_lbl.setAlignment(Qt.AlignHCenter)
        text_lbl.setFont(QFont("Segoe UI", 9))
        text_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        layout.addWidget(text_lbl)


# ---------------------------------------------------------------------------
# Toolbar group (labelled cluster of ActionButtons)
# ---------------------------------------------------------------------------
class ToolbarGroup(QFrame):
    def __init__(self, title: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("toolbarGroup")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(6, 4, 6, 2)
        outer.setSpacing(2)

        self._btn_row = QHBoxLayout()
        self._btn_row.setSpacing(2)
        self._btn_row.setAlignment(Qt.AlignLeft)
        outer.addLayout(self._btn_row)

        title_lbl = QLabel(title.upper())
        title_lbl.setObjectName("toolbarGroupLabel")
        title_lbl.setAlignment(Qt.AlignHCenter)
        outer.addWidget(title_lbl)

    def add_button(self, icon_char: str, label: str) -> ActionButton:
        btn = ActionButton(icon_char, label, self)
        self._btn_row.addWidget(btn)
        return btn


# ---------------------------------------------------------------------------
# Main toolbar (groups separated by vertical lines)
# ---------------------------------------------------------------------------
class MainToolbar(QFrame):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("mainToolbar")
        self.setFixedHeight(80)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(4, 0, 4, 0)
        self._layout.setSpacing(0)
        self._layout.setAlignment(Qt.AlignLeft)

    def add_group(self, title: str) -> ToolbarGroup:
        group = ToolbarGroup(title, self)
        self._layout.addWidget(group)
        return group

    def add_stretch(self):
        self._layout.addStretch()

# ---------------------------------------------------------------------------
# Search / filter bar
# ---------------------------------------------------------------------------
class FilterBar(QFrame):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("filterBar")
        self.setFixedHeight(36)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(8)

        search_icon = QLabel("🔍")
        search_icon.setFont(QFont("Segoe UI Emoji", 10))
        layout.addWidget(search_icon)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText(LANGUAGES[current_language].get("search_input_text"))
        self.search_input.setFont(QFont("Segoe UI", 11))
        self.search_input.setFixedHeight(24)
        layout.addWidget(self.search_input, stretch=1)

        for label in (
            LANGUAGES[current_language].get("all_filter_bar"),
            LANGUAGES[current_language].get("actives_filter_bar"),
            LANGUAGES[current_language].get("critical_filter_bar"),
            LANGUAGES[current_language].get("inactives_filter_bar")):
            btn = QPushButton(label)
            btn.setObjectName("filterChip")
            btn.setCheckable(True)
            btn.setFont(QFont("Segoe UI", 10))
            btn.setFixedHeight(22)
            if label == "Todos":
                btn.setChecked(True)
                btn.setObjectName("filterChipActive")
            layout.addWidget(btn)


# ---------------------------------------------------------------------------
# Inventory data table
# ---------------------------------------------------------------------------
COLUMNS = [
    ("Código",       80),
    ("Descrição",   220),
    ("Categoria",   100),
    ("Localização",  90),
    ("Estoque",      70),
    ("Mín.",         50),
    ("Máx.",         50),
    ("Unid.",        50),
    ("Fornecedor",  130),
    ("Últ. Entrada", 95),
    ("Últ. Saída",   95),
    ("Status",       80),
]

SAMPLE_ROWS = [
    ("RES-0402-10K",  "Resistor SMD 0402 10kΩ 1%",       "Resistor",    "A1-P3",  "48.200", "10.000", "100.000", "un", "Digi-Key",    "23/05/2026", "24/05/2026", "OK"),
    ("CAP-0805-100N", "Capacitor Cerâmico 100nF 50V",     "Capacitor",   "A2-P1",   "3.400",  "5.000",  "50.000", "un", "Mouser",     "20/05/2026", "24/05/2026", "CRÍTICO"),
    ("IC-STM32F103",  "MCU STM32F103C8T6 ARM Cortex-M3", "CI",          "B1-P2",     "120",     "50",     "500",  "un", "STMicro",    "18/05/2026", "22/05/2026", "OK"),
    ("CONN-JST-2P",   "Conector JST-XH 2 Pinos",         "Conector",    "C3-P1",   "2.100",    "500",   "5.000", "un", "Würth",      "21/05/2026", "23/05/2026", "OK"),
    ("RES-0402-100R", "Resistor SMD 0402 100Ω 1%",       "Resistor",    "A1-P4",  "62.000", "10.000", "100.000", "un", "Digi-Key",   "23/05/2026", "23/05/2026", "OK"),
    ("LED-0603-GRN",  "LED SMD 0603 Verde 520nm",        "LED",         "D2-P2",   "8.900",  "2.000",  "20.000", "un", "Lumex",      "17/05/2026", "24/05/2026", "OK"),
    ("IC-LM358",      "Op-Amp LM358 DIP-8",              "CI",          "B2-P1",     "340",     "100",   "1.000", "un", "TI",         "15/05/2026", "20/05/2026", "OK"),
    ("CAP-0402-10N",  "Capacitor Cerâmico 10nF 25V",     "Capacitor",   "A2-P3",   "1.200",  "5.000",  "40.000", "un", "Mouser",     "10/05/2026", "24/05/2026", "CRÍTICO"),
    ("XTAL-16MHZ",    "Cristal Oscilador 16MHz HC-49S",  "Passivo",     "E1-P1",     "890",     "200",   "2.000", "un", "TXC",        "12/05/2026", "21/05/2026", "OK"),
    ("IC-ESP32-WROOM","Módulo ESP32-WROOM-32 4MB",        "Módulo",      "B3-P1",      "74",      "50",     "300", "un", "Espressif",  "19/05/2026", "23/05/2026", "OK"),
    ("FUSE-1A-SMD",   "Fusível SMD 1206 1A 125V",        "Proteção",    "F1-P2",     "430",     "500",   "3.000", "un", "Littelfuse", "08/05/2026", "22/05/2026", "CRÍTICO"),
    ("IND-0805-10UH", "Indutor SMD 0805 10µH 500mA",     "Indutor",     "G1-P1",   "1.650",    "300",   "5.000", "un", "Bourns",     "22/05/2026", "24/05/2026", "OK"),
    ("IND-0805-10UH", "Indutor SMD 0805 10µH 500mA",     "Indutor",     "G1-P1",   "1.650",    "300",   "5.000", "un", "Bourns",     "22/05/2026", "24/05/2026", "OK"),
    ("IND-0805-10UH", "Indutor SMD 0805 10µH 500mA",     "Indutor",     "G1-P1",   "1.650",    "300",   "5.000", "un", "Bourns",     "22/05/2026", "24/05/2026", "OK"),
    ("IND-0805-10UH", "Indutor SMD 0805 10µH 500mA",     "Indutor",     "G1-P1",   "1.650",    "300",   "5.000", "un", "Bourns",     "22/05/2026", "24/05/2026", "OK"),
    ("IND-0805-10UH", "Indutor SMD 0805 10µH 500mA",     "Indutor",     "G1-P1",   "1.650",    "300",   "5.000", "un", "Bourns",     "22/05/2026", "24/05/2026", "OK"),
    ("IND-0805-10UH", "Indutor SMD 0805 10µH 500mA",     "Indutor",     "G1-P1",   "1.650",    "300",   "5.000", "un", "Bourns",     "22/05/2026", "24/05/2026", "OK"),
    ("IND-0805-10UH", "Indutor SMD 0805 10µH 500mA",     "Indutor",     "G1-P1",   "1.650",    "300",   "5.000", "un", "Bourns",     "22/05/2026", "24/05/2026", "OK"),
    ("IND-0805-10UH", "Indutor SMD 0805 10µH 500mA",     "Indutor",     "G1-P1",   "1.650",    "300",   "5.000", "un", "Bourns",     "22/05/2026", "24/05/2026", "OK"),
    ("IND-0805-10UH", "Indutor SMD 0805 10µH 500mA",     "Indutor",     "G1-P1",   "1.650",    "300",   "5.000", "un", "Bourns",     "22/05/2026", "24/05/2026", "OK"),
    ("IND-0805-10UH", "Indutor SMD 0805 10µH 500mA",     "Indutor",     "G1-P1",   "1.650",    "300",   "5.000", "un", "Bourns",     "22/05/2026", "24/05/2026", "OK"),
    ("IND-0805-10UH", "Indutor SMD 0805 10µH 500mA",     "Indutor",     "G1-P1",   "1.650",    "300",   "5.000", "un", "Bourns",     "22/05/2026", "24/05/2026", "OK"),
    ("IND-0805-10UH", "Indutor SMD 0805 10µH 500mA",     "Indutor",     "G1-P1",   "1.650",    "300",   "5.000", "un", "Bourns",     "22/05/2026", "24/05/2026", "OK"),
    ("IND-0805-10UH", "Indutor SMD 0805 10µH 500mA",     "Indutor",     "G1-P1",   "1.650",    "300",   "5.000", "un", "Bourns",     "22/05/2026", "24/05/2026", "OK"),
    ("IND-0805-10UH", "Indutor SMD 0805 10µH 500mA",     "Indutor",     "G1-P1",   "1.650",    "300",   "5.000", "un", "Bourns",     "22/05/2026", "24/05/2026", "OK"),
    ("IND-0805-10UH", "Indutor SMD 0805 10µH 500mA",     "Indutor",     "G1-P1",   "1.650",    "300",   "5.000", "un", "Bourns",     "22/05/2026", "24/05/2026", "OK"),
    ("IND-0805-10UH", "Indutor SMD 0805 10µH 500mA",     "Indutor",     "G1-P1",   "1.650",    "300",   "5.000", "un", "Bourns",     "22/05/2026", "24/05/2026", "OK"),
    ("IND-0805-10UH", "Indutor SMD 0805 10µH 500mA",     "Indutor",     "G1-P1",   "1.650",    "300",   "5.000", "un", "Bourns",     "22/05/2026", "24/05/2026", "OK"),
    ("IND-0805-10UH", "Indutor SMD 0805 10µH 500mA",     "Indutor",     "G1-P1",   "1.650",    "300",   "5.000", "un", "Bourns",     "22/05/2026", "24/05/2026", "OK"),
    ("IND-0805-10UH", "Indutor SMD 0805 10µH 500mA",     "Indutor",     "G1-P1",   "1.650",    "300",   "5.000", "un", "Bourns",     "22/05/2026", "24/05/2026", "OK"),
    ("IND-0805-10UH", "Indutor SMD 0805 10µH 500mA",     "Indutor",     "G1-P1",   "1.650",    "300",   "5.000", "un", "Bourns",     "22/05/2026", "24/05/2026", "OK"),
    ("IND-0805-10UH", "Indutor SMD 0805 10µH 500mA",     "Indutor",     "G1-P1",   "1.650",    "300",   "5.000", "un", "Bourns",     "22/05/2026", "24/05/2026", "OK"),
]

STATUS_COLORS = {
    "OK":      "#4caf78",
    "CRÍTICO": "#e05252",
    "BAIXO":   "#e0a952",
}


class InventoryTable(QTableWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(len(SAMPLE_ROWS), len(COLUMNS), parent)
        self.setObjectName("inventoryTable")

        # Headers
        self.setHorizontalHeaderLabels([c[0] for c in COLUMNS])
        for i, (_, width) in enumerate(COLUMNS):
            self.setColumnWidth(i, width)

        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(28)

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setShowGrid(True)
        self.setSortingEnabled(True)

        self._populate()

    def _populate(self):
        for row_idx, row_data in enumerate(SAMPLE_ROWS):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)

                # Right-align numeric columns
                if col_idx in (4, 5, 6):
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)

                # Colour the Status column
                if col_idx == 11:
                    color = STATUS_COLORS.get(value, "#d4d4d4")
                    item.setForeground(QColor(color))
                    item.setFont(QFont("Segoe UI", 10, QFont.Bold))
                    item.setTextAlignment(Qt.AlignCenter)

                self.setItem(row_idx, col_idx, item)


# ---------------------------------------------------------------------------
# Content area (KPI bar + filter bar + table)
# ---------------------------------------------------------------------------
class ContentArea(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("contentArea")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Page header
        header = QFrame()
        header.setObjectName("pageHeader")
        header.setFixedHeight(44)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 0, 16, 0)

        page_title = QLabel(LANGUAGES[current_language].get("comps_status_title"),)
        page_title.setObjectName("pageTitle")
        page_title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        header_layout.addWidget(page_title)

        header_layout.addStretch()

        breadcrumb = QLabel("DELETAR!!!! PCBStock  ›  Estoque  ›  InventárioDELETAR!!!! ")
        breadcrumb.setObjectName("breadcrumb")
        breadcrumb.setFont(QFont("Segoe UI", 10))
        header_layout.addWidget(breadcrumb)

        layout.addWidget(header)

        # layout.addWidget(KpiBar())
        layout.addWidget(FilterBar())
        layout.addWidget(InventoryTable(), stretch=1)

# ---------------------------------------------------------------------------
# Title bar
# ---------------------------------------------------------------------------
class TitleBar(QFrame):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("titleBar")
        self.setFixedHeight(36)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 12, 0)
        layout.setSpacing(0)

        # Left spacer matching sidebar width
        spacer = QWidget()
        layout.addWidget(spacer)

        for label in (
            LANGUAGES[current_language].get("file_menu_bar_button"),
            LANGUAGES[current_language].get("edit_menu_bar_button"),
            LANGUAGES[current_language].get("show_menu_bar_button"),
            LANGUAGES[current_language].get("tools_menu_bar_button"),
            LANGUAGES[current_language].get("help_menu_bar_button")
        ):
            btn = QPushButton(label)
            btn.setObjectName("menuBarButton")
            btn.setFont(QFont("Segoe UI", 11))
            btn.setFixedHeight(36)
            layout.addWidget(btn)

        layout.addStretch()

# ---------------------------------------------------------------------------
# Main toolbar  (sits above sidebar + content, full width)
# ---------------------------------------------------------------------------
def _build_toolbar() -> MainToolbar:
    toolbar = MainToolbar()

    stock_group = toolbar.add_group(LANGUAGES[current_language].get("stock_subgroup"))
    stock_group.add_button("📦", LANGUAGES[current_language].get("new_item_button"))
    stock_group.add_button("📥", LANGUAGES[current_language].get("receivement_button"))
    stock_group.add_button("📤", LANGUAGES[current_language].get("shipment_button"))
    stock_group.add_button("🔄", LANGUAGES[current_language].get("adjustments_button"))

    orders_group = toolbar.add_group(LANGUAGES[current_language].get("orders_subgroup"))
    orders_group.add_button("📋", LANGUAGES[current_language].get("register_order_button"))
    orders_group.add_button("🧩", LANGUAGES[current_language].get("order_viability_button"))
    orders_group.add_button("✅", LANGUAGES[current_language].get("aprove_button"))

    receiving_group = toolbar.add_group(LANGUAGES[current_language].get("entrance_subgroup"))
    receiving_group.add_button("🔍", LANGUAGES[current_language].get("inspect_button"))
    receiving_group.add_button("📑", LANGUAGES[current_language].get("invoice_button"))

    reports_group = toolbar.add_group(LANGUAGES[current_language].get("reports_subgroup"))
    reports_group.add_button("📊", LANGUAGES[current_language].get("stock_button"))
    reports_group.add_button("📈", LANGUAGES[current_language].get("movement_button"))
    reports_group.add_button("💾", LANGUAGES[current_language].get("export_button"))

    toolbar.add_stretch()

    config_group = toolbar.add_group(LANGUAGES[current_language].get("system_subgroup"))
    config_group.add_button("⚙️", LANGUAGES[current_language].get("config_button"))
    config_group.add_button("🌙", LANGUAGES[current_language].get("theme_button"))

    return toolbar


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------
class MainScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(LANGUAGES[current_language].get("app_title"))
        self.resize(1280, 800)
        self.setStyleSheet(build_stylesheet(_THEME))

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(0)

        root.addWidget(TitleBar())
        root.addWidget(_build_toolbar())

        body = QSplitter(Qt.Horizontal)
        body.setObjectName("bodySplitter")
        body.setHandleWidth(1)
        body.setChildrenCollapsible(False)

        body.addWidget(ContentArea())
        body.setSizes([190, 1090])

        root.addWidget(body, stretch=1)
