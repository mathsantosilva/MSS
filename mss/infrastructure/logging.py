import os
from pathlib import Path
from mss.utils.datetime_utils import data_hora_atual
from mss.core.services.service_result import ServiceResult, Status
from mss.core.constants import MSG_DIRETORIOS_OK, MSG_ERRO_CRIAR_PASTA, MSS_ERRO_CRIAR_ARQUIVO, MSS_SUCESSO_CRIACAO_ARQUIVO

def validar_linha(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        conteudo = f.read()
    linhas = conteudo.count("\n") + 1 if conteudo else 0
    return "" if linhas <= 0 else "\n"

def validar_diretorio(nomes: dict) -> ServiceResult:
    erros = []

    for nome_chave in ["diretorio_log", "diretorio_config", "diretorio_txt"]:
        caminho = nomes.get(nome_chave)
        try:
            if caminho and not os.path.exists(caminho):
                os.makedirs(caminho)
        except Exception as error:
            erros.append(
                f"{data_hora_atual()} - {MSG_ERRO_CRIAR_PASTA} '{caminho}': {error}"
            )

    if erros:
        # Retorna erro sem chamar popup
        return ServiceResult(
            status=Status.ERRO,
            mensagem="\n".join(erros)
        )

    return ServiceResult(
        status=Status.SUCESSO,
        mensagem=MSG_DIRETORIOS_OK
    )

def escrever_arquivo_texto_log(caminho: str | Path, conteudo: str)  -> ServiceResult:
    erros = []
    encoding = "utf-8"
    path = Path(caminho)
    path.parent.mkdir(parents=True, exist_ok=True)

    pula_linha = validar_linha(path)

    try:
        with path.open("a", encoding=encoding) as f:
            f.write(f"{pula_linha}{conteudo}")
    except Exception as error:
        erros.append(
            f"{data_hora_atual()} - {MSS_ERRO_CRIAR_ARQUIVO} '{path}': {error}"
        )
    if erros:
        # Retorna erro sem chamar popup
        return ServiceResult(
            status=Status.ERRO,
            mensagem="\n".join(erros)
        )

    return ServiceResult(
        status=Status.SUCESSO,
        mensagem=MSS_SUCESSO_CRIACAO_ARQUIVO
    )
