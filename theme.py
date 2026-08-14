STYLE = """
* {
    font-family: "Inter", "Cantarell", "Noto Sans", "Segoe UI", sans-serif;
    font-size: 14px;
    outline: none;
}

QMainWindow {
    background: transparent;
}

QFrame#windowBody {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0A0D16, stop:1 #0F1524);
    border: 1px solid #1A2138;
    border-radius: 14px;
}

QWidget {
    background: transparent;
    color: #E8ECF6;
}

QLabel {
    color: #E8ECF6;
    background: transparent;
}

/* -------------------------------------------------------------- titlebar */

QWidget#titleBar {
    background: transparent;
}

QLabel#tbTitle {
    font-size: 13px;
    font-weight: 600;
    color: #8B97B0;
}

QPushButton#tbMin, QPushButton#tbMax, QPushButton#tbClose {
    background: transparent;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 700;
    color: #8B97B0;
    padding: 0;
}
QPushButton#tbMin:hover, QPushButton#tbMax:hover {
    background: #1A2238;
    color: #E8ECF6;
}
QPushButton#tbClose:hover {
    background: #EF4444;
    color: #FFFFFF;
}

/* ----------------------------------------------------------------- toast */

QFrame#toast {
    background: #151C31;
    border: 1px solid #2A3560;
    border-radius: 12px;
}

QLabel#toastMsg {
    color: #E8ECF6;
    font-size: 13px;
    font-weight: 600;
}

QLabel#toastIcon {
    font-size: 15px;
    font-weight: 800;
}

/* ---------------------------------------------------------------- splash */

QFrame#splashCard {
    background: #0C1120;
    border: 1px solid #1E2740;
    border-radius: 18px;
}

QLabel#splashTitle {
    font-size: 30px;
    font-weight: 800;
    color: #F1F5F9;
}

QLabel#splashStatus {
    font-size: 12px;
    color: #8B97B0;
}

QLabel#splashVersion {
    background: #141B2E;
    border: 1px solid #1E2740;
    border-radius: 999px;
    padding: 5px 14px;
    color: #8B97B0;
    font-size: 11px;
    font-weight: 700;
}

/* ---------------------------------------------------------- empty state */

QFrame#emptyState {
    background: #10162A;
    border: 1px solid #1E2740;
    border-radius: 14px;
}

QLabel#emptyIcon {
    font-size: 34px;
    font-weight: 700;
    color: #26304D;
}

QLabel#emptyTitle {
    font-size: 15px;
    font-weight: 700;
    color: #8B97B0;
}

QLabel#emptySub {
    font-size: 12px;
    color: #56647F;
}

/* ---------------------------------------------------------------- sidebar */

QFrame#sidebar {
    background: #0C1120;
    border-right: 1px solid #1A2138;
    border-top-left-radius: 13px;
    border-bottom-left-radius: 13px;
}

QFrame#logoBadge {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6D5EFC, stop:1 #8B5CF6);
    border-radius: 12px;
}

QLabel#logoBadgeText {
    font-size: 16px;
    font-weight: 800;
    color: #FFFFFF;
}

QLabel#logoTitle {
    font-size: 20px;
    font-weight: 800;
    color: #F1F5F9;
}

QLabel#logoSub {
    font-size: 10px;
    font-weight: 700;
    color: #56647F;
    letter-spacing: 3px;
}

QLabel#navSection {
    font-size: 11px;
    font-weight: 700;
    color: #56647F;
    padding: 0 6px 4px 6px;
}

QPushButton#navButton {
    background: transparent;
    border: none;
    border-radius: 12px;
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: 600;
    color: #8B97B0;
}
QPushButton#navButton:hover {
    background: #141B2E;
    color: #E8ECF6;
}
QPushButton#navButton:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6D5EFC, stop:1 #8B5CF6);
    color: #FFFFFF;
}
QPushButton#navButton:checked:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7A6BFD, stop:1 #9A6CF7);
}

QLabel#versionChip {
    background: #141B2E;
    border: 1px solid #1E2740;
    border-radius: 999px;
    padding: 6px 14px;
    color: #8B97B0;
    font-size: 11px;
    font-weight: 700;
}

QLabel#footerText {
    font-size: 11px;
    color: #56647F;
    line-height: 1.4;
}

/* ------------------------------------------------------------- page head */

QLabel#pageTitle {
    font-size: 26px;
    font-weight: 800;
    color: #F1F5F9;
}

QLabel#pageSub {
    font-size: 13px;
    color: #8B97B0;
}

QLabel#clock {
    font-size: 20px;
    font-weight: 800;
    color: #F1F5F9;
}

QLabel#dateLabel {
    font-size: 12px;
    color: #8B97B0;
}

/* ---------------------------------------------------------------- cards */

QFrame#statCard {
    background: #12192B;
    border: 1px solid #1E2740;
    border-radius: 16px;
}
QFrame#statCard:hover {
    border-color: #2E3B5E;
}

QLabel#statValue {
    font-size: 30px;
    font-weight: 800;
    color: #F1F5F9;
}

QLabel#statCaption {
    font-size: 12px;
    font-weight: 600;
    color: #8B97B0;
}

QFrame#actionCard {
    background: #12192B;
    border: 1px solid #1E2740;
    border-radius: 16px;
}

QLabel#cardTitle {
    font-size: 18px;
    font-weight: 700;
    color: #F1F5F9;
}

QLabel#cardSub {
    font-size: 13px;
    color: #8B97B0;
}

QLabel#cardChevron {
    font-size: 20px;
    font-weight: 700;
}

QLabel#panelTitle {
    font-size: 15px;
    font-weight: 700;
    color: #E8ECF6;
}

QLabel#windowTitle {
    font-size: 22px;
    font-weight: 700;
    color: #F1F5F9;
}

QLabel#subtitle, QLabel#status {
    font-size: 13px;
    color: #8B97B0;
}

QLabel#chip {
    background: #141B2E;
    border: 1px solid #26304D;
    border-radius: 999px;
    padding: 7px 18px;
    color: #A5B4FC;
    font-size: 12px;
    font-weight: 600;
}

QLabel#preview {
    background: #0D1322;
    border: 1px solid #1E2740;
    border-radius: 16px;
    color: #5B6478;
    font-size: 15px;
}

QFrame#divider {
    background: #1E2740;
    border: none;
    max-height: 1px;
}

QFrame#headerBar {
    background: transparent;
    border: none;
}

QLabel#appTitle {
    font-size: 26px;
    font-weight: 800;
    letter-spacing: 1px;
    color: #F1F5F9;
}

/* --------------------------------------------------------------- buttons */

QPushButton {
    background: #1A2238;
    color: #E8ECF6;
    border: 1px solid #26304D;
    border-radius: 12px;
    padding: 12px 20px;
    font-size: 14px;
    font-weight: 600;
}
QPushButton:hover {
    background: #202A45;
    border-color: #3D4B76;
    color: #FFFFFF;
}
QPushButton:pressed {
    background: #151C30;
}
QPushButton:disabled {
    background: #151C30;
    border-color: #20273F;
    color: #56647F;
}

QPushButton#menu {
    font-size: 17px;
    padding: 20px;
    border-radius: 14px;
    background: #171D38;
    border: 1px solid #26304D;
}

QPushButton#primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6D5EFC, stop:1 #8B5CF6);
    border: none;
    color: #FFFFFF;
    font-size: 16px;
    padding: 14px 24px;
}
QPushButton#primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7C6DFD, stop:1 #9A6CF7);
}
QPushButton#primary:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5C4DEE, stop:1 #7D4FE0);
}
QPushButton#primary:disabled {
    background: #262B47;
    color: #7B839C;
}

QPushButton#success {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10B981, stop:1 #14B8A6);
    border: none;
    color: #FFFFFF;
    font-size: 16px;
    padding: 14px 24px;
}
QPushButton#success:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #12C68A, stop:1 #17C4B0);
}
QPushButton#success:disabled {
    background: #262B47;
    color: #7B839C;
}

QPushButton#danger {
    background: #EF4444;
    border: none;
    color: #FFFFFF;
}
QPushButton#danger:hover {
    background: #F87171;
}
QPushButton#danger:disabled {
    background: #262B47;
    color: #7B839C;
}

QPushButton#ghost {
    background: transparent;
    border: 1px solid #26304D;
    color: #A5B4FC;
}
QPushButton#ghost:hover {
    background: #1A2238;
    border-color: #6366F1;
}

QPushButton#dangerGhost {
    background: transparent;
    border: 1px solid #7F2A33;
    color: #F87171;
}
QPushButton#dangerGhost:hover {
    background: #2A1620;
    border-color: #EF4444;
    color: #FCA5A5;
}
QPushButton#dangerGhost:disabled {
    background: transparent;
    border-color: #20273F;
    color: #56647F;
}

QPushButton#chip {
    background: #141B2E;
    border: 1px solid #26304D;
    border-radius: 999px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 600;
    color: #A5B4FC;
}
QPushButton#chip:hover {
    background: #1E2845;
    border-color: #6366F1;
    color: #FFFFFF;
}

/* --------------------------------------------------------------- inputs */

QLineEdit, QComboBox, QDateTimeEdit {
    background: #0F1524;
    color: #E8ECF6;
    border: 1px solid #26304D;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 14px;
    selection-background-color: #6D5EFC;
    selection-color: #FFFFFF;
}
QLineEdit:hover, QComboBox:hover, QDateTimeEdit:hover {
    border-color: #3D4B76;
}
QLineEdit:focus, QComboBox:focus, QDateTimeEdit:focus {
    border: 1px solid #7C6CF6;
}

QComboBox::drop-down, QDateTimeEdit::drop-down {
    border: none;
    width: 26px;
}
QComboBox::down-arrow, QDateTimeEdit::down-arrow {
    image: url(assets/arrow-down.png);
    width: 12px;
    height: 8px;
}
QComboBox QAbstractItemView {
    background: #12192B;
    border: 1px solid #26304D;
    border-radius: 10px;
    color: #E8ECF6;
    selection-background-color: #6D5EFC;
    selection-color: #FFFFFF;
    outline: 0;
    padding: 4px;
}

QCalendarWidget QWidget {
    background: #12192B;
    color: #E8ECF6;
}
QCalendarWidget QToolButton {
    background: #1A2238;
    border: none;
    border-radius: 6px;
    padding: 4px 10px;
    color: #E8ECF6;
    font-weight: 600;
}
QCalendarWidget QToolButton:hover {
    background: #26304D;
}
QCalendarWidget QMenu {
    background: #12192B;
    border: 1px solid #26304D;
}
QCalendarWidget QSpinBox {
    background: #1A2238;
    border: 1px solid #26304D;
    border-radius: 6px;
    color: #E8ECF6;
}
QCalendarWidget QAbstractItemView {
    background: #12192B;
    color: #E8ECF6;
    selection-background-color: #6D5EFC;
    selection-color: #FFFFFF;
    border: none;
}
QCalendarWidget QAbstractItemView:disabled {
    color: #56647F;
}

/* --------------------------------------------------------------- tables */

QTableWidget {
    background: #10162A;
    alternate-background-color: #141B31;
    color: #E8ECF6;
    border: 1px solid #1E2740;
    border-radius: 14px;
    gridline-color: transparent;
    selection-background-color: #2D3560;
    selection-color: #FFFFFF;
}
QTableWidget::item {
    padding: 6px 10px;
}
QHeaderView::section {
    background: #1A2238;
    color: #A5B4FC;
    font-weight: 700;
    font-size: 13px;
    padding: 10px 12px;
    border: none;
    border-bottom: 1px solid #1E2740;
}
QTableCornerButton::section {
    background: #1A2238;
    border: none;
}

QListWidget {
    background: #10162A;
    color: #E8ECF6;
    border: 1px solid #1E2740;
    border-radius: 14px;
    padding: 6px;
    outline: 0;
}
QListWidget::item {
    padding: 10px 12px;
    border-radius: 8px;
    color: #E8ECF6;
}
QListWidget::item:hover:!selected {
    background: #1A2238;
}
QListWidget::item:selected {
    background: #2D3560;
    color: #FFFFFF;
}

/* ------------------------------------------------------------ scrollbars */

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: #26304D;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #6366F1;
}
QScrollBar:horizontal {
    background: transparent;
    height: 10px;
    margin: 2px;
}
QScrollBar::handle:horizontal {
    background: #26304D;
    border-radius: 5px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background: #6366F1;
}
QScrollBar::add-line, QScrollBar::sub-line {
    width: 0;
    height: 0;
}
QScrollBar::add-page, QScrollBar::sub-page {
    background: transparent;
}

/* ---------------------------------------------------------------- misc */

QMessageBox {
    background: #10162A;
}
QMessageBox QLabel {
    color: #E8ECF6;
    font-size: 14px;
}
QMessageBox QPushButton {
    min-width: 90px;
    padding: 10px 18px;
}

QToolTip {
    background: #1A2238;
    color: #E8ECF6;
    border: 1px solid #26304D;
    border-radius: 6px;
    padding: 6px;
}
"""

from paths import ASSETS_DIR

ARROW = (ASSETS_DIR / "arrow-down.png").as_posix()
STYLE = STYLE.replace("url(assets/arrow-down.png)", f"url({ARROW})")
