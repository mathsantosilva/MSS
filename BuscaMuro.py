# coding: utf-8
from tkinter import ttk
import datetime
import json
import os
import pyodbc
from tkinter import *
from tkinter.ttk import *

def data_atual():
   data_hora =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
   return data_hora


def manipular_bancomuro(server, username, password, database_update_br, database_update_mx, database_update_pt, database_update_md, bases_muro):

    arquivo = open("Log\Log-manipularbancomuro.txt", "a")

    print(f"\n - Inicio da operação Busca muro {data_atual()}")
    arquivo.write(f"{data_atual()} - INFO - Inicio da operação Busca muro \n")

    versaodatabases = input("- Especifique para qual versão quer fazer o downgrade: ")

    print(f"- Version para downgrade: {versaodatabases}")
    arquivo.write(f"{data_atual()} - INFO - Version para downgrade: {versaodatabases} \n")

    # Pegar a lista de bancos da instancia
    print(f"\n - Iniciando a busca dos bancos na instância {server} \n")
    arquivo.write(f"{data_atual()} - INFO - Iniciando a busca dos bancos na instância \n")
    try:
        cnxn1 = pyodbc.connect(f"DRIVER=SQL Server;SERVER={server};ENCRYPT=not;UID={username};PWD={password}")
        cursor1 = cnxn1.cursor()
        cursor1.execute("SELECT name FROM sys.databases;")
        listasstringinstancia = cursor1.fetchall()
    except pyodbc.DatabaseError as err:
        print(f"- Falha ao tentar buscar os bancos da instancia {err}")
        arquivo.write(f"{data_atual()} - ERRO - Falha ao tentar buscar os bancos da instancia {err} \n")
    else:
        cursor1.commit()
        print("- Consulta na instância realizada com sucesso.")
        arquivo.write(f"{data_atual()} - INFO - Consulta na instância realizada com sucesso. \n")

        print(f"- Quantidade de bancos encontrados: {len(listasstringinstancia)}")
        arquivo.write(f"{data_atual()} - INFO - Quantidade de bancos encontrados: {len(listasstringinstancia)} \n")
    finally:
        print("- Processo Finalizado")
        arquivo.write(f"{data_atual()} - INFO - Processo Finalizado \n")

    # Iniciando o processo no banco de muro.
    for num in range(len(bases_muro)):

        print(f"\n Iniciando o processo no banco: {bases_muro[num]}")
        arquivo.write(f"{data_atual()} - INFO - Iniciando o processo no banco: {bases_muro[num]} \n")

        # Configurando as Variaveis
        lista_connection_string  = []
        listaBancosInstancia = []
        listaNomesBancos = []
        listaIdsBancos = []
        guardarstringcs = []
        guardaridcs = []
        guardabancoinstancia = []
        guardarstringbm = []
        tamnomebanco = 0
        indexbancos = []
        separarstrings = []
        stringsLimpas = []
        connection_string = []
        database_id = []
        databaseupdate = ''

        # Pega a lista de connections strings
        print("- Iniciando a Busca no banco de muro")
        arquivo.write(f"{data_atual()} - INFO - Iniciando a Busca no banco de muro \n")
        try:
            cursor1.execute(f"SELECT [DATABASE_ID],[CONNECTION_STRING] FROM {bases_muro[num]}.[dbo].[KAIROS_DATABASES]")
            lista_connection_string  = cursor1.fetchall()

        except pyodbc.DatabaseError as err:
            print(f"- Falha ao tentar consultar banco de muro: {err}")
            arquivo.write(f"{data_atual()}  - ERRO - Falha ao tentar consultar banco de muro {err} \n")
        else:
            cursor1.commit()
            print("- Consulta no banco de muro realizada com sucesso")
            arquivo.write(f"{data_atual()} - INFO - Consulta no banco de muro realizada com sucesso \n")

            print(f"- Quantidade de registros encontrados: {len(lista_connection_string)}")
            arquivo.write(f"{data_atual()} - INFO - Quantidade de registros encontrados: {len(lista_connection_string)} \n")
        finally:
            print("- Processo Finalizado")
            arquivo.write(f"{data_atual()} - INFO - Processo Finalizado \n")

        # separar o nome do banco nas connection strings
        for i in range(len(lista_connection_string )):
            guardarstringcs.append(lista_connection_string [i].CONNECTION_STRING)
            stringsseparadas = guardarstringcs[i].split(";")
            nomebanco = stringsseparadas[1]
            tamnomebanco = len(nomebanco)
            listaNomesBancos.append(nomebanco[16:tamnomebanco])
            continue

        # separar o id do banco nas connection strings
        for cs in range(len(lista_connection_string)):
            guardaridcs.append(str(lista_connection_string[cs].DATABASE_ID))
            listaIdsBancos.append(guardaridcs[cs])
            continue

        # separar o nome do banco nas instancias
        for ins in range(len(listasstringinstancia)):
            guardabancoinstancia.append(str(listasstringinstancia[ins]))
            nomebancoinstancia = guardabancoinstancia[ins]
            tamnomebancoinstancia = len(nomebancoinstancia)
            tamnomebancoinstancia -= 4
            separarstrings.append(nomebancoinstancia[2:tamnomebancoinstancia])
            listaBancosInstancia.append(separarstrings[ins])
            continue


        # Comparar bancos "strings"
        print("- Iniciando a comparação dos bancos")
        arquivo.write(f"{data_atual()} - INFO - Iniciando a comparação dos bancos \n")
        for comparar in range(len(listaBancosInstancia)):
            if listaBancosInstancia[comparar] in listaNomesBancos:
                indexbancos.append(listaNomesBancos.index(listaBancosInstancia[comparar]))
                indexbancos.sort()
            continue

        for nums in range(len(indexbancos)):
            connection_string.append(lista_connection_string[indexbancos[nums]])
            database_id.append(listaIdsBancos[indexbancos[nums]])

        if len(connection_string) > 0:
            print("- Quantidade de bancos que deram Match: " + str(len(connection_string)))
            arquivo.write(f"{data_atual()} - INFO - Quantidade de bancos que deram Match: {len(connection_string)} \n")
        else:
            print("- Não foram encontrados Match na comparação de bancos")
            arquivo.write(f"{data_atual()} - INFO - Não foram encontrados Match na comparação de bancos \n")
        print("- Processo Finalizado")
        arquivo.write(f"{data_atual()} - INFO - Processo Finalizado \n")

        # Limpar as strings para inserir no banco
        for lim in range(len(connection_string)):
            guardarstringbm.append(str(connection_string[lim].CONNECTION_STRING))
            string = guardarstringbm[lim]
            stringsLimpas.append(string)
            continue
        while True:
            if bases_muro[num] == ('qcmaint_KAIROS_BASE_MURO') or bases_muro[num] == ('qcdev_KAIROS_BASE_MURO'):
                if database_update_br != '':
                    databaseupdate = database_update_br
                    break
                else:
                    print("- Não foi inserido no arquivo de config o apontamento para o banco Muro update BR")
                    arquivo.write(f"{data_atual()} - ERRO - Não foi inserido no arquivo de config o apontamento para o banco Muro update BR \n")
                    databaseupdate = input("Insira o nome da base que será usada: ")
                    arquivo.write(f"{data_atual()} - INFO - Inserido manualmente a base: {databaseupdate} \n")


            elif bases_muro[num] == ("qcmaint_KAIROS_BASE_MURO_MX") or bases_muro[num] == ("qcdev_KAIROS_BASE_MURO_MX"):
                if database_update_mx != '':
                    databaseupdate = database_update_mx
                else:
                    print("-  Não foi inserido no arquivo de config o apontamento para o banco Muro update MX")
                    arquivo.write(f"{data_atual()} - ERRO - Não foi inserido no arquivo de config o apontamento para o banco Muro update MX \n")
                    databaseupdate = input("Insira o nome da base que será utilizada: ")
                    arquivo.write(f"{data_atual()} - INFO - Inserido manualmente a base: {databaseupdate} \n")

            elif bases_muro[num] == ("qcmaint_KAIROS_BASE_MURO_PT") or bases_muro[num] == ("qcdev_KAIROS_BASE_MURO_PT"):
                if database_update_pt != '':
                    databaseupdate = database_update_pt
                else:
                    print("- Não foi inserido no arquivo de config o apontamento para o banco Muro update PT")
                    arquivo.write(f"{data_atual()} - ERRO - Não foi inserido no arquivo de config o apontamento para o banco Muro update PT \n")
                    databaseupdate = input("Insira o nome da base que será utilizada: ")
                    arquivo.write(f"{data_atual()} - INFO - Inserido manualmente a base: {databaseupdate} \n")

            elif bases_muro[num] == ("qcmaint_MDCOMUNE_BASE_MURO") or bases_muro[num] == ("qcdev_MDCOMUNE_BASE_MURO"):
                if database_update_md != '':
                    databaseupdate = database_update_md
                else:
                    print("- Não foi inserido no arquivo de config o apontamento para o banco Muro update MD")
                    arquivo.write(f"{data_atual()} - ERRO - Não foi inserido no arquivo de config o apontamento para o banco Muro update MD \n")
                    databaseupdate = input("Insira o nome da base que será utilizada: ")
                    arquivo.write(f"{data_atual()} - INFO - Inserido manualmente a base: {databaseupdate} \n")
            else:
                print("- Não foi possivel achar uma opção compativel com o banco de muro")
                print("- Insira o banco de Update manualmente")
                arquivo.write(
                    f"{data_atual()} - ERRO - Não foi possivel achar uma opção compativel com o banco de muro \n")
                arquivo.write(
                    f"{data_atual()} - ERRO - Insira o banco de Update manualmente \n")
                databaseupdate = input("Insira o nome da base que será utilizada: ")
                arquivo.write(f"{data_atual()} - INFO - Inserido manualmente a base: {databaseupdate} \n")
            if databaseupdate == "":
                continue
            else:
                break

        # Limpeza base muro UPDATE
        print(f"- Iniciando a limpeza no banco de muro update: {databaseupdate}")
        arquivo.write(f"{data_atual()} - INFO - Iniciando a limpeza no banco de muro update: {databaseupdate} \n")
        try:
            cursor1.execute(f'DELETE FROM {databaseupdate}.[dbo].[KAIROS_DATABASES]')

        except pyodbc.DatabaseError as err:
            print(f"- Falha ao tentar zerar o banco de muro temporário {err}")
            arquivo.write(f"{data_atual()}  - ERRO - Falha ao tentar zerar o banco de muro temporario {err} \n")
        else:
            cursor1.commit()
            print(f"- banco {databaseupdate} zerado com sucesso")
            arquivo.write(f"{data_atual()} - INFO - Banco {databaseupdate} zerado com sucesso \n")
        finally:
            print("- Processo Finalizado")
            arquivo.write(f"{data_atual()} - INFO - Processo Finalizado \n")

        # Inserindo as connections strings no banco muro temporario
        print(f"- Iniciando a inserção das connection strings no banco muro update: {databaseupdate}")
        arquivo.write(f"{data_atual()} - INFO - Iniciando a inserção das connection strings no banco muro update: {databaseupdate} \n")
        if len(stringsLimpas) > 0:
            try:
                cnxn2 = pyodbc.connect(f"DRIVER=SQL Server;SERVER={server};DATABASE={databaseupdate};ENCRYPT=not;UID={username};PWD={password}")
                cursor2 = cnxn2.cursor()

                cursor2.execute("set identity_insert [dbo].[KAIROS_DATABASES]  on")
                for incs in range(len(stringsLimpas)):
                    cursor2.execute(f"INSERT INTO [{databaseupdate}].[dbo].[KAIROS_DATABASES] ([DATABASE_ID],[CONNECTION_STRING] ,[DATABASE_VERSION] ,[FL_MAQUINA_CALCULO] ,[FL_ATIVO]) VALUES(?,?,?,0, 1)", database_id[incs], stringsLimpas[incs], versaodatabases)
                    continue
                cursor2.execute("set identity_insert [dbo].[KAIROS_DATABASES]  off")

            except pyodbc.DatabaseError as err:
                print(f"- Falha ao tentar inserir registros no banco de muro temporário {err}")
                arquivo.write(f"{data_atual()} - ERRO - Falha ao tentar inserir registros no banco de muro temporário {err} \n")
            else:
                cursor2.commit()
                print("- Sucesso ao inserir connection Strings no Banco de muro Update  ")
                arquivo.write(f"{data_atual()} - INFO - Sucesso ao inserir connection Strings no Banco de muro Update \n")

                print(f"- Registros inseridos com sucesso no banco: {databaseupdate}")
                arquivo.write(f"{data_atual()} - INFO - " + f"Registros inseridos com sucesso no banco: {databaseupdate} \n")
            finally:
                print("- Processo Finalizado")
                arquivo.write(f"{data_atual()} - INFO - Processo Finalizado \n")

        else:
            print("- Não a registros para serem inseridos no banco: " + databaseupdate)
            arquivo.write(f"{data_atual()} - INFO - Não a registros para serem inseridos no banco: {databaseupdate} \n")
            print("- Processo Finalizado")
            arquivo.write(f"{data_atual()} - INFO - Processo Finalizado \n")

        # Logando as connection string
        arquivo.write(f"{data_atual()} - INFO - Listando as connection strings utilizadas \n")
        quant = 1
        for log in range(len(connection_string)):
            arquivo.writelines(f"{data_atual()} - INFO - {quant} - {connection_string[log]} \n")
            quant += 1
            continue

        if num < 4:
            num += 1
        print(f"- Concluido a parte {num}  do processo, de um total de {len(bases_muro)} partes.")
        arquivo.write(f"{data_atual()} - INFO - Concluido a parte {num} do processo, de um total de {len(bases_muro)} partes. \n")
        continue

    print(f"- Fim da operação Busca muro {data_atual()}")
    arquivo.write(f"{data_atual()} - INFO - Fim da operação Busca muro \n")
    cursor1.close()
    cursor2.close()
    arquivo.close()


