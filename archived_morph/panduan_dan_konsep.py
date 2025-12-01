"""
PANDUAN PENGEMBANGAN MORPH DAN KONSEP SELF-HOSTING
==================================================

File ini dibuat untuk mendokumentasikan cara penggunaan bootstrap Morph (Python) saat ini
dan menyimpan konsep kode Morph murni (Morph-in-Morph) agar dapat diakses oleh sesi pengembangan lain.

PENULIS: Jules (Sesi Bootstrap)
TUJUAN: Menyediakan jembatan pengetahuan untuk Jules (Sesi Greenfield/Morph Murni).

DAFTAR ISI:
1. PANDUAN BOOTSTRAP: Cara menjalankan kode .fox saat ini.
2. KONSEP SELF-HOSTING: Kode Morph untuk Lexer dan VM yang ditulis dalam Morph.
3. KONSEP COTC: Wrapper untuk psutil dan async.

"""

# =================================================================================================
# BAGIAN 1: PANDUAN BOOTSTRAP (Cara Menggunakan Repo Ini)
# =================================================================================================
"""
Repo ini berisi implementasi bootstrap Morph berbasis Python.
Struktur utama:
- transisi/ : Frontend (Lexer, Parser, AST)
- ivm/      : Backend (Compiler, VM)

CARA MENJALANKAN FILE .FOX:
Gunakan skrip `ivm/main.py`.

Perintah Terminal:
    python3 ivm/main.py <path_ke_file.fox>

Contoh:
    python3 ivm/main.py contoh.fox

CARA MENJALANKAN TES:
Repo ini menggunakan `pytest`.
    pytest tests/                  # Menjalankan semua tes
    pytest tests/test_lx.py        # Menjalankan tes lexer saja
"""

# =================================================================================================
# BAGIAN 2: KONSEP SELF-HOSTING (Morph ditulis dalam Morph)
# =================================================================================================

# Berikut adalah draft kode bagaimana komponen inti Morph akan terlihat jika ditulis
# menggunakan sintaks Morph itu sendiri.

MORPH_TOKEN_FOX = r"""
# core/morph_t.fox
# Definisi Token dan Tipe Token

# Konstanta Tipe Token (Menggunakan string untuk debugging mudah)
biar EOF = "EOF"
biar ILLEGAL = "ILLEGAL"
biar IDENTIFIER = "IDENTIFIER"
biar INT = "INT"
biar STRING = "STRING"

# Operator
biar ASSIGN = "="
biar PLUS = "+"
biar MINUS = "-"
biar BANG = "!"
biar ASTERISK = "*"
biar SLASH = "/"
biar EQ = "=="
biar NOT_EQ = "!="
biar LT = "<"
biar GT = ">"

# Keyword
biar FUNGSI = "FUNGSI"
biar BIAR = "BIAR"
biar JIKA = "JIKA"
biar MAKA = "MAKA"
biar LAIN = "LAIN"
biar AKHIR = "AKHIR"
biar KELAS = "KELAS"
biar WARISI = "WARISI"
biar KEMBALI = "KEMBALI"

# Peta Kata Kunci
biar keywords = {
    "fungsi": FUNGSI,
    "biar": BIAR,
    "jika": JIKA,
    "maka": MAKA,
    "lain": LAIN,
    "akhir": AKHIR,
    "kelas": KELAS,
    "warisi": WARISI,
    "kembali": KEMBALI
}

# Definisi Kelas Token
kelas Token maka
    biar tipe
    biar literal
    biar baris
    biar kolom

    fungsi init(tipe_token, nilai_literal, no_baris, no_kolom) maka
        ini.tipe = tipe_token
        ini.literal = nilai_literal
        ini.baris = no_baris
        ini.kolom = no_kolom
    akhir

    fungsi string() maka
        kembali "Token(" + ini.tipe + ", " + ini.literal + ")"
    akhir
akhir
"""

