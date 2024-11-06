import tkinter as tk
from tkinter import ttk, messagebox
import logging
import os
from configparser import ConfigParser

class AddNoteWindow(tk.Toplevel):
    """Okno dialogowe umożliwiające dodanie nowej notatki do aplikacji."""

    def __init__(self, master, db, user_id):
        """
        Inicjalizuje okno do dodawania nowej notatki.

        Parametry:
            master (tk.Tk): Obiekt nadrzędny (okno główne).
            db (Database): Instancja bazy danych umożliwiająca operacje na notatkach.
            user_id (int): ID użytkownika dodającego notatkę.
        """
        super().__init__(master)
        self.user_id = user_id
        self.db = db
        
        try:
            config = self.load_config()

            self.banned_titles = config["SETTINGS"]["banned_titles"].split(", ")
            self.max_title_length = int(config["SETTINGS"]["max_title_length"])
        except Exception as e:
            raise Exception("Nie udało się załadować konfiguracji: " + str(e))
        
        self.title("Dodawanie notatki")
        window_width = 500
        window_height = 570
        self.geometry(f"{window_width}x{window_height}")
        self.minsize(window_width, window_height)
        
        self.initialize_interface()

    def initialize_interface(self):
        """Tworzy i rozmieszcza elementy interfejsu użytkownika."""
        try:
            title_frame = ttk.Frame(self)
            title_frame.pack(pady=10)

            content_frame = ttk.Frame(self)
            content_frame.pack(pady=10)

            button_frame = ttk.Frame(self)
            button_frame.pack(pady=10)

            ttk.Label(title_frame, text="Tytuł:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
            self.title_entry = ttk.Entry(title_frame, width=50)
            self.title_entry.grid(row=1, column=0, padx=5, pady=5)

            ttk.Label(content_frame, text="Treść:").grid(row=0, column=0, padx=5, pady=5, sticky='w')

            text_frame = ttk.Frame(content_frame)
            text_frame.grid(row=1, column=0)
            self.content_text = tk.Text(text_frame, wrap="word", width=50, height=20)
            self.content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            self.scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.content_text.yview)
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.content_text['yscrollcommand'] = self.scrollbar.set

            ttk.Button(button_frame, text="Zapisz notatkę", command=self.save_note).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Anuluj", command=self.destroy).pack(side=tk.LEFT, padx=5)
        except Exception as e:
            raise Exception("Błąd podczas inicjalizacji interfejsu: " + str(e))

    def save_note(self):
        """
        Zapisuje nową notatkę do bazy danych po przeprowadzeniu walidacji.

        Jeśli walidacja przebiegnie pomyślnie, notatka zostanie dodana, a okno zamknięte.
        W przypadku błędów pojawi się odpowiedni komunikat.
        """
        note_title = self.title_entry.get().strip()
        content = self.content_text.get("1.0", "end-1c").strip()

        try:
            if not self.validate_note_title(note_title):
                return
            
            if not content:
                messagebox.showerror("Błąd", "Treść notatki nie może być pusta.")
                return

            if self.db.add_note(self.user_id, content, note_title):
                messagebox.showinfo("Sukces", "Dodano notatkę!")
                self.destroy()
            else:
                messagebox.showerror("Błąd", "Wystąpił nieznany błąd podczas dodawania notatki.")
        except Exception as e:
            logging.error("Błąd podczas zapisywania nowej notatki: %s", e)
            raise Exception(f"Nie udało się zapisać notatki: {str(e)}")
        
    def load_config():
        """
        Wczytuje konfigurację z pliku config.ini.
        
        Zwraca:
            ConfigParser: Obiekt konfiguracji.
        """
        try:
            config = ConfigParser()
            exe_dir = os.path.dirname(os.path.abspath(__file__)) 
            config_path = os.path.join(exe_dir, "config.ini")
            
            with open(config_path, "r", encoding="utf-8") as config_file:
                config.read_file(config_file)
            return config
        except Exception as e:
            raise Exception("Nie udało się wczytać pliku konfiguracyjnego") from e

    def validate_note_title(self, note_title):
        """
        Waliduje tytuł notatki pod kątem wymagań aplikacji.

        Parametry:
            note_title (str): Tytuł notatki do walidacji.

        Zwraca:
            bool: True, jeśli tytuł jest poprawny, w przeciwnym razie False.
        """
        try:
            if not note_title:
                messagebox.showerror("Błąd", "Notatka powinna mieć tytuł.")
                return False
            elif note_title in self.banned_titles:
                messagebox.showerror("Błąd", "Wybrany tytuł jest zakazany. Proszę wpisać inny.")
                return False
            elif len(note_title) > self.max_title_length:
                messagebox.showerror("Błąd", f"Tytuł nie może przekraczać {self.max_title_length} znaków.")
                return False
            elif self.db.note_name_exists(note_title):
                messagebox.showerror("Błąd", "Notatka z podaną nazwą już istnieje.")
                return False

            return True
        except Exception as e:
            raise Exception("Błąd podczas walidacji tytułu notatki: " + str(e))
