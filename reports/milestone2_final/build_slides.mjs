/** Editable native diagrams/charts. User-authorized PptxGenJS workflow. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import pptxgen from 'pptxgenjs';
import JSZip from 'jszip';
const HERE=path.dirname(fileURLToPath(import.meta.url));
const ROOT=path.resolve(HERE,'../..');
await fs.mkdir(path.join(HERE,'.build'),{recursive:true});
const content=JSON.parse(await fs.readFile(path.join(HERE,'slide_content.json'),'utf8'));
const evidence=JSON.parse(await fs.readFile(path.join(HERE,'assets/verified_evidence.json'),'utf8'));
const R=Object.fromEntries(evidence.experiments.map(r=>[r.name,r]));
const sum=n=>R[n].summary;
const fmt=(v,d=2)=>Number(v).toFixed(d);
const P={navy:'0B1728',navy2:'132D46',cream:'F5F3ED',ink:'152B40',teal:'008D98',cyan:'56D9EB',blue:'427AF2',green:'21966A',orange:'CC7D26',muted:'607486',line:'CED8DD',white:'FFFFFF',pale:'E6F1F1'};
const W=13.333333,H=7.5,FONT='Segoe UI';
const pptx=new pptxgen();pptx.layout='LAYOUT_WIDE';
pptx.author='Nhóm 03: Vũ, Nam, Đạt';pptx.title='DS-AL — Milestone 2 + Lab 1';
pptx.subject='Verified seed-0 CIFAR-100 reproduction and independent reading';
pptx.lang='vi-VN';pptx.theme={headFontFace:FONT,bodyFontFace:FONT,lang:'vi-VN'};
const geometry=[];
function text(sl,t,x,y,w,h,o={}){
 const col=sl._dark?'E4ECF4':P.ink;
 geometry.push({slide:sl._slideNum,kind:'text',text:typeof t==='string'?t:'rich text',x,y,w,h,role:o.role||'body'});
 sl.addText(t,{x,y,w,h,fontFace:FONT,fontSize:21,color:col,margin:0,breakLine:false,valign:'mid',paraSpaceAfterPt:0,...o});
}
function shape(sl,x,y,w,h,fill,line=fill,extra={}){sl.addShape(pptx.ShapeType.rect,{x,y,w,h,fill:{color:fill},line:{color:line,width:0.8},...extra});}
function line(sl,x1,y1,x2,y2,col=P.teal,width=1.5,arrow=false){sl.addShape(pptx.ShapeType.line,{x:Math.min(x1,x2),y:Math.min(y1,y2),w:Math.abs(x2-x1),h:Math.abs(y2-y1),flipH:x2<x1,flipV:y2<y1,line:{color:col,width,...(arrow?{endArrowType:'triangle'}:{})}});}
function elbow(sl,x1,y1,x2,y2,col=P.teal){const mid=(x1+x2)/2;line(sl,x1,y1,mid,y1,col);line(sl,mid,y1,mid,y2,col);line(sl,mid,y2,x2,y2,col,1.5,true);}
function small(sl,t,x,y,w=5,h=.4,o={}){text(sl,t,x,y,w,h,{fontSize:16,color:sl._dark?'A8BAC9':P.muted,...o});}
function headline(sl,t,x,y,w,h=.8,size=34,col){text(sl,t,x,y,w,h,{fontSize:size,bold:true,color:col||(sl._dark?P.white:P.ink)});}
function statement(sl,t,x=.72,y=5.72,w=11.9,h=.6,col=P.teal){line(sl,x,y,x,y+h,col,3);text(sl,t,x+.18,y,w-.18,h,{fontSize:21,bold:true,color:sl._dark?P.cyan:col});}
function node(sl,t,x,y,w=1.65,h=.85,col=P.teal,sub=''){
 shape(sl,x,y,w,h,sl._dark?P.navy2:P.white,col);
 text(sl,t,x+.10,y+.07,w-.2,h-.14,{fontSize:18,bold:true,align:'center',color:sl._dark?P.white:P.ink});
 if(sub)small(sl,sub,x-.12,y+h+.12,w+.24,.65,{fontSize:15,align:'center',valign:'top'});
}
function list(sl,items,x,y,w,fs=22,gap=.90,col){items.forEach((t,i)=>{line(sl,x,y+i*gap+.10,x,y+i*gap+.43,col||P.teal,2.5);text(sl,t,x+.18,y+i*gap,w-.18,.72,{fontSize:fs,valign:'top'});});}
function equation(sl,t,x,y,w,h=.65,fs=27){
 const runs=[];let cursor=0;const pattern=/_([\p{L}\p{N},]+)/gu;let match;
 while((match=pattern.exec(t))){if(match.index>cursor)runs.push({text:t.slice(cursor,match.index)});runs.push({text:match[1],options:{subscript:true}});cursor=pattern.lastIndex;}
 if(cursor<t.length)runs.push({text:t.slice(cursor)});
 text(sl,runs.length?runs:t,x,y,w,h,{fontFace:'Cambria Math',fontSize:fs,color:sl._dark?P.cyan:P.ink});
}
function table(sl,headers,rows,x,y,w,h,{fontSize=19,colW,highlight=[]}={}){
 const data=[headers.map(v=>({text:String(v),options:{bold:true,color:P.white,fill:P.navy2}})),
 ...rows.map((row,i)=>row.map((v,j)=>({text:String(v),options:{fill:highlight.includes(i)?'DDF2EA':i%2?'EAF0F2':P.white,color:P.ink,bold:highlight.includes(i)}})))];
 sl.addTable(data,{x,y,w,h,fontFace:FONT,fontSize,colW,autoPage:false,rowH:h/(rows.length+1),
  margin:[.08,.12,.08,.12],border:{type:'solid',pt:.6,color:P.line},valign:'middle',paraSpaceAfterPt:0});
 geometry.push({slide:sl._slideNum,kind:'table',x,y,w,h});
}
function chart(sl,type,series,x,y,w,h,opts={}){
 const dark=sl._dark;
 sl.addChart(type,series,{x,y,w,h,catAxisLabelFontFace:FONT,valAxisLabelFontFace:FONT,
  catAxisLabelFontSize:16,valAxisLabelFontSize:15,legendFontFace:FONT,legendFontSize:15,
  catAxisLabelColor:dark?'DCE6EE':P.ink,valAxisLabelColor:dark?'DCE6EE':P.ink,
  legendColor:dark?'DCE6EE':P.ink,showLegend:series.length>1,legendPos:'b',
  showTitle:false,showValue:false,showCatName:false,showBorder:false,
  chartColors:[P.teal,P.blue,P.orange],lineDataSymbol:'circle',lineDataSymbolSize:5,lineSize:2.4,
  showCatName:false,valAxisMinVal:0,valAxisMaxVal:100,valAxisMajorUnit:20,
  catAxisLineColor:dark?'617284':'99AAB6',valAxisLineColor:dark?'617284':'99AAB6',
  showCatName:false,showSerName:false,showCatName:false,
  chartArea:{fill:{color:dark?P.navy:P.cream},border:{color:dark?P.navy:P.cream,transparency:100}},
  plotArea:{fill:{color:dark?P.navy:P.cream},border:{color:dark?P.navy:P.cream,transparency:100}},
  valGridLine:{color:dark?'294155':'D5DFE3',width:.5},
  showValAxisTitle:true,valAxisTitle:'Accuracy (%)',valAxisTitleFontSize:15,
  valAxisTitleColor:dark?'C5D1DD':P.muted,showCatName:false,
  dataLabelPosition:'outEnd',dataLabelFormatCode:'0.00',dataLabelColor:dark?P.white:P.ink,
  dataLabelBkgrdColor:dark?P.navy:P.cream,dataLabelFontSize:15,...opts});
 geometry.push({slide:sl._slideNum,kind:'chart',x,y,w,h});
}
function runFooter(sl,s){
 const runs=s.runs.map(n=>R[n]);
 const y=runs.length>2?6.03:6.15;
 runs.forEach((r,i)=>{
  const u=r.verification.url;
  text(sl,u,.72,y+i*.155,11.9,.17,{fontSize:8.8,color:sl._dark?'8EDDE5':P.teal,
   hyperlink:{url:u,tooltip:`${r.name} — verified public W&B run`},role:'run-link'});
 });
}
function base(s){
 const sl=pptx.addSlide();sl._dark=s.dark;sl.background={color:s.dark?P.navy:P.cream};
 shape(sl,.0,.0,.12,H,s.dark?P.cyan:P.teal);
 small(sl,s.section.toUpperCase(),.72,.32,10,.26,{fontSize:11,bold:true,charSpacing:2,color:s.dark?P.cyan:P.teal});
 if(s.kind!=='cover')headline(sl,s.title,.72,.83,11.95,.87,32);
 if(s.kind!=='cover')small(sl,s.message,.75,1.72,11.7,.58,{fontSize:19,color:s.dark?'B8CDD9':P.muted,valign:'top'});
 line(sl,.72,6.72,12.6,6.72,s.dark?'2A4053':P.line,.65);
 const refs=s.refs.map(id=>content.references[id].short).join('\n');
 if(refs)text(sl,refs,.74,6.81,11.6,.50,{fontSize:s.refs.length>2?8.8:9.4,color:s.dark?'A1B4C3':P.muted,valign:'top',role:'citation'});
 text(sl,String(s.number).padStart(2,'0')+' / '+content.slides.length,12.01,7.23,.61,.18,{fontSize:9.4,color:s.dark?'A1B4C3':P.muted,align:'right',role:'page'});
 const provenance=s.runs.map(n=>`${n}: ${R[n].verification.url}\nConfig: ${R[n].directory}/config.json; metrics: ${R[n].directory}/metrics.jsonl`).join('\n');
 sl.addNotes(`${s.notes}\n\n${s.refs.map(id=>content.references[id].full+' '+content.references[id].url).join('\n')}\n\n${provenance}`);
 return sl;
}

for(const s of content.slides){
 const sl=base(s);
 switch(s.kind){
 case 'cover':{
   // A large typographic cover with an editable two-stream architecture motif.
   shape(sl,.35,.6,12.6,1.05,P.navy);
   text(sl,'DS-AL',.72,1.7,6.8,1.45,{fontSize:80,bold:true,color:P.white});
   text(sl,'Học tăng dần lớp\nkhông lưu exemplar',.78,3.28,6.2,1.15,{fontSize:30,color:'C6D6E3'});
   node(sl,'MAIN',8.0,2.65,2.65,.9,P.cyan);node(sl,'COMPENSATION',8.0,4.1,2.65,.9,P.blue);
   elbow(sl,10.65,3.1,11.55,3.8,P.cyan);elbow(sl,10.65,4.55,11.55,3.8,P.blue);
   node(sl,'+',11.6,3.40,.8,.8,P.green);
   text(sl,'Vũ  ·  Nam  ·  Đạt',.8,5.05,6,.5,{fontSize:24,bold:true,color:P.white});
   small(sl,'AAAI 2024  /  CIFAR-100  /  Core scope  /  Seed 0',.8,5.80,11,.38,{fontSize:16});break;
 }
 case 'timeline':{
   const xs=[.9,4.65,8.4];
   const title=['PHA BASE','PHA MỚI 1','PHA MỚI 2'];
   const cls=['Chó, mèo','Chim','Cá'];
   xs.forEach((x,i)=>{shape(sl,x,2.75,3.0,.11,i===0?P.teal:P.blue);small(sl,title[i],x,2.35,3,.3,{bold:true});headline(sl,cls[i],x,3.12,3,.6,28);small(sl,['Học hai lớp ban đầu','Chỉ dữ liệu lớp mới','Tiếp tục mở rộng nhãn'][i],x,3.95,3,.7,{fontSize:18});if(i<2)line(sl,x+3.1,3.4,x+3.55,3.4,P.teal,2,true);});
   statement(sl,'Khi thấy một ảnh mèo ở pha cuối, mô hình vẫn phải nhận đúng.',.9,5.2,11.4,.8);break;
 }
 case 'replay':{
   headline(sl,'REPLAY',.85,2.5,5,.5,27);headline(sl,'EXEMPLAR-FREE',7,2.5,5,.5,27);
   node(sl,'Ảnh cũ',.9,3.0,1.65,.8,P.orange);node(sl,'Ảnh mới',.9,4.05,1.65,.8,P.teal);
   node(sl,'Huấn luyện',3.8,3.52,1.9,.8,P.teal);
   elbow(sl,2.55,3.4,3.8,3.92,P.orange);elbow(sl,2.55,4.45,3.8,3.92,P.teal);
   node(sl,'Dữ liệu mới',7.0,3.4,1.65,.8);node(sl,'G, Q, W',9.55,3.4,2.2,.8,P.blue);
   line(sl,8.65,3.8,9.4,3.8,P.blue,1.5,true);
   small(sl,'Giữ exemplar để học cùng dữ liệu hiện tại',.9,4.95,5.2,.65,{fontSize:20});
   small(sl,'Giữ thống kê và tham số của biểu diễn cố định',7,4.6,5.3,.8,{fontSize:20});
   statement(sl,'Không replay trong bước fit không đồng nghĩa với bảo đảm privacy hình thức.',.9,5.7,11.7,.55);break;
 }
 case 'related':{
   table(sl,['Hướng','Cơ chế','Giới hạn và hệ quả'],[
    ['LwF','Distillation trên dữ liệu mới','Đại diện lớp cũ yếu nếu phân phối thay đổi'],
    ['iCaRL / replay','Giữ exemplar','Cần lưu ảnh cũ và ngân sách bộ nhớ'],
    ['ACIL','Ridge trên feature cố định','Một embedding có thể chưa khớp đủ tốt']],.8,2.55,11.8,2.65,{fontSize:19,colW:[2.2,3.6,6.0]});
   statement(sl,'DS-AL phát triển từ ACIL bằng một nhánh học residual.',.85,5.55,11.6,.6);break;
 }
 case 'contributions':{
   const items=[['LÝ THUYẾT','C-RLS','Nghiệm nhánh chính bằng joint ridge'],['KỸ THUẬT','DAC + PLC','Bù phần dư với cấu trúc nhãn disjoint'],['THỰC NGHIỆM','Benchmark & ablation','Kiểm tra accuracy và số pha']];
   items.forEach((it,i)=>{const y=2.5+i*1.12;small(sl,it[0],.85,y,2.2,.3,{color:P.cyan,bold:true});headline(sl,it[1].replace(' & ','\n& '),3.25,y-.08,3.65,i===2?.85:.62,i===2?23:25);text(sl,it[2],7.4,y-.05,4.7,.7,{fontSize:21});line(sl,.85,y+.82,12.0,y+.82,'294155',.7);});break;
 }
 case 'architecture':{
   node(sl,'Ảnh',.65,3.25,1.15,.8);node(sl,'CNN cố định',2.22,3.25,1.85,.8);node(sl,'Buffer B',4.5,3.25,1.55,.8);
   line(sl,1.8,3.65,2.1,3.65,P.cyan,1.6,true);line(sl,4.07,3.65,4.4,3.65,P.cyan,1.6,true);
   node(sl,'ReLU',6.6,2.55,1.5,.8,P.cyan);node(sl,'W_M',8.58,2.55,1.65,.8,P.cyan);
   node(sl,'tanh',6.6,4.35,1.5,.8,P.blue);node(sl,'W_C',8.58,4.35,1.65,.8,P.blue);
   elbow(sl,6.05,3.65,6.6,2.95,P.cyan);elbow(sl,6.05,3.65,6.6,4.75,P.blue);
   line(sl,8.1,2.95,8.45,2.95,P.cyan,1.5,true);line(sl,8.1,4.75,8.45,4.75,P.blue,1.5,true);
   node(sl,'Σ',11.35,3.45,1.0,.8,P.green);elbow(sl,10.23,2.95,11.35,3.85,P.cyan);elbow(sl,10.23,4.75,11.35,3.85,P.blue);
   small(sl,'× C',10.5,4.7,.7,.3,{fontSize:18,color:P.cyan});
   small(sl,'E = Y − X_M W_M\nPLC khi huấn luyện',8.1,3.48,2.3,.64,{fontSize:14.5,color:'AFCDD9'});
   statement(sl,'Backbone và B cố định; chỉ các head/thống kê cập nhật theo pha.',.8,5.65,11.7,.6);break;
 }
 case 'protocol':{
   table(sl,['Pha','0','1','2','3','4','5'],[['Lớp mới','50','10','10','10','10','10'],['Lớp đánh giá','50','60','70','80','90','100']],.85,2.72,11.6,1.85,{fontSize:21,colW:[2.45,...Array(6).fill(1.525)]});
   small(sl,'Train: 50.000 ảnh',.95,4.85,5,.5,{fontSize:24,bold:true});small(sl,'Test: 10.000 ảnh',7,4.85,5,.5,{fontSize:24,bold:true});
   statement(sl,'K=25: 2 lớp mới/pha.  K=50: 1 lớp mới/pha.',.9,5.55,11.6,.45);break;
 }
 case 'notation':{
   table(sl,['Ký hiệu','Kích thước / ý nghĩa'],[['f(x), B','d chiều; B: d × m'],['X_M,k ; X_C,k','nₖ × m, embedding chính / bù'],['Y_k','nₖ × cₖ, nhãn one-hot toàn cục'],['W_M,k ; W_C,k','m × cₖ, head theo các lớp đã gặp'],['R_M,k ; R_C,k','m × m, nghịch đảo tương quan'],['γ ; C ; K','Điều chuẩn ridge; tỷ lệ bù; số pha mới']],.85,2.45,11.6,3.66,{fontSize:20,colW:[4.25,7.35]});break;
 }
 case 'training':{
   const original=path.join(ROOT,R['base-training'].directory,'metrics.jsonl');
   const historyPath=await fs.access(original).then(()=>original).catch(()=>path.join(ROOT,'experiments/evidence/base-training/metrics.jsonl'));
   const hist=(await fs.readFile(historyPath,'utf8')).trim().split('\n').map(x=>JSON.parse(x));
   chart(sl,pptx.ChartType.line,[{name:'Train accuracy',labels:hist.map(r=>String(r['base/epoch'])),values:hist.map(r=>r['base/train_accuracy'])},{name:'Test base accuracy',labels:hist.map(r=>String(r['base/epoch'])),values:hist.map(r=>r['base/test_accuracy'])}],.8,2.43,8.2,3.35,{lineDataSymbol:'none',catAxisLabelFrequency:'20',catAxisLabelFontSize:15,showCatAxisTitle:true,catAxisTitle:'Epoch',showLegend:true});
   headline(sl,'160',9.45,2.48,2.6,1.2,64,P.teal);small(sl,'epoch trên 50 lớp base',9.45,3.85,2.7,.7,{fontSize:19});
   headline(sl,'76,92%',9.45,4.4,2.7,.7,35,P.ink);small(sl,'test base ở epoch cuối',9.45,5.12,2.7,.5,{fontSize:17});break;
 }
 case 'embeddings':{
   node(sl,'f(x) ∈ ℝ⁶⁴',.85,3.1,2,.9);node(sl,'Z = f(x)B',3.45,3.1,2.1,.9);
   line(sl,2.85,3.55,3.3,3.55,P.teal,1.8,true);
   node(sl,'ReLU(Z)',6.25,2.62,2.2,.85,P.teal);node(sl,'tanh(Z)',6.25,4.20,2.2,.85,P.blue);
   elbow(sl,5.55,3.55,6.25,3.045,P.teal);elbow(sl,5.55,3.55,6.25,4.625,P.blue);
   const z=[-2,-1,0,1,2];chart(sl,pptx.ChartType.line,[{name:'ReLU',labels:z.map(String),values:z.map(v=>Math.max(0,v))},{name:'tanh',labels:z.map(String),values:z.map(Math.tanh)}],8.95,2.4,3.6,3.3,{valAxisMinVal:-2,valAxisMaxVal:2,valAxisMajorUnit:1,valAxisTitle:'Activation',showLegend:true,catAxisTitle:'z',showCatAxisTitle:true});
   small(sl,'Minh họa định nghĩa activation; không phải dữ liệu đo.',.88,5.52,10,.4,{fontSize:17});break;
 }
 case 'ridge':{
   equation(sl,'min_W  ‖Y − XW‖²_F + γ‖W‖²_F',1.0,2.65,11.5,.85,35);
   line(sl,1.2,3.7,6.3,3.7,P.teal,3);line(sl,7.7,3.7,11.6,3.7,P.blue,3);
   headline(sl,'Khớp nhãn',1.2,3.95,4.6,.55,28);small(sl,'Giảm sai số trên embedding cố định',1.2,4.6,4.6,.75,{fontSize:21});
   headline(sl,'Điều chuẩn',7.7,3.95,4,.55,28);small(sl,'γ > 0 giúp có nghiệm duy nhất',7.7,4.6,4.1,.75,{fontSize:21});
   equation(sl,'W = (XᵀX + γI)⁻¹XᵀY',1.2,5.55,10,.6,29);break;
 }
 case 'padding':{
   table(sl,['W cũ','Lớp 1','Lớp 2'],[['hàng i','w_i1','w_i2'],['hàng j','w_j1','w_j2']],.9,2.8,4.1,1.8,{fontSize:21,colW:[1.3,1.4,1.4]});
   line(sl,5.15,3.7,5.9,3.7,P.teal,2.5,true);
   table(sl,['W⁺','Lớp 1','Lớp 2','Lớp 3','Lớp 4'],[['hàng i','w_i1','w_i2','0','0'],['hàng j','w_j1','w_j2','0','0']],6.05,2.8,6.4,1.8,{fontSize:20,colW:[1.3,1.275,1.275,1.275,1.275]});
   equation(sl,'Yₖ = [ 0_cũ   Y_mới ]',.95,5.05,10,.62,29);
   small(sl,'Ví dụ ký hiệu: 2 lớp cũ và 2 lớp mới. Các cột luôn có cùng ý nghĩa.',.95,5.8,11.5,.4,{fontSize:18});break;
 }
 case 'crls':{
   equation(sl,'W⁺ = [ Wₖ₋₁   0 ]',.9,2.43,11.5,.53,27);
   equation(sl,'Lₖ = Rₖ₋₁ Xₖᵀ (I + Xₖ Rₖ₋₁ Xₖᵀ)⁻¹',.9,3.18,11.6,.7,29);
   equation(sl,'Rₖ = Rₖ₋₁ − Lₖ Xₖ Rₖ₋₁',.9,4.03,11.6,.67,29);
   equation(sl,'Wₖ = W⁺ + Lₖ (Yₖ − Xₖ W⁺)',.9,4.9,11.6,.67,29);
   small(sl,'Xₖ = X_M,k, Wₖ = W_M,k. Lₖ = RₖXₖᵀ theo Supplement A.11.',.95,5.83,11.6,.4,{fontSize:18});break;
 }
 case 'proof':{
   const steps=[['1','Gₖ = γI + Σᵢ XᵢᵀXᵢ'],['2','Qₖ = Σᵢ XᵢᵀYᵢ  (đã padding)'],['3','Wₖ = Gₖ⁻¹Qₖ']];
   steps.forEach((v,i)=>{const y=2.5+i*1.05;text(sl,v[0],.92,y,.7,.6,{fontSize:34,bold:true,color:P.teal});equation(sl,v[1],2.0,y,10.2,.75,31);});
   statement(sl,'Cộng thống kê của pha mới giữ nguyên objective ridge toàn cục.',.98,5.82,11.4,.52);break;
 }
 case 'guarantee':{
   list(sl,['CNN và B cố định','γ > 0 giữ nguyên giữa các pha','Nhãn disjoint, padding đúng','Cập nhật đủ dữ liệu pha hiện tại'],.9,2.5,5.0,22,.8,P.cyan);
   headline(sl,'Bảo đảm',7.0,2.6,4.9,.5,29,P.cyan);text(sl,'Main head bằng\nnghiệm joint ridge',7.0,3.3,5.1,1.1,{fontSize:31,bold:true});
   text(sl,'Giới hạn: không bảo đảm joint CNN,\naccuracy bất biến hay toàn DAC bất biến.',7.0,4.7,5.2,1.2,{fontSize:21,color:'D6E0E8'});break;
 }
 case 'solvers':{
   headline(sl,'WOODBURY RLS',.9,2.5,5.6,.5,26);headline(sl,'STATS + CHOLESKY',7.0,2.5,5.4,.5,26);
   list(sl,['Duy trì R và cập nhật theo batch','O(m²b + mb² + b³) mỗi batch','Test đối chiếu với nghiệm joint'],.95,3.3,5.0,20,.8);
   list(sl,['Duy trì G và Q, giải cuối pha','O(Nm² + K m³), theo cách giải','Benchmark nhóm dùng float64'],7.05,3.3,5.1,20,.8);
   statement(sl,'Hai cách giải cùng objective; không đồng nhất runtime của chúng.',.95,5.9,11.5,.5);break;
 }
 case 'residual':{
   const xs=[.85,4.65,8.45];const labels=['Fit toàn bộ main','Eₖ = Yₖ − X_M,k W_M,k','Fit compensation'];
   xs.forEach((x,i)=>{node(sl,labels[i],x,3.0,3.25,1.0,i===2?P.blue:P.teal);if(i<2)line(sl,x+3.3,3.5,x+3.65,3.5,P.teal,2,true);});
   small(sl,'Kết thúc pha k',.9,4.35,3.2,.6,{fontSize:20});small(sl,'Tạo nhãn sau nghiệm main cuối',4.65,4.35,3.25,.7,{fontSize:20});small(sl,'Áp PLC ở pha mới',8.45,4.35,3.3,.6,{fontSize:20});
   statement(sl,'Residual sau từng minibatch tạo ra một ngữ nghĩa khác.',.9,5.55,11.5,.65);break;
 }
 case 'plc':{
   small(sl,'2 cột lớp cũ',3.6,2.38,4.4,.3,{bold:true,color:P.orange,align:'center'});small(sl,'2 cột lớp mới',8.0,2.38,4.4,.3,{bold:true,color:P.teal,align:'center'});
   table(sl,['Residual E','Cũ 1','Cũ 2','Mới 3','Mới 4'],[['Mẫu lớp 3','−0.20','−0.10','0.45','−0.15'],['Mẫu lớp 4','−0.05','−0.25','−0.10','0.40']],.9,2.83,11.5,1.36,{fontSize:21,colW:[2.7,2.2,2.2,2.2,2.2]});
   table(sl,['Sau PLC','Cũ 1','Cũ 2','Mới 3','Mới 4'],[['Mẫu lớp 3','0','0','0.45','−0.15'],['Mẫu lớp 4','0','0','−0.10','0.40']],.9,4.55,11.5,1.36,{fontSize:21,colW:[2.7,2.2,2.2,2.2,2.2]});
   small(sl,'Ví dụ đại số minh họa. Giữ cả residual âm trong các cột mới; pha 0 không áp PLC.',.95,6.15,11.4,.35,{fontSize:16});break;
 }
 case 'fusion':{
   node(sl,'X_M W_M',1.1,2.9,3.05,1.0,P.cyan);node(sl,'C · X_C W_C',1.1,4.5,3.05,1.0,P.blue);
   elbow(sl,4.15,3.4,6.0,4.1,P.cyan);elbow(sl,4.15,5.0,6.0,4.1,P.blue);
   node(sl,'Σ',6.05,3.55,1.0,1.1,P.green);line(sl,7.05,4.1,7.85,4.1,P.green,2,true);node(sl,'argmax trên cₖ lớp',8.05,3.55,4.2,1.1,P.green);
   small(sl,'C = 0,6 trong suite CIFAR-100',8.1,5.0,4.2,.65,{fontSize:21});
   statement(sl,'Score chưa chuẩn hóa không tự động là xác suất calibrated.',.95,5.95,11.4,.5);break;
 }
 case 'memory':{
   headline(sl,'1 GiB',.95,2.4,5.3,1.4,74,P.cyan);equation(sl,'2 × 8192² × 8 byte',1.0,3.95,5.4,.6,26);
   small(sl,'Chỉ hai ma trận FP64\nStorage lý thuyết, không phải peak RAM đo',1.0,4.8,5.3,1.2,{fontSize:22});
   table(sl,['m','Hai ma trận'],[[512,'4 MiB'],[1024,'16 MiB'],[2048,'64 MiB'],[8192,'1024 MiB']],7.2,2.72,5.0,2.6,{fontSize:21,colW:[2.0,3.0]});
   text(sl,'Còn head O(mc), B O(dm),\nworkspace Cholesky, CNN và cache.',7.2,5.5,5.1,.7,{fontSize:21});break;
 }
 case 'metrics':{
   equation(sl,'Ā = (A₀ + … + A_K) / (K + 1)',.9,2.6,11.6,.7,30);
   const p=R['dsal-k5'].phases;chart(sl,pptx.ChartType.line,[{name:'DS-AL seed 0',labels:p.map(x=>String(x.phase)),values:p.map(x=>x.accuracy)}],.9,3.5,7.0,2.35,{showLegend:false,showCatAxisTitle:true,catAxisTitle:'Pha k'});
   headline(sl,'A_K = 56,87%',8.5,3.65,3.6,.8,33,P.teal);small(sl,'Đủ 100 lớp ở pha cuối',8.5,4.62,3.5,.7,{fontSize:21});break;
 }
 case 'scope':{
   const rows=[['E1','Đối sánh Table 1','CIFAR-100 / ResNet-32 / K=5'],['E2','Ablation DAC / PLC','Chuyển ImageNet-Full sang CIFAR-100'],['E3','Phân tích nhóm thiết kế','Chiều buffer và accuracy / thời gian']];
   rows.forEach((v,i)=>{let y=2.55+i*1.12;headline(sl,v[0],.9,y,1.1,.6,32,P.cyan);headline(sl,v[1],2.35,y,4.3,.7,25);text(sl,v[2],7.0,y,5.1,.8,{fontSize:22});line(sl,.95,y+.91,12.1,y+.91,'294155',.7);});
   small(sl,'Không claim tái hiện nguyên Table 2, ImageNet hoặc K=500.',.95,6.25,11.5,.3,{fontSize:17,color:'F1BE7C'});break;
 }
 case 'setup':{
   const cfg=R['dsal-k5'].config,rev=cfg.feature_identity.dataset.revision;
   table(sl,['Thành phần','Thiết lập nhóm'],[['Dataset','CIFAR-100, B50, revision '+rev.slice(0,12)],['Backbone','ResNet-32, 64-D, checkpoint epoch 160'],['Analytic','m=8192, γ=0.1, C=0.6, tanh'],['Projection / solver','N(0,1), không bias; stats / float64'],['Ghép cặp biến thể','Cùng feature cache, class order và seed 0']],.85,2.43,11.65,3.18,{fontSize:20,colW:[3.3,8.35]});break;
 }
 case 'tests':{
   headline(sl,'11 / 11',.95,2.45,4.2,1.2,65,P.teal);small(sl,'kiểm thử đạt\nchạy lại trong đợt rà soát',1.0,3.75,4.2,1.0,{fontSize:22});
   list(sl,['RLS / stats bằng joint ridge','Residual cuối pha và PLC đúng cột','Chunk size giữ ngữ nghĩa pha','Resume khớp quỹ đạo tối ưu','Sync giữ file gốc, chặn ID collision'],5.6,2.47,6.5,20,.70);
   small(sl,'Core tự viết: src/methods/analytic.py. Mã tác giả chỉ dùng đối chiếu riêng.',1,6.1,11.3,.38,{fontSize:17});break;
 }
 case 'provenance': case 'trace':{
   const labels=['Config','Data revision','Checkpoint hash','Metrics','W&B'];
   labels.forEach((t,i)=>{node(sl,t,.85+i*2.42,3.0,2.05,.95,i===4?P.green:P.teal);if(i<4)line(sl,2.92+i*2.42,3.47,3.16+i*2.42,3.47,P.teal,1.5,true);});
   small(sl,'Commit run: d8d485f + dirty=true; giữ manifest source SHA-256.',.95,4.65,11.5,.55,{fontSize:22});
   small(sl,'Repo public: mã, snapshot log/config và mapping W&B truy vết kết quả.',.95,5.4,11.5,.55,{fontSize:21,color:P.teal});break;
 }
 case 'paper_table':{
   table(sl,['K','ACIL Ā','DS-AL Ā','ACIL A_K','DS-AL A_K'],[
    [5,'66.30','66.39 ±0.09','57.78','58.26 ±0.09'],[25,'65.95','66.20 ±0.05','57.65','58.32 ±0.12'],[50,'66.01','66.33 ±0.11','57.83','58.37 ±0.15']],.85,2.75,11.6,2.15,{fontSize:21,colW:[1,2.3,3.0,2.3,3.0]});
   text(sl,'Nguồn: tác giả, Table 1. CIFAR-100 ResNet-32; các giá trị trong ngoặc của ResNet-18 được loại.',.95,5.3,11.4,.85,{fontSize:22,color:'B9D0DE'});break;
 }
 case 'paper_compare':{
   const a=sum('acil-k5'),d=sum('dsal-k5');
   headline(sl,'Trung bình Ā',1.0,2.4,5.6,.45,24);headline(sl,'Pha cuối A_K',7,2.4,5.0,.45,24);
   chart(sl,pptx.ChartType.bar,[{name:'Paper',labels:['ACIL','DS-AL'],values:[66.30,66.39]},{name:'Nhóm seed 0',labels:['ACIL','DS-AL'],values:[a.average_accuracy,d.average_accuracy]}],.8,2.98,5.8,2.72,{barDir:'col',showValue:true,showMarker:false,chartColors:['9EAFBB',P.teal]});
   chart(sl,pptx.ChartType.bar,[{name:'Paper',labels:['ACIL','DS-AL'],values:[57.78,58.26]},{name:'Nhóm seed 0',labels:['ACIL','DS-AL'],values:[a.last_accuracy,d.last_accuracy]}],6.85,2.98,5.8,2.72,{barDir:'col',showValue:true,showMarker:false,chartColors:['9EAFBB',P.teal]});break;
 }
 case 'gap':{
   const a=sum('acil-k5'),d=sum('dsal-k5');
   table(sl,['Phương pháp','Paper A_K','Nhóm A_K','Δ (pp)','Δ tương đối'],[
    ['ACIL','57.78',fmt(a.last_accuracy),fmt(a.last_accuracy-57.78),fmt(100*(a.last_accuracy-57.78)/57.78)+'%'],
    ['DS-AL','58.26',fmt(d.last_accuracy),fmt(d.last_accuracy-58.26),fmt(100*(d.last_accuracy-58.26)/58.26)+'%']],.85,2.7,11.6,1.95,{fontSize:21,colW:[2.4,2.3,2.3,2,2.6]});
   text(sl,'Δ tương đối = 100 × (nhóm − paper) / paper',.98,5.05,11.3,.65,{fontSize:27,color:P.cyan});
   small(sl,'Paper: mean 3 runs. Nhóm: một seed. Chưa suy ra nguyên nhân hoặc ý nghĩa thống kê.',.98,5.75,11.3,.45,{fontSize:18});break;
 }
 case 'ablation':{
   const names=['acil-k5','dac-no-plc-k5','dsal-k5'];
   table(sl,['Biến thể','Ā (%)','A_K (%)'],names.map((n,i)=>[['ACIL','DAC không PLC','DAC + PLC'][i],fmt(sum(n).average_accuracy),fmt(sum(n).last_accuracy)]),.9,2.65,7.2,2.3,{fontSize:23,colW:[3.5,1.85,1.85],highlight:[2]});
   headline(sl,'+0,63 pp',8.7,2.9,3.6,.9,42,P.green);small(sl,'PLC so với DAC không PLC',8.7,3.9,3.6,.72,{fontSize:20});
   small(sl,'DAC đơn lẻ: −0,32 pp so với ACIL.\nDS-AL đầy đủ: +0,31 pp so với ACIL.',.98,5.25,11.2,.7,{fontSize:21});break;
 }
 case 'phase_curves':{
   const n=['acil-k5','dac-no-plc-k5','dsal-k5'];
   chart(sl,pptx.ChartType.line,n.map((name,i)=>({name:['ACIL','DAC không PLC','DS-AL'][i],labels:R[name].phases.map(p=>String(p.classes)),values:R[name].phases.map(p=>p.accuracy)})),.85,2.5,7.6,3.23,{showCatAxisTitle:true,catAxisTitle:'Số lớp đã gặp'});
   headline(sl,'Lớp mới',9.0,2.7,3.0,.45,25);headline(sl,'+2,60 pp',9.0,3.25,3.1,.7,34,P.green);
   headline(sl,'Lớp base',9.0,4.2,3.0,.45,25);headline(sl,'−1,98 pp',9.0,4.75,3.1,.7,34,P.orange);
   small(sl,'DS-AL so với ACIL, pha cuối',8.95,5.6,3.4,.38,{fontSize:15});break;
 }
 case 'phase_sweep':{
   const names=['dsal-k5','dsal-k25','dsal-k50'];
   table(sl,['K','Ā (%)','A_K (%)'],names.map((n,i)=>[[5,25,50][i],fmt(sum(n).average_accuracy),fmt(sum(n).last_accuracy)]),.9,2.65,6.4,2.25,{fontSize:24,colW:[1.4,2.5,2.5]});
   headline(sl,'0,04 pp',8.1,2.98,4.1,.95,48,P.teal);small(sl,'Khoảng dao động A_K\ntrong 3 cấu hình K',8.15,4.03,3.8,.98,{fontSize:23});
   small(sl,'Quan sát ổn định ở seed 0; chưa chứng minh bất biến chính xác toàn DS-AL.',.98,5.48,11.2,.55,{fontSize:21});break;
 }
 case 'research_design':{
   headline(sl,'m',.98,2.5,1.4,1.25,70,P.teal);text(sl,'512   1024   2048   8192',2.6,2.85,9.2,.8,{fontSize:34,bold:true});
   table(sl,['Giữ cố định','Thay đổi / đo'],[['CIFAR, backbone, class order, seed 0','Biến độc lập: chiều buffer m'],['γ=0.1, C=0.6, tanh, stats/FP64','Đo: Ā, A_K, fit_seconds'],['Cùng feature cache và K=5','Giả thuyết: capacity tăng, chi phí tăng']],.95,3.75,11.4,1.6,{fontSize:17.5,colW:[6.1,5.3]});
   small(sl,'Giới hạn: projection cùng seed nhưng không lồng nhau; chỉ một realization.',.98,5.62,11.4,.34,{fontSize:17,color:P.orange});break;
 }
 case 'buffer_results':{
   const names=['buffer-512','buffer-1024','buffer-2048','dsal-k5'];
   chart(sl,pptx.ChartType.bar,[{name:'A_K',labels:['512','1024','2048','8192'],values:names.map(n=>sum(n).last_accuracy)}],.8,2.65,6.15,3.15,{barDir:'col',showValue:true,showLegend:false,showCatAxisTitle:true,catAxisTitle:'Chiều buffer m',chartColors:[P.teal]});
   table(sl,['m','A_K (%)','Fit (s)'],names.map((n,i)=>[[512,1024,2048,8192][i],fmt(sum(n).last_accuracy),fmt(sum(n).fit_seconds,3)]),7.45,2.8,4.95,2.6,{fontSize:20,colW:[1.25,1.75,1.95]});
   small(sl,'Fit CPU, cộng các pha. Không gồm huấn luyện CNN, feature extraction hoặc logging.',7.45,5.55,4.95,.5,{fontSize:15});break;
 }
 case 'evidence_hypothesis':{
   headline(sl,'ĐÃ XÁC MINH',.95,2.5,5.3,.5,26,P.teal);headline(sl,'CẦN KIỂM CHỨNG',7.0,2.5,5.4,.5,26,P.orange);
   list(sl,['Nhóm 1 seed; paper mean 3 runs','Stats solver khác đường chạy RLS','Residual nhạy với cách chia batch'],1.0,3.28,5.1,20,.88);
   list(sl,['Ảnh hưởng class order / khởi tạo','Ảnh hưởng phân phối projection','Mức đóng góp từng yếu tố vào gap'],7.05,3.28,5.0,20,.88,P.orange);
   statement(sl,'Khác biệt cấu hình không tự chứng minh nguyên nhân gap accuracy.',.98,5.98,11.4,.5);break;
 }
 case 'conclusion':{
   const items=[['56,87%','A_K của DS-AL K=5'],['+0,31 pp','DS-AL so với ACIL'],['+0,63 pp','PLC so với DAC không PLC']];
   items.forEach((v,i)=>{let x=.95+i*4.05;headline(sl,v[0],x,2.75,3.8,1.0,42,P.cyan);text(sl,v[1],x,4.0,3.6,.9,{fontSize:23});});
   text(sl,'Kết luận giới hạn ở seed 0 và protocol CIFAR-100 đã khai báo.\nChưa có mean/std nhiều seed hoặc benchmark ImageNet.',.98,5.3,11.4,.68,{fontSize:21,color:'C8D9E6'});break;
 }
 case 'evidence_gap':{
   headline(sl,'Đã xác minh',.95,2.5,5.5,.55,28,P.teal);
   headline(sl,'Chưa xác định nhân quả',7.0,2.5,5.5,.55,28,P.orange);
   list(sl,['Nhóm: 1 seed; paper: mean 3 runs','Stats và RLS cùng objective ở tests','Ablation đã chuyển dataset','Batch đổi thời điểm tạo residual'],1.0,3.15,5.4,19,.58);
   list(sl,['Class order và khởi tạo backbone','Phân phối projection chưa đủ rõ','Ảnh hưởng phiên bản thư viện','Mức đóng góp của từng yếu tố vào gap'],7.05,3.15,5.2,19,.58,P.orange);
   small(sl,'Khác biệt môi trường được ghi nhận không tự trở thành lời giải thích cho accuracy gap.',1.0,5.72,11.4,.33,{fontSize:16});break;
 }
 case 'gain_detail':{
   equation(sl,'Lₖ = Rₖ₋₁ Xₖᵀ (I + Xₖ Rₖ₋₁ Xₖᵀ)⁻¹ = RₖXₖᵀ',.9,2.65,11.5,.85,26);
   table(sl,['Đối tượng','Kích thước'],[['Xₖ','nₖ × m'],['Lₖ','m × nₖ'],['Yₖ − XₖW⁺','nₖ × cₖ'],['Lₖ(Yₖ − XₖW⁺)','m × cₖ']],1.1,3.8,10.8,2.2,{fontSize:23,colW:[6.4,4.4]});break;
 }
 case 'reference':{
   const rows=evidence.reference.measurements;
   table(sl,['Batch tác giả','Δ main tối đa','Δ compensation','Δ score'],rows.map(r=>[r.official_batch_size,r.main_max_abs_difference.toExponential(2),r.comp_max_abs_difference.toExponential(2),r.scores_max_abs_difference.toExponential(2)]),.9,2.7,11.5,1.9,{fontSize:22,colW:[2.9,2.9,2.9,2.8]});
   statement(sl,'Cùng projection và đầu vào nhỏ; chỉ đổi cách chia batch của mã tham chiếu.',.98,5.12,11.3,.72);
   small(sl,'Checkout tác giả: 0afd6bf87622e808ce7f730f8556e78229b9e758',.98,5.85,11.4,.25,{fontSize:15});break;
 }
 case 'mechanism':{
   const rows=evidence.mechanisms['phase-dependence'];
   chart(sl,pptx.ChartType.line,[0,1,2].map(seed=>({name:'Seed '+seed,labels:['1','2','5'],values:rows.filter(r=>r.seed===seed).map(r=>r.comp_relative_difference)})),.9,2.6,7.1,3.25,{valAxisMinVal:0,valAxisMaxVal:.6,valAxisMajorUnit:.2,valAxisTitle:'Δ tương đối W_C',showCatAxisTitle:true,catAxisTitle:'Số pha mới'});
   headline(sl,'W_M ≈ bất biến',8.55,2.9,3.9,.75,27,P.teal);small(sl,'Sai khác cỡ 10⁻¹⁴',8.6,3.7,3.6,.6,{fontSize:22});
   headline(sl,'W_C có thay đổi',8.55,4.55,3.9,.75,27,P.orange);small(sl,'Cơ chế tổng hợp, không phải CIFAR',8.6,5.4,3.7,.45,{fontSize:16});break;
 }
 case 'provenance_detail':{
   const c=R['dsal-k5'].config,id=c.feature_identity;
   table(sl,['Thông tin','Giá trị lưu lại'],[['Class order (12 lớp đầu)',id.class_order.slice(0,12).join(', ')],['Dataset revision',id.dataset.revision],['Checkpoint SHA-256',id.checkpoint_sha256],['Seed / dtype / solver','0 / float64 / stats'],['Phiên bản chạy','Python 3.11.8; torch 2.5.1+cpu; W&B 0.23.1']],.85,2.5,11.6,3.12,{fontSize:17,colW:[3.9,7.7]});
   small(sl,'Config và manifest đầy đủ nằm trong assets/verified_evidence.json của bộ slide.',.98,5.8,11.3,.4,{fontSize:17});break;
 }
 case 'readiness':{
   const items=[['Đã có','40 slide, notes, citations, số đo seed 0 và W&B public'],['Nguồn công khai','Repo, mã tạo slide, snapshot log và mapping W&B'],['Cần nêu giới hạn','Một seed; ablation chuyển dataset; chưa có ImageNet'],['Cần nhóm bảo vệ','Hiểu công thức, protocol, gap và phân tích tự thiết kế']];
   items.forEach((v,i)=>{let y=2.5+i*.91;text(sl,v[0],.98,y,3.0,.6,{fontSize:23,bold:true,color:i===0?P.cyan:'EAB780'});text(sl,v[1],4.25,y,8.0,.65,{fontSize:21});});break;
 }
 default:throw new Error('Unknown slide kind '+s.kind);
 }
 if(s.runs.length)runFooter(sl,s);
}

const output=path.join(HERE,'DSAL_Milestone2_Lab1_Final.pptx');
await pptx.writeFile({fileName:output,compression:true});
// PptxGenJS 4.0.1 leaves a non-existent slideMaster override. Remove only that override.
const zip=await JSZip.loadAsync(await fs.readFile(output));
let ct=await zip.file('[Content_Types].xml').async('string');
ct=ct.replace(/<Override\b[^>]*PartName="([^"]+)"[^>]*\/>/g,(match,part)=>zip.file(part.replace(/^\//,''))?match:'');
zip.file('[Content_Types].xml',ct);
await fs.writeFile(output,await zip.generateAsync({type:'nodebuffer',compression:'DEFLATE'}));
await fs.copyFile(output,path.join(HERE,'03.pptx'));
await fs.writeFile(path.join(HERE,'.build/geometry.json'),JSON.stringify(geometry,null,2));
await fs.writeFile(path.join(HERE,'.build/build.json'),JSON.stringify({slides:content.slides.length,font:FONT,
 output,source_sha256:createHash('sha256').update(JSON.stringify(content)).digest('hex'),
 evidence_sha256:createHash('sha256').update(JSON.stringify(evidence)).digest('hex')},null,2));
console.log(JSON.stringify({output,slides:content.slides.length,bytes:(await fs.stat(output)).size}));
