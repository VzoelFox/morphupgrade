use std::fs::{self, File};
use std::io::{self, Read, Write};
use std::net::{TcpStream, Shutdown};
use std::env;
use std::time::{SystemTime, UNIX_EPOCH};
use std::thread;
use std::time::Duration;
use std::rc::Rc;
use std::cell::RefCell;
use std::collections::HashMap;

// Constants
const MAGIC: &[u8] = b"VZOEL FOXS";

// --- Data Structures ---

#[derive(Debug, Clone)]
struct Function {
    name: String,
    code: Rc<CodeObject>,
    closure: Vec<Rc<RefCell<Constant>>>,
    globals: Rc<RefCell<HashMap<String, Constant>>>,
}

#[derive(Debug, Clone)]
struct Module {
    name: String,
    globals: Rc<RefCell<HashMap<String, Constant>>>,
}

#[derive(Debug)]
struct FileHandle(RefCell<Option<File>>);

#[derive(Debug, Clone)]
enum Constant {
    Nil,
    Boolean(bool),
    Integer(i32),
    Float(f64),
    String(String),
    List(Rc<RefCell<Vec<Constant>>>),
    Code(Rc<CodeObject>),
    Dict(Rc<RefCell<Vec<(Constant, Constant)>>>),
    Cell(Rc<RefCell<Constant>>),
    Function(Rc<Function>),
    Module(Rc<Module>),
    File(Rc<FileHandle>),
    Socket(Rc<RefCell<Option<TcpStream>>>),
}

// Implement PartialEq for Comparisons
impl PartialEq for Constant {
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (Constant::Nil, Constant::Nil) => true,
            (Constant::Boolean(a), Constant::Boolean(b)) => a == b,
            (Constant::Integer(a), Constant::Integer(b)) => a == b,
            (Constant::Float(a), Constant::Float(b)) => a == b,
            (Constant::String(a), Constant::String(b)) => a == b,
            (Constant::List(a), Constant::List(b)) => a == b,
            (Constant::Dict(a), Constant::Dict(b)) => a == b,
            (Constant::Cell(a), Constant::Cell(b)) => a == b,
            (Constant::Function(a), Constant::Function(b)) => Rc::ptr_eq(&a.code, &b.code), // Function equality based on code identity
            (Constant::Code(a), Constant::Code(b)) => Rc::ptr_eq(a, b),
            (Constant::Module(a), Constant::Module(b)) => Rc::ptr_eq(a, b),
            (Constant::File(a), Constant::File(b)) => Rc::ptr_eq(a, b),
            (Constant::Socket(a), Constant::Socket(b)) => Rc::ptr_eq(a, b),
            _ => false,
        }
    }
}

// Implement PartialOrd for Comparisons
impl PartialOrd for Constant {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        match (self, other) {
            (Constant::Integer(a), Constant::Integer(b)) => a.partial_cmp(b),
            (Constant::Float(a), Constant::Float(b)) => a.partial_cmp(b),
            (Constant::Integer(a), Constant::Float(b)) => (*a as f64).partial_cmp(b),
            (Constant::Float(a), Constant::Integer(b)) => a.partial_cmp(&(*b as f64)),
            _ => None,
        }
    }
}

impl Constant {
    fn type_name(&self) -> String {
         match self {
             Constant::Nil => "nil".to_string(),
             Constant::Boolean(_) => "boolean".to_string(),
             Constant::Integer(_) => "angka".to_string(),
             Constant::Float(_) => "angka".to_string(),
             Constant::String(_) => "teks".to_string(),
             Constant::List(_) => "list".to_string(),
             Constant::Dict(_) => "dict".to_string(),
             Constant::Code(_) => "kode".to_string(),
             Constant::Function(_) => "fungsi".to_string(),
             Constant::Module(_) => "modul".to_string(),
             Constant::File(_) => "file".to_string(),
             Constant::Socket(_) => "socket".to_string(),
             Constant::Cell(_) => "cell".to_string(),
         }
    }
}

#[derive(Debug, Clone)]
struct CodeObject {
    name: String,
    args: Vec<String>,
    constants: Vec<Constant>,
    instructions: Vec<(u8, Constant)>,
    free_vars: Vec<String>,
    cell_vars: Vec<String>,
}

#[derive(Debug, Clone)]
struct TryBlock {
    handler_pc: usize,
    stack_depth: usize,
}

#[derive(Debug, Clone)]
struct CallFrame {
    code: Rc<CodeObject>,
    pc: usize,
    locals: HashMap<String, Constant>,
    globals: Rc<RefCell<HashMap<String, Constant>>>,
    closure: Vec<Rc<RefCell<Constant>>>,
    try_stack: Vec<TryBlock>,
}

// --- VM Runtime ---

struct VM {
    frames: Vec<CallFrame>,
    stack: Vec<Constant>,
    modules: HashMap<String, Rc<Module>>,
    universals: HashMap<String, Constant>,
}

impl VM {
    fn throw_exception(&mut self, exc: Constant) {
         let mut handled = false;
         let mut catch_frame_idx = 0;
         let mut catch_block = TryBlock { handler_pc: 0, stack_depth: 0 };

         // 1. Search for a handler up the call stack
         for i in (0..self.frames.len()).rev() {
             let frame = &mut self.frames[i];
             if let Some(block) = frame.try_stack.pop() {
                 catch_frame_idx = i;
                 catch_block = block;
                 handled = true;
                 break;
             }
         }

         if handled {
             // 2. Unwind frames
             self.frames.truncate(catch_frame_idx + 1);

             // 3. Restore state in the catching frame
             let frame = self.frames.last_mut().unwrap();
             frame.pc = catch_block.handler_pc;

             // 4. Restore data stack
             self.stack.truncate(catch_block.stack_depth);
             self.stack.push(exc);
         } else {
             // Unhandled exception: Print and Exit
             println!("Panic: Unhandled Exception: {:?}", exc);
             println!("Traceback (most recent call last):");
             for f in &self.frames {
                 println!("  File \"{}\", line ?, in {}", "unknown", f.code.name);
             }
             std::process::exit(1);
         }
    }

