# fox_engine/internal/aliansi_nilai_tetap.py

class _Auto:
    """Objek sentinel untuk nilai otomatis."""
    pass

auto = _Auto()

class MetaAliansi(type):
    """Metaclass untuk AliansiNilaiTetap."""
    def __new__(cls, name, bases, dct):
        definisi_anggota = {k: v for k, v in dct.items() if not k.startswith('_')}
        for k in definisi_anggota:
            del dct[k]

        kelas_baru = super().__new__(cls, name, bases, dct)

        peta_anggota = {}
        urutan_anggota = []
        hitungan_auto = 1

        for nama_anggota, nilai_anggota in definisi_anggota.items():
            if nilai_anggota is auto:
                nilai_final = hitungan_auto
                hitungan_auto += 1
            else:
                # Terima nilai yang ditetapkan secara eksplisit
                nilai_final = nilai_anggota

            anggota = object.__new__(kelas_baru)
            anggota._nama = nama_anggota
            anggota._nilai = nilai_final

            setattr(kelas_baru, nama_anggota, anggota)
            peta_anggota[nama_anggota] = anggota
            urutan_anggota.append(anggota)

        kelas_baru._peta_anggota_ = peta_anggota
        kelas_baru._urutan_anggota_ = urutan_anggota
        return kelas_baru

    def __iter__(cls):
        return iter(cls._urutan_anggota_)

class AliansiNilaiTetap(metaclass=MetaAliansi):
    """Kelas dasar untuk membuat enumerasi nilai-nilai tetap."""
    def __init__(self, *args, **kwargs):
        raise TypeError("Tidak dapat menginstansiasi Aliansi secara langsung.")

    def __repr__(self):
        return f"<{self.__class__.__name__}.{self._nama}>"

    @property
    def name(self):
        return self._nama

    @property
    def value(self):
        return self._nilai
