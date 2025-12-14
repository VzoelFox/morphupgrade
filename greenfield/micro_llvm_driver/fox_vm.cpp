#include "fox_vm.hpp"
#include <iostream>
#include <iomanip>
#include <chrono>
#include <thread>
#include <cmath>
#include <algorithm>
#include <filesystem>
#include <cstdio>

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

FoxVM::FoxVM() {
    setup_builtins();
    setup_backend();
}

void FoxVM::setup_builtins() {
    globals["tulis"] = make_native_func([](FoxVM& vm, int argc) {
        // Tulis (Print) accepts N args, prints them, returns nil
        // Args are on stack. reverse logic needed?
        // Native func args are popped by caller? NO.
        // CALL opcode: "func_to_call->native_func(*this, arg_count);"
        // Stack has args pushed.
        // We should pop them.
        std::vector<FoxObjectPtr> print_args;
        for(int i=0; i<argc; i++) {
             print_args.push_back(vm.pop_stack());
        }
        // Stack was [Arg1, Arg2]. Pop -> Arg2, Arg1.
        // So print_args is reversed.
        for(int i=argc-1; i>=0; i--) {
            vm.builtin_tulis(print_args[i]);
        }
        vm.push_stack(make_nil());
    });

    globals["teks"] = make_native_func([](FoxVM& vm, int argc) {
        if (argc > 0) {
            auto obj = vm.pop_stack();
            // Discard extra args
            for(int i=1; i<argc; i++) vm.pop_stack();

            // Same logic as conv_str
            if (obj->type == ObjectType::STRING) vm.push_stack(obj);
            else if (obj->type == ObjectType::INTEGER) vm.push_stack(make_str(std::to_string(obj->int_val)));
            else if (obj->type == ObjectType::FLOAT) vm.push_stack(make_str(std::to_string(obj->float_val)));
            else if (obj->type == ObjectType::BOOLEAN) vm.push_stack(make_str(obj->bool_val ? "benar" : "salah"));
            else if (obj->type == ObjectType::NIL) vm.push_stack(make_str("nil"));
            else vm.push_stack(make_str("<obj>"));
        } else {
            vm.push_stack(make_str(""));
        }
    });

    // _keys_builtin for dict keys
    globals["_keys_builtin"] = make_native_func([](FoxVM& vm, int argc) {
        auto obj = vm.pop_stack();
        auto list = std::make_shared<FoxObject>(ObjectType::LIST);
        if (obj->type == ObjectType::DICT) {
            for(auto const& [key, val] : obj->dict_val) {
                list->list_val.push_back(make_str(key));
            }
        }
        vm.push_stack(list);
    });
}

void FoxVM::push_stack(FoxObjectPtr obj) {
    if (!call_stack.empty()) {
        call_stack.back().stack.push_back(obj);
    }
}

FoxObjectPtr FoxVM::pop_stack() {
    if (!call_stack.empty() && !call_stack.back().stack.empty()) {
        auto o = call_stack.back().stack.back();
        call_stack.back().stack.pop_back();
        return o;
    }
    return make_nil();
}

FoxObjectPtr FoxVM::peek_stack(int offset) {
    if (!call_stack.empty()) {
        auto& s = call_stack.back().stack;
        if (offset < (int)s.size()) {
            return s[s.size() - 1 - offset];
        }
    }
    return make_nil();
}

FoxObjectPtr FoxVM::make_native_func(NativeFunc f) {
    auto o = std::make_shared<FoxObject>(ObjectType::NATIVE_FUNCTION);
    o->native_func = f;
    return o;
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
    } else if (arg->type == ObjectType::LIST) {
        std::cout << "[";
        for(size_t i=0; i<arg->list_val.size(); i++) {
            if (i > 0) std::cout << ", ";
            auto item = arg->list_val[i];
            // Simple recursive printing
            if (item->type == ObjectType::STRING) std::cout << "\"" << item->str_val << "\"";
            else if (item->type == ObjectType::INTEGER) std::cout << item->int_val;
            else if (item->type == ObjectType::FLOAT) std::cout << item->float_val;
            else if (item->type == ObjectType::GENERATOR) std::cout << "<generator>";
            else std::cout << "<obj>";
        }
        std::cout << "]" << std::endl;
    } else if (arg->type == ObjectType::DICT) {
        std::cout << "{";
        int count = 0;
        for(auto const& [key, val] : arg->dict_val) {
            if (count > 0) std::cout << ", ";
            std::cout << "\"" << key << "\": ";
            if (val->type == ObjectType::STRING) std::cout << "\"" << val->str_val << "\"";
            else if (val->type == ObjectType::INTEGER) std::cout << val->int_val;
            else if (val->type == ObjectType::NATIVE_FUNCTION) std::cout << "<native_func>";
            else std::cout << "<obj>";
            count++;
        }
        std::cout << "}" << std::endl;
    } else if (arg->type == ObjectType::GENERATOR) {
        std::cout << "<generator>" << std::endl;
    } else {
        std::cout << "<object>" << std::endl;
    }
}

