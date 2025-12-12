import pytest
import random
import string
from mss.utils.string_utils import limpar_string

def gerar_digitos(qtd):
    return ''.join(str(random.randint(0, 9)) for _ in range(qtd))

def inserir_pontuacoes_aleatorias(s):
    caracteres = ['.', '-', '/', '(', ')']
    resultado = []

    for char in s:
        resultado.append(char)
        if random.random() < 0.3:
            resultado.append(random.choice(caracteres))

    return ''.join(resultado)

@pytest.mark.parametrize("qtd_digitos, qtd_documentos", [
    (11, 1),   # CPF único
    (14, 1),   # CNPJ único
    (9, 1),    # CEI único
    (11, 5),   # CPF lista
    (14, 5),   # CNPJ lista
    (9, 5),    # CEI lista
])
def test_limpar_documentos(qtd_digitos, qtd_documentos):

    puros = [gerar_digitos(qtd_digitos) for _ in range(qtd_documentos)]
    sujos = [inserir_pontuacoes_aleatorias(doc) for doc in puros]

    resultados = limpar_string(sujos)

    assert isinstance(resultados, list)
    assert resultados == puros

def test_limpar_lista_vazia():
    assert limpar_string([]) == []

def test_limpar_documento_so_pontuacao():
    sujo = ["..--///()()"]
    resultado = limpar_string(sujo)
    assert resultado == [""]

