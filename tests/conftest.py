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
# Tambahkan path ke engine baru dan lama untuk mengakomodasi refactoring
sys.path.insert(0, os.path.join(base_dir, 'morphupgrade', 'morph_engine_py'))
sys.path.insert(0, os.path.join(base_dir, 'morph_engine'))


from morph_engine.Morph import Morph


# ============================================================================
# FIXTURES - Reusable Test Components
# ============================================================================

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
            # Gunakan kelas Morph yang baru untuk menjalankan kode
            morph_app = Morph()
            morph_app._jalankan(source_code) # Panggil metode internal untuk eksekusi
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
