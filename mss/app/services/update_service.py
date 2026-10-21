import shutil

from app.core.settings import Settings
from app.services.config_service import ConfigService
from app.services.util_service import UtilService
from github import Github
from datetime import datetime
import hashlib
import subprocess
import requests
import re
import configparser
import os
from app.core.constants import (
    NM_PASTA_CONFIG,
    NM_ARQUIVO_JSON_FIXO,
    APP_VERSION,
    PATH_PROG,
    APP_NAME_EXTENSION,
    PATH_TEMP_APP,
    APP_NAME_EXTENSION_LEGACY,
    FORMATO_DATA,
)

class update_service:
    def __init__(self, settings):
        self.util_service = UtilService()
        self.config_service = ConfigService()
        self.settings = settings

    def validar_data_atualizacao_config(self):
        status = {"sucesso": False, "msg_erros": []}
        data_atual = self.util_service.data_atual()
        path_config = os.path.join(NM_PASTA_CONFIG, NM_ARQUIVO_JSON_FIXO)
        if os.path.isfile(path_config):
            try:
                config_json = self.config_service.load_json_config_fixo(path_config)
                data_ultima_atualizacao = datetime.strptime(config_json.get("last_update_check"), FORMATO_DATA).date()
                if data_ultima_atualizacao < data_atual:
                    self.settings.program.check_updates_on_startup = True
                    status["sucesso"] = True
                    return status
                else:
                    self.settings.program.check_updates_on_startup = False
                    status["sucesso"] = True
                    return status
            except Exception as error:
                status["msg_erros"].append(f"Erro ao validar a ultima atualização: {error}")
                self.settings.program.check_updates_on_startup = False
                return status
        else:
            self.settings.program.check_updates_on_startup = False
            status["sucesso"] = True
            return status

    def alterar_data_atualizacao_config(self):
        status = {"sucesso": False, "msg_erros": []}
        data_atual = self.util_service.data_atual().strftime(FORMATO_DATA)
        path_config = os.path.join(NM_PASTA_CONFIG, NM_ARQUIVO_JSON_FIXO)
        try:
            config_json = self.config_service.load_json_config_fixo(path_config)
            config_json["last_update_check"] = data_atual
            resultado_atualizacao = self.config_service.update_config_json_fixo(config_json)
            status = resultado_atualizacao
        except Exception as error:
            status["msg_erros"].append(error)

        return status

    def atualizador(self):
        status = {"sucesso": False, "msg_erros": []}

        if self.settings.program.check_updates_on_startup:
            username = "mathsantosilva"
            repository = "MSS"
            tag_atual = APP_VERSION
            ultima_release = self.pesquisar_ultima_release(username, repository, tag_atual)
            if ultima_release:
                if os.path.exists(PATH_TEMP_APP):
                    shutil.rmtree(PATH_TEMP_APP)
                    os.makedirs(PATH_TEMP_APP)
                else:
                    os.makedirs(PATH_TEMP_APP)
                asset = self.buscar_asset_release(ultima_release)
                if isinstance(asset, dict):
                    resultado_download = self.realizar_download(ultima_release, asset)
                    if resultado_download.get("sucesso"):
                        self.executar_comando_batch(asset)
                        self.alterar_data_atualizacao_config()
                        self.util_service.finalizar()
                else:
                    status["sucesso"] = False
                    status["msg_erros"].append(f"Asset não retornado")
            else:
                try:
                    if os.path.exists(PATH_TEMP_APP):
                        shutil.rmtree(PATH_TEMP_APP)
                    status["sucesso"] = True
                except Exception as error:
                    status["sucesso"] = False
                    status["msg_erros"].append(f"Erro ao criar/validar a pasta: {error}")

        return status

    def comparar_tags(self, tag1, tag2):
        # Função para comparar duas tags no formato 'x.y.z'
        # retornar 1 se a primeira for maior, -1 se for menor e 0 se forem iguais

        tag1_limpa = re.sub(r"[^0-9.]", "", tag1)
        tag2_limpa = re.sub(r"[^0-9.]", "", tag2)
        version_regex = r"(\d+)\.(\d+)\.(\d+)"
        match1 = re.match(version_regex, tag1_limpa)
        match2 = re.match(version_regex, tag2_limpa)

        if match1 and match2:
            version1 = tuple(map(int, match1.groups()))
            version2 = tuple(map(int, match2.groups()))

            if version1 > version2:
                return 1
            elif version1 < version2:
                return -1

        return 0

    def pesquisar_ultima_release(self, username, repository, tag_atual):
        github = Github()
        tag_lastest_release = ''
        tag_git = ''
        try:
            restantes, limite = github.rate_limiting
            if restantes > 0:
                repo = github.get_repo(f"{username}/{repository}")
                latest_release = repo.get_latest_release()
                tag_lastest_release = latest_release.tag_name
        except Exception as error:
            print(f"Erro ao consultar tags para atualização: {error}")
            print(f"ERRO - Erro ao consultar tags para atualização: {error}")
        else:
            try:
                if self.comparar_tags(tag_lastest_release, tag_atual) > 0:
                    return tag_lastest_release
                else:
                    return tag_git
            except Exception as error:
                print(f"Erro ao consultar tags para atualização: {error}")
                print(f"ERRO - Erro ao consultar tags para atualização: {error}")

    def realizar_download(self, maior_tag, asset):
        status = {"sucesso": False, "msg_erros": []}
        timeout = 3000
        path_arquivo = os.path.join(PATH_TEMP_APP, asset.get("name"))
        try:
            caminho = f"https://github.com/mathsantosilva/MSS/releases/download/{maior_tag}/{asset.get("name")}"
            response = requests.get(caminho, timeout=timeout)
        except Exception as error:
            status["sucesso"] = False
            status["msg_erros"].append(f"Erro ao consultar tags para atualização: {error}")
        else:
            if response.status_code == 200:
                with open(path_arquivo, "wb") as arquivo:
                    arquivo.write(response.content)
                checksum_esperado = asset.get("digest")
                if checksum_esperado:
                    resultado_checksum = self.validar_checksum(path_arquivo, checksum_esperado)
                    if resultado_checksum:
                        status["sucesso"] = True
            else:
                status["sucesso"] = False
                status["msg_erros"].append(f"A requisição respondeu status code: {response.status_code}")
        return status

    def executar_comando_batch(self, asset):
        nome_script = "script_temp.bat"
        arquivos = os.listdir(PATH_PROG)
        nome_programa = ''
        for arquivo in arquivos:
            if arquivo.lower() == "mss.exe" or arquivo.lower() == "buscamuro.exe":
                nome_programa = arquivo
        arquivos_formatado_json = {}
        comando = f"""@echo off
        chcp 65001 >nul
        cls

        echo ==========================================
        echo   Atualizacao em andamento
        echo ==========================================
        echo.

        echo Aguarde enquanto a atualizacao e realizada...
        echo.

        timeout /t 2 /nobreak >nul

        copy /Y "{PATH_TEMP_APP}\\{asset.get("name")}" "{PATH_PROG}\\{nome_programa}"

        if errorlevel 1 (
            echo.
            echo [ERRO] Nao foi possivel concluir a atualizacao.
            echo Verifique se o programa esta aberto ou se voce possui permissao.
            echo.
            pause
            exit /b 1
        )

        echo.
        echo Atualizacao realizada com sucesso.
        echo.
        pause
        exit /b 0
        """
        arquivo = open(f"{PATH_TEMP_APP}/{nome_script}", "a", encoding="UTF-8")
        arquivo.write(comando)
        arquivo.close()
        subprocess.Popen(['start', 'cmd', '/k', f'{PATH_TEMP_APP}/{nome_script}'], shell=True, text=True)

    def buscar_asset_release(self, tag):
        url = f"https://api.github.com/repos/mathsantosilva/MSS/releases/tags/{tag}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        release = response.json()

        for asset in release.get("assets", []):
            if asset.get("name") == APP_NAME_EXTENSION_LEGACY or asset.get("name") == APP_NAME_EXTENSION:
                return asset

        return None

    def calcular_sha256(self, path_arquivo):
        sha256 = hashlib.sha256()

        with open(path_arquivo, "rb") as arquivo:
            for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
                sha256.update(bloco)

        return f"sha256:{sha256.hexdigest()}"

    def validar_checksum(self, path_arquivo, checksum_esperado):
        if not os.path.isfile(path_arquivo):
            return False

        checksum_atual = self.calcular_sha256(path_arquivo)
        return checksum_atual.lower() == checksum_esperado.strip().lower()