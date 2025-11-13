import json
from typing import Any, Dict, List, Optional, Union
from .log_setup import logger
from . import absolute_sntx_morph as ast
from .absolute_sntx_morph import (
    Bagian, DeklarasiVariabel, Assignment, PernyataanEkspresi,
    Tulis, JikaMaka, Selama, FungsiDeklarasi, PernyataanKembalikan, Kelas,
    TipeDeklarasi, Jodohkan, Pilih, Varian, JodohkanKasus, PolaVarian, PolaEkspr,
    PilihKasus, KasusLainnya, AmbilSemua, AmbilSebagian, Pinjam, FungsiAsinkDeklarasi,
    Konstanta, Identitas, FoxBinary, FoxUnary, PanggilFungsi, Tunggu,
    Daftar, Kamus, Akses, AmbilProperti, AturProperti, Ini,
    St, Xprs
)
from .morph_t import Token, TipeToken

TOKEN_TYPE_MAP = {
    # Keywords
    "BIAR": TipeToken.BIAR, "TETAP": TipeToken.TETAP,
    "UBAH": TipeToken.UBAH, "EQUAL": TipeToken.SAMADENGAN,
    "JIKA": TipeToken.JIKA, "MAKA": TipeToken.MAKA,
    "LAIN": TipeToken.LAIN, "AKHIR": TipeToken.AKHIR,
    "SELAMA": TipeToken.SELAMA, "FUNGSI": TipeToken.FUNGSI,
    "KEMBALI": TipeToken.KEMBALI, "KEMBALIKAN": TipeToken.KEMBALIKAN,
    "TULIS": TipeToken.TULIS,
    "KELAS": TipeToken.KELAS, "WARISI": TipeToken.WARISI,
    "INI": TipeToken.INI, "INDUK": TipeToken.INDUK,
    "ASINK": TipeToken.ASINK, "TUNGGU": TipeToken.TUNGGU,
    "TIPE": TipeToken.TIPE, "JODOHKAN": TipeToken.JODOHKAN, "DENGAN": TipeToken.DENGAN,
    "PINJAM": TipeToken.PINJAM, "AMBIL_SEMUA": TipeToken.AMBIL_SEMUA,
    "AMBIL_SEBAGIAN": TipeToken.AMBIL_SEBAGIAN, "DARI": TipeToken.DARI,
    "SEBAGAI": TipeToken.SEBAGAI,
    "PILIH": TipeToken.PILIH, "KETIKA": TipeToken.KETIKA, "LAINNYA": TipeToken.LAINNYA,


    # Operators
    "PLUS": TipeToken.TAMBAH, "MINUS": TipeToken.KURANG,
    "BINTANG": TipeToken.KALI, "GARIS_MIRING": TipeToken.BAGI,
    "PANGKAT": TipeToken.PANGKAT, "PERSEN": TipeToken.MODULO,
    "SAMA_DENGAN": TipeToken.SAMA_DENGAN, "TIDAK_SAMA": TipeToken.TIDAK_SAMA,
    "KURANG_DARI": TipeToken.KURANG_DARI, "KURANG_SAMA": TipeToken.KURANG_SAMA,
    "LEBIH_DARI": TipeToken.LEBIH_DARI, "LEBIH_SAMA": TipeToken.LEBIH_SAMA,
    "DAN": TipeToken.DAN, "ATAU": TipeToken.ATAU, "TIDAK": TipeToken.TIDAK,

    # Literals & Identifiers
    "ANGKA": TipeToken.ANGKA, "TEKS": TipeToken.TEKS,
    "BENAR": TipeToken.BENAR, "SALAH": TipeToken.SALAH, "NIL": TipeToken.NIL,
    "NAMA": TipeToken.NAMA,

    # Delimiters
    "LPAREN": TipeToken.KURUNG_BUKA, "RPAREN": TipeToken.KURUNG_TUTUP,
    "LBRACKET": TipeToken.SIKU_BUKA, "RBRACKET": TipeToken.SIKU_TUTUP,
    "LBRACE": TipeToken.KURAWAL_BUKA, "RBRACE": TipeToken.KURAWAL_TUTUP,
    "KOMA": TipeToken.KOMA, "TITIK": TipeToken.TITIK,
    "TITIK_KOMA": TipeToken.TITIK_KOMA, "COLON": TipeToken.TITIK_DUA,
    "PIPE": TipeToken.GARIS_PEMISAH,
}

