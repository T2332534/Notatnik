import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
import mysql.connector

from database import Database
from add_note_window import AddNoteWindow
from edit_note_window import EditNoteWindow 
from user_managment import ManageAccountWindow 
from admin_window import AdminWindow

class Notes:
    def __init__(self, root, user_id, username, password, host, database):
        
        """
        Inicjalizuje główne okno aplikacji Notatki oraz łączy się z bazą danych.

        Parametry:
        root (Tk): Główne okno aplikacji Tkinter.
        user_id (int): ID aktualnie zalogowanego użytkownika.
        username (str): Nazwa użytkownika do połączenia z bazą danych.
        password (str): Hasło użytkownika do połączenia z bazą danych.
        host (str): Host, na którym znajduje się baza danych.
        database (str): Nazwa bazy danych do użycia.

        Działania:
        - Ustawia tytuł i rozmiar okna.
        - Ustala minimalny rozmiar okna.
        - Inicjalizuje połączenie z bazą danych, a w przypadku błędu wyświetla komunikat o błędzie i zamyka aplikację.
        - Ustala status administratora dla użytkownika.
        - Tworzy ramkę dla menu aplikacji oraz ustawia siatkę dla rozmieszczenia elementów interfejsu.
        
        W przypadku pomyślnego połączenia z bazą danych, wywołuje metodę `initialize_interface` w celu skonfigurowania interfejsu użytkownika.
        """
        
        try:
            self.root = root
            self.root.title("Notatki")
            window_width = 800
            window_height = 600
            self.root.geometry(f"{window_width}x{window_height}")
            self.root.minsize(window_width, window_height)
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            self.user_id = user_id
            if self.user_id:
                self.logged_in = True

            self.db = Database(username, password, host, database)

            self.add_note_window = None
            self.edit_note_window = None
            self.manage_account_window = None
            self.admin_window = None


            self.is_admin = self.db.is_admin(self.user_id)
            
            self.filter_by_title_var = tk.BooleanVar(value=True)
            self.filter_by_content_var = tk.BooleanVar(value=True) 
            
            
            self.menu_frame = ttk.Frame(self.root, padding="10")
            self.menu_frame.pack(pady=10, fill='x')
            
            self.root.grid_columnconfigure(0, weight=1)
            self.root.grid_rowconfigure(0, weight=1)

            self.initialize_interface()
        except Exception as err:
            self.major_error(err)
            return

    # ============================
    # Funkcje interface'u
    # ============================


    def initialize_interface(self):
        """Tworzy elementy interfejsu użytkownika i ustawia ich rozmieszczenie."""
        
        try:
            self.refresh_user_data()

            text_frame = ttk.Frame(self.root)
            text_frame.pack(pady=2,fill='x')

            self.note_content = tk.Text(text_frame, wrap="word", width=70, height=80, state="disabled")
            self.note_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            self.scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.note_content.yview)
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            self.note_content['yscrollcommand'] = self.scrollbar.set

                
            self.add_admin_privileges()
                
            self.combo = ttk.Combobox(self.menu_frame)
            self.combo.grid(row=1, column=0)

            self.combo['values'] = ["Wybierz notatkę"]
            self.combo.current(0)
            self.combo.bind("<<ComboboxSelected>>", self.display_note_content)

            ttk.Label(self.menu_frame, text="Słowo kluczowe: ").grid(row=0, column=1)
            self.key_word = ttk.Entry(self.menu_frame, width=25)
            self.key_word.grid(row=1, column=1)
            self.key_word.bind("<KeyRelease>", self.filter_notes)

            def update_filters(*args):
                self.filter_notes()

            self.filter_by_title_var.trace_add("write", update_filters)
            self.filter_by_content_var.trace_add("write", update_filters)

            ttk.Checkbutton(self.menu_frame, text="Filtruj po nazwie notatki", variable=self.filter_by_title_var).grid(row=2, column=1, sticky="w")
        
            ttk.Checkbutton(self.menu_frame, text="Filtruj po zawartości notatki", variable=self.filter_by_content_var).grid(row=3, column=1, sticky="w")

            ttk.Button(self.menu_frame, text="Dodaj notatkę", command=self.add_note).grid(row=1, column=2, padx=5, pady=5)
            
            ttk.Button(self.menu_frame, text="Edytuj wybraną notatkę", command=self.edit_note).grid(row=1, column=3, padx=5, pady=5)
            manage_account_button = ttk.Button(self.menu_frame, text="Zarządzaj kontem", command=self.manage_account)
            manage_account_button.grid(row=1, column=4, padx=5, pady=5)

            manage_account_button = ttk.Button(self.menu_frame, text="Wyloguj się", command=self.log_out)
            manage_account_button.grid(row=2, column=0, padx=5, pady=5)

            self.refresh_notes()
            
        except Exception as err:
            self.major_error(err)
            return

    def display_note_content(self,event=None):
        """Wyświetla treść wybranej notatki. Jeśli nie ma wybranej notatki,
           użytkownik otrzymuje odpowiedni komunikat informujący o braku treści.
        """
        try:
            self.note_content.config(state="normal")
            self.note_content.delete("1.0", tk.END)

            if len(self.combo['values']) > 1:
                
                selected_note = self.combo.get()
                
                if selected_note != "Wybierz notatkę":
                    content = self.db.get_note_content(self.user_id, selected_note)
                    self.note_content.insert(tk.END, content or "Brak treści dla wybranej notatki.")
                else:
                    self.note_content.insert(tk.END, "Wybierz notatkę z listy.")
            else:
                if self.key_word.get():
                    self.note_content.insert(tk.END, "Brak notatek dla wybranego klucza.")
                else:
                    self.note_content.insert(tk.END, "Brak notatek.")
            
            self.note_content.config(state="disabled")
        except Exception as err:
            self.major_error(err)
            return
        
    def refresh_user_data(self,event=None):
        """Odświeża wyświetlane informacje o użytkowniku, takie jak login i rola."""
        try:
            login = self.db.get_login(self.user_id)
            if login:
                formatted_login = self.format_username(login)
                admin_label = " (admin)" if self.is_admin else ""
                self.info_label = ttk.Label(self.menu_frame, text=f"Użytkownik: {formatted_login}{admin_label}", font=("Arial", 12, "bold") ).grid(row=0, column=0, padx=5, pady=5)
            else:
                raise Exception(f"Wystąpił błąd połączenia z użytkownikiem (brak zwracanego loginu)")
        except Exception as err:
            self.major_error(err)
            return 
        
    def add_admin_privileges(self):
        """Sprawdza, czy użytkownik ma uprawnienia administratora i dodaje przycisk uruchamiający panel administratora."""
        try:
            if self.db.is_admin(self.user_id):
                admin_button = ttk.Button(self.menu_frame, text="Panel Administratora", command=self.admin_panel)
                admin_button.grid(row=3,column=0)
        except Exception as err:
            self.major_error(err)
            return 
    # ============================================
    # Funkcje obsługujące inne działąnia aplikacji
    # ============================================
        
        
    def refresh_notes(self, filtered_notes=None):
        """Odświeża listę notatek w interfejsie użytkownika, w tym listę filtrowanych notatek.
           Parametry:
           filtered_notes (list, opcjonalnie): Lista notatek po zastosowaniu filtru. Jeśli brak, pobiera wszystkie notatki.
        """
        
        
        try:
            if filtered_notes is None:
                tables = self.db.get_note_names(self.user_id)
            else:
                tables = filtered_notes

            if tables:
                self.combo['values'] = ["Wybierz notatkę"] + tables
                self.combo.current(0)
            else:
                self.combo['values'] = ["Brak dostępnych notatek"]
                self.combo.current(0)
        except Exception as err:
            self.major_error(err)
            return 
        
    def log_out(self):
        """Wylogowuje użytkownika i zamyka aplikację po potwierdzeniu. """
        try:
            if self.db.get_login(self.user_id):
                confirmation = messagebox.askyesno("Potwierdzenie", "Czy chcesz się wylogować?")
                if not confirmation:
                    return
            self.logged_in = False
            self.root.destroy() 
        except Exception as err:
            self.major_error(err)
            return 
        
    def filter_notes(self,event=None):
        """Filtruje notatki na podstawie słowa kluczowego i zaznaczonych filtrów."""
        try:   
            keyword = self.key_word.get().lower()
            all_notes = self.db.get_note_names(self.user_id)
            filtered_notes = []
            if not self.filter_by_title_var.get() and not self.filter_by_content_var.get():
                filtered_notes = all_notes 
            else:
                for note in all_notes:
                    title_matches = self.filter_by_title_var.get() and keyword in note.lower()
                    content_matches = self.filter_by_content_var.get() and keyword in (self.db.get_note_content(self.user_id, note) or "").lower()

                    if title_matches or content_matches:
                        filtered_notes.append(note)

            self.refresh_notes(filtered_notes)
        except Exception as err:
            self.major_error(err)
            return 
    # ====================================
    # Funkcje uruchamiające okna dodatkowe
    # ====================================
        
    def add_note(self):
        """Otwiera okno dodawania notatki, a po zamknięciu okna odświeża listę notatek."""
        try:
            if self.add_note_window is None or not self.add_note_window.winfo_exists():
                self.add_note_window = AddNoteWindow(self.root, self.db, self.user_id)
                self.add_note_window.wait_window()
                self.refresh_notes()
        except Exception as err:
            self.major_error(err)
            return 

    def edit_note(self):
        """Pozwala na edytowanie wybranej notatki. Wyświetla komunikat, jeśli nie wybrano notatki."""
        try:
            selected_note = self.combo.get()
            if selected_note != "Wybierz notatkę" and selected_note != "Brak dostępnych notatek":
                if self.edit_note_window is None or not self.edit_note_window.winfo_exists():
                    note_content = self.db.get_note_content(self.user_id, selected_note)
                    self.edit_note_window = EditNoteWindow(self.root, self.db, self.user_id, selected_note, note_content)
                    self.edit_note_window.wait_window(self.edit_note_window) 
                    self.refresh_notes()
            else:
                messagebox.showerror("Błąd", "Nie wybrano notatki do edycji")
        except Exception as err:
            self.major_error(err)
            return     
            
    def admin_panel(self):
        """Otwiera panel administratora, jeśli użytkownik ma uprawnienia."""
        try:
            if self.db.is_admin(self.user_id):
                if self.admin_window is None or not self.admin_window.winfo_exists():
                    self.admin_window = AdminWindow(self.root, self.db, self.user_id)
            else:
                raise Exception("Brak uprawnień administratora. Ten przycisk nie powinien się wyświetlać")
        except Exception as err:
            self.major_error(err)
            return 

    def manage_account(self):
        """Otwiera okno zarządzania kontem użytkownika, a po zamknięciu odświeża potrzebne dane lub wylogowuje w przypadku usunięcia konta."""
        try:
            if self.manage_account_window is None or not self.manage_account_window.winfo_exists():
                self.manage_account_window = ManageAccountWindow(self.root, self.db, self.user_id)
                self.manage_account_window.wait_window(self.manage_account_window)
                if self.db.get_login(self.user_id):
                    self.refresh_user_data()
                else:
                    self.log_out()
        except Exception as err:
            self.major_error(err)
            return 
                      
    # ============================
    # Funkcje pomocnicze
    # ============================
            
    def format_username(self,username):
        """ Formatuje nazwę użytkownika do maksymalnej długości, dodając wielokropek, jeśli jest za długa.

            Parametry:
            username (str): Nazwa użytkownika do sformatowania.
        """  
        try:
            max_length = 15 
            if len(username) > max_length:
                return username[:max_length] + "..." 
            return username
        except Exception as err:
            self.major_error(err)
            return 
        
    def on_closing(self):
        """Zamyka wszystkie dodatkowe okna, gdy główne okno jest zamykane."""
        if self.add_note_window:
            self.add_note_window.destroy()
        if self.edit_note_window:
            self.edit_note_window.destroy()
        if self.manage_account_window:
            self.manage_account_window.destroy()
        if self.admin_window:
            self.admin_window.destroy()
        self.root.destroy()  
        
    def major_error(self, error):
        if self.root:
            messagebox.showerror("Błąd: ", error or "Nieznany błąd")
            self.root.quit()
