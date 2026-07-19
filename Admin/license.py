"""Pemeriksaan HWID dan form permintaan lisensi CLue Theam."""

from datetime import date, datetime
import hashlib
import platform
import uuid
import webbrowser
from pathlib import Path
from urllib.parse import quote

import customtkinter as ctk
from PIL import Image, ImageTk


THEME_DIR = Path(__file__).resolve().parent / "Theme"
DEFAULT_LOGO_PATH = THEME_DIR / "Clue_Theam.png"
DEFAULT_ICON_PATH = THEME_DIR / "Clue_Theam.ico"

COUNTRY_CODES = {
    "+62  Indonesia": "62",
    "+60  Malaysia": "60",
    "+65  Singapura": "65",
    "+1  AS/Kanada": "1",
    "+44  Inggris": "44",
    "+61  Australia": "61",
}


def get_hwid():
    """Menghasilkan identitas perangkat yang stabil tanpa data pribadi pengguna."""
    value = ""
    if platform.system() == "Windows":
        try:
            import winreg
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Cryptography",
            ) as key:
                value = winreg.QueryValueEx(key, "MachineGuid")[0]
        except OSError:
            pass
    if not value:
        value = f"{platform.node()}-{uuid.getnode():012X}"
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest().upper()
    return f"{digest[:8]}-{digest[8:12]}-{digest[12:16]}-{digest[16:20]}-{digest[20:32]}-STORE"


def normalize_hwid(value):
    return "".join(char for char in str(value or "").casefold() if char.isalnum())


def find_device_license(rows, hwid):
    target = normalize_hwid(hwid)
    return next(
        (
            row for row in rows
            if normalize_hwid(row.get("HWID")) == target
            or (
                len(normalize_hwid(row.get("HWID"))) >= 20
                and normalize_hwid(row.get("HWID"))[:20] == target[:20]
            )
        ),
        None,
    )


def license_is_valid(row):
    if not row:
        return False
    status = row.get("Status", "").strip().casefold()
    if status not in ("on", "aktif", "active", "admin"):
        return False
    expiry = row.get("Expiry Date", "").strip()
    if expiry.casefold() in ("permanen", "permanent", "lifetime"):
        return True
    try:
        return datetime.strptime(expiry, "%Y-%m-%d").date() >= date.today()
    except ValueError:
        return False


def find_customer_service_phone(rows):
    """Mengambil nomor layanan pelanggan dari sheet lisensi."""
    row = next(
        (
            item for item in rows
            if item.get("Nama User", "").strip().casefold()
            in ("costumer cervice", "customer service", "customer support")
            or item.get("Status", "").strip().casefold() == "cs"
        ),
        None,
    )
    return "".join(char for char in (row or {}).get("HP", "") if char.isdigit())


