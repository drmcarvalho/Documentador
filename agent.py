import json
import multiprocessing
import time
from pathlib import Path
from multiprocessing import Process
import logging.config
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import constants


logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

CONFIG_ERROR_MESSAGE = (
    "Configuration error: The JSON structure is invalid (schema mismatch) or "
    "the file path specified in 'path_file' was not found or "
    "the path specified in 'output' was not found."
)
CONFIG_ERROR_INVALID_MESSAGE = "The config.json file is invalid"

logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)


def make_request(url, payload, headers, method="GET"):
    try:
        data = json.dumps(payload).encode("utf-8")
        req = Request(url, data=data, headers=headers, method=method)
        response = urlopen(req)
        return {response.read().decode(), response.code}
    except HTTPError as e:
        logger.error("An error occurred during the HTTP request")
        return {None, e.code}


class DocumentadorAgent:
    _processes = []
    _config_path = "config.json"
    _prompt_cfg = (
        "Please convert the following code into a Control Flow Graph using graphviz dot language syntax.\n"
        "```\n"
        "{code}\n"
        "```\n"
        "The output must be only the CFG diagram in DOT language.\n"
    )
    _prompt_class_diagram = ""

    def __init__(self):
        self._load_config()

    def _load_config(self, first_time=True):
        try:
            with open(self._config_path, "rb") as file:
                jsondata = file.read()
                if not jsondata:
                    if first_time:
                        raise RuntimeError(CONFIG_ERROR_INVALID_MESSAGE)
                    else:
                        raise ValueError(CONFIG_ERROR_INVALID_MESSAGE)
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
            logger.info(
                f"{multiprocessing.current_process()} got CTRL-C at {self._watch_config.__name__ }"
            )

    def _send_prompt(self):
        pass

    def _watch_files(self):
        try:
            updatefile = 0
            while True:
                tracking = self._config["tracking"]
                if tracking:
                    for trackfile in tracking:
                        file = Path(trackfile["path_file"])
                        st = file.stat()
                        if st.st_mtime > updatefile:
                            updatefile = st.st_mtime
                            logger.info(f"File changed: {file.name}")
                            with open(file.resolve(), "r") as f:
                                data = f.read()
                                if not data:
                                    continue
                                if "graph" in trackfile:
                                    prompt = self._prompt_cfg.format(code=data)
                                    content, code = make_request(
                                        constants.API_URL_GEMINI,
                                        {
                                            "contents": [
                                                {
                                                    "parts": [
                                                        {
                                                            "text": prompt
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                        {
                                            constants.API_KEY_GEMINI_HEADER: constants.API_KEY,
                                            "Content-Type": "application/json"
                                        },
                                        "POST",
                                    )
                                    if 200 <= code <= 299:
                                        pass
                                if "class" in trackfile:
                                    pass  # TODO: generate class diagram
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info(
                f"{multiprocessing.current_process()} got CTRL-C at {self._watch_files.__name__}"
            )

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
