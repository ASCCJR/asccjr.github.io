# L6-A — protocolo do piloto controlado

## Perguntas e unidades

Doze consumidores locais, sem treinamento ou amostragem de mercado. Três alvos separados:

1. **breaks_when_response_available:** o programa completava com a resposta v1 e passa a lançar exceção com v2, para ao menos um input de teste? A disponibilidade da resposta é condicionada; não se confunde com permissão de acesso. Erros sem exceção não estão cobertos.
2. **used_in_baseline_window:** ocorreu chamada concluída na janela anterior? Referência: recibos HTTP completos do roteiro, fora dos spans usados como entrada.
3. **can_access_endpoint:** a sonda ao endpoint sob a identidade verificada conclui (200), é negada (403) ou fica indeterminada (503)? Estado fixo do laboratório, não permissão universal.

A remoção proposta de `cliente_id` é input comum a todas as condições. O consumidor de referência executa funções reais sobre payloads obtidos por HTTP, sem consultar os campos obrigatórios declarados ao analisador. O leitor privilegiado da fixture apenas obtém v1/v2 para os testes funcionais; não é técnica de contorno de um ambiente externo. As credenciais são temporárias e locais.

## Condições

C: manifesto de consumo (com erros deliberados); R: spans CLIENT/SERVER anteriores e nomes de campos acessados; A: snapshot de política. Avaliar C, R, A, CR, CA, RA e CRA. A regra de R que usa acesso direto a campo como sinal de quebra é uma hipótese deliberadamente limitada: pode errar em try/except. Nunca usar spans do teste posterior, labels, resultados de regressão ou código do oráculo como input do preditor.

Fontes conflitantes: abster-se. Sem campo acessado: não inferir ausência de dependência. Sem trace: não inferir ausência de uso. Acesso negado não elimina incompatibilidade de contrato. Política é reutilização do avaliador L5; enforcement do servidor é código separado, diretamente sobre uma tabela congelada.

## Perturbações fixadas antes da execução

Base; runtime removido; declarações vencidas; políticas marcadas incompletas; spans duplicados idênticos; spans rotulados em outro ambiente. São seis vistas das mesmas 12 referências, não 72 amostras independentes. Não agregar significância sobre as vistas. Perda de informação mantém a referência do mundo executado, muda somente o que o preditor enxerga.

## Métricas

Reportar TP/TN/FP/FN, abstenções em positivos/negativos e referências indeterminadas separadamente. Precisão = TP/(TP+FP); recall nos respondidos = TP/(TP+FN). Reportar também recuperação de positivos = TP/(TP+FN+abstenções positivas), cobertura = respondidos/referências binárias, acurácia dos respondidos e corretas/todas as referências binárias. Denominador zero é null, não 100%. Abstenção não é acerto nem negativo. Referência UNKNOWN nunca entra como acerto binário; afirmações definitivas nesses casos são contadas à parte.

## Independência e limites

O oráculo é comportamental e implementado separadamente do candidato. Não é benchmark externo, teste cego, pesquisa com clientes ou prova causal de benefício universal. Os casos e preditores têm o mesmo autor; nenhum programa é holdout de autoria independente. Doze programas têm comportamentos escolhidos, alguns compartilham funções. Nem todos os tipos de erro ou fluxos empresariais estão cobertos.

O protocolo e os fontes são hasheados antes da coleta. Esse congelamento local não constitui pré-registro externo. Não ajustar regras para apagar erros após esta rodada: correções futuras terão versão e nova avaliação. Os testes de software verificam a medição; uma heurística errar contra a referência não deve fazer o teste de medição falhar por si só.

## Artefatos e escopo

Persistir evidência, referências, previsões isoladas, contagens, linhas por caso e hashes. Não publicar credenciais, payloads ou logs de contatos. Não alterar o grafo, a M3, o Pages, o L5 ou o edital. Os candidatos desta pasta não substituem o analisador de produto.

## Referências metodológicas consultadas

- scikit-learn, precision_recall_fscore_support: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html — definições convencionais e denominadores sem observações.
- Geifman e El-Yaniv, Selective Classification for Deep Neural Networks (2017): https://arxiv.org/abs/1705.08500 — considerar cobertura junto ao erro quando se permite abstenção. Este experimento não implementa o modelo do artigo nem herda suas garantias.
