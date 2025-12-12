use std::fs::File;
use std::io::{self, Read, Write};
use std::env;
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
            (Constant::Function(a), Constant::Function(b)) => Rc::ptr_eq(&a.code, &b.code),
            (Constant::Code(a), Constant::Code(b)) => Rc::ptr_eq(a, b),
            (Constant::Module(a), Constant::Module(b)) => Rc::ptr_eq(a, b),
            (Constant::File(a), Constant::File(b)) => Rc::ptr_eq(a, b),
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
struct CallFrame {
    code: Rc<CodeObject>,
    pc: usize,
    locals: HashMap<String, Constant>,
    globals: Rc<RefCell<HashMap<String, Constant>>>,
    closure: Vec<Rc<RefCell<Constant>>>,
}

// --- VM Runtime ---

struct VM {
    frames: Vec<CallFrame>,
    stack: Vec<Constant>,
    modules: HashMap<String, Rc<Module>>,
    universals: HashMap<String, Constant>,
}

impl VM {
    fn new() -> Self {
        let mut universals = HashMap::new();

        // 1. Inject 'argumen_sistem'
        let args: Vec<Constant> = env::args().map(Constant::String).collect();
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

        // 4. Inject String Intrinsics
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

        VM {
            frames: Vec::new(),
            stack: Vec::new(),
            modules: HashMap::new(),
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

            // println!("DEBUG: PC: {}, OP: {}, Stack: {:?}", self.frames.last().unwrap().pc - 1, op, self.stack);

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
                4 => {
                    let b = self.stack.pop().unwrap(); let a = self.stack.pop().unwrap();
                    match (&a, &b) {
                         (Constant::Integer(ia), Constant::Integer(ib)) => self.stack.push(Constant::Integer(ia + ib)),
                         (Constant::String(sa), Constant::String(sb)) => self.stack.push(Constant::String(sa.clone() + sb)),
                         _ => panic!("ADD mismatch"),
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
                    if let Some(m) = self.modules.get(&path) { self.stack.push(Constant::Module(m.clone())); }
                    else {
                        let filename = path.clone() + ".mvm";
                        let mut file = File::open(&filename).expect("Module file not found");
                        let mut buffer = Vec::new();
                        file.read_to_end(&mut buffer).unwrap();
                        let mut reader = Reader::new(buffer);
                        reader.read_bytes(16);
                        if let Some(Constant::Code(code_rc)) = reader.read_constant() {
                            let globals = Rc::new(RefCell::new(HashMap::new()));
                            let module = Rc::new(Module { name: path.clone(), globals: globals.clone() });
                            self.modules.insert(path.clone(), module.clone());
                            self.run_code(code_rc, globals);
                            if self.stack.pop().is_none() {} // Pop RetVal
                            self.stack.push(Constant::Module(module));
                        } else { panic!("Invalid module"); }
                    }
                },
                // IO Opcodes
                87 => { // IO_OPEN
                    let mode_v = self.stack.pop().unwrap();
                    let path_v = self.stack.pop().unwrap();
                    if let (Constant::String(path), Constant::String(_mode)) = (path_v, mode_v) {
                        let f = if _mode == "w" { File::create(path) } else { File::open(path) };
                        match f {
                            Ok(file) => self.stack.push(Constant::File(Rc::new(FileHandle(RefCell::new(Some(file)))))),
                            Err(_) => panic!("IO_OPEN failed"),
                        }
                    } else { panic!("IO_OPEN args"); }
                },
                88 => { // IO_READ
                    let _size_v = self.stack.pop().unwrap();
                    let handle = self.stack.pop().unwrap();
                    if let Constant::File(fh) = handle {
                        let mut file_opt = fh.0.borrow_mut();
                        if let Some(ref mut file) = *file_opt {
                            let mut buf = String::new();
                            file.read_to_string(&mut buf).unwrap();
                            self.stack.push(Constant::String(buf));
                        } else { panic!("File closed"); }
                    } else { panic!("IO_READ expects File"); }
                },
                89 => { // IO_WRITE
                    let content = self.stack.pop().unwrap();
                    let handle = self.stack.pop().unwrap();
                    if let (Constant::File(fh), Constant::String(s)) = (handle, content) {
                        let mut file_opt = fh.0.borrow_mut();
                        if let Some(ref mut file) = *file_opt {
                            file.write_all(s.as_bytes()).unwrap();
                            self.stack.push(Constant::Nil);
                        } else { panic!("File closed"); }
                    } else { panic!("IO_WRITE expects File, String"); }
                },
                90 => { // IO_CLOSE
                    let handle = self.stack.pop().unwrap();
                    if let Constant::File(fh) = handle { *fh.0.borrow_mut() = None; self.stack.push(Constant::Nil); }
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
                64 => { // STR
                    let val = self.stack.pop().expect("Stack underflow STR");
                    let s = match val {
                        Constant::String(s) => s,
                        Constant::Integer(i) => i.to_string(),
                        Constant::Float(f) => f.to_string(),
                        Constant::Boolean(b) => b.to_string(),
                        Constant::Nil => "nil".to_string(),
                        _ => format!("{:?}", val),
                    };
                    self.stack.push(Constant::String(s));
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
                         self.stack.push(Constant::Code(Rc::new(co)));
                    }
                },
                47 => { // CALL
                     let arg_count = if let Constant::Integer(c) = arg { c as usize } else { panic!("CALL arg"); };
                     let mut args = Vec::new();
                     for _ in 0..arg_count { args.push(self.stack.pop().expect("Stack")); }
                     args.reverse();

                     let func_obj = self.stack.pop().expect("Stack");
                     let (co, closure) = match func_obj {
                         Constant::Code(c) => (c, Vec::new()),
                         Constant::Function(f) => (f.code.clone(), f.closure.clone()),
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
                         globals: self.frames.last().unwrap().globals.clone(),
                         closure,
                     };
                     self.frames.push(frame);
                },
                48 => { self.frames.pop(); },
                53 => { // PRINT
                    let count = if let Constant::Integer(c) = arg { c as usize } else { 0 };
                    let start = self.stack.len() - count;
                    let args: Vec<Constant> = self.stack.drain(start..).collect();
                    for a in args { print!("{:?} ", a); }
                    println!();
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
                    let code_obj = self.stack.pop().expect("Stack");
                    let closure_list = self.stack.pop().expect("Stack");
                    if let Constant::Code(co) = code_obj {
                         if let Constant::List(cells_rc) = closure_list {
                             let mut closure = Vec::new();
                             for c in cells_rc.borrow().iter() {
                                 if let Constant::Cell(cell_ref) = c { closure.push(cell_ref.clone()); }
                                 else { panic!("MAKE_FUNCTION closure invalid"); }
                             }
                             let func = Function { name: co.name.clone(), code: co.clone(), closure };
                             self.stack.push(Constant::Function(Rc::new(func)));
                         }
                    }
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
