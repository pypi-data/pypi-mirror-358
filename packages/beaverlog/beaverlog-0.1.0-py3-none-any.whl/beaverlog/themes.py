import logging


class Theme:
    def __init__(self, name: str, is_colored: bool = False):
        self.name = name
        self.is_colored = is_colored
        self.set_theme(self.name)

    def set_theme(self, name: str):
        self.name = name

        match name:
            case 'basic':  # Ancien
                self.format_string = '%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s'

            case 'minimalist':  # Ancien
                self.format_string = '%(message)s'

            case 'maximalist':  # Ancien renommé
                self.format_string = (
                    '%(asctime)s.%(msecs)03d | %(levelname)s | %(name)s\n'
                    '%(filename)s - %(module)s - %(funcName)s:%(lineno)d\n'
                    '%(message)s'
                )

            case 'dev':
                self.format_string = '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s'

            case 'debug':
                self.format_string = '%(asctime)s | %(levelname)s | %(name)s | %(module)s.%(funcName)s:%(lineno)d | %(message)s'

            case 'stacktrace':
                self.format_string = '%(asctime)s %(levelname)s [%(name)s] %(message)s\n%(exc_info)s'

            case 'audit':
                self.format_string = '%(created)f | %(processName)s:%(process)d | %(threadName)s:%(thread)d | %(levelname)s | %(message)s'

            case 'fileorigin':
                self.format_string = '%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] - %(message)s'

            case 'numerical':
                self.format_string = '%(asctime)s - %(levelno)s - %(name)s - %(message)s'

            case 'security':
                self.format_string = '%(asctime)s | %(levelname)s | %(process)d | %(pathname)s:%(lineno)d | %(threadName)s | %(message)s'

            case 'asyncio':
                self.format_string = '%(asctime)s [%(levelname)s] %(taskName)s | %(message)s'

            case _:
                self.format_string = '%(message)s'

    def get_formatter(self):
        if self.is_colored:
            return ColorFormatter(self.format_string, datefmt='%Y-%m-%d %H:%M:%S')
        else:
            return logging.Formatter(self.format_string, datefmt='%Y-%m-%d %H:%M:%S')


class ColorFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt=fmt, datefmt=datefmt)

    def format(self, record):
        level_color = LevelColor.get_color(record.levelno)
        record.levelname = f"{level_color}{record.levelname:<8}{LevelColor.RESET}"
        return super().format(record)


class LevelColor:
    RESET = "\033[0m"
    DEBUG = "\033[2m"
    INFO = "\033[32m"
    WARNING = "\033[33m"
    ERROR = "\033[31m"
    CRITICAL = "\033[41m"

    @classmethod
    def get_color(cls, level):
        return {
            logging.DEBUG: cls.DEBUG,
            logging.INFO: cls.INFO,
            logging.WARNING: cls.WARNING,
            logging.ERROR: cls.ERROR,
            logging.CRITICAL: cls.CRITICAL,
        }.get(level, "")
