import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from tkinter import messagebox
import bcrypt
from database import Database
from notes import Notes
import re

class LoginWindow:
    def __init__(self, root, username, password, host, database):
        """Inicjalizuje okno logowania oraz łączy się z bazą danych.

        Parametry:
            root (tk.Tk): Główne okno aplikacji.
            username (str): Nazwa użytkownika do połączenia z bazą danych.
            password (str): Hasło użytkownika do połączenia z bazą danych.
            host (str): Adres hosta bazy danych.
            database (str): Nazwa bazy danych.
        """
        self.root = root
        self.root.geometry("300x250")
        self.is_logged_in = False
        self.user_id = None

        try:
            self.db = Database(username, password, host, database)
        except Exception as err:
            self.major_error(err)
            return

        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill="both", expand=True)

        self.change_form("1")

    def change_form(self, form_type):
        """Zmienia widok formularza logowania lub rejestracji.

        Parametry:
            form_type (str): Typ formularza ("1" dla logowania, "2" dla rejestracji).
        """
        try:
            for widget in self.main_frame.winfo_children():
                widget.destroy()

            if form_type == "1":
                self.root.title("Okno logowania")
                self.form_label = ttk.Label(self.main_frame, text="Logowanie", font=("Helvetica", 16))
                self.form_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

                ttk.Label(self.main_frame, text="Login:").grid(row=1, column=0, padx=5, pady=5)
                self.username_entry = ttk.Entry(self.main_frame, width=25)
                self.username_entry.grid(row=1, column=1, padx=5, pady=5)

                ttk.Label(self.main_frame, text="Hasło:").grid(row=2, column=0, padx=5, pady=5)
                self.password_entry = ttk.Entry(self.main_frame, width=25, show="*")
                self.password_entry.grid(row=2, column=1, padx=5, pady=5)

                ttk.Button(self.main_frame, text="Zaloguj", command=self.login_user).grid(row=3, column=0, columnspan=2, padx=5, pady=5)
                ttk.Button(self.main_frame, text="Zarejestruj się", command=lambda: self.change_form("2")).grid(row=4, column=0, columnspan=2, padx=5, pady=5)

            elif form_type == "2":
                self.root.title("Okno rejestracji")
                self.form_label = ttk.Label(self.main_frame, text="Rejestracja", font=("Helvetica", 16))
                self.form_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

                ttk.Label(self.main_frame, text="Login:").grid(row=1, column=0, padx=5, pady=5)
                self.username_entry = ttk.Entry(self.main_frame, width=25)
                self.username_entry.grid(row=1, column=1, padx=5, pady=5)

                ttk.Label(self.main_frame, text="Hasło:").grid(row=2, column=0, padx=5, pady=5)
                self.password_entry = ttk.Entry(self.main_frame, width=25, show="*")
                self.password_entry.grid(row=2, column=1, padx=5, pady=5)

                ttk.Label(self.main_frame, text="Potwierdź hasło:").grid(row=3, column=0, padx=5, pady=5)
                self.confirm_password_entry = ttk.Entry(self.main_frame, width=25, show="*")
                self.confirm_password_entry.grid(row=3, column=1, padx=5, pady=5)

                ttk.Button(self.main_frame, text="Zarejestruj", command=self.register_user).grid(row=4, column=0, columnspan=2, padx=5, pady=5)
                ttk.Button(self.main_frame, text="Zaloguj się", command=lambda: self.change_form("1")).grid(row=5, column=0, columnspan=2, padx=5, pady=5)
            else:
                messagebox.showinfo("Błąd", "Wystąpił błąd w kodzie aplikacji!")
        except Exception as e:
            self.major_error(e)

    def check_password_strength(self, password):
        """Sprawdza, czy hasło jest wystarczająco silne i zwraca komunikaty o błędach.

        Parametry:
            password (str): Hasło do sprawdzenia.

        Returns:
            tuple: (is_strong: bool, messages: list) - True, jeśli hasło jest silne, False w przeciwnym razie.
        """
        try:
            messages = []
            
            if len(password) < 8:
                messages.append("Hasło musi mieć co najmniej 8 znaków.")
            if not re.search("[a-z]", password):
                messages.append("Hasło musi zawierać co najmniej jedną małą literę.")
            if not re.search("[A-Z]", password):  
                messages.append("Hasło musi zawierać co najmniej jedną dużą literę.")
            if not re.search("[0-9]", password):  
                messages.append("Hasło musi zawierać co najmniej jedną cyfrę.")
            if not re.search("[@#$%^&+=!]", password): 
                messages.append("Hasło musi zawierać co najmniej jeden znak specjalny.")
            
            is_strong = len(messages) == 0
            return is_strong, messages
        except Exception as e:
            self.major_error(e)

    def register_user(self):
        """Funkcja rejestrująca nowego użytkownika."""
        try:
            login = self.username_entry.get()
            password = self.password_entry.get()
            confirm_password = self.confirm_password_entry.get()

            if not login:
                messagebox.showerror("Błąd rejestracji", "Login nie może być pusty.")
                return
            if not password:
                messagebox.showerror("Błąd rejestracji", "Hasło nie może być puste.")
                return

            if self.db.login_exists(login):
                messagebox.showerror("Błąd rejestracji", "Ten login jest już zajęty. Wybierz inny.")
                return

            if password != confirm_password:
                messagebox.showerror("Błąd rejestracji", "Hasła nie są takie same.")
                return

            is_strong, messages = self.check_password_strength(password)
            if not is_strong:
                messagebox.showerror("Błąd rejestracji", "Hasło jest słabe:\n" + "\n".join(messages))
                return

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            self.db.add_user(login, hashed_password.decode('utf-8'))
            messagebox.showinfo("Rejestracja", "Rejestracja zakończona sukcesem!")
            self.change_form("1")
        except Exception as e:
            self.major_error(e)

    def login_user(self):
        """Funkcja logująca użytkownika."""
        try:
            username = self.username_entry.get()
            password = self.password_entry.get()

            self.user_id = self.db.verify_user(username, password)
            if self.user_id:
                messagebox.showinfo("Zalogowano", "Logowanie udane!")
                self.is_logged_in = True
                self.root.destroy() 
            else:
                messagebox.showerror("Błąd", "Nieprawidłowy login lub hasło!")
        except Exception as e:
            self.major_error(e)

    def clear_window(self):
        """Czyści okno główne z wprowadzonych danych."""
        try:
            for widget in self.main_frame.winfo_children():
                widget.destroy()
            self.username_entry = None
            self.password_entry = None
            self.confirm_password_entry = None
        except Exception as e:
            self.major_error(e)

    def major_error(self, error):
        """Wyświetla komunikat o poważnym błędzie i zamyka aplikację.

        Parametry:
            error (Exception): Obiekt błędu do wyświetlenia.
        """
        try:
            messagebox.showerror("Błąd krytyczny", str(error))
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Błąd podczas obsługi błędu krytycznego", str(e))
            self.root.destroy()