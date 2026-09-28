# Entrega 3 — Sprint de Inovação

**Disciplina:** Empreendedorismo / Projetos  
**Status:** rascunho — painel de pares ainda precisa de feedback real  
**Projetos do grupo:** ParkAI e EvidentGraph

---

## Estrutura usada

A Sprint segue quatro movimentos:

1. **Divergir** — buscar mecanismos fora do setor.
2. **Convergir** — escolher entre alternativas usando critérios definidos previamente.
3. **Provar** — definir uma prova mínima de mercado.
4. **Ouvir** — coletar feedback de pares e assumir um compromisso concreto.

---

# 1. Sprint — ParkAI

## Etapa 1 — Divergir

### Problema sem jargão

> **Como aproveitar melhor um recurso que perde valor quando fica vazio, sem afastar quem precisa utilizá-lo?**

### Domínios distantes observados

#### A. Feira livre

**Mecanismo:** a xepa reduz o preço de algo que perderá valor se não for vendido.

**Transferência:** reduzir preço de vagas em períodos de baixa demanda.

#### B. Energia elétrica

**Mecanismo:** tarifas diferenciadas podem deslocar consumo para períodos com menor pressão na rede.

**Transferência:** criar incentivos para deslocar parte da demanda de estacionamento para horários/dias menos congestionados.

#### C. Companhias aéreas

**Mecanismo:** capacidade limitada e perecível é comercializada com preços diferentes conforme momento e demanda.

**Transferência:** precificação de vagas levando em conta ocupação prevista e proximidade do horário de uso.

### Três ideias finalistas

1. **Pricing-as-a-Service**  
   API/motor de recomendação de preço integrado ao software atual da garagem.

2. **Reserva leve por WhatsApp**  
   Consulta, oferta e reserva sem exigir instalação de aplicativo.

3. **Diagnóstico de receita/ociosidade como serviço**  
   Análise periódica dos dados da garagem antes de construir uma plataforma completa.

---

## Etapa 2 — Convergir com critério

Critérios definidos **antes** da pontuação:

| Critério | Peso |
|---|---:|
| Valor potencial para o cliente | 30% |
| Diferenciação | 25% |
| Facilidade de testar | 25% |
| Viabilidade técnica no estágio atual | 20% |

Pontuação de trabalho: **1 = baixa / 5 = alta**.

| Ideia | Valor | Diferenciação | Testabilidade | Viabilidade | Nota ponderada |
|---|---:|---:|---:|---:|---:|
| Pricing-as-a-Service | 5 | 4 | 5 | 4 | **4,55** |
| WhatsApp/reserva leve | 4 | 3 | 5 | 5 | **4,20** |
| Diagnóstico como serviço | 3 | 2 | 5 | 5 | **3,65** |

### Ideia escolhida provisoriamente

**Pricing-as-a-Service**

### Motivo

A ideia preserva o valor central do ParkAI — usar dados para melhorar decisões de preço — sem exigir que a garagem substitua todo o seu sistema ou que o motorista adote imediatamente um novo aplicativo.

---

## Etapa 3 — Prova mínima de mercado

Não basta perguntar se gestores “gostam da ideia”.

### Evidência desejada

Conseguir pelo menos um gestor/operador de estacionamento disposto a:

1. fornecer um conjunto limitado de dados históricos;
2. receber recomendações de preço para períodos reais;
3. avaliar um piloto;
4. assumir um compromisso concreto caso o teste atinja um resultado combinado.

O compromisso mais forte seria:

- piloto pago; ou
- carta de intenção condicionada a uma métrica; ou
- autorização para testar a recomendação em uma garagem real.

### Teste mínimo

Não é necessário construir IA completa.

Pode-se começar com:

- dados históricos;
- regras/simulações simples de preço;
- planilha ou API mockada;
- comparação entre preço atual e recomendação;
- entrevista estruturada com gestor.

---

## Etapa 4 — Painel de pares

**A preencher com feedback real do grupo/colegas.**

### Potencial
> O que estamos subestimando?

Resposta: ______________________________________________

### Risco
> Que premissa deixa você em dúvida?

Resposta: ______________________________________________

### Ação
> Que estratégia faria isso avançar?

Resposta: ______________________________________________

### Compromisso a testar

________________________________________________________

---

# 2. Sprint — EvidentGraph

## Etapa 1 — Divergir

### Problema sem jargão

> **Como descobrir, antes de tomar uma decisão, o que realmente está conectado e quem pode ser afetado?**

