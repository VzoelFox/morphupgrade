# transisi/runtime_fox.py
from fox_engine.api import sfox, wfox, mfox_baca_file, dapatkan_manajer_fox
from .translator import Penerjemah, Fungsi
from . import absolute_sntx_morph as ast
from .morph_t import TipeToken, Token

class RuntimeMORPHFox:
    """
    Fase 1: Wrapper Fox Engine untuk interpreter existing.
    Compiler pipeline adalah PLACEHOLDER untuk Fase 2.
    """

    def __init__(self, interpreter: Penerjemah):
        self.interpreter = interpreter  # Gunakan interpreter existing!
        self.manajer = dapatkan_manajer_fox()

        # Fase 1: Cache ini akan selalu kosong
        # Fase 2: Di sini compiled bytecode akan disimpan
        self.compiler_cache = {}

    async def compile_morph_function(self, fungsi_node: ast.FungsiDeklarasi):
        """
        FASE 1: PLACEHOLDER - Selalu return None
        FASE 2: Implement transpiler MORPH → Python bytecode
        """
        # TODO Fase 2: Transpilation logic
        # bytecode = self._transpile_to_python(fungsi_node)
        # return compile(bytecode, ...)
        return None

    async def execute_function(self, fungsi: Fungsi, args):
        """Route eksekusi fungsi ke strategy yang tepat"""

        # Fase 1: Cache check akan selalu False
        if fungsi.deklarasi.nama.nilai in self.compiler_cache:
            # Fase 2: Compiled path
            return await self._execute_compiled(fungsi, args)

        # Fase 1: SELALU masuk jalur interpreted ini
        return await self._execute_interpreted(fungsi, args)

    async def _execute_interpreted(self, fungsi: Fungsi, args: list):
        """Jalur interpreter existing dengan Fox routing"""

        async def _run_via_interpreter():
            # Panggil 'fungsi.panggil' secara langsung dengan argumen yang sudah dievaluasi.
            # Token dari nama fungsi digunakan untuk pelaporan error.
            coro = fungsi.panggil(self.interpreter, args, fungsi.deklarasi.nama)
            # Karena 'panggil' mengembalikan coroutine, kita perlu meng-await-nya.
            return await coro

        # Heuristik sederhana: fungsi kecil → sfox, besar → wfox
        if self._is_lightweight_function(fungsi):
            return await sfox(
                f"exec_{fungsi.deklarasi.nama.nilai}",
                _run_via_interpreter
            )
        else:
            return await wfox(
                f"exec_{fungsi.deklarasi.nama.nilai}",
                _run_via_interpreter,
                estimasi_durasi=0.3  # Placeholder estimate
            )

    async def _execute_compiled(self, fungsi, args):
        """FASE 2: Untuk compiled functions"""
        # Fase 1: Tidak akan dipanggil
        raise NotImplementedError("Compiled execution - Fase 2")

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
