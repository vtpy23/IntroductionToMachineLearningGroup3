"""Report only complete, independently verified core benchmark replications."""
import csv
import json
import statistics
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
STUDY=ROOT/'outputs/multiseed-20261119'
REPORT=ROOT/'experiments/multiseed/20261119'
METHODS=['acil-k5','dac-no-plc-k5','dsal-k5']
ENTITY='vu-lam-vnuhcm-university-of-science'
PROJECT='intro-ml-group3-dsal'
HOST='https://api.forge.coreweave.com'

def normalized_config(config):
    """Only random seed, isolated paths and metadata may differ from seed0."""
    import copy
    value=copy.deepcopy(config)
    for key in ['provenance','feature_identity','output','tracking']:
        value.pop(key,None)
    value['seed']=value['class_order_seed']=0
    value['training'].pop('checkpoint',None)
    return value

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def verify_remote(seed):
    import wandb
    from scripts.sync_wandb import synced_metadata, same_measurement
    from src.utils.reproducibility import write_json
    api=wandb.Api(overrides={'base_url':HOST},timeout=30)
    verified=[]
    out=ROOT/'outputs/core-seed0' if seed==0 else STUDY/f'core-seed{seed}'
    for method in ['base-training',*METHODS]:
        local=read(out/method/'summary.json')
        tracking=synced_metadata(out/method/'summary.json',ROOT/'outputs' if seed==0 else STUDY)
        assert tracking.get('public_visibility_verified'), (seed,method,'public access not verified')
        run=api.run(f'{ENTITY}/{PROJECT}/{tracking["wandb_run_id"]}')
        assert run.state=='finished' and run.config['seed']==seed
        config=read(out/method/'config.json')
        for key in ['seed','class_order_seed','training','analytic','protocol','output']:
            assert run.config[key]==config[key], (run.id,key)
        if method=='base-training':
            rows={int(r['base/epoch']):r for r in (json.loads(s) for s in (out/method/'metrics.jsonl').read_text().splitlines())}
            assert set(rows)==set(range(1,161))
            remote={int(r['base/epoch']):r for r in run.scan_history(keys=['base/epoch','base/loss','base/test_accuracy'])}
            for epoch,row in rows.items():
                for key in ['base/loss','base/test_accuracy']:
                    assert same_measurement(remote[epoch][key],row[key]), (run.id,epoch,key)
        else:
            phases=read(out/method/'phases.json')
            assert [r['phase'] for r in phases]==list(range(6))
            assert [r['classes'] for r in phases]==[50,60,70,80,90,100]
            assert same_measurement(local['average_accuracy'],statistics.mean(r['accuracy'] for r in phases))
            assert same_measurement(local['last_accuracy'],phases[-1]['accuracy'])
            remote={int(r['cil/phase']):r for r in run.scan_history(keys=['cil/phase','cil/accuracy','cil/fit_seconds'])}
            for row in phases:
                for key in ['accuracy','fit_seconds']:
                    assert same_measurement(remote[row['phase']]['cil/'+key],row[key])
            for key in ['average_accuracy','last_accuracy','fit_seconds','elapsed_seconds']:
                assert same_measurement(run.summary[key],local[key])
        verified.append({'seed':seed,'method':method,'run_id':run.id,'url':run.url,
                         'state':run.state,'public':True,'history_verified':True,
                         'verified_utc':datetime.now(timezone.utc).isoformat()})
    # Verification sidecar is in the study, even for seed0: originals untouched.
    write_json(STUDY/f'verification/seed{seed}.json',verified)
    return verified

def aggregate_rows(rows):
    aggregate=[]
    for method in METHODS:
        valid=[r for r in rows if r['method']==method]
        if sorted(r['seed'] for r in valid)==[0,1,2]:
            aggregate.append({'method':method,'n':3,
                              'Abar_mean':statistics.mean(r['Abar'] for r in valid),
                              'Abar_std_sample_ddof1':statistics.stdev(r['Abar'] for r in valid),
                              'AK_mean':statistics.mean(r['AK'] for r in valid),
                              'AK_std_sample_ddof1':statistics.stdev(r['AK'] for r in valid)})
    return aggregate

