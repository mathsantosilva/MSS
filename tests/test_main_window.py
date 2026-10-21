import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from app.ui import main_window as main_window_module


def test_main_window_inicializa_sem_configuracao(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        main_window_module,
        "mostrar_alerta",
        lambda *args, **kwargs: None,
    )

    app = QApplication.instance() or QApplication([])
    window = main_window_module.MainWindow()

    assert window.windowTitle().startswith("MSS - ")
    assert window.stack.count() == 18

    window.close()
    app.processEvents()
