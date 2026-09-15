"""Reproduce tables and an optional figure from the public CSV files."""
from collections import Counter
from decimal import Decimal
import argparse
import csv
import io
import json
from release_data import ROOT, load

def summarize(data):
    summaries=[]
    for c in data['configurations']:
        cid=c['configuration_id']
        rows=[r for r in data['results'] if r['configuration_id']==cid]
        audits=[r for r in data['axioms'] if r['configuration_id']==cid]
        checks=[r for r in data['checks'] if r['configuration_id']==cid]
        ac=Counter(a['audit_outcome'] for a in audits)
        cc=Counter(a['verdict'] for a in checks)
        accepted=sum(r['retained_outcome']=='accepted' for r in rows)
        summaries.append(dict(configuration_id=cid,system=c['system'],model=c['model'],effort=c['effort'],adapter=c['adapter'],
            reported_rules=c['reported_rules'],retained_accepted=accepted,retained_tasks=len(rows),
            reported_strict=c['reported_strict'],audit_coverage=len(audits),audit_clean=ac['clean'],
            audit_forbidden=ac['forbidden_dependency'],audit_inconclusive=ac['inconclusive'],
            independent_eligible=72,independent_coverage=len(checks),independent_accepted=cc['accepted'],
            independent_judged=cc['accepted']+cc['rejected_axiom'],independent_excluded=cc['harness_module_artifact'],
            matching_recorded_hashes=sum(r['artifact_hash_check']=='match' for r in rows),
            observed_artifact_hashes=sum(bool(r['artifact_sha256']) for r in rows),
            elapsed_field_coverage=sum(r['recorded_elapsed_seconds'] is not None for r in rows),
            reported_cost_usd=c['reported_cost_usd'],reported_input_million=c['reported_input_million'],
            reported_cached_input_million=c['reported_cached_input_million'],reported_output_million=c['reported_output_million'],
            reported_cost_per_retained_acceptance=(c['reported_cost_usd']/accepted).quantize(Decimal('.01')) if accepted else None))
    return summaries

def numeric_reports(data):
    rows=summarize(data)
    md=['# Evaluation summary','',
        'The reported columns transcribe manuscript Table 1. Retained columns are computed from this release. Missing audits are not passing audits.', '',
        '## Acceptance and audit coverage','',
        '| Configuration | Reported Rules | Retained accepted / tasks | Reported Strict | Retained clean / audited | Independent accepted / judged | Checker records / eligible |',
        '| --- | --- | --- | --- | --- | --- | --- |']
    for r in rows:
        clean=f"{r['audit_clean']}/{r['audit_coverage']}" if r['audit_coverage'] else 'unavailable'
        indep=f"{r['independent_accepted']}/{r['independent_judged']}" if r['independent_judged'] else 'unavailable'
        strict=r['reported_strict'] if r['reported_strict'] is not None else 'unavailable'
        md.append(f"| `{r['configuration_id']}` | {r['reported_rules']} | {r['retained_accepted']}/{r['retained_tasks']} | {strict} | {clean} | {indep} | {r['independent_coverage']}/72 |")
    md+=['','Configuration names, models, effort, and adapters are defined in [reported_results.csv](../reported_results.csv). The denominators above have different meanings. The one-task Codex audits cover only task 222. See [reconciliation](../RECONCILIATION.md) for score differences.','',
         '## Reported resources','',
         '| Configuration | Cost USD | Input M | Cached input M | Output M | Cost / retained acceptance USD | Elapsed field coverage |',
         '| --- | --- | --- | --- | --- | --- | --- |']
    for r in rows:
        md.append(f"| `{r['configuration_id']}` | {r['reported_cost_usd']:.0f} | {r['reported_input_million']} | {r['reported_cached_input_million']} | {r['reported_output_million']} | {r['reported_cost_per_retained_acceptance']} | {r['elapsed_field_coverage']}/100 |")
    md+=['','Costs and tokens are rounded manuscript values. Cache is included in total input. The cost ratio combines reported cost with retained acceptance and is descriptive. The final-result elapsed fields have different timing scopes and are not aggregated.','',
         '## Export checks','',
         f"The export contains {len(data['results']):,} task records, {len(data['axioms']):,} task-level axiom audits, and {len(data['checks']):,} independent-checker records.",'',
         f"There are {sum(r['matching_recorded_hashes'] for r in rows):,} matching recorded candidate digests and {sum(r['observed_artifact_hashes'] for r in rows):,} observed candidate files. Hashes identify artifacts and do not independently certify correctness.",'']
    by_repo=[]
    task_repos={t['task_id']:t['repository'] for t in data['tasks']}
    for c in data['configurations']:
        for repo in sorted(set(task_repos.values())):
            subset=[r for r in data['results'] if r['configuration_id']==c['configuration_id'] and task_repos[r['task_id']]==repo]
            by_repo.append(dict(configuration_id=c['configuration_id'],repository=repo,tasks=len(subset),retained_accepted=sum(r['retained_outcome']=='accepted' for r in subset)))
    def csv_text(items):
        s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=list(items[0]),lineterminator='\n');w.writeheader();w.writerows(items);return s.getvalue()
    return {'reports/summary.md':'\n'.join(md),
            'reports/summary.json':json.dumps(dict(subset_tasks=100,configurations=rows),indent=2,default=str)+'\n',
            'reports/by_repository.csv':csv_text(by_repo)}

