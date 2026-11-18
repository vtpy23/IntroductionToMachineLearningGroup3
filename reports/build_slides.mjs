/**
 * Native editable PowerPoint authoring, explicitly requested by the user.
 * Academic content comes from deck_content.json / SLIDES.md. No invented data.
 * Rebuild: node reports/build_slides.mjs --group-id 03
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import pptxgen from 'pptxgenjs';
import JSZip from 'jszip';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.dirname(here);
const idAt = process.argv.indexOf('--group-id');
const groupId = idAt >= 0 ? process.argv[idAt + 1] : '03';
const diagnosticAt = process.argv.indexOf('--diagnostic-slide');
const diagnosticSlide = diagnosticAt >= 0 ? Number(process.argv[diagnosticAt + 1]) : null;
if (!/^[A-Za-z0-9_-]+$/.test(groupId)) throw new Error('Invalid group ID');
const out = path.join(here, 'output');
await fs.mkdir(out, { recursive: true });
await fs.mkdir(path.join(here, '.build'), { recursive: true });
const raw = await fs.readFile(path.join(here, 'deck_content.json'), 'utf8');
const spec = JSON.parse(raw);
const resultsPath = path.join(root, 'experiments/reproduction/results.json');
let results = [];
try { results = JSON.parse(await fs.readFile(resultsPath, 'utf8')); } catch { /* Explicit placeholders below. */ }
try {
  const remote=JSON.parse(await fs.readFile(path.join(root,'experiments/reproduction/wandb_results.json'),'utf8'));
  const existing=new Set(results.map(r=>r.wandb_url).filter(Boolean));
  results.push(...remote.filter(r=>!r.wandb_url||!existing.has(r.wandb_url)));
} catch { /* W&B fetch is optional until the project is connected. */ }
const C = { navy:'102C46', teal:'007F86', ink:'26394A', muted:'5B6E7D', pale:'EAF5F4',
  line:'D6E2E9', white:'FFFFFF', bg:'F8FAFC', amber:'9C6418', amberBg:'FFF5E5', blue:'537BA3' };
const W = 13.333333, H = 7.5;
const geometry = [];
const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'Nhóm 03: Vũ, Nam, Đạt';
pptx.subject = 'DS-AL: đọc hiểu và tái hiện, Milestone 2';
pptx.title = 'DS-AL – Nhóm 03';
pptx.company = 'Introduction to Machine Learning';
pptx.lang = 'vi-VN';
pptx.theme = { headFontFace:'Arial', bodyFontFace:'Arial', lang:'vi-VN' };

