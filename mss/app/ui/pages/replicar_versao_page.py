from PySide6.QtCore import Signal
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QComboBox,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QHBoxLayout,
    QSizePolicy,
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

class ReplicarVersaoPage(QWidget):
    iniciar_replicar_versao = Signal()

    def __init__(self, connections=None):
        super().__init__()
        self.connections_dict = {}
        self.connections = connections
        self._page_montada = False

    def montar_tela(self):

        if self._page_montada:
            return

        self.setObjectName("ReplicarVersaoPage")

        titulo = QLabel("Replicar Versões")
        titulo.setObjectName("pageTitle")

        descricao = QLabel("Selecione o servidor para executar a rotina.")
        descricao.setObjectName("pageDescription")

        # Campo select
        self.combo_servidor = QComboBox()
        self.combo_servidor.addItem("Selecione um servidor")
        if len(self.connections) > 0:
            for servidor in self.connections:
                self.combo_servidor.addItem(servidor.name)
                self.connections_dict[servidor.name] = servidor

        # Faz o combo ocupar o espaço horizontal disponível
        self.combo_servidor.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        # Campo de saída somente leitura
        self.output_saida = QTextEdit()
        self.output_saida.setReadOnly(True)
        self.output_saida.setPlaceholderText("A saída da rotina será exibida aqui...")

        btn_executar = QPushButton("Executar")
        btn_limpar_saida = QPushButton("Limpar saída")

        btn_executar.clicked.connect(self.executar_rotina)
        btn_limpar_saida.clicked.connect(self.output_saida.clear)

        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(12)

        form_layout.addWidget(QLabel("Servidor"), 0, 0)
        form_layout.addWidget(self.combo_servidor, 0, 1)

        botoes_layout = QHBoxLayout()
        botoes_layout.addStretch()
        botoes_layout.addWidget(btn_limpar_saida)
        botoes_layout.addWidget(btn_executar)

        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        layout.addWidget(titulo)
        layout.addWidget(descricao)
        layout.addSpacing(12)
        layout.addLayout(form_layout)

        layout.addSpacing(16)
        layout.addWidget(QLabel("Saída"))
        layout.addWidget(self.output_saida)

        layout.addLayout(botoes_layout)

        self.setLayout(layout)

        self._page_montada = True

    def executar_rotina(self):
        servidor = self.combo_servidor.currentText()

        self.output_saida.append("Iniciando rotina...")
        self.output_saida.append(f"Servidor selecionado: {servidor}")
        self.output_saida.append("Processamento finalizado.")

    def atualizar_elementos(self):
        if len(self.connections) > 0:
            self.combo_servidor.clear()
            for servidor in self.connections:
                self.combo_servidor.addItem(servidor.name)
                self.connections_dict[servidor.name] = servidor

    def aplicar_settings(self, settings):
        self.settings = settings
        self.connections = settings.connections
        self.wall_databases = settings.wall_databases

        if not self._page_montada:
            self.montar_tela()

        self.atualizar_elementos()