def _json_to_token(json_data: Dict[str, Any]) -> Token:
    """Mengubah sub-kamus JSON menjadi objek Token dengan error handling yang lebih baik."""
    tipe_str = json_data.get("tipe")
    tipe = TOKEN_TYPE_MAP.get(tipe_str)

    if tipe is None:
        # List available types untuk debugging
        available_types = ", ".join(sorted(TOKEN_TYPE_MAP.keys()))

        logger.warning(
            f"Token type '{tipe_str}' tidak ditemukan di TOKEN_TYPE_MAP.\n"
            f"Available types: {available_types}\n"
            f"Token data: {json_data}"
        )
        err_msg = (
            f"Tipe token tidak diketahui: '{tipe_str}'.\n"
            f"Tipe yang tersedia: {available_types}\n"
            f"Hint: Periksa output OCaml compiler atau tambahkan pemetaan di TOKEN_TYPE_MAP"
        )
        logger.error(err_msg)
        raise ValueError(err_msg)

    logger.debug(f"Token dikonversi: {tipe_str} -> {tipe.name}")
    return Token(
        tipe=tipe,
        nilai=json_data.get("nilai"),
        baris=json_data.get("baris", 0),
        kolom=json_data.get("kolom", 0)
    )

def _json_to_konstanta(literal_json: Dict[str, Any], lokasi: Optional[Any] = None) -> Konstanta:
    """Mengubah objek literal JSON menjadi node Konstanta."""
    tipe_literal = literal_json.get("tipe")
    nilai_literal = literal_json.get("nilai")

    # CRITICAL FIX: Robust type conversion
    if tipe_literal == "angka":
        token_type = TipeToken.ANGKA
        # Handle both string and numeric inputs
        if isinstance(nilai_literal, (int, float)):
            # Nilai sudah berupa angka, tidak perlu konversi
            pass
        elif isinstance(nilai_literal, str):
            logger.warning(
                f"Literal angka diterima sebagai string: '{nilai_literal}'. "
                "Ini valid, tapi pastikan OCaml compiler konsisten."
            )
            try:
                float_val = float(nilai_literal)

                # Tangani nilai-nilai khusus
                is_finite = float('-inf') < float_val < float('inf')
                if not is_finite:
                    logger.warning(f"Nilai numerik khusus terdeteksi: {nilai_literal}")
                    nilai_literal = float_val
                # Coba konversi ke int hanya jika nilainya finite dan merupakan bilangan bulat
                elif float_val == int(float_val):
                    nilai_literal = int(float_val)
                else:
                    nilai_literal = float_val
            except (ValueError, OverflowError) as e:
                raise ValueError(
                    f"Nilai angka di luar jangkauan atau format tidak valid: '{nilai_literal}'\n"
                    f"Error: {e}\n"
                    f"Hint: Pastikan OCaml compiler menghasilkan format numerik yang valid"
                ) from e
        else:
            raise TypeError(f"Nilai angka harus berupa number atau string, dapat: {type(nilai_literal)}")

    elif tipe_literal == "teks":
        token_type = TipeToken.TEKS
        # Ensure it's a string
        if not isinstance(nilai_literal, str):
            nilai_literal = str(nilai_literal)

    elif tipe_literal == "boolean":
        token_type = TipeToken.BENAR if nilai_literal else TipeToken.SALAH
        # Normalize boolean values
        if isinstance(nilai_literal, str):
            nilai_literal = nilai_literal.lower() in ('true', 'benar', '1')

    elif tipe_literal == "nil":
        token_type = TipeToken.NIL
        nilai_literal = None

    else:
        raise ValueError(f"Tipe literal tidak diketahui: {tipe_literal}")

    dummy_token = Token(tipe=token_type, nilai=nilai_literal, baris=0, kolom=0)
    return Konstanta(dummy_token, lokasi)


