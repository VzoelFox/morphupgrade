// transpiler/js/Morph.js
const fs = require('fs');
const readline = require('readline');
const { Leksikal } = require('./lx.js');
const { Pengurai } = require('./crusher.js');
const { Penerjemah } = require('./translator.js');

class Morph {
    constructor() { this.penerjemah = new Penerjemah(); this.adaKesalahan = false; }
    jalankanFile(p) {
        try {
            const s = fs.readFileSync(p, 'utf8');
            this._jalankan(s);
            if (this.adaKesalahan) process.exit(65);
        } catch (e) {
            if (e.code === 'ENOENT') { console.error(`Kesalahan: File tidak ditemukan di '${p}'`); process.exit(1); }
            else throw e;
        }
    }
    jalankanPrompt() {
        const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
        console.log("Selamat datang di MORPH.js v1.0\nKetik 'keluar()' untuk berhenti.");
        const prompt = () => {
            rl.question('> ', (b) => {
                if (b.toLowerCase() === 'keluar()') { rl.close(); return; }
                this._jalankan(b);
                this.adaKesalahan = false;
                prompt();
            });
        };
        prompt();
        rl.on('close', () => { console.log('Sampai jumpa!'); process.exit(0); });
    }
    _jalankan(s) {
        const l = new Leksikal(s);
        const { tokens, errors: le } = l.buatToken();
        if (le.length > 0) {
            le.forEach(e => console.error(`[Baris ${e.baris}] Kesalahan Leksikal: ${e.pesan}`));
            this.adaKesalahan = true; return;
        }
        const p = new Pengurai(tokens);
        const prog = p.urai();
        if (p.daftar_kesalahan.length > 0) {
            p.daftar_kesalahan.forEach(e => {
                const { token: t, pesan: ps } = e;
                if (t.tipe === 'ADS') console.error(`[Baris ${t.baris}] Kesalahan di akhir: ${ps}`);
                else console.error(`[Baris ${t.baris}] Kesalahan deket '${t.nilai}': ${ps}`);
            });
            this.adaKesalahan = true; return;
        }
        if (prog) this.penerjemah.terjemahkan(prog);
    }
}

if (require.main === module) {
    const args = process.argv.slice(2);
    const app = new Morph();
    if (args.length > 1) { console.log("Penggunaan: node Morph.js [nama_file.fox]"); process.exit(64); }
    else if (args.length === 1) app.jalankanFile(args[0]);
    else app.jalankanPrompt();
}

module.exports = { Morph };