def report():
    from scripts.sync_wandb import synced_metadata
    from src.utils.reproducibility import sha256_file,write_json
    rows=[];missing=[]
    for seed in [0,1,2]:
        out=ROOT/'outputs/core-seed0' if seed==0 else STUDY/f'core-seed{seed}'
        for method in METHODS:
            path=out/method/'summary.json'
            reason=None
            if not path.exists() or not read(path).get('completed'):
                reason='not completed'
            elif not (STUDY/f'verification/seed{seed}.json').exists():
                reason='remote config/history verification pending'
            if reason:
                missing.append({'seed':seed,'method':method,'reason':reason});continue
            verified=read(STUDY/f'verification/seed{seed}.json')
            s=read(path);config=read(out/method/'config.json');phases=read(out/method/'phases.json')
            tracking=synced_metadata(path,ROOT/'outputs' if seed==0 else STUDY)
            assert tracking.get('submission_ready')
            assert any(r['method']==method and r['run_id']==tracking['wandb_run_id'] and r['history_verified'] for r in verified)
            assert config['seed']==seed and len(phases)==6 and s['phases']==5 and s['buffer_size']==8192
            baseline=read(ROOT/'outputs/core-seed0'/method/'config.json')
            assert normalized_config(config)==normalized_config(baseline), (seed,method,'protocol mismatch')
            assert abs(statistics.mean(r['accuracy'] for r in phases)-s['average_accuracy'])<1e-10
            assert phases[-1]['accuracy']==s['last_accuracy'] and config['analytic_batch_size']==512
            identity=config['feature_identity']
            rows.append({'seed':seed,'method':method,'Abar':s['average_accuracy'],'AK':s['last_accuracy'],
                         'fit_seconds':s['fit_seconds'],'elapsed_seconds':s['elapsed_seconds'],
                         'url':tracking['wandb_url'],'run_id':tracking['wandb_run_id'],
                         'config_sha256':sha256_file(out/method/'config.json'),
                         'checkpoint_sha256':identity['checkpoint_sha256'],'feature_identity':identity,
                         'phase_accuracy':[r['accuracy'] for r in phases]})
    for seed in [0,1,2]:
        paired=[r for r in rows if r['seed']==seed]
        if paired:
            assert all(r['feature_identity']==paired[0]['feature_identity'] for r in paired)
    complete_identities={seed:next(r['checkpoint_sha256'] for r in rows if r['seed']==seed)
                         for seed in [0,1,2] if any(r['seed']==seed for r in rows)}
    assert len(set(complete_identities.values()))==len(complete_identities), 'Backbone checkpoints must differ across seeds.'
    aggregate=aggregate_rows(rows)
    output={'updated_utc':datetime.now(timezone.utc).isoformat(),'rows':rows,'aggregate':aggregate,'missing':missing,
            'std_definition':'sample standard deviation, ddof=1; only complete verified triplets',
            'paper_comparison':{'scope':'DS-AL CIFAR-100 ResNet-32 B50 K5, non-parenthetical Table 1; mean of 3 runs',
                                'Abar':66.39,'AK':58.26,'source':'https://doi.org/10.1609/aaai.v38i15.29670',
                                'ablation_scope':'DAC/PLC adapted to CIFAR-100; not original ImageNet-Full Table 2'}}
    write_json(REPORT/'results.json',output)
    with (REPORT/'results.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['seed','method','Abar','AK','fit_seconds','elapsed_seconds','url','run_id','checkpoint_sha256','config_sha256'],extrasaction='ignore')
        writer.writeheader();writer.writerows(rows)
    lines=['# Thực nghiệm độc lập seed 0, 1, 2','',f'Cập nhật UTC: {output["updated_utc"]}',
           '', '## Kết quả đã hoàn thành và xác minh','',
           '| Seed | Phương pháp | A-bar (%) | A_K (%) | Fit (s) | W&B |',
           '| --- | --- | ---: | ---: | ---: | --- |']
    for r in rows:
        lines.append(f'| {r["seed"]} | {r["method"]} | {r["Abar"]:.6f} | {r["AK"]:.6f} | {r["fit_seconds"]:.3f} | [{r["run_id"]}]({r["url"]}) |')
    lines+=['','## Tổng hợp ba seed','', 'SD là độ lệch chuẩn mẫu (ddof=1), chỉ tính khi đủ ba seed hợp lệ và có bằng chứng W&B.']
    if aggregate:
        lines+=['','| Phương pháp | n | A-bar mean ± SD (%) | A_K mean ± SD (%) |','| --- | ---: | ---: | ---: |']
        for a in aggregate:
            lines.append(f'| {a["method"]} | 3 | {a["Abar_mean"]:.4f} ± {a["Abar_std_sample_ddof1"]:.4f} | {a["AK_mean"]:.4f} ± {a["AK_std_sample_ddof1"]:.4f} |')
    else:
        lines+=['','Chưa đủ ba seed đã xác minh; chưa tính mean hoặc SD.']
    lines+=['','## Đối chiếu bài báo','',
            'DS-AL, CIFAR-100 / ResNet-32 / B50 / K5, Table 1: A-bar = 66,39%, A_K = 58,26% (trung bình ba lần chạy). DOI: https://doi.org/10.1609/aaai.v38i15.29670.',
            'Không dùng ImageNet-Full Table 2 để đối chiếu trực tiếp ablation CIFAR-100.']
    for a in aggregate:
        if a['method']=='dsal-k5':
            lines+=['',f'Chênh lệch DS-AL so với bài báo: A-bar {a["Abar_mean"]-66.39:+.4f} pp; A_K {a["AK_mean"]-58.26:+.4f} pp.',
                    'Ba seed chưa đủ để khẳng định ý nghĩa thống kê. Sai khác có thể gắn với implementation độc lập, class order và chi tiết huấn luyện; không suy ra nguyên nhân chỉ từ bảng điểm.']
    receipts=[read(p) for p in sorted((STUDY/'logs').glob('*-receipt.json'))]
    lines+=['','## Thời gian và tài nguyên','',
            'Huấn luyện và analytic chạy tuần tự trong `.venv-cpu`: PyTorch 2.5.1+cpu, 8 CPU threads. Seed 0 cũng dùng môi trường CPU này. Giữ nguyên 160 epoch, batch 128, B50, K5, buffer 8192, FP64, analytic batch 512, gamma 0,1, C=0,6.',
            'Fit/elapsed lấy từ log thật. Peak RAM được lấy mẫu mỗi 10 giây, có thể bỏ lỡ đỉnh ngắn. Đây không phải benchmark thời gian trên phần cứng được kiểm soát.',
            '', '| Công đoạn | Exit | Thời gian (phút) | Peak RSS lấy mẫu (GiB) |','| --- | ---: | ---: | ---: |']
    for r in receipts:
        lines.append(f'| {r["stage"]} | {r["exit_code"]} | {r["elapsed_seconds"]/60:.2f} | {r["peak_sampled_rss_bytes"]/2**30:.3f} |')
    lines+=['','## Trạng thái còn thiếu','']
    lines += [f'- Seed {m["seed"]}, {m["method"]}: {m["reason"]}.' for m in missing] or ['Không còn thiếu kết quả trong phạm vi ba phương pháp × ba seed.']
    manifest=read(STUDY/'manifest.json')
    lines+=['','## Tái lập và checkpoint','',
            f'Git HEAD: `{manifest["git_commit"]}`. Working tree có thay đổi; `provenance.json` lưu hash chính xác source/config. Bản sao source nằm trong `outputs/multiseed-20261119/source_snapshot/`, không chứa `.env` hoặc credentials.',
            'Checkpoint riêng tại `checkpoints/multiseed-20261119/`, gồm model, optimizer, scheduler, RNG và DataLoader; thay thế nguyên tử mỗi epoch. Không tái sử dụng backbone seed 0 cho seed 1/2.',
            'Cùng seed: dùng chung backbone, class order, feature cache và projection seed. Khác seed: thay cả class order, khởi tạo backbone, shuffle/augmentation và projection, không chỉ tên run.',
            'Analytic chưa hỗ trợ resume giữa pha. Nếu gián đoạn, giữ nguyên attempt cũ rồi tính lại toàn bộ phương pháp cùng cấu hình; không ghép các attempt khác cấu hình.',
            'Không mở rộng khảo sát K/buffer hoặc thay đổi slide. W&B được sync từ bản sao, xác minh config/summary/history. Không lưu API key trong source/config Git.']
    (REPORT/'RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return output

if __name__=='__main__':
    report()
