// Executed inside the existing PptxGenJS wrapper, where code/replaceCase exist.
code=code.replace('DS-AL — Milestone 2 + Lab 1 — Three Seeds','DS-AL — Milestone 2 + Lab 1 — Strict Review');
code=code.replace("const A=V.aggregates,D=V.paired;",`const A=V.aggregates,D=V.paired;
const SENS=JSON.parse(await fs.readFile(path.join(HERE,'../../experiments/strict-review/20261119/results.json'),'utf8'));
`);
code=code.replace("pptx.subject='Verified three-seed CIFAR-100 reproduction and independent reading';","pptx.subject='Strict academic review; preserved three-seed benchmarks and measured posthoc sensitivity';");
code=code.replace('function runFooter(sl,s){',`function runFooter(sl,s){
 if(s.analysisRuns){
  small(sl,'W&B',.75,6.25,.65,.28,{fontSize:13,bold:true});
  SENS.rows.forEach((row,i)=>{const u=row.tracking.wandb_url;text(sl,'Sensitivity C · seed '+row.seed,1.6+i*3.55,6.23,3.25,.32,{fontSize:14,color:P.teal,hyperlink:{url:u,tooltip:u},role:'run-link'});});return;
 }
`);
code=code.replace('if(s.runs.length||s.seedMethods?.length)runFooter(sl,s);','if(s.runs.length||s.seedMethods?.length||s.analysisRuns)runFooter(sl,s);');
code=code.replace("const provenance=[legacyProvenance,...seedSources(s).map", "const analysisProvenance=(s.analysisRuns||s.analysisSources)?SENS.rows.map(r=>`Sensitivity C seed ${r.seed}: ${r.tracking.wandb_url}\\nAnalysis/config: experiments/strict-review/20261119/saved-C-sensitivity-seed${r.seed}/`).join('\\n'):'';\n const provenance=[legacyProvenance,analysisProvenance,...seedSources(s).map");
replaceCase('related',`
 table(sl,['Tiền nhiệm','Ý tưởng và ưu điểm','Hạn chế và hệ quả'],[
 ['LwF','Distillation giữ hành vi cũ','Dữ liệu mới lệch phân phối: lớp cũ có thể giảm'],
 ['iCaRL','Replay / prototype hỗ trợ biểu diễn','Lưu exemplar: cần ngân sách ảnh và quyền giữ dữ liệu'],
 ['ACIL','Ridge khớp joint trên fixed features','Backbone base cố định: lớp mới có thể thiếu biểu diễn']
 ],.85,2.48,11.6,2.95,{fontSize:18,colW:[1.55,4.45,5.6]});
 statement(sl,'DS-AL thêm một embedding và head residual để tăng khả năng khớp.',.9,5.72,11.5,.48);break;`);
replaceCase('notation',`
 equation(sl,'D_k = {(x_i, y_i)} ; y_i ∈ L_k',.9,2.50,7.1,.58,26);
 equation(sl,'L_i ∩ L_j = ∅  (i ≠ j)',.9,3.25,7.1,.58,26);
 equation(sl,'C_k = L_0 ∪ … ∪ L_k ; c_k = |C_k|',.9,4.00,7.15,.62,25);
 text(sl,'hₖ: ảnh → tất cả lớp trong Cₖ\\nSₖ = update(Sₖ₋₁, Dₖ)',.95,4.85,6.7,.85,{fontSize:23,bold:true});
 table(sl,['Đối tượng','Kích thước'],[['f(x), B','d ; d × m'],['X_M,k ; X_C,k','nₖ × m'],['Y_k ; W_k','nₖ × cₖ ; m × cₖ'],['G_k ; R_k','m × m']],8.35,2.58,4.0,2.95,{fontSize:18,colW:[2.05,1.95]});
 small(sl,'Không task ID khi dự đoán. Pha k chỉ đọc D_k và trạng thái cũ.',.95,5.96,11.4,.32,{fontSize:19,color:P.teal});break;`);
replaceCase('residual',`
 node(sl,'Main cuối pha',.95,2.67,3.3,.72,P.teal);
 node(sl,'Residual Eₖ',5,2.67,3.0,.72,P.blue);
 node(sl,'PLC rồi fit W_C',8.8,2.67,3.5,.72,P.orange);
 line(sl,4.3,3.03,4.85,3.03,P.teal,2,true);line(sl,8.05,3.03,8.65,3.03,P.orange,2,true);
 equation(sl,'E_k = Y_k − X_M,k W_M,k',1.0,3.87,11.4,.70,31);
 equation(sl,'XᵀE_joint = γW_M,k',1.0,4.88,6.2,.65,29);
 text(sl,'X là embedding tích lũy\\nγ > 0: chưa trực giao chính xác',7.1,4.82,5.1,.83,{fontSize:21});
 small(sl,'DAC học residual với activation khác; không có bảo đảm tăng accuracy.',1.0,5.96,11.3,.34,{fontSize:18,color:P.teal});break;`);
