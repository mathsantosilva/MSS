# coding: utf-8
from datetime import datetime
import json
import os
import re
import sys
from tkinter import colorchooser
from tkinter.ttk import *
import pyodbc
from github import Github
import requests
import shutil
import subprocess
from tkinter import *
import threading
import redis
import configparser
import random
import math


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

def pesquisar_maior_tag(username, repository, tag_atual, popup_mensagem):
    github = Github()
    tags = []
    try:
        repo = github.get_repo(f"{username}/{repository}")
        tags_on = repo.get_tags()
        for tag_in in tags_on:
            tags.append(tag_in.name)
    except Exception as error:
        popup_mensagem(f"Erro ao consultar tags para atualização: {error} ")
    else:
        maior_tag = None
        try:
            for tag in tags:
                if comparar_tags(tag, tag_atual) > 0:
                    if maior_tag is None or comparar_tags(tag, maior_tag) > 0:
                        maior_tag = tag
                        break
        except Exception as error:
            popup_mensagem(f"Erro ao consultar tags para atualização: {error} ")

        return maior_tag

def realizar_download(maior_tag, popup_mensagem):
    try:
        caminho = f"https://github.com/mathsantosilva/MSS/releases/download/{maior_tag}/BuscaMuro.exe"
        response = requests.get(caminho)
    except Exception as error:
        popup_mensagem(f"Erro ao consultar tags para atualização: {error} ")
    else:
        try:
            if os.path.exists("C:/MSS_temp"):
                return
            else:
                os.makedirs("C:/MSS_temp")
        except Exception as error:
            popup_mensagem(f"Erro ao criar/validar a pasta C:/MSS_temp: {error} ")
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

def fechar_janela(msg):
    msg.destroy()

def data_hora_atual():
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return data_hora

def data_atual():
    data_hora = datetime.now().strftime("%d-%m-%Y")
    return data_hora

def validar_linha(nome):
    with open(f"Log\\{nome}.txt", "r") as arquivo_insp:
        conteudo = arquivo_insp.read()
        linhas = conteudo.count("\n") + 1
        caracteres = conteudo.count("")
    if linhas == 1 and caracteres == 1:
        pula_linha = ""
    else:
        pula_linha = "\n"

    return pula_linha

def validar_diretorio(nomes, popup_mensagem):
    # Criar diretorio log
    try:
        if not os.path.exists(nomes['diretorio_log']):
            os.makedirs(nomes['diretorio_log'])
    except Exception as error:
        popup_mensagem(
            f"\n{data_hora_atual()} - INFO - Erro ao criar/validar a pasta {nomes['diretorio_log']}: {error} ")

    # Criar diretorio config
    try:
        if not os.path.exists(nomes['diretorio_config']):
            os.makedirs(nomes['diretorio_config'])
    except Exception as error:
        popup_mensagem(
            f"\n{data_hora_atual()} - INFO - Erro ao criar/validar a pasta {nomes['diretorio_config']}: {error} ")

