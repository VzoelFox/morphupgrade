# tests/test_ffi.py
import pytest

def test_ffi_load_module_and_access_variable(capture_output):
    """Menguji 'pinjam' untuk memuat modul Python dan mengakses variabelnya."""
    program = """
    pinjam "tests/fixtures/pustaka_pinjaman.py" sebagai Pustaka
    tulis(Pustaka.NAMA_PUSTAKA)
    """
    output = capture_output(program)
    assert output == "Pustaka Uji Coba Pinjaman"

def test_ffi_call_simple_function(capture_output):
    """Menguji pemanggilan fungsi Python sederhana dengan konversi tipe dasar."""
    program = """
    pinjam "tests/fixtures/pustaka_pinjaman.py" sebagai Pustaka
    biar hasil = Pustaka.tambah(15, 10)
    tulis(hasil)
    """
    output = capture_output(program)
    assert output == "25"

def test_ffi_complex_type_conversion(capture_output):
    """Menguji konversi tipe data array/kamus bolak-balik."""
    program = """
    pinjam "tests/fixtures/pustaka_pinjaman.py" sebagai Pustaka
    biar list_hasil = Pustaka.gabung_list([1, 2], [3, 4])
    tulis(list_hasil[3]) # Harusnya 4

    biar kamus_hasil = Pustaka.buat_kamus("kunci", "nilai")
    tulis(kamus_hasil["kunci"])
    """
    output = capture_output(program)
    assert output.strip() == "4\nnilai"

def test_ffi_unsupported_return_type_is_wrapped(capture_output):
    """Menguji bahwa tipe data Python yang tidak dikenal dibungkus menjadi ObjekPinjaman."""
    program = """
    pinjam "tests/fixtures/pustaka_pinjaman.py" sebagai Pustaka
    biar hasil_tuple = Pustaka.dapatkan_tuple()

    # Coba akses elemen dari objek pinjaman (tuple)
    tulis(hasil_tuple[1])
    """
    output = capture_output(program)
    assert output == "dua puluh"

def test_ffi_python_exception_handling(capture_output):
    """Memastikan pengecualian dari Python ditangkap dan dilaporkan sebagai KesalahanRuntime."""
    program = """
    pinjam "tests/fixtures/pustaka_pinjaman.py" sebagai Pustaka
    Pustaka.gagal_dengan_pesan()
    """
    output = capture_output(program)
    assert "Kesalahan saat menjalankan fungsi pinjaman" in output
    assert "Ini adalah pesan kesalahan dari Python." in output

def test_ffi_class_instantiation_and_method_call(capture_output):
    """Menguji instansiasi kelas Python dan pemanggilan metodenya."""
    program = """
    pinjam "tests/fixtures/pustaka_pinjaman.py" sebagai Pustaka
    biar kalkulator = Pustaka.Kalkulator(10)

    kalkulator.tambahkan(5)
    biar total = kalkulator.dapatkan_total()
    tulis(total)
    """
    output = capture_output(program)
    assert output == "15"

def test_ffi_write_assignment(capture_output):
    """Menguji assignment (penulisan) kembali ke objek Python."""
    program = """
    pinjam "tests/fixtures/pustaka_pinjaman.py" sebagai Pustaka
    biar kalkulator = Pustaka.Kalkulator(0)

    kalkulator.total = 100
    tulis(kalkulator.dapatkan_total())

    biar data = {"list": [10, 20]}
    kalkulator.data = data
    kalkulator.data["list"][1] = 99
    tulis(kalkulator.data["list"][1])
    """
    output = capture_output(program)
    assert output.strip() == "100\n99"

def test_ffi_nested_data_conversion(capture_output):
    """Menguji konversi tipe data bersarang secara bolak-balik."""
    program = """
    pinjam "tests/fixtures/pustaka_pinjaman.py" sebagai Pustaka
    biar data_morph = {"nama": "Vzoel", "nilai": [10, 30]}
    biar hasil = Pustaka.proses_data_bersarang(data_morph)

    # Hasilnya adalah list dari tuple, yang menjadi list dari ObjekPinjaman
    tulis(hasil[0][0]) # akses nested: list -> ObjekPinjaman -> elemen tuple
    tulis(hasil[1][1][0])
    """
    output = capture_output(program)
    assert output.strip() == "sukses\n100"

def test_ffi_better_object_representation(capture_output):
    """Menguji bahwa 'tulis' pada ObjekPinjaman memberikan output yang informatif."""
    program = """
    pinjam "tests/fixtures/pustaka_pinjaman.py" sebagai Pustaka
    biar kalkulator = Pustaka.Kalkulator(5)
    tulis(kalkulator)
    """
    output = capture_output(program)
    assert "objek pinjaman" in output
    assert "Kalkulator object" in output # Berdasarkan repr default dari objek kelas Python
