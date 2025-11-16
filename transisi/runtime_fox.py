# transisi/runtime_fox.py
from fox_engine.api import sfox, wfox, mfox_baca_file, dapatkan_manajer_fox, tfox
from .translator import Penerjemah, Fungsi
from . import absolute_sntx_morph as ast
from .morph_t import TipeToken, Token
from typing import Any
import asyncio

class RuntimeMORPHFox:
    """
    Mengelola eksekusi kode MORPH, menggabungkan interpretasi
    dengan kompilasi Just-In-Time (JIT) menggunakan Fox Engine.
    """
    JIT_THRESHOLD = 10 # Panggil sebuah fungsi 10 kali untuk memicu kompilasi JIT

    def __init__(self, interpreter: Penerjemah):
        self.interpreter = interpreter
        self.manajer = dapatkan_manajer_fox()

        # Cache untuk menyimpan bytecode yang sudah dikompilasi
        self.compiler_cache: dict[str, Any] = {}
        # Lacak "hot functions"
        self.call_counts: dict[str, int] = {}
        # Lacak fungsi yang sedang dikompilasi untuk menghindari kompilasi ganda
        self.compilation_in_progress: set[str] = set()

    async def compile_morph_function(self, fungsi: Fungsi):
        """
        Memicu kompilasi fungsi di latar belakang menggunakan ThunderFox (tfox).
        Ini adalah placeholder, hanya menghasilkan bytecode dummy.
        """
        nama_fungsi = fungsi.deklarasi.nama.nilai
        if nama_fungsi in self.compilation_in_progress:
            return

        self.compilation_in_progress.add(nama_fungsi)

        async def _compile_task():
            # Placeholder: proses kompilasi yang berat
            await asyncio.sleep(0.1)  # Simulasi kerja
            return f"morphc_bytecode_untuk_{nama_fungsi}"

        try:
            # Gunakan tfox untuk tugas berat (CPU-bound)
            bytecode = await tfox(f"compile_{nama_fungsi}", _compile_task)
            self.compiler_cache[nama_fungsi] = bytecode
            print(f"INFO: Fungsi '{nama_fungsi}' berhasil dikompilasi di latar belakang.")
        except Exception as e:
            print(f"ERROR: Kompilasi untuk '{nama_fungsi}' gagal: {e}")
        finally:
            self.compilation_in_progress.remove(nama_fungsi)

    async def execute_function(self, fungsi: Fungsi, args: list):
        """Merutekan eksekusi ke jalur terkompilasi (jika ada) atau terinterpretasi."""
        nama_fungsi = fungsi.deklarasi.nama.nilai

        if nama_fungsi in self.compiler_cache:
            return await self._execute_compiled(fungsi, args)

        return await self._execute_interpreted(fungsi, args)

    async def _execute_interpreted(self, fungsi: Fungsi, args: list):
        """Menjalankan fungsi melalui interpreter dan melacak 'hotness' untuk JIT."""
        nama_fungsi = fungsi.deklarasi.nama.nilai

        # Lacak panggilan
        self.call_counts[nama_fungsi] = self.call_counts.get(nama_fungsi, 0) + 1

        # Periksa apakah sudah waktunya JIT
        if self.call_counts[nama_fungsi] >= self.JIT_THRESHOLD:
            # Memicu kompilasi di latar belakang tanpa menunggu hasilnya
            asyncio.create_task(self.compile_morph_function(fungsi))

        # Eksekusi seperti biasa
        async def _run_via_interpreter():
            coro = fungsi.panggil(self.interpreter, args, fungsi.deklarasi.nama)
            return await coro

        if self._is_lightweight_function(fungsi):
            return await sfox(f"interp_{nama_fungsi}", _run_via_interpreter)
        else:
            return await wfox(f"interp_{nama_fungsi}", _run_via_interpreter)

    async def _execute_compiled(self, fungsi: Fungsi, args: list):
        """Menjalankan fungsi yang sudah dikompilasi menggunakan WaterFox (wfox)."""
        nama_fungsi = fungsi.deklarasi.nama.nilai
        bytecode = self.compiler_cache[nama_fungsi]

        async def _exec_task():
            # Placeholder: eksekusi bytecode
            print(f"INFO: Menjalankan bytecode '{bytecode}' untuk fungsi '{nama_fungsi}'.")
            await asyncio.sleep(0.01) # Simulasi eksekusi cepat
            return "hasil_dari_eksekusi_terkompilasi"

        # Gunakan wfox untuk eksekusi seimbang
        return await wfox(f"exec_{nama_fungsi}", _exec_task)

    async def load_module(self, path: str):
        """Route module loading ke MiniFox untuk I/O optimization"""

        # Gunakan MiniFox untuk baca file
        source = await mfox_baca_file(
            nama=f"load_module_{path}",
            path=path
        )

        # NOTE: source is bytes, need to decode
        source_str = source.decode('utf-8')

        # Parse & execute dengan interpreter existing
        return await self.interpreter._jalankan_modul_dari_sumber(path, source_str)

    def _is_lightweight_function(self, fungsi: Fungsi) -> bool:
        """Heuristik sederhana untuk routing decision"""
        # Fungsi dengan < 10 statements → lightweight
        if hasattr(fungsi.deklarasi, 'badan') and hasattr(fungsi.deklarasi.badan, 'daftar_pernyataan'):
            body_size = len(fungsi.deklarasi.badan.daftar_pernyataan)
            return body_size < 10
        return False
