# ivm/main.py
import sys
import argparse
from transisi.lx import Leksikal
from transisi.crusher import Pengurai
from ivm.compiler import Compiler
from ivm.vms.standard_vm import StandardVM

def main():
    parser = argparse.ArgumentParser(description="IVM Runner for .fox files")
    parser.add_argument("file", help="The .fox file to execute.")
    parser.add_argument('vm_args', nargs=argparse.REMAINDER, help="Arguments for the script.")
    args = parser.parse_args()

    # Menghapus nama skrip itu sendiri dari daftar argumen jika ada
    script_args = args.vm_args
    if script_args and script_args[0] == '--':
        script_args = script_args[1:]

    # Masukkan nama script sebagai argumen ke-0 (Standar argv)
    script_args = [args.file] + script_args

    # Cek apakah file binary .mvm
    if args.file.endswith('.mvm'):
        try:
            vm = StandardVM(script_args=script_args)
            # VM load_module sudah punya logika read binary .mvm
            # Tapi kita perlu load sebagai *main script*.
            # load_module mengembalikan globals dict.
            # Kita perlu cara agar VM mengeksekusinya sebagai main.

            # Cara alternatif: Baca manual, deserialisasi, lalu vm.load(code_obj)
            with open(args.file, 'rb') as f:
                binary_data = f.read()

            if binary_data[:10] != b"VZOEL FOXS":
                print(f"Error: File '{args.file}' bukan format Morph yang valid (Magic Header mismatch).", file=sys.stderr)
                sys.exit(1)

            payload = binary_data[16:]
            from ivm.core.deserializer import deserialize_code_object
            code_obj = deserialize_code_object(payload, filename=args.file)

            # Load dan jalankan level modul
            vm.load(code_obj)
            vm.run()

            # Pasca-run: Cek apakah ada fungsi 'utama' di globals, lalu jalankan jika ada
            if "utama" in vm.globals:
                utama_func = vm.globals["utama"]
                vm.call_function_internal(utama_func, [])
                vm.run()

        except Exception as e:
            import traceback
            print(f"\nError running binary file:", file=sys.stderr)
            traceback.print_exc()
            sys.exit(1)

        return

    # Text Source Path (.fox)
    try:
        with open(args.file, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        lexer = Leksikal(source, nama_file=args.file)
        tokens, errors = lexer.buat_token()
        if errors:
            # TODO: Gunakan error formatter yang lebih baik
            print("Lexer Errors:", file=sys.stderr)
            for err in errors:
                print(err, file=sys.stderr)
            sys.exit(1)

        parser = Pengurai(tokens)
        ast = parser.urai()
        if not ast:
            print("Parser Errors:", file=sys.stderr)
            # TODO: Gunakan error formatter yang lebih baik
            for err in parser.daftar_kesalahan:
                print(err, file=sys.stderr)
            sys.exit(1)

        compiler = Compiler()
        # Perubahan Penting: is_main_script=False agar compiler tidak hardcode call utama()
        code_obj = compiler.compile(ast, filename=args.file, is_main_script=False)

        # Inisialisasi VM dengan argumen
        vm = StandardVM(script_args=script_args)
        vm.load(code_obj)
        vm.run()

        # Pasca-run: Cek apakah ada fungsi 'utama' di globals, lalu jalankan jika ada
        if "utama" in vm.globals:
            utama_func = vm.globals["utama"]
            vm.call_function_internal(utama_func, [])
            vm.run()

    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
