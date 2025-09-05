# coding: utf-8
from datetime import datetime
import json
import os
import re
import sys
from tkinter import colorchooser
from tkinter.ttk import *
from tkinter import *
import pyodbc
from github import Github
import requests
import shutil
import subprocess
import threading
import redis
import configparser
import random
import math
import time


# processos de atualização prog
def comparar_tags(tag1, tag2):
    # Função para comparar duas tags no formato 'x.y.z'
    # retornar 1 se a primeira for maior, -1 se for menor e 0 se forem iguais
    version_regex = r"(\d+)\.(\d+)\.(\d+)"
    match1 = re.match(version_regex, tag1)
    match2 = re.match(version_regex, tag2)

    if match1 and match2:
        version1 = tuple(map(int, match1.groups()))
        version2 = tuple(map(int, match2.groups()))

        if version1 > version2:
            return 1
        elif version1 < version2:
            return -1

    return 0

def pesquisar_maior_tag(username, repository, tag_atual, criar_popup_mensagem):
    github = Github()
    tags = []
    try:
        repo = github.get_repo(f"{username}/{repository}")
        tags_on = repo.get_tags()
        for tag_in in tags_on:
            tags.append(tag_in.name)
    except Exception as error:
        criar_popup_mensagem(f"Erro ao consultar tags para atualização: {error} ")
    else:
        maior_tag = None
        try:
            for tag in tags:
                if comparar_tags(tag, tag_atual) > 0:
                    if maior_tag is None or comparar_tags(tag, maior_tag) > 0:
                        maior_tag = tag
                        break
        except Exception as error:
            criar_popup_mensagem(f"Erro ao consultar tags para atualização: {error} ")

        return maior_tag

def realizar_download(maior_tag, criar_popup_mensagem):
    try:
        caminho = f"https://github.com/mathsantosilva/MSS/releases/download/{maior_tag}/BuscaMuro.exe"
        response = requests.get(caminho)
    except Exception as error:
        criar_popup_mensagem(f"Erro ao consultar tags para atualização: {error} ")
    else:
        try:
            if os.path.exists("C:/MSS_temp"):
                return
            else:
                os.makedirs("C:/MSS_temp")
        except Exception as error:
            criar_popup_mensagem(f"Erro ao criar/validar a pasta C:/MSS_temp: {error} ")
        with open("C:/MSS_temp/BuscaMuro.exe", "wb") as arquivo:
            arquivo.write(response.content)
            arquivo.close()

def executar_comando_batch(dir_atual):
    comando = f"""@echo off
chcp 65001
cls
echo Aguarde enquanto a atualização esta em andamento
xcopy "C:\\MSS_temp\\BuscaMuro.exe" "{dir_atual}\\BuscaMuro.exe" /w/E/Y/H
echo.
echo Atualização realizada com sucesso 
echo.
pause
exit
"""
    arquivo = open("C:/MSS_temp/script_temp.bat", "a", encoding="UTF-8")
    arquivo.write(comando)
    arquivo.close()
    subprocess.Popen(['start', 'cmd', '/k', 'C:/MSS_temp/script_temp.bat'], shell=True, text=True)

# Fechar janela pop_mensagem
def fechar_janela(msg):
    msg.destroy()

# Processos para obter datas/hora
def data_hora_atual():
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return data_hora

def data_atual():
    data_hora = datetime.now().strftime("%d-%m-%Y")
    return data_hora

# Processos para arquivos de log
def validar_linha(diretorio, nome):
    with open(f"{diretorio}\\{nome}.txt", "r") as arquivo_insp:
        conteudo = arquivo_insp.read()
        linhas = conteudo.count("\n") + 1
        caracteres = conteudo.count("")
    if linhas == 1 and caracteres == 1:
        pula_linha = ""
    else:
        pula_linha = "\n"

    return pula_linha

def validar_diretorio(nomes, criar_popup_mensagem):
    # Criar diretorio log
    try:
        if not os.path.exists(nomes['diretorio_log']):
            os.makedirs(nomes['diretorio_log'])
    except Exception as error:
        criar_popup_mensagem(
            f"\n{data_hora_atual()} - INFO - Erro ao criar/validar a pasta {nomes['diretorio_log']}: {error} ")

    # Criar diretorio config
    try:
        if not os.path.exists(nomes['diretorio_config']):
            os.makedirs(nomes['diretorio_config'])
    except Exception as error:
        criar_popup_mensagem(
            f"\n{data_hora_atual()} - INFO - Erro ao criar/validar a pasta {nomes['diretorio_config']}: {error} ")

    # Criar diretorio txt
    try:
        if not os.path.exists(nomes['diretorio_txt']):
            os.makedirs(nomes['diretorio_txt'])
    except Exception as error:
        criar_popup_mensagem(
            f"\n{data_hora_atual()} - INFO - Erro ao criar/validar a pasta {nomes['diretorio_txt']}: {error} ")

class Aplicativo:
    version = "4.1.1"
    version_json = '2.1'
    mensagem_json = "Refatorado json para melhorar a estrutura do redis_qa"
    coluna = 0
    widget = []
    nomes = dict()
    entries = []
    nomes['pasta_config'] = 'Config/'
    nomes['diretorio_log'] = 'Log'
    nomes['diretorio_txt'] = 'Arquivos'
    nomes['diretorio_config'] = 'Config'
    nomes['arquivo_base_muro'] = 'base_muro'
    nomes['arquivo_busca_bancos'] = 'atualizar_registros_update'
    nomes['arquivo_replicar_version'] = 'replicar_version'
    nomes['arquivo_download_backup'] = 'download_backup'
    nomes['arquivo_restaurar_banco'] = 'restaurar_banco'
    nomes['arquivo_connection_strings'] = 'connection_strings'
    nomes['arquivo_validar'] = 'consultar_versions'
    nomes['arquivo_buscar_empresas'] = 'buscar_empresas'
    nomes['arquivo_redis'] = 'limpeza_redis'
    nomes['arquivo_config_default'] = 'prog'
    nomes['arquivo_doc_pis'] = 'PIS_gerados'
    nomes['arquivo_doc_cpf'] = 'CPFs_gerados'
    nomes['arquivo_doc_cnpj'] = 'CNPJs_gerados'
    nomes['arquivo_doc_cei'] = 'CEIs_gerados'
    nomes['arquivo_doc_nif'] = 'NIFs_gerados'

    def __init__(self):
        self.color_default = "#F0F0F0"
        self.color_default_navs = "#ADADAD"
        self.color_default_fonte = "#000000"
        self.infos_config_prog = dict()
        self.infos_config = dict()
        self.arquivo_log = None
        self.config_selecionado = None
        self.arquivo_config = None
        self.placeholder_text = None
        self.label_config_selecionado = None
        self.label = None
        self.entry = None
        self.label_restaurar_backup = None
        self.nome_campo_caixa = None
        self.widtexto = None
        self.arquivo = None
        self.label_lista_arquivos = None
        self.combobox = None
        self.button_nav_escolher = None
        self.button_nav_criar = None
        self.thread = None
        self.arquivo_download = None
        self.button_restaurar_inicio = None
        self.button_restaurar_voltar = None
        self.button_download_inicio = None
        self.button_download_voltar = None
        self.button_busca_inicio = None
        self.button_busca_voltar = None
        self.button_atualizacao_inicio = None
        self.button_atualizacao_voltar = None
        self.button_replicar_inicio = None
        self.button_replicar_voltar = None
        self.button_ferramenta_busca_banco = None
        self.button_ferramenta_buscar_versions = None
        self.button_ferramenta_replicar_version = None
        self.button_ferramenta_config = None
        self.button_ferramenta_voltar = None
        self.button_ferramenta_sair = None
        self.button_menu_ferramentas = None
        self.button_menu_download = None
        self.button_menu_restaurar = None
        self.button_menu_config = None
        self.button_menu_sair = None
        self.button_config_existente = None
        self.button_config_novo = None
        self.button_config_sair = None
        self.app = None
        self.status_thread = None
        self.app = None
        self.main()

# Processo inicial/final
    def finalizar(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Programa finalizado")
        sys.exit(200)

    def atualizador(self):
        if self.infos_config_prog['atualizar']:
            username = "mathsantosilva"
            repository = "MSS"
            tag_atual = self.version
            maior_tag = pesquisar_maior_tag(username, repository, tag_atual, self.criar_popup_mensagem)

            if maior_tag is not None:
                realizar_download(maior_tag, self.criar_popup_mensagem)
                if os.path.exists("C:/MSS_temp"):
                    dir_atual = os.getcwd()
                    executar_comando_batch(dir_atual)
                    self.alterar_data_atualizacao_config()
                    self.finalizar()
                else:
                    return
            else:
                try:
                    if os.path.exists("C:/MSS_temp"):
                        shutil.rmtree("C:/MSS_temp")
                    else:
                        return
                except Exception as error:
                    self.criar_popup_mensagem(f"Erro ao criar/validar a pasta {self.nomes['diretorio_log']}: {error} ")
        else:
            return

# Processos arquivo .json
    def criar_config(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Rotina - Criação de config ")
        nome_banco_escolhido = self.entry.get()
        if nome_banco_escolhido == self.placeholder_text or nome_banco_escolhido == "":
            self.criar_popup_mensagem("O campo nome deverá ser preenchido")
            return
        else:
            nome_banco_escolhido = nome_banco_escolhido.replace(".json", "")
            nome_config = nome_banco_escolhido

            if os.path.exists(f"{self.nomes['diretorio_config']}\\{nome_config}.json"):
                self.criar_popup_mensagem(
                    "Já existe um arquivo .json com o mesmo nome\nInforme outro nome para o arquivo config")
            else:
                arquivo_config = (f"""{{
    "controle_versao_json": {{
        "versao": "{self.version_json}",
        "data": "{data_hora_atual()}",
        "comentario": "{self.mensagem_json}"
    }},
    "bancos_update": {{
        "database_update_br": "",
        "database_update_mx": "",
        "database_update_pt": "",
        "database_update_md": ""
    }},
    "bases_muro": [
        ""
    ],
    "conexoes": [
        {{
            "nome": "",
            "server": "",
            "username": "",
            "password": ""
        }}
    ],
    "redis_qa": {{
        "grupo_1":[
            {{
                "nome_redis": "",
                "ip": "",
                "port": ""
            }},
            {{
                "nome_redis": "",
                "ip": "",
                "port": ""
            }}
        ],
        "grupo_2":[
            {{
                "nome_redis": "",
                "ip": "",
                "port": ""
            }},
            {{
                "nome_redis": "",
                "ip": "",
                "port": ""
            }}
        ]	
    }}
}}""")
                self.escrever_arquivo_config(nome_config, arquivo_config, "json")
                self.criar_popup_mensagem("Novo config criado com sucesso")
                self.escrever_arquivo_log(self.nomes['arquivo_base_muro'],
                                          f"INFO - Novo config criado com sucesso, configure e selecione para ser utilizado {nome_config}")

    def atualizar_arquivo_json(self, config_selecionado, versao_config):
        try:
            formatar_redis = ''
            formatar_conexoes = ''
            formatar_conexoes_antiga = ''
            redis_formatados = dict()
            conexoes_formatados = dict()
            format_bases_utilizadas = ''
            nome_redis = []
            nome_redis_atual = ''
            count = 0
            redis_atual_form = []
            bases_utilizadas = self.infos_config['bases_muro']
            tam_bases_utilizadas = len(bases_utilizadas)
            redis_qa = self.infos_config['redis_qa']
            server_principal = ''
            count_redis_qa = len(redis_qa)
            count_redis_final = 1
            if versao_config != "antiga":
                if redis_qa != '':
                    for red in redis_qa:
                        count_redis = 1
                        for key_red in red:
                            tam_lista_redis = len(red[key_red])
                            for item_red in red[key_red]:
                                if count_redis >= tam_lista_redis:
                                    virgula_redis = ''
                                else:
                                    virgula_redis = ','
                                if count_redis_final >= count_redis_qa:
                                    virgula_redis_final = ''
                                else:
                                    virgula_redis_final = ','
                                if len(item_red) > 1:
                                    pre_formato_redis = f"""
            {{
                "nome_redis": "{item_red["nome_redis"]}",
                "ip": "{item_red['ip']}",
                "port": "{item_red['port']}"
            }}"""
                                    tam_pre_formato_redis = len(pre_formato_redis)
                                    pre_formato_redis = pre_formato_redis[0:tam_pre_formato_redis]
                                    formatar_redis = formatar_redis[0:len(formatar_redis)-2] + pre_formato_redis + virgula_redis + "]" + virgula_redis_final
                                else:
                                    nome_redis_atual = item_red['nome']
                                    pre_formato_redis = f"""
        "{nome_redis_atual}": [  """
                                    tam_pre_formato_redis = len(pre_formato_redis)
                                    pre_formato_redis = pre_formato_redis[0:(tam_pre_formato_redis)]
                                    formatar_redis = formatar_redis + pre_formato_redis
                                count_redis += 1
                            count_redis_final += 1
                    redis_formatados["redis_qa"] = formatar_redis
                else:
                    redis_padrao = f"""
        "grupo_1":[
            {{
                "nome_redis": "",
                "ip": "",
                "port": ""
            }},
            {{
                "nome_redis": "",
                "ip": "",
                "port": ""
            }}
        ],
        "grupo_2":[
            {{
                "nome_redis": "",
                "ip": "",
                "port": ""
            }},
            {{
                "nome_redis": "",
                "ip": "",
                "port": ""
            }}
        ]"""
                    redis_formatados["redis_qa"] = redis_padrao
            else:
                tam_lista_redis_ant = len(redis_qa)
                count_redis = 1
                if redis_qa != '':
                    for red in redis_qa:
                        if count_redis >= tam_lista_redis_ant:
                            virgula_redis = ''
                        else:
                            virgula_redis = ','
                        if count_redis_final >= count_redis_qa:
                            virgula_redis_final = ''
                        else:
                            virgula_redis_final = ','
                        if count_redis == 1:
                            nome_redis_atual = "grupo_1"
                            pre_formato_redis = f"""
            "{nome_redis_atual}": [  """
                            tam_pre_formato_redis = len(pre_formato_redis)
                            pre_formato_redis = pre_formato_redis[0:(tam_pre_formato_redis)]
                            formatar_redis = formatar_redis + pre_formato_redis
                        pre_formato_redis = f"""
                {{
                    "nome_redis": "{red["nome_redis"]}",
                    "ip": "{red['ip']}",
                    "port": "{red['port']}"
                }}"""
                        tam_pre_formato_redis = len(pre_formato_redis)
                        pre_formato_redis = pre_formato_redis[0:tam_pre_formato_redis]
                        formatar_redis = formatar_redis[0:len(formatar_redis)-2] + pre_formato_redis + virgula_redis + "]" + virgula_redis_final
                        count_redis += 1
                        count_redis_final += 1
                    redis_formatados["redis_qa"] = formatar_redis
                else:
                    redis_padrao = f"""
        "grupo_1":[
            {{
                "nome_redis": "",
                "ip": "",
                "port": ""
            }},
            {{
                "nome_redis": "",
                "ip": "",
                "port": ""
            }}
        ],
        "grupo_2":[
            {{
                "nome_redis": "",
                "ip": "",
                "port": ""
            }},
            {{
                "nome_redis": "",
                "ip": "",
                "port": ""
            }}
        ]"""
                    redis_formatados["redis_qa"] = redis_padrao
            for base in bases_utilizadas:
                if tam_bases_utilizadas > 1:
                    if count > 0:
                        formatando_bases_utilizadas = f""" 
        "{base}",
    """
                        format_bases_utilizadas = format_bases_utilizadas + formatando_bases_utilizadas
                        format_bases_utilizadas = format_bases_utilizadas.strip()
                    else:
                        formatando_bases_utilizadas = f""" "{base}",
    """
                        format_bases_utilizadas = format_bases_utilizadas + formatando_bases_utilizadas
                        format_bases_utilizadas = format_bases_utilizadas.strip()
                    count +=1
                else:
                    formatando_bases_utilizadas = f""" "{base}"
    """
                    format_bases_utilizadas = format_bases_utilizadas + formatando_bases_utilizadas
                    format_bases_utilizadas = format_bases_utilizadas.strip()
            if "," in format_bases_utilizadas:
                tam_format_bases_utilizadas = len(format_bases_utilizadas)-1
                format_bases_utilizadas = format_bases_utilizadas[0:tam_format_bases_utilizadas]
            if self.infos_config['server'] != '':
                self.infos_config['server'] = self.infos_config['server'].lower()
                if "\\" in self.infos_config['server']:
                    self.infos_config['server'] = self.infos_config['server'].replace('\\', '\\\\')
                if self.infos_config['server'] == '':
                    name_server_2 = ''
                elif "pt" in self.infos_config['server']:
                    name_server_2 = '2019'
                else:
                    name_server_2 = '2017'
                if self.infos_config['server_principal'] == '':
                    virgula_con_ant = ''
                else:
                    virgula_con_ant = ','

                pre_formato_conexoes_ant = f"""
        {{
            "nome": "{name_server_2}",
            "server": "{self.infos_config['server']}",
            "username": "{self.infos_config['username']}",
            "password": "{self.infos_config['password']}"

        }}"""
                tam_pre_formato_conexoes_ant = len(pre_formato_conexoes_ant)
                pre_formato_conexoes_ant = pre_formato_conexoes_ant[0:tam_pre_formato_conexoes_ant]
                formatar_conexoes_antiga = formatar_conexoes_antiga[0:len(formatar_conexoes_antiga)] + pre_formato_conexoes_ant + virgula_con_ant
                conexoes_formatados["conexoes"] = formatar_conexoes_antiga
            if self.infos_config['server_principal'] != '':
                self.infos_config['server_principal'] = self.infos_config['server_principal'].lower()
                virgula_con_ant = ''
                if self.infos_config['server_principal'] == self.infos_config['server']:
                    self.infos_config['server_principal'] = ''
                    self.infos_config['username_principal'] = ''
                    self.infos_config['password_principal'] = ''
                if self.infos_config['server_principal'] == '':
                    name_server_1 = ''
                elif "pt" in self.infos_config['server_principal']:
                    name_server_1 = '2019'
                else:
                    name_server_1 = '2017'
                if '\\' in self.infos_config['server_principal']:
                    self.infos_config['server_principal'] = self.infos_config['server_principal'].replace('\\', '\\\\')
                pre_formato_conexoes_ant = f"""
        {{
            "nome": "{name_server_1}",
            "server": "{self.infos_config['server_principal']}",
            "username": "{self.infos_config['username_principal']}",
            "password": "{self.infos_config['password_principal']}"
    
        }}"""
                tam_pre_formato_conexoes_ant = len(pre_formato_conexoes_ant)
                pre_formato_conexoes_ant = pre_formato_conexoes_ant[0:tam_pre_formato_conexoes_ant]
                formatar_conexoes_antiga = formatar_conexoes_antiga[0:len(formatar_conexoes_antiga)] + pre_formato_conexoes_ant + virgula_con_ant
            conexoes_formatados["conexoes"] = formatar_conexoes_antiga
            if self.infos_config['conexoes'] != '':
                count_conexoes = 1
                count_conexoes_final = 1
                tam_lista_conexoes = len(self.infos_config['conexoes'])
                for con_atual in self.infos_config['conexoes']:
                    if count_conexoes >= tam_lista_conexoes:
                        virgula_con = ''
                    else:
                        virgula_con = ','
                    if '\\' in con_atual['server']:
                        con_atual['server'] = con_atual['server'].replace('\\', '\\\\')
                    pre_formato_conexoes = f"""
        {{
            "nome": "{con_atual['nome']}",
            "server": "{con_atual['server']}",
            "username": "{con_atual['username']}",
            "password": "{con_atual['password']}"
        }}"""
                    tam_pre_formato_conexoes = len(pre_formato_conexoes)
                    pre_formato_conexoes = pre_formato_conexoes[0:tam_pre_formato_conexoes]
                    formatar_conexoes = formatar_conexoes[0:len(formatar_conexoes)] + pre_formato_conexoes + virgula_con
                    count_conexoes += 1
                conexoes_formatados["conexoes"] = formatar_conexoes

            json_atualizado = f"""{{
    "controle_versao_json": {{
        "versao": "{self.version_json}",
        "data": "{data_hora_atual()}",
        "comentario": "{self.mensagem_json}"
    }},
    "bancos_update": {{
        "database_update_br": "{self.infos_config['database_update_br']}",
        "database_update_mx": "{self.infos_config['database_update_mx']}",
        "database_update_pt": "{self.infos_config['database_update_pt']}",
        "database_update_md": "{self.infos_config['database_update_md']}"
    }},
    "bases_muro": [
        {format_bases_utilizadas}
    ],
    "conexoes": [{conexoes_formatados["conexoes"]}],
    "redis_qa": {{{redis_formatados['redis_qa']}	
    }}
}}"""
            config_selecionado = config_selecionado.split('.')
            self.escrever_arquivo_config(config_selecionado[0], json_atualizado, config_selecionado[1])
            self.criar_popup_mensagem(f"O Arquivo json foi atualizado, selecione novamente")
            self.infos_config['status'] = False
            return self.infos_config['status']
        except Exception as name_error:
            self.criar_popup_mensagem(f"Existem erros de formatação no arquivo de config escolhido:\n {name_error}")
            self.escrever_arquivo_log(self.nomes['arquivo_base_muro'],f"INFO - Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente: {name_error} ")
            self.infos_config['status'] = False
            return self.infos_config['status']

    def ler_parametros_arquivo_json(self, params_dict, versao_config):
        self.infos_config['status'] = False
        try:
            match versao_config:
                case "atual":
                    tam_conexoes = len(params_dict["conexoes"])
                    for con in range(tam_conexoes):
                        if params_dict["conexoes"][con]['server'] != '':
                            validacao_conexoes = True
                            break
                        else:
                            validacao_conexoes = False
                            continue

                    if not validacao_conexoes:
                        self.criar_popup_mensagem(
                            "Valores não foram especificados no json, edite o arquivo e tente novamente")
                        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'],
                                                  f"INFO - Valores não foram especificados no json, edite o arquivo e tente novamente")
                        return
                    else:
                        try:
                            self.infos_config["controle_versao_json"] = params_dict["controle_versao_json"]
                            self.infos_config["database_update_br"] = params_dict["bancos_update"]["database_update_br"]
                            self.infos_config["database_update_mx"] = params_dict["bancos_update"]["database_update_mx"]
                            self.infos_config["database_update_pt"] = params_dict["bancos_update"]["database_update_pt"]
                            self.infos_config["database_update_md"] = params_dict["bancos_update"]["database_update_md"]
                            self.infos_config['bases_muro'] = params_dict["bases_muro"]
                            self.infos_config['conexoes'] = params_dict["conexoes"]
                            self.infos_config['redis_qa'] = params_dict["redis_qa"]
                            self.infos_config['server'] = ''
                            self.infos_config['username'] = ''
                            self.infos_config['password'] = ''
                            self.infos_config['server_principal'] = ''
                            self.infos_config['username_principal'] = ''
                            self.infos_config['password_principal'] = ''
                            self.criar_dict_conexoes()
                            self.infos_config['status'] = True
                            return
                        except Exception as name_error:
                            self.criar_popup_mensagem(
                                f"Existem erros de formatação no arquivo de config escolhido:\n {name_error}")
                            self.escrever_arquivo_log(self.nomes['arquivo_base_muro'],
                                                      f"INFO - Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente: {name_error} ")
                case "desatualizada":
                    tam_conexoes = len(params_dict["conexoes"])
                    for con in range(tam_conexoes):
                        if params_dict["conexoes"][con]['server'] != '':
                            validacao_conexoes = True
                            break
                        else:
                            validacao_conexoes = False
                            continue

                    if not validacao_conexoes:
                        self.criar_popup_mensagem(
                            "Valores não foram especificados no json, edite o arquivo e tente novamente")
                        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'],
                                                  f"INFO - Valores não foram especificados no json, edite o arquivo e tente novamente")
                        return

                    else:
                        self.infos_config["controle_versao_json"] = params_dict["controle_versao_json"]
                        self.infos_config["database_update_br"] = params_dict["bancos_update"]["database_update_br"]
                        self.infos_config["database_update_mx"] = params_dict["bancos_update"]["database_update_mx"]
                        self.infos_config["database_update_pt"] = params_dict["bancos_update"]["database_update_pt"]
                        self.infos_config["database_update_md"] = params_dict["bancos_update"]["database_update_md"]
                        self.infos_config['bases_muro'] = params_dict["bases_muro"]
                        self.infos_config['conexoes'] = params_dict["conexoes"]
                        self.infos_config['redis_qa'] = params_dict["redis_qa"]
                        self.infos_config['server'] = ''
                        self.infos_config['username'] = ''
                        self.infos_config['password'] = ''
                        self.infos_config['server_principal'] = ''
                        self.infos_config['username_principal'] = ''
                        self.infos_config['password_principal'] = ''
                        self.infos_config['status'] = True
                        self.atualizar_arquivo_json(self.config_selecionado, versao_config)
                case "antiga":
                    try:
                        if params_dict['conexao']['server'] == '' or params_dict["conexao"]["username"] == '' or \
                                params_dict["conexao"]["password"] == '':
                            self.criar_popup_mensagem(
                                "Valores não foram especificados no json, edite o arquivo e tente novamente")
                            self.escrever_arquivo_log(self.nomes['arquivo_base_muro'],
                                                      f"INFO - Valores não foram especificados no json, edite o arquivo e tente novamente")
                            self.trocar_tela_config()
                        elif not params_dict["bases_muro"]:
                            self.criar_popup_mensagem(
                                "Valores não foram especificados no json, edite o arquivo e tente novamente")
                            self.escrever_arquivo_log(self.nomes['arquivo_base_muro'],
                                                      f"INFO - Valores não foram especificados no json, edite o arquivo e tente novamente")
                            self.trocar_tela_config()
                    except Exception as name_error:
                        self.criar_popup_mensagem(
                            "Ocorreu um erro ao tentar validar as tags de conexão, verifique o config e tente novamente")
                        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'],
                                                  f"INFO - Ocorreu um erro ao tentar validar as tags de conexão, verifique o config e tente novamente")
                        self.trocar_tela_config()
                    # Carregar json
                    self.infos_config['server'] = params_dict["conexao"]["server"]
                    self.infos_config['username'] = params_dict["conexao"]["username"]
                    self.infos_config['password'] = params_dict["conexao"]["password"]
                    self.infos_config['database_update_br'] = params_dict["database_update_br"]
                    self.infos_config['database_update_mx'] = params_dict["database_update_mx"]
                    self.infos_config['database_update_pt'] = params_dict["database_update_pt"]
                    self.infos_config['database_update_md'] = params_dict["database_update_md"]
                    self.infos_config['bases_muro'] = params_dict["bases_muro"]
                    self.infos_config['conexoes'] = ''
                    try:
                        if (params_dict)["configs_restaurar_download"]["server_principal"] != '':
                            self.infos_config['server_principal'] = (params_dict)["configs_restaurar_download"]["server_principal"]
                            self.infos_config['username_principal'] = (params_dict)["configs_restaurar_download"]["username_principal"]
                            self.infos_config['password_principal'] = (params_dict)["configs_restaurar_download"]["password_principal"]
                    except Exception as name_error:
                        self.criar_popup_mensagem(
                            "Ocorreu um erro ao tentar validar as tags do server_principal, foram preenchidas vazias")
                        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'],
                                                  f"INFO - Ocorreu um erro ao tentar validar as tags de conexão, foram preenchidas vazias")
                        self.infos_config['server_principal'] = ""
                        self.infos_config['username_principal'] = ""
                        self.infos_config['password_principal'] = ""
                    try:
                        if params_dict["redis_qa"] != '':
                            self.infos_config['redis_qa'] = params_dict["redis_qa"]
                    except Exception as name_error:
                        self.criar_popup_mensagem("Ocorreu um erro ao tentar validar as tags do redis_qa, foram preenchidas vazias")
                        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'],
                                                  f"INFO - Ocorreu um erro ao tentar validar as tags de conexão, foram preenchidas vazias")
                        self.infos_config['redis_qa'] = ""
                    self.atualizar_arquivo_json(self.config_selecionado, versao_config)
                    return
                case _:
                    self.criar_popup_mensagem("Erro ao ler arquivo config")
        except Exception as name_error:
            self.criar_popup_mensagem(
                f"Existem erros de formatação no arquivo de config escolhido:\n {name_error}")
            self.escrever_arquivo_log(self.nomes['arquivo_base_muro'],
                                      f"INFO - Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente: {name_error} ")
            self.trocar_tela_config()

    def escrever_arquivo_config(self, nome_arquivo, texto, extensao):
        self.arquivo_config = open(f"{self.nomes['diretorio_config']}\\{nome_arquivo}.{extensao}", "w")
        self.arquivo_config.close()
        self.arquivo_config = open(f"{self.nomes['diretorio_config']}\\{nome_arquivo}.{extensao}", "w")
        self.arquivo_config.write(texto)
        self.arquivo_config.close()

    def escolher_config_existente(self):
        params_dict = ''
        versao = 0
        self.infos_config['status'] = False

        # Validando se o metodo esta escolhendo o config de forma manual ou automatica
        if self.infos_config_prog['escolha_manual']:
            self.config_selecionado = self.combobox.get()
        elif self.infos_config_prog['escolha_manual'] is False and self.infos_config_prog['config_default'] != "":
            self.config_selecionado = self.infos_config_prog['config_default']
        else:
            self.criar_popup_mensagem(
                f"Erro na validação do arquivo config: {self.infos_config_prog['escolha_manual']} e {self.infos_config_prog['config_default']}")

        # Validando o arquivo de config
        try:
            if os.path.isfile(f"{self.nomes['diretorio_config']}\\{self.config_selecionado}"):
                config_bjt = open(f"{self.nomes['diretorio_config']}\\{self.config_selecionado}", "r")
                config_json = config_bjt.read().lower()
                params_dict = json.loads(config_json)
            else:
                self.criar_popup_mensagem(f"Não foi possível encontrar um .JSON com esse nome na pasta {self.nomes['diretorio_config']}!")
                self.trocar_tela_config()
                return
        except Exception as name_error:
            self.criar_popup_mensagem(f"Existem erros de formatação no arquivo de config escolhido:\n {name_error}")
            self.escrever_arquivo_log(self.nomes['arquivo_base_muro'],
                                      f"INFO - Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente: {name_error} ")
            self.trocar_tela_config()
        else:
            try:
                if float(params_dict['controle_versao_json']['versao']) >= float(self.version_json):
                    versao_config = "atual"
                else:
                    versao_config = "desatualizada"
            except Exception as error:
                versao_config = "antiga"

            self.ler_parametros_arquivo_json(params_dict, versao_config)

        if self.infos_config['status']:
            self.atualizar_config_default(self.config_selecionado)
            self.trocar_tela_menu_geral()
        else:
            self.trocar_tela_config()

