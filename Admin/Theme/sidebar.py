"""Komponen sidebar navigasi CLue Theam."""

import customtkinter as ctk


class SidebarKasir(ctk.CTkFrame):
    """Sidebar berisi navigasi, profil kasir, dan tombol keluar."""

    def __init__(self, parent, colors, current_user, on_transaction, on_attendance,
                 on_products, on_employees, on_settings, on_logout,
                 active_page="transaksi", font="Segoe UI"):
        super().__init__(parent, width=224, corner_radius=0, fg_color=colors["sidebar"])
        self.colors = colors
        self.current_user = current_user
        self.on_transaction = on_transaction
        self.on_attendance = on_attendance
        self.on_products = on_products
        self.on_employees = on_employees
        self.active_page = active_page
        self.on_settings = on_settings
        self.on_logout = on_logout
        self.font_name = font

        self.grid_propagate(False)
        self.grid_rowconfigure(8, weight=1)
        self.build_brand()
        self.build_navigation()
        self.build_profile()

    def build_brand(self):
        brand = ctk.CTkFrame(self, fg_color="transparent")
        brand.grid(row=0, column=0, padx=22, pady=(30, 35), sticky="ew")
        ctk.CTkLabel(
            brand, text="CLUE  •  KASIR", text_color=self.colors["primary"],
            font=(self.font_name, 13, "bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            brand, text="Panel navigasi", text_color=self.colors["muted"],
            font=(self.font_name, 10),
        ).pack(anchor="w", pady=(3, 0))

    def build_navigation(self):
        ctk.CTkLabel(
            self, text="MENU UTAMA", text_color=self.colors["muted"],
            font=(self.font_name, 10, "bold"),
        ).grid(row=1, column=0, padx=24, pady=(0, 10), sticky="w")
        self.nav_button("▣   Transaksi", 2, active=self.active_page == "transaksi",
                        command=self.on_transaction)
        self.nav_button("✓   Absensi", 3, active=self.active_page == "absensi",
                        command=self.on_attendance)
        self.nav_button("▤   Riwayat", 4)
        is_admin = self.current_user[2].casefold() == "admin"
        self.nav_button("□   Produk" if is_admin else "🔒   Produk", 5,
                        active=self.active_page == "produk",
                        command=self.on_products if is_admin else None,
                        disabled=not is_admin)
        self.nav_button("♙   Karyawan" if is_admin else "🔒   Karyawan", 6,
                        active=self.active_page == "karyawan",
                        command=self.on_employees if is_admin else None,
                        disabled=not is_admin)
        self.nav_button("⚙   Pengaturan", 7, command=self.on_settings)

    def nav_button(self, text, row, active=False, command=None, disabled=False):
        ctk.CTkButton(
            self, text=text, anchor="w", height=44, corner_radius=10,
            fg_color=self.colors["surface_alt"] if active else "transparent",
            hover_color=self.colors["surface_alt"],
            text_color=self.colors["primary"] if active else self.colors["muted"],
            font=(self.font_name, 12, "bold" if active else "normal"),
            command=command, state="disabled" if disabled else "normal",
        ).grid(row=row, column=0, padx=14, pady=3, sticky="ew")

    def build_profile(self):
        username, name, role = self.current_user
        profile = ctk.CTkFrame(self, fg_color=self.colors["surface"], corner_radius=14)
        profile.grid(row=9, column=0, padx=16, pady=18, sticky="ew")
        ctk.CTkLabel(
            profile, text=name[:1].upper(), width=36, height=36, corner_radius=18,
            fg_color=self.colors["surface_alt"], font=(self.font_name, 14, "bold"),
        ).pack(side="left", padx=12, pady=12)
        info = ctk.CTkFrame(profile, fg_color="transparent")
        info.pack(side="left", pady=10)
        ctk.CTkLabel(
            info, text=name, font=(self.font_name, 12, "bold"),
            text_color=self.colors["text"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            info, text=f"{role} • Shift aktif", font=(self.font_name, 10),
            text_color=self.colors["success"],
        ).pack(anchor="w")
        ctk.CTkButton(
            self, text="Keluar", height=34, corner_radius=9, fg_color="transparent",
            hover_color=self.colors["surface_alt"], text_color=self.colors["muted"],
            command=self.on_logout,
        ).grid(row=10, column=0, padx=16, pady=(0, 18), sticky="ew")
