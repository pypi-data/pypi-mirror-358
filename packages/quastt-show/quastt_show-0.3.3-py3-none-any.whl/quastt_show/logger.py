import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock


class SimpleQLogger:
    """
    Logger & Profiler performant pentru quastt_show.
    - Profilează funcții (decorator) cu timp de execuție precis (perf_counter)
    - Loghează mesaje (INFO, DEBUG, ERROR) cu timestamp
    - Suportă execuție paralelă a mai multor funcții profile (n_jobs)
    - Raport complet erori, timpi, mesaje
    """

    LEVELS = {"DEBUG": 10, "INFO": 20, "ERROR": 30}

    def __init__(
        self,
        logfile="simpleqlogger.log",
        n_jobs=1,
        log_level="INFO",
        log_to_console=True,
        max_log_memory=1000,
    ):
        self.logfile = logfile
        self.n_jobs = n_jobs if n_jobs != 0 else 1
        self.log_level = log_level.upper() if log_level.upper() in self.LEVELS else "INFO"
        self.log_to_console = log_to_console
        self.max_log_memory = max_log_memory  # nr max mesaje in memorie

        self._lock = Lock()
        self._logs = []
        self._errors = []
        self._profiles = {}  # {func_name: [exec_times]}

    # ---------------- Timestamp ----------------

    def _timestamp(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # ---------------- Logging ----------------

    def _should_log(self, level):
        return self.LEVELS[level] >= self.LEVELS[self.log_level]

    def _write_to_file(self, entry):
        try:
            with open(self.logfile, "a", encoding="utf-8") as f:
                f.write(entry + "\n")
        except Exception as e:
            print(f"[SimpleQLogger ERROR] Cannot write to file: {e}")

    def _add_log(self, entry, level):
        with self._lock:
            if len(self._logs) >= self.max_log_memory:
                self._logs.pop(0)
            self._logs.append((level, entry))
        self._write_to_file(entry)
        if self.log_to_console and level != "DEBUG":
            print(entry)

    def debug(self, message):
        if self._should_log("DEBUG"):
            self._add_log(f"[{self._timestamp()}] DEBUG: {message}", "DEBUG")

    def info(self, message):
        if self._should_log("INFO"):
            self._add_log(f"[{self._timestamp()}] INFO: {message}", "INFO")

    def error(self, message, exc: Exception = None):
        ts = self._timestamp()
        base_msg = f"[{ts}] ERROR: {message}"
        if exc:
            tb = traceback.format_exc()
            entry = f"{base_msg}\nException:\n{tb}"
        else:
            entry = base_msg
        with self._lock:
            self._errors.append(entry)
        self._add_log(entry, "ERROR")

    # ---------------- Profilare funcții ----------------

    def profile(self, func=None):
        """
        Decorator pentru profilare timp execuție.
        Poate fi folosit cu sau fără paranteze.
        """

        def decorator(f):
            def wrapper(*args, **kwargs):
                start = time.perf_counter()
                try:
                    result = f(*args, **kwargs)
                except Exception as e:
                    self.error(f"Exception in '{f.__name__}'", e)
                    raise
                elapsed = time.perf_counter() - start
                with self._lock:
                    if f.__name__ not in self._profiles:
                        self._profiles[f.__name__] = []
                    self._profiles[f.__name__].append(elapsed)
                self.debug(f"Func '{f.__name__}' exec time: {elapsed:.6f}s")
                return result

            return wrapper

        if func:
            return decorator(func)
        return decorator

    # -------------- Profilare paralelă (ThreadPool) --------------

    def profile_parallel(self, funcs_with_args):
        """
        Execută funcții în paralel și profilează execuția.
        funcs_with_args: listă de tuple (func, args, kwargs)
        Returnează lista cu rezultatele.
        """
        n_workers = min(self.n_jobs, len(funcs_with_args))
        results = [None] * len(funcs_with_args)
        with ThreadPoolExecutor(max_workers=n_workers) as executor:
            futures = {
                executor.submit(self._profile_wrapper, f, *a, **kw): idx
                for idx, (f, a, kw) in enumerate(funcs_with_args)
            }
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    self.error(f"Error in parallel func idx={idx}", e)
                    results[idx] = None
        return results

    def _profile_wrapper(self, func, *args, **kwargs):
        """
        Wrapper intern pentru profilare în execuții paralele.
        """
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            self.error(f"Exception in parallel func '{func.__name__}'", e)
            raise
        elapsed = time.perf_counter() - start
        with self._lock:
            if func.__name__ not in self._profiles:
                self._profiles[func.__name__] = []
            self._profiles[func.__name__].append(elapsed)
        self.debug(f"[Parallel] Func '{func.__name__}' exec time: {elapsed:.6f}s")
        return result

    # ---------------- Rapoarte ----------------

    def get_profile_report(self):
        lines = ["=== Profile Report ==="]
        with self._lock:
            if not self._profiles:
                lines.append("No profiling data.")
            else:
                for f, times in self._profiles.items():
                    count = len(times)
                    total = sum(times)
                    avg = total / count if count > 0 else 0
                    mn = min(times) if times else 0
                    mx = max(times) if times else 0
                    lines.append(
                        f"{f}: calls={count}, total={total:.6f}s, avg={avg:.6f}s, min={mn:.6f}s, max={mx:.6f}s"
                    )
        return "\n".join(lines)

    def get_error_report(self):
        lines = ["=== Error Report ==="]
        with self._lock:
            if not self._errors:
                lines.append("No errors logged.")
            else:
                lines.extend(self._errors)
        return "\n".join(lines)

    def get_log_report(self, level_filter=None):
        """
        level_filter: None (toate), "INFO", "DEBUG", "ERROR"
        """
        lines = ["=== Log Report ==="]
        with self._lock:
            filtered = (
                [entry for lvl, entry in self._logs if lvl == level_filter]
                if level_filter
                else [entry for _, entry in self._logs]
            )
            if not filtered:
                lines.append("No logs found.")
            else:
                lines.extend(filtered)
        return "\n".join(lines)

    # ---------------- Reset ----------------

    def clear(self):
        with self._lock:
            self._logs.clear()
            self._errors.clear()
            self._profiles.clear()
        self.info("Logger cleared all data.")


# --------------------- Exemplu de utilizare ---------------------

if __name__ == "__main__":
    logger = SimpleQLogger(n_jobs=4, log_level="DEBUG", log_to_console=True)

    @logger.profile
    def slow_square(x):
        time.sleep(0.1)
        return x * x

    @logger.profile
    def might_fail(x):
        time.sleep(0.05)
        if x == 3:
            raise ValueError("Intentional error!")
        return x + 10

    # Rulez funcții normal
    for i in range(5):
        try:
            print(f"slow_square({i}) = {slow_square(i)}")
        except Exception as e:
            print(f"Caught error: {e}")

    # Rulez funcții în paralel
    funcs = [(might_fail, (i,), {}) for i in range(5)]
    results = logger.profile_parallel(funcs)
    print("Parallel results:", results)

    print("\n" + logger.get_profile_report())
    print("\n" + logger.get_error_report())
    print("\n" + logger.get_log_report())
