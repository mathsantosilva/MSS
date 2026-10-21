# Contexto universal do projeto MSS

> Memória persistente e fonte de orientação do projeto. Leia este arquivo antes de implementar, revisar ou planejar mudanças. Ele descreve o produto, a arquitetura real, a migração em andamento, as decisões já materializadas e o estado conhecido do repositório.

## 1. Identificação do snapshot

- **Projeto:** MSS, também apresentado na interface e no legado como MSS BuscaMuro.
- **Repositório:** `mathsantosilva/MSS`.
- **Plataforma principal:** Windows desktop.
- **Linguagem:** Python.
- **Data deste levantamento:** 20 de outubro de 2026.
- **Branch de entrega:** `codex/pyside6-migration`.
- **Base da entrega:** `dev` em `f501ee4c9d2d36421d1d219549a5acb4e7fb1ddd`.
- **Estado:** primeiro snapshot consolidado da migração PySide6; a infraestrutura visual/configuração existe, mas a maior parte das operações ainda não possui paridade funcional.

As informações abaixo foram reconstruídas a partir do código do working tree, do índice Git, do `README.md`, do histórico local, das tags e do estado consultado no GitHub. O conteúdo de configurações locais foi tratado como sensível e não foi copiado.

### Como interpretar os estados

- **Legado funcional:** comportamento existente em `BuscaMuro.py`; é referência de paridade, mas não representa a arquitetura desejada.
- **Implementado na migração:** existe código concreto na árvore `mss/`.
- **Estrutura/UI apenas:** a tela ou interface existe, porém a operação real ainda está simulada ou desconectada.
- **Pendente:** não há implementação equivalente utilizável na aplicação nova.
- **Decisão inferida:** direção fortemente indicada pelo código atual, mas sem ADR ou registro formal anterior.

## 2. Propósito do produto

O MSS é uma ferramenta desktop para reduzir trabalho operacional e repetitivo em ambientes de desenvolvimento, teste e manutenção. O problema original é a atualização em lote de referências de bancos: um “banco de muro” pode possuir dezenas de milhares de connection strings, muitas delas inválidas para determinada instância de testes. O sistema busca as bases existentes, compara referências e ajuda a construir ou manter bancos de muro apenas com conexões válidas para o ambiente escolhido.

Com o tempo, a aplicação agregou ferramentas relacionadas ao mesmo fluxo operacional:

- localizar bancos e atualizar registros de bancos de muro/update;
- consultar e replicar versões entre bancos;
- buscar informações de empresas ligadas às bases;
- baixar e restaurar backups SQL Server;
- limpar uma instância Redis ou um grupo de instâncias;
- gerar e validar documentos de teste;
- criar, editar e selecionar arquivos de configuração;
- personalizar aparência;
- verificar releases no GitHub e substituir o executável local.

O produto é orientado a uso interno e trabalha com operações potencialmente destrutivas. Clareza do ambiente selecionado, validação de entrada, logs e execução fora da thread da interface são requisitos essenciais, não detalhes opcionais.

## 3. Vocabulário do domínio

| Termo | Significado no projeto |
| --- | --- |
| **Banco de muro** | Banco de referência que mantém registros/connection strings de outras bases. |
| **Banco update** | Banco de atualização por localidade, configurado para BR, PT, MX e MD. |
| **Base de muro** | Nome de uma base de referência listada em `bases_muro`. |
| **Conexão** | Ambiente SQL identificado por nome, servidor, usuário e senha. |
| **Configuração fixa** | `mss_config.json`; guarda seleção atual, data de atualização, versão do formato e aparência. |
| **Configuração de ambiente** | JSON selecionável com metadados, bancos update, bases de muro, conexões SQL e grupos Redis. |
| **Grupo Redis** | Conjunto nomeado de instâncias Redis, cada uma com nome, IP e porta. |
| **Versão do aplicativo** | Versão usada para janela, atualização automática, tag e asset de release. Hoje está inconsistente entre legado e migração. |
| **Versão do JSON** | Versão do formato de configuração; não deve ser confundida com a versão do aplicativo. |
| **Paridade** | A nova aplicação reproduz o comportamento necessário do legado com tratamento de erro e testes equivalentes. |

## 4. Princípios que devem orientar a migração

