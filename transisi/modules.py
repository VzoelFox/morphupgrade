# transisi/modules.py
# Handler untuk sistem modul MORPH

import os
import threading
from typing import Dict, Any, TYPE_CHECKING

from .kesalahan import KesalahanRuntime
from .morph_t import Token

if TYPE_CHECKING:
    from .translator import Penerjemah


class ModuleCache:
    """Menyimpan hasil eksekusi modul yang sudah berhasil dengan mekanisme eviksi."""

    def __init__(self, maxsize=128):  # Default 128 modules
        self.maxsize = int(os.getenv('MORPH_MODULE_CACHE_SIZE', maxsize))
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def get(self, absolute_path: str):
        """Mengambil modul dari cache jika ada."""
        with self._lock:
            return self._cache.get(absolute_path)

    def set(self, absolute_path: str, exports: Dict[str, Any]):
        """Menyimpan hasil ekspor modul ke cache. Menerapkan eviksi jika cache penuh."""
        with self._lock:
            if len(self._cache) >= self.maxsize:
                # Evict entri tertua (FIFO untuk kesederhanaan)
                try:
                    oldest_key = next(iter(self._cache))
                    del self._cache[oldest_key]
                except StopIteration:
                    # Cache kosong, tidak ada yang perlu dihapus
                    pass
            self._cache[absolute_path] = exports

    def clear(self):
        """Membersihkan cache, berguna untuk testing."""
        with self._lock:
            self._cache.clear()

class ModuleLoader:
    """Mengelola pemuatan, resolusi path, dan caching modul."""
    def __init__(self, interpreter: "Penerjemah"):
        self.interpreter = interpreter
        self.cache = ModuleCache()
        # Stack untuk melacak rantai impor dan mendeteksi impor melingkar
        self._loading_stack: list[str] = []

        # Tentukan search path berdasarkan environment variable dan default
        self.search_paths = []
        morph_path = os.getenv('MORPH_PATH', '')
        if morph_path:
            # Gunakan os.pathsep agar kompatibel lintas platform (mis: ':' di Linux, ';' di Windows)
            self.search_paths.extend(morph_path.split(os.pathsep))

        # Tambahkan path untuk standard library bawaan (jika ada nanti)
        stdlib_path = os.path.join(os.path.dirname(__file__), 'stdlib')
        self.search_paths.append(stdlib_path)

    def _resolve_path(self, path_token: Token, importer_file: str | None) -> str:
        """Mencari path absolut dari sebuah modul berdasarkan prioritas."""
        import_path = path_token.nilai
        # 1. Jika path sudah absolut, gunakan langsung
        if os.path.isabs(import_path):
            if os.path.exists(import_path):
                return import_path
            raise KesalahanRuntime(path_token, f"File tidak ditemukan: {import_path}")

        # 2. Coba path relatif terhadap file yang mengimpor
        # Jika importer_file None (misal, dari REPL), gunakan direktori kerja saat ini
        base_dir = os.path.dirname(os.path.abspath(importer_file)) if importer_file else os.getcwd()
        relative_candidate = os.path.join(base_dir, import_path)
        if os.path.exists(relative_candidate):
            return os.path.abspath(relative_candidate)

        # 3. Fallback: Cari di search_paths (MORPH_PATH, stdlib)
        for search_dir in self.search_paths:
            candidate = os.path.join(search_dir, import_path)
            if os.path.exists(candidate):
                return os.path.abspath(candidate)

        raise KesalahanRuntime(path_token, f"Modul '{import_path}' tidak ditemukan.")

    async def load_module(self, path_token: Token, importer_file: str | None) -> Dict[str, Any]:
        """Orkestrasi proses pemuatan modul: resolve, check cache, check circular, eksekusi."""
        abs_path = self._resolve_path(path_token, importer_file)

        # Cek impor melingkar
        if abs_path in self._loading_stack:
            # Tampilkan nama file saja agar rantai error lebih ringkas
            chain_display = [os.path.basename(p) for p in self._loading_stack]
            chain = " -> ".join(chain_display + [os.path.basename(abs_path)])
            raise KesalahanRuntime(
                path_token,
                f"Import melingkar terdeteksi!\nRantai: {chain}"
            )

        # Cek cache (hanya untuk modul yang sudah berhasil di-load sebelumnya)
        cached_module = self.cache.get(abs_path)
        if cached_module is not None:
            return cached_module

        # Tambahkan ke stack sebelum eksekusi
        self._loading_stack.append(abs_path)

        try:
            # Delegasikan eksekusi ke interpreter
            exports = await self.interpreter._jalankan_modul(abs_path)
            # Jika berhasil, simpan ke cache
            self.cache.set(abs_path, exports)
            return exports
        finally:
            # Selalu keluarkan dari stack, baik berhasil maupun gagal
            self._loading_stack.pop()
