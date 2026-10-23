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
  function relationshipLabel(id,s){
    if(id===s.root)return 'Ativo em foco';
    const verbs={CALLS:'chama',READS:'lê',WRITES:'grava em',DERIVES_TO:'origina',ROUTES_TO:'encaminha para',CONTAINS:'contém',USES_TOOL:'usa a ferramenta',HOSTS:'hospeda',HAS_IDENTITY:'tem identidade',USES_MODEL:'usa o modelo',TRAINED_ON:'é treinado com'};
    const edge=s.edgeIds.map(key=>relations[key]).find(r=>r&&((r.source===s.root&&r.target===id)||(r.target===s.root&&r.source===id)));
    if(edge)return `${EGGraph.label(assets[edge.source])} ${verbs[edge.kind]||edge.kind} ${EGGraph.label(assets[edge.target])}`;
    if($('graphScope').value==='impact'&&s.root===result.change.target){
      const path=result.consumers.find(row=>row.consumer===id)?.paths.find(p=>p.length>1&&relations[p[0]]?.source===id&&relations[p.at(-1)]?.target===s.root);
      if(path)return 'Caminho registrado: '+[id,...path.map(key=>relations[key].target)].map(key=>EGGraph.label(assets[key])).join(' → ');
    }
    if(s.custom?.mode==='upstream')return `Recurso a montante do foco · ${distanceLabel(id,s)}`;
    if(s.custom?.mode==='downstream')return `Consumidor a jusante do foco · ${distanceLabel(id,s)}`;
    return s.custom?.mode==='process'?'Processo compartilhado; não comprova dependência':'Sem vínculo direto com o foco neste recorte';
  }
  function addActions(){
    if(!ready)return;const {selected,custom}=EGGraph.snapshot(),a=assets[selected];if(!a)return;
    const meta=$('graphInspector').querySelector('.inspector-meta');
    const actions=document.createElement('section');actions.className='investigate-actions';actions.setAttribute('aria-label','Investigar ativo selecionado');
    actions.innerHTML='<h3>Investigar este ativo</h3>'+Object.entries(captions).map(([mode,label])=>`<button class="secondary" data-investigate="${mode}" aria-pressed="${custom?.root===selected&&custom?.mode===mode}"><span>${mode==='upstream'?'←':mode==='downstream'?'→':'▦'}</span>${label}</button>`).join('');
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
    $('investigationNote').textContent=q?(q.mode==='process'?'Ativos associados aos processos do foco. Associação não comprova dependência.':`Vínculos do catálogo, não uma previsão de falha. ${q.maxDepth===1?'Somente relações diretas.':`Até ${q.maxDepth} níveis.`}${q.hasMore?' Há conexões além deste alcance.':''}`)+(hidden>0?` ${hidden} ativos ocultos pelos filtros.`:''):'Selecione um ativo para destacar suas conexões. A lista de conexões mostra o mesmo recorte; Lista da análise retorna aos consumidores da mudança.';
    $('depthControl').hidden=!q||q.mode==='process';
    $('workspaceEnvironment').textContent=data.provenance?'Fonte em revisão':'Demonstração · dados fictícios';
    $('graphAsGraph').classList.toggle('selected',!list);$('graphAsGraph').setAttribute('aria-pressed',String(!list));
    $('graphToList').classList.toggle('selected',list);$('graphToList').setAttribute('aria-pressed',String(list));
    $('graphViewport').hidden=list;$('graphListPanel').hidden=!list;$('graphNavigation').hidden=list;
    document.querySelector('.graph-legend').hidden=list;
    renderList(s);
  }
  function renderList(s){
    const ids=[...s.ids].sort((a,b)=>a===s.root?-1:b===s.root?1:(s.custom?.distance[a]??0)-(s.custom?.distance[b]??0)||EGGraph.label(assets[a]).localeCompare(EGGraph.label(assets[b]),'pt-BR'));
    $('exploreRows').innerHTML=ids.map(id=>{const a=assets[id];return `<tr data-explore-row="${esc(id)}" class="${id===s.selected?'active-row':''}"><td data-label="Ativo"><button class="text-btn asset-select" data-select-asset="${esc(id)}">${esc(EGGraph.label(a))}</button><small>${esc(KINDS[a.kind])} · ${esc(envLabel(a.environment))}</small></td><td data-label="Relação com o foco">${esc(relationshipLabel(id,s))}</td><td data-label="Responsável / operação">${esc(team(a.owner))}<small>${esc(processNames(a).join(' · ')||'Processo não mapeado')}</small></td><td data-label="Ações"><button class="row-open" data-explore-detail="${esc(id)}">Detalhes</button></td></tr>`;}).join('')||'<tr><td colspan="4" class="empty">Nenhum ativo corresponde aos filtros.</td></tr>';
    $('exploreCount').textContent=`${ids.length} ativos · ${s.edgeIds.length} relações — mesmo recorte do grafo`;
    $('exportContext').disabled=!ids.length;
  }
  function showRepresentation(value){list=value;refresh();if(!value)EGGraph.repaint();emit('representation');}
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
  function initializeInvestigation(){
    if(ready)return;
    ready=true;
    $('graphAsGraph').addEventListener('click',()=>showRepresentation(false));$('graphToList').addEventListener('click',()=>showRepresentation(true));
    $('graphAsGraph').disabled=false;$('graphToList').disabled=false;
    $('investigationDepth').addEventListener('change',()=>{const q=EGGraph.snapshot().custom;if(q)EGGraph.explore(EGExplore.query(data,q.root,q.mode,Number($('investigationDepth').value)));});
    $('exportContext').addEventListener('click',exportContext);
    $('graphInspector').addEventListener('click',e=>{const b=e.target.closest('button');if(b?.dataset.investigate)ask(b.dataset.investigate);if(b?.dataset.reviewSelected)reviewSelected(b.dataset.reviewSelected);});
    $('exploreRows').addEventListener('click',e=>{const b=e.target.closest('button');if(b?.dataset.selectAsset)EGGraph.select(b.dataset.selectAsset);if(b?.dataset.exploreDetail){EGGraph.select(b.dataset.exploreDetail);openDetails(b.dataset.exploreDetail);}});
    $('consumerRows').addEventListener('click',e=>{const b=e.target.closest('[data-return-graph]');if(b){setView('lineage');EGGraph.select(b.dataset.returnGraph);showRepresentation(false);if(!EGGraph.snapshot().ids.includes(b.dataset.returnGraph))EGGraph.focus(b.dataset.returnGraph);}});
    document.querySelector('#aboutDialog .dialog-body').insertAdjacentHTML('beforeend','<p>Os vínculos usados na exploração são os do catálogo sintético; registros antigos e atuais não são reconciliados por essa navegação. “De que depende?” segue recursos usados e origens dos dados. “Quem depende dele?” percorre o sentido inverso. Estrutura e identidade não autorizam acesso. Notas são locais e podem ser apagadas pelo navegador.</p>');
    addActions();refresh();decorateResults();initializeNavigation();
  }
  // Share view state and evidence identifiers; local notes and checks never do.
  let navigationReady=false,restoring=false,navigationTimer=null;
  const routeKeys=['view','change','open','focus','asset','scope','area','technical','mode','depth','expanded','rep','impact','owner','activity','search','sort','inventory','kind','inventoryArea','page','detail','detailKind','evidence'];
  function routeURL(){
    const url=new URL(location.href),s=EGGraph.snapshot();
    for(const key of routeKeys)url.searchParams.delete('eg_'+key);
    const values={view,change:$('changeSelect').value,
      open:result.change.id!==$('changeSelect').value?result.change.id:'',
      focus:s.root!==result.change.target?s.root:'',asset:s.selected!==s.root?s.selected:'',
      scope:$('graphScope').value!=='context'?$('graphScope').value:'',area:$('graphDomain').value,
      technical:$('graphTechnical').checked?'1':'',mode:s.custom?.mode||'',
      depth:[2,4].includes(s.custom?.maxDepth)?String(s.custom.maxDepth):'',expanded:s.expanded.join(','),rep:list?'list':'graph',
      impact:impactFilter,owner:$('ownerFilter').value,activity:$('activityFilter').value,
      search:$('search').value,sort:ascending===null?'':ascending?'asc':'desc',
      inventory:$('inventorySearch').value,kind:$('kindFilter').value,inventoryArea:$('domainFilter').value,
      page:inventoryPage?String(inventoryPage):'',
      detail:$('detailDialog').open?detailContext?.id||'':'',detailKind:$('detailDialog').open?detailContext?.kind||'':'',evidence:$('detailDialog').open?detailContext?.evidence||'':''};
    for(const [key,value] of Object.entries(values))if(value!=='')url.searchParams.set('eg_'+key,value);
    return url;
  }
  function recordRoute(replace=false){
    if(!navigationReady||restoring||!['http:','https:'].includes(location.protocol))return;
    const url=routeURL();if(url.href===location.href)return;
    history[replace?'replaceState':'pushState'](null,'',url.href);
  }
  function scheduleRoute(replace=false){
    if(!navigationReady||restoring)return;
    clearTimeout(navigationTimer);navigationTimer=setTimeout(()=>recordRoute(replace),0);
  }
  function readRoute(){
    const p=new URL(location.href).searchParams,get=key=>(p.get('eg_'+key)||'').slice(0,12000);
    const choice=(key,allowed,fallback)=>allowed.includes(get(key))?get(key):fallback;
    const changes=data.results.map(r=>r.change.id),change=choice('change',changes,changes[0]);
    const open=choice('open',changes,change),opened=data.results.find(r=>r.change.id===open);
    const exists=id=>Object.hasOwn(assets,id),root=exists(get('focus'))?get('focus'):opened.change.target;
    const modes=Object.keys(captions),mode=choice('mode',modes,'');
    const domain=key=>choice(key,data.domains.map(d=>d.id),'');
    const detailKind=choice('detailKind',['asset','consumer','relation'],''),detailId=get('detail');
    const row=detailKind==='consumer'&&change===open?opened.consumers.find(r=>r.consumer===detailId):null;
    const detail=detailKind==='asset'&&exists(detailId)||row||detailKind==='relation'&&Object.hasOwn(relations,detailId)?{kind:detailKind,id:detailId,evidence:''}:null;
    if(detail){const allowed=detail.kind==='relation'?relations[detail.id].evidence_ids:row?.evidence_ids||assets[detail.id]?.evidence_ids||[];if(allowed.includes(get('evidence')))detail.evidence=get('evidence');}
    return {view:choice('view',['lineage','analysis','inventory'],'lineage'),change,open,
      root,selected:exists(get('asset'))?get('asset'):root,
      mode,depth:Number(choice('depth',['1','2','4'],'1')),
      scope:mode?'investigation':choice('scope',['context','impact','all'],p.has('eg_view')?'context':'impact'),domain:domain('area'),
      technical:get('technical')==='1',expanded:[...new Set(get('expanded').split(',').filter(exists))],
      list:choice('rep',['list','graph'],window.matchMedia?.('(max-width: 780px)').matches?'list':'graph')==='list',detail,impact:choice('impact',Object.keys(IMPACT),''),
      owner:choice('owner',[...new Set(opened.consumers.map(r=>r.owner))],''),
      activity:choice('activity',Object.keys(ACTIVITY),''),search:get('search').slice(0,160),
      ascending:get('sort')==='asc'?true:get('sort')==='desc'?false:null,
      inventory:get('inventory').slice(0,160),kind:choice('kind',[...new Set(data.assets.map(a=>a.kind))],''),
      inventoryArea:domain('inventoryArea'),page:Math.max(0,Math.min(Math.ceil(data.assets.length/15)-1,Number.parseInt(get('page'),10)||0))};
  }
  function restoreRoute(){
    clearTimeout(navigationTimer);const s=readRoute();restoring=true;
    try{
      dismissNotice();detailContext=null;
      if($('detailDialog').open)$('detailDialog').close();
      $('changeSelect').value=s.open;meta();openAnalysis();
      $('search').value=s.search;$('ownerFilter').value=s.owner;$('activityFilter').value=s.activity;
      impactFilter=s.impact;ascending=s.ascending;renderConsumers();
      if(s.change!==s.open){$('changeSelect').value=s.change;meta();$('analysisResult').hidden=true;$('notAnalyzed').hidden=false;analysisStatus(true);}
      $('inventorySearch').value=s.inventory;$('kindFilter').value=s.kind;$('domainFilter').value=s.inventoryArea;inventoryPage=s.page;
      $('investigationDepth').value=String(s.depth);setView('lineage');EGGraph.restore(s);showRepresentation(s.list);setView(s.view);
      if(s.detail){
        if(s.detail.kind==='relation')EGGraph.openEdge(s.detail.id);else openDetails(s.detail.id,s.detail.kind==='asset');
        const ev=Array.from($('detailBody').querySelectorAll('[data-evidence-id]')).find(el=>el.dataset.evidenceId===s.detail.evidence);
        if(ev){detailContext.evidence=s.detail.evidence;ev.open=true;ev.querySelector('summary').focus();ev.scrollIntoView?.({block:'nearest'});}
      }
    }finally{restoring=false;}
  }
  function initializeNavigation(){
    if(navigationReady)return;
    navigationReady=true;restoreRoute();recordRoute(true);
    for(const event of ['view','analysis','graphpaint','graphselect','filtered','representation','detail'])document.addEventListener('eg:'+event,()=>scheduleRoute());
    document.addEventListener('change',e=>{if(['changeSelect','inventorySearch','kindFilter','domainFilter'].includes(e.target.id))scheduleRoute();});
    document.addEventListener('input',e=>{if(['search','inventorySearch'].includes(e.target.id))scheduleRoute(true);});
    document.addEventListener('click',e=>{if(e.target.closest('#prevPage,#nextPage'))scheduleRoute();});
    window.addEventListener('popstate',restoreRoute);
    // Commit dismissal before an immediate reload can restore the previous dialog URL.
    const dismissDetailRoute=()=>{detailContext=null;recordRoute();};
    $('closeDetail').addEventListener('click',dismissDetailRoute);
    $('detailDialog').addEventListener('cancel',dismissDetailRoute);
    $('detailDialog').addEventListener('close',()=>{if(!$('detailDialog').open)dismissDetailRoute();});
    $('detailBody').addEventListener('toggle',e=>{
      if(!detailContext||!e.target.matches('[data-evidence-id]'))return;
      if(e.target.open)detailContext.evidence=e.target.dataset.evidenceId;
      else if(detailContext.evidence===e.target.dataset.evidenceId)detailContext.evidence='';
      scheduleRoute();
    },true);
    for(const id of ['copyContextLink','copyDetailLink'])$(id).disabled=!['http:','https:'].includes(location.protocol);
    const copyLink=async()=>{
      clearTimeout(navigationTimer);recordRoute(true);
      let message;
      try{await navigator.clipboard.writeText(location.href);message=$('detailDialog').open?'Link copiado. Reabre este detalhe e a evidência selecionada. Notas continuam locais.':'Link copiado. Ele reabre esta vista, a seleção e os filtros. Notas continuam locais.';}
      catch{message='Copie o endereço na barra do navegador. Notas continuam locais.';}
      if($('detailDialog').open)$('detailShareStatus').textContent=message;else notify(message);
    };
    $('copyContextLink').addEventListener('click',copyLink);$('copyDetailLink').addEventListener('click',copyLink);
    window.EGNavigation={url:()=>routeURL().href};
  }
  document.addEventListener('eg:ready',initializeInvestigation);
  document.addEventListener('eg:graphinspect',addActions);
  document.addEventListener('eg:graphpaint',refresh);
  document.addEventListener('eg:graphselect',()=>{if(ready)markSelected();});
  document.addEventListener('eg:filtered',decorateResults);
  window.EGInvestigation={report:contextReport,showGraph:()=>showRepresentation(false)};
  if(window.EG_READY)initializeInvestigation();
})();
