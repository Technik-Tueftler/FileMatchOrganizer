"""Doc
"""

import os
import platform
from pathlib import Path
import re
from dataclasses import dataclass, field
from typing import List
import tkinter as tk
from tkinter import PhotoImage, filedialog
from tempfile import TemporaryDirectory
from PIL import Image
from pdfquery import PDFQuery
from pdf2image import convert_from_path
import pytesseract

from constants import APP_INFORMATION, INITIAL_DIRECTORY

pattern = re.compile(r'\b\d+\s[A-Z]+\s\d+/\d+\b')

if platform.system() == "Windows":
    # We may need to do some additional downloading and setup...
    # Windows needs a PyTesseract Download
    # https://github.com/UB-Mannheim/tesseract/wiki/Downloading-Tesseract-OCR-Engine

    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    # Windows also needs poppler_exe
    # https://github.com/oschwartz10612/poppler-windows/releases/

    path_to_poppler_exe = Path(
        r"C:\Users\Technik_Tueftler\Downloads\Release-24.02.0-0\poppler-24.02.0\Library\bin"
    )

    # Put our output files in a sane place...
    out_directory = Path(r"~\Desktop").expanduser()
else:
    out_directory = Path("~").expanduser()

@dataclass
class AnalyzedFile:
    """Class of a analyzed pdf file for further processing
    """
    start_file_path: Path
    target_file_path: Path
    matched_pattern: List[int] = field(default_factory=list)
    analyzed_pages: List[int] = field(default_factory=list)
    def __repr__(self):
        if self.start_file_path is not None:
            return f"AnalyzedFile: {self.start_file_path}"
        return f"AnalyzedFile: {self.target_file_path}"

@dataclass
class AppSettings:
    """Generic class to organize settings 
    """
    initial_dir = INITIAL_DIRECTORY
    folder_start_path = None
    folder_target_path = None


settings = AppSettings()


class FileOrganizerApp:
    """General class for the application with GUI and"""

    def __init__(self, root):
        self.root = root
        self.root.title("File Match Organizer")
        root.iconphoto(True, PhotoImage(file="../files/icon.png"))

        # Menü erstellen
        self.menu_bar = tk.Menu(root)
        self.root.config(menu=self.menu_bar)

        self.menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Menü", menu=self.menu)

        self.menu.add_command(label="Information", command=self.show_information)
        self.menu.add_command(label="Einstellungen", command=self.show_settings)

        # Widgets
        self.file_label = tk.Label(root, text="Wähle Start- und Ziel-Verzeichnis aus:")
        self.file_label.pack(pady=10)

        self.file_button = tk.Button(
            root, text="Start-Verzeichnis", command=self.choose_start_folder
        )
        self.file_button.pack(pady=5)

        self.folder_button = tk.Button(
            root, text="Ziel-Verzeichnis", command=self.choose_target_folder
        )
        self.folder_button.pack(pady=5)

        self.organize_button = tk.Button(
            root, text="Organisieren", command=self.organize_files
        )
        self.organize_button.pack(pady=10)

        self.finish_button = tk.Button(root, text="Beenden", command=self.finish_app)
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

    def choose_start_folder(self):
        folder_start_path = filedialog.askdirectory(
            title="Ordner auswählen", initialdir=settings.initial_dir
        )
        settings.folder_start_path = folder_start_path
        # Hier könntest du den ausgewählten Ordnerpfad weiterverarbeiten oder speichern
        # image_3 = Image.open("89orp82.jpg")
        # photo_3 = ImageTk.PhotoImage(image_3)

        # Label widget to display the image
        # self.labelimage.configure(image=photo_3)
        # self.labelimage.image = photo_3

    def choose_target_folder(self):
        target_folder_path = filedialog.askdirectory(
            title="Ordner auswählen", initialdir=settings.initial_dir
        )
        settings.folder_target_path = target_folder_path

    def organize_files(self):
        """Handle function to analyze files and reorder
        """
        start_files = []
        end_files = []
        for root_path, _, files in os.walk(settings.folder_start_path):
            for name in files:
                if name.endswith(".pdf"):
                    with TemporaryDirectory() as tempdir:
                        pdf_file = Path(os.path.join(root_path, name))
                        images = converting_pdf_to_images(tempdir, pdf_file)
                        text = recognizing_text(images)
                        all_matches = [re.findall(pattern, s) for s in text]
                        print(all_matches)
                        start_files.append(AnalyzedFile(start_file_path=pdf_file,
                                                        target_file_path=None,
                                                        matched_pattern=all_matches,
                                                        analyzed_pages=text))
                        print(25*"#")

        for root_path, _, files in os.walk(settings.folder_target_path):
            for name in files:
                if name.endswith(".pdf"):
                    with TemporaryDirectory() as tempdir:
                        pdf_file = Path(os.path.join(root_path, name))
                        images = converting_pdf_to_images(tempdir, pdf_file)
                        text = recognizing_text(images)
                        all_matches = [re.findall(pattern, s) for s in text]
                        print(all_matches)
                        end_files.append(AnalyzedFile(start_file_path=None,
                                                        target_file_path=pdf_file,
                                                        matched_pattern=all_matches,
                                                        analyzed_pages=text))

    def finish_app(self):
        self.root.destroy()

    def show_information(self):
        info_window = tk.Toplevel(self.root)
        info_window.title("Informationen")

        info_label = tk.Label(info_window, text=APP_INFORMATION)
        info_label.pack(padx=20, pady=20)

        close_button = tk.Button(
            info_window, text="Schließen", command=info_window.destroy
        )
        close_button.pack(pady=10)

    def show_settings(self):
        # Hier könntest du ein Fenster oder Popup für Einstellungen anzeigen
        pass


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
        print(tempdir)
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
    root = tk.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()
