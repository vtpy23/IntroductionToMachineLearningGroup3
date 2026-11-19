"""Reconcile original logs/configs with live Forge; no experiment or W&B writes."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics as stats
import math
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
sys.path.insert(0,str(ROOT))
BUILD=HERE/'.build/three-seeds'
METHODS=['acil-k5','dac-no-plc-k5','dsal-k5']
ENTITY='vu-lam-vnuhcm-university-of-science'
PROJECT='intro-ml-group3-dsal'
HOST='https://api.forge.coreweave.com'

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def same(a,b):
    if isinstance(a,(int,float)) and not isinstance(a,bool) and isinstance(b,(int,float)):
        return math.isclose(a,b,rel_tol=1e-12,abs_tol=0)
    return a==b
def distribution(values):
    return {'values':values,'mean':stats.mean(values),'sd':stats.stdev(values),'n':len(values),'ddof':1}

def verify_seed(seed):
    import wandb
    from src.utils.tracking import public_run_accessible
    out=ROOT/'outputs/core-seed0' if seed==0 else ROOT/f'outputs/multiseed-20261119/core-seed{seed}'
    api=wandb.Api(overrides={'base_url':HOST},timeout=30)
    assert api.viewer
    rows=[]
    for method in ['base-training',*METHODS]:
        folder=out/method
        config=read(folder/'config.json');summary=read(folder/'summary.json')
        assert summary['completed'] and config['seed']==seed
        run=api.run(f'{ENTITY}/{PROJECT}/{summary["wandb_run_id"]}')
        assert run.state=='finished' and run.summary.get('completed')
        # Early seed0 metadata predates the explicit endpoint config field.
        # Read via the forced Forge endpoint; reject a conflicting stored host.
        assert run.config.get('tracking',{}).get('base_url',HOST)==HOST
        for key in ['seed','class_order_seed','training','analytic','protocol','output']:
            assert run.config[key]==config[key],(seed,method,key)
        if method!='base-training':assert run.config['feature_identity']==config['feature_identity']
        history=[json.loads(line) for line in (folder/'metrics.jsonl').read_text().splitlines()]
        axis='base/epoch' if method=='base-training' else 'cil/phase'
        local={int(r[axis]):r for r in history}
        remote={int(r[axis]):r for r in run.scan_history() if r.get(axis) is not None}
        expected=set(range(1,161)) if method=='base-training' else set(range(6))
        assert set(local)==set(remote)==expected,(seed,method,'history coverage')
        for step,row in local.items():
            for key,value in row.items():
                if key!='step':assert same(remote[step].get(key),value),(seed,method,step,key)
        skip={'wandb_url','wandb_run_id','tracking_mode','submission_ready','public_visibility_verified'}
        for key,value in summary.items():
            if key not in skip:assert same(run.summary.get(key),value),(seed,method,key)
        assert public_run_accessible(ENTITY,PROJECT,run.id,HOST)
        row={'seed':seed,'method':method,'directory':folder.relative_to(ROOT).as_posix(),
             'url':run.url,'run_id':run.id,'state':run.state,'public':True,
             'config':config,'summary':summary,'history':list(local.values()),
             'verified_history_rows':len(local),
             'files_sha256':{name:sha(folder/name) for name in ['config.json','summary.json','metrics.jsonl']}}
        if method!='base-training':
            phases=read(folder/'phases.json')
            assert [r['classes'] for r in phases]==[50,60,70,80,90,100]
            assert same(stats.mean(r['accuracy'] for r in phases),summary['average_accuracy'])
            assert same(phases[-1]['accuracy'],summary['last_accuracy'])
            row['phases']=phases;row['files_sha256']['phases.json']=sha(folder/'phases.json')
        rows.append(row)
    identities=[r['config']['feature_identity'] for r in rows if r['method']!='base-training']
    assert all(x==identities[0] for x in identities)
    assert identities[0]['checkpoint_sha256']==rows[0]['summary']['checkpoint_sha256']
    assert identities[0]['dataset']['revision']=='aadb3af77e9048adbea6b47c21a81e47dd092ae5'
    print(f'Seed {seed}: four finished/public runs and all measured history verified.',flush=True)
    return rows

def main():
    from dotenv import load_dotenv
    load_dotenv(ROOT/'.env')
    BUILD.mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        rows=[r for group in pool.map(verify_seed,[0,1,2]) for r in group]
    grouped={m:[next(r for r in rows if r['method']==m and r['seed']==s) for s in [0,1,2]] for m in METHODS}
    aggregates={}
    for m,group in grouped.items():
        aggregates[m]={key:distribution([r['summary'][key] for r in group])
                       for key in ['average_accuracy','last_accuracy','base_accuracy','novel_accuracy','fit_seconds','elapsed_seconds']}
        aggregates[m]['phase_accuracy']=[distribution([r['phases'][p]['accuracy'] for r in group]) for p in range(6)]
    paired={}
    for name,other in [('dsal_minus_acil','acil-k5'),('plc_gain','dac-no-plc-k5'),('dac_minus_acil','acil-k5')]:
        first='dac-no-plc-k5' if name=='dac_minus_acil' else 'dsal-k5'
        paired[name]={key:distribution([grouped[first][s]['summary'][key]-grouped[other][s]['summary'][key] for s in range(3)])
                      for key in ['average_accuracy','last_accuracy','base_accuracy','novel_accuracy']}
    previous=read(ROOT/'experiments/multiseed/20261119/results.json')
    for a in previous['aggregate']:
        for metric,prefix in [('average_accuracy','Abar'),('last_accuracy','AK')]:
            assert same(a[prefix+'_mean'],aggregates[a['method']][metric]['mean'])
            assert same(a[prefix+'_std_sample_ddof1'],aggregates[a['method']][metric]['sd'])
    baseline=HERE/'DSAL_Milestone2_Lab1_Final_v3.pptx'
    result={'verified_utc':datetime.now(timezone.utc).isoformat(),'base_url':HOST,'entity':ENTITY,'project':PROJECT,
            'baseline_pptx':baseline.name,'baseline_sha256':sha(baseline),'runs':rows,
            'aggregates':aggregates,'paired':paired,'all_12_runs_verified':True,
            'sd_definition':'sample SD across seeds 0,1,2; ddof=1; not standard error or confidence interval',
            'phase_mean_definition':'Abar_s=(A_s,0+...+A_s,5)/6; then average Abar_s across three seeds',
            'checkpoint_audit':read(ROOT/'experiments/multiseed/20261119/verification/completion-audit.json')}
    (HERE/'assets/three_seeds_verified.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'aggregates':aggregates,'paired':paired},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
