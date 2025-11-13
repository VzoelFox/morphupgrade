import pytest

# Daftar kasus uji komprehensif untuk `jodohkan`
# Setiap tuple berisi: (nama_tes, input_kode, output_yang_diharapkan)
TEST_CASES = [
    (
        "pola_literal",
        """
        fungsi cek(nilai) maka
            jodohkan nilai dengan
                | 10 maka
                    tulis("Sepuluh")
                | "halo" maka
                    tulis("Teks Halo")
                | benar maka
                    tulis("Boolean Benar")
            akhir
        akhir
        cek(10)
        cek("halo")
        cek(benar)
        """,
        '"Sepuluh""Teks Halo""Boolean Benar"'
    ),
    (
        "pola_wildcard_dan_ikatan_variabel",
        """
        fungsi proses(data) maka
            jodohkan data dengan
                | 99 maka
                    tulis("Sembilan Puluh Sembilan")
                | _ maka
                    tulis("Apa pun selain 99")
            akhir
        akhir
        proses(99)
        proses("tes")
        """,
        '"Sembilan Puluh Sembilan""Apa pun selain 99"'
    ),
    (
        "pola_ikatan_variabel_menangkap_nilai",
        """
        fungsi tangkap(nilai) maka
            jodohkan nilai dengan
                | x maka
                    tulis("Menangkap nilai:", x)
            akhir
        akhir
        tangkap(123)
        tangkap("abc")
        """,
        '"Menangkap nilai:" 123"Menangkap nilai:" "abc"'
    ),
    (
        "pola_varian_sederhana_dan_dengan_ikatan",
        """
        tipe Hasil = Sukses(data) | Gagal | Kosong
        fungsi cek_hasil(hasil) maka
            jodohkan hasil dengan
                | Sukses(pesan) maka
                    tulis("Berhasil:", pesan)
                | Gagal maka
                    tulis("Gagal Total")
                | Kosong maka
                    tulis("Tidak ada data")
            akhir
        akhir
        cek_hasil(Sukses("data penting"))
        cek_hasil(Gagal)
        cek_hasil(Kosong)
        """,
        '"Berhasil:" "data penting"'
    ),
    (
        "pola_varian_dengan_banyak_ikatan",
        """
        tipe Respon = Data(kode, pesan) | Eror(kode)
        fungsi proses_respon(r) maka
            jodohkan r dengan
                | Data(kode, d) maka
                    tulis("OK:", d)
                | Eror(kode_error) maka
                    tulis("Eror:", kode_error)
            akhir
        akhir
        proses_respon(Data(200, "konten"))
        proses_respon(Eror(500))
        """,
        '"OK:" "konten""Eror:" 500'
    ),
    (
        "pola_daftar_kosong_dan_satu_elemen",
        """
        fungsi cek_daftar(d) maka
            jodohkan d dengan
                | [] maka
                    tulis("Kosong")
                | [x] maka
                    tulis("Satu elemen:", x)
            akhir
        akhir
        cek_daftar([])
        cek_daftar([99])
        """,
        '"Kosong""Satu elemen:" 99'
    ),
    (
        "pola_daftar_destructuring_kompleks",
        """
        fungsi proses_perintah(cmd) maka
            jodohkan cmd dengan
                | ["tambah", a, b] maka
                    tulis(a + b)
                | ["ubah", id, _, nilai_baru] maka
                    tulis("Ubah", id, "menjadi", nilai_baru)
                | ["hapus", id] maka
                    tulis("Hapus", id)
                | _ maka
                    tulis("Perintah tidak valid")
            akhir
        akhir
        proses_perintah(["tambah", 10, 20])
        proses_perintah(["ubah", 123, "abaikan", "nilaiX"])
        proses_perintah(["hapus", 456])
        proses_perintah("bukan perintah")
        """,
        '30"Ubah" 123 "menjadi" "nilaiX""Hapus" 456"Perintah tidak valid"'
    ),
]

@pytest.mark.parametrize("nama,kode,output_diharapkan", TEST_CASES)
def test_jodohkan_integration(run_morph_program, nama, kode, output_diharapkan):
    """
    Menjalankan tes integrasi untuk berbagai skenario `jodohkan`.
    """
    output, errors = run_morph_program(kode)

    assert not errors, f"Tes '{nama}' gagal dengan error: {errors}"

    # Normalisasi output untuk perbandingan yang konsisten
    cleaned_output = output.strip().replace('\n', '')
    assert cleaned_output == output_diharapkan, f"Output untuk tes '{nama}' tidak sesuai harapan."
