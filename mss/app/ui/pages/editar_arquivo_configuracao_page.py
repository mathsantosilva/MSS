import json
import os
from pathlib import Path

from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.core.constants import NM_PASTA_CONFIG
from app.services.config_service import ConfigService


class EditarArquivoConfiguracao(QWidget):
    def __init__(self):
        super().__init__()
        self._page_montada = False
        self.arquivos_jsons = {}
        self.aplicar_estilo()
        self.config_service = ConfigService()

    def montar_tela(self):
        if self._page_montada:
            return

        self.setObjectName("EditarArquivoConfiguracao")

        titulo = QLabel("Editar arquivo de Configuração")
        titulo.setObjectName("pageTitle")

        descricao = QLabel("Selecione um arquivo de configuração para editar seus valores.")
        descricao.setObjectName("pageDescription")

        self.combo_arquivo_configuracao = QComboBox()
        self.combo_arquivo_configuracao.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        self.label_status_config = QLabel("")
        self.label_status_config.setObjectName("configStatus")
        self.label_status_config.setVisible(False)

        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(12)
        form_layout.addWidget(QLabel("Arquivo configuração"), 0, 0)
        form_layout.addWidget(self.combo_arquivo_configuracao, 0, 1)
        form_layout.addWidget(QLabel("Status:"), 1, 0)
        form_layout.addWidget(self.label_status_config, 1, 1)
        form_layout.setColumnStretch(1, 1)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.criar_aba_geral(), "Geral")
        self.tabs.addTab(self.criar_aba_bancos(), "Bancos")
        self.tabs.addTab(self.criar_aba_bases(), "Bases")
        self.tabs.addTab(self.criar_aba_conexoes(), "Conexões")
        self.tabs.addTab(self.criar_aba_redis(), "Redis")

        self.btn_recarregar = QPushButton("Recarregar")
        self.btn_salvar = QPushButton("Salvar")
        self.btn_recarregar.clicked.connect(self.atualizar_elementos)
        self.btn_salvar.clicked.connect(self.salvar_arquivo_configuracao)

        botoes_layout = QHBoxLayout()
        botoes_layout.addStretch()
        botoes_layout.addWidget(self.btn_recarregar)
        botoes_layout.addWidget(self.btn_salvar)

        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)
        layout.addWidget(titulo)
        layout.addWidget(descricao)
        layout.addSpacing(8)
        layout.addLayout(form_layout)
        layout.addWidget(self.tabs)
        layout.addLayout(botoes_layout)

        self.setLayout(layout)

        self.combo_arquivo_configuracao.currentTextChanged.connect(
            self.preencher_dados_arquivo_configuracao
        )

        self.atualizar_elementos()
        self._page_montada = True

    def atualizar_elementos(self):
        self.tabs.setCurrentIndex(0)
        self.arquivos_jsons = self.config_service.buscar_lista_configuracoes()

        self.combo_arquivo_configuracao.blockSignals(True)
        self.combo_arquivo_configuracao.clear()
        self.combo_arquivo_configuracao.addItem("Selecione um arquivo")
        self.combo_arquivo_configuracao.addItems(self.arquivos_jsons.keys())

        self.combo_arquivo_configuracao.blockSignals(False)
        self.preencher_dados_arquivo_configuracao(self.combo_arquivo_configuracao.currentText())

    def criar_aba_geral(self):
        widget = QWidget()

        self.input_versao = QLineEdit()
        self.input_data = QLineEdit()
        self.input_comentario = QLineEdit()

        layout = QGridLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(12)
        layout.addWidget(QLabel("Versão"), 0, 0)
        layout.addWidget(self.input_versao, 0, 1)
        layout.addWidget(QLabel("Data"), 1, 0)
        layout.addWidget(self.input_data, 1, 1)
        layout.addWidget(QLabel("Comentário"), 2, 0)
        layout.addWidget(self.input_comentario, 2, 1)
        layout.setColumnStretch(1, 1)
        layout.setRowStretch(3, 1)

        widget.setLayout(layout)
        return widget

    def criar_aba_bancos(self):
        widget = QWidget()

        self.input_database_update_br = QLineEdit()
        self.input_database_update_pt = QLineEdit()
        self.input_database_update_mx = QLineEdit()
        self.input_database_update_md = QLineEdit()

        layout = QGridLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(12)
        layout.addWidget(QLabel("Database update BR"), 0, 0)
        layout.addWidget(self.input_database_update_br, 0, 1)
        layout.addWidget(QLabel("Database update PT"), 1, 0)
        layout.addWidget(self.input_database_update_pt, 1, 1)
        layout.addWidget(QLabel("Database update MX"), 2, 0)
        layout.addWidget(self.input_database_update_mx, 2, 1)
        layout.addWidget(QLabel("Database update MD"), 3, 0)
        layout.addWidget(self.input_database_update_md, 3, 1)
        layout.setColumnStretch(1, 1)
        layout.setRowStretch(4, 1)

        widget.setLayout(layout)
        return widget

    def criar_aba_bases(self):
        widget = QWidget()

        self.tabela_bases = self.criar_tabela(["Base de muro"])

        btn_adicionar = QPushButton("Adicionar base")
        btn_remover = QPushButton("Remover selecionada")
        btn_adicionar.clicked.connect(lambda: self.adicionar_linha(self.tabela_bases, [""]))
        btn_remover.clicked.connect(lambda: self.remover_linha_selecionada(self.tabela_bases))

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        layout.addWidget(self.tabela_bases)
        layout.addLayout(self.criar_botoes_tabela(btn_adicionar, btn_remover))

        widget.setLayout(layout)
        return widget

    def criar_aba_conexoes(self):
        widget = QWidget()

        self.tabela_conexoes = self.criar_tabela(["Nome", "Server", "Username", "Password"])

        btn_adicionar = QPushButton("Adicionar conexão")
        btn_remover = QPushButton("Remover selecionada")
        btn_adicionar.clicked.connect(lambda: self.adicionar_linha(self.tabela_conexoes, ["", "", "", ""]))
        btn_remover.clicked.connect(lambda: self.remover_linha_selecionada(self.tabela_conexoes))

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        layout.addWidget(self.tabela_conexoes)
        layout.addLayout(self.criar_botoes_tabela(btn_adicionar, btn_remover))

        widget.setLayout(layout)
        return widget

    def criar_aba_redis(self):
        widget = QWidget()

        self.combo_grupo_redis = QComboBox()
        self.tabelas_redis = {}

        self.container_tabela_redis = QVBoxLayout()

        btn_adicionar_grupo = QPushButton("Adicionar grupo")
        btn_remover_grupo = QPushButton("Remover grupo")
        btn_adicionar_redis = QPushButton("Adicionar Redis")
        btn_remover_redis = QPushButton("Remover selecionado")

        self.combo_grupo_redis.currentTextChanged.connect(self.exibir_grupo_redis)
        btn_adicionar_grupo.clicked.connect(self.adicionar_grupo_redis)
        btn_remover_grupo.clicked.connect(self.remover_grupo_redis)
        btn_adicionar_redis.clicked.connect(self.adicionar_redis_grupo_atual)
        btn_remover_redis.clicked.connect(self.remover_redis_grupo_atual)

        grupo_box = QGroupBox("Grupo")
        grupo_layout = QHBoxLayout()
        grupo_layout.addWidget(self.combo_grupo_redis)
        grupo_layout.addWidget(btn_adicionar_grupo)
        grupo_layout.addWidget(btn_remover_grupo)
        grupo_box.setLayout(grupo_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        layout.addWidget(grupo_box)
        layout.addLayout(self.container_tabela_redis)
        layout.addLayout(self.criar_botoes_tabela(btn_adicionar_redis, btn_remover_redis))

        widget.setLayout(layout)
        return widget

    def criar_tabela(self, colunas):
        tabela = QTableWidget(0, len(colunas))
        tabela.setHorizontalHeaderLabels(colunas)
        tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tabela.verticalHeader().setVisible(False)
        tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tabela.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        return tabela

    def criar_botoes_tabela(self, btn_adicionar, btn_remover):
        layout = QHBoxLayout()
        layout.addStretch()
        layout.addWidget(btn_remover)
        layout.addWidget(btn_adicionar)
        return layout

    def preencher_dados_arquivo_configuracao(self, nome_arquivo):
        retorno_arquivo = self.config_service.carregar_arquivo_json(nome_arquivo, self.arquivos_jsons)

        if not retorno_arquivo.get("sucesso", False):
            if not retorno_arquivo.get('msg_erro'):
                self.limpar_formulario()
            else:
                self.mostrar_falha(f"{retorno_arquivo.get('msg_erro')}")
        else:
            self.preencher_formulario(retorno_arquivo.get("json"))
            self.label_status_config.setVisible(False)

    def preencher_formulario(self, config):
        metadata = config.get("controle_versao_json", {})
        bancos_update = config.get("bancos_update", {})

        self.input_versao.setText(metadata.get("versao", ""))
        self.input_versao.setEnabled(False)
        self.input_data.setText(metadata.get("data", ""))
        self.input_data.setEnabled(False)
        self.input_comentario.setText(metadata.get("comentario", ""))
        self.input_comentario.setEnabled(False)
        self.input_database_update_br.setText(bancos_update.get("database_update_br", ""))
        self.input_database_update_pt.setText(bancos_update.get("database_update_pt", ""))
        self.input_database_update_mx.setText(bancos_update.get("database_update_mx", ""))
        self.input_database_update_md.setText(bancos_update.get("database_update_md", ""))

        self.preencher_tabela(
            self.tabela_bases,
            [[base] for base in config.get("bases_muro", [])],
            [""]
        )

        self.preencher_tabela(
            self.tabela_conexoes,
            [
                [
                    conexao.get("nome", ""),
                    conexao.get("server", ""),
                    conexao.get("username", ""),
                    conexao.get("password", ""),
                ]
                for conexao in config.get("conexoes", [])
            ],
            ["", "", "", ""]
        )

        self.preencher_redis(config.get("redis_qa", {}))

    def preencher_redis(self, redis_qa):
        self.limpar_grupos_redis()

        if not redis_qa:
            redis_qa = {"grupo_1": []}

        for grupo, instancias in redis_qa.items():
            tabela = self.criar_tabela(["Nome Redis", "IP", "Porta"])
            self.preencher_tabela(
                tabela,
                [
                    [
                        instancia.get("nome_redis", ""),
                        instancia.get("ip", ""),
                        instancia.get("port", ""),
                    ]
                    for instancia in instancias
                ],
                ["", "", ""]
            )
            tabela.setVisible(False)
            self.tabelas_redis[grupo] = tabela
            self.container_tabela_redis.addWidget(tabela)
            self.combo_grupo_redis.addItem(grupo)

        self.combo_grupo_redis.setCurrentIndex(0)
        self.exibir_grupo_redis(self.combo_grupo_redis.currentText())

    def preencher_tabela(self, tabela, linhas, valores_vazios):
        tabela.setRowCount(0)

        if not linhas:
            linhas = [valores_vazios]

        for valores in linhas:
            self.adicionar_linha(tabela, valores)

    def adicionar_linha(self, tabela, valores):
        linha = tabela.rowCount()
        tabela.insertRow(linha)

        for coluna, valor in enumerate(valores):
            tabela.setItem(linha, coluna, QTableWidgetItem(str(valor)))

    def remover_linha_selecionada(self, tabela):
        linha = tabela.currentRow()
        if linha >= 0:
            tabela.removeRow(linha)

    def adicionar_grupo_redis(self):
        numero_grupo = len(self.tabelas_redis) + 1
        nome_grupo = f"grupo_{numero_grupo}"

        while nome_grupo in self.tabelas_redis:
            numero_grupo += 1
            nome_grupo = f"grupo_{numero_grupo}"

        tabela = self.criar_tabela(["Nome Redis", "IP", "Porta"])
        self.adicionar_linha(tabela, ["", "", ""])
        tabela.setVisible(False)

        self.tabelas_redis[nome_grupo] = tabela
        self.container_tabela_redis.addWidget(tabela)
        self.combo_grupo_redis.addItem(nome_grupo)
        self.combo_grupo_redis.setCurrentText(nome_grupo)

    def remover_grupo_redis(self):
        nome_grupo = self.combo_grupo_redis.currentText()
        tabela = self.tabelas_redis.pop(nome_grupo, None)

        if tabela is None:
            return

        self.container_tabela_redis.removeWidget(tabela)
        tabela.deleteLater()
        self.combo_grupo_redis.removeItem(self.combo_grupo_redis.currentIndex())

        if not self.tabelas_redis:
            self.adicionar_grupo_redis()

    def exibir_grupo_redis(self, nome_grupo):
        for grupo, tabela in self.tabelas_redis.items():
            tabela.setVisible(grupo == nome_grupo)

    def adicionar_redis_grupo_atual(self):
        tabela = self.tabelas_redis.get(self.combo_grupo_redis.currentText())
        if tabela:
            self.adicionar_linha(tabela, ["", "", ""])

    def remover_redis_grupo_atual(self):
        tabela = self.tabelas_redis.get(self.combo_grupo_redis.currentText())
        if tabela:
            self.remover_linha_selecionada(tabela)

    def salvar_arquivo_configuracao(self):
        nome_arquivo = self.combo_arquivo_configuracao.currentText()

        if nome_arquivo == "Selecione um arquivo":
            self.mostrar_falha("Selecione um arquivo para salvar.")
            return

        caminho_arquivo = self.arquivos_jsons.get(nome_arquivo)

        if not caminho_arquivo:
            self.mostrar_falha("Arquivo de configuração não encontrado na lista.")
            return

        try:
            with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
                json.dump(self.montar_config(), arquivo, indent=4, ensure_ascii=False)

            self.mostrar_sucesso(f"Arquivo {nome_arquivo} salvo com sucesso.")

        except Exception as erro:
            self.mostrar_falha(f"Erro ao salvar arquivo: {erro}")

    def montar_config(self):
        return {
            "controle_versao_json": {
                "versao": self.input_versao.text().strip(),
                "data": self.input_data.text().strip(),
                "comentario": self.input_comentario.text().strip(),
            },
            "bancos_update": {
                "database_update_br": self.input_database_update_br.text().strip(),
                "database_update_pt": self.input_database_update_pt.text().strip(),
                "database_update_mx": self.input_database_update_mx.text().strip(),
                "database_update_md": self.input_database_update_md.text().strip(),
            },
            "bases_muro": self.obter_bases_muro(),
            "conexoes": self.obter_conexoes(),
            "redis_qa": self.obter_redis_qa(),
        }

    def obter_bases_muro(self):
        bases = []

        for linha in range(self.tabela_bases.rowCount()):
            base = self.obter_texto_tabela(self.tabela_bases, linha, 0)
            if base:
                bases.append(base)

        return bases

    def obter_conexoes(self):
        conexoes = []

        for linha in range(self.tabela_conexoes.rowCount()):
            nome = self.obter_texto_tabela(self.tabela_conexoes, linha, 0)
            server = self.obter_texto_tabela(self.tabela_conexoes, linha, 1)
            username = self.obter_texto_tabela(self.tabela_conexoes, linha, 2)
            password = self.obter_texto_tabela(self.tabela_conexoes, linha, 3)

            if any([nome, server, username, password]):
                conexoes.append({
                    "nome": nome,
                    "server": server,
                    "username": username,
                    "password": password,
                })

        return conexoes

    def obter_redis_qa(self):
        redis_qa = {}

        for grupo, tabela in self.tabelas_redis.items():
            instancias = []

            for linha in range(tabela.rowCount()):
                nome_redis = self.obter_texto_tabela(tabela, linha, 0)
                ip = self.obter_texto_tabela(tabela, linha, 1)
                port = self.obter_texto_tabela(tabela, linha, 2)

                if any([nome_redis, ip, port]):
                    instancias.append({
                        "nome_redis": nome_redis,
                        "ip": ip,
                        "port": port,
                    })

            redis_qa[grupo] = instancias

        return redis_qa

    def obter_texto_tabela(self, tabela, linha, coluna):
        item = tabela.item(linha, coluna)

        if item is None:
            return ""

        return item.text().strip()

    def limpar_formulario(self):
        self.input_versao.clear()
        self.input_data.clear()
        self.input_comentario.clear()
        self.input_database_update_br.clear()
        self.input_database_update_pt.clear()
        self.input_database_update_mx.clear()
        self.input_database_update_md.clear()
        self.preencher_tabela(self.tabela_bases, [], [""])
        self.preencher_tabela(self.tabela_conexoes, [], ["", "", "", ""])
        self.preencher_redis({})
        self.label_status_config.setVisible(False)

    def limpar_grupos_redis(self):
        self.combo_grupo_redis.blockSignals(True)
        self.combo_grupo_redis.clear()
        self.combo_grupo_redis.blockSignals(False)

        for tabela in self.tabelas_redis.values():
            self.container_tabela_redis.removeWidget(tabela)
            tabela.deleteLater()

        self.tabelas_redis.clear()

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
