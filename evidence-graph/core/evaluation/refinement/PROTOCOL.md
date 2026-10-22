# L6-B — protocolo antes da medição

## Pergunta e não objetivo

Distinguir leitura observada, requisito declarado, impacto potencial, inferência de exceção e resultado confirmado. Não melhorar números chamando todas as previsões de riscos, nem substituir a L6-A. O alvo binário original continua: exceção na tarefa sob disponibilidade da resposta v2, tendo completado em v1. Correção de negócio é um segundo alvo explícito, medido somente nos oito novos casos.

## Fontes e comparação

C/R/A e os 12 consumidores originais são reutilizados sem editar os fontes da L6-A. Adiciona-se **S**, código local de uma função associado manualmente a um consumidor, mais a hipótese de dicionário built-in exato com campos string obrigatórios. A associação é confiável apenas dentro da fixture. OpenAPI genérico não garante ausência de campos extras: o contrato fechado é uma hipótese adicional declarada, não inferido silenciosamente do documento anterior.

Quatro braços: A_CRA (original); B_without_S (declara/observa risco, abstém-se de prever exceção); S_only; B_with_S. A acurácia de S não é atribuída à fusão sob o mesmo orçamento de evidências. Se S_only = B_with_S, reportar essa igualdade. C/R/A continuam relevantes para explicar declarações, uso e permissão, não resolvem automaticamente o comportamento de fallback.

S analisa AST sem eval/exec/import do texto. Aceita um subconjunto estrito; qualquer forma não suportada produz UNKNOWN. Nenhum caminho não reconhecido é interpretado como segurança. São hipóteses verificáveis no laboratório, não prova formal nem análise geral de Python. Código associado à versão errada, vencido ou com hash inválido é descartado. Hash identifica conteúdo, não autentica autoria.

## Casos e independência

Mesmos 12 casos antigos, conhecidos ao desenhar B: comparação de desenvolvimento, não holdout. Oito novos casos, também da mesma autoria; não alegar revisão externa. Dois compartilham o mesmo programa, mas diferem nos requisitos de negócio para mostrar que retorno sem exceção não prova correção. Outros incluem len, helper externo, ramo condicional, raise e slice, que devem permanecer fora da análise restrita.

Expectativas de negócio em semantic_requirements.json ficam apenas no avaliador. Preditor em subprocesso lê inputs de evidência e fonte, nunca truth, requisitos ou resultados posteriores. É isolamento de interface, não sandbox contra código hostil. Inputs e fixtures são locais e confiáveis; não executar código de usuário arbitrário.

Referências funcionais dos casos novos usam respostas v1/v2 obtidas por HTTP real; somente funções de teste pré-definidas são executadas. O oráculo de requisito compara resultados com expectativas explícitas e avalia baseline antes de chamar uma mudança de regressão. Não classificar erro pré-existente como causado pela remoção.

## Medição fixada

Preservar métricas da L6-A: TP/TN/FP/FN, abstenção em positivos/negativos, cobertura e recuperação de positivos com desconhecidos no denominador apropriado. UNKNOWN não é acerto, nem NO. Denominador zero permanece null.

Reaplicar seis vistas originais; acrescentar fonte S vencida e hash incorreto. Vistas não são amostras independentes. Nos novos casos reportar previsões de exceção separadas de requisitos violados e erros silenciosos. Não afirmar que a previsão resolve os erros sem exceção: semantic_correctness permanece UNKNOWN, e failure_confirmed_by_execution permanece NOT_TESTED no candidato.

Congelar código, protocolo, requisitos e dependências locais reutilizadas por hash antes de cada execução. Não modificar regras com base nos resultados para esconder erro; futuras mudanças recebem outra versão. Congelamento local não é pré-registro externo. O experimento não precisa melhorar para ser corretamente implementado.

## Preservação

Sem alteração no L6-A, L1–L5, UI, Pages, datasets, arquivos pessoais, documentos da equipe ou oportunidades. Saídas locais em diretório novo; sem sobrescrita, merge, deploy ou contato externo. Entrega em código, JSON/CSV e Markdown, sem redesenho.

Referência técnica: documentação oficial de ast, https://docs.python.org/3/library/ast.html. Uso de ast.parse não executa funções recebidas, mas não oferece por si só sandbox de recursos; tamanho/nós são delimitados e código hostil não está no escopo.
