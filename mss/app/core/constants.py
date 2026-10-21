# app/core/constants.py
import os

APP_NAME = "MSS"
APP_NAME_EXTENSION = "MSS.exe"
APP_NAME_EXTENSION_LEGACY = "BuscaMuro.exe"
APP_VERSION = "3.0.0"
JSON_VERSION = "3.0"
VERSION_JSON = '2.3'

WINDOW_TITLE = f"{APP_NAME} - {APP_VERSION}"
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600
WINDOW_MIN_WIDTH = 700
WINDOW_MIN_HEIGHT = 40
SPACING = 20
MARGIN_TOP = 10
MARGIN_BOTTOM = 10
MARGIN_LEFT = 50
MARGIN_RIGHT = 50
COLOR_BTN = "#3b82f6"
COLOR_FONT_BTN = "white"
COLOR_BTN_HOVER = "#2563eb"
COLOR_BTN_PRESSED = "#1d4ed8"
COLOR_TITLE = "black"
COLOR_BACKGROUND = "white"

MENU_TITLE = "MENU"

TITLE_TOOLS = "Ferramentas"
BTN_BANCO_MURO = "Banco de Muro"
BTN_REDIS = "Redis"
BTN_DOCUMENTOS = "Documentos"
BTN_SAIR = "Sair"
BTN_VOLTAR = "Voltar"

NM_PASTA_LOG = "Log"
NM_PASTA_CONFIG = "Configs"
NM_PASTA_ARQUIVO = "Arquivos"

NM_ARQUIVO_CONFIG = 'prog.conf'
NM_ARQUIVO_JSON_FIXO = "mss_config.json"

PATH_PROG = os.getcwd()
PATH_TEMP_APP = f"{PATH_PROG.split("\\")[0]}/MSS_temp"

NOTES_JSON = "Novo arquivo de configuracao do MSS"
MENSAGEM_JSON = "Refatorado json para melhorar a estrutura do redis_qa"

FORMATO_DATA = "%d-%m-%Y"
