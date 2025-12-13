#include "fox_vm.hpp"
#include <iostream>
#include <iomanip>
#include <chrono>
#include <thread>
#include <cmath>

// --- Helper Constructors ---
FoxObjectPtr make_nil() { return std::make_shared<FoxObject>(ObjectType::NIL); }
FoxObjectPtr make_bool(bool v) {
    auto o = std::make_shared<FoxObject>(ObjectType::BOOLEAN);
    o->bool_val = v;
    return o;
}
FoxObjectPtr make_int(int64_t v) {
    auto o = std::make_shared<FoxObject>(ObjectType::INTEGER);
    o->int_val = v;
    return o;
}
FoxObjectPtr make_float(double v) {
    auto o = std::make_shared<FoxObject>(ObjectType::FLOAT);
    o->float_val = v;
    return o;
}
FoxObjectPtr make_str(std::string s) {
    auto o = std::make_shared<FoxObject>(ObjectType::STRING);
    o->str_val = s;
    return o;
}

// --- Logic Helpers ---
bool is_truthy(FoxObjectPtr o) {
    switch(o->type) {
        case ObjectType::NIL: return false;
        case ObjectType::BOOLEAN: return o->bool_val;
        case ObjectType::INTEGER: return o->int_val != 0;
        case ObjectType::FLOAT: return o->float_val != 0.0;
        case ObjectType::STRING: return !o->str_val.empty();
        default: return true;
    }
}

bool check_equality(FoxObjectPtr a, FoxObjectPtr b) {
    if (a->type != b->type) {
        if ((a->type == ObjectType::INTEGER || a->type == ObjectType::FLOAT) &&
            (b->type == ObjectType::INTEGER || b->type == ObjectType::FLOAT)) {
             double val_a = (a->type == ObjectType::INTEGER) ? (double)a->int_val : a->float_val;
             double val_b = (b->type == ObjectType::INTEGER) ? (double)b->int_val : b->float_val;
             return val_a == val_b;
        }
        return false;
    }
    switch(a->type) {
        case ObjectType::NIL: return true;
        case ObjectType::BOOLEAN: return a->bool_val == b->bool_val;
        case ObjectType::INTEGER: return a->int_val == b->int_val;
        case ObjectType::FLOAT: return a->float_val == b->float_val;
        case ObjectType::STRING: return a->str_val == b->str_val;
        default: return a == b;
    }
}

bool check_less(FoxObjectPtr a, FoxObjectPtr b) {
    if ((a->type == ObjectType::INTEGER || a->type == ObjectType::FLOAT) &&
        (b->type == ObjectType::INTEGER || b->type == ObjectType::FLOAT)) {
            double val_a = (a->type == ObjectType::INTEGER) ? (double)a->int_val : a->float_val;
            double val_b = (b->type == ObjectType::INTEGER) ? (double)b->int_val : b->float_val;
            return val_a < val_b;
    }
    if (a->type == ObjectType::STRING && b->type == ObjectType::STRING) {
        return a->str_val < b->str_val;
    }
    return false;
}

// --- VM Implementation ---

FoxVM::FoxVM() {
    setup_builtins();
}

void FoxVM::setup_builtins() {
    globals["tulis"] = make_str("<native_tulis>");
    globals["teks"] = make_str("<native_teks>");
}

// --- Binary Reader ---

uint8_t FoxVM::read_byte(std::ifstream& f) {
    char b;
    f.read(&b, 1);
    return static_cast<uint8_t>(b);
}

uint32_t FoxVM::read_int(std::ifstream& f) {
    uint32_t val = 0;
    f.read(reinterpret_cast<char*>(&val), 4);
    return val;
}

double FoxVM::read_double(std::ifstream& f) {
    double val;
    f.read(reinterpret_cast<char*>(&val), 8);
    return val;
}

std::string FoxVM::read_string(std::ifstream& f) {
    uint32_t len = read_int(f);
    if (len == 0) return "";
    std::string s(len, '\0');
    f.read(&s[0], len);
    return s;
}

