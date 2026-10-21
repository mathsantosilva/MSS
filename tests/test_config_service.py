from app.services.config_service import ConfigService


def test_load_prog_conf_aceita_diretorio_legado(tmp_path, monkeypatch):
    config_dir = tmp_path / "Config"
    config_dir.mkdir()
    (config_dir / "prog.conf").write_text(
        """[ConfiguracoesGerais]
config_default = ambiente.json

[ConfiguracoesAparencia]
background_color_fundo = #F0F0F0
background_color_titulos = #F0F0F0
background_color_botoes = #F0F0F0
background_color_botoes_navs = #ADADAD
background_color_fonte = #000000
""",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    config = ConfigService().load_prog_conf()

    assert config is not None
    assert config.get("ConfiguracoesGerais", "config_default") == "ambiente.json"
