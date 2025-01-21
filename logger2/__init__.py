import atexit
import json
import logging.config
import logging.handlers
import pathlib
import queue
import logging
from threading import Thread

logger = logging.getLogger("my_app")  # __name__ is a common choice




class QueueListenerThread(Thread):
    def __init__(self, log_queue, handlers):
        super().__init__(daemon=True)  # Ensure it doesn't block application shutdown
        self.log_queue = log_queue
        self.handlers = handlers
        self.running = True

    def run(self):
        while self.running:
            try:
                record = self.log_queue.get()
                if record is None:  # Sentinel value to stop the listener
                    break
                for handler in self.handlers:
                    handler.handle(record)
            except Exception:
                logging.getLogger("queue_listener").exception(
                    "Error processing log record"
                )

    def stop(self):
        self.running = False
        self.log_queue.put(None)  # Stop signal


def setup_logging():
    config_file = pathlib.Path(__file__).parent / "2-stderr-json-file.json"
    with open(config_file) as f_in:
        config = json.load(f_in)

    # Create the logging configuration
    logging.config.dictConfig(config)

    # Manually set up the queue and the listener
    log_queue = queue.Queue(-1)  # Unlimited size queue
    queue_handler = logging.handlers.QueueHandler(log_queue)

    # Get handlers from the config
    stderr_handler = logging.StreamHandler()
    file_json_handler = logging.handlers.RotatingFileHandler(
        filename="logs/my_app.log.jsonl", maxBytes=10000, backupCount=3
    )
    stderr_handler.setFormatter(logging.Formatter(
        config["formatters"]["simple"]["format"]))
    file_json_handler.setFormatter(logging.Formatter(
        config["formatters"]["json"]["fmt_keys"]))

    handlers = [stderr_handler, file_json_handler]

    # Set up the queue handler and add it to the root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(queue_handler)
    root_logger.setLevel(logging.DEBUG)

    # Start the QueueListener in a thread
    listener = QueueListenerThread(log_queue, handlers)
    listener.start()
    atexit.register(listener.stop)


def main():
    setup_logging()
    logging.basicConfig(level="INFO")
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
