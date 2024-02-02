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
  		"versao": "2.0",
  		"data": "2024-02-01 20:22:17",
  		"comentario": "Refatorado json para aceitar varias conex�es e redis"
  	},
  	"bancos_update": {
  		"database_update_br": "",
  		"database_update_mx": "",
  		"database_update_pt": "",
  		"database_update_md": ""
  	},
  	"bases_muro": [
  
  	],
      "conexoes": [
  		{
  			"nome": "",
  			"server": "",
  			"username": "",
  			"password": ""
  		},
  		{
  			"nome":"",
  			"server": "",
  			"username": "",
  			"password": ""
  		}
  	],
  	"redis_qa": [
  		{
  			"grupo_1": [
  			{
  				"nome": ""
  			},
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
  		},
  		{
  			"grupo_2":[
  			{
  				"nome": ""
  			},
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
  	]
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
