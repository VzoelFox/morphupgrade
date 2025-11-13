# tests/test_ocaml_loader_robustness.py
import pytest
from transisi.ocaml_loader import deserialize_ast

def test_malformed_numeric_literal_raises_error():
    """
    Memverifikasi bahwa literal angka dengan tipe nilai yang salah (misalnya, list)
    di dalam JSON AST akan melempar TypeError yang terkendali, bukan crash.
    """
    malformed_ast_json = {
        "program": {
            "body": [
                {
                    "deskripsi": {
                        "node_type": "pernyataan_ekspresi",
                        "ekspresi": {
                            "deskripsi": {
                                "node_type": "konstanta",
                                "literal": {
                                    "tipe": "angka",
                                    # Nilai ini seharusnya number atau string, bukan list.
                                    # Ini akan menyebabkan float() melempar TypeError.
                                    "nilai": [1, 2, 3]
                                }
                            },
                            "lokasi": {}
                        }
                    },
                    "lokasi": {}
                }
            ]
        }
    }

    # Kita mengharapkan TypeError karena float() tidak bisa dipanggil pada list.
    with pytest.raises(TypeError, match="Nilai angka harus berupa number atau string"):
        deserialize_ast(malformed_ast_json)

def test_unknown_token_type_raises_error():
    """
    Memverifikasi bahwa tipe token yang tidak dikenal di JSON AST
    akan melempar ValueError yang informatif.
    """
    malformed_ast_json = {
        "program": {
            "body": [
                {
                    "deskripsi": {
                        "node_type": "deklarasi_variabel",
                        # Tipe token "SALAH_KETIK" tidak ada di TOKEN_TYPE_MAP
                        "jenis_deklarasi": {"tipe": "SALAH_KETIK", "nilai": "biar", "baris": 1, "kolom": 1},
                        "nama": {"tipe": "NAMA", "nilai": "x", "baris": 1, "kolom": 5},
                        "nilai": None
                    },
                    "lokasi": {}
                }
            ]
        }
    }

    with pytest.raises(ValueError, match="Tipe token tidak diketahui: 'SALAH_KETIK'"):
        deserialize_ast(malformed_ast_json)