1. **Preservar comportamento antes de remover o legado.** `BuscaMuro.py` permanece como referência até que cada fluxo tenha paridade verificável.
2. **Migrar em fatias verticais.** Uma tela só está migrada quando UI, validação, serviço, integração, erros e testes estão conectados.
3. **Separar apresentação de operação.** Widgets coletam dados e exibem resultados; serviços executam regras e integrações.
4. **Não bloquear a interface.** SQL, Redis, rede, filesystem pesado e subprocessos devem sair da thread principal do Qt.
5. **Tornar dependências externas substituíveis.** Banco, Redis, GitHub, HTTP, relógio e filesystem precisam permitir testes sem alcançar ambientes reais.
6. **Manter configuração compatível durante a transição.** A leitura dos JSON existentes é parte do contrato do produto.
7. **Tratar credenciais como segredo.** Estrutura pode ser documentada; valores reais nunca devem entrar no Git, nos logs de agentes ou neste contexto.
8. **Entregar mudanças pequenas e revisáveis.** A divergência atual entre branches e o volume do working tree tornam commits grandes especialmente arriscados.
9. **Distinguir layout de funcionalidade.** Mensagens simuladas na saída de uma página não equivalem à rotina operacional do legado.
10. **Atualizar este contexto junto com decisões duradouras.** O arquivo deve refletir o sistema que realmente existe.

### Preferências de colaboração conhecidas

- Manter um contexto universal suficientemente completo para que um novo chat ou agente não precise redescobrir o projeto arquivo por arquivo.
- Fazer o `AGENTS.md` apontar obrigatoriamente para esta fonte de contexto.
- Comunicar documentação, estado e decisões em português do Brasil.
- Separar com clareza fatos confirmados, inferências arquiteturais, trabalho em andamento e pendências.
- Quando uma entrega estiver pronta para revisão e fizer sentido publicá-la, disponibilizá-la no GitHub por pull request sem misturar mudanças locais ainda não consolidadas.

## 5. As três gerações de arquitetura presentes

### 5.1 Monólito legado — referência funcional

O arquivo `BuscaMuro.py` concentra aproximadamente 5,6 mil linhas e utiliza Tkinter. A classe `Aplicativo` mantém estado de tela, configuração e operação, e o arquivo também contém funções globais de atualização, data e filesystem.

Responsabilidades presentes no monólito:

- inicialização e navegação da UI;
- leitura, criação e migração de configurações;
- personalização de cores;
- logging e arquivos de saída;
- conexão SQL Server via `pyodbc`;
- busca de bases e empresas;
- atualização/manipulação de bancos update;
- consulta e replicação de versões;
- download e restauração de backups;
- Redis via pacote `redis`;
- geração e validação de NIF, CNPJ, CPF, CEI e PIS;
- atualização do próprio executável via GitHub/PyGithub e `requests`;
- threads manuais para operações iniciadas pela UI.

O legado declara versão `4.2.0`, correspondente à tag local mais recente observada. Ele tem ampla cobertura funcional, mas mistura UI, estado, I/O, regras e integrações, o que dificulta teste e manutenção.

### 5.2 Modularização intermediária — tentativa anterior

O commit atual de `dev` contém uma tentativa de separar responsabilidades em:

- `app/container.py`;
- `core/`;
- `domain/`;
- `ui/`;
- `use_cases/`;
- `main.py` na raiz.

Ela introduziu conceitos úteis como container de dependências, filesystem, logger, serviço de versões e classes de geração/validação de documentos. Porém, no working tree levantado, toda essa estrutura está preparada para remoção. A UI intermediária era mínima e parte do container referenciava módulos inexistentes, portanto ela não deve ser tratada como arquitetura ativa.

O trecho local adicionado ao `README.md` ainda recomenda essa estrutura intermediária. Essa orientação está desatualizada em relação à árvore `mss/` e precisa ser reconciliada quando a migração for consolidada.

### 5.3 Aplicação nova — direção atual

A árvore `mss/` representa a nova direção. Ela usa PySide6 e organiza o código em:

```text
mss/
├── main.py
└── app/
    ├── core/
    │   ├── constants.py
    │   └── settings.py
    ├── services/
    ├── ui/
    │   ├── main_window.py
    │   ├── pages/
    │   └── widgets/
    └── workers/
```

Fluxo arquitetural pretendido:

