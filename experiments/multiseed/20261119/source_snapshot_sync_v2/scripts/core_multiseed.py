"""Sequential core replication with isolated checkpoints and verified W&B evidence.

Scientific training, feature extraction and analytic functions are reused intact.
Controller imports no PyTorch; workers use the existing CPU environment of seed0.
"""
import argparse
import copy
import ctypes
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from scripts.core_multiseed_report import ROOT,STUDY,REPORT,METHODS,HOST,ENTITY,PROJECT,read

CPU=ROOT/'.venv-cpu/Scripts/python.exe'
API_PYTHON=ROOT/'.venv/Scripts/python.exe'

def utc():
    return datetime.now(timezone.utc).isoformat()

def write(path,obj):
    from src.utils.reproducibility import write_json
    write_json(path,obj)

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()

def source_manifest():
    return {p.relative_to(ROOT).as_posix():digest(p) for folder in ['src','scripts','configs']
            for p in (ROOT/folder).rglob('*') if p.suffix in ['.py','.json','.ps1','.mjs']}

def check_sources():
    manifest=read(STUDY/'manifest.json')
    assert source_manifest()==manifest['source_sha256'], 'Source changed; resume requires exactly the same code.'
    assert digest(ROOT/'data/cache/dataset.json')==manifest['dataset_metadata_sha256']
    for item in manifest['configs']:
        assert digest(ROOT/item['path'])==item['sha256'], 'Config changed; use a new experiment.'

def initialize():
    if (STUDY/'manifest.json').exists():
        check_sources();return
    config=read(ROOT/'configs/cifar100_core.json')
    assert config['seed']==config['class_order_seed']==0
    assert config['protocol']=={'base_classes':50,'phases':5}
    assert config['training']['epochs']==160 and config['analytic']['buffer_size']==8192
    config['suite']=[v for v in config['suite'] if v['name'] in METHODS]
    assert [v['name'] for v in config['suite']]==METHODS
    config['tracking']={'entity':ENTITY,'project':PROJECT,'base_url':HOST}
    configs=[]
    for seed in [1,2]:
        current=copy.deepcopy(config)
        current['seed']=current['class_order_seed']=seed
        current['output']=f'outputs/multiseed-20261119/core-seed{seed}'
        current['training']['checkpoint']=f'checkpoints/multiseed-20261119/seed{seed}-resnet32.pt'
        assert not (ROOT/current['output']).exists(), 'Existing output without matching manifest.'
        assert not (ROOT/current['training']['checkpoint']).exists(), 'Existing checkpoint without matching manifest.'
        target=REPORT/f'configs/seed{seed}.json'
        if target.exists():
            assert read(target)==current
        else:
            write(target,current)
        configs.append({'seed':seed,'path':target.relative_to(ROOT).as_posix(),'sha256':digest(target)})
    protected={p.relative_to(ROOT).as_posix():digest(p) for p in (ROOT/'outputs/core-seed0').rglob('*')
               if p.is_file() and 'wandb' not in p.parts}
    checkpoint=ROOT/'checkpoints/core-seed0-resnet32.pt'
    protected[checkpoint.relative_to(ROOT).as_posix()]=digest(checkpoint)
    features=read(ROOT/'outputs/core-seed0/feature_cache.json')
    assert digest(ROOT/features['path'])==features['sha256']
    protected[features['path']]=features['sha256']
    source=source_manifest()
    for relative in source:
        target=STUDY/'source_snapshot'/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/relative,target)
    epochs={int(r['base/epoch']):r for r in (json.loads(s) for s in (ROOT/'outputs/core-seed0/base-training/metrics.jsonl').read_text().splitlines())}
    assert set(epochs)==set(range(1,161))
    manifest={'created_utc':utc(),'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
              'git_dirty':bool(subprocess.check_output(['git','status','--porcelain'],text=True,encoding='utf-8')),
              'source_sha256':source,'configs':configs,'protected_seed0_sha256':protected,
              'dataset_metadata':read(ROOT/'data/cache/dataset.json'),
              'dataset_metadata_sha256':digest(ROOT/'data/cache/dataset.json'),
              'seed0_training_seconds':sum(r['base/seconds'] for r in epochs.values()),
              'execution_backend':'CPU torch 2.5.1+cpu; existing seed0 environment; 8 threads; sequential',
              'seed_protocol':'independent class order, backbone initialization, shuffle/augmentation, projection; paired methods within seed',
              'methods':METHODS,'seeds_to_run':[1,2],'wandb':config['tracking']}
    write(STUDY/'manifest.json',manifest)
    write(REPORT/'provenance.json',{k:v for k,v in manifest.items() if k!='protected_seed0_sha256'})

