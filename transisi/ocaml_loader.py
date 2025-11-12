import json
from typing import Any, Dict, List, Optional

from . import absolute_sntx_morph as ast
from .absolute_sntx_morph import (
    # Program
    Bagian,

    # Statements
    DeklarasiVariabel, Assignment, PernyataanEkspresi,
    Tulis, JikaMaka, Selama, Pilih, PilihKasus, KasusLainnya,
    Jodohkan, JodohkanKasus,
    FungsiDeklarasi, FungsiAsinkDeklarasi, PernyataanKembalikan,
    Kelas, TipeDeklarasi, Varian,
    AmbilSemua, AmbilSebagian, Pinjam,

    # Expressions
    Konstanta, Identitas, FoxBinary, FoxUnary,
    Daftar, Kamus, PanggilFungsi, Akses,
    AmbilProperti, AturProperti, Ini, Induk,
    Tunggu, Ambil,

    # Patterns
    PolaLiteral, PolaWildcard, PolaVarian,

    # Base classes
    St, Xprs
)
from .morph_t import Token, TipeToken

# Mapping dari string JSON ke enum TipeToken Python
TOKEN_TYPE_MAP = {
    # Deklarasi & Assignment
    "BIAR": TipeToken.BIAR,
    "TETAP": TipeToken.TETAP,
    "UBAH": TipeToken.UBAH,
    "EQUAL": TipeToken.SAMADENGAN,

    # Operators Aritmatika
    "PLUS": TipeToken.TAMBAH,
    "MINUS": TipeToken.KURANG,
    "BINTANG": TipeToken.KALI,
    "GARIS_MIRING": TipeToken.BAGI,
    "PANGKAT": TipeToken.PANGKAT,
    "PERSEN": TipeToken.MODULO,

    # Operators Perbandingan
    "SAMA_DENGAN": TipeToken.SAMA_DENGAN,
    "TIDAK_SAMA": TipeToken.TIDAK_SAMA,
    "KURANG_DARI": TipeToken.KURANG_DARI,
    "KURANG_SAMA": TipeToken.KURANG_SAMA,
    "LEBIH_DARI": TipeToken.LEBIH_DARI,
    "LEBIH_SAMA": TipeToken.LEBIH_SAMA,

    # Operators Logika
    "DAN": TipeToken.DAN,
    "ATAU": TipeToken.ATAU,
    "TIDAK": TipeToken.TIDAK,

    # Control Flow
    "JIKA": TipeToken.JIKA,
    "MAKA": TipeToken.MAKA,
    "LAIN": TipeToken.LAIN,
    "AKHIR": TipeToken.AKHIR,
    "SELAMA": TipeToken.SELAMA,
    "PILIH": TipeToken.PILIH,
    "KETIKA": TipeToken.KETIKA,
    "LAINNYA": TipeToken.LAINNYA,

    # Functions
    "FUNGSI": TipeToken.FUNGSI,
    "KEMBALI": TipeToken.KEMBALI,
    "ASINK": TipeToken.ASINK,
    "TUNGGU": TipeToken.TUNGGU,

    # Classes
    "KELAS": TipeToken.KELAS,
    "WARISI": TipeToken.WARISI,
    "INI": TipeToken.INI,
    "INDUK": TipeToken.INDUK,

    # Pattern Matching
    "TIPE": TipeToken.TIPE,
    "JODOHKAN": TipeToken.JODOHKAN,
    "DENGAN": TipeToken.DENGAN,

    # Modules & FFI
    "PINJAM": TipeToken.PINJAM,
    "AMBIL_SEMUA": TipeToken.AMBIL_SEMUA,
    "AMBIL_SEBAGIAN": TipeToken.AMBIL_SEBAGIAN,
    "DARI": TipeToken.DARI,
    "SEBAGAI": TipeToken.SEBAGAI,

    # Built-ins
    "TULIS": TipeToken.TULIS,
    "AMBIL": TipeToken.AMBIL,

    # Literals
    "ANGKA": TipeToken.ANGKA,
    "TEKS": TipeToken.TEKS,
    "BENAR": TipeToken.BENAR,
    "SALAH": TipeToken.SALAH,
    "NIL": TipeToken.NIL,
    "NAMA": TipeToken.NAMA,

    # Delimiters
    "LPAREN": TipeToken.KURUNG_BUKA,
    "RPAREN": TipeToken.KURUNG_TUTUP,
    "LBRACE": TipeToken.KURAWAL_BUKA,
    "RBRACE": TipeToken.KURAWAL_TUTUP,
    "LBRACKET": TipeToken.SIKU_BUKA,
    "RBRACKET": TipeToken.SIKU_TUTUP,

    # Punctuation
    "KOMA": TipeToken.KOMA,
    "TITIK": TipeToken.TITIK,
    "TITIK_KOMA": TipeToken.TITIK_KOMA,
    "TITIK_DUA": TipeToken.TITIK_DUA,
    "GARIS_PEMISAH": TipeToken.GARIS_PEMISAH,
    "PIPE": TipeToken.GARIS_PEMISAH,
    "COLON": TipeToken.TITIK_DUA,
    "DOT": TipeToken.TITIK,

    # Special
    "NEWLINE": TipeToken.AKHIR_BARIS,
    "EOF": TipeToken.ADS,
}

