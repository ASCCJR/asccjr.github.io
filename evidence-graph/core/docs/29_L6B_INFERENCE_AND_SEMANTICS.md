# L6-B — dependência observada, inferência e resultado de negócio

**Data:** 2026-10-16. **Base:** `4b1a025571860c18e3e1b389e517a563fa734e28` (L6-A).  
**Estado:** código experimental, sem promoção ao produto, merge ou deploy.  
**Pasta:** `core/evaluation/refinement/`.

## Entrega e fronteiras

Implementamos uma inferência restrita que acrescenta código do consumidor como evidência S. Ela separa requisito declarado, acesso observado a campo, impacto potencial, previsão de exceção e confirmação por execução. Correção de negócio é outra pergunta e não é deduzida de uma execução sem exceção.

A L6-A continua intacta como baseline. Nenhum código L1–L5, interface M3, site Pages, catálogo Grupo Aurora, documento de equipe, material pessoal ou variante de edital foi modificado. A autorização para continuar o Core não foi usada como autorização de merge ou publicação.

## O que S realmente faz

`bounded_static.py` lê uma AST de Python sem executar o texto recebido. Reconhece retornos simples, acesso literal a campos, `get`, strings, concatenação, `upper/lower` e um `try/except KeyError` delimitado. Usa uma hipótese explícita de respostas exatas como dicionários built-in, campos string obrigatórios e ausência de efeitos externos.

Essa hipótese é adicional. OpenAPI genérico não garante sozinho que um campo omitido do esquema nunca será retornado. O laboratório conhece a implementação que produz a resposta; o vínculo código/consumidor e o contrato fechado ainda são fornecidos por configuração controlada, não descobertos em uma empresa.

Código condicional, loops, chamadas externas, acesso dinâmico, slices, schemas abertos/nullable e sintaxe não suportada produzem UNKNOWN. Código de outra versão, outro ambiente, vencido, com hash diferente ou referente a outra mudança não sustenta conclusão. Hash de conteúdo não autentica origem.

Isso é análise condicional de um subconjunto pequeno, não prova formal de um analisador geral nem sandbox para código hostil. O texto é limitado em tamanho e nós; somente fixtures locais confiáveis são usadas. Os resultados continuam candidatos, fora do analisador do produto.

## Comparação justa: mesmas perguntas, informação adicional explícita

O alvo original permanece **exceção após a mudança sob disponibilidade da resposta**. Não foi trocado por “campo lido” para melhorar números. Reproduzimos os mesmos 12 casos e preservamos o baseline:

| Condição | Corretas | FP | FN | Inconclusivas |
|---|---:|---:|---:|---:|
| A_CRA, sem alterações | 7 | 2 | 0 | 3 |
| B sem S | 0 | 0 | 0 | 12 |
| Somente S | 11 | 0 | 0 | 1 |
| B com S | 11 | 0 | 0 | 1 |

**Não atribuímos essa melhora à fusão com a mesma informação.** O novo braço recebe código e uma hipótese de resposta exata que A não tinha. S isolado obtém as mesmas previsões de exceção de B completo. C/R/A continuam explicando contexto, declarações, uso e permissão; não são a causa desse ganho específico.

B sem S não transforma manifesto ou leitura anterior em prova de exceção. Ele preserva os indícios de impacto, mas perde toda a cobertura de previsão binária. Zero falsos positivos por abstenção total não é resultado perfeito nem solução suficiente.

Nos casos antigos, o tratamento de KeyError deixa de ser confundido com falha, o `get(...).upper()` sem default continua sendo reconhecido como incompatível e os manifestos que contradizem o código continuam visíveis como divergências. O ramo condicional não reconhecido permanece inconclusivo.

## Oito casos novos e um limite de negócio

Acrescentamos oito casos, com sete funções de entrada. Os dois primeiros compartilham a mesma função de fallback, mas têm requisitos diferentes. Ainda são da mesma autoria, não holdout ou revisão externa.

| Caso | Previsão de exceção | Exceção executada | Regra de negócio violada |
|---|---|---|---|
| n01: pedido precisa manter identificador | NO | NO | YES |
| n02: consulta admite anonimato | NO | NO | NO |
| n03: comprimento do identificador | UNKNOWN | NO | YES |
| n04: exceção convertida para ValueError | UNKNOWN | YES | YES |
| n05: função auxiliar de normalização | UNKNOWN | NO | NO |
| n06: ramo condicional completo | UNKNOWN | YES | YES |
| n07: sufixo usado no roteamento | UNKNOWN | NO | YES |
| n08: situação em maiúsculas | NO | NO | NO |

