# coding: utf-8
import datetime
import json
import os
import re
import sys
import pyodbc
from github import Github
import requests
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk
import threading
import redis

def comparar_tags(tag1, tag2):
    # Função para comparar duas tags no formato 'x.y.z' e retornar 1 se a primeira for maior, -1 se for menor e 0 se forem iguais
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

def pesquisar_maior_tag(username, repository, tag_atual):
    github = Github()
    repo = github.get_repo(f"{username}/{repository}")
    tags = repo.get_tags()

    maior_tag = None
    for tag in tags:
        if comparar_tags(tag.name, tag_atual) > 0:
            if maior_tag is None or comparar_tags(tag.name, maior_tag) > 0:
                maior_tag = tag.name
                break

    return maior_tag

def realizar_download(maior_tag):
    caminho = f"https://github.com/mathsantosilva/MSS/releases/download/{maior_tag}/BuscaMuro.exe"
    response = requests.get(caminho)
    try:
        if os.path.exists("C:/MSS_temp"):
            return
        else:
            os.makedirs("C:/MSS_temp")
    except Exception as error:
        prog.mensagem(f"Erro ao criar/validar a pasta C:/MSS_temp: {error} ")
    with open("C:/MSS_temp/BuscaMuro.exe", "wb") as arquivo:
        arquivo.write(response.content)
        arquivo.close()

