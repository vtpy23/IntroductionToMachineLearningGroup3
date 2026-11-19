"""Keep actual v3 as package base; replace only updated slides/notes/charts.

Custom SD error bars reference added numeric worksheet cells, remaining editable
in PowerPoint. No workbook or chart belonging to a seed0 sweep is replaced.
"""
import hashlib
import copy
import io
import json
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E

HERE=Path(__file__).resolve().parent
BUILD=HERE/'.build/three-seeds'
BASE=HERE/'DSAL_Milestone2_Lab1_Final_v3.pptx'
GENERATED=BUILD/'generated.pptx'
OUTPUT=BUILD/'candidate.pptx'
UPDATED=[1,7,9,21,22,23,24,25,27,28,29,30,31,34,35,39,40]
NOTE_ONLY=[16]
CHARTS=[1,3,4,5,6]
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
    'c':'http://schemas.openxmlformats.org/drawingml/2006/chart',
    's':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def xml(data):return E.fromstring(data)
def serial(node):return E.tostring(node,encoding='UTF-8',xml_declaration=True,standalone=True)
def sha(data):return hashlib.sha256(data).hexdigest()
def node(parent,tag,attrs=None,text=None):
    prefix,local=tag.split(':');child=E.SubElement(parent,'{'+NS[prefix]+'}'+local,attrs or {})
    if text is not None:child.text=str(text)
    return child

v=json.loads((HERE/'assets/three_seeds_verified.json').read_text(encoding='utf-8'))
A=v['aggregates'];core=['acil-k5','dac-no-plc-k5','dsal-k5']
error_specs={
 4:{1:{'name':'SD across seeds','values':[A[m]['average_accuracy']['sd'] for m in ['acil-k5','dsal-k5']]}},
 5:{1:{'name':'SD across seeds','values':[A[m]['last_accuracy']['sd'] for m in ['acil-k5','dsal-k5']]}},
 6:{i:{'name':m+' SD','values':[x['sd'] for x in A[m]['phase_accuracy']]} for i,m in enumerate(core)}
}

def patch_error_bars(chart_bytes,workbook_bytes,spec):
    chart=xml(chart_bytes)
    series=chart.findall('.//c:ser',NS)
    with ZipFile(io.BytesIO(workbook_bytes)) as z:
        sheet=xml(z.read('xl/worksheets/sheet1.xml'))
        sheet_data=sheet.find('s:sheetData',NS)
        max_col=max(ord(c.get('r')[0])-64 for c in sheet.findall('.//s:c',NS))
        for offset,(index,item) in enumerate(spec.items(),1):
            col=chr(64+max_col+offset)
            values=item['values']
            for i,value in enumerate([item['name'],*values],1):
                row=next((r for r in sheet_data if r.get('r')==str(i)),None)
                if row is None:row=node(sheet_data,'s:row',{'r':str(i)})
                row.set('spans','1:'+str(max_col+len(spec)))
                cell=node(row,'s:c',{'r':f'{col}{i}'})
                if i==1:
                    cell.set('t','inlineStr');inline=node(cell,'s:is');node(inline,'s:t',text=value)
                else:node(cell,'s:v',text=repr(value))
            ser=series[index]
            old=ser.find('c:errBars',NS)
            if old is not None:ser.remove(old)
            err=E.Element('{'+NS['c']+'}errBars')
            # CT_LineSer / CT_BarSer require error bars before category/value refs.
            before=next(c for c in ser if E.QName(c).localname in ['cat','val'])
            ser.insert(ser.index(before),err)
            node(err,'c:errDir',{'val':'y'});node(err,'c:errBarType',{'val':'both'})
            node(err,'c:errValType',{'val':'cust'});node(err,'c:noEndCap',{'val':'0'})
            for sign in ['plus','minus']:
                side=node(err,'c:'+sign);ref=node(side,'c:numRef')
                node(ref,'c:f',text=f'Sheet1!${col}$2:${col}${len(values)+1}')
                cache=node(ref,'c:numCache');node(cache,'c:formatCode',text='0.0000')
                node(cache,'c:ptCount',{'val':str(len(values))})
                for i,value in enumerate(values):node(node(cache,'c:pt',{'idx':str(i)}),'c:v',text=repr(value))
            props=node(err,'c:spPr');line=node(props,'a:ln',{'w':'9525'})
            color=ser.find('c:spPr/a:ln/a:solidFill/a:srgbClr',NS)
            if color is None:color=ser.find('c:spPr/a:solidFill/a:srgbClr',NS)
            fill=node(line,'a:solidFill');node(fill,'a:srgbClr',{'val':color.get('val') if color is not None else '008D98'})
            node(line,'a:prstDash',{'val':'solid'})
        last_col=chr(64+max_col+len(spec))
        last_row=max(int(r.get('r')) for r in sheet_data)
        sheet.find('s:dimension',NS).set('ref',f'A1:{last_col}{last_row}')
        buf=io.BytesIO()
        with ZipFile(buf,'w',ZIP_DEFLATED) as w:
            for part in z.infolist():w.writestr(part,serial(sheet) if part.filename=='xl/worksheets/sheet1.xml' else z.read(part.filename))
    return serial(chart),buf.getvalue()

