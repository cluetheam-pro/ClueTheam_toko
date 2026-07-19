"""Tampilan kartu identitas karyawan CLue Theam."""

from pathlib import Path
import os

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageTk
from tkinter import messagebox


THEME_DIR = Path(__file__).resolve().parent / "Theme"
LOGO_PATH = THEME_DIR / "Clue_Theam.png"
ICON_PATH = THEME_DIR / "Clue_Theam.ico"
IDCARD_OUTPUT_DIR = Path(__file__).resolve().parent / "IDCards"

CARD_THEMES = {
    "Hijau": {"primary": "#18A66A", "dark": "#087A4B", "pale": "#EAF8F1"},
    "Biru": {"primary": "#2563EB", "dark": "#1E40AF", "pale": "#EFF6FF"},
    "Merah": {"primary": "#DC2626", "dark": "#991B1B", "pale": "#FEF2F2"},
    "Ungu": {"primary": "#7C3AED", "dark": "#5B21B6", "pale": "#F5F3FF"},
}

CODE39 = {
    "0": "nnwwnwnnn", "1": "wnnwnnnnw", "2": "nnwwnnnnw",
    "3": "wnwwnnnnn", "4": "nnnwwnnnw", "5": "wnnwwnnnn",
    "6": "nnwwwnnnn", "7": "nnnwnnwnw", "8": "wnnwnnwnn",
    "9": "nnwwnnwnn", "A": "wnnnnwnnw", "B": "nnwnnwnnw",
    "C": "wnwnnwnnn", "D": "nnnnwwnnw", "E": "wnnnwwnnn",
    "F": "nnwnwwnnn", "G": "nnnnnwwnw", "H": "wnnnnwwnn",
    "I": "nnwnnwwnn", "J": "nnnnwwwnn", "K": "wnnnnnnww",
    "L": "nnwnnnnww", "M": "wnwnnnnwn", "N": "nnnnwnnww",
    "O": "wnnnwnnwn", "P": "nnwnwnnwn", "Q": "nnnnnnwww",
    "R": "wnnnnnwwn", "S": "nnwnnnwwn", "T": "nnnnwnwwn",
    "U": "wwnnnnnnw", "V": "nwwnnnnnw", "W": "wwwnnnnnn",
    "X": "nwnnwnnnw", "Y": "wwnnwnnnn", "Z": "nwwnwnnnn",
    "-": "nwnnnnwnw", "*": "nwnnwnwnn",
}