def _json_to_token(json_data: Dict[str, Any]) -> Token:
    """Mengubah sub-kamus JSON menjadi objek Token."""
    tipe_str = json_data.get("tipe")
    tipe = TOKEN_TYPE_MAP.get(tipe_str)
    if tipe is None:
        raise ValueError(f"Tipe token tidak diketahui: '{tipe_str}'")

    # CRITICAL FIX: Handle nilai yang bisa string atau number
    nilai_raw = json_data.get("nilai")

    # Convert based on token type
    if tipe == TipeToken.ANGKA:
        if isinstance(nilai_raw, (int, float)):
            nilai = nilai_raw
        elif isinstance(nilai_raw, str):
            nilai = float(nilai_raw) if '.' in nilai_raw else int(float(nilai_raw))
        else:
            nilai = None
    elif tipe in (TipeToken.BENAR, TipeToken.SALAH):
        nilai = (tipe == TipeToken.BENAR)
    elif tipe == TipeToken.NIL:
        nilai = None
    else:
        nilai = nilai_raw

    return Token(
        tipe=tipe,
        nilai=nilai,
        baris=json_data.get("baris", 0),
        kolom=json_data.get("kolom", 0)
    )

def _deserialize_pola(json_data: Dict[str, Any]) -> ast.Pola:
    """Mendeserialisasi pola untuk pattern matching."""
    pola_type = json_data.get("node_type")

    if pola_type == "PolaLiteral":
        nilai = Konstanta(_json_to_token(json_data.get("nilai")))
        return PolaLiteral(nilai)

    elif pola_type == "PolaWildcard":
        token = _json_to_token(json_data.get("token"))
        return PolaWildcard(token)

    elif pola_type == "PolaVarian":
        nama = _json_to_token(json_data.get("nama"))
        daftar_ikatan = [_json_to_token(i) for i in json_data.get("daftar_ikatan", [])]
        return PolaVarian(nama, daftar_ikatan)

    else:
        raise NotImplementedError(
            f"Deserialisasi untuk pola tipe '{pola_type}' belum diimplementasikan."
        )

