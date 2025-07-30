import logging
import datetime
import os

def setup_logger(verbose=False):
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    logs_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    traceback_log = os.path.join(logs_dir, f"traceback-file-transfer-{timestamp}.txt")
    status_log = os.path.join(logs_dir, f"status-file-transfer-{timestamp}.txt")

    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(traceback_log, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    status_logger = logging.getLogger("StatusLogger")
    status_handler = logging.FileHandler(status_log, encoding='utf-8')
    status_handler.setLevel(logging.INFO)
    status_handler.setFormatter(logging.Formatter("%(asctime)s [STATUS] %(message)s"))
    status_logger.addHandler(status_handler)
    status_logger.propagate = False
    status_logger.setLevel(logging.INFO)

    return logging.getLogger("ESP32BatchServer"), status_logger
