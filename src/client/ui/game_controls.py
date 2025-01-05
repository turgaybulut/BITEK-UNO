import tkinter as tk
from tkinter import messagebox
import random


class GameControls:
    @staticmethod
    def validate_room_code(root, code, callback):
        if code.isdigit() and len(code) == 4:
            callback(code)
        else:
            messagebox.showerror("Error", "Invalid room code!")

    @staticmethod
    def create_new_room(callback):
        room_code = str(random.randint(1000, 9999))
        callback(room_code)
