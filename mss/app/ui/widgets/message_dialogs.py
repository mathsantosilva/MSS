from PySide6.QtWidgets import QMessageBox


def mostrar_info(parent, titulo, mensagem):
    QMessageBox.information(parent, titulo, mensagem)


def mostrar_erro(parent, titulo, mensagem):
    QMessageBox.critical(parent, titulo, mensagem)

def mostrar_alerta(parent, titulo, mensagem):
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle(titulo)
    msg.setText(mensagem)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)

    msg.show()

    return msg

def mostrar_aviso(parent, titulo, mensagem):
    QMessageBox.warning(parent, titulo, mensagem)


def confirmar(parent, titulo, mensagem):
    resposta = QMessageBox.question(
        parent,
        titulo,
        mensagem,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )

    return resposta == QMessageBox.StandardButton.Yes