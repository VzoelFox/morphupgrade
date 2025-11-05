# tests/fixtures/pustaka_pinjaman.py

"""
Modul Python sederhana untuk diimpor oleh MORPH untuk pengujian FFI.
"""

NAMA_PUSTAKA = "Pustaka Uji Coba Pinjaman"

def tambah(a, b):
    """Fungsi sederhana yang menjumlahkan dua angka."""
    return a + b

def gabung_list(list1, list2):
    """Menggabungkan dua list dan mengembalikannya."""
    return list1 + list2

def buat_kamus(kunci, nilai):
    """Membuat kamus sederhana."""
    return {kunci: nilai}

def dapatkan_tuple():
    """Mengembalikan tuple, tipe data yang tidak didukung secara native oleh MORPH."""
    return (10, "dua puluh", True)

def gagal_dengan_pesan():
    """Fungsi yang selalu memunculkan pengecualian."""
    raise ValueError("Ini adalah pesan kesalahan dari Python.")

class Kalkulator:
    """Kelas sederhana untuk menguji instansiasi dan pemanggilan metode."""
    def __init__(self, nilai_awal=0):
        self.total = nilai_awal

    def tambahkan(self, nilai):
        self.total += nilai
        return self.total

    def dapatkan_total(self):
        return self.total

def proses_data_bersarang(data):
    """
    Menerima struktur data, memvalidasi isinya, dan mengembalikan yang baru.
    Contoh: Menerima dict, mengembalikan list dari tuple.
    """
    if not isinstance(data, dict):
        raise TypeError("Input harus berupa dict")

    nama = data.get("nama")
    nilai = data.get("nilai")

    if nama == "Vzoel" and nilai[1] == 30:
        return [("sukses", True), ("data", (100, 200))]

    return [("gagal", False)]