def independence_check():
    """Diagnostic hashes, not an accuracy experiment or tracked W&B run."""
    import numpy as np
    import torch
    from src.models.resnet import CifarResNet32
    from src.datasets.cifar100 import class_order
    from src.utils.reproducibility import seed_everything
    assert not torch.cuda.is_available()
    state=torch.load(ROOT/'checkpoints/core-seed0-resnet32.pt',map_location='cpu',weights_only=False)
    signature=state['signature']
    assert state['epoch']==160 and signature['seed']==0 and signature['class_order']==class_order(0).tolist()
    assert signature['dataset_revision']==read(STUDY/'manifest.json')['dataset_metadata']['revision']
    assert all(k in state for k in ['optimizer','scheduler','torch_rng','loader_rng'])
    diagnostic=[]
    for seed in [0,1,2]:
        seed_everything(seed)
        model=CifarResNet32(50)
        initial=hashlib.sha256(b''.join(t.detach().numpy().tobytes() for t in model.state_dict().values())).hexdigest()
        gen=torch.Generator(device='cpu').manual_seed(seed)
        projection=torch.randn(64,8192,generator=gen,dtype=torch.float64)
        diagnostic.append({'seed':seed,'class_order':class_order(seed).tolist(),
                           'initial_backbone_sha256':initial,
                           'projection_sha256':hashlib.sha256(projection.numpy().tobytes()).hexdigest()})
    assert len({tuple(r['class_order']) for r in diagnostic})==3
    assert len({r['initial_backbone_sha256'] for r in diagnostic})==3
    assert len({r['projection_sha256'] for r in diagnostic})==3
    write(STUDY/'verification/seed-independence.json',{'scope':'diagnostic only; no research scores',
          'seeds':diagnostic,'seed0_checkpoint_epoch':state['epoch'],'rng_resume_fields_present':True})

def worker(config_path,stage):
    import torch
    from scripts.run import load_config,prepare_data,train_backbone,extract_features
    from src.utils.reproducibility import seed_everything,provenance
    from src.utils.tracking import Tracker
    config=load_config(config_path)
    assert not torch.cuda.is_available(), 'CPU environment required for this study.'
    seed_everything(config['seed'])
    torch.set_num_threads(config['cpu_threads'])
    out=ROOT/config['output']
    out.mkdir(parents=True,exist_ok=True)
    environment=provenance()
    write(out/f'environment-{stage}.json',environment)
    if stage=='prepare':
        data=prepare_data(config)
        assert data['metadata']==read(STUDY/'manifest.json')['dataset_metadata']
        checkpoint=ROOT/config['training']['checkpoint']
        state=torch.load(checkpoint,map_location='cpu',weights_only=False) if checkpoint.exists() else None
        summary_path=out/'base-training/summary.json'
        done=state is not None and state['epoch']==config['training']['epochs']
        tracker=None
        if not (done and summary_path.exists() and read(summary_path).get('completed')):
            tracker=Tracker(out/'base-training',{**config,'provenance':environment},'lab1-reproduction','offline')
        model=train_backbone(config,data,checkpoint,'cpu',tracker)
        if tracker:
            if done:
                # Recover a tracker interrupted after the final atomic checkpoint.
                rows={int(r['base/epoch']):r for r in (json.loads(s) for s in (out/'base-training/metrics.jsonl').read_text().splitlines())}
                assert set(rows)==set(range(1,config['training']['epochs']+1))
                for epoch,row in sorted(rows.items()):
                    tracker.run.log({k:v for k,v in row.items() if k!='step'},step=epoch)
            tracker.finish({'completed':True,'epochs':config['training']['epochs'],'checkpoint_sha256':digest(checkpoint)})
        features=extract_features(model,config,data,checkpoint,'cpu')
        assert features['identity']['checkpoint_sha256']==digest(checkpoint)
    else:
        from scripts.suite import run_suite
        cached=read(out/'feature_cache.json')
        assert digest(ROOT/cached['path'])==cached['sha256']
        features=torch.load(ROOT/cached['path'],map_location='cpu',weights_only=False)
        assert features['identity']['checkpoint_sha256']==digest(ROOT/config['training']['checkpoint'])
        from src.datasets.cifar100 import class_order
        assert features['identity']['class_order']==class_order(config['class_order_seed']).tolist()
        assert features['identity']['dataset']==read(STUDY/'manifest.json')['dataset_metadata']
        assert features['identity']['limits']==config['dataset']
        for variant in config['suite']:
            directory=out/variant['name']
            if directory.exists() and not (directory/'summary.json').exists():
                expected=copy.deepcopy(config);expected.pop('suite')
                for section in ['analytic','protocol']:
                    expected[section].update(variant.get(section,{}))
                expected['lab']=variant.get('lab',config.get('lab','lab1-reproduction'))
                old=read(directory/'config.json')
                assert {k:v for k,v in old.items() if k not in ['provenance','feature_identity']}==expected
                assert old['feature_identity']==features['identity']
                destination=out/'interrupted_attempts'/f'{variant["name"]}-{time.time_ns()}'
                destination.parent.mkdir(exist_ok=True)
                directory.rename(destination)
        run_suite(config,features,out,'offline')

