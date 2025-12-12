# tests/test_utils_datetime.py
from mss.utils.datetime_utils import data_hora_atual
from datetime import datetime
import re

def test_data_hora_atual_completo():
    valor = data_hora_atual()
    # yyyy-mm-dd HH:MM:SS
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", valor)
    assert datetime.strptime(valor, "%Y-%m-%d %H:%M:%S")

def test_data_hora_atual_tipo_hora():
    valor = data_hora_atual('hora')
    # yyyy-mm-dd HH:MM:SS
    assert re.fullmatch(r"\d{2}:\d{2}:\d{2}", valor)
    assert datetime.strptime(valor, "%H:%M:%S")

def test_data_hora_atual_tipo_data():
    valor = data_hora_atual('data')
    # yyyy-mm-dd HH:MM:SS
    assert re.fullmatch(r"\d{2}-\d{2}-\d{4}", valor)
    assert datetime.strptime(valor, "%d-%m-%Y")