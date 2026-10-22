import json
from PySide6.QtCore import Signal
from app.services.config_service import ConfigService
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QComboBox,
    QPlainTextEdit,
    QVBoxLayout,
    QGridLayout,
    QSizePolicy,
    QPushButton,
    QHBoxLayout,
)


class TrocarArquivoConfiguracao(QWidget):
    iniciar_troca_configuracao = Signal(str)

    def __init__(self):
        super().__init__()
        self._page_montada = False
        self.aplicar_estilo()
        self.config_service = ConfigService()

    def montar_tela(self):

        if self._page_montada:
            return

        self.setObjectName("TrocarArquivoConfiguracao")

        titulo = QLabel("Escolher arquivo de Configuração")
        titulo.setObjectName("pageTitle")

        btn_executar = QPushButton("Selecionar")

        btn_executar.clicked.connect(self.executar_trocar_configuracao)

        descricao = QLabel("Selecione um arquivo de configuração para visualizar seu conteúdo.")
        descricao.setObjectName("pageDescription")

        self.combo_arquivo_configuracao = QComboBox()

        self.combo_arquivo_configuracao.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )


        self.input_conteudo_json = QPlainTextEdit()
        self.input_conteudo_json.setReadOnly(True)
        self.input_conteudo_json.setPlaceholderText(
            "O conteúdo do arquivo JSON será exibido aqui..."
        )

        self.arquivos_jsons = self.config_service.buscar_lista_configuracoes()

        self.combo_arquivo_configuracao.currentTextChanged.connect(
            self.preencher_textbox_arquivo_configuracao
        )
        self.label_status_config = QLabel("")
        self.label_status_config.setObjectName("configStatus")
        self.label_status_config.setVisible(True)

        self.btn_recarregar = QPushButton("Recarregar")
        self.btn_recarregar.clicked.connect(self.atualizar_elementos)

        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(12)

        form_layout.addWidget(QLabel("Arquivo configuração"), 0, 0)
        form_layout.addWidget(self.combo_arquivo_configuracao, 0, 1)

        form_layout.addWidget(QLabel("Status: "), 1, 0)
        form_layout.addWidget(self.label_status_config, 1, 1)


        form_layout.setColumnStretch(0, 0)
        form_layout.setColumnStretch(1, 1)

        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        layout.addWidget(titulo)
        layout.addWidget(descricao)
        layout.addSpacing(12)

        layout.addLayout(form_layout)

        layout.addSpacing(16)
        layout.addWidget(QLabel("Conteúdo JSON"))
        layout.addWidget(self.input_conteudo_json)

        botoes_layout = QHBoxLayout()
        botoes_layout.addStretch()
        botoes_layout.addWidget(self.btn_recarregar)
        botoes_layout.addWidget(btn_executar)
        layout.addLayout(botoes_layout)


        self.setLayout(layout)

        self.atualizar_elementos()
        self._page_montada = True

    def preencher_textbox_arquivo_configuracao(self, nome_arquivo):
        retorno_arquivo = self.config_service.carregar_arquivo_json(nome_arquivo, self.arquivos_jsons)
        if not retorno_arquivo.get('sucesso'):
            if retorno_arquivo.get('msg_erro'):
                self.input_conteudo_json.setPlainText(
                    str(retorno_arquivo.get('msg_erro'))
                )
            else:
                self.input_conteudo_json.clear()
            return
        self.input_conteudo_json.setPlainText(str(retorno_arquivo.get("texto")))

    def mostrar_configuracao_aplicada(self, texto):
        self.label_status_config.setProperty("status", "success")
        self.label_status_config.setText(f"Configuração aplicada com sucesso: {texto}")
        self.label_status_config.setVisible(True)
        self.label_status_config.style().unpolish(self.label_status_config)
        self.label_status_config.style().polish(self.label_status_config)

    def mostrar_erro_configuracao(self, mensagem):
        self.label_status_config.setProperty("status", "error")
        self.label_status_config.setText(mensagem)
        self.label_status_config.setVisible(True)
        self.label_status_config.style().unpolish(self.label_status_config)
        self.label_status_config.style().polish(self.label_status_config)

    def limpar_campo_status(self):
        self.label_status_config.setProperty("status", "")
        self.label_status_config.setVisible(False)
        self.label_status_config.style().unpolish(self.label_status_config)
        self.label_status_config.style().polish(self.label_status_config)

    def aplicar_estilo(self):
        self.setStyleSheet("""
            QLabel#configStatus {
                font-size: 13px;
                padding: 6px 8px;
                border-radius: 4px;
            }

            QLabel#configStatus[status="success"] {
                color: #15803d;
                background-color: #dcfce7;
                border: 1px solid #86efac;
            }

            QLabel#configStatus[status="error"] {
                color: #b91c1c;
                background-color: #fee2e2;
                border: 1px solid #fca5a5;
            }""")

    def preencher_combobox_arquivos(self):
        self.arquivos_jsons = self.config_service.buscar_lista_configuracoes()

        self.combo_arquivo_configuracao.clear()

        self.combo_arquivo_configuracao.addItem("Selecione um arquivo")
        self.combo_arquivo_configuracao.addItems(
            self.arquivos_jsons.keys()
        )

    def atualizar_elementos(self):
        self.preencher_combobox_arquivos()
        self.limpar_campo_status()

    def executar_trocar_configuracao(self):
        nome_arquivo = self.combo_arquivo_configuracao.currentText()
        retorno_arquivo = self.config_service.carregar_arquivo_json(nome_arquivo, self.arquivos_jsons)
        if not retorno_arquivo.get('sucesso'):
            if retorno_arquivo.get('msg_erro'):
                self.input_conteudo_json.setPlainText(
                    str(retorno_arquivo.get('msg_erro'))
                )
            else:
                self.input_conteudo_json.clear()
            return
        self.iniciar_troca_configuracao.emit(nome_arquivo)
