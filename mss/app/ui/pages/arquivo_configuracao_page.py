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

class ArquivoConfiguracaoPage(QWidget):
    abrir_trocar_arquivo_configuracao = Signal()
    abrir_editar_arquivo_configuracao = Signal()
    abrir_criar_arquivo_configuracao = Signal()

    def __init__(self):
        super().__init__()
        self._page_montada = False

    def montar_tela(self):
        if self._page_montada:
            return
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        nome_objeto = "ArquivoConfiguracaoPage"
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

        titulo = QLabel("Ferramentas: Arquivo Configuração")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_trocar_configuracao = QPushButton("Trocar Arquivo Configuracao")
        btn_editar_configuracao = QPushButton("Editar Arquivo Configuracao")
        btn_criar_configuracao = QPushButton("Criar Arquivo Configuracao")

        btn_trocar_configuracao.clicked.connect(self.abrir_trocar_arquivo_configuracao.emit)
        btn_editar_configuracao.clicked.connect(self.abrir_editar_arquivo_configuracao.emit)
        btn_criar_configuracao.clicked.connect(self.abrir_criar_arquivo_configuracao.emit)

        for botao in [
            btn_trocar_configuracao,
            btn_editar_configuracao,
            btn_criar_configuracao,
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

        layout.addWidget(btn_trocar_configuracao)
        layout.addWidget(btn_editar_configuracao)
        layout.addWidget(btn_criar_configuracao)

        layout.addStretch()

        self.setLayout(layout)

        self._page_montada = True