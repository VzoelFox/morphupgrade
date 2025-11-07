// transpiler/js/translator.js
const { TipeToken } = require('./morph_t.js');

class KesalahanRuntime extends Error { constructor(t, p) { super(p); this.token = t; } }

class Lingkungan {
    constructor(i = null) { this.nilai = new Map(); this.induk = i; }
    definisi(n, v) { this.nilai.set(n, v); }
    dapatkan(t) {
        if (this.nilai.has(t.nilai)) return this.nilai.get(t.nilai);
        if (this.induk !== null) return this.induk.dapatkan(t);
        throw new KesalahanRuntime(t, `Variabel '${t.nilai}' belum didefinisikan.`);
    }
    tetapkan(t, v) {
        if (this.nilai.has(t.nilai)) { this.nilai.set(t.nilai, v); return; }
        if (this.induk !== null) { this.induk.tetapkan(t, v); return; }
        throw new KesalahanRuntime(t, `Variabel '${t.nilai}' belum didefinisikan.`);
    }
}

class Penerjemah {
    constructor() { this.lingkungan = new Lingkungan(); }
    terjemahkan(p) {
        try { p.daftar_pernyataan.forEach(s => this._eksekusi(s)); }
        catch (e) {
            if (e instanceof KesalahanRuntime) console.error(`[Baris ${e.token.baris}] Kesalahan Runtime: ${e.message}`);
            else throw e;
        }
    }
    _eksekusi(s) { s.terima(this); }
    _evaluasi(e) { return e.terima(this); }

    kunjungiBagian(n) { n.daftar_pernyataan.forEach(s => this._eksekusi(s)); }
    kunjungiPernyataanEkspresi(n) { this._evaluasi(n.ekspresi); }
    kunjungiDeklarasiVariabel(n) {
        let v = null;
        if (n.nilai !== null) v = this._evaluasi(n.nilai);
        this.lingkungan.definisi(n.nama.nilai, v);
    }
    kunjungiTulis(n) { console.log(n.argumen.map(a => this._keString(this._evaluasi(a))).join(' ')); }
    kunjungiAssignment(n) {
        const v = this._evaluasi(n.nilai);
        this.lingkungan.tetapkan(n.nama, v);
        return v;
    }
    kunjungiIdentitas(n) { return this.lingkungan.dapatkan(n.token); }
    kunjungiKonstanta(n) { return n.nilai; }
    kunjungiFoxUnary(n) {
        const k = this._evaluasi(n.kanan);
        switch (n.op.tipe) {
            case TipeToken.KURANG: this._periksaTipeAngka(n.op, k); return -k;
            case TipeToken.TIDAK: return !this._apakahBenar(k);
        }
        return null;
    }
    kunjungiFoxBinary(n) {
        const ki = this._evaluasi(n.kiri);
        const ka = this._evaluasi(n.kanan);
        switch (n.op.tipe) {
            case TipeToken.TAMBAH:
                if (typeof ki === 'number' && typeof ka === 'number') return ki + ka;
                if (typeof ki === 'string' && typeof ka === 'string') return ki + ka;
                throw new KesalahanRuntime(n.op, "Operan harus dua angka atau dua teks.");
            case TipeToken.KURANG: this._periksaTipeAngka(n.op, ki, ka); return ki - ka;
            case TipeToken.KALI: this._periksaTipeAngka(n.op, ki, ka); return ki * ka;
            case TipeToken.BAGI:
                this._periksaTipeAngka(n.op, ki, ka);
                if (ka === 0) throw new KesalahanRuntime(n.op, "Tidak bisa membagi dengan nol.");
                return ki / ka;
            case TipeToken.LEBIH_DARI: this._periksaTipeAngka(n.op, ki, ka); return ki > ka;
            case TipeToken.KURANG_DARI: this._periksaTipeAngka(n.op, ki, ka); return ki < ka;
            case TipeToken.LEBIH_SAMA: this._periksaTipeAngka(n.op, ki, ka); return ki >= ka;
            case TipeToken.KURANG_SAMA: this._periksaTipeAngka(n.op, ki, ka); return ki <= ka;
            case TipeToken.SAMA_DENGAN: return ki === ka;
            case TipeToken.TIDAK_SAMA: return ki !== ka;
        }
        return null;
    }
    _keString(o) {
        if (o === null) return "nil";
        if (typeof o === 'boolean') return o ? "benar" : "salah";
        return String(o);
    }
    _apakahBenar(o) {
        if (o === null) return false;
        if (typeof o === 'boolean') return o;
        return true;
    }
    _periksaTipeAngka(op, ...ops) {
        for (const o of ops) {
            if (typeof o !== 'number') throw new KesalahanRuntime(op, "Operan harus berupa angka.");
        }
    }
}

module.exports = { Penerjemah };
