"""Form input barang khusus Administrator."""

from pathlib import Path

import customtkinter as ctk
from PIL import Image
from tkinter import ttk


THEME_DIR = Path(__file__).resolve().parent / "Theme"
LOGO_PATH = THEME_DIR / "Clue_Theam.png"
ICON_PATH = THEME_DIR / "Clue_Theam.ico"


class InputBarangTab(ctk.CTkFrame):
    def __init__(self, parent, colors, on_save, on_update, on_load, font="Segoe UI"):
        super().__init__(parent, fg_color="transparent")
        self.colors = colors
        self.on_save = on_save
        self.on_update = on_update
        self.on_load = on_load
        self.font_name = font
        self.logo_image = None
        self.editing_code = None
        self.product_rows = []
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        self.build()
        self.load_products()

    def build(self):
        self.build_product_table()
        right = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0,
            scrollbar_button_color=self.colors["surface_alt"],
            scrollbar_button_hover_color=self.colors["primary_hover"],
        )
        right.grid(row=0, column=1, padx=(16, 0), sticky="nsew")
        right.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(right, corner_radius=16, fg_color=self.colors["surface"])
        header.grid(row=0, column=0, padx=(0, 8), pady=(0, 14), sticky="ew")
        self.create_logo(header, 50).pack(side="left", padx=(16, 12), pady=16)
        title = ctk.CTkFrame(header, fg_color="transparent")
        title.pack(side="left", pady=15)
        ctk.CTkLabel(
            title, text="Input Barang", font=(self.font_name, 21, "bold"),
            text_color=self.colors["text"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            title, text="Khusus Administrator", font=(self.font_name, 9, "bold"),
            text_color=self.colors["primary"],
        ).pack(anchor="w", pady=(2, 0))

        card = ctk.CTkFrame(
            right, corner_radius=15, fg_color=self.colors["surface"],
            border_width=1, border_color=self.colors["border"],
        )
        card.grid(row=1, column=0, padx=(0, 8), sticky="ew")
        card.grid_columnconfigure(0, weight=1)
        self.code_entry = self.add_field(card, "KODE / BARCODE", "Contoh: 004", 0)
        self.name_entry = self.add_field(card, "NAMA BARANG", "Nama produk", 2)
        self.purchase_entry = self.add_price_field(card, "HARGA BELI / MODAL", 4)
        self.purchase_entry.configure(
            validate="key", validatecommand=(self.register(self.validate_price), "%P")
        )
        self.price_entry = self.add_price_field(card, "HARGA JUAL", 6)
        self.price_entry.configure(
            validate="key", validatecommand=(self.register(self.on_price_change), "%P")
        )
        self.add_packaging_field(card, 8)
        self.price_preview = ctk.CTkLabel(
            card, text="Rp 0", font=(self.font_name, 10, "bold"),
            text_color=self.colors["primary"],
        )
        self.price_preview.grid(row=10, column=0, padx=18, pady=(7, 15), sticky="e")
        self.status_label = ctk.CTkLabel(
            right, text="Isi semua informasi barang dengan benar.",
            font=(self.font_name, 9), text_color=self.colors["muted"]
        )
        self.status_label.grid(row=2, column=0, padx=2, pady=(10, 0), sticky="w")
        self.save_button = ctk.CTkButton(
            right, text="＋  Simpan Barang", height=48, corner_radius=11,
            fg_color=self.colors["primary"], hover_color=self.colors["primary_hover"],
            text_color="#062A27", font=(self.font_name, 12, "bold"), command=self.save,
        )
        self.save_button.grid(row=3, column=0, padx=(0, 8), pady=(10, 8), sticky="ew")
        ctk.CTkButton(
            right, text="Bersihkan Form", height=38, corner_radius=10, fg_color="transparent",
            border_width=1, border_color=self.colors["border"],
            hover_color=self.colors["surface_alt"], text_color=self.colors["muted"],
            command=self.clear_form,
        ).grid(row=4, column=0, padx=(0, 8), pady=(0, 12), sticky="ew")
        self.after(120, self.code_entry.focus_set)

    def build_product_table(self):
        table_card = ctk.CTkFrame(self, corner_radius=16, fg_color=self.colors["surface"])
        table_card.grid(row=0, column=0, sticky="nsew")
        table_card.grid_rowconfigure(3, weight=1)
        table_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            table_card, text="Daftar Barang", font=(self.font_name, 20, "bold"),
            text_color=self.colors["text"],
        ).grid(row=0, column=0, padx=18, pady=(20, 2), sticky="w")
        self.count_label = ctk.CTkLabel(
            table_card, text="0 produk tersimpan", font=(self.font_name, 10),
            text_color=self.colors["muted"],
        )
        self.count_label.grid(row=1, column=0, padx=18, pady=(0, 14), sticky="w")
        search_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        search_frame.grid(row=2, column=0, columnspan=2, padx=16, pady=(0, 12), sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)
        self.search_entry = ctk.CTkEntry(
            search_frame, height=38, corner_radius=9, border_color=self.colors["border"],
            fg_color=self.colors["bg"], placeholder_text="Cari kode atau nama barang...",
            font=(self.font_name, 10),
        )
        self.search_entry.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda _event: self.filter_products())
        ctk.CTkButton(
            search_frame, text="Edit Terpilih", width=105, height=38, corner_radius=9,
            fg_color=self.colors["surface_alt"], hover_color=self.colors["primary_hover"],
            text_color=self.colors["text"], font=(self.font_name, 10, "bold"),
            command=self.edit_selected,
        ).grid(row=0, column=1)

        columns = ("kode", "nama", "beli", "jual", "kemasan")
        self.product_table = ttk.Treeview(
            table_card, columns=columns, show="headings", style="Kasir.Treeview"
        )
        vertical_scroll = ttk.Scrollbar(
            table_card, orient="vertical", command=self.product_table.yview
        )
        horizontal_scroll = ttk.Scrollbar(
            table_card, orient="horizontal", command=self.product_table.xview
        )
        self.product_table.configure(
            yscrollcommand=vertical_scroll.set, xscrollcommand=horizontal_scroll.set
        )
        self.product_table.bind("<Double-1>", lambda _event: self.edit_selected())
        headings = {
            "kode": "KODE", "nama": "NAMA BARANG", "beli": "HARGA BELI",
            "jual": "HARGA JUAL", "kemasan": "ISI DUS",
        }
        widths = {"kode": 72, "nama": 150, "beli": 95, "jual": 95, "kemasan": 75}
        for column in columns:
            self.product_table.heading(column, text=headings[column])
            self.product_table.column(
                column, width=widths[column], minwidth=55,
                anchor="w" if column == "nama" else "center",
            )
        self.product_table.grid(row=3, column=0, padx=(16, 0), sticky="nsew")
        vertical_scroll.grid(row=3, column=1, padx=(0, 16), sticky="ns")
        horizontal_scroll.grid(row=4, column=0, padx=(16, 0), pady=(0, 16), sticky="ew")

    @staticmethod
    def rupiah(value):
        return f"Rp {value:,.0f}".replace(",", ".")

    def load_products(self):
        self.product_rows = self.on_load()
        self.filter_products()

    def filter_products(self):
        for item in self.product_table.get_children():
            self.product_table.delete(item)
        query = self.search_entry.get().strip().casefold()
        rows = [
            row for row in self.product_rows
            if not query or query in row[0].casefold() or query in row[1].casefold()
        ]
        for kode, nama, harga_beli, harga_jual, isi_per_dus, satuan in rows:
            self.product_table.insert(
                "", "end",
                values=(kode, nama, self.rupiah(harga_beli), self.rupiah(harga_jual),
                        f"{isi_per_dus} {satuan}"),
            )
        self.count_label.configure(
            text=f"{len(rows)} dari {len(self.product_rows)} produk ditampilkan"
        )

    def edit_selected(self):
        selected = self.product_table.selection()
        if not selected:
            self.count_label.configure(text="Pilih barang yang ingin diedit.")
            return
        code = str(self.product_table.item(selected[0], "values")[0])
        row = next((item for item in self.product_rows if item[0] == code), None)
        if not row:
            return
        self.clear_form(reset_status=False)
        kode, nama, harga_beli, harga_jual, isi_per_dus, satuan = row
        self.code_entry.insert(0, kode)
        self.code_entry.configure(state="disabled")
        self.name_entry.insert(0, nama)
        self.purchase_entry.insert(0, str(harga_beli))
        self.price_entry.insert(0, str(harga_jual))
        self.pack_entry.delete(0, "end")
        self.pack_entry.insert(0, str(isi_per_dus))
        self.unit_var.set(satuan)
        self.editing_code = kode
        self.save_button.configure(text="Simpan Perubahan")
        self.status_label.configure(
            text=f"Mode edit: {nama}", text_color=self.colors["warning"]
        )
        self.name_entry.focus_set()

    def add_field(self, parent, label, placeholder, row):
        ctk.CTkLabel(
            parent, text=label, font=(self.font_name, 9, "bold"),
            text_color=self.colors["muted"],
        ).grid(row=row, column=0, padx=18, pady=(16 if row == 0 else 12, 5), sticky="w")
        entry = ctk.CTkEntry(
            parent, height=40, corner_radius=9, border_color=self.colors["border"],
            fg_color=self.colors["bg"], placeholder_text=placeholder,
            font=(self.font_name, 11),
        )
        entry.grid(row=row + 1, column=0, padx=18, sticky="ew")
        return entry

    def add_price_field(self, parent, label, row):
        ctk.CTkLabel(
            parent, text=label, font=(self.font_name, 9, "bold"),
            text_color=self.colors["muted"],
        ).grid(row=row, column=0, padx=18, pady=(12, 5), sticky="w")
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row + 1, column=0, padx=18, sticky="ew")
        frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            frame, text="Rp", width=48, height=40, corner_radius=9,
            fg_color=self.colors["surface_alt"], text_color=self.colors["text"],
            font=(self.font_name, 11, "bold"),
        ).grid(row=0, column=0, padx=(0, 7))
        entry = ctk.CTkEntry(
            frame, height=40, corner_radius=9, border_color=self.colors["border"],
            fg_color=self.colors["bg"], placeholder_text="15000",
            font=(self.font_name, 11),
        )
        entry.grid(row=0, column=1, sticky="ew")
        return entry

    def add_packaging_field(self, parent, row):
        ctk.CTkLabel(
            parent, text="ISI PER DUS", font=(self.font_name, 9, "bold"),
            text_color=self.colors["muted"],
        ).grid(row=row, column=0, padx=18, pady=(12, 5), sticky="w")
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row + 1, column=0, padx=18, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)
        self.pack_entry = ctk.CTkEntry(
            frame, height=40, corner_radius=9, border_color=self.colors["border"],
            fg_color=self.colors["bg"], placeholder_text="10",
            font=(self.font_name, 11), validate="key",
            validatecommand=(self.register(self.validate_price), "%P"),
        )
        self.pack_entry.grid(row=0, column=0, padx=(0, 7), sticky="ew")
        self.pack_entry.insert(0, "10")
        self.unit_var = ctk.StringVar(value="Pak")
        ctk.CTkOptionMenu(
            frame, values=["Pak", "Pcs", "Botol", "Kaleng", "Sachet"],
            variable=self.unit_var, width=105, height=40, corner_radius=9,
            fg_color=self.colors["surface_alt"], button_color=self.colors["primary_hover"],
        ).grid(row=0, column=1)

    @staticmethod
    def validate_price(value):
        return value == "" or value.isdigit()

    def on_price_change(self, value):
        if not self.validate_price(value):
            return False
        amount = int(value) if value else 0
        if hasattr(self, "price_preview"):
            self.price_preview.configure(text=f"Rp {amount:,.0f}".replace(",", "."))
        return True

    def save(self):
        code = self.code_entry.get().strip()
        name = self.name_entry.get().strip()
        purchase_price = self.purchase_entry.get().strip()
        sale_price = self.price_entry.get().strip()
        pack_size = self.pack_entry.get().strip()
        if not code or not name or not purchase_price or not sale_price or not pack_size:
            self.status_label.configure(text="Semua informasi barang wajib diisi.")
            return
        if min(int(purchase_price), int(sale_price), int(pack_size)) <= 0:
            self.status_label.configure(text="Harga dan isi dus harus lebih besar dari nol.")
            return
        values = (
            code, name, int(purchase_price), int(sale_price),
            int(pack_size), self.unit_var.get(),
        )
        success, message = (
            self.on_update(*values) if self.editing_code else self.on_save(*values)
        )
        if success:
            self.status_label.configure(text=message, text_color=self.colors["success"])
            self.code_entry.configure(state="normal")
            self.code_entry.delete(0, "end")
            self.name_entry.delete(0, "end")
            self.purchase_entry.delete(0, "end")
            self.price_entry.delete(0, "end")
            self.pack_entry.delete(0, "end")
            self.pack_entry.insert(0, "10")
            self.editing_code = None
            self.save_button.configure(text="+  Simpan Barang")
            self.code_entry.focus_set()
            self.load_products()
        else:
            self.status_label.configure(text=message, text_color=self.colors["danger"])

    def clear_form(self, reset_status=True):
        self.code_entry.configure(state="normal")
        for entry in (self.code_entry, self.name_entry, self.purchase_entry, self.price_entry, self.pack_entry):
            entry.delete(0, "end")
        self.pack_entry.insert(0, "10")
        self.unit_var.set("Pak")
        self.editing_code = None
        self.save_button.configure(text="+  Simpan Barang")
        self.price_preview.configure(text="Rp 0")
        if reset_status:
            self.status_label.configure(
                text="Form telah dibersihkan.", text_color=self.colors["muted"]
            )
        self.code_entry.focus_set()

    def create_logo(self, parent, size):
        if LOGO_PATH.is_file():
            try:
                self.logo_image = ctk.CTkImage(Image.open(LOGO_PATH), size=(size, size))
                return ctk.CTkLabel(parent, text="", image=self.logo_image, width=size, height=size)
            except (OSError, ValueError):
                pass
        return ctk.CTkLabel(
            parent, text="C", width=size, height=size, corner_radius=13,
            fg_color=self.colors["primary"], text_color="#062A27",
            font=(self.font_name, 22, "bold"),
        )
