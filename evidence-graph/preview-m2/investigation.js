'use strict';
/* Shared graph/list workspace. No new risk classification is inferred here. */
(() => {
  let list=false,ready=false;
  const captions={upstream:'De que depende?',downstream:'Quem depende dele?',process:'Qual operação está envolvida?'};
  const pretty=p=>({clientes:'Relacionamento com clientes',pedidos:'Registro de pedidos',precos:'Gestão de preços',catalogo:'Catálogo comercial',chamados:'Atendimento de chamados',conversas:'Conversas de atendimento',conhecimento:'Base de conhecimento',satisfacao:'Satisfação do cliente',reposicao:'Planejamento da reposição',conciliacao:'Conciliação financeira',pagamentos:'Pagamentos',faturas:'Faturamento',previsao:'Previsão de demanda',estoque:'Controle de estoque',expedicao:'Expedição',entregas:'Entregas',cobranca:'Fechamento e cobrança',ingestao:'Ingestão de dados',qualidade:'Qualidade dos dados',indicadores:'Indicadores de negócio',identidade:'Gestão de identidades',configuracao:'Configuração de serviços',auditoria:'Auditoria técnica',notificacoes:'Notificações'}[p]||p);
  const processNames=a=>a.processes.map(id=>pretty(processes[id]?.name||id));
  function ask(mode){const id=EGGraph.snapshot().selected;const q=EGExplore.query(data,id,mode,Number($('investigationDepth').value));EGGraph.explore(q);}
  function distanceLabel(id,s){
    if(id===s.root)return 'Ativo em foco';
    if(!s.custom)return 'No contexto';
    if(s.custom.mode==='process')return 'Processo compartilhado';
    const n=s.custom.distance[id];return n===1?'Direto':n?`Indireto · ${n} níveis`:'No contexto';
  }
  function addActions(){
    if(!ready)return;const {selected,custom}=EGGraph.snapshot(),a=assets[selected];if(!a)return;
    const meta=$('graphInspector').querySelector('.inspector-meta');
    const actions=document.createElement('section');actions.className='investigate-actions';actions.setAttribute('aria-label','Investigar ativo selecionado');
    actions.innerHTML=Object.entries(captions).map(([mode,label])=>`<button class="secondary" data-investigate="${mode}" aria-pressed="${custom?.root===selected&&custom?.mode===mode}"><span>${mode==='upstream'?'←':mode==='downstream'?'→':'▦'}</span>${label}</button>`).join('');
    meta.after(actions);
    const dd=meta.querySelectorAll('dd');if(dd[1])dd[1].textContent=processNames(a).join(' · ')||'Processo não mapeado';
    // A selected consumer is shared even when leaving the graph for the review list.
    if(result.consumers.some(r=>r.consumer===selected)){
      const button=document.createElement('button');button.className='primary inspector-main-action';button.dataset.reviewSelected=selected;button.textContent='Revisar este consumidor →';actions.after(button);
    }
  }
  function refresh(){
    if(!ready)return;
    const s=EGGraph.snapshot(),q=s.custom,a=assets[s.root];
    $('investigationTitle').textContent=q?`${captions[q.mode]} ${EGGraph.label(a)}`:`Explorando: ${$('graphFocusName').textContent}`;
    const hidden=q?q.ids.length-s.ids.length:0;
    $('investigationNote').textContent=q?(q.mode==='process'?'Ativos associados aos processos do foco. Associação não comprova dependência.':`Vínculos do catálogo, não uma previsão de falha. ${q.maxDepth===1?'Somente relações diretas.':`Até ${q.maxDepth} níveis.`}${q.hasMore?' Há conexões além deste alcance.':''}`)+(hidden>0?` ${hidden} ativos ocultos pelos filtros.`:''):'Selecione um ativo e use as três perguntas à direita. Grafo e lista exibem o mesmo recorte.';
    $('depthControl').hidden=!q||q.mode==='process';
    $('workspaceEnvironment').textContent=$('graphScope').value==='all'?'Múltiplos ambientes':envLabel(a?.environment||'prod-demo');
    $('graphAsGraph').classList.toggle('selected',!list);$('graphAsGraph').setAttribute('aria-pressed',String(!list));
    $('graphToList').classList.toggle('selected',list);$('graphToList').setAttribute('aria-pressed',String(list));
    $('graphViewport').hidden=list;$('graphListPanel').hidden=!list;
    document.querySelector('.graph-legend').hidden=list;
    renderList(s);
  }
  function renderList(s){
    const ids=[...s.ids].sort((a,b)=>a===s.root?-1:b===s.root?1:(s.custom?.distance[a]??0)-(s.custom?.distance[b]??0)||EGGraph.label(assets[a]).localeCompare(EGGraph.label(assets[b]),'pt-BR'));
    $('exploreRows').innerHTML=ids.map(id=>{const a=assets[id];return `<tr data-explore-row="${esc(id)}" class="${id===s.selected?'active-row':''}"><td><button class="text-btn asset-select" data-select-asset="${esc(id)}">${esc(EGGraph.label(a))}</button><small>${esc(KINDS[a.kind])} · ${esc(envLabel(a.environment))}</small></td><td>${esc(distanceLabel(id,s))}</td><td>${esc(team(a.owner))}<small>${esc(processNames(a).join(' · ')||'Processo não mapeado')}</small></td><td><button class="row-open" data-explore-detail="${esc(id)}">Detalhes</button></td></tr>`;}).join('')||'<tr><td colspan="4" class="empty">Nenhum ativo corresponde aos filtros.</td></tr>';
    $('exploreCount').textContent=`${ids.length} ativos · ${s.edgeIds.length} relações — mesmo recorte do grafo`;
    $('exportContext').disabled=!ids.length;
  }
  function showRepresentation(value){list=value;refresh();if(!value)EGGraph.repaint();}
  function reviewSelected(id){
    const row=result.consumers.find(r=>r.consumer===id);if(!row)return;
    clear();$('search').value=row.name;renderConsumers();setView('analysis');$('search').focus();
  }
  function contextReport(){
    const s=EGGraph.snapshot();const lines=['# EvidentGraph — investigação de dependências','', '**Grupo Aurora: organização e dados fictícios.**', '',$('investigationTitle').textContent,$('investigationNote').textContent,`Dataset: ${data.dataset_version}. Relógio: ${data.clock}.`,`Área: ${$('graphDomain').value||'todas'}. Colunas/identidades: ${$('graphTechnical').checked?'incluídas':'ocultas'}.`,`Ativos: ${s.ids.length}. Relações: ${s.edgeIds.length}.`,'','| Ativo | Tipo | Relação com o foco | Responsável | Operação |','|---|---|---|---|---|'];
    for(const id of s.ids){const a=assets[id];lines.push(`| ${md(EGGraph.label(a))} | ${KINDS[a.kind]} | ${distanceLabel(id,s)} | ${md(team(a.owner))} | ${md(processNames(a).join('; '))} |`);}
    lines.push('','## Relações do recorte');
    for(const id of s.edgeIds){const r=relations[id];lines.push(`- ${r.source} — ${r.kind} → ${r.target}; evidências: ${r.evidence_ids.join(', ')}`);}
    lines.push('','## Limites','Relações do catálogo não comprovam acesso efetivo, permissão, quebra ou causalidade. Processos são vínculos declarados. A análise de impacto específica permanece limitada aos três cenários preparados.');
    return lines.join('\n')+'\n';
  }
  function exportContext(){const blob=new Blob([contextReport()],{type:'text/markdown;charset=utf-8'}),url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download='EvidentGraph_investigacao.md';link.click();setTimeout(()=>URL.revokeObjectURL(url),1500);notify('Recorte exportado com as relações e limitações.');}
  function markSelected(){const s=EGGraph.snapshot();$('exploreRows').querySelectorAll('[data-explore-row]').forEach(row=>row.classList.toggle('active-row',row.dataset.exploreRow===s.selected));}
  // Add an explicit return to the graph next to each review result.
  function decorateResults(){
    if(!ready)return;
    $('consumerRows').querySelectorAll('[data-detail]').forEach(button=>{
      const id=button.dataset.detail;button.closest('tr').classList.toggle('active-row',id===EGGraph.snapshot().selected);
      const b=document.createElement('button');b.className='row-open in-graph';b.dataset.returnGraph=id;b.textContent='Ver no grafo';button.after(b);
    });
  }
  document.addEventListener('eg:ready',()=>{
    ready=true;
    $('graphAsGraph').addEventListener('click',()=>showRepresentation(false));$('graphToList').addEventListener('click',()=>showRepresentation(true));
    $('investigationDepth').addEventListener('change',()=>{const q=EGGraph.snapshot().custom;if(q)EGGraph.explore(EGExplore.query(data,q.root,q.mode,Number($('investigationDepth').value)));});
    $('exportContext').addEventListener('click',exportContext);
    $('graphInspector').addEventListener('click',e=>{const b=e.target.closest('button');if(b?.dataset.investigate)ask(b.dataset.investigate);if(b?.dataset.reviewSelected)reviewSelected(b.dataset.reviewSelected);});
    $('exploreRows').addEventListener('click',e=>{const b=e.target.closest('button');if(b?.dataset.selectAsset)EGGraph.select(b.dataset.selectAsset);if(b?.dataset.exploreDetail){EGGraph.select(b.dataset.exploreDetail);openDetails(b.dataset.exploreDetail);}});
    $('consumerRows').addEventListener('click',e=>{const b=e.target.closest('[data-return-graph]');if(b){setView('lineage');EGGraph.select(b.dataset.returnGraph);showRepresentation(false);if(!EGGraph.snapshot().ids.includes(b.dataset.returnGraph))EGGraph.focus(b.dataset.returnGraph);}});
    document.querySelector('#aboutDialog .dialog-body').insertAdjacentHTML('beforeend','<p>Os vínculos usados na exploração são os do catálogo sintético; registros antigos e atuais não são reconciliados por essa navegação. “De que depende?” segue recursos usados e origens dos dados. “Quem depende dele?” percorre o sentido inverso. Estrutura e identidade não autorizam acesso. Notas são locais e podem ser apagadas pelo navegador.</p>');
    addActions();refresh();decorateResults();
  });
  document.addEventListener('eg:graphinspect',addActions);
  document.addEventListener('eg:graphpaint',refresh);
  document.addEventListener('eg:graphselect',()=>{if(ready)markSelected();});
  document.addEventListener('eg:filtered',decorateResults);
  window.EGInvestigation={report:contextReport};
})();
