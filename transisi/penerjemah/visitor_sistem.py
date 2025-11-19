# transisi/penerjemah/visitor_sistem.py
from .. import absolute_sntx_morph as ast
from ..kesalahan import KesalahanRuntime, KesalahanTipe, KesalahanNama
from .tipe_runtime import (
    Lingkungan, TipeVarian, KonstruktorVarian,
    MorphKelas, Fungsi, FungsiAsink
)

class SystemVisitor:
    async def kunjungi_Kelas(self, node: ast.Kelas):
        superkelas = None
        if node.superkelas is not None:
            superkelas = await self._evaluasi(node.superkelas)
            if not isinstance(superkelas, MorphKelas):
                raise KesalahanTipe(node.superkelas.token, "Superkelas harus berupa sebuah kelas.")
        self.lingkungan.definisi(node.nama.nilai, None)
        lingkungan_kelas = self.lingkungan
        if superkelas is not None:
            lingkungan_kelas = Lingkungan(induk=self.lingkungan)
            lingkungan_kelas.definisi("induk", superkelas)
        metode = {}
        for metode_node in node.metode:
            adalah_inisiasi = metode_node.nama.nilai == "inisiasi"
            FungsiTipe = FungsiAsink if isinstance(metode_node, ast.FungsiAsinkDeklarasi) else Fungsi
            fungsi = FungsiTipe(metode_node, lingkungan_kelas, adalah_inisiasi)
            metode[metode_node.nama.nilai] = fungsi
        kelas = MorphKelas(node.nama.nilai, superkelas, metode)
        self.lingkungan.tetapkan(node.nama, kelas)

    async def kunjungi_TipeDeklarasi(self, node: ast.TipeDeklarasi):
        nama_tipe = node.nama.nilai
        tipe_varian = TipeVarian(nama_tipe)
        self.lingkungan.definisi(nama_tipe, tipe_varian)
        for varian_node in node.daftar_varian:
            nama_varian = varian_node.nama.nilai
            aritas = len(varian_node.parameter)
            konstruktor = KonstruktorVarian(nama_varian, aritas)
            tipe_varian.konstruktor[nama_varian] = konstruktor
            if nama_varian in self.lingkungan.nilai:
                raise KesalahanNama(varian_node.nama, f"Nama '{nama_varian}' sudah didefinisikan sebelumnya.")
            self.lingkungan.definisi(nama_varian, konstruktor)

    async def kunjungi_FungsiDeklarasi(self, node: ast.FungsiDeklarasi):
        fungsi = Fungsi(node, self.lingkungan)
        self.lingkungan.definisi(node.nama.nilai, fungsi)

    async def kunjungi_FungsiAsinkDeklarasi(self, node: ast.FungsiAsinkDeklarasi):
        fungsi = FungsiAsink(node, self.lingkungan)
        self.lingkungan.definisi(node.nama.nilai, fungsi)

    async def kunjungi_AmbilSemua(self, node: ast.AmbilSemua):
        exports = await self.module_loader.load_module(node.path_file, self.current_file)
        if node.alias:
            self.lingkungan.definisi(node.alias.nilai, exports)
        else:
            for nama, nilai in exports.items():
                self.lingkungan.definisi(nama, nilai)

    async def kunjungi_AmbilSebagian(self, node: ast.AmbilSebagian):
        exports = await self.module_loader.load_module(node.path_file, self.current_file)
        for simbol_token in node.daftar_simbol:
            nama = simbol_token.nilai
            if nama not in exports:
                raise KesalahanNama(simbol_token, f"Simbol '{nama}' tidak ditemukan di modul '{node.path_file.nilai}'.")
            self.lingkungan.definisi(nama, exports[nama])

    async def kunjungi_Pinjam(self, node: ast.Pinjam):
        module_path = node.path_file.nilai
        alias = node.alias.nilai if node.alias else None
        if not alias:
            raise KesalahanRuntime(node.path_file, "FFI import harus pakai alias ('sebagai').")
        py_module = self.ffi_bridge.import_module(module_path, node.path_file)
        self.lingkungan.definisi(alias, py_module)
