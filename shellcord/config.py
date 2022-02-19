import logging
# Markdown helpers
TRIPLE_TICKS = "```"

# Scord files
SCORD_LOG_REGEX = r"scord-log-\w+.json"
SCORD_ID_REGEX = r"scord-(\w+)-(\w+)"
DEFAULT_OUT_FILE = "scord-out.md"

# Set to get debug logging without setting the cli option
FORCE_DEBUG = False


DEFAULT_LOG_LEVEL = logging.INFO
