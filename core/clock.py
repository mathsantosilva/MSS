from datetime import datetime

class Clock:
    @staticmethod
    def data_hora_atual() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def data_atual() -> str:
        return datetime.now().strftime("%d-%m-%Y")
