from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QComboBox,
    QLineEdit,
    QCheckBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QHBoxLayout,
    QSizePolicy
)


class GeradorDocumentosPage(QWidget):
    def __init__(self):
        super().__init__()
        self._page_montada = False

    def montar_tela(self):

        if self._page_montada:
            return

        self.setObjectName("GeradorDocumentosPage")

        titulo = QLabel("Gerar Documentos")
        titulo.setObjectName("pageTitle")

        descricao = QLabel("Selecione o tipo de documento e informe a quantidade para geração.")
        descricao.setObjectName("pageDescription")

        # 1 - ComboBox Documentos
        self.combo_documentos = QComboBox()
        self.combo_documentos.addItem("Selecione um documento")
        self.combo_documentos.addItems([
            "CEI",
            "CNPJ",
            "CPF",
            "NIF",
            "PIS"
        ])
        self.combo_documentos.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        # 2 - Campo editável Quantidade
        self.input_quantidade = QLineEdit()
        self.input_quantidade.setPlaceholderText("Ex: 10")
        self.input_quantidade.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        # 3 - Checkbox Gerar com máscara
        self.check_gerar_mascara = QCheckBox("Gerar com máscara")

        # 4 - Checkbox Gerar em arquivo txt
        self.check_gerar_txt = QCheckBox("Gerar em arquivo TXT")

        # 5 - Campo Saída não editável
        self.output_saida = QPlainTextEdit()
        self.output_saida.setReadOnly(True)
        self.output_saida.setPlaceholderText("A saída da rotina será exibida aqui...")

        btn_limpar_saida = QPushButton("Limpar saída")
        btn_executar = QPushButton("Executar")

        btn_limpar_saida.clicked.connect(self.output_saida.clear)
        btn_executar.clicked.connect(self.executar_rotina)

        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(12)

        form_layout.addWidget(QLabel("Documentos"), 0, 0)
        form_layout.addWidget(self.combo_documentos, 0, 1)

        form_layout.addWidget(QLabel("Quantidade"), 1, 0)
        form_layout.addWidget(self.input_quantidade, 1, 1)

        form_layout.addWidget(self.check_gerar_mascara, 2, 1)
        form_layout.addWidget(self.check_gerar_txt, 3, 1)

        # Coluna 0 fica para labels, coluna 1 expande com os campos
        form_layout.setColumnStretch(0, 0)
        form_layout.setColumnStretch(1, 1)

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
        documento = self.combo_documentos.currentText()
        quantidade = self.input_quantidade.text()
        gerar_mascara = self.check_gerar_mascara.isChecked()
        gerar_txt = self.check_gerar_txt.isChecked()

        self.output_saida.appendPlainText("Iniciando geração de documentos...")
        self.output_saida.appendPlainText(f"Documento: {documento}")
        self.output_saida.appendPlainText(f"Quantidade: {quantidade}")
        self.output_saida.appendPlainText(f"Gerar com máscara: {gerar_mascara}")
        self.output_saida.appendPlainText(f"Gerar em TXT: {gerar_txt}")
        self.output_saida.appendPlainText("Rotina finalizada.")