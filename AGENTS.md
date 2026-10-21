# Instruções para agentes do projeto MSS

## Leitura obrigatória

Antes de analisar, planejar ou alterar qualquer parte deste repositório, leia integralmente [`CONTEXTO_DO_PROJETO.md`](CONTEXTO_DO_PROJETO.md). Esse documento é a memória persistente e o mapa arquitetural do MSS.

Também confira `git status --short --branch` antes de editar. A migração atual pode conter alterações locais parcialmente adicionadas ao índice; nunca presuma que `HEAD`, o índice e o working tree representam o mesmo estado.

## Ordem de autoridade

1. Pedido atual do usuário e instruções do ambiente.
2. Este `AGENTS.md`.
3. `CONTEXTO_DO_PROJETO.md`.
4. Código, testes e histórico Git mais recentes.

Se o código ou o histórico contradisserem o contexto, não esconda a divergência: valide a intenção, preserve o trabalho existente e atualize o contexto junto com a mudança.

## Direção do projeto

- O MSS é uma aplicação desktop Windows em Python voltada a operações de apoio sobre SQL Server, bancos de muro, Redis, backups, documentos de teste e configurações.
- `BuscaMuro.py` é a implementação legada e continua sendo a principal referência de comportamento enquanto a paridade não for comprovada.
- A direção arquitetural atual é a aplicação PySide6 em `mss/`, com UI, serviços, modelos de configuração e workers separados.
- As pastas legadas/intermediárias `app/`, `core/`, `domain/`, `ui/` e `use_cases/` não devem ser restauradas ou adotadas como arquitetura-alvo sem uma decisão explícita; elas representam uma tentativa anterior de modularização.
- Migre por fluxo vertical: tela, validação, serviço, integração, tratamento de erro e teste. Não marque uma tela como concluída apenas porque o layout existe.

## Regras de segurança e dados

- Nunca registre, exiba, versione ou copie senhas, connection strings, IPs internos, nomes sensíveis de ambientes, tokens ou dados reais presentes em `Config/`, `Configs/` ou arquivos equivalentes.
- Use placeholders e estruturas de exemplo em documentação e testes.
- Não execute `FLUSHALL`, restauração de banco, alteração de versão, download/substituição de executável ou SQL contra ambientes reais sem solicitação explícita e alvo confirmado pelo usuário.
- Testes de banco, Redis, GitHub e atualização devem usar doubles, mocks ou ambientes descartáveis por padrão.
- Preserve `BuscaMuro.py` e o executável legado até que exista paridade funcional validada e uma decisão registrada de remoção.

## Convenções de implementação

- Mantenha a linguagem de produto e a documentação em português do Brasil, preservando termos de domínio já usados pelo projeto.
- Considere Windows como plataforma operacional primária.
- Na aplicação nova, a UI não deve conter SQL, acesso Redis, download, filesystem destrutivo ou regra de documento; delegue essas ações aos serviços.
- Operações demoradas não devem bloquear a thread da UI. Utilize o padrão de worker Qt já iniciado em `mss/app/workers/task_worker.py` ou uma evolução compatível.
- Centralize caminhos e configuração; evite comportamento dependente do diretório atual de execução.
- Não misture artefatos gerados (`*.exe`, `__pycache__`, logs, saídas em `Arquivos/`) com código-fonte.
- Ao tocar em versionamento ou atualização, reconcilie as versões do legado, da aplicação nova, das tags e dos assets de release.

## Validação mínima

Adapte os comandos ao escopo da mudança, mas preserve este baseline:

```powershell
.\.venv\Scripts\python.exe -m compileall -q mss tests
$env:PYTHONPATH = "mss"
.\.venv\Scripts\python.exe -c "from app.ui.main_window import MainWindow"
.\.venv\Scripts\python.exe -m pytest -q
```

O contexto registra falhas conhecidas desses comandos. Uma mudança não deve alegar sucesso ignorando falhas de importação, ausência de testes ou execução simulada.

## Manutenção do contexto

Atualize `CONTEXTO_DO_PROJETO.md` na mesma mudança quando houver:

- decisão arquitetural ou funcional duradoura;
- alteração de ponto de entrada, estrutura de pastas ou fluxo de configuração;
- conclusão, remoção ou substituição de uma funcionalidade relevante;
- mudança no estado da migração, build, testes, release ou branches de trabalho;
- novo risco, dependência, integração ou regra operacional que afete trabalhos futuros.

Não transforme o contexto em diário de commits. Registre apenas o estado consolidado, decisões que continuam válidas, pendências acionáveis e referências úteis. Nunca inclua segredos.