# Processos arquivo .config
    def criar_arquivo_config_prog(self):
            arquivo_config = f"""[ConfiguracoesGerais]
    config_default = 
    data_ultima_atualizacao =

    [ConfiguracoesAparencia]
    background_color_fundo = {self.color_default}
    background_color_titulos = {self.color_default}
    background_color_botoes = {self.color_default}
    background_color_botoes_navs = {self.color_default_navs}
    background_color_fonte = {self.color_default_fonte}"""
            self.escrever_arquivo_config(self.nomes['arquivo_config_default'], arquivo_config, "conf")

    def atualizar_config_default(self, config_setado):
        try:
            config = configparser.ConfigParser()
            config.read(f"{self.nomes['diretorio_config']}\\{self.nomes['arquivo_config_default']}.conf")
            config.set('ConfiguracoesGerais', 'config_default', config_setado)
            self.salvar_alteracoes_config(config)
            self.infos_config_prog['config_default'] = config_setado
        except Exception as error:
            self.criar_popup_mensagem(f"Erro ao atualizar o arquivo config: {error}")

    def salvar_alteracoes_config(self, config):
        try:
            with open(f"{self.nomes['diretorio_config']}\\{self.nomes['arquivo_config_default']}.conf", 'w') as config_file:
                config.write(config_file)
        except Exception as error:
            self.criar_popup_mensagem(f"Erro ao atualizar o arquivo config: {error}")

    def ler_arquivo_config(self):
        try:
            self.infos_config_prog["config_default"] = ""
            self.infos_config_prog["background_color_fundo"] = self.color_default
            self.infos_config_prog["background_color_titulos"] = self.color_default
            self.infos_config_prog["background_color_botoes"] = self.color_default
            self.infos_config_prog["background_color_botoes_navs"] = self.color_default_navs
            self.infos_config_prog["background_color_fonte"] = self.color_default_fonte
            config = configparser.ConfigParser()
            config.read(f"{self.nomes['diretorio_config']}\\{self.nomes['arquivo_config_default']}.conf")
            config_default = config.get('ConfiguracoesGerais', 'config_default')
            background_color_fundo = config.get('ConfiguracoesAparencia', 'background_color_fundo')
            background_color_titulos = config.get('ConfiguracoesAparencia', 'background_color_titulos')
            background_color_botoes = config.get('ConfiguracoesAparencia', 'background_color_botoes')
            background_color_botoes_navs = config.get('ConfiguracoesAparencia', 'background_color_botoes_navs')
            background_color_fonte = config.get('ConfiguracoesAparencia', 'background_color_fonte')
            if config_default != "":
                self.infos_config_prog["config_default"] = config_default
            if background_color_fundo != self.color_default:
                self.infos_config_prog["background_color_fundo"] = background_color_fundo
            if background_color_titulos != self.color_default:
                self.infos_config_prog["background_color_titulos"] = background_color_titulos
            if background_color_botoes != self.color_default:
                self.infos_config_prog["background_color_botoes"] = background_color_botoes
            if background_color_botoes_navs != self.color_default_navs:
                self.infos_config_prog["background_color_botoes_navs"] = background_color_botoes_navs
            if background_color_fonte != self.color_default_fonte:
                self.infos_config_prog["background_color_fonte"] = background_color_fonte
            return background_color_fundo, background_color_titulos, background_color_botoes, background_color_botoes_navs, background_color_fonte
        except Exception as error:
            self.criar_popup_mensagem(f"Erro ao acessar arquivo de configuração default {error}")

    def alterar_data_atualizacao_config(self):
        data = data_atual()
        try:
            config = configparser.ConfigParser()
            config.read(f"{self.nomes['diretorio_config']}\\{self.nomes['arquivo_config_default']}.conf")
            config.set('ConfiguracoesGerais', 'data_ultima_atualizacao', data)
            self.salvar_alteracoes_config(config)
        except Exception as error:
            self.criar_popup_mensagem(f"Erro ao atualizar a data da ultima atualização: {error}")

    def validar_data_atualizacao_config(self):
        data = data_atual()
        data = datetime.strptime(data, "%d-%m-%Y")
        if os.path.isfile(f"{self.nomes['diretorio_config']}\\{self.nomes['arquivo_config_default']}.conf"):
            try:
                config = configparser.ConfigParser()
                config.read(f"{self.nomes['diretorio_config']}\\{self.nomes['arquivo_config_default']}.conf")
                self.infos_config_prog["data_ultima_atualizacao"] = ""
                data_ultima_atualizacao = config.get('ConfiguracoesGerais', 'data_ultima_atualizacao')
                if data_ultima_atualizacao != '':
                    data_ultima_atualizacao = datetime.strptime(data_ultima_atualizacao, "%d-%m-%Y")
                    if data_ultima_atualizacao < data:
                        self.infos_config_prog["atualizar"] = True
                        self.alterar_data_atualizacao_config()
                    else:
                        self.infos_config_prog["atualizar"] = False
                        return
                else:
                    self.infos_config_prog["atualizar"] = True
                    self.alterar_data_atualizacao_config()
            except Exception as error:
                self.criar_popup_mensagem(f"Erro ao validar a ultima atualização: {error}")
                self.infos_config_prog["atualizar"] = False
        else:
            self.infos_config_prog["atualizar"] = False
            return

