import pytest
import os
from ivm.vms.standard_vm import StandardVM

# Lokasi file tes
TEST_FILE_PATH = "greenfield/cotc/io/tes_berkas.fox"

def test_cotc_io_berkas():
    # Pastikan file tes ada
    assert os.path.exists(TEST_FILE_PATH), f"File tes tidak ditemukan: {TEST_FILE_PATH}"

    # Setup VM
    vm = StandardVM()

    # Jalankan modul tes
    try:
        vm.load_module(TEST_FILE_PATH)
    except Exception as e:
        pytest.fail(f"VM Gagal menjalankan tes_berkas.fox: {e}")

    # Verifikasi cleanup (opsional, script harusnya sudah clean up)
    # Jika script gagal di tengah, folder mungkin tersisa.
    if os.path.exists("folder_sementara_tes"):
        import shutil
        shutil.rmtree("folder_sementara_tes")
