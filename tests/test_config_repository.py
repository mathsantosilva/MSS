import json
import pytest
import mss.infrastructure.config_repository as config_repo
from mss.core.constants import MSS_SUCESSO_CRIACAO_CONFIG, MENSAGEM_DEFAULT_JSON, VERSION_JSON, MSS_ERRO_ARQUIVO_EXISTENTE, MSS_ERRO_CAMPO_VAZIO, PLACEHOLDER_TEXT_ARQUIVO, MSS_SUCESSO_CRIACAO_JSON, COLOR_DEAFULT, COLOR_DEAFULT_NAVS, COLOR_DEAFULT_FONTE
from configparser import ConfigParser

@pytest.fixture
def data_fake(monkeypatch):
    fake = "2025-01-01 12:00:00"
    monkeypatch.setattr(
        config_repo,
        "data_hora_atual",
        lambda *args, **kwargs: fake
    )
    return fake

@pytest.fixture
def nomes(tmp_path):
    return {
        "arquivo_base_muro": "base_muro.log",
        "diretorio_log": tmp_path / "log",
        "diretorio_config": tmp_path / "config",
        "diretorio_txt": tmp_path / "Arquivos",
    }

@pytest.fixture
def encoding():
    return "utf-8"

def test_salvar_json_sem_arquivo(nomes, data_fake, encoding):
    nome_do_arquivo = "prog.json"
    path = nomes["diretorio_config"] / nome_do_arquivo

    configrepository = config_repo.ConfigRepository(nomes.get("diretorio_config", ""))
    resultado = configrepository.salvar_config_json(nome_do_arquivo, nomes)

    assert resultado.sucesso
    assert resultado.mensagem == MSS_SUCESSO_CRIACAO_JSON
    assert path.exists()

    dados = json.loads(path.read_text(encoding=encoding))

    # agora valida o conteúdo de forma lógica
    assert dados["controle_versao_json"]["versao"] == VERSION_JSON
    assert dados["controle_versao_json"]["data"] == data_fake
    assert dados["controle_versao_json"]["comentario"] == MENSAGEM_DEFAULT_JSON

    assert dados["bancos_update"] == {
        "database_update_br": "",
        "database_update_mx": "",
        "database_update_pt": "",
        "database_update_md": "",
    }
    assert "redis_qa" in dados
    assert "grupo_1" in dados["redis_qa"]
    assert "grupo_2" in dados["redis_qa"]
    assert len(dados["redis_qa"]["grupo_1"]) == 2

    assert dados["bases_muro"] == [""]
    assert len(dados["conexoes"]) == 1
    assert dados["conexoes"][0] == {
        "nome": "",
        "server": "",
        "username": "",
        "password": "",
    }

def test_salvar_json_com_arquivo(nomes, data_fake, encoding):
    nome_do_arquivo = "prog.json"
    path = nomes["diretorio_config"] / nome_do_arquivo
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = 'teste'
    with path.open("w", encoding=encoding) as f:
        f.write(payload)

    configrepository = config_repo.ConfigRepository(nomes.get("diretorio_config", ""))
    resultado = configrepository.salvar_config_json(nome_do_arquivo, nomes)

    assert resultado.aviso
    assert MSS_ERRO_ARQUIVO_EXISTENTE in resultado.mensagem
    assert path.exists()
    assert path.read_text(encoding="utf-8") == payload

@pytest.mark.parametrize("nome_do_arquivo", ["", PLACEHOLDER_TEXT_ARQUIVO])
def test_salvar_json_nome_invalido_retorna_aviso(nomes, data_fake, encoding, nome_do_arquivo):
    configrepository = config_repo.ConfigRepository(nomes.get("diretorio_config", ""))
    resultado = configrepository.salvar_config_json(nome_do_arquivo, nomes)

    assert resultado.aviso
    assert MSS_ERRO_CAMPO_VAZIO in resultado.mensagem
    assert not nomes["diretorio_config"].exists() or not any(nomes["diretorio_config"].iterdir())

