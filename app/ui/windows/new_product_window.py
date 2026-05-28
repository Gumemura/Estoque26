from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QFrame,
    QScrollArea,
    QWidget,
    QMessageBox,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from app.domain.services.product_service import CreateProductDto, DuplicateInternalCodeError, ProductService
from app.infrastructure.database.connection import SessionLocal
from app.infrastructure.database.repositories.product_repository import ProductRepository
from app.ui.styles.theme import build_stylesheet, LIGHT


# ---------------------------------------------------------------------------
# Predefined categories for dropdowns
# ---------------------------------------------------------------------------
PRIMARY_TYPES = [
    "Passivo",
    "Ativo",
    "Eletromecânico",
    "Módulo",
    "Proteção",
    "Conector",
    "Outro",
]

SECONDARY_TYPES_BY_PRIMARY: dict[str, list[str]] = {
    "Passivo":        ["Resistor", "Capacitor", "Indutor", "Cristal", "Transformador", "Outro"],
    "Ativo":          ["CI", "MCU", "FPGA", "Op-Amp", "Regulador", "Transistor", "Diodo", "LED", "Outro"],
    "Eletromecânico": ["Relé", "Chave", "Motor", "Buzzer", "Outro"],
    "Módulo":         ["Wi-Fi", "Bluetooth", "GPS", "Display", "Câmera", "Outro"],
    "Proteção":       ["Fusível", "TVS", "Varistor", "PTC", "Outro"],
    "Conector":       ["JST", "USB", "RJ45", "Pin Header", "Terminal Block", "Outro"],
    "Outro":          ["Outro"],
}


# ---------------------------------------------------------------------------
# Helper: labelled input row
# ---------------------------------------------------------------------------
def _make_field(label_text: str, placeholder: str = "", required: bool = False) -> tuple[QLabel, QLineEdit]:
    label = QLabel(label_text + (" *" if required else ""))
    label.setObjectName("fieldLabel")
    label.setFont(QFont("Segoe UI", 10))
    label.setFixedWidth(180)

    edit = QLineEdit()
    edit.setObjectName("fieldInput")
    edit.setPlaceholderText(placeholder)
    edit.setFont(QFont("Segoe UI", 11))
    edit.setFixedHeight(30)

    return label, edit


def _make_combo(label_text: str, items: list[str], required: bool = False) -> tuple[QLabel, QComboBox]:
    label = QLabel(label_text + (" *" if required else ""))
    label.setObjectName("fieldLabel")
    label.setFont(QFont("Segoe UI", 10))
    label.setFixedWidth(180)

    combo = QComboBox()
    combo.setObjectName("fieldCombo")
    combo.addItems(items)
    combo.setFont(QFont("Segoe UI", 11))
    combo.setFixedHeight(30)

    return label, combo


def _row(label: QLabel, widget: QWidget) -> QHBoxLayout:
    layout = QHBoxLayout()
    layout.setSpacing(10)
    layout.addWidget(label)
    layout.addWidget(widget, stretch=1)
    return layout


