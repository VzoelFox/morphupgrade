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

        assert "ast" in json_output
        assert "body" in json_output["ast"]
        assert len(json_output["ast"]["body"]) == 1

        stmt = json_output["ast"]["body"][0]
        assert stmt["node_type"] == "JikaMaka"
        assert stmt["kondisi"]["node_type"] == "FoxBinary"
        assert stmt["kondisi"]["operator"]["tipe"] == "LEBIH_DARI"

    def test_function_declaration(self):
        """Test: fungsi tambah(a, b) maka kembali a + b akhir"""
        source = """fungsi tambah(a, b) maka
kembali a + b
akhir
"""
        json_output = compile_morph_to_json(source)

        stmt = json_output["ast"]["body"][0]
        assert stmt["node_type"] == "FungsiDeklarasi"
        assert stmt["nama"]["tipe"] == "NAMA"
        assert stmt["nama"]["nilai"] == "tambah"
        assert len(stmt["parameter"]) == 2
        assert len(stmt["badan"]) == 1

    def test_while_loop(self):
        """Test: selama x < 10 maka ubah x = x + 1 akhir"""
        source = """biar x = 0
selama x < 10 maka
ubah x = x + 1
akhir
"""
        json_output = compile_morph_to_json(source)

        assert len(json_output["ast"]["body"]) == 2
        loop_stmt = json_output["ast"]["body"][1]
        assert loop_stmt["node_type"] == "Selama"
        assert loop_stmt["kondisi"]["node_type"] == "FoxBinary"


class TestPythonDeserializer:
    """Test Python AST deserialization from JSON."""

    def test_deserialize_simple_if(self):
        """Test deserializing JikaMaka structure."""
        json_data = {
            "ast": {
                "body": [{
                    "node_type": "JikaMaka",
                    "kondisi": {
                        "node_type": "FoxBinary",
                        "kiri": {
                            "node_type": "Konstanta",
                            "token": {"tipe": "ANGKA", "nilai": 5.0, "baris": 1, "kolom": 6}
                        },
                        "operator": {"tipe": "LEBIH_DARI", "nilai": None, "baris": 0, "kolom": 0},
                        "kanan": {
                            "node_type": "Konstanta",
                            "token": {"tipe": "ANGKA", "nilai": 3.0, "baris": 1, "kolom": 10}
                        }
                    },
                    "blok_maka": [{
                        "node_type": "Tulis",
                        "argumen": [{
                            "node_type": "Konstanta",
                            "token": {"tipe": "ANGKA", "nilai": 10.0, "baris": 2, "kolom": 7}
                        }]
                    }],
                    "rantai_lain_jika": [],
                    "blok_lain": None
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
            "ast": {
                "body": [{
                    "node_type": "FungsiDeklarasi",
                    "nama": {"tipe": "NAMA", "nilai": "tambah", "baris": 1, "kolom": 8},
                    "parameter": [
                        {"tipe": "NAMA", "nilai": "a", "baris": 1, "kolom": 15},
                        {"tipe": "NAMA", "nilai": "b", "baris": 1, "kolom": 18}
                    ],
                    "badan": [{
                        "node_type": "PernyataanKembalikan",
                        "kata_kunci": {"tipe": "KEMBALI", "nilai": None, "baris": 2, "kolom": 1},
                        "nilai": {
                            "node_type": "FoxBinary",
                            "kiri": {
                                "node_type": "Identitas",
                                "token": {"tipe": "NAMA", "nilai": "a", "baris": 2, "kolom": 10}
                            },
                            "operator": {"tipe": "PLUS", "nilai": None, "baris": 0, "kolom": 0},
                            "kanan": {
                                "node_type": "Identitas",
                                "token": {"tipe": "NAMA", "nilai": "b", "baris": 2, "kolom": 14}
                            }
                        }
                    }]
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

    @pytest.mark.asyncio
    async def test_execute_simple_if(self, capsys):
        """Full pipeline test for if statement."""
        source = "jika 5 > 3 maka\ntulis(10)\nakhir\n"
        json_output = compile_morph_to_json(source)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(json_output, f)
            json_path = f.name

        try:
            morph = Morph()
            await morph.jalankan_dari_ocaml_ast(json_path)
            captured = capsys.readouterr()
            assert "10" in captured.out
        finally:
            os.unlink(json_path)

    @pytest.mark.asyncio
    async def test_execute_function_call(self, capsys):
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
            await morph.jalankan_dari_ocaml_ast(json_path)
            captured = capsys.readouterr()
            assert "8" in captured.out
        finally:
            os.unlink(json_path)