# Subprocessos
    def alterar_status_campos_tela(self, status):
        if status:
            for entry_atual in self.entries:
                entry_atual.config(state='normal')
            self.button_restaurar_inicio.config(state='normal')
            self.button_restaurar_voltar.config(state='normal')
            self.button_restaurar_limpar.config(state='normal')
            self.combobox_servidor_restaurar.config(state='normal')
            self.button_menu_sair.config(state='normal')
        else:
            for entry_atual in self.entries:
                entry_atual.config(state='disabled')
            self.button_restaurar_inicio.config(state='disabled')
            self.button_restaurar_limpar.config(state='disabled')
            self.button_restaurar_voltar.config(state='disabled')
            self.combobox_servidor_restaurar.config(state='disabled')
            self.button_menu_sair.config(state='disabled')

    def buscar_redis_dict(self):
        opcoes_grupo_redis = []
        count = 0
        for red in self.infos_config['redis_qa']:
            if red != '':
                opcoes_grupo_redis.append(red)
            count += 1

        return opcoes_grupo_redis

    def atualizar_opcoes(self, event):
        redis_total = dict()
        red_grupo_atual = ''
        nome_redis = []
        grupo_redis_selecionado = self.combobox_redis_grupo.get()

        for red_grupo_atual in self.infos_config['redis_qa'][grupo_redis_selecionado]:
            try:
                nome_redis.append(red_grupo_atual["nome_redis"])
            except Exception as error:
                continue

        if len(nome_redis) <= 0 or nome_redis == '':
            self.combobox_redis['values'] = nome_redis
            self.combobox_redis.set(nome_redis)
            self.combobox_redis['values'] = nome_redis
            self.escrever_no_input("- A tag ou Grupo do redis se encontra vazio")
            self.escrever_arquivo_log(self.nomes['arquivo_redis'],
                                      f"ERRO - A tag ou Grupo do redis se encontra vazio")
        else:
            self.combobox_redis['values'] = nome_redis
            self.combobox_redis.set(nome_redis[0])

    def criar_dict_conexoes(self):
        grupo_con = dict()
        tam_conexoes = len(self.infos_config['conexoes'])
        if tam_conexoes > 0:
            for con in self.infos_config['conexoes']:
                nome = con['nome']
                con.pop("nome")
                if len(grupo_con) <= 0:
                    grupo_con = {nome: {}}
                else:
                    grupo_con.update({nome: {}})
                grupo_con[nome].update(con)
            self.infos_config['conexoes'] = grupo_con

    def escrever_arquivo_log(self, nome_arquivo, texto):
        validar_diretorio(self.nomes, self.criar_popup_mensagem)
        self.arquivo_log = open(f"{self.nomes['diretorio_log']}\\{nome_arquivo}.txt", "a")
        pula_linha = validar_linha(self.nomes['diretorio_log'], nome_arquivo)
        self.arquivo_log.write(f"{pula_linha}{data_hora_atual()} - {texto}")
        self.arquivo_log.close()

    def escrever_arquivo_txt(self, nome_arquivo, texto):
        validar_diretorio(self.nomes, self.criar_popup_mensagem)
        self.arquivo_txt = open(f"{self.nomes['diretorio_txt']}\\{nome_arquivo}.txt", "a")
        pula_linha = validar_linha(self.nomes['diretorio_txt'], nome_arquivo)
        self.arquivo_txt.write(f"{pula_linha}{data_hora_atual()} - {texto}")
        self.arquivo_txt.close()

    def limpar_string(self, documento_inserido):
        lista_limpa = []
        lista_suja = documento_inserido.split(",")
        for item in lista_suja:
            sem_mascara = item.replace(".", "")
            sem_mascara = sem_mascara.replace(",", "")
            sem_mascara = sem_mascara.replace("-", "")
            sem_mascara = sem_mascara.replace("/", "")
            sem_mascara = sem_mascara.strip()
            lista_limpa.append(sem_mascara)
        return lista_limpa

    def limpar_caixa_texto(self):
        self.widtexto.config(state="normal")
        self.widtexto.delete(1.0, 'end')
        self.widtexto.config(state="disabled")

    def escrever_no_input(self, texto):
        self.widtexto.config(state="normal")
        self.widtexto.insert(END, str(texto) + '\n')
        self.widtexto.see(END)
        self.widtexto.config(state="disabled")

    def criar_popup_mensagem(self, mensagem):
        msg = Tk()
        msg.geometry(f"{self.largura}x200+{self.metade_wid}+{self.metade_hei}")
        msg.configure(bg=self.infos_config_prog["background_color_fundo"])
        msg.grid_rowconfigure(0, weight=1)
        msg.grid_columnconfigure(0, weight=1)
        msg.config(padx=10, pady=10)
        msg.title("MSS - " + self.version + " - ALERTA")
        label_mensagem = Label(
            msg,
            text=f"{mensagem}",
            padx=20,
            pady=20,
            bg=self.infos_config_prog["background_color_titulos"]

        )
        button_sair_mensagem = Button(
            msg,
            text="Fechar",
            width=10,
            height=2,
            background="grey",
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: fechar_janela(msg)

        )
        label_mensagem.grid(row=0, sticky="WE")
        button_sair_mensagem.grid(row=1, pady=(10, 10))

    def remover_widget(self, app, name, ent):
        lista_entry = self.percorrer_widgets(app)
        if name == "*":
            for widget in app.winfo_children():
                if widget.widgetName != "menu":
                    widget.destroy()
        else:
            for item in lista_entry:
                if item == name:
                    match ent:
                        case 'entry':
                            self.entry.destroy()
                            break
                        case 'combobox':
                            self.combobox.destroy()
                            break
                        case 'label':
                            self.label.destroy()
                            break
                        case _:
                            return

    def alterar_background(self):
        backg_fundo = self.entry_background_fundo.get()
        backg_titulos = self.entry_background_titulos.get()
        backg_botoes = self.entry_background_botoes.get()
        backg_botoes_navs = self.entry_background_botoes_navs.get()
        backg_fontes = self.entry_background_fonte.get()

        if backg_fundo == '':
            backg_fundo = self.color_default
        if backg_titulos == '':
            backg_titulos = self.color_default
        if backg_botoes == '':
            backg_botoes = self.color_default
        if backg_botoes_navs == '':
            backg_botoes_navs = self.color_default_navs
        if backg_fontes == '':
            backg_fontes = self.color_default_fonte

        try:
            config = configparser.ConfigParser()
            config.read(f"{self.nomes['diretorio_config']}\\{self.nomes['arquivo_config_default']}.conf")
            config.set('ConfiguracoesAparencia', 'background_color_fundo', backg_fundo)
            config.set('ConfiguracoesAparencia', 'background_color_titulos', backg_titulos)
            config.set('ConfiguracoesAparencia', 'background_color_botoes', backg_botoes)
            config.set('ConfiguracoesAparencia', 'background_color_botoes_navs', backg_botoes_navs)
            config.set('ConfiguracoesAparencia', 'background_color_fonte', backg_fontes)
            self.salvar_alteracoes_config(config)
            self.infos_config_prog["background_color_fundo"] = backg_fundo
            self.infos_config_prog["background_color_titulos"] = backg_titulos
            self.infos_config_prog["background_color_botoes"] = backg_botoes
            self.infos_config_prog["background_color_botoes_navs"] = backg_botoes_navs
            self.infos_config_prog["background_color_fonte"] = backg_fontes
            self.trocar_tela_menu_geral()
        except Exception as error:
            self.criar_popup_mensagem(f"Erro ao Alterar o background: {error}")

    def redefinir_background(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Background Redefinido")
        backg_fundo = self.color_default
        backg_titulos = self.color_default
        backg_botoes = self.color_default
        backg_botoes_navs = self.color_default_navs
        backg_fontes = self.color_default_fonte

        try:
            config = configparser.ConfigParser()
            config.read(f"{self.nomes['diretorio_config']}\\{self.nomes['arquivo_config_default']}.conf")
            config.set('ConfiguracoesAparencia', 'background_color_fundo', backg_fundo)
            config.set('ConfiguracoesAparencia', 'background_color_titulos', backg_titulos)
            config.set('ConfiguracoesAparencia', 'background_color_botoes', backg_botoes)
            config.set('ConfiguracoesAparencia', 'background_color_botoes_navs', backg_botoes_navs)
            config.set('ConfiguracoesAparencia', 'background_color_fonte', backg_fontes)
            self.salvar_alteracoes_config(config)
            self.infos_config_prog["background_color_fundo"] = backg_fundo
            self.infos_config_prog["background_color_titulos"] = backg_titulos
            self.infos_config_prog["background_color_botoes"] = backg_botoes
            self.infos_config_prog["background_color_botoes_navs"] = backg_botoes_navs
            self.infos_config_prog["background_color_fonte"] = backg_fontes
            self.trocar_tela_menu_geral()
        except Exception as error:
            self.criar_popup_mensagem(f"Erro ao Alterar o background: {error}")

    def percorrer_widgets(self, app):
        self.widget.clear()
        if app.winfo_children():
            for child in app.winfo_children():
                self.widget.append(child.widgetName)
                continue
        return self.widget

    def on_entry_click(self, event):
        if self.entry.get() == self.placeholder_text:
            self.entry.delete(0, END)
            self.entry.config(foreground='black')

    def on_focusout(self, event):
        if self.entry.get() == "":
            self.entry.insert(0, self.placeholder_text)
            self.entry.config(foreground='gray')

# Processos principais
    def atualizar_bancos_update(self):
        print("Não implementado")

    def consultar_versions(self):
        try:
            self.button_consultar_inicio.config(state='disabled')
            self.button_consultar_limpar.config(state='disabled')
            self.button_consultar_voltar.config(state='disabled')
            self.combobox_servidor_consulta_version.config(state='disabled')
            self.button_menu_sair.config(state='disabled')
            server = self.combobox_servidor_consulta_version.get()
            tam_base_muro = len(self.infos_config['bases_muro'])
            self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Rotina - Validar atualização")

            self.escrever_arquivo_log(self.nomes['arquivo_validar'], f"INFO - Inicio da validação do banco update ")
            self.escrever_no_input(f"\n- Iniciando consulta no banco update")
            if server == "":
                self.escrever_no_input(f"- Deverá ser selecionado o servidor, antes de prosseguir")
                self.button_consultar_inicio.config(state='normal')
                self.button_consultar_limpar.config(state='normal')
                self.button_consultar_voltar.config(state='normal')
                self.combobox_servidor_consulta_version.config(state='normal')
                self.button_menu_sair.config(state='normal')
                return
            servidor_selecionado = self.infos_config["conexoes"][server]
            for num in range(tam_base_muro):
                database_update = self.valida_banco_update(num)

                try:
                    cnxnrp = pyodbc.connect(
                        f"DRIVER=SQL Server;SERVER={servidor_selecionado['server']};DATABASE={database_update};ENCRYPT=not;UID={servidor_selecionado['username']};PWD={servidor_selecionado['password']}")
                    cursorrp = cnxnrp.cursor()
                    comando = f"select [database_version],  count(database_version) Quantidade from [dbo].[KAIROS_DATABASES] group by [database_version]"
                    cursorrp.execute(comando)
                    result = cursorrp.fetchall()
                except (Exception or pyodbc.DatabaseError) as err:
                    self.escrever_no_input(f"- Falha ao tentar consultar banco de update: {err}")
                    self.escrever_arquivo_log(self.nomes['arquivo_validar'], f"ERRO - Falha ao tentar consultar banco de muro update: {err}")
                else:
                    self.escrever_arquivo_log(
                        self.nomes['arquivo_validar'], f"INFO - Sucesso ao consulta no banco de update")

                    if len(result) > 0:
                        for n in range(len(result)):
                            self.escrever_no_input(f"- {database_update[-2:]} - Version: {result[n][0]} - Quant: {result[n][1]}")
                            self.escrever_arquivo_log(self.nomes['arquivo_validar'], f"INFO - Version: {result[n][0]} - Quantidade: {result[n][1]}")
                    else:
                        self.escrever_no_input(f"- Não foram retornados registros no banco: {database_update}")
                        self.escrever_arquivo_log(
                            self.nomes['arquivo_validar'], f"INFO - Não foram retornados registros no banco:")

                if num < 4:
                    num += 1
                continue

            self.escrever_no_input(f"- Fim da operação de consulta")
            self.escrever_arquivo_log(self.nomes['arquivo_validar'], f"INFO - Fim da operação Validar atualização")
            self.button_consultar_inicio.config(state='normal')
            self.button_consultar_limpar.config(state='normal')
            self.button_consultar_voltar.config(state='normal')
            self.combobox_servidor_consulta_version.config(state='normal')
            self.button_menu_sair.config(state='normal')
        except Exception as error:
            self.escrever_no_input(f"Exceção não tratada: {error}")
            self.button_consultar_inicio.config(state='normal')
            self.button_consultar_limpar.config(state='normal')
            self.button_consultar_voltar.config(state='normal')
            self.combobox_servidor_consulta_version.config(state='normal')
            self.button_menu_sair.config(state='normal')

    def buscar_empresas(self):
        try:
            self.button_busca_empresa_atualizacao_inicio.config(state='disabled')
            self.button_busca_empresa_atualizacao_limpar.config(state='disabled')
            self.button_busca_empresa_atualizacao_voltar.config(state='disabled')
            self.combobox_busca_empresa_servidor_version.config(state='disabled')
            self.combobox_busca_empresa_banco_muro.config(state='disabled')
            self.button_menu_sair.config(state='disabled')
            server = self.combobox_busca_empresa_servidor_version.get()
            base_muro = self.combobox_busca_empresa_banco_muro.get()

            self.escrever_arquivo_log(self.nomes['arquivo_buscar_empresas'], f"INFO - Inicio da busca das empresas ")
            self.escrever_no_input(f"- Inicio da busca das empresas")

            lista_sort_infos_emp = []
            lista_infos_emp = dict()
            data_criacao_db = ''
            lista_razao_social = []
            lista_cnpj_cpf = []
            lista_usuarios = []
            servidor_selecionado = self.infos_config["conexoes"][server]
            lista_limpa_razao_social = []
            lista_limpa_usuarios = []
            lista_limpa_data_criacao_db = []
            lista_limpa_cnpj_cpf = []

            try:
                cnx = pyodbc.connect(f"DRIVER=SQL Server;SERVER={servidor_selecionado['server']};ENCRYPT=not;UID={servidor_selecionado['username']};PWD={servidor_selecionado['password']}", autocommit=True)
                cursor = cnx.cursor()
                cursor.execute(f"""SELECT name FROM sys.databases;""")
                lista_empresas_instancia = cursor.fetchall()
            except (Exception or pyodbc.DatabaseError) as error:
                self.button_busca_empresa_atualizacao_inicio.config(state='normal')
                self.button_busca_empresa_atualizacao_limpar.config(state='normal')
                self.button_busca_empresa_atualizacao_voltar.config(state='normal')
                self.combobox_busca_empresa_servidor_version.config(state='normal')
                self.combobox_busca_empresa_banco_muro.config(state='normal')
                self.button_menu_sair.config(state='normal')
                self.escrever_no_input(f"- Falha ao tentar consultar banco de update: {error}")
                self.escrever_arquivo_log(self.nomes['arquivo_validar'],
                                          f"ERRO - Falha ao tentar consultar banco de muro update: {error}")
            else:
                self.escrever_no_input(f"- Sucesso na busca dos bancos da instancia")
                self.escrever_arquivo_log(self.nomes['arquivo_buscar_empresas'],
                                          f"INFO - Sucesso na busca dos bancos da instancia")
                self.escrever_no_input(f"\n- Iniciando o processo no banco: {base_muro}")
                self.escrever_arquivo_log(self.nomes['arquivo_buscar_empresas'],
                                          f"INFO - Iniciando o processo no banco: {base_muro}")
                self.buscar_connections_strings(servidor_selecionado, lista_empresas_instancia, base_muro)

                tam_lista_empresas_localizadas = len(self.catalog['DATABASE_NAME'])
                for emp in range(tam_lista_empresas_localizadas):
                    try:
                        cnx = pyodbc.connect(f"DRIVER=SQL Server;SERVER={servidor_selecionado['server']};DATABASE={self.catalog['DATABASE_NAME'][emp]};ENCRYPT=not;UID={servidor_selecionado['username']};PWD={servidor_selecionado['password']}",
                            autocommit=True)
                        cursor = cnx.cursor()
                        cursor.execute(f"""
use [{self.catalog['DATABASE_NAME'][emp]}]
IF OBJECT_ID('DBCCPAGE') IS NOT NULL DROP TABLE DBCCPAGE;
CREATE TABLE DBCCPAGE (
ParentObject VARCHAR(255),
[OBJECT] VARCHAR(255),
Field VARCHAR(255),
[VALUE] VARCHAR(255));
INSERT INTO DBCCPAGE
EXECUTE ('DBCC PAGE (''{self.catalog['DATABASE_NAME'][emp]}'', 1, 9, 3) WITH TABLERESULTS;');
""")
                        cursor = cnx.cursor()
                        cursor.execute(f"""
SELECT VALUE FROM DBCCPAGE
WHERE [Field] = 'dbi_modDate';
""")
                        data_criacao_db = (cursor.fetchall())
                        data_criacao_db = data_criacao_db[0].VALUE
                        lista_infos_emp[f'{data_criacao_db}'] = []
                        lista_infos_emp[f'{data_criacao_db}'].append(f"{self.catalog['DATABASE_NAME'][emp]}")
                        cursor = cnx.cursor()
                        cursor.execute(f"""
use [{self.catalog['DATABASE_NAME'][emp]}]
drop table DBCCPAGE
                        """)
                        cursor = cnx.cursor()
                        cursor.execute(f"""SELECT TOP 1 TX_RAZ_SOC FROM [userNewPoint].[EMPRESA_MATRIZ];""")
                        lista_infos_emp[f'{data_criacao_db}'].append(cursor.fetchone())
                        cursor = cnx.cursor()
                        cursor.execute(f"""SELECT TOP 1 NU_CNPJ_CPF FROM [userNewPoint].[empresa];""")
                        lista_infos_emp[f'{data_criacao_db}'].append(cursor.fetchone())
                        cursor = cnx.cursor()
                        cursor.execute(f"""SELECT TOP 1 TX_LOGN FROM [userNewPoint].[USUARIO_CONTROLE_ACESSO] where [TX_LOGN] != 'dmpmaster';""")
                        lista_infos_emp[f'{data_criacao_db}'].append(cursor.fetchone())
                        cursor = cnx.cursor()
                        cursor.execute(f"""select COUNT(id_pess) as QUANT from [userNewPoint].[PESSOA];""")
                        lista_infos_emp[f'{data_criacao_db}'].append(cursor.fetchone())
                        cursor = cnx.cursor()
                        cursor.execute(f"""select COUNT(ID_EMPR) as QUANT from [userNewPoint].[EMPRESA];""")
                        lista_infos_emp[f'{data_criacao_db}'].append(cursor.fetchone())
                    except (Exception or pyodbc.DatabaseError) as error:
                        self.escrever_no_input(f"- Erro ao consultar empresa {self.catalog['DATABASE_NAME'][emp]} - {error}")
                        self.escrever_arquivo_log(self.nomes['arquivo_buscar_empresas'],
                                                  f"ERRO - Erro ao consultar empresa {self.catalog['DATABASE_NAME']}")
                    else:
                        calculo = ((emp + 1) / tam_lista_empresas_localizadas) * 100
                        porcentagem = '{:02.0f}'.format(calculo)
                        self.escrever_no_input(f"- Buscando Dados nas empresas: {porcentagem}%")
                        continue
                for key_info in lista_infos_emp:
                    lista_sort_infos_emp.append(key_info)
                lista_sort_infos_emp.sort()
                for emp in (lista_sort_infos_emp):
                    texto_em_tela = (f"""- Data Criação: {emp}
- Database: {lista_infos_emp[emp][0]}
- Razão Social: {lista_infos_emp[emp][1][0]}
- CNPJ/CPF: {lista_infos_emp[emp][2][0]}
- Usuario: {lista_infos_emp[emp][3][0]}
- Quantidade Funcionarios: {lista_infos_emp[emp][4][0]}
- Quantidade Empresas: {lista_infos_emp[emp][5][0]}
----------------------------------------------------""")
                    self.escrever_no_input(texto_em_tela)
                    self.escrever_arquivo_log(self.nomes['arquivo_buscar_empresas'],f"INFO - Data Criação: {emp} - Database: {lista_infos_emp[emp][0]} - Razão Social: {lista_infos_emp[emp][1][0]} - CNPJ/CPF: {lista_infos_emp[emp][2][0]} - Usuario: {lista_infos_emp[emp][3][0]}- Quantidade Funcionarios: {lista_infos_emp[emp][4][0]} - Quantidade Empresas: {lista_infos_emp[emp][5][0]}")

        except (Exception or pyodbc.DatabaseError) as error:
            self.escrever_no_input(f"- Falha ao tentar consultar banco: {error}")
            self.escrever_arquivo_log(self.nomes['arquivo_buscar_empresas'],
                                      f"ERRO - Falha ao tentar consultar banco: {error}")
            self.button_busca_empresa_atualizacao_inicio.config(state='normal')
            self.button_busca_empresa_atualizacao_limpar.config(state='normal')
            self.button_busca_empresa_atualizacao_voltar.config(state='normal')
            self.combobox_busca_empresa_servidor_version.config(state='normal')
            self.combobox_busca_empresa_banco_muro.config(state='normal')
            self.button_menu_sair.config(state='normal')
        else:
            self.button_busca_empresa_atualizacao_inicio.config(state='normal')
            self.button_busca_empresa_atualizacao_limpar.config(state='normal')
            self.button_busca_empresa_atualizacao_voltar.config(state='normal')
            self.combobox_busca_empresa_servidor_version.config(state='normal')
            self.combobox_busca_empresa_banco_muro.config(state='normal')
            self.button_menu_sair.config(state='normal')

    def buscar_connections_strings(self, servidor_selecionado, lista_string_instancia, base_muro):
        # Iniciando processo banco muro.
        # Configurando as Variáveis
        self.catalog = dict()
        self.catalog['CONNECTION_STRING'] = []
        self.catalog['DATABASE_NAME'] = []
        self.catalog['DATABASE_ID'] = []
        lista_connection_string = []
        index_banco = []
        string_limpa = []
        connection_string = []
        database_id = []
        atual_connection_string = []
        atual_database_name = []
        atual_database_id = []
        lista_limpa_nomes_instancia = []
        database_name = []

        # Pega a lista de connections strings
        try:
            cnxn1 = pyodbc.connect(
                f"DRIVER=SQL Server;SERVER={servidor_selecionado["server"]};ENCRYPT=not;UID={servidor_selecionado['username']};PWD={servidor_selecionado['password']}")
            cursor1 = cnxn1.cursor()
            cursor1.execute(
                f"SELECT [DATABASE_ID],[CONNECTION_STRING] FROM {base_muro}.[dbo].[KAIROS_DATABASES]")
            lista_connection_string = cursor1.fetchall()

        except (Exception or pyodbc.DatabaseError) as err:
            self.escrever_no_input(f"- Falha ao tentar consultar banco de muro: {err}")
            self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'],
                                      f"ERRO - Falha ao tentar consultar banco de muro {err} ")
        else:
            cursor1.commit()

            self.escrever_no_input(f"- Quantidade de registros encontrados: {len(lista_connection_string)}")
            self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'],
                                      f"INFO - Quantidade de registros encontrados: {len(lista_connection_string)} ")

        for i in range(len(lista_connection_string)):
            atual_connection_string.append(lista_connection_string[i].CONNECTION_STRING)
            atual_database_name.append(lista_connection_string[i].CONNECTION_STRING.split(';')[1].split('=')[1])
            atual_database_id.append(lista_connection_string[i].DATABASE_ID)
            continue

        for e in range(len(lista_string_instancia)):
            lista_limpa_nomes_instancia.append(lista_string_instancia[e].name)

        self.catalog['CONNECTION_STRING'] = atual_connection_string
        self.catalog['DATABASE_NAME'] = atual_database_name
        self.catalog['DATABASE_ID'] = atual_database_id

        # Comparar bancos "strings"
        self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"INFO - Iniciando a comparação dos bancos ")
        for comparar in range(len(lista_string_instancia)):
            if lista_limpa_nomes_instancia[comparar] in self.catalog['DATABASE_NAME']:
                database_name.append(lista_limpa_nomes_instancia[comparar])
                index_banco.append(self.catalog['DATABASE_NAME'].index(lista_limpa_nomes_instancia[comparar]))
                index_banco.sort()
            continue

        for nums in range(len(index_banco)):
            connection_string.append(self.catalog['CONNECTION_STRING'][index_banco[nums]])
            database_id.append(self.catalog['DATABASE_ID'][index_banco[nums]])

        self.catalog['DATABASE_ID'] = database_id
        self.catalog['CONNECTION_STRING'] = connection_string
        self.catalog['DATABASE_NAME'] = database_name

        if len(connection_string) > 0:
            self.escrever_no_input("- Quantidade de bancos que deram Match: " + str(len(connection_string)))
            self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'],
                                      f"INFO - Quantidade de bancos que deram Match: {len(connection_string)} ")
        else:
            self.escrever_no_input("- Não foram encontrados Match na comparação de bancos")
            self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'],
                                      f"INFO - Não foram encontrados Match na comparação de bancos ")

        for lim in range(len(connection_string)):
            string_limpa.append(connection_string[lim])
            continue

        # Logando as connection string
        quant = 1
        self.escrever_arquivo_log(self.nomes['arquivo_connection_strings'], f"INFO - Buscar Bancos - Listando as connection strings utilizadas ")
        self.escrever_arquivo_log(self.nomes['arquivo_connection_strings'], f"INFO - Buscar Bancos - Ambiente: {base_muro} ")
        for log in range(len(connection_string)):
            self.escrever_arquivo_log(self.nomes['arquivo_connection_strings'], f"INFO - {quant} - {connection_string[log]}")
            quant += 1
            continue
        self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"INFO - Listado as Connection Strings no arquivo: {self.nomes['arquivo_connection_strings']} ")

    def manipular_banco_update(self):
        try:
            self.entry.config(state='disabled')
            self.combobox_servidor.config(state='disabled')
            self.button_busca_inicio.config(state='disabled')
            self.button_busca_limpar.config(state='disabled')
            self.button_busca_voltar.config(state='disabled')
            self.button_menu_sair.config(state='disabled')
            self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Rotina - Buscar Bancos")
            lista_string_instancia = ''
            cursor1 = ''
            status_consulta = False

            self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], "INFO - Inicio da operação Busca muro ")

            versao_databases = self.entry.get()
            server = self.combobox_servidor.get()
            if versao_databases == '' or versao_databases == self.placeholder_text:
                self.escrever_no_input(f"- O campo Version não pode estar em branco")
                self.button_busca_inicio.config(state='normal')
                self.button_busca_limpar.config(state='normal')
                self.button_busca_voltar.config(state='normal')
                self.combobox_servidor.config(state='normal')
                self.entry.config(state='normal')
                self.button_menu_sair.config(state='normal')
                return
            elif server == "":
                self.escrever_no_input(f"- Deverá ser selecionado o servidor, antes de prosseguir")
                self.button_busca_inicio.config(state='normal')
                self.button_busca_limpar.config(state='normal')
                self.button_busca_voltar.config(state='normal')
                self.combobox_servidor.config(state='normal')
                self.entry.config(state='normal')
                self.button_menu_sair.config(state='normal')
                return
            else:
                servidor_selecionado = self.infos_config["conexoes"][server]
                self.escrever_no_input(f"- Version para downgrade: {versao_databases}")
                self.escrever_arquivo_log(
                    self.nomes['arquivo_busca_bancos'], f"INFO - Version para downgrade: {versao_databases} ")

                # Pegar a lista de bancos da instancia
                self.escrever_arquivo_log(
                    self.nomes['arquivo_busca_bancos'], f"INFO - Iniciando a busca dos bancos na instância: {servidor_selecionado["server"]} ")

                try:
                    cnxn1 = pyodbc.connect(
                        f"DRIVER=SQL Server;SERVER={servidor_selecionado["server"]};ENCRYPT=not;UID={servidor_selecionado['username']};PWD={servidor_selecionado['password']}")
                    cursor1 = cnxn1.cursor()
                    cursor1.execute("SELECT name FROM sys.databases;")
                    lista_string_instancia = cursor1.fetchall()
                except (Exception or pyodbc.DatabaseError) as err:
                    self.escrever_no_input(f"- Falha ao tentar buscar os bancos da instancia {err}")
                    self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"ERRO - Falha ao tentar buscar os bancos da instancia {err} ")
                else:
                    cursor1.commit()

                    self.escrever_no_input(f"- Quantidade de bancos encontrados na instância: {len(lista_string_instancia)}")
                    self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"INFO - Quantidade de bancos encontrados: {len(lista_string_instancia)} ")
                    status_consulta = True
                if status_consulta:
                    # Iniciando processo banco muro.
                    num = 1
                    tam_list_muros = len(self.infos_config.get('bases_muro'))
                    for base_muro in self.infos_config.get('bases_muro'):
                        self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"INFO - Iniciando o processo no banco: {base_muro} ")
                        self.escrever_no_input(f"\n- Iniciando o processo no banco: {base_muro}")
                        self.buscar_connections_strings(servidor_selecionado, lista_string_instancia, base_muro)
                        database_update = self.valida_banco_update(base_muro)
                        if len(self.catalog['CONNECTION_STRING']) > 0:
                            # Limpeza base muro UPDATE
                            self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'],
                                                      f"INFO - limpando o banco: {database_update} ")
                            try:
                                cursor1.execute(f'DELETE FROM {database_update}.[dbo].[KAIROS_DATABASES]')

                            except (Exception or pyodbc.DatabaseError) as err:
                                self.escrever_no_input(f"- Falha ao tentar zerar o banco update {err}")
                                self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"ERRO - Falha ao tentar zerar o banco de muro update {err} ")
                            else:
                                cursor1.commit()
                                self.escrever_no_input(f"- banco update zerado com sucesso")
                                self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"INFO - Banco update zerado com sucesso ")
                        else:
                            self.escrever_no_input("- Não foi realizada a limpeza no banco: " + database_update)
                            self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"INFO - Não foi realizada a limpeza no banco: {database_update} ")

                        # Inserindo as connections strings no banco muro update
                        self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"INFO - Iniciando o processo de inserção:  {database_update} ")
                        if len(self.catalog['CONNECTION_STRING']) > 0:
                            try:
                                cnxn1 = pyodbc.connect(
                                    f"DRIVER=SQL Server;SERVER={servidor_selecionado["server"]};DATABASE={database_update};ENCRYPT=not;UID={servidor_selecionado['username']};PWD={servidor_selecionado['password']}")
                                cursor1 = cnxn1.cursor()

                                cursor1.execute("set identity_insert [dbo].[KAIROS_DATABASES]  on")
                                for incs in range(len(self.catalog['CONNECTION_STRING'])):
                                    montar_comando = f"INSERT INTO [{database_update}].[dbo].[KAIROS_DATABASES] ([DATABASE_ID],[CONNECTION_STRING] ,[DATABASE_VERSION] ,[FL_MAQUINA_CALCULO] ,[FL_ATIVO]) VALUES({self.catalog['DATABASE_ID'][incs]},'{self.catalog['CONNECTION_STRING'][incs]}',{versao_databases},0, 1)"
                                    cursor1.execute(montar_comando)
                                    continue
                                cursor1.execute("set identity_insert [dbo].[KAIROS_DATABASES]  off")

                            except (Exception or pyodbc.DatabaseError) as err:
                                self.escrever_no_input(f"- Falha ao tentar inserir registros no banco update {err}")
                                self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"ERRO - Falha ao tentar inserir registros no banco update {err} ")
                            else:
                                cursor1.commit()
                                self.escrever_no_input("- Sucesso ao inserir registros no Banco")
                                self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"INFO - Sucesso ao inserir connection Strings no Banco de muro Update ")
                        else:
                            self.escrever_no_input("- Não a registros para serem inseridos no banco: " + database_update)
                            self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"INFO - Não a registros para serem inseridos no banco: {database_update} ")


                        self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"INFO - Concluído a parte {num}, de um total de {tam_list_muros}. ")
                        num += 1
                        continue
                    cursor1.close()
                else:
                    self.escrever_no_input(f"- Erro na primeira etapa das buscas, o processo foi interrompido.")
                    self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"INFO - Erro na primeira etapa das buscas, o processo foi interrompido. ")

                self.escrever_no_input(f"\n- Fim da operação Busca muro")
                self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"INFO - Fim da operação Busca muro")
                self.entry.config(state='normal')
                self.button_busca_inicio.config(state='normal')
                self.button_busca_limpar.config(state='normal')
                self.button_busca_voltar.config(state='normal')
                self.combobox_servidor.config(state='normal')
                self.button_menu_sair.config(state='normal')
        except Exception as error:
            self.escrever_no_input(f"Exceção não tratada: {error}")
            self.entry.config(state='normal')
            self.button_busca_inicio.config(state='normal')
            self.button_busca_limpar.config(state='normal')
            self.button_busca_voltar.config(state='normal')
            self.combobox_servidor.config(state='normal')
            self.button_menu_sair.config(state='normal')

    def replicar_version(self):
        try:
            self.button_replicar_inicio.config(state='disabled')
            self.button_replicar_limpar.config(state='disabled')
            self.button_replicar_voltar.config(state='disabled')
            self.combobox_servidor_replicar.config(state='disabled')
            self.button_menu_sair.config(state='disabled')
            server = self.combobox_servidor_replicar.get()
            tam_base_muro = len(self.infos_config['bases_muro'])
            self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Rotina - Replicar version ")

            self.escrever_arquivo_log(self.nomes['arquivo_replicar_version'], f"INFO - Inicio da operação replicar version")
            if server == "":
                self.escrever_no_input(f"- Deverá ser selecionado o servidor, antes de prosseguir")
                self.button_atualizacao_inicio.config(state='normal')
                self.button_replicar_limpar.config(state='normal')
                self.button_atualizacao_voltar.config(state='normal')
                self.combobox_servidor_replicar.config(state='normal')
                self.button_menu_sair.config(state='normal')
                return
            servidor_selecionado = self.infos_config["conexoes"][server]
            for num in range(len(self.infos_config['bases_muro'])):
                lista_registros_db = []
                lista_ids = []
                lista_versions = []
                lista_connection_string = []

                self.escrever_no_input(f"\n- replicando para: {self.infos_config['bases_muro'][num]}")
                self.escrever_arquivo_log(self.nomes['arquivo_replicar_version'], f"INFO - Replicando para: {self.infos_config['bases_muro'][num]}")

                database_update = self.valida_banco_update(num)

                try:
                    cnxnrp1 = pyodbc.connect(
                        f"DRIVER=SQL Server;SERVER={servidor_selecionado['server']};DATABASE={database_update};ENCRYPT=not;UID={servidor_selecionado['username']};PWD={servidor_selecionado['password']}")
                    cursorrp1 = cnxnrp1.cursor()
                    cursorrp1.execute(f"SELECT * FROM {database_update}.[dbo].[KAIROS_DATABASES]")
                    lista_registros_db = cursorrp1.fetchall()
                except (Exception or pyodbc.DatabaseError) as err:
                    self.escrever_no_input("- Falha ao tentar consultar banco de muro update: " + str(err))
                    self.escrever_arquivo_log(self.nomes['arquivo_replicar_version'], f"ERRO - Falha ao tentar consultar banco de muro update: {err}")
                else:
                    cursorrp1.commit()
                    cursorrp1.close()

                    self.escrever_no_input(f"- Sucesso na consulta: {database_update}")
                    self.escrever_arquivo_log(self.nomes['arquivo_replicar_version'], f"INFO - Sucesso na consulta no banco de muro update: {database_update}")

                    self.escrever_no_input(f"- Quantidade de registros encontrados: {len(lista_registros_db)}")
                    self.escrever_arquivo_log(self.nomes['arquivo_replicar_version'], f"INFO - Quantidade de registros encontrados: {len(lista_registros_db)}")

                tam_busca_realizada = len(lista_registros_db)
                if tam_busca_realizada > 0:
                    for nums in range(tam_busca_realizada):
                        lista_ids.append(lista_registros_db[nums].DATABASE_ID)
                        lista_versions.append(lista_registros_db[nums].DATABASE_VERSION)
                        lista_connection_string.append(lista_registros_db[nums].CONNECTION_STRING)
                        continue

                    try:
                        cnxnrp2 = pyodbc.connect(
                            f"DRIVER=SQL Server;SERVER={servidor_selecionado['server']};DATABASE={self.infos_config['bases_muro'][num]};ENCRYPT=not;UID={servidor_selecionado['username']};PWD={servidor_selecionado['password']}")
                        cursorrp2 = cnxnrp2.cursor()
                        for teste2 in range(tam_busca_realizada):
                            montar_comando = f"update [dbo].[KAIROS_DATABASES] set [DATABASE_VERSION] = {lista_versions[teste2]} where [DATABASE_ID] = {lista_ids[teste2]} and [CONNECTION_STRING] = '{lista_connection_string[teste2]}' "
                            cursorrp2.execute(montar_comando)
                            continue
                    except (Exception or pyodbc.DatabaseError) as err:
                        self.escrever_no_input(f"- Falha ao tentar consultar banco de muro update: {err}")
                        self.escrever_arquivo_log(self.nomes['arquivo_replicar_version'], f"ERRO - Falha ao tentar consultar banco de muro update: {err}")
                    else:
                        cursorrp2.commit()
                        cursorrp2.close()
                        self.escrever_no_input(
                            f"- Sucesso ao inserir version's")
                        self.escrever_arquivo_log(
                            self.nomes['arquivo_replicar_version'], f"INFO - Sucesso ao inserir version's")

                        # Logando as connection string
                        self.escrever_arquivo_log(self.nomes['arquivo_connection_strings'], f"INFO - Replicar Version - Listando as connection strings utilizadas ")
                        self.escrever_arquivo_log(self.nomes['arquivo_connection_strings'], f"INFO - Replicar Version - Ambiente: {self.infos_config['bases_muro'][num]} ")
                        quant = 1
                        for log in range(tam_busca_realizada):
                            log_versions = (f"INFO - {quant} - ID: {lista_ids[log]} - Version: {lista_versions[log]} ")
                            self.escrever_arquivo_log(self.nomes['arquivo_connection_strings'], log_versions)
                            quant += 1
                            continue

                        self.escrever_arquivo_log(self.nomes['arquivo_connection_strings'], f"INFO - Processo finalizado")
                        self.escrever_arquivo_log(self.nomes['arquivo_replicar_version'], f"INFO - Listado os version no arquivo: {self.nomes['arquivo_connection_strings']}")
                else:
                    self.escrever_no_input("- Não existem registros para alterar o version")
                    self.escrever_arquivo_log(self.nomes['arquivo_replicar_version'], f"INFO - Não existem registros para alterar o version")

                if num < 4:
                    num += 1

                self.escrever_arquivo_log(self.nomes['arquivo_replicar_version'], f"INFO - Concluído a parte {num}, de um total de {tam_base_muro}.")
                continue

            self.escrever_no_input(f"\n- Fim da operação replicar version")
            self.escrever_arquivo_log(self.nomes['arquivo_replicar_version'], f"INFO - Fim da operação replicar version")
            self.button_replicar_inicio.config(state='normal')
            self.button_replicar_limpar.config(state='normal')
            self.button_replicar_voltar.config(state='normal')
            self.combobox_servidor_replicar.config(state='normal')
            self.button_menu_sair.config(state='normal')

        except Exception as error:
            self.escrever_no_input(f"Exceção não tratada: {error}")
            self.button_replicar_inicio.config(state='normal')
            self.button_replicar_limpar.config(state='normal')
            self.button_replicar_voltar.config(state='normal')
            self.combobox_servidor_replicar.config(state='normal')
            self.button_menu_sair.config(state='normal')

    def valida_banco_update(self, base_muro):
        database_update = ''
        if "mdcomune" in base_muro.lower():
            database_update = self.infos_config['database_update_md']
        elif "pt" in base_muro.lower():
            database_update = self.infos_config['database_update_pt']
        elif "mx" in base_muro.lower():
            database_update = self.infos_config['database_update_mx']
        elif "kairos_base_muro" in base_muro.lower():
            database_update = self.infos_config['database_update_br']
        else:
            self.escrever_no_input(
                "- Não foi inserido no arquivo de config o apontamento para o banco Muro update")
        return database_update

    def restaurar_banco(self):
        try:
            self.alterar_status_campos_tela(False)
            self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Rotina - Restaurar Backup")

            valores_entries = []
            caminho_banco_mdf = ''

            server = self.combobox_servidor_restaurar.get()
            for entry_atual in self.entries:
                valores_entries.append(entry_atual.get())
            nome_bak = valores_entries[1].strip().split('.')[0]
            nome_banco_escolhido = valores_entries[2].strip().split('.')[0]
            caminho_ldf_mdf = valores_entries[0].split(',')
            caminho_banco_ldf = caminho_ldf_mdf[0].strip()
            if len(caminho_ldf_mdf) > 1:
                caminho_banco_mdf = caminho_ldf_mdf[1].strip()

            caminho_eventual = 'G:\\Backup\\Eventual'

            if nome_bak == "":
                self.escrever_no_input("- O campo 'Nome arquivo.bak' deverá ser preenchido")
                self.alterar_status_campos_tela(True)
                self.escrever_no_input("- Processo finalizado")
                return
            elif nome_banco_escolhido == "":
                self.escrever_no_input("- O campo 'Nome do banco' deverá ser preenchido")
                self.alterar_status_campos_tela(True)
                self.escrever_no_input("- Processo finalizado")
                return
            elif caminho_banco_ldf == "":
                self.escrever_no_input("- O Valor de LDF deverá ser preenchido")
                self.alterar_status_campos_tela(True)
                self.escrever_no_input("- Processo finalizado")
                return
            elif caminho_banco_mdf == "":
                self.escrever_no_input("- O Valor de MDF deverá ser preenchido")
                self.alterar_status_campos_tela(True)
                self.escrever_no_input("- Processo finalizado")
                return
            elif server == "":
                self.escrever_no_input(f"- Deverá ser selecionado o servidor, antes de prosseguir")
                self.alterar_status_campos_tela(True)
                self.escrever_no_input("- Processo finalizado")
                return
            else:
                servidor_selecionado = self.infos_config["conexoes"][server]
                self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"INFO - Inserido o nome do banco apresentado no discord: {nome_bak} ")
                self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"INFO - Escolhido o servidor: {servidor_selecionado['server']} ")

                try:
                    cnxnrs = pyodbc.connect(f"DRIVER=SQL Server;SERVER={servidor_selecionado['server']};ENCRYPT=not;UID={servidor_selecionado['username']};PWD={servidor_selecionado['password']}", autocommit=True)
                    cnxnrs.setencoding(encoding='utf-8')
                    cursorrs = cnxnrs.cursor()
                    cursorrs.execute(f" USE [master]; EXEC Sp_addumpdevice'disk', '{nome_banco_escolhido}', '{caminho_eventual}\\{nome_bak}.bak';")
                    result_criar_device = cursorrs.messages
                    time.sleep(5)
                    cursorrs.close()
                except (Exception or pyodbc.DatabaseError) as error:
                    self.escrever_no_input(
                        "- Falha ao tentar executar o comando de criação de device de backup " + str(error))
                    self.escrever_arquivo_log(
                        self.nomes['arquivo_restaurar_banco'], f"ERRO - Falha ao tentar executar o comando de criação de device de backup: {error} ")
                    self.escrever_no_input("- Processo finalizado")
                    self.alterar_status_campos_tela(True)
                    return
                else:
                    self.escrever_no_input(f"- Comando(Criação de Device) - Sucesso ao realizar Criar Device de Backup")
                    self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"INFO - Comando(Criação de Device) - Sucesso ao realizar Criar Device de Backup ")
                    status_etapa1 = True
                    for incs in range(len(result_criar_device)):
                        separados = result_criar_device[0][1].split("]")
                        mensagem = separados[3]
                        self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"INFO - Comando(Criação Device) -  Mensagem SQL: {mensagem} ")

                if status_etapa1:
                    try:
                        cursorrs = cnxnrs.cursor()
                        cursorrs.execute(f"""USE [master]; RESTORE DATABASE "{nome_banco_escolhido}" FROM DISK ='{caminho_eventual}\\{nome_bak}.bak' WITH norecovery, stats = 1, move '{nome_bak}_log' TO '{caminho_banco_ldf}\\{nome_banco_escolhido}_log.ldf', move '{nome_bak}' TO '{caminho_banco_mdf}\\{nome_banco_escolhido}.mdf'""")
                        time.sleep(5)
                    except (Exception or pyodbc.DatabaseError) as error:
                        self.escrever_no_input("- Falha ao tentar executar o comando de restauração de banco: " + str(error))
                        self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"ERRO - Falha ao tentar executar o comando de restauração de banco: {error} ")
                        self.escrever_no_input("- Processo finalizado")
                        self.alterar_status_campos_tela(True)
                        return
                    else:
                        mensagens = []
                        posicao = 3
                        while True:
                            if cursorrs.messages:
                                mensagem = cursorrs.messages
                                separados = mensagem[0][1].split("]")
                                mensagens.append(separados[3])
                                cursorrs.nextset()
                                continue
                            else:
                                break
                        self.escrever_no_input(f"- Comando(Restaurar Banco) - Sucesso ao realizar a restauração do banco")
                        self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"INFO - Comando(Restaurar Banco) - Sucesso ao realizar a restauração do banco ")

                        tam = len(mensagens) - 3
                        for incs in range(posicao):
                            self.escrever_no_input(f"- Comando(Restauração DB) -  Mensagem SQL: {mensagens[tam]}  ")
                            self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"INFO - Comando(Restauração DB) -  Mensagem SQL: {mensagens[tam]} ")
                            tam += 1

                        try:
                            cursorrs = cnxnrs.cursor()
                            cursorrs.execute(f"""RESTORE DATABASE "{nome_banco_escolhido}" WITH recovery ALTER DATABASE "{nome_banco_escolhido}" SET recovery simple""")
                            result_ativar_banco = cursorrs.messages
                            time.sleep(5)
                        except (Exception or pyodbc.DatabaseError) as error:
                            self.escrever_no_input("- Falha ao tentar executar o comando de Ativação do banco: " + str(error))
                            self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"ERRO - Falha ao tentar executar o comando de Ativação do banco: {error} ")
                            self.escrever_no_input("- Processo finalizado")
                            self.alterar_status_campos_tela(True)
                            return
                        else:
                            tam_result = len(result_ativar_banco) - 1
                            while tam_result < len(result_ativar_banco):
                                separados = result_ativar_banco[tam_result][1].split("]")
                                mensagem = separados[3]
                                self.escrever_no_input(f"- Comando(Ativação DB) -  Mensagem SQL: {mensagem}  ")
                                self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"INFO - Comando(Ativação DB) -  Mensagem SQL: {mensagem} ")
                                tam_result += 1

                            try:
                                cursorrs = cnxnrs.cursor()
                                cursorrs.execute(f"""DBCC CHECKDB("{nome_banco_escolhido}")""")
                                result_check = cursorrs.messages
                                time.sleep(5)
                            except (Exception or pyodbc.DatabaseError) as error:
                                self.escrever_no_input(
                                    "- Falha ao tentar executar o comando de checagem do banco: " + str(error))
                                self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"ERRO - Falha ao tentar executar o comando de checagem do banco: {error} ")
                                self.escrever_no_input("- Processo finalizado")
                                self.alterar_status_campos_tela(True)
                                return
                            else:
                                time.sleep(5)
                                looping = True
                                tam_result = len(result_check) - 2
                                while looping:
                                    if tam_result < len(result_check):
                                        separados = result_check[tam_result][1].split("]")
                                        mensagem = separados[3]
                                        self.escrever_no_input(f"- Comando(Checagem DB) - Mensagem SQL: {mensagem}")
                                        self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"INFO - Comando(Checagem DB) - Mensagem SQL: {mensagem} ")
                                        tam_result += 1
                                    else:
                                        looping = False
                                try:
                                    cursorrs = cnxnrs.cursor()
                                    cursorrs.execute(f"""USE [master]; EXEC Sp_dropdevice "{nome_banco_escolhido}";""")
                                    result_excluir_device = cursorrs.messages
                                    time.sleep(5)
                                except (Exception or pyodbc.DatabaseError) as error:
                                    self.escrever_no_input("- Falha ao tentar executar o comando exclusão de device: " + str(error))
                                    self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"ERRO - Falha ao tentar executar o comando de checagem do banco: {error} ")
                                    self.escrever_no_input("- Processo finalizado")
                                    self.alterar_status_campos_tela(True)
                                    return
                                else:
                                    for incs in range(len(result_excluir_device)):
                                        separados = result_excluir_device[0][1].split("]")
                                        mensagem = separados[3]
                                        self.escrever_no_input(f"- Comando(Exclusão Device) -  Mensagem SQL: {mensagem}")
                                        self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"INFO - Comando(Exclusão Device) -  Mensagem SQL: {mensagem}")
                                    try:
                                        cursorrs = cnxnrs.cursor()
                                        cursorrs.execute(f"""USE [{nome_banco_escolhido}] EXEC sp_addrolemember N'db_owner',  N'userNewPoint' EXEC sp_change_users_login 'Update_One', 'userNewPoint','userNewPoint' EXEC sp_addrolemember N'db_owner',  N'newPoint' EXEC sp_change_users_login 'Update_One', 'newPoint', 'newPoint'""")
                                        associar_owner = cursorrs.messages
                                        time.sleep(5)
                                    except (Exception or pyodbc.DatabaseError) as error:
                                        self.escrever_no_input(
                                            "- Falha ao tentar executar o comando de associação do Owner: " + str(error))
                                        self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"ERRO - Falha ao tentar executar o comando de associação do Owner:  {error} ")
                                        self.escrever_no_input("- Processo finalizado")
                                        self.alterar_status_campos_tela(True)
                                        return
                                    else:
                                        separados = associar_owner[0][1].split("]")
                                        mensagem = separados[3]
                                        self.escrever_no_input(f"- Comando(Associar Owner) - Mensagem SQL: {mensagem}")
                                        self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"INFO - Comando(Script Associar Owner) - Mensagem SQL: {mensagem} ")
                                        try:
                                            cursorrs = cnxnrs.cursor()
                                            cursorrs.execute(f"SELECT [TX_LOGN] FROM [userNewPoint].[USUARIO_CONTROLE_ACESSO] where [ID_USU_CNTRL_ACES] = 2")
                                            result_usuario = cursorrs.fetchall()
                                            time.sleep(5)
                                        except (Exception or pyodbc.DatabaseError) as error:
                                            self.escrever_no_input(
                                                "- Falha ao tentar executar o comando de busca de usuario: " + str(
                                                    error))
                                            self.escrever_arquivo_log(
                                                self.nomes['arquivo_restaurar_banco'],
                                                f"ERRO - Falha ao tentar executar o comando de busca de usuario: {error} ")
                                            self.escrever_no_input("- Processo finalizado")
                                            self.alterar_status_campos_tela(True)
                                            return
                                        else:
                                            mensagem = result_usuario[0]
                                            self.escrever_no_input(
                                                f"- Comando(Buscar Usuario) - O usuario que será alterado é: {mensagem}  ")
                                            self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'],
                                                                      f"INFO - Comando(Buscar Usuario) -  Mensagem SQL: {mensagem} ")
                                            try:
                                                cursorrs = cnxnrs.cursor()
                                                cursorrs.execute(f"""USE [{nome_banco_escolhido}] UPDATE [userNewPoint].[USUARIO_CONTROLE_ACESSO] SET [TX_SENHA] = '555BjkhiNWnXXip7Ca6I7Zt3sSakRbn/ncaYmgjvoHk=' WHERE [ID_USU_CNTRL_ACES] = 2""")
                                                time.sleep(5)
                                            except (Exception or pyodbc.DatabaseError) as error:
                                                self.escrever_no_input(
                                                    "- Falha ao tentar executar o comando de alteração de usuario: " + str(
                                                        error))
                                                self.escrever_arquivo_log(
                                                    self.nomes['arquivo_restaurar_banco'],
                                                    f"ERRO - Falha ao tentar executar o comando de alteração de usuario: {error} ")
                                                self.escrever_no_input("- Processo finalizado")
                                                self.alterar_status_campos_tela(True)
                                                return
                                            else:
                                                self.escrever_no_input(
                                                    f"- Comando(Alterar Usuario) - Senha alterada com sucesso  ")
                                                self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'],
                                                                          f"INFO - Comando(Alterar Usuario) -  Mensagem SQL: {mensagem} ")
                    cursorrs.close()

                self.escrever_no_input("- Processo finalizado")
                self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"INFO - Processo finalizado")
                self.alterar_status_campos_tela(True)
        except Exception as error:
            self.escrever_no_input(f"Exceção não tratada: {error}")
            self.alterar_status_campos_tela(True)

    def download_backup(self):
        try:
            self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Rotina - Download Backup ")
            self.button_download_inicio.config(state='disabled')
            self.button_download_limpar.config(state='disabled')
            self.button_download_voltar.config(state='disabled')
            self.combobox_servidor_download.config(state='disabled')
            self.entry.config(state='disabled')
            self.button_menu_sair.config(state='disabled')
            server = self.combobox_servidor_download.get()
            endereco_download = self.entry.get()
            self.escrever_arquivo_log(self.nomes['arquivo_download_backup'],
                                      f"INFO - Inicio da operação Download Backup ")
            self.escrever_arquivo_log(self.nomes['arquivo_download_backup'],
                                      f"INFO - Inserida a URL de Download: {endereco_download} ")

            if server == "":
                self.escrever_no_input(f"- Deverá ser selecionado o servidor, antes de prosseguir")
                self.button_download_inicio.config(state='normal')
                self.button_download_limpar.config(state='normal')
                self.button_download_voltar.config(state='normal')
                self.combobox_servidor_download.config(state='normal')
                self.entry.config(state='normal')
                self.button_menu_sair.config(state='normal')
                return
            elif endereco_download == self.placeholder_text or endereco_download == "":
                self.escrever_no_input("- O campo URL deverá ser preenchido")
                self.button_download_inicio.config(state='normal')
                self.button_download_limpar.config(state='normal')
                self.button_download_voltar.config(state='normal')
                self.combobox_servidor_download.config(state='normal')
                self.entry.config(state='normal')
                self.button_menu_sair.config(state='normal')
                return
            else:
                servidor_selecionado = self.infos_config["conexoes"][server]
                comando = f"""xp_cmdshell 'powershell.exe -file C:\\wget\\download.ps1 bkp "{endereco_download}"'"""

                try:
                    cnxnrp1 = pyodbc.connect(
                        f"DRIVER=SQL Server;SERVER={servidor_selecionado["server"]};ENCRYPT=not;UID={servidor_selecionado['username']};PWD={servidor_selecionado['password']}")
                    cursorrp1 = cnxnrp1.cursor()
                    cursorrp1.execute(comando)
                    result = cursorrp1.fetchall()
                except (Exception or pyodbc.DatabaseError) as err:
                    self.escrever_no_input("- Falha ao tentar executar o comando " + str(err))
                    self.escrever_arquivo_log(self.nomes['arquivo_download_backup'], f"ERRO - Falha ao tentar executar o comando: {err} ")
                else:
                    cursorrp1.commit()

                    self.escrever_arquivo_log(self.nomes['arquivo_download_backup'],
                                              f"INFO - Sucesso ao realizar Download do backup ")
                    self.escrever_arquivo_log(self.nomes['arquivo_download_backup'],
                                              f"INFO - Resultado:")

                    for incs in range(len(result)):
                        semi_separado = (str(result[incs])).split("'")
                        if len(semi_separado) > 1:
                            separado = semi_separado[1].split("(")
                            limpo = separado[0]
                            self.escrever_no_input('- ' + str(limpo))
                            self.escrever_arquivo_log(self.nomes['arquivo_download_backup'], f"INFO - {limpo}")

                        else:
                            limpo = semi_separado[0]
                            self.escrever_no_input("- " + str(limpo))
                            self.escrever_arquivo_log(self.nomes['arquivo_download_backup'], f"INFO - {limpo}")

                    cursorrp1.close()

            self.escrever_no_input("- Processo finalizado")
            self.escrever_arquivo_log(self.nomes['arquivo_download_backup'], f"INFO - Processo finalizado ")
            self.combobox_servidor_download.config(state='normal')
            self.button_download_limpar.config(state='normal')
            self.entry.config(state='normal')
            self.button_download_inicio.config(state='normal')
            self.button_download_voltar.config(state='normal')
            self.button_menu_sair.config(state='normal')

        except Exception as error:
            self.escrever_no_input(f"Exceção não tratada: {error}")
            self.entry.config(state='normal')
            self.combobox_servidor_download.config(state='normal')
            self.button_download_limpar.config(state='normal')
            self.button_download_inicio.config(state='normal')
            self.button_download_voltar.config(state='normal')
            self.button_menu_sair.config(state='normal')

    def limpar_todos_redis(self):
        try:
            self.button_atualizacao_inicio.config(state='disabled')
            self.button_atualizacao_limpar.config(state='disabled')
            self.button_atualizacao_voltar.config(state='disabled')
            self.combobox_redis_grupo.config(state='disabled')
            self.button_menu_sair.config(state='disabled')
            self.escrever_arquivo_log(self.nomes['arquivo_redis'], f"INFO - Inicio da operação Limpar todos Redis ")
            grupo_redis = self.combobox_redis_grupo.get()
            conexoes_atual = ''
            if grupo_redis == "":
                self.escrever_no_input("- Nenhum grupo selecionado, favor escolher e tentar novamente")
                self.escrever_arquivo_log(self.nomes['arquivo_redis'], f"ERRO - Nenhum grupo selecionado, favor escolher e tentar novamente ")
                self.escrever_no_input("- Processo finalizado")
                self.escrever_arquivo_log(self.nomes['arquivo_redis'], f"INFO - Processo finalizado ")
                self.button_atualizacao_inicio.config(state='normal')
                self.button_atualizacao_limpar.config(state='normal')
                self.button_atualizacao_voltar.config(state='normal')
                self.combobox_redis_grupo.config(state='normal')
                self.button_menu_sair.config(state='normal')
                return
            else:
                tam_redis = len(self.infos_config['redis_qa'])
                for red_grupo_atual in self.infos_config['redis_qa']:
                    if red_grupo_atual == grupo_redis:
                        grupo_atual = self.infos_config['redis_qa'][red_grupo_atual]
                        if len(grupo_atual) > 1:
                            conexoes_atual = grupo_atual
                            break
                        else:
                            if grupo_atual[0]['ip'] != '':
                                conexoes_atual = grupo_atual
                                break
                            else:
                                break
                if conexoes_atual != '':
                    for redis_atual in conexoes_atual:
                        try:
                            self.escrever_no_input(f"- Iniciado processo no Redis {redis_atual['nome_redis']}")
                            self.escrever_arquivo_log(self.nomes['arquivo_redis'],f"INFO - Iniciado processo no Redis {redis_atual['nome_redis']} ")
                            redis_host = redis_atual['ip']  # ou o endereço do seu servidor Redis
                            redis_port = redis_atual['port']  # ou a porta que o seu servidor Redis está ouvindo

                            # Criando uma instância do cliente Redis
                            redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

                            try:
                                # Executando o comando FLUSHALL
                                redis_client.flushall()
                            except Exception as err:
                                self.escrever_no_input(f"- Processo finalizado com falha: {err}")
                                self.escrever_arquivo_log(
                                    self.nomes['arquivo_redis'], f"INFO - Processo finalizado com falha: {err}")
                            else:
                                self.escrever_no_input(f"- FLUSHALL executado com sucesso no redis")
                                self.escrever_arquivo_log(
                                    self.nomes['arquivo_redis'], f"INFO - FLUSHALL executado com sucesso no redis")
                        except Exception as error:
                            self.escrever_no_input(f"- Erro ao selecionar redis: {error}")
                            continue
                else:
                    self.escrever_no_input(f"- Não foi encontrado conexões do redis")

            self.escrever_no_input("- Processo finalizado")
            self.escrever_arquivo_log(self.nomes['arquivo_redis'], f"INFO - Processo finalizado ")
            self.button_atualizacao_inicio.config(state='normal')
            self.button_atualizacao_limpar.config(state='normal')
            self.button_atualizacao_voltar.config(state='normal')
            self.combobox_redis_grupo.config(state='normal')
            self.button_menu_sair.config(state='normal')
        except Exception as error:
            self.escrever_no_input(f"Exceção não tratada: {error}")
            self.button_atualizacao_inicio.config(state='normal')
            self.button_atualizacao_limpar.config(state='normal')
            self.button_atualizacao_voltar.config(state='normal')
            self.combobox_redis_grupo.config(state='normal')
            self.button_menu_sair.config(state='normal')

    def limpar_redis_especifico(self):
        try:
            self.combobox_redis.config(state='disabled')
            self.combobox_redis_grupo.config(state='disabled')
            self.button_redis_inicio.config(state='disabled')
            self.button_redis_limpar.config(state='disabled')
            self.button_redis_voltar.config(state='disabled')
            self.button_menu_sair.config(state='disabled')
            self.escrever_arquivo_log(self.nomes['arquivo_redis'], f"INFO - Inicio da operação Limpar Redis especifico")
            grupo_selecionado = self.combobox_redis_grupo.get()
            redis_selecionado = self.combobox_redis.get()
            if grupo_selecionado == "":
                self.escrever_no_input("- O campo Grupo Redis não pode estar vazio")
                self.escrever_arquivo_log(self.nomes['arquivo_redis'], f"ERRO - O campo Grupo Redis não pode estar vazio ")
                self.escrever_no_input("- Processo finalizado")
                self.escrever_arquivo_log(self.nomes['arquivo_redis'], f"INFO - Processo finalizado ")
                self.button_redis_inicio.config(state='normal')
                self.button_redis_limpar.config(state='normal')
                self.button_redis_voltar.config(state='normal')
                self.combobox_redis.config(state='normal')
                self.combobox_redis_grupo.config(state='normal')
                self.button_menu_sair.config(state='normal')
                return
            if redis_selecionado == "":
                self.escrever_no_input("- O campo Redis não pode estar vazio")
                self.escrever_arquivo_log(self.nomes['arquivo_redis'], f"ERRO - O campo Redis não pode estar vazio ")
                self.escrever_no_input("- Processo finalizado")
                self.escrever_arquivo_log(self.nomes['arquivo_redis'], f"INFO - Processo finalizado ")
                self.button_redis_inicio.config(state='normal')
                self.button_redis_limpar.config(state='normal')
                self.button_redis_voltar.config(state='normal')
                self.combobox_redis.config(state='normal')
                self.combobox_redis_grupo.config(state='normal')
                self.button_menu_sair.config(state='normal')
                return
            self.escrever_no_input(f"- Iniciado processo no Redis {redis_selecionado}")
            self.escrever_arquivo_log(
                self.nomes['arquivo_redis'], f"INFO - Iniciado processo no Redis {redis_selecionado} ")
            redis_grupo_escolhido = self.infos_config["redis_qa"][grupo_selecionado]
            for redis_grupo in redis_grupo_escolhido:
                nome_redis_atual = redis_grupo["nome_redis"]
                if nome_redis_atual == redis_selecionado:
                    redis_host = redis_grupo["ip"]
                    redis_port = redis_grupo["port"]
                    break
                else:
                    continue

            # Criando uma instância do cliente Redis
            redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

            try:
                # Executando o comando FLUSHALL
                redis_client.flushall()
            except Exception as err:
                self.escrever_no_input(f"- Processo finalizado com falha: {err}")
                self.escrever_arquivo_log(self.nomes['arquivo_redis'], f"INFO - Processo finalizado com falha: {err}")
            else:
                self.escrever_no_input(f"- FLUSHALL executado com sucesso no redis")
                self.escrever_arquivo_log(self.nomes['arquivo_redis'], f"INFO - FLUSHALL executado com sucesso no redis")
            self.escrever_no_input("- Processo finalizado")
            self.escrever_arquivo_log(self.nomes['arquivo_redis'], f"INFO - Processo finalizado ")
            self.button_redis_inicio.config(state='normal')
            self.button_redis_limpar.config(state='normal')
            self.button_redis_voltar.config(state='normal')
            self.combobox_redis.config(state='normal')
            self.combobox_redis_grupo.config(state='normal')
            self.button_menu_sair.config(state='normal')

        except Exception as error:
            self.escrever_no_input(f"Exceção não tratada: {error}")
            self.button_redis_inicio.config(state='normal')
            self.button_redis_limpar.config(state='normal')
            self.button_redis_voltar.config(state='normal')
            self.combobox_redis.config(state='normal')
            self.combobox_redis_grupo.config(state='normal')
            self.button_menu_sair.config(state='normal')

    def validador_nif(self, documento_inserido):
        try:
            self.combobox.config(state='disabled')
            self.entry.config(state='disabled')
            self.button_gerador_inicio.config(state='disabled')
            self.button_gerador_voltar.config(state='disabled')
            self.button_menu_sair.config(state='disabled')
            self.button_gerador_limpar.config(state='disabled')
            self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Rotina - Gerador NIF")
            lista_sem_mascara = self.limpar_string(documento_inserido)
            for doc in lista_sem_mascara:
                if doc.isdigit():
                    tam_documento = len(doc)
                    sem_digitos_validadores = doc[0:tam_documento - 1]
                    digitos_validadores = doc[tam_documento - 1:tam_documento]

                    basenif = []
                    pos_alga = 0
                    algarismonif = [9, 8, 7, 6, 5, 4, 3, 2]
                    tam_alga1 = len(algarismonif)
                    fase2 = []
                    fase4 = []

                    for num_alg in str(sem_digitos_validadores):
                        basenif.append(num_alg)

                    # Fase 2 - multiplicação primeiro digito
                    for pos in basenif:
                        if pos_alga == tam_alga1:
                            pos_alga = 0
                        fase2.append(int(pos) * int(algarismonif[pos_alga]))
                        pos_alga += 1

                    # Fase 3 - Soma primeiro digito
                    fase3 = sum(fase2)

                    etapa1_nif = math.floor(fase3 / 11)
                    etapa2_nif = fase3 - etapa1_nif * 11
                    if etapa2_nif == 1 or etapa2_nif == 0:
                        dig1_nif = 0
                    else:
                        dig1_nif = 11 - etapa2_nif

                    if dig1_nif == int(digitos_validadores):
                        status_checagem = "Verdadeiro"
                    else:
                        status_checagem = "Falso"
                    self.escrever_no_input(f"- NIF - {doc} - {status_checagem}")
                else:
                    self.escrever_no_input(f"- Documento invalido")

            self.combobox.config(state='normal')
            self.entry.config(state='normal')
            self.button_gerador_inicio.config(state='normal')
            self.button_gerador_voltar.config(state='normal')
            self.button_menu_sair.config(state='normal')
            self.button_gerador_limpar.config(state='normal')
        except Exception as error:
            self.escrever_no_input(f"Exceção não tratada: {error}")
            self.combobox.config(state='normal')
            self.entry.config(state='normal')
            self.button_gerador_inicio.config(state='normal')
            self.button_gerador_voltar.config(state='normal')
            self.button_menu_sair.config(state='normal')
            self.button_gerador_limpar.config(state='normal')

    def validador_cnpj(self, documento_inserido):
        try:
            self.combobox.config(state='disabled')
            self.entry.config(state='disabled')
            self.button_gerador_inicio.config(state='disabled')
            self.button_gerador_voltar.config(state='disabled')
            self.button_menu_sair.config(state='disabled')
            self.button_gerador_limpar.config(state='disabled')
            self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Rotina - Gerador CNPJ")
            lista_sem_mascara = self.limpar_string(documento_inserido)
            for doc in lista_sem_mascara:
                if doc.isdigit():
                    tam_documento = len(doc)
                    sem_digitos_validadores = doc[0:tam_documento - 2]
                    digitos_validadores = doc[tam_documento - 2:tam_documento]

                    basecnpj = []
                    pos_alga = 0
                    algarismocnpj1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
                    algarismocnpj2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3]
                    tam_alga1 = len(algarismocnpj1)
                    tam_alga2 = len(algarismocnpj2)
                    fase2 = []
                    fase4 = []

                    for num_alg in str(sem_digitos_validadores):
                        basecnpj.append(num_alg)

                    # Fase 2 - multiplicação primeiro digito
                    for pos in basecnpj:
                        if pos_alga == tam_alga1:
                            pos_alga = 0
                        fase2.append(int(pos) * int(algarismocnpj1[pos_alga]))
                        pos_alga += 1

                    # Fase 3 - Soma primeiro digito
                    fase3 = sum(fase2)

                    etapa1_cnpj = math.floor(fase3 / 11)
                    etapa2_cnpj = math.floor(etapa1_cnpj * 11)
                    etapa3_cnpj = math.floor(fase3 - etapa2_cnpj)
                    dig1_cnpj = 0 if 11 - etapa3_cnpj > 9 else 11 - etapa3_cnpj

                    # Fase 4 - multiplicação segundo digito
                    for pos in basecnpj:
                        if pos_alga == tam_alga2:
                            pos_alga = 0
                        fase4.append(int(pos) * int(algarismocnpj2[pos_alga]))
                        pos_alga += 1

                    fase4.append(dig1_cnpj * 2)

                    # Fase 5 - Soma primeiro digito
                    fase5 = sum(fase4)

                    etapa4_cnpj = math.floor(fase5 / 11)
                    etapa5_cnpj = math.floor(etapa4_cnpj * 11)
                    etapa6_cnpj = math.floor(fase5 - etapa5_cnpj)
                    dig2_cnpj = 0 if 11 - etapa6_cnpj > 9 else 11 - etapa6_cnpj

                    digitos_gerados = str(dig1_cnpj) + str(dig2_cnpj)

                    if int(digitos_gerados) == int(digitos_validadores):
                        status_checagem = "Verdadeiro"
                    else:
                        status_checagem = "Falso"
                    self.escrever_no_input(f"- CNPJ - {doc} - {status_checagem}")
                else:
                    self.escrever_no_input(f"- Documento invalido")
            self.combobox.config(state='normal')
            self.entry.config(state='normal')
            self.button_gerador_inicio.config(state='normal')
            self.button_gerador_voltar.config(state='normal')
            self.button_menu_sair.config(state='normal')
            self.button_gerador_limpar.config(state='normal')
        except Exception as error:
            self.escrever_no_input(f"Exceção não tratada: {error}")
            self.combobox.config(state='normal')
            self.entry.config(state='normal')
            self.button_gerador_inicio.config(state='normal')
            self.button_gerador_voltar.config(state='normal')
            self.button_menu_sair.config(state='normal')
            self.button_gerador_limpar.config(state='normal')

    def validador_cpf(self, documento_inserido):
        try:
            self.combobox.config(state='disabled')
            self.entry.config(state='disabled')
            self.button_gerador_inicio.config(state='disabled')
            self.button_gerador_voltar.config(state='disabled')
            self.button_menu_sair.config(state='disabled')
            self.button_gerador_limpar.config(state='disabled')
            self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Rotina - Gerador CPF")
            lista_sem_mascara = self.limpar_string(documento_inserido)
            for doc in lista_sem_mascara:
                if doc.isdigit():
                    tam_documento = len(doc)
                    sem_digitos_validadores = doc[0:tam_documento - 2]
                    digitos_validadores = doc[tam_documento - 2:tam_documento]
                    divisor = 11

                    basecpf = []
                    pos_alga = 0
                    algarismocpf1 = [10, 9, 8, 7, 6, 5, 4, 3, 2]
                    algarismocpf2 = [11, 10, 9, 8, 7, 6, 5, 4, 3]
                    tam_alga1 = len(algarismocpf1)
                    tam_alga2 = len(algarismocpf2)
                    fase2 = []
                    fase4 = []

                    for num_alg in str(sem_digitos_validadores):
                        basecpf.append(num_alg)

                    # Fase 2 - multiplicação primeiro digito
                    for pos in basecpf:
                        if pos_alga == tam_alga1:
                            pos_alga = 0
                        fase2.append(int(pos) * int(algarismocpf1[pos_alga]))
                        pos_alga += 1

                    # Fase 3 - Soma primeiro digito
                    fase3 = sum(fase2)

                    etapa1_cpf = math.floor(fase3 / 11)
                    etapa2_cpf = math.floor(etapa1_cpf * 11)
                    etapa3_cpf = math.floor(fase3 - etapa2_cpf)
                    dig1_cpf = 0 if 11 - etapa3_cpf > 9 else 11 - etapa3_cpf

                    pos_alga = 0
                    # Fase 4 - multiplicação segundo digito
                    for pos in basecpf:
                        if pos_alga == tam_alga2:
                            pos_alga = 0
                        fase4.append(int(pos) * int(algarismocpf2[pos_alga]))
                        pos_alga += 1

                    fase4.append(dig1_cpf * 2)
                    # Fase 5 - Soma segundo digito
                    fase5 = sum(fase4)

                    etapa4_cpf = math.floor(fase5 / 11)
                    etapa5_cpf = math.floor(etapa4_cpf * 11)
                    etapa6_cpf = math.floor(fase5 - etapa5_cpf)
                    dig2_cpf = 0 if 11 - etapa6_cpf > 9 else 11 - etapa6_cpf

                    digitos_gerados = str(dig1_cpf) + str(dig2_cpf)

                    if digitos_gerados == digitos_validadores:
                        status_checagem = "Verdadeiro"
                    else:
                        status_checagem = "Falso"
                    self.escrever_no_input(f"- CPF - {doc} - {status_checagem}")
                else:
                    self.escrever_no_input(f"- Documento invalido")

            self.combobox.config(state='normal')
            self.entry.config(state='normal')
            self.button_gerador_inicio.config(state='normal')
            self.button_gerador_voltar.config(state='normal')
            self.button_menu_sair.config(state='normal')
            self.button_gerador_limpar.config(state='normal')
        except Exception as error:
            self.escrever_no_input(f"Exceção não tratada: {error}")
            self.combobox.config(state='normal')
            self.entry.config(state='normal')
            self.button_gerador_inicio.config(state='normal')
            self.button_gerador_voltar.config(state='normal')
            self.button_menu_sair.config(state='normal')
            self.button_gerador_limpar.config(state='normal')

    def validador_cei(self, documento_inserido):
        try:
            self.combobox.config(state='disabled')
            self.entry.config(state='disabled')
            self.button_gerador_inicio.config(state='disabled')
            self.button_gerador_voltar.config(state='disabled')
            self.button_menu_sair.config(state='disabled')
            self.button_gerador_limpar.config(state='disabled')
            self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Rotina - Gerador CEI")
            lista_sem_mascara = self.limpar_string(documento_inserido)
            for doc in lista_sem_mascara:
                if doc.isdigit():
                    tam_documento = len(doc)
                    sem_digitos_validadores = doc[0:tam_documento - 1]
                    digitos_validadores = doc[tam_documento - 1:tam_documento]
                    basecei = []
                    pos_alga = 0
                    algarismopis = [7, 4, 1, 8, 5, 2, 1, 6, 3, 7, 4]
                    tam_alga = len(algarismopis)
                    fase2 = []


                    for num_alg in str(sem_digitos_validadores):
                        basecei.append(num_alg)
                    # Fase 2 - multiplicação
                    for pos in basecei:
                        if pos_alga == tam_alga:
                            pos_alga = 0
                        fase2.append(int(pos) * int(algarismopis[pos_alga]))
                        pos_alga += 1

                    soma = sum(fase2)
                    string_soma = str(soma)
                    soma_digitos = int(string_soma[len(string_soma) - 1]) + int(string_soma[len(string_soma) - 2])
                    etapa1 = math.floor(soma_digitos / 10)
                    if etapa1 == 1:
                        etapa1 = 0
                    etapa2 = (soma_digitos % 10)
                    etapa3 = etapa2 + etapa1
                    etapa4 = (etapa3 % 10)
                    etapa5 = math.floor(10 - (etapa4 % 10))
                    if etapa5 == 10:
                        etapa6 = 0
                    else:
                        etapa6 = etapa5
                    if etapa6 == int(digitos_validadores):
                        status_checagem = "Verdadeiro"
                    else:
                        status_checagem = "Falso"
                    self.escrever_no_input(f"- CEI - {doc} - {status_checagem}")
                else:
                    self.escrever_no_input(f"- Documento invalido")


            self.combobox.config(state='normal')
            self.entry.config(state='normal')
            self.button_gerador_inicio.config(state='normal')
            self.button_gerador_voltar.config(state='normal')
            self.button_menu_sair.config(state='normal')
            self.button_gerador_limpar.config(state='normal')
        except Exception as error:
            self.escrever_no_input(f"Exceção não tratada: {error}")
            self.combobox.config(state='normal')
            self.entry.config(state='normal')
            self.button_gerador_inicio.config(state='normal')
            self.button_gerador_voltar.config(state='normal')
            self.button_menu_sair.config(state='normal')
            self.button_gerador_limpar.config(state='normal')

    def validador_pis(self, documento_inserido):
        try:
            self.combobox.config(state='disabled')
            self.entry.config(state='disabled')
            self.button_gerador_inicio.config(state='disabled')
            self.button_gerador_voltar.config(state='disabled')
            self.button_menu_sair.config(state='disabled')
            self.button_gerador_limpar.config(state='disabled')
            self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Rotina - Gerador PIS")
            lista_sem_mascara = self.limpar_string(documento_inserido)
            for doc in lista_sem_mascara:
                if doc.isdigit():
                    tam_documento = len(doc)
                    sem_digitos_validadores = doc[0:tam_documento - 1]
                    digitos_validadores = doc[tam_documento - 1:tam_documento]
                    divisor = 11

                    basepis = []
                    pos_alga = 0
                    algarismopis = [3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
                    tam_alga = len(algarismopis)
                    fase2 = []

                    for num_alg in str(sem_digitos_validadores):
                        basepis.append(num_alg)
                    # Fase 2 - multiplicação
                    for pos in basepis:
                        if pos_alga == tam_alga:
                            pos_alga = 0
                        fase2.append(int(pos) * int(algarismopis[pos_alga]))
                        pos_alga += 1

                    # Fase 3 - Soma
                    fase3 = sum(fase2)
                    # Fase 6 - Resto da Divisão
                    fase6 = fase3 % divisor
                    # Fase 7 - Validador
                    if divisor - fase6 == 10:
                        fase7 = 0
                    elif divisor - fase6 == 11:
                        fase7 = 0
                    else:
                        fase7 = divisor - fase6

                    if fase7 == int(digitos_validadores):
                        status_checagem = "Verdadeiro"
                    else:
                        status_checagem = "Falso"
                    self.escrever_no_input(f"- Pis - {doc} - {status_checagem}")
                else:
                    self.escrever_no_input(f"- Documento invalido")


            self.combobox.config(state='normal')
            self.entry.config(state='normal')
            self.button_gerador_inicio.config(state='normal')
            self.button_gerador_voltar.config(state='normal')
            self.button_menu_sair.config(state='normal')
            self.button_gerador_limpar.config(state='normal')

        except Exception as error:
            self.escrever_no_input(f"Exceção não tratada: {error}")
            self.combobox.config(state='normal')
            self.entry.config(state='normal')
            self.button_gerador_inicio.config(state='normal')
            self.button_gerador_voltar.config(state='normal')
            self.button_menu_sair.config(state='normal')
            self.button_gerador_limpar.config(state='normal')

    def gerador_nif(self, linhas, checkbox_arquivo):
        try:
            self.combobox.config(state='disabled')
            self.entry.config(state='disabled')
            self.button_gerador_inicio.config(state='disabled')
            self.button_gerador_voltar.config(state='disabled')
            self.button_menu_sair.config(state='disabled')
            self.button_gerador_limpar.config(state='disabled')
            self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Rotina - Gerador NIF")
            contador = int(linhas)

            while contador:
                lista = []
                n1 = 2
                n2 = random.randrange(0, 9, 1)
                n3 = random.randrange(0, 9, 1)
                n4 = random.randrange(0, 9, 1)
                n5 = random.randrange(0, 9, 1)
                n6 = random.randrange(0, 9, 1)
                n7 = random.randrange(0, 9, 1)
                n8 = random.randrange(0, 9, 1)

                soma1 = (n1 * 9) + (n2 * 8) + (n3 * 7) + (n4 * 6) + (n5 * 5) + (n6 * 4) + (n7 * 3) + (n8 * 2)
                etapa1_nif = math.floor(soma1/11)
                etapa2_nif = soma1 - etapa1_nif * 11
                if etapa2_nif == 1 or etapa2_nif == 0:
                    dig1_nif = 0
                else:
                    dig1_nif = 11 - etapa2_nif

                nif_gerado = str(n1) + str(n2) + str(n3) + str(n4) + str(n5) + str(n6) + str(n7) + str(n8) + str(dig1_nif)
                lista.append(nif_gerado)
                contador -= 1
                self.escrever_no_input(lista[0])
                if checkbox_arquivo:
                    self.escrever_arquivo_txt(self.nomes['arquivo_doc_nif'], lista[0])
            self.combobox.config(state='normal')
            self.entry.config(state='normal')
            self.button_gerador_inicio.config(state='normal')
            self.button_gerador_voltar.config(state='normal')
            self.button_menu_sair.config(state='normal')
            self.button_gerador_limpar.config(state='normal')
            self.escrever_no_input(f"- Processo finalizado com sucesso")

        except Exception as error:
            self.escrever_no_input(f"Exceção não tratada: {error}")
            self.combobox.config(state='normal')
            self.entry.config(state='normal')
            self.button_gerador_inicio.config(state='normal')
            self.button_gerador_voltar.config(state='normal')
            self.button_menu_sair.config(state='normal')
            self.button_gerador_limpar.config(state='normal')

    def gerador_cnpj(self, linhas, checkbox_mascara, checkbox_arquivo):
        try:
            self.combobox.config(state='disabled')
            self.entry.config(state='disabled')
            self.button_gerador_inicio.config(state='disabled')
            self.button_gerador_voltar.config(state='disabled')
            self.button_menu_sair.config(state='disabled')
            self.button_gerador_limpar.config(state='disabled')
            self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Rotina - Gerador CNPJ")
            contador = int(linhas)

            while contador:
                lista = []
                n1 = random.randrange(0, 9, 1)
                n2 = random.randrange(0, 9, 1)
                n3 = random.randrange(0, 9, 1)
                n4 = random.randrange(0, 9, 1)
                n5 = random.randrange(0, 9, 1)
                n6 = random.randrange(0, 9, 1)
                n7 = random.randrange(0, 9, 1)
                n8 = random.randrange(0, 9, 1)
                n9 = 0
                n10 = 0
                n11 = 0
                n12 = random.randrange(0, 9, 1)

                soma1 = (n1 * 5) + (n2 * 4) + (n3 * 3) + (n4 * 2) + (n5 * 9) + (n6 * 8) + (n7 * 7) + (n8 * 6) + (n9 * 5) + (n10 * 4) + (n11 * 3) + (n12 * 2)
                etapa1_cnpj = math.floor(soma1/11)
                etapa2_cnpj = math.floor(etapa1_cnpj * 11)
                etapa3_cnpj = math.floor(soma1 - etapa2_cnpj)
                dig1_cnpj = 0 if 11 - etapa3_cnpj > 9 else 11 - etapa3_cnpj

                soma2 = (n1 * 6) + (n2 * 5) + (n3 * 4) + (n4 * 3) + (n5 * 2) + (n6 * 9) + (n7 * 8) + (n8 * 7) + (n9 * 6) + (n10 * 5) + (n11 * 4) + (n12 * 3) + (dig1_cnpj * 2)
                etapa4_cnpj = math.floor(soma2/11)
                etapa5_cnpj = math.floor(etapa4_cnpj*11)
                etapa6_cnpj = math.floor(soma2 - etapa5_cnpj)
                dig2_cnpj = 0 if 11 - etapa6_cnpj > 9 else 11 - etapa6_cnpj

                #  XX.XXX.XXX/XXXX-XX;
                # Fase 8 - montando o cnpj
                cnpj_gerado = str(n1) + str(n2) + str(n3) + str(n4) + str(n5) + str(n6) + str(n7) + str(n8) + str(n9) + str(n10) + str(n11) + str(n12) + str(dig1_cnpj) + str(dig2_cnpj)
                if checkbox_mascara:
                    cnpj_gerado = cnpj_gerado[0:2] + "." + cnpj_gerado[2:5] + "." + cnpj_gerado[5:8] + "/" + cnpj_gerado[8:12] + "-" + cnpj_gerado[12:14]
                lista.append(cnpj_gerado)

                contador -= 1
                self.escrever_no_input(lista[0])

                if checkbox_arquivo:
                    self.escrever_arquivo_txt(self.nomes['arquivo_doc_cnpj'], lista[0])
            self.combobox.config(state='normal')
            self.entry.config(state='normal')
            self.button_gerador_inicio.config(state='normal')
            self.button_gerador_voltar.config(state='normal')
            self.button_menu_sair.config(state='normal')
            self.button_gerador_limpar.config(state='normal')
            self.escrever_no_input(f"- Processo finalizado com sucesso")

        except Exception as error:
            self.escrever_no_input(f"Exceção não tratada: {error}")
            self.combobox.config(state='normal')
            self.entry.config(state='normal')
            self.button_gerador_inicio.config(state='normal')
            self.button_gerador_voltar.config(state='normal')
            self.button_menu_sair.config(state='normal')
            self.button_gerador_limpar.config(state='normal')

    def gerador_cpf(self, linhas, checkbox_mascara, checkbox_arquivo):
        try:
            self.combobox.config(state='disabled')
            self.entry.config(state='disabled')
            self.button_gerador_inicio.config(state='disabled')
            self.button_gerador_voltar.config(state='disabled')
            self.button_menu_sair.config(state='disabled')
            self.button_gerador_limpar.config(state='disabled')
            self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Rotina - Gerador CPF")
            contador = int(linhas)

            while contador:
                lista = []
                n1 = random.randrange(0, 9, 1)
                n2 = random.randrange(0, 9, 1)
                n3 = random.randrange(0, 9, 1)
                n4 = random.randrange(0, 9, 1)
                n5 = random.randrange(0, 9, 1)
                n6 = random.randrange(0, 9, 1)
                n7 = random.randrange(0, 9, 1)
                n8 = random.randrange(0, 9, 1)
                n9 = random.randrange(0, 9, 1)

                soma1 = (n1 * 10) + (n2 * 9) + (n3 * 8) + (n4 * 7) + (n5 * 6) + (n6 * 5) + (n7 * 4) + (n8 * 3) + (n9 * 2)
                etapa1_cpf = math.floor(soma1/11)
                etapa2_cpf = math.floor(etapa1_cpf*11)
                etapa3_cpf = math.floor(soma1 - etapa2_cpf)
                dig1_cpf = 0 if 11 - etapa3_cpf > 9 else 11 - etapa3_cpf

                soma2 = (n1 * 11) + (n2 * 10) + (n3 * 9) + (n4 * 8) + (n5 * 7) + (n6 * 6) + (n7 * 5) + (n8 * 4) + (n9 * 3) + (dig1_cpf * 2)
                etapa4_cpf = math.floor(soma2/11)
                etapa5_cpf = math.floor(etapa4_cpf*11)
                etapa6_cpf = math.floor(soma2 - etapa5_cpf)
                dig2_cpf = 0 if 11 - etapa6_cpf > 9 else 11 - etapa6_cpf

                # XXX.XXX.XXX-XX
                # Fase 8 - montando o cpf
                cpf_gerado = str(n1) + str(n2) + str(n3) + str(n4) + str(n5) + str(n6) + str(n7) + str(n8) + str(n9) + str(dig1_cpf) + str(dig2_cpf)
                if checkbox_mascara:
                    cpf_gerado = cpf_gerado[0:3] + "." + cpf_gerado[3:6] + "." + cpf_gerado[6:9] + "-" + cpf_gerado[9:11]
                lista.append(cpf_gerado)
                contador -= 1
                self.escrever_no_input(lista[0])

                if checkbox_arquivo:
                    self.escrever_arquivo_txt(self.nomes['arquivo_doc_cpf'], lista[0])
            self.combobox.config(state='normal')
            self.entry.config(state='normal')
            self.button_gerador_inicio.config(state='normal')
            self.button_gerador_voltar.config(state='normal')
            self.button_menu_sair.config(state='normal')
            self.button_gerador_limpar.config(state='normal')
            self.escrever_no_input(f"- Processo finalizado com sucesso")

        except Exception as error:
            self.escrever_no_input(f"Exceção não tratada: {error}")
            self.combobox.config(state='normal')
            self.entry.config(state='normal')
            self.button_gerador_inicio.config(state='normal')
            self.button_gerador_voltar.config(state='normal')
            self.button_menu_sair.config(state='normal')
            self.button_gerador_limpar.config(state='normal')

    def gerador_cei(self, linhas, checkbox_mascara, checkbox_arquivo):
        try:
            self.combobox.config(state='disabled')
            self.entry.config(state='disabled')
            self.button_gerador_inicio.config(state='disabled')
            self.button_gerador_voltar.config(state='disabled')
            self.button_menu_sair.config(state='disabled')
            self.button_gerador_limpar.config(state='disabled')
            self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Rotina - Gerador CEI")
            contador = int(linhas)

            while contador:
                lista = []
                n1 = random.randrange(0, 9, 1)
                n2 = random.randrange(0, 9, 1)
                n3 = random.randrange(0, 9, 1)
                n4 = random.randrange(0, 9, 1)
                n5 = random.randrange(0, 9, 1)
                n6 = random.randrange(0, 9, 1)
                n7 = random.randrange(0, 9, 1)
                n8 = random.randrange(0, 9, 1)
                n9 = random.randrange(0, 9, 1)
                n10 = random.randrange(0, 9, 1)
                n11 = 8

                soma = (n1 * 7) + (n2 * 4) + (n3 * 1) + (n4 * 8) + (n5 * 5) + (n6 * 2) + (n7 * 1) + (n8 * 6) + (n9 * 3) + (n10 * 7) + (n11 * 4)
                string_soma = str(soma)
                soma_digitos = int(string_soma[len(string_soma) - 1]) + int(string_soma[len(string_soma) - 2])
                etapa1 = math.floor(soma_digitos / 10)
                if etapa1 == 1:
                    etapa1 = 0
                etapa2 = (soma_digitos % 10)
                etapa3 = etapa2 + etapa1
                etapa4 = (etapa3 % 10)
                etapa5 = math.floor(10 - (etapa4 % 10))
                if etapa5 == 10:
                    etapa6 = 0
                else:
                    etapa6 = etapa5

                # XX.XXX.XXXXX/XX
                # Fase 8 - montando o cei
                cei_gerado = str(n1) + str(n2) + str(n3) + str(n4) + str(n5) + str(n6) + str(n7) + str(n8) + str(n9) + str(n10) + str(n11) + str(etapa6)
                if checkbox_mascara:
                    cei_gerado = cei_gerado[0:2] + "." + cei_gerado[2:5] + "." + cei_gerado[5:10] + "/" + cei_gerado[10:12]
                lista.append(cei_gerado)
                contador -= 1
                self.escrever_no_input(lista[0])

                if checkbox_arquivo:
                    self.escrever_arquivo_txt(self.nomes['arquivo_doc_cei'], lista[0])
            self.combobox.config(state='normal')
            self.entry.config(state='normal')
            self.button_gerador_inicio.config(state='normal')
            self.button_gerador_voltar.config(state='normal')
            self.button_menu_sair.config(state='normal')
            self.button_gerador_limpar.config(state='normal')
            self.escrever_no_input(f"- Processo finalizado com sucesso")

        except Exception as error:
            self.escrever_no_input(f"Exceção não tratada: {error}")
            self.combobox.config(state='normal')
            self.entry.config(state='normal')
            self.button_gerador_inicio.config(state='normal')
            self.button_gerador_voltar.config(state='normal')
            self.button_menu_sair.config(state='normal')
            self.button_gerador_limpar.config(state='normal')

    def gerador_pis(self, linhas, checkbox_mascara, checkbox_arquivo):
        try:
            self.combobox.config(state='disabled')
            self.entry.config(state='disabled')
            self.button_gerador_inicio.config(state='disabled')
            self.button_gerador_voltar.config(state='disabled')
            self.button_menu_sair.config(state='disabled')
            self.button_gerador_limpar.config(state='disabled')
            self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Rotina - Gerador PIS")
            divisor = 11
            contador = int(linhas)

            while contador:
                basepis = []
                lista = []
                pos_alga = 0
                algarismopis = [3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
                pis_gerado = ''
                fase2 = []

                numaleatorio = random.randrange(1000000000, 1999999999, 12345)
                for num_alg in str(numaleatorio):
                    basepis.append(num_alg)
                # Fase 2 - multiplicação
                for pos in basepis:
                    fase2.append(int(pos) * int(algarismopis[pos_alga]))
                    pos_alga += 1

                # Fase 3 - Soma
                fase3 = sum(fase2)
                # Fase 6 - Resto da Divisão
                fase6 = fase3 % divisor
                # Fase 7 - Validador
                if divisor - fase6 == 10:
                    fase7 = 0
                elif divisor - fase6 == 11:
                    fase7 = 0
                else:
                    fase7 = divisor - fase6

                # XXX.XXXXX.XX-X
                # Fase 8 - montando o pis
                for pos in basepis:
                    pis_gerado = str(pis_gerado) + str(pos)
                pis_gerado = str(pis_gerado) + str(fase7)
                if checkbox_mascara:
                    pis_gerado = pis_gerado[0:3] + "." + pis_gerado[3:8] + "." + pis_gerado[8:10] + "-" + pis_gerado[10:11]
                # Guardando os Pis gerados em um Array
                lista.append(pis_gerado)
                contador -= 1
                self.escrever_no_input(lista[0])

                if checkbox_arquivo:
                    self.escrever_arquivo_txt(self.nomes['arquivo_doc_pis'], lista[0])
            self.combobox.config(state='normal')
            self.entry.config(state='normal')
            self.button_gerador_inicio.config(state='normal')
            self.button_gerador_voltar.config(state='normal')
            self.button_menu_sair.config(state='normal')
            self.button_gerador_limpar.config(state='normal')
            self.escrever_no_input(f"- Processo finalizado com sucesso")

        except Exception as error:
            self.escrever_no_input(f"Exceção não tratada: {error}")
            self.combobox.config(state='normal')
            self.entry.config(state='normal')
            self.button_gerador_inicio.config(state='normal')
            self.button_gerador_voltar.config(state='normal')
            self.button_menu_sair.config(state='normal')
            self.button_gerador_limpar.config(state='normal')

# Menus que realizam as validar antes de inicar os processos
    def menu_gerador_documentos(self):
        selecao_combobox = self.combobox.get()
        if self.entry.get() != self.placeholder_text and self.entry.get() != '':
            quant_insirada = self.entry.get()
        else:
            quant_insirada = 1
        checkbox_mascara = self.valor_checkbox_mascara_num.get()
        checkbox_arquivo = self.valor_checkbox_gerar_arquivo.get()
        if str(quant_insirada).isdigit():
            match selecao_combobox:
                case "CEI":
                    self.iniciar_processo_gerar_cei(quant_insirada, checkbox_mascara, checkbox_arquivo)
                case "CNPJ":
                    self.iniciar_processo_gerar_cnpj(quant_insirada, checkbox_mascara, checkbox_arquivo)
                case "CPF":
                    self.iniciar_processo_gerar_cpf(quant_insirada, checkbox_mascara, checkbox_arquivo)
                case "NIF":
                    self.iniciar_processo_gerar_nif(quant_insirada, checkbox_arquivo)
                case "PIS":
                    self.iniciar_processo_gerar_pis(quant_insirada, checkbox_mascara, checkbox_arquivo)
                case _:
                    self.escrever_no_input(f"- Função não implementada")
        else:
            self.escrever_no_input(f"- Insira a quantidade de registros para serem gerados")
            return

    def menu_validador_documentos(self):
        selecao_combobox = self.combobox.get()
        documento_inserido = self.entry.get()
        if documento_inserido != self.placeholder_text and documento_inserido != "":
            match selecao_combobox:
                case "CEI":
                    self.iniciar_processo_validar_cei(documento_inserido)
                case "CNPJ":
                    self.iniciar_processo_validar_cnpj(documento_inserido)
                case "CPF":
                    self.iniciar_processo_validar_cpf(documento_inserido)
                case "NIF":
                    self.iniciar_processo_validar_nif(documento_inserido)
                case "PIS":
                    self.iniciar_processo_validar_pis(documento_inserido)
                case _:
                    self.escrever_no_input(f"- Função não implementada")
        else:
            self.escrever_no_input(f"- Insira o documento que será validado")
            return

    def menu_restaurar_banco(self):
        self.iniciar_processo_restaurar()

    def menu_redis_todos(self):
        self.infos_config['status'] = True
        while True:
            if self.infos_config['status']:
                try:
                    servidores_redis = list(self.infos_config['redis_qa'])
                    if servidores_redis != "":
                        self.iniciar_processo_limpar_redis_todos()
                        break
                    else:
                        self.escrever_no_input(f"- A tag de redis_qa parece estar vazia")
                        self.escrever_arquivo_log(self.nomes['arquivo_redis'], f"INFO - A tag de redis_qa parece estar vazia, preencha e recarregue o config novamente ")
                        self.infos_config['status'] = False
                except (Exception or pyodbc.DatabaseError) as err:
                    self.escrever_no_input(f"- Falha ao tentar ler o arquivo {err}")
                    self.escrever_arquivo_log(self.nomes['arquivo_redis'], f"ERRO - Falha ao tentar ler o arquivo, corrija e tente novamente: {err} ")
                    self.infos_config['status'] = False
            else:
                self.escrever_no_input(f"- Processo finalizado")
                break

    def menu_redis_especifico(self):
        self.infos_config['status'] = True
        while True:
            if self.infos_config['status']:
                try:
                    self.iniciar_processo_limpar_redis_especifico()
                    break
                except (Exception or pyodbc.DatabaseError) as err:
                    self.escrever_no_input(f"- Falha ao tentar ler o arquivo {err}")
                    self.escrever_arquivo_log(self.nomes['arquivo_redis'], f"ERRO - Falha ao tentar ler o arquivo, corrija e tente novamente: {err} ")
                    self.infos_config['status'] = False
            else:
                self.escrever_no_input(f"- Processo finalizado")
                break

    def menu_download_backup(self):
        self.infos_config['status'] = True
        while True:
            if self.infos_config['status']:
                try:
                    self.iniciar_processo_download()
                    break
                except (Exception or pyodbc.DatabaseError) as err:
                    self.escrever_no_input(f"- Falha ao tentar ler o arquivo {err}")
                    self.escrever_arquivo_log(self.nomes['arquivo_download_backup'], f"ERRO - Falha ao tentar ler o arquivo, corrija e tente novamente: {err} ")
                    self.infos_config['status'] = False
            else:
                self.escrever_no_input(f"- Processo finalizado")
                break

# iniciadores de processos
    def iniciar_processo_validar_nif(self, documento_inserido):
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.validador_nif, args=[documento_inserido])
        self.thread.start()

    def iniciar_processo_validar_cnpj(self, documento_inserido):
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.validador_cnpj, args=[documento_inserido])
        self.thread.start()

    def iniciar_processo_validar_cpf(self, documento_inserido):
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.validador_cpf, args=[documento_inserido])
        self.thread.start()

    def iniciar_processo_validar_cei(self, documento_inserido):
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.validador_cei, args=[documento_inserido])
        self.thread.start()

    def iniciar_processo_validar_pis(self, documento_inserido):
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.validador_pis, args=[documento_inserido])
        self.thread.start()

    def iniciar_processo_gerar_nif(self, linhas, checkbox_arquivo):
        self.escrever_no_input(f"- Processo iniciado - Gerador de NIF")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.gerador_nif, args=[linhas, checkbox_arquivo])
        self.thread.start()

    def iniciar_processo_gerar_cnpj(self, linhas, checkbox_mascara, checkbox_arquivo):
        self.escrever_no_input(f"- Processo iniciado - Gerador de CNPJ")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.gerador_cnpj, args=[linhas, checkbox_mascara, checkbox_arquivo])
        self.thread.start()

    def iniciar_processo_gerar_cpf(self, linhas, checkbox_mascara, checkbox_arquivo):
        self.escrever_no_input(f"- Processo iniciado - Gerador de CPF")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.gerador_cpf, args=[linhas, checkbox_mascara, checkbox_arquivo])
        self.thread.start()

    def iniciar_processo_gerar_cei(self, linhas, checkbox_mascara, checkbox_arquivo):
        self.escrever_no_input(f"- Processo iniciado - Gerador de CEI")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.gerador_cei, args=[linhas, checkbox_mascara, checkbox_arquivo])
        self.thread.start()

    def iniciar_processo_gerar_pis(self, linhas, checkbox_mascara, checkbox_arquivo):
        self.escrever_no_input(f"- Processo iniciado - Gerador de PIS")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.gerador_pis, args=[linhas, checkbox_mascara, checkbox_arquivo])
        self.thread.start()

    def iniciar_processo_limpar_redis_especifico(self):
        self.escrever_no_input(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.limpar_redis_especifico)
        self.thread.start()

    def iniciar_processo_limpar_redis_todos(self):
        self.escrever_no_input(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.limpar_todos_redis)
        self.thread.start()

    def iniciar_processo_buscar_empresas(self):
        self.escrever_no_input(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.buscar_empresas)
        self.thread.start()

    def iniciar_processo_consulta(self):
        self.escrever_no_input(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.consultar_versions)
        self.thread.start()

    def iniciar_processo_replicar(self):
        self.escrever_no_input(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.replicar_version)
        self.thread.start()


    def iniciar_processo_download(self):
        self.escrever_no_input(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.download_backup)
        self.thread.start()

    def iniciar_processo_restaurar(self):
        self.escrever_no_input(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.restaurar_banco)
        self.thread.start()

    def iniciar_processo_manipula_banco(self):
        self.escrever_no_input(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.manipular_banco_update)
        self.thread.start()

