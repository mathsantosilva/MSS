from PySide6.QtCore import Signal
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QSizePolicy
)
from app.core.constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_MIN_HEIGHT,
    SPACING,
    MARGIN_TOP,
    MARGIN_BOTTOM,
    MARGIN_LEFT,
    MARGIN_RIGHT,
    COLOR_BTN,
    COLOR_BTN_HOVER,
    COLOR_BTN_PRESSED,
    COLOR_TITLE,
    COLOR_FONT_BTN,
)

class DocumentosPage(QWidget):
    abrir_gerador_documentos = Signal()
    abrir_validador_documentos = Signal()

    def __init__(self):
        super().__init__()
        self._page_montada = False

    def montar_tela(self):

        if self._page_montada:
            return

        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        nome_objeto = "DocumentosPage"
        self.setObjectName(nome_objeto)
        self.setStyleSheet(f"""
            QWidget#{nome_objeto} {{
                background-color: white;
            }}

            QLabel#titulo {{
                color: {COLOR_TITLE};
                font-size: 28px;
                font-weight: bold;
            }}

            QPushButton {{
                background-color: {COLOR_BTN};
                color: {COLOR_FONT_BTN};
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 15px;
            }}

            QPushButton:hover {{
                background-color: {COLOR_BTN_HOVER};
            }}

            QPushButton:pressed {{
                background-color: {COLOR_BTN_PRESSED};
            }}
        """)

        titulo = QLabel("Ferramentas: Documentos")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_gerador_documentos = QPushButton("Gerador de documentos")
        btn_validador_documentos = QPushButton("Validador de documentos")

        btn_gerador_documentos.clicked.connect(self.abrir_gerador_documentos.emit)
        btn_validador_documentos.clicked.connect(self.abrir_validador_documentos.emit)

        for botao in [
            btn_gerador_documentos,
            btn_validador_documentos,
        ]:
            botao.setMinimumHeight(WINDOW_MIN_HEIGHT)
            botao.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed
            )

        layout = QVBoxLayout()
        layout.setContentsMargins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT, MARGIN_BOTTOM)
        layout.setSpacing(SPACING)

        layout.addWidget(titulo)
        layout.addSpacing(SPACING)

        layout.addWidget(btn_gerador_documentos)
        layout.addWidget(btn_validador_documentos)

        layout.addStretch()

        self.setLayout(layout)

        self._page_montada = True