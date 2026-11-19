"""Disposable resource calibration only; never logs research metrics to W&B."""
import ctypes
import json
import time
from pathlib import Path

def memory():
    class Status(ctypes.Structure):
        _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong)] + [
            (key, ctypes.c_ulonglong) for key in ['total_phys', 'avail_phys', 'total_page',
            'avail_page', 'total_virtual', 'avail_virtual', 'avail_extended']]
    status = Status()
    status.length = ctypes.sizeof(status)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
    return {key: getattr(status, key) for key in ['total_phys', 'avail_phys', 'total_page', 'avail_page']}

def main():
    started = time.perf_counter()
    result = {'scope': 'resource calibration on generated inputs; not a research experiment',
              'before_import': memory()}
    import torch
    import torchvision
    import psutil
    from src.models.resnet import CifarResNet32
    torch.set_num_threads(8)
    result.update(torch=torch.__version__, torchvision=torchvision.__version__,
                  cuda=torch.version.cuda, cuda_available=torch.cuda.is_available(),
                  after_import=memory())
    assert torch.cuda.is_available()
    model = CifarResNet32(50).cuda()
    optimizer = torch.optim.SGD(model.parameters(), lr=.1, momentum=.9, weight_decay=5e-4)
    x = torch.zeros(128, 3, 32, 32, device='cuda')
    y = torch.arange(128, device='cuda') % 50
    torch.nn.functional.cross_entropy(model(x), y).backward()
    optimizer.step()
    torch.cuda.synchronize()
    result.update(after_training_batch=memory(), gpu_name=torch.cuda.get_device_name(0),
                  gpu_total_bytes=torch.cuda.get_device_properties(0).total_memory,
                  gpu_peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                  gpu_peak_reserved_bytes=torch.cuda.max_memory_reserved(),
                  process_peak_rss_bytes=psutil.Process().memory_info().peak_wset,
                  elapsed_seconds=time.perf_counter()-started)
    target = Path('artifacts/multiseed-resource-recovery/gpu-probe.json')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result), flush=True)

if __name__ == '__main__':
    main()