replaceCase('memory',`
 headline(sl,'1 GiB',.95,2.60,5.0,1.15,65,P.teal);
 equation(sl,'2 × 8192² × 8 byte',1.0,3.75,5.3,.6,26);
 small(sl,'Hai ma trận FP64 của DS-AL\\nACIL: một ma trận = 512 MiB',1.0,4.52,5.45,.78,{fontSize:21});
 table(sl,['m','Hai ma trận'],[[512,'4 MiB'],[1024,'16 MiB'],[2048,'64 MiB'],[8192,'1024 MiB']],7.0,2.55,5.3,2.85,{fontSize:20,colW:[2.0,3.3]});
 small(sl,'LwF / iCaRL còn cần SGD của CNN; replay thêm M ảnh. Không có runtime chung.',.98,5.72,11.4,.34,{fontSize:18});
 small(sl,'Chỉ storage lý thuyết: chưa gồm head O(mc), B O(dm), CNN và workspace.',.98,6.13,11.4,.30,{fontSize:16});break;`);
replaceCase('scope',`
 const items=[['E1','Table 1: ACIL / DS-AL','K5: ba seed; K25/50: seed 0'],['E4','Figure 4: sensitivity Tanh / C','Ba seed, final heads; không đủ mọi activation'],['E2','Ablation chuyển sang CIFAR','Không tái hiện ImageNet-Full Table 2'],['E3','Phân tích buffer nhóm thiết kế','Seed 0, accuracy / thời gian fit']];
 items.forEach((it,i)=>{let y=2.52+i*.83;headline(sl,it[0],.95,y,1.0,.42,25,i===1?P.teal:P.blue);text(sl,it[1],2.12,y,5.0,.42,{fontSize:22,bold:true});small(sl,it[2],7.35,y,5.0,.47,{fontSize:18});if(i<3)line(sl,.95,y+.64,12.25,y+.64,P.line,.7);});
 small(sl,'Core được biện minh theo nguồn lực; chưa nhận là exact reproduction hoặc Full scope.',.98,6.08,11.5,.30,{fontSize:16.5,color:P.teal});break;`);
replaceCase('tests',`
 headline(sl,'21 / 21',.95,2.5,4.3,1.1,62,P.teal);
 small(sl,'test đại số, protocol,\\nresume và kết quả thống kê',1,3.78,4.2,.90,{fontSize:21});
 list(sl,['C-RLS / padding / residual / PLC','Hai solver, nhiều pha và chunk','Seed, class order, accuracy và SD','Resume giữ quỹ đạo hợp lệ','24 run: đọc công khai toàn bộ dữ liệu'],5.65,2.49,6.4,19,.66);
 small(sl,'Đối chiếu kiến trúc cùng weights: float64; không chứng minh cùng training trajectory.',1.0,6.08,11.3,.32,{fontSize:17});break;`);
replaceCase('trace',`
 table(sl,['Đối sánh','Điều kiện ghép cặp','Số seed'],[
 ['ACIL / DAC / DS-AL','Chung checkpoint, cache, lớp và projection','3'],
 ['Sensitivity C','Giữ nguyên final heads; chỉ thay C lúc suy luận','3'],
 ['K: 5 / 25 / 50','Chung backbone, cache và projection; đổi pha','1 (seed 0)'],
 ['Buffer: 512…8192','Giữ cache / K5 / solver; projection không lồng nhau','1 (seed 0)']
 ],.9,2.63,11.5,2.95,{fontSize:19,colW:[3.1,6.65,1.75]});
 small(sl,'C=0,6 vẫn là benchmark đã chọn trước; sweep hậu nghiệm không dùng để thay số tốt nhất.',.98,5.87,11.4,.34,{fontSize:18,color:P.teal});break;`);
replaceCase('gap',`
 const refs={'acil-k5':[66.30,57.78],'dsal-k5':[66.39,58.26]};
 table(sl,['Phương pháp','Δ Ā (pp)','Δ Ā tương đối','Δ A_K (pp)','Δ A_K tương đối'],['acil-k5','dsal-k5'].map(m=>{const ref=refs[m],a=mn(m,'average_accuracy'),k=mn(m,'last_accuracy');return [methodLabel[m],fv(a-ref[0],3),fv(100*(a-ref[0])/ref[0],3)+'%',fv(k-ref[1],3),fv(100*(k-ref[1])/ref[1],3)+'%'];}),.85,2.60,11.6,1.95,{fontSize:21,colW:[2.0,2.0,2.8,2.0,2.8]});
 headline(sl,'Gain A_K: paper +0,48 pp; nhóm +0,40 pp',.98,4.96,11.4,.52,27,P.teal);
 small(sl,'Cùng chiều, gần về độ lớn; chưa chứng minh nguyên nhân accuracy tuyệt đối thấp hơn.',.98,5.70,11.4,.43,{fontSize:19});break;`);
