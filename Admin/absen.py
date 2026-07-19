"""Tab absensi masuk dan pulang karyawan."""

from datetime import datetime

import customtkinter as ctk
from tkinter import ttk


class AbsensiKaryawanTab(ctk.CTkFrame):
    def __init__(self, parent, colors, current_user, on_check_in, on_check_out,
                 on_load, font="Segoe UI"):
        super().__init__(parent, fg_color="transparent")
        self.colors = colors
        self.current_user = current_user
        self.on_check_in = on_check_in
        self.on_check_out = on_check_out
        self.on_load = on_load
        self.font_name = font
        self.clock_job = None
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.build_header()
        self.build_table()
        self.load_attendance()
        self.update_clock()

    def build_header(self):
        card = ctk.CTkFrame(self, corner_radius=16, fg_color=self.colors["surface"])
        card.grid(row=0, column=0, pady=(0, 16), sticky="ew")
        card.grid_columnconfigure(1, weight=1)
        title = ctk.CTkFrame(card, fg_color="transparent")
        title.grid(row=0, column=0, padx=20, pady=18, sticky="w")
        ctk.CTkLabel(
            title, text="Absensi Karyawan", font=(self.font_name, 20, "bold"),
            text_color=self.colors["text"],
        ).pack(anchor="w")
        self.clock_label = ctk.CTkLabel(
            title, text="", font=(self.font_name, 10), text_color=self.colors["muted"]
        )
        self.clock_label.pack(anchor="w", pady=(2, 0))

        controls = ctk.CTkFrame(card, fg_color="transparent")
        controls.grid(row=0, column=1, padx=20, pady=18, sticky="e")
        self.id_entry = ctk.CTkEntry(
            controls, width=190, height=42, corner_radius=10,
            border_color=self.colors["border"], fg_color=self.colors["bg"],
            placeholder_text="Scan barcode ID karyawan", font=(self.font_name, 11),
        )
        self.id_entry.pack(side="left", padx=(0, 8))
        if self.current_user[2].casefold() == "karyawan":
            self.id_entry.insert(0, self.current_user[0])
            self.id_entry.configure(state="disabled")
        self.id_entry.bind("<Return>", lambda _event: self.check_in())
        ctk.CTkButton(
            controls, text="Masuk", width=82, height=42, corner_radius=10,
            fg_color=self.colors["success"], hover_color="#16A34A",
            font=(self.font_name, 10, "bold"), command=self.check_in,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            controls, text="Pulang", width=82, height=42, corner_radius=10,
            fg_color=self.colors["warning"], hover_color="#D97706",
            text_color="#111827", font=(self.font_name, 10, "bold"),
            command=self.check_out,
        ).pack(side="left")
        self.status_label = ctk.CTkLabel(
            card, text="Pindai ID Card untuk melakukan absensi.",
            font=(self.font_name, 10), text_color=self.colors["muted"],
        )
        self.status_label.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 14), sticky="w")

    def build_table(self):
        card = ctk.CTkFrame(self, corner_radius=16, fg_color=self.colors["surface"])
        card.grid(row=1, column=0, sticky="nsew")
        card.grid_rowconfigure(2, weight=1)
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            card, text="Kehadiran Hari Ini", font=(self.font_name, 17, "bold"),
            text_color=self.colors["text"],
        ).grid(row=0, column=0, padx=18, pady=(18, 2), sticky="w")
        self.count_label = ctk.CTkLabel(
            card, text="0 karyawan hadir", font=(self.font_name, 10),
            text_color=self.colors["muted"],
        )
        self.count_label.grid(row=1, column=0, padx=18, pady=(0, 12), sticky="w")
        columns = ("id", "nama", "tanggal", "masuk", "pulang", "status")
        self.table = ttk.Treeview(card, columns=columns, show="headings", style="Kasir.Treeview")
        headings = {"id": "ID", "nama": "NAMA", "tanggal": "TANGGAL", "masuk": "JAM MASUK", "pulang": "JAM PULANG", "status": "STATUS"}
        widths = {"id": 90, "nama": 180, "tanggal": 105, "masuk": 95, "pulang": 95, "status": 85}
        for column in columns:
            self.table.heading(column, text=headings[column])
            self.table.column(column, width=widths[column], anchor="center")
        self.table.grid(row=2, column=0, padx=16, pady=(0, 16), sticky="nsew")

    def employee_id(self):
        return self.id_entry.get().strip().upper()

    def check_in(self):
        success, message = self.on_check_in(self.employee_id())
        self.show_result(success, message)

    def check_out(self):
        success, message = self.on_check_out(self.employee_id())
        self.show_result(success, message)

    def show_result(self, success, message):
        self.status_label.configure(
            text=message, text_color=self.colors["success"] if success else self.colors["danger"]
        )
        if success:
            self.load_attendance()
            if self.current_user[2].casefold() == "admin":
                self.id_entry.delete(0, "end")
                self.id_entry.focus_set()

    def load_attendance(self):
        rows = self.on_load()
        for item in self.table.get_children():
            self.table.delete(item)
        for row in rows:
            self.table.insert("", "end", values=row)
        self.count_label.configure(text=f"{len(rows)} karyawan tercatat hari ini")

    def update_clock(self):
        self.clock_label.configure(text=datetime.now().strftime("%A, %d %B %Y • %H:%M:%S"))
        self.clock_job = self.after(1000, self.update_clock)

    def destroy(self):
        if self.clock_job:
            self.after_cancel(self.clock_job)
        super().destroy()
