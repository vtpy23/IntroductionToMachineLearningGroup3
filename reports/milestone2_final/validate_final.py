"""Read-only checks for the reviewed seed-0 deck; writes a local QA report only."""
import hashlib
import json
import math
import netrc
import re
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from pypdf import PdfReader

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BUILD=HERE/'.build'
PPTX=HERE/'DSAL_Milestone2_Lab1_Final.pptx'
PDF=HERE/'DSAL_Milestone2_Lab1_Final.pdf'
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
    'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
content=json.loads((HERE/'slide_content.json').read_text(encoding='utf-8'))
evidence=json.loads((HERE/'assets/verified_evidence.json').read_text(encoding='utf-8'))
runs={r['name']:r for r in evidence['experiments']}
checks={}
def check(name,condition,detail=True):
    assert condition,name
    checks[name]=detail
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def experiment_path(run):
    original=ROOT/run['directory']
    return original if original.exists() else ROOT/'experiments/evidence'/run['name']
def texts(root):return '\n'.join(t.text or '' for t in root.findall('.//a:t',NS))
def same_numbers(left,right):
    return len(left)==len(right) and all(math.isclose(float(a),float(b),rel_tol=1e-12,abs_tol=1e-13) for a,b in zip(left,right))

pdf=PdfReader(PDF)
check('pdf_pages',len(pdf.pages)==40,len(pdf.pages))
check('pptx_under_20_MB',PPTX.stat().st_size<20_000_000,PPTX.stat().st_size)
check('moodle_alias_identical',sha(PPTX)==sha(HERE/'03.pptx'))
notes_counts=[];native_tables=0;linked_runs=set();slide_text={}
with ZipFile(PPTX) as z:
    slides=[n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)]
    check('slide_count',len(slides)==40,len(slides))
    # XML parsing also detects malformed or incorrectly encoded package parts.
    for part in z.namelist():
        if part.endswith(('.xml','.rels')):ET.fromstring(z.read(part))
    for s in content['slides']:
        i=s['number'];root=ET.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
        text=texts(root);slide_text[i]=text
        notes=texts(ET.fromstring(z.read(f'ppt/notesSlides/notesSlide{i}.xml')))
        count=len(notes.split());notes_counts.append(count)
        check(f'notes_{i}',0<count<=500,count)
        check(f'title_{i}',s['title'] in text or (i==1 and 'DS-AL' in text))
        check(f'not_references_slide_{i}',s['title'].strip().lower() not in ['references','tài liệu tham khảo'])
        check(f'no_replacement_character_{i}','\ufffd' not in text+notes and '???' not in text+notes)
        for source in s['refs']:
            check(f'citation_{i}_{source}',f'[{source}]' in text and content['references'][source]['url'] in notes)
        relpart=f'ppt/slides/_rels/slide{i}.xml.rels'
        rels=ET.fromstring(z.read(relpart))
        targets={r.attrib['Target'] for r in rels if r.attrib.get('Type','').endswith('/hyperlink')}
        for name in s['runs']:
            url=runs[name]['verification']['url'];linked_runs.add(name)
            check(f'run_{i}_{name}',url in text and url in notes and url in targets)
        native_tables+=len(root.findall('.//a:tbl',NS))
        page_text=pdf.pages[i-1].extract_text() or ''
        check(f'pdf_nonempty_{i}',len(page_text)>100,len(page_text))
        for name in s['runs']:
            check(f'pdf_run_id_{i}_{name}',runs[name]['verification']['run_id'] in page_text)
    charts=sorted([n for n in z.namelist() if re.fullmatch(r'ppt/charts/chart\d+\.xml',n)],key=lambda n:int(re.search(r'chart(\d+)',n).group(1)))
    check('native_chart_count',len(charts)==8,len(charts))
    embeddings=[n for n in z.namelist() if n.startswith('ppt/embeddings/') and n.endswith('.xlsx')]
    check('chart_workbooks',len(embeddings)==8,len(embeddings))
    history=[json.loads(l) for l in (experiment_path(runs['base-training'])/'metrics.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
    a=runs['acil-k5']['summary'];d=runs['dsal-k5']['summary']
    phases=lambda n:[p['accuracy'] for p in runs[n]['phases']]
    expected=[
        [[r['base/train_accuracy'] for r in history],[r['base/test_accuracy'] for r in history]],
        [[0,0,0,1,2],[math.tanh(v) for v in [-2,-1,0,1,2]]],
        [phases('dsal-k5')],
        [[66.30,66.39],[a['average_accuracy'],d['average_accuracy']]],
        [[57.78,58.26],[a['last_accuracy'],d['last_accuracy']]],
        [phases(n) for n in ['acil-k5','dac-no-plc-k5','dsal-k5']],
        [[runs[n]['summary']['last_accuracy'] for n in ['buffer-512','buffer-1024','buffer-2048','dsal-k5']]],
        [[r['comp_relative_difference'] for r in evidence['mechanisms']['phase-dependence'] if r['seed']==seed] for seed in range(3)]
    ]
    for j,(part,exp) in enumerate(zip(charts,expected),1):
        root=ET.fromstring(z.read(part))
        observed=[[v.text for v in series.findall('c:val//c:numCache/c:pt/c:v',NS)] for series in root.findall('.//c:ser',NS)]
        check(f'chart_{j}_values',len(observed)==len(exp) and all(same_numbers(x,y) for x,y in zip(observed,exp)))
        if root.find('.//c:barChart',NS) is not None:
            minimum=root.find('.//c:valAx/c:scaling/c:min',NS)
            check(f'bar_{j}_zero_baseline',minimum is not None and minimum.attrib['val']=='0')
    # Scan authenticated passwords in memory only; never output a credential.
    passwords=[]
    for netpath in [Path.home()/'_netrc',Path.home()/'.netrc']:
        if netpath.exists():
            passwords.extend(v[2].encode() for v in netrc.netrc(str(netpath)).hosts.values() if v[2] and len(v[2])>=16)
    leaks=[]
    for p in HERE.rglob('*'):
        if p.is_file() and p.suffix.lower() in {'.py','.mjs','.md','.json','.log','.txt','.ps1','.pdf','.pptx'}:
            data=p.read_bytes()
            if any(key in data for key in passwords):leaks.append(str(p.relative_to(HERE)))
    for part in z.namelist():
        if part.endswith(('.xml','.rels')) and any(key in z.read(part) for key in passwords):leaks.append(part)
    check('credential_scan_no_leaks',not leaks,{'files_with_leaks':len(leaks),'credential_source_available':bool(passwords)})

for r in runs.values():
    v=r['verification']
    check('verified_'+r['name'],v['status']=='VERIFIED' and v['state']=='finished' and v['public'] and v['base_url']=='https://api.forge.coreweave.com')
    if 'summary_sha256' in r:
        check('summary_unchanged_'+r['name'],sha(experiment_path(r)/'summary.json')==r['summary_sha256'])
    local=json.loads((experiment_path(r)/'summary.json').read_text(encoding='utf-8'))
    check('summary_matches_snapshot_'+r['name'],local==r['summary'])

for i,strings in {26:['58.26','58.32','58.37'],28:['-1.39','-2.39%'],29:['56.24','56.87','+0,63'],31:['56.83','0,04'],33:['51.46','0.901','86.513'],35:['56,87%','+0,31','+0,63']}.items():
    for token in strings:
        check(f'critical_number_{i}_{token}',token in slide_text[i] and token in (pdf.pages[i-1].extract_text() or ''))

fit=json.loads((BUILD/'text-fit.json').read_text(encoding='utf-8-sig'))
check('powerpoint_text_fit',not any(r['Overflow'] for r in fit),{'checked':len(fit),'overflow_candidates':0})
geometry=json.loads((BUILD/'geometry.json').read_text(encoding='utf-8'))
bad=[x for x in geometry if x['x']<-.01 or x['y']<-.01 or x['x']+x['w']>13.3434 or x['y']+x['h']>7.51]
check('no_out_of_canvas_content',not bad)
protected_path=BUILD/'protected-before.json'
if protected_path.exists():
    protected=json.loads(protected_path.read_text(encoding='utf-8'))
    changed=[p for p,h in protected.items() if sha(ROOT/p)!=h]
    check('protected_experiment_files_unchanged',not changed,len(protected))
else:
    check('original_outputs_not_available_in_clone',True,'Check byte-identical published snapshots instead; no claim about unavailable weights.')
manifest=json.loads((ROOT/'experiments/evidence/manifest.json').read_text(encoding='utf-8'))
check('published_evidence_hashes',all(sha(ROOT/x['published'])==x['sha256'] for x in manifest['files']),len(manifest['files']))
check('all_slides_rendered',all((BUILD/'rendered'/f'slide-{i:02d}.png').exists() for i in range(1,41)))
result={'status':'PASS','snapshot_date':'2026-11-19','slides':40,'notes_max_words':max(notes_counts),
        'native_charts':8,'native_tables':native_tables,'linked_runs':len(linked_runs),'verified_runs':len(runs),
        'pptx_sha256':sha(PPTX),'pdf_sha256':sha(PDF),'checks':checks,
        'limits':['Visual overlap review is manual; COM height check alone is insufficient.',
                  'Scientific scope/publication conditions are in SLIDE_REVIEW_REPORT.md.']}
(BUILD/'final-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['checks','limits']},ensure_ascii=False,indent=2))
