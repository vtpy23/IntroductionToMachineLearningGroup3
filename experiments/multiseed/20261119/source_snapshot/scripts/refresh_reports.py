"""Refresh measured results and export PPTX/PDF using the retained PptxGenJS source."""
import argparse
import shutil
import subprocess
import sys


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group-id',default='03')
    parser.add_argument('--from-wandb',action='store_true')
    parser.add_argument('--no-pdf',action='store_true')
    args=parser.parse_args()
    if args.from_wandb:
        subprocess.run([sys.executable,'-m','scripts.fetch_wandb'],check=True)
    subprocess.run([sys.executable,'-m','scripts.summarize'],check=True)
    subprocess.run(['node','reports/build_slides.mjs','--group-id',args.group_id],check=True)
    if not args.no_pdf:
        powershell=shutil.which('powershell') or shutil.which('pwsh')
        if not powershell:
            raise SystemExit('PPTX generated. PDF rendering needs Windows PowerPoint and scripts/render_reports.ps1.')
        subprocess.run([powershell,'-NoProfile','-ExecutionPolicy','Bypass','-File',
                        'scripts/render_reports.ps1','-GroupId',args.group_id],check=True)
        subprocess.run([sys.executable,'-m','scripts.validate_reports','--group-id',args.group_id],check=True)


if __name__=='__main__':
    main()
