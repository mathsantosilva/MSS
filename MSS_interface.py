from tkinter import *

import BuscaMuro
from BuscaMuro import *


def menu_cascata(menu):
    menu_ferramentas = Menu(menu)
    menu.add_cascade(label="Ferramentas", menu=menu_ferramentas)
    menu_ferramentas.add_command(label="Teste1", command=lambda: print("Top"))
    menu_ferramentas.add_command(label="Teste2", command=lambda: print("Left"))
    menu_ferramentas.add_command(label="Teste3", command=lambda: print("Right"))
    menu_ferramentas.add_command(label="Teste4", command=lambda: print("Bottom"))

    menu_download_backup = Menu(menu)
    menu.add_cascade(label="Download Backup", menu=menu_download_backup)
    menu_download_backup.add_command(label="Teste1", command=lambda: print("Top"))
    menu_download_backup.add_command(label="Teste2", command=lambda: print("Left"))
    menu_download_backup.add_command(label="Teste3", command=lambda: print("Right"))
    menu_download_backup.add_command(label="Teste4", command=lambda: print("Bottom"))

    menu_restaurar_banco = Menu(menu)
    menu.add_cascade(label="Restaurar Banco", menu=menu_download_backup)
    menu_restaurar_banco.add_command(label="Teste1", command=lambda: print("Top"))
    menu_restaurar_banco.add_command(label="Teste2", command=lambda: print("Left"))
    menu_restaurar_banco.add_command(label="Teste3", command=lambda: print("Right"))
    menu_restaurar_banco.add_command(label="Teste4", command=lambda: print("Bottom"))

def mensagem(app,button_config_novo,texto):
    button_config_novo.config(state='disabled')

def button_selecao(app):
    button_config_existente = Button(
        app,
        text="Config existente",
        width= "15",
        height= "1",
        command=lambda: mensagem(app,button_config_novo,"Escolha o existente")
    )
    button_config_novo = Button(
        app,
        text="Config Novo",
        width="15",
        height="1",
        command=lambda: mensagem(app,button_config_existente,"Escolha o Novo")
    )
    button_sair = Button(
        app,
        text="Sair",
        width="15",
        height="1",
        command=lambda: sys.exit(200)
    )
    button_config_existente.pack()
    button_config_novo.pack()
    button_sair.pack()

class Aplicativo:
    version = "2.0.0"

    app = Tk()
    app.title("MSS - " + version)
    app.geometry("300x250")
    menu = Menu(app)
    app.config(menu=menu)

    label_principal = Label(app, text="Escolha o Config", padx='10', pady='10')
    label_principal.pack()

    menu_cascata(menu)
    button_selecao(app)

prog = Aplicativo()
prog.app.mainloop()