```text
mss/main.py
  -> QApplication
  -> MainWindow
     -> AppSideBar + QStackedWidget
     -> páginas PySide6
        -> serviços de aplicação
           -> SQL Server / Redis / GitHub / HTTP / filesystem
        -> TaskWorker para tarefas demoradas

Configs/mss_config.json
  -> ConfigService
  -> dataclasses de Settings
  -> MainWindow, sidebar e páginas
```

Essa direção começou como uma **decisão inferida** pelo código local e foi formalizada no primeiro snapshot da branch `codex/pyside6-migration`. Ainda não existe um ADR separado.

## 6. Arquitetura da aplicação PySide6

### 6.1 Entrada e composição

`mss/main.py` cria o `QApplication`, instancia `MainWindow`, mostra a janela e inicia o event loop.

`mss/app/ui/main_window.py` é hoje o composition root real. Ele:

1. garante a existência de `Log`, `Configs` e `Arquivos`;
2. carrega configurações por `ConfigService`;
3. cria o serviço de atualização e verifica a data da última consulta;
4. configura a janela em 900 × 600, com mínimo de 800 × 500;
5. cria a sidebar e o `QStackedWidget`;
6. instancia todas as páginas de uma vez;
7. conecta navegação e troca de arquivo de configuração;
8. abre o dashboard quando existe configuração selecionada, ou força a área de configuração quando não existe.

Não há container de injeção de dependência na aplicação nova. A janela instancia serviços e páginas diretamente.

### 6.2 Navegação e design visual

A navegação é feita por uma sidebar fixa de 220 px, com seções pai e opções filhas. A seção ativa expande seus filhos e usa estados `checked` dos botões.

Mapa da sidebar:

- Dashboard;
- Banco de Muro;
  - Buscar bancos;
  - Consultar versão;
  - Replicar versão;
- Redis;
  - Limpar todos;
  - Limpar específico;
- Documentos;
  - Gerador;
  - Validador;
- Informações Empresas;
  - Buscar dados;
- Configuração;
  - Arquivos;
  - Trocar arquivo;
  - Editar arquivo;
  - Criar arquivo.

O estilo hoje está codificado em `MainWindow.aplicar_estilo()`:

- sidebar escura `#111827`;
- fundo de conteúdo claro `#f9fafb`;
- azul principal/ativo `#2563eb`;
- textos claros/cinzas na navegação;
- páginas com margens amplas e cartões/botões simples.

As cores presentes em `Settings.appearance` ainda não controlam o stylesheet principal. `AppMenuBar` possui ações de tema claro/escuro, mas não é instanciado por `MainWindow` e suas ações não têm implementação. O botão/sinal de “Aparência” também não está conectado a uma página funcional.

### 6.3 Modelo de configuração tipado

`mss/app/core/settings.py` define dataclasses para:

- `ProgramSettings`;
- `AppearanceSettings`;
- `JsonMetadataSettings`;
- `DatabaseUpdateSettings`;
- `ConnectionSettings`;
- `RedisInstanceSettings`;
- `RedisGroupSettings`;
- `Settings` como agregado principal.

Esse modelo já alimenta sidebar, seletores de servidor, bancos de muro e grupos Redis. É uma base importante da arquitetura nova e deve permanecer independente de widgets.

### 6.4 Serviços

| Serviço | Estado observado | Responsabilidade atual/pretendida |
| --- | --- | --- |
| `ConfigService` | Parcialmente implementado | Carrega configuração fixa e de ambiente, cria `Settings`, lista, lê, cria e atualiza JSON. |
| `FileSystemService` | Implementado, simples | Cria diretórios principais relativos ao diretório atual. |
| `update_service` | Implementado, com riscos | Consulta release, compara versão, baixa asset, valida SHA-256 quando disponível e cria batch de substituição. |
| `UtilService` | Implementado, simples | Data atual e encerramento do processo. |
| `banco_muro_service` | Stub | Apenas espera dois segundos e retorna mensagem. |
| `backup_service` | Vazio | Migração ainda não iniciada. |
| `documentos_service` | Vazio | Regras continuam somente no legado/arquitetura removida. |
| `redis_service` | Vazio | Operações Redis continuam somente no legado/arquitetura removida. |

Não existe ainda um serviço novo dedicado a empresas, versões SQL ou logs de domínio.

### 6.5 Workers

`TaskWorker` encapsula uma função em `QThread` e expõe sinais `progresso`, `finalizado` e `erro`. Ele é uma fundação adequada para não travar a UI, mas não está conectado às páginas operacionais no snapshot atual.

