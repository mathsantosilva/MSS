# coding: utf-8
import datetime
import json
import os
import re
import sys
import pyodbc

def data_atual():
   data_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
   return data_hora


def criar_config(arquivo_principal):

    while True:
        print("\n- Tela - Criação de config")
        arquivo_principal.write(f"\n{data_atual()} - INFO - Tela - Criação de config ")
        nome_escolhido = input("- Insira o nome que deseja para o arquivo de config: (Sem o .json) \nEscolha: ")
        nome_config = nome_escolhido + ".json"

        if os.path.exists("Config\\" + nome_config):
            print("- Já existe um arquivo .json com o mesmo nome")
            print("- Informe outro nome para o arquivo config")
            continue
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
}
"configs_restaurar_download": {
    "server_principal":"",
    "username": "",
    "password": ""
}
}
    """)
            print("- Novo config criado com sucesso, configure e selecione para ser utilizado")
            arquivo_principal.write(f"\n{data_atual()} - INFO - Novo config criado com sucesso, configure e selecione para ser utilizado ")
            break


def sair():
    sys.exit(200)


def valida_banco_update(arquivo, infos_config, num):

    while True:
        if infos_config['bases_muro'][num] == 'qcmaint_kairos_base_muro' or infos_config['bases_muro'][num] == 'qcdev_kairos_base_muro':
            if infos_config['database_update_br'] != '':
                database_update = infos_config['database_update_br']
                break
            else:
                print("- Não foi inserido no arquivo de config o apontamento para o banco Muro update BR")
                arquivo.write(
                    f"{data_atual()} - ERRO - Não foi inserido no arquivo de config o apontamento para o banco Muro update BR ")
                database_update = input("Insira o nome da base que será usada: ").lower()
                arquivo.write(f"\n{data_atual()} - INFO - Inserido manualmente a base: {database_update} ")

        elif infos_config['bases_muro'][num] == "qcmaint_kairos_base_muro_mx" or infos_config['bases_muro'][num] == "qcdev_kairos_base_muro_mx":
            if infos_config['database_update_mx'] != '':
                database_update = infos_config['database_update_mx']
            else:
                print("-  Não foi inserido no arquivo de config o apontamento para o banco Muro update MX")
                arquivo.write(
                    f"{data_atual()} - ERRO - Não foi inserido no arquivo de config o apontamento para o banco Muro update MX ")
                database_update = input("Insira o nome da base que será utilizada: ").lower()
                arquivo.write(f"\n{data_atual()} - INFO - Inserido manualmente a base: {database_update} ")

        elif infos_config['bases_muro'][num] == "qcmaint_kairos_base_muro_pt" or infos_config['bases_muro'][num] == "qcdev_kairos_base_muro_pt":
            if infos_config['database_update_pt'] != '':
                database_update = infos_config['database_update_pt']
            else:
                print("- Não foi inserido no arquivo de config o apontamento para o banco Muro update PT")
                arquivo.write(
                    f"{data_atual()} - ERRO - Não foi inserido no arquivo de config o apontamento para o banco Muro update PT ")
                database_update = input("Insira o nome da base que será utilizada: ").lower()
                arquivo.write(f"\n{data_atual()} - INFO - Inserido manualmente a base: {database_update} ")

        elif infos_config['bases_muro'][num] == "qcmaint_mdcomune_base_muro" or infos_config['bases_muro'][num] == "qcdev_mdcomune_base_muro":
            if infos_config['database_update_md'] != '':
                database_update = infos_config['database_update_md']
            else:
                print("- Não foi inserido no arquivo de config o apontamento para o banco Muro update MD")
                arquivo.write(
                    f"{data_atual()} - ERRO - Não foi inserido no arquivo de config o apontamento para o banco Muro update MD ")
                database_update = input("Insira o nome da base que será utilizada: ").lower()
                arquivo.write(f"\n{data_atual()} - INFO - Inserido manualmente a base: {database_update} ")
        else:
            print("- Não foi possível achar uma opção compativel com o banco de muro")
            print("- Insira o banco de Update manualmente")
            arquivo.write(
                f"{data_atual()} - ERRO - Não foi possível achar uma opção compativel com o banco de muro ")
            arquivo.write(
                f"{data_atual()} - ERRO - Insira o banco de Update manualmente ")
            database_update = input("Insira o nome da base que será utilizada: ").lower()
            arquivo.write(f"\n{data_atual()} - INFO - Inserido manualmente a base: {database_update} ")
        if database_update == "":
            continue
        else:
            break
    return database_update


def download_backup(arquivo_principal, arquivo_backup, infos_config):

    print("\n- Tela - Download Backup")
    arquivo_principal.write(f"\n{data_atual()} - INFO - Tela - Download Backup ")

    print(f"- Inicio da operação Download Backup {data_atual()}")
    arquivo_backup.write(f"{data_atual()} - INFO - Inicio da operação Download Backup ")

    endereco_download = input("|Insira a URL de backup gerada no discord: ")
    arquivo_backup.write(f"\n{data_atual()} - INFO - Inserida a URL de Download: {endereco_download} ")

    comando = f"""xp_cmdshell 'powershell.exe -file C:\\wget\\download.ps1 bkp "{endereco_download}"'"""

    try:
        cnxnrp1 = pyodbc.connect(
            f"DRIVER=SQL Server;SERVER={infos_config['server_principal']};ENCRYPT=not;UID={infos_config['username_principal']};PWD={infos_config['password_principal']}")
        cursorrp1 = cnxnrp1.cursor()
        cursorrp1.execute(comando)
        result = cursorrp1.fetchall()
    except (Exception or pyodbc.DatabaseError) as err:
        print("- Falha ao tentar executar o comando " + str(err))
        arquivo_backup.write(f"\n{data_atual()} - ERRO - Falha ao tentar executar o comando: {err} ")
    else:
        cursorrp1.commit()

        print(f"\n- Sucesso ao realizar Download do backup ")
        arquivo_backup.write(f"\n{data_atual()} - INFO - Sucesso ao realizar Download do backup ")

        print(f"- Resultado:")
        arquivo_backup.write(f"\n{data_atual()} - INFO - Resultado:")

        for incs in range(len(result)):

            semi_separado = (str(result[incs])).split("'")
            if len(semi_separado) > 1:
                separado = semi_separado[1].split("(")
                limpo = separado[0]
                print('- ' + str(limpo))
                arquivo_backup.write(f"\n{data_atual()} - INFO - {limpo}")

            else:
                limpo = semi_separado[0]
                print("- " + str(limpo))
                arquivo_backup.write(f"\n{data_atual()} - INFO - {limpo}")

        cursorrp1.close()
    finally:
        print("- Processo finalizado")
        arquivo_backup.write(f"\n{data_atual()} - INFO - Processo finalizado \n")

    arquivo_backup.close()


def restaurar_banco(arquivo_principal, arquivo_restauracao, infos_config):

    cnxnrs = ''
    cursorrs = ''

    print("\n- Tela - Restauração de banco")
    arquivo_principal.write(f"\n{data_atual()} - INFO - Tela - Restauração de banco ")

    print(f"- Inicio da operação Restauração de banco {data_atual()}")
    arquivo_restauracao.write(f"{data_atual()} - INFO - Inicio da operação Restauração de banco ")

    nome_banco_restaurado = input("|Insira o nome do banco apresentado no discord(Sem o .bak): ")
    arquivo_restauracao.write(f"\n{data_atual()} - INFO - Inserido o nome do banco apresentado no discord: {nome_banco_restaurado} ")

    arquivo_restauracao.write(f"\n{data_atual()} - INFO - Escolhido o servidor: {infos_config['server']} ")

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
            f"DRIVER=SQL Server;SERVER={infos_config['server_principal']};ENCRYPT=not;UID={infos_config['username_principal']};PWD={infos_config['password_principal']}")
        cnxnrs.timeout = 12
        cursorrs = cnxnrs.cursor()
        cursorrs.execute(comando_criar_device)
        result_criar_device = cursorrs.messages
    except (Exception or pyodbc.DatabaseError) as err:
        print("- Falha ao tentar executar o comando de criação de device de backup " + str(err))
        arquivo_restauracao.write(f"\n{data_atual()} - ERRO - Falha ao tentar executar o comando de criação de device de backup: {err} ")
    else:
        cursorrs.commit()
        print(f"\n- Sucesso ao realizar Criar Device de Backup")
        arquivo_restauracao.write(f"\n{data_atual()} - INFO - Sucesso ao realizar Criar Device de Backup ")
        status_etapa1 = True
        for incs in range(len(result_criar_device)):
            separados = result_criar_device[0][1].split("]")
            mensagem = separados[3]
            print(f"- Comando(Criação Device) -  Mensagem SQL: {mensagem}  ")
            arquivo_restauracao.write(f"\n{data_atual()} - INFO - Comando(Criação Device) -  Mensagem SQL: {mensagem} ")

    if status_etapa1:
        try:
            cursorrs = cnxnrs.cursor()
            cursorrs.execute(comando_restaurar_banco)
        except (Exception or pyodbc.DatabaseError) as err:
            print("- Falha ao tentar executar o comando de restauração de banco: " + str(err))
            arquivo_restauracao.write(
                f"\n{data_atual()} - ERRO - Falha ao tentar executar o comando de restauração de banco: {err} ")
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
            print(f"- Sucesso ao realizar a restauração do banco")
            arquivo_restauracao.write(f"\n{data_atual()} - INFO - Sucesso ao realizar a restauração do banco ")

            tam = len(mensagens)-3
            for incs in range(posicao):
                print(f"- Comando(Restauração DB) -  Mensagem SQL: {mensagens[tam]}  ")
                arquivo_restauracao.write(f"\n{data_atual()} - INFO - Comando(Restauração DB) -  Mensagem SQL: {mensagens[tam]} ")
                tam += 1

            try:
                cursorrs.execute(comando_ativar_banco)
                result_ativar_banco = cursorrs.messages
            except (Exception or pyodbc.DatabaseError) as err:
                print("- Falha ao tentar executar o comando de Ativação do banco: " + str(err))
                arquivo_restauracao.write(f"\n{data_atual()} - ERRO - Falha ao tentar executar o comando de Ativação do banco: {err} ")
            else:
                tam_result = len(result_ativar_banco)-1
                while tam_result < len(result_ativar_banco):
                    separados = result_ativar_banco[tam_result][1].split("]")
                    mensagem = separados[3]
                    print(f"- Comando(Ativação DB) -  Mensagem SQL: {mensagem}  ")
                    arquivo_restauracao.write(f"\n{data_atual()} - INFO - Comando(Ativação DB) -  Mensagem SQL: {mensagem} ")
                    tam_result += 1

                try:
                    cursorrs.execute(comando_checar_banco)
                    result_check = cursorrs.messages
                except (Exception or pyodbc.DatabaseError) as err:
                    print("- Falha ao tentar executar o comando de checagem do banco: " + str(err))
                    arquivo_restauracao.write(f"\n{data_atual()} - ERRO - Falha ao tentar executar o comando de checagem do banco: {err} ")
                else:
                    looping = True
                    tam_result = len(result_check) - 2
                    while looping:
                        if tam_result < len(result_check):
                            separados = result_check[tam_result][1].split("]")
                            mensagem = separados[3]
                            print(f"- Comando(Checagem DB) - Mensagem SQL: {mensagem}")
                            arquivo_restauracao.write(f"\n{data_atual()} - INFO - Comando(Checagem DB) - Mensagem SQL: {mensagem} ")
                            tam_result += 1
                        else:
                            looping = False
                    try:
                        cursorrs.execute(comando_excluir_device)
                        result_excluir_device = cursorrs.messages
                    except (Exception or pyodbc.DatabaseError) as err:
                        print("- Falha ao tentar executar o comando de checagem do banco: " + str(err))
                        arquivo_restauracao.write(f"\n{data_atual()} - ERRO - Falha ao tentar executar o comando de checagem do banco: {err} ")
                    else:
                        for incs in range(len(result_excluir_device)):
                            separados = result_excluir_device[0][1].split("]")
                            mensagem = separados[3]
                            print(f"- Comando(Exclusão Device) -  Mensagem SQL: {mensagem}  ")
                            arquivo_restauracao.write(f"\n{data_atual()} - INFO - Comando(Exclusão Device) -  Mensagem SQL: {mensagem} ")

                        try:
                            cursorrs.execute(comando_primeiro_script)
                            associar_owner = cursorrs.messages
                        except (Exception or pyodbc.DatabaseError) as err:
                            print("- Falha ao tentar executar o comando de associação do Owner: " + str(err))
                            arquivo_restauracao.write(f"\n{data_atual()} - ERRO - Falha ao tentar executar o comando de associação do Owner:  {err} ")
                        else:
                            separados = associar_owner[0][1].split("]")
                            mensagem = separados[3]
                            print(f"- Comando(Associar Owner) - Mensagem SQL: {mensagem}")
                            arquivo_restauracao.write(f"\n{data_atual()} - INFO - Comando(Script Associar Owner) - Mensagem SQL: {mensagem} ")

                            try:
                                cursorrs.execute(comando_segundo_script)
                                compatibilidade = cursorrs.messages
                            except (Exception or pyodbc.DatabaseError) as err:
                                print("- Falha ao tentar executar o comando " + str(err))
                                arquivo_restauracao.write(f"\n{data_atual()} - ERRO - Falha ao tentar executar o comando: {err} ")
                            else:
                                separados = compatibilidade[0][1].split("]")
                                mensagem = separados[3]
                                print(f"- Comando(Compatibilidade) - Mensagem SQL: {mensagem}")
                                arquivo_restauracao.write(f"\n{data_atual()} - INFO - Comando(Script Compatibilidade) - Mensagem SQL: {mensagem} ")
        cursorrs.close()

    print("- Processo finalizado")
    arquivo_restauracao.write(f"\n{data_atual()} - INFO - Processo finalizado")
    arquivo_restauracao.close()


class BuscaMuro:

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
    nomes['arquivo_validar'] = 'validar_atualizacao'
    version = "1.5.2"

    def validar_atualizacao(self, arquivo_principal, infos_config):

        tam_base_muro = len(infos_config['bases_muro'])

        arquivo_validar = open(f"Log\\{self.nomes['arquivo_validar']}.txt", "a")

        print("\n- Tela - Validar atualização")
        arquivo_principal.write(f"\n{data_atual()} - INFO - Tela - Validar atualização")

        print(f"- Inicio da validação do banco update {data_atual()}")
        arquivo_validar.write(f"{data_atual()} - INFO - Inicio da validação do banco update ")

        for num in range(tam_base_muro):
            database_update = valida_banco_update(arquivo_validar, infos_config, num)

            try:
                cnxnrp = pyodbc.connect(
                    f"DRIVER=SQL Server;SERVER={infos_config['server']};DATABASE={database_update};ENCRYPT=not;UID={infos_config['username']};PWD={infos_config['password']}")
                cursorrp = cnxnrp.cursor()
                comando = f"select [database_version],  count(database_version) Quantidade from [dbo].[KAIROS_DATABASES] group by [database_version]"
                cursorrp.execute(comando)
                result = cursorrp.fetchall()
            except (Exception or pyodbc.DatabaseError) as err:
                print(f"- Falha ao tentar consultar banco de update: {err}")
                arquivo_validar.write(f"\n{data_atual()} - ERRO - Falha ao tentar consultar banco de muro update: {err}")
            else:
                print(f"- Sucesso na consultar no banco de update: {database_update}")
                arquivo_validar.write(f"\n{data_atual()} - INFO - Sucesso na consultar no banco de update")

                if len(result) > 0:
                    for n in range(len(result)):
                        print(f"- Version: {result[n][0]} - Quantidade: {result[n][1]}")
                        arquivo_validar.write(f"\n{data_atual()} - INFO - Version: {result[n][0]} - Quantidade: {result[n][1]}")
                else:
                    print(f"- Não foram retornados registros no banco: {database_update}")
                    arquivo_validar.write(f"\n{data_atual()} - INFO - Não foram retornados registros no banco:")

            if num < 4:
                num += 1
            print(f"- Concluído a parte {num} do processo, de um total de {tam_base_muro} partes. ")
            arquivo_validar.write(f"\n{data_atual()} - INFO - Concluído a parte {num} do processo, de um total de {len(infos_config['bases_muro'])} partes. ")
            continue

        print(f"- Fim da operação Validar atualização {data_atual()}")
        arquivo_validar.write(f"\n{data_atual()} - INFO - Fim da operação Validar atualização \n")
        arquivo_validar.close()

    def escolher_config(self, arquivo_principal):

        arquivo_config = ''
        infos_config = dict()
        certo = True

        while certo:
            while certo:

                print("\n- Tela - Configs")
                arquivo_principal.write(f"\n{data_atual()} - INFO - Tela - Configs ")
                print("- Escolha qual função deseja utilizar: ")
                escolha_menu = input("""|1 - Utilizar config existente
