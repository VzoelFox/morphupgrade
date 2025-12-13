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
#include <functional>

enum class ObjectType {
    NIL, BOOLEAN, INTEGER, FLOAT, STRING, LIST, DICT, CODE_OBJECT,
    FUNCTION, CLASS, INSTANCE, BOUND_METHOD, CELL, NATIVE_FUNCTION,
    GENERATOR
};

struct FoxObject;
using FoxObjectPtr = std::shared_ptr<FoxObject>;

class FoxVM; // Forward decl

// Native function callback signature
using NativeFunc = std::function<void(FoxVM&, int)>;

struct CodeObject {
    std::string name;
    std::vector<std::string> arg_names;
    std::vector<FoxObjectPtr> constants;
    std::vector<std::pair<uint8_t, FoxObjectPtr>> instructions;
    std::vector<std::string> free_vars;
    std::vector<std::string> cell_vars;
};

struct TryBlock {
    int handler_pc;
    size_t stack_depth;
};

struct Frame {
    std::shared_ptr<CodeObject> code;
    size_t pc = 0;
    std::vector<FoxObjectPtr> stack;
    std::map<std::string, FoxObjectPtr> locals;
    std::map<std::string, FoxObjectPtr> cells;
    std::vector<TryBlock> try_stack;
    bool is_init = false;
    FoxObjectPtr init_instance;

    // Module Support
    bool is_module = false;
    std::string module_name;

    Frame(std::shared_ptr<CodeObject> c) : code(c), pc(0) {}
};

struct FoxObject {
    ObjectType type;
    int64_t int_val = 0;
    double float_val = 0.0;
    bool bool_val = false;
    std::string str_val;
    std::vector<FoxObjectPtr> list_val;
    std::map<std::string, FoxObjectPtr> dict_val;
    std::shared_ptr<CodeObject> code_val;
    std::map<std::string, FoxObjectPtr> closure_cells;
    std::string name_val;
    std::map<std::string, FoxObjectPtr> methods;
    FoxObjectPtr super_class;
    FoxObjectPtr klass;
    std::map<std::string, FoxObjectPtr> properties;
    FoxObjectPtr instance;
    FoxObjectPtr method;
    FoxObjectPtr cell_value;
    std::shared_ptr<Frame> gen_frame;
    bool gen_finished = false;

    FoxObject(ObjectType t) : type(t) {}
};

// Exception for Yield Control Flow
struct VMYieldException {};

class FoxVM {
public:
    FoxVM();
    void load_and_run(const std::string& filepath);

    // Helpers for Native Functions
    void push_stack(FoxObjectPtr obj);
    FoxObjectPtr pop_stack();
    FoxObjectPtr peek_stack(int offset = 0);
    FoxObjectPtr make_native_func(NativeFunc f);

    // Exposed for sys_yield
    std::vector<Frame> call_stack;
    void pop_frame();

    // Exposed for Import
    std::map<std::string, FoxObjectPtr> modules;

private:
    std::map<std::string, FoxObjectPtr> globals;
    std::map<std::string, FoxObjectPtr> native_modules;

    FoxObjectPtr read_object(std::ifstream& f);
    FoxObjectPtr read_code_object(std::ifstream& f);
    uint32_t read_int(std::ifstream& f);
    double read_double(std::ifstream& f);
    std::string read_string(std::ifstream& f);
    uint8_t read_byte(std::ifstream& f);

    void run();
    void push_frame(std::shared_ptr<CodeObject> code, std::vector<FoxObjectPtr> args, FoxObjectPtr func_obj = nullptr);
    void handle_exception(FoxObjectPtr exc);

    void setup_builtins();
    void setup_backend();
    void builtin_tulis(FoxObjectPtr arg);
};

#endif
