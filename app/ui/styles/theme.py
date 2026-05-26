from dataclasses import dataclass


@dataclass(frozen=True)
class ColorScheme:
    bg_primary: str    # main window / grid background
    bg_secondary: str  # ribbon, formula bar, panels
    bg_input: str      # text inputs, address box
    bg_header: str     # row/column headers
    bg_title: str      # title bar, tab bar, status bar
    bg_title_dark: str # darker variant for title bar borders/hover

    accent: str        # active tab text, fx label, selected headers
    accent_dark: str   # title bar base (darker green)

    text_primary: str
    text_muted: str    # ribbon group labels, status labels
    text_on_accent: str  # text on green backgrounds

    border: str
    selection_bg: str  # selected cell background
    selection_fg: str  # selected cell text

    ribbon_btn_hover_bg: str
    ribbon_btn_hover_border: str
    ribbon_btn_pressed_bg: str

    sheet_tab_hover_bg: str
    sheet_tab_hover_fg: str

    scrollbar_track: str
    scrollbar_handle: str
    scrollbar_handle_hover: str


DARK = ColorScheme(
    ##REFAZER!!
    bg_primary="#1e1e1e",
    bg_secondary="#252526",
    bg_input="#3c3c3c",
    bg_header="#2d2d2d",
    bg_title="#1a3d2b",
    bg_title_dark="#14301f",

    accent="#4caf78",
    accent_dark="#1a5c38",

    text_primary="#d4d4d4",
    text_muted="#6a6a6a",
    text_on_accent="#c8e6c9",

    border="#3a3a3a",
    selection_bg="#1e4d33",
    selection_fg="#d4d4d4",

    ribbon_btn_hover_bg="#2d4a38",
    ribbon_btn_hover_border="#3d6b4f",
    ribbon_btn_pressed_bg="#1e3d2b",

    sheet_tab_hover_bg="#2d4a38",
    sheet_tab_hover_fg="#c8e6c9",

    scrollbar_track="#252526",
    scrollbar_handle="#4a4a4a",
    scrollbar_handle_hover="#5a5a5a",
)

LIGHT = ColorScheme(
    bg_primary="#f3f3f3",
    bg_secondary="#f3f3f3",
    bg_input="#ffffff",
    bg_header="#f3f3f3",
    bg_title="#b1b1b1",
    bg_title_dark="#1a5c38",

    accent="#217346",
    accent_dark="#1a5c38",

    text_primary="#1f1f1f",
    text_muted="#666666",
    text_on_accent="#ffffff",

    border="#d1d1d1",
    selection_bg="#b8d4e8",
    selection_fg="#000000",

    ribbon_btn_hover_bg="#e2edf4",
    ribbon_btn_hover_border="#bdd5e8",
    ribbon_btn_pressed_bg="#c9dcea",

    sheet_tab_hover_bg="#e0ece5",
    sheet_tab_hover_fg="#1f1f1f",

    scrollbar_track="#e8e8e8",
    scrollbar_handle="#b0b0b0",
    scrollbar_handle_hover="#909090",
)


def build_stylesheet(scheme: ColorScheme) -> str:
    return f"""
QWidget {{
    color: {scheme.text_primary};
    font-family: "Segoe UI", sans-serif;
}}

QSplitter::handle {{
    background-color: {scheme.border};
    width: 1px;
}}

/* ── Title bar ── */
#titleBar {{
    background-color: {scheme.bg_title};
}}
#menuBarButton {{
    background: transparent;
    color: {scheme.text_muted};
    border: none;
    padding: 0 12px;
    font-size: 11px;
}}
#menuBarButton:hover {{
    background-color: {scheme.ribbon_btn_hover_bg};
    color: {scheme.text_primary};
}}

/* ── Main toolbar ── */
#mainToolbar {{
    background-color: {scheme.bg_secondary};
}}
#toolbarGroup {{
    background-color: transparent;
    border: 1px solid {scheme.border};
    border-radius: 6px;
    padding-right: 8px;
    margin-right: 8px;
    margin-top: 8px;
}}
#toolbarGroupLabel {{
    color: {scheme.text_muted};
    font-size: 9px;
    letter-spacing: 0.5px;
}}
#actionButton {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
}}
#actionButton:hover {{
    background-color: {scheme.ribbon_btn_hover_bg};
    border: 1px solid {scheme.ribbon_btn_hover_border};
}}
#actionButton:pressed {{
    background-color: {scheme.ribbon_btn_pressed_bg};
}}
#actionButtonIcon {{
    color: {scheme.accent};
}}
#actionButtonLabel {{
    color: {scheme.text_primary};
    font-size: 9px;
}}

/* ── Content area ── */
#contentArea {{
    background-color: {scheme.bg_primary};
}}
#pageHeader {{
    background-color: {scheme.bg_secondary};
}}
#pageTitle {{
    color: {scheme.text_primary};
}}
#breadcrumb {{
    color: {scheme.text_muted};
}}

/* ── Filter bar ── */
#filterBar {{
    background-color: {scheme.bg_secondary};
}}
#searchInput {{
    background-color: {scheme.bg_input};
    color: {scheme.text_primary};
    border: 1px solid {scheme.border};
    border-radius: 3px;
    padding: 0 6px;
    font-size: 11px;
}}
#searchInput:focus {{
    border: 1px solid {scheme.accent};
}}
#filterChip {{
    background-color: transparent;
    color: {scheme.text_muted};
    border: 1px solid {scheme.border};
    border-radius: 10px;
    padding: 0 10px;
    font-size: 10px;
}}
#filterChip:hover {{
    background-color: {scheme.ribbon_btn_hover_bg};
    color: {scheme.text_primary};
}}
#filterChipActive {{
    background-color: {scheme.accent_dark};
    color: {scheme.text_on_accent};
    border: 1px solid {scheme.accent_dark};
    border-radius: 10px;
    padding: 0 10px;
    font-size: 10px;
}}

/* ── Inventory table ── */
#inventoryTable {{
    background-color: {scheme.bg_primary};
    alternate-background-color: {scheme.bg_secondary};
    gridline-color: {scheme.border};
    border: 1px solid {scheme.border};
    selection-background-color: {scheme.selection_bg};
    selection-color: {scheme.selection_fg};
    font-size: 12px;
    color: {scheme.text_primary};
}}
#inventoryTable QHeaderView::section {{
    background-color: {scheme.bg_header};
    border: none;
    border-right: 1px solid {scheme.border};
    border-bottom: 1px solid {scheme.border};
    padding: 0 6px;
    font-size: 10px;
    font-weight: 700;
    color: {scheme.text_muted};
    letter-spacing: 0.4px;
    text-transform: uppercase;
}}
#inventoryTable QHeaderView::section:hover {{
    background-color: {scheme.ribbon_btn_hover_bg};
    color: {scheme.text_primary};
}}
#inventoryTable QScrollBar:vertical {{
    background-color: {scheme.scrollbar_track};
    width: 10px;
    border: none;
}}
#inventoryTable QScrollBar::handle:vertical {{
    background-color: {scheme.scrollbar_handle};
    border-radius: 5px;
    min-height: 20px;
    margin: 1px;
}}
#inventoryTable QScrollBar::handle:vertical:hover {{
    background-color: {scheme.scrollbar_handle_hover};
}}
#inventoryTable QScrollBar::add-line:vertical,
#inventoryTable QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""