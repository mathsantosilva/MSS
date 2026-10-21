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

class LimparEspecificoRedisPage(QWidget):
    iniciar_limpar_especifico_redis = Signal()

    def __init__(self, redis_groups=None):
        super().__init__()
        self.redis_dict = {}
        self.redis_groups = redis_groups
        self._page_montada = False


    def montar_tela(self):

        if self._page_montada:
            return

        self.setObjectName("LimparEspecificoRedisPage")

        titulo = QLabel("Limpar redis especifico")
        titulo.setObjectName("pageTitle")

        descricao = QLabel("Selecione um grupo e redis para executar a rotina.")
        descricao.setObjectName("pageDescription")

        # Campo select grupo
        self.combo_grupo = QComboBox()
        self.combo_grupo.addItem("Selecione um Grupo")
        if self.redis_groups:
            for groups in self.redis_groups:
                self.combo_grupo.addItem(groups.name)

        # Campo select redis
        self.combo_redis = QComboBox()
        self.combo_redis.addItem("Selecione um Redis")
        if self.redis_groups:
            for groups in self.redis_groups:
                for instances in groups.instances:
                    self.combo_redis.addItem(instances.name)
                    self.redis_dict[instances.name] = instances

        # Faz o combo ocupar o espaço horizontal disponível
        self.combo_grupo.setSizePolicy(
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

        form_layout.addWidget(QLabel("Grupo"), 0, 0)
        form_layout.addWidget(self.combo_grupo, 0, 1)

        form_layout.addWidget(QLabel("Redis"), 1, 0)
        form_layout.addWidget(self.combo_redis, 1, 1)

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
        grupo = self.combo_grupo.currentText()
        redis = self.combo_redis.currentText()

        self.output_saida.append("Iniciando rotina...")
        self.output_saida.append(f"grupo selecionado: {grupo}")
        self.output_saida.append(f"redis selecionado: {redis}")
        self.output_saida.append("Processamento finalizado.")

    def atualizar_elementos(self):
        if len(self.redis_groups) > 0:
            self.combo_grupo.clear()
            if self.redis_groups:
                for groups in self.redis_groups:
                    for instances in groups.instances:
                        self.redis_dict[instances.name] = instances
            if self.redis_groups:
                for groups in self.redis_groups:
                    self.combo_grupo.addItem(groups.name)

    def aplicar_settings(self, settings):
        self.settings = settings
        self.redis_groups = settings.redis_groups

        if not self._page_montada:
            self.montar_tela()

        self.atualizar_elementos()