/** User-authorized PptxGenJS workflow; reuse v2 design then splice into actual v3. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {pathToFileURL} from 'node:url';
const HERE=path.dirname(fileURLToPath(import.meta.url));
const BUILD=path.join(HERE,'.build/three-seeds');
await fs.mkdir(BUILD,{recursive:true});
let code=await fs.readFile(path.join(HERE,'build_slides_v2.mjs'),'utf8');
code=code.replace("const HERE=path.dirname(fileURLToPath(import.meta.url));",`const HERE=${JSON.stringify(HERE)};`)
 .replaceAll('slide_content_v2.json','slide_content_three_seeds.json')
 .replaceAll('.build/v2','.build/three-seeds')
 .replace("pptx.title='DS-AL — Milestone 2 + Lab 1 — v2'","pptx.title='DS-AL — Milestone 2 + Lab 1 — Three Seeds'")
 .replace('Verified seed-0 CIFAR-100 reproduction and independent reading','Verified three-seed CIFAR-100 reproduction and independent reading')
 .replace('margin:[.08,.12,.08,.12]','margin:[.035,.10,.035,.10]');
code=code.replace(/^const output=.*$/m,`const output=${JSON.stringify(path.join(BUILD,'generated.pptx'))};`);
code=code.replace("const sum=n=>R[n].summary;",`const sum=n=>R[n].summary;
const V=JSON.parse(await fs.readFile(path.join(HERE,'assets/three_seeds_verified.json'),'utf8'));
const A=V.aggregates,D=V.paired;
const vr=(m,s)=>V.runs.find(r=>r.method===m&&r.seed===s);
const fv=(v,d=2)=>Number(v).toFixed(d).replace('.',',');
const ms=(m,k,d=2)=>fv(A[m][k].mean,d)+' ± '+fv(A[m][k].sd,d);
const mn=(m,k)=>A[m][k].mean;
const seeds=[0,1,2],core=['acil-k5','dac-no-plc-k5','dsal-k5'];
const methodLabel={'base-training':'Backbone','acil-k5':'ACIL','dac-no-plc-k5':'DAC−PLC','dsal-k5':'DS-AL'};
const seedSources=s=>(s.seedMethods||[]).flatMap(m=>seeds.map(seed=>vr(m,seed)));
`);
const oldFooterStart=code.indexOf('function runFooter(sl,s){');
const oldFooterBody=code.indexOf(" const runs=s.runs.map",oldFooterStart);
code=code.slice(0,oldFooterBody)+` if(s.seedMethods?.length){
  const y=s.number===25?6.31:6.23;
  small(sl,'W&B',.75,y+.01,.65,.27,{fontSize:13,bold:true});
  const step=10.9/s.seedMethods.length;
  s.seedMethods.forEach((m,i)=>{
   const gx=1.5+i*step;
   text(sl,methodLabel[m],gx,y,1.12,.30,{fontSize:14,bold:true,color:sl._dark?'C5D9E3':P.muted});
   seeds.forEach((seed,j)=>{
    const url=vr(m,seed).url;
    text(sl,'s'+seed,gx+1.22+j*.56,y,.45,.30,{fontSize:14,color:sl._dark?'8EDDE5':P.teal,hyperlink:{url,tooltip:methodLabel[m]+' seed '+seed+' — '+url},role:'run-link'});
   });
  });
  return;
 }
`+code.slice(oldFooterBody);
code=code.replace("const provenance=s.runs.map(n=>", "const legacyProvenance=s.runs.map(n=>");
code=code.replace("sl.addNotes(`${s.notes}","const provenance=[legacyProvenance,...seedSources(s).map(r=>`${r.method} seed ${r.seed}: ${r.url}\\nConfig: ${r.directory}/config.json; history: ${r.directory}/metrics.jsonl`)].filter(Boolean).join('\\n');\n sl.addNotes(`${s.notes}");
code=code.replace('if(s.runs.length)runFooter(sl,s);','if(s.runs.length||s.seedMethods?.length)runFooter(sl,s);');
code=code.replace('AAAI 2024  /  CIFAR-100  /  Core scope  /  Seed 0','AAAI 2024  /  CIFAR-100  /  Core scope  /  Seeds 0, 1, 2');
code=code.replace('Chuyển ImageNet-Full sang CIFAR-100','Chuyển ImageNet-Full\\nsang CIFAR-100');

function replaceCase(kind,body){
 const marker=kind==='trace'?" case 'provenance': case 'trace':{":` case '${kind}':{`;
 const start=code.indexOf(marker);
 if(start<0)throw new Error('Missing case '+kind);
 let end=code.indexOf("\n case '",start+marker.length);
 if(end<0)end=code.indexOf('\n default:',start);
 code=code.slice(0,start)+marker+'\n'+body+'\n }'+code.slice(end);
}
replaceCase('training',`
 const hist=seeds.map(seed=>vr('base-training',seed).history);
 const labels=hist[0].map(r=>r['base/epoch']===1||r['base/epoch']%20===0?String(r['base/epoch']):'');
 chart(sl,pptx.ChartType.line,seeds.map(seed=>({name:'Seed '+seed,labels,values:hist[seed].map(r=>r['base/test_accuracy'])})),.8,2.43,8.1,3.45,{lineDataSymbol:'none',lineSize:1.8,catAxisLabelFrequency:'1',catAxisLabelFontSize:15,showCatAxisTitle:true,catAxisTitle:'Epoch',valAxisTitle:'Test base accuracy (%)',chartColors:[P.blue,P.orange,P.teal],showLegend:true});
 headline(sl,'160 × 3',9.25,2.5,3.2,.8,43,P.teal);
 small(sl,'epoch × backbone độc lập',9.3,3.38,3.0,.55,{fontSize:17});
 seeds.forEach((seed,i)=>text(sl,'s'+seed+': '+fv(hist[seed].at(-1)['base/test_accuracy'])+'%',9.3,4.10+i*.49,3.0,.40,{fontSize:25,bold:true,color:[P.blue,P.orange,P.teal][seed]}));
 small(sl,'Accuracy test trên lớp base, khác A_K incremental',.95,5.91,11.3,.25,{fontSize:15});break;`);
replaceCase('metrics',`
 equation(sl,'Ā_s = (A_s,0 + … + A_s,5) / 6',.9,2.52,11.5,.65,29);
 equation(sl,'μ(Ā) = (Ā_0 + Ā_1 + Ā_2) / 3',.9,3.24,11.5,.60,27);
 small(sl,'A_K của từng seed (%)',1.5,3.91,5.2,.25,{fontSize:15});
 chart(sl,pptx.ChartType.bar,[{name:'DS-AL A_K',labels:seeds.map(s=>'Seed '+s),values:seeds.map(s=>vr('dsal-k5',s).summary.last_accuracy)}],.88,4.22,6.5,1.78,{barDir:'col',showValue:true,showLegend:false,catAxisLabelFontSize:15,valAxisLabelFontSize:13,showValAxisTitle:false,chartColors:[P.teal]});
 headline(sl,'DS-AL, 3 seed',7.85,4.02,4.6,.40,24,P.teal);
 text(sl,'Ā: '+ms('dsal-k5','average_accuracy')+'%\\nA_K: '+ms('dsal-k5','last_accuracy')+'%',7.85,4.64,4.6,.92,{fontSize:23,bold:true});
 small(sl,'SD mẫu: n=3, ddof=1; không phải SE/CI',7.85,5.72,4.6,.35,{fontSize:15});break;`);
replaceCase('setup',`
 const rev=vr('dsal-k5',0).config.feature_identity.dataset.revision;
 table(sl,['Thành phần','Thiết lập đã xác minh'],[
 ['Dataset','CIFAR-100, B50, revision '+rev.slice(0,12)],
 ['Backbone','3 ResNet-32 độc lập, 64-D, epoch 160'],
 ['Analytic','m=8192, γ=0.1, C=0.6, tanh'],
 ['Projection / solver','N(0,1), không bias; stats / float64'],
 ['Ghép cặp trong seed','Chung checkpoint, cache, class order, projection']
 ],.85,2.43,11.65,3.18,{fontSize:20,colW:[3.3,8.35]});
 small(sl,'Seed 0: CUDA → CPU sau epoch 19; seed 1/2: CPU xuyên suốt.',.98,5.86,11.35,.30,{fontSize:17,color:P.orange});break;`);
replaceCase('tests',`
 headline(sl,'15 / 15',.95,2.45,4.2,1.2,65,P.teal);
 small(sl,'kiểm thử đại số,\\nprotocol, resume và logging',1.0,3.75,4.25,1.10,{fontSize:21});
 list(sl,['Ridge / residual / PLC / chunk size','Resume giữ trạng thái hợp lệ','Sync chặn ID hoặc history sai','Chỉ tính SD khi đủ ba seed','Ba cache và projection được đối chiếu'],5.6,2.47,6.5,20,.70);
 small(sl,'Core tự viết: src/methods/analytic.py. Mã tác giả dùng đối chiếu riêng.',1,6.1,11.3,.38,{fontSize:17});break;`);
replaceCase('trace',`
 const items=[['Biểu diễn','Chung backbone và\\ncache trong mỗi seed'],['Protocol','Chung class order và\\nprojection trong mỗi seed'],['Cách giải','Giữ stats / FP64\\nvà hyperparameters']];
 items.forEach((it,i)=>{let x=.9+i*4.05;line(sl,x,2.6,x+3.6,2.6,i===1?P.blue:P.teal,2);headline(sl,it[0],x,2.82,3.6,.55,27);text(sl,it[1],x,3.35,3.6,.78,{fontSize:21});});
 table(sl,['Đối sánh','Phạm vi dữ liệu'],[
 ['E1 / E2: ACIL, DAC, PLC','Seed 0, 1, 2; backbone riêng cho mỗi seed'],
 ['Số pha K: 5 / 25 / 50','Chỉ seed 0; không gộp với mean ba seed'],
 ['Buffer: 512 / 1024 / 2048 / 8192','Chỉ seed 0; K=5 và cùng feature cache']
 ],.9,4.22,11.4,1.72,{fontSize:17.5,colW:[4.35,7.05]});break;`);
replaceCase('paper_compare',`
 const names=['acil-k5','dsal-k5'];
 headline(sl,'Trung bình qua pha Ā',1,2.4,5.6,.45,24);
 headline(sl,'Accuracy pha cuối A_K',7,2.4,5.4,.45,24);
 chart(sl,pptx.ChartType.bar,[{name:'Paper mean',labels:['ACIL','DS-AL'],values:[66.30,66.39]},{name:'Nhóm mean ± SD',labels:['ACIL','DS-AL'],values:names.map(m=>mn(m,'average_accuracy'))}],.8,2.94,5.8,2.58,{barDir:'col',showValue:true,chartColors:['9EAFBB',P.teal],legendFontSize:14,dataLabelFontSize:14});
 chart(sl,pptx.ChartType.bar,[{name:'Paper mean',labels:['ACIL','DS-AL'],values:[57.78,58.26]},{name:'Nhóm mean ± SD',labels:['ACIL','DS-AL'],values:names.map(m=>mn(m,'last_accuracy'))}],6.85,2.94,5.8,2.58,{barDir:'col',showValue:true,chartColors:['9EAFBB',P.teal],legendFontSize:14,dataLabelFontSize:14});
 small(sl,'ACIL '+ms('acil-k5','average_accuracy')+'   DS-AL '+ms('dsal-k5','average_accuracy'),.98,5.80,5.65,.30,{fontSize:17});
 small(sl,'ACIL '+ms('acil-k5','last_accuracy')+'   DS-AL '+ms('dsal-k5','last_accuracy'),7.03,5.80,5.55,.30,{fontSize:17});break;`);
replaceCase('gap',`
 const refs={'acil-k5':[66.30,57.78],'dsal-k5':[66.39,58.26]};
 table(sl,['Phương pháp','Δ Ā (pp)','Δ Ā tương đối','Δ A_K (pp)','Δ A_K tương đối'],['acil-k5','dsal-k5'].map(m=>{
 const ref=refs[m],a=mn(m,'average_accuracy'),k=mn(m,'last_accuracy');
 return [methodLabel[m],fv(a-ref[0],3),fv(100*(a-ref[0])/ref[0],3)+'%',fv(k-ref[1],3),fv(100*(k-ref[1])/ref[1],3)+'%'];
 }),.85,2.70,11.6,1.95,{fontSize:21,colW:[2.0,2.0,2.8,2.0,2.8]});
 text(sl,'Δ_pp = mean(nhóm) − mean(paper)',.98,5.0,11.3,.55,{fontSize:27,color:P.cyan});
 small(sl,'Chênh lệch mô tả; chưa có kiểm định và chưa tách nguyên nhân.',.98,5.67,11.3,.42,{fontSize:19});break;`);
replaceCase('ablation',`
 table(sl,['Biến thể','Ā ± SD (%)','A_K ± SD (%)'],core.map(m=>[m==='dsal-k5'?'DS-AL (DAC + PLC)':m==='dac-no-plc-k5'?'DAC không PLC':'ACIL',ms(m,'average_accuracy'),ms(m,'last_accuracy')]),.90,2.65,8.25,2.32,{fontSize:19,colW:[3.15,2.55,2.55],highlight:[2]});
 headline(sl,'+'+fv(D.plc_gain.last_accuracy.mean)+' pp',9.45,2.92,3.0,.80,36,P.green);
 small(sl,'PLC so với DAC−PLC\\nA_K tăng ở cả 3 seed',9.45,3.92,3.0,.86,{fontSize:19});
 small(sl,'ΔA_K DS-AL−ACIL: +0,31 / +0,34 / +0,56 pp; mean +0,40 pp',.98,5.28,11.4,.38,{fontSize:20,bold:true});
 small(sl,'PLC: +0,63 / +0,42 / +0,36 pp. DAC−ACIL: −0,32 / −0,08 / +0,20 pp.',.98,5.79,11.4,.33,{fontSize:18});break;`);
replaceCase('phase_curves',`
 chart(sl,pptx.ChartType.line,core.map(m=>({name:methodLabel[m],labels:['50','60','70','80','90','100'],values:A[m].phase_accuracy.map(x=>x.mean)})),.78,2.55,7.55,3.20,{showCatAxisTitle:true,catAxisTitle:'Số lớp đã gặp',valAxisMinVal:50,valAxisMaxVal:80,valAxisMajorUnit:10,chartColors:[P.blue,P.orange,P.teal],lineDataSymbolSize:8,lineSize:2.5,legendFontSize:15});
 small(sl,'Trục Y 50–80%; error bar ±SD giữa seed, không phải CI',.98,5.86,7.3,.28,{fontSize:15});
 headline(sl,'Pha cuối: 100 lớp',8.85,2.62,3.7,.45,23);
 table(sl,['Biến thể','A_K ± SD (%)'],core.map(m=>[methodLabel[m],ms(m,'last_accuracy')]),8.75,3.22,3.83,1.60,{fontSize:16.5,colW:[1.82,2.01],highlight:[2]});
 small(sl,'Mean ΔDS-AL−ACIL, pha cuối',8.85,4.98,3.7,.3,{fontSize:15});
 text(sl,'Lớp mới: +'+fv(D.dsal_minus_acil.novel_accuracy.mean)+' pp\\nLớp base: '+fv(D.dsal_minus_acil.base_accuracy.mean)+' pp',8.85,5.37,3.7,.68,{fontSize:19,bold:true});break;`);
replaceCase('evidence_gap',`
 headline(sl,'Dữ liệu hỗ trợ',.95,2.5,5.3,.5,26,P.teal);
 headline(sl,'Giới hạn còn lại',7.0,2.5,5.4,.5,26,P.orange);
 list(sl,['DS-AL hơn ACIL ở 3/3 seed','PLC tăng A_K ở 3/3 seed','SD A_K DS-AL: 0,19 pp giữa seed','E2 giới hạn trong CIFAR-100'],1.0,3.19,5.25,19,.60);
 list(sl,['3 seed nhỏ, chưa có kiểm định','Seed 0 resume CUDA → CPU','Chi tiết projection chưa đủ rõ','K và buffer chỉ có seed 0'],7.05,3.19,5.0,19,.60,P.orange);
 small(sl,'Nhất quán dấu chưa xác lập ý nghĩa thống kê hoặc nguyên nhân gap.',1.0,5.79,11.4,.36,{fontSize:18});break;`);
replaceCase('conclusion',`
 const items=[[fv(mn('dsal-k5','last_accuracy'))+'%','A_K mean của DS-AL K=5','SD mẫu ±'+fv(A['dsal-k5'].last_accuracy.sd)+' pp'],['+'+fv(D.dsal_minus_acil.last_accuracy.mean)+' pp','DS-AL so với ACIL','Cải thiện ở 3/3 seed'],['+'+fv(D.plc_gain.last_accuracy.mean)+' pp','PLC so với DAC không PLC','Cải thiện ở 3/3 seed']];
 items.forEach((v,i)=>{let x=.95+i*4.05;headline(sl,v[0],x,2.75,3.8,1.0,42,P.cyan);small(sl,v[2],x,3.78,3.75,.40,{fontSize:18,color:'C6D9E4'});text(sl,v[1],x,4.36,3.6,.85,{fontSize:23});});
 text(sl,'CIFAR-100 B50, K=5, ba seed. Chưa có kết luận ý nghĩa thống kê.\\nKhảo sát K/buffer vẫn seed 0; chưa tái hiện ImageNet.',.98,5.43,11.4,.70,{fontSize:21,color:'C8D9E6'});break;`);
replaceCase('provenance_detail',`
 table(sl,['Phương pháp','Seed 0','Seed 1','Seed 2'],core.map(m=>[methodLabel[m],...seeds.map(seed=>{const r=vr(m,seed).summary;return 'Ā '+fv(r.average_accuracy,4)+'\\nA_K '+fv(r.last_accuracy,4);})]),.85,2.48,11.6,3.00,{fontSize:18,colW:[2.6,3,3,3],highlight:[2]});
 small(sl,'Hai seed bổ sung: 6,23 giờ compute; peak RSS lấy mẫu 1,58 GiB (10 s/lần).',.98,5.77,11.4,.34,{fontSize:17});break;`);
replaceCase('readiness',`
 const items=[['Main head','Bằng joint ridge trên fixed features','Bảo đảm đại số, với các điều kiện đã nêu'],['Số pha K','A_K gần ổn định trong benchmark seed 0','Quan sát accuracy, không là đẳng thức trọng số'],['DAC / PLC','PLC tăng mean A_K +0,47 pp, ở 3/3 seed','CIFAR-100 K5, chưa kết luận ý nghĩa thống kê']];
 items.forEach((v,i)=>{let y=2.58+i*1.13;headline(sl,v[0],.95,y,2.6,.55,25,i===0?P.cyan:'EAB780');text(sl,v[1],3.7,y,8.7,.48,{fontSize:23,bold:true});small(sl,v[2],3.72,y+.55,8.7,.42,{fontSize:19,color:'B8CDD9'});if(i<2)line(sl,.95,y+.99,12.35,y+.99,'294155',.7);});break;`);

await fs.writeFile(path.join(BUILD,'generated-builder.mjs'),code,'utf8');
await import(pathToFileURL(path.join(BUILD,'generated-builder.mjs')).href+'?t='+Date.now());
console.log('Generated updated native objects. Splice and error-bar workbook patch follow.');
