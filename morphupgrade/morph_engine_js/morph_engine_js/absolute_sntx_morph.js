// transpiler/js/absolute_sntx_morph.js
class MRPH {
    terima(visitor) {
        const namaMetode = `kunjungi${this.constructor.name}`;
        if (visitor[namaMetode]) return visitor[namaMetode](this);
        throw new Error(`Metode ${namaMetode} belum diimplementasikan di visitor.`);
    }
}
class St extends MRPH {}
class Xprs extends MRPH {}
class Bagian extends MRPH { constructor(p) { super(); this.daftar_pernyataan = p; } }
class Konstanta extends Xprs { constructor(t) { super(); this.token = t; this.nilai = t.nilai; } }
class Identitas extends Xprs { constructor(t) { super(); this.token = t; this.nama = t.nilai; } }
class Daftar extends Xprs { constructor(e) { super(); this.elemen = e; } }
class Kamus extends Xprs { constructor(p) { super(); this.pasangan = p; } }
class FoxBinary extends Xprs { constructor(k, o, kn) { super(); this.kiri = k; this.op = o; this.kanan = kn; } }
class FoxUnary extends Xprs { constructor(o, k) { super(); this.op = o; this.kanan = k; } }
class PanggilFungsi extends Xprs { constructor(c, a) { super(); this.callee = c; this.argumen = a; } }
class Akses extends Xprs { constructor(o, k) { super(); this.objek = o; this.kunci = k; } }
class DeklarasiVariabel extends St { constructor(j, n, nl) { super(); this.jenis_deklarasi = j; this.nama = n; this.nilai = nl; } }
class Assignment extends St { constructor(n, nl) { super(); this.nama = n; this.nilai = nl; } }
class PernyataanEkspresi extends St { constructor(e) { super(); this.ekspresi = e; } }
class JikaMaka extends St { constructor(k, bm, r, bl) { super(); this.kondisi = k; this.blok_maka = bm; this.rantai_lain_jika = r; this.blok_lain = bl; } }
class FungsiDeklarasi extends St { constructor(n, p, b) { super(); this.nama = n; this.parameter = p; this.badan = b; } }
class PernyataanKembalikan extends St { constructor(kk, n) { super(); this.kata_kunci = kk; this.nilai = n; } }
class Selama extends St { constructor(k, b) { super(); this.kondisi = k; this.badan = b; } }
class Tulis extends St { constructor(a) { super(); this.argumen = a; } }
class Ambil extends Xprs { constructor(p) { super(); this.prompt = p; } }
class Pinjam extends St { constructor(p) { super(); this.path_file = p; } }
class Pilih extends St { constructor(e, k, kl) { super(); this.ekspresi = e; this.kasus = k; this.kasus_lainnya = kl; } }
class PilihKasus extends MRPH { constructor(n, b) { super(); this.nilai = n; this.badan = b; } }
class KasusLainnya extends MRPH { constructor(b) { super(); this.badan = b; } }

module.exports = {
    MRPH, St, Xprs, Bagian, Konstanta, Identitas, Daftar, Kamus, FoxBinary, FoxUnary,
    PanggilFungsi, Akses, DeklarasiVariabel, Assignment, PernyataanEkspresi, JikaMaka,
    FungsiDeklarasi, PernyataanKembalikan, Selama, Tulis, Ambil, Pinjam, Pilih,
    PilihKasus, KasusLainnya
};
