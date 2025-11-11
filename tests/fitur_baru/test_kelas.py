# tests/fitur_baru/test_kelas.py

import pytest
from transisi.Morph import Morph

def test_deklarasi_dan_instansiasi_kelas_sederhana(run_morph_program):
    kode = """
    kelas Kue maka
        fungsi inisiasi() maka
            ini.jenis = "Bolu"
        akhir
    akhir
    biar kue_ku = Kue()
    tulis(kue_ku.jenis)
    """
    hasil, error = run_morph_program(kode)
    assert not error
    assert hasil == '"Bolu"'

def test_properti_di_inisiasi(run_morph_program):
    kode = """
    kelas Kue maka
        fungsi inisiasi(rasa) maka
            ini.rasa = rasa
        akhir
    akhir
    biar kue_coklat = Kue("Coklat")
    tulis(kue_coklat.rasa)
    """
    hasil, error = run_morph_program(kode)
    assert not error
    assert hasil == '"Coklat"'

def test_panggil_metode_kelas(run_morph_program):
    kode = """
    kelas Kalkulator maka
        fungsi tambah(a, b) maka
            kembali a + b
        akhir
    akhir
    biar calc = Kalkulator()
    biar hasil = calc.tambah(5, 3)
    tulis(hasil)
    """
    hasil, error = run_morph_program(kode)
    assert not error
    assert hasil == '8'

def test_pewarisan_metode(run_morph_program):
    kode = """
    kelas Hewan maka
        fungsi bersuara() maka
            kembali "Suara hewan..."
        akhir
    akhir
    kelas Kucing warisi Hewan maka
    akhir
    biar meong = Kucing()
    tulis(meong.bersuara())
    """
    hasil, error = run_morph_program(kode)
    assert not error
    assert hasil == '"Suara hewan..."'

def test_panggil_induk_di_inisiasi(run_morph_program):
    kode = """
    kelas Roti maka
        fungsi inisiasi(jenis) maka
            ini.jenis = jenis
        akhir
    akhir
    kelas RotiTawar warisi Roti maka
        fungsi inisiasi(jenis, warna) maka
            induk.inisiasi(jenis)
            ini.warna = warna
        akhir
    akhir
    biar roti_ku = RotiTawar("Gandum", "Coklat")
    tulis(roti_ku.jenis)
    tulis(roti_ku.warna)
    """
    hasil, error = run_morph_program(kode)
    assert not error
    assert hasil == '"Gandum""Coklat"' # Disesuaikan dengan output tulis yang digabung

def test_override_metode(run_morph_program):
    kode = """
    kelas Hewan maka
        fungsi bersuara() maka
            kembali "Suara hewan..."
        akhir
    akhir
    kelas Anjing warisi Hewan maka
        fungsi bersuara() maka
            kembali "Guk guk!"
        akhir
    akhir
    biar doggo = Anjing()
    tulis(doggo.bersuara())
    """
    hasil, error = run_morph_program(kode)
    assert not error
    assert hasil == '"Guk guk!"'

def test_akses_properti_privat_gagal(run_morph_program):
    kode = """
    kelas RahasiaNegara maka
        fungsi inisiasi() maka
            ini._kode_nuklir = "12345"
        akhir
    akhir
    biar rahasia = RahasiaNegara()
    tulis(rahasia._kode_nuklir)
    """
    hasil, error = run_morph_program(kode)
    assert error
    assert "Properti atau metode '_kode_nuklir' bersifat privat" in error[0]

def test_akses_properti_privat_dari_dalam_sukses(run_morph_program):
    kode = """
    kelas RahasiaNegara maka
        fungsi inisiasi(kode) maka
            ini._kode_rahasia = kode
        akhir
        fungsi bocorkan_rahasia() maka
            kembali ini._kode_rahasia
        akhir
    akhir
    biar rahasia = RahasiaNegara("kucing oranye")
    tulis(rahasia.bocorkan_rahasia())
    """
    hasil, error = run_morph_program(kode)
    assert not error
    assert hasil == '"kucing oranye"'
