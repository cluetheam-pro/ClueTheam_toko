import customtkinter as ctk

# 1. Pengaturan Dasar Tema
ctk.set_appearance_mode("Dark")  # Pilihan: "Dark", "Light", "System"
ctk.set_default_color_theme("blue")  # Tema warna tombol

class AplikasiKasir(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pengaturan Jendela Utama
        self.title("Software Toko - Modul Kasir")
        self.geometry("1024x720")
        
        # Membagi layar menjadi 2 kolom (Kiri 70%, Kanan 30%)
        self.grid_columnconfigure(0, weight=7)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # BAGIAN KIRI: Input Barcode & Daftar Belanja
        # ==========================================
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.left_frame.grid_rowconfigure(1, weight=1) # Agar area daftar belanja meluas
        self.left_frame.grid_columnconfigure(0, weight=1)

        # Baris Input Pencarian / Barcode
        self.search_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.search_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.search_frame.grid_columnconfigure(0, weight=1)

        self.entry_barcode = ctk.CTkEntry(self.search_frame, placeholder_text="Scan Barcode / Ketik Kode Barang...", font=("Arial", 16), height=45)
        self.entry_barcode.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.btn_cari = ctk.CTkButton(self.search_frame, text="Cari", font=("Arial", 14, "bold"), height=45, width=100)
        self.btn_cari.grid(row=0, column=1)

        # Tampilan Daftar Belanja (Menggunakan Textbox sebagai visualisasi sementara)
        self.cart_display = ctk.CTkTextbox(self.left_frame, font=("Courier New", 16))
        self.cart_display.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        # Data dummy untuk contoh tampilan
        self.cart_display.insert("0.0", "QTY  | NAMA BARANG                   | HARGA\n")
        self.cart_display.insert("end", "-"*65 + "\n")
        self.cart_display.insert("end", "2    | Kopi Hitam Instan             | Rp 15.000\n")
        self.cart_display.insert("end", "1    | Susu UHT 1 Liter              | Rp 18.500\n")
        self.cart_display.configure(state="disabled") # Dikunci agar tidak bisa diedit manual

        # ==========================================
        # BAGIAN KANAN: Panel Total & Tombol Aksi
        # ==========================================
        self.right_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.right_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        self.right_frame.grid_columnconfigure(0, weight=1)

        # Label Total Belanja
        self.lbl_title_total = ctk.CTkLabel(self.right_frame, text="TOTAL BELANJA", font=("Arial", 20, "bold"))
        self.lbl_title_total.grid(row=0, column=0, pady=(30, 0))

        self.lbl_nilai_total = ctk.CTkLabel(self.right_frame, text="Rp 33.500", font=("Arial", 48, "bold"), text_color="#2ecc71")
        self.lbl_nilai_total.grid(row=1, column=0, pady=(0, 40))

        # Tombol Aksi Kasir
        self.btn_bayar = ctk.CTkButton(self.right_frame, text="BAYAR [F12]", font=("Arial", 20, "bold"), height=70, fg_color="#27ae60", hover_color="#2ecc71")
        self.btn_bayar.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_batal = ctk.CTkButton(self.right_frame, text="BATAL [ESC]", font=("Arial", 16, "bold"), height=50, fg_color="#c0392b", hover_color="#e74c3c")
        self.btn_batal.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

if __name__ == "__main__":
    app = AplikasiKasir()
    # Memastikan kursor otomatis aktif di kolom barcode saat aplikasi dibuka
    app.entry_barcode.focus_set() 
    app.mainloop()