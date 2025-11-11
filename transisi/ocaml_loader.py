import json
from typing import Any, Dict, List, Optional

from .absolute_sntx_morph import (
    Bagian, DeklarasiVariabel, Assignment, FoxBinary, Konstanta, Identitas, St, Xprs, Tulis,
    PernyataanEkspresi
)
from .morph_t import Token, TipeToken

# Mapping dari string JSON ke enum TipeToken Python
TOKEN_TYPE_MAP = {
    "BIAR": TipeToken.BIAR, "UBAH": TipeToken.UBAH,
    "PLUS": TipeToken.TAMBAH, "MINUS": TipeToken.KURANG, "BINTANG": TipeToken.KALI,
    "GARIS_MIRING": TipeToken.BAGI, "PANGKAT": TipeToken.PANGKAT, "PERSEN": TipeToken.MODULO,
    "SAMA_DENGAN": TipeToken.SAMA_DENGAN,
    "TULIS": TipeToken.TULIS,
    "ANGKA": TipeToken.ANGKA, "NAMA": TipeToken.NAMA,
    "LPAREN": TipeToken.KURUNG_BUKA, "RPAREN": TipeToken.KURUNG_TUTUP, "KOMA": TipeToken.KOMA,
    "EOF": TipeToken.ADS
}

def _json_to_token(json_data: Dict[str, Any]) -> Token:
    """Mengubah sub-kamus JSON menjadi objek Token."""
    tipe_str = json_data.get("tipe")
    tipe = TOKEN_TYPE_MAP.get(tipe_str)
    if tipe is None:
        raise ValueError(f"Tipe token tidak diketahui: '{tipe_str}'")

    return Token(
        tipe=tipe,
        nilai=json_data.get("nilai"), # Bisa jadi float, string, atau null
        baris=json_data.get("baris"),
        kolom=json_data.get("kolom")
    )

def _deserialize_expr(json_data: Dict[str, Any]) -> Xprs:
    """Mendeserialisasi ekspresi JSON menjadi objek Xprs."""
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
    else:
        raise NotImplementedError(f"Deserialisasi untuk ekspresi tipe '{node_type}' belum diimplementasikan.")

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
        nama = _json_to_token(json_data.get("nama"))
        nilai = _deserialize_expr(json_data.get("nilai"))
        return Assignment(nama, nilai)
    elif node_type == "Tulis":
        argumen_json = json_data.get("argumen", [])
        argumen = [_deserialize_expr(arg) for arg in argumen_json]
        return Tulis(argumen)
    elif node_type == "PernyataanEkspresi":
        return PernyataanEkspresi(_deserialize_expr(json_data.get("ekspresi")))
    else:
        raise NotImplementedError(f"Deserialisasi untuk pernyataan tipe '{node_type}' belum diimplementasikan.")

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