|2 - Criar um config em branco
|3 - Voltar
|Escolha:""")

                if escolha_menu == "1":
                    print("- Opção 1 selecionada - Utilizar config existente")
                    arquivo_principal.write(f"\n{data_atual()} - INFO - Opção 1 selecionada - Utilizar config existente ")
                    print("\n- Tela - Config existente")
                    arquivo_principal.write(f"\n{data_atual()} - INFO - Tela - Config existente ")
                    while certo:
                        cont_arquivos = 1
                        dir_arquivos_configs = []
                        dir_arquivo_index = []
                        print("Arquivos Json dentro da pasta config: ")
                        arquivos_diretorio = os.listdir(self.nomes['pasta_config'])
                        for arquivo_dir in arquivos_diretorio:
                            match_arquivo = re.search("\\.json$", arquivo_dir)
                            if match_arquivo is not None:
                                dir_arquivos_configs.append(arquivo_dir)
                                dir_arquivo_index.append(arquivos_diretorio.index(arquivo_dir))
                        for itens_arquivos in dir_arquivos_configs:
                            print(f"|{cont_arquivos} - {itens_arquivos}")
                            cont_arquivos += 1

                        if escolha_menu == "1":
                            tamanho_configs = len(dir_arquivo_index) + 1
                            escolha_arquivo = input("""|Insira o numero correspondente ao config desejado. (Ele deverá estar na pasta config)
