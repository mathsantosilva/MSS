from git import Repo
import os

def atualizar_programa():

    # Caminho para o diretório onde o programa está localizado
    print("Passou 1")
    diretorio_programa = "c:/MSS"
    print("Passou 2")

    # Verifica se o repositório já está clonado
    if os.path.exists(diretorio_programa):
        print("Passou 3")
        repo = Repo(diretorio_programa)
        repo.remotes.origin.pull()
    else:
        print("Passou 4")
        Repo.clone_from("https://github.com/mathsantosilva/MSS.git", diretorio_programa)

atualizar_programa()