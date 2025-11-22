# transisi/penerjemah/visitor_pernyataan.py
from .. import absolute_sntx_morph as ast
from ..morph_t import TipeToken
from ..kesalahan import KesalahanRuntime, KesalahanTipe, KesalahanIndeks, KesalahanKunci, KesalahanPola
from .tipe_runtime import NilaiKembalian, BerhentiLoop, LanjutkanLoop, Lingkungan, MorphInstance
from transisi.common.result import ObjekError

# Helper untuk kompatibilitas
def buat_objek_error(e: Exception, node: ast.MRPH = None):
    pesan = str(e)
    baris = getattr(node, 'token', None).baris if hasattr(node, 'token') else (node.lokasi.baris if node and node.lokasi else 0)
    kolom = getattr(node, 'token', None).kolom if hasattr(node, 'token') else (node.lokasi.kolom if node and node.lokasi else 0)
    return ObjekError(pesan=pesan, baris=baris, kolom=kolom)

class StatementVisitor:
    async def kunjungi_Bagian(self, node: ast.Bagian):
        for pernyataan in node.daftar_pernyataan:
            await self._eksekusi(pernyataan)

    async def kunjungi_PernyataanEkspresi(self, node: ast.PernyataanEkspresi):
        await self._evaluasi(node.ekspresi)

    async def kunjungi_CobaTangkap(self, node: ast.CobaTangkap):
        try:
            await self._eksekusi_blok(node.blok_coba, Lingkungan(induk=self.lingkungan))
        except Exception as e:
            # Tangani error, baik itu internal Python error atau KesalahanRuntime Morph
            if isinstance(e, (NilaiKembalian, BerhentiLoop, LanjutkanLoop)):
                 # Jangan tangkap sinyal kontrol flow!
                raise e

            lingkungan_tangkap = Lingkungan(induk=self.lingkungan)
            if node.nama_error:
                # Bungkus error ke dalam struktur standar Morph
                obj_error = buat_objek_error(e, node)
                lingkungan_tangkap.definisi(node.nama_error.nilai, obj_error, False)

            await self._eksekusi_blok(node.blok_tangkap, lingkungan_tangkap)

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
        counter = 0
        batas = getattr(self, 'batas_loop', 10000) # Fallback jika atribut tidak ada

        while self._apakah_benar(await self._evaluasi(node.kondisi)):
            counter += 1
            if counter > batas:
                raise KesalahanRuntime(node.token, f"Loop melebihi batas iterasi maksimum ({batas}). Kemungkinan infinite loop.")

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

    async def kunjungi_Jodohkan(self, node: ast.Jodohkan):
        nilai_ekspresi = await self._evaluasi(node.ekspresi)
        for kasus in node.kasus:
            lingkungan_kasus = Lingkungan(induk=self.lingkungan)
            cocok, _ = await self._pola_cocok(kasus.pola, nilai_ekspresi, lingkungan_kasus)
            if cocok:
                if kasus.jaga:
                    nilai_jaga = await self._evaluasi_dalam_lingkungan(kasus.jaga, lingkungan_kasus)
                    if not self._apakah_benar(nilai_jaga):
                        continue
                await self._eksekusi_blok(kasus.badan, lingkungan_kasus)
                return
        # Jika tidak ada kasus yang cocok, interpreter lama akan melempar KesalahanPola.
        # Namun, sekarang tanggung jawab ini ada pada VM jika tidak ada yang cocok.
        # Di sini kita tidak melakukan apa-apa, membiarkan eksekusi selesai.
        # Perilaku error akan ditangani oleh kompiler ivm.
