from PySide6.QtGui import QAction


class AppMenuBar:
    def __init__(self, main_window):
        self.main_window = main_window
        self.menu_bar = main_window.menuBar()

        self.criar_menus()

    def criar_menus(self):
        self.criar_menu_configuracao()
        self.criar_menu_aparencia()

    def criar_menu_configuracao(self):
        menu_configuracao = self.menu_bar.addMenu("Configuração")

        action_abrir_config = QAction("Trocar arquivo de Configuração", self.main_window)
        action_sair = QAction("Sair", self.main_window)

        action_sair.triggered.connect(self.main_window.close)

        menu_configuracao.addAction(action_abrir_config)
        menu_configuracao.addSeparator()
        menu_configuracao.addAction(action_sair)

    def criar_menu_aparencia(self):
        menu_aparencia = self.menu_bar.addMenu("Aparência")

        action_tema_claro = QAction("Tema claro", self.main_window)
        action_tema_escuro = QAction("Tema escuro", self.main_window)

        menu_aparencia.addAction(action_tema_claro)
        menu_aparencia.addAction(action_tema_escuro)