    fn new() -> Self {
        let mut universals = HashMap::new();

        // 1. Inject 'argumen_sistem'
        // Skip executable name (args[0]) to match Python sys.argv behavior where argv[0] is script name
        let args: Vec<Constant> = env::args().skip(1).map(Constant::String).collect();
        let args_list = Constant::List(Rc::new(RefCell::new(args)));
        universals.insert("argumen_sistem".to_string(), args_list);

        // 2. Inject 'tulis'
        let tulis_co = CodeObject {
            name: "tulis".to_string(), args: vec!["msg".to_string()], constants: vec![Constant::Nil],
            instructions: vec![(25, Constant::String("msg".to_string())), (53, Constant::Integer(1)), (1, Constant::Nil), (48, Constant::Nil)],
            free_vars: Vec::new(), cell_vars: Vec::new(),
        };
        universals.insert("tulis".to_string(), Constant::Code(Rc::new(tulis_co)));

        // 3. Inject 'teks'
        let teks_co = CodeObject {
            name: "teks".to_string(), args: vec!["obj".to_string()], constants: vec![],
            instructions: vec![(25, Constant::String("obj".to_string())), (64, Constant::Nil), (48, Constant::Nil)],
            free_vars: Vec::new(), cell_vars: Vec::new(),
        };
        universals.insert("teks".to_string(), Constant::Code(Rc::new(teks_co)));

        // 3b. Inject '_str_builtin' (Alias for STR opcode, used by stdlib/core)
        let str_builtin_co = CodeObject {
            name: "_str_builtin".to_string(), args: vec!["obj".to_string()], constants: vec![],
            instructions: vec![(25, Constant::String("obj".to_string())), (64, Constant::Nil), (48, Constant::Nil)],
            free_vars: Vec::new(), cell_vars: Vec::new(),
        };
        universals.insert("_str_builtin".to_string(), Constant::Code(Rc::new(str_builtin_co)));

        // 4. Inject 'tipe'
        let tipe_co = CodeObject {
            name: "tipe".to_string(), args: vec!["obj".to_string()], constants: vec![],
            instructions: vec![(25, Constant::String("obj".to_string())), (63, Constant::Nil), (48, Constant::Nil)],
            free_vars: Vec::new(), cell_vars: Vec::new(),
        };
        universals.insert("tipe".to_string(), Constant::Code(Rc::new(tipe_co)));

        // 5. Inject String Intrinsics
        // _intrinsik_str_kecil (75)
        let str_lower_co = CodeObject {
            name: "_intrinsik_str_kecil".to_string(), args: vec!["s".to_string()], constants: vec![],
            instructions: vec![(25, Constant::String("s".to_string())), (75, Constant::Nil), (48, Constant::Nil)],
            free_vars: Vec::new(), cell_vars: Vec::new(),
        };
        universals.insert("_intrinsik_str_kecil".to_string(), Constant::Code(Rc::new(str_lower_co)));

        // _intrinsik_str_besar (76)
        let str_upper_co = CodeObject {
            name: "_intrinsik_str_besar".to_string(), args: vec!["s".to_string()], constants: vec![],
            instructions: vec![(25, Constant::String("s".to_string())), (76, Constant::Nil), (48, Constant::Nil)],
            free_vars: Vec::new(), cell_vars: Vec::new(),
        };
        universals.insert("_intrinsik_str_besar".to_string(), Constant::Code(Rc::new(str_upper_co)));

        // _intrinsik_str_temukan (77)
        let str_find_co = CodeObject {
            name: "_intrinsik_str_temukan".to_string(), args: vec!["h".to_string(), "n".to_string()], constants: vec![],
            instructions: vec![(25, Constant::String("h".to_string())), (25, Constant::String("n".to_string())), (77, Constant::Nil), (48, Constant::Nil)],
            free_vars: Vec::new(), cell_vars: Vec::new(),
        };
        universals.insert("_intrinsik_str_temukan".to_string(), Constant::Code(Rc::new(str_find_co)));

        // _intrinsik_str_ganti (78)
        let str_repl_co = CodeObject {
            name: "_intrinsik_str_ganti".to_string(), args: vec!["h".to_string(), "o".to_string(), "n".to_string()], constants: vec![],
            instructions: vec![(25, Constant::String("h".to_string())), (25, Constant::String("o".to_string())), (25, Constant::String("n".to_string())), (78, Constant::Nil), (48, Constant::Nil)],
            free_vars: Vec::new(), cell_vars: Vec::new(),
        };
        universals.insert("_intrinsik_str_ganti".to_string(), Constant::Code(Rc::new(str_repl_co)));

        let mut modules = HashMap::new();

        // --- Inject Module: _backend ---
        // Ini adalah modul internal yang menyediakan akses ke sistem operasi
        let mut backend_globals = HashMap::new();

        // Helper untuk membuat fungsi wrapper opcode sederhana (arg -> OP -> ret)
        let make_op_fn = |name: &str, op: u8, args: Vec<&str>| -> Constant {
             let mut instrs = Vec::new();
             for arg in &args {
                 instrs.push((25, Constant::String(arg.to_string()))); // LOAD_LOCAL arg
             }
             instrs.push((op, Constant::Nil));
             instrs.push((48, Constant::Nil)); // RET

             let co = CodeObject {
                 name: name.to_string(),
                 args: args.iter().map(|s| s.to_string()).collect(),
                 constants: vec![],
                 instructions: instrs,
                 free_vars: vec![],
                 cell_vars: vec![],
             };
             Constant::Code(Rc::new(co))
        };

        // File System
        backend_globals.insert("fs_buka".to_string(), make_op_fn("fs_buka", 87, vec!["path", "mode"]));
        backend_globals.insert("fs_baca".to_string(), make_op_fn("fs_baca", 88, vec!["handle", "size"]));
        backend_globals.insert("fs_tulis".to_string(), make_op_fn("fs_tulis", 89, vec!["handle", "content"]));
        backend_globals.insert("fs_tutup".to_string(), make_op_fn("fs_tutup", 90, vec!["handle"]));
        backend_globals.insert("fs_ada".to_string(), make_op_fn("fs_ada", 91, vec!["path"]));
        backend_globals.insert("fs_hapus".to_string(), make_op_fn("fs_hapus", 92, vec!["path"]));
        backend_globals.insert("fs_mkdir".to_string(), make_op_fn("fs_mkdir", 93, vec!["path"]));
        backend_globals.insert("fs_listdir".to_string(), make_op_fn("fs_listdir", 94, vec!["path"]));
        backend_globals.insert("fs_cwd".to_string(), make_op_fn("fs_cwd", 95, vec![]));

        // System
        backend_globals.insert("sys_waktu".to_string(), make_op_fn("sys_waktu", 96, vec![]));
        backend_globals.insert("sys_tidur".to_string(), make_op_fn("sys_tidur", 97, vec!["detik"]));
        backend_globals.insert("sys_keluar".to_string(), make_op_fn("sys_keluar", 98, vec!["kode"]));
        backend_globals.insert("sys_platform".to_string(), make_op_fn("sys_platform", 99, vec![]));

        // Network (100-104)
        backend_globals.insert("net_konek".to_string(), make_op_fn("net_konek", 100, vec!["host", "port"]));
        backend_globals.insert("net_kirim".to_string(), make_op_fn("net_kirim", 101, vec!["socket", "data"]));
        backend_globals.insert("net_terima".to_string(), make_op_fn("net_terima", 102, vec!["socket", "size"]));
        backend_globals.insert("net_tutup".to_string(), make_op_fn("net_tutup", 103, vec!["socket"]));

        // Converters (Reuse existing opcodes if possible or fallback)
        // LEN (62), STR (64) are intrinsics, but we can wrap them if needed.
        // For now, syscalls.fox handles sys_host_len/str via _py, but here we should point them to opcodes.
        backend_globals.insert("conv_len".to_string(), make_op_fn("conv_len", 62, vec!["obj"]));
        backend_globals.insert("conv_str".to_string(), make_op_fn("conv_str", 64, vec!["obj"]));

        modules.insert("_backend".to_string(), Rc::new(Module {
            name: "_backend".to_string(),
            globals: Rc::new(RefCell::new(backend_globals))
        }));

        VM {
            frames: Vec::new(),
            stack: Vec::new(),
            modules,
            universals
        }
    }

