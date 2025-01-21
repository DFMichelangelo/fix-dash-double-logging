import atexit
import datetime as dt
import json
import logging
import logging.config
import logging.handlers
import pathlib
import queue
from logging.handlers import QueueHandler, QueueListener

LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


class MyJSONFormatter(logging.Formatter):
    def __init__(self, *, fmt_keys: dict[str, str] | None = None):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    def format(self, record: logging.LogRecord) -> str:
        message = self._prepare_log_dict(record)
        return json.dumps(message, default=str)

    def _prepare_log_dict(self, record: logging.LogRecord):
        always_fields = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(
                record.created, tz=dt.timezone.utc
            ).isoformat(),
        }
        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatStack(record.stack_info)

        message = {
            key: msg_val
            if (msg_val := always_fields.pop(val, None)) is not None
            else getattr(record, val)
            for key, val in self.fmt_keys.items()
        }
        message.update(always_fields)

        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val

        return message


def setup_logging():
    # Load the JSON configuration file
    config_file = pathlib.Path(__file__).parent / "2-stderr-json-file.json"
    with open(config_file) as f_in:
        config = json.load(f_in)

    # Remove the queue handler from the configuration
    handlers = config["handlers"]
    handlers.pop("queue_handler", None)

    # Apply the remaining logging configuration
    logging.config.dictConfig(config)

    # Set up the logging queue
    log_queue = queue.Queue()

    # Add QueueHandler to the root logger
    queue_handler = QueueHandler(log_queue)
    root_logger = logging.getLogger()
    root_logger.addHandler(queue_handler)
    root_logger.setLevel(logging.DEBUG)

    # Create handlers manually for QueueListener
    stderr_handler = logging.StreamHandler()
    stderr_handler.setFormatter(
        logging.Formatter("[%(levelname)s|%(module)s|L%(lineno)d] %(asctime)s: %(message)s")
    )
    stderr_handler.setLevel(logging.WARNING)

    file_json_handler = logging.handlers.RotatingFileHandler(
        "logs/my_app.log.jsonl", maxBytes=10000, backupCount=3
    )
    file_json_handler.setFormatter(
        MyJSONFormatter(
            fmt_keys={
                "level": "levelname",
                "message": "message",
                "timestamp": "timestamp",
                "logger": "name",
                "module": "module",
                "function": "funcName",
                "line": "lineno",
                "thread_name": "threadName",
            }
        )
    )
    file_json_handler.setLevel(logging.DEBUG)

    # Create and start the QueueListener
    queue_listener = QueueListener(log_queue, stderr_handler, file_json_handler)
    queue_listener.start()

    # Ensure the QueueListener is stopped gracefully at program exit
    atexit.register(queue_listener.stop)


def main():
    setup_logging()
    
    # add start timer
    logging.basicConfig(level="INFO")
    start_time = dt.datetime.now()
    logger = logging.getLogger("my_app")

    # add end timer
    end_time = dt.datetime.now()
    print("TIME")
    print(end_time - start_time)
    logger.debug("debug message", extra={"x": "hello"})
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")
    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("exception message")


if __name__ == "__main__":
    main()