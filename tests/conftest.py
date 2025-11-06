# tests/conftest.py
"""
Pytest configuration and shared fixtures.
"""
import pytest
import sys
import os
from io import StringIO

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from morph_engine.lx import Leksikal
from morph_engine.crusher import Pengurai
from morph_engine.translator import Translator
from morph_engine.Morph import jalankan_kode


# ============================================================================
# FIXTURES - Reusable Test Components
# ============================================================================

@pytest.fixture
def lexer_factory():
    """Factory untuk membuat Leksikal instance dengan kode input."""
    def _create_lexer(source_code):
        return Leksikal(source_code)
    return _create_lexer


@pytest.fixture
def parser_factory():
    """Factory untuk membuat Pengurai instance dari kode input."""
    def _create_parser(source_code, debug_mode=False):
        lexer = Leksikal(source_code)
        tokens = lexer.buat_token()
        return Pengurai(tokens, debug_mode=debug_mode)
    return _create_parser


@pytest.fixture
def interpreter_factory():
    """Factory untuk membuat Penerjemah instance dari kode input."""
    def _create_interpreter(source_code):
        lexer = Leksikal(source_code)
        tokens = lexer.buat_token()
        parser = Pengurai(tokens)
        ast = parser.urai()
        return Translator(ast)
    return _create_interpreter


@pytest.fixture
def capture_output():
    """Fixture untuk menangkap stdout output dari tulis()."""
    def _capture(source_code):
        # Redirect stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = captured_output = StringIO()
        sys.stderr = captured_stderr = StringIO()

        try:
            # Menyediakan path dummy agar impor relatif dapat berfungsi dari root proyek
            jalankan_kode(source_code, file_path=os.path.join(os.getcwd(), "<test_case>"))
            stdout_val = captured_output.getvalue()
            stderr_val = captured_stderr.getvalue()
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        return stdout_val.strip() if not stderr_val else stderr_val.strip()

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
