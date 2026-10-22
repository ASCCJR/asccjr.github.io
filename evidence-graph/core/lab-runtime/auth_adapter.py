"""Map an L5 capture to the existing graph/list contract; keep sources separate."""
from collections import Counter
import hashlib
import json
from auth_lab import ACTION, ENVIRONMENT, RESOURCE, analyze

DOMAINS = {'Comercial':'comercial','Atendimento':'atendimento','Financeiro':'financeiro'}


def adapt(raw: bytes) -> dict:
    if len(raw)>5_000_000:
        raise ValueError('Capture exceeds 5 MB')
    run=json.loads(raw);analysis=analyze(run)
    if analysis['removed_fields'] != ['cliente_id']:
        raise ValueError('Viewer limited to cliente_id removal')
    sha=hashlib.sha256(raw).hexdigest();version='auth-view-0.1-'+sha
    api,table='l5-api-clientes','l5-table-customers'
    assets=[];relations=[];evidence=[];rows=[];db_refs=set()
    teams=[{'id':'l5-team-'+v,'domain':v,'name':'Equipe '+k} for k,v in DOMAINS.items()]
    teams.append({'id':'l5-team-plataforma','domain':'plataforma','name':'Equipe Plataforma'})
    def asset(id,name,kind,domain,version='local'):
        assets.append({'id':id,'name':name,'kind':kind,'domain':domain,'owner':'l5-team-'+domain,
            'environment':ENVIRONMENT,'version':version,'processes':[],'criticality':'not_assessed',
            'metadata_origin':'explicit_lab_mapping'})
    def ev(id,family,subject,target,ref,claim,details,ver):
        if not any(e['id']==id for e in evidence):
            evidence.append({'id':id,'family':family,'source':'l5-'+family,'origin_id':sha+':'+ref,
                'reference':'run.json'+ref,'subject':subject,'target':target,
                'subject_version':ver,'target_version':ver,'environment':ENVIRONMENT,
                'collected_at':run['finished_at'],'valid_from':None,'valid_until':None,
                'claim':claim,'details':details})
        return id
    def span_ref(index,subject,target):
        s=run['spans'][index]
        return ev('l5-span-'+s['span_id'],'runtime',subject,target,'#/spans/'+str(index),
                  'access_attempt',s,s['attributes'].get('auth.phase','local'))
    asset(api,'API de clientes','api','plataforma','v1 / v2')
    contract_refs=[ev('l5-openapi-'+v,'code',api,api,'#/openapi/'+v,'api_contract',
                      {'origin':'Contrato OpenAPI obtido por HTTP'},v) for v in ['v1','v2']]
    for i,row in enumerate(analysis['consumers']):
        id='l5-'+row['consumer'];identity=id+'-identity';domain=DOMAINS[row['owner']]
        asset(id,row['name'],'application',domain);asset(identity,'Identidade · '+row['consumer'],'identity',domain)
        config=ev(id+'-config','config',id,api,'#/consumers/'+str(i),'consumer_fields',
                  {'required_fields':run['consumers'][i].get('required_fields'),
                   'origin':'Configuração do cliente de laboratório, não descoberta no código'},'local')
        relations.append({'id':id+'-identity-link','source':id,'target':identity,'kind':'HAS_IDENTITY',
                          'evidence_ids':[config]})
        refs=[config,*contract_refs]
        for v,p in row['phases'].items():
            refs.append(ev(id+'-policy-'+v,'authorization',identity,api,
                '#/phases/'+v+'/policies/'+row['consumer'],'policy_evaluation',
                {'evaluation':p['policy'],'action':ACTION,'resource':RESOURCE,'evaluated_at':run['phases'][v]['at'],
                 'origin':'Avaliação derivada do snapshot local; autoridade limitada ao laboratório'},v))
            for event in p['events']:
                refs += [span_ref(index,id,api) for index in event['span_indices']]
                if event['successful']:
                    db_refs.update(span_ref(index,api,table) for index in event['database_indices'])
        rid=id+'-calls';refs=list(dict.fromkeys(refs))
        relations.append({'id':rid,'source':id,'target':api,'kind':'CALLS','evidence_ids':refs,
                          'meaning':'Caminho configurado; tentativa e sucesso são separados nas evidências'})
        phases=row['phases'];decision=phases['v1']['policy']['decision']
        action=('Revisar a migração do contrato' if row['contract']=='INCOMPATIBILITY'
                else 'Confirmar limites do contrato e ampliar testes')
        if decision=='DENY':action='Revisar a necessidade de acesso; não alterar a regra sem autorização'
        if decision=='INDETERMINATE':action='Restabelecer a fonte de política antes de liberar acesso'
        rows.append({'consumer':id,'name':row['name'],'owner':'l5-team-'+domain,'processes':[],
            'criticality':'not_assessed','impact':row['contract'],
            'activity':'OBSERVED' if phases['v1']['successful_use']=='OBSERVED' else 'UNKNOWN',
            'paths':[[rid]],'evidence_ids':refs,'origin_ids':[],'authorization':decision,
            'field_access':'NOT_EVALUATED','contract_conflict':False,'next_step':action,
            'limitations':['Autorização limitada à ação e ao endpoint desta política local.',
                          'Contrato, permissão e execução são dimensões distintas.',
                          'Processos e criticidade não foram inferidos; captura histórica.'],
            'auth_phases':phases,'lab_regression':phases['v2']['regression']})
    if db_refs:
        asset(table,'customers · SQLite','table','plataforma')
        relations.append({'id':'l5-api-reads','source':api,'target':table,'kind':'READS','evidence_ids':sorted(db_refs)})
    for row in rows:
        row['origin_ids']=sorted({e['origin_id'] for e in evidence if e['id'] in row['evidence_ids']})
    change={'id':'AUTH-001','target':api,'operation':'remove_field','field':'cliente_id',
            'before_version':'v1','after_version':'v2','environment':ENVIRONMENT,
            'window_start':run['started_at'],'window_end':run['finished_at']}
    result={'change':change,'consumers':rows,'truncated':False,'scope_complete':False,
            'dataset_version':version,'clock':run['finished_at'],
            'scope_note':'Política local, tentativa, acesso concluído e contrato são avaliações distintas.',
            'counts':{'consumers':len(rows),'impact':dict(Counter(r['impact'] for r in rows)),
                      'activity':dict(Counter(r['activity'] for r in rows))}}
    limits=['Política local por identidade, ação e recurso; não IAM corporativo ou permissão por coluna.',
            'As identidades usam tokens efêmeros no processo de laboratório, não OAuth/JWT de produção.',
            'O controle foi aplicado na API de laboratório; o HTML é apenas um leitor de evidências.',
            'Não observar chamada não prova ausência de uso. Tentativa negada não é leitura.',
            'Dados fictícios e capturas históricas, sem monitoramento ao vivo ou conexão empresarial.',
            'Hash identifica conteúdo, não autentica telemetria de terceiros.',
            'Requisitos declarados compartilhados com clientes de teste; não é benchmark independente.']
    return {'synthetic':False,'dataset_version':version,'clock':run['finished_at'],'assets':assets,
        'teams':teams,'processes':[],'domains':[{'id':t['domain'],'name':t['name'].removeprefix('Equipe ')} for t in teams],
        'sources':[{'id':'l5-'+f,'family':f} for f in ['config','code','runtime','authorization']],
        'relations':relations,'evidence':evidence,'coverage':[],'results':[result],
        'full_catalog_counts':{'assets':len(assets),'relations':len(relations)},
        'provenance':{'kind':'l5_capture','adapter_version':'0.1','source_sha256':sha,
            'business_data':'synthetic','telemetry':'real_local_execution','started_at':run['started_at'],
            'finished_at':run['finished_at'],'spans_in_capture':len(run['spans']),
            'spans_used':len([e for e in evidence if e['family']=='runtime']),'limitations':limits}}
