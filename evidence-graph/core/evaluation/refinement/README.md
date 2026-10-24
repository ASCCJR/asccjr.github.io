# L6-B — inferência restrita e validação de resultado

Continuação exploratória da L6-A, sem alterar seus arquivos ou a interface.

## Executar

Na raiz do repositório, com as dependências anteriores:

```sh
python -m pip install -r evidence-graph/core/lab-runtime/requirements.txt
python evidence-graph/core/evaluation/refinement/run_refinement.py --out evidence-graph/core/evaluation/runs/l6b-01
cd evidence-graph/core/evaluation/refinement
python -m unittest -v test_refinement
```

O destino deve ser novo. Saídas no projeto ficam sob `evaluation/runs/`. Nada é publicado ou mesclado automaticamente.

## Arquivos

- `bounded_static.py`: análise sem execução de um subconjunto pequeno de Python, sob contrato exato de resposta do laboratório.
- `candidate.py`: separa requisito declarado, campo observado, impacto potencial, previsão de exceção, confirmação e correção de negócio.
- `challenges.py`: oito casos novos, sete funções de entrada; são fixtures da mesma autoria, não validação externa.
- `semantic_requirements.json`: expectativas de resultado, usadas só pelo avaliador, nunca pelo preditor.
- `run_refinement.py`: coleta real HTTP, condições, abstenções, comparação e relatórios.
- `test_refinement.py`: 62 testes de medição, inferência limitada e preservação.
- `PROTOCOL.md`: hipóteses, fontes adicionais, alvos e limitações fixados antes da medição.

## Resultado de referência

Nos mesmos 12 casos: A_CRA = 7 corretas, 2 falsos positivos, 3 inconclusivas; B com S = 11 corretas, nenhum erro binário observado, 1 inconclusiva. S traz código e hipóteses adicionais: não é vitória da fusão com a mesma informação. S isolado produz as mesmas previsões de exceção. Sem S, o candidato abstém-se nos 12 casos; isso reduz cobertura e não é acerto.

Nos oito novos: três previsões corretas de exceção, cinco inconclusivas. Três programas violam a regra de negócio sem lançar exceção. Não dizer que o candidato detectou esses três erros: foram encontrados pelo oráculo de requisitos; a correção semântica continua UNKNOWN para o preditor.

Casos antigos conhecidos, novos do mesmo autor. Sem benchmark externo, inferência geral, UI nova ou prova de superioridade comercial. Veja `core/docs/29_L6B_INFERENCE_AND_SEMANTICS.md`.
