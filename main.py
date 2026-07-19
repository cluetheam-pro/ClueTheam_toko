from datetime import datetime
from pathlib import Path
import hashlib
import hmac
import secrets
import shutil
import sqlite3
from tkinter import messagebox, ttk

import customtkinter as ctk
from PIL import Image, ImageTk

from Admin.login import LoginPage
from Admin.product import InputBarangTab
from Admin.employee import KaryawanTab
from Admin.absen import AbsensiKaryawanTab
from Admin.computer_config import get_database_path
from Admin.Theme.dashbord import DashboardPengaturan, THEMES, get_theme
from Admin.Theme.header import HeaderToko
from Admin.Theme.sidebar import SidebarKasir

COLORS = get_theme("Gelap")

FONT = "Segoe UI"
DB_PATH = get_database_path()
THEME_DIR = Path(__file__).resolve().parent / "Admin" / "Theme"
EMPLOYEE_PHOTO_DIR = DB_PATH.parent / "EmployeePhotos"
DEFAULT_LOGO_PATH = THEME_DIR / "Clue_Theam.png"
DEFAULT_ICON_PATH = THEME_DIR / "Clue_Theam.ico"
CUSTOM_ICON_PATH = THEME_DIR / "icon.png"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")


def rupiah(value):
    return f"Rp {value:,.0f}".replace(",", ".")


