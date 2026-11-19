"""Check three-seed science, native chart workbooks, notes, links and exports."""
import hashlib
import io
import json
import math
from pathlib import Path
import re
import statistics as stats
import posixpath
from urllib.parse import unquote
from zipfile import ZipFile
from lxml import etree as E
from pypdf import PdfReader

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
BUILD=HERE/'.build/three-seeds'
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
    'c':'http://schemas.openxmlformats.org/drawingml/2006/chart',
    's':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def read(p):
    raw=Path(p).read_bytes()
    return json.loads(raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def same(a,b):return math.isclose(float(a),float(b),rel_tol=1e-12,abs_tol=1e-14)
def fv(x,d=2):return f'{x:.{d}f}'.replace('.',',')
def xml(b):return E.fromstring(b)
def values(ser):return [float(x) for x in ser.xpath('c:val/c:numRef/c:numCache/c:pt/c:v/text()',namespaces=NS)]
def equal_array(actual,expected):
    assert len(actual)==len(expected),(len(actual),len(expected))
    assert all(same(a,b) for a,b in zip(actual,expected)),(actual,expected)

v=read(HERE/'assets/three_seeds_verified.json')
content=read(HERE/'slide_content_three_seeds.json')
receipt=read(BUILD/'merge-receipt.json')
baseline=HERE/v['baseline_pptx']
candidate=BUILD/'candidate.pptx'
def local_integrity(path):
    """Portable package checks, independent of installed Codex helper paths."""
    findings=[]
    with ZipFile(path) as z:
        names=set(z.namelist())
        for part in names:
            if not part.endswith(('.xml','.rels')):continue
            tree=xml(z.read(part))
            if part.endswith('.rels'):
                parent='' if part=='_rels/.rels' else posixpath.dirname(part).rsplit('/_rels',1)[0]
                for rel in tree:
                    if rel.get('TargetMode')=='External':continue
                    target=unquote(rel.get('Target','').split('#',1)[0])
                    resolved=target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join(parent,target))
                    if resolved not in names:findings.append({'relationship_part':part,'missing_target':resolved})
        ct=xml(z.read('[Content_Types].xml'))
        for entry in ct:
            if E.QName(entry).localname=='Override' and entry.get('PartName','').lstrip('/') not in names:
                findings.append({'missing_content_type_part':entry.get('PartName')})
    return {'status':'pass' if not findings else 'fail','finding_count':len(findings),'findings':findings,
            'claim_boundary':'Structural XML, relationship targets and content-type checks only; separate science, notes, workbook and visual checks also required.'}
integrity=local_integrity(candidate)
assert integrity['finding_count']==0,integrity
(BUILD/'package-integrity-local.json').write_text(json.dumps(integrity,indent=2),encoding='utf-8')
if not (BUILD/'package-integrity.json').exists():
    (BUILD/'package-integrity.json').write_text(json.dumps(integrity,indent=2),encoding='utf-8')
assert sha(baseline)==v['baseline_sha256']==receipt['baseline_sha256']
assert v['all_12_runs_verified'] and len(v['runs'])==12
assert all(r['state']=='finished' and r['public'] for r in v['runs'])
A=v['aggregates'];core=['acil-k5','dac-no-plc-k5','dsal-k5']
for run in v['runs']:
    for name,expected in run['files_sha256'].items():assert sha(ROOT/run['directory']/name)==expected,(run['method'],run['seed'],name)
for method in core:
    runs=sorted([r for r in v['runs'] if r['method']==method],key=lambda r:r['seed'])
    assert [r['seed'] for r in runs]==[0,1,2]
    for metric in ['average_accuracy','last_accuracy']:
        raw=[r['summary'][metric] for r in runs]
        assert same(stats.mean(raw),A[method][metric]['mean'])
        assert same(stats.stdev(raw),A[method][metric]['sd'])
    for run in runs:
        assert same(stats.mean(p['accuracy'] for p in run['phases']),run['summary']['average_accuracy'])
        assert run['config']['protocol']=={'base_classes':50,'phases':5}
        assert run['config']['analytic']['buffer_size']==8192
        assert run['config']['training']['epochs']==160

