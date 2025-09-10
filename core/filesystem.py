import os

class FileSystem:
    def validar_linha(self, diretorio: str, nome: str) -> str:
        with open(f"{diretorio}\\{nome}.txt", "r") as f:
            conteudo = f.read()
            linhas = conteudo.count("\n") + 1
            caracteres = conteudo.count("")
        return "" if (linhas == 1 and caracteres == 1) else "\n"

    def validar_diretorio(self, nomes: dict, popup):
        for key in ("diretorio_log", "diretorio_config", "diretorio_txt"):
            try:
                os.makedirs(nomes[key], exist_ok=True)
            except Exception as e:
                popup(f"Erro ao criar/validar a pasta {nomes[key]}: {e}")

    def escrever_arquivo_txt(self, path: str, texto: str):
        with open(path, "a", encoding="utf-8") as f:
            f.write(texto)
