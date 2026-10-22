<h1 align="center"> MSS </h1>

![Logo_MSS](https://github.com/mathsantosilva/MSS/assets/44808193/25f6e0c7-8f57-46c7-8607-c70db71ef395)


## Introdução
O MSS foi desenvolvido para resolver um problema em particular "Atualização da bancos em lote" quando se tem um banco de muro "Banco de referencia com connections strings" com mais de 24 mil referencias,
<br>Reduzindo as horas que eram levadas nas atualizações por conta das tentativas falhas, criando um novo banco de muro com somente referencias de bancos que existem nas instancias de Testes

### Principais funções
- Realiza busca e inserção das connections strings no banco de muro
- Realiza consulta da versão das connections strings para validar atualizações
- Replica o version atualizado do banco de muro update para o banco de muro padrão
- Realiza o download dos backups de banco para a pasta eventual
- Realiza a restauração dos backups da pasta eventual
- Realiza o Flushall de todos os redis
- Realiza o Flushall de redis especificos
- Realiza a Criação de numero de documentos para realização de Testes (CEI, CNPJ, CPF, NIF, PIS)
- Realiza a validação de numeros de documentos (CEI, CNPJ, CPF, NIF, PIS)
- Alteração da aparencia do Programa (Mudança das cores padrões)

### Arquivos de configuração
- Exemplo: Config.json

```json
{
    "controle_versao_json": {
        "versao": "2.1",
  		"data": "2024-05-29 19:00:00",
  		"comentario": "Refatorado json para melhorar a estrutura do redis_qa"
    },
    "bancos_update": {
        "database_update_br": "",
        "database_update_mx": "",
        "database_update_pt": "",
        "database_update_md": ""
    },
    "bases_muro": [
        ""
    ],
    "conexoes": [
        {
            "nome": "",
            "server": "",
            "username": "",
            "password": ""
        }
    ],
    "redis_qa": {
        "grupo_1":[
            {
                "nome_redis": "",
                "ip": "",
                "port": ""
            },
            {
                "nome_redis": "",
                "ip": "",
                "port": ""
            }
        ],
        "grupo_2":[
            {
                "nome_redis": "",
                "ip": "",
                "port": ""
            },
            {
                "nome_redis": "",
                "ip": "",
                "port": ""
            }
        ]	
    }
}
```

- Exemplo: prog.conf
```conf
[ConfiguracoesGerais]
config_default = 
data_ultima_atualizacao = 01-02-2024

[ConfiguracoesAparencia]
background_color_fundo = #F0F0F0
background_color_titulos = #F0F0F0
background_color_botoes = #F0F0F0
background_color_botoes_navs = #ADADAD
background_color_fonte = #000000
```

## Migração atual para PySide6

O MSS está sendo migrado gradualmente do monólito Tkinter `BuscaMuro.py` para a aplicação PySide6 em `mss/`.

A nova estrutura separa:

- modelos e constantes em `mss/app/core/`;
- integrações e regras operacionais em `mss/app/services/`;
- janela, navegação e páginas em `mss/app/ui/`;
- tarefas de longa duração em `mss/app/workers/`.

O monólito continua sendo a referência funcional até que cada fluxo novo tenha serviço real, tratamento de erros e testes de paridade. Algumas páginas PySide6 ainda representam somente a interface e não executam a operação correspondente.

Consulte [`CONTEXTO_DO_PROJETO.md`](CONTEXTO_DO_PROJETO.md) para o mapa completo da arquitetura, estado de cada módulo, decisões, riscos e sequência recomendada da migração.

### Execução da aplicação nova

No PowerShell, a partir da raiz do repositório:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:PYTHONPATH = "mss"
.\.venv\Scripts\python.exe mss\main.py
```

### Validação de desenvolvimento

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m compileall -q mss tests
.\.venv\Scripts\python.exe -m pytest -q
```
