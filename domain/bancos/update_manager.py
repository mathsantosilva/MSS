class UpdateManager:

    def __init__(self):
        print('')

    def atualizar_bancos_update(self):
        print("Não implementado")

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