Resultado de previsão de exceção nos novos casos: **3 corretas, 0 erros e 5 inconclusivas**. A baixa cobertura é explícita. Não contamos UNKNOWN como acerto.

**Três casos violam o requisito sem lançar exceção.** O programa termina, mas perde o identificador ou entrega um valor inadequado. Em n01 e n02, código idêntico produz a mesma previsão técnica; apenas o requisito de negócio distingue a falha. O candidato não recebe as expectativas e mantém `semantic_correctness=UNKNOWN`. Esses três erros foram identificados pelo avaliador, não automaticamente pelo preditor.

A referência executa as funções com respostas obtidas por HTTP local e compara a saída a expectativas declaradas em arquivo separado. O estado anterior também é conferido, para não chamar um erro pré-existente de regressão. A previsão continua com `failure_confirmed_by_execution=NOT_TESTED`, pois não recebe o resultado posterior.

## Robustez e rastreabilidade

Reaplicamos as seis vistas da L6-A e acrescentamos S vencido e S com hash incorreto. As seis primeiras não mudam a previsão baseada em S, pois esse braço usa a fonte adicional. Quando S é inválido, as 12 respostas voltam a UNKNOWN. Essa independência deixa visível o efeito da nova fonte e não é apresentada como ganho mágico por mais evidências.

Protocolo, código, requisitos semânticos e módulos anteriores reutilizados são hasheados antes da execução. Predições rodam em subprocesso com caminhos apenas dos inputs de evidência e código. Esse isolamento de interfaces não é sandbox adversarial nem pré-registro externo. Fonte, código e casos têm a mesma autoria; não há generalização estatística demonstrada.

Execução de referência final: baseline iniciado em **2026-10-16T18:19:08.443657+00:00**, com 22 spans/11 traces no cenário anterior. A nova referência semântica realizou 18 chamadas de teste a duas versões de uma API local, além da leitura de seus dois contratos OpenAPI. Nenhuma consulta empresarial, credencial externa ou payload real foi usado.

`results.json` SHA-256:

```text
a90c4d79c6eab6da7c0da15b3bd4963f4ad99b73443fb7988b58e8393cdeea19
```

A medição final repetiu exatamente as contagens da primeira medição. Ajustes de validação rejeitaram argumentos duplicados e fontes de uma mudança diferente; não alteraram os resultados registrados. Um teste de texto esperava uma palavra em inglês no relatório em português e foi corrigido para a formulação realmente emitida; não houve retirada de verificação funcional.

## Testes e reprodução

**229 testes locais aprovados nesta rodada:** 124 regressões L1/L2/L4/L5, 43 testes L6-A e 62 testes L6-B. Não houve teste novo de navegador: a interface não mudou. Os cinco arquivos Python enviados foram conferidos por hash de blob com os arquivos testados. O workflow adiciona a nova suíte às anteriores; verificar o run do commit antes de afirmar sucesso no CI.

```sh
python -m pip install -r evidence-graph/core/lab-runtime/requirements.txt
python evidence-graph/core/evaluation/refinement/run_refinement.py --out evidence-graph/core/evaluation/runs/l6b-01
cd evidence-graph/core/evaluation/refinement
python -m unittest -v test_refinement
```

Pasta existente é recusada; saídas no projeto ficam em `evaluation/runs/`. Falha deixa marcador INCOMPLETE e não manifesto de sucesso. CSV/JSON preservam previsões, erros, abstenções e origens. O pacote entregue inclui uma execução concluída; novas execuções terão tempos e hashes de captura diferentes.

## Próximo marco limitado

Não ampliar indefinidamente o subconjunto de Python só para melhorar estes casos. Preparar revisão de cenários por outra pessoa e conferir se o recorte é útil para o usuário. Na próxima ligação com a apresentação, distinguir **indício de impacto**, **inferência com hipóteses** e **resultado de teste**; não converter as previsões deste piloto em rótulos genéricos de “vai quebrar”. O grafo/lineage e a experiência Grupo Aurora permanecem a base visual.

A medição de resultados de negócio foi iniciada, não resolvida universalmente. A revisão independente e as sessões com usuários seguem pendentes. O edital continua separado do desenvolvimento do Core.

Referência técnica: documentação oficial de AST do Python, https://docs.python.org/3/library/ast.html. Essa referência explica a ferramenta de parsing; não valida esta implementação ou sua novidade.