## 7. Estado funcional por módulo

| Módulo | Legado | Migração PySide6 | Estado real |
| --- | --- | --- | --- |
| Dashboard | Não é o foco do legado | Layout e cards criados | Visual apenas. |
| Seleção/criação/edição de configuração | Funcional no monólito | Implementação substancial presente | É o fluxo mais avançado da migração; ainda requer testes e correções de caminhos/fallback. |
| Banco de muro — atualizar registros | Funcional no monólito | Formulário existe | Execução imprime valores simulados `"teste"`; sem SQL. |
| Banco de muro — consultar versões | Funcional no monólito | Formulário existe | Execução simulada; sem SQL. |
| Banco de muro — replicar versão | Funcional no monólito | Formulário existe | Execução apenas ecoa seleção; sem SQL. |
| Dados de empresas | Funcional no monólito | Formulário existe | Execução simulada; sem serviço. |
| Redis — limpar grupo | Funcional no monólito | Formulário existe | Não chama Redis. |
| Redis — limpar específico | Funcional no monólito | Formulário existe | Não chama Redis. |
| Gerar documentos | Funcional no monólito | Formulário existe | Apenas ecoa opções; serviço vazio. |
| Validar documentos | Funcional no monólito | Formulário existe | Apenas ecoa entrada; serviço vazio. |
| Download de backup | Funcional no monólito | Ausente da navegação nova | Pendente. |
| Restauração de backup | Funcional com issue aberta no legado | Serviço vazio e UI ausente | Pendente. |
| Aparência/temas | Alterável no legado | Estrutura parcial | Não conectada; estilo principal é fixo. |
| Autoatualização | Presente no legado | Serviço portado em parte | Não validado ponta a ponta e com versões divergentes. |
| Logging operacional | Presente no legado | Ausente como serviço | Pendente. |

## 8. Configuração e dados locais

### 8.1 Formatos

A migração trabalha com dois tipos de JSON.

Configuração fixa `mss_config.json`:

```json
{
  "selected_config": "<arquivo-de-ambiente>.json",
  "last_update_check": "DD-MM-AAAA",
  "version": "3.0",
  "notes": "<observação>",
  "check_updates_on_startup": true,
  "appearance": {
    "colors": {
      "window_background": "#...",
      "title_background": "#...",
      "button_background": "#...",
      "nav_button_background": "#...",
      "text": "#..."
    }
  }
}
```

Configuração de ambiente:

```json
{
  "controle_versao_json": {
    "versao": "<versão-do-formato>",
    "data": "<data/hora>",
    "comentario": "<descrição>"
  },
  "bancos_update": {
    "database_update_br": "<nome>",
    "database_update_pt": "<nome>",
    "database_update_mx": "<nome>",
    "database_update_md": "<nome>"
  },
  "bases_muro": ["<base>"],
  "conexoes": [
    {
      "nome": "<apelido>",
      "server": "<servidor>",
      "username": "<usuário>",
      "password": "<segredo>"
    }
  ],
  "redis_qa": {
    "<grupo>": [
      {
        "nome_redis": "<apelido>",
        "ip": "<endereço>",
        "port": "<porta>"
      }
    ]
  }
}
```

### 8.2 Situação dos diretórios

- O legado usa principalmente `Config/` e `prog.conf`.
- A migração nova usa `Configs/` e `mss_config.json`.
- Existem diretórios `Configs/` tanto na raiz quanto dentro de `mss/`.
- Os caminhos são relativos ao `os.getcwd()`, portanto a configuração encontrada muda conforme o diretório de onde o programa é iniciado.
- Os JSON são ignorados globalmente por `.gitignore`, o que ajuda a evitar credenciais no Git, mas também impede versionar exemplos com a extensão `.json` sem uma exceção explícita.

A direção recomendada é definir um único diretório de dados da aplicação, resolvido a partir de uma raiz estável ou diretório de dados do usuário, e manter apenas um exemplo sanitizado no repositório.

## 9. Integrações e dependências

### Dependências externas observadas

- `PySide6`: nova interface desktop;
- `pyodbc`: SQL Server;
- `redis`: operações Redis;
- `PyGithub` (`github`): tags/releases;
- `requests`: download e API de releases;
- `PyInstaller`: build do executável;
- `pytest`: framework disponível no ambiente, ainda sem suíte coletável.

