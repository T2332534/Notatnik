import tkinter as tk 
from tkinter import ttk, messagebox
import logging
from configparser import ConfigParser
import os

class EditNoteWindow(tk.Toplevel):
    """
    Klasa reprezentująca okno edycji notatki. Pozwala użytkownikowi na edycję tytułu i treści istniejącej notatki oraz na jej usunięcie.
    """

    def __init__(self, master, db, user_id, note_title, note_content):
        """
        Inicjalizuje okno edycji notatki z danymi wyjściowymi.

        Parametry:
            master (tk.Tk): Główne okno aplikacji.
            db (Database): Obiekt bazy danych.
            user_id (int): ID użytkownika.
            note_title (str): Oryginalny tytuł notatki.
            note_content (str): Oryginalna treść notatki.
        """
        super().__init__(master)
        self.user_id = user_id
        self.db = db
        try:
            self.config = self.load_config()
        except Exception as e:
            logging.error("Błąd podczas wczytywania konfiguracji: %s", e)
            raise Exception("Nie udało się wczytać konfiguracji")

        self.banned_titles = self.config["SETTINGS"]["banned_titles"].split(", ")
        self.max_title_length = int(self.config["SETTINGS"]["max_title_length"])

        self.original_title = note_title
        self.title("Edycja notatki")
        self.setup_window()
        self.initialize_interface(note_content)

    def setup_window(self):
        """
        Ustawia podstawowe parametry okna, takie jak wymiary i minimalny rozmiar.
        """
        try:
            window_width, window_height = 500, 570
            self.geometry(f"{window_width}x{window_height}")
            self.minsize(window_width, window_height)
        except Exception as e:
            logging.error("Błąd podczas ustawiania parametrów okna: %s", e)
            raise Exception("Nie udało się ustawić parametrów okna")

    def initialize_interface(self, note_content):
        """
        Tworzy i rozmieszcza widżety w oknie, w tym pole na tytuł, pole tekstowe na treść oraz przyciski.

        Parametry:
            note_content (str): Treść notatki do wyświetlenia i edycji.
        """
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
            self.title_entry.insert(0, self.original_title)

            ttk.Label(content_frame, text="Treść:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
            self.create_text_widget(content_frame, note_content)

            ttk.Button(button_frame, text="Zapisz edytowaną notatkę", command=self.save_note).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Anuluj", command=self.destroy).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Usuń notatkę", command=self.delete_note).pack(side=tk.LEFT, padx=5)
        except Exception as e:
            logging.error("Błąd podczas tworzenia interfejsu: %s", e)
            raise Exception("Nie udało się utworzyć interfejsu")

    def create_text_widget(self, parent, note_content):
        """
        Tworzy pole tekstowe do edycji treści notatki wraz z pionowym paskiem przewijania.

        Parametry:
            parent (ttk.Frame): Ramka, w której zostanie umieszczone pole tekstowe.
            note_content (str): Treść notatki do wyświetlenia i edycji.
        """
        try:
            text_frame = ttk.Frame(parent)
            text_frame.grid(row=1, column=0)
            self.content_text = tk.Text(text_frame, wrap="word", width=50, height=20)
            self.content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            if isinstance(note_content, str):
                self.content_text.insert("1.0", note_content)
            else:
                self.content_text.insert("1.0", "")

            scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.content_text.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.content_text['yscrollcommand'] = scrollbar.set
        except Exception as e:
            logging.error("Błąd podczas tworzenia pola tekstowego: %s", e)
            raise Exception("Nie udało się utworzyć pola tekstowego")

    def save_note(self):
        """
        Sprawdza poprawność tytułu i treści notatki, a następnie zapisuje zmiany do bazy danych.
        
        Jeśli zapis jest udany, zamyka okno edycji i wyświetla komunikat sukcesu.
        W przypadku błędu wyświetla komunikat błędu.
        """
        new_title = self.title_entry.get().strip()
        content = self.content_text.get("1.0", "end-1c").strip()

        try:
            if not self.validate_title(new_title):
                return

            if not content:
                messagebox.showerror("Błąd", "Treść notatki nie może być pusta.")
                return

            if self.db.update_note(self.user_id, self.original_title, content, new_title):
                messagebox.showinfo("Sukces", "Zaktualizowano notatkę!")
                self.destroy()
            else:
                messagebox.showerror("Błąd", "Wystąpił nieznany błąd podczas aktualizacji notatki.")
        except Exception as e:
            logging.error("Błąd podczas zapisywania notatki: %s", e)
            messagebox.showerror("Błąd", f"Nie udało się zapisać notatki: {str(e)}")

    def delete_note(self):
        """
        Usuwa notatkę z bazy danych po potwierdzeniu przez użytkownika.
        
        W przypadku sukcesu zamyka okno edycji i wyświetla komunikat sukcesu.
        W przypadku błędu wyświetla komunikat błędu.
        """
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć tę notatkę?"):
            try:
                if self.db.delete_note(self.original_title):
                    messagebox.showinfo("Sukces", "Notatka została usunięta.")
                    self.destroy()
                else:
                    messagebox.showerror("Błąd", "Wystąpił błąd podczas usuwania notatki.")
            except Exception as e:
                logging.error("Błąd podczas usuwania notatki: %s", e)
                messagebox.showerror("Błąd", f"Nie udało się usunąć notatki: {str(e)}")

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
    

    def validate_title(self, new_title):
        """
        Waliduje wprowadzone dane w polu tytułu notatki.

        Parametry:
            new_title (str): Tytuł notatki do sprawdzenia.

        Zwraca:
            bool: True, jeśli tytuł jest poprawny, False w przeciwnym razie.
        """
        try:
            if not new_title:
                messagebox.showerror("Błąd", "Notatka powinna mieć tytuł.")
                return False
            if new_title in self.banned_titles:
                messagebox.showerror("Błąd", "Wybrany tytuł jest zakazany. Proszę wpisać inny.")
                return False
            if len(new_title) > self.max_title_length:
                messagebox.showerror("Błąd", f"Tytuł nie może przekraczać {self.max_title_length} znaków.")
                return False
            if self.db.note_name_exists(new_title) and new_title != self.original_title:
                messagebox.showerror("Błąd", "Notatka z podaną nazwą już istnieje.")
                return False
            return True
        except Exception as e:
            logging.error("Błąd podczas walidacji tytułu: %s", e)
            raise Exception("Nie udało się zweryfikować tytułu")