|Escolha: """)
                            if escolha_arquivo.isdigit():
                                if int(escolha_arquivo) in range(1, tamanho_configs):
                                    arquivo_config = arquivos_diretorio[dir_arquivo_index[int(escolha_arquivo) - 1]]
                                else:
                                    print(f'Opção errada, insira novamente')
                                    continue
                            else:
                                print(f'Opção errada, insira novamente')
                                continue

                            # Validando o arquivo de config
                            try:
                                if os.path.isfile("Config\\" + arquivo_config):
                                    config_bjt = open("Config\\" + arquivo_config, "r")
                                    config_json = config_bjt.read().lower()
                                    params_dict = json.loads(config_json)
                                    certo = False
                                else:
                                    print(
                                        f"- Não foi possível encontrar um .JSON com esse nome na pasta {self.nomes['diretorio_config']}, tente novamente!")
                                    arquivo_principal.write(
                                        f"{data_atual()} - INFO - Não foi possível encontrar um .JSON com esse nome na pasta {self.nomes['diretorio_config']}, tente novamente! ")
                                    certo = True
                                    continue
                            except Exception as name_error:
                                print(
                                    f"- Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente: {name_error}")
                                arquivo_principal.write(
                                    f"{data_atual()} - INFO - Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente: {name_error} ")
                                certo = True
                                continue

                            try:
                                if params_dict["conexao"]["server"] == '':
                                    print("- O valor do server não foi especificado no config, Informe e tente novamente ")
                                    arquivo_principal.write(
                                        f"{data_atual()} - INFO - O valor do server não foi especificado no config, Informe e tente novamente ")
                                    certo = True
                                    continue
                                elif params_dict["conexao"]["username"] == '':
                                    print(
                                        "-  O valor do Username não foi especificado no config, Informe e tente novamente ")
                                    arquivo_principal.write(
                                        f"{data_atual()} - INFO - O valor do Username não foi especificado no config, Informe e tente novamente ")
                                    certo = True
                                    continue
                                elif params_dict["conexao"]["password"] == '':
                                    print(
                                        "-  O valor do Password não foi especificado no config, Informe e tente novamente ")
                                    arquivo_principal.write(
                                        f"{data_atual()} - INFO - O valor do Password não foi especificado no config, Informe e tente novamente ")
                                    certo = True
                                    continue
                                elif not params_dict["bases_muro"]:
                                    print(
                                        "-  O valor do Base_Muro não foi especificado no config, Informe e tente novamente ")
                                    arquivo_principal.write(
                                        f"{data_atual()} - INFO - O valor do Base_Muro não foi especificado no config, Informe e tente novamente ")
                                    certo = True
                                    continue
                            except Exception as name_error:
                                print(
                                    f"-  Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente: {name_error}")
                                arquivo_principal.write(
                                    f"{data_atual()} - INFO - Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente: {name_error} ")
                                certo = True
                                continue

                            try:
                                # Carregar config
                                infos_config['server'] = params_dict["conexao"]["server"]
                                infos_config['username'] = params_dict["conexao"]["username"]
                                infos_config['password'] = params_dict["conexao"]["password"]
                                infos_config['database_update_br'] = params_dict["database_update_br"]
                                infos_config['database_update_mx'] = params_dict["database_update_mx"]
                                infos_config['database_update_pt'] = params_dict["database_update_pt"]
                                infos_config['database_update_md'] = params_dict["database_update_md"]
                                infos_config['bases_muro'] = params_dict["bases_muro"]
                            except Exception as name_error:
                                print(
                                    f"-  Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente: {name_error}")
                                arquivo_principal.write(
                                    f"{data_atual()} - INFO - Existem erros de formatação no arquivo de config escolhido, corrija e tente novamente: {name_error} ")
                            else:
                                infos_config['status'] = True
                                # Limpando strings vazias na base muro
                                limpa_muro_tam = len(infos_config['bases_muro'])
                                for num in range(0, limpa_muro_tam, +1):
                                    if '' in infos_config['bases_muro']:
                                        infos_config['bases_muro'].remove('')
                                        continue
                                    else:
                                        break
                                try:
                                    infos_config['server_principal'] = params_dict["configs_restaurar_download"]["server_principal"]
                                    infos_config['username_principal'] = params_dict["configs_restaurar_download"]["username_principal"]
                                    infos_config['password_principal'] = params_dict["configs_restaurar_download"]["password_principal"]
                                except Exception as name_error:
                                    print(
                                        f"- O config esta estava desatualizado, foram inseridas as novas tags no config, configure elas para usar as rotinas {self.nomes['arquivo_download_backup']} e {self.nomes['arquivo_restaurar_banco']}: {name_error}")
                                    arquivo_principal.write(
                                        f"{data_atual()} - INFO - O config esta estava desatualizado, foram inseridas as novas tags no config, configure elas para usar as rotinas {self.nomes['arquivo_download_backup']} e {self.nomes['arquivo_restaurar_banco']}: {name_error}")
                                    infos_config['server_principal'] = ""
                                    infos_config['username_principal'] = ""
                                    infos_config['password_principal'] = ""
                                    atualizar_config = open("Config\\" + arquivo_config, "w")
                                    bases_utilizadas = str(f"{infos_config['bases_muro']}")
                                    bases_utilizadas = bases_utilizadas.replace("'", '"')
                                    server_utilizado = infos_config['server']
                                    if "\\" in server_utilizado:
                                        server_utilizado = server_utilizado.replace('\\', '\\\\')
                                    config_atualizado = f"""{{
    "database_update_br": "{infos_config['database_update_br']}",
    "database_update_mx": "{infos_config['database_update_mx']}",
    "database_update_pt": "{infos_config['database_update_pt']}",
    "database_update_md": "{infos_config['database_update_md']}",
    "bases_muro": {bases_utilizadas},
    "conexao": {{
        "server": "{server_utilizado}",
        "username": "{infos_config['username']}",
        "password": "{infos_config['password']}"
    }},
    "configs_restaurar_download": {{
        "server_principal": "",
        "username_principal": "",
        "password_principal": ""
    }}
}}
"""
                                    atualizar_config.write(config_atualizado)

                                    atualizar_config.close()
                        continue
                    continue
                elif escolha_menu == "2":
                    print("- Opção 2 selecionada - Criar Config")
                    arquivo_principal.write(f"\n{data_atual()} - INFO - Opção 2 selecionada - Criar Config ")
                    criar_config(arquivo_principal)
                    certo = True
                    continue
                elif escolha_menu == "3":
                    print("- Opção 3 selecionada - Voltar")
                    arquivo_principal.write(f"\n{data_atual()} - INFO - Opção 3 selecionada - Voltar ")
                    infos_config['status'] = False
                    return infos_config

                else:
                    print("- Opção invalida, insira novamente \n")
                    arquivo_principal.write(f"\n{data_atual()} - INFO - Opção invalida, insira novamente ")
                    certo = True
                    continue
            continue

        print(f"- Config escolhido: {arquivo_config}")
        arquivo_principal.write(f"\n{data_atual()} - INFO - Config escolhido: {arquivo_config} ")
        arquivo_principal.write(f"\n{data_atual()} - INFO - Server: {infos_config['server']} ")
        arquivo_principal.write(f"\n{data_atual()} - INFO - Base Muro Update BR: {infos_config['database_update_br']} ")
        arquivo_principal.write(f"\n{data_atual()} - INFO - Base Muro Update MX: {infos_config['database_update_mx']} ")
        arquivo_principal.write(f"\n{data_atual()} - INFO - Base Muro Update PT: {infos_config['database_update_pt']} ")
        arquivo_principal.write(f"\n{data_atual()} - INFO - Base Muro Update MD: {infos_config['database_update_md']} ")
        arquivo_principal.write(f"\n{data_atual()} - INFO - Bases Muro: {infos_config['bases_muro']} ")

        return infos_config

    def manipular_banco_muro(self, arquivo_principal, infos_config):
        lista_string_instancia = ''
        cursor1 = ''

        status_consulta = False

        arquivo = open(f"Log\\{self.nomes['arquivo_busca_bancos']}.txt", "a")

        print("\n- Tela - Busca muro")
        arquivo_principal.write(f"\n{data_atual()} - INFO - Tela - Busca muro ")

        print(f"- Inicio da operação Busca muro {data_atual()}")
        arquivo.write(f"{data_atual()} - INFO - Inicio da operação Busca muro ")

        versao_databases = input("- Especifique para qual versão quer fazer o downgrade: ")

        print(f"- Version para downgrade: {versao_databases}")
        arquivo.write(f"\n{data_atual()} - INFO - Version para downgrade: {versao_databases} ")

        # Pegar a lista de bancos da instancia
        print(f"\n- Iniciando a busca dos bancos na instância: {infos_config['server']} ")
        arquivo.write(f"\n{data_atual()} - INFO - Iniciando a busca dos bancos na instância: {infos_config['server']} ")

        try:
            cnxn1 = pyodbc.connect(f"DRIVER=SQL Server;SERVER={infos_config['server']};ENCRYPT=not;UID={infos_config['username']};PWD={infos_config['password']}")
            cursor1 = cnxn1.cursor()
            cursor1.execute("SELECT name FROM sys.databases;")
            lista_string_instancia = cursor1.fetchall()
        except (Exception or pyodbc.DatabaseError) as err:
            print(f"- Falha ao tentar buscar os bancos da instancia {err}")
            arquivo.write(f"\n{data_atual()} - ERRO - Falha ao tentar buscar os bancos da instancia {err} ")
        else:
            cursor1.commit()
            print("- Consulta na instância realizada com sucesso.")
            arquivo.write(f"\n{data_atual()} - INFO - Consulta na instância realizada com sucesso. ")

            print(f"- Quantidade de bancos encontrados: {len(lista_string_instancia)}")
            arquivo.write(f"\n{data_atual()} - INFO - Quantidade de bancos encontrados: {len(lista_string_instancia)} ")
            status_consulta = True
        finally:
            print("- Processo Finalizado\n")
            arquivo.write(f"\n{data_atual()} - INFO - Processo Finalizado ")

        if status_consulta:

            # Iniciando processo banco muro.
            for num in range(len(infos_config['bases_muro'])):

                print(f"- Iniciando o processo no banco: {infos_config['bases_muro'][num]}")
                arquivo.write(f"\n{data_atual()} - INFO - Iniciando o processo no banco: {infos_config['bases_muro'][num]} ")

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
                print("- Iniciando a Busca no banco de muro")
                arquivo.write(f"\n{data_atual()} - INFO - Iniciando a Busca no banco de muro ")
                try:
                    cursor1.execute(f"SELECT [DATABASE_ID],[CONNECTION_STRING] FROM {infos_config['bases_muro'][num]}.[dbo].[KAIROS_DATABASES]")
                    lista_connection_string = cursor1.fetchall()

                except (Exception or pyodbc.DatabaseError) as err:
                    print(f"- Falha ao tentar consultar banco de muro: {err}")
                    arquivo.write(f"\n{data_atual()} - ERRO - Falha ao tentar consultar banco de muro {err} ")
                else:
                    cursor1.commit()
                    print("- Consulta no banco de muro realizada com sucesso")
                    arquivo.write(f"\n{data_atual()} - INFO - Consulta no banco de muro realizada com sucesso ")

                    print(f"- Quantidade de registros encontrados: {len(lista_connection_string)}")
                    arquivo.write(f"\n{data_atual()} - INFO - Quantidade de registros encontrados: {len(lista_connection_string)} ")
                finally:
                    print("- Processo Finalizado\n")
                    arquivo.write(f"\n{data_atual()} - INFO - Processo Finalizado ")

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
                print("- Iniciando a comparação dos bancos")
                arquivo.write(f"\n{data_atual()} - INFO - Iniciando a comparação dos bancos ")
                for comparar in range(len(lista_banco_instancia)):
                    if lista_banco_instancia[comparar] in lista_nome_banco:
                        index_banco.append(lista_nome_banco.index(lista_banco_instancia[comparar]))
                        index_banco.sort()
                    continue

                for nums in range(len(index_banco)):
                    connection_string.append(lista_connection_string[index_banco[nums]])
                    database_id.append(lista_id_banco[index_banco[nums]])

                if len(connection_string) > 0:
                    print("- Quantidade de bancos que deram Match: " + str(len(connection_string)))
                    arquivo.write(f"\n{data_atual()} - INFO - Quantidade de bancos que deram Match: {len(connection_string)} ")
                else:
                    print("- Não foram encontrados Match na comparação de bancos")
                    arquivo.write(f"\n{data_atual()} - INFO - Não foram encontrados Match na comparação de bancos ")
                print("- Processo Finalizado\n")
                arquivo.write(f"\n{data_atual()} - INFO - Processo Finalizado ")

                # Limpar as strings para inserir no banco
                for lim in range(len(connection_string)):
                    guarda_string_bm.append(str(connection_string[lim].CONNECTION_STRING))
                    string = guarda_string_bm[lim]
                    string_limpa.append(string)
                    continue

                database_update = valida_banco_update(arquivo, infos_config, num)
                if len(string_limpa) > 0:
                    # Limpeza base muro UPDATE
                    print(f"- Iniciando a limpeza no banco de muro update: {database_update}")
                    arquivo.write(f"\n{data_atual()} - INFO - Iniciando a limpeza no banco de muro update: {database_update} ")
                    try:
                        cursor1.execute(f'DELETE FROM {database_update}.[dbo].[KAIROS_DATABASES]')

                    except (Exception or pyodbc.DatabaseError) as err:
                        print(f"- Falha ao tentar zerar o banco update {err}")
                        arquivo.write(f"\n{data_atual()}  - ERRO - Falha ao tentar zerar o banco de muro update {err} ")
                    else:
                        cursor1.commit()
                        print(f"- banco {database_update} zerado com sucesso")
                        arquivo.write(f"\n{data_atual()} - INFO - Banco {database_update} zerado com sucesso ")
                    finally:
                        print("- Processo Finalizado\n")
                        arquivo.write(f"\n{data_atual()} - INFO - Processo Finalizado ")
                else:
                    print("- Não foi realizada a limpeza no banco: " + database_update)
                    arquivo.write(f"\n{data_atual()} - INFO - Não foi realizada a limpeza no banco: {database_update} ")
                    print("- Processo Finalizado\n")
                    arquivo.write(f"\n{data_atual()} - INFO - Processo Finalizado ")

                # Inserindo as connections strings no banco muro update
                print(f"- Iniciando a inserção das connection strings no banco muro update: {database_update}")
                arquivo.write(f"\n{data_atual()} - INFO - Iniciando a inserção das connection strings no banco muro update: {database_update} ")
                if len(string_limpa) > 0:
                    try:
                        cnxn1 = pyodbc.connect(f"DRIVER=SQL Server;SERVER={infos_config['server']};DATABASE={database_update};ENCRYPT=not;UID={infos_config['username']};PWD={infos_config['password']}")
                        cursor1 = cnxn1.cursor()

                        cursor1.execute("set identity_insert [dbo].[KAIROS_DATABASES]  on")
                        for incs in range(len(string_limpa)):
                            montar_comando = f"INSERT INTO [{database_update}].[dbo].[KAIROS_DATABASES] ([DATABASE_ID],[CONNECTION_STRING] ,[DATABASE_VERSION] ,[FL_MAQUINA_CALCULO] ,[FL_ATIVO]) VALUES({database_id[incs]},'{string_limpa[incs]}',{versao_databases},0, 1)"
                            cursor1.execute(montar_comando)
                            continue
                        cursor1.execute("set identity_insert [dbo].[KAIROS_DATABASES]  off")

                    except (Exception or pyodbc.DatabaseError) as err:
                        print(f"- Falha ao tentar inserir registros no banco update {err}")
                        arquivo.write(f"\n{data_atual()} - ERRO - Falha ao tentar inserir registros no banco update {err} ")
                    else:
                        cursor1.commit()
                        print("- Sucesso ao inserir connection Strings no Banco de muro Update  ")
                        arquivo.write(f"\n{data_atual()} - INFO - Sucesso ao inserir connection Strings no Banco de muro Update ")

                        # Logando as connection string
                        quant = 1
                        arquivo_strings = open(f"Log\\{self.nomes['arquivo_connection_strings']}.txt", "a")
                        arquivo_strings.write(
                            f"{data_atual()} - INFO - Buscar Bancos - Listando as connection strings utilizadas ")
                        arquivo_strings.write(f"\n{data_atual()} - INFO - Buscar Bancos - Ambiente: {infos_config['bases_muro'][num]} ")
                        for log in range(len(connection_string)):
                            arquivo_strings.writelines(f"\n{data_atual()} - INFO - {quant} - {connection_string[log]} ")
                            quant += 1
                            continue

                        arquivo_strings.write(f"\n{data_atual()} - INFO - Processo Finalizado \n")
                        arquivo_strings.close()
                        arquivo.write(
                            f"\n{data_atual()} - INFO - Listado as Connection Strings no arquivo: {self.nomes['arquivo_connection_strings']} ")

                    finally:
                        print("- Processo Finalizado\n")
                        arquivo.write(f"\n{data_atual()} - INFO - Processo Finalizado ")

                else:
                    print("- Não a registros para serem inseridos no banco: " + database_update)
                    arquivo.write(f"\n{data_atual()} - INFO - Não a registros para serem inseridos no banco: {database_update} ")
                    print("- Processo Finalizado\n")
                    arquivo.write(f"\n{data_atual()} - INFO - Processo Finalizado ")

                if num < 4:
                    num += 1
                print(f"- Concluído a parte {num} do processo, de um total de {len(infos_config['bases_muro'])} partes.")
                arquivo.write(f"\n{data_atual()} - INFO - Concluído a parte {num} do processo, de um total de {len(infos_config['bases_muro'])} partes. ")
                continue
            cursor1.close()
        else:
            print(f"- Erro na primeira etapa das buscas, o processo foi interrompido.")
            arquivo.write(
                f"\n{data_atual()} - INFO - Erro na primeira etapa das buscas, o processo foi interrompido. ")

        print(f"- Fim da operação Busca muro {data_atual()}")
        arquivo.write(f"\n{data_atual()} - INFO - Fim da operação Busca muro \n")
        arquivo.close()

    def replicar_version(self, arquivo_principal, infos_config):

        arquivo_replicar = open(f"Log\\{self.nomes['arquivo_replicar_version']}.txt", "a")

        print("\n- Tela - replicar version")
        arquivo_principal.write(f"\n{data_atual()} - INFO - Tela - replicar version ")

        print(f"- Inicio da operação replicar version {data_atual()}")
        arquivo_replicar.write(f"{data_atual()} - INFO - Inicio da operação replicar version")

        for num in range(len(infos_config['bases_muro'])):
            lista_registros_db = []
            lista_ids = []
            lista_versions = []
            lista_connection_string = []

            print(f"- Iniciando o processo no banco: {infos_config['bases_muro'][num]}")
            arquivo_replicar.write(f"\n{data_atual()} - INFO - Iniciando o processo no banco: {infos_config['bases_muro'][num]}")

            database_update = valida_banco_update(arquivo_replicar, infos_config, num)

            try:
                cnxnrp1 = pyodbc.connect(f"DRIVER=SQL Server;SERVER={infos_config['server']};DATABASE={database_update};ENCRYPT=not;UID={infos_config['username']};PWD={infos_config['password']}")
                cursorrp1 = cnxnrp1.cursor()
                cursorrp1.execute(f"SELECT * FROM {database_update}.[dbo].[KAIROS_DATABASES]")
                lista_registros_db = cursorrp1.fetchall()
            except (Exception or pyodbc.DatabaseError) as err:
                print("- Falha ao tentar consultar banco de muro update: " + str(err))
                arquivo_replicar.write(f"\n{data_atual()} - ERRO - Falha ao tentar consultar banco de muro update: {err}")
            else:
                cursorrp1.commit()
                cursorrp1.close()

                print(f"- Sucesso na consulta no banco de muro update: {database_update}")
                arquivo_replicar.write(f"\n{data_atual()} - INFO - Sucesso na consulta no banco de muro update: {database_update}")

                print(f"- Quantidade de registros encontrados: {len(lista_registros_db)}")
                arquivo_replicar.write(f"\n{data_atual()} - INFO - Quantidade de registros encontrados: {len(lista_registros_db)}")
            finally:
                print("- Processo finalizado")

            tam_busca_realizada = len(lista_registros_db)
            if tam_busca_realizada > 0:
                for nums in range(tam_busca_realizada):
                    lista_ids.append(lista_registros_db[nums].DATABASE_ID)
                    lista_versions.append(lista_registros_db[nums].DATABASE_VERSION)
                    lista_connection_string.append(lista_registros_db[nums].CONNECTION_STRING)
                    continue

                try:
                    cnxnrp2 = pyodbc.connect(f"DRIVER=SQL Server;SERVER={infos_config['server']};DATABASE={infos_config['bases_muro'][num]};ENCRYPT=not;UID={infos_config['username']};PWD={infos_config['password']}")
                    cursorrp2 = cnxnrp2.cursor()
                    for teste2 in range(tam_busca_realizada):
                        montar_comando = f"update [dbo].[KAIROS_DATABASES] set [DATABASE_VERSION] = {lista_versions[teste2]} where [DATABASE_ID] = {lista_ids[teste2]} and [CONNECTION_STRING] = '{lista_connection_string[teste2]}' "
                        cursorrp2.execute(montar_comando)
                        continue
                except (Exception or pyodbc.DatabaseError) as err:
                    print(f"- Falha ao tentar consultar banco de muro update: {err}")
                    arquivo_replicar.write(f"\n{data_atual()} - ERRO - Falha ao tentar consultar banco de muro update: {err}")
                else:
                    cursorrp2.commit()
                    cursorrp2.close()
                    print(f"- Sucesso ao inserir version no banco de muro: {infos_config['bases_muro'][num]}")
                    arquivo_replicar.write(f"\n{data_atual()} - INFO - Sucesso ao inserir version no banco de muro: {infos_config['bases_muro'][num]}")

                    # Logando as connection string
                    arquivo_replicar_strings = open(f"Log\\{self.nomes['arquivo_connection_strings']}.txt", "a")
                    arquivo_replicar_strings.write(f"{data_atual()} - INFO - Replicar Version - Listando as connection strings utilizadas ")
                    arquivo_replicar_strings.write(f"\n{data_atual()} - INFO - Replicar Version - Ambiente: {infos_config['bases_muro'][num]} ")
                    quant = 1
                    for log in range(tam_busca_realizada):
                        arquivo_replicar_strings.writelines(
                            f"\n{data_atual()} - INFO - {quant} - ID: {lista_ids[log]} - Version: {lista_versions[log]} ")
                        quant += 1
                        continue

                    arquivo_replicar_strings.write(f"\n{data_atual()} - INFO - Processo finalizado \n")
                    arquivo_replicar_strings.close()
                    arquivo_replicar.write(
                        f"\n{data_atual()} - INFO - Listado os version no arquivo: {self.nomes['arquivo_connection_strings']}")
                finally:
                    print("- Processo finalizado")
            else:
                print("- Não existem registros para alterar o version")
                arquivo_replicar.write(f"\n{data_atual()} - INFO - Não existem registros para alterar o version")

            if num < 4:
                num += 1

            print(f"- Concluído a parte {num} do processo, de um total de {len(infos_config['bases_muro'])} partes.")
            arquivo_replicar.write(f"\n{data_atual()} - INFO - Concluído a parte {num} do processo, de um total de {len(infos_config['bases_muro'])} partes.")
            continue

        print(f"- Fim da operação replicar version {data_atual()}")
        arquivo_replicar.write(f"\n{data_atual()} - INFO - Fim da operação replicar version \n")
        arquivo_replicar.close()

    def ferramentas_muro(self, arquivo_principal, infos_config):
        while True:
            print("\n- Tela - Ferramentas do Banco de muro")
            arquivo_principal.write(f"\n{data_atual()} - INFO - Tela - Ferramentas do Banco de muro ")
            print("- Qual operação deseja realizar: ")
            escolha = input("""|1 - Buscar Bancos
