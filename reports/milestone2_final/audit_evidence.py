"""Read-only audit of local evidence and the configured Forge project."""
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from src.utils.tracking import public_run_accessible
from scripts.sync_wandb import synced_metadata

OUT=Path(__file__).resolve().parent
BUILD=OUT/'.build'
ASSETS=OUT/'assets'
ASSETS.mkdir(exist_ok=True)
paper={5:{'acil':[66.30,57.78],'dsal':[66.39,58.26]},
       25:{'acil':[65.95,57.65],'dsal':[66.20,58.32]},
       50:{'acil':[66.01,57.83],'dsal':[66.33,58.37]}}
names=['base-training','acil-k5','dac-no-plc-k5','dsal-k5','dsal-k25','dsal-k50','buffer-512','buffer-1024','buffer-2048']
entries=[]
def evidence_path(directory):
    """Use original outputs when available, otherwise the published snapshot."""
    return directory if directory.exists() else ROOT/'experiments/evidence'/directory.name

def tracking_metadata(directory):
    snapshot=ROOT/'experiments/evidence'/directory.name/'tracking.json'
    if (directory/'summary.json').exists():
        return synced_metadata(directory/'summary.json',ROOT/'outputs')
    return json.loads(snapshot.read_text(encoding='utf-8'))

for name in names:
    original=ROOT/'outputs/core-seed0'/name
    directory=evidence_path(original)
    config=json.loads((directory/'config.json').read_text(encoding='utf-8'))
    summary=json.loads((directory/'summary.json').read_text(encoding='utf-8'))
    assert summary.get('completed') is True,name
    phases=json.loads((directory/'phases.json').read_text()) if (directory/'phases.json').exists() else []
    if phases:
        assert len(phases)==config['protocol']['phases']+1,name
        assert math.isclose(sum(x['accuracy'] for x in phases)/len(phases),summary['average_accuracy'],rel_tol=1e-12)
        assert math.isclose(phases[-1]['accuracy'],summary['last_accuracy'],rel_tol=1e-12)
    metadata=tracking_metadata(original)
    entries.append({'name':name,'directory':original.relative_to(ROOT).as_posix(),
                    'config':config,'summary':summary,'phases':phases,'tracking':metadata,
                    'summary_sha256':hashlib.sha256((directory/'summary.json').read_bytes()).hexdigest()})
for directory in [ROOT/'outputs/reference-comparison',*[ROOT/'outputs/empirics-synthetic'/name for name in ['phase-dependence','ridge-residue','scaling']]]:
    original=directory
    directory=evidence_path(original)
    summary=json.loads((directory/'summary.json').read_text(encoding='utf-8'))
    config=json.loads((directory/'config.json').read_text(encoding='utf-8'))
    entries.append({'name':directory.name,'directory':original.relative_to(ROOT).as_posix(),
                    'config':config,'summary':summary,'phases':[],
                    'tracking':tracking_metadata(original)})

import wandb
base='https://api.forge.coreweave.com'
entity='vu-lam-vnuhcm-university-of-science'
project='intro-ml-group3-dsal'
api=wandb.Api(overrides={'base_url':base},timeout=30)
remote={run.id:run for run in api.runs(f'{entity}/{project}',per_page=100)}
for item in entries:
    run_id=item['summary'].get('wandb_run_id')
    try:
        run=remote[run_id]
        assert run.state=='finished'
        assert run.summary.get('completed')
        for key,value in item['summary'].items():
            if isinstance(value,(int,float)) and not isinstance(value,bool):
                assert math.isclose(run.summary[key],value,rel_tol=1e-12,abs_tol=0.0),(run_id,key)
        public=public_run_accessible(entity,project,run_id,base)
        assert public
        history=list(run.scan_history(page_size=1000))
        expected=[json.loads(line) for line in (evidence_path(ROOT/item['directory'])/'metrics.jsonl').read_text(encoding='utf-8').splitlines()]
        # Resume can replay prior rows. Verify the final occurrence at each step.
        keyed={row['_step']:row for row in history}
        for row in expected:
            for key,value in row.items():
                if key=='step':continue
                actual=keyed[row['step']].get(key)
                if isinstance(value,(float,int)) and not isinstance(value,bool):
                    assert math.isclose(actual,value,rel_tol=1e-12,abs_tol=0.0),(run_id,key)
                else: assert actual==value
        item['verification']={'status':'VERIFIED','state':run.state,'public':public,
                              'url':run.url,'run_id':run.id,'history_rows':len(history),
                              'config':dict(run.config),'base_url':base}
    except Exception as error:
        item['verification']={'status':'NEEDS VERIFICATION','run_id':run_id,
                              'error_type':type(error).__name__}
    print(item['name'],item['verification']['status'],flush=True)

evidence={'checked_on':'2026-11-19','base_url':base,'entity':entity,'project':project,
          'paper_table1':paper,'experiments':entries,
          'reference':json.loads((evidence_path(ROOT/'outputs/reference-comparison')/'comparison.json').read_text()),
          'mechanisms':{name:json.loads((ROOT/'experiments/empirics'/f'{name}.json').read_text()) for name in ['phase-dependence','ridge-residue','scaling']}}
(ASSETS/'verified_evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
print('Verified',sum(e['verification']['status']=='VERIFIED' for e in entries),'of',len(entries),flush=True)
