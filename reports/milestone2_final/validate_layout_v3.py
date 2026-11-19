"""Check layout-only changes against v2 and the native PowerPoint exports."""
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
BUILD = HERE / '.build/v3'
NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart'}
def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8*1024*1024), b''):
            h.update(block)
    return h.hexdigest()

receipt = read_json(BUILD / 'repair.json')
protected_inputs = [HERE / receipt['source'], HERE / 'DSAL_Milestone2_Lab1_Final_v2.pdf',
                    HERE / 'assets/verified_evidence.json']
for path in protected_inputs:
    assert sha(path) == receipt['source_sha256'][path.name], path

attribute_changes = []
def compare_elements(old, new, part):
    assert old.tag == new.tag and old.text == new.text and old.tail == new.tail, (part, old.tag)
    assert len(old) == len(new), (part, old.tag)
    for attr in set(old.attrib) | set(new.attrib):
        before, after = old.get(attr), new.get(attr)
        if before == after:
            continue
        tag = E.QName(old).localname
        if part.startswith('ppt/slides/'):
            permitted = ((tag == 'off' and attr == 'y') or (tag == 'ext' and attr == 'cy')
                         or (tag == 'tr' and attr == 'h') or (tag == 'tcPr' and attr in ['marT', 'marB']))
        else:
            permitted = (tag == 'bodyPr' and attr in ['rot', 'wrap'] and
                         old.getparent().tag == '{'+NS['c']+'}txPr' and
                         old.getparent().getparent().tag == '{'+NS['c']+'}catAx')
        assert permitted, (part, tag, attr, before, after)
        attribute_changes.append({'part': part, 'element': tag, 'attribute': attr,
                                  'before': before, 'after': after})
    for a, b in zip(old, new):
        compare_elements(a, b, part)

with ZipFile(protected_inputs[0]) as old, ZipFile(BUILD / 'candidate.pptx') as new:
    assert set(old.namelist()) == set(new.namelist())
    changed = [part for part in old.namelist() if old.read(part) != new.read(part)]
    assert set(changed) == set(receipt['changed_parts']), changed
    for part in changed:
        compare_elements(E.fromstring(old.read(part)), E.fromstring(new.read(part)), part)
    slides = sorted([p for p in new.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', p)])
    notes = [p for p in new.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml', p)]
    charts = [p for p in new.namelist() if re.fullmatch(r'ppt/charts/chart\d+\.xml', p)]
    rels = [p for p in new.namelist() if p.endswith('.rels')]
    workbooks = [p for p in new.namelist() if p.endswith('.xlsx')]
    assert len(slides) == len(notes) == 40
    for part in notes + rels + workbooks:
        assert old.read(part) == new.read(part), part
    for part in slides:
        a, b = E.fromstring(old.read(part)), E.fromstring(new.read(part))
        assert a.xpath('//a:t/text()', namespaces=NS) == b.xpath('//a:t/text()', namespaces=NS)
    for part in charts:
        a, b = E.fromstring(old.read(part)), E.fromstring(new.read(part))
        assert a.xpath('//c:v/text() | //c:f/text() | //a:t/text()', namespaces=NS) == b.xpath('//c:v/text() | //c:f/text() | //a:t/text()', namespaces=NS)
    max_note_words = max(len(' '.join(E.fromstring(new.read(p)).xpath('//a:t/text()', namespaces=NS)).split()) for p in notes)
    pdf = PdfReader(BUILD / 'candidate.pdf')
    assert len(pdf.pages) == 40
    pdf_link_count = 0
    for i, page in enumerate(pdf.pages, 1):
        relpart = f'ppt/slides/_rels/slide{i}.xml.rels'
        relationships = E.fromstring(new.read(relpart))
        expected = {r.get('Target') for r in relationships if r.get('Type', '').endswith('/hyperlink')}
        actual = set()
        for ref in page.get('/Annots', []):
            annot = ref.get_object()
            action = annot.get('/A', {})
            if action.get('/URI'):
                actual.add(str(action['/URI']))
                pdf_link_count += 1
        assert expected <= actual, (i, sorted(expected - actual))

fit = read_json(BUILD / 'text-fit.json')
assert len(fit) == 730 and not any(x['Overflow'] for x in fit)
gaps = read_json(BUILD / 'native-table-gaps.json')
assert len(gaps) == 20 and all(x['GapInches'] > 0 for x in gaps)
assert all(x['GapInches'] >= .25 for x in gaps if x['Slide'] in [25, 33])
assert len(list((BUILD / 'rendered').glob('slide-*.png'))) == 40
for i in range(1, 41):
    assert (BUILD / f'rendered/slide-{i:02}.png').stat().st_size > 10000

# Check PDF text bounding boxes stay inside each slide canvas.
bounds = E.parse(str(BUILD / 'pdf-bounds.html'))
xns = {'h': 'http://www.w3.org/1999/xhtml'}
pages = bounds.findall('.//h:page', xns)
assert len(pages) == 40
for page in pages:
    w, h = float(page.get('width')), float(page.get('height'))
    for word in page.findall('.//h:word', xns):
        assert float(word.get('xMin')) >= -.1 and float(word.get('yMin')) >= -.1
        assert float(word.get('xMax')) <= w+.1 and float(word.get('yMax')) <= h+.1

protection = read_json(HERE / '.build/protected-before.json')
for relative, expected_sha in protection.items():
    assert sha(ROOT / relative) == expected_sha, relative

result = {'passed': True, 'slides': 40, 'notes_byte_identical': len(notes),
          'max_note_words': max_note_words, 'all_slide_text_identical': True,
          'relationships_byte_identical': len(rels), 'pdf_hyperlinks_verified': pdf_link_count,
          'editable_charts_data_identical': len(charts), 'workbooks_byte_identical': len(workbooks),
          'text_cells_checked': len(fit), 'overflow_candidates': 0,
          'native_tables_checked': len(gaps), 'table_footer_gaps_inches': {str(x['Slide']): x['GapInches'] for x in gaps},
          'protected_experiment_files_unchanged': len(protection),
          'changed_parts': changed, 'attribute_changes': attribute_changes,
          'candidate_sha256': sha(BUILD / 'candidate.pptx'),
          'pdf_sha256': sha(BUILD / 'candidate.pdf')}
(BUILD / 'validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in result.items() if k != 'attribute_changes'}, ensure_ascii=False, indent=2))
