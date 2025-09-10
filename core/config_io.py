import json, os, configparser
from core.clock import Clock

class ConfigIO:
    def __init__(self, nomes: dict, popup, logger):
        self.nomes = nomes
        self.popup = popup
        self.log = logger

    def escrever_arquivo_config(self, nome_arquivo, texto, extensao):
        path = f"{self.nomes['diretorio_config']}\\{nome_arquivo}.{extensao}"
        with open(path, "w", encoding="utf-8") as f: f.write(texto)

    # mova criar_config, atualizar_arquivo_json, ler_parametros_arquivo_json,
    # escolher_config_existente, criar_arquivo_config_prog, atualizar_config_default,
    # salvar_alteracoes_config, ler_arquivo_config, alterar_data_atualizacao_config,
    # validar_data_atualizacao_config para métodos desta classe
