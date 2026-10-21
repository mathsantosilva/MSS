import json
import os
from datetime import datetime
from app.services.config_service import ConfigService
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QGridLayout,
    QPushButton,
    QHBoxLayout,
    QLineEdit,
)

from app.core.constants import (
    MENSAGEM_JSON,
    VERSION_JSON,
    NM_PASTA_CONFIG,
)


class CriarArquivoConfiguracao(QWidget):
    def __init__(self):
        super().__init__()
        self._page_montada = False
        self.config_service = ConfigService()

    def montar_tela(self):
        if self._page_montada:
            return

        self.setObjectName("CriarArquivoConfiguracao")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(16)

        titulo = QLabel("Criar arquivo de Configuração")
        titulo.setObjectName("pageTitle")

        descricao = QLabel("Escolha um nome de arquivo sem a extensão (.json).")
        descricao.setObjectName("pageDescription")

        self.btn_executar = QPushButton("Criar")
        self.btn_executar.clicked.connect(self.criar_arquivo_config_json)

        label_nome = QLabel("Nome do arquivo")
        self.input_nome_arquivo = QLineEdit()
        self.input_nome_arquivo.setPlaceholderText("Ex: qcmaint")

        self.label_status_config = QLabel("")
        self.label_status_config.setObjectName("configStatus")
        self.label_status_config.setVisible(True)

        form_layout = QGridLayout()
        form_layout.setSpacing(8)
        form_layout.addWidget(QLabel("Status: "), 0, 0)
        form_layout.addWidget(self.label_status_config, 0, 1)
        form_layout.addWidget(label_nome)
        form_layout.addWidget(self.input_nome_arquivo)

        botoes_layout = QHBoxLayout()
        botoes_layout.addStretch()
        botoes_layout.addWidget(self.btn_executar)

        main_layout.addWidget(titulo)
        main_layout.addWidget(descricao)
        main_layout.addSpacing(12)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(botoes_layout)
        main_layout.addStretch()

        container = QWidget()
        container.setMaximumWidth(620)
        container.setLayout(main_layout)

        page_layout = QVBoxLayout()
        page_layout.setContentsMargins(32, 32, 32, 32)
        page_layout.addWidget(container)
        page_layout.addStretch()

        self.setLayout(page_layout)
        self.aplicar_estilo()
        self._page_montada = True

    def criar_arquivo_config_json(self):
        lista_arquivos = self.config_service.buscar_lista_configuracoes()

        try:
            nome_selecionado = self.input_nome_arquivo.text()
            nome_selecionado = nome_selecionado.split(".")
            if isinstance(nome_selecionado, list):
                nome_selecionado = nome_selecionado[0]
            if not nome_selecionado:
                msg = "Preencha um nome para continuar"
                self.mostrar_falha(msg)
                return
            nome_formatado = nome_selecionado + ".json"
            data_hora = datetime.now().strftime("%d-%m-%Y")

            if nome_formatado in lista_arquivos:
                msg = "Nome de arquivo já utlizado, favor escolher outro"
                self.mostrar_falha(msg)
                return
            arquivo_config = {
                "controle_versao_json": {
                    "versao": VERSION_JSON,
                    "data": data_hora,
                    "comentario": MENSAGEM_JSON,
                },
                "bancos_update": {
                    "database_update_br": "",
                    "database_update_mx": "",
                    "database_update_pt": "",
                    "database_update_md": "",
                },
                "bases_muro": [
                    ""
                ],
                "conexoes": [
                    {
                        "nome": "",
                        "server": "",
                        "username": "",
                        "password": "",
                    }
                ],
                "redis_qa": {
                    "grupo_1": [
                        {
                            "nome_redis": "",
                            "ip": "",
                            "port": "",
                        },
                        {
                            "nome_redis": "",
                            "ip": "",
                            "port": "",
                        },
                    ],
                    "grupo_2": [
                        {
                            "nome_redis": "",
                            "ip": "",
                            "port": "",
                        },
                        {
                            "nome_redis": "",
                            "ip": "",
                            "port": "",
                        },
                    ],
                },
            }
            path_config = os.path.join(NM_PASTA_CONFIG, nome_formatado)
            with open(path_config, "w", encoding="utf-8") as arquivo:
                json.dump(arquivo_config, arquivo, indent=4)

            self.mostrar_sucesso(f"Arquivo {nome_formatado} criado com sucesso.")

        except Exception as error:
            self.mostrar_falha(str(error))

    def mostrar_sucesso(self, texto):
        self.label_status_config.setProperty("status", "success")
        self.label_status_config.setText(texto)
        self.label_status_config.setVisible(True)
        self.label_status_config.style().unpolish(self.label_status_config)
        self.label_status_config.style().polish(self.label_status_config)

    def mostrar_falha(self, mensagem):
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

    def atualizar_elementos(self):
        self.input_nome_arquivo.clear()
        self.limpar_campo_status()

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
            }
        """)
