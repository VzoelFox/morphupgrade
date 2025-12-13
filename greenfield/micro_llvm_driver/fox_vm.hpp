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

enum class ObjectType {
    NIL, BOOLEAN, INTEGER, FLOAT, STRING, LIST, DICT, CODE_OBJECT,
    FUNCTION, CLASS, INSTANCE, BOUND_METHOD, CELL
};

struct FoxObject;
using FoxObjectPtr = std::shared_ptr<FoxObject>;

struct CodeObject {
    std::string name;
    std::vector<std::string> arg_names;
    std::vector<FoxObjectPtr> constants;
    std::vector<std::pair<uint8_t, FoxObjectPtr>> instructions;

    // Meta for closure
    std::vector<std::string> free_vars; // Captured from parent
    std::vector<std::string> cell_vars; // Captured by children
};

struct FoxObject {
    ObjectType type;

    // Primitives
    int64_t int_val = 0;
    double float_val = 0.0;
    bool bool_val = false;
    std::string str_val;

    // Complex
    std::vector<FoxObjectPtr> list_val;
    std::map<std::string, FoxObjectPtr> dict_val;

    // Code
    std::shared_ptr<CodeObject> code_val;

    // Function / Closure
    std::map<std::string, FoxObjectPtr> closure_cells; // name -> Cell

    // Class
    std::string name_val;
    std::map<std::string, FoxObjectPtr> methods;
    FoxObjectPtr super_class;

    // Instance
    FoxObjectPtr klass;
    std::map<std::string, FoxObjectPtr> properties;

    // Bound Method
    FoxObjectPtr instance;
    FoxObjectPtr method;

    // Cell
    FoxObjectPtr cell_value;

    FoxObject(ObjectType t) : type(t) {}
};

struct Frame {
    std::shared_ptr<CodeObject> code;
    int pc = 0;
    std::vector<FoxObjectPtr> stack;
    std::map<std::string, FoxObjectPtr> locals;
    std::map<std::string, FoxObjectPtr> cells; // name -> Cell Object (shared ptr)

    // Init Flag
    bool is_init = false;
    FoxObjectPtr init_instance;

    Frame(std::shared_ptr<CodeObject> c) : code(c), pc(0) {}
};

class FoxVM {
public:
    FoxVM();
    void load_and_run(const std::string& filepath);

private:
    std::vector<Frame> call_stack;
    std::map<std::string, FoxObjectPtr> globals;

    // Deserialisasi
    FoxObjectPtr read_object(std::ifstream& f);
    FoxObjectPtr read_code_object(std::ifstream& f);
    uint32_t read_int(std::ifstream& f);
    double read_double(std::ifstream& f);
    std::string read_string(std::ifstream& f);
    uint8_t read_byte(std::ifstream& f);

    // Eksekusi
    void run();
    void push_frame(std::shared_ptr<CodeObject> code, std::vector<FoxObjectPtr> args, FoxObjectPtr func_obj = nullptr);
    void pop_frame();

    // Builtins
    void setup_builtins();
    void builtin_tulis(FoxObjectPtr arg);
};

#endif
