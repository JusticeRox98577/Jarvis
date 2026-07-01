CYAN = "#28e0ff"
CYAN_DIM = "#0f6f85"
CYAN_GLOW = "#8ff7ff"
GRID_COLOR = "#0c2b36"
BG_DARK = "#020a12"
BG_PANEL = "#04141f"
AMBER = "#ff9c33"
GREEN = "#39ff8f"
TEXT = "#c8faff"

STYLESHEET = f"""
QWidget {{
    background-color: {BG_DARK};
    color: {TEXT};
    font-family: 'Consolas', 'Segoe UI';
}}
QTextEdit, QLineEdit {{
    background-color: {BG_PANEL};
    border: 1px solid {CYAN_DIM};
    border-radius: 4px;
    padding: 6px;
    color: {CYAN_GLOW};
    selection-background-color: {CYAN_DIM};
}}
QPushButton {{
    background-color: {BG_PANEL};
    border: 1px solid {CYAN};
    border-radius: 4px;
    color: {CYAN};
    padding: 6px 14px;
    font-weight: bold;
    letter-spacing: 1px;
}}
QPushButton:hover {{
    background-color: {CYAN_DIM};
    color: #ffffff;
}}
QPushButton:checked {{
    background-color: {CYAN};
    color: #001015;
}}
QPushButton:disabled {{
    color: {CYAN_DIM};
    border-color: {CYAN_DIM};
}}
QLabel#title {{
    color: {CYAN};
    font-size: 22px;
    font-weight: bold;
    letter-spacing: 6px;
}}
QLabel#clock {{
    color: {CYAN_GLOW};
    font-size: 16px;
    letter-spacing: 2px;
}}
QLabel#status {{
    color: {CYAN_GLOW};
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 4px;
}}
QLabel#panelHeader {{
    color: {CYAN_DIM};
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 3px;
}}
QScrollBar:vertical {{
    background: {BG_DARK};
    width: 8px;
}}
QScrollBar::handle:vertical {{
    background: {CYAN_DIM};
    border-radius: 4px;
}}
"""
