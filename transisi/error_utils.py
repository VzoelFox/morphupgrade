# transisi/error_utils.py
# Utilitas Pemformatan Error untuk "Kelahiran Kembali MORPH"

from .morph_t import Token, TipeToken
from .kesalahan import KesalahanFFI

class FormatterKesalahan:
    """
    Satu tempat buat ngurusin semua format pesan error.
    Biar pesannya konsisten, jelas, dan gaul.
    """

    def __init__(self, sumber_kode: str):
        self.sumber_kode = sumber_kode.splitlines()

    def _dapatkan_konteks_baris(self, baris: int, kolom: int = 0) -> tuple[str, str]:
        """Ambil baris kode dan buat pointer penunjuk kolom."""
        if not (0 < baris <= len(self.sumber_kode)):
            return "", ""

        line = self.sumber_kode[baris - 1]

        # Ganti tab dengan spasi untuk perhitungan visual yang konsisten
        visual_line = line.replace('\t', '    ')
        kolom_visual = kolom

        # Sesuaikan posisi kolom jika ada tab sebelum kolom error
        kolom_asli = 0
        tambahan_spasi = 0
        for char in line:
            kolom_asli += 1
            if kolom_asli >= kolom:
                break
            if char == '\t':
                tambahan_spasi += 3 # 1 tab = 4 spasi, jadi tambah 3

        kolom_visual += tambahan_spasi

        # Hitung spasi di depan untuk alignment pointer yang benar pada baris visual
        leading_spaces = len(visual_line) - len(visual_line.lstrip())
        pointer = ' ' * (kolom_visual - 1 - leading_spaces) + '^'

        return visual_line.strip(), pointer

    def format_lexer(self, kesalahan: dict) -> str:
        """Format untuk kesalahan yang ditemukan sama Lexer."""
        pesan = kesalahan.get("pesan", "Error tidak dikenal")
        baris = kesalahan.get("baris", 0)
        kolom = kesalahan.get("kolom", 0)

        header = f"Duh, ada typo nih di baris {baris}, kolom {kolom}!"
        konteks, pointer = self._dapatkan_konteks_baris(baris, kolom)

        pesan_final = f"{header}\n> {konteks}\n  {pointer}\n! {pesan}"
        return pesan_final

    def format_parser(self, token: Token, pesan: str) -> str:
        """Format untuk kesalahan sintaks yang ditemukan Parser."""
        if token.tipe == TipeToken.ADS:
            lokasi = "di akhir file"
            konteks = self._dapatkan_konteks_baris(len(self.sumber_kode))[0]
            pointer = "" # Tidak ada pointer yang jelas untuk akhir file
        else:
            lokasi = f"deket token '{token.nilai}'"
            konteks, pointer = self._dapatkan_konteks_baris(token.baris, token.kolom)

        header = f"Hmm, kayaknya ada yang aneh di baris {token.baris}..."
        pesan_final = f"{header}\n> {konteks}\n  {pointer}\n! {pesan} ({lokasi})"
        return pesan_final

    def format_runtime(self, error, call_stack: list) -> str:
        """Format untuk kesalahan pas program lagi jalan."""
        token = error.token
        pesan = error.pesan
        nama_error = error.__class__.__name__

        header = f"Waduh, programnya crash di baris {token.baris}!"
        konteks = self._dapatkan_konteks_baris(token.baris)
        pesan_error = f"[{nama_error}] {pesan}"

        # Tambahan untuk FFI Errors
        python_info = ""
        if isinstance(error, KesalahanFFI) and error.python_exception:
            py_exc = error.python_exception
            python_info = f"\\n\\nDetail dari Python:\\n  {type(py_exc).__name__}: {str(py_exc)}"

        stack_trace = "\\nJejak Panggilan (dari yang paling baru):\\n"
        if not call_stack:
            stack_trace += "  (tidak ada dalam fungsi)"
        else:
            for i, frame in enumerate(reversed(call_stack)):
                stack_trace += f"  {i}: {frame}\\n"

        pesan_final = f"{header}\\n> {konteks}\\n! {pesan_error}{python_info}{stack_trace}"
        return pesan_final