def test_salvar_json_sem_extensao(nomes, data_fake, encoding):
    nome_do_arquivo = "prog"
    path = nomes["diretorio_config"] / f"{nome_do_arquivo}.json"

    configrepository = config_repo.ConfigRepository(nomes.get("diretorio_config", ""))
    resultado = configrepository.salvar_config_json(nome_do_arquivo, nomes)

    assert resultado.sucesso
    assert resultado.mensagem == MSS_SUCESSO_CRIACAO_JSON
    assert path.exists()

    dados = json.loads(path.read_text(encoding=encoding))

    # agora valida o conteúdo de forma lógica
    assert dados["controle_versao_json"]["versao"] == VERSION_JSON
    assert dados["controle_versao_json"]["data"] == data_fake
    assert dados["controle_versao_json"]["comentario"] == MENSAGEM_DEFAULT_JSON

    assert dados["bancos_update"] == {
        "database_update_br": "",
        "database_update_mx": "",
        "database_update_pt": "",
        "database_update_md": "",
    }

    assert "redis_qa" in dados
    assert "grupo_1" in dados["redis_qa"]
    assert "grupo_2" in dados["redis_qa"]
    assert len(dados["redis_qa"]["grupo_1"]) == 2

    assert dados["bases_muro"] == [""]
    assert len(dados["conexoes"]) == 1
    assert dados["conexoes"][0] == {
        "nome": "",
        "server": "",
        "username": "",
        "password": "",
    }

def test_salvar_json_case_sensitive(nomes, data_fake, encoding):
    nome_do_arquivo = "config.JSON"
    path = nomes["diretorio_config"] / nome_do_arquivo

    configrepository = config_repo.ConfigRepository(nomes.get("diretorio_config", ""))
    resultado = configrepository.salvar_config_json(nome_do_arquivo, nomes)

    assert resultado.sucesso
    assert resultado.mensagem == MSS_SUCESSO_CRIACAO_JSON
    assert path.exists()

    dados = json.loads(path.read_text(encoding=encoding))

    # agora valida o conteúdo de forma lógica
    assert dados["controle_versao_json"]["versao"] == VERSION_JSON
    assert dados["controle_versao_json"]["data"] == data_fake
    assert dados["controle_versao_json"]["comentario"] == MENSAGEM_DEFAULT_JSON

    assert dados["bancos_update"] == {
        "database_update_br": "",
        "database_update_mx": "",
        "database_update_pt": "",
        "database_update_md": "",
    }

    assert "redis_qa" in dados
    assert "grupo_1" in dados["redis_qa"]
    assert "grupo_2" in dados["redis_qa"]
    assert len(dados["redis_qa"]["grupo_1"]) == 2

    assert dados["bases_muro"] == [""]
    assert len(dados["conexoes"]) == 1
    assert dados["conexoes"][0] == {
        "nome": "",
        "server": "",
        "username": "",
        "password": "",
    }

def test_salvar_config_sem_arquivo(nomes, data_fake, encoding):
    nome_do_arquivo = "prog.conf"
    path = nomes["diretorio_config"] / nome_do_arquivo

    configrepository = config_repo.ConfigRepository(nomes.get("diretorio_config", ""))
    resultado = configrepository.salvar_config_prog(nome_do_arquivo, nomes)

    assert resultado.sucesso
    assert resultado.mensagem == MSS_SUCESSO_CRIACAO_CONFIG
    assert path.exists()

    with path.open("r", encoding=encoding) as f:
        texto_lido = f.read()

    config = ConfigParser()
    config.read(path)
    assert config.get("ConfiguracoesGerais", "config_default") == ""
    assert config.get("ConfiguracoesAparencia", "background_color_fundo") == COLOR_DEAFULT
    assert config.get("ConfiguracoesAparencia", "background_color_titulos") == COLOR_DEAFULT
    assert config.get("ConfiguracoesAparencia", "background_color_botoes") == COLOR_DEAFULT
    assert config.get("ConfiguracoesAparencia", "background_color_botoes_navs") == COLOR_DEAFULT_NAVS
    assert config.get("ConfiguracoesAparencia", "background_color_fonte") == COLOR_DEAFULT_FONTE

