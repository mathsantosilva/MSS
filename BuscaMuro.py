# coding: utf-8
from tkinter import ttk
import datetime
import json
import os
import pyodbc
from tkinter import *
from tkinter.ttk import *

def manipularbancomuro(server, username, password, database_update_BR, database_update_MX, database_update_PT, database_update_MD, bases_Muro):

    arquivo = open("Log\Log-manipularbancomuro.txt", "a")

    print("\n" + '- Inicio da operação Busca muro ' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    arquivo.write(datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Inicio da operação Busca muro ' + "\n")

    versaodatabases = input("- Especifique para qual versão quer fazer o downgrade: ")

    print("- Version para downgrade: " + versaodatabases)
    arquivo.write(datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Version para downgrade: ' + versaodatabases + "\n")

    # Pegar a lista de bancos da instancia
    print("\n" + "- Iniciando a busca dos bancos na instância " + server + "\n")
    arquivo.write(datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Iniciando a busca dos bancos na instância" + "\n")
    try:
        cnxn3 = pyodbc.connect(
            'DRIVER=SQL Server;SERVER=' + server + ';ENCRYPT=not;UID=' + username + ';PWD=' + password)
        cursor3 = cnxn3.cursor()
        cursor3.execute("SELECT name FROM sys.databases;")
        listasStringInstancia = cursor3.fetchall()
    except pyodbc.DatabaseError as err:
        print("- Falha ao tentar buscar os bancos da instancia " + str(err))
        arquivo.write(datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - ERRO - " + "Falha ao tentar buscar os bancos da instancia " + str(err) + "\n")
    else:
        cursor3.commit()
        print("- Consulta na instância realizada com sucesso.")
        arquivo.write(datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Consulta na instância realizada com sucesso." + "\n")

        print("- Quantidade de bancos encontrados: " + str(len(listasStringInstancia)))
        arquivo.write(datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Quantidade de bancos encontrados: " + str(
            len(listasStringInstancia)) + "\n")
        cursor3.close()
    finally:
        print("- Processo Finalizado")
        arquivo.write(datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Processo Finalizado' + "\n")

    # Iniciando o processo no banco de muro.
    for num in range(len(bases_Muro)):

        print("\n" + 'Iniciando o processo no banco: ' + bases_Muro[num])
        arquivo.write(datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Iniciando o processo no banco: ' + bases_Muro[num] + "\n")

        # Configurando as Variaveis
        listaConnectionString = []
        listaBancosInstancia = []
        listaNomesBancos = []
        listaIdsBancos = []
        guardarstringcs = []
        guardaridcs = []
        guardabancoinstancia = []
        guardastring = []
        guardarstringbm = []
        conexaorealizada = []
        stringcorreta = []
        tamnomebanco = 0
        separarstrings = []
        stringsLimpas = []
        limparstring = []
        guardarmatchstrings = []
        connection_string = []
        database_id = []
        databaseupdate = ''
        basesmadis = ["qcmaint_MDCOMUNE_BASE_MURO",
                      "qcdev_MDCOMUNE_BASE_MURO",
                      "qcdev2_MDCOMUNE_BASE_MURO",
                      "MDCOMUNE_BASE_MURO"]

        # Pega a lista de connections strings
        print("- Iniciando a Busca no banco de muro")
        arquivo.write(datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Iniciando a Busca no banco de muro" + "\n")
        try:
            cnxn4 = pyodbc.connect(
                'DRIVER=SQL Server;SERVER=' + server + ';DATABASE=' + bases_Muro[
                    num] + ';ENCRYPT=not;UID=' + username + ';PWD=' + password)
            cursor4 = cnxn4.cursor()
            cursor4.execute("SELECT [DATABASE_ID],[CONNECTION_STRING] FROM "
                            + bases_Muro[num] + ".[dbo].[KAIROS_DATABASES]")
            listaConnectionString = cursor4.fetchall()

        except pyodbc.DatabaseError as err:
            print("- Falha ao tentar consultar banco de muro: " + str(err))
            arquivo.write(datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") + " - ERRO - " + "Falha ao tentar consultar banco de muro " + str(err) + "\n")
        else:
            cursor4.commit()
            print("- Consulta no banco de muro realizada com sucesso")
            arquivo.write(datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Consulta no banco de muro realizada com sucesso." + "\n")

            print("- Quantidade de registros encontrados: " + str(len(listaConnectionString)))
            arquivo.write(datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Quantidade de registros encontrados: " + str(
                len(listaConnectionString)) + "\n")
            cursor4.close()
        finally:
            print("- Processo Finalizado")
            arquivo.write(datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Processo Finalizado' + "\n")

        # separar o nome do banco nas connection strings
        for i in range(len(listaConnectionString)):
            guardarstringcs.append(listaConnectionString[i].CONNECTION_STRING)
            stringsseparadas = guardarstringcs[i].split(";")
            nomebanco = stringsseparadas[1]
            tamnomebanco = len(nomebanco)
            listaNomesBancos.append(nomebanco[16:tamnomebanco])
            continue

        # separar o id do banco nas connection strings
        for cs in range(len(listaConnectionString)):
            guardaridcs.append(str(listaConnectionString[cs]))
            stringsidseparadas = guardaridcs[cs].split(",")
            stringsid1separadas = stringsidseparadas[0].split(",")
            numid = stringsid1separadas[0]
            tamnumid = len(numid)
            listaIdsBancos.append(numid[1:tamnumid])
            continue

        # separar o nome do banco nas instancias
        for ins in range(len(listasStringInstancia)):
            guardabancoinstancia.append(str(listasStringInstancia[ins]))
            nomebancoinstancia = guardabancoinstancia[ins]
            tamnomebancoinstancia = len(nomebancoinstancia)
            tamnomebancoinstancia -= 4
            separarstrings.append(nomebancoinstancia[2:tamnomebancoinstancia])
            listaBancosInstancia.append(separarstrings[ins])
            continue

        # Comparar bancos "strings"
        print("- Iniciando a comparação dos bancos")
        arquivo.write(datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Iniciando a comparação dos bancos" + "\n")
        for com in range(len(listaNomesBancos)):
            for l in range(len(listaBancosInstancia)):
                if listaNomesBancos[com] == listaBancosInstancia[l]:
                    connection_string.append(listaConnectionString[com])
                    database_id.append(listaIdsBancos[com])

                    guardarmatchstrings.append(
                        'são iguais: ' + str(listaBancosInstancia[l]) + ' ' + str(listaNomesBancos[com]))
                continue
            continue
        if len(connection_string) > 0:
            print("- Quantidade de bancos que deram Match: " + str(len(connection_string)))
            arquivo.write(datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") + " - INFO - "
                          + "Quantidade de bancos que deram Match: " + str(len(connection_string)) + "\n")
        else:
            print("- Não foram encontrados Match na comparação de bancos")
            arquivo.write(datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Não foram encontrados Match na comparação de bancos" + "\n")
        print("- Processo Finalizado")
        arquivo.write(datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Processo Finalizado' + "\n")

        # Limpar as strings para inserir no banco
        for lim in range(len(connection_string)):
            guardarstringbm.append(str(connection_string[lim].CONNECTION_STRING))
            string = guardarstringbm[lim]
            stringsLimpas.append(string)
            continue

        if bases_Muro[num] == ('qcmaint_KAIROS_BASE_MURO') or bases_Muro[num] == ('qcdev_KAIROS_BASE_MURO'):
            if database_update_BR != '':
                databaseupdate = database_update_BR
            else:
                print("- Não foi inserido no arquivo de config o apontamento para o banco Muro update BR")
                arquivo.write(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - ERRO - "
                              + "Não foi inserido no arquivo de config o apontamento para o banco Muro update BR" + "\n")
                databaseupdate = input("Insira o nome da base que será usada: ")
                arquivo.write(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - INFO - "
                              + "Inserido manualmente a base: " + databaseupdate + "\n")

        elif bases_Muro[num] == ("qcmaint_KAIROS_BASE_MURO_MX") or bases_Muro[num] == ("qcdev_KAIROS_BASE_MURO_MX"):
            if database_update_MX != '':
                databaseupdate = database_update_MX
            else:
                print("-  Não foi inserido no arquivo de config o apontamento para o banco Muro update MX")
                arquivo.write(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - ERRO - "
                              + "Não foi inserido no arquivo de config o apontamento para o banco Muro update MX" + "\n")
                databaseupdate = input("Insira o nome da base que será utilizada: ")
                arquivo.write(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - INFO - "
                              + "Inserido manualmente a base: " + databaseupdate + "\n")

        elif bases_Muro[num] == ("qcmaint_KAIROS_BASE_MURO_PT") or bases_Muro[num] == ("qcdev_KAIROS_BASE_MURO_PT"):
            if database_update_PT != '':
                databaseupdate = database_update_PT
            else:
                print("- Não foi inserido no arquivo de config o apontamento para o banco Muro update PT")
                arquivo.write(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - ERRO - "
                              + "Não foi inserido no arquivo de config o apontamento para o banco Muro update PT" + "\n")
                databaseupdate = input("Insira o nome da base que será utilizada: ")
                arquivo.write(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - INFO - "
                              + "Inserido manualmente a base: " + databaseupdate + "\n")

        elif bases_Muro[num] == ("qcmaint_MDCOMUNE_BASE_MURO") or bases_Muro[num] == ("qcdev_MDCOMUNE_BASE_MURO"):
            if database_update_MD != '':
                databaseupdate = database_update_MD
            else:
                print("- Não foi inserido no arquivo de config o apontamento para o banco Muro update MD")
                arquivo.write(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - ERRO - "
                              + "Não foi inserido no arquivo de config o apontamento para o banco Muro update MD" + "\n")
                databaseupdate = input("Insira o nome da base que será utilizada: ")
                arquivo.write(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - INFO - "
                              + "Inserido manualmente a base: " + databaseupdate + "\n")


        # Limpeza base muro UPDATE
        print("- Iniciando a limpeza no banco de muro update: " + databaseupdate)
        arquivo.write(datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Iniciando a limpeza no banco de muro update: " + databaseupdate + "\n")
        try:
            cnxn1 = pyodbc.connect(
                'DRIVER=SQL Server;SERVER=' + server
                + ';DATABASE=' + databaseupdate + ';ENCRYPT=not;UID=' + username + ';PWD=' + password)
            cursor1 = cnxn1.cursor()
            cursor1.execute('DELETE FROM ' + databaseupdate + '.[dbo].[KAIROS_DATABASES]')

        except pyodbc.DatabaseError as err:
            print("- Falha ao tentar zerar o banco de muro temporário " + str(err))
            arquivo.write(datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") + " - ERRO - " + "Falha ao tentar zerar o banco de muro temporario " + str(
                err) + "\n")
        else:
            cursor1.commit()
            print("- banco " + databaseupdate + " zerado com sucesso")
            arquivo.write(datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Banco " + databaseupdate + " zerado com sucesso" + "\n")
            cursor1.close()
        finally:
            print("- Processo Finalizado")
            arquivo.write(datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Processo Finalizado' + "\n")

        # Inserindo as connections strings no banco muro temporario
        print("- Iniciando a inserção das connection strings no banco muro update: " + databaseupdate)
        arquivo.write(datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Iniciando a inserção das connection strings no banco muro update: " + databaseupdate + "\n")
        if len(stringsLimpas) > 0:
            try:
                cnxn5 = pyodbc.connect(
                    'DRIVER=SQL Server;SERVER=' + server + ';DATABASE=' + databaseupdate + ';ENCRYPT=not;UID=' + username + ';PWD=' + password)
                cursor5 = cnxn5.cursor()

                cursor5.execute("set identity_insert [dbo].[KAIROS_DATABASES]  on")
                for incs in range(len(stringsLimpas)):
                    cursor5.execute("INSERT INTO [dbo].[KAIROS_DATABASES] ([DATABASE_ID],[CONNECTION_STRING] ,[DATABASE_VERSION] ,[FL_MAQUINA_CALCULO] ,[FL_ATIVO]) VALUES(?,?,?,0, 1)", database_id[incs], stringsLimpas[incs], versaodatabases)
                    continue
                cursor5.execute("set identity_insert [dbo].[KAIROS_DATABASES]  off")

            except pyodbc.DatabaseError as err:
                print("- Falha ao tentar inserir registros no banco de muro temporário " + str(err))
                arquivo.write("\n" + datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S ") + " - ERRO - "
                              + "Falha ao tentar inserir registros no banco de muro temporário " + str(
                    err) + "\n")
            else:
                cursor5.commit()
                cursor5.close()
                print("- Sucesso ao inserir connection Strings no Banco de muro Update  ")
                arquivo.write(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - INFO - "
                              + "Sucesso ao inserir connection Strings no Banco de muro Update  " + "\n")
            finally:
                print("- Registros inseridos com sucesso no banco: " + databaseupdate)
                arquivo.write(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Registros inseridos com sucesso no banco: "
                              + databaseupdate + "\n")

        else:
            print("- Não a registros para serem inseridos no banco: " + databaseupdate)
            arquivo.write(datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") + " - INFO - "
                          + "Não a registros para serem inseridos no banco: " + databaseupdate + "\n")

        print("- Processo Finalizado")
        arquivo.write(datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Processo Finalizado' + "\n")

        # Logando as connection string
        arquivo.write(datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Listando as connection strings utilizadas' + "\n")
        quant = 1
        for log in range(len(connection_string)):
            arquivo.writelines(datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") + " - INFO - " + str(quant) + " - " + str(
                connection_string[log]) + "\n")
            quant += 1
            continue

        if num < 4:
            num += 1
        print("- Concluido a parte " + str(num) + " do processo, de um total de " + str(len(bases_Muro)) + " partes.")
        arquivo.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " - INFO - " + "Concluido a parte " + str(
                num) + " do processo, de um total de " + str(len(bases_Muro)) + " partes." + "\n")
        continue

    print("- Fim da operação Busca muro " + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    arquivo.write(datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Fim da operação Busca muro" + "\n")
    arquivo.close()


def replicarversion(server, username, password, database_update_BR, database_update_MX, database_update_PT, database_update_MD, bases_Muro):

    num = 0
    tambasesmuro = len(bases_Muro)

    arquivologreplicar = open("Log\log-replicarversion.txt", "a")

    print("\n" + '- Inicio da operação replicar version '
          + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + "\n")
    arquivologreplicar.write(datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Inicio da operação replicar version")

    for num in range(len(bases_Muro)):
        listaregistrosdb = []
        listaids = []
        listaversions = []
        listaconnectionstring = []

        print("- Iniciando o processo no banco: " + bases_Muro[num])
        arquivologreplicar.write("\n" + datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Iniciando o processo no banco: ' + bases_Muro[num])

        if bases_Muro[num] == ("qcmaint_KAIROS_BASE_MURO" or "qcdev_MDCOMUNE_BASE_MURO_BR"):
            if database_update_BR != '':
                databaseupdate = database_update_BR
            else:
                print("- Não foi inserido no arquivo de config o apontamento para o banco Muro update BR")
                arquivologreplicar.write(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - ERRO - "
                              + "Não foi inserido no arquivo de config o apontamento para o banco Muro update BR" + "\n")
                databaseupdate = input("Insira o nome da base que será usada: ")
                arquivologreplicar.write(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - INFO - "
                              + "Inserido manualmente a base: " + databaseupdate + "\n")

        elif bases_Muro[num] == ("qcmaint_KAIROS_BASE_MURO_MX" or "qcdev_MDCOMUNE_BASE_MURO_MX"):
            if database_update_MX != '':
                databaseupdate = database_update_MX
            else:
                print("-  Não foi inserido no arquivo de config o apontamento para o banco Muro update MX")
                arquivologreplicar.write(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - ERRO - "
                              + "Não foi inserido no arquivo de config o apontamento para o banco Muro update MX" + "\n")
                databaseupdate = input("Insira o nome da base que será utilizada: ")
                arquivologreplicar.write(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - INFO - "
                              + "Inserido manualmente a base: " + databaseupdate + "\n")

        elif bases_Muro[num] == ("qcmaint_KAIROS_BASE_MURO_PT" or "qcdev_MDCOMUNE_BASE_MURO_PT"):
            if database_update_PT != '':
                databaseupdate = database_update_PT
            else:
                print("- Não foi inserido no arquivo de config o apontamento para o banco Muro update PT")
                arquivologreplicar.write(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - ERRO - "
                              + "Não foi inserido no arquivo de config o apontamento para o banco Muro update PT" + "\n")
                databaseupdate = input("Insira o nome da base que será utilizada: ")
                arquivologreplicar.write(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - INFO - "
                              + "Inserido manualmente a base: " + databaseupdate + "\n")

        elif bases_Muro[num] == ("qcmaint_MDCOMUNE_BASE_MURO" or "qcdev_MDCOMUNE_BASE_MURO_MD"):
            if database_update_MD != '':
                databaseupdate = database_update_MD
            else:
                print("- Não foi inserido no arquivo de config o apontamento para o banco Muro update MD")
                arquivologreplicar.write(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - ERRO - "
                              + "Não foi inserido no arquivo de config o apontamento para o banco Muro update MD" + "\n")
                databaseupdate = input("Insira o nome da base que será utilizada: ")
                arquivologreplicar.write(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - INFO - "
                              + "Inserido manualmente a base: " + databaseupdate + "\n")

        try:
            cnxnrp1 = pyodbc.connect(
                'DRIVER=SQL Server;SERVER=' + server
                                            + ';DATABASE=' + databaseupdate
                + ';ENCRYPT=not;UID=' + username + ';PWD=' + password)
            cursorrp1 = cnxnrp1.cursor()
            cursorrp1.execute("SELECT * FROM " + databaseupdate + ".[dbo].[KAIROS_DATABASES]")
            listaregistrosdb = cursorrp1.fetchall()
        except pyodbc.DatabaseError as err:
            print("- Falha ao tentar consultar banco de muro update: " + str(err))
            arquivologreplicar.write("\n" + datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") + " - ERRO - " + "Falha ao tentar consultar banco de muro update: " + str(err))
        else:
            cursorrp1.commit()
            cursorrp1.close()

            print("- Sucesso na consulta no banco de muro update: " + databaseupdate)
            arquivologreplicar.write("\n" + datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Sucesso na consulta no banco de muro update: " + databaseupdate)

            print("- Quantidade de registros encontrados: " + str(len(listaregistrosdb)))
            arquivologreplicar.write("\n" + datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") + " - INFO - "
                                     + "Quantidade de registros encontrados: " + str(len(listaregistrosdb)))
        finally:
            print("- Processo finalizado")

        tambuscarealizada = len(listaregistrosdb)
        if tambuscarealizada > 0:
            for teste in range(tambuscarealizada):
                listaids.append(listaregistrosdb[teste].DATABASE_ID)
                listaversions.append(listaregistrosdb[teste].DATABASE_VERSION)
                listaconnectionstring.append(listaregistrosdb[teste].CONNECTION_STRING)
                continue

            try:
                cnxnrp2 = pyodbc.connect(
                    'DRIVER=SQL Server;SERVER=' + server + ';DATABASE=' + bases_Muro[num] + ';ENCRYPT=not;UID=' + username + ';PWD=' + password)
                cursorrp2 = cnxnrp2.cursor()
                for teste2 in range(tambuscarealizada):
                    cursorrp2.execute("update [dbo].[KAIROS_DATABASES] set [DATABASE_VERSION] = ? where [DATABASE_ID] = ? and [CONNECTION_STRING] = ? ", listaversions[teste2], listaids[teste2], listaconnectionstring[teste2])
                    continue
            except pyodbc.DatabaseError as err:
                print("- Falha ao tentar consultar banco de muro update: " + str(err))
                arquivologreplicar.write("\n" + datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - ERRO - " + "Falha ao tentar consultar banco de muro update: " + str(err))
            else:
                cursorrp2.commit()
                cursorrp2.close()
                print("- Sucesso ao inserir version no banco de muro: " + bases_Muro[num])
                arquivologreplicar.write("\n" + datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - INFO - "
                                         + "Sucesso ao inserir version no banco de muro: " + bases_Muro[num])
            finally:
                print("- Processo finalizado")
        else:
            print("- Não existem registros para alterar o version")
            arquivologreplicar.write("\n" + datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") + " - ERRO - " + "Não existem registros para alterar o version")

        # Logando as connection string
        quant = 1
        for log in range(tambuscarealizada):
            arquivologreplicar.writelines("\n" + datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") + " - INFO - " + str(quant) + " - " + "ID: " + str(listaids[log]) + " - " + "Version: " + str(listaversions[log]))
            quant += 1
            continue

        if num < 4:
            num += 1

        print("- Concluido a parte " + str(num)
              + " do processo, de um total de " + str(len(bases_Muro)) + " partes." + "\n")
        arquivologreplicar.write(
            "\n" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " - INFO - " + "Concluido a parte " + str(
                num) + " do processo, de um total de " + str(len(bases_Muro)) + " partes.")
        continue

    print("- Fim da operação replicar version " + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    arquivologreplicar.write("\n" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " - INFO - " + "Fim da operação replicar version")
    arquivologreplicar.close()


def criarconfig(arquivoprincipal):

    while True:
        nomeescolhido = input("- Insira o nome que deseja para o arquivo de config: (Sem o .json)\nEscolha: ")
        nomeconfig = nomeescolhido + ".json"
        try:
            if os.path.exists("Config"):
                print("- Pasta Config encontrada")
            else:
                os.makedirs("Config")
                print("- Pasta Config criada com sucesso")
        except OSError as error:
            print("- Erro ao criar/validar a pasta Config: " + str(error))

        if os.path.exists("Config\\" + nomeconfig):
            print("- Já existe um arquivo .json com o mesmo nome")
            print("- Informe outro nome para o arquivo config")
            continue
        else:
            arquivoconfig = open("Config\\" + nomeconfig, "w")
            arquivoconfig = open("Config\\" + nomeconfig, "a")

            arquivoconfig.write(
"""{
    "database_update_BR": "",
    "database_update_MX": "",
    "database_update_PT": "",
    "database_update_MD": "",
    "bases_Muro": [],
    "conexao": {
        "server": "",
        "username": "",
        "password": ""
    }
}
    """)
            print("- Novo config criado com sucesso, configure e selecione ele para ser utilizado")
            arquivoprincipal.write(datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") + " - INFO - "
                                   + "Novo config criado com sucesso, configure e selecione ele para ser utilizado" + "\n")
            break


def menu(arquivoprincipal):

    certo = True

    while certo:
        while certo:
            print("\n" + "- Deseja usar um config existente ou criar um novo")
            escolhaconfig = input("|1 - Utilizar um config existente\n|2 - Criar um config em branco\n|Escolha: ")

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
                            arquivoprincipal.write(datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S") + " - INFO - "
                                                   + "Não foi possível encontrar um .JSON com esse nome, tente novamente!" + "\n")
                            certo = True
                            continue
                    except ValueError as N:
                        print("-  Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente: " + str(N))
                        arquivoprincipal.write(datetime.datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S") + " - INFO - "
                                               + "Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente: " + str(N) + "\n")
                        certo = True
                        continue

            elif escolhaconfig == "2":
                criarconfig(arquivoprincipal)
                certo = True
                continue
            else:
                print("- Opção invalida, insira novamente\n")
                certo = True
                continue
            if params_dict["conexao"]["server"] == '':
                print("-  O valor do server não foi especificado no config, informe e tente novamente ")
                arquivoprincipal.write(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - INFO - "
                                       + 'O valor do server não foi especificado no config, informe e tente novamente ' + "\n")
                certo = True
                continue
            elif params_dict["conexao"]["username"] == '':
                print("-  O valor do Username não foi especificado no config, informe e tente novamente ")
                arquivoprincipal.write(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - INFO - "
                                       + 'O valor do Username não foi especificado no config, informe e tente novamente ' + "\n")
                certo = True
                continue
            elif params_dict["conexao"]["password"] == '':
                print("-  O valor do Password não foi especificado no config, informe e tente novamente ")
                arquivoprincipal.write(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - INFO - "
                                       + 'O valor do Password não foi especificado no config, informe e tente novamente ' + "\n")
                certo = True
                continue
            elif params_dict["bases_Muro"] == []:
                print("-  O valor do Base_Muro não foi especificado no config, informe e tente novamente ")
                arquivoprincipal.write(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - INFO - "
                                       + 'O valor do Base_Muro não foi especificado no config, informe e tente novamente ' + "\n")
                certo = True
                continue
            break
        break

    print("- Config escolhido: " + arquivo_config)
    arquivoprincipal.write(datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Config escolhido: " + arquivo_config + "\n")

    try:
        # Carregar config
        server = params_dict["conexao"]["server"]
        username = params_dict["conexao"]["username"]
        password = params_dict["conexao"]["password"]
        database_update_BR = params_dict["database_update_BR"]
        database_update_MX = params_dict["database_update_MX"]
        database_update_PT = params_dict["database_update_PT"]
        database_update_MD = params_dict["database_update_MD"]
        bases_Muro = params_dict["bases_Muro"]
    except ValueError as N:
        print("-  Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente: " + str(N))
        arquivoprincipal.write(datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente' + str(N) + "\n")

    # Limpando strings vazias na base muro
    limpamurotam = len(bases_Muro)
    for num in range(0, limpamurotam, +1):
        if '' in bases_Muro:
            bases_Muro.remove('')
            continue
        else:
            break

    print("- Server: " + server)
    arquivoprincipal.write(datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Server: ' + server + "\n")

    print("- User: " + username)
    arquivoprincipal.write(datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'User: ' + username + "\n")

    print("- Password: " + password)
    arquivoprincipal.write(datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Password: ' + password + "\n")

    print("- Base Muro Update BR: " + database_update_BR)
    arquivoprincipal.write(datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Base Muro Update BR: ' + database_update_BR + "\n")

    print("- Base Muro Update MX: " + database_update_MX)
    arquivoprincipal.write(datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Base Muro Update MX: ' + database_update_MX + "\n")

    print("- Base Muro Update PT: " + database_update_PT)
    arquivoprincipal.write(datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Base Muro Update PT: ' + database_update_PT + "\n")

    print("- Base Muro Update MD: " + database_update_MD)
    arquivoprincipal.write(datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Base Muro Update MD: ' + database_update_MD + "\n")

    print("- Bases Muro: " + str(bases_Muro))
    arquivoprincipal.write(datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Bases Muro: ' + str(bases_Muro) + "\n")

    while True:
        print("\n" + "- Qual operação deseja realizar: ")
        escolha = input("|1 - Buscar Bancos\n|2 - Replicar version\n|3 - Trocar o config\n|4 - Sair\n|Escolha: ")
        if str(escolha) == "4":
            print("- Opção 4 selecionada - Sair")
            arquivoprincipal.write(datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Opção 4 selecionada - Sair" + "\n")
            arquivoprincipal.close()
            exit()
        if str(escolha) == "1" or str(escolha) == "2" or str(escolha) == "3":
            match escolha:
                case "1":
                    print("- Opção 1 selecionada - Buscar Bancos")
                    arquivoprincipal.write(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Opção 1 selecionada - Buscar Bancos' + "\n")
                    manipularbancomuro(server, username, password, database_update_BR, database_update_MX, database_update_PT, database_update_MD, bases_Muro)
                case "2":
                    print("- Opção 2 selecionada - Replicar version")
                    arquivoprincipal.write(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Opção 2 selecionada - Replicar version' + "\n")
                    replicarversion(server, username, password, database_update_BR, database_update_MX, database_update_PT, database_update_MD, bases_Muro)
                case "3":
                    print("- Opção 3 selecionada - Trocar o config")
                    arquivoprincipal.write(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Opção 3 selecionada - Trocar o config' + "\n")
                    menu(arquivoprincipal)
                case "4":
                    return
                case _:
                    print("-  Opção invalida, insira novamente!")
                    arquivoprincipal.write(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Opção invalida, insira novamente!' + "\n")
        else:
            print("-  Opção invalida, insira novamente!")
            arquivoprincipal.write(datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Opção invalida, insira novamente!' + "\n")
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
        print("- Erro ao criar/validar a pasta Log: " + str(error))

    arquivoprincipal = open("Log\Log-basemuro.txt", "a")

    print("- Programa iniciado " + datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"))
    arquivoprincipal.write(datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Programa iniciado" + "\n")

    version = "1.2.1"

    print("- Versão: " + version)
    arquivoprincipal.write(datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Versão: ' + version + "\n")
    menu(arquivoprincipal)


main()