FoxObjectPtr FoxVM::read_code_object(std::ifstream& f) {
    auto co = std::make_shared<CodeObject>();
    co->name = read_string(f);

    uint8_t arg_count = read_byte(f);
    for(int i=0; i<arg_count; i++) {
        std::string arg_name = read_string(f);
        co->arg_names.push_back(arg_name);
    }

    uint32_t const_count = read_int(f);
    for(uint32_t i=0; i<const_count; i++) {
        co->constants.push_back(read_object(f));
    }

    uint32_t instr_count = read_int(f);
    for(uint32_t i=0; i<instr_count; i++) {
        uint8_t op = read_byte(f);
        FoxObjectPtr arg = read_object(f);
        co->instructions.push_back({op, arg});
    }

    auto obj = std::make_shared<FoxObject>(ObjectType::CODE_OBJECT);
    obj->code_val = co;
    return obj;
}

FoxObjectPtr FoxVM::read_object(std::ifstream& f) {
    uint8_t tag = read_byte(f);

    switch(tag) {
        case 1: return make_nil();
        case 2: {
            uint8_t val = read_byte(f);
            return make_bool(val == 1);
        }
        case 3: {
            uint32_t val = read_int(f);
            return make_int(val);
        }
        case 4: { // Float
            double val = read_double(f);
            return make_float(val);
        }
        case 5: {
            std::string s = read_string(f);
            return make_str(s);
        }
        case 7: {
            return read_code_object(f);
        }
        default:
            std::cerr << "[VM] Tag " << (int)tag << " belum didukung sepenuhnya." << std::endl;
            return make_nil();
    }
}

void FoxVM::load_and_run(const std::string& filepath) {
    std::ifstream f(filepath, std::ios::binary);
    if (!f.is_open()) {
        std::cerr << "[VM] Gagal membuka file: " << filepath << std::endl;
        return;
    }

    char magic[10];
    f.read(magic, 10);
    std::string magic_str(magic, 10);
    if (magic_str != "VZOEL FOXS") {
        std::cerr << "[VM] Magic bytes invalid! Bukan file .mvm yang valid." << std::endl;
        return;
    }

    f.ignore(6);
    FoxObjectPtr root = read_object(f);

    if (root->type == ObjectType::CODE_OBJECT) {
        std::cout << "[VM] Booting Morph Kernel (C++ Native)..." << std::endl;
        run_frame(root->code_val);
    } else {
        std::cerr << "[VM] Root object bukan CodeObject!" << std::endl;
    }
}

