// transpiler/js/crusher.js
const { TipeToken } = require('./morph_t.js');
const ast = require('./absolute_sntx_morph.js');
class PenguraiKesalahan extends Error {}

class Pengurai {
    constructor(t) { this.tokens = t; this.saat_ini = 0; this.daftar_kesalahan = []; }
    urai() {
        const p = [];
        while (!this._diAkhir()) {
            if (this._cocok(TipeToken.AKHIR_BARIS)) continue;
            const s = this._deklarasi();
            if (s) p.push(s);
        }
        return new ast.Bagian(p);
    }
    _deklarasi() {
        try {
            if (this._cocok(TipeToken.BIAR, TipeToken.TETAP)) return this._deklarasiVariabel();
            return this._pernyataan();
        } catch (e) { if (e instanceof PenguraiKesalahan) { this._sinkronisasi(); return null; } throw e; }
    }
    _deklarasiVariabel() {
        const jd = this._sebelumnya();
        const n = this._konsumsi(TipeToken.NAMA, "Dibutuhkan nama variabel.");
        let nl = null;
        if (this._cocok(TipeToken.SAMADENGAN)) nl = this._ekspresi();
        this._konsumsiAkhirBaris("Dibutuhkan baris baru atau titik koma setelah deklarasi variabel.");
        return new ast.DeklarasiVariabel(jd, n, nl);
    }
    _pernyataan() {
        if (this._cocok(TipeToken.TULIS)) return this._pernyataanTulis();
        if (this._cocok(TipeToken.KURAWAL_BUKA)) return new ast.Bagian(this._blok());
        return this._pernyataanEkspresi();
    }
    _pernyataanTulis() {
        this._konsumsi(TipeToken.KURUNG_BUKA, "Dibutuhkan '(' setelah 'tulis'.");
        const a = [];
        if (!this._periksa(TipeToken.KURUNG_TUTUP)) {
            do { a.push(this._ekspresi()); } while (this._cocok(TipeToken.KOMA));
        }
        this._konsumsi(TipeToken.KURUNG_TUTUP, "Dibutuhkan ')' setelah argumen.");
        this._konsumsiAkhirBaris("Dibutuhkan baris baru atau titik koma setelah pernyataan 'tulis'.");
        return new ast.Tulis(a);
    }
    _blok() {
        const p = [];
        while (!this._periksa(TipeToken.KURAWAL_TUTUP) && !this._diAkhir()) p.push(this._deklarasi());
        this._konsumsi(TipeToken.KURAWAL_TUTUP, "Dibutuhkan '}' untuk menutup blok.");
        return p;
    }
    _pernyataanEkspresi() {
        const e = this._ekspresi();
        this._konsumsiAkhirBaris("Dibutuhkan baris baru atau titik koma setelah ekspresi.");
        return new ast.PernyataanEkspresi(e);
    }
    _ekspresi() { return this._penugasan(); }
    _penugasan() {
        const e = this._logikaAtau();
        if (this._cocok(TipeToken.SAMADENGAN)) {
            const eq = this._sebelumnya();
            const n = this._penugasan();
            if (e instanceof ast.Identitas) return new ast.Assignment(e.token, n);
            this._kesalahan(eq, "Target penugasan tidak valid.");
        }
        return e;
    }
    _logikaAtau() { return this._buatParserBiner(() => this._logikaDan(), TipeToken.ATAU); }
    _logikaDan() { return this._buatParserBiner(() => this._perbandingan(), TipeToken.DAN); }
    _perbandingan() { return this._buatParserBiner(() => this._penjumlahan(), TipeToken.SAMA_DENGAN, TipeToken.TIDAK_SAMA, TipeToken.KURANG_DARI, TipeToken.KURANG_SAMA, TipeToken.LEBIH_DARI, TipeToken.LEBIH_SAMA); }
    _penjumlahan() { return this._buatParserBiner(() => this._perkalian(), TipeToken.TAMBAH, TipeToken.KURANG); }
    _perkalian() { return this._buatParserBiner(() => this._unary(), TipeToken.KALI, TipeToken.BAGI, TipeToken.MODULO); }
    _buatParserBiner(m, ...tts) {
        let e = m();
        while (this._cocok(...tts)) {
            const o = this._sebelumnya();
            const k = m();
            e = new ast.FoxBinary(e, o, k);
        }
        return e;
    }
    _unary() {
        if (this._cocok(TipeToken.TIDAK, TipeToken.KURANG)) {
            const o = this._sebelumnya();
            const k = this._unary();
            return new ast.FoxUnary(o, k);
        }
        return this._primary();
    }
    _primary() {
        if (this._cocok(TipeToken.SALAH, TipeToken.BENAR, TipeToken.NIL, TipeToken.ANGKA, TipeToken.TEKS)) return new ast.Konstanta(this._sebelumnya());
        if (this._cocok(TipeToken.NAMA)) return new ast.Identitas(this._sebelumnya());
        if (this._cocok(TipeToken.KURUNG_BUKA)) {
            const e = this._ekspresi();
            this._konsumsi(TipeToken.KURUNG_TUTUP, "Dibutuhkan ')' setelah ekspresi.");
            return e;
        }
        throw this._kesalahan(this._intip(), "Ekspresi tidak terduga.");
    }
    _konsumsi(t, p) { if (this._periksa(t)) return this._maju(); throw this._kesalahan(this._intip(), p); }
    _konsumsiAkhirBaris(p) {
        if (this._cocok(TipeToken.AKHIR_BARIS, TipeToken.TITIK_KOMA)) return;
        if (this._periksa(TipeToken.AKHIR) || this._periksa(TipeToken.KURAWAL_TUTUP) || this._diAkhir()) return;
        throw this._kesalahan(this._intip(), p);
    }
    _cocok(...tts) { for (const t of tts) { if (this._periksa(t)) { this._maju(); return true; } } return false; }
    _periksa(t) { return !this._diAkhir() && this._intip().tipe === t; }
    _maju() { if (!this._diAkhir()) this.saat_ini++; return this._sebelumnya(); }
    _diAkhir() { return this._intip().tipe === TipeToken.ADS; }
    _intip() { return this.tokens[this.saat_ini]; }
    _sebelumnya() { return this.tokens[this.saat_ini - 1]; }
    _kesalahan(t, p) { this.daftar_kesalahan.push({ token: t, pesan: p }); return new PenguraiKesalahan(p); }
    _sinkronisasi() {
        this._maju();
        while (!this._diAkhir()) {
            if ([TipeToken.AKHIR_BARIS, TipeToken.TITIK_KOMA].includes(this._sebelumnya().tipe)) return;
            if ([TipeToken.FUNGSI, TipeToken.BIAR, TipeToken.TETAP, TipeToken.JIKA, TipeToken.SELAMA, TipeToken.KEMBALIKAN, TipeToken.TULIS].includes(this._intip().tipe)) return;
            this._maju();
        }
    }
}

module.exports = { Pengurai };
