"""Doc
"""

import os
import platform
from pathlib import Path
import re
import shutil
from datetime import datetime
from dataclasses import dataclass, field
import time
from typing import List
import tkinter as tk
from tkinter import PhotoImage, filedialog, messagebox
from tempfile import TemporaryDirectory
from PIL import Image
from pdfquery import PDFQuery
from pdf2image import convert_from_path
import pytesseract
from tqdm import tqdm
import db

from constants import (
    APP_INFORMATION,
    INITIAL_DIRECTORY,
    OUTPUT_FILE,
    LOG_FILE,
    APP_ICON,
)
from configuration import text_pattern, pytesseract_path, path_to_poppler_exe

pattern = re.compile(r"\b" + text_pattern + r"\b")

if platform.system() == "Windows":
    # We may need to do some additional downloading and setup...
    # Windows needs a PyTesseract Download
    # https://github.com/UB-Mannheim/tesseract/wiki/Downloading-Tesseract-OCR-Engine

    pytesseract_path = r"" + pytesseract_path
    pytesseract.pytesseract.tesseract_cmd = pytesseract_path

    # Windows also needs poppler_exe
    # https://github.com/oschwartz10612/poppler-windows/releases/

    path_to_poppler_exe = Path(r"" + path_to_poppler_exe)

    # Put our output files in a sane place...
    out_directory = Path(r"~\Desktop").expanduser()
else:
    out_directory = Path("~").expanduser()


@dataclass
class PdfFile:
    """Class of a pdf file for further processing during indexing"""

    path: str
    directory: str
    name: str


@dataclass
class AnalyzedFile:
    """Class of a analyzed pdf file for further processing"""

    path: str
    file: str
    matched_pattern: List[int] = field(default_factory=list)
    analyzed_pages: List[int] = field(default_factory=list)

    def __repr__(self):
        return f"AnalyzedFile: {self.file} in {self.path}"


@dataclass
class AppSettings:
    """Generic class to organize settings"""

    initial_dir = INITIAL_DIRECTORY
    folder_start_path = None
    folder_target_path = None


settings = AppSettings()