void FoxVM::run_frame(std::shared_ptr<CodeObject> code) {
    int pc = 0;
    while (pc < code->instructions.size()) {
        auto& inst = code->instructions[pc];
        uint8_t op = inst.first;
        FoxObjectPtr arg = inst.second;

        switch(op) {
            case 1: // PUSH_CONST
                stack.push_back(arg);
                break;

            case 2: // POP
                if (!stack.empty()) stack.pop_back();
                break;

            case 4: // ADD
            {
                auto b = stack.back(); stack.pop_back();
                auto a = stack.back(); stack.pop_back();

                if (a->type == ObjectType::STRING && b->type == ObjectType::STRING) {
                    stack.push_back(make_str(a->str_val + b->str_val));
                }
                else if ((a->type == ObjectType::INTEGER || a->type == ObjectType::FLOAT) &&
                         (b->type == ObjectType::INTEGER || b->type == ObjectType::FLOAT)) {
                    double val_a = (a->type == ObjectType::INTEGER) ? (double)a->int_val : a->float_val;
                    double val_b = (b->type == ObjectType::INTEGER) ? (double)b->int_val : b->float_val;
                    bool res_is_int = (a->type == ObjectType::INTEGER && b->type == ObjectType::INTEGER);

                    if (res_is_int) stack.push_back(make_int((int64_t)(val_a + val_b)));
                    else stack.push_back(make_float(val_a + val_b));
                }
                else {
                    stack.push_back(make_nil());
                }
            }
            break;

            case 5: // SUB
            {
                auto b = stack.back(); stack.pop_back();
                auto a = stack.back(); stack.pop_back();
                if ((a->type == ObjectType::INTEGER || a->type == ObjectType::FLOAT) &&
                    (b->type == ObjectType::INTEGER || b->type == ObjectType::FLOAT)) {
                    double val_a = (a->type == ObjectType::INTEGER) ? (double)a->int_val : a->float_val;
                    double val_b = (b->type == ObjectType::INTEGER) ? (double)b->int_val : b->float_val;
                    bool res_is_int = (a->type == ObjectType::INTEGER && b->type == ObjectType::INTEGER);

                    if (res_is_int) stack.push_back(make_int((int64_t)(val_a - val_b)));
                    else stack.push_back(make_float(val_a - val_b));
                } else {
                    stack.push_back(make_nil());
                }
            }
            break;

            case 6: // MUL
            {
                auto b = stack.back(); stack.pop_back();
                auto a = stack.back(); stack.pop_back();
                if ((a->type == ObjectType::INTEGER || a->type == ObjectType::FLOAT) &&
                    (b->type == ObjectType::INTEGER || b->type == ObjectType::FLOAT)) {
                    double val_a = (a->type == ObjectType::INTEGER) ? (double)a->int_val : a->float_val;
                    double val_b = (b->type == ObjectType::INTEGER) ? (double)b->int_val : b->float_val;
                    bool res_is_int = (a->type == ObjectType::INTEGER && b->type == ObjectType::INTEGER);

                    if (res_is_int) stack.push_back(make_int((int64_t)(val_a * val_b)));
                    else stack.push_back(make_float(val_a * val_b));
                } else {
                    stack.push_back(make_nil());
                }
            }
            break;

            case 7: // DIV
            {
                auto b = stack.back(); stack.pop_back();
                auto a = stack.back(); stack.pop_back();
                if ((a->type == ObjectType::INTEGER || a->type == ObjectType::FLOAT) &&
                    (b->type == ObjectType::INTEGER || b->type == ObjectType::FLOAT)) {
                    double val_a = (a->type == ObjectType::INTEGER) ? (double)a->int_val : a->float_val;
                    double val_b = (b->type == ObjectType::INTEGER) ? (double)b->int_val : b->float_val;

                    if (val_b == 0) {
                        std::cerr << "Division by zero" << std::endl;
                        stack.push_back(make_nil());
                    } else {
                        stack.push_back(make_float(val_a / val_b));
                    }
                } else {
                    stack.push_back(make_nil());
                }
            }
            break;

            case 8: // MOD
            {
                auto b = stack.back(); stack.pop_back();
                auto a = stack.back(); stack.pop_back();
                if ((a->type == ObjectType::INTEGER || a->type == ObjectType::FLOAT) &&
                    (b->type == ObjectType::INTEGER || b->type == ObjectType::FLOAT)) {
                    double val_a = (a->type == ObjectType::INTEGER) ? (double)a->int_val : a->float_val;
                    double val_b = (b->type == ObjectType::INTEGER) ? (double)b->int_val : b->float_val;
                    bool res_is_int = (a->type == ObjectType::INTEGER && b->type == ObjectType::INTEGER);

                    if (res_is_int && val_b != 0) stack.push_back(make_int((int64_t)val_a % (int64_t)val_b));
                    else stack.push_back(make_float(std::fmod(val_a, val_b)));
                } else {
                    stack.push_back(make_nil());
                }
            }
            break;

            case 9: // EQ
            {
                auto b = stack.back(); stack.pop_back();
                auto a = stack.back(); stack.pop_back();
                stack.push_back(make_bool(check_equality(a, b)));
            }
            break;

            case 10: // NEQ
            {
                auto b = stack.back(); stack.pop_back();
                auto a = stack.back(); stack.pop_back();
                stack.push_back(make_bool(!check_equality(a, b)));
            }
            break;

            case 11: // GT
            {
                auto b = stack.back(); stack.pop_back();
                auto a = stack.back(); stack.pop_back();
                stack.push_back(make_bool(check_less(b, a)));
            }
            break;

            case 12: // LT
            {
                auto b = stack.back(); stack.pop_back();
                auto a = stack.back(); stack.pop_back();
                stack.push_back(make_bool(check_less(a, b)));
            }
            break;

            case 13: // GTE
            {
                auto b = stack.back(); stack.pop_back();
                auto a = stack.back(); stack.pop_back();
                stack.push_back(make_bool(!check_less(a, b)));
            }
            break;

            case 14: // LTE
            {
                auto b = stack.back(); stack.pop_back();
                auto a = stack.back(); stack.pop_back();
                stack.push_back(make_bool(!check_less(b, a)));
            }
            break;

            case 15: // NOT
            {
                auto val = stack.back(); stack.pop_back();
                stack.push_back(make_bool(!is_truthy(val)));
            }
            break;

            case 16: // AND
            {
                auto b = stack.back(); stack.pop_back();
                auto a = stack.back(); stack.pop_back();
                if (!is_truthy(a)) stack.push_back(a);
                else stack.push_back(b);
            }
            break;

            case 17: // OR
            {
                auto b = stack.back(); stack.pop_back();
                auto a = stack.back(); stack.pop_back();
                if (is_truthy(a)) stack.push_back(a);
                else stack.push_back(b);
            }
            break;

            case 23: // LOAD_VAR
                {
                    std::string name = arg->str_val;
                    if (globals.count(name)) {
                        stack.push_back(globals[name]);
                    } else {
                        stack.push_back(make_nil());
                    }
                }
                break;

            case 24: // STORE_VAR
                {
                    std::string name = arg->str_val;
                    globals[name] = stack.back();
                    stack.pop_back();
                }
                break;

            case 44: // JMP
                pc = (int)arg->int_val;
                continue;

            case 45: // JMP_IF_FALSE
            {
                auto val = stack.back(); stack.pop_back();
                if (!is_truthy(val)) {
                    pc = (int)arg->int_val;
                    continue;
                }
            }
            break;

            case 46: // JMP_IF_TRUE
            {
                auto val = stack.back(); stack.pop_back();
                if (is_truthy(val)) {
                    pc = (int)arg->int_val;
                    continue;
                }
            }
            break;

            case 53: // PRINT
                {
                    int count = arg->int_val;
                    std::vector<FoxObjectPtr> print_args;
                    for(int i=0; i<count; i++) {
                        print_args.push_back(stack.back());
                        stack.pop_back();
                    }
                    for(int i=count-1; i>=0; i--) {
                        builtin_tulis(print_args[i]);
                    }
                }
                break;

            case 79: // SYS_TIME
                {
                    auto now = std::chrono::system_clock::now();
                    auto duration = now.time_since_epoch();
                    double seconds = std::chrono::duration<double>(duration).count();
                    stack.push_back(make_float(seconds));
                }
                break;

            case 80: // SYS_SLEEP
                {
                    auto val = stack.back(); stack.pop_back();
                    double duration = 0.0;
                    if (val->type == ObjectType::INTEGER) duration = (double)val->int_val;
                    else if (val->type == ObjectType::FLOAT) duration = val->float_val;

                    std::this_thread::sleep_for(std::chrono::duration<double>(duration));
                    stack.push_back(make_nil());
                }
                break;

            case 81: // SYS_PLATFORM
                {
                    std::string p = "unknown";
                    #if defined(__EMSCRIPTEN__)
                    p = "web";
                    #elif defined(__ANDROID__)
                    p = "android";
                    #elif defined(_WIN32)
                    p = "win32";
                    #elif defined(__APPLE__)
                    p = "darwin";
                    #elif defined(__linux__)
                    p = "linux";
                    #endif
                    stack.push_back(make_str(p));
                }
                break;

            case 47: // CALL
                {
                    int arg_count = arg->int_val;
                     for(int i=0; i<arg_count; i++) stack.pop_back();
                     stack.pop_back();
                     stack.push_back(make_nil());
                }
                break;

            case 48: // RET
                return;

            default:
                break;
        }
        pc++;
    }
}

void FoxVM::builtin_tulis(FoxObjectPtr arg) {
    if (arg->type == ObjectType::STRING) {
        std::cout << arg->str_val << std::endl;
    } else if (arg->type == ObjectType::INTEGER) {
        std::cout << arg->int_val << std::endl;
    } else if (arg->type == ObjectType::FLOAT) {
        std::cout << arg->float_val << std::endl;
    } else if (arg->type == ObjectType::BOOLEAN) {
        std::cout << (arg->bool_val ? "benar" : "salah") << std::endl;
    } else if (arg->type == ObjectType::NIL) {
        std::cout << "nil" << std::endl;
    } else {
        std::cout << "<object>" << std::endl;
    }
}
