# L6-A — piloto de avaliação de evidências

Não é uma nova interface nem um novo produto. Esta pasta testa heurísticas candidatas antes de promovê-las ao analisador. O grafo M3 e o laboratório L5 permanecem intactos.

## Executar

Python 3.10+ e dependências existentes do laboratório. Na raiz do repositório:

```sh
python -m pip install -r evidence-graph/core/lab-runtime/requirements.txt
python evidence-graph/core/evaluation/run_experiment.py --out evidence-graph/core/evaluation/runs/l6-01
cd evidence-graph/core/evaluation
python -m unittest -v test_experiment
```

A pasta de saída precisa ser nova. Saídas no projeto ficam sob `evaluation/runs/`, ignoradas no Git. Não há fallback sintético caso HTTP falhe, nem deploy ou envio de dados a terceiros.

## Ler

`PROTOCOL.md` define perguntas, fontes, abstenções e limites. `runs/l6-01/report.md` traz o resumo calculado; `cases.csv` mostra todas as respostas; `results.json` preserva as contagens. `evidence.json` não contém os resultados dos testes posteriores; `truth.json` guarda as referências separadamente. O preditor roda em subprocesso, recebe só o caminho de evidência e não lê os arquivos de referência. Isso é isolamento de interfaces, não sandbox adversarial.

## Casos preparados

| ID | Comportamento | Condição que queremos expor |
|---|---|---|
| c01 | Campo obrigatório de pedidos | Incompatibilidade real com retirada do campo |
| c02 | Usa somente status | Mudança sem exceção nessa tarefa |
| c03 | Rotina mensal, não executada no baseline | Dependência declarada sem observação |
| c04 | Campo obrigatório sem manifesto | Dependência que só aparece na execução |
| c05 | get com valor padrão | Referência opcional ao campo |
| c06 | Acesso direto com tratamento de KeyError | Acesso observado não implica quebra |
| c07 | Exige campo que o manifesto omite | Declaração errada e conflito entre fontes |
| c08 | Negado pelo controle de acesso | Negativa não elimina incompatibilidade intrínseca |
| c09 | Política indisponível | Referência de permissão indeterminada |
| c10 | Ramo não executado no baseline | Cobertura incompleta dos inputs |
| c11 | get seguido de upper sem default | Lookup opcional não garante tolerância |
| c12 | Manifesto exige campo não utilizado | Documentação falsa positiva sem contraditório suficiente |

São 12 casos de consumidor derivados de seis funções, não 12 implementações independentes de mercado. `oracle_consumers.py` não importa o preditor nem os requisitos do manifesto. O critério funcional é conclusão/exceção sobre os inputs preparados; não julga correção de negócio sem exceção.

As heurísticas de R/C deste experimento não foram integradas ao grafo ou ao cálculo de impacto do produto. Resultados, inclusive erros, devem ser mantidos. Uma próxima política de decisão exige nova versão do experimento.
