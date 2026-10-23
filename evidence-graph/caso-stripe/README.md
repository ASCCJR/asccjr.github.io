# Caso público da Stripe com consumidor simulado

Esta página combina contratos públicos preservados de duas versões da API com
um leitor antigo e um leitor adaptado criados para demonstração. Não representa
um cliente, incidente ou integração real da Stripe. A execução é local e sintética;
o navegador mostra resultados registrados, sem chamar a API.

- `sources/before.json` e `sources/after.json`: contratos públicos completos,
  fixados por hash e commit nas referências de `manifest.json`.
- `sources/CONTRACTS_LICENSE.txt`: aviso MIT do fornecedor, preservado.
- `demo/consumer_demo.py`: código próprio efetivamente executado.
- `demo/consumer_demo_cases.json`: nove cenários fictícios e expectativas da tarefa.
- `demo/result.json`: 23 registros de entrada, saída, expectativa e exceção.
- `case-bundle.json`: documentos e simulação, identificados separadamente.

Para repetir somente a execução dos leitores, com Python 3.12 ou posterior e
sem novas bibliotecas, obter os arquivos de `demo/` e executar:

```sh
python3 demo/replay_consumer.py
```

O replay compara a execução com os resultados preservados e não revalida contratos
ou chamadas externas. As divergências do leitor antigo em relação à expectativa
são o fenômeno demonstrado; a saída adaptada cobre somente os exemplos preparados.
A geração da visualização e a conferência dos formatos dos contratos continuam
no adaptador do projeto. Consumidores reais permanecem UNKNOWN e sua execução
NOT_VERIFIED; não há validação de negócio ou garantia de migração segura.

O catálogo fictício Grupo Aurora permanece disponível no seletor de fontes e
na página `../preview-m2/`. Os relatórios privados de avaliação não integram esta
publicação. Os arquivos da página têm hashes no manifesto; o parâmetro dos recursos
estáticos renova o cache e não fixa a página em uma revisão imutável.
