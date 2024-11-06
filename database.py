import mysql.connector
import bcrypt
import logging

from tkinter import messagebox

class Database:
    def __init__(self, username, password, host, database):
        """
        Inicjalizacja obiektu Database i nawiązanie połączenia z bazą danych MySQL.
        Utworzenie bazy danych "notatnik" oraz tabel "notes" i "users", jeśli nie istnieją.

        :param username: Nazwa użytkownika bazy danych
        :param password: Hasło użytkownika bazy danych
        :param host: Adres hosta bazy danych
        :param database: Nazwa bazy danych do użycia
        """
        try:
            self.connection = mysql.connector.connect(
                user=username,
                password=password,
                host=host
            )
            self.cursor = self.connection.cursor()
        except mysql.connector.Error as err:
            raise Exception(f"Błąd podczas łączenia się z bazą danych: {err}")

        try:
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
            self.cursor.execute(f"USE {database}")

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    text TEXT,
                    name VARCHAR(255)
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    login VARCHAR(255),
                    password VARCHAR(255),
                    role ENUM('user', 'admin') DEFAULT 'user'
                )
            """)

            self.connection.commit()
        except mysql.connector.Error as err:
            raise Exception(f"Błąd podczas tworzenia tabel: {err}")

    # ============================
    # Funkcje związane z użytkownikami
    # ============================

    def add_user(self, login, password):
        """
        Dodanie nowego użytkownika do tabeli "users".

        :param login: Login użytkownika
        :param password: Hasło użytkownika
        """
        try:
            self.cursor.execute("""
                INSERT INTO users (login, password)
                VALUES (%s, %s)
            """, (login, password))
            self.connection.commit()
        except mysql.connector.Error as err:
            raise Exception(f"Błąd podczas dodawania użytkownika: {err}")

    def verify_user(self, login, password):
        """
        Sprawdza, czy użytkownik z podanym loginem i hasłem istnieje w bazie danych i zwraca jego ID.

        :param login: login użytkownika
        :param password: hasło użytkownika
        :return: user_id, jeśli użytkownik istnieje i hasło jest poprawne, False w przeciwnym razie
        """
        try:
            self.cursor.execute("SELECT id, password FROM users WHERE login = %s", (login,))
            result = self.cursor.fetchone()

            if result:
                user_id, stored_password = result
                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    return user_id
            return False
        except mysql.connector.Error as err:
            raise Exception(f"Błąd podczas weryfikacji użytkownika: {err}")

    def login_exists(self, login):
        """
        Sprawdzenie, czy użytkownik już istnieje w bazie danych.

        :param login: Login użytkownika do sprawdzenia
        :return: True jeśli użytkownik istnieje, False w przeciwnym razie
        """
        try:
            self.cursor.execute("SELECT 1 FROM users WHERE login = %s", (login,))
            return self.cursor.fetchone() is not None
        except mysql.connector.Error as err:
            raise Exception(f"Błąd podczas sprawdzania istnienia loginu: {err}")

    def get_all_users(self):
        """
        Pobiera listę wszystkich użytkowników wraz z ich ID i loginem.

        :return: Lista słowników z kluczami 'user_id' i 'login' lub lista krotek.
        """
        try:
            self.cursor.execute('SELECT id, login FROM users WHERE role = "user"')
            users = [{"user_id": row[0], "login": row[1]} for row in self.cursor.fetchall()]
            return users
        except mysql.connector.Error as err:
            raise Exception(f"Błąd podczas pobierania listy użytkowników: {err}")

    def set_admin_status(self, user_id):
        """
        Nadaje lub usuwa uprawnienia administratora dla użytkownika.

        :param user_id: ID użytkownika
        :return: True, jeśli operacja zakończyła się powodzeniem, False w przeciwnym razie
        """
        try:
            query = "UPDATE users SET role = %s WHERE id = %s"
            self.cursor.execute(query, ("admin", user_id))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except mysql.connector.Error as err:
            raise Exception(f"Błąd podczas nadawania uprawnień administratora: {err}")

    def update_password(self, user_id, new_password):
        """
        Aktualizacja hasła użytkownika.

        :param user_id: ID użytkownika
        :param new_password: Nowe, zaszyfrowane hasło
        :return: True, jeśli operacja zakończyła się powodzeniem; False w przeciwnym razie
        """
        try:
            self.cursor.execute("UPDATE users SET password = %s WHERE id = %s", (new_password, user_id))
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            raise Exception(f"Błąd podczas aktualizacji hasła: {err}")

    def update_login(self, user_id, new_login):
        """
        Aktualizuje login użytkownika.

        :param user_id: ID użytkownika
        :param new_login: Nowy login użytkownika
        :return: True, jeśli operacja zakończyła się powodzeniem
        """
        try:
            self.cursor.execute("UPDATE users SET login=%s WHERE id=%s", (new_login, user_id))
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            raise Exception(f"Błąd podczas aktualizacji loginu: {err}")

    def delete_user(self, user_id):
        """
        Usunięcie użytkownika z bazy danych.

        :param user_id: ID użytkownika
        :return: True, jeśli operacja zakończyła się powodzeniem; False w przeciwnym razie
        """
        try:
            self.cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            raise Exception(f"Błąd podczas usuwania użytkownika: {err}")

    def get_login(self, user_id):
        """
        Pobranie loginu użytkownika na podstawie jego ID.

        :param user_id: ID użytkownika
        :return: Login użytkownika lub False, jeśli nie znaleziono
        """
        try:
            self.cursor.execute("SELECT login FROM users WHERE id = %s", (user_id,))
            result = self.cursor.fetchone()
            return result[0] if result else False
        except mysql.connector.Error as err:
            raise Exception(f"Błąd podczas pobierania loginu: {err}")

    def is_admin(self, user_id):
        """
        Sprawdza, czy użytkownik o danym user_id jest administratorem.

        :param user_id: ID użytkownika
        :return: True, jeśli użytkownik jest administratorem, False w przeciwnym razie
        """
        try:
            self.cursor.execute("SELECT role FROM users WHERE id = %s", (user_id,))
            result = self.cursor.fetchone()
            return result[0] == 'admin' if result else False
        except mysql.connector.Error as err:
            raise Exception(f"Błąd podczas sprawdzania roli użytkownika: {err}")

    # ============================
    # Funkcje związane z notatkami
    # ============================

    def add_note(self, user_id, text, name):
        """
        Dodanie nowej notatki do tabeli "notes".

        :param user_id: ID użytkownika, który dodał notatkę
        :param text: Treść notatki
        :param name: Nazwa notatki
        :return: True w przypadku powodzenia, False w przypadku błędu
        """
        try:
            self.cursor.execute("""
                INSERT INTO notes (user_id, text, name)
                VALUES (%s, %s, %s)
            """, (user_id, text, name))
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            raise Exception(f"Błąd podczas dodawania notatki: {err}")

    def update_note(self, user_id, original_name, new_text, new_name):
        """
        Aktualizuje istniejącą notatkę w tabeli "notes".

        :param user_id: ID użytkownika, który edytuje notatkę
        :param original_name: Oryginalna nazwa notatki
        :param new_text: Nowa treść notatki
        :param new_name: Nowa nazwa notatki
        :return: True w przypadku powodzenia, False w przypadku błędu
        """
        try:
            self.cursor.execute("""
                UPDATE notes
                SET text = %s, name = %s
                WHERE user_id = %s AND name = %s
            """, (new_text, new_name, user_id, original_name))
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            raise Exception(f"Błąd podczas aktualizacji notatki: {err}")

    def note_name_exists(self, name):
        """
        Sprawdzenie, czy notatka o danej nazwie istnieje w bazie danych.

        :param name: Nazwa notatki do sprawdzenia
        :return: True jeśli notatka istnieje, False w przeciwnym razie
        """
        try:
            self.cursor.execute("SELECT 1 FROM notes WHERE name = %s", (name,))
            return self.cursor.fetchone() is not None
        except mysql.connector.Error as err:
            raise Exception(f"Błąd podczas sprawdzania istnienia notatki: {err}")

    def delete_note(self, note_title):
        """
        Usuwa notatkę z bazy danych.

        :param note_title: Tytuł notatki do usunięcia
        :return: True jeśli usunięcie się powiodło, False w przeciwnym razie
        """
        try:
            self.cursor.execute("DELETE FROM notes WHERE name = %s", (note_title,))
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            raise Exception(f"Błąd podczas usuwania notatki: {err}")

    def get_note_names(self, user_id):
        """
        Pobranie nazw notatek dla danego użytkownika.

        :param user_id: ID użytkownika
        :return: Lista nazw notatek
        """
        try:
            if self.is_admin(user_id):
                self.cursor.execute("SELECT name FROM notes")
            else:
                self.cursor.execute("SELECT name FROM notes WHERE user_id = %s", (user_id,))
            return [row[0] for row in self.cursor.fetchall()]
        except mysql.connector.Error as err:
            raise Exception(f"Błąd podczas pobierania nazw notatek: {err}")

    def get_note_content(self, user_id, note_name):
        """
        Pobiera treść notatki na podstawie user_id i nazwy notatki.
        Administratorzy mogą pobierać notatki wszystkich użytkowników.

        :param user_id: ID użytkownika
        :param note_name: Nazwa notatki
        :return: Treść notatki lub None, jeśli nie znaleziono
        """
        try:
            if self.is_admin(user_id):
                query = "SELECT text FROM notes WHERE name = %s"
                self.cursor.execute(query, (note_name,))
            else:
                query = "SELECT text FROM notes WHERE user_id = %s AND name = %s"
                self.cursor.execute(query, (user_id, note_name))

            result = self.cursor.fetchall()
            return result[0][0] if result else None
        except mysql.connector.Error as err:
            raise Exception(f"Błąd podczas pobierania treści notatki: {err}")

    # ============================
    # Funkcje pomocnicze
    # ============================

    def clear_notes(self):
        """
        Czyszczenie tabeli notatek.
        """
        try:
            self.cursor.execute("TRUNCATE TABLE notes")
            self.connection.commit()
        except mysql.connector.Error as err:
            raise Exception(f"Błąd podczas czyszczenia tabeli notatek: {err}")

    def __del__(self):
        """
        Zamknięcie połączenia z bazą danych (jeśli istnieje) przy usuwaniu obiektu.
        """
        if hasattr(self, 'connection'):
            self.connection.close()
