# transisi/Morph.py
# Titik Masuk Utama untuk "Kelahiran Kembali MORPH"

import sys
from .lx import Leksikal
from .crusher import Pengurai
from .translator import Penerjemah
from .error_utils import FormatterKesalahan

class Morph:
    def __init__(self):
        # Inisialisasi penerjemah ditiadakan di sini,
        # karena butuh sumber kode untuk formatter
        self.ada_kesalahan = False

    def jalankan_file(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                sumber = file.read()
            self._jalankan(sumber)
        except FileNotFoundError:
            print(f"Kesalahan: File tidak ditemukan di '{path}'")
            sys.exit(1)

        if self.ada_kesalahan:
            sys.exit(65) # Kode exit untuk kesalahan data, sesuai konvensi

    def jalankan_prompt(self):
        print("Selamat datang di MORPH v2.0 (Kelahiran Kembali)")
        print("Ketik 'keluar()' untuk berhenti.")
        while True:
            try:
                baris = input("> ")
                if baris.lower() == "keluar()":
                    break
                self._jalankan(baris)
                self.ada_kesalahan = False # Reset error untuk sesi interaktif
            except EOFError:
                print("\nSampai jumpa!")
                break
            except KeyboardInterrupt:
                print("\nSesi dihentikan.")
                break

    def _jalankan(self, sumber: str):
        formatter = FormatterKesalahan(sumber)

        lexer = Leksikal(sumber)
        tokens, kesalahan_lexer = lexer.buat_token()

        if kesalahan_lexer:
            for pesan, baris, kolom in kesalahan_lexer:
                print(formatter.format_lexer(pesan, baris, kolom))
            self.ada_kesalahan = True
            return

        parser = Pengurai(tokens)
        program = parser.urai()

        if parser.daftar_kesalahan:
            for token, pesan in parser.daftar_kesalahan:
                print(formatter.format_parser(token, pesan))
            self.ada_kesalahan = True
            return

        if program:
            # Buat instance Penerjemah di sini, setelah kita punya formatter
            penerjemah = Penerjemah(formatter)
            penerjemah.terjemahkan(program)

def main():
    """Fungsi utama untuk menjalankan interpreter MORPH dari CLI."""
    # Perlu cara untuk menjalankan skrip ini secara langsung.
    # Biasanya, ini akan di-setup dalam sebuah entry point package.
    # Untuk pengujian, kita bisa hardcode path file.

    # Contoh penggunaan:
    # morph_instance = Morph()
    # if len(sys.argv) > 1:
    #     morph_instance.jalankan_file(sys.argv[1])
    # else:
    #     morph_instance.jalankan_prompt()

    # Karena kita tidak bisa menjalankan CLI secara langsung di sini,
    # kita hanya akan pastikan filenya ada.
    print("Titik masuk Morph.py berhasil dibuat.")
    print("Gunakan fungsi main() untuk integrasi CLI.")


if __name__ == "__main__":
    # Kode ini memungkinkan file dijalankan, misal: python -m transisi.Morph
    args = sys.argv[1:]
    morph_app = Morph()
    if len(args) > 1:
        print("Penggunaan: python -m transisi.Morph [nama_file.fox]")
        sys.exit(64)
    elif len(args) == 1:
        morph_app.jalankan_file(args[0])
    else:
        morph_app.jalankan_prompt()
