import pyodbc

class EmpresasService:
    def __init__(self, logger, clock):
        self.log = logger
        self.clock = clock

    def buscar_connections_strings(self, servidor: dict, lista_instancia, base_muro: str, escrever_no_input):
        # porta seu buscar_connections_strings para cá
        # (mantendo a assinatura e chamadas que você já usa)
        pass

    def buscar_empresas(self, conexoes: dict, server_key: str, base_muro: str,
                        escrever_no_input, popup, ui_ctrls):
        """
        Move aqui a lógica atual de buscar_empresas, recebendo dependências por parâmetro:
        - conexoes: dict (self.infos_config["conexoes"])
        - escrever_no_input: função da UI para log em tela
        - popup: função para mensagens
        - ui_ctrls: objeto/struct com botões/combos a habilitar/desabilitar
        """
        pass
