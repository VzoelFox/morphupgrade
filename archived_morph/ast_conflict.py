"""
SKELETON SELF-HOSTING: AST
==========================
File ini berisi draf kode Morph untuk Definisi AST Lengkap.
Ini adalah padanan dari `transisi/absolute_sntx_morph.py`.
"""

MORPH_SOURCE = r"""
# core/ast.fox
# Struktur AST (Abstract Syntax Tree) Lengkap

kelas Node maka
    fungsi token_literal() maka kembali "" akhir
    fungsi string() maka kembali "" akhir
akhir

kelas Pernyataan warisi Node maka akhir
kelas Ekspresi warisi Node maka akhir

# ==========================================
# Node Level Atas
# ==========================================

kelas Program warisi Node maka
    biar pernyataan

    fungsi init() maka
        ini.pernyataan = []
    akhir

    fungsi token_literal() maka
        jika panjang(ini.pernyataan) > 0 maka
            kembali ini.pernyataan[0].token_literal()
        lain
            kembali ""
        akhir
    akhir

    fungsi string() maka
        biar out = ""
        untuk p dalam ini.pernyataan maka
            out = out + p.string()
        akhir
        kembali out
    akhir
akhir

# ==========================================
# Literal & Identitas
# ==========================================

kelas Konstanta warisi Ekspresi maka
    biar token
    biar nilai
    fungsi init(token, nilai) maka
        ini.token = token
        ini.nilai = nilai
    akhir
akhir

kelas Identitas warisi Ekspresi maka
    biar token
    biar nama
    fungsi init(token, nama) maka
        ini.token = token
        ini.nama = nama
    akhir
    fungsi string() maka kembali ini.nama akhir
akhir

kelas Daftar warisi Ekspresi maka
    biar elemen # List[Ekspresi]
    fungsi init(elemen) maka ini.elemen = elemen akhir
akhir

kelas Kamus warisi Ekspresi maka
    biar pasangan # List[(Key, Value)]
    fungsi init(pasangan) maka ini.pasangan = pasangan akhir
akhir

# ==========================================
# Ekspresi
# ==========================================

kelas FoxBinary warisi Ekspresi maka
    biar kiri
    biar op
    biar kanan
    fungsi init(kiri, op, kanan) maka
        ini.kiri = kiri
        ini.op = op
        ini.kanan = kanan
    akhir
akhir

kelas FoxUnary warisi Ekspresi maka
    biar op
    biar kanan
    fungsi init(op, kanan) maka
        ini.op = op
        ini.kanan = kanan
    akhir
akhir

kelas PanggilFungsi warisi Ekspresi maka
    biar callee
    biar argumen
    fungsi init(callee, argumen) maka
        ini.callee = callee
        ini.argumen = argumen
    akhir
akhir

kelas Akses warisi Ekspresi maka
    biar objek
    biar kunci
    fungsi init(objek, kunci) maka
        ini.objek = objek
        ini.kunci = kunci
    akhir
akhir

kelas AmbilProperti warisi Ekspresi maka
    biar objek
    biar nama
    fungsi init(objek, nama) maka
        ini.objek = objek
        ini.nama = nama
    akhir
akhir

kelas AturProperti warisi Ekspresi maka
    biar objek
    biar nama
    biar nilai
    fungsi init(objek, nama, nilai) maka
        ini.objek = objek
        ini.nama = nama
        ini.nilai = nilai
    akhir
akhir

kelas Ini warisi Ekspresi maka
    biar token
    fungsi init(token) maka ini.token = token akhir
akhir

kelas Induk warisi Ekspresi maka
    biar token
    biar metode
    fungsi init(token, metode) maka
        ini.token = token
        ini.metode = metode
    akhir
akhir

kelas Tunggu warisi Ekspresi maka
    biar token
    biar ekspresi
    fungsi init(token, ekspresi) maka
        ini.token = token
        ini.ekspresi = ekspresi
    akhir
akhir

kelas Ambil warisi Ekspresi maka
    biar prompt
    fungsi init(prompt) maka ini.prompt = prompt akhir
akhir

# ==========================================
# Pernyataan (Statements)
# ==========================================

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

kelas DeklarasiVariabel warisi Pernyataan maka
    # Mencakup BIAR dan TETAP
    biar jenis # Token (BIAR/TETAP)
    biar nama
    biar nilai
    fungsi init(jenis, nama, nilai) maka
        ini.jenis = jenis
        ini.nama = nama
        ini.nilai = nilai
    akhir
akhir

kelas Assignment warisi Pernyataan maka
    biar target
    biar nilai
    fungsi init(target, nilai) maka
        ini.target = target
        ini.nilai = nilai
    akhir
akhir

kelas PernyataanEkspresi warisi Pernyataan maka
    biar ekspresi
    fungsi init(ekspresi) maka ini.ekspresi = ekspresi akhir
akhir

kelas JikaMaka warisi Pernyataan maka
    biar kondisi
    biar blok_maka
    biar rantai_lain_jika # List[(kondisi, blok)]
    biar blok_lain        # Optional[Blok]
    fungsi init(kondisi, blok_maka, rantai_lain_jika, blok_lain) maka
        ini.kondisi = kondisi
        ini.blok_maka = blok_maka
        ini.rantai_lain_jika = rantai_lain_jika
        ini.blok_lain = blok_lain
    akhir
akhir

kelas Selama warisi Pernyataan maka
    biar kondisi
    biar badan
    fungsi init(kondisi, badan) maka
        ini.kondisi = kondisi
        ini.badan = badan
    akhir
akhir

kelas Berhenti warisi Pernyataan maka
    biar token
    fungsi init(token) maka ini.token = token akhir
akhir

kelas Lanjutkan warisi Pernyataan maka
    biar token
    fungsi init(token) maka ini.token = token akhir
akhir

kelas PernyataanKembalikan warisi Pernyataan maka
    biar token
    biar nilai
    fungsi init(token, nilai) maka
        ini.token = token
        ini.nilai = nilai
    akhir
akhir

kelas Tulis warisi Pernyataan maka
    biar argumen
    fungsi init(argumen) maka ini.argumen = argumen akhir
akhir

# ==========================================
# Fungsi & Kelas
# ==========================================

kelas FungsiDeklarasi warisi Pernyataan maka
    biar nama
    biar parameter
    biar badan
    fungsi init(nama, parameter, badan) maka
        ini.nama = nama
        ini.parameter = parameter
        ini.badan = badan
    akhir
akhir

kelas FungsiAsinkDeklarasi warisi Pernyataan maka
    biar nama
    biar parameter
    biar badan
    fungsi init(nama, parameter, badan) maka
        ini.nama = nama
        ini.parameter = parameter
        ini.badan = badan
    akhir
akhir

kelas Kelas warisi Pernyataan maka
    biar nama
    biar superkelas
    biar metode
    fungsi init(nama, superkelas, metode) maka
        ini.nama = nama
        ini.superkelas = superkelas
        ini.metode = metode
    akhir
akhir

# ==========================================
# Modules & FFI
# ==========================================

kelas AmbilSemua warisi Pernyataan maka
    biar path_file
    biar alias
    fungsi init(path, alias) maka
        ini.path_file = path
        ini.alias = alias
    akhir
akhir

kelas AmbilSebagian warisi Pernyataan maka
    biar daftar_simbol
    biar path_file
    fungsi init(simbols, path) maka
        ini.daftar_simbol = simbols
        ini.path_file = path
    akhir
akhir

kelas Pinjam warisi Pernyataan maka
    biar path_file
    biar alias
    biar butuh_aot
    fungsi init(path, alias, aot) maka
        ini.path_file = path
        ini.alias = alias
        ini.butuh_aot = aot
    akhir
akhir

# ==========================================
# Pattern Matching (Jodohkan)
# ==========================================

kelas Jodohkan warisi Pernyataan maka
    biar ekspresi
    biar kasus # List[JodohkanKasus]
    fungsi init(expr, kasus) maka
        ini.ekspresi = expr
        ini.kasus = kasus
    akhir
akhir

kelas JodohkanKasus warisi Node maka
    biar pola
    biar jaga
    biar badan
    fungsi init(pola, jaga, badan) maka
        ini.pola = pola
        ini.jaga = jaga
        ini.badan = badan
    akhir
akhir

# Pola-pola
kelas Pola warisi Node maka akhir

kelas PolaLiteral warisi Pola maka
    biar nilai
    fungsi init(n) maka ini.nilai = n akhir
akhir

kelas PolaWildcard warisi Pola maka
    biar token
    fungsi init(t) maka ini.token = t akhir
akhir

kelas PolaIkatanVariabel warisi Pola maka
    biar token
    fungsi init(t) maka ini.token = t akhir
akhir

kelas PolaVarian warisi Pola maka
    biar nama
    biar daftar_ikatan
    fungsi init(nama, ikatan) maka
        ini.nama = nama
        ini.daftar_ikatan = ikatan
    akhir
akhir

kelas PolaDaftar warisi Pola maka
    biar daftar_pola
    biar pola_sisa
    fungsi init(pola, sisa) maka
        ini.daftar_pola = pola
        ini.pola_sisa = sisa
    akhir
akhir

# ==========================================
# Switch Case (Pilih)
# ==========================================

kelas Pilih warisi Pernyataan maka
    biar ekspresi
    biar kasus # List[PilihKasus]
    biar kasus_lainnya
    fungsi init(expr, k, kl) maka
        ini.ekspresi = expr
        ini.kasus = k
        ini.kasus_lainnya = kl
    akhir
akhir

kelas PilihKasus warisi Node maka
    biar nilai # List[Ekspresi]
    biar badan
    fungsi init(n, b) maka
        ini.nilai = n
        ini.badan = b
    akhir
akhir

kelas KasusLainnya warisi Node maka
    biar badan
    fungsi init(b) maka ini.badan = b akhir
akhir

# ==========================================
# Error Handling (Coba-Tangkap)
# ==========================================

kelas CobaTangkap warisi Pernyataan maka
    biar blok_coba
    biar daftar_tangkap
    biar blok_akhirnya
    fungsi init(coba, tangkap, akhirnya) maka
        ini.blok_coba = coba
        ini.daftar_tangkap = tangkap
        ini.blok_akhirnya = akhirnya
    akhir
akhir

kelas Tangkap warisi Node maka
    biar nama_error
    biar kondisi_jaga
    biar badan
    fungsi init(nama, jaga, badan) maka
        ini.nama_error = nama
        ini.kondisi_jaga = jaga
        ini.badan = badan
    akhir
akhir

kelas Lemparkan warisi Pernyataan maka
    biar ekspresi
    biar jenis
    fungsi init(expr, jenis) maka
        ini.ekspresi = expr
        ini.jenis = jenis
    akhir
akhir

# ==========================================
# Tipe Varian
# ==========================================

kelas TipeDeklarasi warisi Pernyataan maka
    biar nama
    biar daftar_varian
    fungsi init(nama, varian) maka
        ini.nama = nama
        ini.daftar_varian = varian
    akhir
akhir

kelas Varian warisi Node maka
    biar nama
    biar parameter
    fungsi init(nama, param) maka
        ini.nama = nama
        ini.parameter = param
    akhir
akhir
"""