def replicar_version(server, username, password, database_update_br, database_update_mx, database_update_pt, database_update_md, bases_muro):

    num = 0
    tambasesmuro = len(bases_muro)

    arquivologreplicar = open("Log\log-replicarversion.txt", "a")

    print(f" \n - Inicio da operação replicar version {data_atual()} \n")
    arquivologreplicar.write(f"{data_atual()} - INFO - Inicio da operação replicar version")

    for num in range(len(bases_muro)):
        listaregistrosdb = []
        listaids = []
        listaversions = []
        listaconnectionstring = []

        print(f"- Iniciando o processo no banco: {bases_muro[num]}")
        arquivologreplicar.write(f"\n{data_atual()} - INFO - Iniciando o processo no banco: {bases_muro[num]}")

        while True:
            if bases_muro[num] == ('qcmaint_KAIROS_BASE_MURO') or bases_muro[num] == ('qcdev_KAIROS_BASE_MURO'):
                if database_update_br != '':
                    databaseupdate = database_update_br
                    break
                else:
                    print("- Não foi inserido no arquivo de config o apontamento para o banco Muro update BR")
                    arquivologreplicar.write(f"{data_atual()} - ERRO - Não foi inserido no arquivo de config o apontamento para o banco Muro update BR \n")
                    databaseupdate = input("Insira o nome da base que será usada: ")
                    arquivologreplicar.write(f"{data_atual()} - INFO - Inserido manualmente a base: {databaseupdate} \n")


            elif bases_muro[num] == ("qcmaint_KAIROS_BASE_MURO_MX") or bases_muro[num] == ("qcdev_KAIROS_BASE_MURO_MX"):
                if database_update_mx != '':
                    databaseupdate = database_update_mx
                else:
                    print("-  Não foi inserido no arquivo de config o apontamento para o banco Muro update MX")
                    arquivologreplicar.write(f"{data_atual()} - ERRO - Não foi inserido no arquivo de config o apontamento para o banco Muro update MX \n")
                    databaseupdate = input("Insira o nome da base que será utilizada: ")
                    arquivologreplicar.write(f"{data_atual()} - INFO - Inserido manualmente a base: {databaseupdate} \n")

            elif bases_muro[num] == ("qcmaint_KAIROS_BASE_MURO_PT") or bases_muro[num] == ("qcdev_KAIROS_BASE_MURO_PT"):
                if database_update_pt != '':
                    databaseupdate = database_update_pt
                else:
                    print("- Não foi inserido no arquivo de config o apontamento para o banco Muro update PT")
                    arquivologreplicar.write(f"{data_atual()} - ERRO - Não foi inserido no arquivo de config o apontamento para o banco Muro update PT \n")
                    databaseupdate = input("Insira o nome da base que será utilizada: ")
                    arquivologreplicar.write(f"{data_atual()} - INFO - Inserido manualmente a base: {databaseupdate} \n")

            elif bases_muro[num] == ("qcmaint_MDCOMUNE_BASE_MURO") or bases_muro[num] == ("qcdev_MDCOMUNE_BASE_MURO"):
                if database_update_md != '':
                    databaseupdate = database_update_md
                else:
                    print("- Não foi inserido no arquivo de config o apontamento para o banco Muro update MD")
                    arquivologreplicar.write(f"{data_atual()} - ERRO - Não foi inserido no arquivo de config o apontamento para o banco Muro update MD \n")
                    databaseupdate = input("Insira o nome da base que será utilizada: ")
                    arquivologreplicar.write(f"{data_atual()} - INFO - Inserido manualmente a base: {databaseupdate} \n")
            else:
                print("- Não foi possivel achar uma opção compativel com o banco de muro")
                print("- Insira o banco de Update manualmente")
                arquivologreplicar.write(
                    f"{data_atual()} - ERRO - Não foi possivel achar uma opção compativel com o banco de muro \n")
                arquivologreplicar.write(
                    f"{data_atual()} - ERRO - Insira o banco de Update manualmente \n")
                databaseupdate = input("Insira o nome da base que será utilizada: ")
                arquivologreplicar.write(f"{data_atual()} - INFO - Inserido manualmente a base: {databaseupdate} \n")
            if databaseupdate == "":
                continue
            else:
                break

        try:
            cnxnrp1 = pyodbc.connect(f"DRIVER=SQL Server;SERVER={server};DATABASE={databaseupdate};ENCRYPT=not;UID={username};PWD={password}")
            cursorrp1 = cnxnrp1.cursor()
            cursorrp1.execute(f"SELECT * FROM {databaseupdate}.[dbo].[KAIROS_DATABASES]")
            listaregistrosdb = cursorrp1.fetchall()
        except pyodbc.DatabaseError as err:
            print("- Falha ao tentar consultar banco de muro update: " + str(err))
            arquivologreplicar.write(f"\n{data_atual()} - ERRO - Falha ao tentar consultar banco de muro update: {err}")
        else:
            cursorrp1.commit()
            cursorrp1.close()

            print(f"- Sucesso na consulta no banco de muro update: {databaseupdate}")
            arquivologreplicar.write(f"\n{data_atual()} - INFO - Sucesso na consulta no banco de muro update: {databaseupdate}")

            print(f"- Quantidade de registros encontrados: {len(listaregistrosdb)}")
            arquivologreplicar.write(f"\n{data_atual()} - INFO - Quantidade de registros encontrados: {len(listaregistrosdb)}")
        finally:
            print("- Processo finalizado")

        tambuscarealizada = len(listaregistrosdb)
        if tambuscarealizada > 0:
            for nums in range(tambuscarealizada):
                listaids.append(listaregistrosdb[nums].DATABASE_ID)
                listaversions.append(listaregistrosdb[nums].DATABASE_VERSION)
                listaconnectionstring.append(listaregistrosdb[nums].CONNECTION_STRING)
                continue

            try:
                cnxnrp2 = pyodbc.connect(f"DRIVER=SQL Server;SERVER={server};DATABASE={bases_muro[num]};ENCRYPT=not;UID={username};PWD={password}")
                cursorrp2 = cnxnrp2.cursor()
                for teste2 in range(tambuscarealizada):
                    cursorrp2.execute("update [dbo].[KAIROS_DATABASES] set [DATABASE_VERSION] = ? where [DATABASE_ID] = ? and [CONNECTION_STRING] = ? ", listaversions[teste2], listaids[teste2], listaconnectionstring[teste2])
                    continue
            except pyodbc.DatabaseError as err:
                print(f"- Falha ao tentar consultar banco de muro update: {err}")
                arquivologreplicar.write(f"\n{data_atual()} - ERRO - Falha ao tentar consultar banco de muro update: {err}")
            else:
                cursorrp2.commit()
                cursorrp2.close()
                print(f"- Sucesso ao inserir version no banco de muro: {bases_muro[num]}")
                arquivologreplicar.write(f"\n{data_atual()} - INFO - Sucesso ao inserir version no banco de muro: {bases_muro[num]}")
            finally:
                print("- Processo finalizado")
        else:
            print("- Não existem registros para alterar o version")
            arquivologreplicar.write(f"\n{data_atual()} - ERRO - Não existem registros para alterar o version")

        # Logando as connection string
        quant = 1
        for log in range(tambuscarealizada):
            arquivologreplicar.writelines(f"\n{data_atual()} - INFO - {quant} - ID: {listaids[log]} - Version: {listaversions[log]}")
            quant += 1
            continue

        if num < 4:
            num += 1

        print(f"- Concluido a parte {num} do processo, de um total de {len(bases_muro)} partes. \n")
        arquivologreplicar.write(f"\n{data_atual()} - INFO - Concluido a parte {num} do processo, de um total de {len(bases_muro)} partes.")
        continue

    print(f"- Fim da operação replicar version {data_atual()}")
    arquivologreplicar.write(f"\n{data_atual()} - INFO - Fim da operação replicar version\n")
    arquivologreplicar.close()


