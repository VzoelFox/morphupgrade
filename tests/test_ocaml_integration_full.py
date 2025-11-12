"""
Full integration test suite for OCaml parser → Python interpreter
"""
import pytest
import json
import subprocess
import tempfile
import os
from pathlib import Path

from transisi.ocaml_loader import load_compiled_ast, deserialize_ast
from transisi.Morph import Morph
from transisi import absolute_sntx_morph as ast

# Path constants
UNIVERSAL_DIR = Path(__file__).parent.parent / "universal"
COMPILER = UNIVERSAL_DIR / "_build" / "default" / "main.exe"
SAMPLES_DIR = Path(__file__).parent / "samples"


def compile_morph_to_json(source_code: str) -> dict:
    """Compile MORPH source to JSON using OCaml compiler."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.morph', delete=False) as f:
        f.write(source_code)
        temp_file = f.name

    output_file = temp_file + ".json"

    try:
        subprocess.run(
            [str(COMPILER), temp_file, output_file],
            capture_output=True,
            text=True,
            check=True
        )
        with open(output_file, "r") as f:
            return json.load(f)
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Compilation failed:\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}")
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        if os.path.exists(output_file):
            os.unlink(output_file)


class TestOCamlParserIntegration:
    """Test OCaml parser output structure."""

    def test_simple_if(self):
        """Test: jika 5 > 3 maka tulis(10) akhir"""
        source = "jika 5 > 3 maka\ntulis(10)\nakhir\n"
        json_output = compile_morph_to_json(source)

        assert "program" in json_output
        assert "body" in json_output["program"]
        assert len(json_output["program"]["body"]) == 1

        stmt_node = json_output["program"]["body"][0]
        assert "deskripsi" in stmt_node
        assert "lokasi" in stmt_node

        stmt_desc = stmt_node["deskripsi"]
        assert stmt_desc["node_type"] == "jika_maka"

        kondisi_desc = stmt_desc["kondisi"]["deskripsi"]
        assert kondisi_desc["node_type"] == "fox_binary"
        assert kondisi_desc["operator"]["tipe"] == "LEBIH_DARI"

    def test_function_declaration(self):
        """Test: fungsi tambah(a, b) maka kembali a + b akhir"""
        source = """fungsi tambah(a, b) maka
kembali a + b
akhir
"""
        json_output = compile_morph_to_json(source)

        stmt_desc = json_output["program"]["body"][0]["deskripsi"]
        assert stmt_desc["node_type"] == "fungsi_deklarasi"
        assert stmt_desc["nama"]["tipe"] == "NAMA"
        assert stmt_desc["nama"]["nilai"] == "tambah"
        assert len(stmt_desc["parameter"]) == 2
        assert len(stmt_desc["badan"]) == 1

    def test_while_loop(self):
        """Test: selama x < 10 maka ubah x = x + 1 akhir"""
        source = """biar x = 0
selama x < 10 maka
ubah x = x + 1
akhir
"""
        json_output = compile_morph_to_json(source)

        assert len(json_output["program"]["body"]) == 2
        loop_stmt_desc = json_output["program"]["body"][1]["deskripsi"]
        assert loop_stmt_desc["node_type"] == "selama"
        assert loop_stmt_desc["kondisi"]["deskripsi"]["node_type"] == "fox_binary"


class TestPythonDeserializer:
    """Test Python AST deserialization from JSON."""

    def test_deserialize_simple_if(self):
        """Test deserializing JikaMaka structure."""
        json_data = {
            "program": {
                "body": [{
                    "deskripsi": {
                        "node_type": "jika_maka",
                        "kondisi": {
                            "deskripsi": {
                                "node_type": "fox_binary",
                                "kiri": { "deskripsi": { "node_type": "konstanta", "literal": {"tipe": "angka", "nilai": 5.0}}},
                                "operator": {"tipe": "LEBIH_DARI"},
                                "kanan": { "deskripsi": { "node_type": "konstanta", "literal": {"tipe": "angka", "nilai": 3.0}}}
                            },
                            "lokasi": {}
                        },
                        "blok_maka": [{
                            "deskripsi": {
                                "node_type": "tulis",
                                "argumen": [{
                                    "deskripsi": { "node_type": "konstanta", "literal": {"tipe": "angka", "nilai": 10.0}},
                                    "lokasi": {}
                                }]
                            },
                            "lokasi": {}
                        }],
                        "rantai_lain_jika": [],
                        "blok_lain": None
                    },
                    "lokasi": {}
                }]
            }
        }


        ast_obj = deserialize_ast(json_data)

        assert isinstance(ast_obj, ast.Bagian)
        assert len(ast_obj.daftar_pernyataan) == 1

        stmt = ast_obj.daftar_pernyataan[0]
        assert isinstance(stmt, ast.JikaMaka)
        assert isinstance(stmt.kondisi, ast.FoxBinary)
        assert isinstance(stmt.blok_maka, ast.Bagian)

    def test_deserialize_function(self):
        """Test deserializing FungsiDeklarasi."""
        json_data = {
            "program": {
                "body": [{
                    "deskripsi": {
                        "node_type": "fungsi_deklarasi",
                        "nama": {"tipe": "NAMA", "nilai": "tambah"},
                        "parameter": [
                            {"tipe": "NAMA", "nilai": "a"},
                            {"tipe": "NAMA", "nilai": "b"}
                        ],
                        "badan": [{
                            "deskripsi": {
                                "node_type": "pernyataan_kembalikan",
                                "kata_kunci": {"tipe": "KEMBALI"},
                                "nilai": {
                                    "deskripsi": {
                                        "node_type": "fox_binary",
                                        "kiri": {"deskripsi": {"node_type": "identitas", "token": {"tipe": "NAMA", "nilai": "a"}}},
                                        "operator": {"tipe": "PLUS"},
                                        "kanan": {"deskripsi": {"node_type": "identitas", "token": {"tipe": "NAMA", "nilai": "b"}}}
                                    },
                                    "lokasi": {}
                                }
                            },
                            "lokasi": {}
                        }]
                    },
                    "lokasi": {}
                }]
            }
        }


        ast_obj = deserialize_ast(json_data)
        stmt = ast_obj.daftar_pernyataan[0]

        assert isinstance(stmt, ast.FungsiDeklarasi)
        assert stmt.nama.nilai == "tambah"
        assert len(stmt.parameter) == 2
        assert stmt.parameter[0].nilai == "a"


class TestEndToEndExecution:
    """Test complete pipeline: Source → OCaml → JSON → Python → Execute"""

    def test_execute_simple_if(self, capsys):
        """Full pipeline test for if statement."""
        source = "jika 5 > 3 maka\ntulis(10)\nakhir\n"
        json_output = compile_morph_to_json(source)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(json_output, f)
            json_path = f.name

        try:
            morph = Morph()
            morph.jalankan_dari_ocaml_ast(json_path)
            captured = capsys.readouterr()
            assert "10" in captured.out
        finally:
            os.unlink(json_path)

    def test_execute_function_call(self, capsys):
        """Full pipeline test for function declaration and call."""
        source = """fungsi tambah(a, b) maka
kembali a + b
akhir

biar hasil = tambah(5, 3)
tulis(hasil)
"""
        json_output = compile_morph_to_json(source)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(json_output, f)
            json_path = f.name

        try:
            morph = Morph()
            morph.jalankan_dari_ocaml_ast(json_path)
            captured = capsys.readouterr()
            assert "8" in captured.out
        finally:
            os.unlink(json_path)