MORPH_LEXER_FOX = r"""
# core/lx_morph.fox
# Lexer Morph yang ditulis dalam Morph

ambil_semua "core/morph_t.fox" sebagai T

kelas Lexer maka
    biar masukan
    biar posisi
    biar posisi_baca
    biar ch
    biar baris
    biar kolom

    fungsi init(masukan_kode) maka
        ini.masukan = masukan_kode
        ini.posisi = 0
        ini.posisi_baca = 0
        ini.ch = ""
        ini.baris = 1
        ini.kolom = 1
        ini.baca_karakter()
    akhir

    fungsi baca_karakter() maka
        jika ini.posisi_baca >= panjang(ini.masukan) maka
            ini.ch = 0 # EOF
        lain
            ini.ch = ini.masukan[ini.posisi_baca]
        akhir

        ini.posisi = ini.posisi_baca
        ini.posisi_baca = ini.posisi_baca + 1
        ini.kolom = ini.kolom + 1
    akhir

    fungsi token_berikutnya() maka
        biar tok = nil
        ini.lewati_spasi()

        pilih ini.ch
        ketika "=" maka
            jika ini.intip_karakter() == "=" maka
                ini.baca_karakter()
                tok = T.Token(T.EQ, "==", ini.baris, ini.kolom)
            lain
                tok = T.Token(T.ASSIGN, "=", ini.baris, ini.kolom)
            akhir
        ketika "+" maka
            tok = T.Token(T.PLUS, "+", ini.baris, ini.kolom)
        ketika "-" maka
            tok = T.Token(T.MINUS, "-", ini.baris, ini.kolom)
        ketika 0 maka
            tok = T.Token(T.EOF, "", ini.baris, ini.kolom)
        lainnya maka
            jika adl_huruf(ini.ch) maka
                biar ident = ini.baca_identifier()
                biar tipe = T.cari_keyword(ident)
                kembali T.Token(tipe, ident, ini.baris, ini.kolom)
            lain jika adl_digit(ini.ch) maka
                biar num = ini.baca_angka()
                kembali T.Token(T.INT, num, ini.baris, ini.kolom)
            lain
                tok = T.Token(T.ILLEGAL, ini.ch, ini.baris, ini.kolom)
            akhir
        akhir

        ini.baca_karakter()
        kembali tok
    akhir

    fungsi lewati_spasi() maka
        selama ini.ch == " " atau ini.ch == "\t" atau ini.ch == "\n" atau ini.ch == "\r" maka
            jika ini.ch == "\n" maka
                ini.baris = ini.baris + 1
                ini.kolom = 0
            akhir
            ini.baca_karakter()
        akhir
    akhir
akhir
"""

MORPH_AST_FOX = r"""
# core/ast_morph.fox
# Struktur AST (Abstract Syntax Tree)

kelas Node maka
    fungsi token_literal() maka
        kembali ""
    akhir
akhir

kelas Pernyataan warisi Node maka
    # Kelas dasar untuk semua pernyataan
akhir

kelas Ekspresi warisi Node maka
    # Kelas dasar untuk semua ekspresi
akhir

# --- Pernyataan ---

kelas PernyataanBiar warisi Pernyataan maka
    biar token
    biar nama
    biar nilai

    fungsi init(token, nama, nilai) maka
        ini.token = token
        ini.nama = nama
        ini.nilai = nilai
    akhir
akhir

kelas PernyataanKembali warisi Pernyataan maka
    biar token
    biar nilai_kembali

    fungsi init(token, nilai) maka
        ini.token = token
        ini.nilai_kembali = nilai
    akhir
akhir

# --- Ekspresi ---

kelas Identitas warisi Ekspresi maka
    biar token
    biar nilai

    fungsi init(token, val) maka
        ini.token = token
        ini.nilai = val
    akhir
akhir
"""

# =================================================================================================
# BAGIAN 3: KONSEP COTC (Component-Oriented Thread Concepts) & FFI
# =================================================================================================
"""
Konsep untuk membungkus library sistem (psutil) dan async menggunakan Morph FFI.
Idenya adalah membuat modul Morph yang memanggil fungsi native Python di backend.
"""

MORPH_COTC_SYSTEM_FOX = r"""
# pustaka/sistem.fox
# Wrapper untuk psutil (System Monitoring)

pinjam "sys" sebagai _sys
pinjam "psutil" sebagai _psutil

kelas MonitorSistem maka
    fungsi init() maka
        # Inisialisasi jika perlu
    akhir

    fungsi cpu_persen() maka
        kembali _psutil.cpu_percent(interval=1)
    akhir

    fungsi memori_terpakai() maka
        biar mem = _psutil.virtual_memory()
        kembali mem.percent
    akhir

    fungsi info_disk() maka
        biar disk = _psutil.disk_usage('/')
        kembali {
            "total": disk.total,
            "terpakai": disk.used,
            "bebas": disk.free,
            "persen": disk.percent
        }
    akhir
akhir
"""

MORPH_ASYNC_CONCEPTS = r"""
# pustaka/asinkron.fox
# Konsep konkurensi di Morph

# Morph mendukung 'asink' dan 'tunggu' secara native.
# Di backend, ini dipetakan ke Python asyncio.

asink fungsi ambil_data_url(url) maka
    tulis("Mengambil data dari: " + url)
    # Simulasi IO bound operation
    tunggu tidur(1000) # tidur 1 detik
    kembali "Data dari " + url
akhir

asink fungsi main() maka
    biar hasil1 = tunggu ambil_data_url("http://contoh.com")
    tulis(hasil1)

    # Menjalankan konkuren (konsep masa depan)
    # biar tugas1 = jalan_belakang ambil_data_url("...")
    # biar tugas2 = jalan_belakang ambil_data_url("...")
    # tunggu gabung(tugas1, tugas2)
akhir
"""
