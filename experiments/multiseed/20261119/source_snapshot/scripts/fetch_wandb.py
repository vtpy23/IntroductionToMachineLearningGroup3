"""Fetch completed benchmark summaries from the configured W&B project."""
import argparse
import os
from pathlib import Path

from src.utils.reproducibility import write_json


def main():
    from dotenv import load_dotenv
    load_dotenv()
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--entity',default=os.environ.get('WANDB_ENTITY'))
    parser.add_argument('--project',default=os.environ.get('WANDB_PROJECT','intro-ml-group3-dsal'))
    args=parser.parse_args()
    if not args.entity:
        raise SystemExit('Set WANDB_ENTITY in .env or pass --entity. Authenticate with wandb login.')
    import wandb
    api=wandb.Api()
    rows=[]
    for run in api.runs(f'{args.entity}/{args.project}'):
        summary=dict(run.summary)
        config=dict(run.config)
        if run.state!='finished' or not summary.get('completed') or 'last_accuracy' not in summary:
            continue
        analytic=config.get('analytic',{})
        dataset=config.get('dataset',{})
        method='dsal' if analytic.get('use_compensation',True) else 'acil'
        phases=config.get('protocol',{}).get('phases')
        eligible=(not dataset.get('train_per_class') and not dataset.get('test_per_class')
                  and config.get('training',{}).get('epochs')==160
                  and analytic.get('buffer_size')==8192 and analytic.get('plc',True))
        from scripts.summarize import PAPER
        paper=PAPER.get(phases,{}).get(method) if eligible else None
        rows.append({'run':f'wandb/{run.name}','method':method,'protocol':summary.get('protocol'),
                     'phases':phases,'buffer_size':analytic.get('buffer_size'),'seed':config.get('seed'),
                     'average_accuracy':summary['average_accuracy'],'last_accuracy':summary['last_accuracy'],
                     'fit_seconds':summary.get('fit_seconds'),'wandb_url':run.url,
                     'paper_average_accuracy':paper[0] if paper else None,
                     'paper_last_accuracy':paper[1] if paper else None,
                     'last_gap_percentage_points':summary['last_accuracy']-paper[1] if paper else None,
                     'last_relative_deviation_percent':100*(summary['last_accuracy']-paper[1])/paper[1] if paper else None,
                     'submission_ready':bool(summary.get('public_visibility_verified',False)),
                     'source':'completed W&B run summary'})
    write_json('experiments/reproduction/wandb_results.json',rows)
    print(f'Fetched {len(rows)} completed classification runs')


if __name__=='__main__':
    main()