class Aplicativo:
    version = "3.4.1"
    coluna = 1
    widget = []
    nomes = dict()
    nomes['pasta_config'] = 'Config/'
    nomes['diretorio_log'] = 'Log'
    nomes['diretorio_config'] = 'Config'
    nomes['arquivo_base_muro'] = 'base_muro'
    nomes['arquivo_busca_bancos'] = 'busca_bancos'
    nomes['arquivo_replicar_version'] = 'replicar_version'
    nomes['arquivo_download_backup'] = 'download_backup'
    nomes['arquivo_restaurar_banco'] = 'restaurar_banco'
    nomes['arquivo_connection_strings'] = 'connection_strings'
    nomes['arquivo_validar'] = 'buscar_versions'
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

    def finalizar(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Programa finalizado")
        sys.exit(200)

    def limpar_string(self, documento_inserido):
        lista_limpa = []
        lista_suja = documento_inserido.split(",")
        for item in lista_suja:
            sem_mascara = item.replace(".", "")
            sem_mascara = sem_mascara.replace(",", "")
            sem_mascara = sem_mascara.replace("-", "")
            sem_mascara = sem_mascara.replace("/", "")
            lista_limpa.append(sem_mascara)
        return lista_limpa

    def escrever_arquivo_log(self, nome_arquivo, texto):
        self.arquivo_log = open(f"{self.nomes['diretorio_log']}\\{nome_arquivo}.txt", "a")
        pula_linha = validar_linha(nome_arquivo)
        self.arquivo_log.write(f"{pula_linha}{data_hora_atual()} - {texto}")
        self.arquivo_log.close()

    def escrever_arquivo_config(self, nome_arquivo, texto, extensao):
        self.arquivo_config = open(f"{self.nomes['diretorio_config']}\\{nome_arquivo}.{extensao}", "a")
        self.arquivo_config.write(texto)
        self.arquivo_config.close()

    def atualizador(self):
        if self.infos_config_prog['atualizar']:
            username = "mathsantosilva"
            repository = "MSS"
            tag_atual = self.version
            maior_tag = pesquisar_maior_tag(username, repository, tag_atual, self.popup_mensagem)

            if maior_tag is not None:
                realizar_download(maior_tag, self.popup_mensagem)
                if os.path.exists("C:/MSS_temp"):
                    dir_atual = os.getcwd()
                    executar_comando_batch(dir_atual)
                    self.alterar_ult_busca()
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
                    self.popup_mensagem(f"Erro ao criar/validar a pasta {self.nomes['diretorio_log']}: {error} ")
        else:
            return

    def menu_cascata(self):
        menu_bar = Menu(self.app)
        self.app.config(menu=menu_bar)
        file_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Configuração", menu=file_menu)
        file_menu.add_command(label="Trocar Configuração", command=self.trocar_tela_config)

        help_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Aparência", menu=help_menu)
        help_menu.add_command(label="Alterar Aparência", command=self.trocar_tela_alterar_aparencia)
        help_menu.add_command(label="Redefinir Aparência", command=self.redefinir_background)

    def validar_atual_config(self):
        data = data_atual()
        data = datetime.strptime(data, "%d-%m-%Y")
        if os.path.isfile(f"{self.nomes['diretorio_config']}\\{self.nomes['arquivo_config_default']}.conf"):
            try:
                config = configparser.ConfigParser()
                config.read(f"{self.nomes['diretorio_config']}\\{self.nomes['arquivo_config_default']}.conf")
                self.infos_config_prog["data_ultima_atualizacao"] = ""
                data_ultima_atualizacao = config.get('ConfiguracoesGerais', 'data_ultima_atualizacao')
                data_ultima_atualizacao = datetime.strptime(data_ultima_atualizacao, "%d-%m-%Y")
                if data_ultima_atualizacao != '':
                    if data_ultima_atualizacao < data:
                        self.infos_config_prog["atualizar"] = True
                        self.alterar_ult_busca()
                    else:
                        self.infos_config_prog["atualizar"] = False
                        return
                else:
                    self.infos_config_prog["atualizar"] = True
                    self.alterar_ult_busca()
            except Exception as error:
                self.popup_mensagem(f"Erro ao validar a ultima atualização: {error}")
                self.infos_config_prog["atualizar"] = False
        else:
            self.infos_config_prog["atualizar"] = False
            return

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
            self.popup_mensagem(f"Erro ao acessar arquivo de configuração default {error}")

    def atualizar_config_default(self, config_setado):
        try:
            config = configparser.ConfigParser()
            config.read(f"{self.nomes['diretorio_config']}\\{self.nomes['arquivo_config_default']}.conf")
            config.set('ConfiguracoesGerais', 'config_default', config_setado)
            self.salvar_alteracoes_config(config)
            self.infos_config_prog['config_default'] = config_setado
        except Exception as error:
            self.popup_mensagem(f"Erro ao atualizar o arquivo config: {error}")
            
    def alterar_ult_busca(self):
        data = data_atual()
        try:
            config = configparser.ConfigParser()
            config.read(f"{self.nomes['diretorio_config']}\\{self.nomes['arquivo_config_default']}.conf")
            config.set('ConfiguracoesGerais', 'data_ultima_atualizacao', data)
            self.salvar_alteracoes_config(config)
        except Exception as error:
            self.popup_mensagem(f"Erro ao atualizar a data da ultima atualização: {error}")

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
            self.trocar_tela_menu()
        except Exception as error:
            self.popup_mensagem(f"Erro ao Alterar o background: {error}")

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
            self.trocar_tela_menu()
        except Exception as error:
            self.popup_mensagem(f"Erro ao Alterar o background: {error}")

    def caixa_selecao_de_cor(self, campo):
        color_code = colorchooser.askcolor(title="Escolha uma cor")
        if color_code[1]:
            campo.delete(0, END)
            campo.insert(0, color_code[1])

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

    def salvar_alteracoes_config(self, config):
        try:
            with open(f"{self.nomes['diretorio_config']}\\{self.nomes['arquivo_config_default']}.conf", 'w') as config_file:
                config.write(config_file)
        except Exception as error:
            self.popup_mensagem(f"Erro ao atualizar o arquivo config: {error}")

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

    def input_placeholder(self, linha_label, linha_entry,  coluna, texto, nome_campo):
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
        self.label.grid(row=linha_label, column=coluna, sticky="WS", pady=(10, 0))
        self.entry.grid(row=linha_entry, column=coluna, columnspan=1, sticky="WEN", pady=(0, 10))

    def escrever_titulos(self, app, tela, linha, coluna):
        self.label_restaurar_backup = Label(
            app,
            text=tela,
            font=('Arial', 12, 'bold'),
            bg=self.infos_config_prog["background_color_titulos"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.label_restaurar_backup.grid(row=linha, column=coluna, sticky="NWE")

    def limpar_linha(self, linha, coluna):
        widgets = self.app.grid_slaves(row=linha, column=coluna)
        for widget in widgets:
            widget.destroy()

    def caixa_texto(self, linha_label, linha_texto, coluna, nome):
        self.nome_campo_caixa = Label(
            text=nome,
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.widtexto = Text(
            self.app,
            height=12,
            wrap="word"
        )
        self.nome_campo_caixa.grid(row=linha_label, column=coluna, sticky="WE")
        self.widtexto.grid(row=linha_texto, column=coluna, sticky="WE")
        self.widtexto.config(width=50)
        self.widtexto.config(state="disabled")

    def limpar_caixa_texto(self):
        self.widtexto.config(state="normal")
        self.widtexto.delete(1.0, 'end')
        self.widtexto.config(state="disabled")

    def escrever_no_input(self, texto):
        self.widtexto.config(state="normal")
        self.widtexto.insert(END, str(texto) + '\n')
        self.widtexto.see(END)
        self.widtexto.config(state="disabled")

    def popup_mensagem(self, mensagem):
        msg = Tk()
        msg.geometry(f"{self.largura}x200+{self.metade_wid}+{self.metade_hei}")
        msg.configure(bg=self.infos_config_prog["background_color_fundo"])
        msg.grid_rowconfigure(0, weight=1)
        msg.grid_columnconfigure(0, weight=1)
        msg.config(padx=10, pady=10)
        msg.title("MSS - " + self.version + " - ALERTA")
        label_mensagem = Label(
            msg,
            text=mensagem,
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

    def texto_config_selecionado(self, app):
        tela = f"Ultimo Config: {self.infos_config_prog['config_default']}"
        self.label_config_selecionado = Label(
            app,
            text=tela,
            font=('Arial', 12),
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.label_config_selecionado.grid(row=0, column=0, columnspan=3, sticky="WN", padx=2, pady=2)

    def buscar_versions(self):
        self.button_atualizacao_inicio.config(state='disabled')
        self.button_atualizacao_voltar.config(state='disabled')
        self.button_menu_sair.config(state='disabled')
        tam_base_muro = len(self.infos_config['bases_muro'])
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Rotina - Validar atualização")

        self.escrever_arquivo_log(self.nomes['arquivo_validar'], f"INFO - Inicio da validação do banco update ")
        self.escrever_no_input(f"\n- Iniciando consulta no banco update")
        for num in range(tam_base_muro):
            database_update = self.valida_banco_update(num)


            try:
                cnxnrp = pyodbc.connect(
                    f"DRIVER=SQL Server;SERVER={self.infos_config['server']};DATABASE={database_update};ENCRYPT=not;UID={self.infos_config['username']};PWD={self.infos_config['password']}")
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
        self.button_atualizacao_inicio.config(state='active')
        self.button_atualizacao_voltar.config(state='active')
        self.button_menu_sair.config(state='active')

    def manipular_banco_muro(self):
        self.entry.config(state='disabled')
        self.button_busca_inicio.config(state='disabled')
        self.button_busca_voltar.config(state='disabled')
        self.button_menu_sair.config(state='disabled')
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Rotina - Buscar Bancos")
        lista_string_instancia = ''
        cursor1 = ''
        status_consulta = False

        self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], "INFO - Inicio da operação Busca muro ")

        versao_databases = self.entry.get()

        if versao_databases == '' or versao_databases == self.placeholder_text:
            self.escrever_no_input(f"-O campo Version não pode estar em branco")
            self.button_busca_inicio.config(state='active')
            self.button_busca_voltar.config(state='active')
            self.entry.config(state='normal')
            self.button_menu_sair.config(state='active')
            return
        else:
            self.escrever_no_input(f"- Version para downgrade: {versao_databases}")
            self.escrever_arquivo_log(
                self.nomes['arquivo_busca_bancos'], "INFO - Version para downgrade: {versao_databases} ")

            # Pegar a lista de bancos da instancia
            self.escrever_arquivo_log(
                self.nomes['arquivo_busca_bancos'], f"INFO - Iniciando a busca dos bancos na instância: {self.infos_config['server']} ")

            try:
                cnxn1 = pyodbc.connect(
                    f"DRIVER=SQL Server;SERVER={self.infos_config['server']};ENCRYPT=not;UID={self.infos_config['username']};PWD={self.infos_config['password']}")
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
                for num in range(len(self.infos_config['bases_muro'])):

                    self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"INFO - Iniciando o processo no banco: {self.infos_config['bases_muro'][num]} ")

                    # Configurando as Variáveis
                    lista_connection_string = []
                    lista_banco_instancia = []
                    lista_nome_banco = []
                    lista_id_banco = []
                    guarda_string_cs = []
                    guarda_id_cs = []
                    guarda_banco_instancia = []
                    guarda_string_bm = []
                    index_banco = []
                    separa_string = []
                    string_limpa = []
                    connection_string = []
                    database_id = []

                    # Pega a lista de connections strings
                    try:
                        cursor1.execute(
                            f"SELECT [DATABASE_ID],[CONNECTION_STRING] FROM {self.infos_config['bases_muro'][num]}.[dbo].[KAIROS_DATABASES]")
                        lista_connection_string = cursor1.fetchall()

                    except (Exception or pyodbc.DatabaseError) as err:
                        self.escrever_no_input(f"- Falha ao tentar consultar banco de muro: {err}")
                        self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"ERRO - Falha ao tentar consultar banco de muro {err} ")
                    else:
                        cursor1.commit()

                        self.escrever_no_input(f"\n- Quantidade de registros encontrados: {len(lista_connection_string)}")
                        self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"INFO - Quantidade de registros encontrados: {len(lista_connection_string)} ")

                    # separar o nome do banco nas connection strings
                    for i in range(len(lista_connection_string)):
                        guarda_string_cs.append(lista_connection_string[i].CONNECTION_STRING)
                        string_separada = guarda_string_cs[i].split(";")
                        catalog = string_separada[1]
                        nome_banco = catalog.split("=")[1]
                        lista_nome_banco.append(nome_banco)
                        continue

                    # separar o id do banco nas connection strings
                    for cs in range(len(lista_connection_string)):
                        guarda_id_cs.append(str(lista_connection_string[cs].DATABASE_ID))
                        lista_id_banco.append(guarda_id_cs[cs])
                        continue

                    # separar o nome do banco nas instancias
                    for ins in range(len(lista_string_instancia)):
                        guarda_banco_instancia.append(str(lista_string_instancia[ins]).split("'")[1])
                        nome_banco_instancia = guarda_banco_instancia[ins]
                        lista_banco_instancia.append(nome_banco_instancia)
                        continue

                    # Comparar bancos "strings"
                    self.escrever_arquivo_log(
                        self.nomes['arquivo_busca_bancos'], f"INFO - Iniciando a comparação dos bancos ")
                    for comparar in range(len(lista_banco_instancia)):
                        if lista_banco_instancia[comparar] in lista_nome_banco:
                            index_banco.append(lista_nome_banco.index(lista_banco_instancia[comparar]))
                            index_banco.sort()
                        continue

                    for nums in range(len(index_banco)):
                        connection_string.append(lista_connection_string[index_banco[nums]])
                        database_id.append(lista_id_banco[index_banco[nums]])

                    if len(connection_string) > 0:
                        self.escrever_no_input("- Quantidade de bancos que deram Match: " + str(len(connection_string)))
                        self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"INFO - Quantidade de bancos que deram Match: {len(connection_string)} ")
                    else:
                        self.escrever_no_input("- Não foram encontrados Match na comparação de bancos")
                        self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"INFO - Não foram encontrados Match na comparação de bancos ")

                    # Limpar as strings para inserir no banco
                    for lim in range(len(connection_string)):
                        guarda_string_bm.append(str(connection_string[lim].CONNECTION_STRING))
                        string = guarda_string_bm[lim]
                        string_limpa.append(string)
                        continue

                    database_update = self.valida_banco_update(num)
                    if len(string_limpa) > 0:
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
                            self.escrever_no_input(f"- banco {database_update} zerado")
                            self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"INFO - Banco {database_update} zerado com sucesso ")
                    else:
                        self.escrever_no_input("- Não foi realizada a limpeza no banco: " + database_update)
                        self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"INFO - Não foi realizada a limpeza no banco: {database_update} ")

                    # Inserindo as connections strings no banco muro update
                    self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"INFO - Iniciando o processo de inserção:  {database_update} ")
                    if len(string_limpa) > 0:
                        try:
                            cnxn1 = pyodbc.connect(
                                f"DRIVER=SQL Server;SERVER={self.infos_config['server']};DATABASE={database_update};ENCRYPT=not;UID={self.infos_config['username']};PWD={self.infos_config['password']}")
                            cursor1 = cnxn1.cursor()

                            cursor1.execute("set identity_insert [dbo].[KAIROS_DATABASES]  on")
                            for incs in range(len(string_limpa)):
                                montar_comando = f"INSERT INTO [{database_update}].[dbo].[KAIROS_DATABASES] ([DATABASE_ID],[CONNECTION_STRING] ,[DATABASE_VERSION] ,[FL_MAQUINA_CALCULO] ,[FL_ATIVO]) VALUES({database_id[incs]},'{string_limpa[incs]}',{versao_databases},0, 1)"
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

                            # Logando as connection string
                            quant = 1
                            self.escrever_arquivo_log(self.nomes['arquivo_connection_strings'], f"INFO - Buscar Bancos - Listando as connection strings utilizadas ")
                            self.escrever_arquivo_log(self.nomes['arquivo_connection_strings'], f"INFO - Buscar Bancos - Ambiente: {self.infos_config['bases_muro'][num]} ")
                            for log in range(len(connection_string)):
                                self.escrever_arquivo_log(self.nomes['arquivo_connection_strings'], f"INFO - {quant} - {connection_string[log]} ")
                                quant += 1
                                continue

                            self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"INFO - Listado as Connection Strings no arquivo: {self.nomes['arquivo_connection_strings']} ")

                    else:
                        self.escrever_no_input("- Não a registros para serem inseridos no banco: " + database_update)
                        self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"INFO - Não a registros para serem inseridos no banco: {database_update} ")
                    if num < 4:
                        num += 1
                    self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"INFO - Concluído a parte {num}, de um total de {len(self.infos_config['bases_muro'])}. ")
                    continue
                cursor1.close()
            else:
                self.escrever_no_input(f"- Erro na primeira etapa das buscas, o processo foi interrompido.")
                self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"INFO - Erro na primeira etapa das buscas, o processo foi interrompido. ")

            self.escrever_no_input(f"\n- Fim da operação Busca muro")
            self.escrever_arquivo_log(self.nomes['arquivo_busca_bancos'], f"INFO - Fim da operação Busca muro")
            self.entry.config(state='normal')
            self.button_busca_inicio.config(state='active')
            self.button_busca_voltar.config(state='active')
            self.button_menu_sair.config(state='active')

    def replicar_version(self):
        self.button_replicar_inicio.config(state='disabled')
        self.button_replicar_voltar.config(state='disabled')
        self.button_menu_sair.config(state='disabled')
        tam_base_muro = len(self.infos_config['bases_muro'])
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Rotina - Replicar version ")

        self.escrever_arquivo_log(self.nomes['arquivo_replicar_version'], f"INFO - Inicio da operação replicar version")

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
                    f"DRIVER=SQL Server;SERVER={self.infos_config['server']};DATABASE={database_update};ENCRYPT=not;UID={self.infos_config['username']};PWD={self.infos_config['password']}")
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
                        f"DRIVER=SQL Server;SERVER={self.infos_config['server']};DATABASE={self.infos_config['bases_muro'][num]};ENCRYPT=not;UID={self.infos_config['username']};PWD={self.infos_config['password']}")
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
                        self.escrever_arquivo_log(self.nomes['arquivo_connection_strings'], f"\n{data_hora_atual()} - INFO - {quant} - ID: {lista_ids[log]} - Version: {lista_versions[log]} ")
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
        self.button_replicar_inicio.config(state='active')
        self.button_replicar_voltar.config(state='active')
        self.button_menu_sair.config(state='active')

    def valida_banco_update(self, num):
        database_update = ''
        muro = self.infos_config['bases_muro'][num]
        while True:
            match muro:
                case 'qcmaint_kairos_base_muro':
                    if self.infos_config['database_update_br'] != '':
                        database_update = self.infos_config['database_update_br']
                        return database_update
                    else:
                        self.escrever_no_input(
                            "- Não foi inserido no arquivo de config o apontamento para o banco Muro update BR")
                case 'qcdev_kairos_base_muro':
                    if self.infos_config['database_update_br'] != '':
                        database_update = self.infos_config['database_update_br']
                        return database_update
                    else:
                        self.escrever_no_input(
                            "- Não foi inserido no arquivo de config o apontamento para o banco Muro update BR")
                case "qcmaint_kairos_base_muro_mx":
                    if self.infos_config['database_update_mx'] != '':
                        database_update = self.infos_config['database_update_mx']
                        return database_update
                    else:
                        self.escrever_no_input(
                            "-  Não foi inserido no arquivo de config o apontamento para o banco Muro update MX")
                case "qcdev_kairos_base_muro_mx":
                    if self.infos_config['database_update_mx'] != '':
                        database_update = self.infos_config['database_update_mx']
                        return database_update
                    else:
                        self.escrever_no_input(
                            "-  Não foi inserido no arquivo de config o apontamento para o banco Muro update MX")
                case "qcmaint_kairos_base_muro_pt":
                    if self.infos_config['database_update_pt'] != '':
                        database_update = self.infos_config['database_update_pt']
                        return database_update
                    else:
                        self.escrever_no_input(
                            "- Não foi inserido no arquivo de config o apontamento para o banco Muro update PT")
                case "qcdev_kairos_base_muro_pt":
                    if self.infos_config['database_update_pt'] != '':
                        database_update = self.infos_config['database_update_pt']
                        return database_update
                    else:
                        self.escrever_no_input(
                            "- Não foi inserido no arquivo de config o apontamento para o banco Muro update PT")
                case "qcmaint_mdcomune_base_muro":
                    if self.infos_config['database_update_md'] != '':
                        database_update = self.infos_config['database_update_md']
                        return database_update
                    else:
                        self.escrever_no_input(
                            "- Não foi inserido no arquivo de config o apontamento para o banco Muro update MD")
                case "qcdev_mdcomune_base_muro":
                    if self.infos_config['database_update_md'] != '':
                        database_update = self.infos_config['database_update_md']
                        return database_update
                    else:
                        self.escrever_no_input(
                            "- Não foi inserido no arquivo de config o apontamento para o banco Muro update MD")
                case _:
                    self.escrever_no_input("- Não foi possível achar uma opção compativel com o banco de muro")
            return database_update

    def escolher_config_existente(self):
        params_dict = ''
        self.infos_config['status'] = False

        if self.infos_config_prog['escolha_manual']:
            self.config_selecionado = self.combobox.get()
        elif self.infos_config_prog['escolha_manual'] is False and self.infos_config_prog['config_default'] != "":
            self.config_selecionado = self.infos_config_prog['config_default']
        else:
            self.popup_mensagem(f"Erro na validação do arquivo config: {self.infos_config_prog['escolha_manual']} e {self.infos_config_prog['config_default']}")

        # Validando o arquivo de config
        try:
            if os.path.isfile(f"{self.nomes['diretorio_config']}\\{self.config_selecionado}"):
                config_bjt = open(f"{self.nomes['diretorio_config']}\\{self.config_selecionado}", "r")
                config_json = config_bjt.read().lower()
                params_dict = json.loads(config_json)
            else:
                self.popup_mensagem(
                    f"Não foi possível encontrar um .JSON com esse nome na pasta {self.nomes['diretorio_config']}!")
        except Exception as name_error:
            self.popup_mensagem(f"Existem erros de formatação no arquivo de config escolhido:\n {name_error}")
            self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente: {name_error} ")
            return
        else:
            try:
                if params_dict['conexao']['server'] == '':
                    self.popup_mensagem("O valor do server não foi especificado no config")
                    self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - O valor do server não foi especificado no config, Informe e tente novamente ")
                    return
                elif params_dict["conexao"]["username"] == '':
                    self.popup_mensagem("O valor do Username não foi especificado no config")
                    self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - O valor do Username não foi especificado no config, Informe e tente novamente ")
                    return
                elif params_dict["conexao"]["password"] == '':
                    self.popup_mensagem("O valor do Password não foi especificado no config")
                    self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - O valor do Password não foi especificado no config, Informe e tente novamente ")
                    return
                elif not params_dict["bases_muro"]:
                    self.popup_mensagem("O valor do Base_Muro não foi especificado no config")
                    self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - O valor do Base_Muro não foi especificado no config, Informe e tente novamente ")
                    return
            except Exception as name_error:
                self.popup_mensagem(f"Existem erros de formatação no arquivo de config escolhido:\n {name_error}")
                self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente: {name_error} ")
            else:
                try:
                    # Carregar config
                    self.infos_config['server'] = params_dict["conexao"]["server"]
                    self.infos_config['username'] = params_dict["conexao"]["username"]
                    self.infos_config['password'] = params_dict["conexao"]["password"]
                    self.infos_config['database_update_br'] = params_dict["database_update_br"]
                    self.infos_config['database_update_mx'] = params_dict["database_update_mx"]
                    self.infos_config['database_update_pt'] = params_dict["database_update_pt"]
                    self.infos_config['database_update_md'] = params_dict["database_update_md"]
                    self.infos_config['bases_muro'] = params_dict["bases_muro"]
                except Exception as name_error:
                    self.popup_mensagem(f"Existem erros de formatação no arquivo de config escolhido:\n {name_error}")
                    self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente: {name_error} ")
                else:
                    self.infos_config['status'] = True
                    # Limpando strings vazias na base muro
                    limpa_muro_tam = len(self.infos_config['bases_muro'])
                    for num in range(0, limpa_muro_tam, +1):
                        if '' in self.infos_config['bases_muro']:
                            self.infos_config['bases_muro'].remove('')
                            continue
                        else:
                            break
                    try:
                        self.infos_config['server_principal'] = (
                            params_dict)["configs_restaurar_download"]["server_principal"]
                        self.infos_config['username_principal'] = (
                            params_dict)["configs_restaurar_download"]["username_principal"]
                        self.infos_config['password_principal'] = (
                            params_dict)["configs_restaurar_download"]["password_principal"]
                    except Exception as name_error:
                        self.popup_mensagem(f"O config esta estava desatualizado, foram inseridas as novas tags no config:\n {name_error}")
                        self.escrever_arquivo_log(
                            self.nomes['arquivo_base_muro'], f"INFO - O config esta estava desatualizado, foram inseridas as novas tags no config, configure elas para usar as rotinas {self.nomes['arquivo_download_backup']} e {self.nomes['arquivo_restaurar_banco']}: {name_error}")
                        self.infos_config['server_principal'] = ""
                        self.infos_config['username_principal'] = ""
                        self.infos_config['password_principal'] = ""
                        bases_utilizadas = str(f"{self.infos_config['bases_muro']}")
                        bases_utilizadas = bases_utilizadas.replace("'", '"')
                        server_utilizado = self.infos_config['server']
                        if "\\" in server_utilizado:
                            server_utilizado = server_utilizado.replace('\\', '\\\\')
                        config_atualizado = f"""{{
    "database_update_br": "{self.infos_config['database_update_br']}",
    "database_update_mx": "{self.infos_config['database_update_mx']}",
    "database_update_pt": "{self.infos_config['database_update_pt']}",
    "database_update_md": "{self.infos_config['database_update_md']}",
    "bases_muro": {bases_utilizadas},
    "conexao": {{
        "server": "{server_utilizado}",
        "username": "{self.infos_config['username']}",
        "password": "{self.infos_config['password']}"
    }},
    "configs_restaurar_download": {{
        "server_principal": "",
        "username_principal": "",
        "password_principal": ""
    }}
}}"""
                        self.escrever_arquivo_config(self.config_selecionado, config_atualizado, "json")
        try:
            self.infos_config['redis_qa'] = params_dict["redis_qa"]
        except Exception as name_error:
            self.popup_mensagem(
                f"O config esta estava desatualizado, foram inseridas as novas tags no config:\n {name_error}")
            self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - O config esta estava desatualizado, foram inseridas as novas tags no config, configure elas para usar as rotinas {self.nomes['arquivo_download_backup']} e {self.nomes['arquivo_restaurar_banco']}: {name_error}")
            self.infos_config['redis_qa'] = ""
            bases_utilizadas = str(f"{self.infos_config['bases_muro']}")
            bases_utilizadas = bases_utilizadas.replace("'", '"')
            server_utilizado = self.infos_config['server']
            if "\\" in server_utilizado:
                server_utilizado = server_utilizado.replace('\\', '\\\\')
            config_atualizado = f"""{{
    "database_update_br": "{self.infos_config['database_update_br']}",
    "database_update_mx": "{self.infos_config['database_update_mx']}",
    "database_update_pt": "{self.infos_config['database_update_pt']}",
    "database_update_md": "{self.infos_config['database_update_md']}",
    "bases_muro": {bases_utilizadas},
    "conexao": {{
        "server": "{server_utilizado}",
        "username": "{self.infos_config['username']}",
        "password": "{self.infos_config['password']}"
    }},
    "configs_restaurar_download": {{
        "server_principal": "{self.infos_config['server_principal']}",
        "username_principal": "{self.infos_config['username_principal']}",
        "password_principal": "{self.infos_config['password_principal']}"
    }},
    "redis_qa": [
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
}}"""
            self.escrever_arquivo_log(self.config_selecionado, config_atualizado)
        if self.infos_config['status']:
            self.atualizar_config_default(self.config_selecionado)
            self.trocar_tela_menu()
        else:
            self.trocar_tela_config()

        return self.infos_config

    def inserir_campos_arquivo_existente(self, app, coluna):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Rotina - Escolher Arquivo Existente")
        opcoes = []

        # listar os arquivos de dentro da pasta
        try:
            arquivos_diretorio = os.listdir(self.nomes['pasta_config'])
        except Exception as name_error:
            self.popup_mensagem(f"Não foi possivel acessar a pasta config: {name_error}")
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
                        self.popup_mensagem(f"Não existe arquivos .json na pasta config")
                        return
                else:
                    self.popup_mensagem(f"Não existe arquivos na pasta config")
                    return

        self.button_config_existente.config(state="disabled")
        self.button_config_novo.config(state="active", fg=self.infos_config_prog["background_color_fonte"])
        self.limpar_linha(5, 1)
        self.limpar_linha(6, 1)
        self.limpar_linha(7, 1)
        self.limpar_linha(10, 2)
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
        self.label_lista_arquivos.grid(row=5, column=coluna, pady=(10, 0), sticky="WS")
        self.combobox.grid(row=6, column=coluna, pady=(0, 10), sticky="WEN")
        self.button_nav_escolher.grid(row=10, column=1, padx=5, pady=5, columnspan=2, sticky="ES")

    def criar_config(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Rotina - Criação de config ")
        nome_escolhido = self.entry.get()
        if nome_escolhido == self.placeholder_text or nome_escolhido == "":
            self.popup_mensagem("O campo nome deverá ser preenchido")
            return
        else:

            nome_config = nome_escolhido + ".json"

            if os.path.exists(f"{self.nomes['diretorio_config']}\\{nome_config}"):
                self.popup_mensagem(
                    "Já existe um arquivo .json com o mesmo nome\nInforme outro nome para o arquivo config")
            else:
                arquivo_config = ("""{{
    "database_update_br": "",
    "database_update_mx": "",
    "database_update_pt": "",
    "database_update_md": "",
    "bases_muro": [],
    "conexao": {{
        "server": "",
        "username": "",
        "password": ""
    }},
    "configs_restaurar_download": {{
        "server_principal": "",
        "username_principal": "",
        "password_principal": ""
    }},
    "redis_qa": [
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
}}""")
                self.escrever_arquivo_config(nome_config, arquivo_config, "json")
                self.popup_mensagem("Novo config criado com sucesso")
                self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Novo config criado com sucesso, configure e selecione para ser utilizado {nome_config}")

    def inserir_campos_arquivo_novo(self, app, coluna):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Rotina - Criar Arquivo config")
        self.button_config_novo.config(state="disabled")
        self.button_config_existente.config(state="active", fg=self.infos_config_prog["background_color_fonte"])
        self.limpar_linha(5, 1)
        self.limpar_linha(6, 1)
        self.limpar_linha(7, 1)
        self.limpar_linha(10, 2)

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
        self.input_placeholder(5, 6,  coluna, "Insira o nome para o arquivo...", "Nome do arquivo:")
        self.button_nav_criar.grid(row=10, column=1, padx=5, pady=5, columnspan=2, sticky="ES")

    def restaurar_banco(self):
        self.button_restaurar_inicio.config(state='disabled')
        self.button_restaurar_voltar.config(state='disabled')
        self.entry.config(state='disabled')
        self.button_menu_sair.config(state='disabled')
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Rotina - Restaurar Backup")
        cnxnrs = ''
        cursorrs = ''

        nome_banco_restaurado = self.entry.get()

        if nome_banco_restaurado == self.placeholder_text or nome_banco_restaurado == "":
            self.escrever_no_input("- O campo acima deverá ser preenchido")
            self.button_restaurar_inicio.config(state='active')
            self.button_restaurar_voltar.config(state='active')
            self.entry.config(state='normal')
            self.button_menu_sair.config(state='active')
            return
        else:
            self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"INFO - Inserido o nome do banco apresentado no discord: {nome_banco_restaurado} ")
            self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"INFO - Escolhido o servidor: {self.infos_config['server']} ")

            comando_criar_device = f"""USE [master];
EXEC Sp_addumpdevice'disk','{nome_banco_restaurado}','G:\\Backup\\Eventual\\{nome_banco_restaurado}.bak';"""

            comando_restaurar_banco = f"""
RESTORE DATABASE "{nome_banco_restaurado}" FROM DISK =
'G:\\Backup\\Eventual\\{nome_banco_restaurado}.bak'

WITH norecovery, stats = 1, move '{nome_banco_restaurado}_log' TO
'E:\\DBDATA\\LOG\\{nome_banco_restaurado}_log.ldf',

move '{nome_banco_restaurado}' TO
'D:\\DBDATA\\DATA\\{nome_banco_restaurado}.mdf'
"""
            comando_ativar_banco = f"""
RESTORE DATABASE "{nome_banco_restaurado}" WITH recovery

ALTER DATABASE "{nome_banco_restaurado}" SET recovery simple
"""
            comando_excluir_device = f"""
EXEC Sp_dropdevice
'{nome_banco_restaurado}';
"""
            comando_checar_banco = f"""
DBCC CHECKDB('{nome_banco_restaurado}')
"""
            comando_primeiro_script = f"""
use [{nome_banco_restaurado}]
EXEC sp_addrolemember N'db_owner',  N'userNewPoint'
EXEC sp_change_users_login 'Update_One', 'userNewPoint',
'userNewPoint'
EXEC sp_addrolemember N'db_owner',  N'newPoint'
EXEC sp_change_users_login 'Update_One', 'newPoint', 'newPoint'
"""
            comando_segundo_script = f"""
USE [master];  
--alterar o banco 
SET NOCOUNT ON
ALTER DATABASE [{nome_banco_restaurado}] SET COMPATIBILITY_LEVEL = 140; 
"""
            status_etapa1 = False

            try:
                cnxnrs = pyodbc.connect(
                    f"DRIVER=SQL Server;SERVER={self.infos_config['server_principal']};ENCRYPT=not;UID={self.infos_config['username_principal']};PWD={self.infos_config['password_principal']}")
                cnxnrs.timeout = 12
                cursorrs = cnxnrs.cursor()
                cursorrs.execute(comando_criar_device)
                result_criar_device = cursorrs.messages
            except (Exception or pyodbc.DatabaseError) as err:
                self.escrever_no_input(
                    "- Falha ao tentar executar o comando de criação de device de backup " + str(err))
                self.escrever_arquivo_log(
                    self.nomes['arquivo_restaurar_banco'], f"ERRO - Falha ao tentar executar o comando de criação de device de backup: {err} ")
            else:
                cursorrs.commit()
                self.escrever_no_input(f"- Sucesso ao realizar Criar Device de Backup")
                self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"INFO - Sucesso ao realizar Criar Device de Backup ")
                status_etapa1 = True
                for incs in range(len(result_criar_device)):
                    separados = result_criar_device[0][1].split("]")
                    mensagem = separados[3]
                    self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"INFO - Comando(Criação Device) -  Mensagem SQL: {mensagem} ")

            if status_etapa1:
                try:
                    cursorrs = cnxnrs.cursor()
                    cursorrs.execute(comando_restaurar_banco)
                except (Exception or pyodbc.DatabaseError) as err:
                    self.escrever_no_input("- Falha ao tentar executar o comando de restauração de banco: " + str(err))
                    self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"ERRO - Falha ao tentar executar o comando de restauração de banco: {err} ")
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
                    cursorrs.commit()
                    self.escrever_no_input(f"- Sucesso ao realizar a restauração do banco")
                    self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"INFO - Sucesso ao realizar a restauração do banco ")

                    tam = len(mensagens) - 3
                    for incs in range(posicao):
                        self.escrever_no_input(f"- Comando(Restauração DB) -  Mensagem SQL: {mensagens[tam]}  ")
                        self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"INFO - Comando(Restauração DB) -  Mensagem SQL: {mensagens[tam]} ")
                        tam += 1

                    try:
                        cursorrs.execute(comando_ativar_banco)
                        result_ativar_banco = cursorrs.messages
                    except (Exception or pyodbc.DatabaseError) as err:
                        self.escrever_no_input("- Falha ao tentar executar o comando de Ativação do banco: " + str(err))
                        self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"ERRO - Falha ao tentar executar o comando de Ativação do banco: {err} ")
                    else:
                        tam_result = len(result_ativar_banco) - 1
                        while tam_result < len(result_ativar_banco):
                            separados = result_ativar_banco[tam_result][1].split("]")
                            mensagem = separados[3]
                            self.escrever_no_input(f"- Comando(Ativação DB) -  Mensagem SQL: {mensagem}  ")
                            self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"INFO - Comando(Ativação DB) -  Mensagem SQL: {mensagem} ")
                            tam_result += 1

                        try:
                            cursorrs.execute(comando_checar_banco)
                            result_check = cursorrs.messages
                        except (Exception or pyodbc.DatabaseError) as err:
                            self.escrever_no_input(
                                "- Falha ao tentar executar o comando de checagem do banco: " + str(err))
                            self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"ERRO - Falha ao tentar executar o comando de checagem do banco: {err} ")
                        else:
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
                                cursorrs.execute(comando_excluir_device)
                                result_excluir_device = cursorrs.messages
                            except (Exception or pyodbc.DatabaseError) as err:
                                self.escrever_no_input(
                                    "- Falha ao tentar executar o comando de checagem do banco: " + str(err))
                                self.escrever_arquivo_log(
                                    self.nomes['arquivo_restaurar_banco'], f"ERRO - Falha ao tentar executar o comando de checagem do banco: {err} ")
                            else:
                                for incs in range(len(result_excluir_device)):
                                    separados = result_excluir_device[0][1].split("]")
                                    mensagem = separados[3]
                                    self.escrever_no_input(f"- Comando(Exclusão Device) -  Mensagem SQL: {mensagem}  ")
                                    self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"INFO - Comando(Exclusão Device) -  Mensagem SQL: {mensagem} ")

                                try:
                                    cursorrs.execute(comando_primeiro_script)
                                    associar_owner = cursorrs.messages
                                except (Exception or pyodbc.DatabaseError) as err:
                                    self.escrever_no_input(
                                        "- Falha ao tentar executar o comando de associação do Owner: " + str(err))
                                    self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"ERRO - Falha ao tentar executar o comando de associação do Owner:  {err} ")
                                else:
                                    separados = associar_owner[0][1].split("]")
                                    mensagem = separados[3]
                                    self.escrever_no_input(f"- Comando(Associar Owner) - Mensagem SQL: {mensagem}")
                                    self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"INFO - Comando(Script Associar Owner) - Mensagem SQL: {mensagem} ")

                                    try:
                                        cursorrs.execute(comando_segundo_script)
                                        compatibilidade = cursorrs.messages
                                    except (Exception or pyodbc.DatabaseError) as err:
                                        self.escrever_no_input("- Falha ao tentar executar o comando " + str(err))
                                        self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"ERRO - Falha ao tentar executar o comando: {err} ")
                                    else:
                                        separados = compatibilidade[0][1].split("]")
                                        mensagem = separados[3]
                                        self.escrever_no_input(f"- Comando(Compatibilidade) - Mensagem SQL: {mensagem}")
                                        self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"INFO - Comando(Script Compatibilidade) - Mensagem SQL: {mensagem} ")
                cursorrs.close()

        self.escrever_no_input("- Processo finalizado")
        self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"INFO - Processo finalizado")
        self.entry.config(state='normal')
        self.button_restaurar_inicio.config(state='active')
        self.button_restaurar_voltar.config(state='active')
        self.button_menu_sair.config(state='active')

    def download_backup(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Rotina - Download Backup ")
        self.button_download_inicio.config(state='disabled')
        self.button_download_voltar.config(state='disabled')
        self.button_menu_sair.config(state='disabled')

        self.entry.config(state='disabled')
        self.escrever_arquivo_log(self.nomes['arquivo_download_backup'],
                                  f"INFO - Inicio da operação Download Backup ")
        endereco_download = self.entry.get()
        self.escrever_arquivo_log(self.nomes['arquivo_download_backup'],
                                  f"INFO - Inserida a URL de Download: {endereco_download} ")

        if endereco_download == self.placeholder_text or endereco_download == "":
            self.escrever_no_input("- O campo acima deverá ser preenchido")
            self.button_download_inicio.config(state='active')
            self.button_download_voltar.config(state='active')
            self.entry.config(state='normal')
            self.button_menu_sair.config(state='active')
            return
        else:
            comando = f"""xp_cmdshell 'powershell.exe -file C:\\wget\\download.ps1 bkp "{endereco_download}"'"""

            try:
                cnxnrp1 = pyodbc.connect(
                    f"DRIVER=SQL Server;SERVER={self.infos_config['server_principal']};ENCRYPT=not;UID={self.infos_config['username_principal']};PWD={self.infos_config['password_principal']}")
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
        self.entry.config(state='normal')
        self.button_download_inicio.config(state='active')
        self.button_download_voltar.config(state='active')
        self.button_menu_sair.config(state='active')

    def limpar_todos_redis(self):
        self.button_atualizacao_inicio.config(state='disabled')
        self.button_atualizacao_voltar.config(state='disabled')
        self.button_menu_sair.config(state='disabled')
        self.escrever_arquivo_log(self.nomes['arquivo_redis'], f"INFO - Inicio da operação Limpar todos Redis ")
        for red_atual in self.infos_config['redis_qa']:
            self.escrever_no_input(
                f"- Iniciado processo no Redis {red_atual['nome_redis']}")
            self.escrever_arquivo_log(self.nomes['arquivo_redis'],
                                      f"INFO - Iniciado processo no Redis {red_atual['nome_redis']} ")
            redis_host = red_atual['ip']  # ou o endereço do seu servidor Redis
            redis_port = red_atual['port']  # ou a porta que o seu servidor Redis está ouvindo

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
        self.escrever_no_input("- Processo finalizado")
        self.escrever_arquivo_log(self.nomes['arquivo_redis'], f"INFO - Processo finalizado ")
        self.button_atualizacao_inicio.config(state='active')
        self.button_atualizacao_voltar.config(state='active')
        self.button_menu_sair.config(state='active')

    def limpar_redis_especifico(self):
        self.combobox.config(state='disabled')
        self.button_redis_inicio.config(state='disabled')
        self.button_redis_voltar.config(state='disabled')
        self.button_menu_sair.config(state='disabled')
        self.escrever_arquivo_log(self.nomes['arquivo_redis'], f"INFO - Inicio da operação Limpar Redis especifico")
        redis_selecionado = self.combobox.get()
        self.escrever_no_input(f"- Iniciado processo no Redis {redis_selecionado}")
        self.escrever_arquivo_log(
            self.nomes['arquivo_redis'], f"INFO - Iniciado processo no Redis {redis_selecionado} ")
        todos_valores_redis = self.infos_config["redis_qa"]
        for redis_unico in todos_valores_redis:
            if redis_unico["nome_redis"] == redis_selecionado:
                self.redis_certo = redis_unico
        redis_host = self.redis_certo["ip"]
        redis_port = self.redis_certo["port"]

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
        self.button_redis_inicio.config(state='active')
        self.button_redis_voltar.config(state='active')
        self.combobox.config(state='active')
        self.button_menu_sair.config(state='active')

    def validador_nif(self, documento_inserido):
        self.combobox.config(state='disabled')
        self.entry.config(state='disabled')
        self.button_gerador_inicio.config(state='disabled')
        self.button_gerador_voltar.config(state='disabled')
        self.button_menu_sair.config(state='disabled')
        self.button_gerador_limpar.config(state='disabled')
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Rotina - Gerador NIF")
        lista_sem_mascara = self.limpar_string(documento_inserido)
        for doc in lista_sem_mascara:
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

            etapa1_nif = math.floor(fase3/11)
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


        self.combobox.config(state='active')
        self.entry.config(state='normal')
        self.button_gerador_inicio.config(state='active')
        self.button_gerador_voltar.config(state='active')
        self.button_menu_sair.config(state='active')
        self.button_gerador_limpar.config(state='active')

    def validador_cnpj(self, documento_inserido):
        self.combobox.config(state='disabled')
        self.entry.config(state='disabled')
        self.button_gerador_inicio.config(state='disabled')
        self.button_gerador_voltar.config(state='disabled')
        self.button_menu_sair.config(state='disabled')
        self.button_gerador_limpar.config(state='disabled')
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Rotina - Gerador CNPJ")
        lista_sem_mascara = self.limpar_string(documento_inserido)
        for doc in lista_sem_mascara:
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

            etapa1_cnpj = math.floor(fase3/11)
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

            etapa4_cnpj = math.floor(fase5/11)
            etapa5_cnpj = math.floor(etapa4_cnpj*11)
            etapa6_cnpj = math.floor(fase5 - etapa5_cnpj)
            dig2_cnpj = 0 if 11 - etapa6_cnpj > 9 else 11 - etapa6_cnpj

            digitos_gerados = str(dig1_cnpj) + str(dig2_cnpj)

            if int(digitos_gerados) == int(digitos_validadores):
                status_checagem = "Verdadeiro"
            else:
                status_checagem = "Falso"
            self.escrever_no_input(f"- CNPJ - {doc} - {status_checagem}")


        self.combobox.config(state='active')
        self.entry.config(state='normal')
        self.button_gerador_inicio.config(state='active')
        self.button_gerador_voltar.config(state='active')
        self.button_menu_sair.config(state='active')
        self.button_gerador_limpar.config(state='active')

    def validador_cpf(self, documento_inserido):
        self.combobox.config(state='disabled')
        self.entry.config(state='disabled')
        self.button_gerador_inicio.config(state='disabled')
        self.button_gerador_voltar.config(state='disabled')
        self.button_menu_sair.config(state='disabled')
        self.button_gerador_limpar.config(state='disabled')
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Rotina - Gerador CPF")
        lista_sem_mascara = self.limpar_string(documento_inserido)
        for doc in lista_sem_mascara:
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

            etapa1_cpf = math.floor(fase3/11)
            etapa2_cpf = math.floor(etapa1_cpf*11)
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

            etapa4_cpf = math.floor(fase5/11)
            etapa5_cpf = math.floor(etapa4_cpf*11)
            etapa6_cpf = math.floor(fase5 - etapa5_cpf)
            dig2_cpf = 0 if 11 - etapa6_cpf > 9 else 11 - etapa6_cpf

            digitos_gerados = str(dig1_cpf) + str(dig2_cpf)

            if digitos_gerados == digitos_validadores:
                status_checagem = "Verdadeiro"
            else:
                status_checagem = "Falso"
            self.escrever_no_input(f"- CPF - {doc} - {status_checagem}")

        self.combobox.config(state='active')
        self.entry.config(state='normal')
        self.button_gerador_inicio.config(state='active')
        self.button_gerador_voltar.config(state='active')
        self.button_menu_sair.config(state='active')
        self.button_gerador_limpar.config(state='active')

    def validador_cei(self, documento_inserido):
        self.combobox.config(state='disabled')
        self.entry.config(state='disabled')
        self.button_gerador_inicio.config(state='disabled')
        self.button_gerador_voltar.config(state='disabled')
        self.button_menu_sair.config(state='disabled')
        self.button_gerador_limpar.config(state='disabled')
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Rotina - Gerador CEI")
        lista_sem_mascara = self.limpar_string(documento_inserido)
        for doc in lista_sem_mascara:
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

        self.combobox.config(state='active')
        self.entry.config(state='normal')
        self.button_gerador_inicio.config(state='active')
        self.button_gerador_voltar.config(state='active')
        self.button_menu_sair.config(state='active')
        self.button_gerador_limpar.config(state='active')

    def validador_pis(self, documento_inserido):
        self.combobox.config(state='disabled')
        self.entry.config(state='disabled')
        self.button_gerador_inicio.config(state='disabled')
        self.button_gerador_voltar.config(state='disabled')
        self.button_menu_sair.config(state='disabled')
        self.button_gerador_limpar.config(state='disabled')
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Rotina - Gerador PIS")
        lista_sem_mascara = self.limpar_string(documento_inserido)
        for doc in lista_sem_mascara:
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

        self.combobox.config(state='active')
        self.entry.config(state='normal')
        self.button_gerador_inicio.config(state='active')
        self.button_gerador_voltar.config(state='active')
        self.button_menu_sair.config(state='active')
        self.button_gerador_limpar.config(state='active')

    def gerador_nif(self, linhas, checkbox_arquivo):
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
                self.escrever_arquivo_log(self.nomes['arquivo_doc_nif'], lista[0])
        self.combobox.config(state='active')
        self.entry.config(state='normal')
        self.button_gerador_inicio.config(state='active')
        self.button_gerador_voltar.config(state='active')
        self.button_menu_sair.config(state='active')
        self.button_gerador_limpar.config(state='active')
        self.escrever_no_input(f"- Processo finalizado com sucesso")

    def gerador_cnpj(self, linhas, checkbox_mascara, checkbox_arquivo):
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
                self.escrever_arquivo_log(self.nomes['arquivo_doc_cnpj'], lista[0])
        self.combobox.config(state='active')
        self.entry.config(state='normal')
        self.button_gerador_inicio.config(state='active')
        self.button_gerador_voltar.config(state='active')
        self.button_menu_sair.config(state='active')
        self.button_gerador_limpar.config(state='active')
        self.escrever_no_input(f"- Processo finalizado com sucesso")

    def gerador_cpf(self, linhas, checkbox_mascara, checkbox_arquivo):
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
                self.escrever_arquivo_log(self.nomes['arquivo_doc_cpf'], lista[0])
        self.combobox.config(state='active')
        self.entry.config(state='normal')
        self.button_gerador_inicio.config(state='active')
        self.button_gerador_voltar.config(state='active')
        self.button_menu_sair.config(state='active')
        self.button_gerador_limpar.config(state='active')
        self.escrever_no_input(f"- Processo finalizado com sucesso")

    def gerador_cei(self, linhas, checkbox_mascara, checkbox_arquivo):
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
                self.escrever_arquivo_log(self.nomes['arquivo_doc_cei'], lista[0])
        self.combobox.config(state='active')
        self.entry.config(state='normal')
        self.button_gerador_inicio.config(state='active')
        self.button_gerador_voltar.config(state='active')
        self.button_menu_sair.config(state='active')
        self.button_gerador_limpar.config(state='active')
        self.escrever_no_input(f"- Processo finalizado com sucesso")

    def gerador_pis(self, linhas, checkbox_mascara, checkbox_arquivo):
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
                self.escrever_arquivo_log(self.nomes['arquivo_doc_pis'], lista[0])
        self.combobox.config(state='active')
        self.entry.config(state='normal')
        self.button_gerador_inicio.config(state='active')
        self.button_gerador_voltar.config(state='active')
        self.button_menu_sair.config(state='active')
        self.button_gerador_limpar.config(state='active')
        self.escrever_no_input(f"- Processo finalizado com sucesso")

    def menu_gerador_documentos(self):
        selecao_combobox = self.combobox.get()
        quant_insirada = self.entry.get()
        checkbox_mascara = self.valor_checkbox_mascara_num.get()
        checkbox_arquivo = self.valor_checkbox_gerar_arquivo.get()
        tam_quant_insirada = int(len(quant_insirada))
        if quant_insirada.isdigit():
            if quant_insirada != self.placeholder_text and quant_insirada != "":
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
        else:
            self.escrever_no_input(f"- Insira somente digitos na caixa de input")
            self.entry.delete(0, tam_quant_insirada)
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
        self.infos_config['status'] = True
        while True:
            if self.infos_config['status']:
                try:
                    if self.infos_config['server_principal'] != "":
                        self.iniciar_processo_restaurar()
                        break
                    else:
                        self.escrever_no_input(f"- A tag de server_principal parece estar vazia")
                        self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"INFO - A tag de server_principal parece estar vazia, preencha e recarregue o config novamente ")
                        self.infos_config['status'] = False
                except (Exception or pyodbc.DatabaseError) as err:
                    self.escrever_no_input(f"- Falha ao tentar ler o arquivo {err}")
                    self.escrever_arquivo_log(self.nomes['arquivo_restaurar_banco'], f"ERRO - Falha ao tentar ler o arquivo, corrija e tente novamente: {err} ")
                    self.infos_config['status'] = False
            else:
                self.escrever_no_input(f"- Processo finalizado")
                break

    def menu_redis_todos(self):
        self.infos_config['status'] = True
        while True:
            if self.infos_config['status']:
                try:
                    if self.infos_config['redis_qa'][0]["nome_redis"] != "":
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
                    if self.infos_config['redis_qa'][0]["nome_redis"] != "":
                        self.iniciar_processo_limpar_redis_especifico()
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

    def menu_download_backup(self):
        self.infos_config['status'] = True
        while True:
            if self.infos_config['status']:
                try:
                    if self.infos_config['server_principal'] != "":
                        self.iniciar_processo_download()
                        break
                    else:
                        self.escrever_no_input(f"- A tag de server_principal parece estar vazia")
                        self.escrever_arquivo_log(self.nomes['arquivo_download_backup'], f"INFO - A tag de server_principal parece estar vazia, preencha e recarregue o config novamente ")
                        self.infos_config['status'] = False
                except (Exception or pyodbc.DatabaseError) as err:
                    self.escrever_no_input(f"- Falha ao tentar ler o arquivo {err}")
                    self.escrever_arquivo_log(self.nomes['arquivo_download_backup'], f"ERRO - Falha ao tentar ler o arquivo, corrija e tente novamente: {err} ")
                    self.infos_config['status'] = False
            else:
                self.escrever_no_input(f"- Processo finalizado")
                break

    def iniciar_processo_validar_nif(self, documento_inserido):
        # Criar uma nova thread para executar o processo demorado
        try:
            self.thread = threading.Thread(target=self.validador_nif, args=[documento_inserido])
            self.thread.start()
        except threading.excepthook as error:
            self.escrever_no_input(f"- Processo finalizado com falha \n {error}")

    def iniciar_processo_validar_cnpj(self, documento_inserido):
        # Criar uma nova thread para executar o processo demorado
        try:
            self.thread = threading.Thread(target=self.validador_cnpj, args=[documento_inserido])
            self.thread.start()
        except threading.excepthook as error:
            self.escrever_no_input(f"- Processo finalizado com falha \n {error}")

    def iniciar_processo_validar_cpf(self, documento_inserido):
        # Criar uma nova thread para executar o processo demorado
        try:
            self.thread = threading.Thread(target=self.validador_cpf, args=[documento_inserido])
            self.thread.start()
        except threading.excepthook as error:
            self.escrever_no_input(f"- Processo finalizado com falha \n {error}")

    def iniciar_processo_validar_cei(self, documento_inserido):
        # Criar uma nova thread para executar o processo demorado
        try:
            self.thread = threading.Thread(target=self.validador_cei, args=[documento_inserido])
            self.thread.start()
        except threading.excepthook as error:
            self.escrever_no_input(f"- Processo finalizado com falha \n {error}")

    def iniciar_processo_validar_pis(self, documento_inserido):
        # Criar uma nova thread para executar o processo demorado
        try:
            self.thread = threading.Thread(target=self.validador_pis, args=[documento_inserido])
            self.thread.start()
        except threading.excepthook as error:
            self.escrever_no_input(f"- Processo finalizado com falha \n {error}")

    def iniciar_processo_gerar_nif(self, linhas, checkbox_arquivo):
        self.escrever_no_input(f"- Processo iniciado - Gerador de NIF")
        # Criar uma nova thread para executar o processo demorado
        try:
            self.thread = threading.Thread(target=self.gerador_nif, args=[linhas, checkbox_arquivo])
            self.thread.start()
        except threading.excepthook as error:
            self.escrever_no_input(f"- Processo finalizado com falha \n {error}")

    def iniciar_processo_gerar_cnpj(self, linhas, checkbox_mascara, checkbox_arquivo):
        self.escrever_no_input(f"- Processo iniciado - Gerador de CNPJ")
        # Criar uma nova thread para executar o processo demorado
        try:
            self.thread = threading.Thread(target=self.gerador_cnpj, args=[linhas, checkbox_mascara, checkbox_arquivo])
            self.thread.start()
        except threading.excepthook as error:
            self.escrever_no_input(f"- Processo finalizado com falha \n {error}")

    def iniciar_processo_gerar_cpf(self, linhas, checkbox_mascara, checkbox_arquivo):
        self.escrever_no_input(f"- Processo iniciado - Gerador de CPF")
        # Criar uma nova thread para executar o processo demorado
        try:
            self.thread = threading.Thread(target=self.gerador_cpf, args=[linhas, checkbox_mascara, checkbox_arquivo])
            self.thread.start()
        except threading.excepthook as error:
            self.escrever_no_input(f"- Processo finalizado com falha \n {error}")

    def iniciar_processo_gerar_cei(self, linhas, checkbox_mascara, checkbox_arquivo):
        self.escrever_no_input(f"- Processo iniciado - Gerador de CEI")
        # Criar uma nova thread para executar o processo demorado
        try:
            self.thread = threading.Thread(target=self.gerador_cei, args=[linhas, checkbox_mascara, checkbox_arquivo])
            self.thread.start()
        except threading.excepthook as error:
            self.escrever_no_input(f"- Processo finalizado com falha \n {error}")

    def iniciar_processo_gerar_pis(self, linhas, checkbox_mascara, checkbox_arquivo):
        self.escrever_no_input(f"- Processo iniciado - Gerador de PIS")
        # Criar uma nova thread para executar o processo demorado
        try:
            self.thread = threading.Thread(target=self.gerador_pis, args=[linhas, checkbox_mascara, checkbox_arquivo])
            self.thread.start()
        except threading.excepthook as error:
            self.escrever_no_input(f"- Processo finalizado com falha \n {error}")

    def iniciar_processo_limpar_redis_especifico(self):
        self.escrever_no_input(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        try:
            self.thread = threading.Thread(target=self.limpar_redis_especifico)
            self.thread.start()
        except threading.excepthook as error:
            self.escrever_no_input(f"- Processo finalizado com falha \n {error}")

    def iniciar_processo_limpar_redis_todos(self):
        self.escrever_no_input(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        try:
            self.thread = threading.Thread(target=self.limpar_todos_redis)
            self.thread.start()
        except threading.excepthook as error:
            self.escrever_no_input(f"- Processo finalizado com falha \n {error}")

    def iniciar_processo_atualizacao(self):
        self.escrever_no_input(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        try:
            self.thread = threading.Thread(target=self.buscar_versions)
            self.thread.start()
        except threading.excepthook as error:
            self.escrever_no_input(f"Processo finalizado com falha \n {error}")

    def iniciar_processo_replicar(self):
        self.escrever_no_input(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        try:
            self.thread = threading.Thread(target=self.replicar_version)
            self.thread.start()
        except threading.excepthook as error:
            self.escrever_no_input(f"Processo finalizado com falha \n {error}")

    def iniciar_processo_download(self):
        self.escrever_no_input(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        try:
            self.thread = threading.Thread(target=self.download_backup)
            self.thread.start()
        except threading.excepthook as error:
            self.escrever_no_input(f"Processo finalizado com falha \n {error}")

    def iniciar_processo_restaurar(self):
        self.escrever_no_input(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        try:
            self.thread = threading.Thread(target=self.restaurar_banco)
            self.thread.start()
        except threading.excepthook as error:
            self.escrever_no_input(f"Processo finalizado com falha \n {error}")

    def iniciar_processo_manipula_banco(self):
        self.escrever_no_input(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        try:
            self.thread = threading.Thread(target=self.manipular_banco_muro)
            self.thread.start()
        except threading.excepthook as error:
            self.escrever_no_input(f"Processo finalizado com falha \n {error}")

    def trocar_tela_validadores(self, app):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Validadores de Documentos")
        peso_linha = 0
        self.app.rowconfigure(1, weight=1)
        self.app.rowconfigure(2, weight=peso_linha)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(5, weight=peso_linha)
        self.app.rowconfigure(6, weight=peso_linha)
        self.app.rowconfigure(7, weight=peso_linha)
        self.app.rowconfigure(8, weight=peso_linha)
        self.app.rowconfigure(9, weight=peso_linha)
        self.app.rowconfigure(10, weight=1)
        self.estruturar_tela()
        self.tela_validadores(app, self.version, self.coluna)

    def trocar_tela_geradores(self, app):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Geradores de Documentos")
        peso_linha = 0
        self.app.rowconfigure(1, weight=1)
        self.app.rowconfigure(2, weight=peso_linha)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(5, weight=peso_linha)
        self.app.rowconfigure(6, weight=peso_linha)
        self.app.rowconfigure(7, weight=peso_linha)
        self.app.rowconfigure(8, weight=peso_linha)
        self.app.rowconfigure(9, weight=peso_linha)
        self.app.rowconfigure(10, weight=1)
        self.estruturar_tela()
        self.tela_geradores(app, self.version, self.coluna)

    def trocar_tela_redis_especifico(self, app):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Limpar redis Especifico")
        peso_linha = 0
        self.app.rowconfigure(1, weight=1)
        self.app.rowconfigure(2, weight=1)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(9, weight=1)
        self.estruturar_tela()
        self.tela_limpar_redis_especifico(app, self.version, self.coluna)

    def trocar_tela_redis_todos(self, app):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Limpar todos os redis")
        peso_linha = 0
        self.app.rowconfigure(1, weight=1)
        self.app.rowconfigure(2, weight=1)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(9, weight=1)
        self.estruturar_tela()
        self.tela_limpar_redis_todos(app, self.version, self.coluna)

    def trocar_tela_ferramentas(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Ferramentas")
        peso_linha = 0
        self.app.rowconfigure(1, weight=1)
        self.app.rowconfigure(2, weight=1)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(5, weight=peso_linha)
        self.app.rowconfigure(9, weight=1)
        self.estruturar_tela()
        self.tela_ferramentas(self.app, self.version, self.coluna)

    def trocar_tela_ferramentas_bancos(self, app):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Ferramentas de banco")
        peso_linha = 0
        self.app.rowconfigure(1, weight=1)
        self.app.rowconfigure(2, weight=1)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(9, weight=1)
        self.estruturar_tela()
        self.tela_ferramentas_bancos(app, self.version, self.coluna)

    def trocar_tela_ferramentas_redis(self, app):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Ferramentas de Redis")
        peso_linha = 0
        self.app.rowconfigure(1, weight=1)
        self.app.rowconfigure(2, weight=1)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(9, weight=1)
        self.estruturar_tela()
        self.tela_ferramentas_redis(app, self.version, self.coluna)

    def trocar_tela_menu(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Menu")
        peso_linha = 0
        self.app.rowconfigure(1, weight=1)
        self.app.rowconfigure(2, weight=1)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(9, weight=1)
        self.estruturar_tela()
        self.tela_menu(self.app, self.version, self.coluna)

    def trocar_tela_busca_muro(self, app):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Busca Muro")
        peso_linha = 0
        self.app.rowconfigure(1, weight=1)
        self.app.rowconfigure(2, weight=1)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(9, weight=1)
        self.estruturar_tela()
        self.tela_busca_muro(app, self.version, self.coluna)

    def trocar_tela_download_backup(self, app):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Download Backup")
        peso_linha = 0
        self.app.rowconfigure(1, weight=1)
        self.app.rowconfigure(2, weight=1)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(9, weight=1)
        self.estruturar_tela()
        self.tela_download_backup(app, self.version, self.coluna)

    def trocar_tela_restaurar_backup(self, app):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Restaurar Backup")
        peso_linha = 0
        self.app.rowconfigure(1, weight=1)
        self.app.rowconfigure(2, weight=1)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(9, weight=1)
        self.estruturar_tela()
        self.tela_restaurar_backup(app, self.version, self.coluna)

    def trocar_tela_buscar_versions(self, app):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Buscar Versions")
        peso_linha = 0
        self.app.rowconfigure(1, weight=1)
        self.app.rowconfigure(2, weight=1)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(9, weight=1)
        self.estruturar_tela()
        self.tela_buscar_versions(app, self.version, self.coluna)

    def trocar_tela_replicar_version(self, app):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Replicar Versions")
        peso_linha = 0
        self.app.rowconfigure(1, weight=1)
        self.app.rowconfigure(2, weight=1)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(9, weight=1)
        self.estruturar_tela()
        self.tela_replicar_version_muro(app, self.version, self.coluna)

    def trocar_tela_alterar_aparencia(self):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], "INFO - Tela - Alterar Aparencia")
        peso_linha = 0
        self.app.rowconfigure(1, weight=1)
        self.app.rowconfigure(2, weight=1)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(5, weight=peso_linha)
        self.app.rowconfigure(6, weight=peso_linha)
        self.app.rowconfigure(9, weight=1)
        self.estruturar_tela()
        self.tela_alterar_aparencia(self.app, self.version, self.coluna)

    def tela_limpar_redis_especifico(self, app, version, coluna):
        titulo = "LIMPAR REDIS ESPECIFICOS"
        app.title("MSS - " + version + " - " + titulo)
        opcoes = []

        if self.infos_config["redis_qa"]:
            for red_nome in self.infos_config["redis_qa"]:
                if self.infos_config['redis_qa'][0]["nome_redis"] != "":
                    opcoes.append(red_nome["nome_redis"])

        else:
            self.popup_mensagem(f"Não existe arquivos .json na pasta config")
            return

        self.label_lista_redis = Label(
            text="Redis:",
            bg=self.infos_config_prog["background_color_fundo"],
            fg=self.infos_config_prog["background_color_fonte"]
        )
        self.combobox = Combobox(
            app,
            values=opcoes,
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
            command=lambda: self.trocar_tela_ferramentas_redis(app)
        )
        self.limpar_linha(10, 2)
        self.escrever_titulos(self.app, titulo, 2, coluna)
        if len(opcoes) > 0:
            self.combobox.set(opcoes[0])
        self.label_lista_redis.grid(row=3, column=coluna, columnspan=1, pady=(10, 0), sticky="WS")
        self.combobox.grid(row=4, column=coluna, columnspan=1, pady=(0, 10), sticky="WEN")
        self.caixa_texto(5, 6, coluna, "Saida:")
        self.button_redis_inicio.grid(row=7, column=coluna, pady=(10, 0))
        self.button_redis_voltar.grid(row=10, column=1, padx=5, pady=5, columnspan=2, sticky="ES")

    def tela_limpar_redis_todos(self, app, version, coluna):
        titulo = "LIMPAR TODOS OS REDIS"
        app.title("MSS - " + version + " - " + titulo)

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
            command=lambda: self.trocar_tela_ferramentas_redis(app)
        )
        self.limpar_linha(10, 2)
        self.escrever_titulos(self.app, titulo, 2, coluna)
        self.caixa_texto(3, 4, coluna, "Saida:")
        self.button_atualizacao_inicio.grid(row=5, column=coluna,  pady=(10, 0))
        self.button_atualizacao_voltar.grid(row=10, column=1, padx=5, pady=5, columnspan=2, sticky="ES")

    def tela_restaurar_backup(self, app, version, coluna):
        titulo = "Restaurar Backup"
        app.title("MSS - " + version + " - " + titulo)

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
            command=lambda: self.trocar_tela_menu()
        )
        self.limpar_linha(10, 2)
        self.escrever_titulos(self.app, titulo, 2, coluna)
        self.input_placeholder(
            3, 4, coluna, " Insira o nome do banco desejado (KAIROS_BASE_123456789)", "Nome do banco:")
        self.caixa_texto(5, 6, coluna, "Saida:")
        self.button_restaurar_inicio.grid(row=7, column=coluna, pady=(10, 0))
        self.button_restaurar_voltar.grid(row=10, column=1, padx=5, pady=5, columnspan=2, sticky="ES")

    def tela_download_backup(self, app, version, coluna):
        titulo = "Download Backup"
        app.title("MSS - " + version + " - " + titulo)

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
            command=lambda: self.trocar_tela_menu()
        )
        self.limpar_linha(10, 2)
        self.escrever_titulos(self.app, titulo, 2, coluna)
        self.input_placeholder(3, 4, coluna, "URL DO BACKUP", "Endereço URL:")
        self.caixa_texto(5, 6, coluna, "Saida:")
        self.button_download_inicio.grid(row=7, column=coluna, pady=(10, 0))
        self.button_download_voltar.grid(row=10, column=1, padx=5, pady=5, columnspan=2, sticky="ES")

    def tela_busca_muro(self, app, version, coluna):
        titulo = "BUSCAR BANCOS"
        app.title("MSS - " + version + " - " + titulo)

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
            command=lambda: self.trocar_tela_ferramentas_bancos(app)
        )

        self.escrever_titulos(self.app, titulo, 2, coluna)
        self.input_placeholder(3, 4, coluna, "Insira o version para downgrade...", "Version:")
        self.caixa_texto(5, 6, coluna, "Saida:")
        self.button_busca_inicio.grid(row=7, column=coluna, padx=5, pady=5)
        self.button_busca_voltar.grid(row=10, column=1, padx=5, pady=5, columnspan=2, sticky="ES")

    def tela_buscar_versions(self, app, version, coluna):
        titulo = "CONSULTAR VERSIONS"
        app.title("MSS - " + version + " - " + titulo)

        self.button_atualizacao_inicio = Button(
            app,
            text="Iniciar",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.iniciar_processo_atualizacao()
        )
        self.button_atualizacao_voltar = Button(
            app,
            text="Voltar",
            width=15,
            height=2,
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_ferramentas_bancos(app)
        )

        self.escrever_titulos(self.app, titulo, 2, coluna)
        self.caixa_texto(3, 4, coluna, "Saida:")
        self.button_atualizacao_inicio.grid(row=5, column=coluna,  pady=(10, 0))
        self.button_atualizacao_voltar.grid(row=10, column=1, padx=5, pady=5, columnspan=2, sticky="ES")

    def tela_replicar_version_muro(self, app, version, coluna):
        titulo = "REPLICAR VERSIONS"
        app.title("MSS - " + version + " - " + titulo)

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
            command=lambda: self.trocar_tela_ferramentas_bancos(app)
        )
        self.limpar_linha(10, 2)
        self.escrever_titulos(self.app, titulo, 2, coluna)
        self.caixa_texto(3, 4, coluna, "Saida:")
        self.button_replicar_inicio.grid(row=5, column=coluna,  pady=(10, 0))
        self.button_replicar_voltar.grid(row=10, column=1, padx=5, pady=5, columnspan=2, sticky="ES")

    def tela_ferramentas_bancos(self, app, version, coluna):
        titulo = "FERRAMENTAS BD"
        app.title("MSS - " + version + " - " + titulo)

        self.button_ferramenta_busca_banco = Button(
            app,
            text="Buscar Bancos",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_busca_muro(app)
        )
        self.button_ferramenta_buscar_versions = Button(
            app,
            text="Buscar Version's",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_buscar_versions(app)
        )
        self.button_ferramenta_replicar_version = Button(
            app,
            text="Replicar version",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_replicar_version(app)
        )
        self.button_ferramenta_voltar = Button(
            app,
            text="Voltar",
            width=15,
            height=2,
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_ferramentas()
        )
        self.limpar_linha(10, 2)
        self.escrever_titulos(self.app, titulo, 2, coluna)
        self.button_ferramenta_busca_banco.grid(row=3, column=coluna)
        self.button_ferramenta_buscar_versions.grid(row=4, column=coluna)
        self.button_ferramenta_replicar_version.grid(row=5, column=coluna)
        self.button_ferramenta_voltar.grid(row=10, column=1, padx=5, pady=5, columnspan=2, sticky="ES")

    def tela_ferramentas_redis(self, app, version, coluna):
        titulo = "FERRAMENTAS REDIS"
        app.title("MSS - " + version + " - " + titulo)

        self.button_ferramenta_busca_banco = Button(
            app,
            text="Limpar todos os redis",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_redis_todos(app)
        )
        self.button_ferramenta_buscar_versions = Button(
            app,
            text="Limpar Redis especifico",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_redis_especifico(app)
        )
        self.button_ferramenta_voltar = Button(
            app,
            text="Voltar",
            width=15,
            height=2,
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_ferramentas()
        )
        self.limpar_linha(10, 2)
        self.escrever_titulos(self.app, titulo, 2, coluna)
        self.button_ferramenta_busca_banco.grid(row=3, column=coluna)
        self.button_ferramenta_buscar_versions.grid(row=4, column=coluna)
        self.button_ferramenta_voltar.grid(row=10, column=1, padx=5, pady=5, columnspan=2, sticky="ES")

    def tela_ferramentas(self, app, version, coluna):
        titulo = "FERRAMENTAS"
        app.title("MSS - " + version + " - " + titulo)

        self.button_menu_ferramentas = Button(
            app,
            text="Ferramentas de Bancos",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_ferramentas_bancos(app)
        )
        self.button_menu_ferramentas_redis = Button(
            app,
            text="Ferramentas Redis",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_ferramentas_redis(app)
        )
        self.button_menu_ferramentas_geradores = Button(
            app,
            text="Gerador de documentos",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_geradores(app)
        )
        self.button_menu_ferramentas_validadores = Button(
            app,
            text="Validador de documentos",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_validadores(app)
        )
        self.button_menu_Voltar = Button(
            app,
            text="Voltar",
            width=15,
            height=2,
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_menu()
        )
        self.limpar_linha(10, 2)
        self.escrever_titulos(self.app, titulo, 2, coluna)
        self.button_menu_ferramentas.grid(row=3, column=coluna)
        self.button_menu_ferramentas_redis.grid(row=4, column=coluna)
        self.button_menu_ferramentas_geradores.grid(row=5, column=coluna)
        self.button_menu_ferramentas_validadores.grid(row=6, column=coluna)
        self.button_menu_Voltar.grid(row=10, column=1, padx=5, pady=5, columnspan=2, sticky="ES")

    def tela_geradores(self, app, version, coluna):
        titulo = "Geradores"
        app.title("MSS - " + version + " - " + titulo)
        opcoes = ["CEI", "CNPJ", "CPF", "NIF", "PIS"]
        self.valor_checkbox_mascara_num = BooleanVar()
        self.valor_checkbox_gerar_arquivo = BooleanVar()
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
            text="Criar",
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
            command=lambda: self.trocar_tela_ferramentas()
        )
        self.limpar_linha(10, 2)
        self.combobox.set(opcoes[0])
        self.escrever_titulos(self.app, titulo, 2, coluna)
        self.combobox.grid(row=3, column=coluna, pady=(0, 10), sticky="SWE")
        self.input_placeholder(4, 5, coluna, " Insira a quantidade de números que serão gerados", "Quantidade:")
        self.checkbox_mascara_num.grid(row=5, column=coluna, pady=(25, 0), sticky="W")
        self.checkbox_gerar_arquivo.grid(row=6, column=coluna, pady=(0, 1), sticky="W")
        self.caixa_texto(7, 8, coluna, "Saida:")
        self.button_gerador_inicio.grid(row=9, column=coluna, pady=(10, 0), sticky="E")
        self.button_gerador_limpar.grid(row=9, column=coluna, pady=(10, 0), sticky="W")
        self.button_gerador_voltar.grid(row=10, column=1, padx=5, pady=5, columnspan=2, sticky="ES")

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
            command=lambda: self.trocar_tela_ferramentas()
        )
        self.limpar_linha(10, 2)
        self.combobox.set(opcoes[0])
        self.escrever_titulos(self.app, titulo, 2, coluna)
        self.combobox.grid(row=3, column=coluna, pady=(0, 10), sticky="SWE")
        self.input_placeholder(4, 5, coluna, " Insira o documento para ser validado", "Documento:")
        self.caixa_texto(7, 8, coluna, "Saida:")
        self.button_gerador_inicio.grid(row=9, column=coluna, pady=(10, 0), sticky="E")
        self.button_gerador_limpar.grid(row=9, column=coluna, pady=(10, 0), sticky="W")
        self.button_gerador_voltar.grid(row=10, column=1, padx=5, pady=5, columnspan=2, sticky="ES")

    def tela_menu(self, app, version, coluna):
        titulo = "Menu"
        app.title("MSS - " + version + " - " + titulo)

        self.button_menu_ferramentas = Button(
            app,
            text="Ferramentas",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_ferramentas()
        )
        self.button_menu_download = Button(
            app,
            text="Download Backup",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_download_backup(app)
        )
        self.button_menu_restaurar = Button(
            app,
            text="Restaurar Backup",
            width=25,
            height=2,
            bg=self.infos_config_prog["background_color_botoes"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.trocar_tela_restaurar_backup(app)
        )
        self.limpar_linha(10, 2)
        self.escrever_titulos(self.app, titulo, 2, coluna)
        self.button_menu_ferramentas.grid(row=3, column=coluna)
        self.button_menu_download.grid(row=4, column=coluna)
        self.button_menu_restaurar.grid(row=5, column=coluna)

    def tela_config(self, app, version, coluna):
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Tela - CONFIGURAÇÃO")
        titulo = "CONFIGURAÇÃO"
        app.title("MSS - " + version + " - " + titulo)

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
        self.limpar_linha(10, 2)
        self.escrever_titulos(self.app, titulo, 2, coluna)
        self.button_config_existente.grid(row=3, column=coluna, sticky="WE")
        self.button_config_novo.grid(row=4, column=coluna, sticky="WE")

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

        self.limpar_linha(10, 2)
        self.escrever_titulos(self.app, titulo, 2, coluna)
        self.label_background_fundo.grid(row=3, column=coluna, sticky="WN")
        self.entry_background_fundo.grid(row=3, column=coluna, sticky="EN")
        self.button_background_fundo.grid(row=3, column=2, sticky="WS")
        self.label_background_titulos.grid(row=4, column=coluna, sticky="WN")
        self.entry_background_titulos.grid(row=4, column=coluna, sticky="EN")
        self.button_background_titulos.grid(row=4, column=2, sticky="WS")
        self.label_background_botoes.grid(row=5, column=coluna, sticky="WN")
        self.entry_background_botoes.grid(row=5, column=coluna, sticky="EN")
        self.button_background_botoes.grid(row=5, column=2, sticky="WS")
        self.label_background_botoes_navs.grid(row=6, column=coluna, sticky="WN")
        self.entry_background_botoes_navs.grid(row=6, column=coluna, sticky="EN")
        self.button_background_botoes_navs.grid(row=6, column=2, sticky="WS")
        self.label_background_fonte.grid(row=7, column=coluna, sticky="WN")
        self.entry_background_fonte.grid(row=7, column=coluna, sticky="EN")
        self.button_background_fonte.grid(row=7, column=2, sticky="WS")
        self.button_nav_salvar.grid(row=10, column=1, padx=5, pady=5, columnspan=2, sticky="ES")
        self.entry_background_fundo.insert(0, valores_input[0])
        self.entry_background_titulos.insert(0, valores_input[1])
        self.entry_background_botoes.insert(0, valores_input[2])
        self.entry_background_botoes_navs.insert(0, valores_input[3])
        self.entry_background_fonte.insert(0, valores_input[4])

    def botoes_navs(self, app):
        self.button_menu_sair = Button(
            app,
            text="Sair",
            width=15,
            height=2,
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.finalizar()
        )
        self.button_menu_generico = Button(
            app,
            text="",
            width=15,
            height=2,
            bg=self.infos_config_prog["background_color_botoes_navs"],
            fg=self.infos_config_prog["background_color_fonte"],
            command=lambda: self.finalizar()
        )
        self.button_menu_generico.config(state='disabled')
        self.button_menu_sair.grid(row=10, column=0, columnspan=2, padx=5, pady=5, sticky="WS")
        self.button_menu_generico.grid(row=10, column=1, padx=5, pady=5, columnspan=2, sticky="ES")

    def estruturar_tela(self):
        self.app.configure(bg=self.infos_config_prog["background_color_fundo"])
        self.app.rowconfigure(0, weight=0)
        self.app.rowconfigure(10, weight=0)
        self.remover_widget(self.app, '*', '*')
        self.menu_cascata()
        self.texto_config_selecionado(self.app)
        self.botoes_navs(self.app)

    def trocar_tela_config(self):
        peso_linha = 0
        self.app.rowconfigure(1, weight=1)
        self.app.rowconfigure(2, weight=1)
        self.app.rowconfigure(3, weight=peso_linha)
        self.app.rowconfigure(4, weight=peso_linha)
        self.app.rowconfigure(9, weight=1)
        self.estruturar_tela()
        self.tela_config(self.app, self.version, self.coluna)

    def tela(self):
        self.app.geometry(f"{self.largura}x{self.altura}+{self.metade_wid}+{self.metade_hei}")
        self.status_thread = False
        menu = Menu(self.app)
        self.app.config(menu=menu)

        self.peso_linha_zero = 1
        self.peso_linha_um = 1
        self.peso_linha = 1
        self.peso_ultima_linha = 1
        self.peso_coluna = 1

        self.app.columnconfigure(0, weight=self.peso_coluna)
        self.app.columnconfigure(1, weight=self.peso_coluna)
        self.app.columnconfigure(2, weight=self.peso_coluna)
        return self.app

    def main(self):
        self.app = Tk()
        self.largura = 450
        self.altura = 515
        pos_wid = self.app.winfo_screenwidth()
        pos_hei = self.app.winfo_screenheight()
        self.metade_wid = int((pos_wid / 2) - (self.largura / 2))
        self.metade_hei = int((pos_hei / 2) - (self.altura / 2))
        validar_diretorio(self.nomes, self.popup_mensagem)

        # Data/hora inicio do programa
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Programa iniciado")
        # Versão atual do programa
        self.escrever_arquivo_log(self.nomes['arquivo_base_muro'], f"INFO - Versão:  {self.version}")
        self.app = self.tela()
        self.app.protocol("WM_DELETE_WINDOW", self.finalizar)
        self.validar_atual_config()
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
            self.popup_mensagem(f"Erro ao acessar arquivo de configuração default {error}")
            self.trocar_tela_config()

        self.app.mainloop()


prog = Aplicativo()