class IDCardKaryawan(ctk.CTkToplevel):
    def __init__(self, parent, colors, store_name, store_code, employee,
                 font="Segoe UI"):
        super().__init__(parent, fg_color=colors["bg"])
        self.colors = colors
        self.store_name = store_name
        self.store_code = store_code
        self.employee = employee
        self.font_name = font
        self.card_images = []
        self.card_labels = []
        self.theme_var = ctk.StringVar(value="Hijau")
        self.window_icon = None
        self.title("ID Card Karyawan")
        self.geometry("720x675")
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.grid_columnconfigure(0, weight=1)
        self.build()
        self.after(100, self.apply_icon)
        self.after(600, self.apply_icon)

    def build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        for column, label in enumerate(("DEPAN", "BELAKANG")):
            strap = ctk.CTkFrame(
                self, width=18, height=54, corner_radius=0, fg_color="#111827"
            )
            strap.grid(row=0, column=column)
            strap.grid_propagate(False)
            ctk.CTkLabel(
                self, text="○", width=26, height=26, font=(self.font_name, 24),
                text_color="#9CA3AF",
            ).grid(row=1, column=column, pady=0)
            card_label = ctk.CTkLabel(
                self, text="", width=300, height=460,
                corner_radius=6, fg_color="#FFFFFF",
            )
            card_label.grid(row=2, column=column, padx=25)
            self.card_labels.append(card_label)
            ctk.CTkLabel(
                self, text=label, font=(self.font_name, 9, "bold"),
                text_color=self.colors["muted"],
            ).grid(row=3, column=column, pady=(8, 16))

        toolbar = ctk.CTkFrame(self, fg_color=self.colors["surface"], corner_radius=12)
        toolbar.grid(row=4, column=0, columnspan=2, padx=25, pady=(0, 18), sticky="ew")
        ctk.CTkLabel(
            toolbar, text="Tema ID Card", font=(self.font_name, 10, "bold"),
            text_color=self.colors["muted"],
        ).pack(side="left", padx=(16, 10), pady=10)
        ctk.CTkOptionMenu(
            toolbar, values=list(CARD_THEMES), variable=self.theme_var,
            width=120, height=36, corner_radius=9,
            fg_color=self.colors["surface_alt"],
            button_color=self.colors.get("primary_hover", "#0D9488"),
            command=lambda _value: self.refresh_cards(),
        ).pack(side="left", pady=10)
        ctk.CTkButton(
            toolbar, text="Print ID Card", width=130, height=36, corner_radius=9,
            fg_color=self.colors.get("primary", "#14B8A6"),
            hover_color=self.colors.get("primary_hover", "#0D9488"),
            text_color="#062A27", font=(self.font_name, 10, "bold"),
            command=self.print_cards,
        ).pack(side="right", padx=16, pady=10)
        self.refresh_cards()

    def refresh_cards(self):
        rendered_cards = (self.render_id_card(), self.render_back_card())
        self.card_images.clear()
        for label, rendered in zip(self.card_labels, rendered_cards):
            card_image = ctk.CTkImage(
                light_image=rendered, dark_image=rendered, size=(300, 460)
            )
            self.card_images.append(card_image)
            label.configure(image=card_image)

    def current_palette(self):
        return CARD_THEMES.get(self.theme_var.get(), CARD_THEMES["Hijau"])

    def render_id_card(self):
        employee_id, name, _phone, position, _salary, _no_ktp, photo = self.employee[:7]
        card = Image.new("RGB", (600, 920), "#FCFDFD")
        draw = ImageDraw.Draw(card)
        palette = self.current_palette()
        green, dark_green, pale_green = palette["primary"], palette["dark"], palette["pale"]

        # Komposisi warna bertingkat yang tetap bersih di semua tema.
        self.draw_smooth_accents(card, [
            ("ellipse", (-120, -370, 720, 170), green, 0),
            ("ellipse", (430, -250, 750, 150), dark_green, 0),
            ("ellipse", (-110, 800, 710, 1080), green, 0),
            ("ellipse", (-280, 785, 185, 1030), dark_green, 0),
            ("rounded", (28, 350, 42, 680), pale_green, 7),
        ])
        draw = ImageDraw.Draw(card)

        # Lubang gantungan kartu.
        draw.rounded_rectangle((255, 20, 345, 42), radius=10, fill="#0B6441")

        # Foto berbentuk kotak potret dengan sudut sedikit membulat.
        photo_width, photo_height = 168, 188
        try:
            portrait = Image.open(Path(photo)).convert("RGB")
            portrait = ImageOps.fit(
                portrait, (photo_width, photo_height), Image.Resampling.LANCZOS
            )
        except (OSError, ValueError):
            portrait = Image.new("RGB", (photo_width, photo_height), "#D1FAE5")
            fallback = ImageDraw.Draw(portrait)
            fallback.text((62, 56), name[:1].upper(), fill=dark_green,
                          font=self.font(64, bold=True))
        mask = self.smooth_rounded_mask((photo_width, photo_height), 22)
        self.draw_smooth_accents(card, [
            ("rounded", (206, 125, 394, 333), dark_green, 30),
            ("rounded", (211, 130, 389, 328), green, 26),
        ])
        card.paste(portrait, (216, 135), mask)
        draw = ImageDraw.Draw(card)

        self.center_text(draw, name.upper(), 366, self.font(31, bold=True), "#111827")
        self.center_text(draw, position.upper(), 410, self.font(21, bold=True), green)
        draw.line((190, 451, 410, 451), fill="#D1D5DB", width=2)
        self.draw_brand(card, draw, 470, self.font(22, bold=True), dark_green)
        self.center_text(draw, "KARTU IDENTITAS KARYAWAN", 514, self.font(15), "#6B7280")

        barcode = self.make_barcode(employee_id)
        barcode = ImageOps.contain(barcode, (350, 86), Image.Resampling.NEAREST)
        card.paste(barcode, ((600 - barcode.width) // 2, 600))
        self.center_text(draw, employee_id, 700, self.font(20, bold=True), "#111827")
        self.center_text(draw, f"{self.store_code} • EMPLOYEE", 738, self.font(14), "#6B7280")

        self.center_text(draw, self.store_name, 872, self.font(21, bold=True), "white")
        return card

    def render_back_card(self):
        card = Image.new("RGB", (600, 920), "#FCFDFD")
        draw = ImageDraw.Draw(card)
        palette = self.current_palette()
        green, dark_green, pale_green = palette["primary"], palette["dark"], palette["pale"]

        self.draw_smooth_accents(card, [
            ("ellipse", (-120, -370, 720, 170), green, 0),
            ("ellipse", (430, -250, 750, 150), dark_green, 0),
            ("ellipse", (-110, 800, 710, 1080), green, 0),
            ("ellipse", (415, 785, 880, 1030), dark_green, 0),
            ("rounded", (558, 350, 572, 680), pale_green, 7),
        ])
        draw = ImageDraw.Draw(card)
        draw.rounded_rectangle((255, 20, 345, 42), radius=10, fill="#0B6441")

        self.draw_brand(card, draw, 165, self.font(27, bold=True), dark_green, logo_size=(68, 54))
        self.center_text(draw, "KETENTUAN KARTU KARYAWAN", 230, self.font(17, bold=True), "#111827")
        draw.line((105, 270, 495, 270), fill="#D1D5DB", width=2)

        rules = [
            "Kartu wajib digunakan selama jam kerja.",
            "Kartu tidak boleh dipindahtangankan.",
            "Kehilangan kartu segera dilaporkan ke Admin.",
            "Kartu merupakan milik perusahaan.",
        ]
        y = 310
        body_font = self.font(17)
        for index, rule in enumerate(rules, start=1):
            draw.ellipse((92, y + 4, 106, y + 18), fill=green)
            draw.text((122, y), f"{index}. {rule}", font=body_font, fill="#374151")
            y += 62

        self.center_text(draw, "Jika kartu ditemukan, harap dikembalikan ke:",
                         585, self.font(15), "#6B7280")
        self.center_text(draw, self.store_name, 616, self.font(20, bold=True), dark_green)

        draw.line((90, 740, 250, 740), fill="#9CA3AF", width=2)
        draw.line((350, 740, 510, 740), fill="#9CA3AF", width=2)
        self.center_column_text(draw, "Pemegang Kartu", 170, 754, self.font(14), "#6B7280")
        self.center_column_text(draw, "Management", 430, 754, self.font(14), "#6B7280")
        self.center_text(draw, f"{self.store_code} • EMPLOYEE IDENTIFICATION", 775,
                         self.font(14, bold=True), dark_green)
        self.center_text(draw, self.store_name, 872, self.font(21, bold=True), "white")
        return card

    def print_cards(self):
        """Menyimpan lembar depan-belakang lalu mencetak ke printer default."""
        employee_id = self.employee[0]
        front = self.render_id_card()
        back = self.render_back_card()
        sheet = Image.new("RGB", (1260, 980), "white")
        sheet.paste(front, (20, 30))
        sheet.paste(back, (640, 30))
        IDCARD_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output = IDCARD_OUTPUT_DIR / f"{employee_id}_idcard.png"
        try:
            sheet.save(output, "PNG", dpi=(300, 300))
            if os.name != "nt" or not hasattr(os, "startfile"):
                raise OSError("Fitur print hanya tersedia di Windows")
            os.startfile(str(output.resolve()), "print")
            messagebox.showinfo(
                "Print ID Card", "ID Card telah dikirim ke printer default.", parent=self
            )
        except OSError as error:
            messagebox.showerror(
                "Print gagal", f"ID Card tersimpan di:\n{output}\n\n{error}", parent=self
            )

    @staticmethod
    def draw_smooth_accents(card, shapes, scale=4):
        """Menggambar bidang lengkung anti-alias pada layer resolusi tinggi."""
        layer = Image.new("RGBA", (card.width * scale, card.height * scale), (0, 0, 0, 0))
        painter = ImageDraw.Draw(layer)
        for kind, box, fill, radius in shapes:
            scaled_box = tuple(int(value * scale) for value in box)
            if kind == "ellipse":
                painter.ellipse(scaled_box, fill=fill)
            else:
                painter.rounded_rectangle(scaled_box, radius=radius * scale, fill=fill)
        layer = layer.resize(card.size, Image.Resampling.LANCZOS)
        card.paste(layer, (0, 0), layer)

    @staticmethod
    def smooth_rounded_mask(size, radius, scale=4):
        mask = Image.new("L", (size[0] * scale, size[1] * scale), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            (0, 0, mask.width - 1, mask.height - 1), radius=radius * scale, fill=255
        )
        return mask.resize(size, Image.Resampling.LANCZOS)

    @staticmethod
    def font(size, bold=False):
        names = ("arialbd.ttf", "Arial Bold.ttf") if bold else ("arial.ttf", "Arial.ttf")
        for name in names:
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                continue
        return ImageFont.load_default()

    @staticmethod
    def center_text(draw, text, y, font, fill):
        box = draw.textbbox((0, 0), text, font=font)
        x = (600 - (box[2] - box[0])) // 2
        draw.text((x, y), text, font=font, fill=fill)

    @staticmethod
    def center_column_text(draw, text, center_x, y, font, fill):
        box = draw.textbbox((0, 0), text, font=font)
        x = center_x - (box[2] - box[0]) // 2
        draw.text((x, y), text, font=font, fill=fill)

    def draw_brand(self, card, draw, y, font, fill, logo_size=(54, 44)):
        text = self.store_name.upper()
        box = draw.textbbox((0, 0), text, font=font)
        text_width = box[2] - box[0]
        logo = None
        if LOGO_PATH.is_file():
            try:
                logo = Image.open(LOGO_PATH).convert("RGBA")
                logo.thumbnail(logo_size, Image.Resampling.LANCZOS)
            except OSError:
                logo = None
        logo_width = logo.width if logo else 0
        gap = 12 if logo else 0
        start_x = (600 - logo_width - gap - text_width) // 2
        if logo:
            logo_y = y + max(0, ((box[3] - box[1]) - logo.height) // 2)
            card.paste(logo, (start_x, logo_y), logo)
        draw.text((start_x + logo_width + gap, y), text, font=font, fill=fill)

    @staticmethod
    def make_barcode(value):
        """Membuat barcode Code 39 dari ID karyawan."""
        safe_value = "".join(char for char in value.upper() if char in CODE39 and char != "*")
        encoded = f"*{safe_value}*"
        narrow, wide, gap, quiet = 2, 5, 2, 12
        total_width = quiet * 2
        for char in encoded:
            total_width += sum(wide if unit == "w" else narrow for unit in CODE39[char]) + gap
        image = Image.new("RGB", (total_width, 54), "white")
        draw = ImageDraw.Draw(image)
        x = quiet
        for char in encoded:
            for index, unit in enumerate(CODE39[char]):
                width = wide if unit == "w" else narrow
                if index % 2 == 0:
                    draw.rectangle((x, 4, x + width - 1, 49), fill="black")
                x += width
            x += gap
        return image

    def apply_icon(self):
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
