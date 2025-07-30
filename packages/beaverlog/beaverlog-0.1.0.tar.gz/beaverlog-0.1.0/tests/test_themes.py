import pytest
from beaverlog.core import Logger

THEMES = [
    "basic",
    "minimalist",
    "maximalist",
    "dev",
    "debug",
    "stacktrace",
    "audit",
    "fileorigin",
    "numerical",
    "security",
    "asyncio",
    "unknown"
]

LOG_LEVELS = [
    ("debug", "This is message for level : DEBUG"),
    ("info", "This is message for level : INFO"),
    ("warning", "This is message for level : WARNING"),
    ("error", "This is message for level : ERROR"),
    ("critical", "This is message for level : CRITICAL"),
]

@pytest.mark.parametrize("theme_name", THEMES)
@pytest.mark.parametrize("is_colored", [False, True])
def test_logger_theme(theme_name, is_colored):
    print('\n')
    log = Logger(theme_name=theme_name, is_colored=is_colored)
    for log_level, message_level in LOG_LEVELS:
        getattr(log, log_level)(message_level)

