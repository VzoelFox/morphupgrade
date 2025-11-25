import pytest
import os
from ivm.vms.standard_vm import StandardVM

TEST_FILE_PATH = "greenfield/cotc/logika/tes_logika.fox"

def test_cotc_logic():
    assert os.path.exists(TEST_FILE_PATH), f"File tes tidak ditemukan: {TEST_FILE_PATH}"
    vm = StandardVM()

    try:
        vm.load_module(TEST_FILE_PATH)
    except Exception as e:
        pytest.fail(f"VM Gagal menjalankan tes logika: {e}")
