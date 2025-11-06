# fox_engine/internal/kunci.py

import threading

class Kunci:
    """
    Implementasi dari 're-entrant lock' (RLock) dari prinsip dasar.
    Ini memungkinkan utas yang sama untuk memperoleh kunci beberapa kali
    tanpa menyebabkan deadlock.
    """
    def __init__(self):
        self._kondisi = threading.Condition()
        self._pemilik = None
        self._jumlah_akuisisi = 0

    def dapatkan(self, blocking: bool = True, timeout: float = -1) -> bool:
        """Memperoleh kunci, memblokir jika perlu."""
        utas_saat_ini = threading.current_thread()
        with self._kondisi:
            # Jika kunci dimiliki oleh utas lain, tunggu hingga dilepaskan.
            if self._pemilik is not None and self._pemilik != utas_saat_ini:
                if not blocking:
                    return False

                # Tunggu dengan timeout jika ditentukan
                if timeout > 0:
                    if not self._kondisi.wait(timeout):
                        return False
                else: # timeout < 0
                    self._kondisi.wait()

            # Sekarang kunci bebas atau sudah dimiliki oleh kita.
            self._pemilik = utas_saat_ini
            self._jumlah_akuisisi += 1
            return True

    def lepaskan(self):
        """Melepaskan kunci."""
        utas_saat_ini = threading.current_thread()
        with self._kondisi:
            if self._pemilik != utas_saat_ini:
                raise RuntimeError("Tidak dapat melepaskan kunci yang tidak dimiliki.")

            self._jumlah_akuisisi -= 1
            if self._jumlah_akuisisi == 0:
                self._pemilik = None
                # Beri tahu satu utas yang menunggu (jika ada) bahwa kunci bebas.
                self._kondisi.notify()

    def __enter__(self):
        """Memasuki context manager, memperoleh kunci."""
        self.dapatkan()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Keluar dari context manager, melepaskan kunci."""
        self.lepaskan()

    # Properti untuk debugging atau pemeriksaan status (opsional)
    @property
    def terkunci(self) -> bool:
        """Memeriksa apakah kunci saat ini dipegang oleh suatu utas."""
        return self._pemilik is not None
