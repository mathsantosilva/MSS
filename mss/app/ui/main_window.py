from PySide6.QtWidgets import (
    QMainWindow,
    QStackedWidget,
    QWidget,
    QHBoxLayout
)
from app.core.settings import Settings
from app.ui.widgets.app_sidebar import AppSideBar
from app.ui.pages.dashboard_page import DashboardPage
from app.ui.pages.banco_muro_page import BancoMuroPage
from app.ui.pages.redis_page import RedisPage
from app.ui.pages.documentos_page import DocumentosPage
from app.ui.pages.dados_empresas_page import DadosEmpresasPage
from app.ui.pages.configuracao_page import ConfiguracaoPage
from app.ui.pages.buscar_bancos_page import BuscarBancosPage
from app.ui.pages.consultar_versao_page import ConsultarVersaoPage
from app.ui.pages.replicar_versao_page import ReplicarVersaoPage
from app.ui.pages.limpar_todos_redis_page import LimparTodosRedisPage
from app.ui.pages.limpar_especifico_redis_page import LimparEspecificoRedisPage
from app.ui.pages.gerador_documentos_page import GeradorDocumentosPage
from app.ui.pages.validador_documentos_page import ValidadorDocumentosPage
from app.ui.pages.buscar_dados_empresas_page import BuscarDadosEmpresasPage
from app.ui.pages.arquivo_configuracao_page import ArquivoConfiguracaoPage
from app.ui.pages.trocar_arquivo_configuracao_page import TrocarArquivoConfiguracao
from app.ui.pages.editar_arquivo_configuracao_page import EditarArquivoConfiguracao
from app.ui.pages.criar_arquivo_configuracao_page import CriarArquivoConfiguracao
from app.services.filesystem_service import FileSystemService
from app.ui.widgets.message_dialogs import mostrar_info, mostrar_erro, confirmar, mostrar_alerta
from app.services.config_service import ConfigService
from app.services.update_service import update_service
from app.core.constants import (
    APP_NAME,
    APP_VERSION,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        file_service = FileSystemService()
        self.status_config = False

        try:
            file_service.validar_diretorio()
        except Exception as error:
            mostrar_erro(
                self,
                "Validar diretórios",
                str(error)
            )

        self.config_service = ConfigService()
        self.settings = self.config_service.load()
        self.update_service = update_service(self.settings)
        resultado_update = self.update_service.validar_data_atualizacao_config()
        if self.settings.program.check_updates_on_startup:
            self.update_service.atualizador()
        if self.settings.program.selected_config:
            self.status_config = True
        self.setWindowTitle(f"{APP_NAME} - {APP_VERSION}")
        self.resize(900, 600)
        self.setMinimumSize(800, 500)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.central_widget.setLayout(self.main_layout)

        self.app_side_bar = AppSideBar(self.settings, self.status_config)
        self.main_layout.addWidget(self.app_side_bar)

        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack, stretch=1)

        self.dashboard_page = DashboardPage()
        self.banco_muro_page = BancoMuroPage()
        self.redis_page = RedisPage()
        self.documentos_page = DocumentosPage()
        self.dados_empresas_page = DadosEmpresasPage()
        self.configuracao_page = ConfiguracaoPage()
        self.buscar_bancos_page = BuscarBancosPage(self.settings.connections)
        self.consultar_versao_page = ConsultarVersaoPage(self.settings.connections)
        self.replicar_versao_page = ReplicarVersaoPage(self.settings.connections)
        self.limpar_todos_redis_page = LimparTodosRedisPage(self.settings.redis_groups)
        self.limpar_especifico_redis_page = LimparEspecificoRedisPage(self.settings.redis_groups)
        self.buscar_dados_empresas_page = BuscarDadosEmpresasPage(self.settings.connections, self.settings.wall_databases)
        self.gerador_documentos_page = GeradorDocumentosPage()
        self.validador_documentos_page = ValidadorDocumentosPage()
        self.arquivo_configuracao_page = ArquivoConfiguracaoPage()
        self.trocar_arquivo_configuracao_page = TrocarArquivoConfiguracao()
        self.editar_arquivo_configuracao_page = EditarArquivoConfiguracao()
        self.criar_arquivo_configuracao_page = CriarArquivoConfiguracao()

        self.pages = {
            "buscar_bancos_page": self.buscar_bancos_page,
            "consultar_versao_page": self.consultar_versao_page,
            "replicar_versao_page": self.replicar_versao_page,
            "limpar_todos_redis_page": self.limpar_todos_redis_page,
            "limpar_especifico_redis_page": self.limpar_especifico_redis_page,
            "buscar_dados_empresas_page": self.buscar_dados_empresas_page,
        }

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.banco_muro_page)
        self.stack.addWidget(self.redis_page)
        self.stack.addWidget(self.documentos_page)
        self.stack.addWidget(self.dados_empresas_page)
        self.stack.addWidget(self.configuracao_page)
        self.stack.addWidget(self.buscar_bancos_page)
        self.stack.addWidget(self.consultar_versao_page)
        self.stack.addWidget(self.replicar_versao_page)
        self.stack.addWidget(self.limpar_todos_redis_page)
        self.stack.addWidget(self.limpar_especifico_redis_page)
        self.stack.addWidget(self.gerador_documentos_page)
        self.stack.addWidget(self.validador_documentos_page)
        self.stack.addWidget(self.buscar_dados_empresas_page)
        self.stack.addWidget(self.arquivo_configuracao_page)
        self.stack.addWidget(self.trocar_arquivo_configuracao_page)
        self.stack.addWidget(self.editar_arquivo_configuracao_page)
        self.stack.addWidget(self.criar_arquivo_configuracao_page)

        self.botoes_sidebar = self.app_side_bar.botoes()

        self.conectar_sidebar()
        self.conectar_botoes_troca_paginas()
        self.conectar_botoes_execucao()

        if self.status_config:
            self.abrir_pagina(
                self.dashboard_page,
                self.app_side_bar.btn_dashboard
            )
        else:
            self.abrir_pagina(
                self.configuracao_page,
                self.app_side_bar.btn_configuracao
            )
            mostrar_alerta(
                self,
                "Configuração não encontrada",
                "Nenhuma configuração foi encontrada.\nSelecione ou crie um arquivo de configuração."
            )


        self.aplicar_estilo()

    def conectar_sidebar(self):
        self.app_side_bar.btn_dashboard.clicked.connect(
            lambda: self.abrir_pagina(
                self.dashboard_page,
                self.app_side_bar.btn_dashboard
            )
        )

        self.app_side_bar.btn_banco_muro.clicked.connect(
            lambda: self.abrir_pagina(
                self.banco_muro_page,
                self.app_side_bar.btn_banco_muro
            )
        )

        self.app_side_bar.btn_redis.clicked.connect(
            lambda: self.abrir_pagina(
                self.redis_page,
                self.app_side_bar.btn_redis
            )
        )

        self.app_side_bar.btn_documentos.clicked.connect(
            lambda: self.abrir_pagina(
                self.documentos_page,
                self.app_side_bar.btn_documentos
            )
        )

        self.app_side_bar.btn_empresa.clicked.connect(
            lambda: self.abrir_pagina(
                self.dados_empresas_page,
                self.app_side_bar.btn_empresa
            )
        )
        self.app_side_bar.btn_configuracao.clicked.connect(
            lambda: self.abrir_pagina(
                self.configuracao_page,
                self.app_side_bar.btn_configuracao
            )
        )
        self.app_side_bar.btn_buscar_bancos.clicked.connect(self.abrir_buscar_bancos)
        self.app_side_bar.btn_consultar_versao.clicked.connect(self.abrir_consultar_versao)
        self.app_side_bar.btn_replicar_versao.clicked.connect(self.abrir_replicar_versao)
        self.app_side_bar.btn_limpar_todos_redis.clicked.connect(self.abrir_limpar_todos_redis)
        self.app_side_bar.btn_limpar_especifico_redis.clicked.connect(self.abrir_limpar_especifico_redis)
        self.app_side_bar.btn_gerador_documentos.clicked.connect(self.abrir_gerador_documentos)
        self.app_side_bar.btn_validador_documentos.clicked.connect(self.abrir_validador_documentos)
        self.app_side_bar.btn_buscar_dados_empresas.clicked.connect(self.abrir_buscar_dados_empresas)
        self.app_side_bar.btn_arquivo_configuracao.clicked.connect(self.abrir_arquivo_configuracao)
        self.app_side_bar.btn_trocar_configuracao.clicked.connect(self.abrir_trocar_arquivo_configuracao)
        self.app_side_bar.btn_editar_configuracao.clicked.connect(self.abrir_editar_arquivo_configuracao)
        self.app_side_bar.btn_criar_configuracao.clicked.connect(self.abrir_criar_arquivo_configuracao)

    def abrir_pagina(self, pagina, botao_pai, botao_filho=None):
        pagina.montar_tela()

        if hasattr(pagina, "atualizar_elementos"):
            pagina.atualizar_elementos()

        self.stack.setCurrentWidget(pagina)

        self.app_side_bar.definir_secao_ativa(botao_pai, botao_filho)

    def conectar_botoes_troca_paginas(self):
        self.banco_muro_page.abrir_buscar_bancos.connect(
            self.abrir_buscar_bancos
        )
        self.banco_muro_page.abrir_consultar_versao.connect(
            self.abrir_consultar_versao
        )
        self.banco_muro_page.abrir_replicar_versao.connect(
            self.abrir_replicar_versao
        )
        self.redis_page.abrir_limpar_todos_redis.connect(
            self.abrir_limpar_todos_redis
        )
        self.redis_page.abrir_limpar_especifico_redis.connect(
            self.abrir_limpar_especifico_redis
        )
        self.documentos_page.abrir_gerador_documentos.connect(
            self.abrir_gerador_documentos
        )
        self.documentos_page.abrir_validador_documentos.connect(
            self.abrir_validador_documentos
        )
        self.dados_empresas_page.abrir_buscar_dados_empresa.connect(
            self.abrir_buscar_dados_empresas
        )
        self.configuracao_page.abrir_arquivo_configuracao.connect(
            self.abrir_arquivo_configuracao
        )
        self.arquivo_configuracao_page.abrir_trocar_arquivo_configuracao.connect(
            self.abrir_trocar_arquivo_configuracao
        )
        self.arquivo_configuracao_page.abrir_editar_arquivo_configuracao.connect(
            self.abrir_editar_arquivo_configuracao
        )
        self.arquivo_configuracao_page.abrir_criar_arquivo_configuracao.connect(
            self.abrir_criar_arquivo_configuracao
        )

    def conectar_botoes_execucao(self):
        self.trocar_arquivo_configuracao_page.iniciar_troca_configuracao.connect(
            self.trocar_configuracao
        )

    def abrir_buscar_bancos(self):
        self.abrir_pagina(
            self.buscar_bancos_page,
            self.app_side_bar.btn_banco_muro,
            self.app_side_bar.btn_buscar_bancos
        )

    def abrir_consultar_versao(self):
        self.abrir_pagina(
            self.consultar_versao_page,
            self.app_side_bar.btn_banco_muro,
            self.app_side_bar.btn_consultar_versao
        )

    def abrir_replicar_versao(self):
        self.abrir_pagina(
            self.replicar_versao_page,
            self.app_side_bar.btn_banco_muro,
            self.app_side_bar.btn_replicar_versao
        )

    def abrir_limpar_todos_redis(self):
        self.abrir_pagina(
            self.limpar_todos_redis_page,
            self.app_side_bar.btn_redis,
            self.app_side_bar.btn_limpar_todos_redis
        )

    def abrir_limpar_especifico_redis(self):
        self.abrir_pagina(
            self.limpar_especifico_redis_page,
            self.app_side_bar.btn_redis,
            self.app_side_bar.btn_limpar_especifico_redis
        )

    def abrir_gerador_documentos(self):
        self.abrir_pagina(
            self.gerador_documentos_page,
            self.app_side_bar.btn_documentos,
            self.app_side_bar.btn_gerador_documentos
        )

    def abrir_validador_documentos(self):
        self.abrir_pagina(
            self.validador_documentos_page,
            self.app_side_bar.btn_documentos,
            self.app_side_bar.btn_validador_documentos
        )

    def abrir_buscar_dados_empresas(self):
        self.abrir_pagina(
            self.buscar_dados_empresas_page,
            self.app_side_bar.btn_empresa,
            self.app_side_bar.btn_buscar_dados_empresas
        )

    def abrir_arquivo_configuracao(self):
        self.abrir_pagina(
            self.arquivo_configuracao_page,
            self.app_side_bar.btn_configuracao,
            self.app_side_bar.btn_arquivo_configuracao
        )

    def abrir_trocar_arquivo_configuracao(self):
        self.abrir_pagina(
            self.trocar_arquivo_configuracao_page,
            self.app_side_bar.btn_configuracao,
            self.app_side_bar.btn_trocar_configuracao
        )

    def abrir_editar_arquivo_configuracao(self):
        self.abrir_pagina(
            self.editar_arquivo_configuracao_page,
            self.app_side_bar.btn_configuracao,
            self.app_side_bar.btn_editar_configuracao
        )

    def abrir_criar_arquivo_configuracao(self):
        self.abrir_pagina(
            self.criar_arquivo_configuracao_page,
            self.app_side_bar.btn_configuracao,
            self.app_side_bar.btn_criar_configuracao
        )

    def aplicar_estilo(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f3f4f6;
            }

            QFrame#sidebar {
                background-color: #111827;
                border: none;
            }

            QLabel#sidebarTitle {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }

            QLabel#sidebarVersion {
                color: #9ca3af;
                font-size: 12px;
            }

            QPushButton#sidebarButton {
                background-color: transparent;
                color: #d1d5db;
                border: none;
                text-align: left;
                padding: 10px 14px;
                border-radius: 8px;
                font-size: 14px;
            }

            QPushButton#sidebarButton:hover {
                background-color: #1f2937;
                color: white;
            }

            QPushButton#sidebarButton:checked {
                background-color: #2563eb;
                color: white;
                font-weight: bold;
            }

            QPushButton#sidebarChildButton {
                background-color: transparent;
                color: #9ca3af;
                border: none;
                text-align: left;
                padding: 7px 14px 7px 28px;
                border-radius: 6px;
                font-size: 13px;
            }

            QPushButton#sidebarChildButton:hover {
                background-color: #1f2937;
                color: white;
            }

            QPushButton#sidebarChildButton:checked {
                background-color: #1e40af;
                color: white;
            }

            QStackedWidget {
                background-color: #f9fafb;
            }
        """)

    def trocar_configuracao(self, arquivo_json):
        try:
            self.settings = self.config_service.load(arquivo_json)

            if not isinstance(self.settings, Settings):
                raise ValueError("Não foi possível carregar a configuração selecionada.")

            for page in self.pages.values():
                if hasattr(page, "aplicar_settings"):
                    page.aplicar_settings(self.settings)

            self.app_side_bar.atualizar_label_configuracao(arquivo_json)
            self.app_side_bar.atualizar_status_config(True)

            self.trocar_arquivo_configuracao_page.mostrar_configuracao_aplicada(
                arquivo_json
            )

        except Exception as error:
            self.trocar_arquivo_configuracao_page.mostrar_erro_configuracao(
                str(error)
            )
