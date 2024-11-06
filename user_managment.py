import tkinter as tk
from tkinter import ttk, messagebox
import bcrypt
import re

class ManageAccountWindow(tk.Toplevel):
    """
    Klasa reprezentująca okno edycji konta. Pozwala użytkownikowi na zmianę loginu, hasła oraz na usunięcie profilu.
    """
    def __init__(self, master, db, user_id, admin_id=False):
        """
        Inicjalizuje okno zarządzania kontem użytkownika.
        
        Parametry:
            master (tk.Tk): Główne okno aplikacji.
            db (Database): Obiekt bazy danych.
            user_id (int): ID użytkownika.
            admin_id (bool): Czy to konto administratora. Domyślnie False.
        """
        try:
            super().__init__(master)
            self.db = db
            self.user_id = user_id
            self.admin_id = admin_id

            self.title("Zarządzanie kontem")

            if self.admin_id:
                window_width = 400
                window_height = 600
            else:   
                window_width = 400
                window_height = 500
            self.geometry(f"{window_width}x{window_height}")
            self.minsize(window_width, window_height)

            self.info_frame = ttk.Frame(self)
            self.info_frame.pack(pady=10, fill='x')

            self.change_user_data_frame = ttk.Frame(self)
            self.change_user_data_frame.pack(pady=10, fill='x')

            self.delete_account_frame = ttk.Frame(self)
            self.delete_account_frame.pack(pady=10, fill='x')

            self.change_form("login")

            if self.admin_id:
                self.title("Zarządzanie kontem (admin)")
                self.admin_controls_frame = ttk.Frame(self)
                self.admin_controls_frame.pack(pady=10, fill='x') 
                self.display_admin_controls()

            self.display_account_info()

            ttk.Label(self.delete_account_frame, text="Usuń konto:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
            ttk.Label(self.delete_account_frame, text="Podaj hasło administratora:" if self.admin_id else "Podaj hasło:").pack(anchor="w", padx=10, pady=(10, 0))
            self.delete_password_entry = ttk.Entry(self.delete_account_frame, show="*")
            self.delete_password_entry.pack(fill='x', padx=10, pady=(0, 5))

            self.delete_account_button = ttk.Button(self.delete_account_frame, text="Usuń konto", command=self.delete_account)
            self.delete_account_button.pack(pady=5, padx=10)
        except Exception as e:
            raise Exception("Błąd podczas inicjalizacji okna zarządzania kontem.") from e

    def change_form(self, form_type):
        """
        Zmieniamy widok formularza na zmianę loginu lub hasła.
        
        Parametry:
            form_type (str): Typ formularza do wyświetlenia - "login" lub "password".
        """
        try:
            for widget in self.change_user_data_frame.winfo_children():
                widget.destroy()

            if form_type == "login":
                ttk.Label(self.change_user_data_frame, text="Zmień login:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
                ttk.Label(self.change_user_data_frame, text="Nowy login:").pack(anchor="w", padx=10)
                self.new_login_entry = ttk.Entry(self.change_user_data_frame)
                self.new_login_entry.pack(fill='x', padx=10, pady=(0, 5))
                ttk.Label(self.change_user_data_frame, text="Hasło administratora:" if self.admin_id else "Aktualne hasło:").pack(anchor="w", padx=10)
                self.current_password_entry = ttk.Entry(self.change_user_data_frame, show="*")
                self.current_password_entry.pack(fill='x', padx=10, pady=(0, 5))
                ttk.Button(self.change_user_data_frame, text="Zapisz nowy login", command=self.update_login).pack(pady=5, padx=10)
                ttk.Button(self.change_user_data_frame, text="Przełącz na zmianę hasła", command=lambda: self.change_form("password")).pack(pady=5, padx=10)

            elif form_type == "password":
                ttk.Label(self.change_user_data_frame, text="Zmień hasło:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
                ttk.Label(self.change_user_data_frame, text="Hasło administratora:" if self.admin_id else "Aktualne hasło:").pack(anchor="w", padx=10)
                self.current_password_entry = ttk.Entry(self.change_user_data_frame, show="*")
                self.current_password_entry.pack(fill='x', padx=10, pady=(0, 5))
                ttk.Label(self.change_user_data_frame, text="Nowe hasło:").pack(anchor="w", padx=10)
                self.new_password_entry = ttk.Entry(self.change_user_data_frame, show="*")
                self.new_password_entry.pack(fill='x', padx=10, pady=(0, 5))
                ttk.Label(self.change_user_data_frame, text="Potwierdź nowe hasło:").pack(anchor="w", padx=10)
                self.confirm_password_entry = ttk.Entry(self.change_user_data_frame, show="*")
                self.confirm_password_entry.pack(fill='x', padx=10, pady=(0, 5))
                ttk.Button(self.change_user_data_frame, text="Zapisz nowe hasło", command=self.update_password).pack(pady=5, padx=10)
                ttk.Button(self.change_user_data_frame, text="Przełącz na zmianę loginu", command=lambda: self.change_form("login")).pack(pady=5, padx=10)
        except Exception as e:
            raise Exception("Błąd podczas zmiany formularza.") from e

    def display_admin_controls(self):
        """
        Wyświetla kontrolki administratora, w tym opcję nadania uprawnień admina.
        """
        try:
            ttk.Label(self.admin_controls_frame, text="Uprawnienia administratora:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
            ttk.Label(self.admin_controls_frame, text="Hasło administratora:").pack(anchor="w", padx=10)
            self.admin_password_entry = ttk.Entry(self.admin_controls_frame, show="*")
            self.admin_password_entry.pack(fill='x', padx=10, pady=(0, 5))
            ttk.Button(self.admin_controls_frame, text="Nadaj status administratora", command=self.update_admin_status).pack(pady=5, padx=10)
        except Exception as e:
            raise Exception("Błąd podczas wyświetlania opcji administratora.") from e

    def update_admin_status(self):
        """
        Aktualizuje status administratora dla użytkownika.
        """
        try:
            current_password = self.admin_password_entry.get()
            login = self.db.get_login(self.admin_id)
            if not self.db.verify_user(login, current_password):
                messagebox.showwarning("Ostrzeżenie", "Nieprawidłowe hasło administratora.")
                return

            if self.db.set_admin_status(self.user_id):
                status_message = "Uprawnienia administratora zostały zaktualizowane."
                messagebox.showinfo("Sukces", status_message)
                self.destroy()
            else:
                messagebox.showerror("Błąd", "Nie udało się zaktualizować uprawnień.")
        except Exception as e:
            raise Exception("Błąd podczas aktualizacji statusu administratora.") from e

    def update_login(self):
        """
        Aktualizuje login użytkownika po przeprowadzeniu walidacji hasła.
        """
        try:
            new_login = self.new_login_entry.get()
            current_password = self.current_password_entry.get()

            if self.admin_id:
                login = self.db.get_login(self.admin_id)
                if not self.db.verify_user(login, current_password):
                    messagebox.showwarning("Ostrzeżenie", "Nieprawidłowe hasło administratora.")
                    return
            else:
                login = self.db.get_login(self.user_id)
                if not self.db.verify_user(login, current_password):
                    messagebox.showwarning("Ostrzeżenie", "Nieprawidłowe hasło użytkownika.")
                    return

            if self.db.update_login(self.user_id, new_login):
                messagebox.showinfo("Sukces", "Login został zaktualizowany.")
                self.display_account_info()
            else:
                messagebox.showerror("Błąd", "Nie udało się zaktualizować loginu.")
        except Exception as e:
            raise Exception("Błąd podczas aktualizacji loginu.") from e

    def display_account_info(self):
        """
        Wyświetla informacje o koncie użytkownika, takie jak login i rola.
        """
        try:
            for widget in self.info_frame.winfo_children():
                widget.destroy()
            ttk.Label(self.info_frame, text="Informacje o koncie:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
            user_login = self.db.get_login(self.user_id)
            ttk.Label(self.info_frame, text=f"Login: {user_login}").pack(anchor="w", padx=10, pady=(5, 0))
            user_role = "Administrator" if self.db.is_admin(self.user_id) else "Użytkownik"
            ttk.Label(self.info_frame, text=f"Rola: {user_role}").pack(anchor="w", padx=10, pady=(5, 0))
        except Exception as e:
            raise Exception("Błąd podczas wyświetlania informacji o koncie.") from e

    def check_password_strength(self, password):
        """
        Sprawdza, czy hasło jest wystarczająco silne i zwraca komunikaty o błędach.
        
        Parametry:
            password (str): Hasło do sprawdzenia.
        
        Zwraca:
            tuple: (bool, list) - Czy hasło jest silne oraz lista komunikatów o błędach.
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
            raise Exception("Błąd podczas sprawdzania siły hasła.") from e

    def update_password(self):
        """
        Aktualizuje hasło użytkownika po przeprowadzeniu walidacji.
        """
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        current_password = self.current_password_entry.get()

        if new_password != confirm_password:
            messagebox.showwarning("Ostrzeżenie", "Hasła się nie zgadzają.")
            return

        if self.admin_id:
            login = self.db.get_login(self.admin_id)
            if not self.db.verify_user(login,current_password):
                messagebox.showwarning("Ostrzeżenie", "Nieprawidłowe hasło administratora.")
                return
        else:
            login = self.db.get_login(self.user_id)
            if not self.db.verify_user(login, current_password):
                messagebox.showwarning("Ostrzeżenie", "Nieprawidłowe hasło użytkownika.")
                return

        hashed_password = bcrypt.hashpw(current_password.encode('utf-8'), bcrypt.gensalt())
        if self.db.update_password(self.user_id, hashed_password):
            messagebox.showinfo("Sukces", "Hasło zostało zaktualizowane.")
        else:
            messagebox.showerror("Błąd", "Nie udało się zaktualizować hasła.")
            
    def delete_account(self):
        """Usuwa konto użytkownika."""
        try:
            if self.admin_id:
                current_password = self.delete_password_entry.get()
                login = self.db.get_login(self.admin_id)
                if not self.db.verify_user(login,current_password):
                    messagebox.showwarning("Ostrzeżenie", "Nieprawidłowe hasło administratora.")
                    return
            else:
                current_password = self.delete_password_entry.get()
                login = self.db.get_login(self.user_id)
                if not self.db.verify_user(login, current_password):
                    messagebox.showwarning("Ostrzeżenie", "Nieprawidłowe hasło użytkownika.")
                    return
            
            confirmation = messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć swoje konto?")
            login = self.db.get_login(self.user_id)
            
            if confirmation:
                if self.db.delete_user(self.user_id):
                    if self.admin_id:
                        messagebox.showinfo("Konto usunięte", f"Konto użytkownika {login} zostało usunięte.")
                        self.master.load_user_list()
                        self.destroy()
                    else:
                        messagebox.showinfo("Konto usunięte", "Twoje konto zostało usunięte.")    
                        self.destroy()
                else:
                    messagebox.showerror("Błąd", "Nie udało się usunąć konta.")
        except Exception as e:
            raise Exception("Błąd podczas usuwania konta.") from e

