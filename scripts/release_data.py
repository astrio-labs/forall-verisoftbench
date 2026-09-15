"""Load and validate the deliberately narrow public metadata schemas."""
from pathlib import Path
from collections import Counter
from decimal import Decimal
import csv
import json
import re

ROOT = Path(__file__).resolve().parent.parent
CONFIG_COLUMNS = ['configuration_id','system','model','effort','adapter','reported_rules',
                  'reported_strict','reported_independent_accepted','reported_independent_judged',
                  'reported_input_million','reported_cached_input_million','reported_output_million','reported_cost_usd']
RESULT_COLUMNS = ['configuration_id','task_id','recorded_status','retained_outcome','evidence_basis',
                  'attempt_scope','review_rounds','solved_on_sample','recorded_elapsed_seconds',
                  'recorded_proof_sha256','artifact_sha256','artifact_hash_check']
AXIOM_COLUMNS = ['configuration_id','task_id','audit_snapshot','audit_outcome','axioms','axiom_list_complete']
CHECK_COLUMNS = ['configuration_id','task_id','checker_scope','verdict','elapsed_seconds']
AXIOMS = {'propext','Classical.choice','Quot.sound','Lean.ofReduceBool','Lean.trustCompiler','sorryAx'}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def csv_rows(root, filename, columns):
    with (root/filename).open(newline='') as f:
        reader=csv.DictReader(f)
        require(reader.fieldnames==columns, 'Unexpected columns in '+filename)
        rows=list(reader)
    require(all(set(r)==set(columns) and None not in r.values() for r in rows),'Malformed CSV in '+filename)
    return rows

def count(value, optional=False):
    if optional and value=='':
        return None
    require(re.fullmatch(r'\d+',value) is not None,'Invalid integer')
    return int(value)

def number(value, optional=False):
    if optional and value=='':
        return None
    require(re.fullmatch(r'\d+(?:\.\d+)?',value) is not None,'Invalid numeric value')
    return Decimal(value)

