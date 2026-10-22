from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame, QHBoxLayout, QPushButton
from PySide6.QtWidgets import QGridLayout


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self._page_montada = False

    def montar_tela(self):

        if self._page_montada:
            return

        self.setObjectName("dashboardPage")

        titulo = QLabel("Dashboard")
        titulo.setObjectName("pageTitle")

        descricao = QLabel("Acesse rapidamente os principais módulos do MSS BuscaMuro.")
        descricao.setObjectName("pageDescription")

        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        layout.addWidget(titulo)
        layout.addWidget(descricao)

        cards_layout = QGridLayout()
        cards_layout.setHorizontalSpacing(16)
        cards_layout.setVerticalSpacing(16)

        cards_layout.addWidget(self.criar_card(
            "Banco Muro",
            "Atualizações, versões e busca de empresas."
        ), 0,0)

        cards_layout.addWidget(self.criar_card(
            "Redis",
            "Limpeza de grupos ou instâncias específicas."
        ), 0, 1)

        cards_layout.addWidget(self.criar_card(
            "Documentos",
            "Geradores e validadores de documentos."
        ), 0, 2)

        cards_layout.addWidget(self.criar_card(
            "Empresas",
            "Realiza busca pelos dados da empresa."
        ), 1, 0)

        cards_layout.addWidget(self.criar_card(
            "Configuração",
            "Configurações do programa."
        ), 1, 1)

        cards_layout.setColumnStretch(0, 1)
        cards_layout.setColumnStretch(1, 1)
        cards_layout.setColumnStretch(2, 1)

        layout.addSpacing(16)
        layout.addLayout(cards_layout)
        layout.addStretch()

        self.setLayout(layout)

        self._page_montada = True

    def criar_card(self, titulo, descricao):
        card = QFrame()
        card.setObjectName("moduleCard")

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("cardTitle")

        lbl_descricao = QLabel(descricao)
        lbl_descricao.setObjectName("cardDescription")
        lbl_descricao.setWordWrap(True)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(10, 20, 20, 20)
        card_layout.setSpacing(8)

        card_layout.addWidget(lbl_titulo)
        card_layout.addWidget(lbl_descricao)
        card_layout.addStretch()

        card.setLayout(card_layout)

        return card