def _deserialize_expr(json_data: Dict[str, Any]) -> Xprs:
    """Mendeserialisasi ekspresi JSON menjadi objek Xprs."""
    if json_data is None:
        return None

    node_type = json_data.get("node_type")

    if node_type == "Konstanta":
        return Konstanta(_json_to_token(json_data.get("token")))

    elif node_type == "Identitas":
        return Identitas(_json_to_token(json_data.get("token")))

    elif node_type == "FoxBinary":
        kiri = _deserialize_expr(json_data.get("kiri"))
        op = _json_to_token(json_data.get("operator"))
        kanan = _deserialize_expr(json_data.get("kanan"))
        return FoxBinary(kiri, op, kanan)

    elif node_type == "FoxUnary":
        op = _json_to_token(json_data.get("operator"))
        kanan = _deserialize_expr(json_data.get("kanan"))
        return FoxUnary(op, kanan)

    elif node_type == "Daftar":
        elemen = [_deserialize_expr(e) for e in json_data.get("elemen", [])]
        return Daftar(elemen)

    elif node_type == "Kamus":
        pasangan_json = json_data.get("pasangan", [])
        pasangan = [
            (_deserialize_expr(p["kunci"]), _deserialize_expr(p["nilai"]))
            for p in pasangan_json
        ]
        return Kamus(pasangan)

    elif node_type == "PanggilFungsi":
        callee = _deserialize_expr(json_data["callee"])
        token = _json_to_token(json_data["token"])
        argumen = [_deserialize_expr(a) for a in json_data["argumen"]]
        return PanggilFungsi(callee, token, argumen)

    elif node_type == "Akses":
        objek = _deserialize_expr(json_data.get("objek"))
        kunci = _deserialize_expr(json_data.get("kunci"))
        return Akses(objek, kunci)

    elif node_type == "AmbilProperti":
        objek = _deserialize_expr(json_data.get("objek"))
        nama = _json_to_token(json_data.get("nama"))
        return AmbilProperti(objek, nama)

    elif node_type == "AturProperti":
        objek = _deserialize_expr(json_data.get("objek"))
        nama = _json_to_token(json_data.get("nama"))
        nilai = _deserialize_expr(json_data.get("nilai"))
        return AturProperti(objek, nama, nilai)

    elif node_type == "Ini":
        kata_kunci = _json_to_token(json_data.get("kata_kunci"))
        return Ini(kata_kunci)

    elif node_type == "Induk":
        kata_kunci = _json_to_token(json_data.get("kata_kunci"))
        metode = _json_to_token(json_data.get("metode"))
        return Induk(kata_kunci, metode)

    elif node_type == "Tunggu":
        kata_kunci = _json_to_token(json_data.get("kata_kunci"))
        ekspresi = _deserialize_expr(json_data.get("ekspresi"))
        return Tunggu(kata_kunci, ekspresi)

    elif node_type == "Ambil":
        prompt = _deserialize_expr(json_data.get("prompt"))
        return Ambil(prompt)

    else:
        raise NotImplementedError(
            f"Deserialisasi untuk ekspresi tipe '{node_type}' belum diimplementasikan."
        )

