import os
from dotenv import dotenv_values
from constants import APP_ENVIRONMENT, DEFAULT_PATTERN

config = {
    **dotenv_values(APP_ENVIRONMENT),
    **os.environ,
}

text_pattern = config.get("FMO_PATTERN", DEFAULT_PATTERN)
pytesseract_path = config.get("FMO_PYTESSERACT_PATH", "")
path_to_poppler_exe = config.get("FMO_PROPPLER_EXE_PATH", "")
