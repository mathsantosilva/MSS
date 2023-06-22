import tkinter as tk

# Função chamada quando o botão é clicado
def clicar():
    print("Botão clicado!")

# Cria a janela principal
janela = tk.Tk()

# Campo de texto
campo_texto = tk.Entry(janela)
campo_texto.pack()

# Botão
botao = tk.Button(janela, text="Clique aqui!", command=clicar)
botao.pack()

# Caixa de seleção
caixa_selecao = tk.Checkbutton(janela, text="Opção 1")
caixa_selecao.pack()

# Lista suspensa
opcoes = ["Opção 1", "Opção 2", "Opção 3"]
valor_selecionado = tk.StringVar(janela)
valor_selecionado.set(opcoes[0])
lista_suspensa = tk.OptionMenu(janela, valor_selecionado, *opcoes)
lista_suspensa.pack()

# Inicia o loop principal da interface
janela.mainloop()
