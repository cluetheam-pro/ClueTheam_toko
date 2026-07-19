"""Alat konfigurasi komputer utama atau komputer kasir."""

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageTk

from Admin.computer_config import DEFAULT_DATABASE, save_computer_config


THEME_DIR = Path(__file__).resolve().parent / "Admin" / "Theme"
LOGO_PATH = THEME_DIR / "Clue_Theam.png"
ICON_PATH = THEME_DIR / "Clue_Theam.ico"


class SetupKomputer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Setup CLue Theam")
        self.geometry("520x440")
        self.resizable(False, False)
        self.logo_image = None
        self.window_icon = None
        ctk.set_appearance_mode("Dark")
        self.grid_columnconfigure(0, weight=1)
        self.build()
        self.after(100, self.apply_window_icon)
        self.after(600, self.apply_window_icon)

    def build(self):
        heading = ctk.CTkFrame(self, fg_color="transparent")
        heading.grid(row=0, column=0, padx=32, pady=(28, 5), sticky="ew")
        self.create_logo(heading, 54).pack(side="left")
        copy = ctk.CTkFrame(heading, fg_color="transparent")
        copy.pack(side="left", padx=14)
        ctk.CTkLabel(copy, text="Konfigurasi Komputer", font=("Segoe UI", 22, "bold")).pack(anchor="w")
        ctk.CTkLabel(copy, text="CLue Theam", font=("Segoe UI", 10, "bold"),
                     text_color="#2DD4BF").pack(anchor="w")
        ctk.CTkLabel(
            self, text="Pilih fungsi komputer yang akan digunakan.",
            font=("Segoe UI", 11), text_color="#94A3B8",
        ).grid(row=1, column=0, padx=32, pady=(0, 25), sticky="w")

        ctk.CTkButton(
            self, text="Komputer Utama", height=64, corner_radius=14,
            font=("Segoe UI", 15, "bold"), command=self.setup_primary,
        ).grid(row=2, column=0, padx=32, pady=7, sticky="ew")
        ctk.CTkLabel(
            self, text="Menyimpan database pusat dan data administrasi.",
            font=("Segoe UI", 10), text_color="#94A3B8",
        ).grid(row=3, column=0, padx=40, sticky="w")

        ctk.CTkButton(
            self, text="Komputer Kasir", height=64, corner_radius=14,
            fg_color="#1E293B", hover_color="#334155",
            font=("Segoe UI", 15, "bold"), command=self.setup_cashier,
        ).grid(row=4, column=0, padx=32, pady=(20, 7), sticky="ew")
        ctk.CTkLabel(
            self, text="Menggunakan database milik komputer utama melalui jaringan.",
            font=("Segoe UI", 10), text_color="#94A3B8",
        ).grid(row=5, column=0, padx=40, sticky="w")

    def create_logo(self, parent, size):
        if LOGO_PATH.is_file():
            try:
                self.logo_image = ctk.CTkImage(Image.open(LOGO_PATH), size=(size, size))
                return ctk.CTkLabel(parent, text="", image=self.logo_image, width=size, height=size)
            except (OSError, ValueError):
                pass
        return ctk.CTkLabel(
            parent, text="C", width=size, height=size, corner_radius=14,
            fg_color="#2DD4BF", text_color="#062A27", font=("Segoe UI", 24, "bold"),
        )

    def apply_window_icon(self):
        if not ICON_PATH.is_file():
            return
        try:
            icon_path = str(ICON_PATH.resolve())
            self.iconbitmap(default=icon_path)
            self.wm_iconbitmap(icon_path)
            self.window_icon = ImageTk.PhotoImage(Image.open(ICON_PATH).convert("RGBA"))
            self.iconphoto(True, self.window_icon)
        except (OSError, ValueError, RuntimeError):
            self.window_icon = None

    def setup_primary(self):
        save_computer_config("utama", DEFAULT_DATABASE)
        messagebox.showinfo(
            "Setup berhasil",
            f"Komputer diatur sebagai Komputer Utama.\n\nDatabase:\n{DEFAULT_DATABASE}\n\n"
            "Bagikan folder Admin melalui jaringan agar dapat dipilih komputer kasir.",
            parent=self,
        )

    def setup_cashier(self):
        path = filedialog.askopenfilename(
            parent=self, title="Pilih toko.db dari Komputer Utama",
            filetypes=[("Database CLue Theam", "toko.db"), ("SQLite database", "*.db")],
        )
        if not path:
            return
        save_computer_config("kasir", path)
        messagebox.showinfo(
            "Setup berhasil",
            f"Komputer diatur sebagai Komputer Kasir.\n\nDatabase pusat:\n{path}",
            parent=self,
        )


if __name__ == "__main__":
    SetupKomputer().mainloop()
