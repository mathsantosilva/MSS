class Generators:
    def __init__(self):
        print('')

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
