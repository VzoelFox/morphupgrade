# tests/fixtures/_test_internal.py

GLOBAL_STATE = {}

def get_global(key, default=None):
    """Mengambil nilai dari state global."""
    return GLOBAL_STATE.get(key, default)

def set_global(key, value):
    """Mengatur nilai di state global."""
    GLOBAL_STATE[key] = value
    return value

def reset_globals():
    """Membersihkan state global untuk pengujian."""
    GLOBAL_STATE.clear()
