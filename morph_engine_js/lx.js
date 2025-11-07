// transpiler/js/lx.js
const { TipeToken, Token, KATA_KUNCI } = require('./morph_t.js');

class Leksikal {
    constructor(s) { this.sumber = s; this.tokens = []; this.awal = 0; this.saat_ini = 0; this.baris = 1; this.kolom = 1; this.daftar_kesalahan = []; }
    buatToken() {
        while (!this._diAkhir()) { this.awal = this.saat_ini; this._pindaiToken(); }
        this.tokens.push(new Token(TipeToken.ADS, '\0', this.baris, this.kolom));
        return { tokens: this.tokens, errors: this.daftar_kesalahan };
    }
    _diAkhir() { return this.saat_ini >= this.sumber.length; }
    _maju() {
        const c = this.sumber.charAt(this.saat_ini++);
        if (c === '\n') { this.baris++; this.kolom = 1; } else { this.kolom++; }
        return c;
    }
    _cocok(d) {
        if (this._diAkhir() || this.sumber.charAt(this.saat_ini) !== d) return false;
        this.saat_ini++; this.kolom++; return true;
    }
    _intip() { return this._diAkhir() ? '\0' : this.sumber.charAt(this.saat_ini); }
    _intipBerikutnya() { return this.saat_ini + 1 >= this.sumber.length ? '\0' : this.sumber.charAt(this.saat_ini + 1); }
    _tambahToken(t, nl = null) {
        const teks = this.sumber.substring(this.awal, this.saat_ini);
        this.tokens.push(new Token(t, nl !== null ? nl : teks, this.baris, this.kolom - teks.length));
    }
    _catatKesalahan(p) { this.daftar_kesalahan.push({ pesan: p, baris: this.baris, kolom: this.kolom }); }
    _pindaiToken() {
        const c = this._maju();
        switch (c) {
            case ' ': case '\r': case '\t': break;
            case '\n': this._tambahToken(TipeToken.AKHIR_BARIS); break;
            case '(': this._tambahToken(TipeToken.KURUNG_BUKA); break;
            case ')': this._tambahToken(TipeToken.KURUNG_TUTUP); break;
            case '{': this._tambahToken(TipeToken.KURAWAL_BUKA); break;
            case '}': this._tambahToken(TipeToken.KURAWAL_TUTUP); break;
            case '[': this._tambahToken(TipeToken.SIKU_BUKA); break;
            case ']': this._tambahToken(TipeToken.SIKU_TUTUP); break;
            case ',': this._tambahToken(TipeToken.KOMA); break;
            case '.': this._tambahToken(TipeToken.TITIK); break;
            case ';': this._tambahToken(TipeToken.TITIK_KOMA); break;
            case ':': this._tambahToken(TipeToken.TITIK_DUA); break;
            case '-': this._tambahToken(TipeToken.KURANG); break;
            case '+': this._tambahToken(TipeToken.TAMBAH); break;
            case '*': this._tambahToken(TipeToken.KALI); break;
            case '/': this._tambahToken(TipeToken.BAGI); break;
            case '^': this._tambahToken(TipeToken.PANGKAT); break;
            case '%': this._tambahToken(TipeToken.MODULO); break;
            case '!': this._tambahToken(this._cocok('=') ? TipeToken.TIDAK_SAMA : TipeToken.TIDAK); break;
            case '=': this._tambahToken(this._cocok('=') ? TipeToken.SAMA_DENGAN : TipeToken.SAMADENGAN); break;
            case '<': this._tambahToken(this._cocok('=') ? TipeToken.KURANG_SAMA : TipeToken.KURANG_DARI); break;
            case '>': this._tambahToken(this._cocok('=') ? TipeToken.LEBIH_SAMA : TipeToken.LEBIH_DARI); break;
            case '#': while (this._intip() !== '\n' && !this._diAkhir()) this._maju(); break;
            case '"': this._teks(); break;
            default:
                if (this._isDigit(c)) this._angka();
                else if (this._isAlpha(c)) this._nama();
                else { this._catatKesalahan(`Karakter '${c}' tidak dikenal.`); this._tambahToken(TipeToken.TIDAK_DIKENAL, c); }
                break;
        }
    }
    _teks() {
        while (this._intip() !== '"' && !this._diAkhir()) this._maju();
        if (this._diAkhir()) { this._catatKesalahan("Teks tidak ditutup."); return; }
        this._maju();
        this._tambahToken(TipeToken.TEKS, this.sumber.substring(this.awal + 1, this.saat_ini - 1));
    }
    _angka() {
        while (this._isDigit(this._intip())) this._maju();
        if (this._intip() === '.' && this._isDigit(this._intipBerikutnya())) {
            this._maju();
            while (this._isDigit(this._intip())) this._maju();
        }
        this._tambahToken(TipeToken.ANGKA, parseFloat(this.sumber.substring(this.awal, this.saat_ini)));
    }
    _nama() {
        while (this._isAlphaNumeric(this._intip())) this._maju();
        const teks = this.sumber.substring(this.awal, this.saat_ini);
        const tipe = KATA_KUNCI[teks] || TipeToken.NAMA;
        if (tipe === TipeToken.BENAR) this._tambahToken(tipe, true);
        else if (tipe === TipeToken.SALAH) this._tambahToken(tipe, false);
        else if (tipe === TipeToken.NIL) this._tambahToken(tipe, null);
        else this._tambahToken(tipe);
    }
    _isDigit(c) { return c >= '0' && c <= '9'; }
    _isAlpha(c) { return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c === '_'; }
    _isAlphaNumeric(c) { return this._isAlpha(c) || this._isDigit(c); }
}

module.exports = { Leksikal };
