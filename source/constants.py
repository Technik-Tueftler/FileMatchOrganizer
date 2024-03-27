"""Collection of constants for the App
"""
from pathlib import Path

APP_INFORMATION = "Version: v0.0.1"
APP_ICON_PATH = "../files/icon.png"
INITIAL_DIRECTORY = "D:/Workspace/git/FileMatchOrganizer/files"
OUTPUT_FILE = "FileMatchOrganizer_info.txt"
LOG_FILE = "FileMatchOrganizer_log.txt"
DEFAULT_PATTERN = "[A-Z]+\s\d+/\d+|\d+\s[A-Z]+\s\d+/\d+"
ENVIRONMENT_FILE = "../files/.env"
PYTESSERACT_PATH="C:\Program Files\Tesseract-OCR\tesseract.exe"

if Path(APP_ICON_PATH).is_file():
    APP_ICON = APP_ICON_PATH
elif Path("icon.png").is_file():
    APP_ICON = "icon.png"
else:
    APP_ICON = None

if Path(ENVIRONMENT_FILE).is_file():
    APP_ENVIRONMENT = ENVIRONMENT_FILE
else:
    APP_ENVIRONMENT = ".env"
