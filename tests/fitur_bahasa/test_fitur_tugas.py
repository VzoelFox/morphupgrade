# tests/fitur_bahasa/test_fitur_tugas.py

import pytest

@pytest.mark.asyncio
async def test_definisi_dan_panggilan_tugas_sederhana(run_morph_program_async):
    """
    Menguji apakah 'tugas' dapat didefinisikan, dipanggil, dan ditunggu
    menggunakan mode eksekusi paling sederhana (sfox).
    """
    kode = """
    tugas sfox hitung_cepat(a, b) maka
        kembalikan a + b
    akhir

    biar hasil_future = hitung_cepat(10, 5)
    biar hasil_akhir = tunggu hasil_future

    tulis(hasil_akhir)
    """
    # Menjalankan kode dan menangkap output.
    stdout, daftar_kesalahan = await run_morph_program_async(kode)

    # Memastikan tidak ada error runtime
    assert not daftar_kesalahan, f"Ditemukan kesalahan saat eksekusi: {daftar_kesalahan}"

    # Memverifikasi output
    # `tulis` akan mencetak "15" jika a+b berhasil.
    assert stdout.strip() == "15", f"Output yang diharapkan adalah '15', tetapi mendapat '{stdout.strip()}'"

@pytest.mark.asyncio
async def test_tugas_menggunakan_variabel_dari_lingkup_luar(run_morph_program_async):
    """
    Memastikan bahwa tugas (yang dieksekusi via FoxEngine) dapat
    mengakses variabel dari lingkup penutupnya (closure).
    """
    kode = """
    biar pengali = 10
    tugas tfox kali_nilai(x) maka
        kembalikan x * pengali
    akhir

    biar future = kali_nilai(5)
    biar hasil = tunggu future

    tulis(hasil)
    """
    stdout, daftar_kesalahan = await run_morph_program_async(kode)

    assert not daftar_kesalahan, f"Ditemukan kesalahan saat eksekusi: {daftar_kesalahan}"
    assert stdout.strip() == "50", f"Output yang diharapkan adalah '50', tetapi mendapat '{stdout.strip()}'"

@pytest.mark.asyncio
async def test_mode_tugas_tidak_valid(run_morph_program_async):
    """
    Menguji bahwa interpreter akan melempar kesalahan jika mode
    eksekusi yang diberikan ke 'tugas' tidak dikenal.
    """
    kode = """
    tugas jetpack_terbang_tinggi_sekali hitung(a) maka
        kembalikan a
    akhir
    """
    # Diharapkan ada kesalahan runtime
    stdout, daftar_kesalahan = await run_morph_program_async(kode)

    assert daftar_kesalahan, "Diharapkan ada kesalahan runtime, tetapi tidak ada."

    # Periksa pesan kesalahan spesifik
    kesalahan = daftar_kesalahan[0]
    assert "Mode eksekusi 'jetpack_terbang_tinggi_sekali' tidak dikenal" in kesalahan, \
        f"Pesan kesalahan tidak sesuai, mendapat: '{kesalahan}'"

@pytest.mark.asyncio
async def test_tugas_dengan_opsi_valid(run_morph_program_async):
    """
    Menguji sintaks `dengan {opsi}` pada deklarasi 'tugas'
    untuk memastikan opsi seperti prioritas dan batas_waktu
    dapat diproses dengan benar.
    """
    kode = """
    tugas sfox kalkulasi_opsional(a, b) dengan {"prioritas": 5, "batas_waktu": 5.0} maka
        kembalikan a * b
    akhir

    biar future = kalkulasi_opsional(7, 6)
    biar hasil = tunggu future

    tulis(hasil)
    """
    stdout, daftar_kesalahan = await run_morph_program_async(kode)

    assert not daftar_kesalahan, f"Ditemukan kesalahan saat eksekusi: {daftar_kesalahan}"
    assert stdout.strip() == "42", f"Output yang diharapkan adalah '42', tetapi mendapat '{stdout.strip()}'"

@pytest.mark.asyncio
async def test_tugas_dengan_opsi_tidak_valid(run_morph_program_async):
    """
    Menguji bahwa interpreter akan melempar KesalahanKunci jika
    opsi yang tidak valid diberikan dalam klausa `dengan`.
    """
    kode = """
    tugas sfox tugas_gagal(a) dengan {"nama_opsi_salah": 123} maka
        kembalikan a
    akhir

    biar future = tugas_gagal(1)
    tunggu future
    """
    stdout, daftar_kesalahan = await run_morph_program_async(kode)

    assert daftar_kesalahan, "Diharapkan ada kesalahan runtime, tetapi tidak ada."

    kesalahan = daftar_kesalahan[0]
    assert "Opsi tugas tidak valid: 'nama_opsi_salah'" in kesalahan, \
        f"Pesan kesalahan tidak sesuai, mendapat: '{kesalahan}'"
