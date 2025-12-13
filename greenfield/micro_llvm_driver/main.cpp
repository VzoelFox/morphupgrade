#include <iostream>
#include <vector>
#include <string>
#include <cstdlib>

// Helper untuk mengecek string equality
bool eq(const std::string& a, const std::string& b) {
    return a == b;
}

void show_help() {
    std::cout << "Morph CLI (Micro Driver v0.1)" << std::endl;
    std::cout << "Penggunaan:" << std::endl;
    std::cout << "  morph run morph make \"<file.fox>\"" << std::endl;
    std::cout << "  morph install \"star spawn <package.fall>\"" << std::endl;
}

// Fungsi placeholder untuk eksekusi via Python IVM
void execute_shim(const std::string& target_file) {
    // Sanitasi input sederhana (quote) untuk mencegah injeksi shell dasar
    // Idealnya gunakan execvp di masa depan.
    std::string safe_target = "\"" + target_file + "\"";
    std::string cmd = "python3 -m ivm.main " + safe_target;

    std::cout << "[Driver] Menyerahkan kendali ke Kernel (IVM Shim)..." << std::endl;
    int ret = std::system(cmd.c_str());
    if (ret != 0) {
        std::cerr << "[Driver] Eksekusi gagal dengan kode: " << ret << std::endl;
    }
}

// Fungsi placeholder untuk install
void install_shim(const std::string& package_arg) {
    // Parse "star spawn <file>"
    // Expect: "star spawn data.fall"
    std::string marker = "star spawn ";
    size_t pos = package_arg.find(marker);

    if (pos == std::string::npos) {
        std::cerr << "[Driver] Error: Format install salah. Gunakan \"star spawn <file.fall>\"" << std::endl;
        return;
    }

    std::string filename = package_arg.substr(pos + marker.length());
    std::cout << "[Driver] Memanggil Star Spawn untuk paket: " << filename << std::endl;
    std::cout << "[Driver] (Fitur Installer belum diimplementasikan)" << std::endl;
}

int main(int argc, char* argv[]) {
    // Konversi args ke vector string untuk kemudahan
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
        // Expect: run morph make <file>
        if (args.size() >= 4 && eq(args[1], "morph") && eq(args[2], "make")) {
            std::string target = args[3];
            execute_shim(target);
        } else {
            std::cerr << "[Driver] Sintaks salah. Coba: morph run morph make \"file.fox\"" << std::endl;
            return 1;
        }
    }
    else if (eq(command, "install")) {
        // Expect: install "star spawn data.fall"
        if (args.size() >= 2) {
            std::string pkg_arg = args[1];
            install_shim(pkg_arg);
        } else {
            std::cerr << "[Driver] Sintaks salah. Coba: morph install \"star spawn data.fall\"" << std::endl;
            return 1;
        }
    }
    else {
        std::cerr << "[Driver] Perintah tidak dikenal: " << command << std::endl;
        show_help();
        return 1;
    }

    return 0;
}
