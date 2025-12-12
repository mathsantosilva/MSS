from mss.core.services.service_result import ServiceResult, Status
from mss.utils.datetime_utils import data_hora_atual
from mss.core.constants import MSS_ERRO_CAMPO_VAZIO, PLACEHOLDER_TEXT_ARQUIVO, MSS_ERRO_ARQUIVO_EXISTENTE, MENSAGEM_DEFAULT_JSON, VERSION_JSON, MSS_SUCESSO_CRIACAO_CONFIG,MSS_SUCESSO_CRIACAO_JSON, COLOR_DEAFULT, COLOR_DEAFULT_NAVS, COLOR_DEAFULT_FONTE
from mss.infrastructure.logging import escrever_arquivo_texto_log
from mss.utils.file_utils import escrever_arquivo_texto_config
from configparser import ConfigParser
import json
import os

class ConfigRepository:
    def __init__(self, pasta_config: str):
        self.pasta_config = pasta_config

    def ler_config_prog(self, nome_arquivo: str, nomes):
        caminho_log = os.path.join(nomes.get("diretorio_config"), nome_arquivo)
        config = ConfigParser()
        config.read(caminho_log)

    def salvar_config_prog(self, nome_arquivo_json: str, nomes: dict) -> ServiceResult:
        erros: list[str] = []
        agora_config = data_hora_atual()
        caminho_log = os.path.join(nomes.get("diretorio_log", ""), nomes.get("arquivo_base_muro", ""))
        # Log da entrada da rotina
        escrever_arquivo_texto_log(
            caminho_log,
            "INFO - Rotina - Criação de config"
        )

        if not nome_arquivo_json or nome_arquivo_json == PLACEHOLDER_TEXT_ARQUIVO:
            mensagem_erro = f"{data_hora_atual()} - {MSS_ERRO_CAMPO_VAZIO}"
            erros.append(mensagem_erro)

            # Log do erro
            escrever_arquivo_texto_log(
                caminho_log,
                f"AVISO - Falha ao criar config: {mensagem_erro}"
            )

            return ServiceResult(
                status=Status.AVISO,
                mensagem="\n".join(erros),
            )
        if not nome_arquivo_json.lower().endswith(".conf"):
            nome_arquivo_json += ".conf"

        caminho_arquivo = os.path.join(nomes.get("diretorio_config", ""), nome_arquivo_json)

        if os.path.exists(caminho_arquivo):
            mensagem_erro = f"{data_hora_atual()} - {MSS_ERRO_ARQUIVO_EXISTENTE}"
            erros.append(mensagem_erro)

            escrever_arquivo_texto_log(
                caminho_log,
                f"AVISO - {MSS_ERRO_ARQUIVO_EXISTENTE}: {caminho_arquivo}"
            )

            return ServiceResult(
                status=Status.AVISO,
                mensagem="\n".join(erros),
            )

        # Monta JSON base
        arquivo_config = f"""[ConfiguracoesGerais]
config_default = 
data_ultima_atualizacao =

[ConfiguracoesAparencia]
background_color_fundo = {COLOR_DEAFULT}
background_color_titulos = {COLOR_DEAFULT}
background_color_botoes = {COLOR_DEAFULT}
background_color_botoes_navs = {COLOR_DEAFULT_NAVS}
background_color_fonte = {COLOR_DEAFULT_FONTE}"""

        escrever_arquivo_texto_config(caminho_arquivo, arquivo_config)

        escrever_arquivo_texto_log(
            caminho_log,
            f"INFO - config criado com sucesso: {nome_arquivo_json}"
        )

        return ServiceResult(
            status=Status.SUCESSO,
            mensagem=MSS_SUCESSO_CRIACAO_CONFIG,
        )

    def ler_config_json(self, nome_arquivo: str) -> dict:
        ...

    def salvar_config_json(self, nome_arquivo_json: str, nomes: dict | str):
        erros: list[str] = []
        agora_config = data_hora_atual()
        caminho_log = os.path.join(nomes.get("diretorio_log", ""), nomes.get("arquivo_base_muro", ""))
        # Log da entrada da rotina
        escrever_arquivo_texto_log(
            caminho_log,
            "INFO - Rotina - Criação de json"
        )

        if not nome_arquivo_json or nome_arquivo_json == PLACEHOLDER_TEXT_ARQUIVO:
            mensagem_erro = f"{data_hora_atual()} - {MSS_ERRO_CAMPO_VAZIO}"
            erros.append(mensagem_erro)

            # Log do erro
            escrever_arquivo_texto_log(
                caminho_log,
                f"AVISO - Falha ao criar json: {mensagem_erro}"
            )

            return ServiceResult(
                status=Status.AVISO,
                mensagem="\n".join(erros),
            )
        if not nome_arquivo_json.lower().endswith(".json"):
            nome_arquivo_json += ".json"

        caminho_arquivo = os.path.join(nomes.get("diretorio_config", ""), nome_arquivo_json)

        if os.path.exists(caminho_arquivo):
            mensagem_erro = f"{data_hora_atual()} - {MSS_ERRO_ARQUIVO_EXISTENTE}"
            erros.append(mensagem_erro)

            escrever_arquivo_texto_log(
                caminho_log,
                f"AVISO - {MSS_ERRO_ARQUIVO_EXISTENTE}: {caminho_arquivo}"
            )

            return ServiceResult(
                status=Status.AVISO,
                mensagem="\n".join(erros),
            )

        # Monta JSON base
        payload = {
            "controle_versao_json": {
                "versao": VERSION_JSON,
                "data": agora_config,
                "comentario": MENSAGEM_DEFAULT_JSON,
            },
            "bancos_update": {
                "database_update_br": "",
                "database_update_mx": "",
                "database_update_pt": "",
                "database_update_md": "",
            },
            "bases_muro": [
                ""
            ],
            "conexoes": [
                {
                    "nome": "",
                    "server": "",
                    "username": "",
                    "password": "",
                }
            ],
            "redis_qa": {
                "grupo_1": [
                    {"nome_redis": "", "ip": "", "port": ""},
                    {"nome_redis": "", "ip": "", "port": ""},
                ],
                "grupo_2": [
                    {"nome_redis": "", "ip": "", "port": ""},
                    {"nome_redis": "", "ip": "", "port": ""},
                ],
            },
        }

        escrever_arquivo_texto_config(caminho_arquivo, json.dumps(payload, ensure_ascii=False, indent=2))

        escrever_arquivo_texto_log(
            caminho_log,
            f"INFO - json criado com sucesso: {nome_arquivo_json}"
        )

        return ServiceResult(
            status=Status.SUCESSO,
            mensagem=MSS_SUCESSO_CRIACAO_JSON,
        )