void FoxVM::handle_exception(FoxObjectPtr exc) {
    while (!call_stack.empty()) {
        Frame& f = call_stack.back();
        if (!f.try_stack.empty()) {
            // Handler found
            TryBlock handler = f.try_stack.back();
            f.try_stack.pop_back();

            // Unwind Stack to saved depth
            while (f.stack.size() > handler.stack_depth) {
                f.stack.pop_back();
            }

            // Push Exception
            f.stack.push_back(exc);

            // Jump
            f.pc = handler.handler_pc;
            return;
        } else {
            // No handler in this frame, unwind frame
            pop_frame();
        }
    }

    // Uncaught Panic
    std::cout << "Panic: ";
    builtin_tulis(exc);
    exit(1);
}

// --- Backend (I/O, Sys Info, Async) Implementation ---

void FoxVM::setup_backend() {
    auto backend = std::make_shared<FoxObject>(ObjectType::DICT);

    // --- BASIC CORE ---

    // conv_len(obj)
    backend->dict_val["conv_len"] = make_native_func([](FoxVM& vm, int argc) {
        auto obj = vm.pop_stack();
        if (obj->type == ObjectType::STRING) vm.push_stack(make_int(obj->str_val.size()));
        else if (obj->type == ObjectType::LIST) vm.push_stack(make_int(obj->list_val.size()));
        else if (obj->type == ObjectType::DICT) vm.push_stack(make_int(obj->dict_val.size()));
        else vm.push_stack(make_int(0));
    });

    // conv_str(obj) -> string representation
    backend->dict_val["conv_str"] = make_native_func([](FoxVM& vm, int argc) {
        auto obj = vm.pop_stack();
        if (obj->type == ObjectType::STRING) vm.push_stack(obj); // Already string
        else if (obj->type == ObjectType::INTEGER) vm.push_stack(make_str(std::to_string(obj->int_val)));
        else if (obj->type == ObjectType::FLOAT) vm.push_stack(make_str(std::to_string(obj->float_val)));
        else if (obj->type == ObjectType::BOOLEAN) vm.push_stack(make_str(obj->bool_val ? "benar" : "salah"));
        else if (obj->type == ObjectType::NIL) vm.push_stack(make_str("nil"));
        else vm.push_stack(make_str("<obj>"));
    });

    // sys_list_append(list, item)
    backend->dict_val["sys_list_append"] = make_native_func([](FoxVM& vm, int argc) {
        auto item = vm.pop_stack();
        auto list = vm.pop_stack();
        if (list->type == ObjectType::LIST) {
            list->list_val.push_back(item);
        }
        vm.push_stack(make_nil());
    });

    // sys_list_pop(list, idx)
    backend->dict_val["sys_list_pop"] = make_native_func([](FoxVM& vm, int argc) {
        auto idx_obj = vm.pop_stack();
        auto list = vm.pop_stack();
        if (list->type == ObjectType::LIST) {
            int idx = 0;
            if (idx_obj->type == ObjectType::INTEGER) idx = (int)idx_obj->int_val;

            if (idx < 0) idx += list->list_val.size();

            if (idx >= 0 && idx < (int)list->list_val.size()) {
                auto item = list->list_val[idx];
                list->list_val.erase(list->list_val.begin() + idx);
                vm.push_stack(item);
            } else {
                vm.push_stack(make_nil());
            }
        } else {
            vm.push_stack(make_nil());
        }
    });

    // sys_str_join(list, sep)
    backend->dict_val["sys_str_join"] = make_native_func([](FoxVM& vm, int argc) {
        auto sep = vm.pop_stack();
        auto list = vm.pop_stack();
        std::string res;
        std::string s_sep = (sep->type == ObjectType::STRING) ? sep->str_val : "";

        if (list->type == ObjectType::LIST) {
            for(size_t i=0; i<list->list_val.size(); i++) {
                if (i > 0) res += s_sep;
                auto item = list->list_val[i];
                if (item->type == ObjectType::STRING) res += item->str_val;
            }
        }
        vm.push_stack(make_str(res));
    });

    backend->dict_val["sys_to_int"] = make_native_func([](FoxVM& vm, int argc) {
        auto v = vm.pop_stack();
        if (v->type == ObjectType::INTEGER) vm.push_stack(v);
        else if (v->type == ObjectType::FLOAT) vm.push_stack(make_int((int64_t)v->float_val));
        else if (v->type == ObjectType::STRING) {
            try { vm.push_stack(make_int(std::stoll(v->str_val))); } catch(...) { vm.push_stack(make_int(0)); }
        } else vm.push_stack(make_int(0));
    });

    backend->dict_val["sys_to_float"] = make_native_func([](FoxVM& vm, int argc) {
        auto v = vm.pop_stack();
        if (v->type == ObjectType::FLOAT) vm.push_stack(v);
        else if (v->type == ObjectType::INTEGER) vm.push_stack(make_float((double)v->int_val));
        else if (v->type == ObjectType::STRING) {
            try { vm.push_stack(make_float(std::stod(v->str_val))); } catch(...) { vm.push_stack(make_float(0.0)); }
        } else vm.push_stack(make_float(0.0));
    });

    backend->dict_val["sys_chr"] = make_native_func([](FoxVM& vm, int argc) {
        auto v = vm.pop_stack();
        if (v->type == ObjectType::INTEGER) {
            char c = (char)v->int_val;
            vm.push_stack(make_str(std::string(1, c)));
        } else vm.push_stack(make_str(""));
    });

    backend->dict_val["sys_ord"] = make_native_func([](FoxVM& vm, int argc) {
        auto v = vm.pop_stack();
        if (v->type == ObjectType::STRING && !v->str_val.empty()) {
            vm.push_stack(make_int((int64_t)v->str_val[0]));
        } else vm.push_stack(make_int(0));
    });

    // --- IO ---

    // I/O: Buka File
    backend->dict_val["fs_buka"] = make_native_func([](FoxVM& vm, int argc) {
        auto mode_obj = vm.pop_stack();
        auto path_obj = vm.pop_stack();
        std::string path = (path_obj->type == ObjectType::STRING) ? path_obj->str_val : "";
        std::string mode = (mode_obj->type == ObjectType::STRING) ? mode_obj->str_val : "r";

        std::string cmode = "r";
        if (mode == "tulis") cmode = "w";
        else if (mode == "tambah") cmode = "a";
        else if (mode == "biner_baca") cmode = "rb";
        else if (mode == "biner_tulis") cmode = "wb";

        FILE* fp = fopen(path.c_str(), cmode.c_str());
        if (fp) vm.push_stack(make_int((int64_t)fp));
        else vm.push_stack(make_nil());
    });

    // I/O: Baca File
    backend->dict_val["fs_baca"] = make_native_func([](FoxVM& vm, int argc) {
        auto size_obj = vm.pop_stack();
        auto handle = vm.pop_stack();

        if (handle->type == ObjectType::INTEGER && handle->int_val != 0) {
            FILE* fp = (FILE*)handle->int_val;
            fseek(fp, 0, SEEK_END);
            long fsize = ftell(fp);
            fseek(fp, 0, SEEK_SET);
            std::string content(fsize, '\0');
            fread(&content[0], 1, fsize, fp);
            vm.push_stack(make_str(content));
        } else {
             vm.push_stack(make_nil());
        }
    });

    // I/O: Tulis File
    backend->dict_val["fs_tulis"] = make_native_func([](FoxVM& vm, int argc) {
        auto content = vm.pop_stack();
        auto handle = vm.pop_stack();
        if (handle->type == ObjectType::INTEGER && handle->int_val != 0) {
            FILE* fp = (FILE*)handle->int_val;
            if (content->type == ObjectType::STRING) {
                fwrite(content->str_val.c_str(), 1, content->str_val.length(), fp);
            }
        }
        vm.push_stack(make_nil());
    });

    // I/O: Tutup File
    backend->dict_val["fs_tutup"] = make_native_func([](FoxVM& vm, int argc) {
        auto handle = vm.pop_stack();
        if (handle->type == ObjectType::INTEGER && handle->int_val != 0) {
            FILE* fp = (FILE*)handle->int_val;
            fclose(fp);
        }
        vm.push_stack(make_nil());
    });

    // I/O: Cek File Ada
    backend->dict_val["fs_ada"] = make_native_func([](FoxVM& vm, int argc) {
        auto path = vm.pop_stack();
        bool exists = false;
        if (path->type == ObjectType::STRING) {
             exists = std::filesystem::exists(path->str_val);
        }
        vm.push_stack(make_bool(exists));
    });

    // I/O: CWD
    backend->dict_val["fs_cwd"] = make_native_func([](FoxVM& vm, int argc) {
        std::string cwd = std::filesystem::current_path().string();
        vm.push_stack(make_str(cwd));
    });

    // System: Platform
    backend->dict_val["sys_platform"] = make_native_func([](FoxVM& vm, int argc) {
        #if defined(_WIN32)
            vm.push_stack(make_str("win32"));
        #elif defined(__linux__)
            vm.push_stack(make_str("linux"));
        #elif defined(__APPLE__)
            vm.push_stack(make_str("darwin"));
        #else
            vm.push_stack(make_str("unknown"));
        #endif
    });

    // System: Keluar
    backend->dict_val["sys_keluar"] = make_native_func([](FoxVM& vm, int argc) {
        auto code = vm.pop_stack();
        int c = 0;
        if (code->type == ObjectType::INTEGER) c = (int)code->int_val;
        exit(c);
    });

    // Sys Info: CPU
    backend->dict_val["sys_info_cpu"] = make_native_func([](FoxVM& vm, int argc) {
        std::ifstream f("/proc/stat");
        if (f.is_open()) {
            std::string line;
            std::getline(f, line);
            vm.push_stack(make_str(line));
        } else {
            vm.push_stack(make_str("unknown"));
        }
    });

    // Sys Info: Mem
    backend->dict_val["sys_info_mem"] = make_native_func([](FoxVM& vm, int argc) {
        std::ifstream f("/proc/meminfo");
        if (f.is_open()) {
            std::string content((std::istreambuf_iterator<char>(f)), std::istreambuf_iterator<char>());
            if (content.size() > 1024) content.resize(1024);
            vm.push_stack(make_str(content));
        } else {
            vm.push_stack(make_str("unknown"));
        }
    });

    // --- ASYNC PRIMITIVES ---

    // sys_yield(val)
    backend->dict_val["sys_yield"] = make_native_func([](FoxVM& vm, int argc) {
        auto val = vm.pop_stack();

        if (vm.call_stack.size() < 1) return;

        // 1. Snapshot Caller Frame
        Frame& caller = vm.call_stack.back();
        auto saved_frame = std::make_shared<Frame>(caller);

        // 2. Remove Caller Frame
        vm.pop_frame();

        // 3. Return [val, Generator] to Parent
        if (!vm.call_stack.empty()) {
            auto gen = std::make_shared<FoxObject>(ObjectType::GENERATOR);
            gen->gen_frame = saved_frame;

            auto list = std::make_shared<FoxObject>(ObjectType::LIST);
            list->list_val.push_back(val);
            list->list_val.push_back(gen);

            vm.call_stack.back().stack.push_back(list);
        } else {
            // std::cout << "[VM] Yielded from Top Level." << std::endl;
        }

        // 4. THROW Exception to unwind C++ stack immediately
        throw VMYieldException();
    });

    // sys_resume(gen, val)
    backend->dict_val["sys_resume"] = make_native_func([](FoxVM& vm, int argc) {
        auto input_val = vm.pop_stack();
        auto gen_obj = vm.pop_stack();

        if (gen_obj->type == ObjectType::GENERATOR && gen_obj->gen_frame) {
            Frame& restored = *gen_obj->gen_frame;
            vm.call_stack.push_back(restored);
            vm.call_stack.back().stack.push_back(input_val);
        } else {
            vm.push_stack(make_nil());
        }
    });

    native_modules["_backend"] = backend;
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

        try {
            switch(op) {
            case 1: // PUSH_CONST
                frame.stack.push_back(arg);
                break;

            case 2: // POP
                if (!frame.stack.empty()) frame.stack.pop_back();
                break;

            case 3: // DUP
                if (!frame.stack.empty()) frame.stack.push_back(frame.stack.back());
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
                if (frame.is_module) {
                    frame.locals[name] = frame.stack.back();
                } else {
                    globals[name] = frame.stack.back();
                }
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
                    if (obj->properties.count(attr)) frame.stack.push_back(obj->properties[attr]);
                    else if (obj->klass && obj->klass->methods.count(attr)) {
                        auto bm = std::make_shared<FoxObject>(ObjectType::BOUND_METHOD);
                        bm->instance = obj; bm->method = obj->klass->methods[attr];
                        frame.stack.push_back(bm);
                    } else frame.stack.push_back(make_nil());
                } else if (obj->type == ObjectType::DICT) {
                    if (obj->dict_val.count(attr)) frame.stack.push_back(obj->dict_val[attr]);
                    else frame.stack.push_back(make_nil());
                } else if (obj->type == ObjectType::FUNCTION) {
                    if (attr == "code") {
                        auto co_obj = std::make_shared<FoxObject>(ObjectType::CODE_OBJECT);
                        co_obj->code_val = obj->code_val;
                        frame.stack.push_back(co_obj);
                    } else frame.stack.push_back(make_nil());
                } else if (obj->type == ObjectType::STRING) {
                    uint8_t op = 0;
                    if (attr == "kecil") op = 75;
                    else if (attr == "besar") op = 76;
                    else if (attr == "temukan") op = 77;
                    else if (attr == "ganti") op = 78;

                    if (op != 0) {
                        auto co = std::make_shared<CodeObject>();
                        co->name = "<native_" + attr + ">";
                        co->arg_names.push_back("self");
                        if (op == 77) co->arg_names.push_back("needle");
                        if (op == 78) { co->arg_names.push_back("old"); co->arg_names.push_back("new"); }
                        co->instructions.push_back({25, make_str("self")});
                        if (op == 77) co->instructions.push_back({25, make_str("needle")});
                        if (op == 78) { co->instructions.push_back({25, make_str("old")}); co->instructions.push_back({25, make_str("new")}); }
                        co->instructions.push_back({op, make_nil()});
                        co->instructions.push_back({48, make_nil()});
                        auto method_func = std::make_shared<FoxObject>(ObjectType::FUNCTION);
                        method_func->code_val = co;
                        auto bm = std::make_shared<FoxObject>(ObjectType::BOUND_METHOD);
                        bm->instance = obj; bm->method = method_func;
                        frame.stack.push_back(bm);
                    } else frame.stack.push_back(make_nil());
                } else frame.stack.push_back(make_nil());
            }
            break;

            case 39: // STORE_ATTR
            {
                std::string attr = arg->str_val;
                auto val = frame.stack.back(); frame.stack.pop_back();
                auto obj = frame.stack.back(); frame.stack.pop_back();
                if (obj->type == ObjectType::INSTANCE) obj->properties[attr] = val;
            }
            break;

            case 44: frame.pc = (int)arg->int_val; break;
            case 45: { auto v=frame.stack.back(); frame.stack.pop_back(); if(!is_truthy(v)) frame.pc = (int)arg->int_val; } break;
            case 46: { auto v=frame.stack.back(); frame.stack.pop_back(); if(is_truthy(v)) frame.pc = (int)arg->int_val; } break;

            case 47: // CALL
            {
                int arg_count = arg->int_val;
                std::vector<FoxObjectPtr> args;
                for(int i=0; i<arg_count; i++) {
                    args.push_back(frame.stack.back());
                    frame.stack.pop_back();
                }
                std::reverse(args.begin(), args.end());
                auto func_to_call = frame.stack.back(); frame.stack.pop_back();

                if (func_to_call->type == ObjectType::FUNCTION) push_frame(func_to_call->code_val, args, func_to_call);
                else if (func_to_call->type == ObjectType::NATIVE_FUNCTION) {
                     for(auto& a : args) frame.stack.push_back(a);
                     func_to_call->native_func(*this, arg_count);
                }
                else if (func_to_call->type == ObjectType::CLASS) {
                    auto instance = std::make_shared<FoxObject>(ObjectType::INSTANCE);
                    instance->klass = func_to_call;
                    if (func_to_call->methods.count("inisiasi")) {
                        auto init_method = func_to_call->methods["inisiasi"];
                        args.insert(args.begin(), instance);
                        push_frame(init_method->code_val, args, init_method);
                        call_stack.back().is_init = true;
                        call_stack.back().init_instance = instance;
                    } else frame.stack.push_back(instance);
                }
                else if (func_to_call->type == ObjectType::BOUND_METHOD) {
                     auto actual_method = func_to_call->method;
                     if (actual_method->type == ObjectType::NATIVE_FUNCTION) {
                         args.insert(args.begin(), func_to_call->instance);
                         for(auto& a : args) frame.stack.push_back(a);
                         actual_method->native_func(*this, arg_count + 1);
                     } else {
                         args.insert(args.begin(), func_to_call->instance);
                         push_frame(actual_method->code_val, args, actual_method);
                     }
                } else frame.stack.push_back(make_nil());
            }
            break;

            case 48: // RET
            {
                auto ret = frame.stack.empty() ? make_nil() : frame.stack.back();
                bool was_init = frame.is_init;
                FoxObjectPtr instance = frame.init_instance;

                // Module Support
                bool is_mod = frame.is_module;
                std::string mod_name = frame.module_name;
                auto locals_copy = frame.locals;

                pop_frame();
                if (!call_stack.empty()) {
                    if (is_mod) {
                        auto mod_dict = std::make_shared<FoxObject>(ObjectType::DICT);
                        mod_dict->dict_val = locals_copy;
                        this->modules[mod_name] = mod_dict;
                        call_stack.back().stack.push_back(mod_dict);
                    } else if (was_init) {
                        call_stack.back().stack.push_back(instance);
                    } else {
                        call_stack.back().stack.push_back(ret);
                    }
                }
            }
            break;

            case 49: // PUSH_TRY
            {
                int handler_pc = (int)arg->int_val;
                frame.try_stack.push_back({handler_pc, frame.stack.size()});
            }
            break;

            case 50: // POP_TRY
                if (!frame.try_stack.empty()) frame.try_stack.pop_back();
                break;

            case 51: // THROW
            {
                auto exc = frame.stack.back(); frame.stack.pop_back();
                handle_exception(exc);
            }
            break;

            case 52: // IMPORT
            {
                std::string mod_name = arg->str_val;
                if (native_modules.count(mod_name)) {
                    frame.stack.push_back(native_modules[mod_name]);
                } else if (modules.count(mod_name)) {
                    frame.stack.push_back(modules[mod_name]);
                } else {
                    std::string path = mod_name + ".mvm";
                    std::ifstream f(path, std::ios::binary);
                    if (f.is_open()) {
                        char magic[10];
                        f.read(magic, 10);
                        std::string magic_str(magic, 10);
                        if (magic_str == "VZOEL FOXS") {
                            f.ignore(6);
                            auto obj = read_object(f);
                            if (obj->type == ObjectType::CODE_OBJECT) {
                                // std::cout << "[DEBUG] Loading module: " << mod_name << std::endl;
                                push_frame(obj->code_val, {}, nullptr);
                                call_stack.back().is_module = true;
                                call_stack.back().module_name = mod_name;
                            } else {
                                std::cerr << "[DEBUG] Module root is not CODE_OBJECT" << std::endl;
                                frame.stack.push_back(make_nil());
                            }
                        } else {
                             std::cerr << "[DEBUG] Invalid Magic: " << magic_str << std::endl;
                             frame.stack.push_back(make_nil());
                        }
                    } else {
                        std::cerr << "[DEBUG] File not found: " << path << std::endl;
                        frame.stack.push_back(make_nil());
                    }
                }
            }
            break;

            case 61: // IMPORT_NATIVE
            {
                std::string mod_name = arg->str_val;
                if (native_modules.count(mod_name)) frame.stack.push_back(native_modules[mod_name]);
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
                for(int i=count-1; i>=0; i--) builtin_tulis(print_args[i]);
            }
            break;

            // 63: TYPE (ADDED)
            case 63: {
                auto obj = frame.stack.back(); frame.stack.pop_back();
                if (obj->type == ObjectType::STRING) frame.stack.push_back(make_str("teks"));
                else if (obj->type == ObjectType::INTEGER || obj->type == ObjectType::FLOAT) frame.stack.push_back(make_str("angka"));
                else if (obj->type == ObjectType::BOOLEAN) frame.stack.push_back(make_str("boolean"));
                else if (obj->type == ObjectType::LIST) frame.stack.push_back(make_str("daftar"));
                else if (obj->type == ObjectType::DICT) frame.stack.push_back(make_str("kamus"));
                else if (obj->type == ObjectType::NIL) frame.stack.push_back(make_str("nil"));
                else if (obj->type == ObjectType::FUNCTION || obj->type == ObjectType::NATIVE_FUNCTION) frame.stack.push_back(make_str("fungsi"));
                else if (obj->type == ObjectType::GENERATOR) frame.stack.push_back(make_str("generator"));
                else frame.stack.push_back(make_str("objek"));
            }
            break;

            case 59: // SLICE
            {
                auto end = frame.stack.back(); frame.stack.pop_back();
                auto start = frame.stack.back(); frame.stack.pop_back();
                auto obj = frame.stack.back(); frame.stack.pop_back();
                if (obj->type == ObjectType::STRING) {
                    std::string s = obj->str_val;
                    int len = (int)s.length();
                    int s_idx = 0; int e_idx = len;
                    if (start->type == ObjectType::INTEGER) s_idx = (int)start->int_val;
                    if (end->type == ObjectType::INTEGER) e_idx = (int)end->int_val;
                    if (s_idx < 0) s_idx += len; if (e_idx < 0) e_idx += len;
                    if (s_idx < 0) s_idx = 0; if (e_idx > len) e_idx = len; if (s_idx > e_idx) s_idx = e_idx;
                    frame.stack.push_back(make_str(s.substr(s_idx, e_idx - s_idx)));
                } else if (obj->type == ObjectType::LIST) {
                    auto& list = obj->list_val;
                    int len = (int)list.size();
                    int s_idx = 0; int e_idx = len;
                    if (start->type == ObjectType::INTEGER) s_idx = (int)start->int_val;
                    if (end->type == ObjectType::INTEGER) e_idx = (int)end->int_val;
                    if (s_idx < 0) s_idx += len; if (e_idx < 0) e_idx += len;
                    if (s_idx < 0) s_idx = 0; if (e_idx > len) e_idx = len; if (s_idx > e_idx) s_idx = e_idx;
                    auto new_list = std::make_shared<FoxObject>(ObjectType::LIST);
                    for(int i=s_idx; i<e_idx; i++) new_list->list_val.push_back(list[i]);
                    frame.stack.push_back(new_list);
                } else frame.stack.push_back(make_nil());
            }
            break;

            case 60: // BUILD_FUNCTION
            {
                auto dict = frame.stack.back(); frame.stack.pop_back();
                auto co = std::make_shared<CodeObject>();
                if (dict->type == ObjectType::DICT) {
                    if (dict->dict_val.count("nama")) co->name = dict->dict_val["nama"]->str_val;
                    if (dict->dict_val.count("args")) {
                        auto args_l = dict->dict_val["args"];
                        if(args_l->type == ObjectType::LIST) for(auto& s : args_l->list_val) co->arg_names.push_back(s->str_val);
                    }
                    if (dict->dict_val.count("free_vars")) {
                        auto l = dict->dict_val["free_vars"];
                        if(l->type == ObjectType::LIST) for(auto& s : l->list_val) co->free_vars.push_back(s->str_val);
                    }
                    if (dict->dict_val.count("cell_vars")) {
                        auto l = dict->dict_val["cell_vars"];
                        if(l->type == ObjectType::LIST) for(auto& s : l->list_val) co->cell_vars.push_back(s->str_val);
                    }
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
                for(const auto& name : co->free_vars) if (frame.cells.count(name)) func->closure_cells[name] = frame.cells[name];
                frame.stack.push_back(func);
            }
            break;

            case 68: // MAKE_FUNCTION
            {
                int flags = (arg->type == ObjectType::INTEGER) ? (int)arg->int_val : 0;
                auto code_obj_wrapper = frame.stack.back(); frame.stack.pop_back();
                auto func = std::make_shared<FoxObject>(ObjectType::FUNCTION);
                if (code_obj_wrapper->type == ObjectType::CODE_OBJECT) func->code_val = code_obj_wrapper->code_val;
                if (flags == 1) {
                    auto closure_list = frame.stack.back(); frame.stack.pop_back();
                    if (closure_list->type == ObjectType::LIST && func->code_val) {
                        auto& fv = func->code_val->free_vars;
                        for(size_t i=0; i<fv.size() && i<closure_list->list_val.size(); i++) func->closure_cells[fv[i]] = closure_list->list_val[i];
                    }
                }
                frame.stack.push_back(func);
            }
            break;

            case 65: // LOAD_DEREF
            {
                std::string name = arg->str_val;
                if (frame.cells.count(name)) frame.stack.push_back(frame.cells[name]->cell_value); else frame.stack.push_back(make_nil());
            }
            break;
            case 66: // STORE_DEREF
            {
                std::string name = arg->str_val;
                if (frame.cells.count(name)) { frame.cells[name]->cell_value = frame.stack.back(); frame.stack.pop_back(); }
            }
            break;
            case 67: // LOAD_CLOSURE
            {
                std::string name = arg->str_val;
                if (frame.cells.count(name)) frame.stack.push_back(frame.cells[name]); else frame.stack.push_back(make_nil());
            }
            break;

            case 69: { auto b=frame.stack.back(); frame.stack.pop_back(); auto a=frame.stack.back(); frame.stack.pop_back(); frame.stack.push_back(make_int(a->int_val & b->int_val)); } break;
            case 70: { auto b=frame.stack.back(); frame.stack.pop_back(); auto a=frame.stack.back(); frame.stack.pop_back(); frame.stack.push_back(make_int(a->int_val | b->int_val)); } break;
            case 71: { auto b=frame.stack.back(); frame.stack.pop_back(); auto a=frame.stack.back(); frame.stack.pop_back(); frame.stack.push_back(make_int(a->int_val ^ b->int_val)); } break;
            case 72: { auto v=frame.stack.back(); frame.stack.pop_back(); frame.stack.push_back(make_int(~v->int_val)); } break;
            case 73: { auto b=frame.stack.back(); frame.stack.pop_back(); auto a=frame.stack.back(); frame.stack.pop_back(); frame.stack.push_back(make_int(a->int_val << b->int_val)); } break;
            case 74: { auto b=frame.stack.back(); frame.stack.pop_back(); auto a=frame.stack.back(); frame.stack.pop_back(); frame.stack.push_back(make_int(a->int_val >> b->int_val)); } break;

            case 75: // STR_LOWER
            {
                auto obj = frame.stack.back(); frame.stack.pop_back();
                if (obj->type == ObjectType::STRING) {
                    std::string s = obj->str_val;
                    std::transform(s.begin(), s.end(), s.begin(), ::tolower);
                    frame.stack.push_back(make_str(s));
                } else frame.stack.push_back(make_nil());
            }
            break;
            case 76: // STR_UPPER
            {
                auto obj = frame.stack.back(); frame.stack.pop_back();
                if (obj->type == ObjectType::STRING) {
                    std::string s = obj->str_val;
                    std::transform(s.begin(), s.end(), s.begin(), ::toupper);
                    frame.stack.push_back(make_str(s));
                } else frame.stack.push_back(make_nil());
            }
            break;
            case 77: // STR_FIND
            {
                auto needle = frame.stack.back(); frame.stack.pop_back();
                auto haystack = frame.stack.back(); frame.stack.pop_back();
                if (haystack->type == ObjectType::STRING && needle->type == ObjectType::STRING) {
                    int idx = (int)haystack->str_val.find(needle->str_val);
                    frame.stack.push_back(make_int(idx));
                } else frame.stack.push_back(make_int(-1));
            }
            break;
            case 78: // STR_REPLACE
            {
                auto new_s = frame.stack.back(); frame.stack.pop_back();
                auto old_s = frame.stack.back(); frame.stack.pop_back();
                auto hay = frame.stack.back(); frame.stack.pop_back();
                if (hay->type == ObjectType::STRING && old_s->type == ObjectType::STRING && new_s->type == ObjectType::STRING) {
                    std::string res = hay->str_val;
                    std::string from = old_s->str_val;
                    std::string to = new_s->str_val;
                    if(!from.empty()) {
                         size_t pos = 0;
                         while((pos = res.find(from, pos)) != std::string::npos) {
                             res.replace(pos, from.length(), to);
                             pos += to.length();
                         }
                    }
                    frame.stack.push_back(make_str(res));
                } else frame.stack.push_back(make_nil());
            }
            break;

            case 79: { auto n=std::chrono::system_clock::now(); auto d=n.time_since_epoch(); frame.stack.push_back(make_float(std::chrono::duration<double>(d).count())); } break;
            case 80: { auto v=frame.stack.back(); frame.stack.pop_back(); std::this_thread::sleep_for(std::chrono::duration<double>(v->type==ObjectType::INTEGER?(double)v->int_val:v->float_val)); frame.stack.push_back(make_nil()); } break;

            case 81: // SYS_PLATFORM
            {
                std::string p="unknown";
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
                frame.stack.push_back(make_str(p));
            }
            break;

            default: break;
            }
        } catch (VMYieldException& e) {
            // Yield Triggered
            continue;
        }
    }
}
