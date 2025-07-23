# Python Imports #
import logging
import threading


class Logger:
    """
        Custom logger that uses the singleton-pattern to get instantiated.
        Logs to both console and file with thread ID and timestamp.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self, log_file: str = "ofl_app.log"):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.logger = logging.getLogger("ofl_logger")
        self.logger.setLevel(logging.DEBUG)  # TODO: Make this configurable

        formatter = logging.Formatter(
            fmt="%(levelname)-8s  %(asctime)s (%(thread)d) - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # File Handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Avoid adding handlers multiple times
        if not self.logger.hasHandlers():
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

        # Set
        self._initialized = True


    def info(self, msg):
        """ Report events that occur during normal operation of the downloader. """
        self.logger.info(msg)

    def debug(self, msg):
        """ Report events that occur during debugging. """
        self.logger.debug(msg)

    def warning(self, msg):
        """ Issue a warning regarding a particular runtime event. """
        self.logger.warning(msg)

    def error(self, msg):
        """ Report suppression of an error without raising an exception. """
        self.logger.error(msg)


LOGGER = Logger(log_file="ofl_app.log")