def criar_config(arquivoprincipal):

    while True:
        nomeescolhido = input("- Insira o nome que deseja para o arquivo de config: (Sem o .json) \nEscolha: ")
        nomeconfig = nomeescolhido + ".json"
        try:
            if os.path.exists("Config"):
                print("- Pasta Config encontrada")
            else:
                os.makedirs("Config")
                print("- Pasta Config criada com sucesso")
        except OSError as error:
            print(f"- Erro ao criar/validar a pasta Config: {error}")

        if os.path.exists("Config\\" + nomeconfig):
            print("- Já existe um arquivo .json com o mesmo nome")
            print("- Informe outro nome para o arquivo config")
            continue
        else:
            arquivoconfig = open("Config\\" + nomeconfig, "w")
            arquivoconfig = open("Config\\" + nomeconfig, "a")

            arquivoconfig.write(
"""{
    "database_update_br": "",
    "database_update_mx": "",
    "database_update_pt": "",
    "database_update_md": "",
    "bases_muro": [],
    "conexao": {
        "server": "",
        "username": "",
        "password": ""
        }
}
    """)
            print("- Novo config criado com sucesso, configure e selecione para ser utilizado")
            arquivoprincipal.write(f"{data_atual()} - INFO - Novo config criado com sucesso, configure e selecione para ser utilizado \n")
            break