def plot(data,root=ROOT):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows=summarize(data)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,(left,right)=plt.subplots(1,2,figsize=(14.6,9),gridspec_kw={'width_ratios':[1.65,1]},sharey=True)
    fig.patch.set_facecolor('white')
    labels=[f"{r['system']} · {r['model']} {r['effort']}"+ ('\n'+r['adapter']+' adapter' if r['system']=='Forall-Lean-Agent' and r['model']=='GPT-5.6 Sol' and r['effort']=='low' else '') for r in rows]
    y=list(range(len(rows)));colors=['#245DA8' if r['system']=='Forall-Lean-Agent' else '#93B6DF' for r in rows]
    left.barh(y,[r['retained_accepted'] for r in rows],height=.65,color=colors,label='Retained acceptance')
    left.scatter([r['reported_rules'] for r in rows],y,marker='D',facecolors='white',edgecolors='#153E70',s=35,zorder=4,label='Reported Rules')
    for i,r in enumerate(rows):
        label=str(r['retained_accepted'])
        if r['retained_accepted']!=r['reported_rules']:label+=f" / {r['reported_rules']} reported"
        left.text(2,i,label,va='center',color='#102D50',fontsize=9,bbox=dict(facecolor='white',alpha=.85,edgecolor='none',pad=1))
    left.set_yticks(y,labels);left.invert_yaxis();left.set_xlim(0,105)
    left.set_xlabel('Accepted tasks out of 100');left.set_title('Retained evidence and manuscript score',loc='left',fontweight='bold',pad=14)
    left.legend(loc='lower left',bbox_to_anchor=(0,-.13),frameon=False,ncol=2,fontsize=9)
    right.barh(y,[float(r['reported_cost_usd']) for r in rows],height=.65,color=colors)
    right.set_xscale('log');right.set_xlim(20,4000);right.set_xticks([30,100,300,1000,3000],['30','100','300','1,000','3,000'])
    for i,r in enumerate(rows):right.text(float(r['reported_cost_usd'])*1.08,i,f"${r['reported_cost_usd']:,.0f}",va='center',fontsize=10,color='#153E70')
    right.tick_params(axis='y',left=False);right.set_xlabel('Reported cost in USD · logarithmic scale');right.set_title('Manuscript cost',loc='left',fontweight='bold',pad=14)
    for ax in [left,right]:
        ax.grid(axis='x',color='#DAE5F2',linewidth=.7);ax.set_axisbelow(True)
        ax.spines['left'].set_visible(False);ax.spines['bottom'].set_color('#A7BDD5');ax.tick_params(axis='y',length=0)
    fig.suptitle('VeriSoftBench · 100-task subset',x=.03,y=.99,ha='left',fontsize=19,fontweight='bold',color='#153E70')
    fig.text(.03,.017,'Different execution budgets and retained snapshots limit direct cost comparisons. Full benchmark coverage is 500 tasks.',fontsize=9,color='#466580')
    fig.subplots_adjust(left=.335,right=.975,top=.9,bottom=.145,wspace=.16)
    fig.savefig(root/'reports/cost-and-coverage.png',dpi=180,facecolor='white')
    plt.close(fig)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--plots',action='store_true');args=parser.parse_args()
    data=load()
    for path,text in numeric_reports(data).items():(ROOT/path).write_text(text)
    if args.plots:plot(data)
    print('Regenerated summary tables'+(' and figure' if args.plots else ''))

if __name__=='__main__':main()
