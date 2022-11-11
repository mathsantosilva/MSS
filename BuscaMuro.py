# coding: utf-8
import os
import sys
import stdin
from sys import stdin
import datetime
import pyodbc

version = "1.0.2"
datainicio = datetime.datetime.now()
bases = []
databaseupdate = ''
arquivo = open('log.txt', 'w')
arquivo.close()
arquivo = open("log.txt", "a")

print('Versão: ' + version)
arquivo.write(datetime.datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S ") + " - INFO - " + 'Versão: ' + version)

# Entrada de dados
server = input("Insira o nome do servidor: ")
username = input("Insira o user do servidor: ")
password = input("Insira a senha do servidor: ")
opcao = input("Qual ambiente deseja atualizar - (1)QCMAINT | (2)QCDEV: ")
versaodatabases = input("Especifique para qual versão quer fazer o downgrade: ")
databaseupdate = input('Insira a base muro update: ')

# Configura os bancos de muro que serão buscados
while opcao:
    if opcao == '1':
        bases = ['qcmaint_KAIROS_BASE_MURO', 'qcmaint_MDCOMUNE_BASE_MURO', 'qcmaint_KAIROS_BASE_MURO_PT',
                 'qcmaint_KAIROS_BASE_MURO_MX']
        break;
    elif opcao == '2':
        bases = ['qcdev_KAIROS_BASE_MURO', 'qcdev_MDCOMUNE_BASE_MURO', 'qcdev_KAIROS_BASE_MURO_PT',
                 'qcdev_KAIROS_BASE_MURO_MX']
        break;
    else:
        opcao = input('opção invalida, insira novamente: ')
        continue

# Limpando todos os registros do banco update
try:
    cnxn1 = pyodbc.connect(
        'DRIVER=SQL Server;SERVER=' + server + ';DATABASE=' + databaseupdate + ';ENCRYPT=not;UID=' + username + ';PWD=' + password)
    cursor1 = cnxn1.cursor()
    cursor1.execute('DELETE FROM ' + databaseupdate + '.[dbo].[KAIROS_DATABASES]')
except pyodbc.DatabaseError as err:
    cursor1.rollback()
else:
    cursor1.commit()
finally:
    print('banco ' + databaseupdate + ' zerado com sucesso')
    arquivo.write(datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S ") + " - INFO - " + 'Banco ' + databaseupdate + ' zerado com sucesso')

# Inicio do processo
print("\nInicio da operação: " + str(datainicio))
arquivo.write("\n" + datetime.datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S ") + " - INFO - " + " Inicio da operação ")

# Pegar a lista de bancos da instancia
try:
    cnxn3 = pyodbc.connect(
        'DRIVER=SQL Server;SERVER=' + server + ';DATABASE=' + databaseupdate + ';ENCRYPT=not;UID=' + username + ';PWD=' + password)
    cursor3 = cnxn3.cursor()
    cursor3.execute('SELECT name FROM sys.databases;')
    listasStringInstancia = cursor3.fetchall()
except pyodbc.DatabaseError as err:
    cursor3.rollback()
else:
    cursor3.commit()
finally:
    print("Consulta na isntancia realizada com sucesso.")
    arquivo.write("\n" + datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Consulta na isntancia realizada com sucesso.")
    print("Quantidade de bancos encontrados: " + str(len(listasStringInstancia)))
    arquivo.write("\n" + datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Quantidade de bancos encontrados: " + str(
        len(listasStringInstancia)))

for num in range(len(bases)):
    print('Iniciando o processo no banco: ' + bases[num])
    arquivo.write("\n" + datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Iniciando o processo no banco: ' + bases[num])

    # Configurando as Variaveis
    listaConnectionString = []
    listaBancosInstancia = []
    listaNomesBancos = []
    listasStringInstancia = []
    guardarstring = []
    guardabancoinstancia = []
    guardastring = []
    conexaorealizada = []
    stringcorreta = []
    tamnomebanco = 0
    separarstrings = []
    stringsLimpas = []
    limparstring = []
    guardarmatchstrings = []
    connection_string = []

    # Pega a lista de connections strings
    try:
        cnxn2 = pyodbc.connect(
            'DRIVER=SQL Server;SERVER=' + server + ';DATABASE=' + bases[
                num] + ';ENCRYPT=not;UID=' + username + ';PWD=' + password)
        cursor2 = cnxn2.cursor()
        cursor2.execute('SELECT [CONNECTION_STRING] FROM ' + bases[num] + '.[dbo].[KAIROS_DATABASES]')
        listaConnectionString = cursor2.fetchall()
    except pyodbc.DatabaseError as err:
        cursor2.rollback()
    else:
        cursor2.commit()
    finally:
        print("Consulta no banco de muro realizada com sucesso.")
        arquivo.write("\n" + datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Consulta no banco de muro realizada com sucesso.")
        print('Quantidade de registros encontrados: ' + str(len(listaConnectionString)))
        arquivo.write("\n" + datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Quantidade de registros encontrados: " + str(
            len(listaConnectionString)))

    # separar o nome do banco nas connection strings
    for i in range(len(listaConnectionString)):
        guardarstring.append(str(listaConnectionString[i]))
        stringsseparadas = guardarstring[i].split(';')
        nomebanco = stringsseparadas[1]
        tamnomebanco = len(nomebanco)
        listaNomesBancos.append(nomebanco[16:tamnomebanco])
        continue

    # separar o nome do banco nas instancias
    for j in range(len(listasStringInstancia)):
        guardabancoinstancia.append(str(listasStringInstancia[j]))
        nomebancoinstancia = guardabancoinstancia[j]
        tamnomebancoinstancia = len(nomebancoinstancia)
        tamnomebancoinstancia -= 4
        separarstrings.append(nomebancoinstancia[2:tamnomebancoinstancia])
        listaBancosInstancia.append(separarstrings[j])
        continue

    # Comparação dos bancos com strings
    for k in range(len(listaNomesBancos)):
        for l in range(len(listaBancosInstancia)):
            if listaNomesBancos[k] == listaBancosInstancia[l]:
                connection_string.append(listaConnectionString[k])
                guardarmatchstrings.append('são iguais: ' + str(listaBancosInstancia[l]) + ' ' + str(listaNomesBancos[k]))
            continue
        continue
    print("Quantidade de bancos que deram Match: " + str(len(connection_string)))
    arquivo.write("\n" + datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Quantidade de bancos que deram Match: " + str(len(connection_string)))

    # Limpar as strings para inserir no banco
    for j in range(len(connection_string)):
        guardarstring.append(str(connection_string[j]))
        stringsuja = guardarstring[j]
        tamanhodastring = len(stringsuja)
        tamanhodastring -= 4
        limparstring.append(stringsuja[2:tamanhodastring])
        stringsLimpas.append(limparstring[j])
        continue

    # Inserindo as connections strings no banco muro temporario
    if len(stringsLimpas) > 0:
        try:
            cnxn4 = pyodbc.connect(
                'DRIVER=SQL Server;SERVER=' + server + ';DATABASE=' + databaseupdate + ';ENCRYPT=not;UID=' + username + ';PWD=' + password)
            cursor4 = cnxn4.cursor()
        except pyodbc.DatabaseError as err:
            cursor4.rollback()
        else:
            cursor4.commit()
        finally:
            for p in range(len(stringsLimpas)):
                cursor4.execute(
                'INSERT INTO [dbo].[KAIROS_DATABASES]([CONNECTION_STRING],[DATABASE_VERSION],[FL_MAQUINA_CALCULO])VALUES(?,?,0)',
                stringsLimpas[p],versaodatabases).rowcount
                continue
            cursor4.commit()
        print("Registros inseridos com sucesso no banco: " + databaseupdate + "\n")
        arquivo.write("\n" + datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Registros inseridos com sucesso no banco: " + databaseupdate)
    else:
        print("Não a registros para serem inseridos no banco: " + databaseupdate + "\n")
        arquivo.write("\n" + datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + " - INFO - " + "Não a registros para serem inseridos no banco: " + databaseupdate)


    # Logando as connection string
    quant = 1
    for o in range(len(connection_string)):
        arquivo.writelines("\n" + datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S - ") + str(quant) + " - " + str(
            connection_string[o]))
        quant += 1
        continue

    if num < 4:
        num += 1
    print("\n" + "Concluido a parte " + str(num) + " do processo, de um total de " + str(len(bases)) + " partes.")
    arquivo.write("\n" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " - INFO - " + "Concluido a parte "  + str(
        num) + " parte do processo, de um total de " + str(len(bases)) + " partes.")
    continue

datafim = datetime.datetime.now()
print('Fim da operação: ' + str(datafim) + "\n")
arquivo.write("\n" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " - INFO - " + 'Fim da operação')

input("PRESSIONE ENTER PARA FINALIZAR...")
