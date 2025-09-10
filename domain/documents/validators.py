class Validators:
    def __init__(self):
        print('')

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