    // Helper: Run a code object in a specific global scope
    fn run_code(&mut self, code: Rc<CodeObject>, globals: Rc<RefCell<HashMap<String, Constant>>>) {
        let root_frame = CallFrame {
            code,
            pc: 0,
            locals: HashMap::new(),
            globals,
            closure: Vec::new(),
            try_stack: Vec::new(),
        };

        let start_depth = self.frames.len();
        self.frames.push(root_frame);

        while self.frames.len() > start_depth {
            if self.frames.is_empty() { break; }

            let (op, arg) = {
                let frame = self.frames.last_mut().unwrap();
                if frame.pc >= frame.code.instructions.len() {
                    self.frames.pop();
                    continue;
                }
                let instr = &frame.code.instructions[frame.pc];
                frame.pc += 1;
                (instr.0, instr.1.clone())
            };

            match op {
                1 => self.stack.push(arg.clone()),
                2 => { if self.stack.pop().is_none() { panic!("Stack underflow POP"); } },
                3 => {
                    if let Some(val) = self.stack.last() { self.stack.push(val.clone()); }
                    else { panic!("Stack underflow DUP"); }
                },
                // Variable Ops (23-26) ... (Same as Patch 11)
                23 => {
                    if let Constant::String(name) = arg {
                        let mut val = None;
                        if let Some(frame) = self.frames.last() {
                            if let Some(v) = frame.locals.get(&name) { val = Some(v.clone()); }
                            else if let Some(v) = frame.globals.borrow().get(&name) { val = Some(v.clone()); }
                            else if let Some(v) = self.universals.get(&name) { val = Some(v.clone()); }
                        }
                        if let Some(v) = val {
                            if let Constant::Cell(c) = v { self.stack.push(c.borrow().clone()); }
                            else { self.stack.push(v); }
                        } else { panic!("Variable not found: {}", name); }
                    } else { panic!("LOAD_VAR"); }
                },
                24 => {
                    if let Constant::String(name) = arg {
                        let val = self.stack.pop().expect("Stack");
                        if let Some(frame) = self.frames.last() { frame.globals.borrow_mut().insert(name.clone(), val); }
                    } else { panic!("STORE_VAR"); }
                },
                25 => {
                    if let Constant::String(name) = arg {
                        if let Some(frame) = self.frames.last() {
                            if let Some(v) = frame.locals.get(&name) {
                                if let Constant::Cell(c) = v { self.stack.push(c.borrow().clone()); }
                                else { self.stack.push(v.clone()); }
                            } else { panic!("Local not found: {}", name); }
                        }
                    }
                },
                26 => {
                    if let Constant::String(name) = arg {
                         let val = self.stack.pop().expect("Stack");
                         if let Some(frame) = self.frames.last_mut() {
                             if let Some(Constant::Cell(c)) = frame.locals.get(&name).cloned() { *c.borrow_mut() = val; }
                             else { frame.locals.insert(name.clone(), val); }
                         }
                    }
                },
                // Data Ops (27-30) ... (Same)
                27 => {
                    let count = if let Constant::Integer(c) = arg { c as usize } else { 0 };
                    let mut list = Vec::new();
                    for _ in 0..count { list.push(self.stack.pop().expect("Stack")); }
                    list.reverse();
                    self.stack.push(Constant::List(Rc::new(RefCell::new(list))));
                },
                28 => {
                     let count = if let Constant::Integer(c) = arg { c as usize } else { 0 };
                     let mut dict = Vec::new();
                     for _ in 0..count { let v = self.stack.pop().expect("Stack"); let k = self.stack.pop().expect("Stack"); dict.push((k, v)); }
                     dict.reverse();
                     self.stack.push(Constant::Dict(Rc::new(RefCell::new(dict))));
                },
                29 => { // LOAD_INDEX
                     let index = self.stack.pop().expect("Stack");
                     let obj = self.stack.pop().expect("Stack");
                     match obj {
                         Constant::List(l) => {
                             let list = l.borrow();
                             if let Constant::Integer(i) = index {
                                 if i >= 0 && (i as usize) < list.len() { self.stack.push(list[i as usize].clone()); }
                                 else { panic!("Index error"); }
                             }
                         },
                         Constant::Dict(d) => {
                             let dict = d.borrow();
                             let mut found = false;
                             for (k, v) in dict.iter() { if k == &index { self.stack.push(v.clone()); found = true; break; } }
                             if !found { panic!("Key error: {:?}", index); }
                         },
                         Constant::String(s) => {
                             if let Constant::Integer(i) = index {
                                 if i >= 0 && (i as usize) < s.len() { self.stack.push(Constant::String(s.chars().nth(i as usize).unwrap().to_string())); }
                             }
                         },
                         _ => panic!("Not subscriptable"),
                     }
                },
                30 => { // STORE_INDEX
                    let val = self.stack.pop().expect("Stack");
                    let index = self.stack.pop().expect("Stack");
                    let obj = self.stack.pop().expect("Stack");
                    match obj {
                        Constant::List(l) => {
                            let mut list = l.borrow_mut();
                            if let Constant::Integer(i) = index { if i >= 0 && (i as usize) < list.len() { list[i as usize] = val; } }
                        },
                        Constant::Dict(d) => {
                            let mut dict = d.borrow_mut();
                            let mut found = false;
                            for (k, v) in dict.iter_mut() { if k == &index { *v = val.clone(); found = true; break; } }
                            if !found { dict.push((index, val)); }
                        },
                        _ => panic!("Not mutable"),
                    }
                },
                38 => { // LOAD_ATTR
                    let name = if let Constant::String(s) = arg { s } else { panic!("Arg"); };
                    let obj = self.stack.pop().expect("Stack");
                    match obj {
                        Constant::Code(_) => { if name == "code" { self.stack.push(obj); } else { panic!("Attr"); } },
                        Constant::Module(m) => {
                            if let Some(v) = m.globals.borrow().get(&name) { self.stack.push(v.clone()); }
                            else { panic!("Attribute {} not found in module {}", name, m.name); }
                        },
                        _ => panic!("Attr not supported"),
                    }
                },
                // Math & Logic
                4 => { // ADD
                    let b = self.stack.pop().unwrap(); let a = self.stack.pop().unwrap();
                    match (&a, &b) {
                         (Constant::Integer(ia), Constant::Integer(ib)) => self.stack.push(Constant::Integer(ia + ib)),
                         (Constant::Float(fa), Constant::Float(fb)) => self.stack.push(Constant::Float(fa + fb)),
                         (Constant::Integer(ia), Constant::Float(fb)) => self.stack.push(Constant::Float((*ia as f64) + fb)),
                         (Constant::Float(fa), Constant::Integer(ib)) => self.stack.push(Constant::Float(fa + (*ib as f64))),
                         (Constant::String(sa), Constant::String(sb)) => self.stack.push(Constant::String(sa.clone() + sb)),
                         _ => {
                             let msg = format!("TipeError: Operasi '+' tidak valid untuk '{}' dan '{}'", a.type_name(), b.type_name());
                             self.throw_exception(Constant::String(msg));
                         }
                    }
                },
                5 => { // SUB
                    let b = self.stack.pop().unwrap(); let a = self.stack.pop().unwrap();
                    match (&a, &b) {
                         (Constant::Integer(ia), Constant::Integer(ib)) => self.stack.push(Constant::Integer(ia - ib)),
                         (Constant::Float(fa), Constant::Float(fb)) => self.stack.push(Constant::Float(fa - fb)),
                         (Constant::Integer(ia), Constant::Float(fb)) => self.stack.push(Constant::Float((*ia as f64) - fb)),
                         (Constant::Float(fa), Constant::Integer(ib)) => self.stack.push(Constant::Float(fa - (*ib as f64))),
                         _ => {
                             let msg = format!("TipeError: Operasi '-' tidak valid untuk '{}' dan '{}'", a.type_name(), b.type_name());
                             self.throw_exception(Constant::String(msg));
                         }
                    }
                },
                6 => { // MUL
                    let b = self.stack.pop().unwrap(); let a = self.stack.pop().unwrap();
                    match (&a, &b) {
                         (Constant::Integer(ia), Constant::Integer(ib)) => self.stack.push(Constant::Integer(ia * ib)),
                         (Constant::Float(fa), Constant::Float(fb)) => self.stack.push(Constant::Float(fa * fb)),
                         (Constant::Integer(ia), Constant::Float(fb)) => self.stack.push(Constant::Float((*ia as f64) * fb)),
                         (Constant::Float(fa), Constant::Integer(ib)) => self.stack.push(Constant::Float(fa * (*ib as f64))),
                         _ => {
                             let msg = format!("TipeError: Operasi '*' tidak valid untuk '{}' dan '{}'", a.type_name(), b.type_name());
                             self.throw_exception(Constant::String(msg));
                         }
                    }
                },
                7 => { // DIV
                    let b = self.stack.pop().unwrap(); let a = self.stack.pop().unwrap();
                    match (&a, &b) {
                         (Constant::Integer(ia), Constant::Integer(ib)) => {
                             if *ib == 0 { self.throw_exception(Constant::String("Error: Pembagian dengan nol".to_string())); }
                             else { self.stack.push(Constant::Float((*ia as f64) / (*ib as f64))); }
                         },
                         (Constant::Float(fa), Constant::Float(fb)) => {
                             if *fb == 0.0 { self.throw_exception(Constant::String("Error: Pembagian dengan nol".to_string())); }
                             else { self.stack.push(Constant::Float(fa / fb)); }
                         },
                         (Constant::Integer(ia), Constant::Float(fb)) => {
                             if *fb == 0.0 { self.throw_exception(Constant::String("Error: Pembagian dengan nol".to_string())); }
                             else { self.stack.push(Constant::Float((*ia as f64) / fb)); }
                         },
                         (Constant::Float(fa), Constant::Integer(ib)) => {
                             if *ib == 0 { self.throw_exception(Constant::String("Error: Pembagian dengan nol".to_string())); }
                             else { self.stack.push(Constant::Float(fa / (*ib as f64))); }
                         },
                         _ => {
                             let msg = format!("TipeError: Operasi '/' tidak valid untuk '{}' dan '{}'", a.type_name(), b.type_name());
                             self.throw_exception(Constant::String(msg));
                         }
                    }
                },
                8 => { // MOD
                    let b = self.stack.pop().unwrap(); let a = self.stack.pop().unwrap();
                    match (&a, &b) {
                         (Constant::Integer(ia), Constant::Integer(ib)) => {
                             if *ib == 0 { self.throw_exception(Constant::String("Error: Modulo dengan nol".to_string())); }
                             else { self.stack.push(Constant::Integer(ia % ib)); }
                         },
                         _ => {
                             let msg = format!("TipeError: Operasi '%' tidak valid untuk '{}' dan '{}'", a.type_name(), b.type_name());
                             self.throw_exception(Constant::String(msg));
                         }
                    }
                },
                9 => { let b = self.stack.pop().unwrap(); let a = self.stack.pop().unwrap(); self.stack.push(Constant::Boolean(a == b)); },
                44 => { if let Constant::Integer(target) = arg { self.frames.last_mut().unwrap().pc = target as usize; } else { panic!("JMP"); } },
                45 => {
                    let condition = self.stack.pop().expect("Stack");
                    let is_true = match condition { Constant::Boolean(b) => b, Constant::Nil => false, Constant::Integer(i) => i != 0, _ => true };
                    if !is_true { if let Constant::Integer(target) = arg { self.frames.last_mut().unwrap().pc = target as usize; } }
                },
                // IMPORT (52)
                52 => {
                    let path = if let Constant::String(s) = arg { s } else { panic!("Import"); };
                    // println!("DEBUG: Importing '{}'", path);
                    if let Some(m) = self.modules.get(&path) { self.stack.push(Constant::Module(m.clone())); }
                    else {
                        // Strategy: Try path.mvm, then path.fox.mvm
                        let mut filename = path.clone() + ".mvm";
                        if !std::path::Path::new(&filename).exists() {
                            filename = path.clone() + ".fox.mvm";
                        }

                        let mut file = File::open(&filename).expect(&format!("Module file not found: {}", filename));
                        let mut buffer = Vec::new();
                        file.read_to_end(&mut buffer).unwrap();
                        let mut reader = Reader::new(buffer);
                        reader.read_bytes(16);
                        if let Some(Constant::Code(code_rc)) = reader.read_constant() {
                            let globals = Rc::new(RefCell::new(HashMap::new()));

                            // Inject universals to module globals (mimic Python VM behavior)
                            // This allows 'from core import tulis' to work even if tulis is built-in
                            for (k, v) in self.universals.iter() {
                                globals.borrow_mut().insert(k.clone(), v.clone());
                            }

                            let module = Rc::new(Module { name: path.clone(), globals: globals.clone() });
                            self.modules.insert(path.clone(), module.clone());
                            self.run_code(code_rc, globals);
                            if self.stack.pop().is_none() {} // Pop RetVal
                            self.stack.push(Constant::Module(module));
                        } else { panic!("Invalid module"); }
                    }
                },
                61 => { // IMPORT_NATIVE
                    let name = if let Constant::String(s) = arg { s } else { panic!("ImportNative"); };
                    if let Some(m) = self.modules.get(&name) {
                        self.stack.push(Constant::Module(m.clone()));
                    } else {
                        // Native modules like '_backend' should be pre-loaded in VM::new()
                        panic!("Native module not found: {}", name);
                    }
                },
                // IO Opcodes
                87 => { // IO_OPEN
                    let mode_v = self.stack.pop().unwrap();
                    let path_v = self.stack.pop().unwrap();
                    if let (Constant::String(path), Constant::String(_mode)) = (path_v, mode_v) {
                        // Handle "wb" as "w" for Rust
                        let f = if _mode == "w" || _mode == "wb" { File::create(path) } else { File::open(path) };
                        match f {
                            Ok(file) => self.stack.push(Constant::File(Rc::new(FileHandle(RefCell::new(Some(file)))))),
                            Err(_) => self.stack.push(Constant::Nil),
                        }
                    } else { self.stack.push(Constant::Nil); }
                },
                88 => { // IO_READ
                    let _size_v = self.stack.pop().unwrap();
                    let handle = self.stack.pop().unwrap();
                    if let Constant::File(fh) = handle {
                        let mut file_opt = fh.0.borrow_mut();
                        if let Some(ref mut file) = *file_opt {
                            let mut buf = String::new();
                            match file.read_to_string(&mut buf) {
                                Ok(_) => self.stack.push(Constant::String(buf)),
                                Err(_) => self.stack.push(Constant::Nil),
                            }
                        } else { self.stack.push(Constant::Nil); }
                    } else { self.stack.push(Constant::Nil); }
                },
                89 => { // IO_WRITE
                    let content = self.stack.pop().unwrap();
                    let handle = self.stack.pop().unwrap();
                    if let Constant::File(fh) = handle {
                        let mut file_opt = fh.0.borrow_mut();
                        if let Some(ref mut file) = *file_opt {
                            let res = match content {
                                Constant::String(s) => file.write_all(s.as_bytes()),
                                Constant::List(l) => {
                                    let list = l.borrow();
                                    let mut bytes = Vec::new();
                                    for item in list.iter() {
                                        if let Constant::Integer(b) = item { bytes.push(*b as u8); }
                                    }
                                    file.write_all(&bytes)
                                },
                                _ => Err(io::Error::new(io::ErrorKind::InvalidInput, "Invalid content")),
                            };
                            match res {
                                Ok(_) => self.stack.push(Constant::Nil),
                                Err(_) => self.stack.push(Constant::Boolean(false)),
                            }
                        } else { self.stack.push(Constant::Boolean(false)); }
                    } else { self.stack.push(Constant::Boolean(false)); }
                },
                90 => { // IO_CLOSE
                    let handle = self.stack.pop().unwrap();
                    if let Constant::File(fh) = handle { *fh.0.borrow_mut() = None; self.stack.push(Constant::Nil); }
                },
                // System Opcodes (91-99) for _sys_inti
                91 => { // SYS_EXISTS (path)
                     let path = if let Constant::String(s) = self.stack.pop().unwrap() { s } else { panic!("SYS_EXISTS arg"); };
                     self.stack.push(Constant::Boolean(std::path::Path::new(&path).exists()));
                },
                92 => { // SYS_REMOVE (path)
                     let path = if let Constant::String(s) = self.stack.pop().unwrap() { s } else { panic!("SYS_REMOVE arg"); };
                     if let Err(_) = fs::remove_file(&path) { /* Ignore error or panic? For now ignore */ }
                     self.stack.push(Constant::Nil);
                },
                93 => { // SYS_MKDIR (path)
                     let path = if let Constant::String(s) = self.stack.pop().unwrap() { s } else { panic!("SYS_MKDIR arg"); };
                     let _ = fs::create_dir_all(&path);
                     self.stack.push(Constant::Nil);
                },
                94 => { // SYS_LISTDIR (path)
                     let path = if let Constant::String(s) = self.stack.pop().unwrap() { s } else { panic!("SYS_LISTDIR arg"); };
                     let mut list = Vec::new();
                     if let Ok(entries) = fs::read_dir(path) {
                         for entry in entries {
                             if let Ok(entry) = entry {
                                 if let Ok(name) = entry.file_name().into_string() {
                                     list.push(Constant::String(name));
                                 }
                             }
                         }
                     }
                     self.stack.push(Constant::List(Rc::new(RefCell::new(list))));
                },
                95 => { // SYS_CWD
                    if let Ok(path) = env::current_dir() {
                        self.stack.push(Constant::String(path.to_string_lossy().into_owned()));
                    } else {
                        self.stack.push(Constant::String(".".to_string()));
                    }
                },
                96 => { // SYS_TIME
                    let start = SystemTime::now();
                    let since_the_epoch = start.duration_since(UNIX_EPOCH).expect("Time went backwards");
                    self.stack.push(Constant::Float(since_the_epoch.as_secs_f64()));
                },
                97 => { // SYS_SLEEP (seconds)
                    let sec = if let Constant::Integer(i) = self.stack.pop().unwrap() { i as f64 }
                              else if let Constant::Float(f) = self.stack.pop().unwrap() { f }
                              else { 0.0 };
                    thread::sleep(Duration::from_secs_f64(sec));
                    self.stack.push(Constant::Nil);
                },
                98 => { // SYS_EXIT (code)
                    let code = if let Constant::Integer(i) = self.stack.pop().unwrap() { i } else { 0 };
                    std::process::exit(code);
                },
                99 => { // SYS_PLATFORM
                    self.stack.push(Constant::String("rust_vm".to_string()));
                },

                // Network Opcodes (100+)
                100 => { // NET_CONNECT (host, port)
                    let port_v = self.stack.pop().unwrap();
                    let host_v = self.stack.pop().unwrap();
                    if let (Constant::String(host), Constant::Integer(port)) = (host_v, port_v) {
                        match TcpStream::connect(format!("{}:{}", host, port)) {
                            Ok(stream) => self.stack.push(Constant::Socket(Rc::new(RefCell::new(Some(stream))))),
                            Err(_) => self.stack.push(Constant::Nil),
                        }
                    } else { self.stack.push(Constant::Nil); }
                },
                101 => { // NET_SEND (socket, data)
                    let data = self.stack.pop().unwrap();
                    let socket = self.stack.pop().unwrap();
                    if let Constant::Socket(s_rc) = socket {
                        if let Some(ref mut stream) = *s_rc.borrow_mut() {
                             let res = match data {
                                 Constant::String(s) => stream.write_all(s.as_bytes()),
                                 Constant::List(l) => {
                                     let list = l.borrow();
                                     let mut bytes = Vec::new();
                                     for item in list.iter() {
                                         if let Constant::Integer(b) = item { bytes.push(*b as u8); }
                                     }
                                     stream.write_all(&bytes)
                                 },
                                 _ => Err(io::Error::new(io::ErrorKind::InvalidInput, "Invalid Data")),
                             };
                             match res {
                                 Ok(_) => self.stack.push(Constant::Nil),
                                 Err(_) => self.stack.push(Constant::Boolean(false)),
                             }
                        } else { self.stack.push(Constant::Boolean(false)); }
                    } else { self.stack.push(Constant::Boolean(false)); }
                },
                102 => { // NET_RECV (socket, size)
                    let size_v = self.stack.pop().unwrap();
                    let socket = self.stack.pop().unwrap();
                    let size = if let Constant::Integer(i) = size_v { i as usize } else { 4096 };
                    if let Constant::Socket(s_rc) = socket {
                        if let Some(ref mut stream) = *s_rc.borrow_mut() {
                            let mut buf = vec![0; size];
                            match stream.read(&mut buf) {
                                Ok(n) => {
                                    buf.truncate(n);
                                    self.stack.push(Constant::String(String::from_utf8_lossy(&buf).into_owned()));
                                },
                                Err(_) => self.stack.push(Constant::Nil),
                            }
                        } else { self.stack.push(Constant::Nil); }
                    } else { self.stack.push(Constant::Nil); }
                },
                103 => { // NET_CLOSE (socket)
                    let socket = self.stack.pop().unwrap();
                    if let Constant::Socket(s_rc) = socket {
                        // Drop the stream
                        *s_rc.borrow_mut() = None;
                        self.stack.push(Constant::Nil);
                    } else { self.stack.push(Constant::Nil); }
                },

                // --- Patch 12: New Opcodes ---
                59 => { // SLICE (obj, start, end)
                    let end_v = self.stack.pop().expect("Stack");
                    let start_v = self.stack.pop().expect("Stack");
                    let obj = self.stack.pop().expect("Stack");

                    match obj {
                        Constant::String(s) => {
                            let len = s.len() as i32;
                            let start = if let Constant::Integer(i) = start_v { if i < 0 { len + i } else { i } } else { 0 };
                            let end = if let Constant::Integer(i) = end_v { if i < 0 { len + i } else { i } } else { len };

                            // Clamp
                            let start = start.max(0).min(len) as usize;
                            let end = end.max(0).min(len) as usize;
                            let end = end.max(start);

                            self.stack.push(Constant::String(s[start..end].to_string()));
                        },
                        Constant::List(l_rc) => {
                            let list = l_rc.borrow();
                            let len = list.len() as i32;
                            let start = if let Constant::Integer(i) = start_v { if i < 0 { len + i } else { i } } else { 0 };
                            let end = if let Constant::Integer(i) = end_v { if i < 0 { len + i } else { i } } else { len };

                            let start = start.max(0).min(len) as usize;
                            let end = end.max(0).min(len) as usize;
                            let end = end.max(start);

                            let slice = list[start..end].to_vec();
                            self.stack.push(Constant::List(Rc::new(RefCell::new(slice))));
                        },
                        _ => panic!("SLICE not supported on this type"),
                    }
                },
                75 => { // STR_LOWER
                    let v = self.stack.pop().unwrap();
                    if let Constant::String(s) = v { self.stack.push(Constant::String(s.to_lowercase())); }
                    else { panic!("STR_LOWER expects String"); }
                },
                76 => { // STR_UPPER
                    let v = self.stack.pop().unwrap();
                    if let Constant::String(s) = v { self.stack.push(Constant::String(s.to_uppercase())); }
                    else { panic!("STR_UPPER expects String"); }
                },
                77 => { // STR_FIND (haystack, needle)
                    let needle = self.stack.pop().unwrap();
                    let haystack = self.stack.pop().unwrap();
                    if let (Constant::String(h), Constant::String(n)) = (haystack, needle) {
                        match h.find(&n) {
                            Some(idx) => self.stack.push(Constant::Integer(idx as i32)),
                            None => self.stack.push(Constant::Integer(-1)),
                        }
                    } else { panic!("STR_FIND expects String"); }
                },
                78 => { // STR_REPLACE (haystack, old, new)
                    let new_s = self.stack.pop().unwrap();
                    let old_s = self.stack.pop().unwrap();
                    let haystack = self.stack.pop().unwrap();
                    if let (Constant::String(h), Constant::String(o), Constant::String(n)) = (haystack, old_s, new_s) {
                        self.stack.push(Constant::String(h.replace(&o, &n)));
                    } else { panic!("STR_REPLACE expects Strings"); }
                },
                // Functions
                62 => { // LEN
                    let obj = self.stack.pop().expect("Stack");
                    match obj {
                        Constant::String(s) => self.stack.push(Constant::Integer(s.len() as i32)),
                        Constant::List(l) => self.stack.push(Constant::Integer(l.borrow().len() as i32)),
                        Constant::Dict(d) => self.stack.push(Constant::Integer(d.borrow().len() as i32)),
                        _ => panic!("LEN not supported on this type"),
                    }
                },
                63 => { // TYPE
                     let obj = self.stack.pop().expect("Stack");
                     let type_name = match obj {
                         Constant::Nil => "nil",
                         Constant::Boolean(_) => "boolean", // or "logika"?
                         Constant::Integer(_) => "angka",
                         Constant::Float(_) => "angka",
                         Constant::String(_) => "teks",
                         Constant::List(_) => "list", // or "senarai"?
                         Constant::Dict(_) => "dict", // or "kamus"?
                         Constant::Code(_) => "kode",
                         Constant::Function(_) => "fungsi",
                         Constant::Module(_) => "modul",
                         Constant::File(_) => "file",
                         Constant::Socket(_) => "socket",
                         Constant::Cell(_) => "cell",
                     };
                     self.stack.push(Constant::String(type_name.to_string()));
                },
                60 => { // BUILD_FUNCTION
                    let func_def = self.stack.pop().expect("Stack");
                    if let Constant::Dict(entries_rc) = func_def {
                         let entries = entries_rc.borrow();
                         let mut name = String::new();
                         let mut args = Vec::new();
                         let mut instructions = Vec::new();
                         let mut free_vars = Vec::new();
                         let mut cell_vars = Vec::new();

                         for (k, v) in entries.iter() {
                             if let Constant::String(k_str) = k {
                                 if k_str == "nama" { if let Constant::String(n) = v { name = n.clone(); } }
                                 else if k_str == "args" { if let Constant::List(l) = v { for x in l.borrow().iter() { if let Constant::String(s) = x { args.push(s.clone()); } } } }
                                 else if k_str == "instruksi" { if let Constant::List(l) = v { for instr in l.borrow().iter() { if let Constant::List(pair) = instr { let p = pair.borrow(); let op = if let Constant::Integer(o) = p[0] { o as u8 } else { 0 }; instructions.push((op, p[1].clone())); } } } }
                                 else if k_str == "free_vars" { if let Constant::List(l) = v { for x in l.borrow().iter() { if let Constant::String(s) = x { free_vars.push(s.clone()); } } } }
                                 else if k_str == "cell_vars" { if let Constant::List(l) = v { for x in l.borrow().iter() { if let Constant::String(s) = x { cell_vars.push(s.clone()); } } } }
                             }
                         }
                         let co = CodeObject { name, args, constants: Vec::new(), instructions, free_vars, cell_vars };
                         // Patch: Wrap in Function to capture globals (Lexical Scoping)
                         let globals = self.frames.last().unwrap().globals.clone();
                         let func = Function { name: co.name.clone(), code: Rc::new(co), closure: Vec::new(), globals };
                         self.stack.push(Constant::Function(Rc::new(func)));
                    }
                },
                47 => { // CALL
                     let arg_count = if let Constant::Integer(c) = arg { c as usize } else { panic!("CALL arg"); };
                     let mut args = Vec::new();
                     for _ in 0..arg_count { args.push(self.stack.pop().expect("Stack")); }
                     args.reverse();

                     let func_obj = self.stack.pop().expect("Stack");
                     // Determine code, closure, AND globals for the new frame
                     let (co, closure, globals) = match func_obj {
                         Constant::Code(c) => {
                             // Raw CodeObject call: Inherit globals from caller (Dynamic Scoping / Fallback)
                             // This is risky but standard for raw code execution not wrapped in a Function
                             (c, Vec::new(), self.frames.last().unwrap().globals.clone())
                         },
                         Constant::Function(f) => {
                             // Function call: Use the globals captured at definition time (Lexical Scoping)
                             (f.code.clone(), f.closure.clone(), f.globals.clone())
                         },
                         _ => panic!("CALL target invalid: {:?}", func_obj),
                     };

                     let mut locals = HashMap::new();
                     for cell in &co.cell_vars { locals.insert(cell.clone(), Constant::Cell(Rc::new(RefCell::new(Constant::Nil)))); }
                     for (name, val) in co.args.iter().zip(args.into_iter()) {
                         if locals.contains_key(name) {
                             if let Some(Constant::Cell(c)) = locals.get(name) { *c.borrow_mut() = val; }
                         } else { locals.insert(name.clone(), val); }
                     }
                     for (i, name) in co.free_vars.iter().enumerate() {
                         locals.insert(name.clone(), Constant::Cell(closure[i].clone()));
                     }

                     let frame = CallFrame {
                         code: co,
                         pc: 0,
                         locals,
                         globals, // Use the resolved globals
                         closure,
                         try_stack: Vec::new(),
                     };
                     self.frames.push(frame);
                },
                48 => { self.frames.pop(); },
                49 => { // PUSH_TRY (target)
                    if let Constant::Integer(offset) = arg {
                         let frame = self.frames.last_mut().unwrap();
                         let target = frame.pc + (offset as usize); // Relative Jump? No, JMP is absolute usually.
                         // But compiler emits absolute index for JMP, let's assume absolute target for now.
                         // Wait, standard PUSH_TRY usually takes an absolute address or relative offset.
                         // In self-hosted generator, JMP targets are absolute instruction indices.
                         // Let's assume absolute.
                         let target = offset as usize;
                         let depth = self.stack.len();
                         frame.try_stack.push(TryBlock { handler_pc: target, stack_depth: depth });
                    }
                },
                50 => { // POP_TRY
                    if let Some(frame) = self.frames.last_mut() {
                        frame.try_stack.pop();
                    }
                },
                51 => { // THROW
                     let exc = self.stack.pop().expect("Stack");
                     self.throw_exception(exc);
                },
                53 => { // PRINT
                    let count = if let Constant::Integer(c) = arg { c as usize } else { 0 };
                    let start = self.stack.len() - count;
                    let args: Vec<Constant> = self.stack.drain(start..).collect();
                    for a in args { print!("{:?} ", a); }
                    println!();
                    io::stdout().flush().unwrap();
                },
                64 => { // STR
                    let v = self.stack.pop().unwrap();
                    self.stack.push(Constant::String(format!("{:?}", v)));
                },
                65 => { // LOAD_DEREF
                    if let Constant::String(name) = arg {
                        if let Some(frame) = self.frames.last() {
                            if let Some(v) = frame.locals.get(&name) {
                                if let Constant::Cell(c) = v { self.stack.push(c.borrow().clone()); }
                                else { panic!("LOAD_DEREF expected Cell"); }
                            } else { panic!("Deref var not found"); }
                        }
                    }
                },
                66 => { // STORE_DEREF
                    if let Constant::String(name) = arg {
                        let val = self.stack.pop().expect("Stack");
                        if let Some(frame) = self.frames.last() {
                             if let Some(v) = frame.locals.get(&name) {
                                 if let Constant::Cell(c) = v { *c.borrow_mut() = val; }
                                 else { panic!("STORE_DEREF expected Cell"); }
                             } else { panic!("Deref var not found"); }
                        }
                    }
                },
                67 => { // LOAD_CLOSURE
                    if let Constant::String(name) = arg {
                        if let Some(frame) = self.frames.last() {
                            if let Some(v) = frame.locals.get(&name) {
                                if let Constant::Cell(_) = v { self.stack.push(v.clone()); }
                                else { panic!("LOAD_CLOSURE expected Cell"); }
                            } else { panic!("Closure var not found"); }
                        }
                    }
                },
                68 => { // MAKE_FUNCTION
                    let _count = arg;
                    let func_or_code = self.stack.pop().expect("Stack");
                    let closure_list = self.stack.pop().expect("Stack");

                    let co_opt = match func_or_code {
                        Constant::Code(c) => Some(c),
                        Constant::Function(f) => Some(f.code.clone()),
                        _ => None,
                    };

                    if let Some(co) = co_opt {
                         if let Constant::List(cells_rc) = closure_list {
                             let mut closure = Vec::new();
                             for c in cells_rc.borrow().iter() {
                                 if let Constant::Cell(cell_ref) = c { closure.push(cell_ref.clone()); }
                                 else { panic!("MAKE_FUNCTION closure invalid"); }
                             }
                             // Capture current globals (Lexical Scope)
                             let globals = self.frames.last().unwrap().globals.clone();
                             let func = Function { name: co.name.clone(), code: co.clone(), closure, globals };
                             self.stack.push(Constant::Function(Rc::new(func)));
                         }
                    } else { panic!("MAKE_FUNCTION expects Code or Function"); }
                },
                _ => {},
            }
        }
    }
}

