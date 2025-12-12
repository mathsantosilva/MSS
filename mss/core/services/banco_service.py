class BancoService:
    def __init__(self, conexoes, banco_repo, empresa_repo, logger):
        self.conexoes = conexoes     # dict com conexões (já criado em criar_dict_conexoes)
        self.banco_repo = banco_repo
        self.empresa_repo = empresa_repo
        self.logger = logger

    def consultar_versions(self, servidor_nome: str, bases_muro: list[str]):
        # move a lógica de consultar_versions pra cá
        # Retorna lista de resultados, mensagens de log etc.
        ...

    def buscar_empresas(self, servidor_nome: str, base_muro: str):
        # move lógica de buscar_empresas (threads, catalogo etc.) pra cá
        ...