No ambiente local observado, Python é `3.12.7`. Dependências de runtime estão registradas em `requirements.txt`; PyInstaller e pytest ficam em `requirements-dev.txt`. As versões foram fixadas com base no ambiente que validou este snapshot.

### Recursos externos

- GitHub `mathsantosilva/MSS` para código, issues, tags e releases;
- SQL Server para bases de muro, bases update, empresas, versões e backups;
- Redis para limpeza de chaves/instâncias;
- filesystem Windows para configurações, logs, arquivos gerados, backups e atualização do executável;
- shell/batch do Windows para substituir o executável após download.

## 10. Scripts SQL e build

`scripts_banco_update/` contém:

- `Create_update.sql`: cria um banco update e configura propriedades do SQL Server;
- `Atualiza_bases.sql`: cria estruturas como `KAIROS_DATABASES`, `historicos` e `versions` e registra a versão inicial;
- `version.conf`: versão associada aos scripts.

Esses scripts contêm nomes e caminhos que precisam ser adaptados ao ambiente. Nunca devem ser executados automaticamente contra um servidor não confirmado.

`build.py` ainda empacota apenas `BuscaMuro.py` em modo `--onefile -w`. Ele não representa a aplicação PySide6 em `mss/main.py`. Existem executáveis grandes na raiz e dentro de `mss/`; o executável interno e caches Python estão sem regra de ignore específica no estado atual.

## 11. Estrutura de arquivos relevante

| Caminho | Papel atual |
| --- | --- |
| `AGENTS.md` | Obriga agentes a ler e manter este contexto; contém regras operacionais. |
| `CONTEXTO_DO_PROJETO.md` | Memória persistente e fonte de orientação. |
| `README.md` | Apresentação histórica e lista de funções; a estratégia de arquitetura no final está desalinhada com a migração PySide6. |
| `BuscaMuro.py` | Monólito Tkinter e referência funcional legada. |
| `BuscaMuro.exe` | Build legado versionado. |
| `build.py` | Build PyInstaller do legado. |
| `mss/main.py` | Ponto de entrada pretendido da aplicação PySide6. |
| `mss/app/core/constants.py` | Identidade, versões, nomes de pasta, cores e caminhos. |
| `mss/app/core/settings.py` | Dataclasses do modelo de configuração. |
| `mss/app/services/config_service.py` | Leitura, conversão e manutenção de configurações. |
| `mss/app/services/update_service.py` | Atualização automática via GitHub release. |
| `mss/app/services/filesystem_service.py` | Criação das pastas de runtime. |
| `mss/app/services/*.py` restantes | Serviços vazios ou stubs a implementar. |
| `mss/app/ui/main_window.py` | Composição, navegação e troca de configurações. |
| `mss/app/ui/pages/` | Hubs e formulários das funções. |
| `mss/app/ui/widgets/` | Sidebar, diálogos e menu ainda não integrado. |
| `mss/app/workers/task_worker.py` | Abstração inicial de trabalho em `QThread`. |
| `scripts_banco_update/` | Scripts SQL de criação/evolução de banco update. |
| `tests/comparar_tags_test.py` | Script manual, não um teste com asserções. |
| `tests/teste.py` | Protótipo manual de página PySide6, não teste automatizado. |
| `.readthedocs.yaml` | Configuração Sphinx; aponta para `docs/conf.py`, que não existe no snapshot. |
| `Config/`, `Configs/`, `Log/`, `Arquivos/` | Dados locais/runtime; podem conter segredos ou saídas e não são fonte versionada confiável. |

## 12. Decisões já materializadas

### D-001 — Manter o legado como referência temporária

O monólito continua presente e o build oficial ainda parte dele. Não removê-lo antes de paridade e decisão explícita.

### D-002 — Migrar a interface para PySide6

A árvore local nova, a sidebar, o `QStackedWidget`, as páginas e os workers usam PySide6. Esta é a direção atual, embora ainda não formalizada em commit.

### D-003 — Organizar a nova aplicação por UI, serviços, core e workers

A estrutura `mss/app` substitui a tentativa intermediária `domain/use_cases`. Serviços devem conter operação e integração; páginas devem permanecer focadas em entrada/saída.

### D-004 — Representar configuração com dataclasses

Os JSON são convertidos para um agregado `Settings`, reduzindo acesso disperso a dicionários na UI.

