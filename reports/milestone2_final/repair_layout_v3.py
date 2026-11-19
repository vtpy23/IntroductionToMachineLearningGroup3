"""Layout-only OOXML repair. Text, notes, links, charts and measurements stay intact."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E

HERE=Path(__file__).resolve().parent
BUILD=HERE/'.build/v3'
BUILD.mkdir(parents=True,exist_ok=True)
SOURCE=HERE/'DSAL_Milestone2_Lab1_Final_v2.pptx'
TARGET=BUILD/'candidate.pptx'
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
EMU=914400
def emu(value):return str(round(value*EMU))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source_hashes={p.name:sha(p) for p in [SOURCE,HERE/'DSAL_Milestone2_Lab1_Final_v2.pdf',HERE/'assets/verified_evidence.json']}
# Explicit rows include generous space for font leading and cell padding.
# A 1.4 x font-size line-height allowance is validated independently.
layouts={25:(4.22,.43),30:(3.22,.40),32:(3.75,.425),33:(4.80,.40),36:(3.65,.52)}
receipt=[];changes={}
with ZipFile(SOURCE) as src:
    for slide,(top,row_height) in layouts.items():
        part=f'ppt/slides/slide{slide}.xml'
        root=E.fromstring(src.read(part))
        frames=[x for x in root.findall('.//p:graphicFrame',NS) if x.find('.//a:tbl',NS) is not None]
        assert len(frames)==1,(slide,len(frames))
        frame=frames[0];table=frame.find('.//a:tbl',NS);rows=table.findall('a:tr',NS)
        frame.find('p:xfrm/a:off',NS).set('y',emu(top))
        frame.find('p:xfrm/a:ext',NS).set('cy',emu(row_height*len(rows)))
        for row in rows:
            row.set('h',emu(row_height))
            for cell in row.findall('a:tc',NS):
                props=cell.find('a:tcPr',NS)
                props.set('marT',emu(.035));props.set('marB',emu(.035))
        # Dedicated hyperlink lane, safely below both repaired tables.
        if slide in [25,33]:
            for shape in root.findall('.//p:sp',NS):
                label=''.join(t.text or '' for t in shape.findall('.//a:t',NS))
                link=shape.find('.//a:hlinkClick',NS)
                if label=='W&B' or (link is not None and not label.startswith('[')):
                    off=shape.find('.//a:xfrm/a:off',NS)
                    off.set('y',emu(6.32 if label=='W&B' else 6.31))
        changes[part]=E.tostring(root,encoding='UTF-8',xml_declaration=True,standalone=True)
        receipt.append({'slide':slide,'table_y_in':top,'row_height_in':row_height,
                        'table_bottom_in':round(top+len(rows)*row_height,3),'vertical_cell_margin_in':.035})
    # Sparse epoch labels must remain horizontal in PowerPoint. Keep every
    # category string and data value, changing text-box wrapping only.
    chart_part='ppt/charts/chart1.xml'
    chart=E.fromstring(src.read(chart_part))
    axis_body=chart.find('.//c:catAx/c:txPr/a:bodyPr',NS)
    axis_body.set('wrap','none');axis_body.set('rot','0')
    changes[chart_part]=E.tostring(chart,encoding='UTF-8',xml_declaration=True,standalone=True)
    with ZipFile(TARGET,'w',ZIP_DEFLATED) as dst:
        for part in src.infolist():dst.writestr(part,changes.get(part.filename,src.read(part.filename)))
manifest={'source':SOURCE.name,'source_sha256':source_hashes,'output':str(TARGET),
          'changed_parts':list(changes),'layout':receipt,
          'policy':'Only table y/height, row heights, vertical cell padding, selected link-lane y coordinates and chart axis text wrapping changed.'}
(BUILD/'repair.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'slides_repaired':list(layouts),'candidate_bytes':TARGET.stat().st_size},ensure_ascii=False))
