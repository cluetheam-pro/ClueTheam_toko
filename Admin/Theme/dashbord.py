"""Palet dan dashboard pengaturan tampilan CLue Theam."""

import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
from PIL import Image

THEMES = {
    "Gelap": {
        "bg": "#0B1120",
        "sidebar": "#111827",
        "surface": "#172033",
        "surface_alt": "#1E293B",
        "border": "#2A3850",
        "primary": "#2DD4BF",
        "primary_hover": "#14B8A6",
        "success": "#22C55E",
        "danger": "#EF4444",
        "danger_hover": "#DC2626",
        "text": "#F8FAFC",
        "muted": "#94A3B8",
        "warning": "#F59E0B",
    },
    "Terang": {
        "bg": "#F1F5F9",
        "sidebar": "#FFFFFF",
        "surface": "#FFFFFF",
        "surface_alt": "#E2E8F0",
        "border": "#CBD5E1",
        "primary": "#14B8A6",
        "primary_hover": "#0D9488",
        "success": "#16A34A",
        "danger": "#DC2626",
        "danger_hover": "#B91C1C",
        "text": "#0F172A",
        "muted": "#64748B",
        "warning": "#D97706",
    },
}


def get_theme(name="Gelap"):
    """Mengembalikan salinan palet agar sumber tema tidak ikut berubah."""
    return THEMES.get(name, THEMES["Gelap"]).copy()