def menu(arquivoprincipal):
    server = ''
    username = ''
    password = ''
    database_update_br = ''
    database_update_mx = ''
    database_update_pt = ''
    database_update_md = ''
    bases_muro = []
    arquivo_config = ''
    params_dict = ''

    certo = True

    while certo:
        while certo:
            print("\n- Deseja usar um config existente ou criar um novo")
            escolhaconfig = input("|1 - Utilizar um config existente\n|2 - Criar um config em branco\n|3 - Sair\n|Escolha: ")

            if escolhaconfig == "1":
                while certo:
                    # Validando o arquivo de config
                    arquivo_config = input("- Insira o nome do config que será utilizado. (Sem colocar o .json, somente o nome)\n|Escolha: ") + '.json'
                    try:
                        if os.path.isfile(arquivo_config):
                            config_bjt = open(arquivo_config, "r")
                            config_JSON = config_bjt.read()
                            params_dict = json.loads(config_JSON)
                            certo = False
                            break
                        elif os.path.isfile("Config\\" + arquivo_config):
                            config_bjt = open("Config\\" + arquivo_config, "r")
                            config_JSON = config_bjt.read()
                            params_dict = json.loads(config_JSON)
                            certo = False
                            break
                        else:
                            print("- Não foi possível encontrar um .JSON com esse nome, tente novamente!")
                            arquivoprincipal.write(f"{data_atual()} - INFO - Não foi possível encontrar um .JSON com esse nome, tente novamente! \n")
                            certo = True
                            continue
                    except ValueError as name_error:
                        print(f"- Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente: {name_error}")
                        arquivoprincipal.write(f"{data_atual()} - INFO - Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente: {name_error} \n")
                        certo = True
                        continue
            elif escolhaconfig == "2":
                criar_config(arquivoprincipal)
                certo = True
                continue
            elif escolhaconfig == "3":
                return
            else:
                print("- Opção invalida, insira novamente \n")
                certo = True
                continue


            if params_dict["conexao"]["server"] == '':
                print("- O valor do server não foi especificado no config, informe e tente novamente ")
                arquivoprincipal.write(f"{data_atual()} - INFO - O valor do server não foi especificado no config, informe e tente novamente \n")
                certo = True
                continue
            elif params_dict["conexao"]["username"] == '':
                print("-  O valor do Username não foi especificado no config, informe e tente novamente ")
                arquivoprincipal.write(f"{data_atual()} - INFO - O valor do Username não foi especificado no config, informe e tente novamente \n")
                certo = True
                continue
            elif params_dict["conexao"]["password"] == '':
                print("-  O valor do Password não foi especificado no config, informe e tente novamente ")
                arquivoprincipal.write(f"{data_atual()} - INFO - O valor do Password não foi especificado no config, informe e tente novamente \n")
                certo = True
                continue
            elif params_dict["bases_muro"] == []:
                print("-  O valor do Base_Muro não foi especificado no config, informe e tente novamente ")
                arquivoprincipal.write(f"{data_atual()} - INFO - O valor do Base_Muro não foi especificado no config, informe e tente novamente \n")
                certo = True
                continue
            break
        break

    print(f"- Config escolhido: {arquivo_config}")
    arquivoprincipal.write(f"{data_atual()} - INFO - Config escolhido: {arquivo_config} \n")

    try:
        # Carregar config
        server = params_dict["conexao"]["server"]
        username = params_dict["conexao"]["username"]
        password = params_dict["conexao"]["password"]
        database_update_br = params_dict["database_update_br"]
        database_update_mx = params_dict["database_update_mx"]
        database_update_pt = params_dict["database_update_pt"]
        database_update_md = params_dict["database_update_md"]
        bases_muro = params_dict["bases_muro"]
    except ValueError as name_error:
        print(f"-  Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente: {name_error}")
        arquivoprincipal.write(f"{data_atual()} - INFO - Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente: {name_error} \n")

    # Limpando strings vazias na base muro
    limpamurotam = len(bases_muro)
    for num in range(0, limpamurotam, +1):
        if '' in bases_muro:
            bases_muro.remove('')
            continue
        else:
            break

    arquivoprincipal.write(f"{data_atual()} - INFO - Server: {server} \n")

    arquivoprincipal.write(f"{data_atual()} - INFO - User: {username} \n")

    arquivoprincipal.write(f"{data_atual()} - INFO - Password: {password} \n")

    arquivoprincipal.write(f"{data_atual()} - INFO - Base Muro Update BR: {database_update_br} \n")

    arquivoprincipal.write(f"{data_atual()} - INFO - Base Muro Update MX: {database_update_mx} \n")

    arquivoprincipal.write(f"{data_atual()} - INFO - Base Muro Update PT: {database_update_pt} \n")

    arquivoprincipal.write(f"{data_atual()} - INFO - Base Muro Update MD: {database_update_md} \n")

    arquivoprincipal.write(f"{data_atual()} - INFO - Bases Muro: {bases_muro} \n")

    while True:
        print("\n- Qual operação deseja realizar: ")
        escolha = input("|1 - Buscar Bancos\n|2 - Replicar version\n|3 - Trocar o config\n|4 - Sair\n|Escolha: ")
        if str(escolha) == "4":
            print("- Opção 4 selecionada - Sair")
            arquivoprincipal.write(f"{data_atual()} - INFO - Opção 4 selecionada - Sair \n")
            arquivoprincipal.close()
            exit()
        if str(escolha) == "1" or str(escolha) == "2" or str(escolha) == "3":
            match escolha:
                case "1":
                    print("- Opção 1 selecionada - Buscar Bancos")
                    arquivoprincipal.write(f"{data_atual()} - INFO - Opção 1 selecionada - Buscar Bancos \n")
                    manipular_bancomuro(server, username, password, database_update_br, database_update_mx, database_update_pt, database_update_md, bases_muro)
                case "2":
                    print("- Opção 2 selecionada - Replicar version")
                    arquivoprincipal.write(f"{data_atual()} - INFO - Opção 2 selecionada - Replicar version \n")
                    replicar_version(server, username, password, database_update_br, database_update_mx, database_update_pt, database_update_md, bases_muro)
                case "3":
                    print("- Opção 3 selecionada - Trocar o config")
                    arquivoprincipal.write(f"{data_atual()} - INFO - Opção 3 selecionada - Trocar o config \n")
                    menu(arquivoprincipal)
                case "4":
                    return
                case _:
                    print("-  Opção invalida, insira novamente!")
                    arquivoprincipal.write(f"{data_atual()} - INFO - Opção invalida, insira novamente! \n")
        else:
            print("-  Opção invalida, insira novamente!")
            arquivoprincipal.write(f"{data_atual()} - INFO - Opção invalida, insira novamente! \n")
            continue
        continue

    arquivoprincipal.close()


def main():
    try:
        if os.path.exists("Log"):
            print("- Pasta log já existente")
        else:
            os.makedirs("Log")
            print("- Pasta log criada com sucesso")
    except OSError as error:
        print(f"- Erro ao criar/validar a pasta Log: {error}")

    arquivoprincipal = open("Log\Log-basemuro.txt", "a")

    print(f"- Programa iniciado {data_atual()}")
    arquivoprincipal.write(f"{data_atual()} - INFO - Programa iniciado \n" )

    version = "1.2.3"

    print(f"- Versão: {version}")
    arquivoprincipal.write(f"{data_atual()} - INFO - Versão:  {version} \n")
    menu(arquivoprincipal)


main()