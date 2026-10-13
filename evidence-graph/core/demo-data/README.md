# Base sintética do EvidentGraph — M1

Gerador, validação de integridade, analisador de referência delimitado e testes. Sem HTML, backend, bibliotecas externas, rede ou credenciais. Python 3.10+.

```sh
cd evidence-graph/core/demo-data
python -m unittest -v test_model
python model.py --out build
```

## Arquivos

- `model.py`: gera 240 ativos, 512 relações e as evidências dos cenários; valida referências e calcula consumidores de mudanças delimitadas.
- `expected.json`: respostas esperadas escritas independentemente do analisador.
- `test_model.py`: testes de cenário, integridade e mutação de evidências.
- `build/`: saídas regeneráveis, ignoradas pelo Git; não é um site publicado.

Saídas: catálogo `enterprise.json`, manifesto SHA-256, resultados JSON e relatórios Markdown para CHG-001, CHG-002 e CHG-003. Regenerar sobrescreve apenas os arquivos de saída com os mesmos nomes no diretório indicado.

## Leitura para continuar

[Contrato de dados](../docs/13_DATA_CONTRACT.md) · [Cenários e oráculos](../docs/14_SCENARIOS_AND_EXPECTED_RESULTS.md) · [Registro de validação](../docs/15_M1_VALIDATION.md).

## Limites

Trata-se de simulação determinística para apoiar desenho e teste de UX. Não é um coletor, avaliador IAM, parser universal de contratos nem prova de escala empresarial. As relações de autorização/identidade não são spans e não autorizam recursos automaticamente. A análise usa um recorte explícito de relações e preserva desconhecimento.

A geração do inventário é implementada; cobertura real e utilidade para clientes não foram validadas. Não existe nova interface nesta entrega. Campus Mobile, documentos acadêmicos e demo pública permanecem inalterados.
