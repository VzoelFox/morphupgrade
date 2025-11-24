# Greenfield: Morph Self-Hosted Compiler

Direktori ini berisi implementasi compiler bahasa Morph yang ditulis sepenuhnya menggunakan bahasa Morph itu sendiri ("Pure Morph").

## Tujuan
Tujuan utama dari proyek Greenfield adalah mencapai *self-hosting*, di mana compiler Morph dapat mengkompilasi kode sumbernya sendiri tanpa bergantung pada implementasi Python (`transisi`/`ivm`).

## Struktur
*   `morph.fox`: Titik masuk utama (Entry Point) untuk compiler.
*   `lx_morph.fox`: Lexer (Analisis Leksikal) yang mengubah kode sumber menjadi token.
*   `crusher.fox`: Parser (Analisis Sintaksis) yang mengubah token menjadi Abstract Syntax Tree (AST).
*   `absolute_syntax_morph.fox`: Definisi struktur data AST.
*   `morph_t.fox`: Definisi tipe token dan konstanta.

## Cara Menjalankan (Bootstrap)
Saat ini, kode Greenfield dijalankan menggunakan Bootstrap VM (Python) yang ada di direktori `ivm/`.

```bash
# Contoh menjalankan compiler greenfield untuk mengkompilasi script lain
# (Memerlukan script wrapper Python atau Morph saat ini)
```

## Status
*   [x] Lexer (`lx_morph.fox`) - Porting selesai dan terverifikasi.
*   [x] Parser (`crusher.fox`) - Porting selesai dan terverifikasi.
*   [ ] Translator/Compiler - Belum diporting.
*   [ ] Standard Library (`cotc`) - Masih menggunakan stub/python-bridge.