### D-005 — Usar navegação lateral e páginas empilhadas

A interface nova troca o menu/telas montadas do Tkinter por uma sidebar hierárquica e `QStackedWidget`.

### D-006 — Permitir gerenciamento de arquivos de configuração pela UI

Criar, editar, visualizar e selecionar configurações são fluxos de primeira classe. Ao selecionar um arquivo, a janela redistribui `Settings` às páginas que implementam `aplicar_settings`.

### D-007 — Manter atualização por GitHub release

O serviço novo preserva comparação semântica simples, download de asset, checksum quando fornecido e batch Windows para substituição. Esse fluxo ainda precisa ser tornado seguro e coerente com o versionamento novo.

### D-008 — Manter português do Brasil na experiência

Rótulos, mensagens e termos de domínio permanecem em português. Identificadores Python misturam inglês e português; não há decisão formal de renomeá-los em massa.

## 13. Estado Git e da migração em 20/10/2026

### Branches

- `dev` e `origin/dev` apontavam para `f501ee4`.
- `master` e `origin/master` apontavam para `0203e9c`, merge do PR #62.
- `teste` e `origin/teste` apontavam para `80998fa`.
- `maint` e `origin/maint` apontavam para `18c75a1`.
- Em relação a `master`, `dev` tinha 3 commits exclusivos e estava 18 commits atrás no grafo consultado.
- Em relação a `teste`, `dev` tinha 3 commits exclusivos e estava 27 commits atrás.

Não se deve fazer merge/rebase automático sem revisar a diferença: `master` contém as mudanças posteriores de UI Tkinter/CustomTkinter, enquanto o working tree local segue para PySide6.

### Working tree

Antes da consolidação, o repositório estava parcialmente preparado, com arquivos novos vazios no índice e o conteúdo real apenas no working tree. A branch `codex/pyside6-migration` foi criada para reunir deliberadamente:

- remoção da arquitetura intermediária (`app/`, `core/`, `domain/`, `ui/`, `use_cases/` e `main.py` raiz);
- aplicação PySide6 em `mss/app` e seu ponto de entrada `mss/main.py`;
- contexto universal, instruções para agentes e README alinhado;
- manifestos de dependência, configuração do pytest e testes mínimos;
- regras de ignore para configurações, caches, saídas e executáveis gerados.

Alterações da IDE, o protótipo local `tests/teste.py`, configurações reais e artefatos gerados ficaram fora da entrega. Eles não devem ser adicionados posteriormente sem revisão específica.

### Pull requests

