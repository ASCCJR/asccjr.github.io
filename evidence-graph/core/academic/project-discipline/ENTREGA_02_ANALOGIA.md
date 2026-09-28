# Entrega 2 — Analogia

**Disciplina:** Empreendedorismo / Projetos  
**Status:** rascunho para revisão do grupo  
**Projetos do grupo:** ParkAI e EvidentGraph

---

## Método

A analogia foi construída em três passos:

1. identificar **mecanismos** do domínio de origem;
2. transformar os mecanismos em **princípios gerais**;
3. transferir os princípios para o projeto.

A intenção não é copiar a aparência do outro domínio, mas entender **por que algo funciona lá e como esse mecanismo pode funcionar aqui**.

---

# 1. ParkAI — Feira livre × estacionamento

## Domínio de origem: feira livre

Uma feira livre possui mecanismos interessantes para lidar com demanda variável e produtos que perdem valor com o tempo.

| Mecanismo da feira | Princípio geral | Aplicação no ParkAI |
|---|---|---|
| **Xepa:** preços caem no fim da feira para evitar perda de mercadoria | Um recurso que perderá valor pode ter preço ajustado para aumentar a chance de uso | Uma vaga vazia em um período de baixa demanda não pode ser “guardada” para outro dia; reduzir a tarifa pode ser melhor do que deixá-la ociosa |
| **Pregão:** o feirante anuncia ativamente uma oferta | Uma mudança de preço só gera comportamento se for comunicada no momento certo | ParkAI pode notificar motorista por app, WhatsApp ou outro canal quando houver vagas ociosas e preço reduzido |
| **Relação com fregueses recorrentes** | Conhecer padrões de uso permite personalizar a oferta | Ofertas podem considerar horário, localização e padrão de uso do motorista |
| **Barracas competem pela atenção em um mesmo espaço** | Informação clara e comparação reduzem fricção na escolha | O motorista pode comparar disponibilidade, distância e tarifa antes de decidir onde estacionar |

## Ideia transferida

### “Xepa digital de capacidade ociosa”

O ParkAI pode tratar a vaga de estacionamento como um **recurso perecível**: quando um período termina, a capacidade não utilizada daquele horário desaparece.

A analogia sugere usar precificação e comunicação em tempo real para transformar capacidade que seria perdida em uma oportunidade de receita.

## Cuidado

A analogia gera uma hipótese de produto. Ela não prova que consumidores aceitarão preços dinâmicos nem que o modelo aumentará receita. Isso precisa ser testado.

---

# 2. EvidentGraph — Controle de tráfego aéreo × arquitetura digital

## Domínio de origem: controle de tráfego aéreo

O controle de tráfego aéreo precisa distinguir entre:

- o trajeto planejado;
- o que foi autorizado;
- o que está efetivamente acontecendo;
- desvios e incidentes.

Essa estrutura é semelhante ao problema que o EvidentGraph investiga.

| Mecanismo do controle aéreo | Princípio geral | Aplicação no EvidentGraph |
|---|---|---|
| **Plano de voo** descreve a rota esperada | Registrar o comportamento planejado/declarado | Configuração, catálogo, contratos e OpenAPI descrevem dependências esperadas |
| **Torre/controle autoriza o uso de um espaço** | Possibilidade técnica não significa permissão | IAM, scopes, RBAC e políticas dizem se um caminho é autorizado |
| **Radar** mostra onde o avião realmente está | Observar comportamento real, não apenas o planejado | OpenTelemetry, gateway traces e logs mostram dependências observadas |
| **Desvio entre plano e radar** gera atenção | Discordância entre esperado e observado é informação | Runtime pode revelar uma hidden dependency ausente do catálogo ou código |
| **Caixa-preta e registros** ajudam a reconstruir eventos | Evidência histórica aumenta explicabilidade | Provenance e histórico podem apoiar investigação de incidentes e mudanças |

## Ideia transferida

### “Torre de controle da arquitetura”

O EvidentGraph pode ser entendido como uma camada que compara três estados:

```text
O que deveria acontecer
        ↓
O que está autorizado
        ↓
O que realmente aconteceu
```

A contribuição não seria apenas desenhar conexões, mas tornar os **desvios entre esses estados** visíveis e investigáveis.

## Insight gerado pela analogia

A analogia reforça que uma dependência não deveria ser representada apenas como:

```text
A → B
```

Ela pode precisar carregar evidências diferentes:

```text
DECLARADO    sim/não
AUTORIZADO   sim/não
OBSERVADO    sim/não
LINEAGE      sim/não
```

O conflito entre essas evidências pode ser tão importante quanto a própria conexão.
