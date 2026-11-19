"""Versioned presentation copy only; reads frozen evidence, performs no experiments."""
import copy
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
original=json.loads((HERE/'slide_content.json').read_text(encoding='utf-8'))
data=copy.deepcopy(original)
evidence=json.loads((HERE/'assets/verified_evidence.json').read_text(encoding='utf-8'))
runs={r['name']:r for r in evidence['experiments']}
slides={s['number']:s for s in data['slides']}
members=['Lâm Hoàng Vũ – 23122056','Nguyễn Bá Nam – 23122043','Chung Tín Đạt – 23122024']
data['authors']=members
data['version']='v2'
short={
 '1':'[1] H. Zhuang et al., “DS-AL,” Proc. AAAI, vol. 38, no. 15, pp. 17237–17244, 2024.',
 '2':'[2] H. Zhuang et al., “Supplementary Material for DS-AL,” Sec. A–C, 2024.',
 '3':'[3] H. Zhuang et al., “ACIL,” Adv. Neural Inf. Process. Syst., vol. 35, pp. 11602–11614, 2022.',
 '4':'[4] Z. Li and D. Hoiem, “Learning without Forgetting,” IEEE TPAMI, vol. 40, pp. 2935–2947, 2018.',
 '5':'[5] S.-A. Rebuffi et al., “iCaRL,” Proc. CVPR, pp. 2001–2010, 2017.',
 '6':'[6] K. He et al., “Deep Residual Learning for Image Recognition,” Proc. CVPR, pp. 770–778, 2016.'
}
for key,value in short.items():data['references'][key]['short']=value
slides[1]['notes']=slides[1]['notes'].replace('Nhóm Vũ, Nam, Đạt','Nhóm gồm '+', '.join(members))
slides[22]['message']='E1 đối sánh chính, E2 ablation chuyển dataset, E3 khảo sát buffer'
slides[22]['notes']='Phạm vi thực nghiệm gồm E1 đối sánh ACIL với DS-AL trên CIFAR-100 B50, tương ứng phần CIFAR-100 ResNet-32 của Table 1. E2 kiểm tra cơ chế DAC/PLC bằng cách chuyển thí nghiệm ablation từ ImageNet-Full với C=1,4 trong Table 2 sang CIFAR-100 với C=0,6. Vì dataset, backbone và hệ số C thay đổi, E2 không phải tái hiện nguyên Table 2. Chưa có bằng chứng giảng viên đã chấp nhận phạm vi chuyển này. Kết quả E2 chỉ diễn giải trong protocol CIFAR đã nêu. E3 do nhóm thiết kế để khảo sát accuracy và thời gian fit khi thay chiều buffer trên cùng feature cache. Benchmark nhóm hiện chỉ có seed 0; không dùng các seed tổng hợp để thay thế benchmark nhiều seed.'
slides[25].update(title='Điều kiện đối sánh giữa các biến thể',message='Dùng chung biểu diễn và protocol, thay đổi thành phần đang kiểm tra',refs=['1','2'])
slides[25]['notes']='Các phép đối sánh của nhóm dùng cùng CIFAR-100, checkpoint ResNet-32, class order và seed 0. Vì vậy mỗi cặp có thể tập trung vào thành phần đang kiểm tra. E1 so ACIL với DS-AL đầy đủ. E2 so ACIL, DAC không PLC và DAC có PLC, nhằm tách đóng góp của nhánh bù và bước làm sạch nhãn trong protocol CIFAR. Khảo sát số pha thay K=5/25/50, còn khảo sát buffer thay m=512/1024/2048/8192 với K=5. Gamma, C, activation và solver của khảo sát buffer giữ cố định. Khi thay m, projection dùng cùng seed nhưng các ma trận không lồng nhau; vì thế quan sát cũng chịu ảnh hưởng của một realization projection. Đây là thiết kế ghép cặp trong một seed, chưa là ước lượng biến thiên giữa các seed.'
slides[29]['message']='E2: CIFAR-100, seed 0; chuyển từ ImageNet-Full, không tái hiện nguyên Table 2'
slides[29]['notes']+=' E2 là bản chuyển dataset từ ImageNet-Full/C=1,4 của paper sang CIFAR-100/C=0,6; không suy ra mức tác dụng PLC trên ImageNet. Không có thông tin xác nhận giảng viên đã chấp nhận phạm vi này.'
slides[30]['message']='CIFAR-100, seed 0; màu, kiểu nét và marker phân biệt ba biến thể'
slides[30]['notes']+=' Biểu đồ v2 dùng trục accuracy 50–80% để phân biệt tiến trình, được ghi rõ trên slide. Các đường có màu, marker và kiểu nét khác nhau. Bảng pha cuối giữ nguyên giá trị chính xác đã đo. Phóng trục không thêm quan sát và không xác lập ý nghĩa thống kê.'
buffer_small=runs['buffer-512']['summary'];buffer_large=runs['dsal-k5']['summary']
gain=buffer_large['last_accuracy']-buffer_small['last_accuracy'];ratio=buffer_large['fit_seconds']/buffer_small['fit_seconds']
slides[33]['message']=f'Seed 0, 512 → 8192: +{gain:.2f} pp accuracy, thời gian fit ×{ratio:.1f}'.replace('.',',')
slides[33]['notes']+=' Hai biểu đồ dùng cùng thứ tự chiều buffer và hai đơn vị riêng: accuracy (%) và thời gian fit (s). Hai trục cột đều bắt đầu từ 0. Bảng giữ giá trị fit đến ba chữ số thập phân và accuracy đến hai chữ số. Tỷ số thời gian và chênh lệch pp được tính từ số đo chưa làm tròn; đây là thống kê mô tả một seed trên CPU này, không phải khẳng định độ phức tạp thực nghiệm trên mọi máy.'
slides[37]['title']='Đối chiếu mã tác giả trên đầu vào tổng hợp'
slides[37]['message']='Cùng dữ liệu, nhãn và projection; thay batch của mã tham chiếu từ 20 xuống 4'
slides[37]['notes']+=' Các sai khác trên slide là max absolute difference so với triển khai của nhóm, không phải accuracy. Chỉ thay batch size trong đường chạy mã tác giả; triển khai nhóm giữ residual sau nghiệm main cuối pha. Phạm vi là đầu vào tổng hợp nhỏ tại official checkout 0afd6bf87622e808ce7f730f8556e78229b9e758. Kết quả cho thấy hai đường chạy không tương đương với minibatch nhỏ trong thiết lập này, không chứng minh mã tác giả sai nói chung và không định lượng nguyên nhân gap trên CIFAR.'
slides[40].update(title='Phạm vi của các kết luận',message='Phân biệt tương đương nghiệm, ổn định accuracy và tác dụng thực nghiệm',refs=['1','2'],runs=['dac-no-plc-k5','dsal-k5','phase-dependence'])
slides[40]['notes']='Ba loại phát biểu cần được phân biệt. Thứ nhất, Theorem 1 bảo đảm main head bằng nghiệm joint ridge khi feature, projection, activation và gamma cố định, padding đúng và dữ liệu được cập nhật đầy đủ. Thứ hai, accuracy pha cuối của DS-AL gần nhau khi đổi K trong benchmark seed 0 là quan sát thực nghiệm, không suy ra trọng số toàn DS-AL bất biến chính xác. Thứ ba, lợi ích DAC/PLC phụ thuộc protocol; trong CIFAR seed 0, PLC tăng 0,63 pp so DAC không PLC, còn DAC đơn lẻ thấp hơn ACIL. Các seed của bài kiểm tra cơ chế là dữ liệu tổng hợp, không phải các lần lặp CIFAR. Do đó không dùng bảo đảm main ridge để khẳng định không quên ở cấp CNN, tính bất biến của compensation hoặc ý nghĩa thống kê của một chênh lệch accuracy.'
for s in data['slides']:
    s['notes']=s['notes'].replace('Chuyển sang các phương pháp tiền nhiệm.','').replace('Chuyển sang ràng buộc exemplar-free.','')
    assert len(s['notes'].split())<=500,s['number']
(HERE/'slide_content_v2.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
md=['# Nội dung và speaker notes v2','']
for s in data['slides']:
    md += [f"## {s['number']:02d}. {s['title']}",s['message'],'',s['notes'],'']
    md += [data['references'][r]['full']+' '+data['references'][r]['url'] for r in s['refs']]
    md += [f"{name}: {runs[name]['verification']['url']}" for name in s['runs']]
    md += ['']
(HERE/'SLIDE_CONTENT_v2.md').write_text('\n'.join(md).rstrip()+'\n',encoding='utf-8')
print('Prepared v2: 40 slides, frozen seed-0 evidence, no new experiment.')
