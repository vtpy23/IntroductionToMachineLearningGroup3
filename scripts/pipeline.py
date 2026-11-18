"""Unattended resumable pipeline with stage status and separate log files."""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

from src.utils.reproducibility import write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/cifar100_core.json")
    parser.add_argument("--tracking", choices=["offline", "online", "disabled"], default="offline")
    parser.add_argument("--compute", choices=["auto", "cpu", "cuda"], default="auto")
    args = parser.parse_args()
    os.environ["PYTHONUTF8"] = "1"
    os.environ["PYTHONIOENCODING"] = "utf-8"
    directory = Path("outputs/pipeline")
    directory.mkdir(parents=True, exist_ok=True)
    stages = [
        ("tests", ["-m", "pytest", "-q"]),
        ("smoke", ["-m", "scripts.run", "--config", "configs/cifar100_smoke.json", "--stage", "suite", "--tracking", args.tracking]),
        ("mechanism-tests", ["-m", "scripts.empirics", "--tracking", args.tracking]),
        ("initial-summary", ["-m", "scripts.summarize"]),
        ("core-backbone-features", ["-m", "scripts.run", "--config", args.config, "--stage", "prepare", "--tracking", args.tracking]),
        ("core-suite", ["-m", "scripts.run", "--config", args.config, "--stage", "analytic", "--tracking", args.tracking]),
        ("summary", ["-m", "scripts.summarize"]),
        ("reports", ["-m", "scripts.refresh_reports", "--group-id", "03"]),
    ]
    status = {"started": time.time(), "config": args.config, "tracking": args.tracking, "stages": []}
    cpu_python = Path(".venv-cpu/Scripts/python.exe")
    prefer_cpu = args.compute == "cpu"
    if args.compute == "auto" and os.name == "nt" and cpu_python.exists():
        import ctypes
        class MemoryStatus(ctypes.Structure):
            _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong),
                        *[(key, ctypes.c_ulonglong) for key in ["total_phys", "avail_phys", "total_page", "avail_page", "total_virtual", "avail_virtual", "avail_extended"]]]
        memory = MemoryStatus()
        memory.length = ctypes.sizeof(memory)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory))
        # CUDA DLLs plus training require substantial Windows commit headroom.
        prefer_cpu = memory.avail_page < 10 * 2**30
        status["available_commit_bytes_at_start"] = memory.avail_page
    status["compute"] = "cpu" if prefer_cpu else args.compute
    for name, command in stages:
        status["current_stage"] = name
        write_json(directory / "status.json", status)
        with (directory / f"{name}.log").open("a", encoding="utf-8") as log:
            cpu_python = Path(".venv-cpu/Scripts/python.exe")
            use_cpu = cpu_python.exists() and (name != "core-backbone-features" or prefer_cpu)
            executable = str(cpu_python.resolve()) if use_cpu else sys.executable
            result = subprocess.run([executable, *command], stdout=log, stderr=subprocess.STDOUT)
        if result.returncode and name == "core-backbone-features":
            failed_text = (directory / f"{name}.log").read_text(encoding="utf-8", errors="replace").lower()
            memory_failure = any(message in failed_text for message in
                                 ["not enough memory", "out of memory", "defaultcpuallocator", "paging file is too small", "cublas_status_not_initialized"])
            cpu_python = Path(".venv-cpu/Scripts/python.exe")
            if memory_failure and cpu_python.exists() and not Path(".stop-project").exists():
                status["cpu_fallback"] = {"stage": name, "reason": "GPU process exceeded available memory",
                                          "checkpoint": "resumed from last completed epoch"}
                write_json(directory / "status.json", status)
                with (directory / f"{name}-cpu-fallback.log").open("a", encoding="utf-8") as log:
                    result = subprocess.run([str(cpu_python.resolve()), *command], stdout=log, stderr=subprocess.STDOUT)
        status["stages"].append({"name": name, "exit_code": result.returncode, "finished": time.time()})
        if result.returncode:
            status["state"] = "failed"
            write_json(directory / "status.json", status)
            raise SystemExit(result.returncode)
    status["state"] = "completed"
    write_json(directory / "status.json", status)


if __name__ == "__main__":
    main()
