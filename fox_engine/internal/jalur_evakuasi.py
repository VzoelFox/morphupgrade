# fox_engine/internal/jalur_evakuasi.py

import threading
from queue import Queue
from .hasil_masa_depan import HasilMasaDepan

class JalurEvakuasi(threading.Thread):
    """
    Sebuah utas pekerja yang mengambil tugas dari antrean, mengeksekusinya,
    dan menyimpan hasilnya di objek HasilMasaDepan.
    """
    def __init__(self, antrean_tugas: Queue, nama: str):
        super().__init__(name=nama, daemon=True)
        self._antrean_tugas = antrean_tugas
        self._sedang_berhenti = False

    def run(self):
        """
        Metode utama dari utas. Terus mengambil dan menjalankan tugas
        sampai item sentinel (None) diterima.
        """
        while not self._sedang_berhenti:
            try:
                # Ambil tugas dari antrean, blokir hingga ada tugas
                tugas, masa_depan = self._antrean_tugas.get()

                # Cek item sentinel untuk berhenti
                if tugas is None:
                    self._sedang_berhenti = True
                    continue

                # Jalankan tugas dan tangani hasilnya
                try:
                    hasil = tugas()
                    masa_depan.atur_hasil(hasil)
                except Exception as e:
                    masa_depan.atur_pengecualian(e)
            except Exception:
                # Menangani kemungkinan kesalahan saat mengambil dari antrean
                # atau jika ada masalah tak terduga lainnya.
                # Dalam kondisi normal, ini seharusnya tidak terjadi.
                pass
            finally:
                # Pastikan tugas ditandai sebagai selesai, bahkan jika ada kesalahan
                if 'tugas' in locals() and tugas is not None:
                    self._antrean_tugas.task_done()

    def berhenti(self):
        """Memberi sinyal agar utas ini berhenti setelah tugas saat ini selesai."""
        self._sedang_berhenti = True
        # Menambahkan sentinel ke antrean untuk memastikan utas bangun dan keluar
        self._antrean_tugas.put((None, None))
