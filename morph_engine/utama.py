# morph_engine/utama.py
import sys
from .leksikal import Leksikal, LeksikalKesalahan
from .pengurai import Pengurai
from .penerjemah import Penerjemah, KesalahanRuntime

def jalankan_dari_file(nama_file):
    """Membaca file dan menjalankan kontennya. Mengembalikan kode keluar."""
    try:
        with open(nama_file, 'r', encoding='utf-8') as f:
            konten = f.read()
    except FileNotFoundError:
        print(f"Kesalahan: File '{nama_file}' tidak ditemukan.", file=sys.stderr)
        return 1

    return jalankan_kode(konten)

def jalankan_kode(kode):
    """Menjalankan string kode Morph. Mengembalikan kode keluar."""
    sumber_daya = []
    try:
        if not kode.strip():
            return 0

        # 1. Leksikal: Teks -> Token
        leksikal = Leksikal(kode)
        daftar_token = leksikal.buat_token()

        # 2. Pengurai: Token -> AST
        import os
        debug_mode = os.environ.get('MORPH_DEBUG', '0') == '1'
        pengurai = Pengurai(daftar_token, debug_mode=debug_mode)
        ast = pengurai.urai()

        if pengurai.daftar_kesalahan:
            for kesalahan in pengurai.daftar_kesalahan:
                print(str(kesalahan), file=sys.stderr)
            return 1

        # 3. Penerjemah: AST -> Eksekusi
        penerjemah = Penerjemah(ast)
        penerjemah.interpretasi()

    except LeksikalKesalahan as e:
        print(e, file=sys.stderr)
        return 1
    except KesalahanRuntime as e:
        print(e, file=sys.stderr)
        return 2
    finally:
        pass

    return 0

def utama():
    """Fungsi entry point utama dari command line."""
    if len(sys.argv) != 2:
        print("Penggunaan: morph <nama_file.fox>")
        sys.exit(64)

    nama_file = sys.argv[1]
    kode_keluar = jalankan_dari_file(nama_file)
    if kode_keluar is not None:
        sys.exit(kode_keluar)


if __name__ == "__main__":
    utama()
