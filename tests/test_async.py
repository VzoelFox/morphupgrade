# tests/test_async.py
import pytest

def test_tidur_works_with_tunggu(capture_output):
    """
    Memverifikasi bahwa 'tidur' berfungsi dengan benar ketika digunakan
    dengan kata kunci 'tunggu' di dalam fungsi asinkron.
    """
    code = """
    asink fungsi utama() maka
        tulis("mulai")
        tunggu tidur(0.01)
        tulis("selesai")
    akhir
    tunggu utama()
    """
    output = capture_output(code)
    # Fungsi tulis menambahkan kutip, dan tidak ada spasi di antara panggilan
    assert output == '"mulai""selesai"'

def test_tidur_without_tunggu_returns_awaitable(capture_output):
    """
    Memverifikasi bahwa memanggil 'tidur' tanpa 'tunggu' mengembalikan
    sebuah objek awaitable (coroutine) dan bukan nil.
    """
    code = """
    biar hasil = tidur(0.01)
    // Objek coroutine dari Python akan direpresentasikan sebagai string
    // yang tidak kosong, bukan "nil".
    tulis(hasil != nil)
    """
    output = capture_output(code)
    assert output == 'benar'

def test_calling_tunggu_on_non_awaitable_fails(capture_output):
    """
    Memverifikasi bahwa 'tunggu' melempar error jika digunakan pada
    nilai yang bukan awaitable.
    """
    code = """
    asink fungsi utama() maka
        tunggu "ini bukan coroutine"
    akhir
    tunggu utama()
    """
    output = capture_output(code)
    assert "KesalahanTipe" in output
    assert "Ekspresi yang mengikuti 'tunggu' harus bisa ditunggu" in output
