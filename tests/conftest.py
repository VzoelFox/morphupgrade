# tests/conftest.py
"""
Pytest configuration and shared fixtures.
"""
import pytest
import sys
import os
from io import StringIO

# ============================================================================
# FIXTURES - Reusable Test Components
# ============================================================================

@pytest.fixture(scope="function")
def run_morph_program():
    """Fixture SINKRON untuk menjalankan interpreter dan mengembalikan stdout dan daftar kesalahan."""
    def _run(source_code, filename="<tes>"):
        from transisi.Morph import Morph
        morph = Morph()
        output_val, errors_val = morph._jalankan_sync(source_code, filename)
        output_val = output_val or ""
        return output_val.strip(), errors_val
    return _run

@pytest.fixture
async def run_morph_program_async():
    """Fixture ASINKRON untuk menjalankan interpreter, digunakan oleh tes @pytest.mark.asyncio."""
    async def _run(source_code, filename="<tes>"):
        from transisi.Morph import Morph
        morph = Morph()
        output_val, errors_val = await morph._jalankan_async(source_code, filename)
        output_val = output_val or ""
        return output_val.strip(), errors_val
    return _run


@pytest.fixture
def capture_output(run_morph_program):
    """
    Fixture yang disederhanakan untuk menangkap output.
    Menggunakan fixture sinkron untuk kompatibilitas.
    """
    def _capture(source_code):
        output, errors = run_morph_program(source_code)
        if errors:
            return "\\n".join(errors)
        return output
    return _capture


@pytest.fixture
def fixture_file_path():
    """Helper untuk mendapatkan path ke fixture files."""
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    def _get_path(category, filename):
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
