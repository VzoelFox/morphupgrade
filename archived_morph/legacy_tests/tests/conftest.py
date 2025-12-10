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

@pytest.fixture
def run_morph_program():
    """Fixture untuk menjalankan interpreter dan mengembalikan stdout dan daftar kesalahan mentah."""
    def _run(source_code, filename="<tes>", external_objects=None):
        try:
            from transisi.Morph import Morph
            morph = Morph()
            # Panggil _jalankan_sync dan tangkap output dan error yang dikembalikan
            output_val, errors_val = morph._jalankan_sync(
                source_code, filename, ffi_objects=external_objects
            )

            # Pastikan output adalah string, bahkan jika None
            output_val = output_val or ""

            return output_val.strip(), errors_val

        except Exception:
            # Biarkan pytest menangani unexpected exceptions
            raise

    return _run

@pytest.fixture
async def run_morph_program_async():
    """
    Fixture async untuk menjalankan interpreter dan mengembalikan stdout dan daftar kesalahan.
    Dirancang untuk digunakan dengan tes @pytest.mark.asyncio.
    """
    from transisi.Morph import Morph
    morph_instance = Morph()

    async def _run_async(source_code, filename="<tes_async>", external_objects=None):
        try:
            output_val, errors_val = await morph_instance._jalankan_async(
                source_code, filename, ffi_objects=external_objects
            )
            output_val = output_val or ""
            return output_val.strip(), errors_val
        except Exception:
            raise

    return _run_async

@pytest.fixture
def capture_output(run_morph_program):
    """
    Fixture yang disederhanakan untuk menangkap output.
    Sekarang menggunakan `run_morph_program` untuk konsistensi.
    """
    def _capture(source_code):
        output, errors = run_morph_program(source_code)

        if errors:
            # Gabungkan semua pesan error menjadi satu string
            return "\\n".join(errors)

        return output

    return _capture

@pytest.fixture
def capture_output_from_file(capture_output):
    """Fixture untuk membaca file dan menangkap output dari eksekusinya."""
    def _capture_from_file(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            return capture_output(source_code)
        except FileNotFoundError:
            pytest.fail(f"File tes tidak ditemukan di: {file_path}")

    return _capture_from_file


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
