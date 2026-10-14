'use strict';
/* Catalog exploration, not impact/IAM evaluation. Kept pure for Node tests. */
(function (target) {
  const forward = new Set(['CALLS','READS','USES_TOOL','ROUTES_TO','USES_MODEL','TRAINED_ON']);
  const inverse = new Set(['WRITES','DERIVES_TO']);
  function query(catalog, root, mode, maxDepth=1) {
    const assets = Object.fromEntries(catalog.assets.map(a=>[a.id,a]));
    if (!assets[root]) throw new Error('Ativo não encontrado');
    if (!['upstream','downstream','process'].includes(mode)) throw new Error('Consulta inválida');
    if (![1,2,4].includes(maxDepth)) throw new Error('Profundidade inválida');
    const env=assets[root].environment, nodes=new Set([root]), edges=new Set(), distance={[root]:0};
    const valid=catalog.relations.filter(r=>assets[r.source]?.environment===env && assets[r.target]?.environment===env);
    if (mode==='process') {
      const processes=new Set(assets[root].processes);
      for (const a of catalog.assets) if(a.environment===env && a.processes.some(p=>processes.has(p))) {nodes.add(a.id);distance[a.id]=a.id===root?0:null;}
      for (const r of valid) if(nodes.has(r.source)&&nodes.has(r.target))edges.add(r.id);
      return {root,mode,maxDepth,ids:[...nodes],edgeIds:[...edges],distance,hasMore:false};
    }
    const adjacency={};
    for(const r of valid){
      let consumer,provider;
      if(forward.has(r.kind)){consumer=r.source;provider=r.target;}
      else if(inverse.has(r.kind)){consumer=r.target;provider=r.source;}
      else continue; // CONTAINS/HOSTS/HAS_IDENTITY are context, not dataflow/calls.
      const from=mode==='upstream'?consumer:provider,to=mode==='upstream'?provider:consumer;
      (adjacency[from]??=[]).push({to,edge:r.id});
    }
    const queue=[root];
    for(let i=0;i<queue.length;i++){
      const id=queue[i];if(distance[id]>=maxDepth)continue;
      for(const {to,edge} of adjacency[id]||[]){edges.add(edge);if(!nodes.has(to)){nodes.add(to);distance[to]=distance[id]+1;queue.push(to);}}
    }
    const hasMore=[...nodes].some(id=>distance[id]===maxDepth && (adjacency[id]||[]).some(r=>!nodes.has(r.to)));
    return {root,mode,maxDepth,ids:[...nodes],edgeIds:[...edges],distance,hasMore};
  }
  target.EGExplore={query};
  if(typeof module!=='undefined')module.exports={query};
})(globalThis);
