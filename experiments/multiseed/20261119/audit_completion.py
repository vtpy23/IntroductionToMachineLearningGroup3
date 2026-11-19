"""Read-only audit of completed replications; writes separate lightweight evidence.

Run from repository root with .venv-cpu/Scripts/python.exe -X utf8
experiments/multiseed/20261119/audit_completion.py. No fitting or inference occurs.
"""
import hashlib
import json
from pathlib import Path
import shutil
import statistics
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
STUDY=ROOT/'outputs/multiseed-20261119'
METHODS=['acil-k5','dac-no-plc-k5','dsal-k5']

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def write(p,obj):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')

def main():
    assert read(STUDY/'status.json')['state']=='completed', 'Wait for controller completion and W&B verification.'
    results=read(HERE/'results.json')
    assert len(results['rows'])==9 and len(results['aggregate'])==3 and not results['missing']
    manifest=read(STUDY/'manifest.json')
    for relative,expected in manifest['protected_seed0_sha256'].items():assert sha(ROOT/relative)==expected
    for relative,expected in read(STUDY/'verification/seed1-completed-scientific-files.json').items():assert sha(ROOT/relative)==expected
    import torch
    assert torch.__version__=='2.5.1+cpu'
    torch.set_num_threads(1)
    diagnostic=read(STUDY/'verification/seed-independence.json')['seeds']
    actual=[];evidence=[];weights=[]
    for seed in [0,1,2]:
        out=ROOT/'outputs/core-seed0' if seed==0 else STUDY/f'core-seed{seed}'
        checkpoint=ROOT/'checkpoints/core-seed0-resnet32.pt' if seed==0 else ROOT/f'checkpoints/multiseed-20261119/seed{seed}-resnet32.pt'
        state=torch.load(checkpoint,map_location='cpu',weights_only=False)
        assert state['epoch']==160 and state['signature']['seed']==seed
        assert state['signature']['class_order']==diagnostic[seed]['class_order']
        assert state['signature']['base_classes']==50
        assert state['signature']['dataset_revision']==manifest['dataset_metadata']['revision']
        model_hash=hashlib.sha256(b''.join(t.cpu().contiguous().numpy().tobytes() for _,t in sorted(state['model'].items()))).hexdigest()
        weights.append(model_hash)
        cache=read(out/'feature_cache.json')
        assert sha(ROOT/cache['path'])==cache['sha256']
        features=torch.load(ROOT/cache['path'],map_location='cpu',weights_only=False)
        assert features['identity']['checkpoint_sha256']==sha(checkpoint)
        assert features['identity']['class_order']==diagnostic[seed]['class_order']
        assert list(features['train_features'].shape)==[50000,64]
        assert list(features['test_features'].shape)==[10000,64]
        for split,count in [('train',500),('test',100)]:
            unique,counts=torch.unique(features[split+'_labels'],return_counts=True)
            assert unique.tolist()==list(range(100)) and counts.tolist()==[count]*100
        projections=[]
        for method in METHODS:
            cfg=read(out/method/'config.json')
            assert cfg['feature_identity']==features['identity']
            artifact=torch.load(out/method/'classifier.pt',map_location='cpu',weights_only=False)
            assert list(artifact['main'].shape)==[8192,100]
            assert list(artifact['projection'].shape)==[64,8192]
            assert (artifact['comp'] is None)==(method=='acil-k5')
            if artifact['comp'] is not None:assert list(artifact['comp'].shape)==[8192,100]
            ph=hashlib.sha256(artifact['projection'].contiguous().numpy().tobytes()).hexdigest()
            projections.append(ph)
            assert ph==diagnostic[seed]['projection_sha256']
        assert len(set(projections))==1
        remote=read(STUDY/f'verification/seed{seed}.json')
        assert len(remote)==4 and all(r['state']=='finished' and r['public'] and r['history_verified'] for r in remote)
        for method in ['base-training',*METHODS]:
            for name in ['config.json','summary.json','metrics.jsonl','phases.json','ratio_sweep.json']:
                source=out/method/name
                if not source.exists():continue
                destination=HERE/f'evidence/seed{seed}'/method/name
                destination.parent.mkdir(parents=True,exist_ok=True)
                assert not destination.exists() or destination.read_bytes()==source.read_bytes()
                if not destination.exists():shutil.copyfile(source,destination)
                evidence.append({'path':destination.relative_to(ROOT).as_posix(),'sha256':sha(destination)})
        shutil.copyfile(STUDY/f'verification/seed{seed}.json',HERE/f'verification/seed{seed}-remote.json')
        actual.append({'seed':seed,'checkpoint':checkpoint.relative_to(ROOT).as_posix(),
                       'checkpoint_sha256':sha(checkpoint),'model_weights_sha256':model_hash,
                       'feature_cache':cache,'projection_sha256':projections[0],
                       'train_shape':[50000,64],'test_shape':[10000,64],'paired_methods':METHODS})
    assert len(set(weights))==3
    for a in results['aggregate']:
        rows=[r for r in results['rows'] if r['method']==a['method']]
        assert sorted(r['seed'] for r in rows)==[0,1,2]
        for label,key in [('Abar','Abar'),('AK','AK')]:
            assert abs(a[label+'_mean']-statistics.mean(r[key] for r in rows))<1e-12
            assert abs(a[label+'_std_sample_ddof1']-statistics.stdev(r[key] for r in rows))<1e-12
    slide_qa=ROOT/'reports/milestone2_final/qa/v3/validation.json'
    q=read(slide_qa)
    for ext,key in [('pptx','candidate_sha256'),('pdf','pdf_sha256')]:
        assert sha(ROOT/f'reports/milestone2_final/DSAL_Milestone2_Lab1_Final_v3.{ext}')==q[key]
    receipts=[read(p) for p in (STUDY/'logs').glob('*-receipt.json')]
    science=[r for r in receipts if r['stage'] in ['seed1-backbone-features','seed2-backbone-features','seed1-core-three-methods','seed2-core-three-methods'] and r['exit_code']==0 and r['elapsed_seconds']>100]
    assert len(science)==4
    comparisons=[]
    for a in results['aggregate']:
        ref={'acil-k5':(66.30,57.78),'dsal-k5':(66.39,58.26)}.get(a['method'])
        if ref:
            comparisons.append({'method':a['method'],'paper_Abar':ref[0],'paper_AK':ref[1],
                                'Abar_gap_pp':a['Abar_mean']-ref[0],'AK_gap_pp':a['AK_mean']-ref[1],
                                'Abar_relative_deviation_pct':100*(a['Abar_mean']-ref[0])/ref[0],
                                'AK_relative_deviation_pct':100*(a['AK_mean']-ref[1])/ref[1]})
    audit={'completed_utc':datetime.now(timezone.utc).isoformat(),'passed':True,'seeds':actual,
           'verified_scientific_runs':9,'verified_backbone_runs':3,'independent_final_backbone_weights':True,
           'within_seed_projections_identical':True,'across_seed_projections_distinct':True,
           'seed0_and_seed1_protected_files_unchanged':True,'slides_v3_pptx_pdf_unchanged':True,
           'mean_sample_std_ddof1_recalculated':True,'paper_comparisons':comparisons,
           'science_wall_seconds_sum':sum(r['elapsed_seconds'] for r in science),
           'peak_sampled_rss_bytes':max(r['peak_sampled_rss_bytes'] for r in science),
           'peak_sampled_private_bytes':max(r['peak_sampled_private_bytes'] for r in science),
           'resource_sampling_interval_seconds':10,'source_support_revisions':manifest.get('source_revisions'),
           'evidence_files':evidence,'audit_script_sha256':sha(__file__)}
    write(HERE/'verification/completion-audit.json',audit)
    lines=['# Hoàn tất thí nghiệm ba seed','',
           'Đã hoàn thành ACIL, DAC không PLC và DS-AL cho seed 0, 1, 2. Chín run scientific và ba backbone run được xác minh finished, công khai, config/summary/history khớp dữ liệu cục bộ. Không còn thiếu thí nghiệm trong phạm vi này.',
           '', '## Kết quả mean ± sample SD','',
           'Accuracy tính bằng %, SD mẫu dùng ddof=1, n=3. Từng seed và URL W&B xem [RESULTS.md](RESULTS.md).',
           '', '| Phương pháp | A-bar mean ± SD (%) | A_K mean ± SD (%) |', '| --- | ---: | ---: |']
    for a in results['aggregate']:
        lines.append(f'| {a["method"]} | {a["Abar_mean"]:.4f} ± {a["Abar_std_sample_ddof1"]:.4f} | {a["AK_mean"]:.4f} ± {a["AK_std_sample_ddof1"]:.4f} |')
    lines+=['','## Đối chiếu bài báo','',
            'Nguồn: Table 1, CIFAR-100 / ResNet-32 / B50 / K5, giá trị không trong ngoặc; [DS-AL, AAAI 2024](https://doi.org/10.1609/aaai.v38i15.29670).',
            '', '| Phương pháp | A-bar bài báo | Chênh A-bar (pp) | Chênh tương đối (%) | A_K bài báo | Chênh A_K (pp) | Chênh tương đối (%) |',
            '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for c in comparisons:
        lines.append(f'| {c["method"]} | {c["paper_Abar"]:.2f} | {c["Abar_gap_pp"]:+.4f} | {c["Abar_relative_deviation_pct"]:+.3f} | {c["paper_AK"]:.2f} | {c["AK_gap_pp"]:+.4f} | {c["AK_relative_deviation_pct"]:+.3f} |')
    lines+=['','DAC không PLC là ablation chuyển sang CIFAR-100, không đối chiếu trực tiếp với ImageNet-Full Table 2. Ba seed còn ít để suy luận ý nghĩa thống kê hoặc nguyên nhân sai lệch.',
            'Seed 0 có 19 epoch CUDA trước khi resume sang CPU; seed 1/2 dùng CPU xuyên suốt. Vì vậy không coi độ biến thiên đo được là chỉ do seed hoặc so thời gian giữa seed như một benchmark phần cứng kiểm soát. Xem [PREFLIGHT.md](PREFLIGHT.md).',
            '', '## Thời gian và tài nguyên','',
            f'Tổng wall time của hai lượt backbone/features và hai suite ba phương pháp: {audit["science_wall_seconds_sum"]/3600:.4f} giờ. Không cộng thời gian chờ giữa các phiên, đồng bộ W&B hoặc diagnostic vào chi phí scientific này.',
            f'Peak RSS lấy mẫu: {audit["peak_sampled_rss_bytes"]/2**30:.3f} GiB; peak private memory lấy mẫu: {audit["peak_sampled_private_bytes"]/2**30:.3f} GiB. Lấy mẫu mỗi 10 giây nên có thể bỏ lỡ đỉnh ngắn. CPU i7-13620H, 8 PyTorch threads, torch 2.5.1+cpu.',
            'Từng công đoạn, cả lần sync bị lỗi và lần khôi phục, được giữ trong logs/receipts. [SYNC_RECOVERY.md](SYNC_RECOVERY.md) ghi bản sửa support; mã học thuật và hyperparameters không đổi.',
            '', '## Kiểm chứng và khả năng tái lập','',
            'Đã đọc lại checkpoint epoch 160, optimizer/scheduler/RNG, feature cache và chín classifier. Trong cùng seed, projection và feature identity khớp; giữa các seed, class order, khởi tạo và trọng số backbone cuối khác nhau. Không huấn luyện hoặc inference lại trong bước audit.',
            'Source snapshot ban đầu và snapshot support v2 được giữ riêng; provenance ghi Git HEAD, dirty state, hash source/config và thay đổi chỉ ở công cụ sync. Evidence nhẹ được sao chép byte-identical vào `evidence/seed0`, `evidence/seed1`, `evidence/seed2` và có SHA-256 ở `verification/completion-audit.json`.',
            'Seed 0 và số liệu seed 1 giữ nguyên hash. Không chạy thêm khảo sát K/buffer. Slide v3 PPTX/PDF giữ nguyên hash. Các khảo sát K/buffer vẫn chỉ có seed 0 và không được gộp vào mean/SD ba seed.',
            '', '## Việc tiếp theo','',
            '- Cập nhật slide khi nhóm yêu cầu; chưa sửa slide trong đợt này.',
            '- Có thể công bố source/config/evidence nhẹ và báo cáo lên GitHub sau khi rà soát; không đưa checkpoint, data, `.env` hay credentials lên Git.',
            '- Giữ bản sao checkpoint và feature cache để tái lập hoặc mở rộng sau.']
    (HERE/'COMPLETION_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in audit.items() if k not in ['evidence_files','seeds','source_support_revisions']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
