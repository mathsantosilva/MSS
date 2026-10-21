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
    WINDOW_TITLE,
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


class BancoMuroPage(QWidget):
    abrir_buscar_bancos = Signal()
    abrir_consultar_versao = Signal()
    abrir_replicar_versao = Signal()

    def __init__(self):
        super().__init__()
        self._page_montada = False

    def montar_tela(self):

        if self._page_montada:
            return

        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        nome_objeto = "BancoMuroPage"
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

        titulo = QLabel("Ferramentas: Banco de muro")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_buscar_bancos = QPushButton("Buscar bancos")
        btn_consultar_versao = QPushButton("Consultar Versão")
        btn_replicar_versao = QPushButton("Replicar Versão")

        btn_buscar_bancos.clicked.connect(self.abrir_buscar_bancos.emit)
        btn_consultar_versao.clicked.connect(self.abrir_consultar_versao.emit)
        btn_replicar_versao.clicked.connect(self.abrir_replicar_versao.emit)

        for botao in [
            btn_buscar_bancos,
            btn_consultar_versao,
            btn_replicar_versao
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

        layout.addWidget(btn_buscar_bancos)
        layout.addWidget(btn_consultar_versao)
        layout.addWidget(btn_replicar_versao)

        layout.addStretch()

        self.setLayout(layout)

        self._page_montada = True