function text(slide, value, x, y, w, h, opts = {}) {
  geometry.push({ slide:slide._slideNum, kind:'text', x,y,w,h, text: typeof value === 'string' ? value : 'rich text' });
  slide.addText(value, { x,y,w,h, fontFace:'Arial', fontSize:22, color:C.ink,
    margin:0, breakLine:false, valign:'middle', ...opts });
}
function rect(slide,x,y,w,h,fill=C.bg,line=C.line) {
  slide.addShape(pptx.ShapeType.rect,{x,y,w,h,fill:{color:fill},line:{color:line,width:1}});
}
function line(slide,x1,y1,x2,y2,color=C.teal,arrow=false,width=1.8) {
  slide.addShape(pptx.ShapeType.line,{x:x1,y:y1,w:x2-x1,h:y2-y1,
    line:{color,width,...(arrow?{endArrowType:'triangle'}:{})}});
}
function node(slide,label,x,y,w=1.8,h=0.72,color=C.teal) {
  rect(slide,x,y,w,h,C.white,color);
  text(slide,label,x+0.1,y+0.05,w-0.2,h-0.1,{fontSize:17,bold:true,color,align:'center'});
}
function base(s) {
  const slide = pptx.addSlide();
  slide.background = {color:C.white};
  text(slide,s.title,0.62,s.kind==='cover'?0.24:0.40,11.95,s.kind==='cover'?1.10:0.90,{fontSize:s.kind==='cover'?60:32,bold:true,color:C.navy,breakLine:false});
  line(slide,0.63,1.36,12.70,1.36,C.line,false,0.8);
  line(slide,0.63,6.63,12.70,6.63,C.line,false,0.8);
  const slideCitations=[...s.citations];
  if(s.kind==='measured-results'&&!slideCitations.length) slideCitations.push(spec.slides[0].citations[0]);
  const citations = slideCitations.join('\n');
  if (citations) text(slide,citations,0.63,6.72,11.65,0.58,
    {fontSize:8.2,color:C.muted,valign:'top',paraSpaceAfterPt:1});
  text(slide,`${String(s.number).padStart(2,'0')} / ${spec.slides.length}`,12.15,7.16,0.55,0.18,
    {fontSize:9,color:C.muted,align:'right'});
  slide.addNotes(`${s.notes}\n\n${citations}`);
  return slide;
}
function body(slide,items,{x=0.70,y=1.85,w=11.90,fontSize=25,gap=1.23}={}) {
  items.forEach((value,i) => {
    line(slide,x,y+i*gap+0.08,x,y+i*gap+0.63,C.teal,false,2.6);
    text(slide,value,x+0.23,y+i*gap,w-0.23,0.90,{fontSize,valign:'top',paraSpaceAfterPt:0});
  });
}
function table(slide,columns,rows,{x=0.72,y=2.05,w=11.88,h=3.10,fontSize=20,colW}={}) {
  geometry.push({slide:slide._slideNum,kind:'table',x,y,w,h,rows:rows.length+1});
  const data = [columns.map(t=>({text:String(t),options:{bold:true,color:C.white,fill:C.navy}})),
    ...rows.map((row,i)=>row.map(t=>({text:String(t),options:{fill:i%2?C.bg:C.white,color:C.ink}})))];
  slide.addTable(data,{x,y,w,h,colW, fontFace:'Arial',fontSize,
    color:C.ink,border:{type:'solid',pt:0.65,color:C.line},
    margin:[0.08,0.15,0.08,0.15],valign:'middle',autoPage:false,
    rowH:h/(rows.length+1),bold:false,paraSpaceAfterPt:0});
}
function pending(slide,x,y,w,h=1.08) {
  rect(slide,x,y,w,h,C.amberBg,'E8D4B4');
  text(slide,'Chờ kết quả thực nghiệm',x+0.2,y+0.18,w-0.4,h-0.36,
    {fontSize:24,bold:true,color:C.amber,align:'center'});
}
const eligible = results.filter(r=>r.paper_last_accuracy != null && !r.run.includes('/smoke/'));
function resultFor(method,k=5,name='') {
  return eligible.find(r=>r.method===method && r.phases===k && (!name || r.run.includes(name)));
}
const fmt = value => Number.isFinite(value) ? value.toFixed(2) : 'Chờ';
function groupedRows(rows,key) {
  const groups=new Map();
  for(const r of rows) {
    const group=groups.get(r[key])||new Map();
    group.set(r.seed,r); groups.set(r[key],group);
  }
  return [...groups.entries()].sort(([a],[b])=>a-b).map(([label,bySeed])=>{
    const values=[...bySeed.values()].map(r=>r.last_accuracy);
    const mean=values.reduce((a,b)=>a+b,0)/values.length;
    const std=values.length>1?Math.sqrt(values.reduce((a,b)=>a+(b-mean)**2,0)/(values.length-1)):null;
    return [String(label),std===null?fmt(mean):`${fmt(mean)} ± ${fmt(std)}`];
  });
}

