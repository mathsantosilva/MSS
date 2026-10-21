import pytest

from app.services.update_service import update_service


@pytest.mark.parametrize(
    ("tag_a", "tag_b", "resultado_esperado"),
    [
        ("v3.0.1", "3.0.2", -1),
        ("3.1.0", "3.0.9", 1),
        ("4.2.0", "v4.2.0", 0),
        ("versao-invalida", "4.2.0", 0),
    ],
)
def test_comparar_tags(tag_a, tag_b, resultado_esperado):
    service = update_service(settings=None)

    assert service.comparar_tags(tag_a, tag_b) == resultado_esperado


def test_main_window_pode_ser_importada():
    from app.ui.main_window import MainWindow

    assert MainWindow.__name__ == "MainWindow"
