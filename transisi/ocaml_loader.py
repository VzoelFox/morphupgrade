import json
from typing import Any, Dict, List, Optional, Union
from .log_setup import logger
from . import absolute_sntx_morph as ast
from .absolute_sntx_morph import (
    Bagian, DeklarasiVariabel, Assignment, PernyataanEkspresi,
    Tulis, JikaMaka, Selama, FungsiDeklarasi, PernyataanKembalikan,
    Konstanta, Identitas, FoxBinary, FoxUnary, PanggilFungsi,
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
    "KOMA": TipeToken.KOMA, "TITIK_KOMA": TipeToken.TITIK_KOMA,
}

def _json_to_token(json_data: Dict[str, Any]) -> Token:
    """Mengubah sub-kamus JSON menjadi objek Token dengan error handling yang lebih baik."""
    tipe_str = json_data.get("tipe")
    tipe = TOKEN_TYPE_MAP.get(tipe_str)

    if tipe is None:
        logger.warning(
            f"Token type '{tipe_str}' tidak ditemukan di TOKEN_TYPE_MAP. "
            f"Mem-fallback ke TipeToken.NAMA jika memungkinkan, namun ini menandakan potensi masalah."
        )
        # Untuk kasus di mana token tidak kritis (misal: jenis deklarasi),
        # kita bisa coba fallback atau cukup log dan biarkan error terjadi.
        # Untuk sekarang, kita akan memunculkan error untuk fail-fast.
        available_types = ", ".join(sorted(TOKEN_TYPE_MAP.keys()))
        err_msg = (
            f"Tipe token tidak diketahui: '{tipe_str}'.\n"
            f"Tipe yang tersedia: {available_types}"
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

def _json_to_konstanta(literal_json: Dict[str, Any]) -> Konstanta:
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
                # Coba konversi ke float dulu untuk menangani kasus desimal dan saintifik
                # Lalu konversi ke int jika memungkinkan (tidak ada bagian desimal)
                float_val = float(nilai_literal)
                if float_val == int(float_val):
                    nilai_literal = int(float_val)
                else:
                    nilai_literal = float_val
            except (ValueError, OverflowError) as e:
                raise ValueError(
                    f"Nilai angka di luar jangkauan atau format tidak valid: '{nilai_literal}'\n"
                    f"Error: {e}"
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
    return Konstanta(dummy_token)


def _deserialize_expr(expr_json: Optional[Dict[str, Any]]) -> Optional[Xprs]:
    """Mendeserialisasi ekspresi JSON. Returns None jika expr_json adalah None."""
    if expr_json is None:
        return None

    desc = expr_json.get("deskripsi", {})
    node_type = desc.get("node_type")
    logger.debug(f"→ _deserialize_expr: memproses node '{node_type}'")

    # TODO: Tambahkan penanganan lokasi (eloc) jika diperlukan di masa depan

    if node_type == "konstanta":
        return _json_to_konstanta(desc.get("literal"))

    elif node_type == "identitas":
        return Identitas(_json_to_token(desc.get("token")))

    elif node_type == "fox_binary":
        kiri = _deserialize_expr(desc.get("kiri"))
        op = _json_to_token(desc.get("operator"))
        kanan = _deserialize_expr(desc.get("kanan"))
        return FoxBinary(kiri, op, kanan)

    elif node_type == "fox_unary":
        op = _json_to_token(desc.get("operator"))
        kanan = _deserialize_expr(desc.get("kanan"))
        return FoxUnary(op, kanan)

    elif node_type == "panggil_fungsi":
        callee = _deserialize_expr(desc["callee"])
        token = _json_to_token(desc["token"])
        argumen = [_deserialize_expr(a) for a in desc["argumen"]]
        return PanggilFungsi(callee, token, argumen)

    else:
        err_msg = f"Deserialisasi untuk ekspresi tipe '{node_type}' belum diimplementasikan."
        logger.error(err_msg)
        raise NotImplementedError(err_msg)

def _deserialize_stmt(stmt_json: Dict[str, Any]) -> St:
    """Mendeserialisasi pernyataan JSON menjadi objek St."""
    desc = stmt_json.get("deskripsi", {})
    node_type = desc.get("node_type")
    logger.debug(f"→ _deserialize_stmt: memproses node '{node_type}'")

    # TODO: Tambahkan penanganan lokasi (sloc) jika diperlukan di masa depan

    if node_type == "deklarasi_variabel":
        keyword = _json_to_token(desc.get("jenis_deklarasi"))
        nama = _json_to_token(desc.get("nama"))
        init = _deserialize_expr(desc.get("nilai"))
        return DeklarasiVariabel(keyword, nama, init)

    elif node_type == "assignment":
        # Di Python AST, assignment target bisa berupa token atau ekspresi (untuk atur properti)
        # Untuk sekarang, kita asumsikan selalu token
        nama = _json_to_token(desc.get("nama"))
        nilai = _deserialize_expr(desc.get("nilai"))
        return Assignment(nama, nilai)

    elif node_type == "pernyataan_ekspresi":
        return PernyataanEkspresi(_deserialize_expr(desc.get("ekspresi")))

    elif node_type == "tulis":
        argumen = [_deserialize_expr(arg) for arg in desc.get("argumen", [])]
        return Tulis(argumen)

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

        return JikaMaka(kondisi, blok_maka, rantai_lain_jika, blok_lain)

    elif node_type == "selama":
        token = _json_to_token(desc["token"])
        kondisi = _deserialize_expr(desc["kondisi"])
        badan = Bagian([_deserialize_stmt(s) for s in desc["badan"]])
        return Selama(token, kondisi, badan)

    elif node_type == "fungsi_deklarasi":
        nama = _json_to_token(desc["nama"])
        parameter = [_json_to_token(p) for p in desc["parameter"]]
        badan = Bagian([_deserialize_stmt(s) for s in desc["badan"]])
        return FungsiDeklarasi(nama, parameter, badan)

    elif node_type == "pernyataan_kembalikan":
        kata_kunci = _json_to_token(desc["kata_kunci"])
        nilai = _deserialize_expr(desc.get("nilai"))
        return PernyataanKembalikan(kata_kunci, nilai)

    else:
        err_msg = f"Deserialisasi untuk pernyataan tipe '{node_type}' belum diimplementasikan."
        logger.error(err_msg)
        raise NotImplementedError(err_msg)


def deserialize_ast(data: Dict[str, Any]) -> Bagian:
    """Mendeserialisasi kamus Python (dari JSON) menjadi AST Bagian."""
    # Validasi struktur dasar
    if "program" not in data:
        raise ValueError("JSON tidak valid: missing 'program' field")

    program_data = data.get("program", {})
    if "body" not in program_data:
        raise ValueError("JSON tidak valid: missing 'body' di program")

    body_json = program_data.get("body", [])
    logger.debug(f"Mendeserialisasi {len(body_json)} pernyataan tingkat atas.")
    daftar_pernyataan = [_deserialize_stmt(p) for p in body_json]
    logger.info("Deserialisasi AST dari data JSON berhasil diselesaikan.")
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