changes={}
with ZipFile(BASE) as base,ZipFile(GENERATED) as gen:
    for i in UPDATED:
        for part in [f'ppt/slides/slide{i}.xml',f'ppt/slides/_rels/slide{i}.xml.rels',f'ppt/notesSlides/notesSlide{i}.xml']:
            changes[part]=gen.read(part)
    for i in NOTE_ONLY:changes[f'ppt/notesSlides/notesSlide{i}.xml']=gen.read(f'ppt/notesSlides/notesSlide{i}.xml')
    for i in CHARTS:
        chart=f'ppt/charts/chart{i}.xml'
        rel=f'ppt/charts/_rels/chart{i}.xml.rels'
        workbook=f'ppt/embeddings/Microsoft_Excel_Worksheet{i}.xlsx'
        changes[chart]=gen.read(chart);changes[rel]=gen.read(rel);changes[workbook]=gen.read(workbook)
        if i in error_specs:
            changes[chart],changes[workbook]=patch_error_bars(changes[chart],changes[workbook],error_specs[i])
    # Preserve v3's fix for horizontally displayed sparse epoch labels.
    chart=xml(changes['ppt/charts/chart1.xml'])
    body=chart.find('.//c:catAx/c:txPr/a:bodyPr',NS)
    body.set('wrap','none');body.set('rot','0')
    changes['ppt/charts/chart1.xml']=serial(chart)
    changes['docProps/core.xml']=gen.read('docProps/core.xml')
    # Preserve all entry names, relationships and media of the actual source.
    assert set(changes)<=set(base.namelist())
    with ZipFile(OUTPUT,'w',ZIP_DEFLATED) as out:
        for part in base.infolist():out.writestr(copy.copy(part),changes.get(part.filename,base.read(part.filename)))
    receipt={'baseline':BASE.name,'baseline_sha256':sha(BASE.read_bytes()),'candidate_sha256':sha(OUTPUT.read_bytes()),
             'updated_slides':UPDATED,'notes_only':NOTE_ONLY,'updated_charts':CHARTS,'custom_sd_errorbar_charts':list(error_specs),
             'changed_parts':[p for p in base.namelist() if base.read(p)!=changes.get(p,base.read(p))],
             'unchanged_slide_xml':[i for i in range(1,41) if i not in UPDATED],
             'unchanged_chart_parts':['ppt/charts/chart'+str(i)+'.xml' for i in [2,7,8,9]],
             'policy':'Actual v3 is the package base. Only selected slides/notes/charts and core metadata replaced; all sweep data and layouts remain byte-identical.'}
(BUILD/'merge-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'candidate_bytes':OUTPUT.stat().st_size,'slides_updated':len(UPDATED),'source_slide_xml_preserved':40-len(UPDATED),'native_charts':9}))
