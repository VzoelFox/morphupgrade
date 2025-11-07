# transisi/error_utils.py
# Utilitas Pemformatan Error untuk "Kelahiran Kembali MORPH"

from .morph_t import Token, TipeToken

class FormatterKesalahan:
    """
    Satu tempat buat ngurusin semua format pesan error.
    Biar pesannya konsisten, jelas, dan gaul.
    """

    def __init__(self, sumber_kode: str):
        self.sumber_kode = sumber_kode.splitlines()

    def _dapatkan_konteks_baris(self, baris: int) -> str:
        """Ambil baris kode tempat error terjadi."""
        # baris di sini 1-based, jadi kita perlu -1 untuk akses list
        if 0 < baris <= len(self.sumber_kode):
            return self.sumber_kode[baris - 1].strip()
        return ""

    def format_lexer(self, pesan: str, baris: int, kolom: int) -> str:
        """Format untuk kesalahan yang ditemukan sama Lexer."""
        header = f"Duh, ada typo nih di baris {baris}, kolom {kolom}!"
        konteks = self._dapatkan_konteks_baris(baris)
        pesan_final = f"{header}\n> {konteks}\n! {pesan}"
        return pesan_final

    def format_parser(self, token: Token, pesan: str) -> str:
        """Format untuk kesalahan sintaks yang ditemukan Parser."""
        if token.tipe == TipeToken.ADS:
            lokasi = "di akhir file"
        else:
            lokasi = f"deket token '{token.nilai}'"

        header = f"Hmm, kayaknya ada yang aneh di baris {token.baris}..."
        konteks = self._dapatkan_konteks_baris(token.baris)
        pesan_final = f"{header}\n> {konteks}\n! {pesan} ({lokasi})"
        return pesan_final

    def format_runtime(self, error) -> str:
        """Format untuk kesalahan pas program lagi jalan."""
        token = error.token
        pesan = error.pesan
        header = f"Waduh, programnya crash di baris {token.baris}!"
        konteks = self._dapatkan_konteks_baris(token.baris)
        pesan_final = f"{header}\n> {konteks}\n! {pesan}"
        return pesan_final
