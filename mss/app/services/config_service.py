# config_service.py
import configparser
import json
import os
from pathlib import Path

from datetime import datetime
from app.core.settings import (
    AppearanceSettings,
    ConnectionSettings,
    DatabaseUpdateSettings,
    JsonMetadataSettings,
    ProgramSettings,
    RedisGroupSettings,
    RedisInstanceSettings,
    Settings,
)
from app.core.constants import (
    NM_PASTA_CONFIG,
    NM_ARQUIVO_CONFIG,
    JSON_VERSION,
    NM_ARQUIVO_JSON_FIXO,
    NOTES_JSON,
    COLOR_BTN,
    COLOR_FONT_BTN,
    COLOR_TITLE,
    COLOR_BACKGROUND,
)

class ConfigService:
    def __init__(self):
        pass

    def load(self, config_selecionado=None) -> Settings:
        path_config = os.path.join(NM_PASTA_CONFIG, NM_ARQUIVO_JSON_FIXO)
        if not os.path.exists(path_config):
            legacy_config = self.load_prog_conf()
            if legacy_config:
                nome_json = legacy_config.get('ConfiguracoesGerais', 'config_default')
                json_config = self.load_json_config(nome_json)
                config_json_fixo = self.create_config_json(legacy_config, nome_json)
            else:
                config_json_fixo = self.create_config_json()
                return self.build_settings(config_json_fixo)
        else:
            config_json_fixo = self.load_json_config_fixo(path_config)
            if not isinstance(config_json_fixo, dict):
                return self.build_settings(config_json_fixo)

            if config_selecionado:
                json_config = self.load_json_config(config_selecionado)
                config_json_fixo['selected_config'] = config_selecionado
                self.update_config_selecionado(config_json_fixo)
            else:
                nome_json = config_json_fixo.get('selected_config')
                if nome_json:
                    json_config = self.load_json_config(nome_json)
                else:
                    return self.build_settings(config_json_fixo)
            if not isinstance(json_config, dict):
                return self.build_settings(config_json_fixo)


        return self.build_settings(config_json_fixo, json_config)

    def load_prog_conf(self):
        caminhos = [
            Path(NM_PASTA_CONFIG) / NM_ARQUIVO_CONFIG,
            Path("Config") / NM_ARQUIVO_CONFIG,
        ]

        for path_config in caminhos:
            if not path_config.is_file():
                continue

            config = configparser.ConfigParser()
            arquivos_lidos = config.read(path_config, encoding="utf-8")
            if arquivos_lidos:
                return config

        return None

    def load_json_config(self, nome_json):
        try:
            path_config = os.path.join(NM_PASTA_CONFIG, nome_json)
            with open(path_config, "r") as file:
                json_config = json.load(file)

        except Exception as error:
            print(error)
            return error

        return json_config

    def load_json_config_fixo(self, path_json_fixo):
        try:
            with open(path_json_fixo, "r") as file:
                json_config = json.load(file)

        except Exception as error:
            print(error)
            return error

        return json_config

    def update_config_json_fixo(self, config_json):
        status = {"sucesso": False, "msg_erros": []}
        path_config = os.path.join(NM_PASTA_CONFIG, NM_ARQUIVO_JSON_FIXO)
        try:
            with open(path_config, "w") as file:
                json.dump(config_json, file, indent=4, ensure_ascii=False)
                status["sucesso"] = True
        except Exception as error:
            status["msg_erros"].append(error)

        return status

    def create_config_json(self, legacy_config=None, nome_json=""):
        data_hora = datetime.now().strftime("%d-%m-%Y")
        path_config = os.path.join(NM_PASTA_CONFIG, NM_ARQUIVO_JSON_FIXO)
        if legacy_config and nome_json:
            background_color_fundo = legacy_config.get('ConfiguracoesAparencia', 'background_color_fundo')
            background_color_titulos = legacy_config.get('ConfiguracoesAparencia', 'background_color_titulos')
            background_color_botoes = legacy_config.get('ConfiguracoesAparencia', 'background_color_botoes')
            background_color_botoes_navs = legacy_config.get('ConfiguracoesAparencia', 'background_color_botoes_navs')
            background_color_fonte = legacy_config.get('ConfiguracoesAparencia', 'background_color_fonte')

            config = {
                    "selected_config": nome_json,
                    "last_update_check": data_hora,
                    "version": JSON_VERSION,
                    "notes": NOTES_JSON,
                    "appearance": {
                        "colors": {
                            "window_background": background_color_fundo,
                            "title_background": background_color_titulos,
                            "button_background": background_color_botoes,
                            "nav_button_background": background_color_botoes_navs,
                            "text": background_color_fonte
                        }
                    }
                }
        else:
            config = {
                    "selected_config": "",
                    "last_update_check": data_hora,
                    "version": JSON_VERSION,
                    "notes": NOTES_JSON,
                    "appearance": {
                        "colors": {
                            "window_background": COLOR_BACKGROUND,
                            "title_background": COLOR_TITLE,
                            "button_background": COLOR_BTN,
                            "nav_button_background": COLOR_BTN,
                            "text": COLOR_FONT_BTN
                        }
                    }
                }
        try:
            with open(path_config, "w") as file:
                json.dump(config, file, indent=4, ensure_ascii=False)
        except Exception as error:
            print(error)

        return config

    def build_settings(self, config_json_fixo=None, json_config=None):
        if not isinstance(config_json_fixo, dict):
            config_json_fixo = {}

        if not isinstance(json_config, dict):
            json_config = {}

        colors = config_json_fixo.get("appearance", {}).get("colors", {})
        metadata = json_config.get("controle_versao_json", {})
        bancos_update = json_config.get("bancos_update", {})

        return Settings(
            program=ProgramSettings(
                selected_config=config_json_fixo.get("selected_config", ""),
                last_update_check=config_json_fixo.get("last_update_check", ""),
                version=config_json_fixo.get("version", ""),
                notes=config_json_fixo.get("notes", ""),
                check_updates_on_startup=config_json_fixo.get(
                    "check_updates_on_startup",
                    True
                ),
            ),
            appearance=AppearanceSettings(
                window_background=colors.get("window_background", COLOR_BACKGROUND),
                title_background=colors.get("title_background", COLOR_TITLE),
                button_background=colors.get("button_background", COLOR_BTN),
                nav_button_background=colors.get("nav_button_background", COLOR_BTN),
                text=colors.get("text", COLOR_FONT_BTN),
            ),
            json_metadata=JsonMetadataSettings(
                version=metadata.get("versao", ""),
                date=metadata.get("data", ""),
                comment=metadata.get("comentario", ""),
            ),
            database_updates=DatabaseUpdateSettings(
                br=bancos_update.get("database_update_br", ""),
                pt=bancos_update.get("database_update_pt", ""),
                mx=bancos_update.get("database_update_mx", ""),
                md=bancos_update.get("database_update_md", ""),
            ),
            wall_databases=json_config.get("bases_muro", []),
            connections=[
                ConnectionSettings(
                    name=connection.get("nome", ""),
                    server=connection.get("server", ""),
                    username=connection.get("username", ""),
                    password=connection.get("password", ""),
                )
                for connection in json_config.get("conexoes", [])
            ],
            redis_groups=self.build_redis_groups(json_config.get("redis_qa", {})),
        )

    def build_redis_groups(self, redis_qa):
        groups = []

        for group_name, instances in redis_qa.items():
            groups.append(
                RedisGroupSettings(
                    name=group_name,
                    instances=[
                        RedisInstanceSettings(
                            name=instance.get("nome_redis", ""),
                            ip=instance.get("ip", ""),
                            port=self.parse_port(instance.get("port")),
                        )
                        for instance in instances
                        if instance.get("nome_redis")
                    ],
                )
            )

        return groups

    def parse_port(self, port):
        if not port:
            return 0

        return int(port)

    def update_config_selecionado(self, config_json_fixo):
        path_json_fixo = os.path.join(NM_PASTA_CONFIG, NM_ARQUIVO_JSON_FIXO)
        try:
            with open(path_json_fixo, "w") as file:
                json.dump(config_json_fixo, file, indent=4, ensure_ascii=False)

        except Exception as error:
            print(error)
            return error

    def buscar_lista_configuracoes(self):
        path_config = Path(NM_PASTA_CONFIG)
        if not path_config.exists():
            return {}
        arquivos = os.listdir(path_config)
        arquivos_formatado_json = {}
        for arquivo in arquivos:
            if arquivo != "mss_config.json":
                path = path_config / arquivo
                formato = path.suffix.lower()
                if formato == ".json":
                    arquivos_formatado_json[arquivo] = path
        return arquivos_formatado_json

    def carregar_arquivo_json(self, nome_arquivo, arquivos_jsons):
        status = {"sucesso": False, "texto": '', "json": dict(), "msg_erro": ''}
        arquivo_lista_json = arquivos_jsons
        caminho_json = arquivos_jsons.get(nome_arquivo)


        if nome_arquivo == "Selecione um arquivo":
            return status

        if not arquivo_lista_json:
            status["msg_erro"] = "A lista de arquivos esta vazia"
            return status

        if nome_arquivo not in arquivo_lista_json:
            status["msg_erro"] = "Arquivo de configuração não encontrado na lista."
            return status

        if not caminho_json.exists():
            status["msg_erro"] =  f"Arquivo não encontrado:\n{caminho_json}"
            return status

        try:
            with open(caminho_json, "r", encoding="utf-8") as arquivo:
                conteudo = json.load(arquivo)

            conteudo_formatado = json.dumps(
                conteudo,
                indent=4,
                ensure_ascii=False
            )

            status["sucesso"] = True
            status["texto"] = conteudo_formatado
            status["json"] = conteudo

        except json.JSONDecodeError as erro:
            status["msg_erro"] = f"Erro ao ler JSON:\n{erro}"
            return status
        except Exception as erro:
            status["msg_erro"] =  f"Erro inesperado ao abrir arquivo:\n{erro}"
            return status

        return status