def executar_comando_batch(dir_atual):
    comando = f"""@echo off
chcp 65001
cls
echo Aguarde enquanto a atualização esta em andamento
xcopy "C:\MSS_temp\BuscaMuro.exe" "{dir_atual}\BuscaMuro.exe" /w/E/Y/H
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

def data_atual():
    data_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return data_hora

def validar_linha(nome):
    with open(f"Log\\{nome}.txt", "r") as arquivo_insp:
        conteudo = arquivo_insp.read()
        linhas = conteudo.count("\n") + 1
    if linhas == 1:
        pula_linha = ""
    else:
        pula_linha = "\n"

    return pula_linha

def validar_diretorio(nomes, mensagem):
    # Criar diretorio log
    try:
        if not os.path.exists(nomes['diretorio_log']):
            os.makedirs(nomes['diretorio_log'])
    except Exception as error:
        mensagem(f"\n{data_atual()} - INFO - Erro ao criar/validar a pasta {nomes['diretorio_log']}: {error} ")

    # Criar diretorio config
    try:
        if not os.path.exists(nomes['diretorio_config']):
            os.makedirs(nomes['diretorio_config'])
    except Exception as error:
        mensagem(
            f"\n{data_atual()} - INFO - Erro ao criar/validar a pasta {nomes['diretorio_config']}: {error} ")

class Aplicativo:
    version = "2.2.3"
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

    def __init__(self):
        self.placeholder_text = None
        self.label = None
        self.entry = None
        self.label_restaurar_backup = None
        self.nome_campo_caixa = None
        self.widtexto = None
        self.arquivo_validar = None
        self.arquivo = None
        self.arquivo_replicar = None
        self.infos_config = None
        self.label_lista_arquivos = None
        self.combobox = None
        self.button_nav_escolher = None
        self.button_nav_criar = None
        self.thread = None
        self.arquivo_restauracao = None
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
        self.circulo = None
        self.status_thread = None
        self.arquivo_principal = None
        self.app = None
        self.main()

    def finalizar(self):
        self.arquivo_principal.write(f"\n{data_atual()} - INFO - Programa finalizado")
        self.arquivo_principal.close()
        sys.exit(200)

    def atualizador(self):
        username = "mathsantosilva"
        repository = "MSS"
        tag_atual = self.version
        maior_tag = pesquisar_maior_tag(username, repository, tag_atual)

        if maior_tag is not None:
            realizar_download(maior_tag)
            dir_atual = os.getcwd()
            executar_comando_batch(dir_atual)
            self.finalizar()
        else:
            try:
                if os.path.exists("C:/MSS_temp"):
                    shutil.rmtree("C:/MSS_temp")
                else:
                    return
            except Exception as error:
                self.mensagem(f"Erro ao criar/validar a pasta {self.nomes['diretorio_log']}: {error} ")

    def percorrer_widgets(self, app):
        self.widget.clear()
        if app.winfo_children():
            for child in app.winfo_children():
                self.widget.append(child.widgetName)
                continue
        return self.widget

    def on_entry_click(self, event):
        if self.entry.get() == self.placeholder_text:
            self.entry.delete(0, tk.END)
            self.entry.config(foreground='black')

    def on_focusout(self, event):
        if self.entry.get() == "":
            self.entry.insert(0, self.placeholder_text)
            self.entry.config(foreground='gray')

    def input_placeholder(self, linha_label, linha_entry,  coluna, texto, nome_campo):
        texo_com_espaco = "  " + texto
        self.placeholder_text = texo_com_espaco
        placeholder_color = "gray"
        self.label = tk.Label(
            text=nome_campo
        )
        self.entry = tk.Entry(
            self.app,
            fg=placeholder_color
        )
        self.entry.insert(0, self.placeholder_text)
        self.entry.bind("<FocusIn>", self.on_entry_click)
        self.entry.bind("<FocusOut>", self.on_focusout)
        self.label.grid(row=linha_label, column=coluna, sticky="WS", pady=(10, 0))
        self.entry.grid(row=linha_entry, column=coluna, columnspan=1, sticky="WEN", pady=(0, 10))

    def escrever_titulos(self, app, tela, linha, coluna):
        self.label_restaurar_backup = tk.Label(
            app,
            text=tela,
            font=('Arial', 12, 'bold')
        )
        self.label_restaurar_backup.grid(row=linha, column=coluna, sticky="WE")

    def limpar_linha(self, linha):
        widgets = self.app.grid_slaves(row=linha)
        for widget in widgets:
            widget.destroy()

    def caixa_texto(self, linha_label, linha_texto, coluna, nome):
        self.nome_campo_caixa = tk.Label(
            text=nome
        )
        self.widtexto = tk.Text(
            self.app,
            height=12,
            wrap="word"
        )
        self.nome_campo_caixa.grid(row=linha_label, column=coluna, sticky="WE")
        self.widtexto.grid(row=linha_texto, column=coluna, sticky="WE")
        self.widtexto.config(width=50)
        #scrollbar = tk.Scrollbar(self.app, background="red")
        #scrollbar.grid(row=linha, column=coluna, sticky="NSE", padx=0)
        #scrollbar.config(command=self.widtexto.yview)
        self.widtexto.config(state="disabled")

    def escrever(self, texto):
        self.widtexto.config(state="normal")
        self.widtexto.insert(tk.END, str(texto) + '\n')
        self.widtexto.see(tk.END)
        self.widtexto.config(state="disabled")

    def mensagem(self, mensagem):
        msg = tk.Tk()
        msg.geometry(f"{self.largura}x200+{self.metade_wid}+{self.metade_hei}")
        msg.grid_rowconfigure(0, weight=1)
        msg.grid_columnconfigure(0, weight=1)
        msg.config(padx=10, pady=10)
        msg.title("MSS - " + self.version + " - ALERTA")
        label_mensagem = tk.Label(
            msg,
            text=mensagem,
            padx = 20,
            pady = 20

        )
        button_sair_mensagem = tk.Button(
            msg,
            text="Fechar",
            width=10,
            height=2,
            background="grey",
            command=lambda: fechar_janela(msg)

        )
        label_mensagem.grid(row=0, sticky="WE")
        button_sair_mensagem.grid(row=1, pady=(10,10))

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

    def buscar_versions(self):
        self.button_atualizacao_inicio.config(state='disabled')
        self.button_atualizacao_voltar.config(state='disabled')
        tam_base_muro = len(self.infos_config['bases_muro'])
        self.arquivo_validar = open(f"Log\\{self.nomes['arquivo_validar']}.txt", "a")
        pula_linha = validar_linha(self.nomes['arquivo_validar'])
        self.arquivo_principal.write(f"\n{data_atual()} - INFO - Tela - Validar atualização")

        self.arquivo_validar.write(f"{pula_linha}{data_atual()} - INFO - Inicio da validação do banco update ")

        for num in range(tam_base_muro):
            database_update = self.valida_banco_update(num)

            self.escrever(f"\n- Iniciando consulta no banco update")
            try:
                cnxnrp = pyodbc.connect(
                    f"DRIVER=SQL Server;SERVER={self.infos_config['server']};DATABASE={database_update};ENCRYPT=not;UID={self.infos_config['username']};PWD={self.infos_config['password']}")
                cursorrp = cnxnrp.cursor()
                comando = f"select [database_version],  count(database_version) Quantidade from [dbo].[KAIROS_DATABASES] group by [database_version]"
                cursorrp.execute(comando)
                result = cursorrp.fetchall()
            except (Exception or pyodbc.DatabaseError) as err:
                self.escrever(f"- Falha ao tentar consultar banco de update: {err}")
                self.arquivo_validar.write(
                    f"\n{data_atual()} - ERRO - Falha ao tentar consultar banco de muro update: {err}")
            else:
                self.escrever(f"- Sucesso ao consulta: {database_update}")
                self.arquivo_validar.write(f"\n{data_atual()} - INFO - Sucesso ao consulta no banco de update")

                if len(result) > 0:
                    for n in range(len(result)):
                        self.escrever(f"- Version: {result[n][0]} - Quantidade: {result[n][1]}")
                        self.arquivo_validar.write(
                            f"\n{data_atual()} - INFO - Version: {result[n][0]} - Quantidade: {result[n][1]}")
                else:
                    self.escrever(f"- Não foram retornados registros no banco: {database_update}")
                    self.arquivo_validar.write(f"\n{data_atual()} - INFO - Não foram retornados registros no banco:")

            if num < 4:
                num += 1
            self.escrever(f"\n- Concluído a parte {num}, de um total de {tam_base_muro}. ")
            self.arquivo_validar.write(
                f"\n{data_atual()} - INFO - Concluído a parte {num}, de um total de {tam_base_muro}. ")
            continue

        self.escrever(f"- Fim da operação de consulta")
        self.arquivo_validar.write(f"\n{data_atual()} - INFO - Fim da operação Validar atualização")
        self.arquivo_validar.close()
        self.button_atualizacao_inicio.config(state='active')
        self.button_atualizacao_voltar.config(state='active')

    def manipular_banco_muro(self):
        self.entry.config(state='disabled')
        self.button_busca_inicio.config(state='disabled')
        self.button_busca_voltar.config(state='disabled')
        lista_string_instancia = ''
        cursor1 = ''
        status_consulta = False

        self.arquivo = open(f"Log\\{self.nomes['arquivo_busca_bancos']}.txt", "a")
        pula_linha = validar_linha(self.nomes['arquivo_busca_bancos'])
        self.arquivo_principal.write(f"\n{data_atual()} - INFO - Tela - Busca muro ")

        self.escrever(f"- Inicio da operação Buscar Bancos")
        self.arquivo.write(f"{pula_linha}{data_atual()} - INFO - Inicio da operação Busca muro ")

        versao_databases = self.entry.get()

        if versao_databases == '' or versao_databases == self.placeholder_text:
            self.escrever(f"-O campo Version não pode estar em branco")
            self.button_busca_inicio.config(state='active')
            self.button_busca_voltar.config(state='active')
            self.entry.config(state='normal')
            return
        else:
            self.escrever(f"- Version para downgrade: {versao_databases}")
            self.arquivo.write(f"\n{data_atual()} - INFO - Version para downgrade: {versao_databases} ")

            # Pegar a lista de bancos da instancia
            self.escrever(f"\n- Iniciando a busca dos bancos na instância: {self.infos_config['server']} ")
            self.arquivo.write(
                f"\n{data_atual()} - INFO - Iniciando a busca dos bancos na instância: {self.infos_config['server']} ")

            try:
                cnxn1 = pyodbc.connect(
                    f"DRIVER=SQL Server;SERVER={self.infos_config['server']};ENCRYPT=not;UID={self.infos_config['username']};PWD={self.infos_config['password']}")
                cursor1 = cnxn1.cursor()
                cursor1.execute("SELECT name FROM sys.databases;")
                lista_string_instancia = cursor1.fetchall()
            except (Exception or pyodbc.DatabaseError) as err:
                self.escrever(f"- Falha ao tentar buscar os bancos da instancia {err}")
                self.arquivo.write(f"\n{data_atual()} - ERRO - Falha ao tentar buscar os bancos da instancia {err} ")
            else:
                cursor1.commit()

                self.escrever(f"- Quantidade de bancos encontrados: {len(lista_string_instancia)}")
                self.arquivo.write(
                    f"\n{data_atual()} - INFO - Quantidade de bancos encontrados: {len(lista_string_instancia)} ")
                status_consulta = True

            if status_consulta:

                # Iniciando processo banco muro.
                for num in range(len(self.infos_config['bases_muro'])):

                    self.escrever(f"\n- Iniciando o processo no banco: {self.infos_config['bases_muro'][num]}")
                    self.arquivo.write(
                        f"\n{data_atual()} - INFO - Iniciando o processo no banco: {self.infos_config['bases_muro'][num]} ")

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
                        self.escrever(f"- Falha ao tentar consultar banco de muro: {err}")
                        self.arquivo.write(f"\n{data_atual()} - ERRO - Falha ao tentar consultar banco de muro {err} ")
                    else:
                        cursor1.commit()

                        self.escrever(f"- Quantidade de registros encontrados: {len(lista_connection_string)}")
                        self.arquivo.write(
                            f"\n{data_atual()} - INFO - Quantidade de registros encontrados: {len(lista_connection_string)} ")

                    # separar o nome do banco nas connection strings
                    for i in range(len(lista_connection_string)):
                        guarda_string_cs.append(lista_connection_string[i].CONNECTION_STRING)
                        string_separada = guarda_string_cs[i].split(";")
                        nome_banco = string_separada[1]
                        tam_nome_banco = len(nome_banco)
                        lista_nome_banco.append((nome_banco[16:tam_nome_banco]).strip())
                        continue

                    # separar o id do banco nas connection strings
                    for cs in range(len(lista_connection_string)):
                        guarda_id_cs.append(str(lista_connection_string[cs].DATABASE_ID))
                        lista_id_banco.append(guarda_id_cs[cs])
                        continue

                    # separar o nome do banco nas instancias
                    for ins in range(len(lista_string_instancia)):
                        guarda_banco_instancia.append(str(lista_string_instancia[ins]))
                        nome_banco_instancia = guarda_banco_instancia[ins]
                        tam_nome_banco_instancia = len(nome_banco_instancia)
                        tam_nome_banco_instancia -= 4
                        separa_string.append(nome_banco_instancia[2:tam_nome_banco_instancia])
                        lista_banco_instancia.append((separa_string[ins]).strip())
                        continue

                    # Comparar bancos "strings"
                    self.escrever("\n- Iniciando a comparação dos bancos")
                    self.arquivo.write(f"\n{data_atual()} - INFO - Iniciando a comparação dos bancos ")
                    for comparar in range(len(lista_banco_instancia)):
                        if lista_banco_instancia[comparar] in lista_nome_banco:
                            index_banco.append(lista_nome_banco.index(lista_banco_instancia[comparar]))
                            index_banco.sort()
                        continue

                    for nums in range(len(index_banco)):
                        connection_string.append(lista_connection_string[index_banco[nums]])
                        database_id.append(lista_id_banco[index_banco[nums]])

                    if len(connection_string) > 0:
                        self.escrever("- Quantidade de bancos que deram Match: " + str(len(connection_string)))
                        self.arquivo.write(
                            f"\n{data_atual()} - INFO - Quantidade de bancos que deram Match: {len(connection_string)} ")
                    else:
                        self.escrever("- Não foram encontrados Match na comparação de bancos")
                        self.arquivo.write(
                            f"\n{data_atual()} - INFO - Não foram encontrados Match na comparação de bancos ")

                    # Limpar as strings para inserir no banco
                    for lim in range(len(connection_string)):
                        guarda_string_bm.append(str(connection_string[lim].CONNECTION_STRING))
                        string = guarda_string_bm[lim]
                        string_limpa.append(string)
                        continue

                    database_update = self.valida_banco_update(num)
                    self.escrever(f"\n- Iniciando a limpeza dos bancos update`s")
                    if len(string_limpa) > 0:
                        # Limpeza base muro UPDATE
                        self.escrever(f"- limpando o banco: {database_update}")
                        self.arquivo.write(
                            f"\n{data_atual()} - INFO - limpando o banco: {database_update} ")
                        try:
                            cursor1.execute(f'DELETE FROM {database_update}.[dbo].[KAIROS_DATABASES]')

                        except (Exception or pyodbc.DatabaseError) as err:
                            self.escrever(f"- Falha ao tentar zerar o banco update {err}")
                            self.arquivo.write(
                                f"\n{data_atual()}  - ERRO - Falha ao tentar zerar o banco de muro update {err} ")
                        else:
                            cursor1.commit()
                            self.escrever(f"- banco {database_update} zerado com sucesso")
                            self.arquivo.write(f"\n{data_atual()} - INFO - Banco {database_update} zerado com sucesso ")
                    else:
                        self.escrever("- Não foi realizada a limpeza no banco: " + database_update)
                        self.arquivo.write(
                            f"\n{data_atual()} - INFO - Não foi realizada a limpeza no banco: {database_update} ")

                    # Inserindo as connections strings no banco muro update
                    self.escrever(
                        f"\n- Iniciando o processo de inserção: {database_update}")
                    self.arquivo.write(
                        f"\n{data_atual()} - INFO - Iniciando o processo de inserção:  {database_update} ")
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
                            self.escrever(f"- Falha ao tentar inserir registros no banco update {err}")
                            self.arquivo.write(
                                f"\n{data_atual()} - ERRO - Falha ao tentar inserir registros no banco update {err} ")
                        else:
                            cursor1.commit()
                            self.escrever("- Sucesso ao inserir connection Strings no Banco de muro Update  ")
                            self.arquivo.write(
                                f"\n{data_atual()} - INFO - Sucesso ao inserir connection Strings no Banco de muro Update ")

                            # Logando as connection string
                            quant = 1
                            arquivo_strings = open(f"Log\\{self.nomes['arquivo_connection_strings']}.txt", "a")
                            pula_linha = validar_linha(self.nomes['arquivo_connection_strings'])
                            arquivo_strings.write(
                                f"{pula_linha}{data_atual()} - INFO - Buscar Bancos - Listando as connection strings utilizadas ")
                            arquivo_strings.write(
                                f"\n{data_atual()} - INFO - Buscar Bancos - Ambiente: {self.infos_config['bases_muro'][num]} ")
                            for log in range(len(connection_string)):
                                arquivo_strings.writelines(
                                    f"\n{data_atual()} - INFO - {quant} - {connection_string[log]} ")
                                quant += 1
                                continue

                            arquivo_strings.close()
                            self.arquivo.write(
                                f"\n{data_atual()} - INFO - Listado as Connection Strings no arquivo: {self.nomes['arquivo_connection_strings']} ")

                    else:
                        self.escrever("- Não a registros para serem inseridos no banco: " + database_update)
                        self.arquivo.write(
                            f"\n{data_atual()} - INFO - Não a registros para serem inseridos no banco: {database_update} ")
                    if num < 4:
                        num += 1
                    self.escrever(
                        f"\n- Concluído a parte {num}, de um total de {len(self.infos_config['bases_muro'])}.")
                    self.arquivo.write(
                        f"\n{data_atual()} - INFO - Concluído a parte {num}, de um total de {len(self.infos_config['bases_muro'])}. ")
                    continue
                cursor1.close()
            else:
                self.escrever(f"- Erro na primeira etapa das buscas, o processo foi interrompido.")
                self.arquivo.write(
                    f"\n{data_atual()} - INFO - Erro na primeira etapa das buscas, o processo foi interrompido. ")

            self.escrever(f"- Fim da operação Busca muro")
            self.arquivo.write(f"\n{data_atual()} - INFO - Fim da operação Busca muro")
            self.arquivo.close()
            self.entry.config(state='normal')
            self.button_busca_inicio.config(state='active')
            self.button_busca_voltar.config(state='active')

    def replicar_version(self):
        self.button_replicar_inicio.config(state='disabled')
        self.button_replicar_voltar.config(state='disabled')
        tam_base_muro = len(self.infos_config['bases_muro'])
        self.arquivo_replicar = open(f"Log\\{self.nomes['arquivo_replicar_version']}.txt", "a")
        pula_linha = validar_linha(self.nomes['arquivo_replicar_version'])
        self.arquivo_principal.write(f"\n{data_atual()} - INFO - Tela - Replicar version ")

        self.escrever(f"- Inicio da operação replicar version")
        self.arquivo_replicar.write(f"{pula_linha}{data_atual()} - INFO - Inicio da operação replicar version")

        for num in range(len(self.infos_config['bases_muro'])):
            lista_registros_db = []
            lista_ids = []
            lista_versions = []
            lista_connection_string = []

            self.escrever(f"\n- replicando para: {self.infos_config['bases_muro'][num]}")
            self.arquivo_replicar.write(
                f"\n{data_atual()} - INFO - Replicando para: {self.infos_config['bases_muro'][num]}")

            database_update = self.valida_banco_update(num)

            try:
                cnxnrp1 = pyodbc.connect(
                    f"DRIVER=SQL Server;SERVER={self.infos_config['server']};DATABASE={database_update};ENCRYPT=not;UID={self.infos_config['username']};PWD={self.infos_config['password']}")
                cursorrp1 = cnxnrp1.cursor()
                cursorrp1.execute(f"SELECT * FROM {database_update}.[dbo].[KAIROS_DATABASES]")
                lista_registros_db = cursorrp1.fetchall()
            except (Exception or pyodbc.DatabaseError) as err:
                self.escrever("- Falha ao tentar consultar banco de muro update: " + str(err))
                self.arquivo_replicar.write(
                    f"\n{data_atual()} - ERRO - Falha ao tentar consultar banco de muro update: {err}")
            else:
                cursorrp1.commit()
                cursorrp1.close()

                self.escrever(f"- Sucesso na consulta: {database_update}")
                self.arquivo_replicar.write(
                    f"\n{data_atual()} - INFO - Sucesso na consulta no banco de muro update: {database_update}")

                self.escrever(f"- Quantidade de registros encontrados: {len(lista_registros_db)}")
                self.arquivo_replicar.write(
                    f"\n{data_atual()} - INFO - Quantidade de registros encontrados: {len(lista_registros_db)}")

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
                    self.escrever(f"- Falha ao tentar consultar banco de muro update: {err}")
                    self.arquivo_replicar.write(
                        f"\n{data_atual()} - ERRO - Falha ao tentar consultar banco de muro update: {err}")
                else:
                    cursorrp2.commit()
                    cursorrp2.close()
                    self.escrever(
                        f"- Sucesso ao inserir version's")
                    self.arquivo_replicar.write(
                        f"\n{data_atual()} - INFO - Sucesso ao inserir version's")

                    # Logando as connection string
                    arquivo_replicar_strings = open(f"Log\\{self.nomes['arquivo_connection_strings']}.txt", "a")
                    pula_linha = validar_linha(self.nomes['arquivo_connection_strings'])
                    arquivo_replicar_strings.write(
                        f"{pula_linha}{data_atual()} - INFO - Replicar Version - Listando as connection strings utilizadas ")
                    arquivo_replicar_strings.write(
                        f"\n{data_atual()} - INFO - Replicar Version - Ambiente: {self.infos_config['bases_muro'][num]} ")
                    quant = 1
                    for log in range(tam_busca_realizada):
                        arquivo_replicar_strings.writelines(
                            f"\n{data_atual()} - INFO - {quant} - ID: {lista_ids[log]} - Version: {lista_versions[log]} ")
                        quant += 1
                        continue

                    arquivo_replicar_strings.write(f"\n{data_atual()} - INFO - Processo finalizado")
                    arquivo_replicar_strings.close()
                    self.arquivo_replicar.write(
                        f"\n{data_atual()} - INFO - Listado os version no arquivo: {self.nomes['arquivo_connection_strings']}")
            else:
                self.escrever("- Não existem registros para alterar o version")
                self.arquivo_replicar.write(f"\n{data_atual()} - INFO - Não existem registros para alterar o version")

            if num < 4:
                num += 1

            self.escrever(
                f"\n- Concluído a parte {num}, de um total de {tam_base_muro}.")
            self.arquivo_replicar.write(
                f"\n{data_atual()} - INFO - Concluído a parte {num}, de um total de {tam_base_muro}.")
            continue

        self.escrever(f"- Fim da operação replicar version")
        self.arquivo_replicar.write(f"\n{data_atual()} - INFO - Fim da operação replicar version")
        self.arquivo_replicar.close()
        self.button_replicar_inicio.config(state='active')
        self.button_replicar_voltar.config(state='active')

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
                        self.escrever(
                            "- Não foi inserido no arquivo de config o apontamento para o banco Muro update BR")
                        # arquivo.write(f"\n{self.data_atual()} - ERRO - Não foi inserido no arquivo de config o apontamento para o banco Muro update BR ")
                case 'qcdev_kairos_base_muro':
                    if self.infos_config['database_update_br'] != '':
                        database_update = self.infos_config['database_update_br']
                        return database_update
                    else:
                        self.escrever(
                            "- Não foi inserido no arquivo de config o apontamento para o banco Muro update BR")
                        # arquivo.write(f"\n{self.data_atual()} - ERRO - Não foi inserido no arquivo de config o apontamento para o banco Muro update BR ")
                case "qcmaint_kairos_base_muro_mx":
                    if self.infos_config['database_update_mx'] != '':
                        database_update = self.infos_config['database_update_mx']
                        return database_update
                    else:
                        self.escrever(
                            "-  Não foi inserido no arquivo de config o apontamento para o banco Muro update MX")
                        # arquivo.write(
                        #    f"\n{self.data_atual()} - ERRO - Não foi inserido no arquivo de config o apontamento para o banco Muro update MX ")
                case "qcdev_kairos_base_muro_mx":
                    if self.infos_config['database_update_mx'] != '':
                        database_update = self.infos_config['database_update_mx']
                        return database_update
                    else:
                        self.escrever(
                            "-  Não foi inserido no arquivo de config o apontamento para o banco Muro update MX")
                        # arquivo.write(
                        #    f"\n{self.data_atual()} - ERRO - Não foi inserido no arquivo de config o apontamento para o banco Muro update MX ")
                case "qcmaint_kairos_base_muro_pt":
                    if self.infos_config['database_update_pt'] != '':
                        database_update = self.infos_config['database_update_pt']
                        return database_update
                    else:
                        self.escrever(
                            "- Não foi inserido no arquivo de config o apontamento para o banco Muro update PT")
                        # arquivo.write(
                        #    f"\n{self.data_atual()} - ERRO - Não foi inserido no arquivo de config o apontamento para o banco Muro update PT ")
                case "qcdev_kairos_base_muro_pt":
                    if self.infos_config['database_update_pt'] != '':
                        database_update = self.infos_config['database_update_pt']
                        return database_update
                    else:
                        self.escrever(
                            "- Não foi inserido no arquivo de config o apontamento para o banco Muro update PT")
                        # arquivo.write(
                        #    f"\n{self.data_atual()} - ERRO - Não foi inserido no arquivo de config o apontamento para o banco Muro update PT ")
                case "qcmaint_mdcomune_base_muro":
                    if self.infos_config['database_update_md'] != '':
                        database_update = self.infos_config['database_update_md']
                        return database_update
                    else:
                        self.escrever(
                            "- Não foi inserido no arquivo de config o apontamento para o banco Muro update MD")
                        #    arquivo.write(f"\n{self.data_atual()} - ERRO - Não foi inserido no arquivo de config o apontamento para o banco Muro update MD ")
                case "qcdev_mdcomune_base_muro":
                    if self.infos_config['database_update_md'] != '':
                        database_update = self.infos_config['database_update_md']
                        return database_update
                    else:
                        self.escrever(
                            "- Não foi inserido no arquivo de config o apontamento para o banco Muro update MD")
                    #    arquivo.write(f"\n{self.data_atual()} - ERRO - Não foi inserido no arquivo de config o apontamento para o banco Muro update MD ")
                case _:
                    self.escrever("- Não foi possível achar uma opção compativel com o banco de muro")
                    # arquivo.write(
                    #    f"\n{self.data_atual()} - ERRO - Não foi possível achar uma opção compativel com o banco de muro ")
            return database_update

    def escolher_config_existente(self, app):
            params_dict = ''
            self.infos_config['status'] = False
            config_selecionado = self.combobox.get()

            # Validando o arquivo de config
            try:
                if os.path.isfile("Config\\" + config_selecionado):
                    config_bjt = open("Config\\" + config_selecionado, "r")
                    config_json = config_bjt.read().lower()
                    params_dict = json.loads(config_json)
                else:
                    self.mensagem(f"Não foi possível encontrar um .JSON com esse nome na pasta {self.nomes['diretorio_config']}!")
            except Exception as name_error:
                self.mensagem(f"Existem erros de formatação no arquivo de config escolhido:\n {name_error}")
                self.arquivo_principal.write(f"\n{data_atual()} - INFO - Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente: {name_error} ")
                return
            else:
                try:
                    if params_dict["conexao"]["server"] == '':
                        self.mensagem("O valor do server não foi especificado no config")
                        self.arquivo_principal.write(f"\n{data_atual()} - INFO - O valor do server não foi especificado no config, Informe e tente novamente ")
                        return
                    elif params_dict["conexao"]["username"] == '':
                        self.mensagem("O valor do Username não foi especificado no config")
                        self.arquivo_principal.write(f"\n{data_atual()} - INFO - O valor do Username não foi especificado no config, Informe e tente novamente ")
                        return
                    elif params_dict["conexao"]["password"] == '':
                        self.mensagem("O valor do Password não foi especificado no config")
                        self.arquivo_principal.write(f"\n{data_atual()} - INFO - O valor do Password não foi especificado no config, Informe e tente novamente ")
                        return
                    elif not params_dict["bases_muro"]:
                        self.mensagem("O valor do Base_Muro não foi especificado no config")
                        self.arquivo_principal.write(f"\n{data_atual()} - INFO - O valor do Base_Muro não foi especificado no config, Informe e tente novamente ")
                        return
                except Exception as name_error:
                        self.mensagem(f"Existem erros de formatação no arquivo de config escolhido:\n {name_error}")
                        self.arquivo_principal.write(f"\n{data_atual()} - INFO - Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente: {name_error} ")
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
                        self.mensagem(f"Existem erros de formatação no arquivo de config escolhido:\n {name_error}")
                        self.arquivo_principal.write(f"\n{data_atual()} - INFO - Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente: {name_error} ")
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
                            self.infos_config['server_principal'] = params_dict["configs_restaurar_download"]["server_principal"]
                            self.infos_config['username_principal'] = params_dict["configs_restaurar_download"]["username_principal"]
                            self.infos_config['password_principal'] = params_dict["configs_restaurar_download"]["password_principal"]
                        except Exception as name_error:
                            self.mensagem(f"O config esta estava desatualizado, foram inseridas as novas tags no config:\n {name_error}")
                            self.arquivo_principal.write(f"\n{data_atual()} - INFO - O config esta estava desatualizado, foram inseridas as novas tags no config, configure elas para usar as rotinas {self.nomes['arquivo_download_backup']} e {self.nomes['arquivo_restaurar_banco']}: {name_error}")
                            self.infos_config['server_principal'] = ""
                            self.infos_config['username_principal'] = ""
                            self.infos_config['password_principal'] = ""
                            atualizar_config = open("Config\\" + config_selecionado, "w")
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
                            atualizar_config.write(config_atualizado)
                            atualizar_config.close()
                        try:
                            self.infos_config['redis_qa'] = params_dict["redis_qa"]
                        except Exception as name_error:
                            self.mensagem(f"O config esta estava desatualizado, foram inseridas as novas tags no config:\n {name_error}")
                            self.arquivo_principal.write(
                                f"\n{data_atual()} - INFO - O config esta estava desatualizado, foram inseridas as novas tags no config, configure elas para usar as rotinas {self.nomes['arquivo_download_backup']} e {self.nomes['arquivo_restaurar_banco']}: {name_error}")
                            self.infos_config['redis_qa'] = ""
                            atualizar_config = open("Config\\" + config_selecionado, "w")
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
                            atualizar_config.write(config_atualizado)
                            atualizar_config.close()
            if self.infos_config['status']:
                self.trocar_tela_menu(app)

            return self.infos_config

    def arquivo_existente(self, app, coluna):
        self.arquivo_principal.write(f"\n{data_atual()} - INFO - Tela - Escolher Arquivo Existente")
        opcoes = []
        self.infos_config = dict()

        # listar os arquivos de dentro da pasta
        try:
            arquivos_diretorio = os.listdir(self.nomes['pasta_config'])
        except Exception as name_error:
            self.mensagem(f"Não foi possivel acessar a pasta config: {name_error}")
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
                        self.mensagem(f"Não existe arquivos .json na pasta config")
                        return
                else:
                    self.mensagem(f"Não existe arquivos na pasta config")
                    return

        self.button_config_existente.config(state="disabled")
        self.button_config_novo.config(state="active")
        self.limpar_linha(4)
        self.limpar_linha(5)
        self.limpar_linha(8)

        self.label_lista_arquivos = tk.Label(
            text="Lista de arquivos:"
        )
        self.combobox = ttk.Combobox(
            app,
            values=opcoes,
        )
        self.button_nav_escolher = tk.Button(
            app,
            text="Escolher",
            width=15,
            height=2,
            bg="#ADADAD",
            command=lambda: self.escolher_config_existente(app)
        )
        self.combobox.set(opcoes[0])
        self.label_lista_arquivos.grid(row=4, column=coluna, columnspan=1, pady=(10, 0), sticky="WS")
        self.combobox.grid(row=5, column=coluna, columnspan=1, pady =(0, 10), sticky="WEN")
        self.button_nav_escolher.grid(row=8, column=coluna, columnspan=1)

    def criar_config(self):
        self.arquivo_principal.write(f"\n{data_atual()} - INFO - Tela - Criação de config ")
        nome_escolhido = self.entry.get()
        if nome_escolhido == self.placeholder_text or nome_escolhido == "":
            self.mensagem("O campo nome deverá ser preenchido")
            return
        else:

            nome_config = nome_escolhido + ".json"

            if os.path.exists("Config\\" + nome_config):
                self.mensagem("Já existe um arquivo .json com o mesmo nome\nInforme outro nome para o arquivo config")
            else:
                arquivo_config = open("Config\\" + nome_config, "a")
                arquivo_config.write("""{
    "database_update_br": "",
    "database_update_mx": "",
    "database_update_pt": "",
    "database_update_md": "",
    "bases_muro": [],
    "conexao": {
        "server": "",
        "username": "",
        "password": ""
    },
    "configs_restaurar_download": {
        "server_principal": "",
        "username_principal": "",
        "password_principal": ""
    },
	"redis_qa": [
		{
		"nome_redis": "",
		"ip": "",
		"port": ""
		},
		{
		"nome_redis": "",
		"ip": "",
		"port": ""
		}
	]
}""")
                arquivo_config.close()
                self.mensagem("Novo config criado com sucesso")
                self.arquivo_principal.write(f"\n{data_atual()} - INFO - Novo config criado com sucesso, configure e selecione para ser utilizado ")

    def arquivo_novo(self, app, coluna):
        self.arquivo_principal.write(f"\n{data_atual()} - INFO - Tela - Criar Arquivo config")
        self.button_config_novo.config(state="disabled")
        self.button_config_existente.config(state="active")

        self.limpar_linha(4)
        self.limpar_linha(5)
        self.limpar_linha(8)

        self.button_nav_criar = tk.Button(
            app,
            text="Criar",
            name="button_criar",
            width=15,
            height=2,
            bg="#ADADAD",
            command=lambda: self.criar_config()
        )
        self.input_placeholder(4, 5,  coluna, "Insira o nome para o arquivo...", "Nome do arquivo:")
        self.button_nav_criar.grid(row=8, column=coluna, columnspan=1)

    def restaurar_banco(self):
        self.arquivo_principal.write(f"\n{data_atual()} - INFO - Tela - Restaurar Backup")
        self.button_restaurar_inicio.config(state='disabled')
        self.button_restaurar_voltar.config(state='disabled')
        self.entry.config(state='disabled')
        pula_linha = validar_linha(self.nomes['arquivo_restaurar_banco'])
        cnxnrs = ''
        cursorrs = ''

        nome_banco_restaurado = self.entry.get()

        if nome_banco_restaurado == self.placeholder_text or nome_banco_restaurado == "":
            self.escrever("- O campo acima deverá ser preenchido")
            self.button_restaurar_inicio.config(state='active')
            self.button_restaurar_voltar.config(state='active')
            self.entry.config(state='normal')
            return
        else:
            self.arquivo_restauracao.write(f"{pula_linha}{data_atual()} - INFO - Inserido o nome do banco apresentado no discord: {nome_banco_restaurado} ")
            self.arquivo_restauracao.write(f"\n{data_atual()} - INFO - Escolhido o servidor: {self.infos_config['server']} ")

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
                self.escrever("- Falha ao tentar executar o comando de criação de device de backup " + str(err))
                self.arquivo_restauracao.write(f"\n{data_atual()} - ERRO - Falha ao tentar executar o comando de criação de device de backup: {err} ")
            else:
                cursorrs.commit()
                self.escrever(f"- Sucesso ao realizar Criar Device de Backup")
                self.arquivo_restauracao.write(f"\n{data_atual()} - INFO - Sucesso ao realizar Criar Device de Backup ")
                status_etapa1 = True
                for incs in range(len(result_criar_device)):
                    separados = result_criar_device[0][1].split("]")
                    mensagem = separados[3]
                    self.arquivo_restauracao.write(f"\n{data_atual()} - INFO - Comando(Criação Device) -  Mensagem SQL: {mensagem} ")

            if status_etapa1:
                try:
                    cursorrs = cnxnrs.cursor()
                    cursorrs.execute(comando_restaurar_banco)
                except (Exception or pyodbc.DatabaseError) as err:
                    self.escrever("- Falha ao tentar executar o comando de restauração de banco: " + str(err))
                    self.arquivo_restauracao.write(f"\n{data_atual()} - ERRO - Falha ao tentar executar o comando de restauração de banco: {err} ")
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
                    self.escrever(f"- Sucesso ao realizar a restauração do banco")
                    self.arquivo_restauracao.write(f"\n{data_atual()} - INFO - Sucesso ao realizar a restauração do banco ")

                    tam = len(mensagens) - 3
                    for incs in range(posicao):
                        self.escrever(f"- Comando(Restauração DB) -  Mensagem SQL: {mensagens[tam]}  ")
                        self.arquivo_restauracao.write(f"\n{data_atual()} - INFO - Comando(Restauração DB) -  Mensagem SQL: {mensagens[tam]} ")
                        tam += 1

                    try:
                        cursorrs.execute(comando_ativar_banco)
                        result_ativar_banco = cursorrs.messages
                    except (Exception or pyodbc.DatabaseError) as err:
                        self.escrever("- Falha ao tentar executar o comando de Ativação do banco: " + str(err))
                        self.arquivo_restauracao.write(f"\n{data_atual()} - ERRO - Falha ao tentar executar o comando de Ativação do banco: {err} ")
                    else:
                        tam_result = len(result_ativar_banco) - 1
                        while tam_result < len(result_ativar_banco):
                            separados = result_ativar_banco[tam_result][1].split("]")
                            mensagem = separados[3]
                            self.escrever(f"- Comando(Ativação DB) -  Mensagem SQL: {mensagem}  ")
                            self.arquivo_restauracao.write(f"\n{data_atual()} - INFO - Comando(Ativação DB) -  Mensagem SQL: {mensagem} ")
                            tam_result += 1

                        try:
                            cursorrs.execute(comando_checar_banco)
                            result_check = cursorrs.messages
                        except (Exception or pyodbc.DatabaseError) as err:
                            self.escrever("- Falha ao tentar executar o comando de checagem do banco: " + str(err))
                            self.arquivo_restauracao.write(f"\n{data_atual()} - ERRO - Falha ao tentar executar o comando de checagem do banco: {err} ")
                        else:
                            looping = True
                            tam_result = len(result_check) - 2
                            while looping:
                                if tam_result < len(result_check):
                                    separados = result_check[tam_result][1].split("]")
                                    mensagem = separados[3]
                                    self.escrever(f"- Comando(Checagem DB) - Mensagem SQL: {mensagem}")
                                    self.arquivo_restauracao.write(f"\n{data_atual()} - INFO - Comando(Checagem DB) - Mensagem SQL: {mensagem} ")
                                    tam_result += 1
                                else:
                                    looping = False
                            try:
                                cursorrs.execute(comando_excluir_device)
                                result_excluir_device = cursorrs.messages
                            except (Exception or pyodbc.DatabaseError) as err:
                                self.escrever("- Falha ao tentar executar o comando de checagem do banco: " + str(err))
                                self.arquivo_restauracao.write(f"\n{data_atual()} - ERRO - Falha ao tentar executar o comando de checagem do banco: {err} ")
                            else:
                                for incs in range(len(result_excluir_device)):
                                    separados = result_excluir_device[0][1].split("]")
                                    mensagem = separados[3]
                                    self.escrever(f"- Comando(Exclusão Device) -  Mensagem SQL: {mensagem}  ")
                                    self.arquivo_restauracao.write(f"\n{data_atual()} - INFO - Comando(Exclusão Device) -  Mensagem SQL: {mensagem} ")

                                try:
                                    cursorrs.execute(comando_primeiro_script)
                                    associar_owner = cursorrs.messages
                                except (Exception or pyodbc.DatabaseError) as err:
                                    self.escrever("- Falha ao tentar executar o comando de associação do Owner: " + str(err))
                                    self.arquivo_restauracao.write(f"\n{data_atual()} - ERRO - Falha ao tentar executar o comando de associação do Owner:  {err} ")
                                else:
                                    separados = associar_owner[0][1].split("]")
                                    mensagem = separados[3]
                                    self.escrever(f"- Comando(Associar Owner) - Mensagem SQL: {mensagem}")
                                    self.arquivo_restauracao.write(f"\n{data_atual()} - INFO - Comando(Script Associar Owner) - Mensagem SQL: {mensagem} ")

                                    try:
                                        cursorrs.execute(comando_segundo_script)
                                        compatibilidade = cursorrs.messages
                                    except (Exception or pyodbc.DatabaseError) as err:
                                        self.escrever("- Falha ao tentar executar o comando " + str(err))
                                        self.arquivo_restauracao.write(f"\n{data_atual()} - ERRO - Falha ao tentar executar o comando: {err} ")
                                    else:
                                        separados = compatibilidade[0][1].split("]")
                                        mensagem = separados[3]
                                        self.escrever(f"- Comando(Compatibilidade) - Mensagem SQL: {mensagem}")
                                        self.arquivo_restauracao.write(f"\n{data_atual()} - INFO - Comando(Script Compatibilidade) - Mensagem SQL: {mensagem} ")
                cursorrs.close()

        self.escrever("- Processo finalizado")
        self.arquivo_restauracao.write(f"\n{data_atual()} - INFO - Processo finalizado")
        self.arquivo_restauracao.close()
        self.entry.config(state='normal')
        self.button_restaurar_inicio.config(state='active')
        self.button_restaurar_voltar.config(state='active')

    def download_backup(self):
        self.arquivo_principal.write(f"\n{data_atual()} - INFO - Tela - Download Backup ")
        self.button_download_inicio.config(state='disabled')
        self.button_download_voltar.config(state='disabled')
        self.entry.config(state='disabled')
        pula_linha = validar_linha(self.nomes['arquivo_download_backup'])
        self.arquivo_download.write(f"{pula_linha}{data_atual()} - INFO - Inicio da operação Download Backup ")
        endereco_download = self.entry.get()
        self.arquivo_download.write(f"\n{data_atual()} - INFO - Inserida a URL de Download: {endereco_download} ")

        if endereco_download == self.placeholder_text or endereco_download == "":
            self.escrever("- O campo acima deverá ser preenchido")
            self.button_download_inicio.config(state='active')
            self.button_download_voltar.config(state='active')
            self.entry.config(state='normal')
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
                self.escrever("- Falha ao tentar executar o comando " + str(err))
                self.arquivo_download.write(f"\n{data_atual()} - ERRO - Falha ao tentar executar o comando: {err} ")
            else:
                cursorrp1.commit()

                self.arquivo_download.write(f"\n{data_atual()} - INFO - Sucesso ao realizar Download do backup ")
                self.arquivo_download.write(f"\n{data_atual()} - INFO - Resultado:")

                for incs in range(len(result)):
                    semi_separado = (str(result[incs])).split("'")
                    if len(semi_separado) > 1:
                        separado = semi_separado[1].split("(")
                        limpo = separado[0]
                        self.escrever('- ' + str(limpo))
                        self.arquivo_download.write(f"\n{data_atual()} - INFO - {limpo}")

                    else:
                        limpo = semi_separado[0]
                        self.escrever("- " + str(limpo))
                        self.arquivo_download.write(f"\n{data_atual()} - INFO - {limpo}")

                cursorrp1.close()

        self.escrever("- Processo finalizado")
        self.arquivo_download.write(f"\n{data_atual()} - INFO - Processo finalizado ")
        self.arquivo_download.close()
        self.entry.config(state='normal')
        self.button_download_inicio.config(state='active')
        self.button_download_voltar.config(state='active')

    def limpar_todos_redis(self):
        self.button_atualizacao_inicio.config(state='disabled')
        self.button_atualizacao_voltar.config(state='disabled')
        pula_linha = validar_linha(self.nomes['arquivo_redis'])
        self.arquivo_redis.write(f"{pula_linha}{data_atual()} - INFO - Inicio da operação Limpar todos Redis ")
        for red_atual in self.infos_config['redis_qa']:
            self.escrever(f"- Iniciado processo no Redis {red_atual['nome_redis']}")
            self.arquivo_redis.write(f"\n{data_atual()} - INFO - Iniciado processo no Redis {red_atual['nome_redis']} ")
            redis_host = red_atual['ip']  # ou o endereço do seu servidor Redis
            redis_port = red_atual['port']  # ou a porta que o seu servidor Redis está ouvindo

            # Criando uma instância do cliente Redis
            redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

            try:
                # Executando o comando FLUSHALL
                redis_client.flushall()
            except Exception as err:
                self.escrever(f"- Processo finalizado com falha: {err}")
                self.arquivo_redis.write(f"\n{data_atual()} - INFO - Processo finalizado com falha: {err}")
            else:
                self.escrever(f"- FLUSHALL executado com sucesso no redis")
                self.arquivo_redis.write(f"\n{data_atual()} - INFO - FLUSHALL executado com sucesso no redis")
        self.escrever("- Processo finalizado")
        self.arquivo_redis.write(f"\n{data_atual()} - INFO - Processo finalizado ")
        self.button_atualizacao_inicio.config(state='active')
        self.button_atualizacao_voltar.config(state='active')
        self.arquivo_redis.close()

    def limpar_redis_especifico(self):
        self.combobox.config(state='disabled')
        self.button_redis_inicio.config(state='disabled')
        self.button_redis_voltar.config(state='disabled')
        pula_linha = validar_linha(self.nomes['arquivo_redis'])
        self.arquivo_redis.write(f"{pula_linha}{data_atual()} - INFO - Inicio da operação Limpar Redis especifico")
        redis_selecionado = self.combobox.get()
        self.escrever(f"- Iniciado processo no Redis {redis_selecionado}")
        self.arquivo_redis.write(f"\n{data_atual()} - INFO - Iniciado processo no Redis {redis_selecionado} ")
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
            self.escrever(f"- Processo finalizado com falha: {err}")
            self.arquivo_redis.write(f"\n{data_atual()} - INFO - Processo finalizado com falha: {err}")
        else:
            self.escrever(f"- FLUSHALL executado com sucesso no redis")
            self.arquivo_redis.write(f"\n{data_atual()} - INFO - FLUSHALL executado com sucesso no redis")
        self.escrever("- Processo finalizado")
        self.arquivo_redis.write(f"\n{data_atual()} - INFO - Processo finalizado ")
        self.button_redis_inicio.config(state='active')
        self.button_redis_voltar.config(state='active')
        self.combobox.config(state='active')
        self.arquivo_redis.close()

    def menu_restaurar_banco(self):
        self.arquivo_restauracao = open(f"Log\\{self.nomes['arquivo_restaurar_banco']}.txt", "a")
        self.infos_config['status'] = True
        while True:
            if self.infos_config['status']:
                try:
                    if self.infos_config['server_principal'] != "":
                        self.iniciar_processo_restaurar()
                        break
                    else:
                        self.escrever(f"- A tag de server_principal parece estar vazia")
                        self.arquivo_restauracao.write(f"\n{data_atual()} - INFO - A tag de server_principal parece estar vazia, preencha e recarregue o config novamente ")
                        self.infos_config['status'] = False
                except (Exception or pyodbc.DatabaseError) as err:
                    self.escrever(f"- Falha ao tentar ler o arquivo {err}")
                    self.arquivo_restauracao.write(f"\n{data_atual()} - ERRO - Falha ao tentar ler o arquivo, corrija e tente novamente: {err} ")
                    self.infos_config['status'] = False
            else:
                self.escrever(f"- Processo finalizado")
                self.arquivo_restauracao.close()
                break

    def menu_redis_todos(self):
        self.arquivo_redis = open(f"Log\\{self.nomes['arquivo_redis']}.txt", "a")
        self.infos_config['status'] = True
        while True:
            if self.infos_config['status']:
                try:
                    if self.infos_config['redis_qa'][0]["nome_redis"] != "":
                        self.iniciar_processo_limpar_redis_todos()
                        break
                    else:
                        self.escrever(f"- A tag de redis_qa parece estar vazia")
                        self.arquivo_redis.write(f"\n{data_atual()} - INFO - A tag de redis_qa parece estar vazia, preencha e recarregue o config novamente ")
                        self.infos_config['status'] = False
                except (Exception or pyodbc.DatabaseError) as err:
                    self.escrever(f"- Falha ao tentar ler o arquivo {err}")
                    self.arquivo_redis.write(f"\n{data_atual()} - ERRO - Falha ao tentar ler o arquivo, corrija e tente novamente: {err} ")
                    self.infos_config['status'] = False
                    self.arquivo_redis.close()
            else:
                self.escrever(f"- Processo finalizado")
                self.arquivo_redis.close()
                break

    def menu_redis_especifico(self):
        self.arquivo_redis = open(f"Log\\{self.nomes['arquivo_redis']}.txt", "a")
        self.infos_config['status'] = True
        while True:
            if self.infos_config['status']:
                try:
                    if self.infos_config['redis_qa'][0]["nome_redis"] != "":
                        self.iniciar_processo_limpar_redis_especifico()
                        break
                    else:
                        self.escrever(f"- A tag de redis_qa parece estar vazia")
                        self.arquivo_redis.write(f"\n{data_atual()} - INFO - A tag de redis_qa parece estar vazia, preencha e recarregue o config novamente ")
                        self.infos_config['status'] = False
                except (Exception or pyodbc.DatabaseError) as err:
                    self.escrever(f"- Falha ao tentar ler o arquivo {err}")
                    self.arquivo_redis.write(f"\n{data_atual()} - ERRO - Falha ao tentar ler o arquivo, corrija e tente novamente: {err} ")
                    self.infos_config['status'] = False
                    self.arquivo_redis.close()
            else:
                self.escrever(f"- Processo finalizado")
                self.arquivo_redis.close()
                break

    def menu_download_backup(self):
        self.arquivo_download = open(f"Log\\{self.nomes['arquivo_download_backup']}.txt", "a")
        self.infos_config['status'] = True
        while True:
            if self.infos_config['status']:
                try:
                    if self.infos_config['server_principal'] != "":
                        self.iniciar_processo_download()
                        break
                    else:
                        self.escrever(f"- A tag de server_principal parece estar vazia")
                        self.arquivo_download.write(f"\n{data_atual()} - INFO - A tag de server_principal parece estar vazia, preencha e recarregue o config novamente ")
                        self.infos_config['status'] = False
                except (Exception or pyodbc.DatabaseError) as err:
                    self.escrever(f"- Falha ao tentar ler o arquivo {err}")
                    self.arquivo_download.write(f"\n{data_atual()} - ERRO - Falha ao tentar ler o arquivo, corrija e tente novamente: {err} ")
                    self.infos_config['status'] = False
            else:
                self.escrever(f"- Processo finalizado")
                self.arquivo_download.close()
                break

    def iniciar_processo_limpar_redis_especifico(self):
        self.escrever(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        try:
            self.thread = threading.Thread(target=self.limpar_redis_especifico)
            self.thread.start()
        except threading.excepthook as error:
            self.escrever(f"- Processo finalizado com falha \n {error}")

    def iniciar_processo_limpar_redis_todos(self):
        self.escrever(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        try:
            self.thread = threading.Thread(target=self.limpar_todos_redis)
            self.thread.start()
        except threading.excepthook as error:
            self.escrever(f"- Processo finalizado com falha \n {error}")

    def iniciar_processo_atualizacao(self):
        self.escrever(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        try:
            self.thread = threading.Thread(target=self.buscar_versions)
            self.thread.start()
        except threading.excepthook as error:
            self.escrever(f"Processo finalizado com falha \n {error}")

    def iniciar_processo_replicar(self):
        self.escrever(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        try:
            self.thread = threading.Thread(target=self.replicar_version)
            self.thread.start()
        except threading.excepthook as error:
            self.escrever(f"Processo finalizado com falha \n {error}")

    def iniciar_processo_download(self):
        self.escrever(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        try:
            self.thread = threading.Thread(target=self.download_backup)
            self.thread.start()
        except threading.excepthook as error:
            self.escrever(f"Processo finalizado com falha \n {error}")

    def iniciar_processo_restaurar(self):
        self.escrever(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        try:
            self.thread = threading.Thread(target=self.restaurar_banco)
            self.thread.start()
        except threading.excepthook as error:
            self.escrever(f"Processo finalizado com falha \n {error}")

    def iniciar_processo_manipula_banco(self):
        self.escrever(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        try:
            self.thread = threading.Thread(target=self.manipular_banco_muro)
            self.thread.start()
        except threading.excepthook as error:
            self.escrever(f"Processo finalizado com falha \n {error}")

    def trocar_tela_redis_especifico(self, app):
        self.remover_widget(app, '*', '*')
        self.tela_limpar_redis_especifico(app, self.version, self.coluna)

    def trocar_tela_redis_todos(self, app):
        self.remover_widget(app, '*', '*')
        self.tela_limpar_redis_todos(app, self.version, self.coluna)

    def trocar_tela_ferramentas(self, app):
        self.remover_widget(app, '*', '*')
        self.tela_ferramentas(app, self.version, self.coluna)

    def trocar_tela_ferramentas_bancos(self, app):
        self.remover_widget(app, '*', '*')
        self.tela_ferramentas_bancos(app, self.version, self.coluna)

    def trocar_tela_ferramentas_redis(self, app):
        self.remover_widget(app, '*', '*')
        self.tela_ferramentas_redis(app, self.version, self.coluna)

    def trocar_tela_menu(self, app):
        self.remover_widget(app, '*', '*')
        self.tela_menu(app, self.version, self.coluna)

    def trocar_tela_config(self, app):
        self.remover_widget(app, '*', '*')
        self.tela_config(app, self.version, self.coluna)

    def trocar_tela_busca_muro(self, app):
        self.remover_widget(app, '*', '*')
        self.tela_busca_muro(app, self.version, self.coluna)

    def trocar_tela_download_backup(self, app):
        self.remover_widget(app, '*', '*')
        self.tela_download_backup(app, self.version, self.coluna)

    def trocar_tela_restaurar_backup(self, app):
        self.remover_widget(app, '*', '*')
        self.tela_restaurar_backup(app, self.version, self.coluna)

    def trocar_tela_buscar_versions(self, app):
        self.remover_widget(app, '*', '*')
        self.tela_buscar_versions(app, self.version, self.coluna)

    def trocar_tela_replicar_version(self, app):
        self.remover_widget(app, '*', '*')
        self.tela_replicar_version_muro(app, self.version, self.coluna)

    def tela_limpar_redis_especifico(self, app, version, coluna):
        titulo = "LIMPAR REDIS ESPECIFICOS"
        app.title("MSS - " + version + " - " + titulo)
        opcoes = []

        if self.infos_config["redis_qa"]:
            for red_nome in self.infos_config["redis_qa"]:
                if self.infos_config['redis_qa'][0]["nome_redis"] != "":
                    opcoes.append(red_nome["nome_redis"])

        else:
            self.mensagem(f"Não existe arquivos .json na pasta config")
            return

        self.label_lista_redis = tk.Label(
            text="Redis:"
        )
        self.combobox = ttk.Combobox(
            app,
            values=opcoes,
        )
        self.button_redis_inicio = tk.Button(
            app,
            text="Iniciar",
            width=25,
            height=2,
            command=lambda: self.menu_redis_especifico()
        )
        self.button_redis_voltar = tk.Button(
            app,
            text="Voltar",
            width=25,
            height=2,
            command=lambda: self.trocar_tela_ferramentas_redis(app)
        )

        self.escrever_titulos(self.app, titulo, 0, coluna)
        if len(opcoes) > 0:
            self.combobox.set(opcoes[0])
        self.label_lista_redis.grid(row=1, column=coluna, columnspan=1, pady=(10, 0), sticky="WS")
        self.combobox.grid(row=2, column=coluna, columnspan=1, pady =(0, 10), sticky="WEN")
        self.caixa_texto(3, 4, coluna, "Saida:")
        self.button_redis_inicio.grid(row=5, column=coluna, pady=(10, 0))
        self.button_redis_voltar.grid(row=6, column=coluna, pady=(0, 10))

    def tela_limpar_redis_todos(self, app, version, coluna):
        titulo = "LIMPAR TODOS OS REDIS"
        app.title("MSS - " + version + " - " + titulo)

        self.button_atualizacao_inicio = tk.Button(
            app,
            text="Iniciar",
            width=25,
            height=2,
            command=lambda: self.menu_redis_todos()
        )
        self.button_atualizacao_voltar = tk.Button(
            app,
            text="Voltar",
            width=25,
            height=2,
            command=lambda: self.trocar_tela_ferramentas_redis(app)
        )

        self.escrever_titulos(self.app, titulo, 0, coluna)
        self.caixa_texto(1, 2, coluna, "Saida:")
        self.button_atualizacao_inicio.grid(row=3, column=coluna,  pady=(10, 0))
        self.button_atualizacao_voltar.grid(row=4, column=coluna)

    def tela_restaurar_backup(self, app, version, coluna):
        titulo = "Restaurar Backup"
        app.title("MSS - " + version + " - " + titulo)

        self.button_restaurar_inicio = tk.Button(
            app,
            text="Iniciar",
            width=25,
            height=2,
            command=lambda: self.menu_restaurar_banco()
        )
        self.button_restaurar_voltar = tk.Button(
            app,
            text="Voltar",
            width=25,
            height=2,
            command=lambda: self.trocar_tela_menu(app)
        )

        self.escrever_titulos(self.app, titulo, 0, coluna)
        self.input_placeholder(1, 2, coluna, " Insira o nome do banco desejado (KAIROS_BASE_123456789)", "Nome do banco:")
        self.caixa_texto(3, 4, coluna, "Saida:")
        self.button_restaurar_inicio.grid(row=5, column=coluna, pady=(10, 0))
        self.button_restaurar_voltar.grid(row=6, column=coluna, pady=(0, 10))

    def tela_download_backup(self, app, version, coluna):
        titulo = "Download Backup"
        app.title("MSS - " + version + " - " + titulo)

        self.button_download_inicio = tk.Button(
            app,
            text="Iniciar",
            width=25,
            height=2,
            command=lambda: self.menu_download_backup()
        )
        self.button_download_voltar = tk.Button(
            app,
            text="Voltar",
            width=25,
            height=2,
            command=lambda: self.trocar_tela_menu(app)
        )

        self.escrever_titulos(self.app, titulo, 0, coluna)
        self.input_placeholder(1, 2, coluna, "URL DO BACKUP", "Endereço URL:")
        self.caixa_texto(3, 4, coluna, "Saida:")
        self.button_download_inicio.grid(row=5, column=coluna, pady=(10, 0))
        self.button_download_voltar.grid(row=6, column=coluna, pady=(0, 10))

    def tela_busca_muro(self, app, version, coluna):
        titulo = "BUSCAR BANCOS"
        app.title("MSS - " + version + " - " + titulo)

        self.button_busca_inicio = tk.Button(
            app,
            text="Iniciar",
            width=25,
            height=2,
            command=lambda: self.iniciar_processo_manipula_banco()
        )
        self.button_busca_voltar = tk.Button(
            app,
            text="Voltar",
            width=25,
            height=2,
            command=lambda: self.trocar_tela_ferramentas_bancos(app)
        )

        self.escrever_titulos(self.app, titulo, 0, coluna)
        self.input_placeholder(1, 2, coluna, "Insira o version para downgrade...", "Version:")
        self.caixa_texto(3, 4, coluna, "Saida:")
        self.button_busca_inicio.grid(row=5, column=coluna, pady=(10, 0))
        self.button_busca_voltar.grid(row=6, column=coluna, pady=(0, 10))

    def tela_buscar_versions(self, app, version, coluna):
        titulo = "CONSULTAR VERSIONS"
        app.title("MSS - " + version + " - " + titulo)

        self.button_atualizacao_inicio = tk.Button(
            app,
            text="Iniciar",
            width=25,
            height=2,
            command=lambda: self.iniciar_processo_atualizacao()
        )
        self.button_atualizacao_voltar = tk.Button(
            app,
            text="Voltar",
            width=25,
            height=2,
            command=lambda: self.trocar_tela_ferramentas_bancos(app)
        )

        self.escrever_titulos(self.app, titulo, 0, coluna)
        self.caixa_texto(1, 2, coluna, "Saida:")
        self.button_atualizacao_inicio.grid(row=3, column=coluna,  pady=(10, 0))
        self.button_atualizacao_voltar.grid(row=4, column=coluna)

    def tela_replicar_version_muro(self, app, version, coluna):
        titulo = "REPLICAR VERSIONS"
        app.title("MSS - " + version + " - " + titulo)

        self.button_replicar_inicio = tk.Button(
            app,
            text="Iniciar",
            width=25,
            height=2,
            command=lambda: self.iniciar_processo_replicar()
        )
        self.button_replicar_voltar = tk.Button(
            app,
            text="Voltar",
            width=25,
            height=2,
            command=lambda: self.trocar_tela_ferramentas_bancos(app)
        )

        self.escrever_titulos(self.app, titulo, 0, coluna)
        self.caixa_texto(1, 2, coluna, "Saida:")
        self.button_replicar_inicio.grid(row=3, column=coluna,  pady=(10, 0))
        self.button_replicar_voltar.grid(row=4, column=coluna)

    def tela_ferramentas_bancos(self, app, version, coluna):
        titulo = "FERRAMENTAS DE BANCO"
        app.title("MSS - " + version + " - " + titulo)

        self.button_ferramenta_busca_banco = tk.Button(
            app,
            text="Buscar Bancos",
            width=25,
            height=2,
            command=lambda: self.trocar_tela_busca_muro(app)
        )
        self.button_ferramenta_buscar_versions = tk.Button(
            app,
            text="Buscar Version's",
            width=25,
            height=2,
            command=lambda: self.trocar_tela_buscar_versions(app)
        )
        self.button_ferramenta_replicar_version = tk.Button(
            app,
            text="Replicar version",
            width=25,
            height=2,
            command=lambda: self.trocar_tela_replicar_version(app)
        )
        self.button_ferramenta_config = tk.Button(
            app,
            text="Trocar configuração",
            width=25,
            height=2,
            command=lambda: self.trocar_tela_config(app)
        )
        self.button_ferramenta_voltar = tk.Button(
            app,
            text="Voltar - Ferramentas",
            width=25,
            height=2,
            command=lambda: self.trocar_tela_ferramentas(app)
        )
        self.button_ferramenta_sair = tk.Button(
            app,
            text="Sair",
            width=25,
            height=2,
            command=lambda: self.finalizar()
        )
        self.escrever_titulos(self.app, titulo, 0, coluna)
        self.button_ferramenta_busca_banco.grid(row=1, column=coluna)
        self.button_ferramenta_buscar_versions.grid(row=2, column=coluna)
        self.button_ferramenta_replicar_version.grid(row=3, column=coluna)
        self.button_ferramenta_config.grid(row=4, column=coluna)
        self.button_ferramenta_voltar.grid(row=5, column=coluna)
        self.button_ferramenta_sair.grid(row=6, column=coluna)

    def tela_ferramentas_redis(self, app, version, coluna):
        titulo = "FERRAMENTAS DE REDIS"
        app.title("MSS - " + version + " - " + titulo)

        self.button_ferramenta_busca_banco = tk.Button(
            app,
            text="Limpar todos os redis",
            width=25,
            height=2,
            command=lambda: self.trocar_tela_redis_todos(app)
        )
        self.button_ferramenta_buscar_versions = tk.Button(
            app,
            text="Limpar Redis especifico",
            width=25,
            height=2,
            command=lambda: self.trocar_tela_redis_especifico(app)
        )
        self.button_ferramenta_config = tk.Button(
            app,
            text="Trocar configuração",
            width=25,
            height=2,
            command=lambda: self.trocar_tela_config(app)
        )
        self.button_ferramenta_voltar = tk.Button(
            app,
            text="Voltar - Ferramentas",
            width=25,
            height=2,
            command=lambda: self.trocar_tela_ferramentas(app)
        )
        self.button_ferramenta_sair = tk.Button(
            app,
            text="Sair",
            width=25,
            height=2,
            command=lambda: self.finalizar()
        )
        self.escrever_titulos(self.app, titulo, 0, coluna)
        self.button_ferramenta_busca_banco.grid(row=1, column=coluna)
        self.button_ferramenta_buscar_versions.grid(row=2, column=coluna)
        self.button_ferramenta_config.grid(row=3, column=coluna)
        self.button_ferramenta_voltar.grid(row=4, column=coluna)
        self.button_ferramenta_sair.grid(row=5, column=coluna)

    def tela_ferramentas(self, app, version, coluna):
        titulo = "FERRAMENTAS"
        app.title("MSS - " + version + " - " + titulo)

        self.button_menu_ferramentas = tk.Button(
            app,
            text="Ferramentas de Bancos",
            width=25,
            height=2,
            command=lambda: self.trocar_tela_ferramentas_bancos(app)
        )
        self.button_menu_ferramentas_redis = tk.Button(
            app,
            text="Ferramentas Redis",
            width=25,
            height=2,
            command=lambda: self.trocar_tela_ferramentas_redis(app)
        )
        self.button_menu_Voltar = tk.Button(
            app,
            text="Voltar - Menu",
            width=25,
            height=2,
            command=lambda: self.trocar_tela_menu(app)
        )
        self.button_menu_sair = tk.Button(
            app,
            text="Sair",
            width=25,
            height=2,
            command=lambda: self.finalizar()
        )

        self.escrever_titulos(self.app, titulo, 0, coluna)
        self.button_menu_ferramentas.grid(row=1, column=coluna)
        self.button_menu_ferramentas_redis.grid(row=2, column=coluna)
        self.button_menu_Voltar.grid(row=3, column=coluna)
        self.button_menu_sair.grid(row=4, column=coluna)

    def tela_menu(self, app, version, coluna):
        titulo = "Menu"
        app.title("MSS - " + version + " - " + titulo)

        self.button_menu_ferramentas = tk.Button(
            app,
            text="Ferramentas",
            width=25,
            height=2,
            command=lambda: self.trocar_tela_ferramentas(app)
        )
        self.button_menu_download = tk.Button(
            app,
            text="Download Backup",
            width=25,
            height=2,
            command=lambda: self.trocar_tela_download_backup(app)
        )
        self.button_menu_restaurar = tk.Button(
            app,
            text="Restaurar Backup",
            width=25,
            height=2,
            command=lambda: self.trocar_tela_restaurar_backup(app)
        )
        self.button_menu_config = tk.Button(
            app,
            text="Trocar configuração",
            width=25,
            height=2,
            command=lambda: self.trocar_tela_config(app)
        )
        self.button_menu_sair = tk.Button(
            app,
            text="Sair",
            width=25,
            height=2,
            command=lambda: self.finalizar()
        )
        self.escrever_titulos(self.app, titulo, 0, coluna)
        self.button_menu_ferramentas.grid(row=1, column=coluna)
        self.button_menu_download.grid(row=2, column=coluna)
        self.button_menu_restaurar.grid(row=3, column=coluna)
        self.button_menu_config.grid(row=4, column=coluna)
        self.button_menu_sair.grid(row=5, column=coluna)

    def tela_config(self, app, version, coluna):
        self.arquivo_principal.write(f"\n{data_atual()} - INFO - Tela - CONFIGURAÇÃO")
        titulo = "CONFIGURAÇÃO"
        app.title("MSS - " + version + " - " + titulo)

        self.button_config_existente = tk.Button(
            app,
            text="Escolher arquivo Config",
            width=25,
            height=2,
            command=lambda: self.arquivo_existente(app, coluna)
        )
        self.button_config_novo = tk.Button(
            app,
            text="Novo arquivo Config",
            width=25,
            height=2,
            command=lambda: self.arquivo_novo(app, coluna)
        )
        self.button_config_sair = tk.Button(
            app,
            text="sair",
            width=25,
            height=2,
            command=lambda: self.finalizar()
        )

        self.escrever_titulos(self.app, titulo, 0, coluna)
        self.button_config_existente.grid(row=1, column=coluna, sticky="WE")
        self.button_config_novo.grid(row=2, column=coluna, sticky="WE")
        self.button_config_sair.grid(row=3, column=coluna, sticky="WE")

    def tela(self):
        self.app = tk.Tk()
        self.largura = 420
        self.altura = 420

        pos_wid = self.app.winfo_screenwidth()
        pos_hei = self.app.winfo_screenheight()
        self.metade_wid = int((pos_wid / 2) - (self.largura / 2))
        self.metade_hei = int((pos_hei / 2) - (self.altura / 2))
        self.app.geometry(f"{self.largura}x{self.altura}+{self.metade_wid}+{self.metade_hei}")
        self.circulo = []
        self.status_thread = False
        menu = tk.Menu(self.app)
        self.app.config(menu=menu)

        self.app.grid_rowconfigure(0, weight=1)
        self.app.grid_rowconfigure(10, weight=1)
        self.app.grid_columnconfigure(0, weight=1)
        self.app.grid_columnconfigure(5, weight=1)


        return self.app

    def main(self):
        validar_diretorio(self.nomes, self.mensagem)

        # Criar o arquivo de log pricipal
        self.arquivo_principal = open(f"{self.nomes['diretorio_log']}\\{self.nomes['arquivo_base_muro']}.txt", "a")
        pula_linha = validar_linha(self.nomes['arquivo_base_muro'])

        # Data/hora inicio do programa
        self.arquivo_principal.write(f"{pula_linha}{data_atual()} - INFO - Programa iniciado")

        # Validar atualização do programa
        self.atualizador()

        # Versão atual do programa
        self.arquivo_principal.write(f"\n{data_atual()} - INFO - Versão:  {self.version}")

        self.app = self.tela()
        self.app.protocol("WM_DELETE_WINDOW", self.finalizar)
        self.tela_config(self.app, self.version, self.coluna)

        self.app.mainloop()


prog = Aplicativo()