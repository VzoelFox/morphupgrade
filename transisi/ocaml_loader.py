import json
from typing import Any, Dict, List, Optional

from .absolute_sntx_morph import (
    Bagian, DeklarasiVariabel, Assignment, FoxBinary, Konstanta, Identitas, St, Xprs
)
from .morph_t import Token, TipeToken

def _json_to_token(json_data: Dict[str, Any]) -> Token:
    """Mengubah sub-kamus JSON menjadi objek Token."""
    # Nilai tipe token diabaikan untuk saat ini, karena tidak ada dalam output OCaml
    # Kita bisa membuatnya berdasarkan lexeme jika diperlukan.
    return Token(
        tipe=TipeToken.IDENTIFIER, # Tipe dummy
        nilai=json_data['lexeme'],
        baris=json_data['line'],
        kolom=json_data['col']
    )

def _deserialize_expr(json_data: Dict[str, Any]) -> Xprs:
    """Mendeserialisasi ekspresi JSON menjadi objek Xprs."""
    node_type = json_data[0] # Tipe node ada di elemen pertama dari list
    node_data = json_data[1]

    if node_type == "Konstanta":
        # Konvensi: Konstanta berisi satu token
        return Konstanta(_json_to_token(node_data))
    elif node_type == "Identitas":
        # Konvensi: Identitas berisi satu token
        return Identitas(_json_to_token(node_data))
    elif node_type == "FoxBinary":
        # Konvensi: FoxBinary adalah list [expr_kiri, token_op, expr_kanan]
        kiri = _deserialize_expr(node_data[0])
        op = _json_to_token(node_data[1])
        kanan = _deserialize_expr(node_data[2])
        return FoxBinary(kiri, op, kanan)
    else:
        raise NotImplementedError(f"Deserialisasi untuk ekspresi tipe '{node_type}' belum diimplementasikan.")

def _deserialize_stmt(json_data: Dict[str, Any]) -> St:
    """Mendeserialisasi pernyataan JSON menjadi objek St."""
    node_type = json_data[0]
    node_data = json_data[1]

    if node_type == "DeklarasiVariabel":
        # Konvensi: [token_keyword, token_nama, optional_expr_init]
        keyword = _json_to_token(node_data[0])
        nama = _json_to_token(node_data[1])
        # Inisialisasi bisa jadi ["Some", expr] atau ["None"]
        init_json = node_data[2]
        init = _deserialize_expr(init_json[1]) if init_json[0] == "Some" else None
        return DeklarasiVariabel(keyword, nama, init)
    elif node_type == "Assignment":
        # Konvensi: [token_nama, expr_nilai]
        nama = _json_to_token(node_data[0])
        nilai = _deserialize_expr(node_data[1])
        return Assignment(nama, nilai)
    else:
        raise NotImplementedError(f"Deserialisasi untuk pernyataan tipe '{node_type}' belum diimplementasikan.")

def deserialize_ast(data: Dict[str, Any]) -> Bagian:
    """
    Mendeserialisasi kamus Python (dari JSON) menjadi AST Bagian.
    Format JSON OCaml yang diharapkan:
    {
      "daftar_pernyataan": [
        ["DeklarasiVariabel", [token, token, ["Some", expr]]],
        ...
      ]
    }
    """
    pernyataan_json = data.get("daftar_pernyataan", [])
    daftar_pernyataan = [_deserialize_stmt(p) for p in pernyataan_json]
    return Bagian(daftar_pernyataan)

def load_compiled_ast(json_path: str) -> Bagian:
    """Memuat file JSON yang di-compile oleh OCaml dan mengembalikannya sebagai AST Bagian."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return deserialize_ast(data)
