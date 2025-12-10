# tests/fitur_baru/test_ffi_intensif.py
import pytest

@pytest.mark.asyncio
async def test_ffi_konversi_list_bersarang_dan_return(run_morph_program_async):
    """
    Menguji kemampuan FFI untuk menerima list bersarang dari Morph,
    memprosesnya di Python, dan mengembalikan hasilnya ke Morph.
    """
    program = """
    pinjam aot "tests.fixtures.ffi_test_module" sebagai ffi_modul

    fungsi uji_list_bersarang() {
        biar data_bersarang = [[1, 2], [3], [4, 5, 6]]
        biar hasil_rata = ffi_modul.proses_list_bersarang(data_bersarang)

        // Verifikasi tipe dan isi dari hasil
        tulis(hasil_rata)
    }

    uji_list_bersarang()
    """
    output, errors = await run_morph_program_async(program)
    assert not errors, f"Terjadi error: {errors}"

    # Harusnya outputnya adalah list yang sudah diratakan
    expected_output = "[1, 2, 3, 4, 5, 6]"
    assert expected_output in output, f"Output '{output}' tidak sesuai dengan yang diharapkan '{expected_output}'"

@pytest.mark.asyncio
async def test_ffi_modifikasi_kamus_dan_return(run_morph_program_async):
    """
    Menguji kemampuan FFI untuk menerima dictionary dari Morph,
    memodifikasinya di Python, dan mengembalikan objek yang sudah diubah.
    """
    program = """
    pinjam aot "tests.fixtures.ffi_test_module" sebagai ffi_modul

    fungsi uji_kamus() {
        biar data_kamus = {"nama": "Morph", "versi": 2.0}
        biar kamus_diubah = ffi_modul.modifikasi_kamus(data_kamus)

        tulis(kamus_diubah["nama"])
        tulis(kamus_diubah["versi"])
        tulis(kamus_diubah["status_py"])
    }

    uji_kamus()
    """
    output, errors = await run_morph_program_async(program)
    assert not errors, f"Terjadi error: {errors}"

    assert "Morph" in output
    assert "2.0" in output
    assert "diproses" in output, "Kunci 'status_py' yang ditambahkan dari Python tidak ditemukan"

@pytest.mark.asyncio
async def test_ffi_menangkap_error_dari_python(run_morph_program_async):
    """
    Menguji bahwa exception yang terjadi di dalam fungsi FFI Python
    ditangkap dengan benar dan dilaporkan sebagai error runtime di Morph.
    """
    program = """
    pinjam aot "tests.fixtures.ffi_test_module" sebagai ffi_modul

    fungsi uji_penanganan_error() {
        ffi_modul.picu_error()
    }

    uji_penanganan_error()
    """
    output, errors = await run_morph_program_async(program)

    assert errors, "Seharusnya terjadi error, tetapi tidak ada yang dilaporkan"

    # Verifikasi bahwa pesan error dari Python (ValueError) muncul dalam laporan error Morph
    expected_error_message = "Ini adalah kesalahan yang disengaja dari FFI"
    assert expected_error_message in errors, f"Pesan error '{errors}' tidak mengandung detail dari exception Python"

@pytest.mark.asyncio
async def test_ffi_pola_fungsional_reassignment(run_morph_program_async):
    """
    Menguji pola di mana fungsi FFI mengembalikan koleksi baru,
    dan kode Morph harus melakukan reassignment untuk mendapatkan pembaruan.
    """
    program = """
    pinjam aot "tests.fixtures.ffi_test_module" sebagai ffi_modul

    fungsi uji_reassignment() {
        biar data_awal = ["apel", "pisang"]

        // Panggil FFI yang mengembalikan list baru
        ubah data_awal = ffi_modul.tambah_item_ke_daftar(data_awal, "ceri")

        tulis(data_awal)
    }

    uji_reassignment()
    """
    output, errors = await run_morph_program_async(program)
    assert not errors, f"Terjadi error: {errors}"

    expected_output = "['apel', 'pisang', 'ceri']"
    assert expected_output in output, f"Output '{output}' tidak sesuai dengan yang diharapkan '{expected_output}'"