class FileOrganizerApp:
    """General class for the application with GUI and"""

    def __init__(self, window):
        self.root = window
        self.root.title("File Match Organizer")
        if APP_ICON is not None:
            self.root.iconphoto(True, PhotoImage(file=APP_ICON))

        # Menü erstellen
        self.menu_bar = tk.Menu(window)
        self.root.config(menu=self.menu_bar)

        self.menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Menü", menu=self.menu)

        self.menu.add_command(label="Information", command=self.show_information)
        self.menu.add_command(label="Einstellungen", command=self.show_settings)

        # Widgets
        self.file_label = tk.Label(
            self.root, text="Wähle Start- und Ziel-Verzeichnis aus:"
        )
        self.file_label.pack(pady=10)

        self.file_button = tk.Button(
            self.root, text="Start-Verzeichnis", command=self.choose_start_folder
        )
        self.file_button.pack(pady=5)

        self.folder_button = tk.Button(
            self.root, text="Ziel-Verzeichnis", command=self.choose_target_folder
        )
        self.folder_button.pack(pady=5)

        self.organize_button = tk.Button(
            self.root, text="Organisieren", command=self.organize_files
        )
        self.organize_button.pack(pady=10)

        self.index_button = tk.Button(self.root, text="Indexierung", command=self.index)
        self.index_button.pack(pady=10)

        self.finish_button = tk.Button(
            self.root, text="Beenden", command=self.finish_app
        )
        self.finish_button.pack(pady=10)

        # Load the image
        # image_2 = Image.open("89orp8.jpg")
        # photo_2 = ImageTk.PhotoImage(image_2)

        # Label widget to display the image
        # self.labelimage = tk.Label(root, image=photo_2)
        # self.labelimage.image = photo_2
        # self.labelimage.pack(pady=10)

        # def update_picture(self, image):
        # self.labelimage.configure(image=image)
        # self.labelimage.image = image
        if "" in (path_to_poppler_exe, pytesseract_path):
            messagebox.showwarning("WARNING", "not all paths have been indicated")

    def choose_start_folder(self):
        """Reaction of the button for select start directory"""
        folder_start_path = filedialog.askdirectory(
            title="Ordner auswählen", initialdir=settings.initial_dir
        )
        settings.folder_start_path = folder_start_path

    def choose_target_folder(self):
        """Reaction of the button for select target directory"""
        target_folder_path = filedialog.askdirectory(
            title="Ordner auswählen", initialdir=settings.initial_dir
        )
        settings.folder_target_path = target_folder_path

    def organize_files(self):
        """Handle function to analyze files and reorder"""
        start_files = []
        end_files = []
        write_info(f"{datetime.now()}: Starting the conversion of the start files")
        for root_path, _, files in os.walk(settings.folder_start_path):
            for name in files:
                if name.endswith(".pdf"):
                    with TemporaryDirectory() as tempdir:
                        pdf_file = Path(os.path.join(root_path, name))
                        images = converting_pdf_to_images(tempdir, pdf_file)
                        text = recognizing_text(images)
                        all_matches = [re.findall(pattern, s) for s in text]
                        start_files.append(
                            AnalyzedFile(
                                path=root_path,
                                file=name,
                                matched_pattern=list(
                                    {
                                        item
                                        for sublist in all_matches
                                        for item in sublist
                                    }
                                ),
                                analyzed_pages=text,
                            )
                        )
        write_info(
            f"{datetime.now()}: Finishing the conversion of the start files "
            "and starting conversion of the target files"
        )

        for root_path, _, files in os.walk(settings.folder_target_path):
            for name in files:
                if name.endswith(".pdf"):
                    with TemporaryDirectory() as tempdir:
                        pdf_file = Path(os.path.join(root_path, name))
                        images = converting_pdf_to_images(tempdir, pdf_file)
                        text = recognizing_text(images)
                        all_matches = [re.findall(pattern, s) for s in text]
                        end_files.append(
                            AnalyzedFile(
                                path=root_path,
                                file=name,
                                matched_pattern=list(
                                    {
                                        item
                                        for sublist in all_matches
                                        for item in sublist
                                    }
                                ),
                                analyzed_pages=text,
                            )
                        )

        write_info(
            f"{datetime.now()}: Finishing the conversion of the target files and "
            "starting to pattern matching"
        )

        for start_element in start_files:
            for start_match in start_element.matched_pattern:
                match_pattern = self.search_match(start_match, end_files)
                if match_pattern is None:
                    print(f"Keine übereinstimmung gefunden für {start_element}")
                else:
                    move_file(start_element, match_pattern)
                    break
        write_info(f"{datetime.now()}: Finishing pattern matching and file moving")

    def index(self):
        if settings.folder_target_path is None:
            messagebox.showwarning("WARNING", "Please select the target path")
            return
        write_info(f"{datetime.now()}: Start Indexing")
        pdf_files = []
        for root_path, directory, files in os.walk(settings.folder_target_path):
            for name in files:
                if name.endswith(".pdf"):
                    pdf_files.append(
                        PdfFile(path=root_path, directory=directory, name=name)
                    )
        for pdf_file in tqdm(pdf_files):
            with TemporaryDirectory() as tempdir:
                file_path = Path(os.path.join(pdf_file.path, pdf_file.name))
                images = converting_pdf_to_images(tempdir, file_path)
                text = recognizing_text(images)
                all_matches = [re.findall(pattern, s) for s in text]
                matches_flat = [element for list in all_matches for element in list]
                if matches_flat:
                    for match in matches_flat:
                        recorded = (
                            db.session.query(db.Match).filter_by(pattern=match).first()
                        )
                        if recorded is not None:
                            continue
                        db.session.add(
                            db.Match(
                                pattern=match,
                                root_path="NA",
                                match_path=pdf_file.path,
                                match_file=pdf_file.name,
                            )
                        )
                db.session.commit()

    def search_match(
        self, str_pattern: str, objects: List[AnalyzedFile]
    ) -> AnalyzedFile:
        """Function search a string pattern in a list of objects for target directorys

        Args:
            str_pattern (str): Pattern to search
            objects (List[AnalyzedFile]): List of objects which includes the pattern

        Returns:
            AnalyzedFile: Object with the matched pattern
        """
        found_pattern = False
        end_element = None
        for end_element in objects:
            for end_match in end_element.matched_pattern:
                if str_pattern == end_match:
                    print("Hit")
                    print(f"End-Dir: {end_element}")
                    found_pattern = True
                    break
            if found_pattern:
                break
        return end_element

    def finish_app(self):
        """Reaction of the button for close the app"""
        write_info(f"Program ends at: {datetime.now()}")
        self.root.destroy()

    def show_information(self):
        """Reaction of the menu entry to show app information"""
        info_window = tk.Toplevel(self.root)
        info_window.title("Information")

        info_label = tk.Label(info_window, text=APP_INFORMATION)
        info_label.pack(padx=20, pady=20)

        close_button = tk.Button(info_window, text="Close", command=info_window.destroy)
        close_button.pack(pady=10)

    def show_settings(self):
        """Reaction of the menu entry to show app settings"""
        setting_window = tk.Toplevel(self.root)
        setting_window.title("Settings")
        setting_window.geometry("500x300")
        sw_info_label_pattern = tk.Label(setting_window, text="Matched Pattern")
        sw_info_label_pattern.pack(pady=10)


