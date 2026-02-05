import json
import multiprocessing
import time
from pathlib import Path
from multiprocessing import Process
import logging.config


logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",  # Set level to INFO or higher
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

CONFIG_ERROR_MESSAGE = "Configuration error: The JSON structure is invalid (schema mismatch) or " \
                       "the file path specified in 'path_file' was not found or "\
                       "the path specified in 'output' was not found."

logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)


class DocumentadorAgent:
    _processes = []
    _config_path = "config.json"

    def __init__(self):
        self._load_config()

    def _load_config(self, first_time=True):
        try:
            with open(self._config_path, "rb") as file:
                jsondata = file.read()
                if not jsondata:
                    raise ValueError("The config.json file is invalid")
                new_config = json.loads(jsondata)
                is_valid = self._is_valid_config_scheme(new_config)
                if not is_valid:
                    if first_time:
                        raise RuntimeError(CONFIG_ERROR_MESSAGE)
                    else:
                        raise ValueError(CONFIG_ERROR_MESSAGE)
                self._config = new_config
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in config.json: {e}")

    @staticmethod
    def _is_valid_config_scheme(conf):
        if (
            "tracking" in conf
            and isinstance(conf["tracking"], list)
            and "output" in conf
            and isinstance(conf["output"], str)
            and Path(conf["output"]).is_dir()
        ):
            if conf["tracking"]:
                for item in conf["tracking"]:
                    if (
                        "path_file" not in item
                        or "diagram_types" not in item
                        or not isinstance(item["diagram_types"], list)
                        or not isinstance(item["path_file"], str)
                    ):
                        return False
                    file = Path(item["path_file"])
                    if not file.is_file():
                        return False
            return True
        return False

    def _watch_config(self):
        try:
            updatefile = 0
            while True:
                file = Path(self._config_path)
                st = file.stat()
                if st.st_mtime > updatefile:
                    updatefile = st.st_mtime
                    try:
                        self._load_config(False)
                        logger.info("Configuration Updated")
                    except ValueError as e:
                        logger.error(f"Could not update config:\n\t{e}")
                time.sleep(5)
        except KeyboardInterrupt:
            logger.info(f"{multiprocessing.current_process()} got CTRL-C")

    def _send_prompt(self):
        pass

    def _watch_files(self):
        try:
            tracking = self._config["tracking"]
            updatefile = 0
            while True:
                if tracking:
                    for trackfile in tracking:
                        file = Path(trackfile["path_file"])
                        st = file.stat()
                        if st.st_mtime > updatefile:
                            updatefile = st.st_mtime
                            logger.info(f"File changed: {file.name}")
                time.sleep(3)
        except KeyboardInterrupt:
            logger.info(f"{multiprocessing.current_process()} got CTRL-C")

    def start(self):
        for target in (self._watch_config, self._watch_files):
            p = Process(target=target, daemon=True)
            self._processes.append(p)
            p.start()
        try:
            for process in self._processes:
                process.join()
        except KeyboardInterrupt:
            logger.info("Exited")