class FormLisensi(ctk.CTkToplevel):
    """Form pendaftaran atau perpanjangan yang menyalin permintaan lisensi."""

    def __init__(self, parent, colors, hwid, mode="daftar", license_row=None,
                 support_phone="", font="Segoe UI"):
        super().__init__(parent, fg_color=colors["bg"])
        self.colors = colors
        self.hwid = hwid
        self.mode = mode
        self.license_row = license_row or {}
        self.support_phone = "".join(char for char in support_phone if char.isdigit())
        self.font_name = font
        self.app_window = parent.winfo_toplevel()
        self.logo_image = None
        self.icon_image = None
        self.window_icon = None
        is_renewal = mode == "perpanjang"
        self.title("Perpanjang Lisensi" if is_renewal else "Daftar Lisensi")
        self.geometry("400x680")
        self.resizable(False, False)
        self.transient(self.app_window)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.close_application)
        self.grid_columnconfigure(0, weight=1)
        self.build(is_renewal)
        self.after(100, self.apply_window_icon)
        self.after(600, self.apply_window_icon)

    def build(self, is_renewal):
        accent = self.colors["warning"] if is_renewal else self.colors["primary"]
        header = ctk.CTkFrame(self, corner_radius=18, fg_color=self.colors["surface"])
        header.grid(row=0, column=0, padx=16, pady=(16, 12), sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        self.create_logo(header, 44).grid(row=0, column=0, rowspan=2, padx=(12, 10), pady=14)
        ctk.CTkLabel(
            header, text="Perpanjang Lisensi" if is_renewal else "Pendaftaran Lisensi",
            font=(self.font_name, 17, "bold"), text_color=self.colors["text"],
        ).grid(row=0, column=1, padx=(0, 6), pady=(15, 2), sticky="sw")
        ctk.CTkLabel(
            header, text="CLue Theam • Aktivasi", font=(self.font_name, 9, "bold"),
            text_color=accent,
        ).grid(row=1, column=1, padx=(0, 10), pady=(0, 17), sticky="nw")
        self.create_icon(header, 24).grid(
            row=0, column=2, rowspan=2, padx=(0, 10), pady=14, sticky="e"
        )

        notice = ctk.CTkFrame(
            self, corner_radius=12,
            fg_color="#78350F" if is_renewal else self.colors["surface_alt"],
        )
        notice.grid(row=1, column=0, padx=16, pady=(0, 10), sticky="ew")
        ctk.CTkLabel(
            notice, text="!" if is_renewal else "i", width=30, height=30, corner_radius=15,
            fg_color=accent, text_color="#062A27", font=(self.font_name, 14, "bold"),
        ).pack(side="left", padx=(14, 10), pady=13)
        ctk.CTkLabel(
            notice,
            text=("Lisensi perangkat telah nonaktif atau melewati masa berlaku."
                  if is_renewal else "Perangkat ini belum tercatat pada server lisensi."),
            wraplength=270, justify="left", font=(self.font_name, 9),
            text_color=self.colors["text"],
        ).pack(side="left", pady=13)

        self.form_card = ctk.CTkFrame(
            self, corner_radius=16, fg_color=self.colors["surface"],
            border_width=1, border_color=self.colors["border"],
        )
        self.form_card.grid(row=2, column=0, padx=16, sticky="ew")
        self.form_card.grid_columnconfigure(0, weight=1)
        self.name_entry = self.add_field("NAMA PENGGUNA", self.license_row.get("Nama User", ""), 0)
        self.country_var = ctk.StringVar(value="+62  Indonesia")
        self.phone_entry = self.add_phone_field(self.license_row.get("HP", ""), 2)
        self.app_entry = self.add_field("APLIKASI", self.license_row.get("APP", "CLue Theam") or "CLue Theam", 4)
        self.hwid_entry = self.add_field("HWID PERANGKAT", self.hwid, 6)
        self.hwid_entry.configure(state="disabled")
        self.status_label = ctk.CTkLabel(
            self, text="", font=(self.font_name, 10), text_color=self.colors["success"]
        )
        self.status_label.grid(row=3, column=0, padx=32, pady=(10, 0), sticky="w")
        ctk.CTkButton(
            self, text="Perpanjang" if is_renewal else "Daftar",
            height=48, corner_radius=11, fg_color=accent,
            hover_color=self.colors["primary_hover"], text_color="#062A27",
            font=(self.font_name, 12, "bold"), command=self.send_whatsapp,
        ).grid(row=4, column=0, padx=16, pady=(10, 8), sticky="ew")
    def add_field(self, label, value, row):
        ctk.CTkLabel(
            self.form_card, text=label, font=(self.font_name, 9, "bold"),
            text_color=self.colors["muted"],
        ).grid(row=row, column=0, padx=18, pady=(16 if row == 0 else 12, 5), sticky="w")
        entry = ctk.CTkEntry(
            self.form_card, height=40, corner_radius=9, border_color=self.colors["border"],
            fg_color=self.colors["bg"], font=(self.font_name, 11),
        )
        entry.grid(row=row + 1, column=0, padx=18, pady=(0, 4 if row < 6 else 16), sticky="ew")
        entry.insert(0, value)
        return entry

    def add_phone_field(self, value, row):
        ctk.CTkLabel(
            self.form_card, text="NOMOR WHATSAPP", font=(self.font_name, 9, "bold"),
            text_color=self.colors["muted"],
        ).grid(row=row, column=0, padx=18, pady=(12, 5), sticky="w")
        phone_frame = ctk.CTkFrame(self.form_card, fg_color="transparent")
        phone_frame.grid(row=row + 1, column=0, padx=18, pady=(0, 4), sticky="ew")
        phone_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkOptionMenu(
            phone_frame, values=list(COUNTRY_CODES), variable=self.country_var,
            width=125, height=40, corner_radius=9, fg_color=self.colors["surface_alt"],
            button_color=self.colors["primary_hover"], font=(self.font_name, 9),
            dropdown_font=(self.font_name, 10),
        ).grid(row=0, column=0, padx=(0, 7))
        entry = ctk.CTkEntry(
            phone_frame, height=40, corner_radius=9, border_color=self.colors["border"],
            fg_color=self.colors["bg"], placeholder_text="8123456789",
            font=(self.font_name, 11), validate="key",
            validatecommand=(self.register(self.validate_phone), "%P"),
        )
        entry.grid(row=0, column=1, sticky="ew")
        self.set_existing_phone(entry, value)
        return entry

    def set_existing_phone(self, entry, value):
        digits = "".join(char for char in str(value) if char.isdigit())
        for label, code in sorted(COUNTRY_CODES.items(), key=lambda item: len(item[1]), reverse=True):
            if digits.startswith(code):
                self.country_var.set(label)
                digits = digits[len(code):]
                break
        entry.insert(0, digits.lstrip("0"))

    @staticmethod
    def validate_phone(value):
        """Kolom WhatsApp hanya menerima angka atau nilai kosong."""
        return value == "" or (value.isdigit() and len(value) <= 15)

    def create_logo(self, parent, size):
        if DEFAULT_LOGO_PATH.is_file():
            try:
                self.logo_image = ctk.CTkImage(Image.open(DEFAULT_LOGO_PATH), size=(size, size))
                return ctk.CTkLabel(parent, text="", image=self.logo_image, width=size, height=size)
            except (OSError, ValueError):
                pass
        return ctk.CTkLabel(
            parent, text="C", width=size, height=size, corner_radius=16,
            fg_color=self.colors["primary"], text_color="#062A27",
            font=(self.font_name, 28, "bold"),
        )

    def create_icon(self, parent, size):
        if DEFAULT_ICON_PATH.is_file():
            try:
                self.icon_image = ctk.CTkImage(
                    light_image=Image.open(DEFAULT_ICON_PATH).convert("RGBA"),
                    dark_image=Image.open(DEFAULT_ICON_PATH).convert("RGBA"),
                    size=(size, size),
                )
                return ctk.CTkLabel(
                    parent, text="", image=self.icon_image, width=size, height=size,
                    corner_radius=9, fg_color=self.colors["surface_alt"],
                )
            except (OSError, ValueError):
                pass
        return ctk.CTkLabel(
            parent, text="C", width=size, height=size, corner_radius=9,
            fg_color=self.colors["primary"], text_color="#062A27",
            font=(self.font_name, 16, "bold"),
        )

    def apply_window_icon(self):
        if not DEFAULT_ICON_PATH.is_file():
            return
        try:
            icon_path = str(DEFAULT_ICON_PATH.resolve())
            self.iconbitmap(default=icon_path)
            self.wm_iconbitmap(icon_path)
            image = Image.open(DEFAULT_ICON_PATH).convert("RGBA")
            self.window_icon = ImageTk.PhotoImage(image)
            self.iconphoto(True, self.window_icon)
        except (OSError, ValueError, RuntimeError):
            self.window_icon = None

    def send_whatsapp(self):
        name = self.name_entry.get().strip()
        local_phone = self.phone_entry.get().strip().lstrip("0")
        country_code = COUNTRY_CODES[self.country_var.get()]
        phone = f"{country_code}{local_phone}"
        app_name = self.app_entry.get().strip()
        if not name or not local_phone or not app_name:
            self.status_label.configure(
                text="Nama, nomor WhatsApp, dan aplikasi wajib diisi.",
                text_color=self.colors["danger"],
            )
            return
        if len(local_phone) < 7:
            self.status_label.configure(
                text="Nomor HP terlalu pendek.", text_color=self.colors["danger"]
            )
            return
        if not self.support_phone:
            self.status_label.configure(
                text="Nomor Costumer Cervice tidak ditemukan pada sheet.",
                text_color=self.colors["danger"],
            )
            return
        action = "PERPANJANG LISENSI" if self.mode == "perpanjang" else "DAFTAR LISENSI"
        message = (
            f"{action}\nNama: {name}\nHP: {phone}\n"
            f"HWID: {self.hwid}\nAPP: {app_name}"
        )
        whatsapp_url = f"https://wa.me/{self.support_phone}?text={quote(message)}"
        opened = webbrowser.open(whatsapp_url, new=2)
        self.status_label.configure(
            text="WhatsApp berhasil dibuka." if opened else "Tidak dapat membuka WhatsApp.",
            text_color=self.colors["success"] if opened else self.colors["danger"],
        )

    def close_application(self):
        """Menutup form lisensi sekaligus seluruh aplikasi."""
        try:
            self.grab_release()
        except Exception:
            pass
        self.app_window.destroy()
