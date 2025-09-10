from github import Github
from core.filesystem import FileSystem
from core.logging_utils import Logger
from core.cmd import UpdaterCmd
from domain.redis_ops.redis_service import RedisService
from domain.versions.versioning_service import VersioningService
from use_cases.versions_uc import VersionsUC

class Container:
    def __init__(self):
        # valores default de nomes (iguais aos do monolito)
        self.nomes = {
            'pasta_config': 'Config/',
            'diretorio_log': 'Log',
            'diretorio_txt': 'Arquivos',
            'diretorio_config': 'Config',
            'arquivo_base_muro': 'base_muro',
            'arquivo_busca_bancos': 'atualizar_registros_update',
            'arquivo_replicar_version': 'replicar_version',
            'arquivo_download_backup': 'download_backup',
            'arquivo_restaurar_banco': 'restaurar_banco',
            'arquivo_connection_strings': 'connection_strings',
            'arquivo_validar': 'consultar_versions',
            'arquivo_buscar_empresas': 'buscar_empresas',
            'arquivo_redis': 'limpeza_redis',
            'arquivo_config_default': 'prog',
            'arquivo_doc_pis' : 'PIS_gerados',
            'arquivo_doc_cpf' : 'CPFs_gerados',
            'arquivo_doc_cnpj' : 'CNPJs_gerados',
            'arquivo_doc_cei' : 'CEIs_gerados',
            'arquivo_doc_nif' : 'NIFs_gerados'
        }
        self.fs = FileSystem()
        self.fs.validar_diretorio()
        self.logger = Logger(self.nomes, self.fs)
        self.gh = Github()
        self.versioning = VersioningService(self.gh)
        self.updater_cmd = UpdaterCmd()

        # Use cases
        # popup será atribuído pela UI quando o App criar as telas
        self.versions_uc = VersionsUC(self.versioning, self.updater_cmd, self.logger, popup=lambda msg: None)
