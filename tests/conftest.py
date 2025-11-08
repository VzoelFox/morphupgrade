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
def capture_output():
    """Fixture untuk menangkap stdout/stderr dari interpreter."""
    import sys
    from io import StringIO

    def _capture(source_code):
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        try:
            from transisi.Morph import Morph
            morph = Morph()
            _, errors = morph._jalankan(source_code)

            stdout_val = sys.stdout.getvalue()
            stderr_val = sys.stderr.getvalue()

            # Priority: errors > stderr > stdout
            if errors:
                return "\n".join(errors)
            if stderr_val:
                return stderr_val.strip()
            return stdout_val.strip()

        except Exception as e:
            return f"UNEXPECTED ERROR: {str(e)}"
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    return _capture


@pytest.fixture
def run_morph_program():
    """Fixture untuk menjalankan interpreter dan mengembalikan stdout dan daftar kesalahan mentah."""
    def _run(source_code):
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        stdout_val = ""
        errors_val = []

        try:
            from transisi.Morph import Morph
            morph = Morph()
            _, errors_val = morph._jalankan(source_code)
            stdout_val = sys.stdout.getvalue().strip()
        except Exception:
            # Biarkan pytest menangani unexpected exceptions
            raise
        finally:
            sys.stdout = old_stdout

        return stdout_val, errors_val

    return _run


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
