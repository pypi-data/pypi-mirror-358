import threading
import time
import os
import sys
import traceback
from datetime import datetime

# Optional GPU check - we'll try to import pynvml, if fails skip GPU monitoring
try:
    import ctypes
    import platform
    if platform.system() == 'Windows':
        _lib_name = "nvml.dll"
    elif platform.system() == 'Linux':
        _lib_name = "libnvidia-ml.so.1"
    else:
        _lib_name = None
    if _lib_name:
        from ctypes import byref, c_uint, c_ulonglong, c_char_p, c_int
        _nvml = ctypes.cdll.LoadLibrary(_lib_name)

        # Nvml constants & functions:
        NVML_SUCCESS = 0

        class nvmlUtilization_t(ctypes.Structure):
            _fields_ = [("gpu", c_uint), ("memory", c_uint)]

        def nvml_init():
            return _nvml.nvmlInit()

        def nvml_shutdown():
            return _nvml.nvmlShutdown()

        def nvml_device_get_handle_by_index(index, handle_ptr):
            return _nvml.nvmlDeviceGetHandleByIndex(index, handle_ptr)

        def nvml_device_get_utilization_rates(handle, util_ptr):
            return _nvml.nvmlDeviceGetUtilizationRates(handle, util_ptr)

        def nvml_device_get_memory_info(handle, mem_info_ptr):
            return _nvml.nvmlDeviceGetMemoryInfo(handle, mem_info_ptr)

        class nvmlMemory_t(ctypes.Structure):
            _fields_ = [("total", c_ulonglong), ("free", c_ulonglong), ("used", c_ulonglong)]
    else:
        _nvml = None

except Exception:
    _nvml = None


def get_cpu_usage_percent():
    """Return CPU usage percent over 0.1 seconds"""
    try:
        if sys.platform == "win32":
            import psutil
            return psutil.cpu_percent(interval=0.1)
        else:
            # Linux/Mac - approximate by reading /proc/stat or use os.times
            import subprocess
            output = subprocess.check_output("top -bn2 | grep 'Cpu(s)'", shell=True).decode()
            lines = output.strip().split("\n")
            if len(lines) < 2:
                return None
            # Parse 2nd sample line
            line = lines[1]
            # format: Cpu(s):  3.5%us,  1.1%sy,  0.0%ni, 94.9%id,  0.5%wa,  0.0%hi,  0.0%si,  0.0%st
            parts = line.split(',')
            for part in parts:
                if 'id' in part:
                    idle = float(part.strip().split('%')[0])
                    usage = 100.0 - idle
                    return round(usage, 2)
            return None
    except Exception:
        return None


def get_ram_usage_mb():
    """Return RAM used in MB"""
    try:
        if sys.platform == "win32":
            import psutil
            mem = psutil.virtual_memory()
            used_mb = (mem.total - mem.available) / (1024 * 1024)
            return round(used_mb, 2)
        else:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            lines = meminfo.split('\n')
            mem_total_kb = None
            mem_free_kb = None
            buffers_kb = None
            cached_kb = None
            for line in lines:
                if line.startswith("MemTotal:"):
                    mem_total_kb = int(line.split()[1])
                elif line.startswith("MemFree:"):
                    mem_free_kb = int(line.split()[1])
                elif line.startswith("Buffers:"):
                    buffers_kb = int(line.split()[1])
                elif line.startswith("Cached:"):
                    cached_kb = int(line.split()[1])
            if None in (mem_total_kb, mem_free_kb, buffers_kb, cached_kb):
                return None
            used_kb = mem_total_kb - (mem_free_kb + buffers_kb + cached_kb)
            used_mb = used_kb / 1024
            return round(used_mb, 2)
    except Exception:
        return None