def load(root=ROOT):
    tasks=csv_rows(root,'tasks.csv',['task_id','repository'])
    require(len(tasks)==100,'Expected 100 subset tasks')
    task_ids=set()
    for t in tasks:
        t['task_id']=count(t['task_id'])
        require(1<=t['task_id']<=500 and t['task_id'] not in task_ids,'Invalid or duplicate task')
        task_ids.add(t['task_id'])
        require(re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*',t['repository']) is not None,'Invalid repository name')
    configs=csv_rows(root,'reported_results.csv',CONFIG_COLUMNS)
    config_ids=set()
    for c in configs:
        cid=c['configuration_id']
        require(re.fullmatch(r'[a-z][a-z0-9_]*',cid) is not None and cid not in config_ids,'Invalid configuration ID')
        config_ids.add(cid)
        require(c['system'] in {'Claude Code','Codex','OpenCode','Forall-Lean-Agent','Numina-Lean-Agent'},'Invalid system')
        require(c['model'] in {'Opus 5','Fable 5','GPT-5.6 Sol'},'Invalid model')
        require(c['effort'] in {'low','xhigh'} and c['adapter'] in {'Claude Code','Codex','OpenCode'},'Invalid configuration')
        for k in CONFIG_COLUMNS[5:9]:
            c[k]=count(c[k],optional=True)
            require(c[k] is None or 0<=c[k]<=100,'Invalid reported score')
        require(c['reported_rules'] is not None,'Missing reported acceptance count')
        require(c['reported_strict'] is None or c['reported_strict']<=c['reported_rules'],'Strict exceeds Rules')
        accepted,judged=c['reported_independent_accepted'],c['reported_independent_judged']
        require((accepted is None and judged is None) or (accepted is not None and judged is not None and accepted<=judged<=72),'Invalid independent score')
        for k in CONFIG_COLUMNS[9:]:
            c[k]=number(c[k])
        require(c['reported_cached_input_million']<=c['reported_input_million'],'Cache exceeds total input')
    require(len(configs)==13,'Expected 13 configurations')
    results=csv_rows(root,'results.csv',RESULT_COLUMNS)
    seen=set()
    for r in results:
        r['task_id']=count(r['task_id'])
        key=(r['configuration_id'],r['task_id'])
        require(key not in seen and key[0] in config_ids and key[1] in task_ids,'Invalid or duplicate task result')
        seen.add(key)
        require(r['recorded_status'] in {'solved','failed','reviewed_accepted','review_exhausted','harness_prep_failed','prep_failed','capped','timeout','error'},'Invalid recorded status')
        require(r['retained_outcome'] in {'accepted','not_accepted'},'Invalid retained outcome')
        require(r['evidence_basis'] in {'result','reviewed_result','review_parser_recovery'},'Invalid evidence basis')
        require(r['attempt_scope'] in {'retained_run','dependency_recovery','fresh_retry','original_pass'},'Invalid attempt scope')
        r['review_rounds']=count(r['review_rounds'],optional=True)
        r['solved_on_sample']=count(r['solved_on_sample'],optional=True)
        require(r['review_rounds'] is None or 1<=r['review_rounds']<=10,'Invalid review rounds')
        require(r['solved_on_sample'] is None or 1<=r['solved_on_sample']<=8,'Invalid sample index')
        r['recorded_elapsed_seconds']=number(r['recorded_elapsed_seconds'],optional=True)
        for k in ['recorded_proof_sha256','artifact_sha256']:
            require(not r[k] or re.fullmatch(r'[a-f0-9]{64}',r[k]),'Invalid artifact digest')
        recorded,observed=r['recorded_proof_sha256'],r['artifact_sha256']
        expected='match' if recorded and recorded==observed else ('mismatch' if recorded and observed else ('unrecorded' if observed else 'unavailable'))
        require(r['artifact_hash_check']==expected,'Hash-check status is inconsistent')
        if r['evidence_basis']=='review_parser_recovery':
            require(r['configuration_id']=='forall_fable_low' and r['retained_outcome']=='accepted' and
                    r['recorded_status']=='review_exhausted' and r['review_rounds']==5 and expected=='match','Invalid recovered review')
        else:
            require((r['retained_outcome']=='accepted')==(r['recorded_status'] in {'solved','reviewed_accepted'}),'Outcome disagrees with recorded status')
    require(seen=={(c,i) for c in config_ids for i in task_ids},'Incomplete configuration by task matrix')
    audits=csv_rows(root,'axiom_audits.csv',AXIOM_COLUMNS)
    checks=csv_rows(root,'independent_checks.csv',CHECK_COLUMNS)
    result_map={(r['configuration_id'],r['task_id']):r for r in results}
    for rows,kind in [(audits,'audit'),(checks,'checker')]:
        seen=set()
        for r in rows:
            r['task_id']=count(r['task_id'])
            key=(r['configuration_id'],r['task_id'])
            require(key in result_map and key not in seen,'Invalid or duplicate '+kind+' row')
            seen.add(key)
            require(result_map[key]['retained_outcome']=='accepted','Audit attached to unaccepted task')
            if kind=='audit':
                require(r['audit_snapshot'] in {'retained_rescore','retained_result','retained_axiom_audit','dependency_recovery','cumulative_axiom_audit'},'Invalid audit snapshot')
                require(r['audit_outcome'] in {'clean','forbidden_dependency','inconclusive'},'Invalid axiom verdict')
                names=r['axioms'].split('|') if r['axioms'] else []
                require(set(names)<=AXIOMS and len(names)==len(set(names)),'Unexpected axiom name')
                require(r['axiom_list_complete'] in {'True','False'},'Invalid completeness flag')
            else:
                require(r['checker_scope'] in {'retained_snapshot','original_96_accepted'},'Invalid checker scope')
                require(r['verdict'] in {'accepted','rejected_axiom','harness_module_artifact'},'Unexpected checker verdict')
                r['elapsed_seconds']=number(r['elapsed_seconds'],optional=True)
    benchmark=json.loads((root/'environment/benchmark.json').read_text())
    require(set(benchmark)=={'schema_version','benchmark','repository','commit','dataset_sha256','full_task_count','evaluated_task_count','subset_field','repositories','dependency_recovery'},'Unexpected benchmark fields')
    require(benchmark['schema_version']==1 and benchmark['benchmark']=='VeriSoftBench' and benchmark['repository']=='https://github.com/utopia-group/VeriSoftBench','Unexpected benchmark identity')
    require(benchmark['full_task_count']==500 and benchmark['evaluated_task_count']==100 and benchmark['subset_field']=='subset_aristotle','Invalid subset metadata')
    require(re.fullmatch(r'[a-f0-9]{40}',benchmark['commit']) and re.fullmatch(r'[a-f0-9]{64}',benchmark['dataset_sha256']),'Invalid dataset pin')
    require(len(benchmark['repositories'])==11,'Expected 11 source repositories')
    require({r['name'] for r in benchmark['repositories']}=={t['repository'] for t in tasks},'Repository coverage mismatch')
    for repo in benchmark['repositories']:
        require(set(repo)=={'name','url','commit','lean_toolchain','license','dependencies'},'Unexpected repository fields')
        require(re.fullmatch(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo['url']),'Invalid repository URL')
        require(re.fullmatch(r'[a-f0-9]{40}',repo['commit']),'Invalid source pin')
        require(re.fullmatch(r'leanprover/lean4:v[0-9.]+(?:-rc\d+)?',repo['lean_toolchain']),'Invalid Lean pin')
        require(re.fullmatch(r'[A-Za-z0-9. +()-]*',repo['license']),'Invalid license identifier')
        for dep in repo['dependencies']:
            require(set(dep)=={'name','url','rev'},'Unexpected dependency fields')
            require(re.fullmatch(r'(?:[A-Za-z0-9_-]+|«[A-Za-z0-9_-]+»)',dep['name']),'Invalid dependency name')
            require(re.fullmatch(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',dep['url']),'Invalid dependency URL')
            require(re.fullmatch(r'[a-f0-9]{40}',dep['rev']),'Invalid dependency pin')
    require(benchmark['dependency_recovery']==dict(task_id=222,repository='iris-lean',dependency='Qq',
        original_rev='9371548b6ac4467fea4dfc675881f6212cc5565d',recovered_rev='9312503909aa8e8bb392530145cc1677a6298574',lean_toolchain='leanprover/lean4:v4.26.0'),'Unexpected recovery metadata')
    evaluation=json.loads((root/'environment/evaluation.json').read_text())
    require(set(evaluation)=={'schema_version','snapshot_date','outcome_source','reported_source','proof_text_included','configurations','independent_checker'},'Unexpected evaluation fields')
    require(evaluation['schema_version']==1 and evaluation['snapshot_date']=='2026-09-15' and evaluation['proof_text_included'] is False,'Invalid evaluation identity')
    require(evaluation['outcome_source']=='author_retained_evaluation_records' and evaluation['reported_source']=='manuscript_table_1','Invalid provenance')
    require(len(evaluation['configurations'])==13 and {c['configuration_id'] for c in evaluation['configurations']}==config_ids,'Budget configuration mismatch')
    for budget in evaluation['configurations']:
        require(set(budget)=={'configuration_id','target_protocol','max_samples','max_review_rounds','actor_compilation_limit','compilation_limit_scope'},'Unexpected budget fields')
        require(budget['target_protocol'] in {'Pass@8, r=3','1 sample, r<=10'},'Invalid target protocol')
        require(budget['max_samples'] in {1,8} and budget['max_review_rounds'] in {None,3,5,10} and budget['actor_compilation_limit'] in {None,3},'Invalid execution limits')
        require(budget['compilation_limit_scope'] in {'uncapped','per_task','per_sample'},'Invalid compiler scope')
        require((budget['actor_compilation_limit'] is None)==(budget['compilation_limit_scope']=='uncapped'),'Compiler scope mismatch')
    require(evaluation['independent_checker']==dict(comparator_revision='71b52ec',compatibility_patches=2,
        components=['comparator','lean4export','nanoda'],eligible_tasks=72,
        toolchains=['leanprover/lean4:v4.24.0','leanprover/lean4:v4.24.0-rc1'],
        artifact_hashes_in_original_checker_records=False),'Unexpected checker metadata')
    return dict(tasks=tasks,configurations=configs,results=results,axioms=audits,checks=checks)