def run_child(command,label):
    from scripts.probe_multiseed_resources import memory
    import psutil
    check_sources()
    available=memory()
    assert available['avail_page']>=4*2**30, 'Insufficient commit headroom; resume after freeing memory.'
    assert shutil.disk_usage(ROOT).free>=2*2**30, 'Less than 2 GiB free disk.'
    logs=STUDY/'logs';logs.mkdir(exist_ok=True)
    attempt=f'{label}-{time.time_ns()}'
    log=logs/(attempt+'.log')
    state={'state':'running','stage':label,'started_utc':utc(),'controller_pid':os.getpid(),
           'log':log.relative_to(ROOT).as_posix()}
    write(STUDY/'status.json',state)
    started=time.perf_counter();peak_rss=peak_private=0;min_commit=available['avail_page']
    with log.open('w',encoding='utf-8') as stream,(logs/(attempt+'-resources.jsonl')).open('w',encoding='utf-8') as resources:
        process=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT,cwd=ROOT,
                                 env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8'))
        state['worker_pid']=process.pid;write(STUDY/'status.json',state)
        while process.poll() is None:
            rss=private=0
            try:
                parent=psutil.Process(process.pid)
                for item in [parent,*parent.children(recursive=True)]:
                    info=item.memory_info();rss+=info.rss;private+=getattr(info,'private',info.vms)
            except (psutil.NoSuchProcess,psutil.AccessDenied):
                pass
            mem=memory();peak_rss=max(peak_rss,rss);peak_private=max(peak_private,private)
            min_commit=min(min_commit,mem['avail_page'])
            resources.write(json.dumps({'utc':utc(),'rss_bytes':rss,'private_bytes':private,'system':mem})+'\n');resources.flush()
            time.sleep(10)
        returncode=process.wait()
    receipt={'stage':label,'exit_code':returncode,'started_utc':state['started_utc'],'finished_utc':utc(),
             'elapsed_seconds':time.perf_counter()-started,'peak_sampled_rss_bytes':peak_rss,
             'peak_sampled_private_bytes':peak_private,'minimum_available_commit_bytes':min_commit,
             'log':log.relative_to(ROOT).as_posix(),'command':command}
    write(logs/(attempt+'-receipt.json'),receipt)
    if returncode:
        raise RuntimeError(f'{label} failed ({returncode}); checkpoint retained; see {log}')

def restore_apps():
    restore=ROOT/'artifacts/multiseed-resource-recovery/restore_apps.ps1'
    if restore.exists():
        subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(restore)],check=False)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['init','run','worker','independence'])
    parser.add_argument('--config');parser.add_argument('--stage',choices=['prepare','analytic'])
    args=parser.parse_args();os.chdir(ROOT)
    if args.command=='worker':
        check_sources();worker(args.config,args.stage);return
    if args.command=='independence':
        independence_check();return
    initialize()
    if args.command=='init':return
    import psutil
    lock=STUDY/'controller.json'
    if lock.exists():
        previous=read(lock)
        if previous['pid']!=os.getpid() and psutil.pid_exists(previous['pid']):
            other=psutil.Process(previous['pid'])
            assert abs(other.create_time()-previous['created'])>.1, 'Controller is already running.'
    write(lock,{'pid':os.getpid(),'created':psutil.Process().create_time()})
    from scripts.core_multiseed_report import verify_remote,report
    import ctypes
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT/'.env')
        import wandb
        api=wandb.Api(overrides={'base_url':HOST},timeout=30)
        assert api.viewer and api.project(PROJECT,entity=ENTITY)
        if not (STUDY/'verification/seed0.json').exists():verify_remote(0)
        run_child([str(CPU),'-u','-X','utf8','-m','scripts.core_multiseed','independence'],'seed-independence-check')
        report()
        for seed in [1,2]:
            assert not (ROOT/'.stop-project').exists(), 'Pause requested; checkpoint retained.'
            config_path=REPORT/f'configs/seed{seed}.json';config=read(config_path)
            out=ROOT/config['output']
            if not ((out/'feature_cache.json').exists() and (out/'base-training/summary.json').exists() and read(out/'base-training/summary.json').get('completed')):
                run_child([str(CPU),'-u','-X','utf8','-m','scripts.core_multiseed','worker',
                           '--config',str(config_path),'--stage','prepare'],f'seed{seed}-backbone-features')
            run_child([str(CPU),'-u','-X','utf8','-m','scripts.core_multiseed','worker',
                       '--config',str(config_path),'--stage','analytic'],f'seed{seed}-core-three-methods')
            run_child([str(API_PYTHON),'-u','-X','utf8','-m','scripts.sync_wandb','--root',str(out),
                       '--manifest',str(STUDY/f'wandb-sync-seed{seed}-{time.time_ns()}.json')],f'seed{seed}-wandb-sync')
            verify_remote(seed);report()
        check_sources()
        for relative,expected in read(STUDY/'manifest.json')['protected_seed0_sha256'].items():
            assert digest(ROOT/relative)==expected, 'Seed0 data changed.'
        results=report();assert len(results['aggregate'])==3 and not results['missing']
        write(STUDY/'status.json',{'state':'completed','finished_utc':utc(),'report':str(REPORT/'RESULTS.md')})
    except BaseException as error:
        prior=read(STUDY/'status.json') if (STUDY/'status.json').exists() else {}
        write(STUDY/'status.json',{**prior,'state':'stopped','stopped_utc':utc(),'reason':str(error)})
        report();raise
    finally:
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
        restore_apps()

if __name__=='__main__':
    main()