def _deserialize_expr(expr_json: Optional[Dict[str, Any]]) -> Optional[Xprs]:
    """Mendeserialisasi ekspresi JSON. Returns None jika expr_json adalah None."""
    if expr_json is None:
        return None

    desc = expr_json.get("deskripsi", {})
    lokasi = expr_json.get("lokasi")
    node_type = desc.get("node_type")
    logger.debug(f"→ _deserialize_expr: {node_type} | keys={list(desc.keys())}")

    if node_type == "konstanta":
        return _json_to_konstanta(desc.get("literal"), lokasi)

    elif node_type == "identitas":
        return Identitas(_json_to_token(desc.get("token")), lokasi)

    elif node_type == "fox_binary":
        kiri = _deserialize_expr(desc.get("kiri"))
        op = _json_to_token(desc.get("operator"))
        kanan = _deserialize_expr(desc.get("kanan"))
        return FoxBinary(kiri, op, kanan, lokasi)

    elif node_type == "fox_unary":
        op = _json_to_token(desc.get("operator"))
        kanan = _deserialize_expr(desc.get("kanan"))
        return FoxUnary(op, kanan, lokasi)

    elif node_type == "panggil_fungsi":
        callee = _deserialize_expr(desc["callee"])
        token = _json_to_token(desc["token"])
        argumen = [_deserialize_expr(a) for a in desc["argumen"]]
        return PanggilFungsi(callee, token, argumen, lokasi)

    elif node_type == "daftar":
        elemen = [_deserialize_expr(e) for e in desc.get("elemen", [])]
        return Daftar(elemen, lokasi)

    elif node_type == "kamus":
        pasangan = []
        for p in desc.get("pasangan", []):
            kunci = _deserialize_expr(p.get("kunci"))
            nilai = _deserialize_expr(p.get("nilai"))
            pasangan.append((kunci, nilai))
        return Kamus(pasangan, lokasi)

    elif node_type == "akses":
        objek = _deserialize_expr(desc.get("objek"))
        kunci = _deserialize_expr(desc.get("kunci"))
        return Akses(objek, kunci, lokasi)

    elif node_type == "ini":
        return Ini(_json_to_token(desc.get("token")), lokasi)

    elif node_type == "ambil_properti":
        objek = _deserialize_expr(desc.get("objek"))
        nama = _json_to_token(desc.get("nama"))
        return AmbilProperti(objek, nama, lokasi)

    elif node_type == "atur_properti":
        objek = _deserialize_expr(desc.get("objek"))
        nama = _json_to_token(desc.get("nama"))
        nilai = _deserialize_expr(desc.get("nilai"))
        return AturProperti(objek, nama, nilai, lokasi)

    elif node_type == "tunggu":
        token = _json_to_token(desc["token"])
        ekspresi = _deserialize_expr(desc["ekspresi"])
        return Tunggu(token, ekspresi, lokasi)

    else:
        # Berikan konteks penuh untuk debugging
        err_msg = (
            f"Deserialisasi untuk ekspresi tipe '{node_type}' belum diimplementasikan.\n"
            f"Data Node: {json.dumps(desc, indent=2, ensure_ascii=False)}\n"
            f"Hint: Tambahkan handler untuk '{node_type}' di _deserialize_expr()"
        )
        logger.error(err_msg)
        raise NotImplementedError(err_msg)

