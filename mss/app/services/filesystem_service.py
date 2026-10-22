import os
from app.core.constants import (
    NM_PASTA_LOG,
    NM_PASTA_CONFIG,
    NM_PASTA_ARQUIVO,
)

class FileSystemService:
    def __init__(self):
        pass

    def validar_diretorio(self):
        diretorios = {
            "log": NM_PASTA_LOG,
            "config": NM_PASTA_CONFIG,
            "txt": NM_PASTA_ARQUIVO
        }
        erros = []
        for nome, caminho in diretorios.items():
            try:
                os.makedirs(caminho, exist_ok=True)
            except Exception as error:
                erros.append(
                    f"Erro ao criar/validar a pasta '{nome}' ({caminho}): {error}"
                )

        if erros:
            raise RuntimeError("\n".join(erros))

        return True