|2 - Validar Atualização
|3 - Replicar version
|4 - Trocar o config
|5 - Voltar ao Menu Principal
|6 - Sair
|Escolha: """)
            if str(escolha) == "6":
                print("- Opção 6 selecionada - Sair")
                arquivo_principal.write(f"\n{data_atual()} - INFO - Opção 6 selecionada - Sair ")
                arquivo_principal.close()
                sair()
            if str(escolha) != "6":
                match escolha:
                    case "1":
                        print("- Opção 1 selecionada - Buscar Bancos")
                        arquivo_principal.write(f"\n{data_atual()} - INFO - Opção 1 selecionada - Buscar Bancos ")
                        self.manipular_banco_muro(arquivo_principal, infos_config)
                    case "2":
                        print("- Opção 2 selecionada - Validar Atualização")
                        arquivo_principal.write(f"\n{data_atual()} - INFO - Opção 2 selecionada - Replicar version ")
                        self.validar_atualizacao(arquivo_principal, infos_config)
                    case "3":
                        print("- Opção 3 selecionada - Replicar version")
                        arquivo_principal.write(f"\n{data_atual()} - INFO - Opção 2 selecionada - Replicar version ")
                        self.replicar_version(arquivo_principal, infos_config)
                    case "4":
                        print("- Opção 4 selecionada - Trocar o config")
                        arquivo_principal.write(f"\n{data_atual()} - INFO - Opção 3 selecionada - Trocar o config ")
                        self.menu_bancos_muro(arquivo_principal)
                    case "5":
                        print("- Opção 5 selecionada - Voltar ao Menu Principal")
                        arquivo_principal.write(f"\n{data_atual()} - INFO - Opção 4 selecionada - Voltar ao Menu Principal ")
                        self.menu(arquivo_principal)
                    case "6":
                        return
                    case _:
                        print("-  Opção invalida, insira novamente!")
                        arquivo_principal.write(f"\n{data_atual()} - INFO - Opção invalida, insira novamente! ")
            else:
                print("-  Opção invalida, insira novamente!")
                arquivo_principal.write(f"\n{data_atual()} - INFO - Opção invalida, insira novamente! ")
                continue
            continue

    def menu_restaurar_banco(self, arquivo_principal):
        arquivo_restauracao = open(f"Log\\{self.nomes['arquivo_restaurar_banco']}.txt", "a")
        while True:
            infos_config = self.escolher_config(arquivo_principal)
            while True:
                if infos_config['status']:
                    try:
                        if infos_config['server_principal'] != "":
                            restaurar_banco(arquivo_principal, arquivo_restauracao, infos_config)
                            break
                        else:
                            print(f"- A tag de server_principal parece estar vazia, preencha e tente novamente")
                            arquivo_restauracao.write(f"{data_atual()} - INFO - A tag de server_principal parece estar vazia, preencha e tente novamente ")
                            infos_config['status'] = False
                    except (Exception or pyodbc.DatabaseError) as err:
                        print(f"- Falha ao tentar ler o arquivo, corrija e tente novamente: {err}")
                        arquivo_restauracao.write(f"{data_atual()} - ERRO - Falha ao tentar ler o arquivo, corrija e tente novamente: {err} ")
                        infos_config['status'] = False
                else:
                    break
            if infos_config['status']:
                break
            else:
                continue

    def menu_download_backup(self, arquivo_principal):
        arquivo_download = open(f"Log\\{self.nomes['arquivo_download_backup']}.txt", "a")
        while True:
            infos_config = self.escolher_config(arquivo_principal)
            while True:
                if infos_config['status']:
                    try:
                        if infos_config['server_principal'] != "":
                            download_backup(arquivo_principal, arquivo_download, infos_config)
                            break
                        else:
                            print(f"- A tag de server_principal parece estar vazia, preencha e tente novamente")
                            arquivo_download.write(f"{data_atual()} - INFO - A tag de server_principal parece estar vazia, preencha e tente novamente ")
                            infos_config['status'] = False
                    except (Exception or pyodbc.DatabaseError) as err:
                        print(f"- Falha ao tentar ler o arquivo, corrija e tente novamente: {err}")
                        arquivo_download.write(f"{data_atual()} - ERRO - Falha ao tentar ler o arquivo, corrija e tente novamente: {err} ")
                        infos_config['status'] = False
                else:
                    break
            if infos_config['status']:
                break
            else:
                continue

    def menu_bancos_muro(self, arquivo_principal):
        infos_config = self.escolher_config(arquivo_principal)
        self.ferramentas_muro(arquivo_principal, infos_config)

    def menu(self, arquivo_principal):
        certo = True

        while certo:
            while certo:
                print("\n- Tela - Menu Principal")
                arquivo_principal.write(f"\n{data_atual()} - INFO - Tela - Menu Principal ")
                print("- Escolha qual função deseja utilizar: ")
                escolha_menu = input("""|1 - Banco de Muro
