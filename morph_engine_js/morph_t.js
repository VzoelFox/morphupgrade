// transpiler/js/morph_t.js
// Fondasi untuk Tipe Token dan struktur data Token

const TipeToken = {
    ADS: 'ADS', TEKS: 'TEKS', ANGKA: 'ANGKA', NAMA: 'NAMA',
    TAMBAH: 'TAMBAH', KURANG: 'KURANG', KALI: 'KALI', BAGI: 'BAGI', PANGKAT: 'PANGKAT', MODULO: 'MODULO',
    SAMA_DENGAN: 'SAMA_DENGAN', TIDAK_SAMA: 'TIDAK_SAMA', KURANG_DARI: 'KURANG_DARI', LEBIH_DARI: 'LEBIH_DARI', KURANG_SAMA: 'KURANG_SAMA', LEBIH_SAMA: 'LEBIH_SAMA',
    DAN: 'DAN', ATAU: 'ATAU', TIDAK: 'TIDAK',
    TITIK_KOMA: 'TITIK_KOMA', KOMA: 'KOMA', TITIK_DUA: 'TITIK_DUA', TITIK: 'TITIK', TANDA_PANAH: 'TANDA_PANAH',
    KURUNG_BUKA: 'KURUNG_BUKA', KURUNG_TUTUP: 'KURUNG_TUTUP', KURAWAL_BUKA: 'KURAWAL_BUKA', KURAWAL_TUTUP: 'KURAWAL_TUTUP', SIKU_BUKA: 'SIKU_BUKA', SIKU_TUTUP: 'SIKU_TUTUP',
    SAMADENGAN: 'SAMADENGAN',
    BIAR: 'BIAR', TETAP: 'TETAP', UBAH: 'UBAH', FUNGSI: 'FUNGSI', KEMBALIKAN: 'KEMBALIKAN', JIKA: 'JIKA', MAKA: 'MAKA', LAIN: 'LAIN', LAIN_JIKA: 'LAIN_JIKA', SELAMA: 'SELAMA', PILIH: 'PILIH', KETIKA: 'KETIKA', LAINNYA: 'LAINNYA', AKHIR: 'AKHIR', AMBIL: 'AMBIL', TULIS: 'TULIS', PINJAM: 'PINJAM',
    BENAR: 'BENAR', SALAH: 'SALAH', NIL: 'NIL',
    AKHIR_BARIS: 'AKHIR_BARIS', TIDAK_DIKENAL: 'TIDAK_DIKENAL',
};

class Token {
    constructor(tipe, nilai, baris, kolom) {
        this.tipe = tipe; this.nilai = nilai; this.baris = baris; this.kolom = kolom;
    }
}

const KATA_KUNCI = {
    "biar": TipeToken.BIAR, "tetap": TipeToken.TETAP, "ubah": TipeToken.UBAH, "fungsi": TipeToken.FUNGSI, "kembalikan": TipeToken.KEMBALIKAN,
    "jika": TipeToken.JIKA, "maka": TipeToken.MAKA, "lain": TipeToken.LAIN, "lainjika": TipeToken.LAIN_JIKA, "selama": TipeToken.SELAMA,
    "pilih": TipeToken.PILIH, "ketika": TipeToken.KETIKA, "lainnya": TipeToken.LAINNYA, "akhir": TipeToken.AKHIR, "ambil": TipeToken.AMBIL,
    "tulis": TipeToken.TULIS, "pinjam": TipeToken.PINjam, "benar": TipeToken.BENAR, "salah": TipeToken.SALAH, "nil": TipeToken.NIL,
    "dan": TipeToken.DAN, "atau": TipeToken.ATAU, "tidak": TipeToken.TIDAK,
};

module.exports = { TipeToken, Token, KATA_KUNCI };