# ---------------------------------------------------------------------------
# New Product Dialog
# ---------------------------------------------------------------------------
class NewProductWindow(QDialog):
    product_saved = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Novo Produto")
        self.setModal(True)
        self.setMinimumWidth(560)
        self.setStyleSheet(build_stylesheet(LIGHT) + self._extra_styles())

        self._session = SessionLocal()
        self._service = ProductService(repository=ProductRepository(self._session))
        self._build_ui()

    def closeEvent(self, event):
        self._session.close()
        super().closeEvent(event)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Dialog header ──
        header = QFrame()
        header.setObjectName("dialogHeader")
        header.setFixedHeight(56)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        title = QLabel("📦  Novo Produto")
        title.setObjectName("dialogTitle")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeButton")
        close_btn.setFixedSize(28, 28)
        close_btn.clicked.connect(self.reject)
        header_layout.addWidget(close_btn)

        root.addWidget(header)

        # ── Divider ──
        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFixedHeight(1)
        root.addWidget(divider)

        # ── Scrollable form ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setObjectName("formScroll")

        form_container = QWidget()
        form_container.setObjectName("formContainer")
        form = QVBoxLayout(form_container)
        form.setContentsMargins(24, 20, 24, 20)
        form.setSpacing(14)

        # Section: Identification
        form.addWidget(self._section_label("Identificação"))

        lbl, self._internal_code = _make_field("Código Interno", "ex: RES-0402-10K", required=True)
        form.addLayout(_row(lbl, self._internal_code))

        lbl, self._mpn = _make_field("Part Number (MPN)", "ex: RC0402FR-0710KL", required=True)
        form.addLayout(_row(lbl, self._mpn))

        lbl, self._external_code = _make_field("Código Externo", "ex: SKU do fornecedor")
        form.addLayout(_row(lbl, self._external_code))

        lbl, self._barcode = _make_field("Código de Barras", "EAN / QR / DataMatrix", required=True)
        form.addLayout(_row(lbl, self._barcode))

        form.addWidget(self._section_label("Descrição"))

        lbl, self._description = _make_field("Descrição", "ex: Resistor SMD 0402 10kΩ 1%")
        form.addLayout(_row(lbl, self._description))

        lbl, self._supplier = _make_field("Fornecedor", "ex: Digi-Key")
        form.addLayout(_row(lbl, self._supplier))

        lbl, self._stock_location = _make_field("Localização", "ex: A1-P3")
        form.addLayout(_row(lbl, self._stock_location))

        form.addWidget(self._section_label("Classificação"))

        lbl, self._primary_type = _make_combo("Tipo Primário", PRIMARY_TYPES, required=True)
        form.addLayout(_row(lbl, self._primary_type))

        lbl, self._secondary_type = _make_combo(
            "Tipo Secundário",
            SECONDARY_TYPES_BY_PRIMARY[PRIMARY_TYPES[0]],
            required=True,
        )
        form.addLayout(_row(lbl, self._secondary_type))

        # Update secondary type options when primary changes
        self._primary_type.currentTextChanged.connect(self._on_primary_type_changed)

        form.addStretch()
        scroll.setWidget(form_container)
        root.addWidget(scroll, stretch=1)

        # ── Footer ──
        footer = QFrame()
        footer.setObjectName("dialogFooter")
        footer.setFixedHeight(56)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 0, 20, 0)
        footer_layout.setSpacing(10)

        required_note = QLabel("* Campos obrigatórios")
        required_note.setObjectName("requiredNote")
        required_note.setFont(QFont("Segoe UI", 9))
        footer_layout.addWidget(required_note)
        footer_layout.addStretch()

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.setFixedSize(100, 34)
        cancel_btn.setFont(QFont("Segoe UI", 10))
        cancel_btn.clicked.connect(self.reject)
        footer_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Salvar")
        save_btn.setObjectName("saveButton")
        save_btn.setFixedSize(100, 34)
        save_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        save_btn.clicked.connect(self._on_save)
        footer_layout.addWidget(save_btn)

        root.addWidget(footer)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text.upper())
        lbl.setObjectName("sectionLabel")
        lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
        return lbl

    def _on_primary_type_changed(self, primary: str):
        options = SECONDARY_TYPES_BY_PRIMARY.get(primary, ["Outro"])
        self._secondary_type.clear()
        self._secondary_type.addItems(options)

    # ------------------------------------------------------------------
    # Save logic
    # ------------------------------------------------------------------
    def _on_save(self):
        internal_code = self._internal_code.text().strip()
        mpn = self._mpn.text().strip()
        barcode = self._barcode.text().strip()

        # Required field validation
        errors: list[str] = []
        if not internal_code:
            errors.append("Código Interno")
        if not mpn:
            errors.append("Part Number (MPN)")
        if not barcode:
            errors.append("Código de Barras")

        if errors:
            QMessageBox.warning(
                self,
                "Campos obrigatórios",
                "Preencha os campos obrigatórios:\n• " + "\n• ".join(errors),
            )
            return

        dto = CreateProductDto(
            manufacturer_part_number=mpn,
            internal_code=internal_code,
            external_code=self._external_code.text().strip() or None,
            description=self._description.text().strip() or None,
            image=None,
            supplier=self._supplier.text().strip() or None,
            primary_type=self._primary_type.currentText(),
            secondary_type=self._secondary_type.currentText(),
            barcode=barcode,
            stock_location=self._stock_location.text().strip() or None,
        )

        try:
            self._service.create_product(dto)
            self.product_saved.emit()
            QMessageBox.information(
                self,
                "Produto registrado",
                f"Produto '{internal_code}' salvo com sucesso.",
            )
            self.accept()

        except DuplicateInternalCodeError as exc:
            QMessageBox.critical(self, "Código duplicado", str(exc))

        except Exception as exc:
            QMessageBox.critical(
                self,
                "Erro ao salvar",
                f"Ocorreu um erro inesperado:\n{exc}",
            )

    # ------------------------------------------------------------------
    # Extra styles scoped to this dialog
    # ------------------------------------------------------------------
    @staticmethod
    def _extra_styles() -> str:
        return """
QDialog {
    background-color: #f8f8f8;
}
#dialogHeader {
    background-color: #ffffff;
    border-bottom: 1px solid #e0e0e0;
}
#dialogTitle {
    color: #1f1f1f;
}
#closeButton {
    background: transparent;
    border: none;
    color: #888888;
    font-size: 13px;
    border-radius: 4px;
}
#closeButton:hover {
    background-color: #f0f0f0;
    color: #333333;
}
#divider {
    background-color: #e8e8e8;
}
#formScroll {
    background-color: #f8f8f8;
}
#formContainer {
    background-color: #f8f8f8;
}
#sectionLabel {
    color: #217346;
    letter-spacing: 0.8px;
    margin-top: 4px;
    margin-bottom: 2px;
}
#fieldLabel {
    color: #444444;
}
#fieldInput {
    background-color: #ffffff;
    border: 1px solid #d1d1d1;
    border-radius: 4px;
    padding: 0 8px;
    color: #1f1f1f;
}
#fieldInput:focus {
    border: 1px solid #217346;
}
#fieldCombo {
    background-color: #ffffff;
    border: 1px solid #d1d1d1;
    border-radius: 4px;
    padding: 0 8px;
    color: #1f1f1f;
}
#fieldCombo:focus {
    border: 1px solid #217346;
}
#dialogFooter {
    background-color: #ffffff;
    border-top: 1px solid #e0e0e0;
}
#requiredNote {
    color: #999999;
}
#cancelButton {
    background-color: #f0f0f0;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    color: #444444;
}
#cancelButton:hover {
    background-color: #e4e4e4;
}
#saveButton {
    background-color: #217346;
    border: none;
    border-radius: 4px;
    color: #ffffff;
}
#saveButton:hover {
    background-color: #1a5c38;
}
#saveButton:pressed {
    background-color: #154d2f;
}
"""