def test_salvar_config_com_arquivo(nomes, data_fake, encoding):
    nome_do_arquivo = "prog.conf"
    path = nomes["diretorio_config"] / nome_do_arquivo
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = f"""[ConfiguracoesGerais]
config_default = 
data_ultima_atualizacao =

[ConfiguracoesAparencia]
background_color_fundo = {COLOR_DEAFULT}
background_color_titulos = {COLOR_DEAFULT}
background_color_botoes = {COLOR_DEAFULT}
background_color_botoes_navs = {COLOR_DEAFULT_NAVS}
background_color_fonte = {COLOR_DEAFULT_FONTE}"""

    with path.open("w", encoding=encoding) as f:
        f.write(payload)

    configrepository = config_repo.ConfigRepository(nomes.get("diretorio_config", ""))
    resultado = configrepository.salvar_config_prog(nome_do_arquivo, nomes)

    assert resultado.aviso
    assert MSS_ERRO_ARQUIVO_EXISTENTE in resultado.mensagem

@pytest.mark.parametrize("nome_do_arquivo", ["", PLACEHOLDER_TEXT_ARQUIVO])
def test_salvar_config_nome_invalido_retorna_aviso(nomes, data_fake, encoding, nome_do_arquivo):
    configrepository = config_repo.ConfigRepository(nomes.get("diretorio_config", ""))
    resultado = configrepository.salvar_config_prog(nome_do_arquivo, nomes)

    assert resultado.aviso
    assert MSS_ERRO_CAMPO_VAZIO in resultado.mensagem
    assert not nomes["diretorio_config"].exists() or not any(nomes["diretorio_config"].iterdir())

def test_salvar_config_sem_extensao(nomes, data_fake, encoding):
    nome_do_arquivo = "prog"
    path = nomes["diretorio_config"] / f"{nome_do_arquivo}.conf"

    configrepository = config_repo.ConfigRepository(nomes.get("diretorio_config", ""))
    resultado = configrepository.salvar_config_prog(nome_do_arquivo, nomes)

    assert resultado.sucesso
    assert resultado.mensagem == MSS_SUCESSO_CRIACAO_CONFIG
    assert path.exists()

    config = ConfigParser()
    config.read(path)
    assert config.get("ConfiguracoesGerais", "config_default") == ""
    assert config.get("ConfiguracoesAparencia", "background_color_fundo") == COLOR_DEAFULT
    assert config.get("ConfiguracoesAparencia", "background_color_titulos") == COLOR_DEAFULT
    assert config.get("ConfiguracoesAparencia", "background_color_botoes") == COLOR_DEAFULT
    assert config.get("ConfiguracoesAparencia", "background_color_botoes_navs") == COLOR_DEAFULT_NAVS
    assert config.get("ConfiguracoesAparencia", "background_color_fonte") == COLOR_DEAFULT_FONTE

def test_salvar_config_case_sensitive(nomes, data_fake, encoding):
    nome_do_arquivo = "prog.CONF"
    path = nomes["diretorio_config"] / nome_do_arquivo

    configrepository = config_repo.ConfigRepository(nomes.get("diretorio_config", ""))
    resultado = configrepository.salvar_config_prog(nome_do_arquivo, nomes)

    assert resultado.sucesso
    assert resultado.mensagem == MSS_SUCESSO_CRIACAO_CONFIG
    assert path.exists()

    config = ConfigParser()
    config.read(path)
    assert config.get("ConfiguracoesGerais", "config_default") == ""
    assert config.get("ConfiguracoesAparencia", "background_color_fundo") == COLOR_DEAFULT
    assert config.get("ConfiguracoesAparencia", "background_color_titulos") == COLOR_DEAFULT
    assert config.get("ConfiguracoesAparencia", "background_color_botoes") == COLOR_DEAFULT
    assert config.get("ConfiguracoesAparencia", "background_color_botoes_navs") == COLOR_DEAFULT_NAVS
    assert config.get("ConfiguracoesAparencia", "background_color_fonte") == COLOR_DEAFULT_FONTE