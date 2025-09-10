# use_cases/documentos_uc.py
import threading
from domain.documents.validators import *
from domain.documents.generators import *
from domain.redis_ops.redis_service import *
from domain.bancos.update_manager import *



class DocumentosUC:
    def __init__(self):
        print('')
        self.validators = Validators()
        self.generators = Generators()
        self.redis_service = RedisService()
        self.update_manager = UpdateManager()

    def iniciar_processo_validar_nif(self, documento_inserido):
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.validators.validador_nif, args=[documento_inserido])
        self.thread.start()

    def iniciar_processo_validar_cnpj(self, documento_inserido):
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.validators.validador_cnpj, args=[documento_inserido])
        self.thread.start()

    def iniciar_processo_validar_cpf(self, documento_inserido):
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.validators.validador_cpf, args=[documento_inserido])
        self.thread.start()

    def iniciar_processo_validar_cei(self, documento_inserido):
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.validators.validador_cei, args=[documento_inserido])
        self.thread.start()

    def iniciar_processo_validar_pis(self, documento_inserido):
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.validators.validador_pis, args=[documento_inserido])
        self.thread.start()

    def iniciar_processo_gerar_nif(self, linhas, checkbox_arquivo):
        self.escrever_no_input(f"- Processo iniciado - Gerador de NIF")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.generators.gerador_nif, args=[linhas, checkbox_arquivo])
        self.thread.start()

    def iniciar_processo_gerar_cnpj(self, linhas, checkbox_mascara, checkbox_arquivo):
        self.escrever_no_input(f"- Processo iniciado - Gerador de CNPJ")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.generators.gerador_cnpj, args=[linhas, checkbox_mascara, checkbox_arquivo])
        self.thread.start()

    def iniciar_processo_gerar_cpf(self, linhas, checkbox_mascara, checkbox_arquivo):
        self.escrever_no_input(f"- Processo iniciado - Gerador de CPF")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.generators.gerador_cpf, args=[linhas, checkbox_mascara, checkbox_arquivo])
        self.thread.start()

    def iniciar_processo_gerar_cei(self, linhas, checkbox_mascara, checkbox_arquivo):
        self.escrever_no_input(f"- Processo iniciado - Gerador de CEI")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.generators.gerador_cei, args=[linhas, checkbox_mascara, checkbox_arquivo])
        self.thread.start()

    def iniciar_processo_gerar_pis(self, linhas, checkbox_mascara, checkbox_arquivo):
        self.escrever_no_input(f"- Processo iniciado - Gerador de PIS")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.generators.gerador_pis, args=[linhas, checkbox_mascara, checkbox_arquivo])
        self.thread.start()

    def iniciar_processo_limpar_redis_especifico(self):
        self.escrever_no_input(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.redis_service.limpar_redis_especifico)
        self.thread.start()

    def iniciar_processo_limpar_redis_todos(self):
        self.escrever_no_input(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.redis_service.limpar_todos_redis)
        self.thread.start()

    def iniciar_processo_buscar_empresas(self):
        self.escrever_no_input(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.update_manager.buscar_empresas)
        self.thread.start()

    def iniciar_processo_consulta(self):
        self.escrever_no_input(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.update_manager.consultar_versions)
        self.thread.start()

    def iniciar_processo_replicar(self):
        self.escrever_no_input(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.update_manager.replicar_version)
        self.thread.start()

    def iniciar_processo_restaurar(self):
        self.escrever_no_input(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.update_manager.restaurar_banco)
        self.thread.start()

    def iniciar_processo_manipula_banco(self):
        self.escrever_no_input(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.update_manager.manipular_banco_update)
        self.thread.start()

    def iniciar_processo_download(self):
        self.escrever_no_input(f"- Processo iniciado")
        # Criar uma nova thread para executar o processo demorado
        self.thread = threading.Thread(target=self.download_backup)
        self.thread.start()