def _deserialize_stmt(stmt_json: Dict[str, Any]) -> St:
    """Mendeserialisasi pernyataan JSON menjadi objek St."""
    desc = stmt_json.get("deskripsi", {})
    lokasi = stmt_json.get("lokasi")
    node_type = desc.get("node_type")
    logger.debug(f"→ _deserialize_stmt: {node_type} | keys={list(desc.keys())}")

    if node_type == "deklarasi_variabel":
        keyword = _json_to_token(desc.get("jenis_deklarasi"))
        nama = _json_to_token(desc.get("nama"))
        init = _deserialize_expr(desc.get("nilai"))
        return DeklarasiVariabel(keyword, nama, init, lokasi)

    elif node_type == "assignment":
        # Di Python AST, assignment target bisa berupa token atau ekspresi (untuk atur properti)
        # Untuk sekarang, kita asumsikan selalu token
        nama = _json_to_token(desc.get("nama"))
        nilai = _deserialize_expr(desc.get("nilai"))
        return Assignment(nama, nilai, lokasi)

    elif node_type == "pernyataan_ekspresi":
        return PernyataanEkspresi(_deserialize_expr(desc.get("ekspresi")), lokasi)

    elif node_type == "tulis":
        argumen = [_deserialize_expr(arg) for arg in desc.get("argumen", [])]
        return Tulis(argumen, lokasi)

    elif node_type == "jika_maka":
        kondisi = _deserialize_expr(desc["kondisi"])
        blok_maka = Bagian([_deserialize_stmt(s) for s in desc["blok_maka"]])

        rantai_lain_jika = []
        for elif_data in desc.get("rantai_lain_jika", []):
            cond = _deserialize_expr(elif_data["kondisi"])
            body = Bagian([_deserialize_stmt(s) for s in elif_data["blok"]])
            rantai_lain_jika.append((cond, body))

        blok_lain = None
        if desc.get("blok_lain"):
            blok_lain = Bagian([_deserialize_stmt(s) for s in desc["blok_lain"]])

        return JikaMaka(kondisi, blok_maka, rantai_lain_jika, blok_lain, lokasi)

    elif node_type == "selama":
        token = _json_to_token(desc["token"])
        kondisi = _deserialize_expr(desc["kondisi"])
        badan = Bagian([_deserialize_stmt(s) for s in desc["badan"]])
        return Selama(token, kondisi, badan, lokasi)

    elif node_type == "fungsi_deklarasi":
        nama = _json_to_token(desc["nama"])
        parameter = [_json_to_token(p) for p in desc["parameter"]]
        badan = Bagian([_deserialize_stmt(s) for s in desc["badan"]])
        return FungsiDeklarasi(nama, parameter, badan, lokasi)

    elif node_type == "pernyataan_kembalikan":
        kata_kunci = _json_to_token(desc["kata_kunci"])
        nilai = _deserialize_expr(desc.get("nilai"))
        return PernyataanKembalikan(kata_kunci, nilai, lokasi)

    elif node_type == "kelas":
        nama = _json_to_token(desc["nama"])
        superkelas = _deserialize_expr(desc.get("superkelas"))
        metode = [_deserialize_stmt(m) for m in desc.get("metode", [])]
        return Kelas(nama, superkelas, metode, lokasi)

    elif node_type == "tipe_deklarasi":
        nama = _json_to_token(desc["nama"])
        varian = []
        for v in desc.get("varian", []):
            varian_nama = _json_to_token(v.get("nama"))
            parameter = [_json_to_token(p) for p in v.get("parameter", [])]
            varian.append(Varian(varian_nama, parameter))
        return TipeDeklarasi(nama, varian, lokasi)

    elif node_type == "jodohkan":
        target = _deserialize_expr(desc.get("target"))
        kasus = []
        for c in desc.get("kasus", []):
            # HACK: Interim solution, bungkus expr sebagai PolaEkspr
            pola_expr = _deserialize_expr(c.get("pola"))
            pola = PolaEkspr(pola_expr)
            badan = Bagian([_deserialize_stmt(s) for s in c.get("badan", [])])
            kasus.append(JodohkanKasus(pola, badan))
        return Jodohkan(target, kasus, lokasi)

    elif node_type == "pilih":
        target = _deserialize_expr(desc.get("target"))
        kasus = []
        for c in desc.get("kasus", []):
            nilai = [_deserialize_expr(v) for v in c.get("nilai", [])]
            badan = Bagian([_deserialize_stmt(s) for s in c.get("badan", [])])
            kasus.append(PilihKasus(nilai, badan))
        lainnya = None
        if desc.get("lainnya"):
            lainnya = KasusLainnya(Bagian([_deserialize_stmt(s) for s in desc.get("lainnya")]))
        return Pilih(target, kasus, lainnya, lokasi)

    elif node_type == "ambil_semua":
        path = _json_to_token(desc["path"])
        alias = desc.get("alias")
        if alias:
            alias = _json_to_token(alias)
        return AmbilSemua(path, alias, lokasi)

    elif node_type == "ambil_sebagian":
        symbols = [_json_to_token(s) for s in desc["symbols"]]
        path = _json_to_token(desc["path"])
        return AmbilSebagian(symbols, path, lokasi)

    elif node_type == "pinjam":
        path = _json_to_token(desc["path"])
        alias = desc.get("alias")
        if alias:
            alias = _json_to_token(alias)
        return Pinjam(path, alias, lokasi)

    elif node_type == "fungsi_asink_deklarasi":
        nama = _json_to_token(desc["nama"])
        parameter = [_json_to_token(p) for p in desc["parameter"]]
        badan = Bagian([_deserialize_stmt(s) for s in desc["badan"]])
        return FungsiAsinkDeklarasi(nama, parameter, badan, lokasi)

    else:
        # Berikan konteks penuh untuk debugging
        err_msg = (
            f"Deserialisasi untuk pernyataan tipe '{node_type}' belum diimplementasikan.\n"
            f"Data Node: {json.dumps(desc, indent=2, ensure_ascii=False)}\n"
            f"Hint: Tambahkan handler untuk '{node_type}' di _deserialize_stmt()"
        )
        logger.error(err_msg)
        raise NotImplementedError(err_msg)