# Modificadores de telas
    def inserir_menu_cascata(self):
        menu_bar = Menu(self.app)
        self.app.config(menu=menu_bar)
        file_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Configuração", menu=file_menu)
        file_menu.add_command(label="Trocar Configuração", command=self.trocar_tela_config)
        file_menu.add_command(label="Ferramentas banco update", command=self.trocar_tela_atualizacao_banco_update)

        help_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Aparência", menu=help_menu)
        help_menu.add_command(label="Alterar Aparência", command=self.trocar_tela_alterar_aparencia)
        help_menu.add_command(label="Redefinir Aparência", command=self.redefinir_background)

    def inserir_botoes_navs(self, app):
        self.button_menu_sair = Button(
            app,
            text="Sair",
            width=15,
            height=2,
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.finalizar()
        )
        self.button_menu_sair.grid(row=15, column=0, columnspan=2, padx=15, pady=15, sticky="WS")

    def inserir_campos_arquivo_existente(self, app, coluna):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Rotina - Escolher Arquivo Existente")
        opcoes = []
        self.remover_conteudo_linha(6,0)
        self.remover_conteudo_linha(7, 0)


        if self.button_nav_criar != None:
            self.button_nav_criar.config(state="disabled")
        # listar os arquivos de dentro da pasta
        try:
            arquivos_diretorio = os.listdir(self.nomes['pasta_config'])
        except Exception as name_error:
            self.criar_popup_mensagem(f"Não foi possivel acessar a pasta config: {name_error}")
            return
        else:
            loop = True
            while loop:
                dir_arquivos_configs = []
                dir_arquivo_index = []
                if arquivos_diretorio:
                    for arquivo_dir in arquivos_diretorio:
                        match_arquivo = re.search("\\.json$", arquivo_dir)
                        if match_arquivo is not None:
                            dir_arquivos_configs.append(arquivo_dir)
                            dir_arquivo_index.append(arquivos_diretorio.index(arquivo_dir))
                    if dir_arquivos_configs:
                        for itens_arquivos in dir_arquivos_configs:
                            opcoes.append(f"{itens_arquivos}")
                        break
                    else:
                        self.criar_popup_mensagem(f"Não existe arquivos .json na pasta config")
                        return
                else:
                    self.criar_popup_mensagem(f"Não existe arquivos na pasta config")
                    return

        self.infos_config_prog['escolha_manual'] = True

        self.label_lista_arquivos = Label(
            text="Lista de arquivos:",
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.combobox = Combobox(
            app,
            values=opcoes,
        )
        self.button_nav_escolher = Button(
            app,
            text="Escolher",
            width=15,
            height=2,
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.escolher_config_existente()
        )
        if len(opcoes) > 0:
            self.combobox.set(opcoes[0])
        self.label_lista_arquivos.grid(row=6, column=coluna, pady=(10, 0), columnspan=2)
        self.combobox.grid(row=7, column=coluna, pady=(0, 10), columnspan=2)
        self.button_nav_escolher.grid(row=15, column=1, padx=15, pady=15, columnspan=2, sticky="ES")

    def inserir_campos_arquivo_novo(self, app, coluna):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Rotina - Criar Arquivo config")
        self.remover_conteudo_linha(6,0)
        self.remover_conteudo_linha(7, 0)
        if self.button_nav_escolher != None:
            self.button_nav_escolher.config(state="disabled")

        self.button_nav_criar = Button(
            app,
            text="Criar",
            name="button_criar",
            width=15,
            height=2,
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.criar_config()
        )
        self.inserir_input_placeholder_modular('gray', 6, 7, coluna, "Insira o nome para o arquivo...", "Nome do arquivo:", "W", "WE", 50, (0,0) ,(15,0) ,(0,0), (15,15))
        self.button_nav_criar.grid(row=15, column=1, padx=15, pady=15, columnspan=2, sticky="ES")

    def inserir_caixa_seletora(self, linha_label, linha_seletor,  coluna, opcoes, nome_campo):
        self.label = Label(
            text=nome_campo,
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.combobox = Combobox(
            self.app,
            values=opcoes
        )
        self.label.grid(row=linha_label, column=coluna, sticky="WS", pady=(10, 0))
        self.combobox.grid(row=linha_seletor, column=coluna, columnspan=2, pady=(0, 10), sticky="WEN")

    def inserir_input_placeholder_modular(self, cor, linha_label, linha_entry, coluna, texto, nome_campo, posicao_label, posicao_entry, tamanho_elemento, pady_label, padx_label, pady_entry, padx_entry):
        self.placeholder_text = texto
        placeholder_color = cor

        self.label = Label(
            text=nome_campo,
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.entry = Entry(
            self.app,
            width=tamanho_elemento,
            fg=placeholder_color
        )
        self.entry.insert(0, self.placeholder_text)
        self.entry.bind("<FocusIn>", self.on_entry_click)
        self.entry.bind("<FocusOut>", self.on_focusout)
        self.label.grid(row=linha_label, column=coluna, sticky=posicao_label, pady=(pady_label), padx=(padx_label))
        self.entry.grid(row=linha_entry, column=coluna, columnspan=2, sticky=posicao_entry, pady=(pady_entry), padx=(padx_entry))
        self.entries.append(self.entry)

    def inserir_input_placeholder(self, linha_label, linha_entry,  coluna, texto, nome_campo, padding_baixo):
        texo_com_espaco = "  " + texto
        self.placeholder_text = texo_com_espaco
        placeholder_color = "gray"
        self.label = Label(
            text=nome_campo,
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.entry = Entry(
            self.app,
            fg=placeholder_color
        )
        self.entry.insert(0, self.placeholder_text)
        self.entry.bind("<FocusIn>", self.on_entry_click)
        self.entry.bind("<FocusOut>", self.on_focusout)
        self.label.grid(row=linha_label, column=coluna, sticky="W", pady=(10, 0), padx=(15))
        self.entry.grid(row=linha_entry, column=coluna, columnspan=2, sticky="WEN", padx=(15), pady=(0, padding_baixo))

    def inserir_titulos_telas(self, app, nome_tela, linha, coluna, padding_baixo):
        self.label_inserir_titulos = Label(
            app,
            text=nome_tela,
            font=('Arial', 12, 'bold'),
            bg=self.infos_config_prog["background_color_titulos"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.label_inserir_titulos.grid(row=linha, column=coluna, sticky="WE", columnspan=2, pady=(0, padding_baixo))

    def remover_conteudo_linha(self, linha, coluna):
        widgets = self.app.grid_slaves(row=linha, column=coluna)
        for widget in widgets:
            widget.destroy()

    def inserir_caixa_texto(self, linha_label, linha_texto, coluna, nome, pady_label, padx_label, tamanho):
        self.nome_campo_caixa = Label(
            text=nome,
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.widtexto = Text(
            self.app,
            height=tamanho,
            wrap="word"
        )
        self.nome_campo_caixa.grid(row=linha_label, column=coluna, sticky="WE", columnspan=2, pady=(pady_label), padx=(padx_label))
        self.widtexto.grid(row=linha_texto, column=coluna, sticky="WE", columnspan=2, padx=(15))
        self.widtexto.config(width=50)
        self.widtexto.config(state="disabled")

    def caixa_selecao_de_cor(self, campo):
        color_code = colorchooser.askcolor(title="Escolha uma cor")
        if color_code[1]:
            campo.delete(0, END)
            campo.insert(0, color_code[1])

    def texto_config_selecionado(self, app):
        tela = f"Ultimo Config: {self.infos_config_prog['config_default']}"
        self.label_config_selecionado = Label(
            app,
            text=tela,
            font=('Arial', 12),
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.label_config_selecionado.grid(row=0, column=0, columnspan=3, sticky="NW", pady=(0,10))

    def Inserir_estrutura_padrao_telas(self):
        self.app.configure(bg=self.infos_config_prog["background_color_fundo"])
        self.app.rowconfigure(0, weight=0)
        self.app.rowconfigure(15, weight=0)
        self.remover_widget(self.app, '*', '*')
        self.inserir_menu_cascata()
        self.texto_config_selecionado(self.app)
        self.inserir_botoes_navs(self.app)
        self.entries = []

# Realiza as limpezas e contruçoes antes da montagem das telas
    def trocar_tela_menu_geral(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Menu")
        peso_linha = 0
        self.app.rowconfigure(1, weight=self.peso_linha_um)
        self.app.rowconfigure(2, weight=0)
        self.app.rowconfigure(3, weight=1)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(5, weight=peso_linha)
        self.app.rowconfigure(6, weight=peso_linha)
        self.app.rowconfigure(7, weight=peso_linha)
        self.app.rowconfigure(14, weight=1)
        self.Inserir_estrutura_padrao_telas()
        self.tela_menu_geral(self.app, self.version, self.coluna)

    def trocar_tela_menu_ferramentas_bancos(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Ferramenta Banco Muro")
        peso_linha = 0
        self.app.rowconfigure(1, weight=self.peso_linha_um)
        self.app.rowconfigure(2, weight=0)
        self.app.rowconfigure(3, weight=1)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(5, weight=peso_linha)
        self.app.rowconfigure(6, weight=peso_linha)
        self.app.rowconfigure(7, weight=peso_linha)
        self.app.rowconfigure(14, weight=1)
        self.Inserir_estrutura_padrao_telas()
        self.tela_menu_ferramentas_bancos(self.app, self.version, self.coluna)

    def trocar_tela_menu_ferramentas_backup(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Ferramentas Backup")
        peso_linha = 0
        self.app.rowconfigure(1, weight=self.peso_linha_um)
        self.app.rowconfigure(2, weight=0)
        self.app.rowconfigure(3, weight=1)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(5, weight=peso_linha)
        self.app.rowconfigure(14, weight=1)
        self.Inserir_estrutura_padrao_telas()
        self.tela_menu_ferramentas_backup(self.app, self.version, self.coluna)

    def trocar_tela_menu_ferramentas_redis(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Ferramentas Redis")
        peso_linha = 0
        self.app.rowconfigure(1, weight=self.peso_linha_um)
        self.app.rowconfigure(2, weight=0)
        self.app.rowconfigure(3, weight=1)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(5, weight=peso_linha)
        self.app.rowconfigure(14, weight=1)
        self.Inserir_estrutura_padrao_telas()
        self.tela_menu_ferramentas_redis(self.app, self.version, self.coluna)

    def trocar_tela_menu_ferramentas_documentos(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Ferramentas Documentos")
        peso_linha = 0
        self.app.rowconfigure(1, weight=self.peso_linha_um)
        self.app.rowconfigure(2, weight=0)
        self.app.rowconfigure(3, weight=1)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(5, weight=peso_linha)
        self.app.rowconfigure(14, weight=1)
        self.Inserir_estrutura_padrao_telas()
        self.tela_menu_ferramentas_documentos(self.app, self.version, self.coluna)

    def trocar_tela_listar_empresas(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Buscar Empresas")
        peso_linha = 0
        self.app.rowconfigure(1, weight=self.peso_linha_um)
        self.app.rowconfigure(2, weight=0)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(5, weight=peso_linha)
        self.app.rowconfigure(6, weight=peso_linha)
        self.app.rowconfigure(7, weight=peso_linha)
        self.app.rowconfigure(8, weight=peso_linha)
        self.app.rowconfigure(9, weight=peso_linha)
        self.app.rowconfigure(15, weight=1)
        self.Inserir_estrutura_padrao_telas()
        self.tela_listar_empresas(self.app, self.version, self.coluna)

    def trocar_tela_atualizacao_banco_update(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Atualização de banco Update")
        peso_linha = 0
        self.app.rowconfigure(1, weight=self.peso_linha_um)
        self.app.rowconfigure(2, weight=0)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(5, weight=peso_linha)
        self.app.rowconfigure(6, weight=peso_linha)
        self.app.rowconfigure(10, weight=1)
        self.Inserir_estrutura_padrao_telas()
        self.trocar_tela_menu_geral()
        self.criar_popup_mensagem("Tela Não implementada")

    def trocar_tela_validadores(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Validadores de Documentos")
        peso_linha = 0
        self.app.rowconfigure(1, weight=self.peso_linha_um)
        self.app.rowconfigure(2, weight=0)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(5, weight=peso_linha)
        self.app.rowconfigure(6, weight=peso_linha)
        self.app.rowconfigure(7, weight=peso_linha)
        self.app.rowconfigure(8, weight=peso_linha)
        self.app.rowconfigure(10, weight=1)
        self.Inserir_estrutura_padrao_telas()
        self.tela_validadores(self.app, self.version, self.coluna)

    def trocar_tela_geradores(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Geradores de Documentos")
        peso_linha = 0
        self.app.rowconfigure(1, weight=self.peso_linha_um)
        self.app.rowconfigure(2, weight=0)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(5, weight=peso_linha)
        self.app.rowconfigure(6, weight=peso_linha)
        self.app.rowconfigure(7, weight=peso_linha)
        self.app.rowconfigure(8, weight=peso_linha)
        self.app.rowconfigure(9, weight=peso_linha)
        self.app.rowconfigure(10, weight=peso_linha)
        self.app.rowconfigure(11, weight=peso_linha)
        self.app.rowconfigure(12, weight=peso_linha)
        self.app.rowconfigure(13, weight=peso_linha)
        self.app.rowconfigure(14, weight=peso_linha)
        self.app.rowconfigure(15, weight=1)
        self.Inserir_estrutura_padrao_telas()
        self.tela_geradores(self.app, self.version, self.coluna)

    def trocar_tela_redis_especifico(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Limpar redis Especifico")
        peso_linha = 0
        self.app.rowconfigure(1, weight=self.peso_linha_um)
        self.app.rowconfigure(2, weight=0)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(9, weight=1)
        self.Inserir_estrutura_padrao_telas()
        self.tela_limpar_redis_especifico(self.app, self.version, self.coluna)

    def trocar_tela_redis_todos(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Limpar todos os redis")
        peso_linha = 0
        self.app.rowconfigure(1, weight=self.peso_linha_um)
        self.app.rowconfigure(2, weight=0)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(5, weight=peso_linha)
        self.app.rowconfigure(6, weight=peso_linha)
        self.app.rowconfigure(9, weight=1)
        self.Inserir_estrutura_padrao_telas()
        self.tela_limpar_redis_todos(self.app, self.version, self.coluna)

    def trocar_tela_manipular_banco_update(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Atualizar registros update")
        peso_linha = 0
        self.app.rowconfigure(1, weight=self.peso_linha_um)
        self.app.rowconfigure(2, weight=0)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(5, weight=peso_linha)
        self.app.rowconfigure(6, weight=peso_linha)
        self.app.rowconfigure(7, weight=peso_linha)
        self.app.rowconfigure(8, weight=peso_linha)
        self.app.rowconfigure(9, weight=peso_linha)
        self.app.rowconfigure(15, weight=1)
        self.Inserir_estrutura_padrao_telas()
        self.tela_manipular_banco_update(self.app, self.version, self.coluna)

    def trocar_tela_download_backup(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Download Backup")
        peso_linha = 0
        self.app.rowconfigure(1, weight=self.peso_linha_um)
        self.app.rowconfigure(2, weight=0)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(5, weight=peso_linha)
        self.app.rowconfigure(6, weight=peso_linha)
        self.app.rowconfigure(7, weight=peso_linha)
        self.app.rowconfigure(8, weight=peso_linha)
        self.app.rowconfigure(9, weight=1)
        self.Inserir_estrutura_padrao_telas()
        self.tela_download_backup(self.app, self.version, self.coluna)

    def trocar_tela_restaurar_backup(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Restaurar Backup")
        peso_linha = 0
        self.app.rowconfigure(1, weight=self.peso_linha_um)
        self.app.rowconfigure(2, weight=0)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(5, weight=peso_linha)
        self.app.rowconfigure(6, weight=peso_linha)
        self.app.rowconfigure(7, weight=peso_linha)
        self.app.rowconfigure(8, weight=peso_linha)
        self.app.rowconfigure(9, weight=peso_linha)
        self.app.rowconfigure(10, weight=2)
        self.Inserir_estrutura_padrao_telas()
        self.tela_restaurar_backup(self.app, self.version, self.coluna)

    def trocar_tela_consultar_versions(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Consultar Version's")
        peso_linha = 0
        self.app.rowconfigure(1, weight=self.peso_linha_um)
        self.app.rowconfigure(2, weight=0)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(15, weight=1)
        self.Inserir_estrutura_padrao_telas()
        self.tela_consultar_versions(self.app, self.version, self.coluna)

    def trocar_tela_replicar_version(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Replicar Versions")
        peso_linha = 0
        self.app.rowconfigure(1, weight=self.peso_linha_um)
        self.app.rowconfigure(2, weight=0)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(5, weight=peso_linha)
        self.app.rowconfigure(6, weight=peso_linha)
        self.app.rowconfigure(7, weight=peso_linha)
        self.app.rowconfigure(15, weight=1)
        self.Inserir_estrutura_padrao_telas()
        self.tela_replicar_version(self.app, self.version, self.coluna)

    def trocar_tela_alterar_aparencia(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Alterar Aparencia")
        peso_linha = 0
        self.app.rowconfigure(1, weight=self.peso_linha_um)
        self.app.rowconfigure(2, weight=0)
        self.app.rowconfigure(3, weight=1)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(5, weight=peso_linha)
        self.app.rowconfigure(6, weight=peso_linha)
        self.app.rowconfigure(7, weight=peso_linha)
        self.app.rowconfigure(8, weight=peso_linha)
        self.app.rowconfigure(14, weight=1)
        self.Inserir_estrutura_padrao_telas()
        self.tela_alterar_aparencia(self.app, self.version, self.coluna)

    def trocar_tela_config(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Config")
        peso_linha = 0
        self.app.rowconfigure(1, weight=self.peso_linha_um)
        self.app.rowconfigure(2, weight=0)
        self.app.rowconfigure(3, weight=1)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(5, weight=peso_linha)
        self.app.rowconfigure(6, weight=peso_linha)
        self.app.rowconfigure(7, weight=peso_linha)
        self.app.rowconfigure(14, weight=1)
        self.Inserir_estrutura_padrao_telas()
        self.tela_config(self.app, self.version, self.coluna)

# monta as telas
    def tela_menu_geral(self, app, version, coluna):
        titulo = "MENU"
        app.title("MSS - " + version + " - " + titulo)

        self.button_menu_geral_ferramentas_banco = Button(
            app,
            text="Ferramentas Banco Muro",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_menu_ferramentas_bancos()
        )
        self.button_menu_geral_ferramentas_backup = Button(
            app,
            text="Ferramentas Backup",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_menu_ferramentas_backup()
        )
        self.button_menu_geral_ferramentas_redis = Button(
            app,
            text="Ferramentas Redis",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_menu_ferramentas_redis()
        )
        self.button_menu_geral_ferramentas_documentos = Button(
            app,
            text="Ferramentas Documentos",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_menu_ferramentas_documentos()
        )
        self.remover_conteudo_linha(10, 2)
        self.inserir_titulos_telas(self.app, titulo, 2, coluna, self.padding_down_titulos)
        self.button_menu_geral_ferramentas_banco.grid(row=4, column=coluna, columnspan=2)
        self.button_menu_geral_ferramentas_backup.grid(row=5, column=coluna, columnspan=2)
        self.button_menu_geral_ferramentas_redis.grid(row=6, column=coluna, columnspan=2)
        self.button_menu_geral_ferramentas_documentos.grid(row=7, column=coluna, columnspan=2)

    def tela_menu_ferramentas_bancos(self, app, version, coluna):
        titulo = "FERRAMENTAS DE BANCO MURO"
        app.title("MSS - " + version + " - " + titulo)

        self.button_ferramentas_bancos_busca_banco = Button(
            app,
            text="Atualizar registros update",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_manipular_banco_update()
        )
        self.button_ferramentas_bancos_buscar_versions = Button(
            app,
            text="Consultar Version's",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_consultar_versions()
        )
        self.button_ferramentas_bancos_replicar_version = Button(
            app,
            text="Replicar version",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_replicar_version()
        )
        self.button_ferramentas_bancos_buscar_empresas = Button(
            app,
            text="Buscar Empresas",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_listar_empresas()
        )
        self.button_ferramentas_bancos_voltar = Button(
            app,
            text="Voltar",
            width=15,
            height=2,
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_menu_geral()
        )
        self.remover_conteudo_linha(10, 2)
        self.inserir_titulos_telas(self.app, titulo, 2, coluna, self.padding_down_titulos)
        self.button_ferramentas_bancos_busca_banco.grid(row=4, column=coluna, columnspan=2)
        self.button_ferramentas_bancos_buscar_versions.grid(row=5, column=coluna, columnspan=2)
        self.button_ferramentas_bancos_replicar_version.grid(row=6, column=coluna, columnspan=2)
        self.button_ferramentas_bancos_buscar_empresas.grid(row=7, column=coluna, columnspan=2)
        self.button_ferramentas_bancos_voltar.grid(row=15, column=1, padx=15, pady=15, columnspan=2, sticky="ES")

    def tela_menu_ferramentas_backup(self, app, version, coluna):
        titulo = "FERRAMENTAS BACKUP"
        app.title("MSS - " + version + " - " + titulo)

        self.button_menu_download = Button(
            app,
            text="Download Backup",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_download_backup()
        )
        self.button_menu_restaurar = Button(
            app,
            text="Restaurar Backup",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_restaurar_backup()
        )
        self.button_menu_ferramentas_backup_voltar = Button(
            app,
            text="Voltar",
            width=15,
            height=2,
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_menu_geral()
        )
        self.remover_conteudo_linha(10, 2)
        self.inserir_titulos_telas(self.app, titulo, 2, coluna, self.padding_down_titulos)
        self.button_menu_download.grid(row=4, column=coluna, columnspan=2)
        self.button_menu_restaurar.grid(row=5, column=coluna, columnspan=2)
        self.button_menu_ferramentas_backup_voltar.grid(row=15, column=1, padx=15, pady=15, columnspan=2, sticky="ES")

    def tela_menu_ferramentas_redis(self, app, version, coluna):
        titulo = "FERRAMENTAS REDIS"
        app.title("MSS - " + version + " - " + titulo)

        self.button_ferramenta_redis_limpar_todos = Button(
            app,
            text="Limpar todos os redis",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_redis_todos()
        )
        self.button_ferramenta_redis_limpar_espec = Button(
            app,
            text="Limpar Redis especifico",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_redis_especifico()
        )
        self.button_ferramenta_redis_voltar = Button(
            app,
            text="Voltar",
            width=15,
            height=2,
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_menu_geral()
        )
        self.remover_conteudo_linha(10, 2)
        self.inserir_titulos_telas(self.app, titulo, 2, coluna, self.padding_down_titulos)
        self.button_ferramenta_redis_limpar_todos.grid(row=4, column=coluna, columnspan=2)
        self.button_ferramenta_redis_limpar_espec.grid(row=5, column=coluna, columnspan=2)
        self.button_ferramenta_redis_voltar.grid(row=15, column=1, padx=15, pady=15, columnspan=2, sticky="ES")

    def tela_menu_ferramentas_documentos(self, app, version, coluna):
        titulo = "FERRAMENTAS DOCUMENTOS"
        app.title("MSS - " + version + " - " + titulo)

        self.button_menu_ferramentas_documentos_geradores = Button(
            app,
            text="Geradores de documentos",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_geradores()
        )
        self.button_menu_ferramentas_documentos_validadores = Button(
            app,
            text="Validadores de documentos",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_validadores()
        )
        self.button_menu_ferramentas_documentos_voltar = Button(
            app,
            text="Voltar",
            width=15,
            height=2,
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_menu_geral()
        )
        self.remover_conteudo_linha(10, 2)
        self.inserir_titulos_telas(self.app, titulo, 2, coluna, self.padding_down_titulos)
        self.button_menu_ferramentas_documentos_geradores.grid(row=4, column=coluna, columnspan=2)
        self.button_menu_ferramentas_documentos_validadores.grid(row=5, column=coluna, columnspan=2)
        self.button_menu_ferramentas_documentos_voltar.grid(row=15, column=1, padx=15, pady=15, columnspan=2, sticky="ES")

    def tela_listar_empresas(self, app, version, coluna):
        titulo = "BUSCAR EMPRESAS"
        app.title("MSS - " + version + " - " + titulo)
        opcoes_servidor = list(self.infos_config["conexoes"])
        opcoes_basemuro = list(self.infos_config["bases_muro"])

        self.label_busca_empresa_version_servidor = Label(
            text="Servidor:",
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.combobox_busca_empresa_servidor_version = Combobox(
            app,
            values=opcoes_servidor,
        )
        self.label_busca_empresa_banco_muro = Label(
            text="Base Muro:",
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.combobox_busca_empresa_banco_muro = Combobox(
            app,
            values=opcoes_basemuro,
        )
        self.button_busca_empresa_atualizacao_limpar = Button(
            app,
            text="Limpar",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.limpar_caixa_texto()
        )
        self.button_busca_empresa_atualizacao_inicio = Button(
            app,
            text="Iniciar",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.iniciar_processo_buscar_empresas()
        )
        self.button_busca_empresa_atualizacao_voltar = Button(
            app,
            text="Voltar",
            width=15,
            height=2,
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_menu_ferramentas_bancos()
        )
        if len(opcoes_servidor) > 0:
            self.combobox_busca_empresa_servidor_version.set(opcoes_servidor[0])
        if len(opcoes_basemuro) > 0:
            self.combobox_busca_empresa_banco_muro.set(opcoes_basemuro[0])
        self.remover_conteudo_linha(15, 2)
        self.inserir_titulos_telas(self.app, titulo, 2, coluna, self.padding_down_titulos)
        self.label_busca_empresa_version_servidor.grid(row=3, column=coluna, sticky="WS", pady=(10, 0), padx=(15))
        self.combobox_busca_empresa_servidor_version.grid(row=4, column=coluna, columnspan=2, pady=(0, 10), sticky="WE", padx=(15))
        self.label_busca_empresa_banco_muro.grid(row=5, column=coluna, sticky="WS", pady=(10, 0), padx=(15))
        self.combobox_busca_empresa_banco_muro.grid(row=6, column=coluna, columnspan=2, pady=(0, 10), sticky="WE", padx=(15))
        self.inserir_caixa_texto(7, 8, coluna, "Saida:", (10,0), (0,0), 12)
        self.button_busca_empresa_atualizacao_limpar.grid(row=9, column=coluna, padx=(15), pady=(10, 0), sticky="WE")
        self.button_busca_empresa_atualizacao_inicio.grid(row=9, column=1, padx=(15), pady=(10, 0), sticky="WE")
        self.button_busca_empresa_atualizacao_voltar.grid(row=15, column=1, padx=15, pady=15, columnspan=2, sticky="ES")

    def tela_limpar_redis_especifico(self, app, version, coluna):
        titulo = "LIMPAR REDIS ESPECIFICOS"
        app.title("MSS - " + version + " - " + titulo)
        opcoes_redis = []

        opcoes_grupo_redis = self.buscar_redis_dict()

        self.label_grupo_redis = Label(
            text="Grupo Redis:",
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.combobox_redis_grupo = Combobox(
            app,
            values=opcoes_grupo_redis,
        )
        self.label_lista_redis = Label(
            text="Redis:",
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.combobox_redis = Combobox(
            app,
            values=opcoes_redis,
        )
        self.button_redis_limpar = Button(
            app,
            text="Limpar",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.limpar_caixa_texto()
        )
        self.button_redis_inicio = Button(
            app,
            text="Iniciar",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.menu_redis_especifico()
        )
        self.button_redis_voltar = Button(
            app,
            text="Voltar",
            width=15,
            height=2,
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_menu_ferramentas_redis()
        )

        self.remover_conteudo_linha(10, 2)
        self.inserir_titulos_telas(self.app, titulo, 2, coluna, self.padding_down_titulos)
        if len(opcoes_grupo_redis) > 0:
            self.combobox_redis_grupo.set(opcoes_grupo_redis[0])
        if len(opcoes_redis) > 0:
            self.combobox_redis_grupo.set(opcoes_redis[0])
        self.label_grupo_redis.grid(row=3, column=coluna, columnspan=2, pady=(0, 0), padx=(15, 15), sticky="WS")
        self.combobox_redis_grupo.grid(row=4, column=coluna, columnspan=2, pady=(0, 10), padx=(15, 15), sticky="WE")
        self.combobox_redis_grupo.bind("<<ComboboxSelected>>", self.atualizar_opcoes)
        self.label_lista_redis.grid(row=5, column=coluna, columnspan=2, pady=(0, 0), padx=(15, 15), sticky="WS")
        self.combobox_redis.grid(row=6, column=coluna, columnspan=2, pady=(0, 0), padx=(15, 15), sticky="WE")
        self.inserir_caixa_texto(7, 8, coluna, "Saida:", (10,0), (0,0), 12)
        self.button_redis_limpar.grid(row=9, column=coluna, padx=(15), pady=(10, 0), sticky="WE")
        self.button_redis_inicio.grid(row=9, column=1, padx=(15), pady=(10, 0), sticky="WE")
        self.button_redis_voltar.grid(row=15, column=1, padx=15, pady=15, columnspan=2, sticky="ES")
        self.atualizar_opcoes("<<ComboboxSelected>>")

    def tela_limpar_redis_todos(self, app, version, coluna):
        titulo = "LIMPAR TODOS OS REDIS"
        app.title("MSS - " + version + " - " + titulo)

        opcoes_grupo_redis = self.buscar_redis_dict()

        self.label_redis_grupo = Label(
            text="Grupo Redis:",
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.combobox_redis_grupo = Combobox(
            app,
            values=opcoes_grupo_redis,
        )
        self.button_atualizacao_limpar = Button(
            app,
            text="Limpar",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.limpar_caixa_texto()
        )
        self.button_atualizacao_inicio = Button(
            app,
            text="Iniciar",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.menu_redis_todos()
        )
        self.button_atualizacao_voltar = Button(
            app,
            text="Voltar",
            width=15,
            height=2,
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_menu_ferramentas_redis()
        )

        if len(opcoes_grupo_redis) > 0:
            self.combobox_redis_grupo.set(opcoes_grupo_redis[0])
        self.remover_conteudo_linha(10, 2)
        self.inserir_titulos_telas(self.app, titulo, 2, coluna, self.padding_down_titulos)
        self.label_redis_grupo.grid(row=3, column=coluna, columnspan=2, pady=(0, 0), padx=(15, 15), sticky="WS")
        self.combobox_redis_grupo.grid(row=4, column=coluna, columnspan=2, pady=(0, 0), padx=(15, 15), sticky="WE")
        self.inserir_caixa_texto(5, 6, coluna, "Saida:", (10,0), (0,0), 15)
        self.button_atualizacao_limpar.grid(row=9, column=coluna, padx=(15), pady=(10, 0), sticky="WE")
        self.button_atualizacao_inicio.grid(row=9, column=1, padx=(15), pady=(10, 0), sticky="WE")
        self.button_atualizacao_voltar.grid(row=15, column=1, padx=15, pady=15, columnspan=2, sticky="ES")

    def tela_restaurar_backup(self, app, version, coluna):
        titulo = "Restaurar Backup"
        app.title("MSS - " + version + " - " + titulo)
        placeholder_color = "gray"
        opcoes_servidor = list(self.infos_config["conexoes"])

        self.label_restaurar_servidor = Label(
            text="Servidor:",
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.combobox_servidor_restaurar = Combobox(
            app,
            values=opcoes_servidor,
            width=29
        )
        self.button_restaurar_limpar = Button(
            app,
            text="Limpar",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.limpar_caixa_texto()
        )
        self.button_restaurar_inicio = Button(
            app,
            text="Iniciar",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.menu_restaurar_banco()
        )
        self.button_restaurar_voltar = Button(
            app,
            text="Voltar",
            width=15,
            height=2,
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_menu_ferramentas_backup()
        )
        if len(opcoes_servidor) > 0:
            self.combobox_servidor_restaurar.set(opcoes_servidor[0])
        self.remover_conteudo_linha(10, 2)
        self.inserir_titulos_telas(self.app, titulo, 2, coluna, self.padding_down_titulos)
        self.label_restaurar_servidor.grid(row=3, column=coluna, sticky="WS", pady=(10, 0), padx=(10, 10))
        self.combobox_servidor_restaurar.grid(row=4, column=coluna, columnspan=2, pady=(0, 0), padx=(10, 10), sticky="WS")
        self.inserir_input_placeholder_modular('gray', 3, 4, 1, "E:\\DBDATA\\LOG\\PT,D:\\DBDATA\\DATA\\PT","Caminho LDF e MDF:", "WS", "WN", 33, (10,0), (10,0), (0,0), (10,0))
        self.inserir_input_placeholder_modular('black', 5, 6, coluna, "","Nome arquivo .bak:", "WS", "WN", 33, (10,0), (10,0), (0,0), (10,0) )
        self.inserir_input_placeholder_modular('black', 5, 6, 1, "","Nome do banco:", "WS", "WN", 33, (10,0), (10,0), (0,0), (10,0))
        self.inserir_caixa_texto(7, 8, coluna, "Saida:", (10,0), (0,0), 12)
        self.button_restaurar_limpar.grid(row=9, column=coluna, padx=(15), pady=(10, 0),  sticky="WE")
        self.button_restaurar_inicio.grid(row=9, column=1, padx=(15), pady=(10, 0),  sticky="WE")
        self.button_restaurar_voltar.grid(row=15, column=1, padx=15, pady=15, columnspan=2, sticky="ES")

    def tela_download_backup(self, app, version, coluna):
        titulo = "Download Backup"
        app.title("MSS - " + version + " - " + titulo)
        opcoes_servidor = list(self.infos_config["conexoes"])

        self.label_download_servidor = Label(
            text="Servidor:",
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.combobox_servidor_download = Combobox(
            app,
            values=opcoes_servidor,
        )
        self.button_download_limpar = Button(
            app,
            text="Limpar",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.limpar_caixa_texto()
        )
        self.button_download_inicio = Button(
            app,
            text="Iniciar",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.menu_download_backup()
        )
        self.button_download_voltar = Button(
            app,
            text="Voltar",
            width=15,
            height=2,
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_menu_ferramentas_backup()
        )
        if len(opcoes_servidor) > 0:
            self.combobox_servidor_download.set(opcoes_servidor[0])
        self.remover_conteudo_linha(10, 2)
        self.inserir_titulos_telas(self.app, titulo, 2, coluna, self.padding_down_titulos)
        self.label_download_servidor.grid(row=3, column=coluna, sticky="WS", pady=(10, 0), padx=(15))
        self.combobox_servidor_download.grid(row=4, column=coluna, columnspan=2, pady=(0, 10), sticky="WE", padx=(15))
        self.inserir_input_placeholder(5, 6, coluna, "URL DO BACKUP", "Endereço URL:", 5)
        self.inserir_caixa_texto(7, 8, coluna, "Saida:", (10,0), (0,0), 12)
        self.button_download_limpar.grid(row=9, column=coluna, padx=(15), pady=(10, 0), sticky="WE")
        self.button_download_inicio.grid(row=9, column=1, padx=(15), pady=(10, 0), sticky="WE")
        self.button_download_voltar.grid(row=15, column=1, padx=15, pady=15, columnspan=2, sticky="ES")

    def tela_manipular_banco_update(self, app, version, coluna):
        titulo = "ATUALIZAR REGISTROS UPDATE"
        app.title("MSS - " + version + " - " + titulo)
        opcoes_servidor = list(self.infos_config["conexoes"])

        self.label_busca_servidor = Label(
            text="Servidor:",
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.combobox_servidor = Combobox(
            app,
            values=opcoes_servidor,
        )
        self.button_busca_limpar = Button(
            app,
            text="Limpar",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.limpar_caixa_texto()
        )
        self.button_busca_inicio = Button(
            app,
            text="Iniciar",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.iniciar_processo_manipula_banco()
        )
        self.button_busca_voltar = Button(
            app,
            text="Voltar",
            width=15,
            height=2,
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_menu_ferramentas_bancos()
        )
        if len(opcoes_servidor) > 0:
            self.combobox_servidor.set(opcoes_servidor[0])
        self.remover_conteudo_linha(15, 2)
        self.inserir_titulos_telas(self.app, titulo, 2, coluna, self.padding_down_titulos)
        self.inserir_input_placeholder(3, 4, coluna, "Insira o version para downgrade...", "Version:",10)
        self.label_busca_servidor.grid(row=5, column=coluna, sticky="WS", pady=(10, 0), padx=(15))
        self.combobox_servidor.grid(row=6, column=coluna, pady=(0, 10), sticky="WE", columnspan=2, padx=(15))
        self.inserir_caixa_texto(7, 8, coluna, "Saida:", (10,0), (0,0), 12)
        self.button_busca_limpar.grid(row=9, column=coluna, padx=(15), pady=(10, 0), sticky="WE")
        self.button_busca_inicio.grid(row=9, column=1, padx=(15), pady=(10, 0), sticky="WE")
        self.button_busca_voltar.grid(row=15, column=1, padx=15, pady=15, sticky="ES")

    def tela_consultar_versions(self, app, version, coluna):
        titulo = "CONSULTAR VERSION'S"
        app.title("MSS - " + version + " - " + titulo)
        opcoes_servidor = list(self.infos_config["conexoes"])

        self.label_consulta_servidor = Label(
            text="Servidor:",
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.combobox_servidor_consulta_version = Combobox(
            app,
            values=opcoes_servidor,
        )
        self.button_consultar_limpar = Button(
            app,
            text="Limpar",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.limpar_caixa_texto()
        )
        self.button_consultar_inicio = Button(
            app,
            text="Iniciar",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.iniciar_processo_consulta()
        )
        self.button_consultar_voltar = Button(
            app,
            text="Voltar",
            width=15,
            height=2,
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_menu_ferramentas_bancos()
        )
        if len(opcoes_servidor) > 0:
            self.combobox_servidor_consulta_version.set(opcoes_servidor[0])
        self.remover_conteudo_linha(15, 2)
        self.inserir_titulos_telas(self.app, titulo, 2, coluna, self.padding_down_titulos)
        self.label_consulta_servidor.grid(row=3, column=coluna, sticky="WS", pady=(10, 0), padx=(15))
        self.combobox_servidor_consulta_version.grid(row=4, column=coluna, columnspan=2, pady=(0, 10), sticky="WE", padx=(15))
        self.inserir_caixa_texto(5, 6, coluna, "Saida:", (10,0), (0,0), 12)
        self.button_consultar_limpar.grid(row=9, column=coluna, padx=(15), pady=(10, 0), sticky="WE")
        self.button_consultar_inicio.grid(row=9, column=1, padx=(15), pady=(10, 0), sticky="WE")
        self.button_consultar_voltar.grid(row=15, column=1, padx=15, pady=15, columnspan=2, sticky="ES")

    def tela_replicar_version(self, app, version, coluna):
        titulo = "REPLICAR VERSION'S"
        app.title("MSS - " + version + " - " + titulo)
        opcoes_servidor = list(self.infos_config["conexoes"])

        self.label_replicar_servidor = Label(
            text="Servidor:",
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.combobox_servidor_replicar = Combobox(
            app,
            values=opcoes_servidor,
        )
        self.button_replicar_limpar = Button(
            app,
            text="Limpar",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.limpar_caixa_texto()
        )
        self.button_replicar_inicio = Button(
            app,
            text="Iniciar",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.iniciar_processo_replicar()
        )
        self.button_replicar_voltar = Button(
            app,
            text="Voltar",
            width=15,
            height=2,
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_menu_ferramentas_bancos()
        )
        if len(opcoes_servidor) > 0:
            self.combobox_servidor_replicar.set(opcoes_servidor[0])
        self.remover_conteudo_linha(15, 2)
        self.inserir_titulos_telas(self.app, titulo, 2, coluna, self.padding_down_titulos)
        self.label_replicar_servidor.grid(row=3, column=coluna, sticky="W", pady=(10, 0), padx=(15))
        self.combobox_servidor_replicar.grid(row=4, column=coluna, columnspan=2, pady=(0, 10), sticky="WE", padx=(15))
        self.inserir_caixa_texto(5, 6, coluna, "Saida:", (10,0), (0,0), 12)
        self.button_replicar_limpar.grid(row=9, column=coluna, padx=(15), pady=(10, 0), sticky="WE")
        self.button_replicar_inicio.grid(row=9, column=1, padx=(15), pady=(10, 0), sticky="WE")
        self.button_replicar_voltar.grid(row=15, column=1, padx=15, pady=15, columnspan=2, sticky="ES")

    def tela_geradores(self, app, version, coluna):
        titulo = "GERADORES"
        app.title("MSS - " + version + " - " + titulo)
        opcoes = ["CEI", "CNPJ", "CPF", "NIF", "PIS"]
        self.valor_checkbox_mascara_num = BooleanVar()
        self.valor_checkbox_gerar_arquivo = BooleanVar()

        self.label_gerador = Label(
            text="Documentos",
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.combobox = Combobox(
            app,
            values=opcoes,
        )
        self.checkbox_mascara_num = Checkbutton(
            app,
            text='Gerar com mascara',
            onvalue=True,
            offvalue=False,
            variable=self.valor_checkbox_mascara_num
        )
        self.checkbox_gerar_arquivo = Checkbutton(
            app,
            text='Gerar valores em arquivo txt',
            onvalue=True,
            offvalue=False,
            variable=self.valor_checkbox_gerar_arquivo
        )
        self.button_gerador_inicio = Button(
            app,
            text="Gerar",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.menu_gerador_documentos()
        )
        self.button_gerador_limpar = Button(
            app,
            text="Limpar",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.limpar_caixa_texto()
        )
        self.button_gerador_voltar = Button(
            app,
            text="Voltar",
            width=15,
            height=2,
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_menu_ferramentas_documentos()
        )
        self.remover_conteudo_linha(10, 2)
        self.combobox.set(opcoes[0])
        self.inserir_titulos_telas(self.app, titulo, 2, coluna, self.padding_down_titulos)
        self.label_gerador.grid(row=3, column=coluna, padx=(15,0), pady=(0,0), sticky="W")
        self.combobox.grid(row=4, column=coluna, pady=(0, 0), columnspan=2, sticky="WE", padx=(15))
        self.inserir_input_placeholder(5, 6, coluna, "Clique em Gerar ou insira a quantidade desejada", "Quantidade:", 10)
        self.checkbox_mascara_num.grid(row=7, column=coluna, pady=(0, 0), padx=(15,0), sticky="W")
        self.checkbox_gerar_arquivo.grid(row=7, column=1, pady=(0, 0), padx=(0,0), sticky="W")
        self.inserir_caixa_texto(8, 9, coluna, "Saida:", (0,0), (5,0), 12)
        self.button_gerador_limpar.grid(row=10, column=coluna, padx=(15), pady=(10, 0), sticky="WE")
        self.button_gerador_inicio.grid(row=10, column=1, padx=(15), pady=(10, 0), sticky="WE")
        self.button_gerador_voltar.grid(row=15, column=1, padx=15, pady=15, columnspan=2, sticky="ES")

    def tela_validadores(self, app, version, coluna):
        titulo = "Validadores"
        app.title("MSS - " + version + " - " + titulo)
        opcoes = ["CEI", "CNPJ", "CPF", "NIF", "PIS"]
        self.combobox = Combobox(
            app,
            values=opcoes,
        )
        self.button_gerador_inicio = Button(
            app,
            text="Validar",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.menu_validador_documentos()
        )
        self.button_gerador_limpar = Button(
            app,
            text="Limpar",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.limpar_caixa_texto()
        )
        self.button_gerador_voltar = Button(
            app,
            text="Voltar",
            width=15,
            height=2,
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_menu_ferramentas_documentos()
        )
        self.remover_conteudo_linha(10, 2)
        self.combobox.set(opcoes[0])
        self.inserir_titulos_telas(self.app, titulo, 2, coluna, self.padding_down_titulos)
        self.combobox.grid(row=3, column=coluna, pady=(0, 10), padx=(15), columnspan=2, sticky="WE")
        self.inserir_input_placeholder(4, 5, coluna, " Insira o documento para ser validado", "Documento:", 10)
        self.inserir_caixa_texto(6, 7, coluna, "Saida:", (10,0), (0,0), 12)
        self.button_gerador_inicio.grid(row=8, column=1, padx=(15), pady=(10, 0), sticky="WE")
        self.button_gerador_limpar.grid(row=8, column=coluna, padx=(15), pady=(10, 0), sticky="WE")
        self.button_gerador_voltar.grid(row=15, column=1, padx=15, pady=15, sticky="ES")

    def tela_config(self, app, version, coluna):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Tela - CONFIGURAÇÃO")
        titulo = "CONFIGURAÇÃO"
        app.title("MSS - " + version + " - " + titulo)
        self.button_nav_criar = None
        self.button_nav_escolher = None

        self.button_config_existente = Button(
            app,
            text="Escolher arquivo Config",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_titulos"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.inserir_campos_arquivo_existente(app, coluna)
        )
        self.button_config_novo = Button(
            app,
            text="Novo arquivo Config",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_titulos"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.inserir_campos_arquivo_novo(app, coluna)
        )
        self.remover_conteudo_linha(10, 2)
        self.inserir_titulos_telas(self.app, titulo, 2, coluna, self.padding_down_titulos)
        self.button_config_existente.grid(row=4, column=coluna, columnspan=2)
        self.button_config_novo.grid(row=5, column=coluna, columnspan=2)

    def tela_alterar_aparencia(self, app, version, coluna):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Tela - CONFIGURAÇÃO")
        titulo = "ALTERAR APARENCIA"
        app.title("MSS - " + version + " - " + titulo)
        tam_width = 5
        valores_input = self.ler_arquivo_config()

        self.label_background_fundo = Label(
            app,
            text="Cor do fundo",
            font=('Arial', 12),
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.entry_background_fundo = Entry(
            self.app,
            width=10
        )
        self.button_background_fundo = Button(
            app,
            text="Cor",
            width=tam_width,
            height=1,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.caixa_selecao_de_cor(self.entry_background_fundo)
        )
        self.label_background_titulos = Label(
            app,
            text="Cor dos titulos",
            font=('Arial', 12),
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.entry_background_titulos = Entry(
            self.app,
            width=10
        )
        self.button_background_titulos = Button(
            app,
            text="Cor",
            width=tam_width,
            height=1,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.caixa_selecao_de_cor(self.entry_background_titulos)
        )
        self.label_background_botoes = Label(
            app,
            text="Cor dos Botões",
            font=('Arial', 12),
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.entry_background_botoes = Entry(
            self.app,
            width=10
        )
        self.button_background_botoes = Button(
            app,
            text="Cor",
            width=tam_width,
            height=1,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.caixa_selecao_de_cor(self.entry_background_botoes)
        )
        self.label_background_botoes_navs = Label(
            app,
            text="Cor dos Botões navs",
            font=('Arial', 12),
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.entry_background_botoes_navs = Entry(
            self.app,
            width=10
        )
        self.button_background_botoes_navs = Button(
            app,
            text="Cor",
            width=tam_width,
            height=1,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.caixa_selecao_de_cor(self.entry_background_botoes_navs)
        )
        self.label_background_fonte = Label(
            app,
            text="Cor das fontes",
            font=('Arial', 12,),
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.entry_background_fonte = Entry(
            self.app,
            width=10
        )
        self.button_background_fonte = Button(
            app,
            text="Cor",
            width=tam_width,
            height=1,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.caixa_selecao_de_cor(self.entry_background_fonte)
        )
        self.button_nav_salvar = Button(
            app,
            text="Salvar",
            name="button_criar",
            width=15,
            height=2,
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.alterar_background()
        )

        self.remover_conteudo_linha(10, 2)
        self.inserir_titulos_telas(self.app, titulo, 2, coluna, self.padding_down_titulos)
        self.label_background_fundo.grid(row=4, column=coluna, padx=(15,0), pady=(0,0), sticky="W")
        self.entry_background_fundo.grid(row=4, column=coluna, padx=(15,0), pady=(0,0), sticky="E")
        self.button_background_fundo.grid(row=4, column=1, padx=(15,15), pady=(0,0), sticky="WE")
        self.label_background_titulos.grid(row=5, column=coluna, padx=(15,0), pady=(0,0), sticky="W")
        self.entry_background_titulos.grid(row=5, column=coluna, padx=(15,0), pady=(0,0), sticky="E")
        self.button_background_titulos.grid(row=5, column=1, padx=(15,15), pady=(0,0), sticky="WE")
        self.label_background_botoes.grid(row=6, column=coluna, padx=(15,0), pady=(0,0), sticky="W")
        self.entry_background_botoes.grid(row=6, column=coluna, padx=(15,0), pady=(0,0), sticky="E")
        self.button_background_botoes.grid(row=6, column=1, padx=(15,15), pady=(0,0), sticky="WE")
        self.label_background_botoes_navs.grid(row=7, column=coluna, padx=(15,0), pady=(0,0), sticky="W")
        self.entry_background_botoes_navs.grid(row=7, column=coluna, padx=(15,0), pady=(0,0), sticky="E")
        self.button_background_botoes_navs.grid(row=7, column=1, padx=(15,15), pady=(0,0), sticky="WE")
        self.label_background_fonte.grid(row=8, column=coluna, padx=(15,0), pady=(0,0), sticky="W")
        self.entry_background_fonte.grid(row=8, column=coluna, padx=(15,0), pady=(0,0), sticky="E")
        self.button_background_fonte.grid(row=8, column=1, padx=(15,15), pady=(0,0), sticky="WE")
        self.button_nav_salvar.grid(row=15, column=1, padx=(0,15), pady=(0,15), columnspan=2, sticky="ES")
        self.entry_background_fundo.insert(0, valores_input[0])
        self.entry_background_titulos.insert(0, valores_input[1])
        self.entry_background_botoes.insert(0, valores_input[2])
        self.entry_background_botoes_navs.insert(0, valores_input[3])
        self.entry_background_fonte.insert(0, valores_input[4])

    def tela(self):
        self.app.geometry(f"{self.largura}x{self.altura}+{self.metade_wid}+{self.metade_hei}")
        self.status_thread = False
        menu = Menu(self.app)
        self.app.config(menu=menu)

        self.peso_linha_um = 0
        self.peso_linha_dois = 1
        self.peso_linha = 1
        self.peso_ultima_linha = 1
        self.peso_coluna = 1
        self.padding_down_titulos = 10

        self.app.columnconfigure(0, weight=self.peso_coluna)
        self.app.columnconfigure(1, weight=self.peso_coluna)
        return self.app

    def main(self):
        self.app = Tk()
        self.largura = 450
        self.altura = 535
        pos_wid = self.app.winfo_screenwidth()
        pos_hei = self.app.winfo_screenheight()
        self.metade_wid = int((pos_wid / 2) - (self.largura / 2))
        self.metade_hei = int((pos_hei / 2) - (self.altura / 2))
        validar_diretorio(self.nomes, self.criar_popup_mensagem)

        # Data/hora inicio do programa
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Programa iniciado")
        # Versão atual do programa
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Versão:  {self.version}")
        self.app = self.tela()
        self.app.protocol("WM_DELETE_WINDOW", self.finalizar)
        self.validar_data_atualizacao_config()
        self.atualizador()

        try:
            if os.path.isfile(f"{self.nomes['diretorio_config']}\\{self.nomes['arquivo_config_default']}.conf"):
                self.ler_arquivo_config()
                if self.infos_config_prog['config_default'] != "":
                    self.infos_config_prog['escolha_manual'] = False
                    self.escolher_config_existente()
                else:
                    self.trocar_tela_config()

            else:
                self.criar_arquivo_config_prog()
                self.ler_arquivo_config()
                self.trocar_tela_config()

        except Exception as error:
            self.criar_popup_mensagem(f"Erro ao acessar arquivo de configuração default {error}")
            self.trocar_tela_config()

        self.app.mainloop()


prog = Aplicativo()
