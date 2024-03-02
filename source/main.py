"""Doc
"""
import os
import tkinter as tk
from tkinter import PhotoImage, filedialog

from constants import APP_INFORMATION, INITIAL_DIRECTORY


class AppSettings:
    def __init__(self):
        self.initial_dir = INITIAL_DIRECTORY
        self.folder_start_path = None
        self.folder_target_path = None


settings = AppSettings()


class FileOrganizerApp:
    """General class for the application with GUI and"""

    def __init__(self, root):
        self.root = root
        self.root.title("File Match Organizer")
        # self.root.geometry("500x300")
        icon = PhotoImage(file="../files/icon.png")
        root.iconphoto(True, icon)

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

    def choose_start_folder(self):
        folder_start_path = filedialog.askdirectory(
            title="Ordner auswählen", initialdir=settings.initial_dir
        )
        settings.folder_start_path = folder_start_path
        # Hier könntest du den ausgewählten Ordnerpfad weiterverarbeiten oder speichern

    def choose_target_folder(self):
        target_folder_path = filedialog.askdirectory(
            title="Ordner auswählen", initialdir=settings.initial_dir
        )
        settings.folder_target_path = target_folder_path
        # Hier könntest du die ausgewählte Datei weiterverarbeiten oder speichern

    def organize_files(self):
        # Hier könntest du die Logik implementieren, um die Dateien zu organisieren
        print(settings.folder_start_path)
        print(settings.folder_target_path)
        print(25*"-")
        temp_files = []
        for root, dirs, files in os.walk(settings.folder_start_path):
            for name in files:
                if name.endswith(".txt"):
                    temp_files.append(name)
            print(f"root: {root}")
            print(f"dirs: {dirs}")
            print(f"files: {files}")
            print(25*"-")
        print(f"names: {temp_files}")
        
        for root, dirs, files in os.walk(settings.folder_target_path):
            for name in files:
                ...

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


if __name__ == "__main__":
    root = tk.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()
