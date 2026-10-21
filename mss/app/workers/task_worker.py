from PySide6.QtCore import QThread, Signal


class TaskWorker(QThread):
    progresso = Signal(str)
    finalizado = Signal(str)
    erro = Signal(str)

    def __init__(self, funcao, *args, **kwargs):
        super().__init__()
        self.funcao = funcao
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.progresso.emit("Iniciando execução...")

            resultado = self.funcao(*self.args, **self.kwargs)

            self.finalizado.emit(str(resultado))

        except Exception as erro:
            self.erro.emit(str(erro))