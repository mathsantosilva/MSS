import tkinter as tk

class App(tk.Tk):
    def __init__(self, container):
        super().__init__()
        self.container = container
        self.title("MSS")
        # trocar_tela_* ficam aqui chamando screens/*
