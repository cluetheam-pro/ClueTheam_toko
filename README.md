# CLue Theam Toko

## Instalasi dua komputer

1. Salin aplikasi ke Komputer Utama dan Komputer Kasir.
2. Pada Komputer Utama, jalankan `python setup_komputer.py` lalu pilih **Komputer Utama**.
3. Bagikan folder `Admin` pada jaringan Windows dengan izin baca dan tulis.
4. Pada Komputer Kasir, jalankan `python setup_komputer.py` lalu pilih **Komputer Kasir**.
5. Pilih file `toko.db` dari folder jaringan Komputer Utama.
6. Jalankan aplikasi dengan `python main.py` pada kedua komputer.

Kedua komputer akan menggunakan database produk, transaksi, karyawan, absensi,
pengaturan, dan akun login yang sama.
