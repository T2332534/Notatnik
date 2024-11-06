import tkinter as tk
from tkinter import ttk, messagebox
from user_managment import ManageAccountWindow

class AdminWindow(tk.Toplevel):
    """
    Klasa reprezentująca okno panelu administratora, umożliwiająca zarządzanie użytkownikami.
    """

    def __init__(self, master, db, admin_id):
        """
        Inicjalizuje okno panelu administratora.

        Parametry:
            master (tk.Tk): Główne okno aplikacji.
            db (Database): Obiekt bazy danych.
            admin_id (int): ID administratora.
        """
        try:
            super().__init__(master)
            self.db = db
            self.admin_id = admin_id

            self.title("Panel Administratora")
            window_width = 400
            window_height = 500
            self.geometry(f"{window_width}x{window_height}")
            self.minsize(window_width, window_height)

            ttk.Label(self, text="Lista użytkowników:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
            
            self.user_list_frame = ttk.Frame(self)
            self.user_list_frame.pack(padx=10, pady=10, fill="both", expand=True)
            
            self.user_listbox = tk.Listbox(self.user_list_frame, selectmode=tk.SINGLE)
            self.user_listbox.pack(side="left", fill="both", expand=True)
            
            scrollbar = ttk.Scrollbar(self.user_list_frame, orient="vertical", command=self.user_listbox.yview)
            scrollbar.pack(side="right", fill="y")
            self.user_listbox.config(yscrollcommand=scrollbar.set)

            self.load_user_list()

            ttk.Button(self, text="Zarządzaj kontem", command=self.open_manage_account).pack(pady=10)
        except Exception as e:
            raise Exception("Błąd podczas inicjalizacji okna administratora.") from e

    def load_user_list(self):
        """
        Wczytuje listę zwykłych użytkowników z bazy danych i wyświetla w Listboxie.
        """
        self.user_listbox.delete(0, tk.END)  
        try:
            users = self.db.get_all_users()
            for user in users:
                self.user_listbox.insert(tk.END, f"{user['login']} (ID: {user['user_id']})")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wczytać listy użytkowników: {str(e)}")

    def open_manage_account(self):
        """
        Otwiera formularz zarządzania kontem dla wybranego użytkownika.
        
        Zgłasza ostrzeżenie, jeśli użytkownik nie jest wybrany z listy.
        """
        try:
            selected_user = self.user_listbox.get(self.user_listbox.curselection())
            user_id = int(selected_user.split("ID: ")[1].strip(")"))
            ManageAccountWindow(self, self.db, user_id, self.admin_id) 
        except tk.TclError:
            messagebox.showwarning("Ostrzeżenie", "Wybierz użytkownika z listy, aby zarządzać jego kontem.")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas otwierania formularza zarządzania kontem: {str(e)}")
