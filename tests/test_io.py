# tests/test_io.py
import pytest
import os
from ivm.vm import VirtualMachine
from ivm.kesalahan import KesalahanIOVM
from .test_ivm import run_test_case

# Setup Fixtures
@pytest.fixture(scope="module")
def fixture_dir():
    dir_path = "tests/io_fixtures"
    os.makedirs(dir_path, exist_ok=True)

    # Buat file untuk dibaca
    with open(os.path.join(dir_path, "baca.txt"), "w") as f:
        f.write("konten file baca")

    # File untuk ditimpa
    write_path = os.path.join(dir_path, "tulis.txt")
    if os.path.exists(write_path):
        os.remove(write_path)

    # File untuk ditambahkan
    append_path = os.path.join(dir_path, "tambah.txt")
    with open(append_path, "w") as f:
        f.write("baris pertama\n")

    yield dir_path

    # Teardown (opsional, bisa dikomentari untuk inspeksi)
    # import shutil
    # shutil.rmtree(dir_path)

def test_baca_file_berhasil(capsys, fixture_dir):
    path = os.path.join(fixture_dir, "baca.txt").replace("\\", "/")
    kode = f'tulis(baca_file("{path}"));'
    run_test_case(capsys, kode, "konten file baca")

def test_baca_file_tidak_ditemukan(fixture_dir):
    path = os.path.join(fixture_dir, "tidak_ada.txt").replace("\\", "/")
    kode = f'baca_file("{path}");'
    with pytest.raises(KesalahanIOVM) as excinfo:
        run_test_case(None, kode, "")
    assert "File tidak ditemukan" in str(excinfo.value)

def test_tulis_file_baru(fixture_dir):
    path = os.path.join(fixture_dir, "tulis.txt").replace("\\", "/")
    kode = f'tulis_file("{path}", "halo dunia");'
    run_test_case(None, kode, "")

    with open(path, "r") as f:
        content = f.read()
    assert content == "halo dunia"

def test_tulis_file_tambahkan(fixture_dir):
    path = os.path.join(fixture_dir, "tambah.txt").replace("\\", "/")
    kode = f'tulis_file("{path}", "baris kedua");'
    run_test_case(None, kode, "")

    with open(path, "r") as f:
        content = f.read()
    assert content == "baris pertama\nbaris kedua"
