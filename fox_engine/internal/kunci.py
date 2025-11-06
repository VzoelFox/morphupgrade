# fox_engine/internal/kunci.py

import threading

class Kunci:
    """
    Sebuah implementasi dari mutual exclusion lock yang re-entrant (dapat dimasuki kembali),
    mirip dengan threading.RLock. Ini memungkinkan jalur evakuasi yang sama untuk
    memperoleh kunci ini beberapa kali tanpa menyebabkan deadlock.

    Gunakan ini dengan pernyataan 'with' untuk memastikan kunci selalu dilepaskan.
    """
    def __init__(self):
        # Menggunakan RLock untuk mendukung re-entrancy, sesuai dengan kebutuhan
        # di PencatatTugas dan PemutusSirkuit.
        self._kunci = threading.RLock()

    def dapatkan(self, blocking: bool = True, timeout: float = -1) -> bool:
        """
        Memperoleh kunci, memblokir atau tidak, hingga kunci tersedia.

        Args:
            blocking: Jika True (default), panggilan akan memblokir hingga kunci
                      dilepaskan. Jika False, panggilan tidak akan memblokir.
            timeout: Jika positif, menentukan waktu maksimum dalam detik untuk
                     menunggu kunci. Jika negatif (default), menunggu tanpa batas.
                     Hanya berlaku jika blocking adalah True.

        Returns:
            True jika kunci berhasil didapatkan, False jika tidak (misalnya timeout).
        """
        return self._kunci.acquire(blocking, timeout)

    def lepaskan(self):
        """
        Melepaskan kunci.

        Ini hanya boleh dipanggil dari jalur evakuasi yang saat ini memegang kunci.
        """
        self._kunci.release()

    def __enter__(self):
        """Memasuki context manager, memperoleh kunci."""
        self.dapatkan()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Keluar dari context manager, melepaskan kunci."""
        self.lepaskan()
