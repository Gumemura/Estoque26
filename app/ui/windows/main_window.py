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
from app.ui.windows.new_product_window import NewProductWindow
from app.shared.dict.pt_br import STRINGS as PT_BR

LANGUAGES = {
    "pt_BR": PT_BR
}

_THEME = DARK
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
            LANGUAGES[current_language].get("inactives_filter_bar"),
        ):
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
    ("RES-0402-10K",   "Resistor SMD 0402 10kΩ 1%",           "Resistor",   "A1-P3",  "48.200", "10.000", "100.000", "un", "Digi-Key",    "23/05/2026", "24/05/2026", "OK"),
    ("CAP-0805-100N",  "Capacitor Cerâmico 100nF 50V",         "Capacitor",  "A2-P1",   "3.400",  "5.000",  "50.000", "un", "Mouser",      "20/05/2026", "24/05/2026", "CRÍTICO"),
    ("IC-STM32F103",   "MCU STM32F103C8T6 ARM Cortex-M3",      "CI",         "B1-P2",     "120",     "50",     "500", "un", "STMicro",     "18/05/2026", "22/05/2026", "OK"),
    ("CONN-JST-2P",    "Conector JST-XH 2 Pinos",              "Conector",   "C3-P1",   "2.100",    "500",   "5.000", "un", "Würth",       "21/05/2026", "23/05/2026", "OK"),
    ("RES-0402-100R",  "Resistor SMD 0402 100Ω 1%",            "Resistor",   "A1-P4",  "62.000", "10.000", "100.000", "un", "Digi-Key",    "23/05/2026", "23/05/2026", "OK"),
    ("LED-0603-GRN",   "LED SMD 0603 Verde 520nm",             "LED",        "D2-P2",   "8.900",  "2.000",  "20.000", "un", "Lumex",       "17/05/2026", "24/05/2026", "OK"),
    ("IC-LM358",       "Op-Amp LM358 DIP-8",                   "CI",         "B2-P1",     "340",    "100",   "1.000", "un", "TI",          "15/05/2026", "20/05/2026", "OK"),
    ("CAP-0402-10N",   "Capacitor Cerâmico 10nF 25V",          "Capacitor",  "A2-P3",   "1.200",  "5.000",  "40.000", "un", "Mouser",      "10/05/2026", "24/05/2026", "CRÍTICO"),
    ("XTAL-16MHZ",     "Cristal Oscilador 16MHz HC-49S",       "Passivo",    "E1-P1",     "890",    "200",   "2.000", "un", "TXC",         "12/05/2026", "21/05/2026", "OK"),
    ("IC-ESP32-WROOM", "Módulo ESP32-WROOM-32 4MB",            "Módulo",     "B3-P1",      "74",     "50",     "300", "un", "Espressif",   "19/05/2026", "23/05/2026", "OK"),
    ("FUSE-1A-SMD",    "Fusível SMD 1206 1A 125V",             "Proteção",   "F1-P2",     "430",    "500",   "3.000", "un", "Littelfuse",  "08/05/2026", "22/05/2026", "CRÍTICO"),
    ("IND-0805-10UH",  "Indutor SMD 0805 10µH 500mA",          "Indutor",    "G1-P1",   "1.650",    "300",   "5.000", "un", "Bourns",      "22/05/2026", "24/05/2026", "OK"),
    ("IND-0805-47UH",  "Indutor SMD 0805 47µH 300mA",          "Indutor",    "G1-P2",     "980",    "200",   "3.000", "un", "Bourns",      "20/05/2026", "23/05/2026", "OK"),
    ("IND-1210-100UH", "Indutor SMD 1210 100µH 200mA",         "Indutor",    "G2-P1",     "560",    "200",   "2.000", "un", "Würth",       "14/05/2026", "21/05/2026", "OK"),
    ("RES-0603-1K",    "Resistor SMD 0603 1kΩ 1%",             "Resistor",   "A1-P5",  "33.500", "10.000",  "80.000", "un", "Digi-Key",    "22/05/2026", "24/05/2026", "OK"),
    ("RES-0603-4K7",   "Resistor SMD 0603 4,7kΩ 5%",           "Resistor",   "A1-P6",  "21.000", "10.000",  "80.000", "un", "Digi-Key",    "22/05/2026", "22/05/2026", "OK"),
    ("RES-0805-0R",    "Resistor SMD 0805 0Ω (jumper)",        "Resistor",   "A2-P1",   "4.300",  "2.000",  "20.000", "un", "Yageo",       "11/05/2026", "19/05/2026", "OK"),
    ("CAP-0402-100N",  "Capacitor Cerâmico 0402 100nF 10V",    "Capacitor",  "A3-P1",   "9.800",  "5.000",  "60.000", "un", "Mouser",      "21/05/2026", "24/05/2026", "OK"),
    ("CAP-1210-100U",  "Capacitor Eletrolítico 100µF 25V",     "Capacitor",  "A3-P3",     "720",    "300",   "3.000", "un", "Panasonic",   "09/05/2026", "20/05/2026", "OK"),
    ("CAP-0805-1U",    "Capacitor Cerâmico 0805 1µF 50V",      "Capacitor",  "A3-P2",   "5.100",  "2.000",  "30.000", "un", "TDK",         "18/05/2026", "23/05/2026", "OK"),
    ("IC-NE555",       "Temporizador NE555 DIP-8",             "CI",         "B2-P2",     "215",    "100",   "1.000", "un", "TI",          "13/05/2026", "18/05/2026", "OK"),
    ("IC-74HC595",     "Shift Register 74HC595 SOP-16",        "CI",         "B2-P3",     "180",     "50",     "500", "un", "Nexperia",    "16/05/2026", "22/05/2026", "OK"),
    ("IC-AMS1117-3V3", "Regulador LDO AMS1117 3.3V SOT-223",  "CI",         "B3-P2",     "390",    "100",   "1.500", "un", "AMS",         "17/05/2026", "23/05/2026", "OK"),
    ("TRANS-BC547",    "Transistor NPN BC547 TO-92",           "CI",         "B4-P1",   "1.200",    "500",   "5.000", "un", "Fairchild",   "07/05/2026", "17/05/2026", "OK"),
    ("DIODE-1N4148",   "Diodo Rápido 1N4148 DO-35",           "CI",         "B4-P2",   "3.800",  "1.000",   "8.000", "un", "Vishay",      "05/05/2026", "21/05/2026", "OK"),
    ("DIODE-SS34",     "Diodo Schottky SS34 DO-214AC",        "CI",         "B4-P3",     "640",    "300",   "3.000", "un", "Digi-Key",    "14/05/2026", "20/05/2026", "OK"),
    ("LED-0603-RED",   "LED SMD 0603 Vermelho 630nm",         "LED",        "D2-P1",   "7.200",  "2.000",  "20.000", "un", "Lumex",       "17/05/2026", "24/05/2026", "OK"),
    ("LED-0603-BLU",   "LED SMD 0603 Azul 470nm",            "LED",        "D2-P3",   "4.100",  "2.000",  "20.000", "un", "Lumex",       "17/05/2026", "22/05/2026", "OK"),
    ("CONN-USB-C",     "Conector USB-C SMD 16 Pinos",        "Conector",   "C1-P1",     "310",    "100",   "1.000", "un", "Würth",       "19/05/2026", "23/05/2026", "OK"),
    ("CONN-HDR-10P",   "Pin Header 2.54mm 10 Pinos Macho",   "Conector",   "C2-P1",   "1.480",    "500",   "5.000", "un", "Samtec",      "11/05/2026", "18/05/2026", "OK"),
    ("CONN-RJ45",      "Conector RJ45 com LED integrado",    "Conector",   "C4-P1",     "165",     "50",     "500", "un", "Bel Fuse",    "06/05/2026", "15/05/2026", "OK"),
    ("FUSE-500MA-SMD", "Fusível SMD 1206 500mA 125V",        "Proteção",   "F1-P1",     "290",    "500",   "3.000", "un", "Littelfuse",  "08/05/2026", "20/05/2026", "CRÍTICO"),
    ("TVS-5V-SMD",     "Diodo TVS Unidirecional 5V SOD-123", "Proteção",   "F2-P1",     "870",    "300",   "3.000", "un", "Vishay",      "13/05/2026", "21/05/2026", "OK"),
    ("XTAL-8MHZ",      "Cristal Oscilador 8MHz HC-49S",      "Passivo",    "E1-P2",     "430",    "100",   "1.000", "un", "TXC",         "10/05/2026", "19/05/2026", "OK"),
    ("IC-W25Q128",     "Flash SPI 128Mb SOIC-8",             "CI",         "B1-P3",      "88",     "30",     "300", "un", "Winbond",     "16/05/2026", "22/05/2026", "OK"),
    ("IC-MCP2515",     "Controlador CAN SPI DIP-18",         "CI",         "B2-P4",      "52",     "20",     "200", "un", "Microchip",   "04/05/2026", "14/05/2026", "BAIXO"),
    ("MOD-SIM800L",    "Módulo GSM/GPRS SIM800L",            "Módulo",     "B3-P3",      "18",     "10",     "100", "un", "AI-Thinker",  "02/05/2026", "12/05/2026", "BAIXO"),
    ("MOD-PN532",      "Módulo NFC/RFID PN532",              "Módulo",     "B3-P4",      "24",     "10",     "100", "un", "Elechouse",   "01/05/2026", "10/05/2026", "BAIXO"),
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

                if col_idx in (4, 5, 6):
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)

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

        page_title = QLabel(LANGUAGES[current_language].get("comps_status_title"))
        page_title.setObjectName("pageTitle")
        page_title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        header_layout.addWidget(page_title)

        header_layout.addStretch()

        layout.addWidget(header)

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

        spacer = QWidget()
        layout.addWidget(spacer)

        for label in (
            LANGUAGES[current_language].get("file_menu_bar_button"),
            LANGUAGES[current_language].get("edit_menu_bar_button"),
            LANGUAGES[current_language].get("show_menu_bar_button"),
            LANGUAGES[current_language].get("tools_menu_bar_button"),
            LANGUAGES[current_language].get("help_menu_bar_button"),
        ):
            btn = QPushButton(label)
            btn.setObjectName("menuBarButton")
            btn.setFont(QFont("Segoe UI", 11))
            btn.setFixedHeight(36)
            layout.addWidget(btn)

        layout.addStretch()


# ---------------------------------------------------------------------------
# Main toolbar builder — returns toolbar + named button references
# ---------------------------------------------------------------------------
class _ToolbarButtons:
    """Holds named references to toolbar buttons for signal wiring."""
    new_item: ActionButton


def _build_toolbar() -> tuple[MainToolbar, _ToolbarButtons]:
    toolbar = MainToolbar()
    refs = _ToolbarButtons()

    stock_group = toolbar.add_group(LANGUAGES[current_language].get("stock_subgroup"))
    refs.new_item = stock_group.add_button("📦", LANGUAGES[current_language].get("new_item_button"))
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

    return toolbar, refs


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

        toolbar, btn_refs = _build_toolbar()
        root.addWidget(toolbar)

        # Wire toolbar buttons
        btn_refs.new_item.clicked.connect(self._open_new_product_dialog)

        body = QSplitter(Qt.Horizontal)
        body.setObjectName("bodySplitter")
        body.setHandleWidth(1)
        body.setChildrenCollapsible(False)

        body.addWidget(ContentArea())
        body.setSizes([190, 1090])

        root.addWidget(body, stretch=1)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------
    def _open_new_product_dialog(self):
        dialog = NewProductWindow(parent=self)
        dialog.exec()