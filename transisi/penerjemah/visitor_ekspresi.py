# transisi/penerjemah/visitor_ekspresi.py
import asyncio
from .. import absolute_sntx_morph as ast
from ..morph_t import TipeToken
from ..kesalahan import (
    KesalahanRuntime, KesalahanTipe, KesalahanNama,
    KesalahanIndeks, KesalahanKunci, KesalahanPembagianNol,
    KesalahanAtributFFI
)
from .tipe_runtime import (
    Fungsi, FungsiAsink, MorphKelas, MorphInstance,
    KonstruktorVarian, FungsiBawaan, FungsiBawaanAsink
)
from ..ffi import PythonObject

class ExpressionVisitor:
    async def kunjungi_Tunggu(self, node: ast.Tunggu):
        awaitable = await self._evaluasi(node.ekspresi)
        if asyncio.iscoroutine(awaitable) or hasattr(awaitable, '__await__'):
            return await awaitable
        raise KesalahanTipe(node.kata_kunci, "Ekspresi yang mengikuti 'tunggu' harus bisa ditunggu (awaitable).")

    async def kunjungi_AmbilProperti(self, node: ast.AmbilProperti):
        objek = await self._evaluasi(node.objek)
        if hasattr(objek, 'get_attribute'): # PythonModule, PythonObject
            attr_name = node.nama.nilai
            try:
                py_attr = objek.get_attribute(attr_name)
                return self.ffi_bridge.python_to_morph(py_attr)
            except AttributeError as e:
                obj_name = getattr(objek, 'name', type(objek.obj).__name__)
                raise KesalahanAtributFFI(node.nama, f"Atribut '{attr_name}' tidak ditemukan di objek Python '{obj_name}'.", python_exception=e)
        if isinstance(objek, MorphInstance):
            adalah_akses_internal = isinstance(node.objek, ast.Ini)
            return objek.dapatkan(node.nama, dari_internal=adalah_akses_internal)
        if isinstance(objek, str):
            try:
                py_attr = getattr(objek, node.nama.nilai)
                return self.ffi_bridge.python_to_morph(py_attr)
            except AttributeError:
                pass
        raise KesalahanTipe(node.nama, "Hanya instance kelas atau modul FFI yang memiliki properti.")

    async def kunjungi_AturProperti(self, node: ast.AturProperti):
        adalah_akses_internal = isinstance(node.objek, ast.Ini)
        objek = await self._evaluasi(node.objek)
        if not isinstance(objek, MorphInstance):
            raise KesalahanTipe(node.nama, "Hanya instance dari kelas yang dapat diatur propertinya.")
        nilai = await self._evaluasi(node.nilai)
        objek.tetapkan(node.nama, nilai, dari_internal=adalah_akses_internal)
        return nilai

    async def kunjungi_Ini(self, node: ast.Ini):
        return self.lingkungan.dapatkan(node.kata_kunci)

    async def kunjungi_Induk(self, node: ast.Induk):
        superkelas = self.lingkungan.dapatkan(node.kata_kunci)
        instance = self.lingkungan.dapatkan(Token(TipeToken.NAMA, "ini", node.kata_kunci.baris, node.kata_kunci.kolom))
        metode = superkelas.cari_metode(node.metode.nilai)
        if metode is None:
            raise KesalahanRuntime(node.metode, f"Metode '{node.metode.nilai}' tidak ditemukan di superkelas.")
        return metode.bind(instance)

    async def kunjungi_Kamus(self, node: ast.Kamus):
        kamus = {}
        for kunci_node, nilai_node in node.pasangan:
            kunci = await self._evaluasi(kunci_node)
            if not isinstance(kunci, str):
                raise KesalahanKunci(kunci_node.token, "Kunci kamus harus berupa teks.")
            nilai = await self._evaluasi(nilai_node)
            kamus[kunci] = nilai
        return kamus

    async def kunjungi_Daftar(self, node: ast.Daftar):
        tasks = [self._evaluasi(elem) for elem in node.elemen]
        return await asyncio.gather(*tasks)

    async def kunjungi_Akses(self, node: ast.Akses):
        objek = await self._evaluasi(node.objek)
        kunci = await self._evaluasi(node.kunci)
        if isinstance(objek, (list, str)):
            if not isinstance(kunci, int):
                raise KesalahanTipe(node.kunci.token, "Indeks untuk daftar atau teks harus berupa angka.")
            if 0 <= kunci < len(objek):
                return objek[kunci]
            else:
                raise KesalahanIndeks(node.kunci.token, "Indeks di luar jangkauan.")
        if isinstance(objek, dict):
            if not isinstance(kunci, str):
                raise KesalahanKunci(node.kunci.token, "Kunci kamus harus berupa teks.")
            return objek.get(kunci, None)
        raise KesalahanTipe(node.objek.token, "Objek tidak dapat diakses menggunakan '[]'.")

    async def kunjungi_Ambil(self, node: ast.Ambil):
        prompt_str = ""
        if node.prompt:
            prompt_evaluasi = await self._evaluasi(node.prompt)
            prompt_str = self._ke_string(prompt_evaluasi)
        try:
            return input(prompt_str)
        except EOFError:
            return None

    async def kunjungi_PanggilFungsi(self, node: ast.PanggilFungsi):
        callee = await self._evaluasi(node.callee)
        is_morph_callable = isinstance(callee, (Fungsi, MorphKelas))
        if is_morph_callable:
            self.tingkat_rekursi += 1
            if self.tingkat_rekursi > self.batas_rekursi:
                self.tingkat_rekursi -= 1
                raise KesalahanRuntime(node.token, "Batas kedalaman rekursi tercapai.")
        try:
            tasks = [self._evaluasi(arg) for arg in node.argumen]
            argumen = await asyncio.gather(*tasks)
            if isinstance(callee, MorphKelas):
                return await callee.panggil(self, node)
            if self.runtime and isinstance(callee, (Fungsi, FungsiAsink)):
                return await self.runtime.execute_function(callee, argumen)
            if isinstance(callee, (Fungsi, FungsiAsink)):
                coro = callee.panggil(self, argumen, node.token)
                return coro if isinstance(callee, FungsiAsink) else await coro
            if isinstance(callee, KonstruktorVarian):
                return callee(argumen, node.token)
            if isinstance(callee, (FungsiBawaan, FungsiBawaanAsink)):
                try:
                    result = callee(argumen)
                    return await result if asyncio.iscoroutine(result) else result
                except (KesalahanTipe, KesalahanRuntime) as e:
                    e.token = node.token
                    raise e
            if isinstance(callee, PythonObject):
                if not callable(callee.obj):
                    raise KesalahanTipe(node.token, "Objek Python ini tidak bisa dipanggil.")
                argumen_py = [self.ffi_bridge.morph_to_python(arg) for arg in argumen]
                hasil_py = self.ffi_bridge.safe_call(callee.obj, argumen_py, node.token)
                return self.ffi_bridge.python_to_morph(hasil_py)
            raise KesalahanTipe(node.token, "Hanya fungsi, kelas, atau objek FFI yang bisa dipanggil.")
        finally:
            if is_morph_callable:
                self.tingkat_rekursi -= 1

    async def kunjungi_Identitas(self, node: ast.Identitas):
        return self.lingkungan.dapatkan(node.token)

    async def kunjungi_Konstanta(self, node: ast.Konstanta):
        return node.nilai

    async def kunjungi_FoxUnary(self, node: ast.FoxUnary):
        kanan = await self._evaluasi(node.kanan)
        if node.op.tipe == TipeToken.KURANG:
            self._periksa_tipe_angka(node.op, kanan)
            return -kanan
        if node.op.tipe == TipeToken.TIDAK:
            return not self._apakah_benar(kanan)
        return None

    async def kunjungi_FoxBinary(self, node: ast.FoxBinary):
        op_tipe = node.op.tipe
        if op_tipe == TipeToken.DAN:
            kiri = await self._evaluasi(node.kiri)
            if not self._apakah_benar(kiri): return False
            return self._apakah_benar(await self._evaluasi(node.kanan))
        if op_tipe == TipeToken.ATAU:
            kiri = await self._evaluasi(node.kiri)
            if self._apakah_benar(kiri): return kiri
            return await self._evaluasi(node.kanan)
        kiri = await self._evaluasi(node.kiri)
        kanan = await self._evaluasi(node.kanan)
        if op_tipe == TipeToken.TAMBAH:
            if isinstance(kiri, (int, float)) and isinstance(kanan, (int, float)): return kiri + kanan
            if isinstance(kiri, str) and isinstance(kanan, str): return kiri + kanan
            raise KesalahanTipe(node.op, "Operan harus dua angka atau dua teks.")
        if op_tipe == TipeToken.KURANG:
            self._periksa_tipe_angka(node.op, kiri, kanan); return kiri - kanan
        if op_tipe == TipeToken.KALI:
            self._periksa_tipe_angka(node.op, kiri, kanan); return kiri * kanan
        if op_tipe == TipeToken.BAGI:
            self._periksa_tipe_angka(node.op, kiri, kanan)
            if kanan == 0: raise KesalahanPembagianNol(node.op, "Tidak bisa membagi dengan nol.")
            hasil = kiri / kanan
            return int(hasil) if hasil == int(hasil) else hasil
        if op_tipe == TipeToken.MODULO:
            self._periksa_tipe_angka(node.op, kiri, kanan); return kiri % kanan
        if op_tipe == TipeToken.PANGKAT:
            self._periksa_tipe_angka(node.op, kiri, kanan); return kiri ** kanan
        if op_tipe in (TipeToken.LEBIH_DARI, TipeToken.KURANG_DARI, TipeToken.LEBIH_SAMA, TipeToken.KURANG_SAMA):
            if not ((isinstance(kiri, (int, float)) and isinstance(kanan, (int, float))) or (isinstance(kiri, str) and isinstance(kanan, str))):
                raise KesalahanTipe(node.op, "Operan untuk perbandingan harus dua angka atau dua teks.")
            if op_tipe == TipeToken.LEBIH_DARI: return kiri > kanan
            if op_tipe == TipeToken.KURANG_DARI: return kiri < kanan
            if op_tipe == TipeToken.LEBIH_SAMA: return kiri >= kanan
            if op_tipe == TipeToken.KURANG_SAMA: return kiri <= kanan
        if op_tipe == TipeToken.SAMA_DENGAN: return kiri == kanan
        if op_tipe == TipeToken.TIDAK_SAMA: return kiri != kanan
        return None
