#include "fox_vm.hpp"
#include <iostream>
#include <iomanip>

// --- Helper Constructors ---
FoxObjectPtr make_nil() { return std::make_shared<FoxObject>(ObjectType::NIL); }
FoxObjectPtr make_int(int64_t v) {
    auto o = std::make_shared<FoxObject>(ObjectType::INTEGER);
    o->int_val = v;
    return o;
}
FoxObjectPtr make_str(std::string s) {
    auto o = std::make_shared<FoxObject>(ObjectType::STRING);
    o->str_val = s;
    return o;
}

FoxVM::FoxVM() {
    setup_builtins();
}

void FoxVM::setup_builtins() {
    // Register 'tulis' as a special native hook
    // We treat it as a special string marker for now.
    globals["tulis"] = make_str("<native_tulis>");
}

// --- Binary Reader (Little Endian) ---

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

    uint8_t arg_count = read_byte(f); // pack_byte(panjang(co.argumen)) - This is count
    // Then loop strings
    for(int i=0; i<arg_count; i++) {
        std::string arg_name = read_string(f);
        co->arg_names.push_back(arg_name);
    }

    // Konstanta
    uint32_t const_count = read_int(f);
    for(uint32_t i=0; i<const_count; i++) {
        co->constants.push_back(read_object(f));
    }

    // Instruksi
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
        case 2: { // Bool
            uint8_t val = read_byte(f);
            auto o = std::make_shared<FoxObject>(ObjectType::BOOLEAN);
            o->bool_val = (val == 1);
            return o;
        }
        case 3: { // Int
            uint32_t val = read_int(f);
            return make_int(val);
        }
        case 5: { // String
            std::string s = read_string(f);
            return make_str(s);
        }
        case 7: { // CodeObject
            return read_code_object(f);
        }
        default:
            std::cerr << "[VM] Tag " << (int)tag << " belum didukung sepenuhnya." << std::endl;
            return make_nil(); // Safe fallback for unhandled types
    }
}

void FoxVM::load_and_run(const std::string& filepath) {
    std::ifstream f(filepath, std::ios::binary);
    if (!f.is_open()) {
        std::cerr << "[VM] Gagal membuka file: " << filepath << std::endl;
        return;
    }

    // Header Check
    char magic[10];
    f.read(magic, 10);
    std::string magic_str(magic, 10);
    if (magic_str != "VZOEL FOXS") {
        std::cerr << "[VM] Magic bytes invalid! Bukan file .mvm yang valid." << std::endl;
        return;
    }

    // Skip Ver(1), Flags(1), TS(4) -> Total 6 bytes
    f.ignore(6);

    // Read Root Object
    FoxObjectPtr root = read_object(f);

    if (root->type == ObjectType::CODE_OBJECT) {
        std::cout << "[VM] Booting Morph Kernel (C++ Native)..." << std::endl;
        run_frame(root->code_val);
    } else {
        std::cerr << "[VM] Root object bukan CodeObject!" << std::endl;
    }
}

void FoxVM::run_frame(std::shared_ptr<CodeObject> code) {
    // Opcode Mapping (Sync with opkode.fox)
    // 1: PUSH_CONST
    // 2: POP
    // 23: LOAD_VAR
    // 53: PRINT (Note: Compiler emits PRINT for 'tulis', not CALL)
    // 47: CALL (Used if we call var)
    // 48: RET

    int pc = 0;
    while (pc < code->instructions.size()) {
        auto& inst = code->instructions[pc];
        uint8_t op = inst.first;
        FoxObjectPtr arg = inst.second;

        switch(op) {
            case 1: // PUSH_CONST (1)
                stack.push_back(arg);
                break;

            case 2: // POP (2)
                if (!stack.empty()) stack.pop_back();
                break;

            case 23: // LOAD_VAR (23)
                {
                    std::string name = arg->str_val;
                    if (globals.count(name)) {
                        stack.push_back(globals[name]);
                    } else {
                        // std::cerr << "[VM] Global not found: " << name << std::endl;
                        stack.push_back(make_nil());
                    }
                }
                break;

            case 53: // PRINT (53) - Native Opcode for 'tulis'
                // ArgCount is in operand?
                // Pernyataan.fox: Gen.emit(ctx, ctx.Op["PRINT"], panjang(node.argumen))
                // So Arg is Integer (Count).
                {
                    int count = arg->int_val;
                    // Pop N args
                    std::vector<FoxObjectPtr> print_args;
                    for(int i=0; i<count; i++) {
                        print_args.push_back(stack.back());
                        stack.pop_back();
                    }
                    // Print reverse? Stack LIFO.
                    // Tulis(A, B). Stack: [A, B].
                    // Pop 1: B. Pop 2: A.
                    // Vector: [B, A].
                    // Print A then B.
                    for(int i=count-1; i>=0; i--) {
                        builtin_tulis(print_args[i]);
                    }
                }
                break;

            case 47: // CALL (47)
                // Implement CALL if needed for "Hello World"
                // But 'tulis' is usually compiled to PRINT opcode (53) in Morph.
                // If it is compiled to CALL, we need this.
                {
                    int arg_count = arg->int_val;
                     for(int i=0; i<arg_count; i++) stack.pop_back(); // Pop args
                     stack.pop_back(); // Pop func
                     stack.push_back(make_nil()); // Push ret
                }
                break;

            case 48: // RET (48)
                return;

            default:
                // Ignore unknown opcodes for now (minimal VM)
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
    } else {
        std::cout << "<object>" << std::endl;
    }
}