def _validate_json_structure(data: Dict[str, Any]) -> list[str]:
    """
    Validasi struktural dasar untuk mendeteksi JSON yang salah format sejak awal.
    Mengembalikan daftar masalah (kosong jika valid).
    """
    issues = []

    if "program" not in data:
        issues.append("Field 'program' yang hilang di tingkat root")
        return issues  # Fatal, tidak bisa melanjutkan

    program = data.get("program", {})
    if not isinstance(program, dict):
        issues.append(f"'program' harus berupa dict, dapat: {type(program)}")
        return issues

    if "body" not in program:
        issues.append("Field 'body' yang hilang di dalam program")

    if not isinstance(program.get("body"), list):
        issues.append(f"'body' harus berupa list, dapat: {type(program.get('body'))}")

    return issues


def deserialize_ast(data: Dict[str, Any]) -> Bagian:
    """Mendeserialisasi kamus Python (dari JSON) menjadi AST Bagian."""
    logger.debug("Memulai validasi struktur JSON...")

    # Validasi terlebih dahulu sebelum diproses
    issues = _validate_json_structure(data)
    if issues:
        err_msg = "Struktur JSON tidak valid:\n" + "\n".join(f"  - {issue}" for issue in issues)
        logger.error(err_msg)
        raise ValueError(err_msg)

    logger.debug("Struktur JSON valid, melanjutkan deserialisasi...")

    program_data = data["program"]
    body_json = program_data["body"]

    logger.debug(f"Mendeserialisasi {len(body_json)} pernyataan tingkat atas.")
    daftar_pernyataan = [_deserialize_stmt(p) for p in body_json]
    logger.info(f"Deserialisasi AST berhasil: {len(daftar_pernyataan)} pernyataan diproses.")

    return Bagian(daftar_pernyataan)


def load_compiled_ast(json_path: str) -> Bagian:
    """Memuat file JSON dengan validasi."""
    logger.info(f"Memuat AST yang dikompilasi dari OCaml dari: {json_path}")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        logger.error(f"File AST tidak ditemukan di path: {json_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Gagal mem-parsing JSON dari {json_path}: {e}")
        raise

    return deserialize_ast(data)