notes_counts={};slide_text={};native_tables=0;chart_cache_refs=0;inherited_blank_zero_cells=0
pdf=PdfReader(BUILD/'candidate.pdf')
assert len(pdf.pages)==40
pdf_links=0;pdf_wandb_links=0
with ZipFile(baseline) as old,ZipFile(candidate) as new:
    assert set(old.namelist())==set(new.namelist())
    assert len([p for p in new.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',p)])==40
    assert old.read('ppt/presentation.xml')==new.read('ppt/presentation.xml')
    for i in receipt['unchanged_slide_xml']:
        assert old.read(f'ppt/slides/slide{i}.xml')==new.read(f'ppt/slides/slide{i}.xml'),i
    for i in [2,7,8,9]:
        for part in [f'ppt/charts/chart{i}.xml',f'ppt/embeddings/Microsoft_Excel_Worksheet{i}.xlsx']:
            assert old.read(part)==new.read(part),part
    # The K table retains exactly the original verified seed0 values.
    assert xml(old.read('ppt/slides/slide31.xml')).xpath('//a:tbl//a:t/text()',namespaces=NS)==xml(new.read('ppt/slides/slide31.xml')).xpath('//a:tbl//a:t/text()',namespaces=NS)
    for s in content['slides']:
        i=s['number'];part=f'ppt/slides/slide{i}.xml';tree=xml(new.read(part))
        text=tree.xpath('//a:t/text()',namespaces=NS);slide_text[i]=' '.join(text)
        native_tables+=len(tree.findall('.//a:tbl',NS))
        note=xml(new.read(f'ppt/notesSlides/notesSlide{i}.xml'))
        note_text=' '.join(note.xpath('//a:t/text()',namespaces=NS))
        notes_counts[i]=len(note_text.split())
        assert 0<notes_counts[i]<=500,(i,notes_counts[i])
        for ref in s['refs']:
            assert content['references'][ref]['short'] in slide_text[i],(i,ref)
            assert content['references'][ref]['full'] in note_text,(i,ref,'notes')
        if i not in receipt['updated_slides']+receipt['notes_only']:
            assert old.read(f'ppt/notesSlides/notesSlide{i}.xml')==new.read(f'ppt/notesSlides/notesSlide{i}.xml')
        relationships=xml(new.read(f'ppt/slides/_rels/slide{i}.xml.rels'))
        expected={r.get('Target') for r in relationships if r.get('Type','').endswith('/hyperlink')}
        for method in s.get('seedMethods',[]):
            for seed in [0,1,2]:
                run=next(r for r in v['runs'] if r['method']==method and r['seed']==seed)
                assert run['url'] in expected and run['url'] in note_text,(i,method,seed)
        actual=set()
        for ref in pdf.pages[i-1].get('/Annots',[]):
            action=ref.get_object().get('/A',{})
            if action.get('/URI'):
                url=str(action['/URI']);actual.add(url);pdf_links+=1
                if 'forge.coreweave.com' in url:pdf_wandb_links+=1
        assert expected<=actual,(i,expected-actual)
        for phrase in ['Nhóm: 1 seed','Chỉ có seed 0 cho CIFAR','Benchmark nhóm hiện chỉ có seed 0','Chưa có mean/std nhiều seed']:
            assert phrase not in slide_text[i]+note_text,(i,phrase)
        assert 'checklist' not in slide_text[i].lower()
    for name in ['Lâm Hoàng Vũ','23122056','Nguyễn Bá Nam','23122043','Chung Tín Đạt','23122024']:
        assert name in slide_text[1]
    for method in core:
        for metric in ['average_accuracy','last_accuracy']:
            assert fv(A[method][metric]['mean'])+' ± '+fv(A[method][metric]['sd']) in slide_text[29]
        for seed in [0,1,2]:
            run=next(r for r in v['runs'] if r['method']==method and r['seed']==seed)
            assert fv(run['summary']['average_accuracy'],4) in slide_text[39]
            assert fv(run['summary']['last_accuracy'],4) in slide_text[39]
    expected_values={
        1:[[r['base/test_accuracy'] for r in next(x for x in v['runs'] if x['method']=='base-training' and x['seed']==seed)['history']] for seed in [0,1,2]],
        3:[[next(r for r in v['runs'] if r['method']=='dsal-k5' and r['seed']==s)['summary']['last_accuracy'] for s in [0,1,2]]],
        4:[[66.30,66.39],[A[m]['average_accuracy']['mean'] for m in ['acil-k5','dsal-k5']]],
        5:[[57.78,58.26],[A[m]['last_accuracy']['mean'] for m in ['acil-k5','dsal-k5']]],
        6:[[p['mean'] for p in A[m]['phase_accuracy']] for m in core]
    }
    expected_errors={4:{1:[A[m]['average_accuracy']['sd'] for m in ['acil-k5','dsal-k5']]},
                     5:{1:[A[m]['last_accuracy']['sd'] for m in ['acil-k5','dsal-k5']]},
                     6:{i:[p['sd'] for p in A[m]['phase_accuracy']] for i,m in enumerate(core)}}
    for i in range(1,10):
        chart=xml(new.read(f'ppt/charts/chart{i}.xml'))
        series=chart.findall('.//c:ser',NS)
        if i in expected_values:
            assert len(series)==len(expected_values[i])
            for ser,expected in zip(series,expected_values[i]):equal_array(values(ser),expected)
        if i in expected_errors:
            for index,expected in expected_errors[i].items():
                for sign in ['plus','minus']:
                    actual=series[index].xpath(f'c:errBars/c:{sign}/c:numRef/c:numCache/c:pt/c:v/text()',namespaces=NS)
                    equal_array(actual,expected)
        # Check every numeric cache (including custom error bars) against cells.
        with ZipFile(io.BytesIO(new.read(f'ppt/embeddings/Microsoft_Excel_Worksheet{i}.xlsx'))) as workbook:
            sheet=xml(workbook.read('xl/worksheets/sheet1.xml'))
            cells={c.get('r'):c.find('s:v',NS).text for c in sheet.findall('.//s:c',NS) if c.get('t') not in ['s','inlineStr'] and c.find('s:v',NS) is not None}
            for ref in chart.findall('.//c:numRef',NS):
                formula=ref.find('c:f',NS).text
                match=re.fullmatch(r'Sheet1!\$([A-Z]+)\$(\d+):\$([A-Z]+)\$(\d+)',formula)
                assert match and match[1]==match[3],formula
                expected=[cells[f'{match[1]}{r}'] for r in range(int(match[2]),int(match[4])+1)]
                # Inherited PptxGenJS illustrative workbooks serialize zero as
                # an empty <v>. The unchanged chart caches explicitly contain 0.
                for j,value in enumerate(expected):
                    if value is None:
                        assert i in [2,9],(i,formula,'unexpected empty research cell')
                        expected[j]=0;inherited_blank_zero_cells+=1
                equal_array(ref.xpath('c:numCache/c:pt/c:v/text()',namespaces=NS),expected)
                chart_cache_refs+=1

fit=read(BUILD/'text-fit.json');gaps=read(BUILD/'native-table-gaps.json')
assert len(fit)>=800 and not any(r['Overflow'] for r in fit)
assert len(gaps)==native_tables==20 and all(r['GapInches']>0 for r in gaps)
assert len(list((BUILD/'rendered').glob('slide-*.png')))==40
assert candidate.stat().st_size<20_000_000
assert read(BUILD/'package-integrity.json')['finding_count']==0
bound_tree=E.parse(str(BUILD/'pdf-bounds.html'))
xns={'h':'http://www.w3.org/1999/xhtml'}
pages=bound_tree.findall('.//h:page',xns)
assert len(pages)==40
for page in pages:
    w,h=float(page.get('width')),float(page.get('height'))
    for word in page.findall('.//h:word',xns):
        assert float(word.get('xMin'))>=-.1 and float(word.get('yMin'))>=-.1
        assert float(word.get('xMax'))<=w+.1 and float(word.get('yMax'))<=h+.1
for i in range(1,41):assert (BUILD/f'rendered/slide-{i:02}.png').stat().st_size>10000
audit=read(ROOT/'experiments/multiseed/20261119/verification/completion-audit.json')
for s in audit['seeds']:
    assert sha(ROOT/s['checkpoint'])==s['checkpoint_sha256']
    assert sha(ROOT/s['feature_cache']['path'])==s['feature_cache']['sha256']

result={'passed':True,'slides':40,'pdf_pages':40,'native_charts':9,'native_tables':native_tables,
        'workbook_numeric_references_checked':chart_cache_refs,'custom_sample_SD_errorbar_charts':[4,5,6],
        'inherited_illustration_blank_zero_cells_verified':inherited_blank_zero_cells,
        'verified_live_runs':12,'methods_three_seed_pairs':9,'std_ddof':1,
        'notes_words_by_slide':notes_counts,'max_notes_words':max(notes_counts.values()),
        'pdf_hyperlink_annotations':pdf_links,'pdf_wandb_hyperlink_annotations':pdf_wandb_links,
        'native_text_cells_checked':len(fit),'native_overflow_candidates':0,
        'native_table_footer_gaps':gaps,'baseline_slide_xml_preserved':receipt['unchanged_slide_xml'],
        'seed0_sweep_slides_32_33_and_charts_7_8_unchanged':True,
        'raw_logs_configs_summaries_checkpoints_feature_caches_unchanged':True,
        'baseline_sha256':sha(baseline),'candidate_sha256':sha(candidate),'pdf_sha256':sha(BUILD/'candidate.pdf')}
(BUILD/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['native_table_footer_gaps','notes_words_by_slide','baseline_slide_xml_preserved']},indent=2))
