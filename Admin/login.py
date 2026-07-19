"""Halaman login Admin dan Karyawan CLue Theam."""

from pathlib import Path
import csv
import io
import threading
from urllib.request import Request, urlopen

import customtkinter as ctk
from PIL import Image

from Admin.license import (
    FormLisensi,
    find_customer_service_phone,
    find_device_license,
    get_hwid,
    license_is_valid,
)


LICENSE_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vThh5A6yIG2pqiF4gEGIyvB_r5F3ev_fLTy3kvWc7Jm44mGa2y5Oc_fSyJxmStqa16Li_2Mq_sLCQi_"
    "/pub?gid=0&single=true&output=csv"
)


class LoginPage(ctk.CTkFrame):
    """Halaman login dua panel dengan identitas toko."""

    def __init__(self, parent, colors, store_name, logo_path, on_login,
                 font="Segoe UI"):
        super().__init__(parent, fg_color="transparent")
        self.colors = colors
        self.store_name = store_name or "CLue Theam"
        self.logo_path = logo_path
        self.on_login = on_login
        self.font_name = font
        self.logo_images = []
        self.license_rows = []
        self.hwid = get_hwid()
        self.license_dialog_shown = False

        self.grid_columnconfigure(0, weight=10)
        self.grid_columnconfigure(1, weight=9)
        self.grid_rowconfigure(0, weight=1)
        self.build_hero()
        self.build_form()
        self.load_license_async()
        self.after(150, self.username_entry.focus_set)

    def build_hero(self):
        hero = ctk.CTkFrame(self, corner_radius=22, fg_color=self.colors["primary"])
        hero.grid(row=0, column=0, padx=(0, 12), sticky="nsew")
        hero.grid_rowconfigure(1, weight=1)
        self.create_logo(hero, 68).grid(row=0, column=0, padx=38, pady=(38, 0), sticky="w")
        copy = ctk.CTkFrame(hero, fg_color="transparent")
        copy.grid(row=1, column=0, padx=38, pady=38, sticky="sw")
        ctk.CTkLabel(
            copy, text=self.store_name, justify="left", font=(self.font_name, 14, "bold"),
            text_color="#115E59",
        ).pack(anchor="w", pady=(0, 10))
        ctk.CTkLabel(
            copy, text="Kelola transaksi\nlebih cepat.", justify="left",
            font=(self.font_name, 32, "bold"), text_color="#062A27",
        ).pack(anchor="w")
        ctk.CTkLabel(
            copy, text="Sistem kasir sederhana, aman, dan mudah digunakan.",
            wraplength=330, justify="left", font=(self.font_name, 12),
            text_color="#115E59",
        ).pack(anchor="w", pady=(14, 0))
        badges = ctk.CTkFrame(copy, fg_color="transparent")
        badges.pack(anchor="w", pady=(24, 0))
        for text in ("✓ Aman", "✓ Cepat", "✓ Praktis"):
            ctk.CTkLabel(
                badges, text=text, height=28, corner_radius=8, fg_color="#5EEAD4",
                text_color="#115E59", font=(self.font_name, 9, "bold"),
            ).pack(side="left", padx=(0, 7), ipadx=7)

        license_card = ctk.CTkFrame(copy, corner_radius=12, fg_color="#0F766E")
        license_card.pack(anchor="w", fill="x", pady=(22, 0))
        license_header = ctk.CTkFrame(license_card, fg_color="transparent")
        license_header.pack(fill="x", padx=14, pady=(12, 2))
        ctk.CTkLabel(
            license_header, text="LISENSI APLIKASI", font=(self.font_name, 9, "bold"),
            text_color="#99F6E4",
        ).pack(side="left")
        self.license_status = ctk.CTkLabel(
            license_header, text="MEMERIKSA", height=22, corner_radius=7,
            fg_color="#134E4A", text_color="#CCFBF1", font=(self.font_name, 8, "bold"),
        )
        self.license_status.pack(side="right", ipadx=6)
        self.license_owner = ctk.CTkLabel(
            license_card, text="Mengambil data lisensi...", font=(self.font_name, 11, "bold"),
            text_color="#F0FDFA",
        )
        self.license_owner.pack(anchor="w", padx=14, pady=(2, 0))
        self.license_detail = ctk.CTkLabel(
            license_card, text="Pastikan perangkat terhubung ke internet", wraplength=300,
            justify="left", font=(self.font_name, 9), text_color="#99F6E4",
        )
        self.license_detail.pack(anchor="w", padx=14, pady=(3, 12))

    def build_form(self):
        form = ctk.CTkFrame(
            self, corner_radius=22, fg_color=self.colors["surface"],
            border_width=1, border_color=self.colors["border"],
        )
        form.grid(row=0, column=1, padx=(12, 0), sticky="nsew")
        form.grid_columnconfigure(0, weight=1)
        heading = ctk.CTkFrame(form, fg_color="transparent")
        heading.grid(row=0, column=0, padx=32, pady=(34, 4), sticky="ew")
        self.create_logo(heading, 44).pack(side="left")
        heading_copy = ctk.CTkFrame(heading, fg_color="transparent")
        heading_copy.pack(side="left", padx=12)
        ctk.CTkLabel(
            heading_copy, text="Selamat datang", font=(self.font_name, 21, "bold"),
            text_color=self.colors["text"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            heading_copy, text=self.store_name, font=(self.font_name, 10, "bold"),
            text_color=self.colors["primary"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            form, text="Masuk dengan akun Admin atau Karyawan", font=(self.font_name, 11),
            text_color=self.colors["muted"],
        ).grid(row=1, column=0, padx=32, pady=(8, 24), sticky="w")
        self.field_label(form, "USERNAME / ID KARYAWAN", 2)
        self.username_entry = ctk.CTkEntry(
            form, height=46, corner_radius=10, border_color=self.colors["border"],
            fg_color=self.colors["bg"], placeholder_text="Ketik username atau scan barcode",
            font=(self.font_name, 12),
        )
        self.username_entry.grid(row=3, column=0, padx=32, sticky="ew")
        self.field_label(form, "PASSWORD", 4, pady=(18, 7))
        self.password_entry = ctk.CTkEntry(
            form, height=46, corner_radius=10, border_color=self.colors["border"],
            fg_color=self.colors["bg"], placeholder_text="Masukkan password", show="*",
            font=(self.font_name, 12),
        )
        self.password_entry.grid(row=5, column=0, padx=32, sticky="ew")
        self.show_password_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            form, text="Tampilkan password", variable=self.show_password_var,
            width=20, height=20, checkbox_width=18, checkbox_height=18,
            border_color=self.colors["border"], fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"], text_color=self.colors["muted"],
            font=(self.font_name, 10), command=self.toggle_password,
        ).grid(row=6, column=0, padx=32, pady=(10, 0), sticky="w")
        self.error_label = ctk.CTkLabel(
            form, text="", font=(self.font_name, 10), text_color=self.colors["danger"]
        )
        self.error_label.grid(row=7, column=0, padx=32, pady=(7, 0), sticky="w")
        self.login_button = ctk.CTkButton(
            form, text="Masuk", height=48, corner_radius=11,
            fg_color=self.colors["primary"], hover_color=self.colors["primary_hover"],
            text_color="#062A27", font=(self.font_name, 13, "bold"), command=self.submit,
            state="disabled",
        )
        self.login_button.grid(row=8, column=0, padx=32, pady=(10, 12), sticky="ew")
        ctk.CTkLabel(
            form, text="Akun hanya dapat dibuat oleh pengelola sistem",
            font=(self.font_name, 9), text_color=self.colors["muted"],
        ).grid(row=9, column=0, padx=32)
        self.username_entry.bind("<Return>", lambda _event: self.password_entry.focus_set())
        self.username_entry.bind("<KeyRelease>", lambda _event: self.show_matching_license())
        self.password_entry.bind("<Return>", lambda _event: self.submit())

    def field_label(self, parent, text, row, pady=(0, 7)):
        ctk.CTkLabel(
            parent, text=text, font=(self.font_name, 9, "bold"),
            text_color=self.colors["muted"],
        ).grid(row=row, column=0, padx=30, pady=pady, sticky="w")

    def submit(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if self.on_login(username, password):
            return
        self.error_label.configure(text="Username atau password salah.")
        self.password_entry.delete(0, "end")
        self.password_entry.focus_set()

    def toggle_password(self):
        self.password_entry.configure(show="" if self.show_password_var.get() else "*")

    def load_license_async(self):
        threading.Thread(target=self.fetch_license, daemon=True).start()

    def fetch_license(self):
        try:
            request = Request(LICENSE_URL, headers={"User-Agent": "CLue-Theam/1.0"})
            with urlopen(request, timeout=12) as response:
                content = response.read().decode("utf-8-sig")
            rows = list(csv.DictReader(io.StringIO(content)))
            self.after(0, lambda: self.set_license_rows(rows))
        except Exception:
            self.after(0, self.show_license_offline)

    def set_license_rows(self, rows):
        self.license_rows = rows
        row = find_device_license(rows, self.hwid)
        if row and license_is_valid(row):
            self.login_button.configure(state="normal")
            self.show_device_license(row, True)
            return
        self.login_button.configure(state="disabled")
        self.show_device_license(row, False)
        if not self.license_dialog_shown:
            self.license_dialog_shown = True
            mode = "perpanjang" if row else "daftar"
            support_phone = find_customer_service_phone(rows)
            self.after(250, lambda: FormLisensi(
                self, self.colors, self.hwid, mode, row, support_phone, self.font_name
            ))

    def show_matching_license(self):
        row = find_device_license(self.license_rows, self.hwid)
        if row:
            self.show_device_license(row, license_is_valid(row))

    def show_device_license(self, row, active):
        if not row:
            self.license_owner.configure(text="Perangkat belum terdaftar")
            self.license_detail.configure(text=f"HWID: {self.hwid}")
            self.license_status.configure(text="BELUM ADA", fg_color="#991B1B", text_color="#FEE2E2")
            return
        owner = row.get("Nama User", "Lisensi tidak bernama").strip()
        expiry = row.get("Expiry Date", "-").strip() or "-"
        app_name = row.get("APP", "").strip() or "CLue Theam"
        self.license_owner.configure(text=owner)
        self.license_detail.configure(text=f"{app_name}  •  Berlaku: {expiry}")
        self.license_status.configure(
            text="AKTIF" if active else "NONAKTIF",
            fg_color="#166534" if active else "#991B1B",
            text_color="#DCFCE7" if active else "#FEE2E2",
        )

    def show_license_offline(self):
        self.license_status.configure(text="OFFLINE", fg_color="#78350F", text_color="#FEF3C7")
        self.license_owner.configure(text="Data lisensi tidak tersedia")
        self.license_detail.configure(text="Periksa koneksi internet, lalu buka ulang aplikasi.")

    def create_logo(self, parent, size):
        path = Path(self.logo_path) if self.logo_path else None
        if path and path.is_file():
            try:
                logo_image = ctk.CTkImage(Image.open(path), size=(size, size))
                self.logo_images.append(logo_image)
                return ctk.CTkLabel(parent, text="", image=logo_image, width=size, height=size)
            except (OSError, ValueError):
                pass
        initial = self.store_name[:1].upper() if self.store_name else "T"
        return ctk.CTkLabel(
            parent, text=initial, width=size, height=size, corner_radius=max(10, size // 3),
            fg_color="#062A27", text_color=self.colors["primary"],
            font=(self.font_name, max(18, size // 2), "bold"),
        )
