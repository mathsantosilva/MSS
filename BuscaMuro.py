# coding: utf-8
import datetime
import json
import os
import pyodbc

# Validando o arquivo de config
while True:
    arquivo_config = input("Insira o nome do config que será utilizado: ")

    try:
        if os.path.isfile(arquivo_config):
            config_bjt = open(arquivo_config, "r")
            config_JSON = config_bjt.read()
            params_dict = json.loads(config_JSON)
            break
        else:

            print("Não foi possivel encontrar um .JSON com esse nome, tente novamente!")
            continue
    except:
        print('Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente')
        continue

versaodatabases = input("Especifique para qual versão quer fazer o downgrade: ")

version = "1.0.4"
arquivo = open('log.txt', 'w')
arquivo.close()
arquivo = open("log.txt", "a")

server = ''
username = ''
password = ''
database_update_BR = ''
database_update_MX = ''
database_update_PT = ''
database_update_MD = ''
bases_Muro = ''

print("\n" + 'Versão: ' + version)
arquivo.write(datetime.datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Versão: ' + version + "\n")
try:
    # Entrada de dados
    server = params_dict["conexao"]["server"]
    username = params_dict["conexao"]["username"]
    password = params_dict["conexao"]["password"]
    database_update_BR = params_dict["database_update_BR"]
    database_update_MX = params_dict["database_update_MX"]
    database_update_PT = params_dict["database_update_PT"]
    database_update_MD = params_dict["database_update_MD"]
    bases_Muro = params_dict["bases_Muro"]
except:
    print('Alguma informação importante esta faltando no config, confira a seguir')
    arquivo.write(datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - ERRO - " + 'Algum dado importante esta faltando no config, confira a seguir')


print('Server: ' + server)
arquivo.write(datetime.datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Server: ' + server + "\n")

print('User: ' + username)
arquivo.write(datetime.datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'User: ' + username + "\n")

print('Password: ' + password)
arquivo.write(datetime.datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Password: ' + password + "\n")

print('Base Muro Update BR: ' + database_update_BR)
arquivo.write(datetime.datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Base Muro Update BR: ' + database_update_BR + "\n")

print('Base Muro Update MX: ' + database_update_MX)
arquivo.write(datetime.datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Base Muro Update MX: ' + database_update_MX + "\n")

print('Base Muro Update PT: ' + database_update_PT)
arquivo.write(datetime.datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Base Muro Update PT: ' + database_update_PT + "\n")

print('Base Muro Update MD: ' + database_update_MD)
arquivo.write(datetime.datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Base Muro Update MD: ' + database_update_MD + "\n")

print('Bases Muro: ' + str(bases_Muro))
arquivo.write(datetime.datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Bases Muro: ' + str(bases_Muro))

# Inicio do processo
print("\n" + "Inicio da operação: " + str(datetime.datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S")) + "\n")
arquivo.write("\n" + datetime.datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Inicio da operação ")

  # Pegar a lista de bancos da instancia
try:
    cnxn3 = pyodbc.connect(
        'DRIVER=SQL Server;SERVER=' + server + ';ENCRYPT=not;UID=' + username + ';PWD=' + password)
    cursor3 = cnxn3.cursor()
    cursor3.execute('SELECT name FROM sys.databases;')
    listasStringInstancia = cursor3.fetchall()
except pyodbc.DatabaseError as err:
    print("Falha ao tentar buscar os bancos da instancia " + str(err))
    arquivo.write("\n" + datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - ERRO - " + "Falha ao tentar buscar os bancos da instancia " + str(err))
else:
    cursor3.commit()
    print("Consulta na isntancia realizada com sucesso.")
    arquivo.write("\n" + datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Consulta na isntancia realizada com sucesso.")

    print("Quantidade de bancos encontrados: " + str(len(listasStringInstancia)))
    arquivo.write("\n" + datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Quantidade de bancos encontrados: " + str(
        len(listasStringInstancia)))
    cursor3.close()
finally:
    print('Processo Finalizado' + "\n")
    arquivo.write("\n" + datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Processo Finalizado')


for num in range(len(bases_Muro)):
    print('Iniciando o processo no banco: ' + bases_Muro[num])
    arquivo.write("\n" + datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Iniciando o processo no banco: ' + bases_Muro[num])

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
    basesmadis = ["qcmaint_MDCOMUNE_BASE_MURO", "qcdev_MDCOMUNE_BASE_MURO", "qcdev2_MDCOMUNE_BASE_MURO", "MDCOMUNE_BASE_MURO"]

    # Pega a lista de connections strings
    try:
        cnxn4 = pyodbc.connect(
            'DRIVER=SQL Server;SERVER=' + server + ';DATABASE=' + bases_Muro[
                num] + ';ENCRYPT=not;UID=' + username + ';PWD=' + password)
        cursor4 = cnxn4.cursor()
        cursor4.execute('SELECT [DATABASE_ID],[CONNECTION_STRING] FROM ' + bases_Muro[num] + '.[dbo].[KAIROS_DATABASES]')
        listaConnectionString = cursor4.fetchall()

    except pyodbc.DatabaseError as err:
        print("Falha ao tentar consultar banco de muro: " + str(err))
        arquivo.write("\n" + datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - ERRO - " + "Falha ao tentar consultar banco de muro " + str(err))
    else:
        cursor4.commit()
        print("Consulta no banco de muro realizada com sucesso.")
        arquivo.write("\n" + datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Consulta no banco de muro realizada com sucesso.")
        print('Quantidade de registros encontrados: ' + str(len(listaConnectionString)))
        arquivo.write("\n" + datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Quantidade de registros encontrados: " + str(
            len(listaConnectionString)))
        cursor4.close()
    finally:
        print('Processo Finalizado')
        arquivo.write("\n" + datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Processo Finalizado')

    # separar o nome do banco nas connection strings
    for i in range(len(listaConnectionString)):
        guardarstringcs.append(listaConnectionString[i].CONNECTION_STRING)
        stringsseparadas = guardarstringcs[i].split(';')
        nomebanco = stringsseparadas[1]
        tamnomebanco = len(nomebanco)
        listaNomesBancos.append(nomebanco[16:tamnomebanco])
        continue

    # separar o id do banco nas connection strings
    for cs in range(len(listaConnectionString)):
        guardaridcs.append(str(listaConnectionString[cs]))
        stringsidseparadas = guardaridcs[cs].split(',')
        stringsid1separadas = stringsidseparadas[0].split(',')
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

    # Comparação dos bancos com strings
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
        print("Quantidade de bancos que deram Match: " + str(len(connection_string)))
        arquivo.write("\n" + datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Quantidade de bancos que deram Match: " + str(len(connection_string)))
    else:
        print("Não foram encontrados Match na comparação de bancos")
        arquivo.write("\n" + datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Não foram encontrados Match na comparação de bancos")

    # Limpar as strings para inserir no banco
    for lim in range(len(connection_string)):
        guardarstringbm.append(str(connection_string[lim].CONNECTION_STRING))
        string = guardarstringbm[lim]
        stringsLimpas.append(string)
        continue

    match bases_Muro[num]:
        case 'qcmaint_KAIROS_BASE_MURO':
            if database_update_BR != '':
                databaseupdate = database_update_BR
            else:
                print('Não foi inserido o banco Muro UPDATE BR no arquivo de config')
                arquivo.write("\n" + datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - ERRO - "
                              + "Não foi inserido o banco Muro UPDATE BR no arquivo de config")
                databaseupdate = input("Insira o nome da base que será usada: ")
                arquivo.write("\n" + datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - INFO - "
                              + "Inserido manualmente a base: " + databaseupdate)

        case 'qcmaint_KAIROS_BASE_MURO_MX':
            if database_update_MX != '':
                databaseupdate = database_update_MX
            else:
                print('Não foi inserido o banco Muro  UPDATE MX no arquivo de config')
                arquivo.write("\n" + datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - ERRO - "
                              + "Não foi inserido o banco Muro UPDATE MX no arquivo de config")
                databaseupdate = input("Insira a base que será usada: ")
                arquivo.write("\n" + datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - INFO - "
                              + "Inserido manualmente a base: " + databaseupdate)
        case 'qcmaint_KAIROS_BASE_MURO_PT':
            if database_update_PT != '':
                databaseupdate = database_update_PT
            else:
                print('Não foi inserido o banco Muro UPDATE PT no arquivo de config')
                arquivo.write("\n" + datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - ERRO - "
                              + "Não foi inserido o banco Muro UPDATE PT no arquivo de config")
                databaseupdate = input("Insira a base que será usada: ")
                arquivo.write("\n" + datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - INFO - "
                              + "Inserido manualmente a base: " + databaseupdate)
        case 'qcmaint_MDCOMUNE_BASE_MURO':
            if database_update_MD != '':
                databaseupdate = database_update_MD
            else:
                print('Não foi inserido o banco Muro UPDATE MD no arquivo de config')
                arquivo.write("\n" + datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - ERRO - "
                              + "Não foi inserido o banco Muro UPDATE MD no arquivo de config")
                databaseupdate = input("Insira a base que será usada: ")
                arquivo.write("\n" + datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - INFO - "
                              + "Inserido manualmente a base: " + databaseupdate)
        case 'qcdev_MDCOMUNE_BASE_MURO_BR':
            if database_update_BR != '':
                databaseupdate = database_update_BR
            else:
                print('Não foi inserido o banco Muro UPDATE BR no arquivo de config')
                arquivo.write("\n" + datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - ERRO - "
                              + "Não foi inserido o banco Muro UPDATE BR no arquivo de config")
                databaseupdate = input("Insira a base que será usada: ")
                arquivo.write("\n" + datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - INFO - "
                              + "Inserido manualmente a base: " + databaseupdate)
        case 'qcdev_MDCOMUNE_BASE_MURO_MX':
            if database_update_MX != '':
                databaseupdate = database_update_MX
            else:
                print('Não foi inserido o banco Muro UPDATE MX no arquivo de config')
                arquivo.write("\n" + datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - ERRO - "
                              + "Não foi inserido o banco Muro UPDATE MX no arquivo de config")
                databaseupdate = input("Insira a base que será usada: ")
                arquivo.write("\n" + datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - INFO - "
                              + "Inserido manualmente a base: " + databaseupdate)
        case 'qcdev_MDCOMUNE_BASE_MURO_PT':
            if database_update_PT != '':
                databaseupdate = database_update_PT
            else:
                print('Não foi inserido o banco Muro UPDATE PT no arquivo de config')
                arquivo.write("\n" + datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - ERRO - "
                              + "Não foi inserido o banco Muro UPDATE PT no arquivo de config")
                databaseupdate = input("Insira a base que será usada: ")
                arquivo.write("\n" + datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - INFO - "
                              + "Inserido manualmente a base: " + databaseupdate)
        case 'qcdev_MDCOMUNE_BASE_MURO_MD':
            if database_update_MD != '':
                databaseupdate = database_update_MD
            else:
                print('Não foi inserido o banco Muro UPDATE MD no arquivo de config')
                arquivo.write("\n" + datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + " - ERRO - "
                              + "Não foi inserido o banco Muro UPDATE MD no arquivo de config")
                databaseupdate = input("Insira a base que será usada: ")
            arquivo.write("\n" + datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") + " - INFO - "
                          + "Inserido manualmente a base: " + databaseupdate)


    # Limpeza base muro UPDATE
    try:
        cnxn1 = pyodbc.connect(
            'DRIVER=SQL Server;SERVER=' + server + ';DATABASE=' + databaseupdate + ';ENCRYPT=not;UID=' + username + ';PWD=' + password)
        cursor1 = cnxn1.cursor()
        cursor1.execute('DELETE FROM ' + databaseupdate + '.[dbo].[KAIROS_DATABASES]')

    except pyodbc.DatabaseError as err:
        print("Falha ao tentar zerar o banco de muro temporario " + str(err))
        arquivo.write("\n" + datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - ERRO - " + "Falha ao tentar zerar o banco de muro temporario " + str(
            err))
    else:
        cursor1.commit()
        print('banco ' + databaseupdate + ' zerado com sucesso')
        arquivo.write("\n" + datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Banco ' + databaseupdate + ' zerado com sucesso')
        cursor1.close()
    finally:
        print('Processo Finalizado')
        arquivo.write("\n" + datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Processo Finalizado')


    # Inserindo as connections strings no banco muro temporario
    if len(stringsLimpas) > 0:
        try:
            cnxn5 = pyodbc.connect(
                'DRIVER=SQL Server;SERVER=' + server + ';DATABASE=' + databaseupdate + ';ENCRYPT=not;UID=' + username + ';PWD=' + password)
            cursor5 = cnxn5.cursor()
        except pyodbc.DatabaseError as err:
            print("Falha ao tentar inserir registros no banco de muro temporario " + str(err))
            arquivo.write("\n" + datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S ") + " - ERRO - " + "Falha ao tentar inserir registros no banco de muro temporario " + str(
                err))
        else:
            cursor5.execute('set identity_insert [dbo].[KAIROS_DATABASES]  on')
            for incs in range(len(stringsLimpas)):
                cursor5.execute('INSERT INTO [dbo].[KAIROS_DATABASES] ([DATABASE_ID],[CONNECTION_STRING] ,[DATABASE_VERSION] ,[FL_MAQUINA_CALCULO] ,[FL_ATIVO]) VALUES(?,?,?,0, 1)', database_id[incs], stringsLimpas[incs], versaodatabases)
                continue

            cursor5.execute('set identity_insert [dbo].[KAIROS_DATABASES]  off')
            cursor5.commit()
            cursor5.close()
        finally:
            print("Registros inseridos com sucesso no banco: " + databaseupdate)
            arquivo.write("\n" + datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Registros inseridos com sucesso no banco: " + databaseupdate)

    else:
        print("Não a registros para serem inseridos no banco: " + databaseupdate)
        arquivo.write("\n" + datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Não a registros para serem inseridos no banco: " + databaseupdate)

    # Logando as connection string
    quant = 1
    for log in range(len(connection_string)):
        arquivo.writelines("\n" + datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S - ") + str(quant) + " - " + str(
            connection_string[log]))
        quant += 1
        continue

    if num < 4:
        num += 1
    print("Concluido a parte " + str(num) + " do processo, de um total de " + str(len(bases_Muro)) + " partes." + "\n")
    arquivo.write(
        "\n" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " - INFO - " + "Concluido a parte " + str(
            num) + " parte do processo, de um total de " + str(len(bases_Muro)) + " partes.")
    continue

print('Fim da operação: ' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + "\n")
arquivo.write("\n" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Fim da operação')


input("PRESSIONE ENTER PARA FINALIZAR...")
