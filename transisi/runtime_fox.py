# transisi/runtime_fox.py
from fox_engine.api import sfox, wfox, mfox_baca_file, dapatkan_manajer_fox, tfox
from .translator import Penerjemah, Fungsi
from . import absolute_sntx_morph as ast
from .morph_t import TipeToken, Token
from .transpiler import Transpiler
from typing import Any
import asyncio

class JitModuleProxy:
    """
    Sebuah proxy yang mencegat akses item pada objek modul Morph dari dalam
    kode JIT. Jika item yang diakses adalah sebuah Fungsi, ia akan membungkusnya
    dalam panggilan yang dapat dieksekusi secara sinkron sebelum mengembalikannya.
    """
    def __init__(self, module_obj, runtime, loop):
        self._module = module_obj
        self._runtime = runtime
        self._loop = loop

    def __getitem__(self, key):
        """Mencegat akses item, misalnya, `modul["fungsi"]`."""
        item = self._module[key]
        if isinstance(item, Fungsi):
            def wrapper(*args_panggilan):
                future = asyncio.run_coroutine_threadsafe(
                    self._runtime.execute_function(item, list(args_panggilan)), self._loop
                )
                return future.result()
            return wrapper
        return item

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
        Memicu transpilasi dan kompilasi fungsi MORPH ke bytecode Python
        secara asinkron menggunakan ThunderFox (tfox).
        """
        nama_fungsi = fungsi.deklarasi.nama.nilai
        if nama_fungsi in self.compilation_in_progress:
            return

        self.compilation_in_progress.add(nama_fungsi)

        async def _compile_task():
            # Transpilasi isi fungsi ke source code Python
            # Teruskan lingkungan penutup (closure) dari fungsi
            transpiler = Transpiler(fungsi.penutup)
            body_code = transpiler.transpilasi(fungsi.deklarasi)

            # Kompilasi hanya isi fungsi
            return compile(body_code, f"<morph-jit-body:{nama_fungsi}>", "exec")

        try:
            bytecode = await tfox(f"compile_{nama_fungsi}", _compile_task)
            self.compiler_cache[nama_fungsi] = bytecode
            print(f"INFO: Fungsi '{nama_fungsi}' berhasil di-JIT-compile ke bytecode Python.")
        except Exception as e:
            print(f"ERROR: JIT-compilation untuk '{nama_fungsi}' gagal: {e}")
        finally:
            self.compilation_in_progress.remove(nama_fungsi)

    async def paksa_kompilasi_aot(self, fungsi: Fungsi):
        """
        Secara proaktif memicu kompilasi untuk sebuah fungsi.
        Melewati pengecekan ambang batas JIT.
        """
        nama_fungsi = fungsi.deklarasi.nama.nilai
        if nama_fungsi in self.compiler_cache or nama_fungsi in self.compilation_in_progress:
            return # Sudah dikompilasi atau sedang dalam proses

        # Langsung panggil compile_morph_function
        await self.compile_morph_function(fungsi)

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
        """
        Membungkus bytecode isi fungsi dalam fungsi Python dinamis,
        mengeksekusinya, dan mengembalikan hasilnya.
        """
        nama_fungsi = fungsi.deklarasi.nama.nilai
        body_bytecode = self.compiler_cache[nama_fungsi]

        async def _exec_task():
            parameter_names = [p.nilai for p in fungsi.deklarasi.parameter]

            # Buat fungsi wrapper dinamis
            # 1. Deklarasi fungsi
            func_def = f"def {nama_fungsi}({', '.join(parameter_names)}):\n"
            # 2. Inisialisasi variabel hasil
            func_def += "    __hasil = None\n"
            # 3. Eksekusi bytecode isi fungsi (ini memerlukan cara khusus)
            #    Kita akan definisikan fungsi inner dan exec body di dalamnya

            namespace = {}
            # Definisikan fungsi 'pembungkus' yang akan berisi body
            exec(f"def _{nama_fungsi}_wrapper(): pass", namespace)

            # Ganti code object dari fungsi wrapper dengan body kita
            wrapper_func = namespace[f'_{nama_fungsi}_wrapper']
            # Atur ulang code object dengan argumen yang benar
            final_code = wrapper_func.__code__.replace(
                co_code=body_bytecode.co_code,
                co_consts=body_bytecode.co_consts,
                co_names=body_bytecode.co_names,
                co_varnames=tuple(parameter_names),
                co_argcount=len(parameter_names)
            )

            # Buat fungsi akhir dengan code object yang sudah diperbaiki
            final_func = type(lambda: None)(final_code, {})

            # Panggil fungsi yang sudah dikompilasi dengan argumennya
            return final_func(*args)

        # Setelah dipikir-pikir, pendekatan di atas terlalu rumit.
        # Mari kita gunakan cara yang lebih sederhana dan lebih mudah dibaca.

        async def _exec_task_simple(runtime_self):
            parameter_names = [p.nilai for p in fungsi.deklarasi.parameter]

            def sync_executor(*current_args):
                local_namespace = {nama: nilai for nama, nilai in zip(parameter_names, current_args)}
                current_loop = asyncio.get_running_loop()

                for nama in body_bytecode.co_names:
                    if nama == nama_fungsi:
                        local_namespace[nama] = sync_executor
                        continue

                    try:
                        nilai = fungsi.penutup.dapatkan(Token(TipeToken.NAMA, nama, 0, 0))

                        if isinstance(nilai, dict) and 'tipe' not in nilai: # Modul Morph
                            local_namespace[nama] = JitModuleProxy(nilai, runtime_self, current_loop)
                        elif isinstance(nilai, Fungsi): # Fungsi Morph biasa
                            def make_wrapper(f):
                                def wrapper(*args_panggilan):
                                    future = asyncio.run_coroutine_threadsafe(
                                        runtime_self.execute_function(f, list(args_panggilan)), current_loop
                                    )
                                    return future.result()
                                return wrapper
                            local_namespace[nama] = make_wrapper(nilai)
                        else:
                            local_namespace[nama] = nilai
                    except Exception:
                        pass

                local_namespace['__hasil'] = None
                exec(body_bytecode, {}, local_namespace)
                return local_namespace['__hasil']

            return sync_executor(*args)

        return await tfox(f"exec_{nama_fungsi}", lambda: _exec_task_simple(self))

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
