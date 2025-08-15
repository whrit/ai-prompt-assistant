import os
import sys
import time
import logging
import threading
import traceback
from pathlib import Path


_logger = None


def _default_log_dir() -> Path:
    base = Path(os.path.expanduser("~/Library/Application Support/AI Prompt Assistant/logs"))
    base.mkdir(parents=True, exist_ok=True)
    return base


def setup_debugging(enabled: bool = True, log_dir: Path | None = None) -> None:
    global _logger
    if _logger is not None:
        return
    if not enabled:
        _logger = logging.getLogger("aipa")
        _logger.addHandler(logging.NullHandler())
        return
    log_dir = log_dir or _default_log_dir()
    log_path = log_dir / "app.log"
    logger = logging.getLogger("aipa")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fmt = logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(threadName)s %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    _logger = logger

    # Global exception hook
    def _hook(exc_type, exc, tb):
        try:
            logger.error("Uncaught exception: %s", "".join(traceback.format_exception(exc_type, exc, tb)))
        except Exception:
            pass
        # Also print to stderr for visibility
        sys.__excepthook__(exc_type, exc, tb)

    sys.excepthook = _hook

    # Optional: faulthandler to dump threads on SIGUSR2 if available
    try:
        import faulthandler, signal
        faulthandler.enable(file=open(log_dir / "faulthandler.log", "a"))
        faulthandler.register(signal.SIGUSR2, all_threads=True)
    except Exception:
        pass


def get_logger() -> logging.Logger:
    global _logger
    if _logger is None:
        setup_debugging(enabled=True)
    return _logger


def log_debug(msg: str, **context):
    logger = get_logger()
    try:
        if context:
            msg = f"{msg} | {context}"
        logger.debug(msg)
    except Exception:
        pass


def log_error(msg: str, **context):
    logger = get_logger()
    try:
        if context:
            msg = f"{msg} | {context}"
        logger.error(msg)
    except Exception:
        pass


def log_exception(where: str):
    logger = get_logger()
    try:
        logger.error("Exception in %s: %s", where, traceback.format_exc())
    except Exception:
        pass


def log_call(func):
    def wrapper(*args, **kwargs):
        log_debug(f"ENTER {func.__qualname__}")
        try:
            result = func(*args, **kwargs)
            log_debug(f"EXIT {func.__qualname__}")
            return result
        except Exception:
            log_exception(func.__qualname__)
            raise
    return wrapper


class UIHeartbeat:
    def __init__(self, interval: float = 0.5, warn_after: float = 3.0):
        self._last = time.time()
        self._interval = interval
        self._warn_after = warn_after
        self._stop = threading.Event()

    def tick(self):
        self._last = time.time()

    def start_watcher(self):
        logger = get_logger()
        def _watch():
            while not self._stop.is_set():
                time.sleep(self._interval)
                if time.time() - self._last > self._warn_after:
                    logger.warning("UI heartbeat stalled for %.2fs", time.time() - self._last)
        t = threading.Thread(target=_watch, name="UIHeartbeatWatcher", daemon=True)
        t.start()

    def stop(self):
        self._stop.set()


