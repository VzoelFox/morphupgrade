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


# Impor komponen dari engine BARU menggunakan path absolut
from morphupgrade.morph_engine_py.leksikal import Leksikal
from morphupgrade.morph_engine_py.pengurai import Pengurai
from morphupgrade.morph_engine_py.penerjemah import Penerjemah


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
        try:
            # Alur kerja untuk engine BARU
            lexer = Leksikal(source_code)
            tokens = lexer.buat_token()

            parser = Pengurai(tokens)
            ast = parser.urai()

            # Teruskan file_path ke Penerjemah
            interpreter = Penerjemah(ast, file_path=file_path)
            interpreter.interpretasi()

            stdout_val = captured_output.getvalue()
            stderr_val = captured_stderr.getvalue()
            output_val = stdout_val.strip() if not stderr_val else stderr_val.strip()

        except Exception as e:
            # Tangkap semua exception (Parser, Runtime) dan jadikan output
            output_val = str(e).strip()
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