// ... Reader (unchanged) ...
struct Reader { buffer: Vec<u8>, pos: usize }
impl Reader {
    fn new(b: Vec<u8>) -> Self { Reader { buffer: b, pos: 0 } }
    fn read_byte(&mut self) -> Option<u8> { if self.pos < self.buffer.len() { let b = self.buffer[self.pos]; self.pos+=1; Some(b) } else { None } }
    fn read_bytes(&mut self, n: usize) -> Option<Vec<u8>> { if self.pos+n <= self.buffer.len() { let s = self.buffer[self.pos..self.pos+n].to_vec(); self.pos+=n; Some(s) } else { None } }
    fn read_int(&mut self) -> Option<i32> { let b = self.read_bytes(4)?; Some(i32::from_le_bytes(b.try_into().ok()?)) }
    fn read_float(&mut self) -> Option<f64> { let b = self.read_bytes(8)?; Some(f64::from_le_bytes(b.try_into().ok()?)) }
    fn read_string_raw(&mut self) -> Option<String> { let len = self.read_int()?; if len < 0 { return None; } let b = self.read_bytes(len as usize)?; String::from_utf8(b).ok() }
    fn read_constant(&mut self) -> Option<Constant> {
        let tag = self.read_byte()?;
        match tag {
            1 => Some(Constant::Nil),
            2 => Some(Constant::Boolean(self.read_byte()? == 1)),
            3 => Some(Constant::Integer(self.read_int()?)),
            4 => Some(Constant::Float(self.read_float()?)),
            5 => Some(Constant::String(self.read_string_raw()?)),
            6 => { let c = self.read_int()?; let mut l = Vec::new(); for _ in 0..c { l.push(self.read_constant()?); } Some(Constant::List(Rc::new(RefCell::new(l)))) },
            7 => Some(Constant::Code(Rc::new(self.read_code_object()?))),
            8 => { let c = self.read_int()?; let mut d = Vec::new(); for _ in 0..c { let k=self.read_constant()?; let v=self.read_constant()?; d.push((k,v)); } Some(Constant::Dict(Rc::new(RefCell::new(d)))) },
            _ => None,
        }
    }
    fn read_code_object(&mut self) -> Option<CodeObject> {
        let name = self.read_string_raw()?;
        let ac = self.read_byte()?; let mut args = Vec::new(); for _ in 0..ac { args.push(self.read_string_raw()?); }
        let cc = self.read_int()?; let mut consts = Vec::new(); for _ in 0..cc { consts.push(self.read_constant()?); }
        let ic = self.read_int()?; let mut instrs = Vec::new(); for _ in 0..ic { let o = self.read_byte()?; let a = self.read_constant()?; instrs.push((o, a)); }
        Some(CodeObject { name, args, constants: consts, instructions: instrs, free_vars: Vec::new(), cell_vars: Vec::new() })
    }
}

fn main() -> io::Result<()> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 { println!("Usage: morph_vm <file.mvm>"); return Ok(()); }
    let filename = &args[1];
    let mut file = File::open(filename)?;
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer)?;
    let mut reader = Reader::new(buffer);
    reader.read_bytes(16);
    if let Some(Constant::Code(co)) = reader.read_constant() {
        let mut vm = VM::new();
        let globals = Rc::new(RefCell::new(HashMap::new()));
        vm.run_code(co, globals);
    } else { panic!("Invalid"); }
    Ok(())
}
