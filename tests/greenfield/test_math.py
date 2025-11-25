import pytest
import os
import sys
import importlib
from ivm.core import opcodes
from ivm import compiler
from ivm.vms import standard_vm

# Force reload to ensure Op enums are consistent
importlib.reload(opcodes)
importlib.reload(compiler)
importlib.reload(standard_vm)

from ivm.vms.standard_vm import StandardVM

TEST_FILE_PATH = "greenfield/cotc/matematika/tes_matematika.fox"

def test_cotc_math():
    assert os.path.exists(TEST_FILE_PATH), f"File tes tidak ditemukan: {TEST_FILE_PATH}"
    vm = StandardVM()

    try:
        vm.load_module(TEST_FILE_PATH)
    except Exception as e:
        pytest.fail(f"VM Gagal menjalankan tes matematika: {e}")
