# morph_engine/Morph.py
import sys
from .lx import Leksikal, LeksikalKesalahan
from .crusher import Pengurai
from .sentuhan_akhir import SentuhanAkhir, ElegiKeheningan

def jalankan_dari_file(nama_file):
    """Membaca file dan menjalankan kontennya. Mengembalikan kode keluar."""
    try:
        with open(nama_file, 'r', encoding='utf-8') as f:
            konten = f.read()
    except FileNotFoundError:
        print(f"Kesalahan: File '{nama_file}' tidak ditemukan.", file=sys.stderr)
        return 1
    return jalankan_kode(konten, file_path=nama_file)

def jalankan_kode(kode, file_path=None):
    """Menjalankan string kode Morph. Mengembalikan kode keluar."""
    try:
        if not kode.strip(): return 0

        # 1. Leksikal: Teks -> Token
        leksikal = Leksikal(kode)
        daftar_token = leksikal.buat_token()

        # 2. Pengurai: Token -> AST
        import os
        debug_mode = os.environ.get('MORPH_DEBUG', '0') == '1'
        pengurai = Pengurai(daftar_token, debug_mode=debug_mode)
        ast = pengurai.urai()

        # 3. Penerjemah: AST -> Eksekusi
        penerjemah = SentuhanAkhir(ast, file_path=file_path)
        penerjemah.interpretasi()

    except (LeksikalKesalahan, ElegiKeheningan) as e:
        print(e, file=sys.stderr)
        return 2 if isinstance(e, ElegiKeheningan) else 1
    finally:
        pass
    return 0

def utama():
    """Fungsi entry point utama dari command line."""
    if len(sys.argv) != 2:
        print("Penggunaan: morph <nama_file.fox>")
        sys.exit(64)
    kode_keluar = jalankan_dari_file(sys.argv[1])
    if kode_keluar is not None:
        sys.exit(kode_keluar)

if __name__ == "__main__":
    utama()