replaceCase('phase_sweep',`
 table(sl,['K','Paper Ā','Nhóm Ā','Paper A_K','Nhóm A_K','Δ A_K (pp)'],[5,25,50].map((k,i)=>{const p=[[66.39,58.26],[66.20,58.32],[66.33,58.37]][i],r=sum('dsal-k'+k);return [k,fmt(p[0]),fmt(r.average_accuracy),fmt(p[1]),fmt(r.last_accuracy),fv(r.last_accuracy-p[1])];}),.85,2.70,11.6,2.48,{fontSize:20,colW:[.70,2.0,2.0,2.05,2.05,2.8]});
 small(sl,'A_K nhóm dao động 0,04 pp. Mean paper so với một seed nhóm: chưa có SD cho K25/50.',.98,5.56,11.4,.45,{fontSize:19,color:P.teal});break;`);
replaceCase('evidence_gap',`
 table(sl,['Yếu tố','Nguồn đối chiếu','Nhóm / phạm vi xác minh'],[
 ['Base training','Supplement C: 160 epoch, SGD, milestones','Khớp cấu hình đã nêu; khác README hiện tại'],
 ['Projection','Checkout: Uniform(−0,125; +0,125)','Normal(0,1): khác biệt đã xác minh'],
 ['Class order / init','Checkout: Python Random / Kaiming fan_in','NumPy RandomState / fan_out: khác biệt'],
 ['Residual','Algorithm 1: cuối pha; code: minibatch','Nhóm theo Algorithm 1; tác động CIFAR chưa đo'],
 ['Solver / backend','Paper RLS; workstation RTX3090','Stats FP64; seed 0 đổi backend khi resume']
 ],.85,2.44,11.65,3.48,{fontSize:17.5,colW:[2.2,4.3,5.15]});
 break;`);
const ratioCase=` case 'ratio_sensitivity':{
 chart(sl,pptx.ChartType.line,[...SENS.rows.map(r=>({name:'Seed '+r.seed,labels:r.ratios.map(x=>x.ratio.toFixed(1)),values:r.ratios.map(x=>x.all_accuracy)})),{name:'Mean ± SD',labels:SENS.aggregate.map(x=>x.ratio.toFixed(1)),values:SENS.aggregate.map(x=>x.all_accuracy.mean)}],.80,2.56,7.6,3.35,{showCatAxisTitle:true,catAxisTitle:'Compensation ratio C',valAxisMinVal:55.8,valAxisMaxVal:57.4,valAxisMajorUnit:.4,valAxisLabelFormatCode:'0.0',chartColors:[P.blue,P.orange,'A3AFBA',P.teal],legendFontSize:13,lineDataSymbolSize:5,lineSize:1.7,catAxisLabelFontSize:13});
 table(sl,['C','A_K mean ± SD'],[0,.6,1].map(c=>{let r=SENS.aggregate.find(x=>x.ratio===c);return [c.toFixed(1),fv(r.all_accuracy.mean)+' ± '+fv(r.all_accuracy.sd)];}),8.85,2.85,3.6,1.75,{fontSize:18,colW:[.7,2.9]});
 text(sl,'Paper: đỉnh quanh 0,6\\nNhóm: đỉnh 0,7–0,8',8.88,4.90,3.65,.75,{fontSize:20,bold:true});
 small(sl,'Phân tích test hậu nghiệm; giữ benchmark C=0,6. Chỉ Tanh, không tái hiện toàn Figure 4.',.98,5.98,11.4,.28,{fontSize:16.5,color:P.teal});break;
 }
`;
code=code.replace(" case 'gain_detail':{",ratioCase+" case 'gain_detail':{");
const groupsCase=` case 'base_novel_analysis':{
 table(sl,['Phương pháp','Base mean ± SD','Novel mean ± SD','A_K mean ± SD'],core.map(m=>[methodLabel[m],ms(m,'base_accuracy'),ms(m,'novel_accuracy'),ms(m,'last_accuracy')]),.85,2.56,11.6,2.22,{fontSize:20,colW:[2.3,3.1,3.1,3.1],highlight:[2]});
 headline(sl,'DAC−ACIL: base −4,43 pp / novel +4,29 pp',.98,5.05,11.4,.45,25,P.orange);
 headline(sl,'PLC−DAC: base +2,29 pp / novel −1,35 pp',.98,5.72,11.4,.45,25,P.teal);break;
 }
`;
code=code.replace(" case 'readiness':{",groupsCase+" case 'readiness':{");