def _deserialize_stmt(json_data: Dict[str, Any]) -> St:
    """Mendeserialisasi pernyataan JSON menjadi objek St."""
    node_type = json_data.get("node_type")

    if node_type == "DeklarasiVariabel":
        keyword = _json_to_token(json_data.get("jenis_deklarasi"))
        nama = _json_to_token(json_data.get("nama"))
        nilai_json = json_data.get("nilai")
        init = _deserialize_expr(nilai_json) if nilai_json else None
        return DeklarasiVariabel(keyword, nama, init)

    elif node_type == "Assignment":
        nama_data = json_data.get("nama")
        if isinstance(nama_data, dict) and "node_type" in nama_data:
            nama = _deserialize_expr(nama_data)
        else:
            nama = _json_to_token(nama_data)
        nilai = _deserialize_expr(json_data.get("nilai"))
        return Assignment(nama, nilai)

    elif node_type == "PernyataanEkspresi":
        return PernyataanEkspresi(_deserialize_expr(json_data.get("ekspresi")))

    elif node_type == "Tulis":
        argumen_json = json_data.get("argumen", [])
        argumen = [_deserialize_expr(arg) for arg in argumen_json]
        return Tulis(argumen)

    elif node_type == "JikaMaka":
        kondisi = _deserialize_expr(json_data["kondisi"])
        blok_maka = Bagian([_deserialize_stmt(s) for s in json_data["blok_maka"]])

        rantai_lain_jika = []
        for elif_data in json_data.get("rantai_lain_jika", []):
            cond = _deserialize_expr(elif_data["kondisi"])
            body = Bagian([_deserialize_stmt(s) for s in elif_data["blok"]])
            rantai_lain_jika.append((cond, body))

        blok_lain = None
        if json_data.get("blok_lain"):
            blok_lain = Bagian([_deserialize_stmt(s) for s in json_data["blok_lain"]])

        return JikaMaka(kondisi, blok_maka, rantai_lain_jika, blok_lain)

    elif node_type == "Selama":
        token = _json_to_token(json_data["token"])
        kondisi = _deserialize_expr(json_data["kondisi"])
        badan = Bagian([_deserialize_stmt(s) for s in json_data["badan"]])
        return Selama(token, kondisi, badan)

    elif node_type == "Pilih":
        ekspresi = _deserialize_expr(json_data.get("ekspresi"))

        kasus = []
        for kasus_data in json_data.get("kasus", []):
            nilai = _deserialize_expr(kasus_data["nilai"])
            badan = Bagian([_deserialize_stmt(s) for s in kasus_data["badan"]])
            kasus.append(PilihKasus(nilai, badan))

        kasus_lainnya_data = json_data.get("kasus_lainnya")
        kasus_lainnya = None
        if kasus_lainnya_data:
            badan_lainnya = Bagian([_deserialize_stmt(s) for s in kasus_lainnya_data["badan"]])
            kasus_lainnya = KasusLainnya(badan_lainnya)

        return Pilih(ekspresi, kasus, kasus_lainnya)

    elif node_type == "Jodohkan":
        ekspresi = _deserialize_expr(json_data.get("ekspresi"))

        kasus = []
        for kasus_data in json_data.get("kasus", []):
            pola = _deserialize_pola(kasus_data["pola"])
            badan = Bagian([_deserialize_stmt(s) for s in kasus_data["badan"]])
            kasus.append(JodohkanKasus(pola, badan))

        return Jodohkan(ekspresi, kasus)

    elif node_type == "TipeDeklarasi":
        nama = _json_to_token(json_data.get("nama"))

        daftar_varian = []
        for varian_data in json_data.get("daftar_varian", []):
            nama_varian = _json_to_token(varian_data["nama"])
            parameter = [_json_to_token(p) for p in varian_data.get("parameter", [])]
            daftar_varian.append(Varian(nama_varian, parameter))

        return TipeDeklarasi(nama, daftar_varian)

    elif node_type == "FungsiDeklarasi":
        nama = _json_to_token(json_data["nama"])
        parameter = [_json_to_token(p) for p in json_data["parameter"]]
        badan = Bagian([_deserialize_stmt(s) for s in json_data["badan"]])
        return FungsiDeklarasi(nama, parameter, badan)

    elif node_type == "FungsiAsinkDeklarasi":
        nama = _json_to_token(json_data.get("nama"))
        parameter = [_json_to_token(p) for p in json_data.get("parameter", [])]
        badan = Bagian([_deserialize_stmt(s) for s in json_data.get("badan", [])])
        return FungsiAsinkDeklarasi(nama, parameter, badan)

    elif node_type == "PernyataanKembalikan":
        kata_kunci = _json_to_token(json_data["kata_kunci"])
        nilai = None
        if json_data.get("nilai"):
            nilai = _deserialize_expr(json_data["nilai"])
        return PernyataanKembalikan(kata_kunci, nilai)

    elif node_type == "Kelas":
        nama = _json_to_token(json_data.get("nama"))

        superkelas_data = json_data.get("superkelas")
        superkelas = _deserialize_expr(superkelas_data) if superkelas_data else None

        metode = []
        for metode_data in json_data.get("metode", []):
            metode_node = _deserialize_stmt(metode_data)
            metode.append(metode_node)

        return Kelas(nama, superkelas, metode)

    elif node_type == "AmbilSemua":
        path_file = _json_to_token(json_data.get("path_file"))
        alias_data = json_data.get("alias")
        alias = _json_to_token(alias_data) if alias_data else None
        return AmbilSemua(path_file, alias)

    elif node_type == "AmbilSebagian":
        daftar_simbol = [_json_to_token(s) for s in json_data.get("daftar_simbol", [])]
        path_file = _json_to_token(json_data.get("path_file"))
        return AmbilSebagian(daftar_simbol, path_file)

    elif node_type == "Pinjam":
        path_file = _json_to_token(json_data.get("path_file"))
        alias_data = json_data.get("alias")
        alias = _json_to_token(alias_data) if alias_data else None
        return Pinjam(path_file, alias)

    else:
        raise NotImplementedError(
            f"Deserialisasi untuk pernyataan tipe '{node_type}' belum diimplementasikan."
        )

def deserialize_ast(data: Dict[str, Any]) -> Bagian:
    """Mendeserialisasi kamus Python (dari JSON) menjadi AST Bagian."""
    ast_data = data.get("ast", {})
    body_json = ast_data.get("body", [])
    daftar_pernyataan = [_deserialize_stmt(p) for p in body_json]
    return Bagian(daftar_pernyataan)

def load_compiled_ast(json_path: str) -> Bagian:
    """Memuat file JSON yang di-compile oleh OCaml dan mengembalikannya sebagai AST Bagian."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return deserialize_ast(data)