class DashboardPengaturan(ctk.CTkToplevel):
    """Jendela dashboard untuk mengatur tema dan skala aplikasi."""

    def __init__(self, parent, theme_name, ui_scale, store_name, store_code, logo_path, on_save):
        self.colors = get_theme(theme_name)
        super().__init__(parent, fg_color=self.colors["bg"])
        self.on_save = on_save
        self.title("Dashboard Pengaturan")
        self.geometry("620x650")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.theme_var = ctk.StringVar(value=theme_name)
        self.scale_var = ctk.StringVar(value=ui_scale)
        self.store_name_var = ctk.StringVar(value=store_name)
        self.store_code_var = ctk.StringVar(value=store_code)
        self.logo_path_var = ctk.StringVar(value=logo_path)
        self.build_header()
        self.build_settings()
        self.build_actions()
        self.after(100, self.focus_force)

    def build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=32, pady=(28, 18), sticky="ew")
        ctk.CTkLabel(
            header, text="⚙", width=46, height=46, corner_radius=13,
            fg_color=self.colors["primary"], text_color="#062A27",
            font=("Segoe UI", 21, "bold"),
        ).pack(side="left")
        copy = ctk.CTkFrame(header, fg_color="transparent")
        copy.pack(side="left", padx=14)
        ctk.CTkLabel(
            copy, text="Pengaturan Tampilan", font=("Segoe UI", 22, "bold"),
            text_color=self.colors["text"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            copy, text="Atur tampilan CLue Theam sesuai kebutuhan Anda",
            font=("Segoe UI", 11), text_color=self.colors["muted"],
        ).pack(anchor="w", pady=(2, 0))

    def build_settings(self):
        content = ctk.CTkFrame(self, corner_radius=18, fg_color=self.colors["surface"])
        content.grid(row=1, column=0, padx=32, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)

        self.setting_title(content, "Mode Tema", "Pilih tampilan terang atau gelap", 0, 0)
        ctk.CTkSegmentedButton(
            content, values=["Gelap", "Terang"], variable=self.theme_var,
            height=40, selected_color=self.colors["primary"],
            selected_hover_color=self.colors["primary_hover"],
            unselected_color=self.colors["surface_alt"],
            command=self.update_preview,
        ).grid(row=1, column=0, padx=(20, 10), pady=(12, 24), sticky="ew")

        self.setting_title(content, "Skala Antarmuka", "Sesuaikan ukuran teks dan tombol", 0, 1)
        ctk.CTkOptionMenu(
            content, values=["90%", "100%", "110%"], variable=self.scale_var,
            height=40, fg_color=self.colors["surface_alt"],
            button_color=self.colors["primary_hover"],
        ).grid(row=1, column=1, padx=(10, 20), pady=(12, 24), sticky="ew")

        ctk.CTkLabel(content, text="IDENTITAS TOKO", font=("Segoe UI", 9, "bold"),
                     text_color=self.colors["muted"]).grid(
            row=2, column=0, columnspan=2, padx=20, pady=(0, 8), sticky="w")
        self.store_name_entry = ctk.CTkEntry(
            content, textvariable=self.store_name_var, height=42, corner_radius=10,
            border_color=self.colors["border"], fg_color=self.colors["bg"],
            placeholder_text="Nama toko",
        )
        self.store_name_entry.grid(row=3, column=0, columnspan=2, padx=20, sticky="ew")

        self.store_code_entry = ctk.CTkEntry(
            content, textvariable=self.store_code_var, height=42, corner_radius=10,
            border_color=self.colors["border"], fg_color=self.colors["bg"],
            placeholder_text="Kode toko, contoh: CLT",
        )
        self.store_code_entry.grid(row=4, column=0, columnspan=2, padx=20, pady=(10, 0), sticky="ew")

        logo_frame = ctk.CTkFrame(content, fg_color="transparent")
        logo_frame.grid(row=5, column=0, columnspan=2, padx=20, pady=(10, 20), sticky="ew")
        logo_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkEntry(
            logo_frame, textvariable=self.logo_path_var, height=40, corner_radius=10,
            border_color=self.colors["border"], fg_color=self.colors["bg"],
            placeholder_text="Pilih file logo PNG/JPG",
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")
        ctk.CTkButton(
            logo_frame, text="Pilih Logo", width=100, height=40, corner_radius=10,
            fg_color=self.colors["surface_alt"], hover_color=self.colors["border"],
            text_color=self.colors["text"], command=self.choose_logo,
        ).grid(row=0, column=1)

        preview = ctk.CTkFrame(content, corner_radius=14, fg_color=self.colors["bg"])
        preview.grid(row=6, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        preview.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            preview, text="PRATINJAU", font=("Segoe UI", 9, "bold"),
            text_color=self.colors["muted"],
        ).grid(row=0, column=0, padx=16, pady=(15, 8), sticky="w")
        sample = ctk.CTkFrame(preview, corner_radius=11, fg_color=self.colors["surface_alt"])
        sample.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="ew")
        sample.grid_columnconfigure(0, weight=1)
        self.preview_label = ctk.CTkLabel(
            sample, text="Contoh tampilan dashboard", font=("Segoe UI", 12, "bold"),
            text_color=self.colors["text"],
        )
        self.preview_label.grid(row=0, column=0, padx=14, pady=15, sticky="w")
        ctk.CTkButton(
            sample, text="Tombol", width=82, height=32, corner_radius=8,
            fg_color=self.colors["primary"], hover_color=self.colors["primary_hover"],
            text_color="#062A27",
        ).grid(row=0, column=1, padx=14, pady=10)

    def setting_title(self, parent, title, subtitle, row, column):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=column, padx=(20, 10) if column == 0 else (10, 20),
                   pady=(22, 0), sticky="w")
        ctk.CTkLabel(frame, text=title, font=("Segoe UI", 12, "bold"),
                     text_color=self.colors["text"]).pack(anchor="w")
        ctk.CTkLabel(frame, text=subtitle, font=("Segoe UI", 9),
                     text_color=self.colors["muted"]).pack(anchor="w", pady=(2, 0))

    def build_actions(self):
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=2, column=0, padx=32, pady=24, sticky="ew")
        actions.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(
            actions, text="Batal", width=100, height=44, corner_radius=10,
            fg_color="transparent", border_width=1, border_color=self.colors["border"],
            hover_color=self.colors["surface_alt"], text_color=self.colors["muted"],
            command=self.destroy,
        ).grid(row=0, column=1, padx=(0, 10))
        ctk.CTkButton(
            actions, text="Simpan Perubahan", width=160, height=44, corner_radius=10,
            fg_color=self.colors["primary"], hover_color=self.colors["primary_hover"],
            text_color="#062A27", font=("Segoe UI", 11, "bold"), command=self.save,
        ).grid(row=0, column=2)

    def update_preview(self, theme_name):
        self.preview_label.configure(text=f"Contoh dashboard • Tema {theme_name}")

    def choose_logo(self):
        path = filedialog.askopenfilename(
            parent=self,
            title="Pilih Logo Toko",
            filetypes=[("File gambar", "*.png *.jpg *.jpeg *.webp"), ("Semua file", "*.*")],
        )
        if path:
            self.logo_path_var.set(path)
            try:
                preview = ctk.CTkImage(Image.open(Path(path)), size=(32, 32))
                self.preview_logo = preview
                self.preview_label.configure(image=preview, compound="left", text="  Logo toko siap digunakan")
            except (OSError, ValueError):
                self.preview_label.configure(text="File logo tidak dapat dibaca")

    def save(self):
        self.on_save(
            self,
            self.theme_var.get(),
            self.scale_var.get(),
            self.store_name_var.get().strip(),
            self.store_code_var.get().strip(),
            self.logo_path_var.get().strip(),
        )
