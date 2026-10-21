from datetime import datetime, date
import sys

class UtilService:
    def __init__(self):
        pass

    def data_atual(self):
        data_hora = date.today()
        return data_hora

    def finalizar(self):
        sys.exit(200)