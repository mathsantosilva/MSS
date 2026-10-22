from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QComboBox,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QHBoxLayout,
    QSizePolicy
)


class ValidadorDocumentosPage(QWidget):
    def __init__(self):
        super().__init__()
        self._page_montada = False

    def montar_tela(self):

        if self._page_montada:
            return

        self.setObjectName("ValidadorDocumentosPage")

        titulo = QLabel("Validar Documentos")
        titulo.setObjectName("pageTitle")

        descricao = QLabel("Selecione o tipo de documento e informe o documentos para validação.")
        descricao.setObjectName("pageDescription")

        # 1 - ComboBox Documentos
        self.combo_tipo_documentos = QComboBox()
        self.combo_tipo_documentos.addItem("Selecione um documento")
        self.combo_tipo_documentos.addItems([
            "CEI",
            "CNPJ",
            "CPF",
            "NIF",
            "PIS"
        ])
        self.combo_tipo_documentos.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        # 2 - Campo editável Quantidade
        self.input_documentos = QLineEdit()
        self.input_documentos.setPlaceholderText("Ex: 000.000.000-00 ou 00000000000")
        self.input_documentos.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        # 3 - Campo Saída não editável
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

        form_layout.addWidget(QLabel("Tipo Documento"), 0, 0)
        form_layout.addWidget(self.combo_tipo_documentos, 0, 1)

        form_layout.addWidget(QLabel("Documento"), 1, 0)
        form_layout.addWidget(self.input_documentos, 1, 1)


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
        tipo_documento = self.combo_tipo_documentos.currentText()
        documento = self.input_documentos.text()

        self.output_saida.appendPlainText("Iniciando Validação de documentos...")
        self.output_saida.appendPlainText(f"Tipo Documento: {tipo_documento}")
        self.output_saida.appendPlainText(f"Documento: {documento}")
        self.output_saida.appendPlainText("Rotina finalizada.")