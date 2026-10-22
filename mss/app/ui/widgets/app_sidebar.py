from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class AppSideBar(QFrame):
    def __init__(self, settings, status_config):
        super().__init__()

        self.setObjectName("sidebar")
        self.setFixedWidth(220)
        self.settings = settings
        self.status_config = status_config
        self.versao = ""
        self.criar_layout()

    def criar_layout(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(8)
        self.setLayout(layout)

        titulo = QLabel("MSS")
        titulo.setObjectName("sidebarTitle")

        if self.settings:
            config_selecionado = self.settings.program.selected_config
        else:
            config_selecionado = ""

        self.versao = QLabel(config_selecionado)
        self.versao.setObjectName("sidebarVersion")

        layout.addWidget(titulo)
        layout.addWidget(self.versao)
        layout.addSpacing(24)

        self.btn_dashboard = self.criar_botao_sidebar("Dashboard", self.status_config)
        self.btn_banco_muro = self.criar_botao_sidebar("Banco de Muro", self.status_config)
        self.btn_redis = self.criar_botao_sidebar("Redis", self.status_config)
        self.btn_documentos = self.criar_botao_sidebar("Documentos", self.status_config)
        self.btn_empresa = self.criar_botao_sidebar("Informações Empresas", self.status_config)
        self.btn_configuracao = self.criar_botao_sidebar("Configuração", True)

        self.btn_buscar_bancos = self.criar_botao_filho_sidebar("Buscar bancos", self.status_config)
        self.btn_consultar_versao = self.criar_botao_filho_sidebar("Consultar versão", self.status_config)
        self.btn_replicar_versao = self.criar_botao_filho_sidebar("Replicar versão", self.status_config)
        self.btn_limpar_todos_redis = self.criar_botao_filho_sidebar("Limpar todos", self.status_config)
        self.btn_limpar_especifico_redis = self.criar_botao_filho_sidebar("Limpar específico", self.status_config)
        self.btn_gerador_documentos = self.criar_botao_filho_sidebar("Gerador", self.status_config)
        self.btn_validador_documentos = self.criar_botao_filho_sidebar("Validador", self.status_config)
        self.btn_buscar_dados_empresas = self.criar_botao_filho_sidebar("Buscar dados", self.status_config)
        self.btn_arquivo_configuracao = self.criar_botao_filho_sidebar("Arquivos", True)
        self.btn_trocar_configuracao = self.criar_botao_filho_sidebar("Trocar arquivo", True)
        self.btn_editar_configuracao = self.criar_botao_filho_sidebar("Editar arquivo", True)
        self.btn_criar_configuracao = self.criar_botao_filho_sidebar("Criar arquivo", True)

        self.menu_sections = {
            self.btn_banco_muro: [
                self.btn_buscar_bancos,
                self.btn_consultar_versao,
                self.btn_replicar_versao,
            ],
            self.btn_redis: [
                self.btn_limpar_todos_redis,
                self.btn_limpar_especifico_redis,
            ],
            self.btn_documentos: [
                self.btn_gerador_documentos,
                self.btn_validador_documentos,
            ],
            self.btn_empresa: [
                self.btn_buscar_dados_empresas,
            ],
            self.btn_configuracao: [
                self.btn_arquivo_configuracao,
                self.btn_trocar_configuracao,
                self.btn_editar_configuracao,
                self.btn_criar_configuracao,
            ],
        }

        self.adicionar_secao(layout, self.btn_dashboard)
        self.adicionar_secao(layout, self.btn_banco_muro)
        self.adicionar_secao(layout, self.btn_redis)
        self.adicionar_secao(layout, self.btn_documentos)
        self.adicionar_secao(layout, self.btn_empresa)
        self.adicionar_secao(layout, self.btn_configuracao)

        layout.addStretch()

    def adicionar_secao(self, layout, botao_pai):
        layout.addWidget(botao_pai)

        for botao_filho in self.menu_sections.get(botao_pai, []):
            layout.addWidget(botao_filho)

    def criar_botao_sidebar(self, texto, status_config=True):
        botao = QPushButton(texto)
        botao.setObjectName("sidebarButton")
        botao.setCheckable(True)
        botao.setEnabled(status_config)
        botao.setCursor(Qt.CursorShape.PointingHandCursor)
        return botao

    def criar_botao_filho_sidebar(self, texto, status_config=True):
        botao = QPushButton(texto)
        botao.setObjectName("sidebarChildButton")
        botao.setCheckable(True)
        botao.setVisible(False)
        botao.setEnabled(status_config)
        botao.setCursor(Qt.CursorShape.PointingHandCursor)
        return botao

    def botoes(self):
        botoes_pai = [
            self.btn_dashboard,
            self.btn_banco_muro,
            self.btn_redis,
            self.btn_documentos,
            self.btn_empresa,
            self.btn_configuracao,
        ]

        botoes_filho = []
        for filhos in self.menu_sections.values():
            botoes_filho.extend(filhos)

        return botoes_pai + botoes_filho

    def definir_secao_ativa(self, botao_pai, botao_filho=None):
        self.btn_dashboard.setChecked(botao_pai == self.btn_dashboard)

        for pai, filhos in self.menu_sections.items():
            pai.setChecked(pai == botao_pai)

            for filho in filhos:
                filho.setVisible(pai == botao_pai)
                filho.setChecked(filho == botao_filho)

    def atualizar_status_config(self, status_config):
        self.status_config = status_config

        for botao in [
            self.btn_dashboard,
            self.btn_banco_muro,
            self.btn_redis,
            self.btn_documentos,
            self.btn_empresa,
        ]:
            botao.setEnabled(status_config)

        for pai, filhos in self.menu_sections.items():
            if pai == self.btn_configuracao:
                pai.setEnabled(True)
                for filho in filhos:
                    filho.setEnabled(True)
            else:
                for filho in filhos:
                    filho.setEnabled(status_config)

    def atualizar_label_configuracao(self, config_selecionado):
        self.versao.setText(config_selecionado)