class AplikasiKasir(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=COLORS["bg"])
        self.title("CLue Theam — Kasir")
        self.geometry("900x580")
        self.minsize(820, 540)
        self.current_user = None
        self.theme_name = "Gelap"
        self.ui_scale = "100%"
        self.store_name = "CLue Theam"
        self.store_code = "TOKO"
        self.logo_path = str(DEFAULT_LOGO_PATH)
        self.window_icon = None
        self.clock_job = None
        self.setup_database()
        self.load_display_settings()
        self.apply_window_icon()
        self.setup_styles()
        self.show_login()

    def show_login(self):
        if self.clock_job:
            self.after_cancel(self.clock_job)
            self.clock_job = None
        self.unbind("<F12>")
        self.unbind("<Escape>")
        self.unbind("<Control-l>")
        for widget in self.winfo_children():
            widget.destroy()
        self.current_user = None
        self.geometry("900x580")
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        login_page = LoginPage(
            self, COLORS, self.store_name, self.logo_path, self.login, FONT
        )
        login_page.grid(row=0, column=0, padx=38, pady=38, sticky="nsew")
        self.after(100, self.apply_window_icon)

    def login(self, username, password):
        user = self.authenticate(username, password)
        if not user:
            return False
        self.current_user = user
        for widget in self.winfo_children():
            widget.destroy()
        self.geometry("1180x760")
        self.minsize(1000, 680)
        self.build_layout()
        self.bind_shortcuts()
        self.muat_data_ke_tabel()
        self.update_clock()
        self.after(150, self.entry_barcode.focus_set)
        return True

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Kasir.Treeview",
            background=COLORS["surface"],
            fieldbackground=COLORS["surface"],
            foreground=COLORS["text"],
            rowheight=46,
            borderwidth=0,
            font=(FONT, 11),
        )
        style.configure(
            "Kasir.Treeview.Heading",
            background=COLORS["surface_alt"],
            foreground=COLORS["muted"],
            borderwidth=0,
            relief="flat",
            padding=(12, 12),
            font=(FONT, 10, "bold"),
        )
        style.map(
            "Kasir.Treeview",
            background=[("selected", COLORS["primary_hover"])],
            foreground=[("selected", "#FFFFFF")],
        )
        style.map("Kasir.Treeview.Heading", background=[("active", COLORS["surface_alt"])])

    def build_layout(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.build_app_header()
        self.build_sidebar("transaksi")
        self.build_content()

    def build_app_header(self):
        header_bar = ctk.CTkFrame(
            self, height=86, corner_radius=0, fg_color=COLORS["surface"]
        )
        header_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        header_bar.grid_propagate(False)
        header_bar.grid_columnconfigure(0, weight=1)
        header = HeaderToko(header_bar, COLORS, self.store_name, self.logo_path, FONT)
        header.grid(row=0, column=0, padx=28, pady=16, sticky="ew")
        self.lbl_clock = header.clock_label

    def build_sidebar(self, active_page="transaksi"):
        if hasattr(self, "sidebar") and self.sidebar.winfo_exists():
            self.sidebar.destroy()
        self.sidebar = SidebarKasir(
            self, COLORS, self.current_user, self.tampilkan_transaksi,
            self.buka_tab_absensi, self.buka_input_barang, self.buka_tab_karyawan,
            self.buka_pengaturan, self.logout,
            active_page, FONT
        )
        self.sidebar.grid(row=1, column=0, sticky="nsew")

    def build_content(self):
        if hasattr(self, "content_frame") and self.content_frame.winfo_exists():
            self.content_frame.destroy()
        content = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame = content
        content.grid(row=1, column=1, padx=28, pady=24, sticky="nsew")
        content.grid_rowconfigure(1, weight=1)
        content.grid_columnconfigure(0, weight=1)

        search = ctk.CTkFrame(content, height=76, corner_radius=16, fg_color=COLORS["surface"])
        search.grid(row=0, column=0, pady=(0, 16), sticky="ew")
        search.grid_columnconfigure(0, weight=1)
        self.entry_barcode = ctk.CTkEntry(
            search, height=48, corner_radius=12, border_width=1,
            border_color=COLORS["border"], fg_color=COLORS["bg"],
            placeholder_text="⌕  Scan barcode atau ketik kode (001, 002, 003)",
            placeholder_text_color=COLORS["muted"], font=(FONT, 13)
        )
        self.entry_barcode.grid(row=0, column=0, padx=(14, 10), pady=14, sticky="ew")
        self.entry_barcode.bind("<Return>", self.proses_barcode)
        ctk.CTkButton(
            search, text="Tambah Produk", width=140, height=48, corner_radius=12,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="#062A27", font=(FONT, 12, "bold"), command=self.proses_barcode
        ).grid(row=0, column=1, padx=(0, 14), pady=14)

        body = ctk.CTkFrame(content, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=7)
        body.grid_columnconfigure(1, weight=3)
        self.build_cart(body)
        self.build_summary(body)

    def build_cart(self, parent):
        card = ctk.CTkFrame(parent, corner_radius=16, fg_color=COLORS["surface"])
        card.grid(row=0, column=0, padx=(0, 16), sticky="nsew")
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)

        cart_header = ctk.CTkFrame(card, fg_color="transparent")
        cart_header.grid(row=0, column=0, padx=18, pady=(18, 12), sticky="ew")
        self.lbl_item_count = ctk.CTkLabel(cart_header, text="Keranjang • 0 item", font=(FONT, 14, "bold"), text_color=COLORS["text"])
        self.lbl_item_count.pack(side="left")
        ctk.CTkButton(
            cart_header, text="Hapus item", width=90, height=30, corner_radius=8,
            fg_color="transparent", border_width=1, border_color=COLORS["border"],
            hover_color=COLORS["surface_alt"], text_color=COLORS["muted"],
            command=self.hapus_item
        ).pack(side="right")

        columns = ("kode", "nama", "qty", "harga", "subtotal")
        self.tabel = ttk.Treeview(card, columns=columns, show="headings", style="Kasir.Treeview", selectmode="browse")
        headings = {"kode": "KODE", "nama": "PRODUK", "qty": "QTY", "harga": "HARGA", "subtotal": "SUBTOTAL"}
        widths = {"kode": 80, "nama": 220, "qty": 55, "harga": 105, "subtotal": 120}
        for col in columns:
            self.tabel.heading(col, text=headings[col])
            self.tabel.column(col, width=widths[col], minwidth=45, anchor="w" if col == "nama" else "center")
        self.tabel.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="nsew")
        self.tabel.bind("<Delete>", lambda _event: self.hapus_item())

    def build_summary(self, parent):
        summary = ctk.CTkFrame(parent, corner_radius=16, fg_color=COLORS["surface"])
        summary.grid(row=0, column=1, sticky="nsew")
        summary.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(summary, text="Ringkasan Pembayaran", font=(FONT, 15, "bold"), text_color=COLORS["text"]).grid(
            row=0, column=0, padx=20, pady=(22, 24), sticky="w"
        )
        self.lbl_subtotal = self.summary_row(summary, "Subtotal", "Rp 0", 1)
        self.summary_row(summary, "Diskon", "Rp 0", 2, COLORS["success"])
        self.summary_row(summary, "Pajak", "Rp 0", 3)
        ctk.CTkFrame(summary, height=1, fg_color=COLORS["border"]).grid(row=4, column=0, padx=20, pady=18, sticky="ew")

        ctk.CTkLabel(summary, text="TOTAL", font=(FONT, 10, "bold"), text_color=COLORS["muted"]).grid(row=5, column=0, padx=20, sticky="w")
        self.lbl_nilai_total = ctk.CTkLabel(summary, text="Rp 0", font=(FONT, 31, "bold"), text_color=COLORS["primary"])
        self.lbl_nilai_total.grid(row=6, column=0, padx=20, pady=(2, 26), sticky="w")

        ctk.CTkButton(
            summary, text="Bayar Sekarang   F12", height=56, corner_radius=12,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="#062A27", font=(FONT, 14, "bold"), command=self.bayar
        ).grid(row=7, column=0, padx=20, sticky="ew")
        ctk.CTkButton(
            summary, text="Batalkan Transaksi   Esc", height=44, corner_radius=12,
            fg_color="transparent", border_width=1, border_color=COLORS["border"],
            hover_color=COLORS["surface_alt"], text_color=COLORS["muted"], command=self.batalkan
        ).grid(row=8, column=0, padx=20, pady=(10, 18), sticky="ew")
        ctk.CTkLabel(summary, text="Enter  Tambah   •   Del  Hapus", font=(FONT, 9), text_color=COLORS["muted"]).grid(
            row=9, column=0, padx=20, pady=(0, 16)
        )

    def summary_row(self, parent, label, value, row, color=None):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=0, padx=20, pady=5, sticky="ew")
        ctk.CTkLabel(frame, text=label, font=(FONT, 11), text_color=COLORS["muted"]).pack(side="left")
        result = ctk.CTkLabel(frame, text=value, font=(FONT, 11, "bold"), text_color=color or COLORS["text"])
        result.pack(side="right")
        return result

    def setup_database(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS keranjang (kode TEXT PRIMARY KEY, nama TEXT, qty INTEGER, harga INTEGER, subtotal INTEGER)")
            cursor.execute("CREATE TABLE IF NOT EXISTS produk (kode TEXT PRIMARY KEY, nama TEXT, harga INTEGER)")
            product_columns = {row[1] for row in cursor.execute("PRAGMA table_info(produk)")}
            for column, definition in (
                ("harga_beli", "INTEGER NOT NULL DEFAULT 0"),
                ("isi_per_dus", "INTEGER NOT NULL DEFAULT 1"),
                ("satuan", "TEXT NOT NULL DEFAULT 'Pak'"),
            ):
                if column not in product_columns:
                    cursor.execute(f"ALTER TABLE produk ADD COLUMN {column} {definition}")
            cursor.execute("SELECT COUNT(*) FROM produk")
            if cursor.fetchone()[0] == 0:
                cursor.executemany("INSERT INTO produk (kode, nama, harga) VALUES (?, ?, ?)", [
                    ("001", "Kopi Hitam Instan", 15000),
                    ("002", "Susu UHT 1 Liter", 18500),
                    ("003", "Roti Tawar Premium", 20000),
                ])
            cursor.execute("""CREATE TABLE IF NOT EXISTS pengguna (
                username TEXT PRIMARY KEY,
                nama TEXT NOT NULL,
                role TEXT NOT NULL,
                salt TEXT NOT NULL,
                password_hash TEXT NOT NULL
            )""")
            cursor.execute("SELECT COUNT(*) FROM pengguna")
            if cursor.fetchone()[0] == 0:
                self.create_user(cursor, "admin", "Administrator", "Admin", "admin123")
                self.create_user(cursor, "karyawan", "Karyawan Toko", "Karyawan", "kasir123")
            cursor.execute("CREATE TABLE IF NOT EXISTS app_settings (kunci TEXT PRIMARY KEY, nilai TEXT NOT NULL)")
            cursor.execute("""CREATE TABLE IF NOT EXISTS karyawan (
                id_karyawan TEXT PRIMARY KEY,
                nama TEXT NOT NULL,
                no_hp TEXT NOT NULL,
                jabatan TEXT NOT NULL,
                gaji INTEGER NOT NULL
            )""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS absensi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_karyawan TEXT NOT NULL,
                tanggal TEXT NOT NULL,
                jam_masuk TEXT NOT NULL,
                jam_pulang TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Hadir',
                UNIQUE(id_karyawan, tanggal)
            )""")
            employee_columns = {row[1] for row in cursor.execute("PRAGMA table_info(karyawan)")}
            for column, definition in (
                ("no_ktp", "TEXT NOT NULL DEFAULT ''"),
                ("foto", "TEXT NOT NULL DEFAULT ''"),
                ("periode_gaji", "TEXT NOT NULL DEFAULT 'Bulanan'"),
            ):
                if column not in employee_columns:
                    cursor.execute(f"ALTER TABLE karyawan ADD COLUMN {column} {definition}")

    def load_display_settings(self):
        with sqlite3.connect(DB_PATH) as conn:
            settings = dict(conn.execute("SELECT kunci, nilai FROM app_settings").fetchall())
        self.theme_name = settings.get("tema", "Gelap")
        self.ui_scale = settings.get("skala", "100%")
        self.store_name = settings.get("nama_toko", "CLue Theam")
        self.store_code = settings.get("kode_toko", "TOKO")
        self.logo_path = settings.get("logo_path", str(DEFAULT_LOGO_PATH))
        if not Path(self.logo_path).is_file():
            self.logo_path = str(DEFAULT_LOGO_PATH)
        if self.theme_name not in THEMES:
            self.theme_name = "Gelap"
        if self.ui_scale not in ("90%", "100%", "110%"):
            self.ui_scale = "100%"
        COLORS.update(THEMES[self.theme_name])
        ctk.set_appearance_mode("Dark" if self.theme_name == "Gelap" else "Light")
        ctk.set_widget_scaling(int(self.ui_scale.rstrip("%")) / 100)

    def buka_pengaturan(self):
        DashboardPengaturan(
            self, self.theme_name, self.ui_scale, self.store_name,
            self.store_code, self.logo_path, self.simpan_pengaturan,
        )

    def buka_input_barang(self):
        if not self.current_user or self.current_user[2].casefold() != "admin":
            messagebox.showwarning(
                "Akses ditolak", "Input barang hanya dapat diakses oleh Admin.", parent=self
            )
            return
        if hasattr(self, "content_frame") and self.content_frame.winfo_exists():
            self.content_frame.destroy()
        self.build_sidebar("produk")
        self.content_frame = InputBarangTab(
            self, COLORS, self.simpan_barang, self.edit_barang,
            self.ambil_daftar_barang, FONT
        )
        self.content_frame.grid(row=1, column=1, padx=28, pady=20, sticky="nsew")

    def tampilkan_transaksi(self):
        self.build_sidebar("transaksi")
        self.build_content()
        self.muat_data_ke_tabel()
        self.after(100, self.entry_barcode.focus_set)

    def buka_tab_absensi(self):
        if hasattr(self, "content_frame") and self.content_frame.winfo_exists():
            self.content_frame.destroy()
        self.build_sidebar("absensi")
        self.content_frame = AbsensiKaryawanTab(
            self, COLORS, self.current_user, self.proses_scan_absensi,
            self.ambil_absensi_hari_ini, FONT,
        )
        self.content_frame.grid(row=1, column=1, padx=28, pady=20, sticky="nsew")

    def proses_scan_absensi(self, id_karyawan):
        if not id_karyawan:
            return False, "Barcode ID Card belum terbaca."
        if (self.current_user[2].casefold() == "karyawan"
                and id_karyawan != self.current_user[0].upper()):
            return False, "Karyawan hanya dapat menggunakan ID Card miliknya sendiri."
        today = datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(DB_PATH) as conn:
            attendance = conn.execute(
                "SELECT jam_masuk, jam_pulang FROM absensi WHERE id_karyawan = ? AND tanggal = ?",
                (id_karyawan, today),
            ).fetchone()
        if not attendance:
            return self.absen_masuk(id_karyawan)
        if not attendance[1]:
            return self.absen_pulang(id_karyawan)
        return False, f"Absensi hari ini sudah lengkap. Masuk {attendance[0]}, pulang {attendance[1]}."

    def absen_masuk(self, id_karyawan):
        if not id_karyawan:
            return False, "Pindai atau masukkan ID karyawan."
        today = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")
        with sqlite3.connect(DB_PATH) as conn:
            employee = conn.execute(
                "SELECT nama FROM karyawan WHERE id_karyawan = ?", (id_karyawan,)
            ).fetchone()
            if not employee:
                return False, f"ID karyawan '{id_karyawan}' tidak ditemukan."
            existing = conn.execute(
                "SELECT jam_masuk FROM absensi WHERE id_karyawan = ? AND tanggal = ?",
                (id_karyawan, today),
            ).fetchone()
            if existing:
                return False, f"{employee[0]} sudah absen masuk pukul {existing[0]}."
            conn.execute(
                "INSERT INTO absensi (id_karyawan, tanggal, jam_masuk) VALUES (?, ?, ?)",
                (id_karyawan, today, current_time),
            )
        return True, f"Absen masuk {employee[0]} berhasil pukul {current_time}."

    def absen_pulang(self, id_karyawan):
        if not id_karyawan:
            return False, "Pindai atau masukkan ID karyawan."
        today = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")
        with sqlite3.connect(DB_PATH) as conn:
            row = conn.execute(
                """SELECT k.nama, a.jam_pulang
                   FROM karyawan k LEFT JOIN absensi a
                   ON a.id_karyawan = k.id_karyawan AND a.tanggal = ?
                   WHERE k.id_karyawan = ?""",
                (today, id_karyawan),
            ).fetchone()
            if not row:
                return False, f"ID karyawan '{id_karyawan}' tidak ditemukan."
            attendance = conn.execute(
                "SELECT jam_pulang FROM absensi WHERE id_karyawan = ? AND tanggal = ?",
                (id_karyawan, today),
            ).fetchone()
            if not attendance:
                return False, "Karyawan belum melakukan absen masuk hari ini."
            if attendance[0]:
                return False, f"{row[0]} sudah absen pulang pukul {attendance[0]}."
            conn.execute(
                "UPDATE absensi SET jam_pulang = ? WHERE id_karyawan = ? AND tanggal = ?",
                (current_time, id_karyawan, today),
            )
        return True, f"Absen pulang {row[0]} berhasil pukul {current_time}."

    def ambil_absensi_hari_ini(self):
        today = datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(DB_PATH) as conn:
            return conn.execute(
                """SELECT a.id_karyawan, k.nama, a.tanggal, a.jam_masuk,
                          CASE WHEN a.jam_pulang = '' THEN '-' ELSE a.jam_pulang END,
                          a.status
                   FROM absensi a JOIN karyawan k ON k.id_karyawan = a.id_karyawan
                   WHERE a.tanggal = ? ORDER BY a.jam_masuk DESC""",
                (today,),
            ).fetchall()

    def buka_tab_karyawan(self):
        if not self.current_user or self.current_user[2].casefold() != "admin":
            messagebox.showwarning(
                "Akses ditolak", "Data karyawan hanya dapat diakses oleh Admin.", parent=self
            )
            return
        if hasattr(self, "content_frame") and self.content_frame.winfo_exists():
            self.content_frame.destroy()
        self.build_sidebar("karyawan")
        self.content_frame = KaryawanTab(
            self, COLORS, self.store_name, self.store_code, self.simpan_karyawan,
            self.edit_karyawan,
            self.ambil_daftar_karyawan, FONT
        )
        self.content_frame.grid(row=1, column=1, padx=28, pady=20, sticky="nsew")

    def simpan_karyawan(self, id_karyawan, nama, no_hp, jabatan, gaji, no_ktp, foto, password, periode_gaji):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                duplicate = conn.execute(
                    "SELECT id_karyawan, no_ktp FROM karyawan WHERE id_karyawan = ? OR no_ktp = ?",
                    (id_karyawan, no_ktp),
                ).fetchone()
                user_exists = conn.execute(
                    "SELECT 1 FROM pengguna WHERE username = ?", (id_karyawan,)
                ).fetchone()
            if duplicate:
                if duplicate[0] == id_karyawan:
                    return False, f"ID karyawan '{id_karyawan}' sudah digunakan."
                return False, "Nomor KTP sudah terdaftar."
            if user_exists:
                return False, f"Akun login '{id_karyawan}' sudah digunakan."
            source = Path(foto)
            EMPLOYEE_PHOTO_DIR.mkdir(parents=True, exist_ok=True)
            destination = EMPLOYEE_PHOTO_DIR / f"{id_karyawan}{source.suffix.lower()}"
            shutil.copy2(source, destination)
            stored_photo = str(Path("EmployeePhotos") / destination.name)
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO karyawan
                       (id_karyawan, nama, no_hp, jabatan, gaji, no_ktp, foto, periode_gaji)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (id_karyawan, nama, no_hp, jabatan, gaji, no_ktp,
                     stored_photo, periode_gaji),
                )
                self.create_user(cursor, id_karyawan, nama, "Karyawan", password)
            return True, f"Karyawan '{nama}' berhasil disimpan."
        except sqlite3.IntegrityError:
            return False, "ID karyawan atau nomor KTP sudah digunakan."
        except (OSError, shutil.Error):
            return False, "Foto karyawan gagal disimpan."

    def ambil_daftar_karyawan(self):
        with sqlite3.connect(DB_PATH) as conn:
            rows = conn.execute(
                """SELECT id_karyawan, nama, no_hp, jabatan, gaji, no_ktp, foto, periode_gaji
                   FROM karyawan ORDER BY nama COLLATE NOCASE"""
            ).fetchall()
        result = []
        for row in rows:
            photo = Path(row[6]) if row[6] else Path()
            resolved_photo = photo if photo.is_absolute() else DB_PATH.parent / photo
            result.append((*row[:6], str(resolved_photo), row[7]))
        return result

    def edit_karyawan(self, id_karyawan, nama, no_hp, jabatan, gaji, no_ktp, foto, password, periode_gaji):
        with sqlite3.connect(DB_PATH) as conn:
            duplicate_ktp = conn.execute(
                "SELECT 1 FROM karyawan WHERE no_ktp = ? AND id_karyawan <> ?",
                (no_ktp, id_karyawan),
            ).fetchone()
            user_exists = conn.execute(
                "SELECT 1 FROM pengguna WHERE username = ?", (id_karyawan,)
            ).fetchone()
        if duplicate_ktp:
            return False, "Nomor KTP sudah digunakan karyawan lain."
        if password and len(password) < 6:
            return False, "Password baru minimal 6 karakter."
        if not user_exists and not password:
            return False, "Masukkan password untuk membuat akun login karyawan."

        source = Path(foto)
        if not source.is_file():
            return False, "File foto karyawan tidak ditemukan."
        EMPLOYEE_PHOTO_DIR.mkdir(parents=True, exist_ok=True)
        destination = EMPLOYEE_PHOTO_DIR / f"{id_karyawan}{source.suffix.lower()}"
        try:
            if source.resolve() != destination.resolve():
                shutil.copy2(source, destination)
            stored_photo = str(Path("EmployeePhotos") / destination.name)
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """UPDATE karyawan
                       SET nama = ?, no_hp = ?, jabatan = ?, gaji = ?, no_ktp = ?, foto = ?, periode_gaji = ?
                       WHERE id_karyawan = ?""",
                    (nama, no_hp, jabatan, gaji, no_ktp, stored_photo,
                     periode_gaji, id_karyawan),
                )
                cursor.execute(
                    "UPDATE pengguna SET nama = ?, role = 'Karyawan' WHERE username = ?",
                    (nama, id_karyawan),
                )
                if password:
                    if user_exists:
                        salt = secrets.token_hex(16)
                        password_hash = hashlib.pbkdf2_hmac(
                            "sha256", password.encode(), bytes.fromhex(salt), 200_000
                        ).hex()
                        cursor.execute(
                            "UPDATE pengguna SET salt = ?, password_hash = ? WHERE username = ?",
                            (salt, password_hash, id_karyawan),
                        )
                    else:
                        self.create_user(cursor, id_karyawan, nama, "Karyawan", password)
            return True, f"Data karyawan '{nama}' berhasil diperbarui."
        except (OSError, shutil.Error, sqlite3.Error):
            return False, "Data karyawan gagal diperbarui."

    def simpan_barang(self, kode, nama, harga_beli, harga_jual, isi_per_dus, satuan):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    """INSERT INTO produk
                       (kode, nama, harga, harga_beli, isi_per_dus, satuan)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (kode, nama, harga_jual, harga_beli, isi_per_dus, satuan),
                )
            return True, f"Barang '{nama}' berhasil disimpan."
        except sqlite3.IntegrityError:
            return False, f"Kode '{kode}' sudah digunakan."

    def ambil_daftar_barang(self):
        with sqlite3.connect(DB_PATH) as conn:
            return conn.execute(
                """SELECT kode, nama, harga_beli, harga, isi_per_dus, satuan
                   FROM produk ORDER BY nama COLLATE NOCASE"""
            ).fetchall()

    def edit_barang(self, kode, nama, harga_beli, harga_jual, isi_per_dus, satuan):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(
                """UPDATE produk
                   SET nama = ?, harga_beli = ?, harga = ?, isi_per_dus = ?, satuan = ?
                   WHERE kode = ?""",
                (nama, harga_beli, harga_jual, isi_per_dus, satuan, kode),
            )
        if cursor.rowcount:
            return True, f"Barang '{nama}' berhasil diperbarui."
        return False, f"Barang dengan kode '{kode}' tidak ditemukan."

    def simpan_pengaturan(self, dialog, tema, skala, nama_toko, kode_toko, logo_path):
        nama_toko = nama_toko or "CLue Theam"
        kode_toko = "".join(char for char in kode_toko.upper() if char.isalnum()) or "TOKO"
        logo_path = self.simpan_logo_ke_theme(logo_path)
        with sqlite3.connect(DB_PATH) as conn:
            conn.executemany("INSERT OR REPLACE INTO app_settings (kunci, nilai) VALUES (?, ?)",
                             [("tema", tema), ("skala", skala),
                              ("nama_toko", nama_toko), ("kode_toko", kode_toko),
                              ("logo_path", logo_path)])
        self.theme_name = tema
        self.ui_scale = skala
        self.store_name = nama_toko
        self.store_code = kode_toko
        self.logo_path = logo_path
        self.apply_window_icon()
        COLORS.update(THEMES[tema])
        ctk.set_appearance_mode("Dark" if tema == "Gelap" else "Light")
        ctk.set_widget_scaling(int(skala.rstrip("%")) / 100)
        dialog.destroy()
        if self.clock_job:
            self.after_cancel(self.clock_job)
            self.clock_job = None
        self.setup_styles()
        for widget in self.winfo_children():
            widget.destroy()
        self.build_layout()
        self.bind_shortcuts()
        self.muat_data_ke_tabel()
        self.update_clock()

    @staticmethod
    def simpan_logo_ke_theme(logo_path):
        """Menyalin logo pilihan ke folder Theme dan membuat ikon aplikasi."""
        source = Path(logo_path) if logo_path else None
        if not source or not source.is_file():
            return str(DEFAULT_LOGO_PATH.resolve())
        THEME_DIR.mkdir(parents=True, exist_ok=True)
        if source.resolve() == DEFAULT_LOGO_PATH.resolve():
            return str(DEFAULT_LOGO_PATH.resolve())
        suffix = source.suffix.lower() if source.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp") else ".png"
        destination = THEME_DIR / f"logo{suffix}"
        try:
            if source.resolve() != destination.resolve():
                shutil.copy2(source, destination)
            icon = Image.open(destination).convert("RGBA")
            icon.thumbnail((64, 64), Image.Resampling.LANCZOS)
            icon.save(CUSTOM_ICON_PATH, "PNG")
            return str(destination.resolve())
        except (OSError, ValueError, shutil.Error):
            return str(source)

    def apply_window_icon(self):
        """Menampilkan logo toko sebagai ikon jendela jika gambarnya tersedia."""
        logo = Path(self.logo_path) if self.logo_path else DEFAULT_LOGO_PATH
        is_default = logo.is_file() and logo.resolve() == DEFAULT_LOGO_PATH.resolve()
        if is_default and DEFAULT_ICON_PATH.is_file():
            path = DEFAULT_ICON_PATH
        elif CUSTOM_ICON_PATH.is_file():
            path = CUSTOM_ICON_PATH
        else:
            path = logo
        if not path or not path.is_file():
            return
        try:
            if path.suffix.lower() == ".ico":
                self.iconbitmap(str(path.resolve()))
            image = Image.open(path).convert("RGBA")
            image.thumbnail((64, 64), Image.Resampling.LANCZOS)
            self.window_icon = ImageTk.PhotoImage(image)
            self.iconphoto(True, self.window_icon)
        except (OSError, ValueError, RuntimeError):
            self.window_icon = None

    @staticmethod
    def create_user(cursor, username, nama, role, password):
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 200_000).hex()
        cursor.execute("INSERT INTO pengguna VALUES (?, ?, ?, ?, ?)",
                       (username, nama, role, salt, password_hash))

    @staticmethod
    def authenticate(username, password):
        if not username or not password:
            return None
        with sqlite3.connect(DB_PATH) as conn:
            row = conn.execute(
                "SELECT username, nama, role, salt, password_hash FROM pengguna WHERE username = ?",
                (username,),
            ).fetchone()
        if not row:
            return None
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(row[3]), 200_000).hex()
        return row[:3] if hmac.compare_digest(candidate, row[4]) else None

    def logout(self):
        if messagebox.askyesno("Keluar", "Keluar dari akun saat ini?", parent=self):
            self.show_login()

    def bind_shortcuts(self):
        self.bind("<F12>", lambda _event: self.bayar())
        self.bind("<Escape>", lambda _event: self.batalkan())
        self.bind("<Control-l>", lambda _event: self.entry_barcode.focus_set())

    def proses_barcode(self, _event=None):
        kode = self.entry_barcode.get().strip()
        if not kode:
            self.entry_barcode.focus_set()
            return
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nama, harga FROM produk WHERE kode = ?", (kode,))
            barang = cursor.fetchone()
            if not barang:
                messagebox.showwarning("Produk tidak ditemukan", f"Kode produk '{kode}' belum terdaftar.", parent=self)
            else:
                cursor.execute("SELECT qty FROM keranjang WHERE kode = ?", (kode,))
                item = cursor.fetchone()
                if item:
                    cursor.execute("UPDATE keranjang SET qty = qty + 1, subtotal = (qty + 1) * harga WHERE kode = ?", (kode,))
                else:
                    cursor.execute("INSERT INTO keranjang VALUES (?, ?, 1, ?, ?)", (kode, barang[0], barang[1], barang[1]))
        self.entry_barcode.delete(0, "end")
        self.muat_data_ke_tabel()
        self.entry_barcode.focus_set()

    def hapus_item(self):
        selected = self.tabel.selection()
        if not selected:
            return
        kode = self.tabel.item(selected[0], "values")[0]
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("DELETE FROM keranjang WHERE kode = ?", (kode,))
        self.muat_data_ke_tabel()

    def batalkan(self):
        if not self.tabel.get_children():
            return
        if messagebox.askyesno("Batalkan transaksi", "Hapus semua item di keranjang?", parent=self):
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("DELETE FROM keranjang")
            self.muat_data_ke_tabel()

    def bayar(self):
        total = self.get_total()
        if total == 0:
            messagebox.showinfo("Keranjang kosong", "Tambahkan produk sebelum melakukan pembayaran.", parent=self)
            return
        if messagebox.askyesno("Konfirmasi pembayaran", f"Proses pembayaran sebesar {rupiah(total)}?", parent=self):
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("DELETE FROM keranjang")
            self.muat_data_ke_tabel()
            messagebox.showinfo("Pembayaran berhasil", "Transaksi berhasil diselesaikan.", parent=self)

    def get_total(self):
        with sqlite3.connect(DB_PATH) as conn:
            return conn.execute("SELECT COALESCE(SUM(subtotal), 0) FROM keranjang").fetchone()[0]

    def muat_data_ke_tabel(self):
        for row in self.tabel.get_children():
            self.tabel.delete(row)
        with sqlite3.connect(DB_PATH) as conn:
            rows = conn.execute("SELECT kode, nama, qty, harga, subtotal FROM keranjang ORDER BY rowid DESC").fetchall()
        total = sum(row[4] for row in rows)
        item_count = sum(row[2] for row in rows)
        for row in rows:
            self.tabel.insert("", "end", values=(row[0], row[1], row[2], rupiah(row[3]), rupiah(row[4])))
        self.lbl_item_count.configure(text=f"Keranjang • {item_count} item")
        self.lbl_subtotal.configure(text=rupiah(total))
        self.lbl_nilai_total.configure(text=rupiah(total))

    def update_clock(self):
        now = datetime.now()
        hari = ("Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min")[now.weekday()]
        self.lbl_clock.configure(text=f"{hari}, {now:%d/%m/%Y  •  %H:%M}")
        self.clock_job = self.after(1000, self.update_clock)


if __name__ == "__main__":
    app = AplikasiKasir()
    app.mainloop()
