"""Validate course formatting and editable PPTX package structures read-only."""
import argparse
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from pypdf import PdfReader

NS = {'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p':'http://schemas.openxmlformats.org/presentationml/2006/main'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group-id', default='03')
    args=parser.parse_args()
    output=Path('reports/output')
    report={}
    for stem,count in [(args.group_id,30),(args.group_id+'-poster-draft',1)]:
        pptx=output/(stem+'.pptx')
        pdf=output/(stem+'.pdf')
        assert pptx.stat().st_size<20_000_000, 'PPTX exceeds 20 MB'
        with zipfile.ZipFile(pptx) as z:
            names=z.namelist()
            slides=sorted(n for n in names if re.fullmatch(r'ppt/slides/slide\d+\.xml',n))
            notes=sorted(n for n in names if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',n))
            assert len(slides)==count,(stem,len(slides))
            assert len(notes)==count,(stem,len(notes))
            note_counts=[]
            for n in notes:
                text=' '.join(ET.fromstring(z.read(n)).itertext())
                words=len(text.split())
                assert 0<words<=500,(n,words)
                note_counts.append(words)
            slides=sorted(slides,key=lambda n:int(re.search(r'slide(\d+)',n).group(1)))
            texts=[' '.join(ET.fromstring(z.read(n)).itertext()) for n in slides]
            if count==30:
                source=json.loads(Path('reports/deck_content.json').read_text(encoding='utf-8'))
                normalize=lambda s:' '.join(str(s).split())
                for actual,approved in zip(texts,source['slides']):
                    for required in [approved['title'],*approved['body']]:
                        assert normalize(required) in normalize(actual), ('Source content missing',approved['number'],required)
                results=json.loads(Path('experiments/reproduction/results.json').read_text(encoding='utf-8'))
                if not any(r.get('paper_last_accuracy') is not None for r in results):
                    assert any('Chờ kết quả thực nghiệm' in s for s in texts), 'Missing explicit experiment placeholders'
                assert all('References' not in s for s in texts), 'Unexpected references-only slide'
            p=ET.fromstring(z.read('ppt/presentation.xml'))
            size=p.find('p:sldSz',NS)
            cx,cy=int(size.attrib['cx']),int(size.attrib['cy'])
            if count==1:
                assert abs(cx/36000-420)<0.1 and abs(cy/36000-594)<0.1
            charts=[n for n in names if re.fullmatch(r'ppt/charts/chart\d+\.xml',n)]
            tables=sum(len(ET.fromstring(z.read(n)).findall('.//a:tbl',NS)) for n in slides)
            report[stem]={'slides':count,'notes':len(notes),'max_note_words':max(note_counts),
                          'editable_charts':len(charts),'editable_tables':tables,
                          'bytes':pptx.stat().st_size,'dimensions_mm':[cx/36000,cy/36000]}
        reader=PdfReader(pdf)
        assert len(reader.pages)==count,(pdf,len(reader.pages))
        assert all((p.extract_text() or '').strip() for p in reader.pages),'Blank PDF page'
        report[stem]['pdf_pages']=len(reader.pages)
    Path('reports/.build/package-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
