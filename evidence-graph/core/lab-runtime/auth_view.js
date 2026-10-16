'use strict';
/* Read-only L5 presentation: policies were enforced by the local API, not this browser. */
(() => {
  const isAuth=()=>data?.provenance?.kind==='l5_capture';
  const labels={ALLOW:'Permitido',DENY:'Negado',INDETERMINATE:'Indeterminado',OBSERVED:'Observado',UNKNOWN:'Não confirmado',NOT_COMPLETED_IN_OBSERVED_ATTEMPT:'Não concluído na tentativa',FAIL_OBSERVED_IN_LAB:'Falhou no teste',PASS_IN_EXECUTED_CHECK:'Passou no teste executado',NOT_VERIFIED:'Não verificado'};
  const text=x=>labels[x]||x;
  const policyBadge=p=>`<span class="badge ${p==='DENY'?'danger':p==='INDETERMINATE'?'warning':'quiet'}">${esc(text(p))}</span>`;
  function panel(r){return `<section class="auth-panel"><h3>Permissão não é execução</h3><div class="detail-grid">${['v1','v2'].map(v=>{const p=r.auth_phases[v];return `<div><small>${v==='v1'?'ANTES · v1':'DEPOIS · v2'}</small><p><strong>Política:</strong> ${policyBadge(p.policy.decision)}</p><p>Tentativa: ${esc(text(p.attempt))}<br>Acesso concluído: ${esc(text(p.successful_use))}<br>Teste do contrato: ${esc(text(p.regression))}</p><small>Motivo: ${esc(p.policy.reason)}</small>${p.events.map(e=>`<p class="small">HTTP ${esc(e.status)} · controle ${esc(e.decision)}<br>Conferência da política: ${esc(e.policy_consistency)}<br><code>${esc(e.trace_id)}</code></p>`).join('')}</div>`;}).join('')}</div><p class="small">Escopo: identidade → customers:read → API de clientes. Não autoriza automaticamente colunas ou outros sistemas.</p></section>`;}
  function decorate(){
    if(!isAuth())return;
    for(const button of $('consumerRows').querySelectorAll('[data-detail]')){
      const r=result.consumers.find(x=>x.consumer===button.dataset.detail);if(!r)continue;
      const cell=button.closest('tr').children[1];
      if(!cell.querySelector('.auth-mini'))cell.insertAdjacentHTML('beforeend',`<div class="auth-mini"><small>POLÍTICA · v1</small>${policyBadge(r.authorization)}<small>TESTE DO CONTRATO · v2</small><span>${esc(text(r.lab_regression))}</span></div>`);
    }
  }
  function inspect(){
    if(!isAuth())return;const r=result.consumers.find(x=>x.consumer===EGGraph.snapshot().selected);
    if(r&&!$('graphInspector').querySelector('.auth-inspect')){const p=r.auth_phases.v1;
      $('graphInspector').querySelector('.inspector-meta').insertAdjacentHTML('beforebegin',`<section class="auth-inspect"><small>POLÍTICA LOCAL · v1</small><p>${policyBadge(p.policy.decision)}</p><p>Tentativa: ${esc(text(p.attempt))}<br>Acesso: ${esc(text(p.successful_use))}</p></section>`);
    }
  }
  function exportAuth(){
    const rows=visibleRows(),p=data.provenance;
    const lines=['# EvidentGraph — revisão de autorização local','',
      '**Aurora Acesso · execução local capturada; dados fictícios; sem conexão ao vivo.**','',
      `Captura SHA-256: ${p.source_sha256}.`,`Período: ${p.started_at} a ${p.finished_at}.`,
      `Fonte: run.json. Exportados: ${rows.length} de ${result.consumers.length} consumidores.`,
      `Busca: ${md($('search').value)}; impacto: ${impactFilter||'todos'}; equipe: ${$('ownerFilter').value||'todas'}; uso: ${$('activityFilter').value||'todos'}.`,'',
      '| Consumidor | Política v1 | Tentativa v1 | Acesso concluído v1 | Contrato | Teste v2 |','|---|---|---|---|---|---|'];
    for(const r of rows){const a=r.auth_phases;lines.push(`| ${md(r.name)} | ${text(a.v1.policy.decision)} | ${text(a.v1.attempt)} | ${text(a.v1.successful_use)} | ${IMPACT[r.impact][0]} | ${text(a.v2.regression)} |`);}
    for(const r of rows){lines.push('',`## ${md(r.name)}`,`Responsável: ${md(team(r.owner))}.`,
      `Verificação manual: ${check(r.consumer).done?'anotada, sem alterar a evidência':'pendente'}.`,
      `Nota: ${md(check(r.consumer).note)||'sem anotação'}.`,`Próximo passo: ${md(r.next_step)}.`);
      for(const v of ['v1','v2']){const a=r.auth_phases[v];lines.push(`- ${v}: política ${text(a.policy.decision)} (${a.policy.reason}); teste ${text(a.regression)}.`);
        for(const e of a.events)lines.push(`- Trace ${e.trace_id}: HTTP ${e.status}; decisão aplicada ${e.decision}; ${e.policy_consistency}.`);}
      for(const id of r.evidence_ids)lines.push(`- ${id}: ${evidences[id].reference}.`);
    }
    lines.push('','## Limites',...p.limitations.map(x=>'- '+x));return lines.join('\n')+'\n';
  }
  document.addEventListener('eg:ready',()=>{
    const select=$('workspaceSource'),source=isAuth()?'access':'aurora';select.value=source;
    const canonical=new URL(location.href);canonical.searchParams.set('source',source);
    try{history.replaceState(null,'',canonical.href);}catch{/* restricted offline origins */}
    const warning=document.createElement('p');warning.id='storageNotice';warning.className='capture-notice';warning.setAttribute('role','status');
    warning.textContent='Notas temporárias: armazenamento indisponível. Exporte antes de recarregar ou trocar a fonte.';
    $('captureNotice').after(warning);warning.hidden=persist;
    const previousStore=store;store=function(id,patch){previousStore(id,patch);warning.hidden=persist;};
    select.addEventListener('change',()=>{
      if(!persist&&Object.values(checks).some(x=>x.note||x.done)&&!confirm('Notas temporárias. Trocar a fonte sem exportar?')){select.value=source;return;}
      const target=new URL(location.href);target.searchParams.set('source',select.value);target.hash='';location.assign(target.href);
    });
    if(!isAuth())return;
    const p=data.provenance;document.title='EvidentGraph · Aurora Acesso';$('contextName').textContent='Aurora Acesso';
    document.querySelector('.company').innerHTML='Aurora Acesso<small>Política e execução local</small>';
    document.querySelector('.catalog-totals small').textContent='nesta captura independente';
    document.querySelector('.footer > span').textContent='EvidentGraph · Aurora Acesso';
    $('datasetLabel').textContent='Captura: '+date(p.finished_at);$('captureNotice').hidden=false;
    $('captureNotice').textContent='Política, tentativa e acesso concluído são respostas separadas. Captura local histórica · '+date(p.finished_at);
    $('graphScope').querySelector('[value="all"]').textContent='Captura completa';
    ACTIVITY.OBSERVED='Acesso concluído antes · v1';ACTIVITY.UNKNOWN='Sem acesso concluído confirmado · v1';
    $('activityFilter').querySelector('[value="UNKNOWN"]').textContent='Sem acesso concluído confirmado';
    $('activityFilter').querySelector('[value="OBSERVED"]').textContent='Acesso concluído antes · v1';
    const details=openDetails;openDetails=function(id,inv=false){details(id,inv);const r=result.consumers.find(x=>x.consumer===id);if(r&&!inv){$('detailBody').insertAdjacentHTML('afterbegin',panel(r));for(const el of $('detailBody').querySelectorAll('.local-note'))if(el.textContent.startsWith('Autorização:'))el.textContent='Autorização avaliada somente nesta política local. Acesso efetivo a campos específicos não é avaliado.';}};
    const original=evidenceMarkup;evidenceMarkup=function(e){if(!['authorization','runtime'].includes(e.family))return original(e);return `<details class="ev"><summary><strong>${e.family==='authorization'?'Política local e avaliação':'Tentativa / execução registrada'}</strong><br><small>${esc(e.id)}</small></summary><pre>${esc(JSON.stringify(e,null,2))}</pre></details>`;};
    document.querySelector('#aboutDialog .dialog-body').innerHTML=`<p><strong>Aurora Acesso</strong> é um laboratório separado do Grupo Aurora. A API aplicou uma política local usando identidades verificadas por tokens efêmeros em memória. O HTML não possui tokens e não aplica controle de acesso.</p><p>Linhas do grafo indicam caminhos configurados ou dependências; não provam acesso bem-sucedido. Abra o consumidor para distinguir política, tentativa e sucesso.</p><p>Fonte: run.json · SHA-256 <code>${esc(p.source_sha256)}</code>.</p><ul>${p.limitations.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`;
    const note=document.querySelector('.bottom-note p');if(note)note.textContent='Contrato incompatível não é acesso negado. Permissão não comprova execução; bloqueio não prova compatibilidade. Escopo de autorização limitado ao endpoint local.';
    report=exportAuth;renderConsumers();inspect();
  });
  document.addEventListener('eg:filtered',decorate);document.addEventListener('eg:graphinspect',inspect);
})();
