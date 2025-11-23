"""
SKELETON SELF-HOSTING: INTERPRETER (EVALUATOR)
"""

MORPH_SOURCE = r"""
# core/translator.fox
# Interpreter Morph Lengkap (Tree-walking evaluator)

ambil_semua "core/ast.fox" sebagai AST
ambil_semua "core/object.fox" sebagai OBJ
ambil_semua "core/env.fox" sebagai ENV

biar NULL = OBJ.Null()
biar TRUE = OBJ.Boolean(benar)
biar FALSE = OBJ.Boolean(salah)

kelas Evaluator maka

    fungsi evaluasi(node, env) maka
        pilih tipe(node)
        # --- Program ---
        ketika AST.Program maka
            kembali ini.eval_program(node, env)

        # --- Pernyataan ---
        ketika AST.PernyataanBiar maka
            biar val = ini.evaluasi(node.nilai, env)
            jika adl_error(val) maka kembali val akhir
            env.set(node.nama.nilai, val)

        ketika AST.DeklarasiVariabel maka
             biar val = ini.evaluasi(node.nilai, env)
             jika adl_error(val) maka kembali val akhir
             env.set(node.nama.nilai, val)

        ketika AST.Assignment maka
             biar val = ini.evaluasi(node.nilai, env)
             jika adl_error(val) maka kembali val akhir
             # Logika assignment kompleks (variabel vs properti vs indeks)
             # Sederhana:
             env.assign(node.target.nama, val)

        ketika AST.PernyataanEkspresi maka
            kembali ini.evaluasi(node.ekspresi, env)

        ketika AST.PernyataanKembalikan maka
            biar val = NULL
            jika node.nilai != nil maka
                val = ini.evaluasi(node.nilai, env)
                jika adl_error(val) maka kembali val akhir
            akhir
            kembali OBJ.ReturnValue(val)

        ketika AST.JikaMaka maka
            kembali ini.eval_jika_maka(node, env)

        ketika AST.Selama maka
            kembali ini.eval_selama(node, env)

        ketika AST.Tulis maka
            biar args = ini.eval_expressions(node.argumen, env)
            jika panjang(args) == 1 dan adl_error(args[0]) maka kembali args[0] akhir
            cetak(args) # Fungsi builtin
            kembali NULL

        # --- Ekspresi ---
        ketika AST.Identitas maka
            kembali ini.eval_identifier(node, env)

        ketika AST.Konstanta maka
            kembali OBJ.dari_native(node.nilai)

        ketika AST.FoxBinary maka
            biar kiri = ini.evaluasi(node.kiri, env)
            jika adl_error(kiri) maka kembali kiri akhir
            biar kanan = ini.evaluasi(node.kanan, env)
            jika adl_error(kanan) maka kembali kanan akhir
            kembali ini.eval_infix(node.op, kiri, kanan)

        ketika AST.FoxUnary maka
            biar kanan = ini.evaluasi(node.kanan, env)
            jika adl_error(kanan) maka kembali kanan akhir
            kembali ini.eval_prefix(node.op, kanan)

        ketika AST.PanggilFungsi maka
            biar fungsi_obj = ini.evaluasi(node.callee, env)
            jika adl_error(fungsi_obj) maka kembali fungsi_obj akhir
            biar args = ini.eval_expressions(node.argumen, env)
            jika panjang(args) == 1 dan adl_error(args[0]) maka kembali args[0] akhir
            kembali ini.terapkan_fungsi(fungsi_obj, args)

        # ... (Node lainnya: Kelas, TryCatch, Jodohkan, dll) ...

        lainnya maka
            kembali error("node tidak dikenal: " + tipe(node))
        akhir
    akhir

    fungsi eval_program(program, env) maka
        biar hasil = NULL
        untuk stmt dalam program.pernyataan maka
            hasil = ini.evaluasi(stmt, env)
            jika tipe(hasil) == OBJ.RETURN_VALUE maka
                kembali hasil.nilai
            lain jika tipe(hasil) == OBJ.ERROR maka
                kembali hasil
            akhir
        akhir
        kembali hasil
    akhir

    fungsi eval_identifier(node, env) maka
        biar val = env.get(node.nama)
        jika val != nil maka
            kembali val
        lain
            kembali error("identifier tidak ditemukan: " + node.nama)
        akhir
    akhir

    fungsi eval_jika_maka(node, env) maka
        biar kondisi = ini.evaluasi(node.kondisi, env)
        jika adl_error(kondisi) maka kembali kondisi akhir

        jika adl_benar(kondisi) maka
            kembali ini.eval_block(node.blok_maka, env)
        lain
            # Cek else-if
            untuk pair dalam node.rantai_lain_jika maka
                biar kond = ini.evaluasi(pair[0], env)
                jika adl_error(kond) maka kembali kond akhir
                jika adl_benar(kond) maka
                    kembali ini.eval_block(pair[1], env)
                akhir
            akhir
            # Cek else
            jika node.blok_lain != nil maka
                kembali ini.eval_block(node.blok_lain, env)
            akhir
        akhir
        kembali NULL
    akhir

    fungsi eval_selama(node, env) maka
        biar hasil = NULL
        selama benar maka
            biar kondisi = ini.evaluasi(node.kondisi, env)
            jika adl_error(kondisi) maka kembali kondisi akhir
            jika tidak adl_benar(kondisi) maka berhenti akhir

            hasil = ini.eval_block(node.badan, env)
            # Handle break/continue/return inside loop if necessary
        akhir
        kembali hasil
    akhir

    fungsi eval_expressions(exps, env) maka
        biar result = []
        untuk e dalam exps maka
            biar evaluated = ini.evaluasi(e, env)
            jika adl_error(evaluated) maka kembali [evaluated] akhir
            result.tambah(evaluated)
        akhir
        kembali result
    akhir

    fungsi terapkan_fungsi(fn, args) maka
        jika tipe(fn) != OBJ.FUNCTION maka
             kembali error("bukan fungsi")
        akhir

        biar extended_env = extend_function_env(fn, args)
        biar evaluated = ini.eval_block(fn.body, extended_env)
        return unwrap_return_value(evaluated)
    akhir

akhir
"""
