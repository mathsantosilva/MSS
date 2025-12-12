# tests/test_infrastructure_logging.py
import os
from mss.infrastructure.logging import validar_linha, validar_diretorio, escrever_arquivo_texto_log
from mss.core.constants import MSG_DIRETORIOS_OK, MSG_ERRO_CRIAR_PASTA, MSS_ERRO_CRIAR_ARQUIVO, MSS_SUCESSO_CRIACAO_ARQUIVO

def test_validar_linha_arquivo_vazio(tmp_path):
    diretorio = tmp_path
    nome = "log"
    path = diretorio / f"{nome}.txt"
    path.write_text("", encoding="utf-8")

    resultado = validar_linha(path)

    # No código original, um arquivo "vazio" retorna ""
    assert resultado == ""

def test_validar_linha_arquivo_com_conteudo(tmp_path):
    diretorio = tmp_path
    nome = "log"
    path = diretorio / f"{nome}.txt"
    path.write_text("linha 1\n", encoding="utf-8")

    resultado = validar_linha(path)

    # Quando já tem conteúdo, deve retornar "\n"
    assert resultado == "\n"

def test_validar_diretorio_sem_pastas(tmp_path):
    nomes = {
        "diretorio_log": tmp_path / "log",
        "diretorio_config": tmp_path / "config",
        "diretorio_txt": tmp_path / "Arquivos",
    }

    resultado = validar_diretorio(nomes)

    assert resultado.sucesso
    assert resultado.mensagem == MSG_DIRETORIOS_OK
    assert (tmp_path / "log").exists()
    assert (tmp_path / "config").exists()
    assert (tmp_path / "Arquivos").exists()

def test_validar_diretorio_todas_as_pastas(tmp_path):
    nomes = {
        "diretorio_log": tmp_path / "log",
        "diretorio_config": tmp_path / "config",
        "diretorio_txt": tmp_path / "Arquivos",
    }
    os.makedirs(nomes['diretorio_log'])
    os.makedirs(nomes['diretorio_config'])
    os.makedirs(nomes['diretorio_txt'])
    resultado = validar_diretorio(nomes)

    assert resultado.sucesso
    assert resultado.mensagem == MSG_DIRETORIOS_OK
    assert (tmp_path / "log").exists()
    assert (tmp_path / "config").exists()
    assert (tmp_path / "Arquivos").exists()

def test_validar_diretorio_erro_mkdir(tmp_path, monkeypatch):
    # Simula um erro em os.makedirs
    def fake_makedirs(path, exist_ok=False):
        raise PermissionError("simulated error")

    monkeypatch.setattr("mss.infrastructure.logging.os.makedirs", fake_makedirs)

    nomes = {
        "diretorio_log": tmp_path / "log",
        "diretorio_config": tmp_path / "config",
        "diretorio_txt": tmp_path / "Arquivos",
    }

    resultado = validar_diretorio(nomes)

    assert resultado.erro
    assert "simulated error" in resultado.mensagem
    assert MSG_ERRO_CRIAR_PASTA in resultado.mensagem

def test_escrever_arquivo_texto_criacao(tmp_path):
    encoding = "utf-8"
    diretorio = tmp_path
    nome = "config"
    path = diretorio / f"{nome}.json"
    texto = "arquivo criado com sucesso"

    resultado = escrever_arquivo_texto_log(path, texto)
    with path.open("r", encoding=encoding) as f:
        texto_lido = f.read()
    assert resultado.sucesso
    assert resultado.mensagem == MSS_SUCESSO_CRIACAO_ARQUIVO
    assert path.exists()
    assert texto == texto_lido

def test_escrever_arquivo_texto_edicao_preenchido(tmp_path):
    encoding = "utf-8"
    diretorio = tmp_path
    nome = "config"
    path = diretorio / f"{nome}.json"
    path.write_text("linha 1", encoding="utf-8")
    texto = "arquivo criado com sucesso"

    resultado = escrever_arquivo_texto_log(path, texto)
    with path.open("r", encoding=encoding) as f:
        texto_lido = f.read()
    assert resultado.sucesso
    assert resultado.mensagem == MSS_SUCESSO_CRIACAO_ARQUIVO
    assert path.exists()
    assert "linha 1\narquivo criado com sucesso" == texto_lido

def test_escrever_arquivo_texto_edicao_vazio(tmp_path):
    encoding = "utf-8"
    diretorio = tmp_path
    nome = "config"
    path = diretorio / f"{nome}.json"
    path.write_text("", encoding="utf-8")
    texto = "arquivo criado com sucesso"


    resultado = escrever_arquivo_texto_log(path, texto)
    with path.open("r", encoding=encoding) as f:
        texto_lido = f.read()
    assert resultado.sucesso
    assert resultado.mensagem == MSS_SUCESSO_CRIACAO_ARQUIVO
    assert path.exists()
    assert texto == texto_lido
