from tkinter import Tk
from tkinter import ttk
from ttkthemes import ThemedTk
from configparser import ConfigParser
import os

from login import LoginWindow
from notes import Notes

def load_config():
    try:
        config = ConfigParser()
        exe_dir = os.path.dirname(os.path.abspath(__file__)) 
        config_path = os.path.join(exe_dir, "config.ini")
        
        with open(config_path, "r", encoding="utf-8") as config_file:
            config.read_file(config_file)
        return config
    except Exception as e:
        raise Exception("Nie udało się wczytać pliku konfiguracyjnego") from e
        
def login():
    config = load_config()
    
    root = ThemedTk(theme="arc")
    login_window = LoginWindow(
        root,
        username=config["DATABASE"]["username"],
        password=config["DATABASE"]["password"],
        host=config["DATABASE"]["host"],
        database=config["DATABASE"]["database"]
    )   
    root.mainloop()
    if login_window.is_logged_in:
        note(login_window.user_id)
        
def note(user_id):
    config = load_config()
    root = ThemedTk(theme="arc")  
    notes_window = Notes(
        root,
        user_id,
        config["DATABASE"]["username"],
        config["DATABASE"]["password"],
        config["DATABASE"]["host"],
        config["DATABASE"]["database"]
    )    
    root.mainloop()
    if not notes_window.logged_in:
        login()
        
if __name__ == "__main__":
    login()