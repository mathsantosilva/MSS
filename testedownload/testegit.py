from git import Repo
from github import Github
import re
import os
import requests
import shutil
import subprocess

def pesquisar_maior_tag(username, repository, tag_atual):
    github = Github()
    repo = github.get_repo(f"{username}/{repository}")
    tags = repo.get_tags()

    maior_tag = None
    for tag in tags:
        if comparar_tags(tag.name, tag_atual) > 0:
            if maior_tag is None or comparar_tags(tag.name, maior_tag) > 0:
                maior_tag = tag.name

    return maior_tag

def comparar_tags(tag1, tag2):
    # Função para comparar duas tags no formato 'x.y.z' e retornar 1 se a primeira for maior, -1 se for menor e 0 se forem iguais
    version_regex = r"(\d+)\.(\d+)\.(\d+)"
    match1 = re.match(version_regex, tag1)
    match2 = re.match(version_regex, tag2)

    if match1 and match2:
        version1 = tuple(map(int, match1.groups()))
        version2 = tuple(map(int, match2.groups()))

        if version1 > version2:
            return 1
        elif version1 < version2:
            return -1

    return 0

def realizar_download(maior_tag):
    caminho = f"https://github.com/mathsantosilva/MSS/releases/download/{maior_tag}/BuscaMuro.exe"
    response = requests.get(caminho)
    try:
        if os.path.exists("C:/MSS_temp"):
            print("Feito")
        else:
            os.makedirs("C:/MSS_temp")
    except Exception as error:
        print(f"INFO - Erro ao criar/validar a pasta C:/MSS_temp: {error} ")
    with open("C:/MSS_temp/BuscaMuro.exe", "wb") as arquivo:
        arquivo.write(response.content)

def executar_comando_batch(dir_atual):
    comando = f"""@echo off
xcopy "C:\MSS_temp\BuscaMuro.exe" "{dir_atual}\BuscaMuro.exe" /w/E/Y/H
echo.
echo Atualização realizada com sucesso 
echo.
start {dir_atual}\BuscaMuro.exe
pause
exit
"""
    arquivo = open("C:/MSS_temp/script.bat", "a")
    arquivo.write(comando)
    resultado = subprocess.Popen(['start', 'cmd', '/k', 'C:/MSS_temp/script.bat'], shell=True, text=True)
    print(resultado)

def atualizador():
    # Exemplo de uso
    username = "mathsantosilva"
    repository = "MSS"
    tag_atual = "1.2.0"

    maior_tag = pesquisar_maior_tag(username, repository, tag_atual)

    if maior_tag != None:
        realizar_download(maior_tag)
        dir_atual = os.getcwd()
        executar_comando_batch(dir_atual)

main()