# ivm/kesalahan.py

class KesalahanRuntimeVM(Exception):
    """Kelas dasar untuk semua error runtime di VM."""
    def __init__(self, pesan: str):
        self.pesan = pesan
        super().__init__(pesan)

class KesalahanTipeVM(KesalahanRuntimeVM):
    """Dilemparkan saat operasi menerima tipe yang salah."""
    pass

class KesalahanIndeksVM(KesalahanRuntimeVM):
    """Dilemparkan saat indeks di luar jangkauan."""
    pass

class KesalahanKunciVM(KesalahanRuntimeVM):
    """Dilemparkan saat kunci kamus tidak ditemukan."""
    pass

class KesalahanNamaVM(KesalahanRuntimeVM):
    """Dilemparkan saat nama (variabel/fungsi) tidak ditemukan."""
    pass

class KesalahanPembagianNolVM(KesalahanRuntimeVM):
    """Dilemparkan saat terjadi pembagian dengan nol."""
    pass

class KesalahanJodoh(KesalahanRuntimeVM):
    """Dilemparkan saat tidak ada pola `jodohkan` yang cocok."""
    pass
