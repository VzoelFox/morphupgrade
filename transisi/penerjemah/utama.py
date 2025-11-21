# transisi/penerjemah/utama.py
import os
import json
import asyncio
from .. import absolute_sntx_morph as ast
from ..morph_t import TipeToken, Token
from ..kesalahan import (
    KesalahanRuntime, KesalahanTipe, KesalahanNama,
    KesalahanIndeks, KesalahanKunci, KesalahanPembagianNol,
    KesalahanPola, KesalahanAtributFFI
)
from ..lx import Leksikal
from ..crusher import Pengurai
from ..modules import ModuleLoader
from ..ffi import FFIBridge, PythonModule, PythonObject
from .tipe_runtime import (
    NilaiKembalian, BerhentiLoop, LanjutkanLoop,
    FungsiBawaan, FungsiBawaanAsink, Lingkungan,
    InstansiVarian, KonstruktorVarian, TipeVarian,
    MorphInstance, MorphKelas, Fungsi, FungsiAsink
)
import io
import sys
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from ..runtime_fox import RuntimeMORPHFox
from ..aot_visitor import AotVisitor
from .visitor_ekspresi import ExpressionVisitor
from .visitor_pernyataan import StatementVisitor
from .visitor_sistem import SystemVisitor

class Penerjemah(ExpressionVisitor, StatementVisitor, SystemVisitor):
    """Visitor yang mengekusi AST."""
    def __init__(self, formatter, output_stream=sys.stdout):
        self.lingkungan_global = Lingkungan()
        self.lingkungan = self.lingkungan_global
        self.formatter = formatter
        self.output_stream = output_stream
        self.call_stack = []
        self.current_file = None
        self.module_loader = ModuleLoader(self)
        self.ffi_bridge = FFIBridge()
        self.runtime: "RuntimeMORPHFox" | None = None
        BATAS_REKURSI_DEFAULT = 800
        batas_dari_env = os.environ.get('MORPH_RECURSION_LIMIT')
        if batas_dari_env and batas_dari_env.isdigit():
            self.batas_rekursi = int(batas_dari_env)
        else:
            self.batas_rekursi = BATAS_REKURSI_DEFAULT
        self.tingkat_rekursi = 0

        # Konfigurasi Batas Loop (Loop Protection)
        BATAS_LOOP_DEFAULT = 10000
        batas_loop_env = os.environ.get('MORPH_LOOP_LIMIT')
        if batas_loop_env and batas_loop_env.isdigit():
            self.batas_loop = int(batas_loop_env)
        else:
            self.batas_loop = BATAS_LOOP_DEFAULT

        self.lingkungan_global.definisi("baca_json", FungsiBawaan(self._fungsi_baca_json))
        self.lingkungan_global.definisi("tidur", FungsiBawaan(self._fungsi_tidur_sync_wrapper))

        # Integrasi Placeholder untuk Circuit Breaker / Runtime Safety
        # Ini akan di-inject oleh ManajerFox atau runtime yang lebih tinggi
        self.pemutus_sirkuit = None

    def _periksa_keamanan_eksekusi(self):
        """
        Memeriksa apakah aman untuk melanjutkan eksekusi.
        Dapat dihubungkan dengan PemutusSirkuit dari fox_engine.
        """
        if self.pemutus_sirkuit and hasattr(self.pemutus_sirkuit, 'bisa_eksekusi'):
            if not self.pemutus_sirkuit.bisa_eksekusi():
                raise KesalahanRuntime(None, "Eksekusi dihentikan oleh Pemutus Sirkuit (Sistem Kelebihan Beban).")

    def _fungsi_baca_json(self, argumen):
        if len(argumen) != 1:
            raise KesalahanTipe(None, f"Fungsi 'baca_json' memerlukan 1 argumen (path file), tetapi menerima {len(argumen)}.")
        path_file = argumen[0]
        if not isinstance(path_file, str):
            raise KesalahanTipe(None, f"Argumen untuk 'baca_json' harus berupa teks (string) path file.")
        try:
            with open(path_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            raise KesalahanRuntime(None, f"File tidak ditemukan: '{path_file}'")
        except json.JSONDecodeError as e:
            raise KesalahanRuntime(None, f"Gagal mem-parsing file '{path_file}'. Format JSON tidak valid: {e.msg}")
        except Exception as e:
            raise KesalahanRuntime(None, f"Terjadi kesalahan saat membaca file '{path_file}': {e}")

    def _fungsi_tidur_sync_wrapper(self, argumen):
        if len(argumen) != 1:
            raise KesalahanTipe(None, "Fungsi 'tidur' memerlukan 1 argumen (durasi dalam detik).")
        durasi = argumen[0]
        if not isinstance(durasi, (int, float)):
            raise KesalahanTipe(None, "Argumen untuk 'tidur' harus berupa angka.")
        return asyncio.sleep(durasi)

    async def terjemahkan(self, program: ast.Bagian, current_file: str | None = None):
        self.module_loader._loading_stack.clear()
        self.current_file = current_file
        self.lingkungan = self.lingkungan_global
        daftar_kesalahan = []
        if current_file:
            abs_path = os.path.abspath(current_file)
            self.module_loader._loading_stack.append(abs_path)
        await self._jalankan_aot_pass(program)
        try:
            for pernyataan in program.daftar_pernyataan:
                hasil_eksekusi = await self._eksekusi_dan_tangkap_error(pernyataan)
                if hasil_eksekusi is not None:
                    daftar_kesalahan.append(hasil_eksekusi)
                    return daftar_kesalahan
            return daftar_kesalahan
        finally:
            self.module_loader._loading_stack.clear()

    async def _jalankan_aot_pass(self, program: ast.Bagian):
        if not self.runtime:
            return
        aot_aliases = set()
        declared_functions = {}
        for pernyataan in program.daftar_pernyataan:
            if isinstance(pernyataan, ast.Pinjam):
                await self._eksekusi(pernyataan)
                if pernyataan.butuh_aot and pernyataan.alias:
                    aot_aliases.add(pernyataan.alias.nilai)
            elif isinstance(pernyataan, (ast.FungsiDeklarasi, ast.FungsiAsinkDeklarasi)):
                declared_functions[pernyataan.nama.nilai] = pernyataan
        if not aot_aliases:
            return
        visitor = AotVisitor(aot_aliases)
        tasks_kompilasi = []
        for nama_fungsi, node_fungsi in declared_functions.items():
            if visitor.periksa(node_fungsi.badan):
                print(f"INFO: AOT hint ditemukan. Memicu kompilasi untuk fungsi '{nama_fungsi}'.")
                fungsi_obj = Fungsi(node_fungsi, self.lingkungan_global)
                tasks_kompilasi.append(self.runtime.paksa_kompilasi_aot(fungsi_obj))
        if tasks_kompilasi:
            await asyncio.gather(*tasks_kompilasi)

    async def _eksekusi_dan_tangkap_error(self, pernyataan: ast.St):
        try:
            await self._eksekusi(pernyataan)
            return None
        except KesalahanRuntime as e:
            stack_untuk_dilaporkan = getattr(e, 'morph_stack', self.call_stack)
            node_untuk_dilaporkan = getattr(e, 'node', pernyataan)
            return self.formatter.format_runtime(e, stack_untuk_dilaporkan, node=node_untuk_dilaporkan)

    async def _eksekusi(self, pernyataan: ast.St):
        self._periksa_keamanan_eksekusi() # Cek safety sebelum setiap pernyataan
        await pernyataan.terima(self)

    async def _evaluasi(self, ekspresi: ast.Xprs):
        try:
            return await ekspresi.terima(self)
        except KesalahanRuntime as e:
            if not hasattr(e, 'node'):
                 e.node = ekspresi
            raise e

    async def _jalankan_modul(self, module_path: str) -> Dict[str, Any]:
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                source = f.read()
            return await self._jalankan_modul_dari_sumber(module_path, source)
        except IOError as e:
            raise KesalahanRuntime(None, f"Tidak bisa membaca file modul: {module_path}. Detail: {e}")

    async def _jalankan_modul_dari_sumber(self, module_path: str, source: str) -> Dict[str, Any]:
        lingkungan_sebelumnya = self.lingkungan
        file_sebelumnya = self.current_file
        lingkungan_modul = Lingkungan(induk=None)
        self.lingkungan = lingkungan_modul
        self.current_file = module_path
        try:
            leksikal = Leksikal(source, f"modul '{os.path.basename(module_path)}'")
            tokens, daftar_kesalahan_lexer = leksikal.buat_token()
            if daftar_kesalahan_lexer:
                kesalahan = daftar_kesalahan_lexer[0]
                pesan_error = kesalahan.get("pesan", "Error tidak diketahui")
                token_dummy = Token(TipeToken.TIDAK_DIKENAL, module_path, kesalahan.get("baris", 1), kesalahan.get("kolom", 1))
                raise KesalahanRuntime(token_dummy, f"Kesalahan leksikal di modul '{os.path.basename(module_path)}': {pesan_error}")
            parser = Pengurai(tokens)
            ast_modul = parser.urai()
            if parser.daftar_kesalahan:
                token_kesalahan, pesan = parser.daftar_kesalahan[0]
                raise KesalahanRuntime(token_kesalahan, f"Kesalahan sintaks di modul '{os.path.basename(module_path)}': {pesan}")
            for pernyataan in ast_modul.daftar_pernyataan:
                await self._eksekusi(pernyataan)
            exports = {nama: nilai for nama, nilai in self.lingkungan.nilai.items() if not nama.startswith('_')}
            return exports
        finally:
            self.lingkungan = lingkungan_sebelumnya
            self.current_file = file_sebelumnya

    async def _evaluasi_dalam_lingkungan(self, ekspresi: ast.Xprs, lingkungan: Lingkungan):
        lingkungan_sebelumnya = self.lingkungan
        self.lingkungan = lingkungan
        try:
            return await self._evaluasi(ekspresi)
        finally:
            self.lingkungan = lingkungan_sebelumnya

    async def _pola_cocok(self, pola: ast.Pola, nilai, lingkungan):
        if isinstance(pola, ast.PolaWildcard):
            return True, lingkungan
        if isinstance(pola, ast.PolaLiteral):
            nilai_pola = await self._evaluasi(pola.nilai)
            return nilai == nilai_pola, lingkungan
        if isinstance(pola, ast.PolaVarian):
            if not isinstance(nilai, InstansiVarian):
                return False, lingkungan
            if pola.nama.nilai != nilai.konstruktor.nama:
                return False, lingkungan
            if len(pola.daftar_ikatan) != len(nilai.argumen):
                raise KesalahanTipe(
                    pola.nama,
                    f"Pola '{pola.nama.nilai}' mengharapkan {len(pola.daftar_ikatan)} argumen, tapi varian memiliki {len(nilai.argumen)}."
                )
            for token_ikatan, nilai_argumen in zip(pola.daftar_ikatan, nilai.argumen):
                if token_ikatan.nilai != '_':
                    lingkungan.definisi(token_ikatan.nilai, nilai_argumen)
            return True, lingkungan
        if isinstance(pola, ast.PolaIkatanVariabel):
            lingkungan.definisi(pola.token.nilai, nilai)
            return True, lingkungan
        if isinstance(pola, ast.PolaDaftar):
            if not isinstance(nilai, list):
                return False, lingkungan
            jumlah_pola_tetap = len(pola.daftar_pola)
            if pola.pola_sisa:
                if len(nilai) < jumlah_pola_tetap:
                    return False, lingkungan
                for i in range(jumlah_pola_tetap):
                    cocok, _ = await self._pola_cocok(pola.daftar_pola[i], nilai[i], lingkungan)
                    if not cocok:
                        return False, lingkungan
                sisa_daftar = nilai[jumlah_pola_tetap:]
                lingkungan.definisi(pola.pola_sisa.nilai, sisa_daftar)
                return True, lingkungan
            else:
                if jumlah_pola_tetap != len(nilai):
                    return False, lingkungan
                for sub_pola, sub_nilai in zip(pola.daftar_pola, nilai):
                    cocok, _ = await self._pola_cocok(sub_pola, sub_nilai, lingkungan)
                    if not cocok:
                        return False, lingkungan
                return True, lingkungan
        return False, lingkungan

    async def _eksekusi_blok(self, blok_node: ast.Bagian, lingkungan_blok: Lingkungan):
        lingkungan_sebelumnya = self.lingkungan
        self.lingkungan = lingkungan_blok
        try:
            for pernyataan in blok_node.daftar_pernyataan:
                await self._eksekusi(pernyataan)
        finally:
            self.lingkungan = lingkungan_sebelumnya

    def _ke_string(self, obj):
        if obj is None: return "nil"
        if isinstance(obj, bool): return "benar" if obj else "salah"
        if isinstance(obj, str): return f'"{obj}"'
        if isinstance(obj, (Fungsi, MorphKelas, MorphInstance)):
            return str(obj)
        if isinstance(obj, list):
            return f"[{', '.join(self._ke_string(e) for e in obj)}]"
        if isinstance(obj, dict):
            pasangan = [f'{self._ke_string(k)}: {self._ke_string(v)}' for k, v in obj.items()]
            return f"{{{', '.join(pasangan)}}}"
        if isinstance(obj, InstansiVarian):
            if not obj.argumen:
                return obj.konstruktor.nama
            args_str = ', '.join(self._ke_string(arg) for arg in obj.argumen)
            return f"{obj.konstruktor.nama}({args_str})"
        return str(obj)

    def _apakah_benar(self, obj):
        if obj is None: return False
        if isinstance(obj, bool): return obj
        return True

    def _periksa_tipe_angka(self, operator, *operands):
        for operand in operands:
            if not isinstance(operand, (int, float)) or isinstance(operand, bool):
                raise KesalahanTipe(operator, "Operan harus berupa angka.")

def patch_ast_nodes():
    async def terima_async(self, visitor):
        nama_metode = 'kunjungi_' + self.__class__.__name__
        metode = getattr(visitor, nama_metode, None)
        if metode is None:
            print(f"PERINGATAN: Metode {nama_metode} belum diimplementasikan di {visitor.__class__.__name__}")
            return None
        return await metode(self)
    ast.MRPH.terima_async = terima_async

    def terima_sync(self, visitor):
        nama_metode = 'kunjungi_' + self.__class__.__name__
        metode = getattr(visitor, nama_metode, None)
        if metode is None:
            print(f"PERINGATAN: Metode {nama_metode} belum diimplementasikan di {visitor.__class__.__name__}")
            return None
        return metode(self)
    ast.MRPH.terima = terima_sync

patch_ast_nodes()