Antes desta entrega, a consulta ao GitHub não encontrou pull request aberto. A documentação deste contexto foi então publicada separadamente no [PR #63 — docs: adicionar contexto universal do projeto MSS](https://github.com/mathsantosilva/MSS/pull/63), aberto contra `dev` e sem incluir a migração local não consolidada.

Os PRs anteriores recentes conhecidos estavam encerrados/mesclados:

- [#58 — Normalize dictionary key quotes in f-strings](https://github.com/mathsantosilva/MSS/pull/58);
- [#59 — feat: refresh tkinter ui styling](https://github.com/mathsantosilva/MSS/pull/59), depois revertido no histórico;
- [#61 — Refine customtkinter navigation](https://github.com/mathsantosilva/MSS/pull/61);
- [#62 — Fix CTk font initialization before Tk root creation](https://github.com/mathsantosilva/MSS/pull/62).

### Issues abertas relevantes

- [#9 — selecionar estado do CPF gerado](https://github.com/mathsantosilva/MSS/issues/9);
- [#55 — selecionar estado do CPF validado](https://github.com/mathsantosilva/MSS/issues/55);
- [#17 — widgets responsivos ao tamanho da janela](https://github.com/mathsantosilva/MSS/issues/17);
- [#25 — painel de atualização de bancos de muro update](https://github.com/mathsantosilva/MSS/issues/25);
- [#26 — desempenho de inicialização](https://github.com/mathsantosilva/MSS/issues/26);
- [#27 — gerenciar conexões Redis pelo programa](https://github.com/mathsantosilva/MSS/issues/27);
- [#28 — gerenciar conexões SQL pelo programa](https://github.com/mathsantosilva/MSS/issues/28);
- [#35 — erro não tratado na restauração de backup](https://github.com/mathsantosilva/MSS/issues/35).

As telas de edição de configuração já avançam parte das issues #27 e #28, mas elas não devem ser fechadas até que o gerenciamento esteja validado e integrado às operações reais. As issues #9 e #55 são relacionadas, porém tratam geração e validação respectivamente.

## 14. Baseline técnico verificado

Com o ambiente virtual local e Python 3.12.7:

- `python -m compileall -q mss tests`: **passou**;
- importação de `MainWindow` com `PYTHONPATH=mss`: **passou**;
- `pytest -q`: **7 testes passaram**.

O baseline cobre comparação de versões, importação e inicialização offscreen da janela, além da leitura do `prog.conf` no diretório legado. Ele ainda é pequeno e não comprova paridade das rotinas operacionais nem inicialização com integrações reais.

## 15. Problemas e riscos conhecidos

### Bloqueadores imediatos

1. **Serviços centrais vazios:** documentos, Redis e backup não foram portados; banco de muro é stub.
2. **Cobertura ainda mínima:** os sete testes não exercitam as operações SQL, Redis, documentos ou update.
3. **Paridade não comprovada:** a aplicação PySide6 é uma fundação de migração, não substituto funcional completo do legado.

### Configuração e caminhos

4. **Comportamento dependente do diretório atual:** `Config`, `Configs`, `Log`, `Arquivos` e `PATH_PROG` usam caminhos relativos a `cwd`.
5. **Duas árvores de configuração:** iniciar na raiz ou dentro de `mss/` pode carregar arquivos diferentes.
6. **Migração de configuração incompleta:** `load_prog_conf()` agora aceita `Config/` e `Configs/`, mas a resolução do JSON selecionado ainda precisa ser unificada.
7. **Erros retornados como dados:** alguns métodos de configuração retornam objetos `Exception`, o que dificulta diferenciar configuração válida de falha.
8. **Porta Redis pode lançar erro:** `parse_port()` usa `int(port)` sem validação amigável.

### Versão, update e release

9. **Versões divergentes:** legado/tag `4.2.0`, aplicação nova `APP_VERSION = 3.0.0`, formato fixo `3.0` e `VERSION_JSON = 2.3`.
10. **Risco de update cruzado:** a aplicação nova pode interpretar a release legada como atualização e substituir `MSS.exe` por um asset incompatível.
11. **Update síncrono na inicialização:** consulta e download podem bloquear a abertura da UI.
12. **Build desatualizado:** `build.py` ainda aponta para `BuscaMuro.py`.

### UI e comportamento

13. **Telas operacionais simuladas:** várias rotinas apenas imprimem seleção e “Processamento finalizado”.
14. **Worker não utilizado:** tarefas longas continuam sem integração ao `TaskWorker`.
15. **Tema desconectado:** configurações de aparência e menu de tema não controlam a UI real.
16. **Backup ausente:** não há páginas novas para download/restauração.
17. **Navegação constrói todas as páginas no início:** pode contribuir para a issue de desempenho quando os construtores ganharem integrações mais pesadas.

### Repositório e documentação

18. **Arquivos locais fora da entrega:** mudanças `.idea` e o protótipo `tests/teste.py` continuam locais e precisam de decisão separada.
19. **Read the Docs incompleto:** `.readthedocs.yaml` referencia `docs/conf.py`, ausente.

## 16. Decisões ainda abertas

Estas perguntas precisam de decisão explícita antes de uma consolidação maior:

1. A migração PySide6 será baseada em `dev`, em `master` atualizado ou em uma branch nova que reconcilie ambos?
2. `mss` será um pacote Python instalável (`python -m mss`) ou uma pasta executada diretamente?
3. Qual será a única raiz oficial para configurações e dados de runtime?
4. Qual esquema de versão unificará aplicativo, formato JSON, scripts SQL, tags e releases?
5. O novo executável continuará se autoatualizando ou o update será separado do processo principal?
6. A aparência será configurável como no legado ou haverá temas fixos claro/escuro?
7. Quando a arquitetura intermediária pode ser definitivamente removida do histórico de trabalho?
8. Quais ambientes seguros serão usados em testes de SQL Server e Redis?
9. O executável deve continuar versionado no Git ou ser publicado apenas como release artifact?

Enquanto não houver decisão, prefira mudanças reversíveis e não apague referências funcionais.

## 17. Próxima sequência recomendada

### Fase 0 — Proteger e tornar o estado reproduzível

1. Criar uma branch dedicada à migração a partir da base escolhida.
2. Revisar separadamente staged, unstaged, untracked e arquivos ignorados.
3. Atualizar `.gitignore` para caches, executáveis gerados e saídas locais.
4. Separar mudanças de IDE e dados locais do código.
5. Registrar dependências e comando oficial de execução.

### Fase 1 — Fazer a casca PySide6 iniciar com segurança

1. Corrigir imports e definir o modo oficial de entrada.
2. Resolver caminhos sem depender de `cwd`.
3. Corrigir fallback/migração de `prog.conf`.
4. Adiar update e integrações pesadas para depois da janela estar visível.
5. Adicionar smoke test de importação e criação da janela em modo offscreen.

### Fase 2 — Criar baseline de regressão

1. Portar primeiro regras puras de comparação de versões e documentos.
2. Testar parsing e round-trip de configuração com fixtures sanitizadas.
3. Criar contratos/fakes para GitHub, HTTP, SQL, Redis e filesystem.
4. Transformar `tests/comparar_tags_test.py` em teste com asserções e mover `tests/teste.py` para exemplos ou removê-lo após validação.

### Fase 3 — Migrar fluxos verticais

Ordem sugerida por risco e reaproveitamento:

1. configuração completa;
2. geração/validação de documentos;
3. consulta de versões, somente leitura;
4. busca de bancos e empresas, somente leitura;
5. replicação e atualização de bancos;
6. Redis, com confirmação explícita e escopo visível;
7. download/restauração de backup;
8. autoatualização e empacotamento.

Cada fluxo deve terminar com UI conectada, serviço real, worker, cancelamento/estado, logs, mensagens de erro e testes.

### Fase 4 — Consolidar release

1. Unificar versão.
2. Atualizar build para PySide6.
3. Validar asset e checksum de release.
4. Atualizar README e documentação.
5. Só então decidir a retirada do monólito e dos executáveis antigos.

## 18. Critério de “migrado” para uma funcionalidade

Uma funcionalidade só pode ser marcada como migrada quando:

- seus casos de entrada e validação estão definidos;
- a UI não contém a regra operacional;
- o serviço correspondente executa o comportamento real;
- integrações externas são substituíveis em testes;
- tarefas demoradas não bloqueiam a UI;
- erros e cancelamentos geram mensagens úteis e logs sem segredos;
- há testes automatizados do núcleo e pelo menos um teste de integração seguro;
- a configuração antiga relevante continua compatível ou possui migração explícita;
- o comportamento foi comparado com `BuscaMuro.py`;
- este contexto e o README foram atualizados quando necessário.

## 19. Regras de manutenção deste arquivo

Atualize este contexto quando ocorrer qualquer uma destas mudanças:

- escolha ou mudança da arquitetura-alvo;
- consolidação da branch de migração;
- novo ponto de entrada, build ou release;
- unificação de caminhos/configuração/versão;
- conclusão de um módulo funcional;
- remoção autorizada de código legado;
- criação de testes que altere o baseline;
- nova integração ou risco operacional;
- decisão que responda a uma das perguntas abertas.

Ao atualizar:

- substitua estado antigo em vez de acumular um diário;
- informe a data do snapshot e evidência verificável;
- diferencie fato, decisão e recomendação;
- preserve links úteis para issues/PRs;
- nunca inclua credenciais, tokens, connection strings ou dados de ambiente.

## 20. Resumo executivo para retomada

O MSS funcional ainda é o monólito Tkinter `BuscaMuro.py` na linha 4.2.0. A branch `codex/pyside6-migration` consolida a fundação da migração para PySide6 em `mss/`, com navegação e gerenciamento de configuração bem adiantados, mas as rotinas operacionais principais ainda não foram ligadas aos serviços. A tentativa intermediária `domain/use_cases` foi removida. O novo código compila, inicializa a janela em modo offscreen e possui um baseline de sete testes. `dev` ainda diverge significativamente de `master` e `teste`.

O próximo trabalho deve unificar caminhos/configuração, impedir update bloqueante na inicialização e ampliar o baseline de testes. Depois, a migração deve avançar fluxo a fluxo, usando o monólito como referência de comportamento até a paridade. O PR #63 mantém a entrega documental isolada; a branch de migração reúne o código e esta documentação para uma revisão integral.
