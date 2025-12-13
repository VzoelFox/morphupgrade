#ifndef FOX_VM_HPP
#define FOX_VM_HPP

#include <string>
#include <vector>
#include <map>
#include <iostream>
#include <fstream>
#include <variant>
#include <memory>
#include <cstdint>

// --- Tipe Data Dasar ---
enum class ObjectType {
    NIL, BOOLEAN, INTEGER, FLOAT, STRING, LIST, DICT, CODE_OBJECT, FUNCTION
};

struct FoxObject;
using FoxObjectPtr = std::shared_ptr<FoxObject>;

struct CodeObject {
    std::string name;
    std::vector<std::string> arg_names;
    std::vector<FoxObjectPtr> constants;
    std::vector<std::pair<uint8_t, FoxObjectPtr>> instructions;
};

struct FoxObject {
    ObjectType type;

    // Simpan nilai menggunakan std::variant atau union sederhana
    int64_t int_val = 0;
    double float_val = 0.0;
    bool bool_val = false;
    std::string str_val;
    std::vector<FoxObjectPtr> list_val;
    std::map<std::string, FoxObjectPtr> dict_val; // Key string sederhana dulu
    std::shared_ptr<CodeObject> code_val;

    FoxObject(ObjectType t) : type(t) {}
};

// --- VM ---
class FoxVM {
public:
    FoxVM();
    void load_and_run(const std::string& filepath);

private:
    std::vector<FoxObjectPtr> stack;
    std::map<std::string, FoxObjectPtr> globals;

    // Deserialisasi
    FoxObjectPtr read_object(std::ifstream& f);
    FoxObjectPtr read_code_object(std::ifstream& f);
    uint32_t read_int(std::ifstream& f);
    std::string read_string(std::ifstream& f);
    uint8_t read_byte(std::ifstream& f);

    // Eksekusi
    void run_frame(std::shared_ptr<CodeObject> code);

    // Builtins
    void setup_builtins();
    void builtin_tulis(FoxObjectPtr arg);
};

#endif
