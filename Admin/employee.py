"""Tab pengelolaan karyawan khusus Administrator."""

import customtkinter as ctk
from tkinter import filedialog, ttk
from pathlib import Path
from PIL import Image, ImageTk

from Admin.idcard import IDCardKaryawan


class KaryawanTab(ctk.CTkFrame):
    def __init__(self, parent, colors, store_name, store_code, on_save, on_update, on_load,
                 font="Segoe UI"):
        super().__init__(parent, fg_color="transparent")
        self.colors = colors
        self.store_name = store_name
        self.store_code = "".join(char for char in store_code.upper() if char.isalnum()) or "TOKO"
        self.on_save = on_save
        self.on_update = on_update
        self.on_load = on_load
        self.font_name = font
        self.photo_image = None
        self.table_images = []
        self.photo_path = ctk.StringVar(value="")
        self.editing_id = None
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        self.build_table()
        self.build_form()
        self.load_employees()

    def build_table(self):
        card = ctk.CTkFrame(self, corner_radius=16, fg_color=self.colors["surface"])
        card.grid(row=0, column=0, sticky="nsew")
        card.grid_rowconfigure(3, weight=1)
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            card, text="Daftar Karyawan", font=(self.font_name, 20, "bold"),
            text_color=self.colors["text"],
        ).grid(row=0, column=0, padx=18, pady=(20, 2), sticky="w")
        self.count_label = ctk.CTkLabel(
            card, text="0 karyawan", font=(self.font_name, 10),
            text_color=self.colors["muted"],
        )
        self.count_label.grid(row=1, column=0, padx=18, pady=(0, 12), sticky="w")
        search = ctk.CTkFrame(card, fg_color="transparent")
        search.grid(row=2, column=0, columnspan=2, padx=16, pady=(0, 12), sticky="ew")
        search.grid_columnconfigure(0, weight=1)
        self.search_entry = ctk.CTkEntry(
            search, height=38, corner_radius=9, border_color=self.colors["border"],
            fg_color=self.colors["bg"], placeholder_text="Cari ID, nama, atau jabatan...",
            font=(self.font_name, 10),
        )
        self.search_entry.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda _event: self.filter_employees())
        ctk.CTkButton(
            search, text="Edit", width=62, height=38, corner_radius=9,
            fg_color=self.colors["surface_alt"], hover_color=self.colors["primary_hover"],
            text_color=self.colors["text"], command=self.edit_selected,
        ).grid(row=0, column=1)
        ctk.CTkButton(
            search, text="ID Card", width=78, height=38, corner_radius=9,
            fg_color=self.colors["surface_alt"], hover_color=self.colors["primary_hover"],
            text_color=self.colors["text"], command=self.show_id_card,
        ).grid(row=0, column=2, padx=(8, 0))

        columns = ("id", "nama", "ktp", "hp", "jabatan", "gaji", "periode")
        self.table = ttk.Treeview(
            card, columns=columns, show="tree headings", style="Kasir.Treeview"
        )
        self.table.heading("#0", text="FOTO")
        self.table.column("#0", width=62, minwidth=62, stretch=False, anchor="center")
        headings = {"id": "ID", "nama": "NAMA", "ktp": "NO. KTP", "hp": "NO. HP", "jabatan": "JABATAN", "gaji": "GAJI", "periode": "PERIODE"}
        widths = {"id": 75, "nama": 135, "ktp": 135, "hp": 110, "jabatan": 95, "gaji": 105, "periode": 85}
        for column in columns:
            self.table.heading(column, text=headings[column])
            self.table.column(column, width=widths[column], minwidth=60,
                              anchor="w" if column in ("nama", "jabatan") else "center")
        vertical = ttk.Scrollbar(card, orient="vertical", command=self.table.yview)
        horizontal = ttk.Scrollbar(card, orient="horizontal", command=self.table.xview)
        self.table.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.table.bind("<Double-1>", lambda _event: self.edit_selected())
        self.table.grid(row=3, column=0, padx=(16, 0), sticky="nsew")
        vertical.grid(row=3, column=1, padx=(0, 16), sticky="ns")
        horizontal.grid(row=4, column=0, padx=(16, 0), pady=(0, 16), sticky="ew")

    def build_form(self):
        right = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0,
            scrollbar_button_color=self.colors["surface_alt"],
        )
        right.grid(row=0, column=1, padx=(16, 0), sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        header = ctk.CTkFrame(right, corner_radius=16, fg_color=self.colors["surface"])
        header.grid(row=0, column=0, padx=(0, 8), pady=(0, 14), sticky="ew")
        ctk.CTkLabel(
            header, text="Input Karyawan", font=(self.font_name, 20, "bold"),
            text_color=self.colors["text"],
        ).pack(anchor="w", padx=18, pady=(18, 2))
        ctk.CTkLabel(
            header, text="Data pegawai dan penggajian", font=(self.font_name, 9, "bold"),
            text_color=self.colors["primary"],
        ).pack(anchor="w", padx=18, pady=(0, 18))

        form = ctk.CTkFrame(
            right, corner_radius=15, fg_color=self.colors["surface"],
            border_width=1, border_color=self.colors["border"],
        )
        form.grid(row=1, column=0, padx=(0, 8), sticky="ew")
        form.grid_columnconfigure(0, weight=1)
        self.id_entry = self.add_field(form, "ID KARYAWAN (OTOMATIS)", f"{self.store_code}001", 0)
        self.id_entry.configure(state="disabled")
        self.name_entry = self.add_field(form, "NAMA LENGKAP", "Nama karyawan", 2)
        self.phone_entry = self.add_field(form, "NOMOR HP", "08123456789", 4, numeric=True)
        self.ktp_entry = self.add_field(form, "NOMOR KTP (16 DIGIT)", "3201234567890123", 6)
        self.ktp_entry.configure(
            validate="key", validatecommand=(self.register(self.only_ktp), "%P")
        )
        self.position_var = ctk.StringVar(value="Kasir")
        self.add_position_dropdown(form, 8)
        self.salary_entry = self.add_field(form, "NOMINAL GAJI", "2500000", 10, numeric=True)
        self.salary_period_var = ctk.StringVar(value="Bulanan")
        self.add_salary_period_dropdown(form, 12)
        self.password_entry = self.add_password_field(form, 14)
        self.add_photo_field(form, 16)
        self.status_label = ctk.CTkLabel(
            right, text="Isi semua data karyawan.", font=(self.font_name, 9),
            text_color=self.colors["muted"],
        )
        self.status_label.grid(row=2, column=0, padx=2, pady=(10, 0), sticky="w")
        self.save_button = ctk.CTkButton(
            right, text="+  Simpan Karyawan", height=48, corner_radius=11,
            fg_color=self.colors["primary"], hover_color=self.colors["primary_hover"],
            text_color="#062A27", font=(self.font_name, 12, "bold"), command=self.save,
        )
        self.save_button.grid(row=3, column=0, padx=(0, 8), pady=(10, 8), sticky="ew")
        ctk.CTkButton(
            right, text="Bersihkan Form", height=38, corner_radius=10,
            fg_color="transparent", border_width=1, border_color=self.colors["border"],
            hover_color=self.colors["surface_alt"], text_color=self.colors["muted"],
            command=self.clear_form,
        ).grid(row=4, column=0, padx=(0, 8), pady=(0, 12), sticky="ew")
        self.after(100, self.id_entry.focus_set)

    def add_field(self, parent, label, placeholder, row, numeric=False):
        ctk.CTkLabel(parent, text=label, font=(self.font_name, 9, "bold"),
                     text_color=self.colors["muted"]).grid(
            row=row, column=0, padx=18, pady=(16 if row == 0 else 12, 5), sticky="w")
        entry = ctk.CTkEntry(
            parent, height=40, corner_radius=9, border_color=self.colors["border"],
            fg_color=self.colors["bg"], placeholder_text=placeholder,
            font=(self.font_name, 11),
        )
        if numeric:
            entry.configure(validate="key", validatecommand=(self.register(self.only_digits), "%P"))
        entry.grid(row=row + 1, column=0, padx=18, sticky="ew")
        return entry

    def add_photo_field(self, parent, row):
        ctk.CTkLabel(
            parent, text="FOTO KARYAWAN", font=(self.font_name, 9, "bold"),
            text_color=self.colors["muted"],
        ).grid(row=row, column=0, padx=18, pady=(12, 5), sticky="w")
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row + 1, column=0, padx=18, pady=(0, 16), sticky="ew")
        frame.grid_columnconfigure(1, weight=1)
        self.photo_preview = ctk.CTkLabel(
            frame, text="Foto", width=52, height=52, corner_radius=10,
            fg_color=self.colors["surface_alt"], text_color=self.colors["muted"],
            font=(self.font_name, 9),
        )
        self.photo_preview.grid(row=0, column=0, padx=(0, 8))
        ctk.CTkEntry(
            frame, textvariable=self.photo_path, height=40, state="disabled",
            fg_color=self.colors["bg"], border_color=self.colors["border"],
            placeholder_text="Belum ada foto",
        ).grid(row=0, column=1, padx=(0, 7), sticky="ew")
        ctk.CTkButton(
            frame, text="Pilih", width=58, height=40, corner_radius=9,
            fg_color=self.colors["surface_alt"], hover_color=self.colors["primary_hover"],
            text_color=self.colors["text"], command=self.choose_photo,
        ).grid(row=0, column=2)

    def add_password_field(self, parent, row):
        ctk.CTkLabel(
            parent, text="PASSWORD LOGIN", font=(self.font_name, 9, "bold"),
            text_color=self.colors["muted"],
        ).grid(row=row, column=0, padx=18, pady=(12, 5), sticky="w")
        entry = ctk.CTkEntry(
            parent, height=40, corner_radius=9, border_color=self.colors["border"],
            fg_color=self.colors["bg"], placeholder_text="Minimal 6 karakter",
            show="*", font=(self.font_name, 11),
        )
        entry.grid(row=row + 1, column=0, padx=18, sticky="ew")
        return entry

    def add_position_dropdown(self, parent, row):
        ctk.CTkLabel(
            parent, text="JABATAN", font=(self.font_name, 9, "bold"),
            text_color=self.colors["muted"],
        ).grid(row=row, column=0, padx=18, pady=(12, 5), sticky="w")
        ctk.CTkOptionMenu(
            parent,
            values=["Kasir", "Admin", "Supervisor", "Gudang", "Pramuniaga"],
            variable=self.position_var, height=40, corner_radius=9,
            fg_color=self.colors["surface_alt"],
            button_color=self.colors["primary_hover"],
            button_hover_color=self.colors["primary"],
            font=(self.font_name, 11), dropdown_font=(self.font_name, 10),
        ).grid(row=row + 1, column=0, padx=18, sticky="ew")

    def add_salary_period_dropdown(self, parent, row):
        ctk.CTkLabel(
            parent, text="PERIODE GAJI", font=(self.font_name, 9, "bold"),
            text_color=self.colors["muted"],
        ).grid(row=row, column=0, padx=18, pady=(12, 5), sticky="w")
        ctk.CTkOptionMenu(
            parent, values=["Harian", "Mingguan", "Bulanan"],
            variable=self.salary_period_var, height=40, corner_radius=9,
            fg_color=self.colors["surface_alt"],
            button_color=self.colors["primary_hover"],
            button_hover_color=self.colors["primary"],
            font=(self.font_name, 11), dropdown_font=(self.font_name, 10),
        ).grid(row=row + 1, column=0, padx=18, sticky="ew")

    def choose_photo(self):
        path = filedialog.askopenfilename(
            parent=self, title="Pilih Foto Karyawan",
            filetypes=[("File gambar", "*.png *.jpg *.jpeg *.webp"), ("Semua file", "*.*")],
        )
        if not path:
            return
        try:
            self.set_photo_preview(path)
        except (OSError, ValueError):
            self.status_label.configure(text="File foto tidak dapat dibaca.", text_color=self.colors["danger"])

    def set_photo_preview(self, path):
        self.photo_image = ctk.CTkImage(Image.open(Path(path)), size=(52, 52))
        self.photo_preview.configure(text="", image=self.photo_image)
        self.photo_path.set(path)

    @staticmethod
    def only_digits(value):
        return value == "" or value.isdigit()

    @staticmethod
    def only_ktp(value):
        return value == "" or (value.isdigit() and len(value) <= 16)

    @staticmethod
    def rupiah(value):
        return f"Rp {value:,.0f}".replace(",", ".")

    def load_employees(self):
        self.rows = self.on_load()
        self.filter_employees()
        self.set_auto_id()

    def set_auto_id(self):
        numbers = []
        for row in self.rows:
            employee_id = str(row[0]).upper()
            if employee_id.startswith(self.store_code):
                suffix = employee_id[len(self.store_code):]
                if suffix.isdigit():
                    numbers.append(int(suffix))
        next_number = max(numbers, default=0) + 1
        self.id_entry.configure(state="normal")
        self.id_entry.delete(0, "end")
        self.id_entry.insert(0, f"{self.store_code}{next_number:03d}")
        self.id_entry.configure(state="disabled")

    def filter_employees(self):
        for item in self.table.get_children():
            self.table.delete(item)
        self.table_images.clear()
        query = self.search_entry.get().strip().casefold()
        rows = [row for row in self.rows if not query or any(
            query in str(value).casefold() for value in row[:4]
        )]
        for employee_id, name, phone, position, salary, no_ktp, photo, period in rows:
            thumbnail = self.load_table_photo(photo)
            self.table.insert(
                "", "end", text="", image=thumbnail,
                values=(employee_id, name, no_ktp, phone, position, self.rupiah(salary), period),
            )
        self.count_label.configure(text=f"{len(rows)} dari {len(self.rows)} karyawan ditampilkan")

    def load_table_photo(self, photo_path):
        path = Path(photo_path) if photo_path else None
        if not path or not path.is_file():
            return ""
        try:
            image = Image.open(path).convert("RGB")
            image.thumbnail((34, 34), Image.Resampling.LANCZOS)
            thumbnail = ImageTk.PhotoImage(image)
            self.table_images.append(thumbnail)
            return thumbnail
        except (OSError, ValueError):
            return ""

    def show_id_card(self):
        selected = self.table.selection()
        if not selected:
            self.count_label.configure(text="Pilih karyawan untuk melihat ID Card.")
            return
        employee_id = str(self.table.item(selected[0], "values")[0])
        employee = next((row for row in self.rows if row[0] == employee_id), None)
        if employee:
            IDCardKaryawan(
                self, self.colors, self.store_name, self.store_code,
                employee, self.font_name,
            )

    def edit_selected(self):
        selected = self.table.selection()
        if not selected:
            self.count_label.configure(text="Pilih karyawan yang ingin diedit.")
            return
        employee_id = str(self.table.item(selected[0], "values")[0])
        employee = next((row for row in self.rows if row[0] == employee_id), None)
        if not employee:
            return
        self.clear_form(reset_status=False)
        employee_id, name, phone, position, salary, no_ktp, photo, period = employee
        self.id_entry.configure(state="normal")
        self.id_entry.delete(0, "end")
        self.id_entry.insert(0, employee_id)
        self.id_entry.configure(state="disabled")
        self.name_entry.insert(0, name)
        self.phone_entry.insert(0, phone)
        self.ktp_entry.insert(0, no_ktp)
        self.position_var.set(position)
        self.salary_entry.insert(0, str(salary))
        self.salary_period_var.set(period)
        if photo and Path(photo).is_file():
            self.set_photo_preview(photo)
        self.editing_id = employee_id
        self.password_entry.configure(placeholder_text="Kosongkan jika tidak diubah")
        self.save_button.configure(text="Simpan Perubahan")
        self.status_label.configure(
            text=f"Mode edit: {name}", text_color=self.colors["warning"]
        )
        self.name_entry.focus_set()

    def save(self):
        values = [
            self.id_entry.get().strip(), self.name_entry.get().strip(),
            self.phone_entry.get().strip(), self.ktp_entry.get().strip(),
            self.position_var.get().strip(), self.salary_entry.get().strip(),
            self.salary_period_var.get().strip(), self.password_entry.get(),
        ]
        required_values = values[:7]
        if not all(required_values) or not self.photo_path.get():
            self.status_label.configure(text="Semua data karyawan wajib diisi.", text_color=self.colors["danger"])
            return
        if len(values[3]) != 16:
            self.status_label.configure(text="Nomor KTP harus tepat 16 digit.", text_color=self.colors["danger"])
            return
        if int(values[5]) <= 0:
            self.status_label.configure(text="Gaji harus lebih besar dari nol.", text_color=self.colors["danger"])
            return
        if not self.editing_id and len(values[7]) < 6:
            self.status_label.configure(
                text="Password minimal 6 karakter.", text_color=self.colors["danger"]
            )
            return
        args = (
            values[0], values[1], values[2], values[4], int(values[5]),
            values[3], self.photo_path.get(), values[7], values[6],
        )
        success, message = self.on_update(*args) if self.editing_id else self.on_save(*args)
        self.status_label.configure(
            text=message, text_color=self.colors["success"] if success else self.colors["danger"]
        )
        if success:
            self.clear_form(reset_status=False)
            self.load_employees()

    def clear_form(self, reset_status=True):
        self.id_entry.configure(state="normal")
        for entry in (self.id_entry, self.name_entry, self.phone_entry, self.ktp_entry,
                      self.salary_entry, self.password_entry):
            entry.delete(0, "end")
        self.position_var.set("Kasir")
        self.salary_period_var.set("Bulanan")
        self.editing_id = None
        self.password_entry.configure(placeholder_text="Minimal 6 karakter")
        self.save_button.configure(text="+  Simpan Karyawan")
        self.photo_path.set("")
        self.photo_preview.configure(text="Foto", image=None)
        self.photo_image = None
        if reset_status:
            self.status_label.configure(text="Form telah dibersihkan.", text_color=self.colors["muted"])
        self.set_auto_id()
        self.name_entry.focus_set()
