#include <iostream>
#include <vector>
#include <string>
#include <cstdlib>
#include "fox_vm.hpp"

// Helper untuk mengecek string equality
bool eq(const std::string& a, const std::string& b) {
    return a == b;
}

void show_help() {
    std::cout << "Morph CLI (Micro Driver v0.2)" << std::endl;
    std::cout << "Penggunaan:" << std::endl;
    std::cout << "  morph run morph make \"<file.fox>\"" << std::endl;
    std::cout << "  morph install \"star spawn <package.fall>\"" << std::endl;
}

// Fungsi eksekusi shim (Python Compiler)
void execute_compile_shim(const std::string& target_file) {
    std::string safe_target = "\"" + target_file + "\"";
    // Build command: python3 -m ivm.main greenfield/morph.fox build <target>
    // Ini menghasilkan .mvm
    std::string cmd = "python3 -m ivm.main greenfield/morph.fox build " + safe_target;

    std::cout << "[Driver] Mengompilasi via Morph Self-Host..." << std::endl;
    int ret = std::system(cmd.c_str());
    if (ret != 0) {
        std::cerr << "[Driver] Kompilasi gagal." << std::endl;
        exit(1);
    }
}

void execute_vm(const std::string& target_file) {
    // Jalankan file .mvm menggunakan C++ Native VM
    FoxVM vm;
    vm.load_and_run(target_file);
}

int main(int argc, char* argv[]) {
    std::vector<std::string> args;
    for (int i = 1; i < argc; ++i) {
        args.push_back(std::string(argv[i]));
    }

    if (args.empty()) {
        show_help();
        return 0;
    }

    std::string command = args[0];

    if (eq(command, "run")) {
        if (args.size() >= 4 && eq(args[1], "morph") && eq(args[2], "make")) {
            std::string target = args[3];

            // Cek ekstensi
            if (target.size() > 4 && target.substr(target.size() - 4) == ".mvm") {
                // Direct execute .mvm
                execute_vm(target);
            } else {
                // Compile source (.fox) -> .mvm, then execute
                execute_compile_shim(target);

                // Construct output filename
                std::string mvm_file = target + ".mvm";
                execute_vm(mvm_file);
            }
        } else {
            std::cerr << "[Driver] Sintaks salah." << std::endl;
            return 1;
        }
    }
    else if (eq(command, "install")) {
        std::cout << "[Driver] Fitur install belum tersedia." << std::endl;
    }
    else {
        show_help();
        return 1;
    }

    return 0;
}