for (const s of spec.slides.filter(s=>!diagnosticSlide || s.number===diagnosticSlide)) {
  const slide = base(s);
  switch(s.kind) {
    case 'cover': {
      // Cover body is deliberately below the retained title frame.
      text(slide,'DUAL-STREAM ANALYTIC LEARNING',0.72,1.83,11.8,0.43,
        {fontSize:18,bold:true,color:C.teal,charSpacing:1.8});
      text(slide,s.body[0],0.72,2.55,11.8,1.05,{fontSize:35,bold:true,color:C.navy});
      text(slide,s.body[1],0.74,4.00,10.5,0.55,{fontSize:24,color:C.muted});
      text(slide,s.body[2],0.74,5.10,10.5,0.48,{fontSize:20,color:C.ink});
      break;
    }
    case 'table': {
      table(slide,s.columns,s.rows,{y:1.94,h:s.rows.length===5?3.75:2.8,
        fontSize:s.columns.length>3?19:21,colW:s.columns.length===2?[2.3,9.58]:undefined});
      if(s.number===22) text(slide,'Số liệu công bố của tác giả, không phải kết quả nhóm',0.75,5.33,11.8,0.55,
        {fontSize:20,color:C.muted});
      break;
    }
    case 'timeline': {
      body(slide,s.body,{y:1.75,w:11.8,fontSize:24,gap:0.96});
      s.labels.forEach((label,i)=>{
        node(slide,label,0.85+i*4.05,5.05,3.45,0.78);
        if(i<2) line(slide,4.36+i*4.05,5.44,4.82+i*4.05,5.44,C.teal,true);
      });
      break;
    }
    case 'comparison': {
      const names=['Replay','ACIL','DS-AL'];
      s.body.forEach((b,i)=>{
        const x=0.78+i*4.12;
        text(slide,names[i],x,2.05,3.65,0.62,{fontSize:30,bold:true,color:i===2?C.teal:C.navy});
        line(slide,x,2.88,x+3.5,2.88,C.line,false,1.2);
        text(slide,b,x,3.25,3.5,1.8,{fontSize:25,valign:'top'});
      });
      break;
    }
    case 'protocol': {
      body(slide,s.body,{x:0.75,y:1.85,w:5.25,fontSize:24,gap:1.22});
      text(slide,'100 lớp',6.90,2.02,4.8,0.6,{fontSize:35,bold:true,color:C.navy});
      rect(slide,6.90,3.05,2.37,0.78,C.navy,C.navy);
      rect(slide,9.27,3.05,2.37,0.78,C.pale,C.teal);
      text(slide,'50 base',6.98,3.16,2.20,0.5,{fontSize:22,bold:true,color:C.white,align:'center'});
      text(slide,'50 mới',9.35,3.16,2.20,0.5,{fontSize:22,bold:true,color:C.teal,align:'center'});
      text(slide,'K = 5 / 25 / 50',6.90,4.25,4.8,0.65,{fontSize:28,color:C.teal});
      break;
    }
    case 'pipeline': {
      body(slide,s.body,{y:1.72,w:11.8,fontSize:21,gap:0.82});
      node(slide,'Ảnh',0.80,4.88,1.35);
      node(slide,'CNN cố định',2.60,4.88,2.00);
      node(slide,'Buffer B',5.05,4.88,1.80);
      node(slide,'C-RLS',7.45,4.10,1.75,0.70);
      node(slide,'DAC + PLC',7.45,5.55,1.75,0.70,C.blue);
      node(slide,'Scores',10.35,4.88,1.70);
      line(slide,2.15,5.24,2.56,5.24,C.teal,true);
      line(slide,4.6,5.24,5.01,5.24,C.teal,true);
      line(slide,6.85,5.24,7.15,5.24);
      line(slide,7.15,4.45,7.15,5.90);
      line(slide,7.15,4.45,7.41,4.45,C.teal,true);
      line(slide,7.15,5.90,7.41,5.90,C.blue,true);
      line(slide,8.325,4.80,8.325,5.51,C.blue,true);
      text(slide,'Eₖ',8.48,5.02,0.55,0.32,{fontSize:15,color:C.blue});
      line(slide,9.2,4.45,9.86,4.45);
      line(slide,9.2,5.90,9.86,5.90,C.blue);
      line(slide,9.86,4.45,9.86,5.90);
      line(slide,9.86,5.24,10.31,5.24,C.teal,true);
      break;
    }
    case 'dual-stream': {
      body(slide,s.body,{y:1.75,w:6.0,fontSize:24,gap:1.16});
      node(slide,'Z = f(x) B',7.00,2.15,4.05,0.80);
      node(slide,'ReLU',6.70,4.00,2.30,0.85);
      node(slide,'Tanh',9.65,4.00,2.30,0.85,C.blue);
      line(slide,9.02,2.95,9.02,3.45);
      line(slide,7.85,3.45,10.80,3.45);
      line(slide,7.85,3.45,7.85,3.96,C.teal,true);
      line(slide,10.80,3.45,10.80,3.96,C.blue,true);
      text(slide,'Nhánh chính',6.70,5.20,2.3,0.50,{fontSize:20,color:C.teal,align:'center'});
      text(slide,'Nhánh bù',9.65,5.20,2.3,0.50,{fontSize:20,color:C.blue,align:'center'});
      break;
    }
    case 'label-matrix': {
      body(slide,s.body,{y:1.80,w:6.05,fontSize:24,gap:1.16});
      const labels=s.number===18?['Residual cũ','Residual mới']:['Lớp cũ','Lớp mới'];
      table(slide,labels,s.number===18?[['0','E mới'],['0','E mới']]:[['Y cũ','0'],['0','Y mới']],
        {x:7.15,y:2.45,w:4.8,h:2.25,fontSize:21,colW:[2.4,2.4]});
      text(slide,s.number===18?'PLC: pha tăng dần':'Nhãn theo lớp toàn cục',7.15,5.15,4.8,0.6,
        {fontSize:21,color:C.muted,align:'center'});
      break;
    }
    case 'equation': {
      if(s.number===14) {
        body(slide,s.body,{y:1.67,w:11.8,fontSize:20,gap:0.78});
        text(slide,'Rₖ = Rₖ₋₁ − Rₖ₋₁ Xₖᵀ (I + XₖRₖ₋₁Xₖᵀ)⁻¹ XₖRₖ₋₁',0.85,4.42,11.65,0.72,
          {fontSize:23,bold:true,color:C.navy,align:'center'});
        text(slide,'Wₖ = [Wₖ₋₁, 0] + RₖXₖᵀ (Yₖ − Xₖ[Wₖ₋₁, 0])',0.85,5.38,11.65,0.72,
          {fontSize:23,bold:true,color:C.teal,align:'center'});
        break;
      }
      s.body.forEach((b,i)=>{
        text(slide,b,0.95,1.85+i*1.42,11.45,1.05,
          {fontSize:b.length>65?26:30,color:i===0?C.navy:C.ink,bold:i===0,align:'center'});
      });
      break;
    }
    case 'complexity': {
      body(slide,s.body,{y:1.85,w:6.1,fontSize:24,gap:1.18});
      slide.addChart(pptx.ChartType.bar,[{name:'Hai ma trận float64',labels:['512','1024','2048','8192'],values:[4,16,64,1024]}],
        {x:7.0,y:1.95,w:5.25,h:3.86,catAxisLabelFontFace:'Arial',catAxisLabelFontSize:13,
         valAxisLabelFontFace:'Arial',valAxisLabelFontSize:12,valAxisTitle:'MiB',showValue:true,
         dataLabelFormatCode:'0',dataLabelPosition:'outEnd',dataLabelColor:C.ink,
         showLegend:false,showTitle:false,barDir:'col',chartColors:[C.teal],
         catAxisTitle:'Chiều buffer m',showCatName:false,
         showCatAxisTitle:true,showValAxisTitle:true,
         valAxisMinVal:0,valAxisMaxVal:1150,showBorder:false});
      text(slide,'Tính từ 2m² × 8 byte, không phải số đo RAM tổng',7.0,5.90,5.25,0.37,{fontSize:13,color:C.muted});
      break;
    }
    case 'verification': {
      body(slide,s.body,{y:1.73,w:11.8,fontSize:23,gap:1.03});
      // Values are read from measured evidence, never embedded as hypothetical results.
      let cmp;
      try { cmp=JSON.parse(await fs.readFile(path.join(root,'experiments/reproduction/reference-comparison.json'),'utf8')); } catch {}
      const full = cmp?.measurements?.find(r=>r.official_batch_size===20);
      if(full) text(slide,`Sai khác scores tối đa, cùng một batch mỗi pha: ${full.scores_max_abs_difference.toExponential(2)}`,
        0.95,5.37,11.4,0.65,{fontSize:22,color:C.teal,bold:true});
      break;
    }
    case 'provenance': {
      body(slide,s.body,{y:1.85,w:11.8,fontSize:25,gap:1.22});
      break;
    }
    case 'measured-results': {
      text(slide,s.body.join('\n'),0.75,1.63,11.85,0.85,{fontSize:19,color:C.muted});
      const a=resultFor('acil',5), d=resultFor('dsal',5,'dsal-k5');
      table(slide,['Phương pháp','Paper A_K (%)','Nhóm A_K (%)','Truy vết W&B'],
        [['ACIL',57.78,fmt(a?.last_accuracy),a?.wandb_url?'Đã có run URL':'Chờ liên kết công khai'],
         ['DS-AL',58.26,fmt(d?.last_accuracy),d?.wandb_url?'Đã có run URL':'Chờ liên kết công khai']],
        {y:2.83,h:1.90,fontSize:18,colW:[2.0,2.35,2.35,5.18]});
      if(!a||!d) pending(slide,2.00,5.17,9.35,0.90);
      slide.addNotes(`Nguồn số paper: [1], Table 1, CIFAR-100 ResNet-32, K=5.\n${[a?.wandb_url,d?.wandb_url].filter(Boolean).join('\n')}`);
      break;
    }
    case 'measured-ablation': {
      text(slide,s.body.join('\n'),0.75,1.62,11.85,1.04,{fontSize:19,color:C.muted});
      const selected = [
        ['C-RLS (ACIL)',eligible.find(r=>r.run.includes('acil-k5'))],
        ['DAC không PLC',results.find(r=>r.run.includes('dac-no-plc-k5')&&!r.run.includes('smoke'))],
        ['DAC + PLC',eligible.find(r=>r.run.includes('dsal-k5'))]
      ];
      table(slide,['Biến thể','A-bar (%)','A_K (%)'],selected.map(([name,r])=>[name,fmt(r?.average_accuracy),fmt(r?.last_accuracy)]),
        {y:3.00,h:2.02,fontSize:21,colW:[5.5,3.19,3.19]});
      if(selected.some(([,r])=>!r)) pending(slide,2.00,5.40,9.35,0.82);
      break;
    }
    case 'measured-sweeps': {
      body(slide,s.body,{y:1.70,w:11.8,fontSize:22,gap:0.88});
      const phaseRows=eligible.filter(r=>r.method==='dsal'&&r.run.includes('dsal-k')).sort((a,b)=>a.phases-b.phases);
      const widthRows=results.filter(r=>!r.run.includes('smoke')&&r.run.includes('buffer-')).sort((a,b)=>a.buffer_size-b.buffer_size);
      if(phaseRows.length) table(slide,['K','A_K (%)'],groupedRows(phaseRows,'phases'),{x:0.85,y:4.85,w:5.50,h:1.26,fontSize:16,colW:[2.1,3.4]});
      else pending(slide,0.85,4.85,5.50,1.04);
      if(widthRows.length) table(slide,['m','A_K (%)'],groupedRows(widthRows,'buffer_size'),{x:7.00,y:4.85,w:5.50,h:1.26,fontSize:16,colW:[2.1,3.4]});
      else pending(slide,7.00,4.85,5.50,1.04);
      text(slide,'Số pha K',0.85,4.23,5.5,0.46,{fontSize:23,bold:true,color:C.navy,align:'center'});
      text(slide,'Chiều buffer m',7.00,4.23,5.5,0.46,{fontSize:23,bold:true,color:C.navy,align:'center'});
      break;
    }
    default:
      body(slide,s.body,{fontSize:s.body.some(b=>b.length>85)?23:26,gap:1.26});
  }
}

