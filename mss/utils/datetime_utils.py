from datetime import datetime

def data_hora_atual(tipo: str | None = None):
    formatos = {
        "hora": "%H:%M:%S",
        "data": "%d-%m-%Y",
        "completo": "%Y-%m-%d %H:%M:%S",
    }

    formato = formatos.get(tipo, formatos["completo"])
    return datetime.now().strftime(formato)