class ResourceMonitor:
    """
    ResourceMonitor: Monitors CPU, RAM and optionally GPU usage with configurable thresholds,
    periodic checks, logging, and customizable alerts.

    Parameters:
    ----------
    cpu_threshold : float (0-100)
        CPU usage percentage above which alert triggers (default 90.0)
    ram_threshold_mb : float
        RAM used in MB above which alert triggers (default 4000.0 MB)
    gpu_threshold : float (0-100)
        GPU usage percentage above which alert triggers (default 90.0)
    monitor_interval_sec : float
        How often to check resource usage in seconds (default 5.0)
    log_to_console : bool
        If True, print logs to console (default True)
    log_to_file : bool
        If True, save logs to file (default False)
    log_file_path : str
        File path for logs (default "resource_monitor.log")
    max_log_lines : int
        Maximum lines to keep in log file before rotation (default 10000)
    alert_callback : callable
        Function called on alert with signature func(resource:str, usage:float)
    stop_on_alert : bool
        If True, stops monitoring on first alert (default False)
    n_jobs : int
        Number of threads to use for parallel monitoring (default 1)

    Usage:
    ------
    monitor = ResourceMonitor(cpu_threshold=80, ram_threshold_mb=3000,
                              monitor_interval_sec=2, log_to_console=True,
                              stop_on_alert=True)
    monitor.start()
    # ... do work ...
    monitor.stop()
    """

    def __init__(self,
                 cpu_threshold=90.0,
                 ram_threshold_mb=4000.0,
                 gpu_threshold=90.0,
                 monitor_interval_sec=5.0,
                 log_to_console=True,
                 log_to_file=False,
                 log_file_path="resource_monitor.log",
                 max_log_lines=10000,
                 alert_callback=None,
                 stop_on_alert=False,
                 n_jobs=1):
        self.cpu_threshold = cpu_threshold
        self.ram_threshold_mb = ram_threshold_mb
        self.gpu_threshold = gpu_threshold
        self.monitor_interval_sec = monitor_interval_sec
        self.log_to_console = log_to_console
        self.log_to_file = log_to_file
        self.log_file_path = log_file_path
        self.max_log_lines = max_log_lines
        self.alert_callback = alert_callback
        self.stop_on_alert = stop_on_alert
        self.n_jobs = max(1, n_jobs)

        self._stop_event = threading.Event()
        self._thread = None
        self._log_lines = []

        # GPU related
        self.gpu_available = False
        self._gpu_handle = None
        self._init_gpu()

    def _init_gpu(self):
        if _nvml:
            try:
                ret = nvml_init()
                if ret == NVML_SUCCESS:
                    # get handle for GPU 0 (first GPU)
                    handle = ctypes.c_void_p()
                    if nvml_device_get_handle_by_index(0, byref(handle)) == NVML_SUCCESS:
                        self.gpu_available = True
                        self._gpu_handle = handle
                    else:
                        self.gpu_available = False
                else:
                    self.gpu_available = False
            except Exception:
                self.gpu_available = False
        else:
            self.gpu_available = False

    def _log(self, msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_msg = f"[{timestamp}] {msg}"
        self._log_lines.append(full_msg)
        if self.log_to_console:
            print(full_msg)
        if self.log_to_file:
            self._write_log_file(full_msg)

        # Rotate log lines if too long
        if len(self._log_lines) > self.max_log_lines:
            self._log_lines = self._log_lines[-self.max_log_lines:]

    def _write_log_file(self, line):
        try:
            with open(self.log_file_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass

    def _check_alerts(self, cpu_usage, ram_usage, gpu_usage):
        alert_triggered = False
        if cpu_usage is not None and cpu_usage > self.cpu_threshold:
            self._log(f"ALERT: CPU usage high: {cpu_usage}% > threshold {self.cpu_threshold}%")
            if self.alert_callback:
                self.alert_callback("CPU", cpu_usage)
            alert_triggered = True

        if ram_usage is not None and ram_usage > self.ram_threshold_mb:
            self._log(f"ALERT: RAM usage high: {ram_usage}MB > threshold {self.ram_threshold_mb}MB")
            if self.alert_callback:
                self.alert_callback("RAM", ram_usage)
            alert_triggered = True

        if self.gpu_available and gpu_usage is not None and gpu_usage > self.gpu_threshold:
            self._log(f"ALERT: GPU usage high: {gpu_usage}% > threshold {self.gpu_threshold}%")
            if self.alert_callback:
                self.alert_callback("GPU", gpu_usage)
            alert_triggered = True

        if alert_triggered and self.stop_on_alert:
            self._log("Stopping monitor due to alert.")
            self.stop()

    def _get_gpu_usage(self):
        if not self.gpu_available or not self._gpu_handle:
            return None
        try:
            util = nvmlUtilization_t()
            if nvml_device_get_utilization_rates(self._gpu_handle, byref(util)) == NVML_SUCCESS:
                return util.gpu
        except Exception:
            return None
        return None

    def _snapshot(self):
        cpu = get_cpu_usage_percent()
        ram = get_ram_usage_mb()
        gpu = self._get_gpu_usage()
        return cpu, ram, gpu

    def _monitor_loop(self):
        self._log("ResourceMonitor started.")
        while not self._stop_event.is_set():
            cpu, ram, gpu = self._snapshot()
            self._log(f"Snapshot - CPU: {cpu}%, RAM: {ram}MB, GPU: {gpu}%")
            self._check_alerts(cpu, ram, gpu)
            time.sleep(self.monitor_interval_sec)
        self._log("ResourceMonitor stopped.")

    def start(self):
        """Start monitoring resources in a background thread."""
        if self._thread and self._thread.is_alive():
            self._log("Monitor already running.")
            return
        self._stop_event.clear()
        if self.n_jobs == 1:
            self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._thread.start()
        else:
            # For multiple threads monitoring (e.g. for different resources)
            self._log(f"Starting {self.n_jobs} monitor threads.")
            self._threads = []
            for i in range(self.n_jobs):
                t = threading.Thread(target=self._monitor_loop, daemon=True)
                self._threads.append(t)
                t.start()

    def stop(self):
        """Stop monitoring."""
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        if hasattr(self, "_threads"):
            for t in self._threads:
                t.join()

    def get_snapshot(self):
        """
        Return current usage snapshot as a dict:
            {'cpu': float, 'ram': float, 'gpu': float or None}
        """
        cpu, ram, gpu = self._snapshot()
        return {"cpu": cpu, "ram": ram, "gpu": gpu}

    def get_report(self):
        """Return a summary report string with last logged lines."""
        return "\n".join(self._log_lines[-20:])


if __name__ == "__main__":
    # Demo usage
    def alert_fn(resource, usage):
        print(f"*** ALERT callback: {resource} usage high: {usage}")

    monitor = ResourceMonitor(cpu_threshold=10,
                              ram_threshold_mb=500,
                              monitor_interval_sec=2,
                              alert_callback=alert_fn,
                              stop_on_alert=False,
                              log_to_console=True,
                              n_jobs=1)

    monitor.start()
    time.sleep(10)
    print("Snapshot:", monitor.get_snapshot())
    monitor.stop()
    print("Final Report:")
    print(monitor.get_report())