if(spec.slides.length<20||spec.slides.length>40) throw new Error('Milestone 2 requires 20–40 slides');
for(const s of spec.slides) if(!s.notes || s.notes.split(/\s+/u).length>500) throw new Error(`Notes invalid on slide ${s.number}`);
for(const g of geometry) if(g.x<0||g.y<0||g.x+g.w>W+0.03||g.y+g.h>H+0.03)
  throw new Error(`Geometry outside slide: ${JSON.stringify(g)}`);
const deckPath = diagnosticSlide ? path.join(here,'.build',`diagnostic-${diagnosticSlide}.pptx`) : path.join(out,`${groupId}.pptx`);
await pptx.writeFile({fileName:deckPath,compression:true});
await normalizeContentTypes(deckPath);
if(diagnosticSlide) { console.log(deckPath); process.exit(0); }

// A separate A2 portrait poster remains explicitly a draft until public W&B is verified.
const posterSpec = JSON.parse(await fs.readFile(path.join(here,'poster_content.json'),'utf8'));
const poster = new pptxgen();
poster.defineLayout({name:'A2_PORTRAIT',width:420/25.4,height:594/25.4});
poster.layout='A2_PORTRAIT';
poster.author=pptx.author; poster.title='DS-AL: phản biện lý thuyết';
poster.theme=pptx.theme; poster.lang='vi-VN';
const ps=poster.addSlide(); ps.background={color:C.white};
function pt(value,x,y,w,h,size=25,options={}) {
  ps.addText(value,{x,y,w,h,fontFace:'Arial',fontSize:size,color:C.ink,margin:0,valign:'top',...options});
}
pt(posterSpec.title,0.68,0.70,15.1,1.35,39,{bold:true,color:C.navy});
pt(posterSpec.subtitle,0.70,2.18,15.0,0.72,23,{color:C.teal});
pt(posterSpec.authors,0.70,3.02,15.0,0.5,21);
pt(posterSpec.status,0.70,3.74,15.0,0.65,20,{bold:true,color:C.amber});
pt('Ba điểm mạnh',0.70,4.70,15.0,0.52,28,{bold:true,color:C.navy});
posterSpec.strengths.forEach((s,i)=>pt(`${i+1}. ${s}`,0.75,5.45+i*0.56,15.0,0.48,22));
for(const [index,item] of posterSpec.limitations.entries()) {
  const y=index===0?7.65:14.70;
  pt(item.title,0.70,y,15.0,0.80,30,{bold:true,color:C.navy});
  pt(item.argument,0.75,y+1.00,7.00,1.65,23);
  pt('Thiết kế kiểm chứng',0.75,y+2.88,7.00,0.45,23,{bold:true,color:C.teal});
  pt(item.design,0.75,y+3.42,7.00,1.54,21);
  if(index===0) {
    const seeds=[...new Set(item.measurements.map(r=>r.seed))];
    ps.addChart(poster.ChartType.line,seeds.map((seed)=>({name:`seed ${seed}`,labels:['1','2','5'],
      values:item.measurements.filter(r=>r.seed===seed).map(r=>r.comp_relative_difference)})),
      {x:8.25,y:y+1.02,w:7.15,h:3.38,showLegend:true,legendPos:'b',legendFontFace:'Arial',legendFontSize:15,
       showTitle:false,showValue:false,catAxisLabelFontSize:16,valAxisLabelFontSize:15,
       chartColors:[C.teal,C.blue,'B58035'],lineSize:2,showMarker:true,
       catAxisTitle:'Số pha mới',valAxisTitle:'Delta tương đối W_C',showCatAxisTitle:true,showValAxisTitle:true,valAxisMinVal:0,valAxisMaxVal:0.60,
       catAxisLabelFontFace:'Arial',valAxisLabelFontFace:'Arial'});
    pt(`Delta W_M tối đa: ${item.main_max_relative_delta.toExponential(2)}\nDelta W_C trung bình: ${(item.comp_mean_relative_delta*100).toFixed(2)}%`,8.30,y+4.56,7.0,0.95,21,{color:C.teal,bold:true});
  } else {
    const rows=[['gamma','||XᵀE||, seed0'],...item.measurements.filter(r=>r.seed===0&&[0.0001,0.1,100].includes(r.gamma)).map(r=>[String(r.gamma),r.cross_residual_norm.toExponential(3)])];
    ps.addTable(rows,{x:8.25,y:y+1.10,w:7.1,h:2.18,fontFace:'Arial',fontSize:21,
      border:{type:'solid',pt:0.8,color:C.line},margin:[0.08,0.15,0.08,0.15],autoPage:false,
      rowH:0.55,color:C.ink,fill:C.bg,colW:[2.3,4.8]});
    pt(`Sai số normal equation tối đa:\n${item.normal_equation_max_error.toExponential(2)}`,8.28,y+3.55,7.05,0.95,22,{bold:true,color:C.teal});
  }
  pt(item.conclusion,0.75,y+5.20,14.7,0.80,21);
  pt(item.future,0.75,y+6.10,14.7,0.74,20,{color:C.muted});
}
pt(posterSpec.citations.join('\n'),0.72,22.12,15.0,0.76,12.5,{color:C.muted});
pt(posterSpec.repository,0.72,23.02,15.0,0.24,11,{color:C.muted});
ps.addNotes(posterSpec.notes+'\n\n'+posterSpec.citations.join('\n'));
const posterPath=path.join(out,`${groupId}-poster-draft.pptx`);
await poster.writeFile({fileName:posterPath,compression:true});
await normalizeContentTypes(posterPath);
await fs.writeFile(path.join(here,'.build','geometry.json'),JSON.stringify(geometry,null,2));
await fs.writeFile(path.join(here,'.build','build.json'),JSON.stringify({groupId,slides:spec.slides.length,
  academicContentSha256:createHash('sha256').update(raw).digest('hex'),deckPath,posterPath,
  placeholder:'Chờ kết quả thực nghiệm',renderer:'PptxGenJS 4.0.1',resultsSource:resultsPath},null,2));
console.log(JSON.stringify({deckPath,posterPath,slideCount:spec.slides.length}));

async function normalizeContentTypes(file) {
  // PptxGenJS 4.0.1 declares one slideMaster per slide but writes only master1.
  // Remove declarations of absent package parts; preserve all authored content.
  const zip=await JSZip.loadAsync(await fs.readFile(file));
  let xml=await zip.file('[Content_Types].xml').async('string');
  const removed=[];
  xml=xml.replace(/<Override\s+PartName="([^"]+)"[^>]*\/>/g,(match,part)=>{
    if(!zip.file(part.replace(/^\//,''))) { removed.push(part); return ''; }
    return match;
  });
  zip.file('[Content_Types].xml',xml);
  await fs.writeFile(file,await zip.generateAsync({type:'nodebuffer',compression:'DEFLATE'}));
  await fs.writeFile(path.join(here,'.build',path.basename(file)+'.package-repairs.json'),JSON.stringify({removedDeclarations:removed},null,2));
}
