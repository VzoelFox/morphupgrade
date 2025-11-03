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
        return 1 # Kode 1 untuk error umum/sistem

    return jalankan_kode(konten)

def jalankan_kode(kode):
    """Menjalankan string kode Morph. Mengembalikan kode keluar."""
    sumber_daya = [] # Placeholder untuk manajemen sumber daya (misal: file handle)
    try:
        if not kode.strip():
            return 0

        # 1. Leksikal: Teks -> Token
        leksikal = Leksikal(kode)
        daftar_token = leksikal.buat_token()

        # 2. Pengurai: Token -> AST
        pengurai = Pengurai(daftar_token)
        ast = pengurai.urai()

        if pengurai.daftar_kesalahan:
            for error in pengurai.daftar_kesalahan:
                print(error, file=sys.stderr)
            return 1 # Exit code 1 untuk kesalahan leksikal/pengurai

        # 3. Penerjemah: AST -> Eksekusi
        penerjemah = Penerjemah(ast)
        penerjemah.interpretasi()

    except LeksikalKesalahan as e:
        print(e, file=sys.stderr)
        return 1 # Exit code 1 untuk kesalahan leksikal/pengurai
    except KesalahanRuntime as e:
        print(e, file=sys.stderr)
        return 2 # Exit code 2 untuk kesalahan runtime
    finally:
        # Placeholder untuk pembersihan sumber daya
        # for sumber in sumber_daya:
        #     sumber.tutup()
        pass

    return 0 # Kode 0 untuk eksekusi sukses

def utama():
    """Fungsi entry point utama dari command line."""
    if len(sys.argv) != 2:
        print("Penggunaan: morph <nama_file.fox>")
        sys.exit(64) # Kode exit konvensi untuk penggunaan argumen yang salah

    nama_file = sys.argv[1]
    jalankan_dari_file(nama_file)

if __name__ == "__main__":
    utama()
