"""Validate presentation artifacts and frozen measurements; no experiment execution."""
import hashlib
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile
from pypdf import PdfReader

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BUILD=HERE/'.build/v2'
PPTX=BUILD/'candidate.pptx'
PDF=BUILD/'candidate.pdf'
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main','c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
content=json.loads((HERE/'slide_content_v2.json').read_text(encoding='utf-8'))
evidence=json.loads((HERE/'assets/verified_evidence.json').read_text(encoding='utf-8'))
runs={r['name']:r for r in evidence['experiments']}
checks={}
def check(name,value,details=True):
    assert value,name
    checks[name]=details
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def text(x):return '\n'.join(t.text or '' for t in x.findall('.//a:t',NS))
def numeric_series(z,part):
    root=ET.fromstring(z.read(part))
    return [[float(v.text) for v in s.findall('c:val//c:numCache/c:pt/c:v',NS)] for s in root.findall('.//c:ser',NS)]
def close(a,b):return len(a)==len(b) and all(len(x)==len(y) and all(math.isclose(u,v,rel_tol=1e-12,abs_tol=1e-13) for u,v in zip(x,y)) for x,y in zip(a,b))

pdf=PdfReader(PDF)
check('40_pages',len(pdf.pages)==40)
check('pptx_under_20MB',PPTX.stat().st_size<20_000_000,PPTX.stat().st_size)
counts=[];all_runs=set();citation_sizes=[];run_sizes=[];all_text={}
with ZipFile(PPTX) as z,ZipFile(HERE/'DSAL_Milestone2_Lab1_Final.pptx') as old:
    check('40_slides',len([n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)])==40)
    for part in z.namelist():
        if part.endswith(('.xml','.rels')):ET.fromstring(z.read(part))
    for s in content['slides']:
        i=s['number'];root=ET.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
        visible=text(root);all_text[i]=visible
        notes=text(ET.fromstring(z.read(f'ppt/notesSlides/notesSlide{i}.xml')))
        counts.append(len(notes.split()))
        check(f'notes_{i}',0<counts[-1]<=500,counts[-1])
        check(f'no_encoding_damage_{i}','\ufffd' not in visible+notes and '???' not in visible+notes)
        check(f'not_references_slide_{i}',s['title'].lower() not in ['references','tài liệu tham khảo'])
        rels=ET.fromstring(z.read(f'ppt/slides/_rels/slide{i}.xml.rels'))
        targets={r.attrib['Target'] for r in rels if r.attrib.get('Type','').endswith('/hyperlink')}
        pdf_links={str(a.get_object().get('/A',{}).get('/URI','')) for a in pdf.pages[i-1].get('/Annots',[])}
        for n in s['runs']:
            u=runs[n]['verification']['url'];all_runs.add(n)
            check(f'run_link_{i}_{n}',u in targets and u in notes and u in pdf_links)
        for r in s['refs']:
            check(f'citation_{i}_{r}',f'[{r}]' in visible and content['references'][r]['url'] in notes)
        for shape in root.findall('.//p:sp',NS):
            st=text(shape)
            if not st:continue
            sizes=[int(x.attrib['sz'])/100 for x in shape.findall('.//a:rPr',NS) if 'sz' in x.attrib]
            if st.startswith('['):citation_sizes+=sizes
            if shape.find('.//a:hlinkClick',NS) is not None and not st.startswith('['):run_sizes+=sizes
        page_text=pdf.pages[i-1].extract_text() or ''
        check(f'pdf_nonempty_{i}',len(page_text)>100)
        if i in [26,28,29,31]:
            old_tables=[text(t) for t in ET.fromstring(old.read(f'ppt/slides/slide{i}.xml')).findall('.//a:tbl',NS)]
            new_tables=[text(t) for t in root.findall('.//a:tbl',NS)]
            check(f'verified_table_unchanged_{i}',old_tables==new_tables)
    charts=[n for n in z.namelist() if re.fullmatch(r'ppt/charts/chart\d+\.xml',n)]
    check('nine_native_charts',len(charts)==9)
    check('nine_embedded_workbooks',len([n for n in z.namelist() if n.startswith('ppt/embeddings/') and n.endswith('.xlsx')])==9)
    for new_i,old_i in [(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(9,8)]:
        check(f'chart_values_preserved_{new_i}',close(numeric_series(z,f'ppt/charts/chart{new_i}.xml'),numeric_series(old,f'ppt/charts/chart{old_i}.xml')))
    fit=[runs[n]['summary']['fit_seconds'] for n in ['buffer-512','buffer-1024','buffer-2048','dsal-k5']]
    check('new_time_chart_exact_values',close(numeric_series(z,'ppt/charts/chart8.xml'),[fit]))
    chart6=ET.fromstring(z.read('ppt/charts/chart6.xml'))
    check('distinct_line_styles',[x.attrib['val'] for x in chart6.findall('.//c:ser/c:spPr/a:ln/a:prstDash',NS)]==['dash','dashDot','solid'])
    check('distinct_markers',[x.attrib['val'] for x in chart6.findall('.//c:ser/c:marker/c:symbol',NS)]==['square','triangle','circle'])
    for i in [4,5,7,8]:
        root=ET.fromstring(z.read(f'ppt/charts/chart{i}.xml'))
        check(f'bar_zero_baseline_{i}',root.find('.//c:valAx/c:scaling/c:min',NS).attrib['val']=='0')
    for i in [11,12,13,14,15,16,17,18,19,36]:
        def academic_shapes(package):
            root=ET.fromstring(package.read(f'ppt/slides/slide{i}.xml'))
            return [text(s) for s in root.findall('.//p:sp',NS) if text(s) and not text(s).startswith('[') and not re.fullmatch(r'\d+ / \d+',text(s))]
        check(f'method_formula_copy_unchanged_{i}',academic_shapes(z)==academic_shapes(old))

check('citation_font_at_least_12pt',citation_sizes and min(citation_sizes)>=12,min(citation_sizes))
check('run_link_font_at_least_14pt',run_sizes and min(run_sizes)>=14,min(run_sizes))
for member in [('Lâm Hoàng Vũ','23122056'),('Nguyễn Bá Nam','23122043'),('Chung Tín Đạt','23122024')]:
    check('cover_'+member[1],all(t in all_text[1] for t in member) and all(t in pdf.pages[0].extract_text() for t in member))
for i in [22,29]:check(f'adapted_E2_{i}','CIFAR' in all_text[i] and 'ImageNet-Full' in all_text[i] and 'Table 2' in all_text[i])
for i in [25,40]:check(f'no_internal_checklist_{i}',not any(token in all_text[i].lower() for token in ['private','cần công khai','trước khi nộp','cần nhóm','chưa push','đã có']))
check('buffer_values_visible',all(t in all_text[33] for t in ['51.46','53.36','54.97','56.87','0.901','1.672','5.177','86.513']))
check('reference_scope_not_overclaimed','tổng hợp' in all_text[37] and 'chưa xác định nguyên nhân gap CIFAR' in all_text[37])
check('40_rendered_pages',all((BUILD/'rendered'/f'slide-{i:02d}.png').exists() for i in range(1,41)))
preserved=json.loads((BUILD/'preserved-before.json').read_text(encoding='utf-8'))
check('previous_files_unchanged',all(digest(ROOT/p)==h for p,h in preserved.items()),len(preserved))
protected=json.loads((HERE/'.build/protected-before.json').read_text(encoding='utf-8'))
check('58_original_experiment_files_unchanged',all(digest(ROOT/p)==h for p,h in protected.items()),len(protected))
geometry=json.loads((BUILD/'geometry.json').read_text(encoding='utf-8'))
check('no_out_of_canvas_shapes',all(g['x']>=0 and g['y']>=0 and g['x']+g['w']<=13.3434 and g['y']+g['h']<=7.51 for g in geometry))
bounds=ET.parse(BUILD/'pdf-bounds.html').getroot()
outside=[]
for page in bounds.iter('{http://www.w3.org/1999/xhtml}page'):
    w=float(page.attrib['width']);h=float(page.attrib['height'])
    for word in page.iter('{http://www.w3.org/1999/xhtml}word'):
        if float(word.attrib['xMin'])<0 or float(word.attrib['xMax'])>w+.1 or float(word.attrib['yMin'])<0 or float(word.attrib['yMax'])>h+.1:outside.append(word.text)
check('pdf_words_within_page',not outside)
result={'status':'PASS','slides':40,'max_notes_words':max(counts),'linked_runs':len(all_runs),'native_charts':9,
        'citation_min_pt':min(citation_sizes),'run_label_min_pt':min(run_sizes),
        'pptx_sha256':digest(PPTX),'pdf_sha256':digest(PDF),'checks':checks,
        'render_engine':'LibreOffice Portable 26.2.4 + Poppler; PowerPoint COM unavailable because Office is unlicensed.',
        'limits':['No claim of a native PowerPoint rerender in this revision.','Visual review complements structural tests.','Benchmark remains one seed; adapted E2 acceptance is unconfirmed.']}
(BUILD/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['checks','limits']},ensure_ascii=False,indent=2))
