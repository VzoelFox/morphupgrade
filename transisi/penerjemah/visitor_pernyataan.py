# transisi/penerjemah/visitor_pernyataan.py
from .. import absolute_sntx_morph as ast
from ..morph_t import TipeToken
from ..kesalahan import KesalahanRuntime, KesalahanTipe, KesalahanIndeks, KesalahanKunci, KesalahanPola
from .tipe_runtime import NilaiKembalian, BerhentiLoop, LanjutkanLoop, Lingkungan, MorphInstance

class StatementVisitor:
    async def kunjungi_Bagian(self, node: ast.Bagian):
        for pernyataan in node.daftar_pernyataan:
            await self._eksekusi(pernyataan)

    async def kunjungi_PernyataanEkspresi(self, node: ast.PernyataanEkspresi):
        await self._evaluasi(node.ekspresi)

    async def kunjungi_DeklarasiVariabel(self, node: ast.DeklarasiVariabel):
        nilai = None
        if node.nilai is not None:
            nilai = await self._evaluasi(node.nilai)
        adalah_konstan = (node.jenis_deklarasi.tipe == TipeToken.TETAP)
        self.lingkungan.definisi(node.nama.nilai, nilai, adalah_konstan)

    async def kunjungi_Tulis(self, node: ast.Tulis):
        output = [self._ke_string(await self._evaluasi(arg)) for arg in node.argumen]
        self.output_stream.write(' '.join(output))

    async def kunjungi_Assignment(self, node: ast.Assignment):
        nilai = await self._evaluasi(node.nilai)
        target = node.target
        if isinstance(target, ast.Identitas):
            self.lingkungan.tetapkan(target.token, nilai)
        elif isinstance(target, ast.Akses):
            objek = await self._evaluasi(target.objek)
            kunci = await self._evaluasi(target.kunci)
            if isinstance(objek, list):
                if not isinstance(kunci, int): raise KesalahanTipe(target.kunci.token, "Indeks daftar harus berupa angka.")
                if not (0 <= kunci < len(objek)): raise KesalahanIndeks(target.kunci.token, "Indeks di luar jangkauan.")
                objek[kunci] = nilai
            elif isinstance(objek, dict):
                if not isinstance(kunci, str): raise KesalahanKunci(target.kunci.token, "Kunci kamus harus berupa teks.")
                objek[kunci] = nilai
            else:
                raise KesalahanTipe(target.objek.token, "Hanya item dalam daftar atau kamus yang dapat diubah.")
        elif isinstance(target, ast.AmbilProperti):
            objek = await self._evaluasi(target.objek)
            if not isinstance(objek, MorphInstance):
                raise KesalahanTipe(target.nama, "Hanya properti dari instance kelas yang bisa diubah.")
            adalah_akses_internal = isinstance(target.objek, ast.Ini)
            objek.tetapkan(target.nama, nilai, dari_internal=adalah_akses_internal)
        else:
            raise KesalahanRuntime(node.target, "Target assignment tidak valid.")

    async def kunjungi_PernyataanKembalikan(self, node: ast.PernyataanKembalikan):
        nilai = await self._evaluasi(node.nilai) if node.nilai is not None else None
        raise NilaiKembalian(nilai)

    async def kunjungi_Berhenti(self, node: ast.Berhenti):
        raise BerhentiLoop()

    async def kunjungi_Lanjutkan(self, node: ast.Lanjutkan):
        raise LanjutkanLoop()

    async def kunjungi_Selama(self, node: ast.Selama):
        while self._apakah_benar(await self._evaluasi(node.kondisi)):
            try:
                await self._eksekusi_blok(node.badan, Lingkungan(induk=self.lingkungan))
            except LanjutkanLoop:
                continue
            except BerhentiLoop:
                break

    async def kunjungi_JikaMaka(self, node: ast.JikaMaka):
        if self._apakah_benar(await self._evaluasi(node.kondisi)):
            await self._eksekusi_blok(node.blok_maka, Lingkungan(induk=self.lingkungan))
        else:
            for kondisi_lain, blok_lain in node.rantai_lain_jika:
                if self._apakah_benar(await self._evaluasi(kondisi_lain)):
                    await self._eksekusi_blok(blok_lain, Lingkungan(induk=self.lingkungan))
                    return
            if node.blok_lain is not None:
                await self._eksekusi_blok(node.blok_lain, Lingkungan(induk=self.lingkungan))

    async def kunjungi_Pilih(self, node: ast.Pilih):
        nilai_ekspresi = await self._evaluasi(node.ekspresi)
        kasus_cocok = False
        for kasus in node.kasus:
            nilai_untuk_diperiksa = kasus.nilai if isinstance(kasus.nilai, list) else [kasus.nilai]
            for nilai_pembanding_node in nilai_untuk_diperiksa:
                nilai_pembanding = await self._evaluasi(nilai_pembanding_node)
                if nilai_ekspresi == nilai_pembanding:
                    await self._eksekusi_blok(kasus.badan, Lingkungan(induk=self.lingkungan))
                    kasus_cocok = True
                    break
            if kasus_cocok: break
        if not kasus_cocok and node.kasus_lainnya is not None:
            await self._eksekusi_blok(node.kasus_lainnya.badan, Lingkungan(induk=self.lingkungan))

    async def kunjungi_JodohkanLiteral(self, node: ast.JodohkanLiteral):
        nilai_ekspresi = await self._evaluasi(node.subjek)
        for kasus in node.kasus:
            nilai_kasus = await self._evaluasi(kasus.nilai)
            if nilai_ekspresi == nilai_kasus:
                await self._eksekusi_blok(kasus.badan, Lingkungan(induk=self.lingkungan))
                return
        raise KesalahanPola(node.subjek.token, "Tidak ada pola `jodohkan` yang cocok.")
