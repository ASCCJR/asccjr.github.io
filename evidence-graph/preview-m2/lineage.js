'use strict';
// One graph model; task results remain the bounded Python analysis, not graph heuristics.
(() => {
  const NS='http://www.w3.org/2000/svg';
  const W=208,H=78,DX=246,DY=100,TOP=57;
  const cols={application:0,agent:0,identity:0,api:1,mcp_tool:1,mcp_server:1,service:2,pipeline:2,table:3,column:4,model:4,dashboard:4};
  const headings=['APLICAÇÕES & AGENTES','APIs & FERRAMENTAS','SERVIÇOS & PIPELINES','DADOS','MODELOS & PAINÉIS'];
  const domainNames={comercial:'Comercial',atendimento:'Atendimento',operacoes:'Operações',financeiro:'Financeiro',dados:'Dados',plataforma:'Plataforma'};
  const names={clientes:'Clientes',pedidos:'Pedidos',precos:'Preços',catalogo:'Catálogo',chamados:'Chamados',conhecimento:'Conhecimento',conversas:'Conversas',satisfacao:'Satisfação',reposicao:'Reposição',conciliacao:'Conciliação',pagamentos:'Pagamentos',faturas:'Faturas',previsao:'Previsão',estoque:'Estoque',expedicao:'Expedição',fornecedores:'Fornecedores',qualidade:'Qualidade',acessos:'Acessos',monitoramento:'Monitoramento',custos:'Custos',contratos:'Contratos'};
  const relNames={CALLS:'Chama',READS:'Lê',WRITES:'Grava',DERIVES_TO:'Origina',ROUTES_TO:'Encaminha para',CONTAINS:'Contém',USES_TOOL:'Usa ferramenta',HOSTS:'Hospeda',HAS_IDENTITY:'Tem identidade',USES_MODEL:'Usa modelo',TRAINED_ON:'Treinado com'};
  const symbols={application:'▣',agent:'✧',api:'↗',service:'⊞',pipeline:'⇢',table:'▤',column:'#',model:'◇',dashboard:'▥',mcp_server:'⌘',mcp_tool:'⚒',identity:'○'};
  let custom=null;
  let root,selected,shown=[],links=[],positions={},expanded=new Set(),zoom=1,tx=0,ty=0,graphWidth=0,graphHeight=0,pan=null,ready=false,resizeObserver,activeColumns=[],keyboardNavigation=false;
  const label=a=>{
    if(!a)return '';
    if(a.name!==a.id)return a.name;
    const bits=a.id.split('-'),tail=bits.slice(2).join(' '),topic=names[bits[2]]||tail||domainNames[a.domain];
    if(a.kind==='table')return (bits.at(-1)==='raw'?'Bruto · ':'Tratado · ')+topic;
    if(a.kind==='column'){const layer=a.id.includes('-raw.')?'Bruto':a.id.includes('-curated.')?'Tratado':'';const field=a.id.split('.').at(-1);return `${layer?layer+' · ':''}${topic.replace(/ (raw|curated)\.[^.]+$/,'')}.${field}`;}
    if(['service','pipeline','api'].includes(a.kind))return `${{service:'Serviço',pipeline:'Pipeline',api:'API'}[a.kind]} · ${topic}`;
    return ({agent:'Agente',model:'Modelo',dashboard:'Painel',application:'Portal',mcp_tool:'Ferramenta',mcp_server:'Servidor MCP',identity:'Identidade'}[a.kind]||'Ativo')+' · '+(domainNames[a.domain]||a.domain)+(bits[2]?` ${names[bits[2]]||bits[2]}`:'');
  };
  function svgEl(tag,attrs={},text){const e=document.createElementNS(NS,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v));if(text!==undefined)e.textContent=text;return e;}
  function addText(g,x,y,text,cls){const t=svgEl('text',{x,y,class:cls},text);g.appendChild(t);return t;}
  function short(text,n=24){return text.length>n?text.slice(0,n-1)+'…':text;}
  function nameLines(text,measure){
    const limit=W-22;if(measure(text)<=limit)return [text];
    let cut=text.lastIndexOf(' ');
    while(cut>0&&measure(text.slice(0,cut))>limit)cut=text.lastIndexOf(' ',cut-1);
    if(cut<=0){cut=text.length;while(cut>1&&measure(text.slice(0,cut))>limit)cut--;}
    const rest=text.slice(cut).trim();let second=rest;
    if(measure(second)>limit){let length=second.length;while(length>1&&measure(second.slice(0,length)+'…')>limit)length--;second=second.slice(0,length)+'…';}
    return [text.slice(0,cut),second];
  }
  function neighbors(ids){const out=new Set(ids);for(const r of data.relations)if(ids.has(r.source)||ids.has(r.target)){out.add(r.source);out.add(r.target);}return out;}
  function visibleSet(){
    let ids;
    if(custom)ids=new Set(custom.ids);
    else if($('graphScope').value==='all')ids=new Set(data.assets.map(a=>a.id));
    else if($('graphScope').value==='impact'){
      ids=new Set([result.change.target]);for(const row of visibleRows())for(const p of row.paths)for(const id of p){const r=relations[id];ids.add(r.source);ids.add(r.target);}
    }else{
      ids=neighbors(neighbors(new Set([root])));
      // Include dashboards that read this neighborhood: actual links only, no invented edges.
      for(const r of data.relations)if(r.kind==='READS'&&ids.has(r.target)&&assets[r.source].kind==='dashboard')ids.add(r.source);
    }
    for(const id of expanded)for(const n of neighbors(new Set([id])))ids.add(n);
    const d=$('graphDomain').value,technical=$('graphTechnical').checked;
    return new Set([...ids].filter(id=>assets[id]&&(!d||assets[id].domain===d)&&(technical||!['column','identity'].includes(assets[id].kind))));
  }
  function layout(){
    const buckets=Array.from({length:5},()=>[]);
    for(const a of shown)buckets[cols[a.kind]??2].push(a);
    for(const b of buckets)b.sort((a,b)=>a.domain.localeCompare(b.domain)||label(a).localeCompare(label(b),'pt-BR'));
    // Deterministic barycentric ordering reduces unnecessary crossings between adjacent columns.
    for(let pass=0;pass<3;pass++){
      const ranks={};buckets.forEach(b=>b.forEach((a,i)=>ranks[a.id]=i));
      buckets.forEach((b,c)=>{
        const mean=a=>{const ns=links.filter(r=>r.source===a.id||r.target===a.id).map(r=>r.source===a.id?r.target:r.source).filter(id=>(cols[assets[id].kind]??2)!==c);return ns.length?ns.reduce((s,id)=>s+(ranks[id]??0),0)/ns.length:ranks[a.id];};
        b.sort((a,b)=>mean(a)-mean(b)||a.id.localeCompare(b.id));
      });
    }
    const longest=Math.max(1,...buckets.map(b=>b.length));
    activeColumns=buckets.map((b,i)=>b.length?i:-1).filter(i=>i>=0);
    positions={};activeColumns.forEach((c,column)=>buckets[c].forEach((a,i)=>positions[a.id]={x:24+column*DX,y:TOP+i*DY+(longest-buckets[c].length)*Math.min(18,DY/2)}));
    graphWidth=48+Math.max(0,activeColumns.length-1)*DX+W;graphHeight=TOP+longest*DY+20;
  }
  function route(r){
    const a=positions[r.source],b=positions[r.target];
    if(a.x===b.x){const x=a.x+W,y1=a.y+H/2,y2=b.y+H/2,off=26;return `M${x},${y1} C${x+off},${y1} ${x+off},${y2} ${x},${y2}`;}
    const right=b.x>a.x,x1=a.x+(right?W:0),x2=b.x+(right?0:W),y1=a.y+H/2,y2=b.y+H/2,curve=Math.max(30,Math.abs(x2-x1)*.5),s=right?1:-1;
    return `M${x1},${y1} C${x1+s*curve},${y1} ${x2-s*curve},${y2} ${x2},${y2}`;
  }
  function edgeType(r){return r.kind==='DERIVES_TO'?'lineage':['CONTAINS','HAS_IDENTITY','HOSTS'].includes(r.kind)?'structure':'dependency';}
  function paint(){
    if(!ready||view!=='lineage')return;
    const ids=visibleSet();shown=data.assets.filter(a=>ids.has(a.id));links=data.relations.filter(r=>ids.has(r.source)&&ids.has(r.target)&&(!custom||custom.edgeIds.includes(r.id)));layout();
    const svg=$('lineageSvg');svg.replaceChildren();
    const defs=svgEl('defs');for(const [id,color] of [['dependency','#a1b0bf'],['lineage','#4e917d'],['structure','#b4bec9'],['selected','#3869b0']]){const m=svgEl('marker',{id:'arr-'+id,viewBox:'0 0 10 10',refX:9,refY:5,markerWidth:6,markerHeight:6,orient:'auto-start-reverse',markerUnits:'strokeWidth'});m.appendChild(svgEl('path',{d:'M1 1 L9 5 L1 9 z',fill:color}));defs.appendChild(m);}svg.appendChild(defs);
    const scene=svgEl('g',{id:'graphScene'});svg.appendChild(scene);
    const context=typeof window.CanvasRenderingContext2D==='function'?document.createElement('canvas').getContext('2d'):null;
    if(context){const probe=addText(scene,0,0,'','node-name');context.font=getComputedStyle(probe).font;probe.remove();}
    const measure=text=>context?context.measureText(text).width:text.length*8;
    activeColumns.forEach((column,i)=>{scene.appendChild(svgEl('rect',{x:12+i*DX,y:14,width:DX-10,height:graphHeight-14,rx:10,class:'graph-lane'}));addText(scene,24+i*DX,35,column===4&&shown.some(a=>a.kind==='column')?'CAMPOS, MODELOS & PAINÉIS':headings[column],'lane-title');});
    for(const r of links){const type=edgeType(r),g=svgEl('g',{'data-edge':r.id,class:'graph-edge-group',role:'button',tabindex:-1,'aria-label':`${label(assets[r.source])} ${relNames[r.kind]||r.kind} ${label(assets[r.target])}`});g.appendChild(svgEl('path',{d:route(r),class:`graph-edge ${type}`,'marker-end':`url(#arr-${type})`}));g.appendChild(svgEl('path',{d:route(r),class:'edge-hit'}));g.appendChild(svgEl('title',{},`${label(assets[r.source])} → ${label(assets[r.target])} · ${relNames[r.kind]||r.kind}`));scene.appendChild(g);}
    const consumers=new Map(result.consumers.map(r=>[r.consumer,r]));
    for(const a of shown){const pos=positions[a.id],row=consumers.get(a.id),isTarget=a.id===result.change.target,g=svgEl('g',{transform:`translate(${pos.x},${pos.y})`,class:`graph-node kind-${a.kind}${isTarget?' change-target':''}`,role:'button',tabindex:0,'aria-label':`${label(a)}, ${KINDS[a.kind]}, ${domainNames[a.domain]}`, 'data-node':a.id});
      g.appendChild(svgEl('rect',{width:W,height:H,rx:7,class:'node-card'}));g.appendChild(svgEl('rect',{x:0,y:10,width:3,height:H-20,rx:1.5,class:'node-stripe'}));g.appendChild(svgEl('rect',{x:11,y:11,width:25,height:25,rx:5,class:'node-icon-bg'}));addText(g,23.5,28,symbols[a.kind]||'◇','node-symbol');addText(g,44,23,short(KINDS[a.kind].toUpperCase(),23),'node-kind');const lines=nameLines(label(a),measure);
      addText(g,11,lines.length>1?46:51,lines[0],'node-name');
      if(lines.length>1)addText(g,11,64,lines[1],'node-name');
      if(row){g.appendChild(svgEl('circle',{cx:W-12,cy:16,r:4,class:'node-status '+IMPACT[row.impact][1]}));}
      g.appendChild(svgEl('title',{},`${label(a)}\n${a.id}\n${team(a.owner)}${row?'\n'+IMPACT[row.impact][0]:''}`));scene.appendChild(g);
    }
    $('graphFocusName').textContent=custom?label(assets[custom.root]):$('graphScope').value==='all'?'Visão corporativa':$('graphScope').value==='impact'?'Caminhos da mudança':label(assets[root]);
    $('graphVisibleCount').textContent=`${shown.length} ativos · ${links.length} relações neste recorte`;
    $('graphCatalogTotal').textContent=`${data.assets.length} ativos · ${data.relations.length} relações`;
    $('graphEmpty').hidden=shown.length>0;
    readable();highlight();inspector();emit('graphpaint');
  }
  function viewportState(){
    const v=$('graphViewport'),boxes=shown.map(a=>{const p=positions[a.id];return {x:p.x*zoom+tx,y:p.y*zoom+ty,right:(p.x+W)*zoom+tx,bottom:(p.y+H)*zoom+ty};});
    return {width:v.clientWidth,height:v.clientHeight,whole:boxes.filter(b=>b.x>=0&&b.y>=0&&b.right<=v.clientWidth&&b.bottom<=v.clientHeight).length,
      left:boxes.some(b=>b.x<0),right:boxes.some(b=>b.right>v.clientWidth),up:boxes.some(b=>b.y<0),down:boxes.some(b=>b.bottom>v.clientHeight)};
  }
  function transform(){const g=$('graphScene');if(g)g.setAttribute('transform',`translate(${tx},${ty}) scale(${zoom})`);$('graphZoomLabel').textContent=Math.round(zoom*100)+'%';
    const s=viewportState();$('graphViewportStatus').textContent=s.whole===shown.length?`${shown.length} ativos inteiros na área visível.`:`${s.whole} de ${shown.length} ativos inteiros na área visível. Use as setas, Ajustar tudo ou Lista de conexões para ver o restante.`;
    $('graphPanControls').querySelectorAll('[data-pan]').forEach(b=>b.disabled=!s[b.dataset.pan]);
  }
  function moveMap(direction){const s=viewportState();if(!s[direction])return;if(direction==='left')tx+=s.width*.65;if(direction==='right')tx-=s.width*.65;if(direction==='up')ty+=s.height*.65;if(direction==='down')ty-=s.height*.65;transform();}
  function fit(){const v=$('graphViewport');zoom=Math.max(.16,Math.min(1.15,(v.clientWidth-32)/graphWidth,(v.clientHeight-28)/graphHeight));tx=(v.clientWidth-graphWidth*zoom)/2;ty=Math.max(12,(v.clientHeight-graphHeight*zoom)/2);transform();}
  function readable(){
    const v=$('graphViewport'),p=positions[selected]||positions[root];zoom=1;
    tx=p?v.clientWidth/2-(p.x+W/2):16;
    ty=p?v.clientHeight/2-(p.y+H/2):16;
    tx=Math.min(16,Math.max(v.clientWidth-graphWidth-16,tx));
    ty=Math.min(16,Math.max(v.clientHeight-graphHeight-16,ty));transform();
  }
  function zoomAt(factor,cx,cy){const v=$('graphViewport');cx=cx??v.clientWidth/2;cy=cy??v.clientHeight/2;const next=Math.max(.12,Math.min(2.8,zoom*factor));tx=cx-(cx-tx)*next/zoom;ty=cy-(cy-ty)*next/zoom;zoom=next;transform();}
  function highlight(){
    const row=result.consumers.find(r=>r.consumer===selected),edgeIds=new Set(row?row.paths.flat():[]),nodeIds=new Set([selected]);
    if(!row)for(const r of links)if(r.source===selected||r.target===selected)edgeIds.add(r.id);
    $('lineageSvg').classList.toggle('has-highlight',edgeIds.size>0);
    for(const id of edgeIds){const r=relations[id];if(r){nodeIds.add(r.source);nodeIds.add(r.target);}}
    $('lineageSvg').querySelectorAll('[data-node]').forEach(n=>{n.classList.toggle('selected',n.dataset.node===selected);n.classList.toggle('path-node',nodeIds.has(n.dataset.node));});
    $('lineageSvg').querySelectorAll('[data-edge]').forEach(g=>{const active=edgeIds.has(g.dataset.edge);g.classList.toggle('edge-selected',active);const r=relations[g.dataset.edge];g.firstElementChild.setAttribute('marker-end',`url(#arr-${active?'selected':edgeType(r)})`);});
  }
  function inspector(){
    const a=assets[selected];if(!a)return;const row=result.consumers.find(r=>r.consumer===a.id),matches=data.results.filter(r=>r.change.target===a.id),total=data.relations.filter(r=>r.source===a.id||r.target===a.id).length;
    let html=`<div class="inspector-overline">ATIVO SELECIONADO</div><div class="inspector-title"><span>${symbols[a.kind]||'◇'}</span><h2>${esc(label(a))}</h2></div><p class="inspector-type">${esc(KINDS[a.kind])} · ${esc(domainNames[a.domain])}</p><dl class="inspector-meta"><dt>Responsável</dt><dd>${esc(team(a.owner))}</dd><dt>Processo</dt><dd>${esc(proc(a.processes))}</dd><dt>Ambiente</dt><dd>${esc(envLabel(a.environment))} · v${esc(a.version)}</dd></dl>`;
    if(row)html+=`<div class="inspector-impact"><span class="inspector-overline">NESTA MUDANÇA</span>${badge(row)}<p>${esc(consumerReason(row))}</p><strong>Próximo passo</strong><p>${esc(row.next_step)}</p></div>`;
    else if(a.id===result.change.target)html+=`<div class="inspector-impact"><span class="inspector-overline">${esc(result.change.id)}</span><strong>${esc(SCENARIOS[result.change.id])}</strong><p>${result.consumers.length} consumidores na revisão. Selecione um para destacar seu caminho.</p></div>`;
    html+=`<div class="inspector-actions"><button class="secondary" data-inspect="${esc(a.id)}">Ver detalhes e evidências</button><button class="text-btn" data-expand="${esc(a.id)}">Expandir conexões (${total})</button><button class="text-btn" data-center="${esc(a.id)}">Focar este ativo</button></div>`;
    if(matches.length)html+=`<button class="primary inspector-main-action" data-review="${esc(matches[0].change.id)}">Revisar impacto →</button>`;
    if(a.id===result.change.target)html+='<div class="inspector-consumers"><h3>Consumidores em análise</h3>'+visibleRows().map(r=>`<button data-select-node="${esc(r.consumer)}"><i class="state-dot ${IMPACT[r.impact][1]}"></i><span>${esc(r.name)}<small>${esc(IMPACT[r.impact][0])}</small></span><b>↗</b></button>`).join('')+'</div>';
    if(!positions[selected])html+='<p class="local-note">O ativo selecionado está fora deste recorte. Use “Focar este ativo” para localizá-lo.</p>';
    const adjacent=links.filter(r=>r.source===a.id||r.target===a.id);
    if(adjacent.length)html+='<details class="inspector-connections"><summary>Conexões com evidências ('+adjacent.length+')</summary>'+adjacent.map(r=>`<button class="text-btn" data-relation="${esc(r.id)}">${esc(label(assets[r.source]))} ${esc(relNames[r.kind]||r.kind).toLowerCase()} ${esc(label(assets[r.target]))}</button>`).join('')+'</details>';
    html+='<p class="inspector-hint">Clique em um nó para destacar suas conexões. Duplo clique para abrir sua vizinhança.</p>';
    $('graphInspector').innerHTML=html;emit('graphinspect');
  }
  function select(id){if(!assets[id])return;selected=id;highlight();inspector();emit('graphselect');}
  function focus(id){if(!assets[id])return;custom=null;root=id;selected=id;expanded.clear();$('graphScope').value='context';$('graphDomain').value='';if(['column','identity'].includes(assets[id].kind))$('graphTechnical').checked=true;setView('lineage');paint();}
  function openEdge(id){const r=relations[id];if(!r)return;$('detailTitle').textContent=relNames[r.kind]||r.kind;$('detailKind').textContent='RELAÇÃO';$('detailBody').innerHTML=`<div class="path"><span>${esc(label(assets[r.source]))}</span><em>↓ ${esc(r.kind)}</em><span>${esc(label(assets[r.target]))}</span></div><h3>Evidências de origem</h3>${r.evidence_ids.map(id=>evidences[id]).filter(Boolean).map(evidenceMarkup).join('')}<p class="local-note">A relação descreve o vínculo indicado, não comprova por si só uma execução, permissão ou falha.</p>`;detailContext={kind:'relation',id,evidence:''};$('detailShareStatus').textContent='';$('detailDialog').showModal();$('closeDetail').focus();emit('detail');}
  function currentAnalysis(id){$('changeSelect').value=id;meta();openAnalysis();$('graphChange').value=id;}
  // Explicit bridge: selection and filtered IDs are shared by the two representations.
  window.EGGraph={
    label,select,focus,openEdge,
    snapshot:()=>({root,selected,custom,expanded:[...expanded],ids:shown.map(a=>a.id),edgeIds:links.map(r=>r.id)}),
    restore:state=>{
      root=Object.hasOwn(assets,state.root)?state.root:result.change.target;selected=Object.hasOwn(assets,state.selected)?state.selected:root;
      expanded=new Set((state.expanded||[]).filter(id=>Object.hasOwn(assets,id)));
      custom=state.mode?EGExplore.query(data,root,state.mode,state.depth):null;
      $('graphScope').value=custom?'investigation':state.scope;$('graphDomain').value=state.domain;
      $('graphTechnical').checked=state.technical;paint();
    },
    explore:(query)=>{custom=query;root=selected=query.root;expanded.clear();$('graphDomain').value='';$('graphScope').value='investigation';setView('lineage');paint();},
    repaint:paint
  };
  function initializeGraph(){
    if(ready)return;
    ready=true;root=selected=result.change.target;
    $('graphChange').innerHTML=$('changeSelect').innerHTML;
    $('graphDomain').innerHTML+=data.domains.map(d=>`<option value="${esc(d.id)}">${esc(domainNames[d.id]||d.name)}</option>`).join('');
    $('graphAssets').innerHTML=data.assets.map(a=>`<option value="${esc(a.id)}">${esc(label(a))}</option>`).join('');
    $('graphChange').addEventListener('change',()=>currentAnalysis($('graphChange').value));
    $('graphScope').addEventListener('change',()=>{custom=null;expanded.clear();if($('graphScope').value==='all')$('graphTechnical').checked=true;paint();});
    for(const id of ['graphDomain','graphTechnical'])$(id).addEventListener('change',paint);
    $('graphReset').addEventListener('click',()=>focus(result.change.target));
    $('graphReview').addEventListener('click',()=>setView('analysis'));
    // Workspace tabs are managed by investigation.js; analysis remains a separate task.
    $('analysisToGraph').addEventListener('click',()=>{custom=null;root=selected=result.change.target;expanded.clear();$('graphScope').value='impact';$('graphDomain').value='';setView('lineage');window.EGInvestigation?.showGraph();});
    $('analysisToGraph').disabled=$('analysisResult').hidden;
    $('graphReview').disabled=false;
    $('graphZoomIn').addEventListener('click',()=>zoomAt(1.25));$('graphZoomOut').addEventListener('click',()=>zoomAt(.8));$('graphFit').addEventListener('click',fit);$('graphReadable').addEventListener('click',readable);
    $('graphFocusSelected').addEventListener('click',()=>{if(positions[selected])readable();else focus(selected);});
    $('graphPanControls').addEventListener('click',e=>{const b=e.target.closest('[data-pan]');if(b)moveMap(b.dataset.pan);});
    $('graphViewport').addEventListener('keydown',e=>{const direction={ArrowLeft:'left',ArrowRight:'right',ArrowUp:'up',ArrowDown:'down'}[e.key];if(e.target===$('graphViewport')&&direction){e.preventDefault();moveMap(direction);}});
    const find=()=>{const q=norm($('graphSearch').value);const a=assets[$('graphSearch').value]||data.assets.find(a=>norm(label(a))===q)||data.assets.find(a=>norm(label(a)+' '+a.id).includes(q));if(!q)return;if(a)focus(a.id);else notify('Nenhum ativo encontrado.');};
    $('graphFind').addEventListener('click',find);$('graphSearch').addEventListener('keydown',e=>{if(e.key==='Enter')find();});
    $('lineageSvg').addEventListener('click',e=>{const n=e.target.closest('[data-node]'),r=e.target.closest('[data-edge]');if(n)select(n.dataset.node);else if(r)openEdge(r.dataset.edge);});
    $('lineageSvg').addEventListener('dblclick',e=>{const n=e.target.closest('[data-node]');if(n)focus(n.dataset.node);});
    $('lineageSvg').addEventListener('keydown',e=>{const n=e.target.closest('[data-node]');if(n&&['Enter',' '].includes(e.key)){e.preventDefault();select(n.dataset.node);}});
    $('graphInspector').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;if(b.dataset.relation){openEdge(b.dataset.relation);return;}if(b.dataset.inspect)openDetails(b.dataset.inspect,!result.consumers.some(r=>r.consumer===b.dataset.inspect));if(b.dataset.expand){custom=null;$('graphScope').value='context';expanded.add(b.dataset.expand);paint();}if(b.dataset.center)focus(b.dataset.center);if(b.dataset.selectNode)select(b.dataset.selectNode);if(b.dataset.review){currentAnalysis(b.dataset.review);setView('analysis');}});
    $('detailBody').addEventListener('click',e=>{const b=e.target.closest('[data-map]');if(b){$('detailDialog').close();focus(b.dataset.map);}});
    const vp=$('graphViewport');vp.addEventListener('pointerdown',e=>{if(e.button!==0||e.target.closest('[data-node],[data-edge],button'))return;pan={x:e.clientX,y:e.clientY,tx,ty};vp.setPointerCapture(e.pointerId);vp.classList.add('panning');});vp.addEventListener('pointermove',e=>{if(!pan)return;tx=pan.tx+e.clientX-pan.x;ty=pan.ty+e.clientY-pan.y;transform();});const end=()=>{pan=null;vp.classList.remove('panning');};vp.addEventListener('pointerup',end);vp.addEventListener('pointercancel',end);
    vp.addEventListener('wheel',e=>{if(e.ctrlKey||e.metaKey){e.preventDefault();const b=vp.getBoundingClientRect();zoomAt(e.deltaY>0?.9:1.1,e.clientX-b.left,e.clientY-b.top);}}, {passive:false});
    document.addEventListener('pointerdown',()=>{keyboardNavigation=false;},true);
    document.addEventListener('keydown',e=>{if(e.key==='Tab')keyboardNavigation=true;},true);
    $('lineageSvg').addEventListener('focusin',e=>{const node=e.target.closest('[data-node]');if(!node||!keyboardNavigation)return;const p=positions[node.dataset.node],v=$('graphViewport');if(p){tx=v.clientWidth/2-(p.x+W/2)*zoom;ty=v.clientHeight/2-(p.y+H/2)*zoom;transform();}});
    resizeObserver=new ResizeObserver(()=>{if(view==='lineage')readable();});resizeObserver.observe(vp);
    setView('lineage');
  }
  document.addEventListener('eg:ready',initializeGraph);
  document.addEventListener('eg:view',()=>{if(ready&&view==='lineage')paint();});
  document.addEventListener('eg:analysis',()=>{if(!ready)return;custom=null;root=selected=result.change.target;expanded.clear();$('graphChange').value=result.change.id;paint();});
  document.addEventListener('eg:filtered',()=>{if(ready)paint();});
  // Register dependent listeners before catching up with an earlier eg:ready.
  if(window.EG_READY)initializeGraph();
})();
