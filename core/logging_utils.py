from core.filesystem import FileSystem
from core.clock import Clock
import os

class Logger:
    def __init__(self, nomes: dict, fs: FileSystem):
        self.nomes = nomes
        self.fs = fs

    def escrever_arquivo_log(self, popup, nome_arquivo: str, texto: str):
        self.fs.validar_diretorio(self.nomes, popup)
        pula = self.fs.validar_linha(self.nomes['diretorio_log'], nome_arquivo)
        path = os.path.join(self.nomes['diretorio_log'], f"{nome_arquivo}.txt")
        self.fs.escrever_arquivo_txt(path, f"{pula}{Clock.data_hora_atual()} - {texto}")
