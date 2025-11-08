# tests/conftest.py
"""
Pytest configuration and shared fixtures.
"""
import pytest
import sys
import os
from io import StringIO

# Add parent directory to path for imports
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, base_dir)


# Impor komponen dari engine yang stabil
from morph_engine.lx import Leksikal
from morph_engine.crusher import Pengurai
from morph_engine.translator import Penerjemah
from morph_engine.error_utils import FormatterKesalahan
from morph_engine.translator import KesalahanRuntime


# ============================================================================
# FIXTURES - Reusable Test Components
# ============================================================================

@pytest.fixture
def capture_output():
    """Fixture untuk menangkap stdout output dari tulis()."""
    def _capture(source_code, file_path="dummy_test_file.fox"):
        # Redirect stdout dan stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = captured_output = StringIO()
        sys.stderr = captured_stderr = StringIO()

        output_val = ""
        formatter = FormatterKesalahan(source_code)

        try:
            # Alur kerja untuk engine stabil
            lexer = Leksikal(source_code)
            tokens, lexer_errors = lexer.buat_token()

            if lexer_errors:
                for pesan, baris, kolom in lexer_errors:
                    print(formatter.format_lexer(pesan, baris, kolom), file=sys.stderr)
            else:
                parser = Pengurai(tokens)
                program = parser.urai()

                if parser.daftar_kesalahan:
                    for token, pesan in parser.daftar_kesalahan:
                        print(formatter.format_parser(token, pesan), file=sys.stderr)
                elif program:
                    interpreter = Penerjemah(formatter)
                    interpreter.terjemahkan(program)

            stdout_val = captured_output.getvalue()
            stderr_val = captured_stderr.getvalue()
            output_val = stdout_val.strip() if not stderr_val else stderr_val.strip()

        except KesalahanRuntime as e:
            # Tangkap kesalahan runtime dari interpreter
            print(formatter.format_runtime(e), file=sys.stderr)
            output_val = captured_stderr.getvalue().strip()
        except Exception as e:
            # Tangkap semua exception lain yang tak terduga
            output_val = f"UNEXPECTED ERROR: {str(e)}".strip()
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        return output_val

    return _capture


@pytest.fixture
def fixture_file_path():
    """Helper untuk mendapatkan path ke fixture files."""
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')

    def _get_path(category, filename):
        """
        Args:
            category: 'valid_programs' atau 'invalid_programs'
            filename: nama file (e.g., 'hello_world.fox')
        """
        return os.path.join(fixtures_dir, category, filename)

    return _get_path


@pytest.fixture
def load_fixture():
    """Load fixture file content."""
    def _load(category, filename):
        fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        path = os.path.join(fixtures_dir, category, filename)

        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    return _load


# ============================================================================
# PARAMETRIZE HELPERS
# ============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
