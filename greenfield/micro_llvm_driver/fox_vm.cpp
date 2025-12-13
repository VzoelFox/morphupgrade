#include "fox_vm.hpp"
#include <iostream>
#include <iomanip>
#include <chrono>
#include <thread>
#include <cmath>
#include <algorithm>

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
FoxObjectPtr make_cell() { return std::make_shared<FoxObject>(ObjectType::CELL); }

// --- Logic Helpers ---
bool is_truthy(FoxObjectPtr o) {
    switch(o->type) {
        case ObjectType::NIL: return false;
        case ObjectType::BOOLEAN: return o->bool_val;
        case ObjectType::INTEGER: return o->int_val != 0;
        case ObjectType::FLOAT: return o->float_val != 0.0;
        case ObjectType::STRING: return !o->str_val.empty();
        case ObjectType::LIST: return !o->list_val.empty();
        case ObjectType::DICT: return !o->dict_val.empty();
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
        case 6: { // List
            uint32_t count = read_int(f);
            auto list = std::make_shared<FoxObject>(ObjectType::LIST);
            for(uint32_t i=0; i<count; i++) {
                list->list_val.push_back(read_object(f));
            }
            return list;
        }
        case 7: {
            return read_code_object(f);
        }
        case 8: { // Dict
            uint32_t count = read_int(f);
            auto dict = std::make_shared<FoxObject>(ObjectType::DICT);
            for(uint32_t i=0; i<count; i++) {
                auto key = read_object(f);
                auto val = read_object(f);
                if(key->type == ObjectType::STRING) {
                    dict->dict_val[key->str_val] = val;
                }
            }
            return dict;
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
        // Push initial frame
        push_frame(root->code_val, {});
        run();
    } else {
        std::cerr << "[VM] Root object bukan CodeObject!" << std::endl;
    }
}

void FoxVM::push_frame(std::shared_ptr<CodeObject> code, std::vector<FoxObjectPtr> args, FoxObjectPtr func_obj) {
    call_stack.emplace_back(code);
    Frame& f = call_stack.back();

    // Init Locals from Args
    for(size_t i=0; i<args.size(); i++) {
        if(i < code->arg_names.size()) {
            f.locals[code->arg_names[i]] = args[i];
        }
    }

    // Init Cells (Create New)
    for(const auto& name : code->cell_vars) {
        f.cells[name] = make_cell();
        // If arg was passed for this cell var, move it
        if (f.locals.count(name)) {
            f.cells[name]->cell_value = f.locals[name];
            f.locals.erase(name);
        }
    }

    // Init Closure (Copy from Func)
    if (func_obj && !func_obj->closure_cells.empty()) {
        for(const auto& name : code->free_vars) {
            if (func_obj->closure_cells.count(name)) {
                f.cells[name] = func_obj->closure_cells[name];
            }
        }
    }
}

void FoxVM::pop_frame() {
    call_stack.pop_back();
}

void FoxVM::run() {
    while(!call_stack.empty()) {
        // Must re-fetch frame ref every iter as stack vector might realloc
        Frame& frame = call_stack.back();

        if (frame.pc >= frame.code->instructions.size()) {
            // Implicit Return Nil
            FoxObjectPtr ret = make_nil();
            bool was_init = frame.is_init;
            FoxObjectPtr instance = frame.init_instance;

            pop_frame();
            if (!call_stack.empty()) {
                if (was_init) call_stack.back().stack.push_back(instance);
                else call_stack.back().stack.push_back(ret);
            }
            continue;
        }

        auto& inst = frame.code->instructions[frame.pc];
        uint8_t op = inst.first;
        FoxObjectPtr arg = inst.second;
        frame.pc++;

        // DEBUG
        // std::cout << "PC:" << frame.pc-1 << " OP:" << (int)op << " Stack:" << frame.stack.size() << std::endl;

        switch(op) {
            case 1: // PUSH_CONST
                frame.stack.push_back(arg);
                break;

            case 2: // POP
                if (!frame.stack.empty()) frame.stack.pop_back();
                break;

            case 4: // ADD
            {
                auto b = frame.stack.back(); frame.stack.pop_back();
                auto a = frame.stack.back(); frame.stack.pop_back();

                if (a->type == ObjectType::STRING && b->type == ObjectType::STRING) {
                    frame.stack.push_back(make_str(a->str_val + b->str_val));
                }
                else if ((a->type == ObjectType::INTEGER || a->type == ObjectType::FLOAT) &&
                         (b->type == ObjectType::INTEGER || b->type == ObjectType::FLOAT)) {
                    double val_a = (a->type == ObjectType::INTEGER) ? (double)a->int_val : a->float_val;
                    double val_b = (b->type == ObjectType::INTEGER) ? (double)b->int_val : b->float_val;
                    bool res_is_int = (a->type == ObjectType::INTEGER && b->type == ObjectType::INTEGER);

                    if (res_is_int) frame.stack.push_back(make_int((int64_t)(val_a + val_b)));
                    else frame.stack.push_back(make_float(val_a + val_b));
                }
                else {
                    frame.stack.push_back(make_nil());
                }
            }
            break;

            case 5: // SUB
            {
                auto b = frame.stack.back(); frame.stack.pop_back();
                auto a = frame.stack.back(); frame.stack.pop_back();
                if ((a->type == ObjectType::INTEGER || a->type == ObjectType::FLOAT) &&
                    (b->type == ObjectType::INTEGER || b->type == ObjectType::FLOAT)) {
                    double val_a = (a->type == ObjectType::INTEGER) ? (double)a->int_val : a->float_val;
                    double val_b = (b->type == ObjectType::INTEGER) ? (double)b->int_val : b->float_val;
                    bool res_is_int = (a->type == ObjectType::INTEGER && b->type == ObjectType::INTEGER);

                    if (res_is_int) frame.stack.push_back(make_int((int64_t)(val_a - val_b)));
                    else frame.stack.push_back(make_float(val_a - val_b));
                } else {
                    frame.stack.push_back(make_nil());
                }
            }
            break;

            case 6: // MUL
            {
                auto b = frame.stack.back(); frame.stack.pop_back();
                auto a = frame.stack.back(); frame.stack.pop_back();
                if ((a->type == ObjectType::INTEGER || a->type == ObjectType::FLOAT) &&
                    (b->type == ObjectType::INTEGER || b->type == ObjectType::FLOAT)) {
                    double val_a = (a->type == ObjectType::INTEGER) ? (double)a->int_val : a->float_val;
                    double val_b = (b->type == ObjectType::INTEGER) ? (double)b->int_val : b->float_val;
                    bool res_is_int = (a->type == ObjectType::INTEGER && b->type == ObjectType::INTEGER);

                    if (res_is_int) frame.stack.push_back(make_int((int64_t)(val_a * val_b)));
                    else frame.stack.push_back(make_float(val_a * val_b));
                } else {
                    frame.stack.push_back(make_nil());
                }
            }
            break;

            case 7: // DIV
            {
                auto b = frame.stack.back(); frame.stack.pop_back();
                auto a = frame.stack.back(); frame.stack.pop_back();
                if ((a->type == ObjectType::INTEGER || a->type == ObjectType::FLOAT) &&
                    (b->type == ObjectType::INTEGER || b->type == ObjectType::FLOAT)) {
                    double val_a = (a->type == ObjectType::INTEGER) ? (double)a->int_val : a->float_val;
                    double val_b = (b->type == ObjectType::INTEGER) ? (double)b->int_val : b->float_val;

                    if (val_b == 0) {
                        frame.stack.push_back(make_nil());
                    } else {
                        frame.stack.push_back(make_float(val_a / val_b));
                    }
                } else {
                    frame.stack.push_back(make_nil());
                }
            }
            break;

            case 8: // MOD
            {
                auto b = frame.stack.back(); frame.stack.pop_back();
                auto a = frame.stack.back(); frame.stack.pop_back();
                if ((a->type == ObjectType::INTEGER || a->type == ObjectType::FLOAT) &&
                    (b->type == ObjectType::INTEGER || b->type == ObjectType::FLOAT)) {
                    double val_a = (a->type == ObjectType::INTEGER) ? (double)a->int_val : a->float_val;
                    double val_b = (b->type == ObjectType::INTEGER) ? (double)b->int_val : b->float_val;
                    bool res_is_int = (a->type == ObjectType::INTEGER && b->type == ObjectType::INTEGER);

                    if (res_is_int && val_b != 0) frame.stack.push_back(make_int((int64_t)val_a % (int64_t)val_b));
                    else frame.stack.push_back(make_float(std::fmod(val_a, val_b)));
                } else {
                    frame.stack.push_back(make_nil());
                }
            }
            break;

            // Logic Ops (9-17)
            case 9: { auto b=frame.stack.back(); frame.stack.pop_back(); auto a=frame.stack.back(); frame.stack.pop_back(); frame.stack.push_back(make_bool(check_equality(a,b))); } break;
            case 10: { auto b=frame.stack.back(); frame.stack.pop_back(); auto a=frame.stack.back(); frame.stack.pop_back(); frame.stack.push_back(make_bool(!check_equality(a,b))); } break;
            case 11: { auto b=frame.stack.back(); frame.stack.pop_back(); auto a=frame.stack.back(); frame.stack.pop_back(); frame.stack.push_back(make_bool(check_less(b,a))); } break;
            case 12: { auto b=frame.stack.back(); frame.stack.pop_back(); auto a=frame.stack.back(); frame.stack.pop_back(); frame.stack.push_back(make_bool(check_less(a,b))); } break;
            case 13: { auto b=frame.stack.back(); frame.stack.pop_back(); auto a=frame.stack.back(); frame.stack.pop_back(); frame.stack.push_back(make_bool(!check_less(a,b))); } break;
            case 14: { auto b=frame.stack.back(); frame.stack.pop_back(); auto a=frame.stack.back(); frame.stack.pop_back(); frame.stack.push_back(make_bool(!check_less(b,a))); } break;
            case 15: { auto v=frame.stack.back(); frame.stack.pop_back(); frame.stack.push_back(make_bool(!is_truthy(v))); } break;
            case 16: { auto b=frame.stack.back(); frame.stack.pop_back(); auto a=frame.stack.back(); frame.stack.pop_back(); if(!is_truthy(a)) frame.stack.push_back(a); else frame.stack.push_back(b); } break;
            case 17: { auto b=frame.stack.back(); frame.stack.pop_back(); auto a=frame.stack.back(); frame.stack.pop_back(); if(is_truthy(a)) frame.stack.push_back(a); else frame.stack.push_back(b); } break;

            case 23: // LOAD_VAR
            {
                std::string name = arg->str_val;
                if (frame.locals.count(name)) frame.stack.push_back(frame.locals[name]);
                else if (globals.count(name)) frame.stack.push_back(globals[name]);
                else frame.stack.push_back(make_nil());
            }
            break;

            case 24: // STORE_VAR
            {
                std::string name = arg->str_val;
                // Simplified: Store to globals.
                // Note: Standard logic checks scope. Self-Hosted assumes LOAD_VAR/STORE_VAR used properly.
                // But wait, top level script uses STORE_VAR. Functions use STORE_LOCAL.
                // If in function, STORE_VAR usually means GLOBAL?
                // Self-Hosted compiler logic: if Analyzer says Global, uses STORE_VAR.
                globals[name] = frame.stack.back();
                frame.stack.pop_back();
            }
            break;

            case 25: // LOAD_LOCAL
            {
                std::string name = arg->str_val;
                if (frame.locals.count(name)) frame.stack.push_back(frame.locals[name]);
                else frame.stack.push_back(make_nil());
            }
            break;

            case 26: // STORE_LOCAL
            {
                std::string name = arg->str_val;
                frame.locals[name] = frame.stack.back();
                frame.stack.pop_back();
            }
            break;

            // Data Structures
            case 27: // BUILD_LIST
            {
                int count = arg->int_val;
                auto list_obj = std::make_shared<FoxObject>(ObjectType::LIST);
                for(int i=0; i<count; i++) {
                    list_obj->list_val.push_back(frame.stack.back());
                    frame.stack.pop_back();
                }
                std::reverse(list_obj->list_val.begin(), list_obj->list_val.end());
                frame.stack.push_back(list_obj);
            }
            break;

            case 28: // BUILD_DICT
            {
                int count = arg->int_val;
                auto dict_obj = std::make_shared<FoxObject>(ObjectType::DICT);
                for(int i=0; i<count; i++) {
                    auto val = frame.stack.back(); frame.stack.pop_back();
                    auto key = frame.stack.back(); frame.stack.pop_back();
                    if(key->type == ObjectType::STRING) {
                        dict_obj->dict_val[key->str_val] = val;
                    }
                }
                frame.stack.push_back(dict_obj);
            }
            break;

            // OOP
            case 37: // BUILD_CLASS
            {
                auto methods = frame.stack.back(); frame.stack.pop_back();
                auto super = frame.stack.back(); frame.stack.pop_back();
                auto name = frame.stack.back(); frame.stack.pop_back();

                auto klass = std::make_shared<FoxObject>(ObjectType::CLASS);
                klass->name_val = (name->type == ObjectType::STRING) ? name->str_val : "AnonClass";
                klass->super_class = super;

                if (methods->type == ObjectType::DICT) {
                    klass->methods = methods->dict_val;
                }
                frame.stack.push_back(klass);
            }
            break;

            case 38: // LOAD_ATTR
            {
                std::string attr = arg->str_val;
                auto obj = frame.stack.back(); frame.stack.pop_back();

                if (obj->type == ObjectType::INSTANCE) {
                    if (obj->properties.count(attr)) {
                        frame.stack.push_back(obj->properties[attr]);
                    } else if (obj->klass && obj->klass->methods.count(attr)) {
                        auto bm = std::make_shared<FoxObject>(ObjectType::BOUND_METHOD);
                        bm->instance = obj;
                        bm->method = obj->klass->methods[attr];
                        frame.stack.push_back(bm);
                    } else {
                        frame.stack.push_back(make_nil());
                    }
                } else if (obj->type == ObjectType::FUNCTION) {
                    if (attr == "code") {
                        auto co_obj = std::make_shared<FoxObject>(ObjectType::CODE_OBJECT);
                        co_obj->code_val = obj->code_val;
                        frame.stack.push_back(co_obj);
                    } else {
                        frame.stack.push_back(make_nil());
                    }
                } else {
                    frame.stack.push_back(make_nil());
                }
            }
            break;

            case 39: // STORE_ATTR
            {
                std::string attr = arg->str_val;
                auto val = frame.stack.back(); frame.stack.pop_back();
                auto obj = frame.stack.back(); frame.stack.pop_back();

                if (obj->type == ObjectType::INSTANCE) {
                    obj->properties[attr] = val;
                }
            }
            break;

            // Control Flow
            case 44: frame.pc = (int)arg->int_val; break;
            case 45: { auto v=frame.stack.back(); frame.stack.pop_back(); if(!is_truthy(v)) frame.pc = (int)arg->int_val; } break;
            case 46: { auto v=frame.stack.back(); frame.stack.pop_back(); if(is_truthy(v)) frame.pc = (int)arg->int_val; } break;

            // Function Call
            case 47: // CALL
            {
                int arg_count = arg->int_val;
                std::vector<FoxObjectPtr> args;
                for(int i=0; i<arg_count; i++) {
                    args.push_back(frame.stack.back());
                    frame.stack.pop_back();
                }
                std::reverse(args.begin(), args.end());

                auto func = frame.stack.back(); frame.stack.pop_back();

                if (func->type == ObjectType::FUNCTION) {
                    push_frame(func->code_val, args, func);
                }
                else if (func->type == ObjectType::CLASS) {
                    auto instance = std::make_shared<FoxObject>(ObjectType::INSTANCE);
                    instance->klass = func;

                    if (func->methods.count("inisiasi")) {
                        auto init_method = func->methods["inisiasi"];
                        args.insert(args.begin(), instance);
                        push_frame(init_method->code_val, args, init_method);
                        call_stack.back().is_init = true;
                        call_stack.back().init_instance = instance;
                    } else {
                        frame.stack.push_back(instance);
                    }
                }
                else if (func->type == ObjectType::BOUND_METHOD) {
                    args.insert(args.begin(), func->instance);
                    push_frame(func->method->code_val, args, func->method);
                }
                else {
                    frame.stack.push_back(make_nil());
                }
            }
            break;

            case 48: // RET
            {
                auto ret = frame.stack.empty() ? make_nil() : frame.stack.back();
                bool was_init = frame.is_init;
                FoxObjectPtr instance = frame.init_instance;

                pop_frame();
                if (!call_stack.empty()) {
                    if (was_init) call_stack.back().stack.push_back(instance);
                    else call_stack.back().stack.push_back(ret);
                }
            }
            break;

            // Functions / Closure
            case 60: // BUILD_FUNCTION
            {
                auto dict = frame.stack.back(); frame.stack.pop_back();
                // We need to construct CodeObject from Dict
                auto co = std::make_shared<CodeObject>();

                if (dict->type == ObjectType::DICT) {
                    // Name
                    if (dict->dict_val.count("nama")) co->name = dict->dict_val["nama"]->str_val;

                    // Args
                    if (dict->dict_val.count("args")) {
                        auto args_l = dict->dict_val["args"];
                        if(args_l->type == ObjectType::LIST) {
                            for(auto& s : args_l->list_val) co->arg_names.push_back(s->str_val);
                        }
                    }

                    // Free/Cell vars
                    if (dict->dict_val.count("free_vars")) {
                        auto l = dict->dict_val["free_vars"];
                        if(l->type == ObjectType::LIST) for(auto& s : l->list_val) co->free_vars.push_back(s->str_val);
                    }
                    if (dict->dict_val.count("cell_vars")) {
                        auto l = dict->dict_val["cell_vars"];
                        if(l->type == ObjectType::LIST) for(auto& s : l->list_val) co->cell_vars.push_back(s->str_val);
                    }

                    // Instructions
                    if (dict->dict_val.count("instruksi")) {
                        auto inst_l = dict->dict_val["instruksi"];
                        if(inst_l->type == ObjectType::LIST) {
                            for(auto& i_obj : inst_l->list_val) {
                                if(i_obj->type == ObjectType::LIST && i_obj->list_val.size() >= 2) {
                                    uint8_t op = (uint8_t)i_obj->list_val[0]->int_val;
                                    FoxObjectPtr arg = i_obj->list_val[1];
                                    co->instructions.push_back({op, arg});
                                }
                            }
                        }
                    }
                }

                auto func = std::make_shared<FoxObject>(ObjectType::FUNCTION);
                func->code_val = co;

                // Capture Closure Cells
                for(const auto& name : co->free_vars) {
                    if (frame.cells.count(name)) {
                        func->closure_cells[name] = frame.cells[name];
                    }
                }

                frame.stack.push_back(func);
            }
            break;

            case 68: // MAKE_FUNCTION
            {
                int flags = 0;
                if (arg->type == ObjectType::INTEGER) flags = (int)arg->int_val;
                else if (arg->type == ObjectType::NIL) flags = 0; // Default

                auto code_obj_wrapper = frame.stack.back(); frame.stack.pop_back();

                auto func = std::make_shared<FoxObject>(ObjectType::FUNCTION);

                if (code_obj_wrapper->type == ObjectType::CODE_OBJECT) {
                    func->code_val = code_obj_wrapper->code_val;
                }

                if (flags == 1) {
                    auto closure_list = frame.stack.back(); frame.stack.pop_back();
                    if (closure_list->type == ObjectType::LIST) {
                        if (func->code_val) {
                            auto& fv = func->code_val->free_vars;
                            for(size_t i=0; i<fv.size() && i<closure_list->list_val.size(); i++) {
                                func->closure_cells[fv[i]] = closure_list->list_val[i];
                            }
                        }
                    }
                }

                frame.stack.push_back(func);
            }
            break;

            case 65: // LOAD_DEREF
            {
                std::string name = arg->str_val;
                if (frame.cells.count(name)) frame.stack.push_back(frame.cells[name]->cell_value);
                else frame.stack.push_back(make_nil());
            }
            break;

            case 66: // STORE_DEREF
            {
                std::string name = arg->str_val;
                if (frame.cells.count(name)) {
                    frame.cells[name]->cell_value = frame.stack.back();
                    frame.stack.pop_back();
                }
            }
            break;

            case 67: // LOAD_CLOSURE
            {
                std::string name = arg->str_val;
                if (frame.cells.count(name)) frame.stack.push_back(frame.cells[name]);
                else frame.stack.push_back(make_nil());
            }
            break;

            case 53: // PRINT
                {
                    int count = arg->int_val;
                    std::vector<FoxObjectPtr> print_args;
                    for(int i=0; i<count; i++) {
                        print_args.push_back(frame.stack.back());
                        frame.stack.pop_back();
                    }
                    for(int i=count-1; i>=0; i--) {
                        builtin_tulis(print_args[i]);
                    }
                }
                break;

            // System Ops
            case 79: { auto n=std::chrono::system_clock::now(); auto d=n.time_since_epoch(); frame.stack.push_back(make_float(std::chrono::duration<double>(d).count())); } break;
            case 80: { auto v=frame.stack.back(); frame.stack.pop_back(); std::this_thread::sleep_for(std::chrono::duration<double>(v->type==ObjectType::INTEGER?(double)v->int_val:v->float_val)); frame.stack.push_back(make_nil()); } break;
            case 81: { std::string p="unknown";
            #if defined(__EMSCRIPTEN__)
            p="web";
            #elif defined(__ANDROID__)
            p="android";
            #elif defined(_WIN32)
            p="win32";
            #elif defined(__APPLE__)
            p="darwin";
            #elif defined(__linux__)
            p="linux";
            #endif
            frame.stack.push_back(make_str(p)); } break;

            default:
                break;
        }
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