def move_file(start_object: AnalyzedFile, target_object: AnalyzedFile) -> None:
    """Function moves the transferred files in target directorys

    Args:
        start_object (AnalyzedFile): Object with file to be moved
        target_object (AnalyzedFile): Object with path where it should be moved to
    """
    check_target_path = Path(os.path.join(target_object.path, start_object.file))
    if check_target_path.is_file():
        write_info(
            f"File with the name {start_object.file} already exists in "
            "directory {target_object.path}"
        )
        return
    start_path = os.path.join(start_object.path, start_object.file)
    target_path = os.path.join(target_object.path, start_object.file)
    shutil.move(start_path, target_path)
    write_info(
        f"File with the name {start_object.file} moved from {start_path} to {target_path}"
    )


def write_info(text: str) -> None:
    """Helper function to write the output file

    Args:
        text (str): Text to be written
    """
    with open(OUTPUT_FILE, "a", encoding="utf-8") as file:
        file.write(f"{text}\n")


def write_log(text: str) -> None:
    """Helper function to write the log file

    Args:
        text (str): Text to be written
    """
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"{text}\n")


def converting_pdf_to_images(tempdir: str, pdf_path: Path) -> List[str]:
    """Function read all PDF pages anc converting it to pictures

    Args:
        pdf_path (str): Path of the PDF file

    Returns:
        list[str]: List of paths with pictures
    """
    image_file_list = []
    if platform.system() == "Windows":
        pdf_pages = convert_from_path(pdf_path, 500, poppler_path=path_to_poppler_exe)
    else:
        pdf_pages = convert_from_path(pdf_path, 500)
    for page_enumeration, page in enumerate(pdf_pages, start=1):
        filename = f"{tempdir}\page_{page_enumeration:03}.jpg"
        page.save(filename, "JPEG")
        image_file_list.append(filename)
    return image_file_list


def recognizing_text(image_file_list: List[str]) -> List[str]:
    """Function recognizes text from image

    Args:
        image_file_list (list[str]): List of paths from images

    Returns:
        list[str]: List of recognized text from images
    """
    text_file_list = []
    for image_file in image_file_list:
        text = str(((pytesseract.image_to_string(Image.open(image_file), lang="deu"))))
        text = text.replace("-\n", "").replace("\n", " ")
        text_file_list.append(text)
    return text_file_list


def extract_text_from_pdf(root_path: str, name: str) -> str:
    """Extract text from PDF
    Args:
        root_path (str): Completely path of the file
        name (str): Name of the PDF file
    """
    pdf = PDFQuery(os.path.join(root_path, name))
    pdf.load()
    text_elements = pdf.pq("LTTextLineHorizontal")
    text = [t.text for t in text_elements]
    return text


if __name__ == "__main__":
    write_info(f"Program start at: {datetime.now()}")
    try:
        root = tk.Tk()
        app = FileOrganizerApp(root)
        root.mainloop()
    except Exception as err:
        write_info(err)
