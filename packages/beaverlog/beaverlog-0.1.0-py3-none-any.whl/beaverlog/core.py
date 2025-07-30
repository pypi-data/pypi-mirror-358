import logging
from .themes import Theme

class Logger(logging.Logger):
    def __init__(self, theme_name: str='default', is_colored: bool=False):
        super().__init__(f'beaverlog.{theme_name}', level=logging.DEBUG)

        theme = Theme(theme_name, is_colored)
        formatter = theme.get_formatter()

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        self.addHandler(handler)