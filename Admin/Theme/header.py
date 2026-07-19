"""Komponen header utama CLue Theam."""

from pathlib import Path

import customtkinter as ctk
from PIL import Image


class HeaderToko(ctk.CTkFrame):
    """Header berisi identitas toko, konteks halaman, dan jam."""

    def __init__(self, parent, colors, store_name, logo_path="", font="Segoe UI"):
        super().__init__(parent, fg_color="transparent")
        self.colors = colors
        self.store_name = store_name or "CLue Theam"
        self.logo_path = logo_path
        self.font_name = font
        self.logo_image = None

        self.grid_columnconfigure(0, weight=1)
        self.build_identity()
        self.clock_label = ctk.CTkLabel(
            self, text="", font=(self.font_name, 12), text_color=self.colors["muted"]
        )
        self.clock_label.grid(row=0, column=1, sticky="e")

    def build_identity(self):
        identity = ctk.CTkFrame(self, fg_color="transparent")
        identity.grid(row=0, column=0, sticky="w")
        self.create_logo(identity, 54).pack(side="left")

        title = ctk.CTkFrame(identity, fg_color="transparent")
        title.pack(side="left", padx=14)
        ctk.CTkLabel(
            title, text=self.store_name, font=(self.font_name, 23, "bold"),
            text_color=self.colors["text"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            title, text="Aplikasi Kasir  •  Transaksi Baru", font=(self.font_name, 11),
            text_color=self.colors["muted"],
        ).pack(anchor="w", pady=(3, 0))

    def create_logo(self, parent, size):
        path = Path(self.logo_path) if self.logo_path else None
        if path and path.is_file():
            try:
                self.logo_image = ctk.CTkImage(Image.open(path), size=(size, size))
                return ctk.CTkLabel(
                    parent, text="", image=self.logo_image, width=size, height=size
                )
            except (OSError, ValueError):
                pass

        initial = self.store_name[:1].upper() if self.store_name else "T"
        return ctk.CTkLabel(
            parent, text=initial, width=size, height=size,
            corner_radius=max(10, size // 3), fg_color=self.colors["primary"],
            text_color="#062A27", font=(self.font_name, max(18, size // 2), "bold"),
        )
