from pathlib import Path
from mss.utils.datetime_utils import data_hora_atual
from mss.core.constants import MSS_ERRO_CRIAR_ARQUIVO, MSS_SUCESSO_CRIACAO_ARQUIVO
from mss.core.services.service_result import ServiceResult, Status

def escrever_arquivo_texto_config(caminho: str | Path, conteudo: str) -> ServiceResult:
    erros = []
    encoding = "utf-8"
    path = Path(caminho)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with path.open("w", encoding=encoding) as f:
            f.write(conteudo)
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