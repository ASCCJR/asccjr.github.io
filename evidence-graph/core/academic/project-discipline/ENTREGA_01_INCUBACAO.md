# Entrega 1 — Incubação

**Disciplina:** Empreendedorismo / Projetos  
**Status:** rascunho para revisão do grupo  
**Projetos do grupo:** ParkAI e EvidentGraph

---

## Pergunta

> **Qual seria uma forma radicalmente diferente de entregar o valor do seu projeto?**

A prática de incubação parte de uma primeira lista de respostas e, depois de um intervalo, busca novas formas de responder ao mesmo problema sem ficar presa à primeira solução.

---

# 1. ParkAI

## Ideias registradas inicialmente pelo grupo

1. **Pricing-as-a-Service**  
   Em vez de entregar um aplicativo completo ao motorista, oferecer apenas um motor/API de precificação dinâmica integrado ao sistema que a garagem já utiliza.

2. **WhatsApp ou SMS**  
   Eliminar a necessidade de instalar um aplicativo. O motorista consulta vaga e preço por mensagem e recebe um link para reserva/pagamento.

3. **Relatório em vez de software**  
   Entregar uma análise periódica sobre ocupação, preço e oportunidades de receita como serviço de consultoria, sem manter uma plataforma permanente.

## Resposta consolidada

A forma mais radicalmente diferente de entregar o valor do ParkAI seria **deixar de vender um aplicativo e entregar apenas a inteligência de precificação como infraestrutura invisível**.

Nesse modelo, o ParkAI funcionaria como um **Pricing-as-a-Service** conectado ao sistema que a garagem já usa. O cliente B2B continuaria operando sua plataforma atual, enquanto o ParkAI enviaria recomendações ou preços dinâmicos por API.

### O que muda

Em vez de:

```text
ParkAI = aplicativo + experiência completa do motorista
```

teríamos:

```text
Sistema existente da garagem
        ↓
     ParkAI API
        ↓
recomendação/preço dinâmico
```

O valor deixa de ser “usar o aplicativo ParkAI” e passa a ser **tomar uma decisão de preço melhor sem trocar o sistema existente**.

## Hipótese a validar

Garagens podem valorizar mais uma integração simples com seus sistemas atuais do que a adoção de uma nova plataforma completa.

---

# 2. EvidentGraph

## Ideias registradas inicialmente pelo grupo

1. **Chat sem grafo visual**  
   O usuário pergunta diretamente “o que quebra?”, “quem acessa?” ou “esse caminho aconteceu?”, enquanto o grafo permanece invisível.

2. **Plugin dentro das ferramentas existentes**  
   Entregar lineage, impacto e risco diretamente em ferramentas como GitHub, Databricks, dbt ou Slack.

3. **Auditoria como serviço**  
   Executar o mapeamento periodicamente e entregar relatórios de risco/dependência, sem exigir o uso contínuo de uma plataforma.

## Ideias que surgiram depois

A reflexão posterior levou a três formas ainda mais específicas de entregar o valor:

- **Pre-Change Evidence Gate:** responder automaticamente dentro de um pull request ou deploy antes de uma mudança ser aplicada.
- **Agent Passport:** gerar uma ficha viva do agente com permissões, tools, APIs alcançáveis, dados sensíveis e comportamento observado.
- **Architecture Black Box:** reconstruir como uma dependência, acesso ou incidente surgiu ao longo do tempo.

## Resposta consolidada

A forma mais radicalmente diferente de entregar o valor do EvidentGraph seria **não pedir que o usuário abra o EvidentGraph**.

Em vez de ser principalmente um dashboard, ele funcionaria como uma infraestrutura invisível dentro do fluxo de engenharia.

Exemplo:

```text
Pull Request / Deploy
        ↓
    EvidentGraph
        ↓
"Esta mudança afeta:
- 2 APIs ativas
- 1 agente em produção
- 1 MCP tool
- 1 dado sensível no caminho"
```

Nesse formato, o valor é entregue **no momento da decisão**, e não depois que alguém decide consultar um grafo.

## Hipótese a validar

Equipes técnicas podem perceber mais valor em receber análise de impacto automaticamente no fluxo de mudança do que em consultar uma plataforma separada.

---

# Síntese

Nos dois projetos, a incubação levou a uma mudança semelhante:

> **o valor não precisa estar preso à interface original do produto.**

- No **ParkAI**, a inteligência pode virar infraestrutura/API.
- No **EvidentGraph**, a inteligência pode aparecer automaticamente no fluxo de engenharia.

As duas propostas ainda são hipóteses e precisam ser testadas com usuários reais.
