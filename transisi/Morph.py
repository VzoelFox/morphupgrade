# transisi/Morph.py
# Titik Masuk Utama untuk "Kelahiran Kembali MORPH"

import sys
import asyncio
from .lx import Leksikal
from .crusher import Pengurai
from .translator import Penerjemah, Lingkungan
from .error_utils import FormatterKesalahan

class Morph:
    def __init__(self):
        self.ada_kesalahan = False

    def jalankan_file(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                sumber = file.read()
            output, daftar_kesalahan = self._jalankan_sync(sumber, path)
            if output:
                print(output, end="")
            if daftar_kesalahan:
                for kesalahan in daftar_kesalahan:
                    print(kesalahan, file=sys.stderr)
        except FileNotFoundError:
            print(f"Kesalahan: File tidak ditemukan di '{path}'", file=sys.stderr)
            sys.exit(1)

        if self.ada_kesalahan:
            sys.exit(65)

    def jalankan_prompt(self):
        self.lingkungan_global_repl = Lingkungan()
        print("Selamat datang di MORPH v2.0 (Kelahiran Kembali)")
        print("Ketik 'keluar()' untuk berhenti, 'reset()' untuk membersihkan state.")
        while True:
            try:
                baris = input("> ")
                if baris.strip().lower() == "keluar()":
                    break
                if baris.strip().lower() == "reset()":
                    self.lingkungan_global_repl = Lingkungan()
                    print("✓ State direset.")
                    continue

                output, daftar_kesalahan = self._jalankan_sync(baris, nama_file="<repl>", lingkungan_khusus=self.lingkungan_global_repl)
                if output:
                    print(output, end="")
                if daftar_kesalahan:
                    for kesalahan in daftar_kesalahan:
                        print(kesalahan, file=sys.stderr)
                self.ada_kesalahan = False
            except EOFError:
                print("\nSampai jumpa!")
                break
            except KeyboardInterrupt:
                print("\nSesi dihentikan.")
                break

    def _jalankan_sync(self, sumber: str, nama_file: str = "<prompt>", lingkungan_khusus=None):
        try:
            return asyncio.run(self._jalankan_async(sumber, nama_file, lingkungan_khusus))
        except KeyboardInterrupt:
            print("\nEksekusi asinkron dihentikan.")
            return None, []


    async def _jalankan_async(self, sumber: str, nama_file: str = "<prompt>", lingkungan_khusus=None):
        import io
        from .translator import Lingkungan

        output_stream = io.StringIO()
        formatter = FormatterKesalahan(sumber)
        daftar_kesalahan = []

        lexer = Leksikal(sumber, nama_file)
        tokens, kesalahan_lexer = lexer.buat_token()

        if kesalahan_lexer:
            for kesalahan in kesalahan_lexer:
                daftar_kesalahan.append(formatter.format_lexer(kesalahan))
            self.ada_kesalahan = True
            return None, daftar_kesalahan

        parser = Pengurai(tokens)
        program = parser.urai()

        if parser.daftar_kesalahan:
            for token, pesan in parser.daftar_kesalahan:
                daftar_kesalahan.append(formatter.format_parser(token, pesan))
            self.ada_kesalahan = True
            return None, daftar_kesalahan

        if program:
            penerjemah = Penerjemah(formatter, output_stream=output_stream)
            if lingkungan_khusus is not None:
                penerjemah.lingkungan_global = lingkungan_khusus

            kesalahan_runtime = await penerjemah.terjemahkan(program, nama_file)
            if kesalahan_runtime:
                self.ada_kesalahan = True
                return output_stream.getvalue(), kesalahan_runtime

        return output_stream.getvalue(), daftar_kesalahan

def main():
    args = sys.argv[1:]
    morph_app = Morph()
    if len(args) > 1:
        print("Penggunaan: python -m transisi.Morph [nama_file.fox]")
        sys.exit(64)
    elif len(args) == 1:
        morph_app.jalankan_file(args[0])
    else:
        morph_app.jalankan_prompt()

if __name__ == "__main__":
    main()