|2 - Download Backup
|3 - Restaurar Backup
|4 - Sair
|Escolha:""")

                if escolha_menu == "1":
                    print("- Opção 1 selecionada - Banco de Muro")
                    arquivo_principal.write(f"\n{data_atual()} - INFO - Opção 1 selecionada - Banco de Muro ")
                    self.menu_bancos_muro(arquivo_principal)
                    certo = True
                    continue
                elif escolha_menu == "2":
                    print("- Opção 2 selecionada - Download Backup")
                    arquivo_principal.write(f"\n{data_atual()} - INFO - Opção 2 selecionada - Download Backup ")
                    self.menu_download_backup(arquivo_principal)
                    certo = True
                    continue
                elif escolha_menu == "3":
                    print("- Opção 3 selecionada - Restaurar Backup")
                    arquivo_principal.write(f"\n{data_atual()} - INFO - Opção 3 selecionada - Restaurar Backup ")
                    self.menu_restaurar_banco(arquivo_principal)
                    certo = True
                    continue
                elif escolha_menu == "4":
                    print("- Opção 4 selecionada - Sair")
                    arquivo_principal.write(f"\n{data_atual()} - INFO - Opção 4 selecionada - Sair \n")
                    arquivo_principal.close()
                    sair()
                else:
                    print("- Opção invalida, insira novamente \n")
                    certo = True
                    continue

    def __init__(self):
        # Criar diretorio log
        try:
            if os.path.exists(self.nomes['diretorio_log']):
                print(f"- Pasta {self.nomes['diretorio_log']} já existente")
            else:
                os.makedirs(self.nomes['diretorio_log'])
                print(f"- Pasta {self.nomes['diretorio_log']} criada com sucesso")
        except Exception as error:
            print(f"- Erro ao criar/validar a pasta {self.nomes['diretorio_log']}: {error}")

        # Criar diretorio config
        try:
            if os.path.exists(self.nomes['diretorio_config']):
                print(f"- Pasta {self.nomes['diretorio_config']} já existente")
            else:
                os.makedirs(self.nomes['diretorio_config'])
                print(f"- Pasta {self.nomes['diretorio_config']} criada com sucesso")
        except Exception as error:
            print(f"- Erro ao criar/validar a pasta {self.nomes['diretorio_config']}: {error}")

        arquivo_principal = open(f"{self.nomes['diretorio_log']}\\{self.nomes['arquivo_base_muro']}.txt", "a")

        print(f"- Programa iniciado {data_atual()}")
        arquivo_principal.write(f"{data_atual()} - INFO - Programa iniciado \n")

        print(f"- Versão: {self.version}")
        arquivo_principal.write(f"{data_atual()} - INFO - Versão:  {self.version} ")
        self.menu(arquivo_principal)


base_muro = BuscaMuro()