### Domínios distantes observados

#### A. Controle de tráfego aéreo

**Mecanismo:** compara rota planejada, autorização e posição observada.

**Transferência:** comparar arquitetura declarada, permissão e runtime.

#### B. Triagem de emergência

**Mecanismo:** casos não recebem a mesma prioridade; urgência e impacto determinam a ordem de ação.

**Transferência:** blast radius deve distinguir dependências críticas, ativas, dormentes e potenciais.

#### C. Antifraude bancária

**Mecanismo:** o risco é analisado no momento da transação, antes de a ação ser aprovada.

**Transferência:** analisar dependências e impacto no momento de um pull request/deploy, antes da mudança entrar em produção.

### Três ideias finalistas

1. **Dependency Control Tower**  
   Interface que compara declarado × autorizado × observado.

2. **Impact Triage**  
   Classificação do blast radius por criticidade, atividade e confiança das evidências.

3. **Pre-Change Evidence Gate**  
   Verificação automática em pull request/deploy que informa o que pode quebrar antes da mudança.

---

## Etapa 2 — Convergir com critério

Critérios definidos antes da pontuação:

| Critério | Peso |
|---|---:|
| Valor potencial para o usuário | 30% |
| Diferenciação | 25% |
| Facilidade de testar | 25% |
| Viabilidade técnica no estágio atual | 20% |

Pontuação de trabalho: **1 = baixa / 5 = alta**.

| Ideia | Valor | Diferenciação | Testabilidade | Viabilidade | Nota ponderada |
|---|---:|---:|---:|---:|---:|
| Dependency Control Tower | 4 | 3 | 3 | 4 | **3,50** |
| Impact Triage | 4 | 3 | 4 | 4 | **3,75** |
| Pre-Change Evidence Gate | 5 | 4 | 5 | 4 | **4,55** |

### Ideia escolhida provisoriamente

**Pre-Change Evidence Gate**

### Motivo

É uma forma direta de entregar a inteligência do EvidentGraph dentro de um momento de decisão real e permite testar valor sem construir uma plataforma corporativa completa.

---

## Etapa 3 — Prova mínima de mercado

### Evidência desejada

A prova mais forte não é alguém dizer que “usaria”.

Buscar uma equipe técnica disposta a:

1. selecionar um repositório ou ambiente controlado;
2. fornecer um conjunto limitado de contratos/metadata e, quando possível, telemetria;
3. testar um relatório de impacto em uma mudança real ou simulada;
4. assumir algum compromisso caso o resultado seja útil.

Exemplos de compromisso:

- aceitar um piloto;
- integrar a checagem em um fluxo de CI de teste;
- dedicar tempo de engenharia para avaliação;
- carta de interesse;
- piloto pago em estágio posterior.

### Teste mínimo

Podemos evitar construir toda a arquitetura inicialmente.

Exemplo:

```text
1 mudança simulada
        ↓
OpenAPI + metadata + trace sintético/real
        ↓
análise EvidentGraph
        ↓
comentário automático no PR
```

Pergunta do teste:

> A informação entregue antes da mudança ajuda o usuário a identificar um impacto que ele não perceberia com as ferramentas atuais?

---

## Etapa 4 — Painel de pares

**A preencher com feedback real do grupo/colegas.**

### Potencial
> O que estamos subestimando?

Resposta: ______________________________________________

### Risco
> Que premissa deixa você em dúvida?

Resposta: ______________________________________________

### Ação
> Que estratégia faria isso avançar?

Resposta: ______________________________________________

### Compromisso a testar

________________________________________________________

---

# Resultado da Sprint

## ParkAI

- **Ideia evoluída:** Pricing-as-a-Service.
- **Próximo teste:** buscar um gestor disposto a avaliar recomendações de preço sobre dados reais/históricos.
- **Prova desejada:** compromisso com piloto, idealmente condicionado a métrica ou pagamento.
- **Feedback de pares:** pendente.

## EvidentGraph

- **Ideia evoluída:** Pre-Change Evidence Gate.
- **Próximo teste:** simular ou executar uma análise de impacto dentro de um fluxo de mudança.
- **Prova desejada:** uma equipe aceitar testar/integrar o mecanismo num ambiente controlado.
- **Feedback de pares:** pendente.

---

## Observação

As pontuações e escolhas acima são **provisórias** e servem como aplicação do método. Elas devem ser revisadas pelo grupo antes da entrega final.
