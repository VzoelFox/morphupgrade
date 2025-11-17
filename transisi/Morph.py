# transisi/Morph.py
import sys
import asyncio
from .lx import Leksikal, TipeToken
from .crusher import Pengurai
from .translator import Penerjemah, Lingkungan
from .error_utils import FormatterKesalahan
from .runtime_fox import RuntimeMORPHFox

class Morph:
    def __init__(self):
        self.ada_kesalahan = False
        # Inisialisasi runtime secara lazy
        self.fox_runtime: RuntimeMORPHFox | None = None
        self.penerjemah: Penerjemah | None = None

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
        # Inisialisasi lingkungan REPL sekali saja (lazy)
        if not hasattr(self, 'lingkungan_global_repl'):
            self.lingkungan_global_repl = Lingkungan()

        print("Selamat datang di MORPH v2.0 (Kelahiran Kembali)")
        print("Ketik 'keluar()' untuk berhenti, 'reset()' untuk membersihkan state.")
        while True:
            try:
                baris_pertama = input("> ")

                if baris_pertama.strip().lower() == "keluar()":
                    break
                if baris_pertama.strip().lower() == "reset()":
                    self.lingkungan_global_repl = Lingkungan()
                    print("✓ State direset.")
                    continue

                kode_lengkap = baris_pertama + "\n"
                prompt = "... "

                # Logika deteksi multi-baris sederhana
                while True:
                    pembuka = kode_lengkap.count("maka") + kode_lengkap.count("{")
                    penutup = kode_lengkap.count("akhir") + kode_lengkap.count("}")

                    # Hanya lanjutkan jika blok belum seimbang
                    if pembuka > penutup:
                        baris_lanjutan = input(prompt)
                        kode_lengkap += baris_lanjutan + "\n"
                    else:
                        break

                output, daftar_kesalahan = self._jalankan_sync(
                    kode_lengkap,
                    nama_file="<repl>",
                    lingkungan_khusus=self.lingkungan_global_repl
                )
                if daftar_kesalahan:
                    for kesalahan in daftar_kesalahan:
                        print(kesalahan, file=sys.stderr)
                    self.ada_kesalahan = False # Reset setelah menampilkan
                    continue # Jangan coba evaluasi ekspresi jika ada kesalahan

                if output:
                    print(output, end="")
                elif self.penerjemah and self.penerjemah.hasil_ekspresi_terakhir is not None:
                    # Jika tidak ada output dari `tulis`, tapi ada hasil evaluasi ekspresi
                    print(self.penerjemah._ke_string(self.penerjemah.hasil_ekspresi_terakhir))

                self.ada_kesalahan = False
            except EOFError:
                print("\nSampai jumpa!")
                break
            except KeyboardInterrupt:
                print("\nSesi dihentikan.")
                break

    def _jalankan_sync(self, sumber: str, nama_file: str = "<prompt>",
                       lingkungan_khusus=None, ffi_objects=None):
        """Wrapper sync yang memanggil async runner."""
        try:
            return asyncio.run(
                self._jalankan_async(
                    sumber,
                    nama_file,
                    lingkungan_khusus,
                    ffi_objects
                )
            )
        except KeyboardInterrupt:
            print("\nEksekusi asinkron dihentikan.")
            return None, []

    async def _jalankan_async(self, sumber: str, nama_file: str = "<prompt>",
                              lingkungan_khusus=None, ffi_objects=None):
        import io

        output_stream = io.StringIO()
        formatter = FormatterKesalahan(sumber if sumber else "")
        daftar_kesalahan = []

        program = None
        if not program:
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
            # Inisialisasi lazy untuk runtime dan interpreter
            if self.penerjemah is None:
                self.penerjemah = Penerjemah(formatter, output_stream=output_stream)
            else:
                # Penting: Perbarui sumber formatter dan output stream untuk setiap baris di REPL
                self.penerjemah.formatter.atur_sumber(sumber)
                self.penerjemah.output_stream = output_stream

            if self.fox_runtime is None:
                # Buat runtime dan hubungkan keduanya
                self.fox_runtime = RuntimeMORPHFox(self.penerjemah)
                self.penerjemah.runtime = self.fox_runtime

            if lingkungan_khusus is not None:
                self.penerjemah.lingkungan_global = lingkungan_khusus

            if ffi_objects:
                for nama, objek in ffi_objects.items():
                    self.penerjemah.lingkungan_global.definisi(nama, objek)

            kesalahan_runtime = await self.penerjemah.terjemahkan(program, nama_file)
            if kesalahan_runtime:
                self.ada_kesalahan = True
                return output_stream.getvalue(), kesalahan_runtime

        return output_stream.getvalue(), daftar_kesalahan

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='MORPH Programming Language v2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh Penggunaan:
  %(prog)s                  Mulai REPL interaktif
  %(prog)s nama_file.fox     Eksekusi sebuah file
  %(prog)s --repl           Mulai REPL secara eksplisit
  %(prog)s --version        Tampilkan versi
        """
    )

    parser.add_argument(
        'file',
        nargs='?',
        help='File skrip Morph yang akan dieksekusi'
    )
    parser.add_argument(
        '-i', '--repl', '--interactive',
        action='store_true',
        help='Mulai REPL interaktif'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='MORPH v2.0.0-beta'
    )

    args = parser.parse_args()
    morph_app = Morph()

    # Prioritas: file > repl eksplisit > repl default
    if args.file:
        morph_app.jalankan_file(args.file)
    else:
        # Tidak ada file = REPL (baik dengan atau tanpa flag)
        morph_app.jalankan_prompt()

if __name__ == "__main__":
    main()
