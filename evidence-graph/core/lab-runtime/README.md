# EvidentGraph — coleta local de evidências (L1)

**Dados de negócio inventados, execução real em laboratório.** Esta pasta não modifica o grafo público do Grupo Aurora nem a variante Claro.

## Pergunta do experimento

Ao remover `cliente_id` da API de clientes, conseguimos separar **incompatibilidade declarada**, **uso observado** e **falha efetivamente vista num teste**?

O comando inicia uma API FastAPI/Uvicorn somente em `127.0.0.1`, consulta um banco SQLite criado para o teste, busca os contratos OpenAPI por HTTP e executa clientes de teste contra as versões v1 e v2. OpenTelemetry registra spans de cliente, servidor e consulta. Os servidores são encerrados ao terminar. Nenhum endpoint empresarial é contatado.

## Executar

A partir desta pasta, com Python 3.10+:

```sh
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest -v test_lab
python lab.py --out runs/primeira-execucao
```

As dependências diretas estão fixadas nas versões testadas; não se trata de lock completo das dependências transitivas. O primeiro download de pacotes requer internet. A execução do laboratório usa apenas loopback.

O diretório de saída precisa ser novo; o comando recusa sobrescrita. Falhas de rede local/startup não são substituídas por dados fabricados. Uma execução incompleta pode deixar o diretório parcial, sem relatório final; use outro diretório para repetir.

## Saídas

| Arquivo | Conteúdo |
|---|---|
| `openapi-v1.json`, `openapi-v2.json` | Contratos obtidos dos dois endpoints locais |
| `contracts.json` | Requisitos declarados dos clientes de teste; não análise automática de código |
| `spans.json` | Spans emitidos pelo SDK durante chamadas reais; exportação JSON própria, não OTLP |
| `run.json` | Registro completo, horários UTC, contratos e spans |
| `analysis.json`, `report.md` | Comparação delimitada e referências às evidências |
| `manifest.json` | Hashes dos arquivos e contagem de spans |
| `lab.sqlite` | Banco descartável com um registro de negócio fictício |

Os identificadores depois de `#` nos relatórios são referências lógicas a registros JSON, não links de navegação implementados.

## Resultado esperado

| Cliente | Contrato | Execução v1 | Teste v2 |
|---|---|---|---|
| pedidos | Exige campo removido | Observada | Falha na verificação do contrato |
| portal | Exige apenas `status` | Observada | Passa na verificação executada |
| exportador | Exige campo removido | Não confirmada | Não executado |

O cliente exportador está declarado, mas não é executado deliberadamente. A ausência de trace não vira “sem dependência”. Dois clientes executados em duas versões produzem quatro traces e doze spans. A busca dos dois OpenAPI também usa HTTP real, mas não está instrumentada na contagem de spans.

## Limites

A instrumentação é manual. A API e os clientes de teste rodam em um processo, com threads e sockets reais; não é infraestrutura distribuída. A identificação por header é rótulo de laboratório, não autenticação. A janela é esta execução, sem cobertura contínua ou reavaliação de frescor em produção.

O comparador cobre exclusivamente a remoção de propriedades da resposta GET/200 deste endpoint. Uma falha significa que a verificação de campos exigidos pelo cliente de teste falhou, não que uma aplicação empresarial caiu. As mesmas declarações de consumo são usadas pelo cliente e pelo comparador; isso não é benchmark independente de precisão/recall.

Não há IAM, MCP, agente generativo, PostgreSQL ou coletor empresarial. Não foi reclassificado o dataset sintético da M1. Usa-se esquema separado `evidentgraph-lab-0.1`; o adaptador para a interface e o motor M1 ainda está pendente. `cliente_id` continua existindo no banco, mas não é retornado pela API v2: consultar a tabela não prova exposição de todos os campos.

Não são gravados valores de clientes, URLs com identificadores, credenciais ou corpos de resposta nos spans. Nomes de campos, rota-modelo, versões e IDs de trace são suficientes para este recorte. Para uso fora do laboratório, seriam necessários controles próprios de segurança e validação de entrada.

## Referências técnicas consultadas em 15/10/2026

- OpenTelemetry Python — instrumentação manual: https://opentelemetry.io/docs/languages/python/instrumentation/
- FastAPI — OpenAPI e metadados: https://fastapi.tiangolo.com/tutorial/metadata/
- FastAPI — modelos de resposta: https://fastapi.tiangolo.com/tutorial/response-model/

O código acima usa essas APIs; resultados e números deste laboratório vêm da execução registrada, não dessas páginas.
